// 商品ページのスマホ表示で、まとめ買い（数量割引）表示の位置と初期選択を確認する（読み取りのみ）
const { chromium, devices } = require('playwright');
const fs = require('fs');
const P = {
  cleaner: 'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush',
  wiper: 'soft-silicone-car-squeegee-integrated-windshield-glass-scraper-tool-scratch-free-paint-safe-auto-washing-accessory-for-home-use',
  pants: 'winter-sweatwear-men-plush-thick-fleece-sweatpant-lambswool-thermal-trousers-casual-pants-waterproof-windproof-warm-cotton-pants',
  gap: 'car-seat-gap-plug-strip-storage-box',
};
(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const [k, h] of Object.entries(P)) {
    const ctx = await browser.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
    const page = await ctx.newPage();
    try {
      const resp = await page.goto('https://looty-japan.com/products/' + h, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(7000);
      const r = await page.evaluate(() => {
        const vh = window.innerHeight;
        const top = el => Math.round(el.getBoundingClientRect().top + window.scrollY);
        const find = (re) => {
          let best = null;
          for (const el of document.querySelectorAll('body *')) {
            if (el.children.length > 0) continue;
            const t = (el.textContent || '').trim();
            if (!t || !re.test(t)) continue;
            const b = el.getBoundingClientRect();
            if (b.width === 0 || b.height === 0) continue;
            const y = top(el);
            if (best === null || y < best.y) best = { y, text: t.slice(0, 60) };
          }
          return best;
        };
        const btn = [...document.querySelectorAll('button, input[type=submit]')].filter(b => /カートに追加/.test(b.textContent || b.value || '') && b.getBoundingClientRect().height > 0).map(b => top(b)).sort((a, b) => a - b)[0];
        const checked = [...document.querySelectorAll('input[type=radio]:checked')].map(i => {
          const lab = i.closest('label') || (i.id && document.querySelector('label[for="' + i.id + '"]')) || i.parentElement;
          return { name: i.name, value: (i.value || '').slice(0, 40), label: lab ? (lab.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 80) : '' };
        });
        return {
          title: document.title.slice(0, 80), vh, pageH: document.body.scrollHeight,
          price: find(/^¥[\d,]+$/), qtyLabel: find(/^数量$/),
          one: find(/1個購入/), two: find(/2個購入/), three: find(/3個購入/),
          vip: find(/VIP特典/), bulkText: find(/まとめ買い/), addToCart: btn, checked,
          text: document.body.innerText,
        };
      });
      r.status = resp.status();
      fs.writeFileSync('pdp_text_' + k + '_1112.txt', r.text);
      delete r.text; out[k] = r;
    } catch (e) { out[k] = { error: String(e).slice(0, 300) }; }
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync('pdp_check_1112.json', JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out, null, 1));
})();
