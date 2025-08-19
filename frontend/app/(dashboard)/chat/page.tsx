'use client';

import { Plus, MessageSquare } from 'lucide-react';
import { useEffect } from 'react';

import { ChatHeader } from '@/components/chat/chat-header';
import { ChatInput } from '@/components/chat/chat-input';
import { ChatMessage } from '@/components/chat/chat-message';
import { ConversationSidebar } from '@/components/chat/conversation-sidebar';
import { TypingIndicator } from '@/components/chat/typing-indicator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { useChatStore } from '@/lib/stores/chat.store';

export default function ChatPage() {
  const {
    conversations,
    activeConversationId,
    messages,
    isConnected,
    typingUsers,
    isLoadingConversations,
    isLoadingMessages,
    error,
    loadConversations,
    setActiveConversation,
    createConversation,
    sendMessage,
    clearError,
  } = useChatStore();

  const activeConversation = conversations?.find((c) => c.id === activeConversationId);
  const activeMessages = activeConversationId ? messages[activeConversationId] || [] : [];

  useEffect(() => {
    loadConversations();

    // Cleanup on unmount
    return () => {
      useChatStore.getState().disconnectWebSocket();
    };
  }, []);

  const handleNewConversation = async () => {
    await createConversation('New Conversation');
  };

  const handleSendMessage = async (message: string) => {
    await sendMessage(message);
  };

  const handleActionClick = (action: string, data?: any) => {
    console.log('Action clicked:', action, data);
    
    // Handle different action types
    switch (action) {
      case 'view_gap_details':
      case 'view_recommendation_details':
      case 'view_full_analysis':
        // Could open a modal or navigate to detail page
        console.log('Viewing details for:', data);
        break;
      
      case 'implement_recommendation':
      case 'create_evidence_task':
        // Could create tasks or initiate workflows
        console.log('Creating action for:', data);
        break;
      
      case 'ask_followup':
        // Send a follow-up message
        if (data && typeof data === 'string') {
          handleSendMessage(data);
        }
        break;
      
      case 'view_all_gaps':
      case 'view_all_recommendations':
        // Could show expanded view
        console.log('Showing all items:', data);
        break;
      
      default:
        console.log('Unhandled action:', action, data);
    }
  };

  if (isLoadingConversations) {
    return (
      <div className="flex h-[calc(100vh-4rem)]">
        <div className="w-80 space-y-4 border-r p-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="text-center text-muted-foreground">
            <MessageSquare className="mx-auto mb-4 h-12 w-12" />
            <p>Loading conversations...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Conversation Sidebar */}
      <div className="flex w-80 flex-col border-r">
        <div className="border-b p-4">
          <Button
            onClick={handleNewConversation}
            className="w-full bg-gold text-navy hover:bg-gold-dark"
          >
            <Plus className="mr-2 h-4 w-4" />
            New Conversation
          </Button>
        </div>
        <ConversationSidebar
          conversations={conversations}
          activeConversationId={activeConversationId}
          onSelectConversation={setActiveConversation}
          onDeleteConversation={useChatStore.getState().deleteConversation}
        />
      </div>

      {/* Chat Area */}
      {activeConversation ? (
        <div className="flex flex-1 flex-col bg-background">
          <ChatHeader
            title={activeConversation.title || 'AI Assistant'}
            isConnected={isConnected}
          />

          {error && (
            <Alert variant="destructive" className="m-4">
              <AlertDescription className="flex items-center justify-between">
                {error}
                <Button variant="ghost" size="sm" onClick={clearError}>
                  Dismiss
                </Button>
              </AlertDescription>
            </Alert>
          )}

          <div className="flex-1 space-y-6 overflow-y-auto p-6">
            {isLoadingMessages ? (
              <div className="space-y-4">
                <Skeleton className="h-20 w-3/4" />
                <Skeleton className="ml-auto h-20 w-3/4" />
                <Skeleton className="h-20 w-3/4" />
              </div>
            ) : activeMessages.length === 0 ? (
              <div className="pt-20 text-center text-muted-foreground">
                <MessageSquare className="mx-auto mb-4 h-12 w-12" />
                <p>Start a conversation with your AI compliance assistant</p>
                <p className="mt-2 text-sm">
                  Ask questions about compliance, policies, or evidence collection
                </p>
              </div>
            ) : (
              <>
                {activeMessages.map((message) => (
                  <ChatMessage 
                    key={message.id} 
                    message={message} 
                    onActionClick={handleActionClick}
                  />
                ))}
                {typingUsers.length > 0 && <TypingIndicator />}
              </>
            )}
          </div>

          <ChatInput onSendMessage={handleSendMessage} />
        </div>
      ) : (
        <div className="flex flex-1 items-center justify-center bg-muted/20">
          <div className="text-center">
            <MessageSquare className="mx-auto mb-4 h-16 w-16 text-muted-foreground" />
            <h2 className="mb-2 text-xl font-semibold">Welcome to ruleIQ AI Assistant</h2>
            <p className="mb-4 text-muted-foreground">
              Select a conversation or start a new one to begin
            </p>
            <Button
              onClick={handleNewConversation}
              className="bg-gold text-navy hover:bg-gold-dark"
            >
              <Plus className="mr-2 h-4 w-4" />
              Start New Conversation
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
