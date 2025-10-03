export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 via-gray-900 to-black py-24">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white sm:text-6xl">
            About <span className="bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">ruleIQ</span>
          </h1>
          <p className="mt-6 text-xl text-gray-300">
            Revolutionizing compliance through AI-powered automation
          </p>
        </div>
        
        <div className="mt-16 space-y-12">
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">Our Mission</h2>
            <p className="text-gray-300 leading-relaxed">
              At ruleIQ, we believe compliance shouldn't be a barrier to innovation. Our AI-powered platform 
              transforms the traditionally complex, time-consuming compliance process into an automated, 
              intelligent system that grows with your business.
            </p>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">What We Do</h2>
            <p className="text-gray-300 leading-relaxed">
              We provide comprehensive compliance automation solutions that help organizations maintain 
              adherence to regulatory frameworks like SOC 2, GDPR, HIPAA, and more. Our platform uses 
              advanced AI to provide intelligent gap analysis, automated evidence collection, and 
              real-time monitoring.
            </p>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">Why Choose ruleIQ</h2>
            <ul className="space-y-3 text-gray-300">
              <li className="flex items-start">
                <span className="mr-3 text-purple-400">•</span>
                <span>60% reduction in compliance costs</span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 text-purple-400">•</span>
                <span>75% faster audit preparation</span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 text-purple-400">•</span>
                <span>99.9% accuracy rate in compliance monitoring</span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 text-purple-400">•</span>
                <span>Support for 50+ compliance frameworks</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}