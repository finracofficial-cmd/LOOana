# -*- coding: utf-8 -*-
"""11/26 定例の深掘り（11/25 の実績）。
① 11/25 の利益を、7日平均との差（倍率の分・量の分）と、出したばかりの3本（チェア v2・ブランケット v2・シートボックス v2）を除いた形に分ける
② 消化（広告費 ÷ その日の最終日予算の合計）を日ごとに並べる（11/25 は配信が少なかった）
③ 同じキャンペーンの中での CPM・クリック率・クリック1回の値段: 11/25 ↔ そのキャンペーンの前7日（11/18〜24）
④ 出したばかりの商品の数字（Meta・11/25）と、クリック1回の粗利から出した線
⑤ 入口別（social／direct）の来訪と買う率: 11/25 ↔ 11/18〜24
入力: w1125.py（CSV）・budget-snapshots.csv・ad_level_1026_1125.txt・meta_ad_1124_raw.json・meta_ad_1125_raw.json・sess_source_1125_raw.json・../o11xx/sess_source_*_raw.json"""
import io, contextlib, json, os, csv, math, collections, datetime, statistics as st, glob
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D0 + '../../..')
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1125.py').read(), g)
A, ALLD, agg, WIN, ACCT, MULTI, CAT = g['A'], g['ALLD'], g['agg'], g['WIN'], g['ACCT'], g['MULTI'], g['CAT']
out = []
def P(s=''): print(s); out.append(s)
T = '2026-11-25'
def tot(days):
    k = 'x' + days[0] + days[-1]; WIN[k] = days; N, DC, Q, K = agg(days, k); return sum(N.values()), sum(K.values()), ACCT(days), N, K
# ---- ① ----
s, k, a, N, K = tot([T]); p = s - k - a; D7p = ALLD[-8:-1]; s7, k7, a7, _, _ = tot(D7p); m7 = (s7 - k7) / a7; m = (s - k) / a
P(f"■ ① 11/25 の利益 {p:,.0f}（倍率 {m:.2f}・広告費 {a:,.0f}）↔ 前の7日（11/18〜24）の平均 {(s7-k7-a7)/7:,.0f}/日（倍率 {m7:.2f}・広告費 {a7/7:,.0f}/日）")
P(f"  差 {p-(s7-k7-a7)/7:+,.0f} ＝ 倍率の分 {(m-m7)*a:+,.0f} ＋ 量の分 {(m7-1)*(a-a7/7):+,.0f}")
NEW = ('姿勢サポートチェア', '3WAY着る電気ブランケット', '2WAYシートボックス')
an = sum(A([T], n) for n in NEW); sn = sum(N.get(n, 0) - K.get(n, 0) for n in NEW)
P(f"  出したばかりの3本（チェア v2 2日目・ブランケット v2／シートボックス v2 初日）: 広告費 {an:,.0f}・粗利 {sn:,.0f}（注文0）→ 除くと 利益 {p-(sn-an):,.0f}・倍率 {((s-k)-sn)/(a-an):.2f}・広告費 {a-an:,.0f}")
nn = 'ナノガラス脱毛パッド'; P(f"  ナノ: 粗利 {N.get(nn,0)-K.get(nn,0):,.0f}・広告費 {A([T],nn):,.0f}・利益 {N.get(nn,0)-K.get(nn,0)-A([T],nn):+,.0f}｜さらにナノも除くと 倍率 {((s-k)-sn-(N.get(nn,0)-K.get(nn,0)))/(a-an-A([T],nn)):.2f}")
# ---- ② 消化 ----
SN = collections.defaultdict(dict)
for r in csv.DictReader(open('data/budget-snapshots.csv')): SN[r['snapshot_date']][(r['campaign'], r['adset'])] = int(r['daily_budget'])
nxt = lambda d: (datetime.date.fromisoformat(d) + datetime.timedelta(1)).isoformat()
P('■ ② 消化（その日の広告費 ÷ 翌日 00時台の記録の日予算の合計。途中で出した・止めた商品がある日はずれる）')
line = []
for d in ALLD[-14:]:
    b = sum(SN[nxt(d)].values()) if nxt(d) in SN else 0; line.append(f"{d[5:]}（{g['wd'](d)}）{ACCT([d])/b:.0%}" if b else f"{d[5:]} —")
