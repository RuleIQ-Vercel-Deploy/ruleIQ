/**
 * Tests for secure storage implementation
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import SecureStorage from '@/lib/utils/secure-storage';

// Mock Web Crypto API for tests
Object.defineProperty(global, 'crypto', {
  value: {
    subtle: {
      generateKey: vi.fn().mockResolvedValue({
        type: 'secret',
        extractable: true,
        algorithm: { name: 'AES-GCM', length: 256 },
        usages: ['encrypt', 'decrypt']
      } as CryptoKey),
      exportKey: vi.fn().mockResolvedValue(new ArrayBuffer(32)),
      importKey: vi.fn().mockResolvedValue({
        type: 'secret',
        extractable: true,
        algorithm: { name: 'AES-GCM', length: 256 },
        usages: ['encrypt', 'decrypt']
      } as CryptoKey),
      encrypt: vi.fn().mockResolvedValue(new ArrayBuffer(32)), // Make this longer to include IV
      decrypt: vi.fn().mockResolvedValue(new TextEncoder().encode('decrypted-token')),
    },
    getRandomValues: vi.fn().mockImplementation((arr: Uint8Array) => {
      for (let i = 0; i < arr.length; i++) {
        arr[i] = Math.floor(Math.random() * 256);
      }
      return arr;
    }),
  },
});

// Mock TextEncoder/TextDecoder
global.TextEncoder = class {
  encode(input: string): Uint8Array {
    return new Uint8Array(Buffer.from(input, 'utf-8'));
  }
} as any;

global.TextDecoder = class {
  decode(input: ArrayBuffer): string {
    return Buffer.from(input).toString('utf-8');
  }
} as any;

// Mock atob/btoa
global.atob = (str: string) => Buffer.from(str, 'base64').toString('utf-8');
global.btoa = (str: string) => Buffer.from(str, 'utf-8').toString('base64');

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
});

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock document.cookie
Object.defineProperty(document, 'cookie', {
  writable: true,
  value: '',
});

describe('SecureStorage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorageMock.getItem.mockReturnValue(null);
    localStorageMock.getItem.mockReturnValue(null);
    document.cookie = '';
  });

  describe('Token Storage', () => {
    it('should store and retrieve access tokens securely', async () => {
      const testToken = 'test-access-token';
      const expiry = Date.now() + 3600000; // 1 hour

      // Mock successful encryption
      const mockEncrypted = 'encrypted-token-data';
      vi.mocked(crypto.subtle.encrypt).mockResolvedValue(
        new ArrayBuffer(16)
      );

      await SecureStorage.setAccessToken(testToken, { expiry });

      expect(sessionStorageMock.setItem).toHaveBeenCalledWith(
        'ruleiq_access_token',
        expect.any(String)
      );
      expect(sessionStorageMock.setItem).toHaveBeenCalledWith(
        'ruleiq_session_expiry',
        expiry.toString()
      );
    });

    it('should retrieve access tokens and decrypt them', async () => {
      const testToken = 'test-access-token';
      const mockEncrypted = 'encrypted-token-data';

      // Mock stored encrypted token
      sessionStorageMock.getItem.mockReturnValue(mockEncrypted);

      // Mock successful decryption
      vi.mocked(crypto.subtle.decrypt).mockResolvedValue(
        new ArrayBuffer(testToken.length)
      );

      const result = await SecureStorage.getAccessToken();

      expect(sessionStorageMock.getItem).toHaveBeenCalledWith('ruleiq_access_token');
      expect(result).toBeDefined();
    });

    it('should handle decryption errors gracefully', async () => {
      const mockEncrypted = 'corrupted-encrypted-data';
      sessionStorageMock.getItem.mockReturnValue(mockEncrypted);

      // Mock decryption failure
      vi.mocked(crypto.subtle.decrypt).mockRejectedValue(new Error('Decryption failed'));

      const result = await SecureStorage.getAccessToken();

      expect(result).toBeNull();
      expect(sessionStorageMock.removeItem).toHaveBeenCalledWith('ruleiq_access_token');
    });
  });

  describe('Session Management', () => {
    it('should correctly identify expired sessions', () => {
      const pastExpiry = Date.now() - 1000; // 1 second ago
      sessionStorageMock.getItem.mockReturnValue(pastExpiry.toString());

      const isExpired = SecureStorage.isSessionExpired();

      expect(isExpired).toBe(true);
    });

    it('should correctly identify valid sessions', () => {
      const futureExpiry = Date.now() + 3600000; // 1 hour from now
      sessionStorageMock.getItem.mockReturnValue(futureExpiry.toString());

      const isExpired = SecureStorage.isSessionExpired();

      expect(isExpired).toBe(false);
    });
  });

  describe('Legacy Token Migration', () => {
    it('should migrate legacy tokens to secure storage', async () => {
      const legacyToken = 'legacy-access-token';
      const legacyRefresh = 'legacy-refresh-token';
      const legacyExpiry = Date.now() + 3600000;

      // Mock legacy tokens in localStorage
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'ruleiq_auth_token') return legacyToken;
        if (key === 'ruleiq_refresh_token') return legacyRefresh;
        if (key === 'ruleiq_session_expiry') return legacyExpiry.toString();
        return null;
      });

      await SecureStorage.migrateLegacyTokens();

      // Should store tokens securely
      expect(sessionStorageMock.setItem).toHaveBeenCalled();
      
      // Should clear legacy tokens
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('ruleiq_auth_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('ruleiq_refresh_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('ruleiq_session_expiry');
    });
  });

  describe('Clear All Data', () => {
    it('should clear all stored tokens and encryption keys', () => {
      SecureStorage.clearAll();

      expect(sessionStorageMock.removeItem).toHaveBeenCalledWith('ruleiq_access_token');
      expect(sessionStorageMock.removeItem).toHaveBeenCalledWith('ruleiq_session_expiry');
      expect(sessionStorageMock.removeItem).toHaveBeenCalledWith('ruleiq_encryption_key');
      
      // Should also clear legacy tokens
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('ruleiq_auth_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('ruleiq_refresh_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('ruleiq_session_expiry');
    });
  });
});