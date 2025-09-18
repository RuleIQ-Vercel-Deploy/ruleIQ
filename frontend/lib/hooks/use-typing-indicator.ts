import { useEffect, useRef, useCallback } from 'react';

import { chatService } from '@/lib/api/chat.service';
import { useChatStore } from '@/lib/stores/chat.store';
import { getWebSocketClient } from '@/lib/websocket/client';

interface UseTypingIndicatorProps {
  sessionId?: string;
  agentId?: string;
  useWebSocketClient?: boolean;
}

export function useTypingIndicator(props?: UseTypingIndicatorProps) {
  const { sessionId, agentId, useWebSocketClient = false } = props || {};
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isTypingRef = useRef(false);
  const { activeConversationId, isConnected } = useChatStore();

  const sendTypingIndicator = useCallback(
    (isTyping: boolean) => {
      // Compute canSend based on the mode
      const canSend = useWebSocketClient
        ? (() => {
            try {
              return getWebSocketClient().getConnectionState().connected;
            } catch {
              return false;
            }
          })()
        : isConnected;

      if (!canSend) return;

      // For WebSocketClient mode
      if (useWebSocketClient && sessionId && agentId) {
        // Only send if typing state actually changed
        if (isTypingRef.current !== isTyping) {
          isTypingRef.current = isTyping;

          try {
            const wsClient = getWebSocketClient();
            wsClient.sendTypingIndicator(isTyping, sessionId, agentId);
          } catch (error) {
            console.error('Failed to send typing indicator via WebSocketClient:', error);
            // Fallback to chatService if WebSocketClient fails
            if (activeConversationId) {
              chatService.sendWebSocketMessage({
                type: 'typing',
                data: {
                  action: isTyping ? 'start' : 'stop',
                  conversation_id: activeConversationId,
                },
              });
            }
          }
        }
      }
      // For chatService mode (backward compatibility)
      else if (activeConversationId) {
        // Only send if typing state actually changed
        if (isTypingRef.current !== isTyping) {
          isTypingRef.current = isTyping;

          chatService.sendWebSocketMessage({
            type: 'typing',
            data: {
              action: isTyping ? 'start' : 'stop',
              conversation_id: activeConversationId,
            },
          });
        }
      }
    },
    [isConnected, activeConversationId, useWebSocketClient, sessionId, agentId],
  );

  const handleTypingStop = useCallback(() => {
    // Clear all timeouts
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
      debounceTimeoutRef.current = null;
    }

    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = null;
    }

    // Send stop typing indicator
    sendTypingIndicator(false);
  }, [sendTypingIndicator]);

  const handleTypingStart = useCallback(
    (message: string) => {
      // Clear existing debounce timeout
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }

      // Don't send typing indicator for empty messages
      if (!message.trim()) {
        handleTypingStop();
        return;
      }

      // Debounce the typing start event (500ms)
      debounceTimeoutRef.current = setTimeout(() => {
        sendTypingIndicator(true);

        // Clear existing stop timeout
        if (typingTimeoutRef.current) {
          clearTimeout(typingTimeoutRef.current);
        }

        // Set timeout to stop typing after 3 seconds of inactivity
        typingTimeoutRef.current = setTimeout(() => {
          sendTypingIndicator(false);
        }, 3000);
      }, 500);
    },
    [sendTypingIndicator, handleTypingStop],
  );

  // Cleanup on unmount or when conversation changes
  useEffect(() => {
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      // Ensure we send stop typing when unmounting
      if (isTypingRef.current) {
        sendTypingIndicator(false);
      }
    };
  }, [activeConversationId, sendTypingIndicator]);

  return {
    handleTypingStart,
    handleTypingStop,
  };
}
