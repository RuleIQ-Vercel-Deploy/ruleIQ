# Manual Accessibility Testing Guide for ruleIQ

This guide provides comprehensive instructions for manual accessibility testing to ensure ruleIQ meets WCAG 2.2 AA standards and provides an excellent experience for all users.

## 🎯 Testing Objectives

- **WCAG 2.2 AA Compliance**: Meet international accessibility standards
- **Screen Reader Compatibility**: Ensure compatibility with NVDA, JAWS, VoiceOver
- **Keyboard Navigation**: Full functionality without mouse
- **Color Accessibility**: Support for color blindness and low vision
- **Cognitive Accessibility**: Clear, understandable interface

## 🛠️ Testing Tools

### Required Tools

- **Screen Readers**: NVDA (free), JAWS (trial), VoiceOver (macOS)
- **Browser Extensions**: axe DevTools, WAVE, Lighthouse
- **Color Tools**: Colour Contrast Analyser, Stark
- **Keyboard Testing**: Built-in browser tools

### Browser Setup

```bash
# Install browser extensions
- axe DevTools (Chrome/Firefox)
- WAVE Web Accessibility Evaluator
- Lighthouse (built into Chrome DevTools)
- Stark (Figma/browser extension)
```

## 📋 Testing Checklist

### 1. Keyboard Navigation Testing

#### Basic Navigation

- [ ] **Tab Order**: Logical tab sequence through all interactive elements
- [ ] **Focus Indicators**: Visible focus indicators on all focusable elements
- [ ] **Skip Links**: "Skip to main content" link works and is visible on focus
- [ ] **Trapped Focus**: Modal dialogs trap focus appropriately
- [ ] **No Keyboard Traps**: Users can navigate away from all elements

#### Specific Key Combinations

```
Tab          - Move to next focusable element
Shift+Tab    - Move to previous focusable element
Enter        - Activate buttons and links
Space        - Activate buttons, check checkboxes
Arrow Keys   - Navigate within components (menus, tabs)
Escape       - Close modals, cancel operations
Home/End     - Navigate to beginning/end of lists
```

#### Testing Steps

1. **Disconnect mouse** or use only keyboard
2. **Start from page top** and tab through entire page
3. **Verify focus order** matches visual layout
4. **Test all interactive elements** (buttons, links, forms, menus)
5. **Check modal behavior** (focus trapping, escape key)

### 2. Screen Reader Testing

#### NVDA Testing (Windows)

```bash
# Download NVDA (free)
https://www.nvaccess.org/download/

# Basic NVDA Commands
NVDA+Space     - Toggle speech mode
NVDA+T         - Read title
NVDA+B         - Read from cursor to end
H              - Navigate by headings
F              - Navigate by form fields
K              - Navigate by links
```

#### VoiceOver Testing (macOS)

```bash
# Enable VoiceOver
Cmd+F5 or System Preferences > Accessibility

# Basic VoiceOver Commands
VO+A           - Start reading
VO+Right/Left  - Navigate elements
VO+Space       - Activate element
VO+U           - Open rotor
VO+H           - Navigate headings
```

#### Testing Scenarios

1. **Page Structure**: Navigate by headings (H1, H2, H3)
2. **Form Fields**: Verify labels are announced correctly
3. **Error Messages**: Check error announcements
4. **Dynamic Content**: Test live regions and updates
5. **Images**: Verify alt text is meaningful
6. **Tables**: Check header associations

### 3. Visual Accessibility Testing

#### Color Contrast Testing

- [ ] **Text Contrast**: Minimum 4.5:1 for normal text
- [ ] **Large Text Contrast**: Minimum 3:1 for large text (18pt+)
- [ ] **UI Elements**: Minimum 3:1 for interactive elements
- [ ] **Focus Indicators**: Minimum 3:1 contrast with background

#### Color Blindness Testing

```bash
# Browser tools for color blindness simulation
Chrome DevTools > Rendering > Emulate vision deficiencies:
- Protanopia (red-blind)
- Deuteranopia (green-blind)
- Tritanopia (blue-blind)
- Achromatopsia (no color)
```

#### Testing Steps

1. **Use contrast analyzer** on all text/background combinations
2. **Simulate color blindness** and verify information is still accessible
3. **Check focus indicators** are visible in all states
4. **Test without color** - ensure meaning isn't conveyed by color alone

### 4. Form Accessibility Testing

#### Form Structure

- [ ] **Labels**: All inputs have associated labels
- [ ] **Required Fields**: Clearly marked and announced
- [ ] **Error Messages**: Associated with fields via aria-describedby
- [ ] **Fieldsets**: Related fields grouped with legend
- [ ] **Instructions**: Clear, accessible help text

#### Testing Process

1. **Navigate forms with keyboard only**
2. **Use screen reader** to verify label announcements
3. **Test error states** - submit invalid forms
4. **Check required field indicators**
5. **Verify help text associations**

### 5. Dynamic Content Testing

#### Live Regions

- [ ] **Status Updates**: Use aria-live="polite" for non-urgent updates
- [ ] **Error Alerts**: Use aria-live="assertive" for urgent messages
- [ ] **Loading States**: Announce loading and completion
- [ ] **Content Changes**: Dynamic updates are announced

