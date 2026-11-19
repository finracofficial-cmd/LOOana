// 11/19 「商品を選ぶ」ボタンの動作確認: 押すと枠とカートボタンが見える位置へ移動するか・カートには入らないか・帯が隠れるか
const { chromium, devices } = require('playwright'); const { open } = require('./jump_lib.js');
const OUT = process.argv[2]; const J = o => JSON.stringify(o);
const P = [['ガラス', 'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush'], ['ワイパー（選択肢なし）', 'soft-silicone-car-squeegee-integrated-windshield-glass-scraper-tool-scratch-free-paint-safe-auto-washing-accessory-for-home-use'], ['インソール（色×サイズ）', 'soft-super-sports-shock-absorption-sweat-absorbent-sockliner-with-massage-function'], ['ブランケット（値段ちがい）', 'thickened-toka-long-wool-casual-blanket']];
(async () => {
  const b = await chromium.launch();
  for (const [devName, dev] of [['iPhone 13', devices['iPhone 13']], ['iPhone SE（小さい画面）', devices['iPhone SE']]]) {
    console.log('■', devName);
    for (const [name, slug] of P) {
      const t = await open(b, dev, slug); const a = await t.st();
      await t.tapBar(); await t.p.waitForTimeout(2200); const c = await t.st(); const n = await t.cartN();
      const ok = c.origTop >= 0 && c.origBottom <= c.vh && c.off && n === 0;
      console.log(` ${name}: 押す前 帯の値段 ${a.price} ${a.tier}・ボタン「${a.label}」・元のボタンは画面の ${a.origTop}px 下 → 押した後 元のボタン ${c.origTop}〜${c.origBottom}px（画面の高さ ${c.vh}）・枠の上 ${c.boxTop}px・帯は${c.off ? '隠れた' : '出たまま'}・カート ${n}個 ｜ ${ok ? '○' : '×'} ｜増えたエラーの種類 ${J([...new Set(t.errs.slice(t.e0))])}`);
      if (devName === 'iPhone 13' && name === 'ガラス') { await t.p.screenshot({ path: OUT + '/jump_glass_before.png' }).catch(() => {}); }
      await t.p.screenshot({ path: `${OUT}/jump_${devName.slice(7, 9).trim() || '13'}_${slug.slice(0, 6)}.png` });
      // そこから下へ流して、帯がまた出るか
      await t.p.evaluate(() => window.scrollBy(0, 1500)); await t.p.waitForTimeout(700); const d = await t.st();
      console.log(`    下へ動かすと帯は${d.off ? '隠れたまま ×' : 'また出る ○'}`);
      await t.ctx.close();
    }
  }
  // 2個を選んだときの帯の値段
  { const t = await open(b, devices['iPhone 13'], 'washable-reusable-fuzz-remover'); const two = t.p.locator('.pumper_block .pmpr-tier-shell__card', { hasText: '2個購入' }).first(); await two.scrollIntoViewIfNeeded(); await two.tap(); await t.p.waitForTimeout(1500); await t.p.evaluate(() => window.scrollTo(0, 200)); await t.p.waitForTimeout(1200); const s = await t.st(); console.log(`■ ナノで2個を選んで上に戻る: 帯 ${s.price} ${s.tier}・ボタン「${s.label}」`); await t.p.screenshot({ path: OUT + '/jump_nano_2ko.png' }); await t.ctx.close(); }
  await b.close();
})();