P('  ' + '・'.join(line))
b25 = sum(SN['2026-11-26'].values()); nb = sum(v for (c, a_), v in SN['2026-11-26'].items() if c in ('3WAY着る電気ブランケットv2', '2WAYシートボックスv2')); na = A([T], '3WAY着る電気ブランケット') + A([T], '2WAYシートボックス')
P(f"  11/25: {a:,.0f} ÷ {b25:,} ＝ {a/b25:.1%}（広告費は暫定）｜15時台に出した2本（予算 {nb:,}・広告費 {na:,.0f}）を除くと {(a-na)/(b25-nb):.1%}")
# ---- ③ 同じキャンペーンの中 ----
R = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))
for l in open(D0 + 'ad_level_1026_1125.txt'):
    if l[0] == '#': continue
    d, c, a_, ad, cost, imp, clk = l.strip().split(','); x = R[c][d]; x[0] += int(cost); x[1] += int(imp); x[2] += int(clk)
P('■ ③ 同じキャンペーンの中: 前7日（11/18〜24）→ 11/25 の CPM｜クリック率｜クリック1回の値段')
tt = [0, 0, 0]; tp = [0, 0, 0]
for c in sorted(R, key=lambda c: -R[c].get(T, [0])[0]):
    t = R[c].get(T, [0, 0, 0]); pv = [v for d, v in R[c].items() if '2026-11-18' <= d <= '2026-11-24']; pc, pi, pk = (sum(v[i] for v in pv) for i in range(3))
    if t[0] < 1000: continue
    if pi < 5000: P(f"  {c}: （前7日の配信が少ない）→ CPM {t[0]/t[1]*1000:,.0f}・クリック率 {t[2]/t[1]:.2%}・クリック1回 {t[0]/max(1,t[2]):.0f}円"); continue
    for i in range(3): tt[i] += t[i]
    # 前7日は「11/25 の表示の割合」で重みをつけて合計する（顔ぶれの違いを除く）
    tp[0] += pc / pi * t[1]; tp[2] += pk / pi * t[1]; tp[1] += t[1]
    P(f"  {c}: CPM {pc/pi*1000:,.0f} → {t[0]/t[1]*1000:,.0f}（{(t[0]/t[1])/(pc/pi)-1:+.0%}）｜{pk/pi:.2%} → {t[2]/t[1]:.2%}｜{pc/pk:.0f} → {t[0]/max(1,t[2]):.0f}円（{(t[0]/max(1,t[2]))/(pc/pk)-1:+.0%}）")
