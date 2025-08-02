import { Loader2 } from 'lucide-react';

export default function Loading() {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-white">
      <div className="flex flex-col items-center gap-4">
        <div className="flex items-center space-x-2">
          <span className="text-3xl font-bold text-neutral-700">
            rule
          </span>
          <span className="text-3xl font-bold text-teal-600">
            IQ
          </span>
        </div>
        <Loader2 className="h-8 w-8 animate-spin text-teal-600" />
        <p className="text-lg text-neutral-600">
          Loading your compliance dashboard...
        </p>
      </div>
    </div>
  );
}
