export default function FeaturesPage() {
  const features = [
    {
      title: 'AI-Powered Analysis',
      description: 'Advanced machine learning algorithms analyze your compliance posture and identify gaps automatically.',
      icon: '🤖'
    },
    {
      title: 'Real-Time Monitoring',
      description: 'Continuous monitoring of your systems with instant alerts when compliance issues arise.',
      icon: '📊'
    },
    {
      title: 'Automated Evidence Collection',
      description: 'Automatically gather and organize evidence for audits, saving weeks of manual work.',
      icon: '📋'
    },
    {
      title: 'Smart Reporting',
      description: 'Generate comprehensive compliance reports with a single click, tailored to any framework.',
      icon: '📈'
    },
    {
      title: 'Team Collaboration',
      description: 'Streamlined workflows that enable seamless coordination across compliance teams.',
      icon: '👥'
    },
    {
      title: 'Policy Automation',
      description: 'Auto-generate and maintain policies that align with your chosen compliance frameworks.',
      icon: '🔧'
    },
    {
      title: 'Risk Assessment',
      description: 'Proactive identification of risks with AI-powered mitigation recommendations.',
      icon: '⚡'
    },
    {
      title: 'Multi-Framework Support',
      description: 'Support for 50+ frameworks including SOC 2, GDPR, HIPAA, ISO 27001, and more.',
      icon: '🌐'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 via-gray-900 to-black py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white sm:text-6xl">
            Powerful <span className="bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">Features</span>
          </h1>
          <p className="mt-6 text-xl text-gray-300">
            Everything you need to automate compliance and reduce risk
          </p>
        </div>
        
        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm transition-all hover:border-purple-500/50"
            >
              <div className="mb-4 text-4xl">{feature.icon}</div>
              <h3 className="mb-3 text-xl font-semibold text-white">
                {feature.title}
              </h3>
              <p className="text-gray-400">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
        
        <div className="mt-16 text-center">
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-4">Ready to Get Started?</h2>
            <p className="text-gray-300 mb-6">
              Transform your compliance process with AI-powered automation
            </p>
            <a 
              href="/signup" 
              className="inline-flex items-center justify-center bg-gradient-to-r from-purple-600 to-purple-700 px-8 py-3 rounded-lg font-semibold text-white hover:from-purple-700 hover:to-purple-800 transition-all"
            >
              Start Free Trial
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}