# -*- coding: utf-8 -*-
"""11/13 21:0x 「マグネットの成功例をいかして他に広告を追加した方がよいものを調べて」
入力: creative_2100_raw.json（Meta 広告別・週別 6/1〜11/13／日別 10/24〜11/13／7日の頻度）と data/daily（商品別の倍率）。
1) 過去に「動いている広告セットに2本目以降を足した」例: 足した週とその次の週で、新しい広告の取り分・クリック率・購入/1万円を古い広告と比べる
2) 今の広告セット: 広告の本数・今の広告の古さ・クリック率の推移・7日の頻度・7日の倍率"""
import json, csv, sys, collections, datetime
R = __file__.rsplit('/scripts/', 1)[0] + '/'
raw = json.load(open(R + 'scripts/daily/ic1113/creative_2100_raw.json'))
num = lambda x: 0.0 if x in ('null', '') else float(x)
def rows(k):
    f = raw[k]['fields']
    for line in raw[k]['rows']:
        vals = next(csv.reader([line]))
        assert len(vals) == len(f), line
        yield dict(zip(f, vals))

# ---- 1) 過去の追加例（週別） ----
W = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0] * 4))   # (camp, adset) -> week -> ad_id -> [cost, imp, clicks, purchases]
NAME = {}
for r in rows('ad_weekly_0601_1113'):
    k = (r['adcampaign_name'], r['adset_name']); w = int(r['Yearweek'].split('|')[1])
    v = W[k][(w, r['ad_id'])]
    for i, f in enumerate(['cost', 'impressions', 'link_clicks', 'offsite_conversions_fb_pixel_purchase']): v[i] += num(r[f])
    NAME[r['ad_id']] = r['ad_name']
print('■ 過去に、動いている広告セットへ広告を足した例（足した週＋次の週。週46は11/13途中まで）')
print('  広告セット / 足した広告（週）: 新しい広告の取り分・クリック率 新 vs 古・購入/1万円 新 vs 古')
cases = []
for k, d in W.items():
    first = {}
    for (w, a), v in d.items():
        if v[0] > 0: first[a] = min(first.get(a, 99), w)
    start = min(first.values())
    for a, w0 in sorted(first.items(), key=lambda x: x[1]):
        if w0 == start: continue
        olds = [b for b, wb in first.items() if wb < w0 and (d.get((w0, b), [0])[0] > 0 or d.get((w0 - 1, b), [0])[0] > 0)]
        if not olds: continue
        weeks = [w0, w0 + 1]
        new = [sum(d.get((w, a), [0] * 4)[i] for w in weeks) for i in range(4)]
        old = [sum(d.get((w, b), [0] * 4)[i] for w in weeks for b in olds) for i in range(4)]
        if new[0] + old[0] == 0: continue
        share = new[0] / (new[0] + old[0])
        ctr = lambda v: v[2] / v[1] * 100 if v[1] else float('nan')
        p10k = lambda v: v[3] / v[0] * 1e4 if v[0] else float('nan')
        cases.append(dict(k=k, ad=NAME[a], w0=w0, share=share, ctr_n=ctr(new), ctr_o=ctr(old), p_n=p10k(new), p_o=p10k(old), cost_n=new[0], cost_o=old[0], pur_n=new[3], pur_o=old[3]))
for c in sorted(cases, key=lambda c: c['w0']):
    print(f"  {c['k'][1]} / {c['ad']}（週{c['w0']}）: 取り分 {c['share']*100:.0f}%（新 {c['cost_n']:,.0f}円）・クリック率 {c['ctr_n']:.2f}% vs {c['ctr_o']:.2f}%・購入/1万円 {c['p_n']:.1f}（{c['pur_n']:.0f}件） vs {c['p_o']:.1f}（{c['pur_o']:.0f}件）")
big = [c for c in cases if c['cost_n'] >= 10000 and c['w0'] < 46]
print(f"  新しい広告に1万円以上使われた例（今週分を除く）{len(big)}件: 取り分50%以上 {sum(c['share'] >= .5 for c in big)}件／クリック率が古い広告より高い {sum(c['ctr_n'] > c['ctr_o'] for c in big)}件／購入/1万円が古い広告より高い {sum(c['p_n'] > c['p_o'] for c in big)}件")
small = [c for c in cases if c['cost_n'] < 10000 and c['w0'] < 46]
print(f"  新しい広告にほとんど使われなかった例（2週で1万円未満）{len(small)}件: " + '・'.join(f"{c['k'][1]}/{c['ad']}" for c in small))

