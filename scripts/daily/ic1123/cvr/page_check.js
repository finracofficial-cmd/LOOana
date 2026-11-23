// 11/23 商品ページに今あるもの（レビュー数・おすすめの枠・動きを見る道具・ボタン）を読む（iPhone 13・計測の通信は止める）
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
const H = { 'ガラスクリーナー': 'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush', 'ワイパー': 'soft-silicone-car-squeegee-integrated-windshield-glass-scraper-tool-scratch-free-paint-safe-auto-washing-accessory-for-home-use', 'レインガード': 'waterproof-film-for-car-rearview-mirror' };
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  const seen = new Set(); await ctx.route('**/*', r => { const u = r.request().url(); for (const k of ['clarity.ms', 'hotjar', 'luckyorange', 'judge.me', 'selleasy', 'monster', 'pumper', 'klaviyo', 'omnisend']) if (u.includes(k)) seen.add(k); return BLOCK.test(u) ? r.abort() : r.continue(); });
  const p = await ctx.newPage();
  for (const [name, h] of Object.entries(H)) {
    await p.goto('https://looty-japan.com/products/' + h, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4500);
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 1500) { scrollTo(0, y); await new Promise(r => setTimeout(r, 150)); } scrollTo(0, 0); });
    await p.waitForTimeout(2500);
    const r = await p.evaluate(() => {
      const txt = document.body.innerText; const t = s => (s || '').replace(/\s+/g, ' ').trim();
      const rev = [...document.querySelectorAll('[class*="jdgm"], [class*="review"]')].map(e => t(e.innerText)).filter(s => /件|レビュー|review/i.test(s) && s.length < 80);
      const heads = [...document.querySelectorAll('h2, h3')].map(e => t(e.innerText)).filter(s => s && s.length < 40);
      return { pageHeight: document.body.scrollHeight, reviewBits: [...new Set(rev)].slice(0, 6), jdgmCards: document.querySelectorAll('.jdgm-rev').length, heads: [...new Set(heads)].slice(0, 40), hasRecs: /おすすめ|一緒に|こちらも|関連/.test(txt) ? (txt.match(/[^\n]{0,20}(おすすめ|一緒に|こちらも|関連)[^\n]{0,20}/g) || []).slice(0, 6) : [], payBtn: !!document.querySelector('.shopify-payment-button, shopify-accelerated-checkout'), imgs: document.querySelectorAll('img').length, videos: document.querySelectorAll('video').length, faq: /よくある質問|Q\.|Ｑ/.test(txt), delivery: (txt.match(/[^\n]{0,25}(営業日|お届け|発送)[^\n]{0,25}/g) || []).slice(0, 5) };
    });
    console.log('■', name); console.log(JSON.stringify(r));
  }
  console.log('■ 読み込もうとした道具:', [...seen].join('・'));
  await b.close();
})();
