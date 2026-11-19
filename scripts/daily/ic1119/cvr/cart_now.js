// 11/19 カートの画面を今の状態で読む（1個と2個）。計測の通信は止める・連絡先は入れない・支払いはしない
const { chromium, devices } = require('playwright');
const OUT = process.argv[2], TAG = process.argv[3] || 'now';
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/i;
(async () => {
  const b = await chromium.launch();
  for (const qty of [1, 2]) {
    const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage();
    await p.route(u => BLOCK.test(u.href), r => r.abort());
    const errs = []; p.on('pageerror', e => errs.push((e.message || '').slice(0, 70)));
    await p.goto('https://looty-japan.com/products/sun-umbrella', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500);
    if (qty === 2) { const two = p.locator('.pumper_block .pmpr-tier-shell__card', { hasText: '2個購入' }).first(); await two.scrollIntoViewIfNeeded(); await two.tap(); await p.waitForTimeout(1500); }
    const e0 = errs.length;
    const btn = p.locator('product-form form[action*="/cart/add"] button[name="add"]').first(); await btn.scrollIntoViewIfNeeded(); await btn.tap(); await p.waitForTimeout(5000);
    const drawer = await p.evaluate(() => { const k = [...document.querySelectorAll('body *')].filter(e => { const s = getComputedStyle(e); const r = e.getBoundingClientRect(); return (s.position === 'fixed' || s.position === 'absolute') && r.height > 400 && r.width > 250 && /ご購入手続き|カート/.test(e.innerText || ''); }).sort((a, b) => (a.innerText || '').length - (b.innerText || '').length)[0]; if (!k) return null; const co = [...k.querySelectorAll('button, a')].find(e => /ご購入手続き/.test(e.innerText || '')); return { text: k.innerText.replace(/\s+/g, ' ').slice(0, 900), coTop: co ? Math.round(co.getBoundingClientRect().top) : null, vh: innerHeight }; });
    const cart = await p.evaluate(async () => { const j = await (await fetch('/cart.js')).json(); return { total: j.total_price / 100, items: j.items.map(i => ({ t: i.product_title.replace(/【[^】]*】/g, '').trim().slice(0, 16), v: i.variant_title, q: i.quantity, line: i.final_line_price / 100 })) }; });
    console.log(`■ ${qty}個 カート`, JSON.stringify(cart)); console.log('  カートの画面の文字:', drawer ? drawer.text : '（見つからず）'); console.log('  「ご購入手続きへ」の位置:', drawer && drawer.coTop, '/ 画面の高さ', drawer && drawer.vh, '｜カートに入れた後のエラー', JSON.stringify([...new Set(errs.slice(e0))]));
    await p.screenshot({ path: `${OUT}/cart_${TAG}_${qty}.png` });
    if (qty === 2) { await p.goto('https://looty-japan.com/checkout', { waitUntil: 'domcontentloaded', timeout: 60000 }); await p.waitForTimeout(5000);
      const fill = async (ph, v) => { const el = p.getByPlaceholder(ph, { exact: false }).first(); await el.fill(v, { timeout: 8000 }).catch(() => {}); await p.waitForTimeout(400); };
      await fill('姓', 'テスト'); await fill('名', '確認'); await fill('郵便番号', '100-0001'); await p.waitForTimeout(2500); await p.locator('select[name="zone"]').first().selectOption({ label: '東京都' }).catch(() => {}); await fill('市区町村', '千代田区'); await fill('住所', '千代田1-1'); await p.keyboard.press('Tab'); await p.waitForTimeout(7000);
      const t = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' ')); const i = t.indexOf('配送方法'); console.log('  決済画面の配送方法の欄:', t.slice(i, i + 60), '｜「荷物」の文:', /個の荷物/.test(t) ? 'あり' : 'なし', '｜合計の欄:', (t.match(/合計[^¥]{0,20}¥[\d,]+/) || [''])[0]); }
    await ctx.close();
  }
  await b.close();
})();
