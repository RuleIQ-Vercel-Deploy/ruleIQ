import { FileText, MoreVertical } from 'lucide-react';
import Image from 'next/image';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { type Evidence, statuses } from '@/lib/data/evidence';

interface EvidenceCardProps {
  evidence: Evidence;
  isSelected: boolean;
  onSelectionChange: (id: string) => void;
}

export function EvidenceCard({ evidence, isSelected, onSelectionChange }: EvidenceCardProps) {
  const status = statuses.find((s) => s.value === evidence.status);

  return (
    <Card className="border-border bg-card transition-all duration-200 hover:border-gold/40 hover:shadow-lg">
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
        <div className="flex items-center gap-3">
          <Checkbox
            checked={isSelected}
            onCheckedChange={() => onSelectionChange(evidence.id)}
            aria-label={`Select ${evidence.name}`}
          />
          <FileText className="h-6 w-6 text-gold" />
          <CardTitle className="text-base font-medium text-foreground">{evidence.name}</CardTitle>
        </div>
        <Button variant="ghost" size="icon" className="h-8 w-8 shrink-0">
          <MoreVertical className="h-4 w-4" />
          <span className="sr-only">More actions</span>
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <Badge
            variant={
              status?.value === 'approved'
                ? 'default'
                : status?.value === 'pending'
                  ? 'secondary'
                  : 'destructive'
            }
          >
            {status?.label}
          </Badge>
          <div className="flex flex-wrap gap-1">
            {evidence.classification.map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>{evidence.uploadDate}</span>
          <div className="flex items-center gap-2">
            <Image
              src={evidence.userAvatar || '/placeholder.svg'}
              alt={evidence.uploadedBy}
              width={24}
              height={24}
              sizes="24px"
              className="rounded-full"
            />
            <span>{evidence.uploadedBy}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
