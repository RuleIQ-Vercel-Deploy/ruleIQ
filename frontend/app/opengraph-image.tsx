import { ImageResponse } from 'next/og';

export const runtime = 'edge';

export const alt = 'RuleIQ - AI-Powered Compliance Automation Platform';
export const size = {
  width: 1200,
  height: 630,
};
export const contentType = 'image/png';

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 60,
          fontWeight: 700,
          color: 'white',
          textAlign: 'center',
          padding: '40px',
        }}
      >
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <div style={{ fontSize: 72, marginBottom: '20px' }}>RuleIQ</div>
          <div style={{ fontSize: 36, fontWeight: 400, opacity: 0.9 }}>
            AI-Powered Compliance Automation
          </div>
        </div>
      </div>
    ),
    {
      ...size,
    }
  );
}