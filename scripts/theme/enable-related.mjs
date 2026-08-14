/**
 * 関連商品セクションを、全商品テンプレートで表示に切り替える。
 *
 * templates/product*.json の "related-products" ブロックの中にある
 * `"disabled": true,` の1行だけを消す。他の場所の "disabled": true
 * （Selleasyのアップセルウィジェット、未使用のFAQタブなど）は触らない。
 *
 * 使い方:
 *   shopify theme pull --store h8ct0k-r2.myshopify.com --theme 159681577202 --only 'templates/product*.json'
 *   node enable-related.mjs
 *   shopify theme push --store h8ct0k-r2.myshopify.com --theme 159681577202 --only 'templates/product*.json'
 *
 * 元に戻すとき:
 *   node enable-related.mjs --restore
 *   （実行時に作った .bak から書き戻す。そのあともう一度 push する）
 */
import { readdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const DIR = 'templates';
const RESTORE = process.argv.includes('--restore');

if (!existsSync(DIR)) {
  console.error(`${DIR}/ が見つかりません。shopify theme pull を実行したフォルダで動かしてください。`);
  process.exit(1);
}

const files = readdirSync(DIR).filter((f) => /^product(\..+)?\.json$/.test(f));
if (files.length === 0) {
  console.error(`${DIR}/ に product*.json がありません。pull の --only 指定を確認してください。`);
  process.exit(1);
}

let done = 0;
let skipped = 0;

for (const f of files) {
  const path = join(DIR, f);
  const bak = `${path}.bak`;

  if (RESTORE) {
    if (!existsSync(bak)) { console.log(`  スキップ ${f}（.bak なし）`); skipped++; continue; }
    writeFileSync(path, readFileSync(bak, 'utf8'));
    console.log(`  戻した   ${f}`);
    done++;
    continue;
  }

  const src = readFileSync(path, 'utf8');

  // "related-products" ブロックの開始位置を特定し、その直後だけを対象にする
  const at = src.indexOf('"type": "related-products"');
  if (at === -1) { console.log(`  スキップ ${f}（related-products セクションなし）`); skipped++; continue; }

  const head = src.slice(0, at);
  const tail = src.slice(at);
  const next = tail.replace(/^("type": "related-products",\s*\n\s*)"disabled":\s*true,\s*\n/, '$1');

  if (next === tail) { console.log(`  スキップ ${f}（すでに表示になっている）`); skipped++; continue; }

  if (!existsSync(bak)) writeFileSync(bak, src);   // 初回だけ元ファイルを退避
  writeFileSync(path, head + next);
  console.log(`  表示に変更 ${f}`);
  done++;
}

console.log(`\n${RESTORE ? '復元' : '変更'} ${done} 件 / スキップ ${skipped} 件 / 全 ${files.length} 件`);
console.log('このあと shopify theme push を実行してください。');
