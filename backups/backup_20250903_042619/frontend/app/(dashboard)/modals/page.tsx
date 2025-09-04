import { ModalShowcase } from '@/components/dialogs/modal-showcase';
import { BreadcrumbNav } from '@/components/navigation/breadcrumb-nav';

export default function ModalsPage() {
  return (
    <>
      <BreadcrumbNav items={[{ title: 'Modals' }]} />

      <main className="flex-1 space-y-6 p-6" style={{ backgroundColor: '#002147' }}>
        <div className="space-y-2">
          <h1 className="text-3xl font-bold" style={{ color: '#F0EAD6' }}>
            Modal & Dialog System
          </h1>
          <p className="text-lg" style={{ color: '#6C757D' }}>
            A comprehensive and accessible modal system for various user interactions.
          </p>
        </div>

        <ModalShowcase />
      </main>
    </>
  );
}
