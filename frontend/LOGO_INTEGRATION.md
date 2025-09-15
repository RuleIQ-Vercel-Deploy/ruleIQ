# Logo Integration Instructions

## Files to Save

Please save the logo images you provided to the following locations:

1. **Light Logo** (for dark backgrounds):
   - Save as: `/public/ruleiq-logo-light.png`
   - This is the version with transparent background

2. **Dark Logo** (for light backgrounds):
   - Save as: `/public/ruleiq-logo-dark.png`
   - This is the version with black background

## Current Implementation

The logo has been integrated into:

### 1. Header Component (`/components/ui/header.tsx`)
- Uses the dark version for the main navigation
- Includes hover effect (scale: 1.05)
- Maintains proper aspect ratio
- Circuit board pattern in "IQ" is preserved

### 2. Design System (`/DESIGN_SYSTEM.md`)
- Logo usage guidelines added
- Minimum sizing requirements
- Clear space requirements
- Implementation examples

## Logo Features

The RuleIQ logo beautifully combines:
- Clean, modern typography
- Circuit board pattern integrated into "IQ"
- Silver gradient on the "I" 
- Technical sophistication matching the compliance automation theme

## Testing

After saving the logo files:
1. The header will automatically display the logo
2. The circuit board pattern should be clearly visible
3. Hover effects will apply on the logo link

## Alternative SVG Option

If you have SVG versions of the logos, you can save them as:
- `/public/ruleiq-logo-light.svg`
- `/public/ruleiq-logo-dark.svg`

Then update the Header component to use SVG for better scalability.
