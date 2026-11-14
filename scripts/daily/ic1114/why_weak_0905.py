# -*- coding: utf-8 -*-
"""11/14 09:0x ユーザー「既存が弱ったのはなぜ？」
入力: why_weak_raw.json（Meta: 9/1〜10/31 キャンペーン別日別・9〜10月 年齢×性別・8/1起点の累計リーチ 4時点）と data/daily（Shopify 売上・個数・原価）。
1) 既存の柱7商品: 9月（9/4〜10/1）→ 10/23週（10/23〜10/29）で 売上÷広告費 を 表示/円（CPMの逆）× クリック率 × 個数/クリック × 円/個 に分ける
2) いつ落ちたか: 7商品合計の 1万円あたりクリック・クリックあたり個数を 7日移動で
3) 出し尽くしか: 8/1起点の累計リーチから、2週ごとの「新しく届いた人/1万円」と累計の頻度
4) 客層: 9月→10月 年齢×性別の配分の変化と、同じ客層の中での購入/1万円の変化（Meta計上の購入）"""
import csv, sys, json, math, collections, datetime
R = __file__.rsplit('/scripts/', 1)[0] + '/'
raw = json.load(open(R + 'scripts/daily/ic1114/why_weak_raw.json'))
num = lambda x: 0.0 if x in ('null', '') else float(x)
def rows(k):
    f = raw[k]['fields']
    for line in raw[k]['rows']:
        v = next(csv.reader([line])); assert len(v) == len(f), line
        yield dict(zip(f, v))
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
PRODS = ['ナノガラス脱毛パッド', '快適マジックインソール', '伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', '高見えレザーヘッドレストフック', '姿勢サポートチェア', 'バランスケアスリッパ']
SH = {n: {r['date']: r for r in g['series'](n)} for n in PRODS}
M = collections.defaultdict(lambda: [0.0] * 5)   # (camp, date) -> cost, imp, clicks, lpv, pur
for r in rows('daily_camp_0901_1031'):
    v = M[(r['adcampaign_name'], r['date'])]
    for i, f in enumerate(['cost', 'impressions', 'link_clicks', 'landing_page_views', 'offsite_conversions_fb_pixel_purchase']): v[i] += num(r[f])
camp = lambda n: g['CAMP'].get(n, n)
D = lambda s: datetime.date.fromisoformat(s); iso = lambda d: d.isoformat()
rng = lambda a, b: [iso(D(a) + datetime.timedelta(k)) for k in range((D(b) - D(a)).days + 1)]
# 照合: Meta の広告費（このクエリ）と data/daily の広告費（9/1〜10/31・7商品）
for n in PRODS:
    a = sum(M[(camp(n), d)][0] for d in rng('2026-09-01', '2026-10-31')); b = sum(SH[n][d]['ad'] for d in rng('2026-09-01', '2026-10-31') if d in SH[n])
    assert abs(a - b) <= max(50, 0.002 * b), (n, a, b)
def agg(ns, ds):
    t = dict(cost=0, imp=0, clk=0, lpv=0, pur=0, sales=0, qty=0, cogs=0)
    for n in ns:
        for d in ds:
            m = M[(camp(n), d)]; s = SH[n].get(d)
            t['cost'] += m[0]; t['imp'] += m[1]; t['clk'] += m[2]; t['lpv'] += m[3]; t['pur'] += m[4]
            if s: t['sales'] += s['sales']; t['qty'] += s['qty'] or 0; t['cogs'] += s['cost'] or 0
    return t
SEP = rng('2026-09-04', '2026-10-01'); OCT = rng('2026-10-23', '2026-10-29')
print('■1 売上÷広告費の分解: 9月（9/4〜10/1・4週） → 10/23週（10/23〜10/29）。各要素の変化と、売上÷広告費の変化への寄与（対数の割合）')
print('   要素: 表示/1000円（CPMの逆）・クリック率・個数/クリック（買われやすさ）・円/個（単価・まとめ買い）')
def comp(t): return dict(ipy=t['imp'] / t['cost'] * 1000, ctr=t['clk'] / t['imp'], qpc=t['qty'] / t['clk'], ypq=t['sales'] / t['qty'], mer=t['sales'] / t['cost'], mult=(t['sales'] - t['cogs']) / t['cost'], lpvc=t['lpv'] / t['clk'], lpvy=t['lpv'] / t['cost'] * 1e4, qpl=t['qty'] / t['lpv'])
NAME = dict(ipy='表示/千円', ctr='クリック率', qpc='個数/クリック', ypq='円/個')
out = {}
for n in PRODS + ['7商品合計']:
    ns = PRODS if n == '7商品合計' else [n]
    a, b = comp(agg(ns, SEP)), comp(agg(ns, OCT)); out[n] = (a, b)
    tot = math.log(b['mer'] / a['mer'])
    parts = {k: math.log(b[k] / a[k]) for k in NAME}
    assert abs(sum(parts.values()) - tot) < 1e-9
    s = '・'.join(f"{NAME[k]} {(b[k]/a[k]-1)*100:+.0f}%" for k in NAME)
    print(f"  {n}: 倍率 {a['mult']:.2f}→{b['mult']:.2f}・売上÷広告費 {a['mer']:.2f}→{b['mer']:.2f}（{(b['mer']/a['mer']-1)*100:+.0f}%）｜ {s}")
    print(f"      CPM {1000/a['ipy']*1000:,.0f}→{1000/b['ipy']*1000:,.0f}・クリック率 {a['ctr']*100:.2f}→{b['ctr']*100:.2f}%・個数/100クリック {a['qpc']*100:.2f}→{b['qpc']*100:.2f}・来訪/クリック {a['lpvc']*100:.0f}→{b['lpvc']*100:.0f}%")
    print(f"      来訪（LPV）で数えると: 来訪/1万円 {a['lpvy']:.0f}→{b['lpvy']:.0f}（{(b['lpvy']/a['lpvy']-1)*100:+.0f}%）・個数/100来訪 {a['qpl']*100:.2f}→{b['qpl']*100:.2f}（{(b['qpl']/a['qpl']-1)*100:+.0f}%）")

