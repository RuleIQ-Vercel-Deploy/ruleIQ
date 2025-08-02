'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface Evidence {
  id: string;
  name: string;
  type: string;
  uploadDate: string;
  status: 'pending' | 'approved' | 'rejected';
}

export function EvidenceList() {
  const [evidence] = useState<Evidence[]>([
    {
      id: '1',
      name: 'Privacy Policy.pdf',
      type: 'document',
      uploadDate: '2024-01-15',
      status: 'approved'
    },
    {
      id: '2',
      name: 'Data Processing Agreement.docx',
      type: 'document',
      uploadDate: '2024-01-14',
      status: 'pending'
    }
  ]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Evidence List</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {evidence.map((item) => (
            <div key={item.id} className="flex items-center justify-between p-3 border rounded">
              <div>
                <div className="font-medium">{item.name}</div>
                <div className="text-sm text-gray-500">{item.uploadDate}</div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs ${
                  item.status === 'approved' ? 'bg-green-100 text-green-800' :
                  item.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {item.status}
                </span>
                <Button size="sm" variant="outline">View</Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
