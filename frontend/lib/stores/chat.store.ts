import { create } from 'zustand';
import { persist } from 'zustand/middleware';

import { chatService } from '@/lib/api/chat.service';
import { ChatWebSocketMessageSchema } from '@/lib/validation/zod-schemas';
import type { ChatMessageMetadata } from '@/lib/validation/zod-schemas';

import { useAuthStore } from './auth.store';

import type { ChatConversation, ChatMessage } from '@/types/api';

// Type guard for error-like objects
function isErrorLike(e: unknown): e is { message: string } {
  return !!e && typeof e === 'object' && 'message' in e && typeof (e as Record<string, unknown>).message === 'string';
}

// Type guard for response errors
function hasResponseStatus(e: unknown): e is { response: { status: number } } {
  return !!e && typeof e === 'object' && 'response' in e &&
         typeof (e as Record<string, unknown>).response === 'object' &&
         (e as Record<string, unknown>).response !== null &&
         'status' in ((e as Record<string, unknown>).response as Record<string, unknown>) &&
         typeof ((e as Record<string, unknown>).response as Record<string, unknown>).status === 'number';
}

interface ChatState {
  // Conversations
  conversations: ChatConversation[];
  activeConversationId: string | null;

  // Widget-specific conversation
  widgetConversationId: string | null;

  // Messages
  messages: Record<string, ChatMessage[]>; // conversationId -> messages

  // WebSocket state
  isConnected: boolean;
  isTyping: boolean;
  typingUsers: string[];

  // Loading states
  isLoadingConversations: boolean;
  isLoadingMessages: boolean;
  isSendingMessage: boolean;

  // Error handling
  error: string | null;

  // WebSocket cleanup handlers
  cleanupHandlers: Map<string, () => void>;

  // Actions
  loadConversations: () => Promise<void>;
  loadConversation: (conversationId: string) => Promise<void>;
  createConversation: (title?: string, initialMessage?: string) => Promise<void>;
  setActiveConversation: (conversationId: string | null) => void;
  sendMessage: (message: string, metadata?: ChatMessageMetadata) => Promise<void>;
  deleteConversation: (conversationId: string) => Promise<void>;

  // Widget-specific actions
  createWidgetConversation: () => Promise<void>;
  loadWidgetConversation: () => Promise<void>;

  // WebSocket actions
  connectWebSocket: (conversationId: string) => void;
  disconnectWebSocket: () => void;

