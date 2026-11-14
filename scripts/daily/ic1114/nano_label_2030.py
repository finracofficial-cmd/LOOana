# -*- coding: utf-8 -*-
"""11/14(土) 20:3x 「ナノガラスの表記をこの前変えたじゃん？広告効率で考えると前後でどう変わった？」
ナノの表示の変更は記録上2つ:
 ①商品名（10/29 08:00〜10/31 00:30 に4回。今の「【在庫セール⏰】…【顧客満足度4.9⭐️】…」は 10/31 00:30 から＝ユーザー申告）
 ②商品ページのテンプレート templates/product.datumoupad.json の更新 11/10 15:11 JST（今は他商品の15分タイマーの代わりに「在庫限りセール中！⏰」の在庫メーター。変更前の中身は記録なし）
それぞれ前後7日（②は後が3日）で、ナノの倍率・売上÷広告費・広告費1万円あたりの注文を、同じ期間のナノ以外（店全体−ナノ）と並べる。偶然かどうかは注文数で（ナノ以外の変化で補正した期待とのポアソン比較）。"""
import os, sys, csv, json, math, collections, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, series, A = g['S'], g['series'], g['A']
N = 'ナノガラス脱毛パッド'
nano = {r['date']: r for r in series(N)}
# 店全体（CSV の全商品の売上・全キャンペーンの広告費）
ST = collections.defaultdict(float); AT = collections.defaultdict(float)
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv', encoding='utf-8')): ST[r['date']] += int(r['gross']) - int(r['disc'])
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv', encoding='utf-8')): AT[r['date']] += float(r['cost'])
O = {r[0]: int(r[1]) for r in json.load(open(D + 'nano_orders_1015_1114.json'))['rows']}
for d in ('2026-10-22', '2026-11-12'):          # 照合: Shopify 直読の売上（値引後）と CSV の系列が一致する
    gross = [int(r[2]) + int(r[3]) for r in json.load(open(D + 'nano_orders_1015_1114.json'))['rows'] if r[0] == d][0]
    assert gross == nano[d]['sales'], (d, gross, nano[d]['sales'])
def days(a, b):
    x = datetime.date.fromisoformat(a); out = []
    while x <= datetime.date.fromisoformat(b): out.append(x.isoformat()); x += datetime.timedelta(1)
    return out
def agg(ds):
    s = sum(nano[d]['sales'] for d in ds); c = sum(nano[d]['cost'] or 0 for d in ds); a = sum(nano[d]['ad'] for d in ds)
    o = sum(O[d] for d in ds); q = sum(nano[d]['qty'] or 0 for d in ds)
    os_ = sum(ST[d] for d in ds) - s; oa = sum(AT[d] for d in ds) - a
    return dict(s=s, c=c, a=a, o=o, q=q, mult=(s - c) / a, mer=s / a, opa=o / a * 1e4, prof=s - c - a, n=len(ds), omer=os_ / oa, oad=oa)
def pois(k, lam, low=True):
    cdf = sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))
    return cdf if low else 1 - cdf + math.exp(-lam) * lam ** k / math.factorial(k)
def show(title, before, after, note=''):
    B, F = agg(before), agg(after)
    print(f'■ {title}{note}')
    for lab, X in (('前 ' + before[0][5:] + '〜' + before[-1][5:], B), ('後 ' + after[0][5:] + '〜' + after[-1][5:], F)):
        print(f"  {lab}（{X['n']}日）: 広告費 {X['a']/X['n']:,.0f}/日・注文 {X['o']/X['n']:.1f}/日・個数 {X['q']/X['n']:.1f}/日・倍率 {X['mult']:.2f}・売上÷広告費 {X['mer']:.2f}・広告費1万円あたり注文 {X['opa']:.2f}・利益 {X['prof']/X['n']:+,.0f}/日 ｜ ナノ以外の売上÷広告費 {X['omer']:.2f}")
    adj = F['omer'] / B['omer']                             # 同じ期間のナノ以外の動き
    lam = B['o'] / B['a'] * F['a'] * adj                    # 前の「注文/広告費」×後の広告費×ナノ以外の変化
    p = pois(F['o'], lam) if F['o'] < lam else pois(F['o'], lam, low=False)
    print(f"  → 倍率 {B['mult']:.2f}→{F['mult']:.2f}（{F['mult']/B['mult']-1:+.0%}）・ナノ以外の売上÷広告費 {B['omer']:.2f}→{F['omer']:.2f}（{adj-1:+.0%}）")
    print(f"  → 注文: 後は {F['o']}件。前の効率×ナノ以外の変化で見た期待 {lam:.1f}件（{F['o']/lam-1:+.0%}）・{'この数以下' if F['o'] < lam else 'この数以上'}になる確率 {p:.1%}\n")
show('①商品名の変更（10/29 08:00〜・今の名前は 10/31 00:30〜）', days('2026-10-22', '2026-10-28'), days('2026-10-31', '2026-11-06'))
show('①の続き（今の名前の2週目）', days('2026-10-22', '2026-10-28'), days('2026-11-07', '2026-11-13'))
show('②商品ページの更新（11/10 15:11・在庫メーター）', days('2026-11-03', '2026-11-09'), days('2026-11-11', '2026-11-13'), '・11/10 は前後が混ざるので除く')
print('■ 日別（ナノ）: 日付 広告費・注文・倍率')
for d in days('2026-10-20', '2026-11-13'):
    r = nano[d]; m = (r['sales'] - (r['cost'] or 0)) / r['ad'] if r['ad'] else float('nan')
    print(f"  {d[5:]}: {r['ad']:>7,.0f}・{O[d]:>2}件・{m:.2f}")