# ---- 2) いつ落ちたか ----
print()
print('■2 いつ落ちたか（7商品合計・7日移動。日付はその7日の最終日）: 1万円あたりクリック・100クリックあたり個数・倍率')
days = rng('2026-09-07', '2026-10-31')
prev = None
for d in days:
    w = rng(iso(D(d) - datetime.timedelta(6)), d); t = agg(PRODS, w)
    if D(d).weekday() in (3,) or d in ('2026-10-31',):   # 木曜ごと
        print(f"  〜{d[5:]}: 1万円あたりクリック {t['clk']/t['cost']*1e4:.0f}・来訪 {t['lpv']/t['cost']*1e4:.0f}・CPM {t['cost']/t['imp']*1000:,.0f}・クリック率 {t['clk']/t['imp']*100:.2f}%・100クリックあたり個数 {t['qty']/t['clk']*100:.2f}・100来訪あたり {t['qty']/t['lpv']*100:.2f}・倍率 {(t['sales']-t['cogs'])/t['cost']:.2f}")
print('  商品別 1万円あたりクリック（週・木曜まで）:')
thu = [d for d in days if D(d).weekday() == 3]
for n in PRODS:
    print('   ' + n[:8] + ': ' + ' '.join(f"{agg([n], rng(iso(D(d)-datetime.timedelta(6)), d))['clk']/max(1,agg([n], rng(iso(D(d)-datetime.timedelta(6)), d))['cost'])*1e4:.0f}" for d in thu) + f"  （{thu[0][5:]}〜{thu[-1][5:]}）")
print('  商品別 100クリックあたり個数（週・木曜まで）:')
for n in PRODS:
    xs = [agg([n], rng(iso(D(d)-datetime.timedelta(6)), d)) for d in thu]
    print('   ' + n[:8] + ': ' + ' '.join(f"{x['qty']/max(1,x['clk'])*100:.1f}" for x in xs))

# ---- 3) 出し尽くしか ----
print()
print('■3 届いた人の累計（8/1から）と、2週ごとに新しく届いた人/1万円・その期間の表示のうち新しい人の割合（目安）・累計の頻度')
RC = {}
for k in ['reach_cum_0801_0914', 'reach_cum_0801_0928', 'reach_cum_0801_1012', 'reach_cum_0801_1026']:
    RC[k[-4:]] = {r['adcampaign_name']: (num(r['reach']), num(r['impressions']), num(r['cost'])) for r in rows(k)}
ks = ['0914', '0928', '1012', '1026']
for n in PRODS:
    c = camp(n); s = []
    for i, k in enumerate(ks):
        r, im, co = RC[k].get(c, (0, 0, 0))
        if i == 0: s.append(f"〜9/14 累計{r/1e4:.1f}万人・頻度{im/max(r,1):.2f}"); continue
        r0, im0, co0 = RC[ks[i-1]].get(c, (0, 0, 0))
        if co - co0 < 1000: s.append(f"〜{k[:2]}/{k[2:]} 配信なし"); continue
        s.append(f"〜{int(k[:2])}/{int(k[2:])} 新規{(r-r0)/(co-co0)*1e4:.0f}人/1万円・新規割合{(r-r0)/(im-im0)*100:.0f}%・頻度{im/r:.2f}")
    print(f"  {n}: " + '／'.join(s))

# ---- 4) 客層 ----
print()
print('■4 客層（Meta 年齢×性別）: 9月→10月。購入/1万円（Meta計上）の変化を「配分の変化」と「同じ客層の中での変化」に分ける')
AG = collections.defaultdict(lambda: [0.0] * 4)   # (month, camp, age, gender)
for r in rows('month_camp_age_gender_0901_1031'):
    if r['gender'] == 'unknown' or r['age'] == 'Unknown': continue
    v = AG[(r['Yearmonth'][-2:], r['adcampaign_name'], r['age'], r['gender'])]
    for i, f in enumerate(['cost', 'impressions', 'link_clicks', 'offsite_conversions_fb_pixel_purchase']): v[i] += num(r[f])
