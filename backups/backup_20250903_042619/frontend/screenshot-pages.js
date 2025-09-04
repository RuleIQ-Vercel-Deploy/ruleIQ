const { chromium } = require('playwright');

async function captureAllPages() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
  });

  const page = await context.newPage();

  // Create screenshots directory
  const fs = require('fs');
  const screenshotsDir = './screenshots';
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir);
  }

  const baseUrl = 'http://localhost:3000';

  try {
    console.log('📸 Starting visual documentation capture...');

    // 1. Landing/Home Page
    console.log('📸 Capturing landing page...');
    await page.goto(baseUrl);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/01-landing-page.png`, fullPage: true });

    // 2. Login Page
    console.log('📸 Capturing login page...');
    await page.goto(`${baseUrl}/login`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/02-login-page.png`, fullPage: true });

    // 3. Register Page
    console.log('📸 Capturing register page...');
    await page.goto(`${baseUrl}/register`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/03-register-page.png`, fullPage: true });

    // 4. Signup Page
    console.log('📸 Capturing signup page...');
    await page.goto(`${baseUrl}/signup`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/04-signup-page.png`, fullPage: true });

    // 5. Dashboard
    console.log('📸 Capturing dashboard...');
    await page.goto(`${baseUrl}/dashboard`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/05-dashboard.png`, fullPage: true });

    // 6. Assessments Page
    console.log('📸 Capturing assessments page...');
    await page.goto(`${baseUrl}/assessments`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/06-assessments-page.png`, fullPage: true });

    // 7. New Assessment
    console.log('📸 Capturing new assessment page...');
    await page.goto(`${baseUrl}/assessments/new`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/07-new-assessment.png`, fullPage: true });

    // 8. Business Profile
    console.log('📸 Capturing business profile page...');
    await page.goto(`${baseUrl}/business-profile`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/08-business-profile.png`, fullPage: true });

    // 9. Settings
    console.log('📸 Capturing settings page...');
    await page.goto(`${baseUrl}/settings`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/09-settings.png`, fullPage: true });

    // 10. Pricing Page
    console.log('📸 Capturing pricing page...');
    await page.goto(`${baseUrl}/pricing`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/10-pricing.png`, fullPage: true });

    // 11. Compliance Wizard
    console.log('📸 Capturing compliance wizard...');
    await page.goto(`${baseUrl}/compliance-wizard`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/11-compliance-wizard.png`, fullPage: true });

    // 12. Chat Interface
    console.log('📸 Capturing chat interface...');
    await page.goto(`${baseUrl}/chat`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/12-chat-interface.png`, fullPage: true });

    // 13. Reports
    console.log('📸 Capturing reports page...');
    await page.goto(`${baseUrl}/reports`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/13-reports.png`, fullPage: true });

    // 14. Policies
    console.log('📸 Capturing policies page...');
    await page.goto(`${baseUrl}/policies`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/14-policies.png`, fullPage: true });

    // 15. Evidence
    console.log('📸 Capturing evidence page...');
    await page.goto(`${baseUrl}/evidence`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/15-evidence.png`, fullPage: true });

    // 16. Analytics
    console.log('📸 Capturing analytics page...');
    await page.goto(`${baseUrl}/analytics`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/16-analytics.png`, fullPage: true });

    // 17. Team Settings
    console.log('📸 Capturing team settings...');
    await page.goto(`${baseUrl}/settings/team`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/17-team-settings.png`, fullPage: true });

    // 18. Billing Settings
    console.log('📸 Capturing billing settings...');
    await page.goto(`${baseUrl}/settings/billing`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/18-billing-settings.png`, fullPage: true });

    // 19. Integrations
    console.log('📸 Capturing integrations page...');
    await page.goto(`${baseUrl}/settings/integrations`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/19-integrations.png`, fullPage: true });

    // 20. Error States
    console.log('📸 Capturing 404 page...');
    await page.goto(`${baseUrl}/non-existent-page`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${screenshotsDir}/20-404-error.png`, fullPage: true });

    console.log('✅ All screenshots captured successfully!');
    console.log('📁 Screenshots saved to ./screenshots/');
  } catch (error) {
    console.error('❌ Error capturing screenshots:', error);
  } finally {
    await browser.close();
  }
}

captureAllPages();
