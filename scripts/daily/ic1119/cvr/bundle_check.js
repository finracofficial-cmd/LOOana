// 11/19 まとめ買い（2個）の選択肢を選んだとき、2個目の色・サイズがどうなるかを確かめる（iPhone 13 の画面・購入はしない）
const { chromium, devices } = require('playwright');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  const p = await ctx.newPage();
  await p.goto('https://looty-japan.com/products/soft-super-sports-shock-absorption-sweat-absorbent-sockliner-with-massage-function', { waitUntil: 'load', timeout: 60000 });
  await p.waitForTimeout(3500);
  // まとめ買いの部品を探す
  const w = await p.evaluate(() => {
    const cands = [...document.querySelectorAll('[class*="kaching"], [class*="bundle"], [class*="quantity-break"], [class*="pumper"], [id*="bundle"], [class*="qb"], [class*="volume"]')].filter(e => e.offsetParent && e.innerText && e.innerText.length > 10);
    const top = cands.filter(e => !cands.some(o => o !== e && o.contains(e)));
    return top.slice(0, 4).map(e => ({ tag: e.tagName, cls: (e.className || '').toString().slice(0, 80), y: Math.round(e.getBoundingClientRect().top + scrollY), text: e.innerText.replace(/\s+/g, ' ').slice(0, 500), selects: [...e.querySelectorAll('select')].map(s => ({ v: s.options[s.selectedIndex] ? s.options[s.selectedIndex].text : '', n: s.options.length })).slice(0, 8) }));
  });
  console.log('まとめ買いの部品:', JSON.stringify(w, null, 1).slice(0, 2500));
  await b.close();
})();
