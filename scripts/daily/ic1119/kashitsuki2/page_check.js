// 11/19 新しい加湿器（充電式ダブルミスト卓上加湿器）の商品ページを読む: 表示・色の選択肢・「商品を選ぶ」ボタン・カートに入るか・決済画面
// 計測の通信は止める・連絡先は入れない・支払いはしない
const { chromium, devices } = require('playwright');
const OUT = process.argv[2]; const SLUG = 'dual-nozzle-humidifier-high-mist-output-desktop-sized-and-quiet-operation';
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/i;
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage();
  await p.route(u => BLOCK.test(u.href), r => r.abort()); const errs = []; p.on('pageerror', e => errs.push((e.message || '').slice(0, 70)));
  const res = await p.goto('https://looty-japan.com/products/' + SLUG, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500);
  console.log('ページの応答:', res.status());
  const info = await p.evaluate(async () => { const j = await (await fetch(location.pathname + '.js')).json(); const q = s => document.querySelector(s); const bar = document.getElementById('looty-jump');
    return { title: j.title.slice(0, 80), variants: j.variants.map(v => ({ t: v.title, price: v.price / 100, available: v.available })), h1: (q('h1') || {}).innerText, priceShown: (q('.price-item--sale, .price-item--regular') || {}).innerText, pills: [...document.querySelectorAll('variant-selects input[type=radio]')].map(i => ({ v: i.value, disabled: i.classList.contains('disabled') || i.disabled })), tiers: [...document.querySelectorAll('.pumper_block .pmpr-tier-shell__card')].map(c => c.innerText.replace(/\s+/g, ' ').slice(0, 40)), pumperOptions: [...document.querySelectorAll('.pumper_block .pmpr-tier-shell__card[data-selected="true"] .pmpr_optsel_option_text')].map(o => o.textContent.trim()), bar: bar ? { price: bar.querySelector('.looty-jump__price').textContent.trim(), label: bar.querySelector('button').textContent.trim(), shown: !bar.hidden } : null, addText: (q('product-form form[action*="/cart/add"] button[name="add"]') || {}).innerText, images: document.querySelectorAll('media-gallery img').length, reviews: (q('.jdgm-prev-badge__text') || {}).innerText }; });
  console.log(JSON.stringify(info, null, 1)); await p.screenshot({ path: OUT + '/k_top.png' });
  if (info.bar) { await p.locator('#looty-jump button').first().tap(); await p.waitForTimeout(2200); await p.screenshot({ path: OUT + '/k_buybox.png' }); }
  const btn = p.locator('product-form form[action*="/cart/add"] button[name="add"]').first(); await btn.scrollIntoViewIfNeeded(); await btn.tap(); await p.waitForTimeout(5000);
  const cart = await p.evaluate(async () => { const j = await (await fetch('/cart.js')).json(); return { total: j.total_price / 100, items: j.items.map(i => ({ t: i.product_title.replace(/【[^】]*】/g, '').trim().slice(0, 22), v: i.variant_title, q: i.quantity, line: i.final_line_price / 100 })) }; });
  console.log('カート（そのまま1個）:', JSON.stringify(cart)); await p.screenshot({ path: OUT + '/k_cart.png' });
  await p.goto('https://looty-japan.com/checkout', { waitUntil: 'domcontentloaded', timeout: 60000 }); await p.waitForTimeout(6000);
  const t = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' ')); console.log('決済画面:', (t.match(/\d+個のアイテム/) || ['（個数の表示なし）'])[0], '｜合計', (t.match(/¥[\d,]+/g) || []).slice(0, 3).join(' '), '｜URL', p.url().slice(0, 60));
  console.log('エラーの種類:', JSON.stringify([...new Set(errs)]));
  await b.close();
})();
