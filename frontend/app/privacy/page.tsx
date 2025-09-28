export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 via-gray-900 to-black py-24">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white sm:text-6xl">
            Privacy <span className="bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">Policy</span>
          </h1>
          <p className="mt-6 text-lg text-gray-300">
            Last updated: September 2025
          </p>
        </div>
        
        <div className="mt-16 space-y-8">
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">Introduction</h2>
            <p className="text-gray-300 leading-relaxed">
              At ruleIQ, we take your privacy seriously. This Privacy Policy explains how we collect, 
              use, disclose, and safeguard your information when you use our compliance automation 
              platform and services.
            </p>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">Information We Collect</h2>
            <div className="space-y-4 text-gray-300">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Information You Provide</h3>
                <p>We collect information you directly provide to us, such as:</p>
                <ul className="mt-2 ml-6 space-y-1">
                  <li>• Account registration information (name, email, company details)</li>
                  <li>• Profile information and preferences</li>
                  <li>• Communication data when you contact us</li>
                  <li>• Compliance-related data you upload to our platform</li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Automatically Collected Information</h3>
                <p>We automatically collect certain information, including:</p>
                <ul className="mt-2 ml-6 space-y-1">
                  <li>• Usage data and analytics</li>
                  <li>• Device information and IP addresses</li>
                  <li>• Cookies and similar tracking technologies</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">How We Use Your Information</h2>
            <ul className="space-y-2 text-gray-300">
              <li>• To provide and maintain our services</li>
              <li>• To process compliance assessments and generate reports</li>
              <li>• To communicate with you about your account and services</li>
              <li>• To improve our platform and develop new features</li>
              <li>• To ensure security and prevent fraud</li>
              <li>• To comply with legal obligations</li>
            </ul>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">Data Security</h2>
            <p className="text-gray-300 leading-relaxed">
              We implement industry-standard security measures to protect your information, including:
            </p>
            <ul className="mt-4 space-y-2 text-gray-300">
              <li>• End-to-end encryption for data in transit and at rest</li>
              <li>• SOC 2 Type II certified infrastructure</li>
              <li>• Regular security audits and penetration testing</li>
              <li>• Multi-factor authentication and access controls</li>
              <li>• Employee security training and background checks</li>
            </ul>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">Your Rights</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              You have the right to:
            </p>
            <ul className="space-y-2 text-gray-300">
              <li>• Access your personal information</li>
              <li>• Correct inaccurate information</li>
              <li>• Delete your personal information</li>
              <li>• Restrict processing of your information</li>
              <li>• Data portability</li>
              <li>• Object to processing</li>
            </ul>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">Contact Us</h2>
            <p className="text-gray-300 leading-relaxed">
              If you have any questions about this Privacy Policy, please contact us at:
            </p>
            <div className="mt-4 text-gray-300">
              <p>Email: <a href="mailto:privacy@ruleiq.ai" className="text-purple-400 hover:text-purple-300">privacy@ruleiq.ai</a></p>
              <p>Address: ruleIQ Limited, London, United Kingdom</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}