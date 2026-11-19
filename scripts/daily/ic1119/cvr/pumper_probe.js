// 11/19 まとめ買いの枠（Pumper）の作りを読む。読むだけ
const { chromium, devices } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage();
  await p.goto('https://looty-japan.com/products/' + process.argv[2], { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500);
  const html = await p.evaluate(() => {
    const el = document.querySelector('.pumper_block') || document.querySelector('[class*="pumper"]');
    if (!el) return 'なし';
    const c = el.cloneNode(true);
    c.querySelectorAll('svg,style,script,img').forEach(x => x.remove());
    return c.outerHTML.replace(/\s+/g, ' ').replace(/ style="[^"]*"/g, '').replace(/ data-[a-z-]+="[^"]{40,}"/g, '');
  });
  console.log(html.slice(0, 7000));
  await b.close();
})();
