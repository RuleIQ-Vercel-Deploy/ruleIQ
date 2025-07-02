"use client"

import { UploadCloud, FileUp, X } from "lucide-react"
import * as React from "react"
import { useDropzone } from "react-dropzone"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

import { FilePreviewCard } from "./file-preview-card"

export interface UploadableFile {
  id: string
  file: File
  status: "pending" | "uploading" | "success" | "error"
  progress: number
  metadata: {
    description: string
    framework: string
    control: string
  }
}

export function FileUploader() {
  const [files, setFiles] = React.useState<UploadableFile[]>([])

  const onDrop = React.useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadableFile[] = acceptedFiles.map((file) => ({
      id: `${file.name}-${Date.now()}`,
      file,
      status: "pending",
      progress: 0,
      metadata: { description: "", framework: "", control: "" },
    }))
    setFiles((prev) => [...prev, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "image/png": [".png"],
      "image/jpeg": [".jpg", ".jpeg"],
    },
  })

  const handleRemoveFile = (id: string) => {
    setFiles((prev) => prev.filter((file) => file.id !== id))
  }

  const handleUpdateMetadata = (id: string, data: Partial<UploadableFile["metadata"]>) => {
    setFiles((prev) =>
      prev.map((file) => (file.id === id ? { ...file, metadata: { ...file.metadata, ...data } } : file)),
    )
  }

  const handleClearAll = () => {
    setFiles([])
  }

  const handleUploadAll = () => {
    setFiles((prev) => prev.map((file) => ({ ...file, status: "uploading" })))

    // Simulate upload
    files.forEach((file) => {
      const interval = setInterval(() => {
        setFiles((prev) =>
          prev.map((f) => {
            if (f.id === file.id) {
              const newProgress = f.progress + 10
              if (newProgress >= 100) {
                clearInterval(interval)
                return { ...f, progress: 100, status: "success" }
              }
              return { ...f, progress: newProgress }
            }
            return f
          }),
        )
      }, 200)
    })
  }

  return (
    <div className="w-full space-y-6">
      {files.length === 0 ? (
        <div
          {...getRootProps()}
          className={cn(
            "flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer transition-colors",
            "border-gold/50 hover:border-gold hover:bg-oxford-blue/50",
            isDragActive && "border-gold bg-oxford-blue/50",
          )}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
            <UploadCloud className="w-10 h-10 mb-4 text-gold" />
            <p className="mb-2 text-lg font-semibold text-eggshell-white">Drag files here or click to browse</p>
            <p className="text-xs text-eggshell-white/60">Supported formats: PDF, DOCX, XLSX, PNG, JPG</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {files.map((file) => (
              <FilePreviewCard key={file.id} file={file} onRemove={handleRemoveFile} onUpdate={handleUpdateMetadata} />
            ))}
          </div>
          <div className="flex justify-end items-center gap-4 pt-4 border-t border-gold/20">
            <Button variant="ghost-ruleiq" onClick={handleClearAll}>
              <X className="mr-2" /> Clear All
            </Button>
            <Button variant="accent" size="medium" onClick={handleUploadAll}>
              <FileUp className="mr-2" /> Upload All ({files.length})
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