#### Testing Scenarios

1. **Form Submission**: Success/error messages announced
2. **Search Results**: Results count and updates announced
3. **Assessment Progress**: Progress updates announced
4. **File Uploads**: Upload status and completion announced

## 🧪 Component-Specific Testing

### Authentication Forms

```bash
# Test login/register forms
1. Navigate with keyboard only
2. Verify password visibility toggle is accessible
3. Check error message announcements
4. Test "Remember me" checkbox
5. Verify forgot password link
```

### Business Profile Wizard

```bash
# Test multi-step wizard
1. Check step indicators are accessible
2. Verify progress announcements
3. Test navigation between steps
4. Check form validation messages
5. Test conditional fields
```

### Assessment Interface

```bash
# Test assessment questions
1. Navigate questions with keyboard
2. Check question numbering announcements
3. Test radio button/checkbox groups
4. Verify progress indicators
5. Test skip/back functionality
```

### Evidence Management

```bash
# Test file upload interface
1. Check drag-and-drop accessibility
2. Test file selection with keyboard
3. Verify upload progress announcements
4. Test file list navigation
5. Check delete/edit actions
```

### Dashboard Widgets

```bash
# Test dashboard components
1. Navigate widget grid with keyboard
2. Check chart accessibility (data tables)
3. Test widget customization
4. Verify data announcements
5. Test responsive behavior
```

## 🔍 Testing Procedures

### Daily Testing Routine

1. **Automated Tests**: Run jest-axe tests with every build
2. **Keyboard Testing**: Test new features with keyboard only
3. **Screen Reader Spot Checks**: Test critical user flows
4. **Contrast Verification**: Check new color combinations

### Weekly Testing Routine

1. **Full Screen Reader Testing**: Complete user journeys
2. **Cross-Browser Testing**: Test in Chrome, Firefox, Safari
3. **Mobile Accessibility**: Test on mobile devices
4. **Performance Impact**: Check accessibility features don't slow down app

### Release Testing Routine

1. **Complete Manual Testing**: All components and flows
2. **Third-Party Audit**: Consider external accessibility audit
3. **User Testing**: Test with actual users with disabilities
4. **Documentation Update**: Update accessibility documentation

## 📊 Testing Documentation

### Test Report Template

```markdown
# Accessibility Test Report

**Date**: [Date]
**Tester**: [Name]
**Component/Page**: [Component name]
**Testing Tools**: [Tools used]

## Test Results

- [ ] Keyboard Navigation: Pass/Fail
- [ ] Screen Reader: Pass/Fail
- [ ] Color Contrast: Pass/Fail
- [ ] WCAG Compliance: Pass/Fail

## Issues Found

1. **Issue**: [Description]
   **Severity**: High/Medium/Low
   **WCAG Criterion**: [e.g., 2.1.1]
   **Steps to Reproduce**: [Steps]
   **Suggested Fix**: [Solution]

## Recommendations

[Improvement suggestions]
```

### Issue Tracking

- **High Priority**: Blocks screen reader users or keyboard navigation
- **Medium Priority**: Reduces usability but doesn't block access
- **Low Priority**: Minor improvements or enhancements

## 🎓 Training Resources

### WCAG Guidelines

- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/)
- [WebAIM Screen Reader Testing](https://webaim.org/articles/screenreader_testing/)
- [Keyboard Accessibility](https://webaim.org/techniques/keyboard/)

### Screen Reader Guides

- [NVDA User Guide](https://www.nvaccess.org/files/nvda/documentation/userGuide.html)
- [VoiceOver User Guide](https://support.apple.com/guide/voiceover/welcome/mac)
- [JAWS Documentation](https://support.freedomscientific.com/Teachers/Manuals/JAWS)

### Testing Tools

- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE Web Accessibility Evaluator](https://wave.webaim.org/)
- [Colour Contrast Analyser](https://www.tpgi.com/color-contrast-checker/)

## 🚀 Implementation Tips

### Quick Wins

1. **Add skip links** to all pages
2. **Ensure focus indicators** are visible
3. **Add alt text** to all images
4. **Associate labels** with form fields
5. **Use semantic HTML** elements

### Common Pitfalls

- **Missing focus indicators** on custom components
- **Inadequate color contrast** on interactive elements
- **Missing error message associations** in forms
- **Inaccessible modal dialogs** without focus trapping
- **Dynamic content** without live region announcements

### Best Practices

- **Test early and often** during development
- **Include accessibility** in definition of done
- **Train team members** on accessibility basics
- **Use automated tools** but don't rely on them exclusively
- **Get feedback** from users with disabilities

## 📞 Support and Resources

### Internal Resources

- Accessibility testing utilities: `tests/accessibility/utils.ts`
- Automated tests: `tests/accessibility/accessibility.test.tsx`
- Component documentation: Include accessibility notes

### External Support

- **WebAIM**: Free accessibility resources and training
- **Deque University**: Comprehensive accessibility courses
- **A11y Project**: Community-driven accessibility resources
- **Government Guidelines**: Section 508, EN 301 549 standards

Remember: Accessibility is not a one-time task but an ongoing commitment to inclusive design. Regular testing and continuous improvement ensure ruleIQ remains accessible to all users.
