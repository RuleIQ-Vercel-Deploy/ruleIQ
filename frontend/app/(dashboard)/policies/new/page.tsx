'use client';

import { IntelligentPolicyWizard } from '@/components/policies/intelligent-policy-wizard';
import { AppSidebar } from '@/components/navigation/app-sidebar';
import { BreadcrumbNav } from '@/components/navigation/breadcrumb-nav';

export default function NewPolicyPage() {
  return (
    <div className="flex min-h-screen w-full">
      <AppSidebar />
      <main className="flex flex-1 flex-col space-y-6 p-6 lg:p-8">
        <BreadcrumbNav
          items={[{ title: 'Policies', href: '/policies' }, { title: 'New Policy' }]}
        />
        <IntelligentPolicyWizard />
      </main>
    </div>
  );
}