P(f"  上の合計（11/25 の表示の割合でそろえた）: CPM {tp[0]/tp[1]*1000:,.0f} → {tt[0]/tt[1]*1000:,.0f}（{(tt[0]/tt[1])/(tp[0]/tp[1])-1:+.0%}）｜クリック率 {tp[2]/tp[1]:.2%} → {tt[2]/tt[1]:.2%}｜クリック1回 {tp[0]/tp[2]:.0f} → {tt[0]/tt[2]:.0f}円（{(tt[0]/tt[2])/(tp[0]/tp[2])-1:+.0%}）")
# ---- ④ 出したばかりの商品 ----
z = lambda x: 0 if x in ('null', '') else int(x)
def rows(f): return [l.strip().split(',') for l in json.load(open(D0 + f))['data']['data'].split('\n')[1:] if l.strip()]
M = rows('meta_ad_1124_raw.json') + rows('meta_ad_1125_raw.json')
P('■ ④ 出したばかりの商品（Meta・広告セット合計）。線＝クリック1回の粗利 ÷ 1.25（倍率 1.25 に届くクリック1回の値段）')
for c, lab, since, gpc, ref in (('姿勢サポートチェアv2', 'チェア v2（11/24 21時台〜・C1）', '2026-11-24', 112, '旧: クリック1回 72円（最初の4日 96円）'),
                               ('3WAY着る電気ブランケットv2', 'ブランケット v2（11/25 15:28〜・D・ボタン「詳しくはこちら」）', '2026-11-25', 139, 'v1: クリック率 5.45%・クリック1回 110円・来訪÷クリック 0.90・カート÷クリック 13.4%・購入÷クリック 2.78%'),
                               ('2WAYシートボックスv2', 'シートボックス v2（11/25 15:35〜・C1）', '2026-11-25', 163, '旧（8/6〜27）: クリック率 3.07%・クリック1回 95円・注文÷クリック 4.34%'),
                               ('クリアビューレインガードフィルムv2', 'レインガード v2（11/23 16時台〜・C1・3日目）', '2026-11-25', None, '')):
    rs = [r for r in M if r[1] == c and r[0] >= since]; cost, imp, clk, lpv, atc, pu = (sum(z(r[i]) for r in rs) for i in (4, 5, 6, 7, 8, 9))
    line = f"  {lab}: 広告費 {cost:,}・表示 {imp:,}・クリック {clk}（クリック率 {clk/imp:.2%}）・クリック1回 {cost/clk:.0f}円・来訪÷クリック {lpv/clk:.2f}・カート {atc}（÷クリック {atc/clk:.1%}）・購入 {pu}（Meta）"
    if gpc: line += f"｜線 {gpc/1.25:.0f}円（粗利 {gpc}円/クリック）・事故停止の線まで 残り {dict(姿=12507, **{'3': 11484, '2': 10299})[c[0]] - cost:,}円｜{ref}"
    P(line)
old = {'姿勢サポートチェアv2': 0.021}   # チェアの旧キャンペーンの 注文÷クリック（ic1125/h16/relaunch_h16.txt の見込み 0.9件÷42クリック）
rs = [r for r in M if r[1] == '姿勢サポートチェアv2']; clk = sum(z(r[6]) for r in rs); e = clk * old['姿勢サポートチェアv2']
P(f"  チェア v2 の注文の見込み（旧の 注文÷クリック 約2.1% × {clk}クリック）{e:.1f}件 → 実際 0件・0件になる確率 {math.exp(-e):.0%}")
# ---- ⑤ 入口別 ----
src = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D0 + 'sess_source_1125_raw.json'))['rows']}
prev = collections.defaultdict(lambda: [0, 0, 0, 0]); nday = 0
for d in ('1118', '1119', '1120', '1121', '1122', '1123', '1124'):
    f = glob.glob(f'scripts/daily/o{d}/sess_source_{d}_raw.json')
    if not f: continue
    nday += 1
    for r in json.load(open(f[0]))['rows']:
        for i in range(4): prev[r[0]][i] += int(r[1 + i])
P(f'■ ⑤ 入口別（11/25 ↔ 11/18〜24 のうち記録のある {nday}日の平均）')
for k_ in ('social', 'direct'):
    t = src[k_]; pv = prev[k_]
    P(f"  {k_}: 来訪 {t[0]:,}（平均 {pv[0]/nday:,.0f}）・カート率 {t[1]/t[0]:.2%}（{pv[1]/pv[0]:.2%}）・買う率 {t[3]/t[0]:.2%}（{pv[3]/pv[0]:.2%}）")
ts = sum(v[0] for v in src.values()); P(f"  direct の割合: 11/25 {src['direct'][0]/ts:.0%}｜{nday}日の平均 {prev['direct'][0]/sum(v[0] for v in prev.values()):.0%}｜Meta のリンククリック（11/25）{sum(z(r[6]) for r in M if r[0]==T):,} → social の来訪 ÷ クリック {src['social'][0]/sum(z(r[6]) for r in M if r[0]==T):.2f}")
open(D0 + 'deep_1126.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
