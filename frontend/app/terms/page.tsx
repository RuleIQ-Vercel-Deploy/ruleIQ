export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 via-gray-900 to-black py-24">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white sm:text-6xl">
            Terms of <span className="bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">Service</span>
          </h1>
          <p className="mt-6 text-lg text-gray-300">
            Last updated: September 2025
          </p>
        </div>
        
        <div className="mt-16 space-y-8">
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">1. Acceptance of Terms</h2>
            <p className="text-gray-300 leading-relaxed">
              By accessing and using ruleIQ's services, you accept and agree to be bound by the terms 
              and provision of this agreement. If you do not agree to abide by the above, please do not 
              use this service.
            </p>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">2. Service Description</h2>
            <p className="text-gray-300 leading-relaxed">
              ruleIQ provides AI-powered compliance automation services, including but not limited to 
              compliance gap analysis, automated evidence collection, risk assessment, policy generation, 
              and audit preparation tools.
            </p>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">3. User Responsibilities</h2>
            <div className="space-y-4 text-gray-300">
              <p>As a user of ruleIQ, you agree to:</p>
              <ul className="ml-6 space-y-2">
                <li>• Provide accurate and complete information</li>
                <li>• Maintain the security of your account credentials</li>
                <li>• Use the service in compliance with all applicable laws</li>
                <li>• Not attempt to access unauthorized areas of the platform</li>
                <li>• Not use the service to transmit malicious code or content</li>
                <li>• Respect intellectual property rights</li>
              </ul>
            </div>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">4. Service Availability</h2>
            <p className="text-gray-300 leading-relaxed">
              We strive to maintain high service availability but cannot guarantee uninterrupted access. 
              We reserve the right to modify, suspend, or discontinue the service with reasonable notice. 
              Scheduled maintenance will be communicated in advance when possible.
            </p>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">5. Data and Privacy</h2>
            <p className="text-gray-300 leading-relaxed">
              Your privacy is important to us. Please review our Privacy Policy, which also governs your 
              use of the service. We implement industry-standard security measures to protect your data 
              and maintain SOC 2 compliance.
            </p>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">6. Payment Terms</h2>
            <div className="space-y-4 text-gray-300">
              <p>For paid services:</p>
              <ul className="ml-6 space-y-2">
                <li>• Fees are billed in advance on a monthly or annual basis</li>
                <li>• All fees are non-refundable unless otherwise specified</li>
                <li>• Price changes will be communicated with 30 days notice</li>
                <li>• Failure to pay may result in service suspension</li>
              </ul>
            </div>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">7. Limitation of Liability</h2>
            <p className="text-gray-300 leading-relaxed">
              ruleIQ shall not be liable for any indirect, incidental, special, consequential, or punitive 
              damages, or any loss of profits or revenues. Our total liability shall not exceed the amount 
              paid by you for the service in the 12 months preceding the claim.
            </p>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">8. Termination</h2>
            <p className="text-gray-300 leading-relaxed">
              Either party may terminate this agreement at any time with written notice. Upon termination, 
              your access to the service will be suspended, and any outstanding fees become immediately due.
            </p>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">9. Governing Law</h2>
            <p className="text-gray-300 leading-relaxed">
              These terms shall be governed by and construed in accordance with the laws of England and Wales, 
              without regard to its conflict of law provisions.
            </p>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">10. Contact Information</h2>
            <p className="text-gray-300 leading-relaxed">
              For questions about these Terms of Service, please contact us at:
            </p>
            <div className="mt-4 text-gray-300">
              <p>Email: <a href="mailto:legal@ruleiq.ai" className="text-purple-400 hover:text-purple-300">legal@ruleiq.ai</a></p>
              <p>Address: ruleIQ Limited, London, United Kingdom</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}