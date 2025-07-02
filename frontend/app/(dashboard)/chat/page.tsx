"use client"

import { Plus, MessageSquare } from "lucide-react"
import { useEffect } from "react"

import { ChatHeader } from "@/components/chat/chat-header"
import { ChatInput } from "@/components/chat/chat-input"
import { ChatMessage } from "@/components/chat/chat-message"
import { ConversationSidebar } from "@/components/chat/conversation-sidebar"
import { TypingIndicator } from "@/components/chat/typing-indicator"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useChatStore } from "@/lib/stores/chat.store"

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
  } = useChatStore()

  const activeConversation = conversations.find(c => c.id === activeConversationId)
  const activeMessages = activeConversationId ? messages[activeConversationId] || [] : []

  useEffect(() => {
    loadConversations()
    
    // Cleanup on unmount
    return () => {
      useChatStore.getState().disconnectWebSocket()
    }
  }, [])

  const handleNewConversation = async () => {
    await createConversation("New Conversation")
  }

  const handleSendMessage = async (message: string) => {
    await sendMessage(message)
  }

  if (isLoadingConversations) {
    return (
      <div className="flex h-[calc(100vh-4rem)]">
        <div className="w-80 border-r p-4 space-y-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center text-muted-foreground">
            <MessageSquare className="h-12 w-12 mx-auto mb-4" />
            <p>Loading conversations...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Conversation Sidebar */}
      <div className="w-80 border-r flex flex-col">
        <div className="p-4 border-b">
          <Button 
            onClick={handleNewConversation} 
            className="w-full bg-gold hover:bg-gold-dark text-navy"
          >
            <Plus className="h-4 w-4 mr-2" />
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
            title={activeConversation.title || "AI Assistant"} 
            isConnected={isConnected}
          />
          
          {error && (
            <Alert variant="destructive" className="m-4">
              <AlertDescription className="flex items-center justify-between">
                {error}
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={clearError}
                >
                  Dismiss
                </Button>
              </AlertDescription>
            </Alert>
          )}

          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {isLoadingMessages ? (
              <div className="space-y-4">
                <Skeleton className="h-20 w-3/4" />
                <Skeleton className="h-20 w-3/4 ml-auto" />
                <Skeleton className="h-20 w-3/4" />
              </div>
            ) : activeMessages.length === 0 ? (
              <div className="text-center text-muted-foreground pt-20">
                <MessageSquare className="h-12 w-12 mx-auto mb-4" />
                <p>Start a conversation with your AI compliance assistant</p>
                <p className="text-sm mt-2">Ask questions about compliance, policies, or evidence collection</p>
              </div>
            ) : (
              <>
                {activeMessages.map((message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}
                {typingUsers.length > 0 && <TypingIndicator />}
              </>
            )}
          </div>
          
          <ChatInput onSendMessage={handleSendMessage} />
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center bg-muted/20">
          <div className="text-center">
            <MessageSquare className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
            <h2 className="text-xl font-semibold mb-2">Welcome to ruleIQ AI Assistant</h2>
            <p className="text-muted-foreground mb-4">
              Select a conversation or start a new one to begin
            </p>
            <Button 
              onClick={handleNewConversation}
              className="bg-gold hover:bg-gold-dark text-navy"
            >
              <Plus className="h-4 w-4 mr-2" />
              Start New Conversation
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}