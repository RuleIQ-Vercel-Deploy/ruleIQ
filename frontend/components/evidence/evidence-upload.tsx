'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface EvidenceUploadProps {
  onUpload?: (files: File[], metadata: any) => void;
}

export function EvidenceUpload({ onUpload }: EvidenceUploadProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [evidenceName, setEvidenceName] = useState('');
  const [description, setDescription] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleUpload = () => {
    if (files.length > 0) {
      onUpload?.(files, {
        name: evidenceName,
        description: description
      });
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Upload Evidence</h3>

      <div>
        <label htmlFor="evidenceName" className="text-sm font-medium">
          Evidence Name
        </label>
        <Input
          id="evidenceName"
          value={evidenceName}
          onChange={(e) => setEvidenceName(e.target.value)}
          placeholder="Enter evidence name"
        />
      </div>

      <div>
        <label htmlFor="description" className="text-sm font-medium">
          Description
        </label>
        <Input
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter description"
        />
      </div>

      <div>
        <label htmlFor="fileUpload" className="text-sm font-medium">
          Select Files
        </label>
        <input
          id="fileUpload"
          type="file"
          multiple
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
      </div>

      <Button
        onClick={handleUpload}
        disabled={files.length === 0}
        tabIndex={0}
      >
        Upload Files
      </Button>
    </div>
  );
}
