"use client"

export default function SyntheticV0PageForDeployment() {
  return (
    <div>
      {/* Basic Tailwind test */}
      <div className="bg-red-500 text-white p-4">
        <h1 className="text-2xl font-bold">🎯 STYLING TEST</h1>
        <p>If this has a red background and white text, Tailwind is working!</p>
      </div>

      {/* More Tailwind tests */}
      <div className="bg-blue-500 text-white p-8 m-4 rounded-lg shadow-lg">
        <h2 className="text-xl font-semibold mb-2">Blue Section</h2>
        <p className="text-sm">This should be blue with white text, padding, margin, rounded corners, and shadow.</p>
      </div>

      <div className="bg-green-500 text-black p-4 border-2 border-black">
        <h3 className="text-lg">Green Section with Border</h3>
        <p>This should be green with black text and border.</p>
      </div>

      {/* Inline styles test for comparison */}
      <div style={{backgroundColor: 'purple', color: 'white', padding: '16px', margin: '16px'}}>
        <h3 style={{fontSize: '1.125rem'}}>Inline Styles Test</h3>
        <p>This uses inline styles - should be purple with white text.</p>
      </div>
    </div>
  )
}