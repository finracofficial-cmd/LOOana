// 11/23 商品ページで「2個購入」を選んだときの動きを読む（iPhone 13 の画面・購入はしない・連絡先は入れない・計測の通信は止める）
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  await ctx.route('**/*', r => BLOCK.test(r.request().url()) ? r.abort() : r.continue());
  const p = await ctx.newPage();
  await p.goto('https://looty-japan.com/products/nano-fine-fiber-defogging-and-windproof-window-cleaning-brush', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4000);
  const dump = async (lab) => {
    const r = await p.evaluate(() => {
      const el = document.querySelector('.pumper_block') || document.querySelector('[class*="pumper"]');
      if (!el) return { none: true };
      const sels = [...el.querySelectorAll('select')].map(s => ({ name: s.name || s.className.slice(0, 40), value: s.options[s.selectedIndex] ? s.options[s.selectedIndex].text.trim() : null, opts: [...s.options].map(o => o.text.trim()), vis: !!(s.offsetParent) }));
      const cls = [...new Set([...el.querySelectorAll('*')].map(e => (e.className && e.className.baseVal === undefined ? String(e.className) : '')).join(' ').split(/\s+/).filter(c => /pumper|selected|active|bar|offer|variant/i.test(c)))].slice(0, 60);
      return { text: el.innerText.replace(/\s+/g, ' ').slice(0, 700), sels, cls, rect: (() => { const q = el.getBoundingClientRect(); return [Math.round(q.top + scrollY), Math.round(q.height)]; })() };
    });
    console.log('■', lab); console.log(JSON.stringify(r));
  };
  await dump('最初の状態');
  const main = await p.evaluate(() => { const f = document.querySelector('form[action*="/cart/add"]'); const id = f && f.querySelector('[name=id]'); const sel = [...document.querySelectorAll('variant-radios input:checked, variant-selects select, fieldset input[type=radio]:checked')].map(e => e.value || (e.options && e.options[e.selectedIndex].text)); const btns = [...document.querySelectorAll('button, a.button, [role=button], shopify-accelerated-checkout, shopify-buy-it-now-button, .shopify-payment-button')].filter(e => e.offsetParent).map(e => (e.innerText || e.tagName).replace(/\s+/g, ' ').slice(0, 30)).filter(t => /カート|購入|buy|Pay|SHOPIFY|選ぶ/i.test(t)); return { variantId: id && id.value, sel, btns: [...new Set(btns)] }; });
  console.log('■ 商品ページの選択とボタン'); console.log(JSON.stringify(main));
  // 「2個購入」の行を押す
  const clicked = await p.evaluate(() => { const el = document.querySelector('.pumper_block') || document.querySelector('[class*="pumper"]'); const cand = [...el.querySelectorAll('*')].filter(e => e.children.length < 12 && /2個購入/.test(e.innerText || '') && !/1個購入/.test(e.innerText || '')); const t = cand.sort((a, b) => (a.innerText.length - b.innerText.length))[0]; if (!t) return null; t.scrollIntoView({ block: 'center' }); t.click(); return t.tagName + '.' + String(t.className).slice(0, 80); });
  console.log('■ 押した要素', clicked); await p.waitForTimeout(1500);
  await dump('「2個購入」を押したあと');
  const el = await p.$('.pumper_block') || await p.$('[class*="pumper"]');
  if (el) await el.screenshot({ path: OUT + '/bundle_2.png' });
  await b.close();
})();
