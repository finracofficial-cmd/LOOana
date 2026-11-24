# -*- coding: utf-8 -*-
"""11/25 00時台「利益率30%はとりたい。そのためには？」
利益率 ＝ 利益 ÷ 売上（値引後）＝ 粗利率 ×（1 − 1/倍率）。倍率＝粗利÷広告費（決済手数料は入れていない・これまでの報告と同じ定義）。
① 店の今の位置と、30% に要る倍率 ② 7日ずつの推移（7/22〜11/24・18回）③ 商品ごと（直近7日・30日）の利益率と「30% に要る倍率」
④ 広告を絞った場合（7日の実績から、線より下の商品の広告と売上を丸ごと引く＝その商品の売上は全部広告から来ているとみなした下の見積もり）
⑤ 率も額も上がる手を積んだ場合（原価 −10%・当たりを足す）
入力: w1124.py（data/daily の売上・値引・原価・広告費）"""
import io, contextlib, os, collections
os.chdir('/home/user/LOOana'); D0 = 'scripts/daily/ic1125/margin/'
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1124.py').read(), g)
A, ALLD, agg, WIN, ACCT, CAT, MAP, MULTI = g['A'], g['ALLD'], g['agg'], g['WIN'], g['ACCT'], g['CAT'], g['MAP'], g['MULTI']
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
def W(days, key):
    WIN[key] = days; N, DC, Q, K = agg(days, key); return N, Q, K
def tot(days, key):
    N, Q, K = W(days, key); s = sum(N.values()); k = sum(K.values()); a = ACCT(days); return s, k, a
need = lambda gm, tgt=0.30: 1 / (1 - tgt / gm)
D7, D30 = ALLD[-7:], ALLD[-30:]
P('■ ① 店の今の位置（利益率＝粗利率 ×（1 − 1/倍率））')
for lab, ds in (('直近7日（11/18〜24）', D7), ('直近30日（10/26〜11/24）', D30)):
    s, k, a = tot(ds, 'm' + lab); gm = (s - k) / s; m = (s - k) / a
    P(f'  {lab}: 売上 {s/len(ds):,.0f}/日・粗利率 {gm:.1%}・広告費 {a/len(ds):,.0f}/日（売上の {a/s:.1%}）・倍率 {m:.2f}・利益 {(s-k-a)/len(ds):,.0f}/日・利益率 {(s-k-a)/s:.1%}｜30% に要る倍率 {need(gm):.2f}（＝広告費を売上の {gm-0.30:.1%} まで・売上÷広告費 {1/(gm-0.30):.2f}）')
P('■ ② 7日ずつの推移（11/24 から7日ずつさかのぼる）: 利益率・倍率・粗利率・広告費/日・利益/日')
blocks = [ALLD[i - 7:i] for i in range(len(ALLD), len(ALLD) - 7 * 18, -7)][::-1]
hit = 0
for b in blocks:
    s, k, a = tot(b, 'b' + b[0]); mg = (s - k - a) / s; hit += mg >= 0.30
    P(f"  {b[0][5:]}〜{b[-1][5:]}: 利益率 {mg:.1%}{' ★' if mg >= 0.30 else ''}・倍率 {(s-k)/a:.2f}・粗利率 {(s-k)/s:.1%}・広告費 {a/7:,.0f}/日・利益 {(s-k-a)/7:,.0f}/日")
P(f'  30% 以上だった回: {hit}/{len(blocks)}')
# ③ 商品ごと
def prod(days, key):
    N, Q, K = W(days, key); names = set(N) | {n for n in MAP if A(days, n)} | {n for n in MULTI if A(days, n)}
    R = {}
    for n in names:
        s = N.get(n, 0); k = K.get(n, 0); a = A(days, n)
        if s or a: R[n] = (s, k, a)
    return R
