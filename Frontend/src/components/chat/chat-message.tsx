"use client"

import { useState } from "react"
import { format } from "date-fns"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Textarea } from "@/components/ui/textarea"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import {
  Bot,
  User,
  Copy,
  Edit,
  Trash2,
  MoreHorizontal,
  ThumbsUp,
  ThumbsDown,
  FileText,
  Code,
  Eye,
  EyeOff,
  Download,
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import type { ChatMessage, ChatFile } from "@/types/api"

interface ChatMessageProps {
  message: ChatMessage
  onEdit?: (messageId: string, content: string) => void
  onDelete?: (messageId: string) => void
  onReaction?: (messageId: string, emoji: string) => void
  showThinking?: boolean
}

export function ChatMessageComponent({
  message,
  onEdit,
  onDelete,
  onReaction,
  showThinking = false,
}: ChatMessageProps) {
  const { toast } = useToast()
  const [isEditing, setIsEditing] = useState(false)
  const [editContent, setEditContent] = useState(message.content)
  const [showThinkingContent, setShowThinkingContent] = useState(false)

  const isUser = message.role === "user"
  const isAssistant = message.role === "assistant"

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      toast({
        title: "Copied to clipboard",
        description: "Message content has been copied.",
      })
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Failed to copy message content.",
        variant: "destructive",
      })
    }
  }

  const handleEdit = () => {
    if (onEdit && editContent.trim() !== message.content) {
      onEdit(message.id, editContent.trim())
    }
    setIsEditing(false)
  }

  const handleReaction = (emoji: string) => {
    if (onReaction) {
      onReaction(message.id, emoji)
    }
  }

  const renderFiles = (files: ChatFile[]) => {
    return (
      <div className="mt-3 space-y-2">
        {files.map((file) => (
          <div key={file.id} className="flex items-center space-x-2 p-2 bg-gray-50 dark:bg-gray-800 rounded">
            <FileText className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium">{file.name}</span>
            <span className="text-xs text-gray-500">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
            <Button size="sm" variant="ghost" onClick={() => window.open(file.url, "_blank")}>
              <Download className="h-3 w-3" />
            </Button>
          </div>
        ))}
      </div>
    )
  }

  const renderCodeBlock = (content: string, language?: string) => {
    return (
      <div className="mt-3">
        <div className="flex items-center justify-between bg-gray-100 dark:bg-gray-800 px-3 py-2 rounded-t">
          <div className="flex items-center space-x-2">
            <Code className="h-4 w-4" />
            {language && <Badge variant="outline">{language}</Badge>}
          </div>
          <Button size="sm" variant="ghost" onClick={handleCopy}>
            <Copy className="h-3 w-3" />
          </Button>
        </div>
        <pre className="bg-gray-50 dark:bg-gray-900 p-3 rounded-b overflow-x-auto">
          <code className="text-sm">{content}</code>
        </pre>
      </div>
    )
  }

  const renderThinking = (thinking: string) => {
    if (!showThinking || !thinking) return null

    return (
      <div className="mt-3 border-l-4 border-blue-200 dark:border-blue-800 pl-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-blue-600 dark:text-blue-400">AI Thinking Process</span>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setShowThinkingContent(!showThinkingContent)}
            className="h-6 w-6 p-0"
          >
            {showThinkingContent ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
          </Button>
        </div>
        {showThinkingContent && (
          <div className="text-sm text-gray-600 dark:text-gray-400 bg-blue-50 dark:bg-blue-950 p-3 rounded">
            {thinking}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className={`flex space-x-3 ${isUser ? "flex-row-reverse space-x-reverse" : ""}`}>
      <Avatar className="h-8 w-8 flex-shrink-0">
        {isUser ? (
          <>
            <AvatarImage src="/placeholder-user.jpg" />
            <AvatarFallback>
              <User className="h-4 w-4" />
            </AvatarFallback>
          </>
        ) : (
          <AvatarFallback className="bg-blue-100 dark:bg-blue-900">
            <Bot className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          </AvatarFallback>
        )}
      </Avatar>

      <div className={`flex-1 max-w-3xl ${isUser ? "flex flex-col items-end" : ""}`}>
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser ? "bg-blue-600 text-white" : "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
          }`}
        >
          {isEditing ? (
            <div className="space-y-3">
              <Textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="min-h-[100px] resize-none"
              />
              <div className="flex space-x-2">
                <Button size="sm" onClick={handleEdit}>
                  Save
                </Button>
                <Button size="sm" variant="outline" onClick={() => setIsEditing(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <>
              <div className="prose prose-sm max-w-none dark:prose-invert">
                {message.message_type === "code" && message.metadata?.code_language
                  ? renderCodeBlock(message.content, message.metadata.code_language)
                  : message.content}
              </div>

              {message.metadata?.files && renderFiles(message.metadata.files)}
              {message.metadata?.thinking && renderThinking(message.metadata.thinking)}

              {message.metadata?.sources && message.metadata.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                  <div className="text-xs text-gray-500 mb-2">Sources:</div>
                  <div className="flex flex-wrap gap-1">
                    {message.metadata.sources.map((source, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {source}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {message.metadata?.confidence && (
                <div className="mt-2 text-xs text-gray-500">
                  Confidence: {Math.round(message.metadata.confidence * 100)}%
                </div>
              )}
            </>
          )}
        </div>

        <div className="flex items-center space-x-2 mt-2">
          <span className="text-xs text-gray-500">{format(new Date(message.created_at), "HH:mm")}</span>
          {message.is_edited && (
            <Badge variant="outline" className="text-xs">
              Edited
            </Badge>
          )}

          <div className="flex items-center space-x-1">
            {/* Reactions */}
            {message.reactions?.map((reaction) => (
              <Button
                key={reaction.emoji}
                size="sm"
                variant="ghost"
                className="h-6 px-2 text-xs"
                onClick={() => handleReaction(reaction.emoji)}
              >
                {reaction.emoji} {reaction.count}
              </Button>
            ))}

            {/* Quick reactions */}
            {isAssistant && (
              <>
                <Button size="sm" variant="ghost" className="h-6 w-6 p-0" onClick={() => handleReaction("👍")}>
                  <ThumbsUp className="h-3 w-3" />
                </Button>
                <Button size="sm" variant="ghost" className="h-6 w-6 p-0" onClick={() => handleReaction("👎")}>
                  <ThumbsDown className="h-3 w-3" />
                </Button>
              </>
            )}

            {/* Actions menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button size="sm" variant="ghost" className="h-6 w-6 p-0">
                  <MoreHorizontal className="h-3 w-3" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleCopy}>
                  <Copy className="h-4 w-4 mr-2" />
                  Copy
                </DropdownMenuItem>
                {isUser && onEdit && (
                  <DropdownMenuItem onClick={() => setIsEditing(true)}>
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </DropdownMenuItem>
                )}
                {onDelete && (
                  <DropdownMenuItem onClick={() => onDelete(message.id)} className="text-red-600">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </div>
  )
}
