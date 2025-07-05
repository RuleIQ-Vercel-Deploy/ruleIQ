import { User, Copy, CheckCircle } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

import type { ChatMessage } from "@/types/api"

interface ChatMessageProps {
  message: ChatMessage
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user"
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Parse message content for structured responses
  const renderMessageContent = () => {
    const {content} = message
    
    // Check if message contains JSON (for structured responses)
    if (content.startsWith('{') || content.startsWith('[')) {
      try {
        const parsed = JSON.parse(content)
        return (
          <pre className="text-sm whitespace-pre-wrap font-mono">
            {JSON.stringify(parsed, null, 2)}
          </pre>
        )
      } catch {
        // Not valid JSON, render as text
      }
    }
    
    // Render as markdown-like text
    return (
      <div className="text-sm space-y-2">
        {content.split('\n\n').map((paragraph, idx) => (
          <p key={idx}>{paragraph}</p>
        ))}
      </div>
    )
  }

  return (
    <div className={cn(
      "flex items-start gap-4",
      isUser && "flex-row-reverse"
    )}>
      {/* Avatar */}
      <div className={cn(
        "flex h-8 w-8 items-center justify-center rounded-full flex-shrink-0",
        isUser ? "bg-gold/20" : "bg-navy"
      )}>
        {isUser ? (
          <User className="h-4 w-4 text-gold" />
        ) : (
          <span className="text-gold font-bold text-sm">IQ</span>
        )}
      </div>

      {/* Message Content */}
      <div className={cn(
        "flex flex-col gap-2 flex-1 max-w-[70%]",
        isUser ? "items-end" : "items-start"
      )}>
        <div
          className={cn(
            "rounded-xl p-4 relative group",
            isUser
              ? "bg-gold/20 text-foreground rounded-tr-none"
              : "bg-muted text-foreground rounded-tl-none"
          )}
        >
          {renderMessageContent()}
          
          {/* Copy button for AI messages */}
          {!isUser && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-2 right-2 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={handleCopy}
            >
              {copied ? (
                <CheckCircle className="h-3 w-3 text-success" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </Button>
          )}
        </div>

        {/* Timestamp */}
        <span className="text-xs text-muted-foreground">
          {new Date(message.created_at).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </span>

        {/* Action suggestions for AI messages */}
        {!isUser && message.metadata?.sources && message.metadata.sources.length > 0 && (
          <div className="flex flex-wrap gap-2 pt-2">
            <span className="text-xs text-muted-foreground">Sources:</span>
            {message.metadata.sources.map((source: string, index: number) => (
              <span key={index} className="text-xs text-gold">
                {source}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
