# -*- coding: utf-8 -*-
"""11/26 「あたり商品は時期で変わるよね？この時期なら何が良い？」
① 月ごとに、利益の大きい商品の上位5つ（7月〜11月・data/daily の CSV・w1125.py の関数。利益＝売上−原価−広告費）
② 10/1 以降に広告を始めた23本を「何に使う物か」で分け直す（洗う・拭く・見えやすくする／車の中の置き場・固定／身につける防寒／暖める・加湿／美容・体）。分け方は Claude の判断
   当たり＝開始〜11/21 の利益 5万円以上（ic1122/plan/life_1122.txt の ②）"""
import io, contextlib, os, re, collections
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D0 + '../../../..')
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1125.py').read(), g)
A, ALLD, agg, WIN, ACCT = g['A'], g['ALLD'], g['agg'], g['WIN'], g['ACCT']
out = []
def P(s=''): print(s); out.append(s)
P('■ ① 月ごとの利益の上位5商品（その月の利益・倍率）｜店の利益/日')
for m in ('2026-07', '2026-08', '2026-09', '2026-10', '2026-11'):
    ds = [d for d in ALLD if d.startswith(m)]; WIN['s' + m] = ds
    try: N, DC, Q, K = agg(ds, 's' + m)
    except AssertionError: P(f"  {m[5:]}月: バリエーション別の記録（daily_variant.csv）が月の途中からなので出さない"); continue
    pr = {n: (N[n] - K[n] - A(ds, n), (N[n] - K[n]) / A(ds, n) if A(ds, n) else None) for n in N}
    top = sorted(pr, key=lambda n: -pr[n][0])[:5]; tot = sum(N.values()) - sum(K.values()) - ACCT(ds)
    P(f"  {m[5:]}月（{len(ds)}日）: " + '・'.join(f"{n} {pr[n][0]:+,.0f}（{'—' if pr[n][1] is None else format(pr[n][1], '.2f')}）" for n in top) + f"｜店 {tot/len(ds):,.0f}円/日")
USE = {'伸縮ワックス洗車ブラシ': '洗う・拭く・見えやすくする', 'ワイド水切りワイパー': '洗う・拭く・見えやすくする', 'クリアビューレインガードフィルム': '洗う・拭く・見えやすくする', 'コードレス毛玉クリーナー': '洗う・拭く・見えやすくする', 'ロングニトリル家事手袋': '洗う・拭く・見えやすくする',
       'マグネットドアクッション': '車の中の置き場・固定・保護', '高見えレザードアポケット': '車の中の置き場・固定・保護', 'すき間収納シートポケット': '車の中の置き場・固定・保護', '360°マルチクリップ車載スマホホルダー': '車の中の置き場・固定・保護',
       'ハイウエストシェイプパンツ': '身につける・防寒', 'ふわとろ高密度ブランケット': '身につける・防寒', 'シリコンホールド膝サポーター': '身につける・防寒', 'アーチフィット逆ヒールサンダル': '身につける・防寒', '防風あったか裏起毛パンツ': '身につける・防寒', '3WAY着る電気ブランケット': '身につける・防寒', '裏起毛タッチ防寒グローブ': '身につける・防寒',
       'コードレスダブルミスト加湿器': '加湿器', '充電式ダブルミスト卓上加湿器': '加湿器',
       'ポータブルヒートシーラー': '台所・家の小物', 'ファスナー修理キット': '台所・家の小物',
       'ネックマッサージャー': '美容・体', '携帯電動シェーバー': '美容・体', 'スマートノーズEMS美顔器': '美容・体'}
rows = []; on = False
for l in open('scripts/daily/ic1122/plan/life_1122.txt'):
    if l.startswith('■ ②'): on = True; continue
    if l.startswith('■ ③'): break
    m = re.match(r'^  (.+?): (\d\d-\d\d)〜・(\d+)日・広告費 ([\d,]+)・利益 ([+\-][\d,]+)・最初の7日 ([\d.]+)・(停止|配信中)', l)
    if on and m: rows.append(dict(n=m.group(1), start=m.group(2), ad=int(m.group(4).replace(',', '')), p=int(m.group(5).replace(',', '').replace('+', '')), f7=float(m.group(6))))
assert len(rows) == 23 and all(r['n'] in USE for r in rows)
P('■ ② 10/1 以降に広告を始めた23本を「何に使う物か」で分ける（当たり＝利益 5万円以上）')
for u in ('洗う・拭く・見えやすくする', '車の中の置き場・固定・保護', '台所・家の小物', '美容・体', '加湿器', '身につける・防寒'):
    v = sorted([r for r in rows if USE[r['n']] == u], key=lambda r: -r['p']); hit = [r for r in v if r['p'] >= 50000]
    P(f"  {u}: {len(v)}本・当たり {len(hit)}本・利益の合計 {sum(r['p'] for r in v):+,}｜" + '・'.join(f"{r['n']}（{r['start']}〜・7日 {r['f7']:.2f}・{r['p']:+,}）" for r in v))
open(D0 + 'season_1126.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
