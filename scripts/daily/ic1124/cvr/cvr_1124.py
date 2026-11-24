# -*- coding: utf-8 -*-
"""11/24 22時台「CVR の低さが気になる」: 買う率を入口（social＝広告・direct＝参照元なし・search）と段（カート・決済画面・完了）に分ける。週は月曜はじまり（9/28 の週は 9/29〜10/4 の6日）。
入力: sess_source_week_0929_1123_raw.json（Shopify）・../why/meta_acct_0928_1123_raw.json（Meta のリンククリック）"""
import json, os, collections, datetime
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'
R = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0, 0]))
for w, src, s, c, ch, done in json.load(open(D0 + 'sess_source_week_0929_1123_raw.json'))['rows']:
    if w == '2026-11-23': continue   # 1日だけ
    v = R[w][src if src in ('social', 'direct', 'search') else 'その他']
    for i, x in enumerate((s, c, ch, done)): v[i] += int(x)
CLK = collections.Counter()
for l in json.load(open(D0 + '../why/meta_acct_0928_1123_raw.json'))['data']['data'].split('\n')[1:]:
    if not l.strip(): continue
    d, cost, imp, k = l.strip().split(','); dd = datetime.date.fromisoformat(d)
    if dd < datetime.date(2026, 9, 29) or dd > datetime.date(2026, 11, 22): continue
    CLK[(dd - datetime.timedelta(dd.weekday())).isoformat()] += int(k)
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
f = lambda v: f"来訪 {v[0]:>6,}・カート {v[1]/v[0]:.2%}・決済画面÷カート {v[2]/v[1]:.0%}・完了÷決済画面 {v[3]/v[2]:.0%}・買う率 {v[3]/v[0]:.2%}"
P('■ 週ごと（月曜はじまり）: 店全体の買う率と、入口ごと')
for w in sorted(R):
    a = [sum(R[w][k][i] for k in R[w]) for i in range(4)]; so, di = R[w]['social'], R[w]['direct']
    P(f"  {w[5:]}の週: 店 {a[3]/a[0]:.2%}（来訪 {a[0]:,}）｜social {so[3]/so[0]:.2%}・direct {di[3]/di[0]:.2%}・search {R[w]['search'][3]/R[w]['search'][0]:.2%}｜来訪の割合 social {so[0]/a[0]:.0%}・direct {di[0]/a[0]:.0%}｜Meta のクリック {CLK[w]:,}・social 来訪÷クリック {so[0]/CLK[w]:.2f}・店の購入÷クリック {a[3]/CLK[w]:.2%}")
P('■ 段ごと（social＝広告から来た人）')
for w in sorted(R): P(f"  {w[5:]}の週: " + f(R[w]['social']))
P('■ 段ごと（direct＝参照元なし）')
for w in sorted(R): P(f"  {w[5:]}の週: " + f(R[w]['direct']))
# 最初の2週 → 最後の2週: 店の買う率の変化を「入口ごとの買う率」と「入口の割合」に分ける
ws = sorted(R); A0, A1 = ws[:2], ws[-2:]
def pool(wl):
    t = collections.defaultdict(lambda: [0, 0, 0, 0])
    for w in wl:
        for k, v in R[w].items():
            for i in range(4): t[k][i] += v[i]
    T = sum(v[0] for v in t.values()); return {k: v[0] / T for k, v in t.items()}, {k: v[3] / v[0] for k, v in t.items() if v[0]}, sum(v[3] for v in t.values()) / T
w0, c0, s0 = pool(A0); w1, c1, s1 = pool(A1)
ks = [k for k in w0 if k in w1 and k in c0 and k in c1]
within = sum(w0[k] * (c1[k] - c0[k]) for k in ks); mix = sum((w1[k] - w0[k]) * c1[k] for k in ks)
P(f"■ 店の買う率 {s0:.2%}（{A0[0][5:]}〜の2週）→ {s1:.2%}（{A1[0][5:]}〜の2週）＝ 入口ごとの買う率が変わった分 {within:+.2%}・入口の割合が変わった分 {mix:+.2%}")
P('  ' + '・'.join(f"{k}: 割合 {w0[k]:.0%} → {w1[k]:.0%}・買う率 {c0[k]:.2%} → {c1[k]:.2%}" for k in ('social', 'direct', 'search', 'その他') if k in ks))
open(D0 + 'cvr_1124.txt', 'w').write('\n'.join(out) + '\n')
# 直近の週の social の買う率は偶然の範囲か（前の7週の平均と比べる・注文数で）
import math
ws = sorted(R); prev7 = ws[:-1]; last = ws[-1]
ps = sum(R[w]['social'][3] for w in prev7) / sum(R[w]['social'][0] for w in prev7)
e = ps * R[last]['social'][0]; k = R[last]['social'][3]; zz = (k - e) / math.sqrt(e)
P(f"■ social の買う率: 前の7週 {ps:.2%} → {last[5:]}の週 {k/R[last]['social'][0]:.2%}（見込み {e:.0f}件・実際 {k}件・{zz:+.1f}σ）→ {'偶然の範囲内' if abs(zz) < 2 else '偶然では起きにくい'}")
# 買う率が 1割上がったときの利益（倍率は 粗利÷広告費 なので、同じ広告費なら粗利が1割増える）: 最後の2週 11/10〜23 の 倍率 1.45・広告費/日（why_1124.txt）
m, ad = 1.45, (173755 + 195425) / 2
P(f"■ 広告から来た人の買う率が 1割（3.1% → 3.4%）上がると: 倍率 {m:.2f} → {m*1.1:.2f}・利益 +{m*0.1*ad:,.0f}円/日（広告費 {ad:,.0f}円/日のまま。倍率と広告費は why_1124.txt の最後の2週）")
open(D0 + 'cvr_1124.txt', 'w').write('\n'.join(out) + '\n')
