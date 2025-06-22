"use client"

import { useState, useCallback } from "react"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { PageHeader } from "@/components/layout/page-header"
import { evidenceSchema, type EvidenceInput } from "@/lib/validators"
import { useToast } from "@/hooks/use-toast"
import { Upload, X, FileText, ImageIcon, File, CheckCircle, AlertTriangle, Loader2, Plus, Tag } from "lucide-react"
import { useDropzone } from "react-dropzone"

const FRAMEWORKS = ["GDPR", "ISO 27001", "SOC 2", "HIPAA", "PCI DSS", "NIST", "ISO 9001", "FedRAMP", "CCPA", "SOX"]

const EVIDENCE_TYPES = [
  "Policy Document",
  "Technical Control",
  "Training Record",
  "Audit Report",
  "Risk Assessment",
  "Procedure",
  "Configuration",
  "Log File",
  "Certificate",
  "Other",
]

const CONTROL_IDS = {
  GDPR: ["Art. 5", "Art. 6", "Art. 7", "Art. 25", "Art. 30", "Art. 32", "Art. 33", "Art. 35"],
  "ISO 27001": ["A.5.1.1", "A.6.1.1", "A.7.2.2", "A.8.1.1", "A.9.1.1", "A.12.1.1", "A.14.1.1"],
  "SOC 2": ["CC1.1", "CC2.1", "CC3.1", "CC4.1", "CC5.1", "CC6.1", "CC7.1", "CC8.1"],
  HIPAA: ["164.308(a)(1)", "164.310(a)(1)", "164.312(a)(1)", "164.314(a)(1)"],
}

interface UploadedFile {
  file: File
  id: string
  progress: number
  status: "uploading" | "completed" | "error"
  preview?: string
}

