'use client';
import { X, FileText } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { FormField } from '@/components/ui/form-field';
import { ProgressBar } from '@/components/ui/progress-bar';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { frameworkOptions, controlMappingOptions } from '@/lib/data/mock-form-data';

import type { UploadableFile } from './file-uploader';

interface FilePreviewCardProps {
  file: UploadableFile;
  onRemove: (id: string) => void;
  onUpdate: (id: string, data: Partial<UploadableFile['metadata']>) => void;
}

export function FilePreviewCard({ file, onRemove, onUpdate }: FilePreviewCardProps) {
  const selectedFramework = file.metadata.framework as keyof typeof controlMappingOptions;
  const controls = controlMappingOptions[selectedFramework] || [];

  const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${Number.parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
  };

  return (
    <div className="bg-oxford-blue/50 space-y-4 rounded-lg border border-gold/20 p-4">
      <div className="flex items-start gap-4">
        <FileText className="mt-1 h-8 w-8 text-gold" />
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <p className="text-eggshell-white truncate text-sm font-medium">{file.file.name}</p>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={() => onRemove(file.id)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-eggshell-white/60 text-xs">{formatBytes(file.file.size)}</p>
          {file.status !== 'pending' && (
            <div className="mt-2">
              <ProgressBar value={file.progress} color="gold" />
            </div>
          )}
        </div>
      </div>

      {/* Metadata Form */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <FormField label="Description" className="md:col-span-2">
          <Textarea
            placeholder="Add a description for this evidence..."
            value={file.metadata.description}
            onChange={(e) => onUpdate(file.id, { description: e.target.value })}
            className="bg-oxford-blue text-eggshell-white border-gold/30 focus:border-gold focus:ring-gold"
          />
        </FormField>
        <FormField label="Framework">
          <Select
            value={file.metadata.framework}
            onValueChange={(value) => onUpdate(file.id, { framework: value, control: '' })}
          >
            <SelectTrigger className="bg-oxford-blue text-eggshell-white border-gold/30 focus:border-gold focus:ring-gold">
              <SelectValue placeholder="Select framework" />
            </SelectTrigger>
            <SelectContent className="bg-oxford-blue text-eggshell-white border-gold/50">
              {frameworkOptions.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </FormField>
        <FormField label="Control Mapping">
          <Select
            value={file.metadata.control}
            onValueChange={(value) => onUpdate(file.id, { control: value })}
            disabled={!file.metadata.framework || controls.length === 0}
          >
            <SelectTrigger className="bg-oxford-blue text-eggshell-white border-gold/30 focus:border-gold focus:ring-gold">
              <SelectValue placeholder="Select control" />
            </SelectTrigger>
            <SelectContent className="bg-oxford-blue text-eggshell-white border-gold/50">
              {controls.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </FormField>
      </div>
    </div>
  );
}