  // Utility actions
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  conversations: [],
  activeConversationId: null,
  widgetConversationId: null,
  messages: {},
  isConnected: false,
  isTyping: false,
  typingUsers: [],
  isLoadingConversations: false,
  isLoadingMessages: false,
  isSendingMessage: false,
  error: null,
  cleanupHandlers: new Map(),
};

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      ...initialState,

      loadConversations: async () => {
        set({ isLoadingConversations: true, error: null });
        try {
          // Check if user is authenticated before attempting to load
          const authToken = useAuthStore.getState().getToken();
          if (!authToken) {
            // No authentication, just set empty conversations and finish loading
            set({
              conversations: [],
              isLoadingConversations: false,
              error: null, // Don't show error for no auth, just show empty state
            });
            return;
          }

          const response = await chatService.getConversations();
          set({ conversations: response.items, isLoadingConversations: false });
        } catch (error: unknown) {
          // Handle authentication errors gracefully
          const errorMessage = isErrorLike(error) ? error.message : 'Failed to load conversations';
          const isAuthError = hasResponseStatus(error) &&
                             (error.response.status === 401 || error.response.status === 403);

          if (isAuthError) {
            // Auth error - just show empty state, don't block the UI
            set({
              conversations: [],
              isLoadingConversations: false,
              error: null, // Don't show auth errors, user can still create new conversation
            });
          } else {
            // Other errors - show briefly but don't block
            set({
              error: errorMessage,
              isLoadingConversations: false,
              conversations: [], // Still allow UI to render
            });
          }
        }
      },

      loadConversation: async (conversationId: string) => {
        set({ isLoadingMessages: true, error: null });
        try {
          const response = await chatService.getConversation(conversationId);
          set((state) => ({
            messages: {
              ...state.messages,
              [conversationId]: response.messages,
            },
            isLoadingMessages: false,
          }));

          // Connect WebSocket for real-time updates
          get().connectWebSocket(conversationId);
        } catch (error: unknown) {
          set({
            error: isErrorLike(error) ? error.message : 'Failed to load conversation',
            isLoadingMessages: false,
          });
        }
      },

      createConversation: async (title?: string, initialMessage?: string) => {
        set({ error: null });
        try {
          const response = await chatService.createConversation({
            title,
            initial_message: initialMessage,
          });

          set((state) => ({
            conversations: [response.conversation, ...state.conversations],
            messages: {
              ...state.messages,
              [response.conversation.id]: response.messages,
            },
            activeConversationId: response.conversation.id,
          }));

          // Connect WebSocket for the new conversation
          get().connectWebSocket(response.conversation.id);
        } catch (error: unknown) {
          set({ error: isErrorLike(error) ? error.message : 'Failed to create conversation' });
        }
      },

      setActiveConversation: (conversationId: string | null) => {
        const state = get();

        // Disconnect from previous conversation
        if (state.activeConversationId && state.activeConversationId !== conversationId) {
          state.disconnectWebSocket();
        }

        set({ activeConversationId: conversationId });

        // Load conversation if not already loaded
        if (conversationId && !state.messages[conversationId]) {
          state.loadConversation(conversationId);
        } else if (conversationId) {
          // Connect WebSocket if switching to existing conversation
          state.connectWebSocket(conversationId);
        }
      },

      sendMessage: async (message: string, metadata?: ChatMessageMetadata) => {
        const state = get();
        const conversationId =
          metadata?.source === 'widget' ? state.widgetConversationId : state.activeConversationId;

        if (!conversationId) return;

        set({ isSendingMessage: true, error: null });

        // Get current user info
        const { user: _user } = useAuthStore.getState();

        // Optimistically add message to UI
        const tempMessage: ChatMessage = {
          id: `temp-${Date.now()}`,
          conversation_id: conversationId,
          role: 'user',
          content: message,
          sequence_number: (state.messages[conversationId]?.length || 0) + 1,
          created_at: new Date().toISOString(),
        };

        set((state) => ({
          messages: {
            ...state.messages,
            [conversationId]: [...(state.messages[conversationId] || []), tempMessage],
          },
        }));

        try {
          // Send via WebSocket if connected, otherwise use REST API
          if (state.isConnected) {
            chatService.sendWebSocketMessage({
              type: 'message',
              data: { content: message, metadata },
            });
          } else {
            // Import IQ Agent service for compliance queries
            const { iqAgentService } = await import('@/lib/api/iq-agent.service');
            const { useIQAgentStore } = await import('@/lib/stores/iq-agent.store');
            
            let response;
            let isIQQuery = false;
            
            try {
              // Check if message is a compliance query
              isIQQuery = iqAgentService.isComplianceQuery(message);
              
              if (isIQQuery) {
                try {
                  // Set initial processing state via IQ Agent store
                  const iqStore = useIQAgentStore.getState();
                  iqStore.clearError();
                  
                  // Note: The actual processing will be handled by queryCompliance below
                  
                  // Add processing indicator message
                  const processingMessage: ChatMessage = {
                    id: `processing-${Date.now()}`,
                    conversation_id: conversationId,
                    role: 'assistant',
                    content: 'Analyzing your compliance question with GraphRAG...',
                    sequence_number: (state.messages[conversationId]?.length || 0) + 2,
                    created_at: new Date().toISOString(),
                    metadata: {
                      source: 'iq_agent',
                      is_processing: true
                    }
                  };
                  
                  set((state) => ({
                    messages: {
                      ...state.messages,
                      [conversationId]: [...(state.messages[conversationId] || []), processingMessage],
                    },
                  }));
                  
                  // Check IQ Agent health first
                  const healthStatus = await iqAgentService.getHealth();
                  
                  if (healthStatus.status === 'healthy' && healthStatus.neo4j_connected) {
                    // Use IQ Agent store's queryCompliance method which handles the full PPALE loop
                    const context = iqAgentService.extractContext(message);
                    
                    await iqStore.queryCompliance(message, { context });
                    
                    // Get the response from the IQ Agent store
                    const iqResponse = useIQAgentStore.getState().currentResponse;
                    
                    if (iqResponse) {
                      // Convert IQ response to chat message format
                      response = {
                        id: `iq-${Date.now()}`,
                        conversation_id: conversationId,
                        role: 'assistant' as const,
                        content: iqResponse.summary,
                        sequence_number: (state.messages[conversationId]?.length || 0) + 2,
                        created_at: new Date().toISOString(),
                        metadata: {
                          source: 'iq_agent',
                          confidence_score: iqResponse.confidence_score,
                          trust_level: iqResponse.trust_level,
                          evidence_count: iqResponse.evidence?.length || 0,
                          graph_nodes: iqResponse.graph_analysis?.nodes_accessed,
                          response_time: iqResponse.response_time_ms
                        }
                      };
                    } else {
                      throw new Error('IQ Agent processing completed but no response received');
                    }
                    
                    // Remove processing message and add actual response
                    set((state) => ({
                      messages: {
                        ...state.messages,
                        [conversationId]: [
                          ...state.messages[conversationId].filter(msg => msg.id !== processingMessage.id),
                          response
                        ],
                      },
                    }));
                    
                    // Don't set response variable since we've already updated the state
                    response = null;
                    
                  } else {
                    // Remove processing message first
                    set((state) => ({
                      messages: {
                        ...state.messages,
                        [conversationId]: state.messages[conversationId].filter(msg => msg.id !== processingMessage.id),
                      },
                    }));
                    
                    // IQ Agent unavailable, show warning and fallback to regular chat
                    iqStore.reportError({
                      error_type: 'service_unavailable',
                      message: 'IQ Agent is temporarily unavailable. Using regular chat.',
                      correlation_id: `health-${Date.now()}`
                    });
                    
                    response = await chatService.sendMessage(conversationId, {
                      content: message,
                    });
                  }
                  
                } catch (iqError) {
                  console.error('IQ Agent error:', iqError);
                  
                  // Remove processing message
                  set((state) => ({
                    messages: {
                      ...state.messages,
                      [conversationId]: state.messages[conversationId].filter(msg => !msg.metadata?.is_processing),
                    },
                  }));
                  
                  // Update IQ Agent store with error
                  iqStore.reportError({
                    error_type: 'processing_error',
                    message: iqError instanceof Error ? iqError.message : 'IQ Agent query failed',
                    correlation_id: `processing-${Date.now()}`
                  });
                  
                  // Fallback to regular chat
                  response = await chatService.sendMessage(conversationId, {
                    content: message,
                  });
                }
              } else {
                // Not a compliance query, use regular chat
                response = await chatService.sendMessage(conversationId, {
                  content: message,
                });
              }
            } catch (error) {
              // If this was an IQ query that failed, make sure we clean up properly
              if (isIQQuery) {
                console.error('IQ Agent processing failed:', error);
                
                // Clean up any processing messages
                set((state) => ({
                  messages: {
                    ...state.messages,
                    [conversationId]: state.messages[conversationId]?.filter(msg => !msg.metadata?.is_processing) || [],
                  },
                }));
                
                // Update IQ Agent store with error
                useIQAgentStore.getState().reportError({
                  error_type: 'chat_integration_error',
                  message: error instanceof Error ? error.message : 'IQ Agent query failed',
                  correlation_id: `chat-${Date.now()}`
                });
              }
              
              // Try fallback to regular chat
              try {
                response = await chatService.sendMessage(conversationId, {
                  content: message,
                });
              } catch (fallbackError) {
                console.error('Fallback chat also failed:', fallbackError);
                throw fallbackError;
              }
            }

            // Replace temp message with real one (only if response is not null)
            if (response) {
              set((state) => ({
                messages: {
                  ...state.messages,
                  [conversationId]:
                    state.messages[conversationId]?.map((msg) =>
                      msg.id === tempMessage.id ? response : msg,
                    ) || [],
                },
              }));
            } else {
              // If response is null (IQ Agent handled state internally), just remove temp message
              set((state) => ({
                messages: {
                  ...state.messages,
                  [conversationId]:
                    state.messages[conversationId]?.filter(msg => msg.id !== tempMessage.id) || [],
                },
              }));
            }
          }

          set({ isSendingMessage: false });
        } catch (error: unknown) {
          // Remove temp message on error
          set((state) => ({
            messages: {
              ...state.messages,
              [conversationId]:
                state.messages[conversationId]?.filter((msg) => msg.id !== tempMessage.id) || [],
            },
            error: isErrorLike(error) ? error.message : 'Failed to send message',
            isSendingMessage: false,
          }));
        }
      },

      deleteConversation: async (conversationId: string) => {
        set({ error: null });
        try {
          await chatService.deleteConversation(conversationId);

          set((state) => {
            const newState: Partial<ChatState> = {
              conversations: state.conversations.filter((c) => c.id !== conversationId),
            };

            // Clean up messages
            const newMessages = { ...state.messages };
            delete newMessages[conversationId];
            newState.messages = newMessages;

            // Reset active conversation if it was deleted
            if (state.activeConversationId === conversationId) {
              newState.activeConversationId = null;
              state.disconnectWebSocket();
            }

            return newState;
          });
        } catch (error: unknown) {
          set({ error: isErrorLike(error) ? error.message : 'Failed to delete conversation' });
        }
      },

      connectWebSocket: (conversationId: string) => {
        const state = get();
        const authToken = useAuthStore.getState().getToken();

        if (!authToken) {
          set({ error: 'Authentication required for chat' });
          return;
        }

        // Clean up any existing handler for this conversation
        const existingCleanup = state.cleanupHandlers.get(conversationId);
        if (existingCleanup) {
          existingCleanup();
        }

        // Set up message handler
        const cleanup = chatService.addMessageHandler((rawMessage: unknown) => {
          // Validate the incoming WebSocket message
          const validation = ChatWebSocketMessageSchema.safeParse(rawMessage);
          if (!validation.success) {
            console.warn('Invalid WebSocket message received:', validation.error);
            return;
          }

          const message = validation.data;

          switch (message.type) {
            case 'connection':
              set({
                isConnected: !!(
                  message.data &&
                  typeof message.data === 'object' &&
                  'status' in message.data &&
                  (message.data as Record<string, unknown>).status === 'connected'
                )
              });
              break;

            case 'message':
              // Add received message to the conversation
              if (
                message.data &&
                typeof message.data === 'object' &&
                'conversation_id' in message.data &&
                (message.data as Record<string, unknown>).conversation_id === conversationId
              ) {
                set((state) => ({
                  messages: {
                    ...state.messages,
                    [conversationId]: [...(state.messages[conversationId] || []), message.data as ChatMessage],
                  },
                }));
              }
              break;

            case 'typing':
              // Handle typing indicators
              if (
                message.data &&
                typeof message.data === 'object' &&
                'action' in message.data &&
                'user' in message.data
              ) {
                const data = message.data as Record<string, unknown>;
                if (data.action === 'start') {
                  set((state) => ({
                    typingUsers: [...state.typingUsers, data.user as string],
                  }));
                } else if (data.action === 'stop') {
                  set((state) => ({
                    typingUsers: state.typingUsers.filter((u) => u !== data.user),
                  }));
                }
              }
              break;

            case 'error':
              set({
                error:
                  message.data &&
                  typeof message.data === 'object' &&
                  'message' in message.data
                    ? (message.data as Record<string, unknown>).message as string
                    : 'WebSocket error occurred'
              });
              break;
          }
        });

        // Store cleanup function
        set((state) => {
          const newHandlers = new Map(state.cleanupHandlers);
          newHandlers.set(conversationId, cleanup);
          return { cleanupHandlers: newHandlers };
        });

        // Connect to WebSocket with auth token
        const wsUrl = `${chatService.getWebSocketUrl(conversationId)}?token=${authToken}`;
        chatService.connectWebSocketWithUrl(wsUrl);
      },

      disconnectWebSocket: () => {
        const state = get();

        // Clean up all message handlers
        state.cleanupHandlers.forEach((cleanup) => cleanup());

        set({
          cleanupHandlers: new Map(),
          isConnected: false,
          typingUsers: [],
        });

        chatService.disconnectWebSocket();
      },

      createWidgetConversation: async () => {
        set({ error: null });
        try {
          const response = await chatService.createConversation({
            title: 'Chat Support',
            initial_message: 'Chat widget conversation',
          });

          set((state) => ({
            widgetConversationId: response.conversation.id,
            messages: {
              ...state.messages,
              [response.conversation.id]: response.messages || [],
            },
          }));

          // Connect WebSocket for the widget conversation
          get().connectWebSocket(response.conversation.id);
        } catch (error: unknown) {
          set({ error: isErrorLike(error)
                ? error.message
                : 'Failed to create widget conversation' });
        }
      },

      loadWidgetConversation: async () => {
        const state = get();
        if (!state.widgetConversationId) return;

        set({ isLoadingMessages: true, error: null });
        try {
          const response = await chatService.getConversation(state.widgetConversationId);
          set((state) => ({
            messages: {
              ...state.messages,
              [state.widgetConversationId!]: response.messages,
            },
            isLoadingMessages: false,
          }));

          // Connect WebSocket for real-time updates
          get().connectWebSocket(state.widgetConversationId);
        } catch (error: unknown) {
          set({
            error: isErrorLike(error)
                ? error.message
                : 'Failed to load widget conversation',
            isLoadingMessages: false,
          });
        }
      },

      clearError: () => set({ error: null }),

      reset: () => {
        get().disconnectWebSocket();
        set(initialState);
      },
    }),
    {
      name: 'chat-store',
      partialize: (state) => ({
        conversations: state.conversations,
        activeConversationId: state.activeConversationId,
        widgetConversationId: state.widgetConversationId,
        messages: state.messages,
      }),
    },
  ),
);
