'use client';

import { useState } from 'react';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    message: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
    console.log('Form submitted:', formData);
    // In a real app, this would send to an API
    alert('Thank you for your message! We\'ll get back to you soon.');
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 via-gray-900 to-black py-24">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white sm:text-6xl">
            Contact <span className="bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">Us</span>
          </h1>
          <p className="mt-6 text-xl text-gray-300">
            Get in touch with our team to learn more about ruleIQ
          </p>
        </div>
        
        <div className="mt-16 grid gap-8 lg:grid-cols-2">
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-6">Send us a message</h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
                  Name *
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  required
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                  Email *
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label htmlFor="company" className="block text-sm font-medium text-gray-300 mb-2">
                  Company
                </label>
                <input
                  type="text"
                  id="company"
                  name="company"
                  value={formData.company}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label htmlFor="message" className="block text-sm font-medium text-gray-300 mb-2">
                  Message *
                </label>
                <textarea
                  id="message"
                  name="message"
                  required
                  rows={5}
                  value={formData.message}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
              
              <button
                type="submit"
                className="w-full bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-3 rounded-lg font-semibold text-white hover:from-purple-700 hover:to-purple-800 transition-all"
              >
                Send Message
              </button>
            </form>
          </div>
          
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8 backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-6">Get in touch</h2>
            
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Sales Inquiries</h3>
                <p className="text-gray-300">Ready to see ruleIQ in action?</p>
                <a href="mailto:sales@ruleiq.ai" className="text-purple-400 hover:text-purple-300 transition-colors">
                  sales@ruleiq.ai
                </a>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Support</h3>
                <p className="text-gray-300">Need help with your account?</p>
                <a href="mailto:support@ruleiq.ai" className="text-purple-400 hover:text-purple-300 transition-colors">
                  support@ruleiq.ai
                </a>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">General</h3>
                <p className="text-gray-300">Have a question or feedback?</p>
                <a href="mailto:hello@ruleiq.ai" className="text-purple-400 hover:text-purple-300 transition-colors">
                  hello@ruleiq.ai
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}