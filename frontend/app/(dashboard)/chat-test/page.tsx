'use client';

import { useState } from 'react';
import { ChatInput } from '@/components/chat/chat-input';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

export default function ChatTestPage() {
  const [messages, setMessages] = useState<string[]>([]);
  
  const handleSendMessage = (message: string) => {
    setMessages([...messages, message]);
    console.log('Message sent:', message);
  };

  return (
    <div className="flex h-screen flex-col">
      <div className="flex-1 overflow-y-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Chat Test Page</h1>
        <p className="mb-4">This is a test page to verify the ChatInput component renders correctly.</p>
        
        <div className="mb-4">
          <Button className="bg-gold text-navy hover:bg-gold-dark">
            <Plus className="mr-2 h-4 w-4" />
            Test Button (Should be visible)
          </Button>
        </div>
        
        <div className="space-y-2">
          {messages.map((msg, idx) => (
            <div key={idx} className="p-2 bg-gray-100 rounded">
              Message {idx + 1}: {msg}
            </div>
          ))}
        </div>
      </div>
      
      <div className="border-t">
        <h2 className="p-4 font-semibold">Below should be the chat input:</h2>
        <ChatInput onSendMessage={handleSendMessage} />
      </div>
    </div>
  );
}