'use client';

import { cn } from '@/lib/utils';
import { Card } from '@/components/ui/card';

interface HoverEffectItem {
  title: string;
  description: string;
  link?: string;
  icon?: React.ReactNode;
}

interface HoverEffectProps {
  items: HoverEffectItem[];
  className?: string;
}

export const HoverEffect = ({ items, className }: HoverEffectProps) => {
  return (
    <div className={cn(
      'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto px-4',
      className
    )}>
      {items.map((item, idx) => (
        <Card key={idx} className="p-6 group hover:shadow-lg hover:shadow-primary/10 transition-all duration-300">
          <div className="space-y-4">
            {item.icon && (
              <div className="text-primary">{item.icon}</div>
            )}
            <h3 className="text-xl font-semibold group-hover:text-primary transition-colors">
              {item.title}
            </h3>
            <p className="text-muted-foreground">{item.description}</p>
          </div>
        </Card>
      ))}
    </div>
  );
};
