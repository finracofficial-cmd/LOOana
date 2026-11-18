# -*- coding: utf-8 -*-
"""11/18(水) 09:1x 「どう？」→ 0〜8時台を過去21日（10/28〜11/17）の同じ時刻と比べる（perf_1810.py の形）。日中の数字なので予算の判定には使わない
Meta: 10/28〜11/14 はアカウント1本、11/15〜18 はキャンペーン別の単日を足す。11/16〜18 のクリックは使わない"""
import json, math, collections, statistics as st, datetime
S = json.load(open('shop_0008.json')); T = '2026-11-18'
SS = {d: (int(g) + int(dc), int(o)) for d, g, dc, o in S['sales']}
SE = {r[0]: [int(x) for x in r[1:]] for r in S['sess']}
AD = collections.defaultdict(lambda: [0, 0]); [AD[d].__setitem__(0, AD[d][0] + int(s)) or AD[d].__setitem__(1, AD[d][1] + int(c)) for d, r, s, c in S['ref_ig_fb']]
num = lambda x: 0 if x == 'null' else int(x)
MA = {}; MC = collections.defaultdict(lambda: [0] * 6)
for l in open('meta_0008.txt'):
    if l[0] == '#': continue
    p = l.strip().split(',')
    if p[0] == 'ACCT': MA[p[1]] = [num(x) for x in p[2:]]
    else: MC[(p[1], p[2])] = [num(x) for x in p[3:]]
for d in ('2026-11-15', '2026-11-16', '2026-11-17', T):
    MA[d] = [sum(v[i] for (dd, c), v in MC.items() if dd == d) for i in range(6)]
for d in ('2026-11-11', '2026-11-12', '2026-11-13', '2026-11-14'):  # キャンペーン別の合計＝アカウント（確かめ）
    assert abs(sum(v[0] for (dd, c), v in MC.items() if dd == d) - MA[d][0]) <= 10, d  # 端数で数円ずれる
P = sorted(d for d in SS if d < T); assert len(P) == 21 and P[0] == '2026-10-28'
wd = lambda d: '月火水木金土日'[datetime.date.fromisoformat(d).weekday()]
def band(lab, f, fm, days=P):
    t = f(T); xs = [f(d) for d in days]; lo = sum(x < t for x in xs)
    out = '範囲内' if min(xs) <= t <= max(xs) else ('範囲の外（下）' if t < min(xs) else '範囲の外（上）')
    print(f"  {lab}: 今日 {fm.format(t)}・過去{len(days)}日 {fm.format(min(xs))}〜{fm.format(max(xs))}（中央値 {fm.format(st.median(xs))}）・今日より低い日 {lo}/{len(days)} → {out}")
