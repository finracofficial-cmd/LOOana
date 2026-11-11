// 数量割引ウィジェットの初期選択を確認（読み取りのみ）
const { chromium, devices } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  const page = await ctx.newPage();
  await page.goto('https://looty-japan.com/products/soft-silicone-car-squeegee-integrated-windshield-glass-scraper-tool-scratch-free-paint-safe-auto-washing-accessory-for-home-use', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(7000);
  const r = await page.evaluate(() => {
    const leaf = [...document.querySelectorAll('body *')].find(el => el.children.length === 0 && /1個購入/.test(el.textContent || '') && el.getBoundingClientRect().height > 0);
    if (!leaf) return 'not found';
    // ウィジェットの外枠まで上がる（3つの選択肢を全部含む最小の祖先）
    let box = leaf;
    while (box.parentElement && !(/3個購入/.test(box.textContent || ''))) box = box.parentElement;
    const rows = [...box.querySelectorAll('*')].filter(e => /^(1個購入|2個購入で10％オフ|3個購入で15％オフ)$/.test((e.textContent || '').trim()) && e.children.length === 0);
    const info = rows.map(e => {
      let p = e; const chain = [];
      for (let i = 0; i < 6 && p && p !== box; i++) { chain.push((p.tagName + '.' + (p.className || '').toString().slice(0, 90)) + (p.getAttribute('aria-checked') ? ' aria-checked=' + p.getAttribute('aria-checked') : '') + (p.getAttribute('data-selected') ? ' data-selected=' + p.getAttribute('data-selected') : '')); p = p.parentElement; }
      const opt = e.closest('[class*=option],[class*=tier],[class*=offer],[class*=bar],label,li') || e.parentElement;
      const cs = getComputedStyle(opt);
      return { text: e.textContent.trim(), chain, border: cs.borderColor + ' ' + cs.borderWidth, bg: cs.backgroundColor };
    });
    const inputs = [...box.querySelectorAll('input')].map(i => ({ type: i.type, name: i.name, value: i.value, checked: i.checked }));
    const qty = [...document.querySelectorAll('input[name=quantity]')].map(i => i.value);
    return { boxTag: box.tagName + '.' + (box.className || '').toString().slice(0, 120), info, inputs, qty };
  });
  console.log(JSON.stringify(r, null, 1));
  await browser.close();
})();
