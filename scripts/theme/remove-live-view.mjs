/**
 * 偽の「今〇人がカートに追加しています。」ブロックを、全商品テンプレートから外す。
 *
 * 中身は Math.floor(Math.random() * 5) + 2 で、在庫にも閲覧者にも一切連動していない。
 * 商品テンプレート（templates/product*.json）の中の custom_liquid ブロックとして
 * 入っているので、そのブロックだけを blocks と block_order から取り除く。
 *
 * 触るのは「本文に liveCount を含む custom_liquid ブロック」だけ。
 * 他の custom_liquid（送料表記・FAQ・バッジなど）は一切触らない。
 *
 * 使い方:
 *   shopify theme pull --store h8ct0k-r2.myshopify.com --theme 159681577202 --only 'templates/product*.json'
 *   node remove-live-view.mjs --dry-run     ← まず何件当たるか見る（書き込まない）
 *   node remove-live-view.mjs
 *   shopify theme push --store h8ct0k-r2.myshopify.com --theme 159681577202 --only 'templates/product*.json'
 *
 * 元に戻すとき:
 *   node remove-live-view.mjs --restore
 *   （実行時に作った backup/ から書き戻す。そのあともう一度 push する）
 */
import { readdirSync, readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const DIR = 'templates';
const BACKUP = 'backup';                 // templates/ の外に置く（push 対象に混ざらないように）
const RESTORE = process.argv.includes('--restore');
const DRY = process.argv.includes('--dry-run');
const MARK = 'liveCount';                // このブロックを見分ける目印
mkdirSync(BACKUP, { recursive: true });

if (!existsSync(DIR)) {
  console.error(`${DIR}/ が見つかりません。shopify theme pull を実行したフォルダで動かしてください。`);
  process.exit(1);
}

const files = readdirSync(DIR).filter((f) => /^product(\..+)?\.json$/.test(f));
if (files.length === 0) {
  console.error(`${DIR}/ に product*.json がありません。pull の --only 指定を確認してください。`);
  process.exit(1);
}

/** Shopify の JSON テンプレートは先頭に /* *​/ コメントを持てる。落とさずに保つ。 */
function splitComment(src) {
  const m = src.match(/^\s*\/\*[\s\S]*?\*\/\s*/);
  return m ? [m[0], src.slice(m[0].length)] : ['', src];
}

let done = 0, skipped = 0, hits = 0;

for (const f of files) {
  const path = join(DIR, f);
  const bak = join(BACKUP, f);

  if (RESTORE) {
    if (!existsSync(bak)) { console.log(`  スキップ ${f}（backup なし）`); skipped++; continue; }
    writeFileSync(path, readFileSync(bak, 'utf8'));
    console.log(`  戻した   ${f}`);
    done++;
    continue;
  }

  const src = readFileSync(path, 'utf8');
  const [comment, body] = splitComment(src);

  let doc;
  try { doc = JSON.parse(body); }
  catch (e) { console.log(`  スキップ ${f}（JSONとして読めない: ${e.message}）`); skipped++; continue; }

  const removed = [];
  for (const section of Object.values(doc.sections ?? {})) {
    if (!section.blocks) continue;
    for (const [id, block] of Object.entries(section.blocks)) {
      const liquid = block?.settings?.custom_liquid;
      if (block?.type !== 'custom_liquid' || typeof liquid !== 'string') continue;
      if (!liquid.includes(MARK)) continue;
      delete section.blocks[id];
      if (Array.isArray(section.block_order)) {
        section.block_order = section.block_order.filter((x) => x !== id);
      }
      removed.push(id);
    }
  }

  if (removed.length === 0) { console.log(`  スキップ ${f}（該当ブロックなし）`); skipped++; continue; }
  hits += removed.length;

  if (DRY) { console.log(`  [dry-run] ${f} → ${removed.length}ブロック該当 ${removed.join(', ')}`); done++; continue; }

  if (!existsSync(bak)) writeFileSync(bak, src);          // 初回だけ元ファイルを退避
  writeFileSync(path, comment + JSON.stringify(doc, null, 2) + '\n');
  console.log(`  外した   ${f}（${removed.length}ブロック）`);
  done++;
}

const verb = RESTORE ? '復元' : DRY ? '該当' : '変更';
console.log(`\n${verb} ${done} 件 / スキップ ${skipped} 件 / 全 ${files.length} 件`
  + (RESTORE ? '' : ` / 外したブロック計 ${hits}`));
if (!DRY) console.log('このあと shopify theme push を実行してください。');
