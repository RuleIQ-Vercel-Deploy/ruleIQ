#!/bin/bash
# Final Targeted Fix - Address remaining critical issues

set -e

echo "🎯 FINAL TARGETED FIX: Addressing remaining critical issues..."

cd frontend

# 1. Fix HTMLFormElement.prototype.requestSubmit issue properly
echo "📋 Step 1: Fixing HTMLFormElement.prototype.requestSubmit properly..."

# Replace the existing mock in setup.ts
cat > tests/setup-htmlform-fix.ts << 'EOF'
// Proper HTMLFormElement.prototype.requestSubmit polyfill
if (!HTMLFormElement.prototype.requestSubmit) {
  HTMLFormElement.prototype.requestSubmit = function(submitter) {
    if (submitter && submitter.form !== this) {
      throw new DOMException('The specified element is not a descendant of this form element', 'NotFoundError');
    }
    
    // Create and dispatch submit event
    const submitEvent = new Event('submit', {
      bubbles: true,
      cancelable: true
    });
    
    // Set submitter if provided
    if (submitter) {
      Object.defineProperty(submitEvent, 'submitter', {
        value: submitter,
        configurable: true
      });
    }
    
    this.dispatchEvent(submitEvent);
  };
}
EOF

# Add this to the beginning of setup.ts
if [ -f "tests/setup.ts" ]; then
    # Create a temporary file with the fix at the beginning
    cat tests/setup-htmlform-fix.ts tests/setup.ts > tests/setup-temp.ts
    mv tests/setup-temp.ts tests/setup.ts
    rm -f tests/setup-htmlform-fix.ts
fi

echo "✅ HTMLFormElement.prototype.requestSubmit fixed"

# 2. Add missing Lucide React icons
echo "📋 Step 2: Adding missing Lucide React icons..."

# Update the Lucide mock to include ALL missing icons
cat > tests/mocks/lucide-react-complete.ts << 'EOF'
import { vi } from 'vitest';

// Create a comprehensive mock for all Lucide React icons
const createIconMock = (name: string) => 
  vi.fn().mockImplementation((props = {}) => ({
    type: 'svg',
    props: {
      className: props.className || '',
      'data-testid': `${name.toLowerCase()}-icon`,
      ...props
    }
  }));

// Export ALL possible Lucide icons (comprehensive list)
export const LucideIconMocks = {
  // Recently missing icons
  Users: createIconMock('Users'),
  BarChart3: createIconMock('BarChart3'),
  Shield: createIconMock('Shield'),
  Filter: createIconMock('Filter'),
  
  // Comprehensive icon list
  Activity: createIconMock('Activity'),
  AlertTriangle: createIconMock('AlertTriangle'),
  ArrowDown: createIconMock('ArrowDown'),
  ArrowLeft: createIconMock('ArrowLeft'),
  ArrowRight: createIconMock('ArrowRight'),
  ArrowUp: createIconMock('ArrowUp'),
  BarChart: createIconMock('BarChart'),
  Battery: createIconMock('Battery'),
  Bell: createIconMock('Bell'),
  Bluetooth: createIconMock('Bluetooth'),
  Bookmark: createIconMock('Bookmark'),
  Calendar: createIconMock('Calendar'),
  Camera: createIconMock('Camera'),
  Check: createIconMock('Check'),
  CheckCircle: createIconMock('CheckCircle'),
  ChevronDown: createIconMock('ChevronDown'),
  ChevronLeft: createIconMock('ChevronLeft'),
  ChevronRight: createIconMock('ChevronRight'),
  ChevronUp: createIconMock('ChevronUp'),
  Circle: createIconMock('Circle'),
  Clipboard: createIconMock('Clipboard'),
  Clock: createIconMock('Clock'),
  Cloud: createIconMock('Cloud'),
  Code: createIconMock('Code'),
  Copy: createIconMock('Copy'),
  Cpu: createIconMock('Cpu'),
  Database: createIconMock('Database'),
  Download: createIconMock('Download'),
  Edit: createIconMock('Edit'),
  ExternalLink: createIconMock('ExternalLink'),
  Eye: createIconMock('Eye'),
  EyeOff: createIconMock('EyeOff'),
  FastForward: createIconMock('FastForward'),
  File: createIconMock('File'),
  FileText: createIconMock('FileText'),
  Flag: createIconMock('Flag'),
  Folder: createIconMock('Folder'),
  Globe: createIconMock('Globe'),
  Grid: createIconMock('Grid'),
  HardDrive: createIconMock('HardDrive'),
  Headphones: createIconMock('Headphones'),
  Heart: createIconMock('Heart'),
  Home: createIconMock('Home'),
  Image: createIconMock('Image'),
  Info: createIconMock('Info'),
  Key: createIconMock('Key'),
  Laptop: createIconMock('Laptop'),
  Layout: createIconMock('Layout'),
  Link: createIconMock('Link'),
  List: createIconMock('List'),
  Lock: createIconMock('Lock'),
  Mail: createIconMock('Mail'),
  MapPin: createIconMock('MapPin'),
  Maximize: createIconMock('Maximize'),
  MemoryStick: createIconMock('MemoryStick'),
  Menu: createIconMock('Menu'),
  Mic: createIconMock('Mic'),
  MicOff: createIconMock('MicOff'),
  Minimize: createIconMock('Minimize'),
  Minus: createIconMock('Minus'),
  Monitor: createIconMock('Monitor'),
  MoreHorizontal: createIconMock('MoreHorizontal'),
  MoreVertical: createIconMock('MoreVertical'),
  Music: createIconMock('Music'),
  Pause: createIconMock('Pause'),
  Phone: createIconMock('Phone'),
  PieChart: createIconMock('PieChart'),
  Play: createIconMock('Play'),
  Plug: createIconMock('Plug'),
  Plus: createIconMock('Plus'),
  Power: createIconMock('Power'),
  Printer: createIconMock('Printer'),
  Refresh: createIconMock('Refresh'),
  Repeat: createIconMock('Repeat'),
  Rewind: createIconMock('Rewind'),
  RotateCcw: createIconMock('RotateCcw'),
  RotateCw: createIconMock('RotateCw'),
  Search: createIconMock('Search'),
  Server: createIconMock('Server'),
  Settings: createIconMock('Settings'),
  Share: createIconMock('Share'),
  Shuffle: createIconMock('Shuffle'),
  Sidebar: createIconMock('Sidebar'),
  SkipBack: createIconMock('SkipBack'),
  SkipForward: createIconMock('SkipForward'),
  Smartphone: createIconMock('Smartphone'),
  Star: createIconMock('Star'),
  Stop: createIconMock('Stop'),
  Tablet: createIconMock('Tablet'),
  Tag: createIconMock('Tag'),
  Trash: createIconMock('Trash'),
  TrendingDown: createIconMock('TrendingDown'),
  TrendingUp: createIconMock('TrendingUp'),
  Unlink: createIconMock('Unlink'),
  Unlock: createIconMock('Unlock'),
  Upload: createIconMock('Upload'),
  User: createIconMock('User'),
  Usb: createIconMock('Usb'),
  Video: createIconMock('Video'),
  Volume: createIconMock('Volume'),
  Volume1: createIconMock('Volume1'),
  Volume2: createIconMock('Volume2'),
  VolumeX: createIconMock('VolumeX'),
  Wifi: createIconMock('Wifi'),
  X: createIconMock('X'),
  XCircle: createIconMock('XCircle'),
  Zap: createIconMock('Zap'),
  
  // Default fallback for any missing icons
  default: createIconMock('Default')
};

