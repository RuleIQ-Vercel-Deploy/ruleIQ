import { BreadcrumbNav } from '@/components/navigation/breadcrumb-nav';
import { ButtonShowcase } from '@/components/ui/button-showcase';

export default function ComponentsPage() {
  return (
    <>
      <BreadcrumbNav items={[{ title: 'Components' }]} />

      <main className="flex-1 space-y-6 p-6" style={{ backgroundColor: '#002147' }}>
        <div className="space-y-2">
          <h1 className="text-3xl font-bold" style={{ color: '#F0EAD6' }}>
            Button Components
          </h1>
          <p className="text-lg" style={{ color: '#6C757D' }}>
            Comprehensive button variant system for the ruleIQ platform
          </p>
        </div>

        <ButtonShowcase />
      </main>
    </>
  );
}
