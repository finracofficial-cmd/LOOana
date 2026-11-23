// 11/23 ①「2個購入」を選んだあとの枠の中身（色の部品の並び）②「よく一緒に購入されている商品」の中身 ③ 購入ボタンの下の速い決済ボタンが見えているか
// iPhone 13・購入しない・連絡先は入れない・計測の通信は止める
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
const OUT = process.argv[2]; const URL = 'https://looty-japan.com/products/nano-fine-fiber-defogging-and-windproof-window-cleaning-brush';
const cartJs = async (p) => p.evaluate(async () => { const c = await (await fetch('/cart.js')).json(); return { total: c.total_price / 100, original: c.original_total_price / 100, items: c.items.map(i => ({ t: i.product_title.replace(/【[^】]*】/g, '').trim().slice(0, 22), v: i.variant_title, q: i.quantity, line: i.final_line_price / 100, props: Object.keys(i.properties || {}) })) }; });
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  await ctx.route('**/*', r => BLOCK.test(r.request().url()) ? r.abort() : r.continue());
  const p = await ctx.newPage(); await p.goto(URL, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4500);
  // ③
  console.log('■ 速い決済ボタン:', JSON.stringify(await p.evaluate(() => [...document.querySelectorAll('.shopify-payment-button, shopify-accelerated-checkout, shopify-buy-it-now-button')].map(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return { tag: e.tagName, cls: String(e.className).slice(0, 50), w: Math.round(r.width), h: Math.round(r.height), display: cs.display, vis: cs.visibility, text: (e.innerText || '').replace(/\s+/g, ' ').slice(0, 40) }; }))));
  // ②
  await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 1200) { scrollTo(0, y); await new Promise(r => setTimeout(r, 200)); } });
  await p.waitForTimeout(2500);
  const fbt = await p.evaluate(() => { const h = [...document.querySelectorAll('h1,h2,h3,h4,div,p,span')].filter(e => e.children.length <= 1 && /よく一緒に購入されている商品/.test(e.innerText || '') && (e.innerText || '').length < 40).pop(); if (!h) return null; let box = h; for (let i = 0; i < 6 && box.parentElement; i++) { box = box.parentElement; if ((box.innerText || '').length > 120) break; } const r = box.getBoundingClientRect(); box.scrollIntoView({ block: 'start' }); return { cls: String(box.className).slice(0, 80), y: Math.round(r.top + scrollY), h: Math.round(r.height), pageH: document.body.scrollHeight, text: box.innerText.replace(/\s+/g, ' ').slice(0, 700) }; });
  console.log('■ よく一緒に購入されている商品:', JSON.stringify(fbt));
  await p.waitForTimeout(800); await p.screenshot({ path: OUT + '/fbt_block.png' });
  // 購入ボタン（カートに追加）の位置
  console.log('■ カートに追加のボタンの位置:', JSON.stringify(await p.evaluate(() => { const b = document.querySelector('form[action*="/cart/add"] button[type=submit], button[name=add]'); const r = b.getBoundingClientRect(); return { y: Math.round(r.top + scrollY), text: b.innerText.trim() }; })));
  // ①
  await p.evaluate(() => scrollTo(0, 0));
  const tier2 = p.locator('.pumper_block .basic-tier-mount__left', { hasText: '2個購入' }).first();
  await tier2.scrollIntoViewIfNeeded(); await tier2.click(); await p.waitForTimeout(1500);
  const dom = await p.evaluate(() => { const walk = (e, d) => { if (d > 9) return ''; const cs = getComputedStyle(e); if (cs.display === 'none') return ''; const own = [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join(' ').slice(0, 30); let s = '  '.repeat(d) + e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).slice(0, 3).join('.') : '') + (own ? ' "' + own + '"' : '') + '\n'; for (const c of e.children) s += walk(c, d + 1); return s; }; return walk(document.querySelector('.pumper_block'), 0); });
  console.log('■ 「2個購入」を選んだあとの枠の中:\n' + dom.split('\n').filter(l => /tier|variant|optsel|"/.test(l)).slice(0, 90).join('\n'));
  await (await p.$('.pumper_block')).screenshot({ path: OUT + '/tier2_open.png' });
  await b.close();
})();
