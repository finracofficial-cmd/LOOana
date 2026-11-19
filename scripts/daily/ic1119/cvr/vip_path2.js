// 11/20 VIP特典の行が付かなかった注文（#32296・#32331＝同じ商品の色ちがいを1個ずつ・7,164円）と同じ買い方を再現する
// 計測の通信は止める・連絡先は入れない・支払いはしない
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/i;
const NANO = 'washable-reusable-fuzz-remover';
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage(); await p.route(u => BLOCK.test(u.href), r => r.abort());
  const open = async () => { await p.goto('https://looty-japan.com/products/' + NANO, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500); };
  const add = async () => { const btn = p.locator('product-form form[action*="/cart/add"] button[name="add"]').first(); await btn.scrollIntoViewIfNeeded(); await btn.tap(); await p.waitForTimeout(5000); };
  const cart = () => p.evaluate(async () => { const j = await (await fetch('/cart.js')).json(); return { total: j.total_price / 100, items: j.items.map(i => ({ t: i.product_title.replace(/【[^】]*】/g, '').trim().slice(0, 20), v: i.variant_title, q: i.quantity, line: i.final_line_price / 100 })) }; });
  await open(); await add(); console.log('1個目（ピュアホワイト）:', JSON.stringify(await cart()));
  await open(); const pill = p.locator('variant-selects label', { hasText: 'マットブラック' }).first(); await pill.scrollIntoViewIfNeeded(); await pill.tap(); await p.waitForTimeout(1500); await add();
  console.log('2個目（色を変えて1個）:', JSON.stringify(await cart())); await p.waitForTimeout(6000); console.log('6秒後:', JSON.stringify((await cart()).items.map(i => i.t + '（' + i.v + '）×' + i.q)));
  await p.goto('https://looty-japan.com/checkout', { waitUntil: 'domcontentloaded', timeout: 60000 }); await p.waitForTimeout(6000);
  const t = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' ')); console.log('決済画面:', (t.match(/\d+個のアイテム/) || ['（個数の表示なし）'])[0]);
  await b.close();
})();
