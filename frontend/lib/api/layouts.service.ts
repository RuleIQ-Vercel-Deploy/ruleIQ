import { apiClient } from './client';
import {
  DashboardLayout,
  LayoutPersistencePayload,
  LayoutSnapshot,
  LayoutTemplate,
  LayoutImportResult,
  LayoutExportOptions,
} from '@/types/layout';

// Request deduplication cache
const pendingRequests = new Map<string, Promise<any>>();

// Helper to create cache key
const getCacheKey = (method: string, userId: string, layoutId?: string) => {
  return `${method}-${userId}${layoutId ? `-${layoutId}` : ''}`;
};

// Helper for request deduplication
const deduplicateRequest = async <T>(
  key: string,
  requestFn: () => Promise<T>
): Promise<T> => {
  const existing = pendingRequests.get(key);
  if (existing) {
    return existing;
  }

  const promise = requestFn().finally(() => {
    pendingRequests.delete(key);
  });

  pendingRequests.set(key, promise);
  return promise;
};

// Calculate checksum for layout data
const calculateChecksum = (layout: DashboardLayout): string => {
  const data = JSON.stringify({
    widgets: layout.widgets,
    ruleOrder: layout.ruleOrder,
  });

  // Simple hash function for checksum
  let hash = 0;
  for (let i = 0; i < data.length; i++) {
    const char = data.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }

  return hash.toString(16);
};

// Validate layout data integrity
const validateLayoutData = (layout: DashboardLayout): boolean => {
  if (!layout || typeof layout !== 'object') {
    return false;
  }

  // Check required fields
  if (!layout.id || !layout.userId || !Array.isArray(layout.widgets) || !Array.isArray(layout.ruleOrder)) {
    return false;
  }

  // Validate widget positions
  for (const widget of layout.widgets) {
    if (!widget.id || typeof widget.gridX !== 'number' || typeof widget.gridY !== 'number') {
      return false;
    }
  }

  return true;
};

// Compress layout data for storage
const compressLayout = (layout: DashboardLayout): string => {
  // In production, you might use a proper compression library
  // For now, we'll just stringify with minimal whitespace
  return JSON.stringify(layout);
};

// Decompress layout data
const decompressLayout = (data: string): DashboardLayout => {
  return JSON.parse(data);
};

