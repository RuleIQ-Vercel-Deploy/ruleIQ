#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const svgPath = path.resolve(process.cwd(), '_req_pages/wireframes/create-wireframe.svg');
const pngPath = path.resolve(process.cwd(), '_req_pages/wireframes/create-wireframe.png');

async function main() {
  const svg = fs.readFileSync(svgPath);
  const image = sharp(svg, { density: 144 });
  await image.resize(1440, 900, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 1 } }).png().toFile(pngPath);
  console.log('PNG written to', pngPath);
}

main().catch(err => { console.error(err); process.exit(1); });
