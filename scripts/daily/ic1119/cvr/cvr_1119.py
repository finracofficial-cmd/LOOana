# -*- coding: utf-8 -*-
"""11/19 「CVR を上げきりたい」: ①9月から今までの倍率を 1人を連れてくる値段（広告費÷来訪）・買う率（購入完了÷来訪）・1注文の粗利 に分ける
②買う率を段ごと（カート・決済画面・完了）に週で並べる ③商品ページ別（広告から来た人・30日）④決済画面で離れる人の中身 ⑤買う率が上がると利益がいくら増えるか
来訪・購入完了は cvr/raw.json（Shopify）、広告費・粗利は data/daily（w1118.py の積み直し）"""
import json, io, contextlib, datetime, statistics as st
R = json.load(open('scripts/daily/ic1119/cvr/raw.json'))
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1118.py').read(), g)
WIN, agg, ACCT, ALLD = g['WIN'], g['agg'], g['ACCT'], g['ALLD']
def gp_ad(ds):
    key = 'c' + ds[0] + ds[-1]; WIN[key] = ds; N, DC, Q, K = agg(ds, key); return sum(N.values()) - sum(K.values()), ACCT(ds)
rows = []
print('■ 週ごと: 倍率 ＝ 来訪÷広告費1万円 × 買う率（購入完了÷来訪）× 1注文の粗利 ｜ カート率・決済画面÷カート・完了÷決済画面')
for w, s, c, k, o in R['week']:
    d0 = datetime.date.fromisoformat(w); ds = [(d0 + datetime.timedelta(i)).isoformat() for i in range(7)]; ds = [d for d in ds if d in ALLD]
    gp, ad = gp_ad(ds); rows.append((w, s / ad * 1e4, o / s, gp / o, gp / ad, c / s, k / c, o / k, ad / len(ds)))
    print(f'  {w[5:]}週: 倍率 {gp/ad:.2f} ＝ {s/ad*1e4:.0f}人 × {o/s:.2%} × {gp/o:,.0f}円 ｜ {c/s:.2%}・{k/c:.0%}・{o/k:.0%} ｜ 1人あたり {ad/s:.0f}円')
sep = rows[0:4]; now = rows[-2:]
f = lambda rs, i: st.mean(r[i] for r in rs)
print(f'■ 9月（8/31〜9/27 の4週の平均）→ 今（11/9〜18 の2週の平均）')
for lab, i, fmt in (('来訪÷広告費1万円', 1, '{:.1f}人'), ('買う率（購入完了÷来訪）', 2, '{:.2%}'), ('1注文の粗利', 3, '{:,.0f}円'), ('倍率', 4, '{:.2f}'), ('カート率', 5, '{:.2%}'), ('完了÷決済画面', 7, '{:.1%}')):
    a, b = f(sep, i), f(now, i); print(f'  {lab}: ' + fmt.format(a) + ' → ' + fmt.format(b) + f'（{b/a-1:+.1%}）')
cv = [r[2] for r in rows]; print(f'  買う率の週ごとの幅（12週）: {min(cv):.2%}〜{max(cv):.2%}')
print('■ 商品ページ別（広告から来た人・10/20〜11/18）: 来訪・カート率・完了÷決済画面・買う率')
for n, s, c, k, o in sorted(R['page'], key=lambda r: -r[4] / r[1]): print(f'  {n}: {s:,}・{c/s:.2%}・{o/k:.0%}・{o/s:.2%}')
tot = [sum(r[i] for r in R['page']) for i in range(1, 5)]; print(f'  15ページの合計: カート率 {tot[1]/tot[0]:.2%}・完了÷決済画面 {tot[3]/tot[2]:.0%}・買う率 {tot[3]/tot[0]:.2%}')
w = [r for r in R['week'] if r[0] == '2026-11-09'][0]; lost = w[3] - w[4]
print(f'■ 決済画面で離れた人（11/9〜15）: 決済画面 {w[3]}・完了 {w[4]}・離れた {lost}。連絡先を入れてから離れた決済は 11/12〜18 で {R["abandoned"]["2026-11-12_18"]}・11/5〜11 で {R["abandoned"]["2026-11-05_11"]}（期間が少しずれる）＝離れた人のおよそ {R["abandoned"]["2026-11-12_18"]/lost:.0%}〜{R["abandoned"]["2026-11-05_11"]/lost:.0%}。残りは連絡先を入れる前に離れている')
gp, ad = gp_ad(ALLD[-7:]); m = gp / ad
print(f'■ 買う率が上がると（直近7日 広告費 {ad/7:,.0f}円/日・倍率 {m:.2f}・利益 {(gp-ad)/7:,.0f}円/日。広告費と客単価はそのまま）')
for x in (0.05, 0.10, 0.20, 0.30): print(f'  買う率 +{x:.0%} → 倍率 {m*(1+x):.2f}・利益 {(gp*(1+x)-ad)/7:,.0f}円/日（{gp*x/7:+,.0f}）')
