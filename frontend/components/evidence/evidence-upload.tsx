'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';

export function EvidenceUpload() {
  const [files, setFiles] = useState<File[]>([]);

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Upload Evidence</h3>
      <input
        type="file"
        multiple
        onChange={(e) => setFiles(Array.from(e.target.files || []))}
        className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
      />
      <Button onClick={() => console.log('Upload files:', files)}>
        Upload Files
      </Button>
    </div>
  );
}
