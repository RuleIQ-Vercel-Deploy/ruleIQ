import apiClient from "@/lib/api-client"
import type { ChatConversation, ChatMessage, ChatSettings } from "@/types/api"

export const chatApi = {
  // Conversations
  getConversations: async (): Promise<ChatConversation[]> => {
    const response = await apiClient.get("/chat/conversations")
    return response.data
  },

  getConversation: async (id: string): Promise<ChatConversation> => {
    const response = await apiClient.get(`/chat/conversations/${id}`)
    return response.data
  },

  createConversation: async (title?: string): Promise<ChatConversation> => {
    const response = await apiClient.post("/chat/conversations", { title })
    return response.data
  },

  updateConversation: async (id: string, data: Partial<ChatConversation>): Promise<ChatConversation> => {
    const response = await apiClient.put(`/chat/conversations/${id}`, data)
    return response.data
  },

  deleteConversation: async (id: string): Promise<void> => {
    await apiClient.delete(`/chat/conversations/${id}`)
  },

  pinConversation: async (id: string, pinned: boolean): Promise<ChatConversation> => {
    const response = await apiClient.patch(`/chat/conversations/${id}/pin`, { is_pinned: pinned })
    return response.data
  },

  // Messages
  getMessages: async (conversationId: string, page = 1, limit = 50): Promise<ChatMessage[]> => {
    const response = await apiClient.get(`/chat/conversations/${conversationId}/messages`, {
      params: { page, limit },
    })
    return response.data
  },

  sendMessage: async (conversationId: string, content: string, files?: File[]): Promise<ChatMessage> => {
    const formData = new FormData()
    formData.append("content", content)
    if (files) {
      files.forEach((file) => formData.append("files", file))
    }

    const response = await apiClient.post(`/chat/conversations/${conversationId}/messages`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    return response.data
  },

  editMessage: async (conversationId: string, messageId: string, content: string): Promise<ChatMessage> => {
    const response = await apiClient.put(`/chat/conversations/${conversationId}/messages/${messageId}`, { content })
    return response.data
  },

  deleteMessage: async (conversationId: string, messageId: string): Promise<void> => {
    await apiClient.delete(`/chat/conversations/${conversationId}/messages/${messageId}`)
  },

  addReaction: async (conversationId: string, messageId: string, emoji: string): Promise<ChatMessage> => {
    const response = await apiClient.post(`/chat/conversations/${conversationId}/messages/${messageId}/reactions`, {
      emoji,
    })
    return response.data
  },

  // Search
  searchMessages: async (query: string, conversationId?: string): Promise<ChatMessage[]> => {
    const params = new URLSearchParams({ query })
    if (conversationId) params.append("conversation_id", conversationId)

    const response = await apiClient.get(`/chat/search?${params}`)
    return response.data
  },

  // Settings
  getSettings: async (): Promise<ChatSettings> => {
    const response = await apiClient.get("/chat/settings")
    return response.data
  },

  updateSettings: async (settings: Partial<ChatSettings>): Promise<ChatSettings> => {
    const response = await apiClient.put("/chat/settings", settings)
    return response.data
  },

  // Export
  exportConversation: async (conversationId: string, format: "json" | "pdf" | "txt"): Promise<Blob> => {
    const response = await apiClient.get(`/chat/conversations/${conversationId}/export`, {
      params: { format },
      responseType: "blob",
    })
    return response.data
  },
}
