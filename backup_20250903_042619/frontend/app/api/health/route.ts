import { NextResponse } from 'next/server';

export async function GET() {
  const body = {
    status: 'ok' as const,
    version: process.env['APP_VERSION'] || '1.0.0',
    timestamp: new Date().toISOString(),
  };

  return NextResponse.json(body, { status: 200 });
}
