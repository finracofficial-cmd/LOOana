// 11/25 カートに入れたあと、画面下の帯（商品を選ぶ ▼）と画面がどうなるかを見る。あわせて、閉じている質問欄の中身（支払い方法・届くまでの日数）を読む
// iPhone 13・計測の通信は止める・連絡先は入れない・購入しない（確認用のカートに1個入るだけ）
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/i;
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['iPhone 13'], deviceScaleFactor: 1, locale: 'ja-JP' });
  await ctx.route('**/*', r => BLOCK.test(r.request().url()) ? r.abort() : r.continue());
  const p = await ctx.newPage(); const t = s => (s || '').replace(/\s+/g, ' ').trim();
  await p.goto('https://looty-japan.com/products/nano-fine-fiber-defogging-and-windproof-window-cleaning-brush', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4500);
  const hidden = await p.evaluate(() => { const t = s => (s || '').replace(/\s+/g, ' ').trim(); return [...document.querySelectorAll('details')].map(d => [t(d.querySelector('summary') && d.querySelector('summary').textContent).slice(0, 40), t(d.textContent).slice(0, 420)]).filter(x => /配送|届く|支払|返品/.test(x[0])); });
  console.log('■ 閉じている質問欄の中身'); hidden.forEach(h => console.log('  ', h[0], '→', h[1]));
  const allTxt = await p.evaluate(() => document.body.textContent);
  console.log('■ ページ全体（隠れている文も含む）に出てくる言葉:', ['PayPay', 'ペイペイ', 'Paidy', 'ペイディ', 'メルペイ', '後払い', 'あと払い', 'お支払い方法', 'コンビニ', '代引'].map(w => w + ' ' + (allTxt.split(w).length - 1)).join('・'));
  const bar = () => p.evaluate(() => { const e = document.getElementById('looty-jump'); const r = e.getBoundingClientRect(); return { text: e.innerText.replace(/\s+/g, ' ').trim(), off: e.classList.contains('is-off'), top: Math.round(r.top) }; });
  const cart = () => p.evaluate(async () => { const c = await (await fetch('/cart.js')).json(); return { n: c.item_count, total: c.total_price / 100, lines: c.items.map(i => i.product_title.slice(-18) + '×' + i.quantity) }; });
  console.log('■ 入れる前: 帯', JSON.stringify(await bar()), 'カート', JSON.stringify(await cart()));
  await p.locator('#looty-jump button').tap(); await p.waitForTimeout(1800);
  await p.locator('product-form button[name="add"]').first().tap(); await p.waitForTimeout(5000);
  const drawer = await p.evaluate(() => { const t = s => (s || '').replace(/\s+/g, ' ').trim(); const w = document.querySelector('#monster-cart-wrapper'); const vis = [...document.querySelectorAll('#monster-cart-wrapper *')].filter(e => e.children.length === 0 && e.getBoundingClientRect().height > 0 && t(e.innerText)); return { open: !!w && w.getBoundingClientRect().width > 100, texts: vis.map(e => t(e.innerText)).filter((x, i, a) => a.indexOf(x) === i).slice(0, 40) }; });
  console.log('■ 入れた直後: カートの引き出し', JSON.stringify(drawer)); console.log('  カート', JSON.stringify(await cart()));
  if (OUT) await p.screenshot({ path: OUT + '/after_atc_drawer.png' });
  // 引き出しを閉じる（閉じるボタン → だめなら外側を押す）
  const closed = await p.evaluate(() => { const c = [...document.querySelectorAll('#monster-cart-wrapper button, #monster-cart-wrapper [role="button"], #monster-cart-wrapper svg')].find(e => /close|閉じ|×/i.test((e.getAttribute('aria-label') || '') + (e.className.baseVal || e.className || '') + (e.innerText || ''))); if (c) { (c.closest('button') || c).dispatchEvent(new MouseEvent('click', { bubbles: true })); return 'button'; } return 'none'; });
  await p.waitForTimeout(1500); if (closed === 'none') { await p.keyboard.press('Escape'); await p.waitForTimeout(1200); }
  if (OUT) await p.screenshot({ path: OUT + '/after_atc_closed.png' });
  const hdr = await p.evaluate(() => { const b = document.querySelector('.cart-count-bubble'); return b ? b.innerText.replace(/\s+/g, ' ').trim() : null; });
  console.log('■ 閉じたあと（' + closed + '）: 帯', JSON.stringify(await bar()), '・ヘッダーのカートの数字', hdr);
  await p.evaluate(() => scrollTo(0, 5200)); await p.waitForTimeout(1200);
  console.log('■ 下へ読み進めたとき: 帯', JSON.stringify(await bar())); if (OUT) await p.screenshot({ path: OUT + '/after_atc_scrolled.png' });
  await p.goto('https://looty-japan.com/products/soft-silicone-car-squeegee-integrated-windshield-glass-scraper-tool-scratch-free-paint-safe-auto-washing-accessory-for-home-use', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4000);
  console.log('■ カートに1個入ったまま別の商品ページ（ワイパー）を開いたとき: 帯', JSON.stringify(await bar()), 'カート', JSON.stringify(await cart()));
  await b.close();
})();
