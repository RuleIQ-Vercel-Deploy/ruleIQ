# State Management with Zustand

This directory contains all Zustand stores for client-side state management.

## Available Stores

- `auth.store.ts` - Authentication state and user management
- `ui.store.ts` - UI state (modals, sidebars, etc.)
- `notifications.store.ts` - Notification management

## Usage

```typescript
import { useAuthStore } from '@/stores/auth.store';

const MyComponent = () => {
  const { user, login, logout } = useAuthStore();
  // ...
};
```

## Best Practices

1. Keep stores focused on a single domain
2. Use TypeScript for type safety
3. Persist only necessary data
4. Clear sensitive data on logout