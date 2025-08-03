# React Key Errors Fix - January 2025

## Issue Identified
- Multiple React key errors in AI-guided signup page
- Duplicate keys: `2`, `4`, `6` causing React warnings
- Error: "Encountered two children with the same key"
- Occurring in AnimatePresence component with message mapping

## Root Cause Analysis
**Problem**: Message ID generation using array length
```typescript
// BROKEN - Creates duplicate IDs
addBotMessage: id: messages.length + 1
addUserMessage: id: prev.length + 1
```

**Why it fails**:
1. Both functions calculate ID based on current array length
2. When messages are added in quick succession, they can get same ID
3. React state updates are asynchronous, so length might not reflect latest state
4. AnimatePresence requires unique keys for proper animations

## Solution Implemented
**Fixed**: Unique ID generation using ref counter
```typescript
// FIXED - Guaranteed unique IDs
const messageIdCounter = React.useRef(0);

addBotMessage: 
  messageIdCounter.current += 1;
  id: messageIdCounter.current

addUserMessage:
  messageIdCounter.current += 1; 
  id: messageIdCounter.current
```

## Files Modified
- `frontend/app/(auth)/signup/page.tsx`: Fixed message ID generation

## Code Changes
1. **Added counter ref**: `const messageIdCounter = React.useRef(0);`
2. **Fixed addBotMessage**: Uses incremented counter instead of array length
3. **Fixed addUserMessage**: Uses incremented counter instead of array length  
4. **Fixed initial message**: Sets counter to 1 for greeting message

## Benefits
- ✅ Unique keys guaranteed for all messages
- ✅ Proper React reconciliation and animations
- ✅ No more console warnings/errors
- ✅ Better performance with AnimatePresence
- ✅ Stable component identity across updates

## Verification
- No more "Encountered two children with the same key" errors
- AnimatePresence animations work correctly
- Message rendering is stable and performant
- All 10 Next.js errors should be resolved with this pattern