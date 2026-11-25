// 11/25 17時台「CVR を上げる仕掛けを教えて。スクロールで下に行くやつみたいな」→ 提案の前に、公開ページに今あるものを洗い出す（iPhone 13・計測の通信は止める・何も買わない）
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/i;
const H = { 'ガラスクリーナー': 'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush', 'ワイパー': 'soft-silicone-car-squeegee-integrated-windshield-glass-scraper-tool-scratch-free-paint-safe-auto-washing-accessory-for-home-use', '姿勢サポートチェア': 'student-children-cushion-chair-waist-support' };
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['iPhone 13'], deviceScaleFactor: 1, locale: 'ja-JP' });
  await ctx.route('**/*', r => BLOCK.test(r.request().url()) ? r.abort() : r.continue());
  const p = await ctx.newPage();
  for (const [name, h] of Object.entries(H)) {
    await p.goto('https://looty-japan.com/products/' + h, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4500);
    if (OUT) await p.screenshot({ path: `${OUT}/${h.slice(0, 12)}_top.png` });
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 1200) { scrollTo(0, y); await new Promise(r => setTimeout(r, 200)); } scrollTo(0, 0); });
    await p.waitForTimeout(2500);
    const r = await p.evaluate(() => {
      const t = s => (s || '').replace(/\s+/g, ' ').trim(); const Y = e => Math.round(e.getBoundingClientRect().top + scrollY);
      const vis = e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none'; };
      const atc = document.querySelector('product-form button[name="add"], button[name="add"]');
      const leaf = [...document.querySelectorAll('body *')].filter(e => vis(e) && e.children.length === 0 && t(e.innerText).length > 1 && !['SCRIPT', 'STYLE', 'OPTION'].includes(e.tagName));
      const find = re => leaf.filter(e => re.test(t(e.innerText))).map(e => [Y(e), t(e.innerText).slice(0, 60)]).slice(0, 6);
      const KW = { '人数・閲覧': /人が.*(見て|閲覧|購入)|閲覧中|が見ています/, '残り・在庫': /残り\s*\d|在庫(わずか|残り|あり|数)|点のみ/, 'タイマー': /終了まで|\d{1,2}\s*[:：]\s*\d{2}\s*[:：]\s*\d{2}|時間\s*\d+\s*分/, '届く日・発送': /お届け|発送|営業日|届く/, '返品・保証': /返品|返金|保証/, '支払い方法': /PayPay|Paidy|ペイディ|後払い|クレジット|Apple Pay|分割/, 'ランキング・実績': /ランキング|累計|No\.?\s*1|満足度|受賞/, 'セット・まとめ買い': /2個|3個|まとめ買い|セット|OFF/, 'VIP': /VIP/ };
      const kw = {}; for (const k in KW) kw[k] = find(KW[k]);
      const fixed = [...document.querySelectorAll('body *')].filter(e => { const cs = getComputedStyle(e); return (cs.position === 'fixed' || cs.position === 'sticky') && vis(e) && e.getBoundingClientRect().height > 20; }).map(e => { const r = e.getBoundingClientRect(); return [e.tagName + (e.id ? '#' + e.id : '') + '.' + String(e.className).slice(0, 30), Math.round(r.top), Math.round(r.height), t(e.innerText).slice(0, 50)]; }).slice(0, 12);
      const media = [...document.querySelectorAll('video, iframe[src*="youtube"], iframe[src*="vimeo"], model-viewer, deferred-media')].map(e => [e.tagName, Y(e), vis(e), (e.getAttribute('src') || '').slice(0, 50), e.autoplay || false]);
      const imgs = [...document.querySelectorAll('img')].filter(vis); const gif = imgs.filter(i => /\.gif/i.test(i.currentSrc || i.src));
      const pay = [...document.querySelectorAll('svg[aria-labelledby], img[alt], .list-payment svg, .payment-icons svg')].map(e => [(e.getAttribute('alt') || (e.querySelector('title') || {}).textContent || '').trim(), Y(e)]).filter(x => /visa|master|amex|jcb|paypay|paidy|apple|google|shop pay|american/i.test(x[0])).slice(0, 14);
      const acc = [...document.querySelectorAll('details > summary')].filter(vis).map(e => [Y(e), t(e.innerText).slice(0, 40)]).slice(0, 20);
      const heads = [...document.querySelectorAll('h1, h2, h3')].filter(vis).map(e => [Y(e), e.tagName, t(e.innerText).slice(0, 40)]).filter(x => x[2]).slice(0, 60);
      const jd = { badge: t((document.querySelector('.jdgm-prev-badge') || {}).innerText), badgeY: document.querySelector('.jdgm-prev-badge') ? Y(document.querySelector('.jdgm-prev-badge')) : null, widgetY: document.querySelector('.jdgm-rev-widg, #judgeme_product_reviews') ? Y(document.querySelector('.jdgm-rev-widg, #judgeme_product_reviews')) : null, cards: document.querySelectorAll('.jdgm-rev').length, photos: document.querySelectorAll('.jdgm-rev__pic-img, .jdgm-rev__pic-link').length };
      const jump = document.getElementById('looty-jump');
      const dyn = document.querySelector('.shopify-payment-button'); const bundle = leaf.find(e => /限定セール/.test(t(e.innerText)));
      const qty = document.querySelector('quantity-input, input[name="quantity"]');
      return { pageHeight: document.body.scrollHeight, viewport: innerHeight, titleY: document.querySelector('h1') ? Y(document.querySelector('h1')) : null, priceY: document.querySelector('.price') ? Y(document.querySelector('.price')) : null, bundleY: bundle ? Y(bundle) : null, atcY: atc ? Y(atc) : null, atcText: atc ? t(atc.innerText) : null, quickPayY: dyn ? Y(dyn) : null, qtyVisible: qty ? vis(qty) : false,
        jumpBar: jump ? { hidden: jump.hidden, text: t(jump.innerText).slice(0, 60) } : null, imgs: imgs.length, imgsAboveATC: atc ? imgs.filter(i => Y(i) < Y(atc)).length : null, gifs: gif.length, media, pay, acc, heads, jd, kw, fixed };
    });
    console.log('■', name); console.log(JSON.stringify(r, null, 0));
    if (OUT && r.atcY) { await p.evaluate(y => scrollTo(0, y - 520), r.atcY); await p.waitForTimeout(1200); await p.screenshot({ path: `${OUT}/${h.slice(0, 12)}_atc.png` }); await p.evaluate(y => scrollTo(0, y + 140), r.atcY); await p.waitForTimeout(900); await p.screenshot({ path: `${OUT}/${h.slice(0, 12)}_below.png` }); }
  }
  await b.close();
})();
