"use client"

import { Paperclip, Send } from "lucide-react"
import { useState, type KeyboardEvent } from "react"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useTypingIndicator } from "@/lib/hooks/use-typing-indicator"

interface ChatInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
}

export function ChatInput({ onSendMessage, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState("")
  const { handleTypingStart, handleTypingStop } = useTypingIndicator()

  const handleSend = () => {
    if (message.trim() && !disabled) {
      handleTypingStop()
      onSendMessage(message.trim())
      setMessage("")
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="p-4 border-t">
      <div className="relative">
        <Textarea
          placeholder="Ask about compliance, policies, or evidence..."
          value={message}
          onChange={(e) => {
            setMessage(e.target.value)
            handleTypingStart(e.target.value)
          }}
          onKeyDown={handleKeyDown}
          onBlur={handleTypingStop}
          disabled={disabled}
          className="w-full resize-none rounded-lg border bg-muted/50 p-3 pr-24 placeholder:text-muted-foreground focus:ring-2 focus:ring-gold"
          rows={3}
        />
        <div className="absolute bottom-2.5 right-3 flex items-center gap-2">
          <Button 
            variant="ghost" 
            size="icon" 
            className="text-muted-foreground hover:text-foreground"
            disabled={disabled}
          >
            <Paperclip className="h-5 w-5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            disabled={!message.trim() || disabled}
            onClick={handleSend}
            className={`
              ${message.trim() && !disabled ? "text-gold hover:bg-gold/10" : "text-muted-foreground"}
            `}
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  )
}
