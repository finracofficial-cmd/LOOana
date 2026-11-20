# -*- coding: utf-8 -*-
"""11/20 17時台 「いまのところ異常とかある？大丈夫？」: 0〜16時台を過去21日（10/30〜11/19）の同じ時刻と比べる／朝と午後に分ける／広告セットの配信／商品別。
日中の数字なので、予算の判定・提案には使わない。入力は raw.txt・../h11/raw.txt（0〜10時台の日別と時間別の率）・data/budget-snapshots.csv"""
import collections, csv, math, re, statistics as st, os
D0 = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D0, '..', '..', '..', '..'))
def load(path):
    R = collections.defaultdict(list)
    for l in open(path):
        if l[0] != '#': p = l.strip().split(','); R[p[0]].append(p[1:])
    return R
R = load(os.path.join(D0, 'raw.txt')); R10 = load(os.path.join(D0, '..', 'h11', 'raw.txt'))
day = lambda rows: {r[0]: [int(x) for x in r[1:]] for r in rows}
S, V, M = day(R['S']), day(R['V']), day(R['M']); S10, V10, M10 = day(R10['S']), day(R10['V']), day(R10['M'])
MH = {int(r[0]): [int(x) for x in r[1:]] for r in R['MH']}; T = {int(r[0]): [int(x) for x in r[1:]] for r in R['T']}; TV = {int(r[0]): [int(x) for x in r[1:]] for r in R['TV']}
H = {int(r[0]): [int(x) for x in r[1:]] for r in R10['H']}
TD = '2026-11-20'; CUT = range(0, 17); AM = range(0, 11); PM = range(11, 17)
tv = lambda h: TV.get(h, [0, 0, 0])
M[TD] = [sum(MH[h][i] for h in CUT) for i in (0, 1, 3, 4, 5)]
# 今日の 0〜10時台は、いまの時間別から作り直す（朝の取得より後に確定した分を含む）
S10[TD] = [sum(T[h][i] for h in AM) for i in range(4)]; V10[TD] = [sum(tv(h)[i] for h in AM) for i in range(3)]; M10[TD] = [sum(MH[h][i] for h in AM) for i in (0, 1, 3, 4, 5)]
assert sum(T[h][0] for h in CUT) == S[TD][0] and sum(T[h][3] for h in CUT) == S[TD][3] and sum(tv(h)[0] for h in CUT) == V[TD][0] and sum(tv(h)[1] for h in CUT) == V[TD][1]
A = [(r[0], r[1], *[int(x) for x in r[2:]]) for r in R['A']]; assert sum(a[2] for a in A) == M[TD][0] and sum(a[3] for a in A) == M[TD][1]
P_ = {r[0]: [int(x) for x in r[1:]] for r in R['P']}; P7 = {r[0]: [int(x) for x in r[1:]] for r in R['P7']}
assert sum(v[1] for v in P_.values()) == V[TD][1] and sum(v[2] for v in P_.values()) == V[TD][2]
past = [d for d in sorted(S) if d < TD]; assert len(past) == 21
assert sum(v[1] for v in P7.values()) == sum(V[d][1] for d in past[-7:]) and sum(v[2] for v in P7.values()) == sum(V[d][2] for d in past[-7:])
def ple(k, l): return sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
def pge(k, l): return 1 - ple(k - 1, l) if k > 0 else 1.0
def met(s, v, m):
    ss, c, k, dn = s; o, g, dc = v; ad, imp = m[0], m[1]
    return collections.OrderedDict([('注文', o), ('売上（値引後）', g - dc), ('広告費', ad), ('売上÷広告費', (g - dc) / ad), ('注文÷広告費1万円', o / ad * 1e4), ('CPM', ad / imp * 1000),
        ('来訪÷広告費1万円', ss / ad * 1e4), ('カート率%', c / ss * 100), ('完了÷決済画面%', dn / k * 100), ('買う率%（購入÷来訪）', dn / ss * 100), ('1注文の売上', (g - dc) / o)])
