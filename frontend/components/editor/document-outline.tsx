"use client"

import { useEffect, useState } from "react"

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

import type { Editor } from "@tiptap/react"

interface OutlineNode {
  id: string
  level: number
  text: string
  children: OutlineNode[]
}

interface DocumentOutlineProps {
  editor: Editor | null
}

export function DocumentOutline({ editor }: DocumentOutlineProps) {
  const [outline, setOutline] = useState<OutlineNode[]>([])

  useEffect(() => {
    if (!editor) return

    const updateOutline = () => {
      const headings: { level: number; text: string; id: string }[] = []

      editor.state.doc.forEach((node, offset) => {
        if (node.type.name.startsWith("heading")) {
          headings.push({
            level: node.attrs['level'],
            text: node.textContent,
            id: `heading-${offset}`,
          })
        }
      })

      const buildTree = (items: typeof headings, level = 1): OutlineNode[] => {
        const tree: OutlineNode[] = []
        let i = 0
        while (i < items.length) {
          const item = items[i]
          if (item && item.level === level) {
            const children: OutlineNode[] = []
            const nextItems = []
            i++
            while (i < items.length && items[i] && items[i]!.level > level) {
              nextItems.push(items[i]!)
              i++
            }
            if (nextItems.length > 0) {
              children.push(...buildTree(nextItems, level + 1))
            }
            tree.push({ 
              id: item.id, 
              level: item.level, 
              text: item.text, 
              children 
            })
          } else {
            i++
          }
        }
        return tree
      }

      setOutline(buildTree(headings))
    }

    editor.on("update", updateOutline)
    updateOutline() // Initial generation

    return () => {
      editor.off("update", updateOutline)
    }
  }, [editor])

  const renderNodes = (nodes: OutlineNode[]) => (
    <Accordion type="multiple" className="w-full" defaultValue={nodes.map((n) => n.id)}>
      {nodes.map((node) => (
        <AccordionItem key={node.id} value={node.id} className="border-b-0">
          <AccordionTrigger
            className={`pl-${(node.level - 1) * 2} py-1 text-sm hover:no-underline hover:bg-gray-700/50 rounded-md`}
          >
            {node.text}
          </AccordionTrigger>
          <AccordionContent className="pb-0">{node.children.length > 0 && renderNodes(node.children)}</AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  )

  return (
    <div className="h-full w-64 border-r border-border bg-background p-4 text-eggshell-white overflow-y-auto">
      <h3 className="text-lg font-semibold mb-4">Outline</h3>
      {renderNodes(outline)}
    </div>
  )
}
