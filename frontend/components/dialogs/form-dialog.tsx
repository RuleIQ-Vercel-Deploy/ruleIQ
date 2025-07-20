"use client"

import * as React from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface FormDialogProps {
  trigger: React.ReactNode
  title: string
  description?: string
  formId: string
  children: React.ReactNode
  submitText?: string
  cancelText?: string
  isLoading?: boolean
}

export function FormDialog({
  trigger,
  title,
  description,
  formId,
  children,
  submitText = "Submit",
  cancelText = "Cancel",
  isLoading = false,
}: FormDialogProps) {
  const [open, setOpen] = React.useState(false)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description && <DialogDescription>{description}</DialogDescription>}
        </DialogHeader>
        <div className="py-4">{children}</div>
        <DialogFooter>
          <Button variant="secondary" size="default" onClick={() => setOpen(false)}>
            {cancelText}
          </Button>
          <Button type="submit" form={formId} variant="default" size="default" disabled={isLoading}>
            {isLoading ? "Submitting..." : submitText}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