export const layoutsService = {
  // Save layout with retry logic
  async saveLayout(userId: string, layout: DashboardLayout, retries = 3): Promise<void> {
    const cacheKey = getCacheKey('save', userId);

    return deduplicateRequest(cacheKey, async () => {
      // Validate layout before sending
      if (!validateLayoutData(layout)) {
        throw new Error('Invalid layout data');
      }

      const payload: LayoutPersistencePayload = {
        layout,
        timestamp: new Date().toISOString(),
        checksum: calculateChecksum(layout),
        compressed: true,
      };

      let attempt = 0;
      let lastError: Error | null = null;

      while (attempt < retries) {
        try {
          await apiClient.post(`/layouts/${userId}`, {
            data: compressLayout(layout),
            checksum: payload.checksum,
            timestamp: payload.timestamp,
          });
          return;
        } catch (error) {
          lastError = error as Error;
          attempt++;

          if (attempt < retries) {
            // Exponential backoff
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
          }
        }
      }

      throw lastError || new Error('Failed to save layout after retries');
    });
  },

  // Get layout with caching
  async getLayout(userId: string): Promise<DashboardLayout | null> {
    const cacheKey = getCacheKey('get', userId);

    return deduplicateRequest(cacheKey, async () => {
      try {
        const response = await apiClient.get<{ data: string; checksum: string }>(`/layouts/${userId}`);

        if (!response.data) {
          return null;
        }

        const layout = decompressLayout(response.data);

        // Validate checksum
        const expectedChecksum = calculateChecksum(layout);
        if (response.checksum && response.checksum !== expectedChecksum) {
          console.warn('Layout checksum mismatch, data may be corrupted');
        }

        // Validate layout structure
        if (!validateLayoutData(layout)) {
          throw new Error('Invalid layout data received from server');
        }

        return layout;
      } catch (error: any) {
        if (error.response?.status === 404) {
          return null; // No saved layout found
        }
        throw error;
      }
    });
  },

  // Delete layout
  async deleteLayout(userId: string): Promise<void> {
    await apiClient.delete(`/layouts/${userId}`);
  },

  // Get all layout snapshots for a user
  async getSnapshots(userId: string): Promise<LayoutSnapshot[]> {
    const response = await apiClient.get<LayoutSnapshot[]>(`/layouts/${userId}/snapshots`);
    return response;
  },

  // Save a layout snapshot
  async saveSnapshot(
    userId: string,
    snapshot: Omit<LayoutSnapshot, 'id' | 'createdAt'>
  ): Promise<LayoutSnapshot> {
    const response = await apiClient.post<LayoutSnapshot>(`/layouts/${userId}/snapshots`, snapshot);
    return response;
  },

  // Delete a snapshot
  async deleteSnapshot(userId: string, snapshotId: string): Promise<void> {
    await apiClient.delete(`/layouts/${userId}/snapshots/${snapshotId}`);
  },

  // Get available layout templates
  async getTemplates(category?: string): Promise<LayoutTemplate[]> {
    const params = category ? { category } : {};
    const response = await apiClient.get<LayoutTemplate[]>('/layouts/templates', { params });
    return response;
  },

  // Apply a template to current layout
  async applyTemplate(userId: string, templateId: string): Promise<DashboardLayout> {
    const response = await apiClient.post<DashboardLayout>(
      `/layouts/${userId}/apply-template`,
      { templateId }
    );
    return response;
  },

  // Export layout in specified format
  async exportLayout(
    userId: string,
    layoutId: string,
    options: LayoutExportOptions
  ): Promise<Blob> {
    const response = await apiClient.post(
      `/layouts/${userId}/export`,
      { layoutId, ...options },
      { responseType: 'blob' }
    );
    return response;
  },

  // Import layout from file
  async importLayout(
    userId: string,
    file: File,
    options?: { replace?: boolean; validate?: boolean }
  ): Promise<LayoutImportResult> {
    const formData = new FormData();
    formData.append('file', file);

    if (options?.replace !== undefined) {
      formData.append('replace', options.replace.toString());
    }

    if (options?.validate !== undefined) {
      formData.append('validate', options.validate.toString());
    }

    const response = await apiClient.post<LayoutImportResult>(
      `/layouts/${userId}/import`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response;
  },

  // Share layout with other users
  async shareLayout(
    userId: string,
    layoutId: string,
    shareWith: string[]
  ): Promise<{ shareUrl: string; expiresAt: string }> {
    const response = await apiClient.post<{ shareUrl: string; expiresAt: string }>(
      `/layouts/${userId}/share`,
      { layoutId, shareWith }
    );
    return response;
  },

  // Get shared layout
  async getSharedLayout(shareToken: string): Promise<DashboardLayout> {
    const response = await apiClient.get<DashboardLayout>(`/layouts/shared/${shareToken}`);
    return response;
  },

  // Duplicate an existing layout
  async duplicateLayout(
    userId: string,
    layoutId: string,
    name: string
  ): Promise<DashboardLayout> {
    const response = await apiClient.post<DashboardLayout>(
      `/layouts/${userId}/duplicate`,
      { layoutId, name }
    );
    return response;
  },

  // Get layout history/versions
  async getLayoutHistory(
    userId: string,
    limit = 10
  ): Promise<Array<{ version: number; timestamp: string; changes: string }>> {
    const response = await apiClient.get<Array<{ version: number; timestamp: string; changes: string }>>(
      `/layouts/${userId}/history`,
      { params: { limit } }
    );
    return response;
  },

  // Restore layout to a previous version
  async restoreVersion(userId: string, version: number): Promise<DashboardLayout> {
    const response = await apiClient.post<DashboardLayout>(
      `/layouts/${userId}/restore`,
      { version }
    );
    return response;
  },

  // Validate layout without saving
  async validateLayout(layout: DashboardLayout): Promise<{
    valid: boolean;
    errors?: string[];
    warnings?: string[];
  }> {
    const response = await apiClient.post<{
      valid: boolean;
      errors?: string[];
      warnings?: string[];
    }>('/layouts/validate', layout);
    return response;
  },

  // Get layout statistics
  async getLayoutStats(userId: string): Promise<{
    totalLayouts: number;
    totalSnapshots: number;
    lastModified: string;
    mostUsedWidgets: Array<{ widgetId: string; count: number }>;
  }> {
    const response = await apiClient.get<{
      totalLayouts: number;
      totalSnapshots: number;
      lastModified: string;
      mostUsedWidgets: Array<{ widgetId: string; count: number }>;
    }>(`/layouts/${userId}/stats`);
    return response;
  },
};