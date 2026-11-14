# -*- coding: utf-8 -*-
"""11/14 19:3x 夕方（16〜18時台）が 11/11 から続けて弱く見える。偶然か・他の時間帯にずれたかを見る。
入力: sess_hourly_1015_1113.json（日×時間帯の来訪・カート）＋ sess_hour_1114_1925.json（今日）＋ sales_hour_1024_1114.json（日×時間帯の注文）"""
import json, math, collections, datetime
D = 'scripts/daily/ic1114/'
S = collections.defaultdict(lambda: [0, 0, 0, 0])
for d, h, *v in json.load(open(D + 'sess_hourly_1015_1113.json'))['rows']: S[d, int(h)] = [int(x) for x in v]
for h, *v in json.load(open(D + 'sess_hour_1114_1925.json'))['rows']: S['2026-11-14', int(h)] = [int(x) for x in v]
O = collections.defaultdict(int)
for d, h, o, g in json.load(open(D + 'sales_hour_1024_1114.json'))['rows']: O[d, int(h)] = int(o)
days = [(datetime.date(2026, 10, 24) + datetime.timedelta(i)).isoformat() for i in range(22)]
HOL = {'2026-11-03'}
B = [('0〜8', range(0, 9)), ('9〜15', range(9, 16)), ('16〜18', range(16, 19)), ('19〜23', range(19, 24))]
def pois_le(k, lam): return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))
base = [d for d in days[:-4] if d not in HOL]          # 10/24〜11/10（祝日除く）を「ふだん」にする
print(f'■ 時間帯ブロック別の購入率（注文÷来訪）。ふだん＝10/24〜11/10（祝日11/3除く{len(base)}日）')
rate = {}
for name, hs in B:
    n = sum(S[d, h][0] for d in base for h in hs); o = sum(O[d, h] for d in base for h in hs); rate[name] = o / n
    ct = sum(S[d, h][1] for d in base for h in hs) / n
    print(f'  ふだん {name}時台: 購入率 {o/n:.2%}・カート投入率 {ct:.2%}')
print('\n■ 11/11〜11/14 の各ブロック（注文 実際／期待＝来訪×ふだんの購入率・カート投入率）')
for d in days[-4:]:
    parts = []
    for name, hs in B:
        if d == '2026-11-14' and name == '19〜23': continue
        n = sum(S[d, h][0] for h in hs); o = sum(O[d, h] for h in hs); c = sum(S[d, h][1] for h in hs)
        parts.append(f'{name}時台 {o}/{n*rate[name]:.1f}（カート {c/n:.1%}）')
    print(f'  {d}: ' + '・'.join(parts))
print('\n■ 4日まとめ（11/11〜11/14）')
for name, hs in B:
    dd = days[-4:] if name != '19〜23' else days[-4:-1]
    n = sum(S[d, h][0] for d in dd for h in hs); o = sum(O[d, h] for d in dd for h in hs); c = sum(S[d, h][1] for d in dd for h in hs)
    lam = n * rate[name]
    nb = sum(S[d, h][0] for d in base for h in hs); cb = sum(S[d, h][1] for d in base for h in hs)
    print(f'  {name}時台（{len(dd)}日）: 注文 {o}・期待 {lam:.1f}（{o/lam-1:+.0%}）・この数以下になる確率 {pois_le(o, lam):.2%}・カート投入率 {c/n:.2%}（ふだん {cb/nb:.2%}）')
# 同じ「4日続けて期待の◯割以下」がふだんの期間にどれくらいあったか（夕方）
ev = {d: (sum(O[d, h] for h in (16, 17, 18)), sum(S[d, h][0] for h in (16, 17, 18)) * rate['16〜18']) for d in days}
print('\n■ 夕方（16〜18時台）の日別 注文／期待: ' + '・'.join(f'{d[5:]} {ev[d][0]}/{ev[d][1]:.1f}' for d in days))
runs = [days[i:i+4] for i in range(len(days) - 7) if all(ev[x][0] < ev[x][1] for x in days[i:i+4])]
print(f'  ふだんの期間で「4日続けて期待を下回った」並び: {len(runs)}回（{", ".join(r[0][5:] + "〜" + r[-1][5:] for r in runs) or "なし"}）')

# ---- 商品（入口ページ）別: 夕方 16〜18時台 11/11〜14 ／ 夕方 10/28〜11/10 ／ 夕方以外 11/11〜13 ----
NAME = {'nano-fine-fiber': 'クリーナー', 'vacuum-adsorption': 'W固定', 'washable-reusable-fuzz': 'ナノ', 'soft-silicone-car-squeegee': 'ワイパー',
        'portable-small-wireless-mini-dust': '4-in-1', 'car-wash-cotton-thread': 'ブラシ', 'soft-super-sports-shock': 'インソール', 'silicone-magnetic-door': 'ドア',
        'winter-sweatwear': 'パンツ', 'waterproof-film-for-car': 'レインガード', 'small-portable-mini-sealing': 'ヒートシーラー', 'student-children-cushion': 'チェア',
        'outdoor-warming-heated-blanket': 'ブランケット', 'high-end-nose-massager': 'ノーズEMS', 'reciprocating-shaver': 'シェーバー', 'seat-hook-chair-back': 'ヘッドレストフック',
        'smart-toothbrush-sterilizer': 'UV歯ブラシ', 'slippers-womens-summer': 'スリッパ'}
