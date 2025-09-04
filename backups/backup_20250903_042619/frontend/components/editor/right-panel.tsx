'use client';

import { Clock, MessageSquare, Info } from 'lucide-react';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { editorData } from '@/lib/data/editor-data';

const { metadata, versions, comments } = editorData;

const VersionHistory = () => (
  <div className="space-y-4">
    {versions.map((version) => (
      <div key={version.id} className="flex items-start gap-4">
        <Avatar className="h-8 w-8 border">
          <AvatarFallback>{version.author.charAt(0)}</AvatarFallback>
        </Avatar>
        <div className="text-sm">
          <p className="font-semibold">{version.summary}</p>
          <p className="text-gray-400">
            By {version.author} on {new Date(version.timestamp).toLocaleDateString()}
          </p>
        </div>
        <Button variant="ghost" size="sm" className="ml-auto">
          Revert
        </Button>
      </div>
    ))}
  </div>
);

const CommentsThread = () => (
  <div className="space-y-6">
    {comments.map((comment) => (
      <div key={comment.id}>
        <div className="flex items-start gap-3">
          <Avatar className="h-8 w-8 border">
            <AvatarImage src={comment.avatar || '/placeholder.svg'} alt={comment.author} />
            <AvatarFallback>{comment.author.charAt(0)}</AvatarFallback>
          </Avatar>
          <div className="w-full rounded-lg border bg-gray-800/50 p-3 text-sm">
            <div className="flex items-center justify-between">
              <p className="text-eggshell-white font-semibold">{comment.author}</p>
              <p className="text-xs text-gray-400">
                {new Date(comment.timestamp).toLocaleDateString()}
              </p>
            </div>
            <p className="mt-1 text-gray-300">{comment.text}</p>
          </div>
        </div>
        {comment.replies.map((reply) => (
          <div key={reply.id} className="ml-8 mt-3 flex items-start gap-3">
            <Avatar className="h-8 w-8 border">
              <AvatarImage src={reply.avatar || '/placeholder.svg'} alt={reply.author} />
              <AvatarFallback>{reply.author.charAt(0)}</AvatarFallback>
            </Avatar>
            <div className="w-full rounded-lg border bg-gray-800/50 p-3 text-sm">
              <div className="flex items-center justify-between">
                <p className="text-eggshell-white font-semibold">{reply.author}</p>
                <p className="text-xs text-gray-400">
                  {new Date(reply.timestamp).toLocaleDateString()}
                </p>
              </div>
              <p className="mt-1 text-gray-300">{reply.text}</p>
            </div>
          </div>
        ))}
      </div>
    ))}
    <div className="mt-4 flex flex-col gap-2">
      <Textarea
        placeholder="Add a comment..."
        className="text-eggshell-white border-border bg-gray-800"
      />
      <Button className="self-end">Comment</Button>
    </div>
  </div>
);

const MetadataDisplay = () => (
  <div className="space-y-3 text-sm">
    <div className="flex justify-between">
      <span className="text-gray-400">Author:</span>
      <span className="text-eggshell-white font-medium">{metadata.author}</span>
    </div>
    <div className="flex justify-between">
      <span className="text-gray-400">Created:</span>
      <span className="text-eggshell-white font-medium">
        {new Date(metadata.createdAt).toLocaleDateString()}
      </span>
    </div>
    <div className="flex justify-between">
      <span className="text-gray-400">Last Modified:</span>
      <span className="text-eggshell-white font-medium">
        {new Date(metadata.lastModified).toLocaleDateString()}
      </span>
    </div>
    <div className="flex items-center justify-between">
      <span className="text-gray-400">Status:</span>
      <span className="text-eggshell-white font-medium">{metadata.status}</span>
    </div>
  </div>
);

export function RightPanel() {
  return (
    <Card className="text-eggshell-white h-full w-full max-w-sm flex-col border-l border-border bg-background">
      <Tabs defaultValue="comments" className="flex h-full flex-col">
        <TabsList className="grid w-full grid-cols-3 bg-gray-900/50">
          <TabsTrigger value="history">
            <Clock className="mr-2 h-4 w-4" /> History
          </TabsTrigger>
          <TabsTrigger value="comments">
            <MessageSquare className="mr-2 h-4 w-4" /> Comments
          </TabsTrigger>
          <TabsTrigger value="metadata">
            <Info className="mr-2 h-4 w-4" /> Details
          </TabsTrigger>
        </TabsList>
        <div className="flex-grow overflow-y-auto p-4">
          <TabsContent value="history">
            <VersionHistory />
          </TabsContent>
          <TabsContent value="comments">
            <CommentsThread />
          </TabsContent>
          <TabsContent value="metadata">
            <MetadataDisplay />
          </TabsContent>
        </div>
      </Tabs>
    </Card>
  );
}
