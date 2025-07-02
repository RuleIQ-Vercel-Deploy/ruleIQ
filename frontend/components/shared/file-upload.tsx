"use client"

import { 
  FileIcon, 
  Upload, 
  X, 
  CheckCircle2, 
  AlertCircle,
  FileText,
  FileImage,
  File,
  Loader2
} from "lucide-react"
import * as React from "react"
import { useDropzone, type Accept } from "react-dropzone"

import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Body, Caption } from "@/components/ui/typography"
import { useAppStore } from "@/lib/stores/app.store"
import { cn } from "@/lib/utils"

export interface FileWithProgress extends File {
  id: string
  progress?: number
  status?: 'uploading' | 'success' | 'error'
  error?: string
}

interface FileUploadProps {
  className?: string
  onUpload: (files: File[]) => void | Promise<void>
  acceptedTypes?: string[]
  maxSize?: number
  maxFiles?: number
  multiple?: boolean
  disabled?: boolean
  showFileList?: boolean
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))  } ${  sizes[i]}`
}

const getFileIcon = (file: File) => {
  const {type} = file
  if (type.startsWith('image/')) return FileImage
  if (type.includes('pdf') || type.includes('document')) return FileText
  return File
}

export function FileUpload({
  className,
  onUpload,
  acceptedTypes = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg'],
  maxSize = 10 * 1024 * 1024, // 10MB default
  maxFiles = 5,
  multiple = true,
  disabled = false,
  showFileList = true,
}: FileUploadProps) {
  const [files, setFiles] = React.useState<FileWithProgress[]>([])
  const [uploading, setUploading] = React.useState(false)
  const { addNotification } = useAppStore()

  // Create accept object for react-dropzone
  const accept: Accept = React.useMemo(() => {
    const mimeTypes: Accept = {}
    acceptedTypes.forEach(type => {
      switch (type.toLowerCase()) {
        case 'pdf':
          mimeTypes['application/pdf'] = ['.pdf']
          break
        case 'doc':
          mimeTypes['application/msword'] = ['.doc']
          break
        case 'docx':
          mimeTypes['application/vnd.openxmlformats-officedocument.wordprocessingml.document'] = ['.docx']
          break
        case 'xls':
          mimeTypes['application/vnd.ms-excel'] = ['.xls']
          break
        case 'xlsx':
          mimeTypes['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'] = ['.xlsx']
          break
        case 'png':
          mimeTypes['image/png'] = ['.png']
          break
        case 'jpg':
        case 'jpeg':
          mimeTypes['image/jpeg'] = ['.jpg', '.jpeg']
          break
        default:
          break
      }
    })
    return mimeTypes
  }, [acceptedTypes])

  const onDrop = React.useCallback(async (acceptedFiles: File[]) => {
    // Create file objects with IDs and initial status
    const newFiles: FileWithProgress[] = acceptedFiles.map(file => ({
      ...file,
      id: crypto.randomUUID(),
      progress: 0,
      status: 'uploading' as const,
    }))

    setFiles(prev => [...prev, ...newFiles])
    setUploading(true)

    try {
      // Simulate upload progress for each file
      await Promise.all(newFiles.map(async (file) => {
        // Simulate progress updates
        for (let progress = 0; progress <= 100; progress += 10) {
          await new Promise(resolve => setTimeout(resolve, 100))
          setFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, progress } : f
          ))
        }

        // Mark as success
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'success' as const } : f
        ))
      }))

      // Call the onUpload handler
      await onUpload(acceptedFiles)
      
      addNotification({
        type: 'success',
        title: 'Files uploaded successfully',
        message: `${acceptedFiles.length} file(s) uploaded`,
        duration: 3000,
      })
    } catch (error) {
      // Mark files as error
      newFiles.forEach(file => {
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { 
            ...f, 
            status: 'error' as const,
            error: 'Upload failed' 
          } : f
        ))
      })
      
      addNotification({
        type: 'error',
        title: 'Upload failed',
        message: error instanceof Error ? error.message : 'Failed to upload files',
        duration: 5000,
      })
    } finally {
      setUploading(false)
    }
  }, [onUpload, addNotification])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept,
    maxSize,
    maxFiles: multiple ? maxFiles : 1,
    multiple,
    disabled: disabled || uploading,
  })

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId))
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div
        {...getRootProps()}
        className={cn(
          "relative overflow-hidden rounded-lg border-2 border-dashed transition-all duration-200",
          "hover:border-gold hover:bg-gold/5",
          "focus:outline-none focus:ring-2 focus:ring-gold focus:ring-offset-2",
          isDragActive && !isDragReject && "border-gold bg-gold/10",
          isDragReject && "border-error bg-error/10",
          disabled && "opacity-50 cursor-not-allowed",
          "cursor-pointer p-8",
          className
        )}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center justify-center space-y-3 text-center">
          {isDragReject ? (
            <>
              <AlertCircle className="h-12 w-12 text-error" />
              <Body color="error">File type not accepted or too large</Body>
            </>
          ) : (
            <>
              <Upload className={cn(
                "h-12 w-12 transition-colors",
                isDragActive ? "text-gold" : "text-muted-foreground"
              )} />
              <div className="space-y-1">
                <Body>
                  {isDragActive ? "Drop files here" : "Drag & drop files here"}
                </Body>
                <Caption color="muted">
                  or click to select files
                </Caption>
              </div>
              <div className="space-y-1">
                <Caption color="muted">
                  Accepted: {acceptedTypes.join(', ').toUpperCase()}
                </Caption>
                <Caption color="muted">
                  Max size: {formatFileSize(maxSize)} • Max files: {maxFiles}
                </Caption>
              </div>
            </>
          )}
        </div>
      </div>

      {/* File List */}
      {showFileList && files.length > 0 && (
        <div className="space-y-2">
          <Body weight="medium">Uploaded Files</Body>
          <div className="space-y-2">
            {files.map((file) => {
              const Icon = getFileIcon(file)
              return (
                <div
                  key={file.id}
                  className="flex items-center gap-3 rounded-lg border border-border bg-card p-3"
                >
                  <Icon className="h-8 w-8 text-muted-foreground shrink-0" />
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <Body className="truncate">{file.name}</Body>
                      {file.status === 'success' && (
                        <CheckCircle2 className="h-4 w-4 text-success shrink-0" />
                      )}
                      {file.status === 'error' && (
                        <AlertCircle className="h-4 w-4 text-error shrink-0" />
                      )}
                    </div>
                    <Caption color="muted">{formatFileSize(file.size)}</Caption>
                    
                    {file.status === 'uploading' && file.progress !== undefined && (
                      <Progress value={file.progress} className="mt-2 h-1" />
                    )}
                    
                    {file.error && (
                      <Caption color="error" className="mt-1">{file.error}</Caption>
                    )}
                  </div>
                  
                  {file.status === 'uploading' ? (
                    <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                  ) : (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeFile(file.id)}
                      className="shrink-0"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}