sub = lambda a, b: [x - y for x, y in zip(a, b)]
blocks = {'0〜16時台': lambda d: met(S[d], V[d], M[d]), '0〜10時台': lambda d: met(S10[d], V10[d], M10[d]), '11〜16時台': lambda d: met(sub(S[d], S10[d]), sub(V[d], V10[d]), sub(M[d], M10[d]))}
out = []
for bl, f in blocks.items():
    out.append(f'■ {bl}: 今日（11/20 金）と 過去21日（10/30〜11/19）の同じ時刻')
    for k, v in f(TD).items():
        xs = [f(d)[k] for d in past]; lo = sum(x < v for x in xs)
        w = '範囲の外（下）' if v < min(xs) else ('範囲の外（上）' if v > max(xs) else '範囲内')
        out.append(f'  {k}: 今日 {v:,.2f}・過去 {min(xs):,.2f}〜{max(xs):,.2f}（中央値 {st.median(xs):,.2f}・差 {v/st.median(xs)-1:+.0%}）・今日より低い日 {lo}/21 → {w}')
for lab, hs in (('0〜16時台', CUT), ('0〜10時台', AM), ('11〜16時台', PM)):
    s = sum(T[h][0] for h in hs); c = sum(T[h][1] for h in hs); dn = sum(T[h][3] for h in hs); e = sum(T[h][0] * H[h][3] / H[h][0] for h in hs); ec = sum(T[h][0] * H[h][1] / H[h][0] for h in hs)
    pr = f'{dn}件以上 {pge(dn, e):.1%}' if dn >= e else f'{dn}件以下 {ple(dn, e):.1%}'; prc = f'{c}件以上 {pge(c, ec):.1%}' if c >= ec else f'{c}件以下 {ple(c, ec):.1%}'
    out.append(f'  偶然かどうか（{lab}・見込み＝今日の来訪×過去21日のその時刻の率）: 来訪 {s}・カート追加 {c}（見込み {ec:.1f}・{prc}）・購入 {dn}（見込み {e:.1f}・{pr}）')
out.append('■ 同じ 11〜16時台の直近: 注文・広告費・売上÷広告費・買う率')
f = blocks['11〜16時台']
for d in past[-7:] + [TD]:
    x = f(d); out.append(f"  {d[5:]}: {x['注文']}件・{x['広告費']:,}・{x['売上÷広告費']:.2f}・{x['買う率%（購入÷来訪）']:.2f}%")
out.append('■ 今日の時間別: 来訪・カート追加・決済画面・購入（見込み）｜注文・売上（値引後）・広告費')
for h in range(0, 18):
    e = T[h][0] * H[h][3] / H[h][0]; out.append(f'  {h}時台: {T[h][0]}・{T[h][1]}・{T[h][2]}・{T[h][3]}（{e:.1f}）｜{tv(h)[0]}・{tv(h)[1]-tv(h)[2]:,}・{MH[h][0]:,}' + ('（取り込み途中）' if h == 17 else ''))
out.append(f"  Meta が数えた購入（0〜16時台） {M[TD][4]}件・Shopify の注文 {V[TD][0]}件")
out.append('■ 広告セットの配信（0〜16時台の広告費 ÷ 日予算。日予算は data/budget-snapshots.csv の 11/20・11/20a）')
B = {}
for r in csv.reader(open(os.path.join(ROOT, 'data/budget-snapshots.csv'))):
    if r and r[0] in ('2026-11-20', '2026-11-20a'): B[r[2]] = int(float(r[3]))
tb = 0
for cn, an, cost, imp, clk, atc, pu in sorted(A, key=lambda a: -a[2]):
    b = B.get(an); tb += b or 0
    out.append(f'  {an}: {cost:,} ÷ ' + (f'{b:,} = {cost/b:.0%}' if b else f'{b}（停止）') + f'・表示 {imp:,}・クリック率 {clk/imp:.2%}・CPM {cost/imp*1000:,.0f}')
