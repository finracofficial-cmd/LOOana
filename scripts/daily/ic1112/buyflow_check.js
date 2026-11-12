// 購入の流れが動くかの確認（スマホ表示・商品ページ→カート追加→決済画面の表示まで。情報の入力・注文はしない）
const { chromium, devices } = require('playwright');
const P = {
  cleaner: 'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush',
  wiper: 'soft-silicone-car-squeegee-integrated-windshield-glass-scraper-tool-scratch-free-paint-safe-auto-washing-accessory-for-home-use',
  car: null,
};
(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const [k, h] of Object.entries(P)) {
    if (!h) continue;
    const ctx = await browser.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
    const page = await ctx.newPage();
    const errs = []; page.on('pageerror', e => errs.push(String(e).slice(0, 160)));
    const r = { steps: [] };
    try {
      const resp = await page.goto('https://looty-japan.com/products/' + h, { waitUntil: 'domcontentloaded', timeout: 60000 });
      r.status = resp.status();
      await page.waitForTimeout(6000);
      const btn = page.locator('button[name="add"], form[action*="/cart/add"] button[type="submit"]').first();
      r.btnCount = await page.locator('button[name="add"], form[action*="/cart/add"] button[type="submit"]').count();
      r.btnText = (await btn.innerText().catch(() => '')).trim().slice(0, 40);
      r.btnDisabled = await btn.isDisabled().catch(() => null);
      await btn.scrollIntoViewIfNeeded().catch(() => {});
      await btn.click({ timeout: 15000 });
      r.steps.push('clicked add-to-cart');
      await page.waitForTimeout(5000);
      const cart = await page.evaluate(async () => { const x = await fetch('/cart.js', { credentials: 'same-origin' }); return x.json(); });
      r.cart = { item_count: cart.item_count, total_price: cart.total_price, items: cart.items.map(i => ({ title: i.product_title.slice(0, 40), qty: i.quantity, price: i.final_line_price })) };
      r.urlAfterAdd = page.url().slice(0, 120);
      const co = await page.goto('https://looty-japan.com/checkout', { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(8000);
      r.checkout = { status: co.status(), url: page.url().replace(/\?.*$/, '').slice(0, 90), title: (await page.title()).slice(0, 60) };
      const txt = await page.evaluate(() => document.body.innerText);
      r.checkoutHas = { email: /メール|連絡先/.test(txt), pay: /お支払い|支払い/.test(txt), total: (txt.match(/合計[\s\S]{0,40}?¥[\d,]+/) || [''])[0].replace(/\s+/g, ' ').slice(0, 60), shopPay: /Shop Pay|shop pay/i.test(txt), errorText: (txt.match(/エラー|問題が発生|利用できません|在庫切れ|売り切れ/g) || []).slice(0, 5) };
      r.checkoutTextHead = txt.replace(/\s+/g, ' ').slice(0, 400);
    } catch (e) { r.error = String(e).slice(0, 300); }
    r.pageErrors = errs.slice(0, 5);
    out[k] = r;
    await ctx.close();
  }
  await browser.close();
  require('fs').writeFileSync('buyflow_check_1112_1040.json', JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out, null, 1));
})();
