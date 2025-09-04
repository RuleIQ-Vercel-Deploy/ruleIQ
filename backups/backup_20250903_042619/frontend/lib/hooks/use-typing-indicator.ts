import { useEffect, useRef, useCallback } from 'react';

import { chatService } from '@/lib/api/chat.service';
import { useChatStore } from '@/lib/stores/chat.store';

export function useTypingIndicator() {
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isTypingRef = useRef(false);
  const { activeConversationId, isConnected } = useChatStore();

  const sendTypingIndicator = useCallback(
    (isTyping: boolean) => {
      if (!isConnected || !activeConversationId) return;

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
    },
    [isConnected, activeConversationId],
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
