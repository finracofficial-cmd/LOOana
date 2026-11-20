// 11/21 まとめ買いの枠とカートの今の出方を読む（iPhone 13 の画面・購入はしない・計測の通信は止める）
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
const H = { 'ガラスクリーナー': 'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush', 'ナノ': 'washable-reusable-fuzz-remover' };
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  await ctx.route('**/*', r => BLOCK.test(r.request().url()) ? r.abort() : r.continue());
  const p = await ctx.newPage();
  // 商品の一覧から、フック・インソールのページの名前を引く
  await p.goto('https://looty-japan.com/products.json?limit=250', { timeout: 60000 });
  const prods = JSON.parse(await p.evaluate(() => document.body.innerText)).products;
  for (const k of ['ヘッドレストフック', 'マジックインソール', 'W固定']) { const f = prods.find(x => x.title.includes(k)); if (f) H[k] = f.handle; }
  for (const [name, h] of Object.entries(H)) {
    await p.goto('https://looty-japan.com/products/' + h, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500);
    const r = await p.evaluate(() => {
      const el = document.querySelector('.pumper_block') || document.querySelector('[class*="pumper"]');
      if (!el) return { none: true };
      const radios = [...el.querySelectorAll('input[type=radio]')].map(i => ({ checked: i.checked, label: (i.closest('label,div') || i).innerText.replace(/\s+/g, ' ').slice(0, 60) }));
      const btn = document.querySelector('form[action*="/cart/add"] button[type=submit], button[name=add]');
      return { y: Math.round(el.getBoundingClientRect().top + scrollY), btnY: btn ? Math.round(btn.getBoundingClientRect().top + scrollY) : null, h: innerHeight, text: el.innerText.replace(/\s+/g, ' ').slice(0, 420), radios };
    });
    console.log('■', name, h); console.log(JSON.stringify(r));
  }
  // カート: ガラスクリーナー1個を入れて、カートの画面の文字を読む
  await p.goto('https://looty-japan.com/products/' + H['ガラスクリーナー'], { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3000);
  const vid = await p.evaluate(() => { const i = document.querySelector('form[action*="/cart/add"] [name=id]'); return i ? i.value : null; });
  await p.evaluate(async (id) => { await fetch('/cart/add.js', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id, quantity: 1 }) }); }, vid);
  await p.goto('https://looty-japan.com/cart', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(5000);
  const cart = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' ').slice(0, 1500));
  console.log('■ カート（1個）の画面の文字:'); console.log(cart);
  await p.screenshot({ path: process.argv[2] || 'cart_1121.png', fullPage: true });
  await b.close();
})();
