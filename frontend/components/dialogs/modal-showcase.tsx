'use client';

import { AlertTriangle, Trash2, UserPlus } from 'lucide-react';
import * as React from 'react';

import { ConfirmDialog } from '@/components/dialogs/confirm-dialog';
import { FormDialog } from '@/components/dialogs/form-dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FormField } from '@/components/ui/form-field';
import { Input } from '@/components/ui/input';

export function ModalShowcase() {
  const [formState, setFormState] = React.useState({
    name: '',
    email: '',
  });
  const [isLoading, setIsLoading] = React.useState(false);
  const [feedback, setFeedback] = React.useState('');

  const handleFormSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    setFeedback('');

    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      setFeedback(`User "${formState.name}" with email "${formState.email}" has been added.`);
    // TODO: Replace with proper logging
    }, 1500);
  };

  const handleConfirmAction = () => {
    setFeedback('The item has been successfully deleted.');
    // TODO: Replace with proper logging
  };

  return (
    <div className="space-y-8">
      {/* Feedback Area */}
      {feedback && (
        <div
          className="rounded-md border p-4 text-sm"
          style={{
            backgroundColor: 'rgba(40, 167, 69, 0.1)',
            borderColor: 'rgba(40, 167, 69, 0.3)',
            color: '#28A745',
          }}
        >
          {feedback}
        </div>
      )}

      {/* Confirm Dialog Showcase */}
      <Card className="ruleiq-card">
        <CardHeader>
          <CardTitle style={{ color: '#F0EAD6' }}>Confirm Dialog</CardTitle>
          <CardDescription style={{ color: '#6C757D' }}>
            For actions that require user confirmation, especially destructive ones.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-4">
          <ConfirmDialog
            trigger={
              <Button variant="secondary" size="default">
                Show Confirmation
              </Button>
            }
            title="Are you sure?"
            description="This action cannot be undone. This will permanently delete the item from our servers."
            onConfirm={handleConfirmAction}
            icon={AlertTriangle}
          />
          <ConfirmDialog
            trigger={
              <Button variant="destructive" size="default">
                <Trash2 className="h-4 w-4" />
                Delete Item
              </Button>
            }
            title="Delete this item permanently?"
            description="This is a destructive action. All data associated with this item will be lost forever."
            onConfirm={handleConfirmAction}
            confirmText="Yes, delete it"
            variant="destructive"
            icon={Trash2}
          />
        </CardContent>
      </Card>

      {/* Form Modal Showcase */}
      <Card className="ruleiq-card">
        <CardHeader>
          <CardTitle style={{ color: '#F0EAD6' }}>Form Modal</CardTitle>
          <CardDescription style={{ color: '#6C757D' }}>
            For capturing user input without navigating away from the current page.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <FormDialog
            trigger={
              <Button variant="default" size="default">
                <UserPlus className="h-4 w-4" />
                Add New User
              </Button>
            }
            title="Add a New User"
            description="Enter the details below to add a new user to the system. Click submit when you're done."
            formId="add-user-form"
            submitText="Add User"
            isLoading={isLoading}
          >
            <form id="add-user-form" onSubmit={handleFormSubmit} className="space-y-4">
              <FormField label="Full Name" required>
                <Input
                  placeholder="John Doe"
                  value={formState.name}
                  onChange={(e) => setFormState({ ...formState, name: e.target.value })}
                  required
                />
              </FormField>
              <FormField label="Email Address" required>
                <Input
                  type="email"
                  placeholder="john.doe@company.com"
                  value={formState.email}
                  onChange={(e) => setFormState({ ...formState, email: e.target.value })}
                  required
                />
              </FormField>
            </form>
          </FormDialog>
        </CardContent>
      </Card>

      {/* Accessibility & Focus Management */}
      <Card className="ruleiq-card">
        <CardHeader>
          <CardTitle style={{ color: '#F0EAD6' }}>Accessibility & Focus Management</CardTitle>
          <CardDescription style={{ color: '#6C757D' }}>
            The modal system is built with accessibility in mind, ensuring a seamless user
            experience.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm" style={{ color: '#F0EAD6' }}>
          <p>
            <strong>Focus Trapping:</strong> When a modal is opened, focus is automatically moved
            inside and contained within it. You can use the{' '}
            <kbd className="bg-oxford-blue/80 rounded p-1">Tab</kbd> key to navigate between
            interactive elements like buttons and inputs.
          </p>
          <p>
            <strong>Focus Restoration:</strong> Upon closing the modal (either by clicking the
            'Cancel' button, the 'X' icon, or pressing the{' '}
            <kbd className="bg-oxford-blue/80 rounded p-1">Esc</kbd> key), focus is automatically
            returned to the element that originally triggered it.
          </p>
          <p>
            <strong>Screen Reader Support:</strong> Proper ARIA attributes are used to announce the
            modal's role, title, and description to screen reader users.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
