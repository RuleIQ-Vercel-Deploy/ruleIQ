"use client"

import { useState, useEffect, useRef } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { ConversationSidebar } from "@/components/chat/conversation-sidebar"
import { ChatMessageComponent } from "@/components/chat/chat-message"
import { MessageInput } from "@/components/chat/message-input"
import { Settings, Download, Share, MoreHorizontal, Bot, Loader2, AlertCircle, RefreshCw } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import type { ChatConversation, ChatMessage, ChatSettings } from "@/types/api"

// Mock data - replace with actual API calls
const mockConversations: ChatConversation[] = [
  {
    id: "1",
    title: "GDPR Compliance Questions",
    created_at: "2024-01-15T10:00:00Z",
    updated_at: "2024-01-20T14:30:00Z",
    message_count: 12,
    last_message: "Thank you for the detailed explanation about data retention policies.",
    is_pinned: true,
    tags: ["GDPR", "Data Protection"],
  },
  {
    id: "2",
    title: "SOC 2 Assessment Help",
    created_at: "2024-01-18T09:15:00Z",
    updated_at: "2024-01-19T16:45:00Z",
    message_count: 8,
    last_message: "Can you help me understand the access control requirements?",
    tags: ["SOC 2", "Security"],
  },
  {
    id: "3",
    title: "ISO 27001 Implementation",
    created_at: "2024-01-10T11:30:00Z",
    updated_at: "2024-01-18T13:20:00Z",
    message_count: 15,
    last_message: "What are the key documentation requirements for ISO 27001?",
    tags: ["ISO 27001", "Implementation"],
  },
]

const mockMessages: ChatMessage[] = [
  {
    id: "1",
    conversation_id: "1",
    content: "Hi! I need help understanding GDPR data retention requirements for our customer database.",
    role: "user",
    created_at: "2024-01-20T14:00:00Z",
  },
  {
    id: "2",
    conversation_id: "1",
    content:
      "I'd be happy to help you understand GDPR data retention requirements. Under GDPR, personal data should only be kept for as long as necessary for the purposes for which it was collected. Here are the key principles:\n\n1. **Purpose Limitation**: Data should only be retained for the specific, explicit, and legitimate purposes for which it was collected.\n\n2. **Storage Limitation**: Personal data should be kept in a form that permits identification of data subjects for no longer than necessary.\n\n3. **Documentation**: You must document your retention periods and the legal basis for retention.\n\nFor customer databases specifically, consider:\n- Active customer relationships\n- Legal obligations (tax records, etc.)\n- Legitimate interests (fraud prevention)\n- Consent-based processing\n\nWhat type of customer data are you primarily concerned about?",
    role: "assistant",
    created_at: "2024-01-20T14:01:00Z",
    metadata: {
      confidence: 0.95,
      sources: ["GDPR Article 5", "GDPR Article 17", "ICO Guidance"],
      thinking:
        "The user is asking about GDPR data retention, which is a fundamental principle under Article 5. I should provide a comprehensive overview covering the key principles and practical considerations for customer databases.",
    },
  },
  {
    id: "3",
    conversation_id: "1",
    content:
      "We store customer contact information, purchase history, and support tickets. Some customers haven't made purchases in over 3 years. Should we delete their data?",
    role: "user",
    created_at: "2024-01-20T14:05:00Z",
  },
  {
    id: "4",
    conversation_id: "1",
    content:
      'Great question! For inactive customers (3+ years without purchases), you should evaluate each data category:\n\n**Customer Contact Information:**\n- If no legitimate business need, consider deletion\n- Check if you have consent for marketing communications\n- Consider "right to be forgotten" requests\n\n**Purchase History:**\n- May need retention for:\n  - Tax/accounting purposes (typically 6-7 years)\n  - Warranty obligations\n  - Fraud prevention (legitimate interest)\n- Can be anonymized after legal requirements are met\n\n**Support Tickets:**\n- Retain for service improvement and legal protection\n- Consider anonymizing after 2-3 years\n- Delete if no ongoing issues\n\n**Recommendations:**\n1. Implement automated retention policies\n2. Regular data audits (annually)\n3. Customer re-engagement campaigns before deletion\n4. Clear privacy policy stating retention periods\n\nWould you like help creating a retention schedule for these data types?',
    role: "assistant",
    created_at: "2024-01-20T14:07:00Z",
    metadata: {
      confidence: 0.92,
      sources: ["GDPR Article 6", "GDPR Article 17", "Data Protection Authorities"],
    },
  },
]

const mockSettings: ChatSettings = {
  model: "gpt-4",
  temperature: 0.7,
  max_tokens: 2000,
  auto_save: true,
  show_thinking: false,
  enable_web_search: true,
  enable_code_execution: false,
}

