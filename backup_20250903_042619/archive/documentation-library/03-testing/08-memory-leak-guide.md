# Memory Leak Detection Guide

## Overview

This guide explains how to use the memory leak detection system for React components in the ruleIQ frontend.

## What Memory Leaks Are Detected

The system detects the following common memory leak patterns:

1. **Event Listeners**: Not removed on component unmount
2. **Timers**: `setTimeout` calls not cleared with `clearTimeout`
3. **Intervals**: `setInterval` calls not cleared with `clearInterval`
4. **Abort Controllers**: Fetch requests not aborted on unmount
5. **Subscriptions**: Observable/EventEmitter subscriptions not unsubscribed

## Running Memory Leak Tests

### Run All Memory Leak Tests
```bash
pnpm test:memory-leaks
```

### Watch Mode
```bash
pnpm test:memory-leaks:watch
```

### Generate Comprehensive Report
```bash
pnpm test:memory-leaks:report
```

## Writing Memory Leak Tests

### Basic Component Test

```typescript
import { testComponentMemoryLeaks } from '@/tests/utils/component-test-helpers';

describe('MyComponent Memory Leaks', () => {
  it('should cleanup all resources on unmount', async () => {
    await testComponentMemoryLeaks(
      MyComponent,
      { prop1: 'value1' }, // props
      async (result) => {
        // Optional: interact with component
        const button = screen.getByRole('button');
        fireEvent.click(button);
      }
    );
  });
});
```

### Advanced Testing with Leak Detection

```typescript
import { renderWithLeakDetection } from '@/tests/utils/component-test-helpers';

it('should cleanup event listeners', () => {
  const { unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
    <MyComponent />
  );
  
  // Interact with component
  fireEvent.click(screen.getByRole('button'));
  
  // Unmount
  unmount();
  
  // Assert no leaks
  assertNoLeaks();
  
  // Get detailed report if needed
  const report = leakDetector.getReport();
  console.log('Memory leak report:', report);
  
  // Cleanup
  leakDetector.teardown();
});
```

### Testing Rapid Mount/Unmount Cycles

```typescript
import { testRapidMountUnmount } from '@/tests/utils/component-test-helpers';

it('should handle rapid mount/unmount without leaks', async () => {
  await testRapidMountUnmount(MyComponent, { prop1: 'value' }, 10);
});
```

## Common Memory Leak Patterns and Fixes

### 1. Event Listeners

**❌ Bad - Memory Leak**
```typescript
useEffect(() => {
  const handler = () => console.log('clicked');
  document.addEventListener('click', handler);
  // Missing cleanup!
}, []);
```

**✅ Good - Proper Cleanup**
```typescript
useEffect(() => {
  const handler = () => console.log('clicked');
  document.addEventListener('click', handler);
  
  return () => {
    document.removeEventListener('click', handler);
  };
}, []);
```

### 2. Timers

**❌ Bad - Memory Leak**
```typescript
useEffect(() => {
  setTimeout(() => {
    setData('updated');
  }, 1000);
}, []);
```

**✅ Good - Proper Cleanup**
```typescript
useEffect(() => {
  const timer = setTimeout(() => {
    setData('updated');
  }, 1000);
  
  return () => {
    clearTimeout(timer);
  };
}, []);
```

### 3. Intervals

**❌ Bad - Memory Leak**
```typescript
useEffect(() => {
  setInterval(() => {
    fetchData();
  }, 5000);
}, []);
```

**✅ Good - Proper Cleanup**
```typescript
useEffect(() => {
  const interval = setInterval(() => {
    fetchData();
  }, 5000);
  
  return () => {
    clearInterval(interval);
  };
}, []);
```

### 4. Async Operations

**❌ Bad - Memory Leak**
```typescript
useEffect(() => {
  fetch('/api/data')
    .then(res => res.json())
    .then(data => setData(data));
}, []);
```

**✅ Good - Proper Cleanup**
```typescript
useEffect(() => {
  const controller = new AbortController();
  
  fetch('/api/data', { signal: controller.signal })
    .then(res => res.json())
    .then(data => setData(data))
    .catch(err => {
      if (err.name !== 'AbortError') {
        console.error(err);
      }
    });
  
  return () => {
    controller.abort();
  };
}, []);
```

### 5. Component State Updates After Unmount

**❌ Bad - Memory Leak**
```typescript
const [data, setData] = useState(null);

useEffect(() => {
  fetchData().then(result => {
    setData(result); // May execute after unmount!
  });
}, []);
```

**✅ Good - Proper Cleanup**
```typescript
const [data, setData] = useState(null);

useEffect(() => {
  let isMounted = true;
  
  fetchData().then(result => {
    if (isMounted) {
      setData(result);
    }
  });
  
  return () => {
    isMounted = false;
  };
}, []);
```

## Memory Leak Report Structure

The leak detector generates reports with the following structure:

```typescript
{
  eventListeners: {
    added: 5,
    removed: 3,
    leaked: 2,
    details: [
      { event: 'click', count: 1 },
      { event: 'keydown', count: 1 }
    ]
  },
  timers: {
    created: 3,
    cleared: 2,
    leaked: 1
  },
  intervals: {
    created: 1,
    cleared: 0,
    leaked: 1
  },
  abortControllers: {
    created: 2,
    aborted: 1,
    leaked: 1
  }
}
```

## Best Practices

1. **Always test components that use:**
   - Event listeners (window, document, or DOM elements)
   - Timers (setTimeout, setInterval)
   - Async operations (fetch, promises)
   - External subscriptions
   - WebSockets or SSE connections

2. **Test edge cases:**
   - Unmounting during loading states
   - Unmounting during async operations
   - Rapid mount/unmount cycles
   - Error states

3. **Use the appropriate test helper:**
   - `testComponentMemoryLeaks` for simple tests
   - `renderWithLeakDetection` for detailed control
   - `testRapidMountUnmount` for stress testing

4. **Review leak reports:**
   - Check the detailed report for specific leak types
   - Look for patterns in leaked resources
   - Fix the root cause, not just the symptom

## Troubleshooting

### False Positives

Sometimes the detector might report false positives for:
- React's internal event listeners
- Third-party library resources
- Browser extensions

To handle these:
1. Check if the leak count is consistent
2. Verify the leak is from your code
3. Use more specific assertions

### Async Cleanup

For components with async cleanup:
```typescript
await testComponentMemoryLeaks(
  MyComponent,
  {},
  async (result) => {
    // Wait for async operations
    await waitFor(() => {
      expect(screen.getByText('Loaded')).toBeInTheDocument();
    });
  }
);
```

### Debugging Leaks

To debug specific leaks:
```typescript
const report = leakDetector.getReport();
console.log('Leaked event listeners:', report.eventListeners.details);
console.log('Active timers:', report.timers.leaked);
```

## CI/CD Integration

Add to your CI pipeline:
```yaml
- name: Run Memory Leak Tests
  run: pnpm test:memory-leaks
  
- name: Generate Memory Leak Report
  if: failure()
  run: pnpm test:memory-leaks:report
  
- name: Upload Report
  if: failure()
  uses: actions/upload-artifact@v2
  with:
    name: memory-leak-report
    path: frontend/memory-leak-test-report.md
```