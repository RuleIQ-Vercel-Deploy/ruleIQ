// Manual OAuth2 Authentication Test Script
// Run this in the browser console to test authentication flow

console.log('🚀 Starting OAuth2 Authentication Test...');

// Test helper functions
const testAuth = {
  // Test 1: Check if auth store is available
  checkAuthStore() {
    console.log('📋 Test 1: Checking Auth Store availability...');
    try {
      const store = window.__AUTH_STORE__ || window.useAuthStore;
      if (store) {
        console.log('✅ Auth store is available');
        return true;
      } else {
        console.log('❌ Auth store not found in global scope');
        return false;
      }
    } catch (error) {
      console.log('❌ Error accessing auth store:', error);
      return false;
    }
  },

  // Test 2: Check localStorage for auth data
  checkLocalStorage() {
    console.log('📋 Test 2: Checking localStorage for auth data...');
    try {
      const authData = localStorage.getItem('auth-storage');
      if (authData) {
        const parsed = JSON.parse(authData);
        console.log('✅ Auth data found in localStorage:', {
          hasUser: !!parsed.state?.user,
          hasTokens: !!parsed.state?.tokens,
          isAuthenticated: parsed.state?.isAuthenticated,
        });
        return parsed;
      } else {
        console.log('ℹ️ No auth data in localStorage');
        return null;
      }
    } catch (error) {
      console.log('❌ Error reading localStorage:', error);
      return null;
    }
  },

  // Test 3: Check if we're on the login page
  checkLoginPage() {
    console.log('📋 Test 3: Checking if on login page...');
    const loginForm = document.querySelector('form');
    const emailInput = document.querySelector('input[type="email"], input[id="email"]');
    const passwordInput = document.querySelector('input[type="password"], input[id="password"]');
    const loginButton = document.querySelector('button[type="submit"]');

    const isLoginPage = !!(loginForm && emailInput && passwordInput && loginButton);
    console.log(`${isLoginPage ? '✅' : '❌'} Login page elements:`, {
      form: !!loginForm,
      emailInput: !!emailInput,
      passwordInput: !!passwordInput,
      loginButton: !!loginButton,
    });

    return isLoginPage;
  },

  // Test 4: Simulate login process
  async simulateLogin(email = 'test@example.com', password = 'password123') {
    console.log('📋 Test 4: Simulating login process...');

    const emailInput = document.querySelector('input[type="email"], input[id="email"]');
    const passwordInput = document.querySelector('input[type="password"], input[id="password"]');
    const loginButton = document.querySelector('button[type="submit"]');

    if (!emailInput || !passwordInput || !loginButton) {
      console.log('❌ Login form elements not found');
      return false;
    }

    try {
      // Fill in credentials
      emailInput.value = email;
      emailInput.dispatchEvent(new Event('input', { bubbles: true }));
      emailInput.dispatchEvent(new Event('change', { bubbles: true }));

      passwordInput.value = password;
      passwordInput.dispatchEvent(new Event('input', { bubbles: true }));
      passwordInput.dispatchEvent(new Event('change', { bubbles: true }));

      console.log('✅ Credentials filled in');

      // Click login button
      loginButton.click();
      console.log('✅ Login button clicked');

      // Wait for response
      await new Promise((resolve) => setTimeout(resolve, 2000));

      return true;
    } catch (error) {
      console.log('❌ Error during login simulation:', error);
      return false;
    }
  },

  // Test 5: Check network requests
  monitorNetworkRequests() {
    console.log('📋 Test 5: Setting up network request monitoring...');

    // Override fetch to monitor requests
    const originalFetch = window.fetch;
    const requests = [];

    window.fetch = function (...args) {
      const url = args[0];
      const options = args[1] || {};

      requests.push({
        url,
        method: options.method || 'GET',
        headers: options.headers || {},
        timestamp: new Date().toISOString(),
      });

      console.log('🌐 Network Request:', {
        method: options.method || 'GET',
        url: url,
        hasAuth: !!(options.headers && options.headers['Authorization']),
      });

      return originalFetch.apply(this, args);
    };

    return {
      getRequests: () => requests,
      restore: () => {
        window.fetch = originalFetch;
      },
    };
  },

  // Test 6: Check protected route access
  async testProtectedRoute() {
    console.log('📋 Test 6: Testing protected route access...');

    try {
      // Try to navigate to dashboard
      const currentUrl = window.location.href;
      window.history.pushState({}, '', '/dashboard');

      await new Promise((resolve) => setTimeout(resolve, 1000));

      const newUrl = window.location.href;
      const wasRedirected = newUrl !== currentUrl + 'dashboard' && newUrl.includes('/dashboard');

      console.log(`${wasRedirected ? '✅' : 'ℹ️'} Protected route test:`, {
        originalUrl: currentUrl,
        attemptedUrl: currentUrl + 'dashboard',
        finalUrl: newUrl,
        accessGranted: newUrl.includes('/dashboard'),
      });

      return newUrl.includes('/dashboard');
    } catch (error) {
      console.log('❌ Error testing protected route:', error);
      return false;
    }
  },

  // Test 7: Full authentication flow test
  async runFullTest() {
    console.log('🎯 Running full authentication flow test...');

    const results = {
      authStoreAvailable: this.checkAuthStore(),
      localStorageData: this.checkLocalStorage(),
      isOnLoginPage: this.checkLoginPage(),
      networkMonitor: this.monitorNetworkRequests(),
    };

    if (results.isOnLoginPage) {
      console.log('🔐 Attempting login...');
      const loginSuccess = await this.simulateLogin();
      results.loginAttempted = loginSuccess;

      if (loginSuccess) {
        await new Promise((resolve) => setTimeout(resolve, 3000));
        results.postLoginStorage = this.checkLocalStorage();
        results.protectedRouteAccess = await this.testProtectedRoute();
      }
    }

    // Restore network monitoring
    results.networkMonitor.restore();
    results.networkRequests = results.networkMonitor.getRequests();

    console.log('📊 Test Results Summary:', results);
    return results;
  },
};

// Auto-run full test
console.log('🎬 Auto-running full authentication test...');
testAuth
  .runFullTest()
  .then((results) => {
    console.log('🏁 Test completed!');
    console.log('📋 Final Results:', JSON.stringify(results, null, 2));
  })
  .catch((error) => {
    console.error('💥 Test failed:', error);
  });

// Make testAuth available globally for manual testing
window.testAuth = testAuth;
console.log('💡 Manual testing functions available at window.testAuth');
console.log('   • testAuth.checkAuthStore()');
console.log('   • testAuth.checkLocalStorage()');
console.log('   • testAuth.checkLoginPage()');
console.log('   • testAuth.simulateLogin()');
console.log('   • testAuth.testProtectedRoute()');
console.log('   • testAuth.runFullTest()');