export function EvidenceUpload() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [tagInput, setTagInput] = useState("")

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors },
  } = useForm<EvidenceInput>({
    resolver: zodResolver(evidenceSchema),
    defaultValues: {
      tags: [],
    },
  })

  const watchedFramework = watch("framework")
  const watchedTags = watch("tags")

  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach((file) => {
      const id = Math.random().toString(36).substr(2, 9)
      const uploadedFile: UploadedFile = {
        file,
        id,
        progress: 0,
        status: "uploading",
      }

      // Create preview for images
      if (file.type.startsWith("image/")) {
        const reader = new FileReader()
        reader.onload = (e) => {
          setUploadedFiles((prev) => prev.map((f) => (f.id === id ? { ...f, preview: e.target?.result as string } : f)))
        }
        reader.readAsDataURL(file)
      }

      setUploadedFiles((prev) => [...prev, uploadedFile])

      // Simulate file upload
      simulateUpload(id)
    })
  }, [])

  const simulateUpload = (fileId: string) => {
    const interval = setInterval(() => {
      setUploadedFiles((prev) =>
        prev.map((file) => {
          if (file.id === fileId) {
            const newProgress = Math.min(file.progress + Math.random() * 30, 100)
            const status = newProgress === 100 ? "completed" : "uploading"
            return { ...file, progress: newProgress, status }
          }
          return file
        }),
      )
    }, 500)

    setTimeout(() => {
      clearInterval(interval)
      setUploadedFiles((prev) =>
        prev.map((file) => (file.id === fileId ? { ...file, progress: 100, status: "completed" } : file)),
      )
    }, 3000)
  }

  const removeFile = (fileId: string) => {
    setUploadedFiles((prev) => prev.filter((file) => file.id !== fileId))
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/msword": [".doc"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "application/vnd.ms-excel": [".xls"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "text/plain": [".txt"],
      "image/*": [".png", ".jpg", ".jpeg", ".gif"],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
  })

  const addTag = () => {
    if (tagInput.trim() && !watchedTags.includes(tagInput.trim())) {
      setValue("tags", [...watchedTags, tagInput.trim()])
      setTagInput("")
    }
  }

  const removeTag = (tagToRemove: string) => {
    setValue(
      "tags",
      watchedTags.filter((tag) => tag !== tagToRemove),
    )
  }

  const onSubmit = async (data: EvidenceInput) => {
    if (uploadedFiles.length === 0) {
      toast({
        variant: "destructive",
        title: "No files uploaded",
        description: "Please upload at least one file.",
      })
      return
    }

    setIsLoading(true)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000))

      toast({
        title: "Evidence Uploaded",
        description: `${data.title} has been uploaded successfully.`,
      })

      navigate("/app/evidence")
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Upload Failed",
        description: "Failed to upload evidence. Please try again.",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const getFileIcon = (file: File) => {
    if (file.type.startsWith("image/")) return ImageIcon
    if (file.type === "application/pdf") return FileText
    return File
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Upload Evidence"
        description="Add new compliance evidence and documentation"
        breadcrumbs={[{ label: "Evidence Management", href: "/app/evidence" }, { label: "Upload Evidence" }]}
      />

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* File Upload */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Upload className="h-5 w-5" />
                  <span>File Upload</span>
                </CardTitle>
                <CardDescription>
                  Upload evidence files (PDF, DOC, XLS, images). Maximum file size: 10MB
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                    isDragActive
                      ? "border-blue-400 bg-blue-50 dark:bg-blue-950"
                      : "border-gray-300 hover:border-gray-400"
                  }`}
                >
                  <input {...getInputProps()} />
                  <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  {isDragActive ? (
                    <p className="text-blue-600">Drop the files here...</p>
                  ) : (
                    <div>
                      <p className="text-gray-600 mb-2">
                        Drag & drop files here, or <span className="text-blue-600">click to browse</span>
                      </p>
                      <p className="text-sm text-gray-500">Supports PDF, DOC, DOCX, XLS, XLSX, TXT, and images</p>
                    </div>
                  )}
                </div>

                {/* Uploaded Files */}
                {uploadedFiles.length > 0 && (
                  <div className="mt-6 space-y-3">
                    <h4 className="font-medium">Uploaded Files</h4>
                    {uploadedFiles.map((uploadedFile) => {
                      const FileIcon = getFileIcon(uploadedFile.file)
                      return (
                        <div key={uploadedFile.id} className="flex items-center space-x-3 p-3 border rounded-lg">
                          {uploadedFile.preview ? (
                            <img
                              src={uploadedFile.preview || "/placeholder.svg"}
                              alt={uploadedFile.file.name}
                              className="w-10 h-10 object-cover rounded"
                            />
                          ) : (
                            <FileIcon className="h-10 w-10 text-gray-400" />
                          )}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{uploadedFile.file.name}</p>
                            <p className="text-xs text-gray-500">
                              {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                            {uploadedFile.status === "uploading" && (
                              <Progress value={uploadedFile.progress} className="h-1 mt-1" />
                            )}
                          </div>
                          <div className="flex items-center space-x-2">
                            {uploadedFile.status === "completed" && <CheckCircle className="h-5 w-5 text-green-500" />}
                            {uploadedFile.status === "error" && <AlertTriangle className="h-5 w-5 text-red-500" />}
                            <Button type="button" variant="ghost" size="sm" onClick={() => removeFile(uploadedFile.id)}>
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Evidence Details */}
            <Card>
              <CardHeader>
                <CardTitle>Evidence Details</CardTitle>
                <CardDescription>Provide information about the evidence</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="title">
                    Title <span className="text-red-500">*</span>
                  </Label>
                  <Input id="title" {...register("title")} disabled={isLoading} placeholder="Enter evidence title" />
                  {errors.title && <p className="text-sm text-red-600">{errors.title.message}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    {...register("description")}
                    disabled={isLoading}
                    placeholder="Describe the evidence and its purpose"
                    rows={3}
                  />
                  {errors.description && <p className="text-sm text-red-600">{errors.description.message}</p>}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="framework">
                      Framework <span className="text-red-500">*</span>
                    </Label>
                    <Controller
                      name="framework"
                      control={control}
                      render={({ field }) => (
                        <Select onValueChange={field.onChange} value={field.value} disabled={isLoading}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select framework" />
                          </SelectTrigger>
                          <SelectContent>
                            {FRAMEWORKS.map((framework) => (
                              <SelectItem key={framework} value={framework}>
                                {framework}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      )}
                    />
                    {errors.framework && <p className="text-sm text-red-600">{errors.framework.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="control_id">
                      Control ID <span className="text-red-500">*</span>
                    </Label>
                    <Controller
                      name="control_id"
                      control={control}
                      render={({ field }) => (
                        <Select onValueChange={field.onChange} value={field.value} disabled={isLoading}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select control ID" />
                          </SelectTrigger>
                          <SelectContent>
                            {watchedFramework &&
                              CONTROL_IDS[watchedFramework as keyof typeof CONTROL_IDS]?.map((controlId) => (
                                <SelectItem key={controlId} value={controlId}>
                                  {controlId}
                                </SelectItem>
                              ))}
                          </SelectContent>
                        </Select>
                      )}
                    />
                    {errors.control_id && <p className="text-sm text-red-600">{errors.control_id.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="evidence_type">Evidence Type</Label>
                    <Controller
                      name="evidence_type"
                      control={control}
                      render={({ field }) => (
                        <Select onValueChange={field.onChange} value={field.value} disabled={isLoading}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select evidence type" />
                          </SelectTrigger>
                          <SelectContent>
                            {EVIDENCE_TYPES.map((type) => (
                              <SelectItem key={type} value={type}>
                                {type}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      )}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="source">Source</Label>
                    <Input
                      id="source"
                      {...register("source")}
                      disabled={isLoading}
                      placeholder="Evidence source or origin"
                    />
                  </div>
                </div>

                {/* Tags */}
                <div className="space-y-2">
                  <Label>Tags</Label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {watchedTags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="flex items-center space-x-1">
                        <Tag className="h-3 w-3" />
                        <span>{tag}</span>
                        <X className="h-3 w-3 cursor-pointer" onClick={() => removeTag(tag)} />
                      </Badge>
                    ))}
                  </div>
                  <div className="flex space-x-2">
                    <Input
                      value={tagInput}
                      onChange={(e) => setTagInput(e.target.value)}
                      placeholder="Add a tag"
                      onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addTag())}
                      disabled={isLoading}
                    />
                    <Button type="button" onClick={addTag} disabled={isLoading || !tagInput.trim()}>
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Form Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button type="submit" className="w-full" disabled={isLoading || uploadedFiles.length === 0}>
                  {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Evidence
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={() => navigate("/app/evidence")}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
              </CardContent>
            </Card>

            {/* Upload Guidelines */}
            <Card>
              <CardHeader>
                <CardTitle>Upload Guidelines</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="space-y-2">
                  <h4 className="font-medium">Supported Formats:</h4>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    <li>PDF documents</li>
                    <li>Word documents (DOC, DOCX)</li>
                    <li>Excel spreadsheets (XLS, XLSX)</li>
                    <li>Text files (TXT)</li>
                    <li>Images (PNG, JPG, GIF)</li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium">Best Practices:</h4>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    <li>Use descriptive file names</li>
                    <li>Include version numbers</li>
                    <li>Add relevant tags for searchability</li>
                    <li>Ensure files are up-to-date</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Upload Status */}
            {uploadedFiles.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Upload Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Files uploaded:</span>
                      <span className="font-medium">{uploadedFiles.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Completed:</span>
                      <span className="font-medium text-green-600">
                        {uploadedFiles.filter((f) => f.status === "completed").length}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>In progress:</span>
                      <span className="font-medium text-blue-600">
                        {uploadedFiles.filter((f) => f.status === "uploading").length}
                      </span>
                    </div>
                    {uploadedFiles.some((f) => f.status === "error") && (
                      <div className="flex justify-between">
                        <span>Errors:</span>
                        <span className="font-medium text-red-600">
                          {uploadedFiles.filter((f) => f.status === "error").length}
                        </span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </form>
    </div>
  )
}
