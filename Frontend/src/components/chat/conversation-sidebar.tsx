"use client"

import { useState } from "react"
import { format, isToday, isYesterday, isThisWeek } from "date-fns"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Plus, Search, MoreHorizontal, Pin, PinOff, Edit, Trash2, MessageSquare, Tag } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import type { ChatConversation } from "@/types/api"

interface ConversationSidebarProps {
  conversations: ChatConversation[]
  activeConversationId?: string
  onSelectConversation: (conversationId: string) => void
  onCreateConversation: () => void
  onUpdateConversation: (conversationId: string, data: Partial<ChatConversation>) => void
  onDeleteConversation: (conversationId: string) => void
  onPinConversation: (conversationId: string, pinned: boolean) => void
}

export function ConversationSidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onCreateConversation,
  onUpdateConversation,
  onDeleteConversation,
  onPinConversation,
}: ConversationSidebarProps) {
  const { toast } = useToast()
  const [searchQuery, setSearchQuery] = useState("")
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState("")

  const filteredConversations = conversations.filter((conv) =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const groupedConversations = {
    pinned: filteredConversations.filter((conv) => conv.is_pinned),
    today: filteredConversations.filter((conv) => !conv.is_pinned && isToday(new Date(conv.updated_at))),
    yesterday: filteredConversations.filter((conv) => !conv.is_pinned && isYesterday(new Date(conv.updated_at))),
    thisWeek: filteredConversations.filter(
      (conv) =>
        !conv.is_pinned &&
        !isToday(new Date(conv.updated_at)) &&
        !isYesterday(new Date(conv.updated_at)) &&
        isThisWeek(new Date(conv.updated_at)),
    ),
    older: filteredConversations.filter((conv) => !conv.is_pinned && !isThisWeek(new Date(conv.updated_at))),
  }

  const handleEditStart = (conversation: ChatConversation) => {
    setEditingId(conversation.id)
    setEditTitle(conversation.title)
  }

  const handleEditSave = (conversationId: string) => {
    if (editTitle.trim() && editTitle !== conversations.find((c) => c.id === conversationId)?.title) {
      onUpdateConversation(conversationId, { title: editTitle.trim() })
      toast({
        title: "Conversation renamed",
        description: "The conversation title has been updated.",
      })
    }
    setEditingId(null)
    setEditTitle("")
  }

  const handleEditCancel = () => {
    setEditingId(null)
    setEditTitle("")
  }

  const formatDate = (date: string) => {
    const d = new Date(date)
    if (isToday(d)) return "Today"
    if (isYesterday(d)) return "Yesterday"
    return format(d, "MMM d")
  }

  const renderConversationItem = (conversation: ChatConversation) => {
    const isActive = conversation.id === activeConversationId
    const isEditing = editingId === conversation.id

    return (
      <div
        key={conversation.id}
        className={`group relative p-3 rounded-lg cursor-pointer transition-colors ${
          isActive
            ? "bg-blue-100 dark:bg-blue-900 border border-blue-200 dark:border-blue-800"
            : "hover:bg-gray-100 dark:hover:bg-gray-800"
        }`}
        onClick={() => !isEditing && onSelectConversation(conversation.id)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            {isEditing ? (
              <div className="space-y-2" onClick={(e) => e.stopPropagation()}>
                <Input
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleEditSave(conversation.id)
                    if (e.key === "Escape") handleEditCancel()
                  }}
                  className="text-sm"
                  autoFocus
                />
                <div className="flex space-x-1">
                  <Button size="sm" onClick={() => handleEditSave(conversation.id)}>
                    Save
                  </Button>
                  <Button size="sm" variant="outline" onClick={handleEditCancel}>
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <>
                <div className="flex items-center space-x-2">
                  <h3 className="font-medium text-sm truncate">{conversation.title}</h3>
                  {conversation.is_pinned && <Pin className="h-3 w-3 text-blue-500 flex-shrink-0" />}
                </div>
                {conversation.last_message && (
                  <p className="text-xs text-gray-500 truncate mt-1">{conversation.last_message}</p>
                )}
                <div className="flex items-center justify-between mt-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-400">{formatDate(conversation.updated_at)}</span>
                    {conversation.message_count > 0 && (
                      <Badge variant="outline" className="text-xs">
                        {conversation.message_count}
                      </Badge>
                    )}
                  </div>
                  {conversation.tags && conversation.tags.length > 0 && (
                    <div className="flex items-center space-x-1">
                      <Tag className="h-3 w-3 text-gray-400" />
                      <span className="text-xs text-gray-400">{conversation.tags.length}</span>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>

          {!isEditing && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={(e) => e.stopPropagation()}
                >
                  <MoreHorizontal className="h-3 w-3" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => onPinConversation(conversation.id, !conversation.is_pinned)}>
                  {conversation.is_pinned ? (
                    <>
                      <PinOff className="h-4 w-4 mr-2" />
                      Unpin
                    </>
                  ) : (
                    <>
                      <Pin className="h-4 w-4 mr-2" />
                      Pin
                    </>
                  )}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleEditStart(conversation)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Rename
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => onDeleteConversation(conversation.id)} className="text-red-600">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>
    )
  }

  const renderConversationGroup = (title: string, conversations: ChatConversation[]) => {
    if (conversations.length === 0) return null

    return (
      <div className="space-y-2">
        <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider px-3">{title}</h4>
        <div className="space-y-1">{conversations.map(renderConversationItem)}</div>
      </div>
    )
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center space-x-2">
            <MessageSquare className="h-5 w-5" />
            <span>Conversations</span>
          </CardTitle>
          <Button size="sm" onClick={onCreateConversation}>
            <Plus className="h-4 w-4" />
          </Button>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto space-y-6">
        {filteredConversations.length === 0 ? (
          <div className="text-center py-8">
            <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">{searchQuery ? "No conversations found" : "No conversations yet"}</p>
            {!searchQuery && (
              <Button size="sm" onClick={onCreateConversation} className="mt-2">
                Start your first conversation
              </Button>
            )}
          </div>
        ) : (
          <>
            {renderConversationGroup("Pinned", groupedConversations.pinned)}
            {renderConversationGroup("Today", groupedConversations.today)}
            {renderConversationGroup("Yesterday", groupedConversations.yesterday)}
            {renderConversationGroup("This Week", groupedConversations.thisWeek)}
            {renderConversationGroup("Older", groupedConversations.older)}
          </>
        )}
      </CardContent>
    </Card>
  )
}
