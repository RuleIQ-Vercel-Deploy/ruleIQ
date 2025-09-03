import { FormShowcase } from '@/components/forms/form-showcase';
import { BreadcrumbNav } from '@/components/navigation/breadcrumb-nav';

export default function FormsPage() {
  return (
    <main className="flex-1 space-y-6 p-6" style={{ backgroundColor: '#002147' }}>
      <BreadcrumbNav items={[{ title: 'Forms' }]} />

      <div className="space-y-2">
        <h1 className="text-3xl font-bold" style={{ color: '#F0EAD6' }}>
          Form Components
        </h1>
        <p className="text-lg" style={{ color: '#6C757D' }}>
          Comprehensive form components with validation states and enhanced user experience
        </p>
      </div>

      <FormShowcase />
    </main>
  );
}
