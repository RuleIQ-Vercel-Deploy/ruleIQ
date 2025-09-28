import { useCallback, useEffect, useRef, useState } from 'react';

export interface NavigationItem {
  id: string;
  label: string;
  href?: string;
  disabled?: boolean;
  children?: NavigationItem[];
  [key: string]: any;
}

export interface UseKeyboardNavigationOptions {
  items: NavigationItem[];
  isNested?: boolean;
  onSelect?: (item: NavigationItem, index: number) => void;
  onExpand?: (item: NavigationItem, expanded: boolean) => void;
  onEscape?: () => void;
  onSearch?: (query: string) => void;
  orientation?: 'horizontal' | 'vertical';
  loop?: boolean;
  homeEndKeys?: boolean;
  typeaheadTimeout?: number;
  skipDisabled?: boolean;
}

export function useKeyboardNavigation({
  items,
  isNested = false,
  onSelect,
  onExpand,
  onEscape,
  onSearch,
  orientation = 'vertical',
  loop = true,
  homeEndKeys = true,
  typeaheadTimeout = 500,
  skipDisabled = true,
}: UseKeyboardNavigationOptions) {
  const [focusedIndex, setFocusedIndex] = useState(0);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [searchBuffer, setSearchBuffer] = useState('');
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const itemRefs = useRef<(HTMLElement | null)[]>([]);

  // Get the next valid index based on direction
  const getNextIndex = useCallback(
    (currentIndex: number, direction: 'next' | 'prev'): number => {
      const step = direction === 'next' ? 1 : -1;
      let nextIndex = currentIndex + step;

      // Handle looping
      if (loop) {
        if (nextIndex < 0) nextIndex = items.length - 1;
        if (nextIndex >= items.length) nextIndex = 0;
      } else {
        if (nextIndex < 0) nextIndex = 0;
        if (nextIndex >= items.length) nextIndex = items.length - 1;
      }

      // Skip disabled items if requested
      if (skipDisabled) {
        const startIndex = nextIndex;
        while (items[nextIndex]?.disabled) {
          nextIndex += step;
          if (loop) {
            if (nextIndex < 0) nextIndex = items.length - 1;
            if (nextIndex >= items.length) nextIndex = 0;
          } else {
            if (nextIndex < 0 || nextIndex >= items.length) {
              return currentIndex; // Stay at current if no valid item found
            }
          }
          // Prevent infinite loop
          if (nextIndex === startIndex) {
            return currentIndex;
          }
        }
      }

      return nextIndex;
    },
    [items, loop, skipDisabled]
  );

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      const isVertical = orientation === 'vertical';
      const prevKey = isVertical ? 'ArrowUp' : 'ArrowLeft';
      const nextKey = isVertical ? 'ArrowDown' : 'ArrowRight';
      const expandKey = isVertical ? 'ArrowRight' : 'ArrowDown';
      const collapseKey = isVertical ? 'ArrowLeft' : 'ArrowUp';

      switch (event.key) {
        case prevKey:
          event.preventDefault();
          setFocusedIndex((prev) => getNextIndex(prev, 'prev'));
          break;

        case nextKey:
          event.preventDefault();
          setFocusedIndex((prev) => getNextIndex(prev, 'next'));
          break;

        case expandKey:
          if (isNested && items[focusedIndex]?.children) {
            event.preventDefault();
            const item = items[focusedIndex];
            const isExpanded = expandedItems.has(item.id);
            setExpandedItems((prev) => {
              const next = new Set(prev);
              if (isExpanded) {
                next.delete(item.id);
              } else {
                next.add(item.id);
              }
              return next;
            });
            onExpand?.(item, !isExpanded);
          }
          break;

        case collapseKey:
          if (isNested && items[focusedIndex] && expandedItems.has(items[focusedIndex].id)) {
            event.preventDefault();
            const item = items[focusedIndex];
            if (item) {
              setExpandedItems((prev) => {
                const next = new Set(prev);
                next.delete(item.id);
                return next;
              });
              onExpand?.(item, false);
            }
          }
          break;

        case 'Enter':
        case ' ':
          event.preventDefault();
          const currentItem = items[focusedIndex];
          if (currentItem && !currentItem.disabled) {
            onSelect?.(currentItem, focusedIndex);
          }
          break;

        case 'Escape':
          event.preventDefault();
          onEscape?.();
          break;

        case 'Home':
          if (homeEndKeys) {
            event.preventDefault();
            let firstIndex = 0;
            if (skipDisabled) {
              while (items[firstIndex]?.disabled && firstIndex < items.length - 1) {
                firstIndex++;
              }
            }
            setFocusedIndex(firstIndex);
          }
          break;

        case 'End':
          if (homeEndKeys) {
            event.preventDefault();
            let lastIndex = items.length - 1;
            if (skipDisabled) {
              while (items[lastIndex]?.disabled && lastIndex > 0) {
                lastIndex--;
              }
            }
            setFocusedIndex(lastIndex);
          }
          break;

        case 'Tab':
          // Let Tab key work normally for focus management
          break;

        default:
          // Handle typeahead search
          if (event.key.length === 1 && !event.metaKey && !event.ctrlKey && !event.altKey) {
            handleTypeahead(event.key);
          }
          break;
      }
    },
    [
      orientation,
      isNested,
      items,
      focusedIndex,
      expandedItems,
      getNextIndex,
      onSelect,
      onExpand,
      onEscape,
      homeEndKeys,
      skipDisabled,
    ]
  );

  // Handle typeahead search
  const handleTypeahead = useCallback(
    (key: string) => {
      if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
      
      const newSearchBuffer = searchBuffer + key.toLowerCase();
      setSearchBuffer(newSearchBuffer);
      
      // Find matching item
      const matchingIndex = items.findIndex((item) =>
        item.label.toLowerCase().startsWith(newSearchBuffer)
      );
      
      if (matchingIndex !== -1 && items[matchingIndex] && (!skipDisabled || !items[matchingIndex].disabled)) {
        setFocusedIndex(matchingIndex);
      }
      
      onSearch?.(newSearchBuffer);
      
      // Clear search buffer after timeout
      searchTimeoutRef.current = setTimeout(() => {
        setSearchBuffer('');
      }, typeaheadTimeout);
    },
    [searchBuffer, items, skipDisabled, onSearch, typeaheadTimeout]
  );

  // Set up event listeners
  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    };
  }, [handleKeyDown]);

  // Focus management
  useEffect(() => {
    itemRefs.current[focusedIndex]?.focus();
  }, [focusedIndex]);

  // Reset focused index when items change
  useEffect(() => {
    if (focusedIndex >= items.length) {
      setFocusedIndex(Math.max(0, items.length - 1));
    }
  }, [items.length, focusedIndex]);

  // Focus trap management
  const createFocusTrap = useCallback((container: HTMLElement | null) => {
    if (!container) return;

    const focusableElements = container.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );

    const firstFocusable = focusableElements[0] as HTMLElement;
    const lastFocusable = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTrapFocus = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
          e.preventDefault();
          lastFocusable?.focus();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          e.preventDefault();
          firstFocusable?.focus();
        }
      }
    };

    container.addEventListener('keydown', handleTrapFocus);
    return () => container.removeEventListener('keydown', handleTrapFocus);
  }, []);

  // Utility functions for navigation
  const navigateToIndex = useCallback((index: number) => {
    if (index >= 0 && index < items.length) {
      setFocusedIndex(index);
    }
  }, [items.length]);

  const navigateToItem = useCallback((itemId: string) => {
    const index = items.findIndex((item) => item.id === itemId);
    if (index !== -1) {
      setFocusedIndex(index);
    }
  }, [items]);

  const navigateNext = useCallback(() => {
    setFocusedIndex((prev) => getNextIndex(prev, 'next'));
  }, [getNextIndex]);

  const navigatePrev = useCallback(() => {
    setFocusedIndex((prev) => getNextIndex(prev, 'prev'));
  }, [getNextIndex]);

  const expandItem = useCallback((itemId: string) => {
    setExpandedItems((prev) => new Set(prev).add(itemId));
  }, []);

  const collapseItem = useCallback((itemId: string) => {
    setExpandedItems((prev) => {
      const next = new Set(prev);
      next.delete(itemId);
      return next;
    });
  }, []);

  const toggleItem = useCallback((itemId: string) => {
    setExpandedItems((prev) => {
      const next = new Set(prev);
      if (next.has(itemId)) {
        next.delete(itemId);
      } else {
        next.add(itemId);
      }
      return next;
    });
  }, []);

  const expandAll = useCallback(() => {
    const allExpandable = items
      .filter((item) => item.children && item.children.length > 0)
      .map((item) => item.id);
    setExpandedItems(new Set(allExpandable));
  }, [items]);

  const collapseAll = useCallback(() => {
    setExpandedItems(new Set());
  }, []);

  return {
    focusedIndex,
    setFocusedIndex,
    expandedItems,
    searchBuffer,
    itemRefs,
    navigateToIndex,
    navigateToItem,
    navigateNext,
    navigatePrev,
    expandItem,
    collapseItem,
    toggleItem,
    expandAll,
    collapseAll,
    createFocusTrap,
    isItemExpanded: (itemId: string) => expandedItems.has(itemId),
    isItemFocused: (index: number) => focusedIndex === index,
  };
}