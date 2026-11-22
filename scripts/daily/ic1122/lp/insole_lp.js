// 11/22 インソールの商品ページを見る（iPhone 13 の画面・購入はしない・計測の通信は止める）: サイズの案内と、購入ボタンのまわりの文
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  await ctx.route('**/*', r => BLOCK.test(r.request().url()) ? r.abort() : r.continue());
  const p = await ctx.newPage();
  await p.goto('https://looty-japan.com/products/soft-super-sports-shock-absorption-sweat-absorbent-sockliner-with-massage-function', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4000);
  const info = await p.evaluate(() => {
    const vis = e => e.offsetParent !== null;
    const txt = document.body.innerText;
    const lines = txt.split('\n').map(s => s.trim()).filter(Boolean);
    const size = lines.map((s, i) => ({ i, s })).filter(x => /サイズ|cm|センチ|交換|返品|カット|大きめ|小さめ/.test(x.s)).map(x => x.i + ': ' + x.s.slice(0, 110));
    const pick = [...document.querySelectorAll('fieldset, variant-radios, variant-selects, .product-form__input')].filter(vis).map(e => ({ y: Math.round(e.getBoundingClientRect().top + scrollY), t: e.innerText.replace(/\s+/g, ' ').slice(0, 260) })).slice(0, 6);
    const btn = [...document.querySelectorAll('button[name=add], form[action*="/cart/add"] button[type=submit]')].filter(vis)[0];
    const by = btn ? Math.round(btn.getBoundingClientRect().top + scrollY) : null;
    // 購入ボタンの上下 350px にある文字
    const near = []; const seen = new Set();
    document.querySelectorAll('p, span, li, div, h2, h3, button, label').forEach(e => { if (!vis(e) || e.children.length > 2) return; const r = e.getBoundingClientRect(); const y = r.top + scrollY; const t = e.innerText.replace(/\s+/g, ' ').trim(); if (by && Math.abs(y - by) < 350 && t.length > 3 && t.length < 120 && !seen.has(t)) { seen.add(t); near.push(Math.round(y - by) + ': ' + t); } });
    const imgs = [...document.querySelectorAll('img')].filter(vis).map(i => ({ y: Math.round(i.getBoundingClientRect().top + scrollY), alt: (i.alt || '').slice(0, 60), w: i.naturalWidth })).filter(i => /サイズ|size/i.test(i.alt)).slice(0, 8);
    return { height: document.body.scrollHeight, lines: lines.length, size, pick, by, near: near.slice(0, 40), imgs, nimg: document.querySelectorAll('img').length };
  });
  console.log(JSON.stringify(info, null, 1));
  const shots = [['top', 0], ['picker', Math.max(0, (info.pick[0] ? info.pick[0].y : 600) - 120)], ['buy', Math.max(0, (info.by || 2000) - 420)]];
  for (const [n, y] of shots) { await p.evaluate(y => window.scrollTo(0, y), y); await p.waitForTimeout(900); await p.screenshot({ path: OUT + '/insole_' + n + '.png' }); }
  await b.close();
})();