out.append(f'  合計: {sum(a[2] for a in A):,} ÷ {tb:,} = {sum(a[2] for a in A)/tb:.0%}（過去の同じ時刻: ' + '・'.join(f'{d[5:]} {M[d][0]:,}' for d in past[-4:]) + '）')
out.append('■ 商品別（今日 0〜16時台。広告費が出ている全キャンペーン＋カタログ）: 注文・個数・売上（値引後）・広告費・売上÷広告費 ｜ うち 11〜16時台の注文 ｜ 直近7日（11/13〜19）の同じ時刻の平均注文 → 偶然の範囲か')
PD10 = {r[1]: [int(x) for x in r[2:]] for r in R10['PD'] if r[0] == TD}
camp = collections.defaultdict(lambda: [0, 0, 0])
for cn, an, cost, imp, clk, atc, pu in A: camp[cn][0] += cost; camp[cn][1] += imp; camp[cn][2] += clk
used = set()
for cn, (cost, imp, clk) in sorted(camp.items(), key=lambda x: -x[1][0]):
    key = re.sub(r'\s*v\d+$', '', cn).strip()
    if cn.startswith('カタログ'): out.append(f'  {cn}: —・—・—・{cost:,}・—'); continue
    o, g, dc, q = P_.get(key, [0, 0, 0, 0]); used.add(key); lam = P7.get(key, [0])[0] / 7; pm = o - PD10.get(key, [0])[0]
    pr = '比べる過去なし' if lam == 0 else (f'{o}件以上 {pge(o, lam):.0%}' if o >= lam else f'{o}件以下 {ple(o, lam):.0%}')
    out.append(f'  {cn}: {o}件・{q}個・{g-dc:,}・{cost:,}・{(g-dc)/cost:.2f} ｜ {pm}件 ｜ 平均 {lam:.1f} → {pr}')
assert set(P_) <= used
out.append(f"  合計: 売上（値引後） {sum(v[1]-v[2] for v in P_.values()):,}・広告費 {sum(a[2] for a in A):,}・売上÷広告費 {sum(v[1]-v[2] for v in P_.values())/sum(a[2] for a in A):.2f}")
open(os.path.join(D0, 'today_h17.txt'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
# --- 追記: 午後（11〜16時台）を 11/19 と合わせて見る・連絡先を入れて買わなかった決済の数
ab = {r[0]: int(r[1]) for r in R['AB']}; abm = {r[0]: int(r[1]) for r in R['ABM']}
rate = sum(H[h][3] for h in PM) / sum(H[h][0] for h in PM); ck = sum(H[h][3] for h in PM) / sum(H[h][2] for h in PM)
ex = ['■ 午後（11〜16時台）を 11/19 と今日の2日で合わせると']
for lab, ds in (('11/19', ['2026-11-19']), ('今日', [TD]), ('2日合計', ['2026-11-19', TD])):
    s = sum(S[d][0] - S10[d][0] for d in ds); k = sum(S[d][2] - S10[d][2] for d in ds); dn = sum(S[d][3] - S10[d][3] for d in ds); lam = s * rate
    pb = sum(math.comb(k, i) * ck ** i * (1 - ck) ** (k - i) for i in range(dn + 1))
    ex.append(f'  {lab}: 来訪 {s}・決済画面 {k}・購入 {dn}（来訪×過去21日の率 {rate:.2%}＝見込み {lam:.1f}・{dn}件以下 {ple(dn, lam):.1%}）・完了÷決済画面 {dn/k:.0%}（過去21日 {ck:.0%}・この数以下 {pb:.1%}）')
ex.append('  連絡先を入れて買わなかった決済（11〜17時に作られた数）: ' + '・'.join(f'{d[5:]} {ab[d]}' for d in sorted(ab)) + '／0〜11時: ' + '・'.join(f'{d[5:]} {abm[d]}' for d in sorted(abm)))
print('\n'.join(ex)); open(os.path.join(D0, 'today_h17.txt'), 'a').write('\n'.join(ex) + '\n')
