// Copy-only entrypoint: the broadsheet is pre-rendered by draw.py and
// committed as entry.png; this program just copies it to the output dir.
// Node 22 ESM, standard library only, no network, no randomness.
// The image is the entry: 38 stories, 3 heroes, 10 minis, 25 briefs.
import { copyFileSync, chmodSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const dest = join(outDir, "entry.png");
copyFileSync(new URL("./entry.png", import.meta.url), dest);
chmodSync(dest, 0o644);
