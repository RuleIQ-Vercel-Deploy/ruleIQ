"use client"

import TextAlign from "@tiptap/extension-text-align"
import Underline from "@tiptap/extension-underline"
import { useEditor, EditorContent } from "@tiptap/react"
import StarterKit from "@tiptap/starter-kit"

import { ActionBar } from "@/components/editor/action-bar"
import { DocumentOutline } from "@/components/editor/document-outline"
import { RightPanel } from "@/components/editor/right-panel"
import { Toolbar } from "@/components/editor/toolbar"
import { editorData } from "@/lib/data/editor-data"

export default function EditorPage() {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Underline,
      TextAlign.configure({
        types: ["heading", "paragraph"],
      }),
    ],
    content: editorData.initialContent,
    editorProps: {
      attributes: {
        class: "prose dark:prose-invert max-w-none",
      },
    },
  })

  return (
    <div className="flex h-screen w-full bg-background text-eggshell-white">
      <DocumentOutline editor={editor} />
      <div className="flex flex-1 flex-col">
        <Toolbar editor={editor} />
        <main className="flex-1 overflow-y-auto">
          <EditorContent editor={editor} />
        </main>
        <ActionBar />
      </div>
      <RightPanel />
    </div>
  )
}
