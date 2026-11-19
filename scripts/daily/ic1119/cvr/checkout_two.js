// 11/19 まとめ買い（2個）と1個で、決済画面に住所を入れた後の「配送方法」と合計の表示を比べる（iPhone 13 の画面・メールは入れない・支払いはしない）
const { chromium, devices } = require('playwright');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch();
  for (const qty of [2, 1]) {
    const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage();
    await p.goto('https://looty-japan.com/products/washable-reusable-fuzz-remover', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3000);
    if (qty === 2) { const two = p.getByText('2個購入で10％オフ', { exact: false }).first(); await two.scrollIntoViewIfNeeded(); await two.tap().catch(e => console.log('tap2 err', e.message.slice(0, 60))); await p.waitForTimeout(1500); }
    const btn = p.locator('button[name="add"], .product-form__submit').first(); await btn.scrollIntoViewIfNeeded(); await btn.tap(); await p.waitForTimeout(4000);
    const cart = await p.evaluate(async () => { const j = await (await fetch('/cart.js')).json(); return { total: j.total_price / 100, items: j.items.map(i => ({ t: i.product_title.replace(/【[^】]*】/g, '').trim().slice(0, 16), v: i.variant_title, q: i.quantity, line: i.final_line_price / 100 })) }; });
    console.log(`■ ${qty}個: カート`, JSON.stringify(cart));
    await p.goto('https://looty-japan.com/checkout', { waitUntil: 'domcontentloaded', timeout: 60000 }); await p.waitForTimeout(5000);
    const fill = async (ph, v) => { const el = p.getByPlaceholder(ph, { exact: false }).first(); await el.scrollIntoViewIfNeeded().catch(() => {}); await el.fill(v, { timeout: 8000 }).catch(e => console.log('  入力できず', ph, e.message.slice(0, 50))); await p.waitForTimeout(400); };
    await fill('姓', 'テスト'); await fill('名', '確認'); await fill('郵便番号', '100-0001'); await p.waitForTimeout(2500);
    const z = p.locator('select[name="zone"]').first(); await z.selectOption({ label: '東京都' }).catch(() => {});
    await fill('市区町村', '千代田区'); await fill('住所', '千代田1-1'); await p.keyboard.press('Tab'); await p.waitForTimeout(7000);
    const t = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
    const cut = (a, n) => { const i = t.indexOf(a); return i < 0 ? '（見つからず）' : t.slice(i, i + n); };
    console.log('  配送方法の欄:', cut('配送方法', 260));
    console.log('  注文内容の欄:', cut('小計', 260));
    await p.screenshot({ path: OUT + `/c_${qty}_full.png`, fullPage: true });
    await ctx.close();
  }
  await b.close();
})();