def name(p):
    if p == '/': return 'トップ'
    for k, v in NAME.items():
        if k in p: return v
    return 'その他'
def lp(f):
    agg = collections.defaultdict(lambda: [0, 0, 0])
    for p, s, a, c in json.load(open(D + f))['rows']:
        x = agg[name(p)]; x[0] += int(s); x[1] += int(a); x[2] += int(c)
    return agg
LB, LA, LN = lp('lp_1618_1111_1114.json'), lp('lp_1618_1028_1110.json'), lp('lp_not1618_1111_1113.json')
print('\n■ 入口ページ別（来訪・カート投入率・決済完了）: 夕方 11/11〜14 ／ 夕方 10/28〜11/10 ／ 夕方以外 11/11〜13')
short = 0; tot_exp = 0
for k in sorted(LB, key=lambda k: -LB[k][0]):
    b, a, n = LB[k], LA.get(k, [0, 0, 0]), LN.get(k, [0, 0, 0])
    if b[0] < 20: continue
    ref = a if a[0] >= 100 else n                     # 夕方の過去が少ないページは同じ日の夕方以外の率を使う
    exp = b[0] * ref[2] / ref[0] if ref[0] else 0; tot_exp += exp
    f = lambda x: f'{x[0]}人・カート {x[1]/x[0]:.1%}・完了 {x[2]}' if x[0] else '—'
    print(f'  {k}: {f(b)}（期待 {exp:.1f}） ／ {f(a)} ／ {f(n)}')
print(f'  夕方 11/11〜14 の決済完了 合計 {sum(v[2] for v in LB.values())}・各ページの率からの期待 約{tot_exp:.0f}（来訪20未満のページを除く）')

# ---- Meta 広告別（W固定・クリーナー）: クリック→カート ----
def ma(f):
    r = collections.defaultdict(lambda: [0, 0, 0])
    for l in open(D + f):
        if l[0] == '#': continue
        d, c, ad, cost, imp, clk, atc, pur = l.strip().split(',')
        per = 'B' if d >= '2026-11-11' else 'A'
        x = r['W固定' if c.startswith('W固定') else c[:4], ad, per]; x[0] += int(clk) if clk != 'null' else 0; x[1] += int(atc) if atc != 'null' else 0; x[2] += int(pur) if pur != 'null' else 0
    return r
EV, AL = ma('meta_ad_1618_wc.txt'), ma('meta_ad_0018_wc.txt')
print('\n■ Meta 広告別のカート÷クリック（16〜18時台 ／ 0〜15時台）。A期間＝11/4〜10・B期間＝11/11〜14')
for c in ('W固定', '伸縮ガラ'):
    for ad in ('A', 'B'):
        for per in ('A', 'B'):
            e = EV.get((c, ad, per)); a = AL.get((c, ad, per))
            if not e or not a or e[0] == 0: continue
            o = [a[i] - e[i] for i in range(3)]
            print(f'  {c} 広告{ad}・{per}期間: 夕方 クリック {e[0]}・カート {e[1]}（{e[1]/e[0]:.1%}）・購入 {e[2]} ／ 0〜15時台 クリック {o[0]}・カート {o[1]}（{o[1]/o[0]:.1%}）・購入 {o[2]}')

# ---- 夕方に来た人が夜（19〜23時台）に買っているか ----
from datetime import datetime as _dt, timedelta as _td, timezone as _tz
JST = _tz(_td(hours=9))
def back(f):
    od = json.load(open(D + f))['orders']; k = 0
    for o in od:
        c = _dt.fromisoformat(o['createdAt'].replace('Z', '+00:00')).astimezone(JST)
        if any((lambda t: t.date() == c.date() and 16 <= t.hour <= 18)(_dt.fromisoformat(m['occurredAt'].replace('Z', '+00:00')).astimezone(JST))
               for m in o['customerJourneySummary']['moments']['nodes']): k += 1
    return k, len(od)
k1, n1 = back('journey_1923_1111_1113.json'); k0, n0 = back('journey_1923_1104_1106.json')
print(f'\n■ 19〜23時台の注文のうち、同じ日の16〜18時台にも来ていた人: 11/11〜13 {k1}/{n1} ／ 11/4〜6 {k0}/{n0}')
