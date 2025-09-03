import { vi } from 'vitest';

// Create mock components for all lucide-react icons
const createMockIcon = (name: string) => {
  const MockIcon = vi.fn(({ className, ...props }) => {
    return {
      type: 'svg',
      props: {
        'data-testid': `${name.toLowerCase()}-icon`,
        className,
        ...props,
      },
    };
  });
  MockIcon.displayName = name;
  return MockIcon;
};

// Export commonly used icons
export const ThumbsUp = createMockIcon('ThumbsUp');
export const ThumbsDown = createMockIcon('ThumbsDown');
export const HelpCircle = createMockIcon('HelpCircle');
export const Info = createMockIcon('Info');
export const AlertCircle = createMockIcon('AlertCircle');
export const CheckCircle = createMockIcon('CheckCircle');
export const X = createMockIcon('X');
export const Plus = createMockIcon('Plus');
export const Minus = createMockIcon('Minus');
export const Edit = createMockIcon('Edit');
export const Trash = createMockIcon('Trash');
export const Save = createMockIcon('Save');
export const Upload = createMockIcon('Upload');
export const Download = createMockIcon('Download');
export const Search = createMockIcon('Search');
export const Filter = createMockIcon('Filter');
export const Settings = createMockIcon('Settings');
export const User = createMockIcon('User');
export const Lock = createMockIcon('Lock');
export const Unlock = createMockIcon('Unlock');
export const Eye = createMockIcon('Eye');
export const EyeOff = createMockIcon('EyeOff');
export const ChevronDown = createMockIcon('ChevronDown');
export const ChevronUp = createMockIcon('ChevronUp');
export const ChevronLeft = createMockIcon('ChevronLeft');
export const ChevronRight = createMockIcon('ChevronRight');
export const ArrowLeft = createMockIcon('ArrowLeft');
export const ArrowRight = createMockIcon('ArrowRight');
export const ArrowUp = createMockIcon('ArrowUp');
export const ArrowDown = createMockIcon('ArrowDown');
export const Menu = createMockIcon('Menu');
export const MoreHorizontal = createMockIcon('MoreHorizontal');
export const MoreVertical = createMockIcon('MoreVertical');
export const Calendar = createMockIcon('Calendar');
export const Clock = createMockIcon('Clock');
export const Mail = createMockIcon('Mail');
export const Phone = createMockIcon('Phone');
export const Home = createMockIcon('Home');
export const Building = createMockIcon('Building');
export const FileText = createMockIcon('FileText');
export const File = createMockIcon('File');
export const Folder = createMockIcon('Folder');
export const Image = createMockIcon('Image');
export const Video = createMockIcon('Video');
export const Music = createMockIcon('Music');
export const Headphones = createMockIcon('Headphones');
export const Camera = createMockIcon('Camera');
export const Mic = createMockIcon('Mic');
export const MicOff = createMockIcon('MicOff');
export const Volume2 = createMockIcon('Volume2');
export const VolumeX = createMockIcon('VolumeX');
export const Play = createMockIcon('Play');
export const Pause = createMockIcon('Pause');
export const Stop = createMockIcon('Stop');
export const SkipBack = createMockIcon('SkipBack');
export const SkipForward = createMockIcon('SkipForward');
export const Repeat = createMockIcon('Repeat');
export const Shuffle = createMockIcon('Shuffle');
export const Heart = createMockIcon('Heart');
export const Star = createMockIcon('Star');
export const Bookmark = createMockIcon('Bookmark');
export const Share = createMockIcon('Share');
export const Copy = createMockIcon('Copy');
export const Link = createMockIcon('Link');
export const ExternalLink = createMockIcon('ExternalLink');
export const Maximize = createMockIcon('Maximize');
export const Minimize = createMockIcon('Minimize');
export const RefreshCw = createMockIcon('RefreshCw');
export const RotateCcw = createMockIcon('RotateCcw');
export const RotateCw = createMockIcon('RotateCw');
export const Zap = createMockIcon('Zap');
export const Wifi = createMockIcon('Wifi');
export const WifiOff = createMockIcon('WifiOff');
export const Battery = createMockIcon('Battery');
export const BatteryLow = createMockIcon('BatteryLow');
export const Bluetooth = createMockIcon('Bluetooth');
export const Smartphone = createMockIcon('Smartphone');
export const Tablet = createMockIcon('Tablet');
export const Laptop = createMockIcon('Laptop');
export const Monitor = createMockIcon('Monitor');
export const Tv = createMockIcon('Tv');
export const Printer = createMockIcon('Printer');
export const HardDrive = createMockIcon('HardDrive');
export const Server = createMockIcon('Server');
export const Database = createMockIcon('Database');
export const Cloud = createMockIcon('Cloud');
export const CloudOff = createMockIcon('CloudOff');
export const Globe = createMockIcon('Globe');
export const MapPin = createMockIcon('MapPin');
export const Navigation = createMockIcon('Navigation');
export const Compass = createMockIcon('Compass');
export const Map = createMockIcon('Map');
export const Layers = createMockIcon('Layers');
export const Package = createMockIcon('Package');
export const ShoppingCart = createMockIcon('ShoppingCart');
export const ShoppingBag = createMockIcon('ShoppingBag');
export const CreditCard = createMockIcon('CreditCard');
export const DollarSign = createMockIcon('DollarSign');
export const TrendingUp = createMockIcon('TrendingUp');
export const TrendingDown = createMockIcon('TrendingDown');
export const BarChart = createMockIcon('BarChart');
export const PieChart = createMockIcon('PieChart');
export const Activity = createMockIcon('Activity');
export const Target = createMockIcon('Target');
export const Award = createMockIcon('Award');
export const Gift = createMockIcon('Gift');
export const Flag = createMockIcon('Flag');
export const Tag = createMockIcon('Tag');
export const Hash = createMockIcon('Hash');
export const AtSign = createMockIcon('AtSign');
export const Percent = createMockIcon('Percent');
export const Type = createMockIcon('Type');
export const Bold = createMockIcon('Bold');
export const Italic = createMockIcon('Italic');
export const Underline = createMockIcon('Underline');
export const AlignLeft = createMockIcon('AlignLeft');
export const AlignCenter = createMockIcon('AlignCenter');
export const AlignRight = createMockIcon('AlignRight');
export const AlignJustify = createMockIcon('AlignJustify');
export const List = createMockIcon('List');
export const Grid = createMockIcon('Grid');
export const Columns = createMockIcon('Columns');
export const Sidebar = createMockIcon('Sidebar');
export const Layout = createMockIcon('Layout');
export const Square = createMockIcon('Square');
export const Circle = createMockIcon('Circle');
export const Triangle = createMockIcon('Triangle');
export const Hexagon = createMockIcon('Hexagon');
export const Octagon = createMockIcon('Octagon');
export const Pentagon = createMockIcon('Pentagon');
export const Diamond = createMockIcon('Diamond');
export const Droplet = createMockIcon('Droplet');
export const Flame = createMockIcon('Flame');
export const Sun = createMockIcon('Sun');
export const Moon = createMockIcon('Moon');
export const CloudRain = createMockIcon('CloudRain');
export const CloudSnow = createMockIcon('CloudSnow');
export const Thermometer = createMockIcon('Thermometer');
export const Umbrella = createMockIcon('Umbrella');
export const Wind = createMockIcon('Wind');
export const Sunrise = createMockIcon('Sunrise');
export const Sunset = createMockIcon('Sunset');

// Default export for any icon not explicitly listed
export default new Proxy(
  {},
  {
    get: (target, prop) => {
      if (typeof prop === 'string') {
        return createMockIcon(prop);
      }
      return undefined;
    },
  },
);
