import { vi } from 'vitest';

// Emergency comprehensive Lucide React mock
const createEmergencyIconMock = (name: string) =>
  vi.fn().mockImplementation((props = {}) => {
    return {
      type: 'svg',
      props: {
        className: props.className || '',
        'data-testid': `${name.toLowerCase()}-icon`,
        'aria-hidden': true,
        ...props,
      },
      children: name, // For debugging
    };
  });

// Create a comprehensive icon list
const iconList = [
  'BarChart3',
  'Shield',
  'Filter',
  'Users',
  'Check',
  'X',
  'Upload',
  'Download',
  'Eye',
  'Edit',
  'Trash',
  'Plus',
  'Minus',
  'Search',
  'Settings',
  'User',
  'Home',
  'FileText',
  'BarChart',
  'PieChart',
  'TrendingUp',
  'TrendingDown',
  'AlertTriangle',
  'Info',
  'CheckCircle',
  'XCircle',
  'Clock',
  'Calendar',
  'Mail',
  'Phone',
  'MapPin',
  'Globe',
  'Lock',
  'Unlock',
  'Key',
  'Database',
  'Server',
  'Cloud',
  'Wifi',
  'Activity',
  'Zap',
  'Star',
  'Heart',
  'Bookmark',
  'Flag',
  'Tag',
  'Folder',
  'File',
  'Image',
  'Video',
  'Music',
  'Headphones',
  'Camera',
  'Printer',
  'Monitor',
  'Smartphone',
  'Tablet',
  'Laptop',
  'HardDrive',
  'Cpu',
  'MemoryStick',
  'Battery',
  'Power',
  'Plug',
  'Bluetooth',
  'Usb',
  'ChevronDown',
  'ChevronUp',
  'ChevronLeft',
  'ChevronRight',
  'ArrowUp',
  'ArrowDown',
  'ArrowLeft',
  'ArrowRight',
  'MoreHorizontal',
  'MoreVertical',
  'Menu',
  'Grid',
  'List',
  'Layout',
  'Sidebar',
  'Maximize',
  'Minimize',
  'Copy',
  'Clipboard',
  'Share',
  'ExternalLink',
  'Link',
  'Unlink',
  'Refresh',
  'RotateCw',
  'RotateCcw',
  'Repeat',
  'Shuffle',
  'Play',
  'Pause',
  'Stop',
  'SkipBack',
  'SkipForward',
  'FastForward',
  'Rewind',
  'Volume',
  'Volume1',
  'Volume2',
  'VolumeX',
  'Mic',
  'MicOff',
];

// Create the mock object
const LucideMocks: Record<string, ReturnType<typeof createEmergencyIconMock>> = {};
iconList.forEach((iconName) => {
  LucideMocks[iconName] = createEmergencyIconMock(iconName);
});

// Create a proxy for any missing icons
export const EmergencyLucideProxy = new Proxy(LucideMocks, {
  get(target, prop) {
    if (typeof prop === 'string' && prop in target) {
      return target[prop];
    }
    // Create a mock for any missing icon on the fly
    const newMock = createEmergencyIconMock(String(prop));
    if (typeof prop === 'string') {
      target[prop] = newMock;
    }
    return newMock;
  },
});
