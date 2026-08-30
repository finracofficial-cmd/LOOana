# -*- coding: utf-8 -*-
"""2026-08-30 ユーザーによる予算見直しのチェック。
   予算（変更後）= Meta 直読（campaign_and_resource_get / campaign_detail_level="ad_groups"）の実測。
   予算（変更前）= data/budget-snapshots.csv（同日の最後のスナップショットを採る）。
   採算 = w0829.py 経由の CSV 実測（8/29終端）。★リテラルは Meta 直読値の転記のみ。"""
import runpy, collections, csv
g = runpy.run_path('scripts/daily/w0829.py')
S, AD, MAP, STORE = g['S'], g['AD'], g['MAP'], g['STORE']
N3, N7, K3, K7, Q3, Q7 = g['N3'], g['N7'], g['K3'], g['K7'], g['Q3'], g['Q7']
D3, D7, A = g['D3'], g['D7'], g['A']
INV = {v: k for k, v in MAP.items()}

# --- Meta直読（2026-08-30 変更後・ENABLEDの広告セットのみ合計）---
NOW = {'ナノガラス脱毛パッド':80000,'W固定スマホ車載ホルダー':35000,'快適マジックインソール':30000,
 'ムダ毛シェーバー':17000,'カタログ全部（テスト）':18000,'2WAYシートボックス':11000,
 '姿勢サポートチェア':12000,'むくみ取りかっさ':13000,'バランスケアスリッパ':12000,
 '完全遮光・接触冷感UVハット':6000,'ナノバブルシャワーヘッド':8000,'偏光・調光サングラス':5000,
 'ビジュアル耳かき':8000}

# --- スナップショット: 同日に複数回取った日(末尾 b/c/d)は「最後の1本」を採る（合算しない）---
_BS = collections.defaultdict(dict)
for r in csv.reader(open('data/budget-snapshots.csv')):
    if not r or r[0] == 'snapshot_date': continue
    d = r[0][:10]
    day = _BS[r[1]].setdefault(d, {}); day[r[0]] = day.get(r[0], 0) + int(r[3])
BUD = collections.defaultdict(dict)
for cp, byday in _BS.items():
    for d, sn in byday.items(): BUD[cp][d] = sn[max(sn)]
PREV = {cp: BUD[cp].get('2026-08-30', 0) for cp in set(NOW) | set(BUD)}

print('■ ① 予算の差分（8/30朝スナップショット → 現在。どちらもMeta直読の実測）')
print(f'  {"キャンペーン":<26}{"変更前":>9}{"変更後":>9}{"差":>9}{"変化率":>9}')
CH, tp, tn = [], 0, 0
for cp in sorted(NOW, key=lambda c: -NOW[c]):
    p, n = PREV.get(cp, 0), NOW[cp]; tp += p; tn += n
    if p != n: CH.append(cp)
    print(f'  {cp:<26}{p:>9,}{n:>9,}{n-p:>+9,}{(n/p-1 if p else 0):>9.1%}' + ('  ←変更' if p != n else ''))
print(f'  {"合計":<26}{tp:>9,}{tn:>9,}{tn-tp:>+9,}{tn/tp-1:>9.1%}   変更 {len(CH)}件')

def eco(n, N, K, Qd, days):
    s = N.get(n, 0)
    if not s: return None
    k = K.get(n, 0); a = A(days, n); q = Qd.get(n, 0); gm = 1 - k/s
    return dict(s=s, k=k, a=a, q=q, mer=(s/a if a else None), be=1/gm,
                tg=(1/(gm-0.35) if gm-0.35 > 0 else None),
                becpa=((s-k)/q if q else None), cpa=(a/q if q and a else None), p=s-k-a)

def wu(cp, days):
    """消化率 = 実消化 ÷ Σ(その日の日予算)。予算が動いた週でも正しく出る。
       スナップショットが無い日（キャンペーン開始前など）は分子・分母の両方から外し、日数を返す"""
    dd = [d for d in days if d in BUD[cp] and BUD[cp][d]]
    b = sum(BUD[cp][d] for d in dd)
    if not b: return None, 0
    return sum(AD[cp].get(d, 0) for d in dd) / b, len(dd)

