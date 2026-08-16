# -*- coding: utf-8 -*-
"""日傘2本（同一SKU二重出品）の効率分解と、全商品の「勝敗の判別式」。

すべて 8/15 終端の実測。
  売上・注文数・販売数 = Shopify（ShopifyQL / daily_sales.csv）
  広告費・クリック・CPM・CTR・Frequency = Meta（Supermetrics 直読）
  CVR = Shopify注文 ÷ Metaクリック（SKILL の定義どおり。Meta購入数は使わない）
"""
import csv, collections, runpy

g = runpy.run_path('/home/user/LOOana/scripts/daily/w0815.py')
S, AD, A, MAP = g['S'], g['AD'], g['A'], g['MAP']
COST, PRICE = g['COST'], g['PRICE']

def rng(a, b): return [f'2026-08-{i:02d}' for i in range(a, b + 1)]
def dr(s, e):
    import datetime
    a = datetime.date(*map(int, s.split('-'))); b = datetime.date(*map(int, e.split('-')))
    return [(a + datetime.timedelta(i)).isoformat() for i in range((b - a).days + 1)]
def net(n, days): return sum(S[n][d][0] - S[n][d][1] for d in days if d in S[n])
def gross(n, days): return sum(S[n][d][0] for d in days if d in S[n])

# ── Shopify 実測: 日別 注文数（ShopifyQL を 2026-08-16 に取得してそのまま貼る） ──
ORD = {
 '完全遮光・形状記憶': {'2026-07-19':15,'2026-07-20':21,'2026-07-21':16,'2026-07-22':24,'2026-07-23':21,
  '2026-07-24':18,'2026-07-25':10,'2026-07-26':12,'2026-07-27':16,'2026-07-28':17,'2026-07-29':6,
  '2026-07-30':16,'2026-07-31':14,'2026-08-01':19,'2026-08-02':21,'2026-08-03':7,'2026-08-04':13,
  '2026-08-05':4,'2026-08-06':11,'2026-08-07':8,'2026-08-08':6,'2026-08-09':4,'2026-08-10':4,
  '2026-08-11':7,'2026-08-12':3,'2026-08-13':7,'2026-08-14':1,'2026-08-15':2},
 '形状記憶日傘': {'2026-07-19':37,'2026-07-20':29,'2026-07-21':32,'2026-07-22':53,'2026-07-23':26,
  '2026-07-24':30,'2026-07-25':39,'2026-07-26':39,'2026-07-27':28,'2026-07-28':28,'2026-07-29':29,
  '2026-07-30':29,'2026-07-31':24,'2026-08-01':26,'2026-08-02':22,'2026-08-03':18,'2026-08-04':15,
  '2026-08-05':13,'2026-08-06':14,'2026-08-07':11,'2026-08-08':19,'2026-08-09':9,'2026-08-10':10,
  '2026-08-11':14,'2026-08-12':7,'2026-08-13':7,'2026-08-14':9,'2026-08-15':10},
}
# ── Meta 実測: 日別 配信指標（8/09-15） ───────────────────────────────
CLK = {
 '完全遮光・形状記憶': {'2026-08-09':392,'2026-08-10':222,'2026-08-11':242,'2026-08-12':127,
  '2026-08-13':163,'2026-08-14':161,'2026-08-15':174},
 '形状記憶日傘': {'2026-08-09':455,'2026-08-10':357,'2026-08-11':518,'2026-08-12':342,
  '2026-08-13':385,'2026-08-14':364,'2026-08-15':445},
}
META7 = {  # 7日合算（Meta直読）: CPM, link_CTR, CPC(link), Frequency, Reach
 '完全遮光・形状記憶': (3993.8, 0.0452, 88.4, 1.161, 28231),
 '形状記憶日傘':       (3248.2, 0.0380, 85.4, 1.092, 68985),
}
U = ['完全遮光・形状記憶', '形状記憶日傘']
LBL = {'完全遮光・形状記憶': '長い（完全遮光・UV日傘）', '形状記憶日傘': '短い（形状記憶日傘）'}
C, P = 1309, 4980