export function ChatInterface() {
  const { conversationId } = useParams<{ conversationId?: string }>()
  const navigate = useNavigate()
  const { toast } = useToast()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const [conversations, setConversations] = useState<ChatConversation[]>(mockConversations)
  const [messages, setMessages] = useState<ChatMessage[]>(mockMessages)
  const [settings, setSettings] = useState<ChatSettings>(mockSettings)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  const activeConversation = conversations.find((c) => c.id === conversationId)
  const conversationMessages = messages.filter((m) => m.conversation_id === conversationId)

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [conversationMessages])

  useEffect(() => {
    // Load conversation data when conversationId changes
    if (conversationId) {
      // loadConversationData(conversationId)
    }
  }, [conversationId])

  const handleCreateConversation = async () => {
    try {
      const newConversation: ChatConversation = {
        id: `conv_${Date.now()}`,
        title: "New Conversation",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_count: 0,
      }
      setConversations((prev) => [newConversation, ...prev])
      navigate(`/app/chat/${newConversation.id}`)
    } catch (error) {
      toast({
        title: "Failed to create conversation",
        description: "Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleUpdateConversation = async (id: string, data: Partial<ChatConversation>) => {
    try {
      setConversations((prev) =>
        prev.map((conv) => (conv.id === id ? { ...conv, ...data, updated_at: new Date().toISOString() } : conv)),
      )
    } catch (error) {
      toast({
        title: "Failed to update conversation",
        description: "Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleDeleteConversation = async (id: string) => {
    try {
      setConversations((prev) => prev.filter((conv) => conv.id !== id))
      if (conversationId === id) {
        navigate("/app/chat")
      }
      toast({
        title: "Conversation deleted",
        description: "The conversation has been removed.",
      })
    } catch (error) {
      toast({
        title: "Failed to delete conversation",
        description: "Please try again.",
        variant: "destructive",
      })
    }
  }

  const handlePinConversation = async (id: string, pinned: boolean) => {
    try {
      setConversations((prev) => prev.map((conv) => (conv.id === id ? { ...conv, is_pinned: pinned } : conv)))
      toast({
        title: pinned ? "Conversation pinned" : "Conversation unpinned",
        description: pinned ? "The conversation has been pinned to the top." : "The conversation has been unpinned.",
      })
    } catch (error) {
      toast({
        title: "Failed to update conversation",
        description: "Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleSendMessage = async (content: string, files?: File[]) => {
    if (!conversationId) return

    setLoading(true)
    setError(null)

    try {
      // Add user message
      const userMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        conversation_id: conversationId,
        content,
        role: "user",
        created_at: new Date().toISOString(),
        metadata: files
          ? {
              files: files.map((f) => ({
                id: `file_${Date.now()}`,
                name: f.name,
                size: f.size,
                type: f.type,
                url: URL.createObjectURL(f),
                uploaded_at: new Date().toISOString(),
              })),
            }
          : undefined,
      }

      setMessages((prev) => [...prev, userMessage])

      // Simulate AI response
      setTimeout(() => {
        const assistantMessage: ChatMessage = {
          id: `msg_${Date.now() + 1}`,
          conversation_id: conversationId,
          content:
            "I understand your question about compliance requirements. Let me provide you with a detailed response based on the latest regulations and best practices...",
          role: "assistant",
          created_at: new Date().toISOString(),
          metadata: {
            confidence: 0.88,
            thinking:
              "The user is asking about compliance requirements. I should provide comprehensive guidance while being careful to note that this is general information and they should consult with legal experts for specific situations.",
          },
        }

        setMessages((prev) => [...prev, assistantMessage])
        setLoading(false)

        // Update conversation
        setConversations((prev) =>
          prev.map((conv) =>
            conv.id === conversationId
              ? {
                  ...conv,
                  message_count: conv.message_count + 2,
                  last_message: content.substring(0, 100) + (content.length > 100 ? "..." : ""),
                  updated_at: new Date().toISOString(),
                }
              : conv,
          ),
        )
      }, 2000)
    } catch (error) {
      setError("Failed to send message. Please try again.")
      setLoading(false)
    }
  }

  const handleEditMessage = async (messageId: string, content: string) => {
    try {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId ? { ...msg, content, is_edited: true, edited_at: new Date().toISOString() } : msg,
        ),
      )
      toast({
        title: "Message updated",
        description: "Your message has been edited.",
      })
    } catch (error) {
      toast({
        title: "Failed to edit message",
        description: "Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleDeleteMessage = async (messageId: string) => {
    try {
      setMessages((prev) => prev.filter((msg) => msg.id !== messageId))
      toast({
        title: "Message deleted",
        description: "The message has been removed.",
      })
    } catch (error) {
      toast({
        title: "Failed to delete message",
        description: "Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleReaction = async (messageId: string, emoji: string) => {
    try {
      setMessages((prev) =>
        prev.map((msg) => {
          if (msg.id === messageId) {
            const reactions = msg.reactions || []
            const existingReaction = reactions.find((r) => r.emoji === emoji)

            if (existingReaction) {
              // Toggle reaction
              return {
                ...msg,
                reactions: reactions
                  .map((r) => (r.emoji === emoji ? { ...r, count: r.count > 0 ? r.count - 1 : 0 } : r))
                  .filter((r) => r.count > 0),
              }
            } else {
              // Add new reaction
              return {
                ...msg,
                reactions: [...reactions, { emoji, count: 1, users: ["current_user"] }],
              }
            }
          }
          return msg
        }),
      )
    } catch (error) {
      toast({
        title: "Failed to add reaction",
        description: "Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleExportConversation = async (format: "json" | "pdf" | "txt") => {
    try {
      // Simulate export
      toast({
        title: "Export started",
        description: `Exporting conversation as ${format.toUpperCase()}...`,
      })
    } catch (error) {
      toast({
        title: "Export failed",
        description: "Please try again.",
        variant: "destructive",
      })
    }
  }

  if (!conversationId) {
    return (
      <div className="h-full flex">
        <div className="w-80 border-r">
          <ConversationSidebar
            conversations={conversations}
            onSelectConversation={(id) => navigate(`/app/chat/${id}`)}
            onCreateConversation={handleCreateConversation}
            onUpdateConversation={handleUpdateConversation}
            onDeleteConversation={handleDeleteConversation}
            onPinConversation={handlePinConversation}
          />
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-4">
            <Bot className="h-16 w-16 text-gray-400 mx-auto" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Welcome to AI Assistant</h2>
              <p className="text-gray-600 dark:text-gray-300 mt-2">
                Select a conversation or start a new one to begin chatting.
              </p>
            </div>
            <Button onClick={handleCreateConversation}>Start New Conversation</Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex">
      {/* Sidebar */}
      <div className={`border-r transition-all duration-300 ${sidebarCollapsed ? "w-0" : "w-80"}`}>
        {!sidebarCollapsed && (
          <ConversationSidebar
            conversations={conversations}
            activeConversationId={conversationId}
            onSelectConversation={(id) => navigate(`/app/chat/${id}`)}
            onCreateConversation={handleCreateConversation}
            onUpdateConversation={handleUpdateConversation}
            onDeleteConversation={handleDeleteConversation}
            onPinConversation={handlePinConversation}
          />
        )}
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Button size="sm" variant="ghost" onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
                ☰
              </Button>
              <div>
                <h1 className="font-semibold text-lg">{activeConversation?.title}</h1>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <span>{conversationMessages.length} messages</span>
                  {activeConversation?.tags && (
                    <>
                      <Separator orientation="vertical" className="h-4" />
                      <div className="flex space-x-1">
                        {activeConversation.tags.map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button size="sm" variant="outline">
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => handleExportConversation("txt")}>Export as Text</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleExportConversation("json")}>Export as JSON</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleExportConversation("pdf")}>Export as PDF</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button size="sm" variant="ghost">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem>
                    <Share className="h-4 w-4 mr-2" />
                    Share Conversation
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Settings className="h-4 w-4 mr-2" />
                    Chat Settings
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
          {error && (
            <div className="flex items-center space-x-2 p-3 bg-red-50 dark:bg-red-900 rounded-lg">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <span className="text-red-600 text-sm">{error}</span>
              <Button size="sm" variant="ghost" onClick={() => setError(null)}>
                <RefreshCw className="h-3 w-3" />
              </Button>
            </div>
          )}

          {conversationMessages.map((message) => (
            <ChatMessageComponent
              key={message.id}
              message={message}
              onEdit={handleEditMessage}
              onDelete={handleDeleteMessage}
              onReaction={handleReaction}
              showThinking={settings.show_thinking}
            />
          ))}

          {loading && (
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                <Bot className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="flex items-center space-x-2 bg-white dark:bg-gray-800 border rounded-lg px-4 py-3">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm text-gray-600 dark:text-gray-300">AI is thinking...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="border-t px-6 py-4">
          <MessageInput
            onSendMessage={handleSendMessage}
            disabled={loading}
            placeholder="Ask me anything about compliance..."
          />
        </div>
      </div>
    </div>
  )
}