P('■ ③ 商品ごと（直近7日・広告費の多い順）: 売上/日・粗利率・広告費/日・倍率・利益/日・利益率｜30% に要る倍率 ｜直近30日の倍率・利益率')
R7 = prod(D7, 'p7'); R30 = prod(D30, 'p30')
for n, (s, k, a) in sorted(R7.items(), key=lambda x: -x[1][2]):
    if not a: continue
    gm = (s - k) / s if s else 0; m = (s - k) / a
    s3, k3, a3 = R30.get(n, (0, 0, 0)); m30 = f'{(s3-k3)/a3:.2f}・{(s3-k3-a3)/s3:.0%}' if a3 and s3 else '—'
    nd = f'{need(gm):.2f}' if gm > 0.30 else '—'
    P(f"  {n}: 売上 {s/7:,.0f}・粗利率 {gm:.0%}・広告費 {a/7:,.0f}・倍率 {m:.2f}・利益 {(s-k-a)/7:+,.0f}・利益率 {((s-k-a)/s if s else 0):.0%}｜要る倍率 {nd}｜30日 {m30}")
noad = [(n, v) for n, v in R7.items() if not v[2]]
P(f"  広告なしで売れた商品（7日）: 売上 {sum(v[0] for n, v in noad)/7:,.0f}/日・粗利 {sum(v[0]-v[1] for n, v in noad)/7:,.0f}/日｜カタログの広告費 {CAT(D7)/7:,.0f}/日（売上は商品に分けられない）")
# ④ 絞った場合
P('■ ④ 広告を絞った場合（直近7日の実績から、線より下の商品の広告費と売上を丸ごと引いた見積もり。カタログと広告なしの売上は残す）')
S, K, AD = sum(v[0] for v in R7.values()), sum(v[1] for v in R7.values()), ACCT(D7)
def scen(lab, cut):
    s = S - sum(R7[n][0] for n in cut); k = K - sum(R7[n][1] for n in cut); a = AD - sum(R7[n][2] for n in cut)
    P(f"  {lab}: 売上 {s/7:,.0f}/日・広告費 {a/7:,.0f}/日・利益 {(s-k-a)/7:,.0f}/日・倍率 {(s-k)/a:.2f}・利益率 {(s-k-a)/s:.1%}" + (f"｜止める {len(cut)}本: " + '・'.join(sorted(cut, key=lambda n: -R7[n][2])) if cut else ''))
mult = lambda n: (R7[n][0] - R7[n][1]) / R7[n][2]
marg = lambda n: (R7[n][0] - R7[n][1] - R7[n][2]) / R7[n][0] if R7[n][0] else -1
ads = [n for n in R7 if R7[n][2]]
scen('今のまま', [])
scen('倍率 1.0 未満を止める', [n for n in ads if mult(n) < 1.0])
scen('倍率 1.25 未満を止める', [n for n in ads if mult(n) < 1.25])
scen('倍率 1.5 未満を止める', [n for n in ads if mult(n) < 1.5])
scen('利益率 30% 未満の商品を全部止める', [n for n in ads if marg(n) < 0.30])
LIVE = ('伸縮ガラスクリーナー', 'ナノガラス脱毛パッド', 'ワイド水切りワイパー', 'W固定スマホ車載ホルダー', '快適マジックインソール', 'スマートノーズEMS美顔器', 'マグネットドアクッション', '360°マルチクリップ車載スマホホルダー', '4-in-1マルチクリーナー', 'クリアビューレインガードフィルム', '姿勢サポートチェア')   # 11/25 00:2x の直読で配信中の商品（カタログを除く）
assert all(n in R7 for n in LIVE)
scen('すでに止めた商品を除く（＝11/25 00:2x に配信中の11商品だけ）', [n for n in ads if n not in LIVE])
scen('配信中の11商品から ノーズ v2・ドアも除く', [n for n in ads if n not in LIVE or n in ('スマートノーズEMS美顔器', 'マグネットドアクッション')])
lo = [n for n in ads if mult(n) < 1.25]
P(f"  倍率 1.25 未満の10本の広告費 {sum(R7[n][2] for n in lo)/7:,.0f}/日（広告費の {sum(R7[n][2] for n in lo)/AD:.0%}）・利益の合計 {sum(R7[n][0]-R7[n][1]-R7[n][2] for n in lo)/7:+,.0f}/日")
# ⑤ 積んだ場合（1.25 未満を止めた形を土台に）
P('■ ⑤ 率も額も上がる手を積んだ場合（土台＝直近7日から 倍率 1.25 未満の商品を除いた形）')
cut = [n for n in ads if mult(n) < 1.25]
s0 = (S - sum(R7[n][0] for n in cut)) / 7; k0 = (K - sum(R7[n][1] for n in cut)) / 7; a0 = (AD - sum(R7[n][2] for n in cut)) / 7
P(f'  土台: 売上 {s0:,.0f}・利益 {s0-k0-a0:,.0f}・利益率 {(s0-k0-a0)/s0:.1%}')
top5 = ('伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', '4-in-1マルチクリーナー', 'ナノガラス脱毛パッド', 'ワイド水切りワイパー')
c5 = sum(R7[n][1] for n in top5) / 7
k1 = k0 - c5 * 0.10
P(f'  ＋主力5本の原価を 10% 下げる（5本の原価 {c5:,.0f}/日 → −{c5*0.10:,.0f}）: 利益 {s0-k1-a0:,.0f}・利益率 {(s0-k1-a0)/s0:.1%}')
# 当たり1本＝10/23〜11/5 に当たった3本（洗車ブラシ・ドア・ワイパー）の最初の14日の実績の平均
H = []
for n, st in (('伸縮ワックス洗車ブラシ', '2026-10-23'), ('マグネットドアクッション', '2026-10-31'), ('ワイド水切りワイパー', '2026-11-04')):
    ds = [d for d in ALLD if d >= st][:14]; N, Q, Kk = W(ds, 'h' + n); H.append((N.get(n, 0) / 14, Kk.get(n, 0) / 14, A(ds, n) / 14))
    P(f"    当たりの例 {n}（最初の14日）: 売上 {H[-1][0]:,.0f}/日・広告費 {H[-1][2]:,.0f}/日・倍率 {(H[-1][0]-H[-1][1])/H[-1][2]:.2f}・利益 {H[-1][0]-H[-1][1]-H[-1][2]:,.0f}/日・利益率 {(H[-1][0]-H[-1][1]-H[-1][2])/H[-1][0]:.0%}")