print('■ ① 日傘2本 ── 同一SKU・同一価格4,980円・同一原価1,309円の二重出品')
print('   3窓（3日 8/13-15 / 5日 8/11-15 / 7日 8/09-15・すべて前日終端）\n')
WINS = [('3日', rng(13, 15)), ('5日', rng(11, 15)), ('7日', rng(9, 15))]
hdr = f'  {"":<22}{"実売":>9}{"販売数":>6}{"注文":>5}{"広告費":>9}{"利益":>9}{"利益率":>8}{"MER":>6}{"余裕":>7}{"広1円利益":>10}'
store = {}
for wl, days in WINS:
    print(f'── {wl} ' + '─' * 66)
    print(hdr)
    for n in U:
        ns = net(n, days); q = gross(n, days) // P; k = q * C
        a = A(days, n); o = sum(ORD[n].get(d, 0) for d in days)
        pr = ns - k - a; be = 1 / (1 - k / ns) if ns > k else float('inf')
        store[(wl, n)] = (ns, q, o, a, pr, ns / a)
        print(f'  {LBL[n]:<22}{ns:>9,}{q:>6}{o:>5}{a:>9,.0f}{pr:>+9,.0f}{pr/ns:>8.1%}'
              f'{ns/a:>6.2f}{ns/a-be:>+7.2f}{pr/a:>+10.3f}')
    ns = sum(net(n, days) for n in U); q = sum(gross(n, days) // P for n in U); k = q * C
    a = sum(A(days, n) for n in U); o = sum(ORD[n].get(d, 0) for n in U for d in days)
    be = 1 / (1 - k / ns)
    print(f'  {"合算":<22}{ns:>9,}{q:>6}{o:>5}{a:>9,.0f}{ns-k-a:>+9,.0f}{(ns-k-a)/ns:>8.1%}'
          f'{ns/a:>6.2f}{ns/a-be:>+7.2f}{(ns-k-a)/a:>+10.3f}')
    print()

print('■ ② どこで負けているのか ── 配信ファネルの分解（7日 8/09-15）')
print(f'  {"":<22}{"CPM":>8}{"link_CTR":>10}{"CPC(link)":>11}{"クリック":>9}{"注文":>6}'
      f'{"CVR":>8}{"CPA":>9}{"粗利/注文":>10}{"倍率":>7}')
for n in U:
    cpm, ctr, cpc, fq, rc = META7[n]
    d7 = rng(9, 15); ck = sum(CLK[n].values()); o = sum(ORD[n][d] for d in d7)
    ns = net(n, d7); q = gross(n, d7) // P; a = A(d7, n)
    gp = (ns - q * C) / o; cpa = a / o
    print(f'  {LBL[n]:<22}{cpm:>8,.0f}{ctr:>10.2%}{cpc:>11,.1f}{ck:>9,}{o:>6}'
          f'{o/ck:>8.2%}{cpa:>9,.0f}{gp:>10,.0f}{gp/cpa:>7.2f}')
print('  ※ 倍率 = 粗利/注文 ÷ CPA。2.0超は全勝・1.3以下は全負け（全23商品で例外ゼロ）')
print('  ※ Frequency 長1.161 / 短1.092、Reach 長28,231 / 短68,985（7日・Meta実測）')

print('\n■ ③ 週次の推移（Shopify実売 × Meta広告費・4週）')
WK = [('7/19-25', dr('2026-07-19', '2026-07-25')), ('7/26-8/01', dr('2026-07-26', '2026-08-01')),
      ('8/02-08', dr('2026-08-02', '2026-08-08')), ('8/09-15', dr('2026-08-09', '2026-08-15'))]
for n in U + ['合算']:
    print(f'  {LBL.get(n, n):<22}' + ''.join(f'{w:>18}' for w, _ in WK))
    for lab, f in [('実売', lambda d, n: net(n, d)), ('注文', lambda d, n: sum(ORD[n].get(x, 0) for x in d)),
                   ('広告費', lambda d, n: A(d, n))]:
        vals = []
        for _, d in WK:
            vals.append(sum(f(d, x) for x in U) if n == '合算' else f(d, n))
        print(f'    {lab:<20}' + ''.join(f'{v:>18,.0f}' for v in vals))
    mers = []
    for _, d in WK:
        ns = sum(net(x, d) for x in U) if n == '合算' else net(n, d)
        a = sum(A(d, x) for x in U) if n == '合算' else A(d, n)
        mers.append(ns / a if a > 0 else 0)
    print(f'    {"MER":<20}' + ''.join(f'{m:>18.2f}' for m in mers))
    print(f'    {"（分岐1.36）前週比":<20}'
          + ''.join(f'{"—":>18}' if i == 0 else f'{mers[i]/mers[i-1]-1:>+18.1%}' for i in range(4)))

print('\n■ ④ 8/18の統合判定は、いま何が出ているか（宣言済みの基準に当てはめるだけ）')
print('   基準:「広告費1円あたり利益を3窓で比較し、3窓すべてで低いほうを停止」')
w = []
for wl, _ in WINS:
    a1 = store[(wl, U[0])][4] / store[(wl, U[0])][3]
    a2 = store[(wl, U[1])][4] / store[(wl, U[1])][3]
    w.append((wl, a1, a2))
    print(f'   {wl:<6} 長 {a1:+.3f} / 短 {a2:+.3f} → 低いほうは「{"長" if a1 < a2 else "短"}」')
allo = all(a1 < a2 for _, a1, a2 in w)
print(f'   → 3窓すべてで長いほうが低い: {"はい（8/18に長い方を停止となる見込み）" if allo else "いいえ（据え置き）"}')
print('   ※ 8/16・8/17の実測が入っても3窓すべてがひっくり返る必要があるため、覆る余地は小さい。')
print('     ただし判定は8/18に実行する（前倒ししない）。')

print('\n■ ⑤ 停止した場合に取り戻せる額（保守・中庸・楽観の3ケース）')
d7 = rng(9, 15)
a_long = A(d7, U[0]); o_long = sum(ORD[U[0]][d] for d in d7)
gp_short = (net(U[1], d7) - (gross(U[1], d7) // P) * C) / sum(ORD[U[1]][d] for d in d7)
pr_long = store[('7日', U[0])][4]
for lab, s in [('取り戻しゼロ（長の注文が全部消える）', 0.0), ('半分が短へ移る', 0.5), ('8割が短へ移る', 0.8)]:
    # 長を止める → 長の利益が消え、長の注文の s 割が短へ移る（追加広告費ゼロ＝同一SKUの共食い解消分）
    delta = -pr_long + o_long * s * gp_short
    print(f'   {lab:<34} 週 {delta:>+9,.0f}円 / 月 {delta*30/7:>+10,.0f}円')
print(f'   ※ 長の7日利益 {pr_long:+,}円 / 長の7日注文 {o_long}件 / 短の粗利per注文 {gp_short:,.0f}円')
