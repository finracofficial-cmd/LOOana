// 11/19 お店に入った「商品を選ぶ」ボタンの、PC での見え方と、商品ページ以外・ページのいちばん下の余白を確かめる（読むだけ・計測の通信は止める）
const { chromium, devices } = require('playwright');
const OUT = process.argv[2];
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/i;
const G = 'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush';
(async () => {
  const b = await chromium.launch();
  const look = async (name, opt, path, shot) => { const ctx = await b.newContext({ ...opt, locale: 'ja-JP' }); const p = await ctx.newPage(); await p.route(u => BLOCK.test(u.href), q => q.abort());
    await p.goto('https://looty-japan.com' + path, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3000);
    const r = await p.evaluate(() => { const sec = document.querySelector('[id*="custom_liquid_AHmw"]'); const bar = document.getElementById('looty-jump'); const out = { 幅: innerWidth, セクションあり: !!sec, 帯のコードあり: !!bar };
      if (sec) { const inner = sec.querySelector('[class*="padding"]'); const cs = inner ? getComputedStyle(inner) : null; out.セクションの高さ = Math.round(sec.getBoundingClientRect().height); out.余白 = cs ? cs.paddingTop + ' / ' + cs.paddingBottom : null; out.背景 = getComputedStyle(sec.firstElementChild || sec).backgroundColor; }
      if (bar) { const s = getComputedStyle(bar); out.帯の表示 = s.display; out.帯の位置 = s.display === 'none' ? null : Math.round(bar.getBoundingClientRect().top); }
      out.bodyの下の余白 = getComputedStyle(document.body).paddingBottom; return out; });
    console.log('■', name, JSON.stringify(r));
    if (shot) { await p.evaluate(() => { const sec = document.querySelector('[id*="custom_liquid_AHmw"]'); if (sec) sec.scrollIntoView({ block: 'center' }); }); await p.waitForTimeout(900); await p.screenshot({ path: OUT + '/' + shot }); }
    await ctx.close(); };
  const pc = { viewport: { width: 1280, height: 800 } }, tab = { viewport: { width: 820, height: 1100 } };
  await look('PC・商品ページ', pc, '/products/' + G, 'pc_product_footer.png');
  await look('タブレット幅（820px）・商品ページ', tab, '/products/' + G, null);
  await look('スマホ・商品ページ（フッターの上）', devices['iPhone 13'], '/products/' + G, 'sp_product_footer.png');
  await look('スマホ・トップページ', devices['iPhone 13'], '/', 'sp_home_footer.png');
  await look('スマホ・カートのページ', devices['iPhone 13'], '/cart', null);
  await look('PC・トップページ', pc, '/', null);
  await b.close();
})();
