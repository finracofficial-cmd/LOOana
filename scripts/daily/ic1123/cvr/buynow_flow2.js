// 11/23 枠で「2個購入」（2個目を別の色に）→ 速い決済ボタン → 決済画面の中身（VIP特典の行が付くか）。比べる相手: カート経由（bundle_flow2.js）
// iPhone 13・購入しない・連絡先は入れない・計測の通信は止める
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
const OUT = process.argv[2]; const URL = 'https://looty-japan.com/products/nano-fine-fiber-defogging-and-windproof-window-cleaning-brush';
const summary = async (p) => { const tg = p.locator('button[aria-controls][aria-expanded="false"]').first(); await tg.click({ timeout: 5000 }).catch(() => {}); await p.waitForTimeout(1500); const t = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' ')); const i = t.indexOf('ご注文内容'); return t.slice(i, i + 620); };
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  await ctx.route('**/*', r => BLOCK.test(r.request().url()) ? r.abort() : r.continue());
  const p = await ctx.newPage(); await p.goto(URL, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4500);
  const t = p.locator('.pumper_block .basic-tier-mount__left', { hasText: '2個購入' }).first(); await t.scrollIntoViewIfNeeded(); await t.click(); await p.waitForTimeout(1500);
  const trg = p.locator('.pumper_block .pmpr_optsel_trigger'); console.log('色の部品の数:', await trg.count());
  if (await trg.count() >= 2) { await trg.nth(1).click(); await p.waitForTimeout(700); const opt = p.locator('.pmpr_optsel_option:visible', { hasText: 'グレー' }).last(); console.log('グレーの選択肢:', await opt.count()); await opt.click({ timeout: 4000 }).catch(e => console.log('押せず', String(e).slice(0, 100))); await p.waitForTimeout(1000); }
  console.log('枠の文字:', (await p.evaluate(() => document.querySelector('.pumper_block').innerText.replace(/\s+/g, ' '))).slice(0, 110));
  await p.getByText('別のお支払い方法').first().click({ timeout: 8000 }); await p.waitForTimeout(8000);
  console.log('■ 速いボタン経由の決済画面:', await summary(p));
  await p.screenshot({ path: OUT + '/buynow_2colors.png', fullPage: false });
  // 同じ端末でそのまま商品ページへ戻る → カートの中身はどうなっているか
  await p.goto(URL, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500);
  console.log('■ 戻ったあとのカート:', JSON.stringify(await p.evaluate(async () => { const c = await (await fetch('/cart.js')).json(); return { total: c.total_price / 100, n: c.item_count, items: c.items.map(i => (i.variant_title || 'VIP') + '×' + i.quantity) }; })));
  console.log('■ 戻ったあとの枠:', (await p.evaluate(() => document.querySelector('.pumper_block').innerText.replace(/\s+/g, ' '))).slice(0, 80), '／選ばれている段:', await p.evaluate(() => { const c = [...document.querySelectorAll('.pumper_block .pmpr-tier-shell__card')]; return c.map(e => (e.innerText.match(/\d個購入/) || [''])[0] + (e.querySelector('input:checked') ? '✓' : '')).join(' '); }));
  await ctx.close(); await b.close();
})();