for n in PRODS:
    c = camp(n)
    seg = sorted({(k[2], k[3]) for k in AG if k[1] == c})
    S9 = {s: AG[('09', c) + s] for s in seg}; S10 = {s: AG[('10', c) + s] for s in seg}
    c9 = sum(v[0] for v in S9.values()); c10 = sum(v[0] for v in S10.values())
    p9 = sum(v[3] for v in S9.values()) / c9 * 1e4; p10 = sum(v[3] for v in S10.values()) / c10 * 1e4
    k9 = sum(v[2] for v in S9.values()) / c9 * 1e4; k10 = sum(v[2] for v in S10.values()) / c10 * 1e4
    # 10月の配分 × 9月の客層別の購入率 = 配分だけ変わった場合
    mixp = sum(S10[s][0] / c10 * (S9[s][3] / S9[s][0] * 1e4 if S9[s][0] > 0 else 0) for s in seg)
    mixk = sum(S10[s][0] / c10 * (S9[s][2] / S9[s][0] * 1e4 if S9[s][0] > 0 else 0) for s in seg)
    top = lambda S, cc: '・'.join(f"{a}{'女' if gg=='female' else '男'}{v[0]/cc*100:.0f}%" for (a, gg), v in sorted(S.items(), key=lambda x: -x[1][0])[:3])
    male9 = sum(v[0] for (a, gg), v in S9.items() if gg == 'male') / c9; male10 = sum(v[0] for (a, gg), v in S10.items() if gg == 'male') / c10
    print(f"  {n}: 広告費の上位 9月 {top(S9,c9)} → 10月 {top(S10,c10)}／男性の割合 {male9*100:.0f}%→{male10*100:.0f}%")
    print(f"      クリック/1万円 {k9:.0f}→{k10:.0f}（配分の変化だけなら {mixk:.0f}）・購入/1万円 {p9:.2f}→{p10:.2f}（配分の変化だけなら {mixp:.2f}）")

# ---- 5) 配置 ----
print()
print('■5 配置（既存7商品・ISO週 月〜日）: 広告費の割合と、配置ごとのクリック率・来訪/1万円。1万円あたり来訪の変化を「配置の配分」と「同じ配置の中」に分ける')
PL = collections.defaultdict(lambda: [0.0] * 5)
for r in rows('week_placement_7prod_0914_1101'):
    w = int(r['Yearweek'].split('|')[1]); pos = r['publisher_platform'] + '/' + r['platform_position']
    v = PL[(w, pos)]
    for i, f in enumerate(['cost', 'impressions', 'link_clicks', 'landing_page_views', 'offsite_conversions_fb_pixel_purchase']): v[i] += num(r[f])
MAIN = ['instagram/feed', 'instagram/instagram_reels', 'instagram/instagram_stories', 'facebook/facebook_reels', 'facebook/feed', 'threads/threads_feed']
for w in range(38, 45):
    tot = [sum(v[i] for (ww, p), v in PL.items() if ww == w) for i in range(5)]
    s = '・'.join(f"{p.split('/')[-1].replace('instagram_','IG').replace('facebook_','FB').replace('feed','feed')}{('(IG)' if p=='instagram/feed' else '(FB)' if p=='facebook/feed' else '')} {PL[(w,p)][0]/tot[0]*100:.0f}%/{PL[(w,p)][2]/max(PL[(w,p)][1],1)*100:.2f}%" for p in MAIN)
    print(f"  週{w}: 来訪/1万円 {tot[3]/tot[0]*1e4:.0f}・クリック率 {tot[2]/tot[1]*100:.2f}%｜ 割合/クリック率: {s}")
def per(w, p, i): v = PL[(w, p)]; return v[i] / v[0] * 1e4 if v[0] else 0
for a, b in [(38, 39), (39, 43)]:
    A = [sum(PL[(a, p)][i] for p in {pp for (ww, pp) in PL if ww == a}) for i in range(5)]
    B = [sum(PL[(b, p)][i] for p in {pp for (ww, pp) in PL if ww == b}) for i in range(5)]
    ps = {pp for (ww, pp) in PL if ww in (a, b)}
    mix = sum(PL[(b, p)][0] / B[0] * per(a, p, 3) for p in ps if PL[(a, p)][0] > 0)
    print(f"  週{a}→週{b}: 来訪/1万円 {A[3]/A[0]*1e4:.0f}→{B[3]/B[0]*1e4:.0f}（配置の配分だけ変わったなら {mix:.0f}）")
    for p in MAIN:
        print(f"     {p}: 割合 {PL[(a,p)][0]/A[0]*100:.0f}%→{PL[(b,p)][0]/B[0]*100:.0f}%・来訪/1万円 {per(a,p,3):.0f}→{per(b,p,3):.0f}・CPM {PL[(a,p)][0]/PL[(a,p)][1]*1000:,.0f}→{PL[(b,p)][0]/PL[(b,p)][1]*1000:,.0f}・クリック率 {PL[(a,p)][2]/PL[(a,p)][1]*100:.2f}→{PL[(b,p)][2]/PL[(b,p)][1]*100:.2f}%・購入/1万円 {per(a,p,4):.1f}→{per(b,p,4):.1f}")
