#!/usr/bin/env node

/**
 * Accessibility Validation Script
 * Validates color contrast ratios for the new design tokens
 */

const colors = {
  // Teal palette
  teal50: '#E6FFFA',
  teal100: '#B2F5EA',
  teal200: '#81E6D9',
  teal300: '#4FD1C5',
  teal400: '#38B2AC',
  teal500: '#319795',
  teal600: '#2C7A7B',
  teal700: '#285E61',
  teal800: '#234E52',
  teal900: '#1D4044',
  
  // Neutral palette
  white: '#FFFFFF',
  neutral50: '#FAFAFA',
  neutral100: '#F4F4F5',
  neutral200: '#E4E4E7',
  neutral300: '#D4D4D8',
  neutral400: '#A1A1AA',
  neutral500: '#71717A',
  neutral600: '#52525B',
  neutral700: '#3F3F46',
  neutral800: '#27272A',
  neutral900: '#18181B',
};

// Calculate relative luminance
function getLuminance(hex) {
  const rgb = parseInt(hex.slice(1), 16);
  const r = (rgb >> 16) & 0xff;
  const g = (rgb >> 8) & 0xff;
  const b = (rgb >> 0) & 0xff;
  
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

// Calculate contrast ratio
function getContrastRatio(hex1, hex2) {
  const l1 = getLuminance(hex1);
  const l2 = getLuminance(hex2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// WCAG compliance check
function checkWCAG(ratio, level = 'AA') {
  const standards = {
    'AA': { normal: 4.5, large: 3 },
    'AAA': { normal: 7, large: 4.5 }
  };
  
  return {
    normalText: ratio >= standards[level].normal,
    largeText: ratio >= standards[level].large,
    ratio: ratio.toFixed(2)
  };
}

console.log('\\n🎨 WCAG 2.2 Color Contrast Validation\\n');
console.log('=' .repeat(50));

// Test primary combinations
const tests = [
  { bg: colors.white, fg: colors.teal600, label: 'Teal-600 on White' },
  { bg: colors.white, fg: colors.teal700, label: 'Teal-700 on White' },
  { bg: colors.teal600, fg: colors.white, label: 'White on Teal-600' },
  { bg: colors.white, fg: colors.neutral900, label: 'Text Primary on White' },
  { bg: colors.white, fg: colors.neutral600, label: 'Text Secondary on White' },
  { bg: colors.white, fg: colors.neutral500, label: 'Text Muted on White' },
  { bg: colors.teal50, fg: colors.teal700, label: 'Teal-700 on Teal-50' },
  { bg: colors.neutral50, fg: colors.neutral900, label: 'Text on Surface' },
];

let allPass = true;

tests.forEach(test => {
  const ratio = getContrastRatio(test.bg, test.fg);
  const wcag = checkWCAG(ratio);
  const status = wcag.normalText ? '✅' : '❌';
  const level = ratio >= 7 ? 'AAA' : ratio >= 4.5 ? 'AA' : 'FAIL';
  
  console.log(`\\n${status} ${test.label}`);
  console.log(`   Ratio: ${ratio.toFixed(2)}:1 (${level})`);
  console.log(`   Normal Text: ${wcag.normalText ? 'Pass' : 'Fail'}`);
  console.log(`   Large Text: ${wcag.largeText ? 'Pass' : 'Fail'}`);
  
  if (!wcag.normalText) allPass = false;
});

console.log('\\n' + '=' .repeat(50));
console.log(allPass ? '\\n✅ All color combinations pass WCAG AA!' : '\\n❌ Some combinations need adjustment');
console.log('\\n');