'use client';

import { cn } from '@/lib/utils';

interface FloatingNavProps {
  navItems: Array<{
    name: string;
    link: string;
  }>;
  className?: string;
}

export const FloatingNav = ({ navItems, className }: FloatingNavProps) => {
  return (
    <nav className={cn(
      'fixed top-4 left-1/2 transform -translate-x-1/2 z-50',
      'bg-background/80 backdrop-blur-md border rounded-full px-6 py-3',
      'shadow-lg shadow-primary/10',
      className
    )}>
      <ul className="flex space-x-6">
        {navItems.map((item) => (
          <li key={item.name}>
            <a
              href={item.link}
              className="text-sm font-medium text-foreground/80 hover:text-primary transition-colors"
            >
              {item.name}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
};
