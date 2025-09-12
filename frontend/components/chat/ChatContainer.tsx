'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ChatMessage, TrustLevel, Agent, Session } from '@/lib/websocket/types';
import { getWebSocketClient } from '@/lib/websocket/client';
import { Message } from './Message';
import { TrustIndicator } from './TrustIndicator';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';

interface ChatContainerProps {
  agent: Agent;
  session: Session;
  onSessionEnd?: () => void;
}

export function ChatContainer({ agent, session, onSessionEnd }: ChatContainerProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(session.messages || []);
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Initialize WebSocket connection
  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
    
    const wsClient = getWebSocketClient(wsUrl, {
      onOpen: () => {
        setIsConnected(true);
        setIsConnecting(false);
        toast({
          title: 'Connected',
          description: 'Connected to agent service',
        });
      },
      onClose: () => {
        setIsConnected(false);
        toast({
          title: 'Disconnected',
          description: 'Connection to agent service lost',
          variant: 'destructive',
        });
      },
      onError: (error) => {
        console.error('WebSocket error:', error);
        toast({
          title: 'Connection Error',
          description: 'Failed to connect to agent service',
          variant: 'destructive',
        });
      },
      onMessage: (wsMessage) => {
        // Convert WSMessage to ChatMessage
        const chatMessage: ChatMessage = {
          id: wsMessage.id,
          content: wsMessage.payload.content || '',
          role: wsMessage.payload.metadata?.role || 'agent',
          timestamp: wsMessage.timestamp,
          agentId: wsMessage.payload.metadata?.agentId,
          sessionId: wsMessage.payload.metadata?.sessionId,
          trustLevel: wsMessage.payload.metadata?.trustLevel,
          status: 'delivered'
        };
        
        setMessages(prev => [...prev, chatMessage]);
      },
      onTyping: (indicator) => {
        if (indicator.sessionId === session.id) {
          setIsTyping(indicator.isTyping);
        }
      }
    });

    setIsConnecting(true);
    wsClient.connect();

    return () => {
      wsClient.disconnect();
    };
  }, [session.id, toast]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle sending messages
  const handleSendMessage = useCallback((content: string, attachments?: File[]) => {
    const wsClient = getWebSocketClient();
    
    const newMessage: ChatMessage = {
      id: `${Date.now()}-${Math.random()}`,
      content,
      role: 'user',
      timestamp: new Date(),
      sessionId: session.id,
      status: 'sending'
    };
    
    // Optimistically add message to UI
    setMessages(prev => [...prev, newMessage]);
    
    // Send through WebSocket
    wsClient.sendChatMessage(content, {
      agentId: agent.id,
      sessionId: session.id,
      userId: session.userId,
      role: 'user'
    });
    
    // Update message status after a delay
    setTimeout(() => {
      setMessages(prev => 
        prev.map(msg => 
          msg.id === newMessage.id 
            ? { ...msg, status: 'sent' }
            : msg
        )
      );
    }, 500);
  }, [agent.id, session.id, session.userId]);

  return (
    <Card className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold">
            {agent.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h3 className="font-semibold">{agent.name}</h3>
            <p className="text-sm text-muted-foreground">{agent.personaType}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <TrustIndicator trustLevel={session.trustLevel} />
          <div className="flex items-center gap-1">
            <span
              className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-gray-400'
              }`}
            />
            <span className="text-xs text-muted-foreground">
              {isConnected ? 'Connected' : isConnecting ? 'Connecting...' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <Message key={message.id} message={message} />
          ))}
          {isTyping && (
            <TypingIndicator agentName={agent.name} />
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="border-t p-4">
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={!isConnected}
          placeholder={
            isConnected
              ? `Message ${agent.name}...`
              : 'Waiting for connection...'
          }
        />
      </div>
    </Card>
  );
}