hs, hk, ha = (sum(x[i] for x in H) / 3 for i in range(3))
for nhit in (1, 2, 3):
    s = s0 + hs * nhit; k = k1 + hk * nhit; a = a0 + ha * nhit
    P(f'  ＋当たり {nhit}本（上の3本の平均: 売上 {hs:,.0f}・広告費 {ha:,.0f}・利益 {hs-hk-ha:,.0f}/日）: 売上 {s:,.0f}・利益 {s-k-a:,.0f}・利益率 {(s-k-a)/s:.1%}')
open(D0 + 'margin_1125.txt', 'w').write('\n'.join(out) + '\n')
# ⑥ 11/25 ユーザー「仕入れ値下げるのは無理」「予算の上げ下げは利益額最大化が前提」→ 原価の値下げなしで積み直す
P('■ ⑥ 原価の値下げなしで積んだ場合（土台＝直近7日から 倍率 1.25 未満の商品を除いた形）')
for nhit in (0, 1, 2, 3, 4, 5):
    s = s0 + hs * nhit; k = k0 + hk * nhit; a = a0 + ha * nhit
    P(f'  当たり {nhit}本: 売上 {s:,.0f}・広告費 {a:,.0f}・利益 {s-k-a:,.0f}/日・倍率 {(s-k)/a:.2f}・利益率 {(s-k-a)/s:.1%}')
P('  （当たり1本＝洗車ブラシ・ドア・ワイパーの最初の14日の平均。当たりの利益は3〜6週目に落ちるので、同時に走っている本数として読む）')
P('■ ⑦ 原価の割合（原価÷売上）と、利益率 30% に要る 売上÷広告費（＝1 ÷（1 − 原価の割合 − 0.30））')
P('  ' + '・'.join(f'原価 {c:.0%} → {1/(1-c-0.30):.2f}' for c in (0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.43)))
P('  直近30日の商品ごと（広告費の多い順）: 原価の割合・売上÷広告費・要る 売上÷広告費・利益率')
for n, (s, k, a) in sorted(R30.items(), key=lambda x: -x[1][2])[:16]:
    if not a or not s: continue
    c = k / s; nd = 1 / (1 - c - 0.30) if c < 0.70 else float('inf')
    P(f'    {n}: 原価 {c:.0%}・売上÷広告費 {s/a:.2f}（要る {nd:.2f}）・利益率 {(s-k-a)/s:.0%}')
open(D0 + 'margin_1125.txt', 'w').write('\n'.join(out) + '\n')