def pois_le(k, lam): return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))
print(f'■ 店全体（0〜8時台・過去21日 10/28〜11/17 の同時刻）・広告費 今日 {MA[T][0]:,}')
band('売上（値引後）', lambda d: SS[d][0], '{:,}')
band('売上÷広告費', lambda d: SS[d][0] / MA[d][0], '{:.2f}')
band('注文', lambda d: SS[d][1], '{}')
band('広告費', lambda d: MA[d][0], '{:,}')
band('来訪', lambda d: SE[d][0], '{}')
band('着地（Meta LPV）÷広告費1万円', lambda d: MA[d][3] / MA[d][0] * 10000, '{:.0f}')
band('来訪÷広告費1万円', lambda d: SE[d][0] / MA[d][0] * 10000, '{:.0f}')
band('購入率%（注文÷来訪）', lambda d: SS[d][1] / SE[d][0] * 100, '{:.2f}')
band('カート投入率%（全体）', lambda d: SE[d][1] / SE[d][0] * 100, '{:.2f}')
band('カート投入率%（instagram+facebook から）', lambda d: AD[d][1] / AD[d][0] * 100, '{:.2f}')
band('Meta カート追加÷LPV%', lambda d: MA[d][4] / MA[d][3] * 100, '{:.1f}')
band('決済完了÷決済画面%', lambda d: SE[d][3] / SE[d][2] * 100, '{:.0f}')
band('客単価', lambda d: SS[d][0] / SS[d][1], '{:,.0f}')
cvr = sum(SS[d][1] for d in P) / sum(SE[d][0] for d in P); lam = cvr * SE[T][0]
print(f"  → 注文 {SS[T][1]}（来訪{SE[T][0]}×過去21日の購入率{cvr*100:.2f}%＝期待 {lam:.1f}）・この数以下になる確率 {pois_le(SS[T][1], lam)*100:.0f}%")
cr = sum(AD[d][1] for d in P) / sum(AD[d][0] for d in P); lam2 = cr * AD[T][0]
print(f"  → 広告から来た人のカート {AD[T][1]}（来訪{AD[T][0]}×過去21日の率{cr*100:.2f}%＝期待 {lam2:.1f}）・この数以下になる確率 {pois_le(AD[T][1], lam2)*100:.0f}%")
w = [d for d in P if wd(d) == '水']; print('  水曜だけ（' + '・'.join(d[5:] for d in w) + '）:'); band('売上（水曜）', lambda d: SS[d][0], '{:,}', w); band('売上÷広告費（水曜）', lambda d: SS[d][0] / MA[d][0], '{:.2f}', w)
# 商品別
SHORT = ['ワイド水切りワイパー', 'マグネットドアクッション', 'クリアビューレインガードフィルム', '快適マジックインソール', '伸縮ワックス洗車ブラシ', '伸縮ガラスクリーナー', '4-in-1マルチクリーナー', '2WAYシートボックス', 'ナノガラス脱毛パッド', 'W固定スマホ車載ホルダー', '防風あったか裏起毛パンツ', '3WAY着る電気ブランケット', '携帯電動シェーバー', 'スマートノーズEMS美顔器', '360°マルチクリップ車載スマホホルダー', 'コードレスダブルミスト加湿器', '壁掛けディスペンサー', '3D足臭リセットブラシ', '裏起毛タッチ防寒グローブ']
PO = collections.defaultdict(int); PS = collections.defaultdict(int)
for d, t, g, dc, o in json.load(open('prod_0008.json'))['rows']:
    n = next((s for s in SHORT if s in t), None)
    if n: PO[(d, n)] += int(o); PS[(d, n)] += int(g) + int(dc)
ALIAS = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '快適マジックインソール v3': '快適マジックインソール', '快適マジックインソールv2': '快適マジックインソール', '高見えレザーヘッドレストフックv2': '高見えレザーヘッドレストフック'}
AT = collections.defaultdict(int)
for (d, c), v in MC.items():
    if d == T and v[0] > 0: AT[ALIAS.get(c, c)] += v[0]
PB = ['2026-11-11', '2026-11-12', '2026-11-13', '2026-11-14', '2026-11-15', '2026-11-16', '2026-11-17']
print(f"■ 商品別（0〜8時台・今日広告費が出た全キャンペーン。期待＝11/11〜17 の同時刻の 注文÷広告費 × 今日の広告費）・広告費の合計 {sum(AT.values()):,}")
for n in sorted(AT, key=lambda n: -AT[n]):
    a = AT[n]; o = PO.get((T, n), 0); ln = f"  {n}: {o}注文・売上 {PS.get((T, n), 0):,}・広告費 {a:,}"
    if n.startswith('カタログ'): print(ln + '（商品に分けられない）'); continue
    a6 = sum(v[0] for (d, c), v in MC.items() if d in PB and ALIAS.get(c, c) == n); o6 = sum(PO.get((d, n), 0) for d in PB)
    if not a6 or not o6: print(ln + f'（比べる過去なし・過去7日の同時刻 広告費 {a6:,}・注文 {o6}）'); continue
    lam = o6 / a6 * a; p = 1 - pois_le(o - 1, lam) if o >= lam else pois_le(o, lam)
    print(ln + f"・期待 {lam:.1f}・{'多い' if o >= lam else '少ない'}側 {p*100:.0f}%")
others = [(n, o) for (d, n), o in PO.items() if d == T and n not in AT]
print('  広告なしの商品の注文: ' + '・'.join(f'{n} {o}' for n, o in others))