# ---- 2) 今の広告セット ----
D = collections.defaultdict(lambda: [0.0] * 4)   # (adset, ad_id, date)
ADS = collections.defaultdict(set); FIRST = {}
for r in rows('ad_daily_1024_1113'):
    v = D[(r['adset_name'], r['ad_id'], r['date'])]
    for i, f in enumerate(['cost', 'impressions', 'link_clicks', 'offsite_conversions_fb_pixel_purchase']): v[i] += num(r[f])
    ADS[r['adset_name']].add(r['ad_id'])
CAMP_OF = {}
for r in rows('ads_active_1106_1113'): CAMP_OF[r['adset_name']] = r['adcampaign_name']
FREQ = {r['adset_name']: (num(r['frequency']), num(r['reach'])) for r in rows('adset_reach_1106_1112')}
wk_first = {}
for k, d in W.items():
    for (w, a), v in d.items():
        if v[0] > 0: wk_first[a] = min(wk_first.get(a, 99), w)
def agg(adset, ads, dates):
    v = [0.0] * 4
    for a in ads:
        for dt in dates:
            x = D.get((adset, a, dt))
            if x:
                for i in range(4): v[i] += x[i]
    return v
day = lambda s, k: (datetime.date.fromisoformat(s) + datetime.timedelta(k)).isoformat()
L7 = [day('2026-11-12', -k) for k in range(7)]; L3 = ['2026-11-11', '2026-11-12', '2026-11-13']; P7 = [day('2026-11-05', -k) for k in range(7)]
# 商品別 7日の倍率（data/daily・11/6〜11/12）
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
MULT = {}
for n in g['S']:
    camp = g['CAMP'].get(n, n)
    rs = [r for r in g['series'](n) if r['date'] in L7]
    ad = sum(r['ad'] for r in rs)
    if ad > 0: MULT[camp] = ((sum(r['sales'] for r in rs) - sum(r['cost'] or 0 for r in rs)) / ad, ad)
print()
print('■ 今の広告セット（11/13 に広告費が出ているもの）: 広告の本数・今の主な広告の古さ・クリック率（その広告の最初の2週 → 前の7日 10/30〜11/5 → 直近7日 11/6〜11/12 → 直近3日 11/11〜11/13）・7日の頻度・商品の7日の倍率')
out = []
for adset in sorted(ADS, key=lambda s: -sum(D.get((s, a, d), [0])[0] for a in ADS[s] for d in L7)):
    live = [a for a in ADS[adset] if D.get((adset, a, '2026-11-13'), [0])[0] > 0]
    if not live: continue
    main = max(live, key=lambda a: sum(D.get((adset, a, d), [0])[0] for d in L7))
    w0 = wk_first.get(main)
    # 最初の2週（週別データ）
    k = [kk for kk in W if kk[1] == adset][0]
    f2 = [sum(W[k].get((w, main), [0] * 4)[i] for w in (w0, w0 + 1)) for i in range(4)]
    ctr = lambda v: v[2] / v[1] * 100 if v[1] else float('nan')
    c_f2 = ctr(f2); c_p7 = ctr(agg(adset, [main], P7)); c_l7 = ctr(agg(adset, [main], L7)); c_l3 = ctr(agg(adset, [main], L3))
    age_w = 46 - w0
    fr = FREQ.get(adset, (float('nan'), 0))
    camp = CAMP_OF.get(adset, k[0])
    m = MULT.get(camp, (float('nan'), 0))
    cost7 = sum(agg(adset, ADS[adset], L7)[:1])
    out.append(dict(adset=adset, camp=camp, n=len(live), main=NAME[main], w0=w0, age=age_w, c_f2=c_f2, c_p7=c_p7, c_l7=c_l7, c_l3=c_l3, fr=fr[0], mult=m[0], cost7=cost7))
    print(f"  {adset}: 広告{len(live)}本（主 {NAME[main]}・週{w0}から＝約{age_w}週）・クリック率 {c_f2:.2f} → {c_p7:.2f} → {c_l7:.2f} → {c_l3:.2f}%（最初比 {(c_l3/c_f2-1)*100:+.0f}%）・頻度 {fr[0]:.2f}・倍率7日 {m[0]:.2f}（商品・広告費 {m[1]:,.0f}）・この広告セット7日 {cost7:,.0f}円")
json.dump(out, open(R + 'scripts/daily/ic1113/creative_2100_out.json', 'w'), ensure_ascii=False, indent=1)
