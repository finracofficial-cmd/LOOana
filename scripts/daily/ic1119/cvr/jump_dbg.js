// 11/19 「商品を選ぶ」ボタンが2つに見えた3商品の中身を読む（読むだけ・計測の通信は止める）
const { chromium, devices } = require('playwright'); const { open } = require('./jump_lib.js');
(async () => {
  const b = await chromium.launch();
  for (const slug of process.argv.slice(2)) {
    const t = await open(b, devices['iPhone 13'], slug);
    const r = await t.p.evaluate(() => { const bars = document.querySelectorAll('#looty-jump'); const bar = bars[0]; return { bars: bars.length, html: bar.outerHTML.replace(/\s+/g, ' ').slice(0, 900), buttons: [...bar.querySelectorAll('button')].map(x => ({ cls: x.className, text: x.innerText.slice(0, 30), id: x.id, parent: x.parentElement.className || x.parentElement.id })) }; });
    console.log('■', slug.slice(0, 40)); console.log(JSON.stringify(r, null, 1));
    await t.ctx.close();
  }
  await b.close();
})();