// Create a proxy to handle any missing icons dynamically
export const LucideProxy = new Proxy(LucideIconMocks, {
  get(target, prop) {
    if (prop in target) {
      return target[prop as keyof typeof target];
    }
    // Create a mock for any missing icon on the fly
    console.log(`Creating mock for missing Lucide icon: ${String(prop)}`);
    return createIconMock(String(prop));
  }
});
EOF

# Update setup.ts to use the proxy
cat >> tests/setup.ts << 'EOF'

// Import and use comprehensive Lucide React mock with proxy
import { LucideProxy } from './mocks/lucide-react-complete';

vi.mock('lucide-react', () => LucideProxy);
EOF

echo "✅ Comprehensive Lucide React icons added with proxy fallback"

# 3. Fix user-workflows.test.tsx syntax error completely
echo "📋 Step 3: Fixing user-workflows.test.tsx syntax error completely..."

if [ -f "tests/integration/user-workflows.test.tsx" ]; then
    # Fix the specific syntax error on line 662
    sed -i 's/const { default: LoginPage } = await import/const LoginPageModule = await import/g' tests/integration/user-workflows.test.tsx
    sed -i 's/const LoginPageModule = await import(\(.*\));/const LoginPageModule = await import(\1);\n        const LoginPage = LoginPageModule.default;/g' tests/integration/user-workflows.test.tsx
    
    echo "✅ User workflows syntax error completely fixed"
fi

# 4. Create a comprehensive AI service mock
echo "📋 Step 4: Creating comprehensive AI service mock..."

cat > tests/mocks/ai-service-mock.ts << 'EOF'
import { vi } from 'vitest';

// Comprehensive AI service mock
export const mockAIService = {
  generateFollowUpQuestions: vi.fn().mockResolvedValue([
    'What is your data retention policy?',
    'How do you handle data breaches?',
    'Do you have employee training programs?'
  ]),
  
  getEnhancedResponse: vi.fn().mockResolvedValue({
    response: 'This is a mock AI response',
    confidence: 0.85,
    suggestions: ['Consider implementing automated data deletion']
  }),
  
  analyzeCompliance: vi.fn().mockResolvedValue({
    score: 85,
    recommendations: ['Improve data retention policies'],
    risks: ['Missing employee training records']
  }),
  
  // Add timeout handling
  generateFollowUpQuestionsWithTimeout: vi.fn().mockImplementation(async (timeout = 5000) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          'What is your data retention policy?',
          'How do you handle data breaches?',
          'Do you have employee training programs?'
        ]);
      }, 100); // Quick response to avoid timeouts
    });
  })
};

// Mock the AI service module
vi.mock('@/lib/services/ai-service', () => ({
  AIService: mockAIService,
  default: mockAIService
}));

// Mock AI-related utilities
vi.mock('@/lib/assessment-engine/QuestionnaireEngine', () => ({
  QuestionnaireEngine: {
    generateAIFollowUpQuestions: mockAIService.generateFollowUpQuestions,
    getEnhancedAIResponse: mockAIService.getEnhancedResponse
  }
}));
EOF

# Add AI service mock to setup
cat >> tests/setup.ts << 'EOF'

// Import AI service mock
import './mocks/ai-service-mock';
EOF

echo "✅ Comprehensive AI service mock created"

echo "🎉 FINAL TARGETED FIX COMPLETED!"
echo ""
echo "📊 Summary of targeted fixes:"
echo "✅ HTMLFormElement.prototype.requestSubmit properly polyfilled"
echo "✅ Comprehensive Lucide React icons with proxy fallback"
echo "✅ User workflows syntax error completely resolved"
echo "✅ AI service mock with timeout handling"
echo ""
echo "🚀 Expected result: Significant improvement in test pass rate"
echo "Run: pnpm test --run to verify targeted fixes"

cd ..
echo "✅ Final targeted test fix completed!"
