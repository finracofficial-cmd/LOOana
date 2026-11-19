// 固定カートボタン（全商品用）を、開いた商品ページに仮で差し込むための共通部分。お店には書き込まない
// Liquid の部分（値段・選択肢の有無・バリエーション別の値段）は /products/<ハンドル>.js から同じ形に作る
const fs = require('fs');
const SRC = fs.readFileSync('/home/user/LOOana/data/theme-ops/sticky-atc-2026-11-19/sticky-atc-all.liquid', 'utf8');
const css = SRC.match(/<style>([\s\S]*?)<\/style>/)[1], js = SRC.match(/<script>\n([\s\S]*?)<\/script>/)[1];
const note = SRC.match(/assign looty_satc_note = '([^']*)'/)[1];
const yen = n => '¥' + Math.round(n / 100).toLocaleString('en-US');
// 計測（Shopify の集計・Meta などのピクセル）に混ざらないよう、計測の通信は止める
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/i;
async function open(b, devices, slug) {
  const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage();
  await p.route(u => BLOCK.test(u.href), r => r.abort());
  const errs = []; p.on('pageerror', e => errs.push((e.message || '').slice(0, 60) + ' @' + (((e.stack || '').split('\n')[1] || '').match(/:(\d+):\d+\)?$/) || [])[1]));
  await p.goto('https://looty-japan.com/products/' + slug, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500);
  const prod = await p.evaluate(async () => (await fetch(location.pathname.replace(/\/$/, '') + '.js')).json());
  const first = prod.variants.find(v => v.available) || prod.variants[0];
  const data = {}; prod.variants.forEach(v => data[String(v.id)] = yen(v.price));
  const html = `<div id="looty-sticky-atc" class="looty-satc" hidden data-need-pick="${prod.variants.length > 1 ? 1 : 0}"><div class="looty-satc__info"><span class="looty-satc__note">${note}</span><span class="looty-satc__line"><span class="looty-satc__price">${yen(first.price)}</span><span class="looty-satc__tier"></span></span></div><button type="button" class="looty-satc__btn" data-label-add="カートに追加する" data-label-pick="選んでカートに追加" data-label-out="売り切れ">カートに追加する</button></div><script type="application/json" id="looty-satc-data">${JSON.stringify(data)}</script>`;
  const e0 = errs.length;
  await p.evaluate(h => { const d = document.createElement('div'); d.innerHTML = h; [...d.children].forEach(c => document.body.appendChild(c)); }, html);
  await p.addStyleTag({ content: css }); await p.evaluate(js); await p.waitForTimeout(1300);
  const st = () => p.evaluate(() => { const bar = document.getElementById('looty-sticky-atc'); const r = bar.getBoundingClientRect(); const o = document.querySelector('product-form form[action*="/cart/add"] button[name="add"], button.product-form__submit'); const sel = document.querySelector('.pumper_block .pmpr-tier-shell__card[data-selected="true"] .pmpr-tier-price__total'); return { price: bar.querySelector('.looty-satc__price').textContent, tier: bar.querySelector('.looty-satc__tier').textContent, label: bar.querySelector('button').textContent, off: bar.classList.contains('is-off'), barTop: Math.round(r.top), vh: innerHeight, y: Math.round(scrollY), origTop: o ? Math.round(o.getBoundingClientRect().top) : null, pumper: !!document.querySelector('.pumper_block'), tierPrice: sel ? sel.textContent.trim() : null }; });
  const cart = () => p.evaluate(async () => { const j = await (await fetch('/cart.js')).json(); return { total: j.total_price / 100, items: j.items.map(i => ({ t: i.product_title.replace(/【[^】]*】/g, '').trim().slice(0, 14), v: i.variant_title, q: i.quantity, line: i.final_line_price / 100 })) }; });
  const tapBar = async () => { await p.locator('#looty-sticky-atc button').tap(); };
  return { ctx, p, prod, st, cart, tapBar, errs, e0 };
}
module.exports = { open, yen };
