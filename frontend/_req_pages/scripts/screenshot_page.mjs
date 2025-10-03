#!/usr/bin/env node
import { chromium } from 'playwright';
import path from 'node:path';
import fs from 'node:fs';

const url = process.env.PAGE_URL || 'http://localhost:4000/requirements/create-wireframe';
const outPath = process.env.OUT_PATH || path.resolve(process.cwd(), '_req_pages/screenshots/create-wireframe.png');

async function main() {
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  await page.screenshot({ path: outPath, fullPage: true });
  await browser.close();
  console.log('Screenshot saved to', outPath);
}

main().catch((err) => { console.error(err); process.exit(1); });
