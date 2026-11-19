// 「商品を選ぶ」ボタン（sticky-jump.liquid）を、開いた商品ページに仮で差し込むための共通部分。お店には書き込まない・計測の通信は止める
const fs = require('fs');
const SRC = fs.readFileSync('/home/user/LOOana/data/theme-ops/sticky-atc-2026-11-19/sticky-jump.liquid', 'utf8');
const css = SRC.match(/<style>([\s\S]*?)<\/style>/)[1], js = SRC.match(/<script>\n([\s\S]*?)<\/script>/)[1];
const note = SRC.match(/assign looty_jump_note = '([^']*)'/)[1], label = SRC.match(/assign looty_jump_label = '([^']*)'/)[1];
const yen = n => '¥' + Math.round(n / 100).toLocaleString('en-US');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/i;
async function open(b, dev, slug) {
  const ctx = await b.newContext({ ...dev, locale: 'ja-JP' }); const p = await ctx.newPage();
  await p.route(u => BLOCK.test(u.href), r => r.abort());
  const errs = []; p.on('pageerror', e => errs.push((e.message || '').slice(0, 60)));
  await p.goto('https://looty-japan.com/products/' + slug, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500);
  const prod = await p.evaluate(async () => (await fetch(location.pathname.replace(/\/$/, '') + '.js')).json());
  const first = prod.variants.find(v => v.available) || prod.variants[0];
  const data = {}; prod.variants.forEach(v => data[String(v.id)] = yen(v.price));
  const html = `<div id="looty-jump" class="looty-jump" hidden><div class="looty-jump__info"><span class="looty-jump__note">${note}</span><span class="looty-jump__line"><span class="looty-jump__price">${yen(first.price)}</span><span class="looty-jump__tier"></span></span></div><button type="button" class="looty-jump__btn">${label}</button></div><script type="application/json" id="looty-jump-data">${JSON.stringify(data)}</script>`;
  const e0 = errs.length;
  await p.evaluate(h => { const d = document.createElement('div'); d.innerHTML = h; [...d.children].forEach(c => document.body.appendChild(c)); }, html);
  await p.addStyleTag({ content: css }); await p.evaluate(js); await p.waitForTimeout(1300);
  const st = () => p.evaluate(() => { const bar = document.getElementById('looty-jump'); const r = bar.getBoundingClientRect(); const o = document.querySelector('product-form form[action*="/cart/add"] button[name="add"], button.product-form__submit'); const or = o ? o.getBoundingClientRect() : null; const box = document.querySelector('.pumper_block'); const sel = document.querySelector('.pumper_block .pmpr-tier-shell__card[data-selected="true"] .pmpr-tier-price__total'); return { price: bar.querySelector('.looty-jump__price').textContent, tier: bar.querySelector('.looty-jump__tier').textContent, label: bar.querySelector('button').textContent, off: bar.classList.contains('is-off'), barTop: Math.round(r.top), vh: innerHeight, y: Math.round(scrollY), origTop: or ? Math.round(or.top) : null, origBottom: or ? Math.round(or.bottom) : null, boxTop: box ? Math.round(box.getBoundingClientRect().top) : null, tierPrice: sel ? sel.textContent.trim() : null }; });
  const cartN = () => p.evaluate(async () => (await (await fetch('/cart.js')).json()).item_count);
  const tapBar = async () => { await p.locator('#looty-jump button').tap(); };
  return { ctx, p, prod, st, cartN, tapBar, errs, e0, first };
}
module.exports = { open, yen, label };