print('\n■ ② 変更されたキャンペーンの採算（8/29終端・CSV実測）')
print(f'  {"商品":<22}{"予算":>17}{"7日MER":>8}{"分岐":>6}{"目標":>6}{"余裕":>7}'
      f'{"3日MER":>8}{"3日余裕":>8}{"倍率7d":>8}{"倍率3d":>8}{"週消化率":>9}')
for cp in CH:
    n = INV.get(cp, cp)
    b7 = eco(n, N7, K7, Q7, D7); b3 = eco(n, N3, K3, Q3, D3)
    w, nd = wu(cp, D7)
    f = lambda v, s='{:.2f}': (s.format(v) if v is not None else '—')
    r7 = b7['becpa']/b7['cpa'] if b7 and b7['becpa'] and b7['cpa'] else None
    r3 = b3['becpa']/b3['cpa'] if b3 and b3['becpa'] and b3['cpa'] else None
    print(f'  {n:<22}{PREV[cp]:>8,}→{NOW[cp]:>8,}{f(b7["mer"]):>8}{f(b7["be"]):>6}{f(b7["tg"]):>6}'
          f'{f(b7["mer"]-b7["be"],"{:+.2f}"):>7}{f(b3["mer"] if b3 else None):>8}'
          f'{f((b3["mer"]-b3["be"]) if b3 and b3["mer"] else None,"{:+.2f}"):>8}'
          f'{f(r7):>8}{f(r3):>8}{f(w,"{:.0%}"):>9}{("(" + str(nd) + "日)") if nd != 7 else "":>7}')

print('\n■ ③ 増額の妥当性（限界MER = 平均MER×0.7 で評価。1円あたり利益 = 限界MER×粗利率 − 1）')
print(f'  {"商品":<22}{"増減/日":>9}{"限界MER":>9}{"粗利率":>8}{"1円あたり利益":>13}{"×0.6端":>9}{"×0.8端":>9}{"週の増減":>10}  頑健性')
for cp in CH:
    n = INV.get(cp, cp); b7 = eco(n, N7, K7, Q7, D7)
    if not b7 or not b7['mer']: continue
    gm = 1 - b7['k']/b7['s']; d = NOW[cp] - PREV[cp]
    ends = [b7['mer']*x*gm - 1 for x in (0.6, 0.7, 0.8)]
    rob = '一致' if (all(e > 0 for e in ends) or all(e < 0 for e in ends)) else '⚠️符号が割れる'
    print(f'  {n:<22}{d:>+9,}{b7["mer"]*0.7:>9.2f}{gm:>8.1%}{ends[1]:>+13.3f}'
          f'{ends[0]:>+9.3f}{ends[2]:>+9.3f}{ends[1]*d*7:>+10,.0f}  {rob}')

print('\n■ ④ 全体への影響')
tot7 = sum(A(D7, n) for n in N7) + sum(AD[c].get(d, 0) for c in ('カタログ全部（テスト）','カタログ全部（テスト） 夏以外') for d in D7)
net7 = sum(N7.values()); cost7 = sum(K7.values())
print(f'  7日(8/23-29) 実売 {net7:,} / 原価 {cost7:,.0f} / 広告 {tot7:,.0f} → MER {net7/tot7:.2f} / '
      f'分岐 {1/(1-cost7/net7):.2f} / 利益 {net7-cost7-tot7:+,.0f}')
print(f'  日予算 {tp:,} → {tn:,}（{tn-tp:+,}円/日・{tn/tp-1:+.1%}）= 週 {(tn-tp)*7:+,}円')
print(f'  全店の粗利率 {1-cost7/net7:.1%} なので、増やした分が全店平均の限界MER({net7/tot7*0.7:.2f})で回れば '
      f'週 {((net7/tot7*0.7)*(1-cost7/net7)-1)*(tn-tp)*7:+,.0f}円')
