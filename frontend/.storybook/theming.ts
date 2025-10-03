import fs from "node:fs";
import path from "node:path";

export type StyleRules = {
  colors: Record<string, string>;
  shadows: Record<string, string>;
  font: Record<string, string>;
  transitions: Record<string, string>;
  radii: Record<string, string>;
};

export function loadStyleRules(): StyleRules {
  const p = path.resolve(process.cwd(), "_index_ops/quality_gate/style_rules.json");
  const raw = fs.readFileSync(p, "utf8");
  return JSON.parse(raw);
}
