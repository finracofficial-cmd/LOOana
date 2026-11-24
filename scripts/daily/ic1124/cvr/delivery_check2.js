// 11/24 22時台 閉じている「注文してから届くまで」「配送・返品について」の中身を textContent で読む（計測は止める・カートには入れない）
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  await ctx.route('**/*', r => BLOCK.test(r.request().url()) ? r.abort() : r.continue());
  const p = await ctx.newPage();
  await p.goto('https://looty-japan.com/products/nano-fine-fiber-defogging-and-windproof-window-cleaning-brush', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4000);
  const r = await p.evaluate(() => {
    const t = s => (s || '').replace(/\s+/g, ' ').trim();
    const out = [];
    for (const d of document.querySelectorAll('details, [class*="accordion"], [class*="collapsible"]')) {
      const s = t(d.textContent); if (/届くまで|配送・返品|営業日|発送/.test(s) && s.length < 1500) out.push(s);
    }
    return [...new Set(out)].slice(0, 6);
  });
  for (const s of r) console.log('■', s);
  await b.close();
})();
