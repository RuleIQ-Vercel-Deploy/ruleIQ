'use client';

import { ChevronLeft, MessageSquare, Trash2 } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

import type { ChatConversation } from '@/types/api';

interface ConversationSidebarProps {
  conversations: ChatConversation[];
  activeConversationId: string | null;
  onSelectConversation: (conversationId: string) => void;
  onDeleteConversation?: (conversationId: string) => void;
}

export function ConversationSidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onDeleteConversation,
}: ConversationSidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div
      className={cn(
        'relative flex flex-col border-r bg-background transition-all duration-300',
        isCollapsed ? 'w-16' : 'w-80',
      )}
    >
      <div className="flex items-center justify-between border-b p-4">
        {!isCollapsed && <h2 className="text-lg font-semibold">Conversations</h2>}
        <Button variant="ghost" size="icon" onClick={() => setIsCollapsed(!isCollapsed)}>
          <ChevronLeft
            className={cn('h-5 w-5 transition-transform', isCollapsed && 'rotate-180')}
          />
        </Button>
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto p-2">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className={cn(
              'group flex items-center gap-2 rounded-lg transition-colors',
              conv.id === activeConversationId ? 'bg-muted' : 'hover:bg-muted/50',
            )}
          >
            <Button
              variant="ghost"
              className={cn(
                'h-auto flex-1 justify-start gap-3 px-3 py-2 text-left',
                isCollapsed ? 'justify-center px-2' : '',
              )}
              onClick={() => onSelectConversation(conv.id)}
            >
              <MessageSquare className="h-4 w-4 flex-shrink-0" />
              {!isCollapsed && (
                <div className="flex-1 overflow-hidden">
                  <p className="truncate font-medium">{conv.title || 'New Conversation'}</p>
                  <p className="truncate text-xs text-muted-foreground">
                    {new Date(conv.updated_at).toLocaleDateString()}
                  </p>
                </div>
              )}
            </Button>
            {!isCollapsed && onDeleteConversation && (
              <Button
                variant="ghost"
                size="icon"
                className="opacity-0 transition-opacity group-hover:opacity-100"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteConversation(conv.id);
                }}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        ))}
      </nav>
    </div>
  );
}
