// 11/21 カートの引き出し（Monster Cart）の今の文字を読む（計測の通信は止める・購入はしない）
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  await ctx.route('**/*', r => BLOCK.test(r.request().url()) ? r.abort() : r.continue());
  const p = await ctx.newPage();
  await p.goto('https://looty-japan.com/products/nano-fine-fiber-defogging-and-windproof-window-cleaning-brush', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3000);
  const vid = await p.evaluate(() => document.querySelector('form[action*="/cart/add"] [name=id]').value);
  await p.evaluate(async (id) => { await fetch('/cart/add.js', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id, quantity: 1 }) }); }, vid);
  await p.goto('https://looty-japan.com/cart', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(6000);
  const t = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
  const i = t.indexOf('確保されています'); console.log(t.slice(Math.max(0, i - 40), i + 900));
  await b.close();
})();
