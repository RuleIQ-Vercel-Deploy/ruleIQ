"use client"

import {
  Bold,
  Italic,
  Underline,
  Strikethrough,
  Heading1,
  Heading2,
  Heading3,
  List,
  ListOrdered,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
} from "lucide-react"

import { Toggle } from "@/components/ui/toggle"

import type { Editor } from "@tiptap/react"

interface ToolbarProps {
  editor: Editor | null
}

export function Toolbar({ editor }: ToolbarProps) {
  if (!editor) return null

  const formattingOptions = [
    { command: "toggleBold", icon: Bold, name: "Bold" },
    { command: "toggleItalic", icon: Italic, name: "Italic" },
    { command: "toggleUnderline", icon: Underline, name: "Underline" },
    { command: "toggleStrike", icon: Strikethrough, name: "Strikethrough" },
  ]

  const headingOptions = [
    { level: 1, icon: Heading1, name: "H1" },
    { level: 2, icon: Heading2, name: "H2" },
    { level: 3, icon: Heading3, name: "H3" },
  ]

  const listOptions = [
    { command: "toggleBulletList", icon: List, name: "Bullet List" },
    { command: "toggleOrderedList", icon: ListOrdered, name: "Ordered List" },
  ]

  const alignmentOptions = [
    { align: "left", icon: AlignLeft, name: "Left" },
    { align: "center", icon: AlignCenter, name: "Center" },
    { align: "right", icon: AlignRight, name: "Right" },
    { align: "justify", icon: AlignJustify, name: "Justify" },
  ]

  return (
    <div className="flex flex-wrap items-center gap-1 border-b border-border bg-background p-2">
      {formattingOptions.map((opt) => (
        <Toggle
          key={opt.name}
          size="sm"
          pressed={editor.isActive(opt.name.toLowerCase())}
          onPressedChange={() => {
            switch (opt.command) {
              case 'toggleBold': return editor.chain().focus().toggleBold().run()
              case 'toggleItalic': return editor.chain().focus().toggleItalic().run()
              case 'toggleUnderline': return editor.chain().focus().toggleUnderline().run()
              case 'toggleStrike': return editor.chain().focus().toggleStrike().run()
              default: return
            }
          }}
        >
          <opt.icon className="h-4 w-4" />
        </Toggle>
      ))}
      <div className="h-6 w-px bg-border mx-1" />
      {headingOptions.map((opt) => (
        <Toggle
          key={opt.name}
          size="sm"
          pressed={editor.isActive("heading", { level: opt.level })}
          onPressedChange={() => editor.chain().focus().toggleHeading({ level: opt.level as 1 | 2 | 3 }).run()}
        >
          <opt.icon className="h-4 w-4" />
        </Toggle>
      ))}
      <div className="h-6 w-px bg-border mx-1" />
      {listOptions.map((opt) => (
        <Toggle
          key={opt.name}
          size="sm"
          pressed={editor.isActive(opt.name.toLowerCase())}
          onPressedChange={() => {
            switch (opt.command) {
              case 'toggleBulletList': return editor.chain().focus().toggleBulletList().run()
              case 'toggleOrderedList': return editor.chain().focus().toggleOrderedList().run()
              default: return
            }
          }}
        >
          <opt.icon className="h-4 w-4" />
        </Toggle>
      ))}
      <div className="h-6 w-px bg-border mx-1" />
      {alignmentOptions.map((opt) => (
        <Toggle
          key={opt.name}
          size="sm"
          pressed={editor.isActive({ textAlign: opt.align })}
          onPressedChange={() => editor.chain().focus().setTextAlign(opt.align).run()}
        >
          <opt.icon className="h-4 w-4" />
        </Toggle>
      ))}
    </div>
  )
}
