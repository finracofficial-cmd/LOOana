// 11/24 22時台 商品ページに「届くまでの日数」がどう書かれているかを読む（iPhone 13・計測の通信は止める・カートには入れない）
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
const H = { 'ガラスクリーナー': 'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush', 'ワイパー': 'soft-silicone-car-squeegee-integrated-windshield-glass-scraper-tool-scratch-free-paint-safe-auto-washing-accessory-for-home-use', 'チェア': 'student-children-cushion-chair-waist-support' };
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  await ctx.route('**/*', r => BLOCK.test(r.request().url()) ? r.abort() : r.continue());
  const p = await ctx.newPage();
  for (const [name, h] of Object.entries(H)) {
    await p.goto('https://looty-japan.com/products/' + h, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4000);
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 1500) { scrollTo(0, y); await new Promise(r => setTimeout(r, 150)); } scrollTo(0, 0); });
    await p.waitForTimeout(2000);
    const r = await p.evaluate(() => {
      const txt = document.body.innerText;
      const hits = (txt.match(/[^\n]{0,40}(営業日|お届け|発送|到着|届く|配送)[^\n]{0,40}/g) || []).map(s => s.trim());
      return { n: hits.length, hits: [...new Set(hits)].slice(0, 12) };
    });
    console.log('■', name, JSON.stringify(r));
  }
  await b.close();
})();
