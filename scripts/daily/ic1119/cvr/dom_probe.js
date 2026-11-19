// 11/19 商品ページの作りを調べる（まとめ買いの枠・色やサイズの選び方・元のボタン）。読むだけ
const { chromium, devices } = require('playwright');
const slugs = process.argv.slice(2);
(async () => {
  const b = await chromium.launch();
  for (const slug of slugs) {
    const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage();
    await p.goto('https://looty-japan.com/products/' + slug, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500);
    const r = await p.evaluate(() => {
      const q = s => [...document.querySelectorAll(s)];
      const add = document.querySelector('form[action*="/cart/add"] button[name="add"], button.product-form__submit');
      const forms = q('form[action*="/cart/add"]').map(f => ({ id: f.id, cls: f.className.slice(0, 60), hasAdd: !!f.querySelector('[name="add"]'), idInput: (f.querySelector('[name="id"]') || {}).value, qty: (f.querySelector('[name="quantity"]') || {}).value }));
      const custom = [...new Set(q('*').map(e => e.tagName.toLowerCase()).filter(t => t.includes('-')))].slice(0, 60);
      const radios = q('input[type="radio"]').map(i => ({ name: (i.name || '').replace(/\s+/g, ' ').slice(0, 30), val: (i.value || '').slice(0, 24), chk: i.checked, par: (i.closest('[class]') || {}).className.toString().slice(0, 50), inVS: !!i.closest('variant-selects, variant-radios') }));
      const selects = q('select').map(s => ({ name: (s.name || '').slice(0, 30), cls: s.className.slice(0, 40), n: s.options.length, val: (s.value || '').slice(0, 20), par: ((s.closest('[class*="kaching"],[class*="bundle"],[class*="pumper"],variant-selects') || {}).className || '').toString().slice(0, 60), vis: s.offsetParent !== null }));
      const appEls = [...new Set(q('[class*="kaching"],[class*="pumper"],[id*="kaching"],[id*="pumper"],[class*="bundle"]').map(e => e.tagName.toLowerCase() + '.' + e.className.toString().split(' ')[0]))].slice(0, 40);
      const scripts = [...new Set(q('script[src]').map(s => s.src).filter(s => /kaching|pumper|monster|bundle|upsell|sticky/i.test(s)).map(s => s.split('?')[0].slice(0, 110)))];
      return { addText: add && add.innerText.trim(), addDisabled: add && add.disabled, addTop: add && Math.round(add.getBoundingClientRect().top + scrollY), forms, custom, radios: radios.slice(0, 30), selects, appEls, scripts };
    });
    console.log('■', slug.slice(0, 40)); console.log(JSON.stringify(r, null, 1).slice(0, 5200));
    await ctx.close();
  }
  await b.close();
})();
