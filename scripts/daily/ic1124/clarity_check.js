// 11/24 Clarity を入れたあと: 公開ページが Clarity の読み込みをしに行くか（行った通信は止めるので、こちらの閲覧は記録されない）と、お客さんに見えるもの（チャットの窓など）が増えていないか
// iPhone 13・計測の通信（Shopify・Meta・Clarity など）は全部止める
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  const hits = new Set();
  await ctx.route('**/*', r => { const u = r.request().url(); if (/clarity/i.test(u)) hits.add(u.replace(/\?.*/, '').slice(0, 120)); return BLOCK.test(u) ? r.abort() : r.continue(); });
  const p = await ctx.newPage();
  for (const path of ['/', '/products/nano-fine-fiber-defogging-and-windproof-window-cleaning-brush', '/cart']) {
    await p.goto('https://looty-japan.com' + path, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(6000);
    const vis = await p.evaluate(() => [...document.querySelectorAll('iframe, [id*="clarity" i], [class*="clarity" i], [id*="agent" i], [class*="brand-agent" i]')].filter(e => e.getBoundingClientRect().width > 0).map(e => (e.tagName + ' ' + (e.id || '') + ' ' + String(e.className || '').slice(0, 40) + ' ' + (e.src || '').slice(0, 60)).trim()));
    const scripts = await p.evaluate(() => [...document.scripts].map(s => s.src).filter(s => /clarity/i.test(s)));
    console.log('■', path, '｜Clarity を読む script タグ:', JSON.stringify(scripts), '｜見えている iframe など:', JSON.stringify(vis));
  }
  console.log('■ Clarity への通信（止めた）:', JSON.stringify([...hits]));
  await p.screenshot({ path: process.argv[2] + '/clarity_cart.png' }); await b.close();
})();
