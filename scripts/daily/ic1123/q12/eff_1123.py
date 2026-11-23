# -*- coding: utf-8 -*-
"""11/23 12時台「広告効率が悪化してる気がする／利益率／広告費が設定より多い／フック／新商品／UV」への答えの数字。
入力: w1122.py（daily_*.csv の積み直し）・o1122/meta_acct_daily_1004_1122.txt・o1122/sess_daily_1004_1122.json・data/daily/daily_order_bands.csv・data/budget-snapshots.csv・
o1122/an1123_out.json・orders_7d_1116_1122_raw.json・ad_level_1026_1122.txt・この q12 の今日の取得ファイル（0〜11時台の広告・12:1x までの注文）"""
import io, contextlib, os, json, csv, math, collections, datetime, re
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D0 + '../../../..')
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1122.py').read(), g)
WIN, agg, A, ACCT, ALLD, HOL = g['WIN'], g['agg'], g['A'], g['ACCT'], g['ALLD'], g['HOL']
def tot(days):
    key = 'e' + days[0] + days[-1]; WIN[key] = days; N, DC, Q, K = agg(days, key); s = sum(N.values()); k = sum(K.values()); a = ACCT(days); return s, k, a
MA = {}
for l in open('scripts/daily/o1122/meta_acct_daily_1004_1122.txt'):
    if l[0] == '#': continue
    p = l.strip().split(','); MA[p[0]] = (int(p[1]), int(p[2]), int(p[4]))            # cost, imp, link_clicks
SE = {r[0]: (int(r[1]), int(r[2]), int(r[4])) for r in json.load(open('scripts/daily/o1122/sess_daily_1004_1122.json'))['rows']}   # 来訪・カート・購入
OR = {r['date']: int(r['orders']) for r in csv.DictReader(open('data/daily/daily_order_bands.csv'))}
L = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); L.append(s)
def rng(a, b): return [d for d in ALLD if a <= d <= b]
def fac(days):
    s, k, a = tot(days); imp = sum(MA[d][1] for d in days); clk = sum(MA[d][2] for d in days); ses = sum(SE[d][0] for d in days); o = sum(OR[d] for d in days)
    return dict(n=len(days), s=s, k=k, a=a, mer=s / a, bai=(s - k) / a, pr=(s - k - a) / s, kr=k / s, ar=a / s, prof=(s - k - a) / len(days), adday=a / len(days),
                cpm=a / imp * 1000, ctr=clk / imp, spc=ses / clk, cvr=o / ses, aov=s / o, cpc=a / clk)
blocks = [('11/16〜22', '2026-11-16', '2026-11-22'), ('11/9〜15', '2026-11-09', '2026-11-15'), ('11/2〜8', '2026-11-02', '2026-11-08'), ('10/26〜11/1', '2026-10-26', '2026-11-01'),
          ('10/19〜25', '2026-10-19', '2026-10-25'), ('10/12〜18', '2026-10-12', '2026-10-18'), ('10/5〜11', '2026-10-05', '2026-10-11')]
P('■ ① 週ごと（7日ずつ・新しい順）: 売上÷広告費｜倍率｜利益率＝100%−原価率−広告費率｜利益/日・広告費/日｜CPM・クリック率・来訪÷クリック・買う率（注文÷来訪）・1注文の売上')
F = {}
for lab, a, b in blocks:
    f = fac(rng(a, b)); F[lab] = f
    P(f"  {lab}: {f['mer']:.2f}｜{f['bai']:.2f}｜{f['pr']:.1%}＝100−{f['kr']:.1%}−{f['ar']:.1%}｜{f['prof']:,.0f}・{f['adday']:,.0f}｜CPM {f['cpm']:,.0f}・{f['ctr']:.2%}・{f['spc']:.2f}・{f['cvr']:.2%}・{f['aov']:,.0f}")
new = F['11/16〜22']; old = fac(rng('2026-10-19', '2026-11-15'))
P('■ ② 直近7日（11/16〜22）÷ その前の28日（10/19〜11/15）: 売上÷広告費＝表示÷広告費 × クリック率 × 来訪÷クリック × 買う率 × 1注文の売上')
P(f"  売上÷広告費 {old['mer']:.2f} → {new['mer']:.2f}（{new['mer']/old['mer']-1:+.1%}）・倍率 {old['bai']:.2f} → {new['bai']:.2f}・利益率 {old['pr']:.1%} → {new['pr']:.1%}（原価率 {old['kr']:.1%} → {new['kr']:.1%}・広告費率 {old['ar']:.1%} → {new['ar']:.1%}）")
parts = [('表示÷広告費（CPM の逆）', old['cpm'] / new['cpm'], f"CPM {old['cpm']:,.0f} → {new['cpm']:,.0f}"), ('クリック率', new['ctr'] / old['ctr'], f"{old['ctr']:.2%} → {new['ctr']:.2%}"),
         ('来訪÷クリック', new['spc'] / old['spc'], f"{old['spc']:.2f} → {new['spc']:.2f}"), ('買う率', new['cvr'] / old['cvr'], f"{old['cvr']:.2%} → {new['cvr']:.2%}"), ('1注文の売上', new['aov'] / old['aov'], f"{old['aov']:,.0f} → {new['aov']:,.0f}")]
chk = 1
for n, r, t in parts: chk *= r; P(f'  {n}: ×{r:.3f}（{r-1:+.1%}）　{t}')
assert abs(chk - new['mer'] / old['mer']) < 1e-6
P(f"  クリック1回の広告費: {old['cpc']:.0f}円 → {new['cpc']:.0f}円（{new['cpc']/old['cpc']-1:+.1%}）")
# 7日ごとの買う率のぶれ（注文数から）: ±2σ ≒ 2/√注文
P(f"  買う率の偶然のぶれ（7日・注文 {sum(OR[d] for d in rng('2026-11-16','2026-11-22'))}件）: ±{2/math.sqrt(sum(OR[d] for d in rng('2026-11-16','2026-11-22'))):.0%}")
# ---- ③ 広告費 ÷ 日予算（その日の最後の日予算の合計＝翌日0時台の全体スナップショット）
SN = collections.defaultdict(dict)
for r in csv.DictReader(open('data/budget-snapshots.csv')): SN[r['snapshot_date']][(r['campaign'], r['adset'])] = int(r['daily_budget'])
nxt = lambda d: (datetime.date.fromisoformat(d) + datetime.timedelta(1)).isoformat()
WD = '月火水木金土日'; rows = []
for d in rng('2026-10-25', '2026-11-22'):
    s = SN.get(nxt(d))
    if not s or len(s) < 8: continue
    b = sum(s.values()); rows.append((d, WD[datetime.date.fromisoformat(d).weekday()], ACCT([d]), b))
P('■ ③ 広告費 ÷ 日予算の合計（その日の最後の日予算＝翌日0時台の記録。日中に予算を変えた日はずれる）')
byw = collections.defaultdict(list)
for d, w, a, b in rows: byw[w].append(a / b)
P('  曜日ごとの平均（10/25〜11/22）: ' + '・'.join(f'{w} {sum(byw[w])/len(byw[w]):.0%}（{len(byw[w])}日）' for w in '日月火水木金土' if byw[w]))
P('  日曜だけ: ' + '・'.join(f'{d[5:]} {a/b:.0%}' for d, w, a, b in rows if w == '日'))
P('  直近14日: ' + '・'.join(f'{d[5:]}{w} {a/b:.0%}' for d, w, a, b in rows[-14:]))
for lab, a_, b_ in (('11/15(日)〜11/21(土)', '2026-11-15', '2026-11-21'), ('11/8〜11/14', '2026-11-08', '2026-11-14'), ('11/1〜11/7', '2026-11-01', '2026-11-07')):
    rr = [x for x in rows if a_ <= x[0] <= b_]
    if len(rr) == 7: P(f'  週（日〜土）{lab}: 広告費 {sum(x[2] for x in rr):,.0f} ÷ 日予算の合計 {sum(x[3] for x in rr):,} ＝ {sum(x[2] for x in rr)/sum(x[3] for x in rr):.1%}')
# ---- ④ 商品のまとまりごとの7日（11/16〜22）
OUT = json.load(open('scripts/daily/o1122/an1123_out.json')); D7 = ALLD[-7:]
OLD4 = ('伸縮ガラスクリーナー', 'ナノガラス脱毛パッド', 'ワイド水切りワイパー', 'W固定スマホ車載ホルダー')
grp = collections.OrderedDict([('長く売っている4本（ガラス・ナノ・ワイパー・W固定）', [0, 0]), ('そのほかの広告を出した商品', [0, 0])])
for o in OUT:
    a7 = A(D7, o['n'])
    if not a7: continue
    k = list(grp)[0] if o['n'] in OLD4 else list(grp)[1]; grp[k][0] += o['p7']; grp[k][1] += a7
P('■ ④ 直近7日（11/16〜22）の利益と広告費')
for k, (p, a) in grp.items(): P(f'  {k}: 利益 {p:+,.0f}（{p/7:+,.0f}/日）・広告費 {a:,.0f}（{a/7:,.0f}/日）・倍率 {1+p/a:.2f}')
P(f"  カタログ全部（テスト）: 広告費 {g['CAT'](D7):,.0f}（{g['CAT'](D7)/7:,.0f}/日・商品に分けられない）")
P('  そのほかの中身（7日の利益・倍率）: ' + '・'.join(f"{o['n']} {o['p7']:+,.0f}（{o['m7']:.2f}）" for o in sorted(OUT, key=lambda o: -o['p7']) if o['n'] not in OLD4 and A(D7, o['n'])))
# ---- ⑤ フック v5
nm = lambda t: re.sub(r'【[^】]*】', '', t).replace('LOOTY', '', 1).strip()
IDN = {r[0]: nm(r[1]) for f in ('product_totals_1022_1120_raw.json', 'product_totals_0629_1120_raw.json') for r in json.load(open('scripts/daily/ic1121/aov/' + f))['rows'] if r[0]}
O7 = {IDN[r[0]]: int(r[1]) for r in json.load(open('scripts/daily/o1122/orders_7d_1116_1122_raw.json'))['rows'] if r[0] in IDN}
H = '高見えレザーヘッドレストフック'; rate = O7[H] / A(D7, H)
pois = lambda k, l: math.exp(-l + k * math.log(l) - math.lgamma(k + 1)); ple = lambda k, l: sum(pois(i, l) for i in range(k + 1))
def table(f):
    out = []
    for l in json.load(open(D0 + f))['data']['data'].split('\n')[1:]:
        l = l.strip()
        if l: out.append(l.split(','))
    return out
z = lambda x: 0 if x in ('null', '') else int(round(float(x)))
TC = {r[0]: [z(x) for x in r[1:]] for r in table('meta_camp_h11_1123_raw.json')}     # 今日 0〜11時台: cost, imp, clk, atc, purchase
a21, a22 = A(['2026-11-21'], H), A(['2026-11-22'], H); a23 = TC['高見えレザーヘッドレストフックv5'][0]
P(f'■ ⑤ フック v5: 直近7日（11/16〜22）の注文 {O7[H]}件 ÷ 広告費 {A(D7, H):,.0f} ＝ 1万円あたり {rate*1e4:.2f}件')
P(f'  11/22: 広告費 {a22:,.0f} → 見込み {a22*rate:.1f}件・実際 0件（0件になる確率 {ple(0, a22*rate):.0%}）')
P(f'  11/21〜22: 広告費 {a21+a22:,.0f} → 見込み {(a21+a22)*rate:.1f}件・実際 1件（1件以下 {ple(1, (a21+a22)*rate):.0%}）')
P(f'  今日 0〜11時台: 広告費 {a23:,}・注文 0（12:1x まで）→ 11/21〜今日11時台: 見込み {(a21+a22+a23)*rate:.1f}件・実際 1件（1件以下 {ple(1, (a21+a22+a23)*rate):.1%}）')
e3 = (a21 + a22 + 8000 * 1.1) * rate
P(f'  今日が終日 0件なら（広告費を 8,800 と置いた場合）: 3日の見込み {e3:.1f}件・実際 1件（1件以下 {ple(1, e3):.1%}）')
v5 = [d for d in ALLD if d >= '2026-11-18']; WIN['h5'] = v5; N, DC, Q, K = agg(v5, 'h5'); s5, k5, q5 = N.get(H, 0), K.get(H, 0), Q.get(H, 0); a5 = sum(g['AD']['高見えレザーヘッドレストフックv5'].get(d, 0) for d in v5)
P(f'  v5 の通算（11/18〜22・5日）: {q5}個・売上 {s5:,}・原価 {k5:,}・広告費 {a5:,.0f}・倍率 {(s5-k5)/a5:.2f}')
mu = (s5 - k5) / q5   # 1個あたりの粗利（通算の実績）
for lab, ad_rest in (('今日 8,800・明日 6,400（明日 −20% にした場合）', 8800 + 6400), ('今日 8,800・明日 8,800', 17600)):
    need = 1.25 * (a5 + ad_rest) - (s5 - k5)
    P(f'  7日（11/18〜24）で 1.25 に届くには（{lab}）: あと粗利 {need:,.0f}円 ＝ 約 {need/mu:.1f}個（1個の粗利 {mu:,.0f}円・2日で）')
# ---- ⑥ 新商品
P('■ ⑥ 新しく出した商品: 11/22 までの通算（終日の確定・暫定）／今日（広告は 0〜11時台・注文は 12:1x まで）')
O = {nm(r[0]): (int(r[1]), int(r[4])) for r in json.load(open(D0 + 'orders_by_product_1123_h12_raw.json'))['rows'] if r[0] and not r[0].startswith('VIP')}
for n, camp, start, price in (('360°マルチクリップ車載スマホホルダー', '360°マルチクリップ車載スマホホルダー', '2026-11-16', 3980), ('高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv5', '2026-11-18', 3980),
                              ('充電式ダブルミスト卓上加湿器', '充電式ダブルミスト卓上加湿器', '2026-11-19', 5980), ('コードレス毛玉クリーナー', 'コードレス毛玉クリーナーv2', '2026-11-22', 4980), ('UV歯ブラシ除菌器', 'UV歯ブラシ除菌器 v2', '2026-11-22', 8980)):
    ds = [d for d in ALLD if d >= start]; key = 'n' + n; WIN[key] = ds; N, DC, Q, K = agg(ds, key); a = sum(g['AD'][camp].get(d, 0) for d in ds); s, k, q = N.get(n, 0), K.get(n, 0), Q.get(n, 0)
    t = TC[camp]; o = O.get(n, (0, 0)); be = (price - g['COST'][n]) if n != '高見えレザーヘッドレストフック' else price - 732
    P(f"  {camp}（{start[5:]}〜・{len(ds)}日）: {q}個・広告費 {a:,.0f}・倍率 {(s-k)/a:.2f}・利益 {s-k-a:+,.0f}｜今日: 広告費 {t[0]:,}・クリック率 {t[2]/t[1]:.2%}・カート {t[3]}・注文 {o[0]}（{o[1]}個）｜1個の粗利（定価）{be:,}円")
# ---- ⑦ UV v2 のクリック
P('■ ⑦ UV歯ブラシ除菌器 v2 のクリック')
R = collections.defaultdict(lambda: [0, 0, 0])
for l in open('scripts/daily/o1122/ad_level_1026_1122.txt'):
    if l[0] == '#': continue
    d, c, a_, ad, cost, imp, clk = l.strip().split(',')
    if 'UV歯ブラシ' in c: x = R[(d, c)]; x[0] += int(cost); x[1] += int(imp); x[2] += int(clk)
for (d, c), x in sorted(R.items()): P(f'  {d[5:]} {c}: 広告費 {x[0]:,}・表示 {x[1]:,}・クリック {x[2]}・クリック率 {x[2]/x[1]:.2%}・CPM {x[0]/x[1]*1000:,.0f}・クリック1回 {x[0]/x[2]:,.0f}円')
u = TC['UV歯ブラシ除菌器 v2']; y = R[('2026-11-22', 'UV歯ブラシ除菌器 v2')]
P(f'  11-23 0〜11時台: 広告費 {u[0]:,}・表示 {u[1]:,}・クリック {u[2]}・クリック率 {u[2]/u[1]:.2%}・CPM {u[0]/u[1]*1000:,.0f}・クリック1回 {u[0]/u[2]:,.0f}円・カート {u[3]}・購入 {u[4]}（Shopify の注文 {O.get("UV歯ブラシ除菌器",(0,0))[0]}）')
c2, i2, k2 = y[0] + u[0], y[1] + u[1], y[2] + u[2]; p0 = k2 / i2; se = math.sqrt(p0 * (1 - p0) * (1 / y[1] + 1 / u[1])); zz = (u[2] / u[1] - y[2] / y[1]) / se
P(f'  2日の合計: 広告費 {c2:,}・表示 {i2:,}・クリック {k2}・クリック率 {k2/i2:.2%}（クリック {k2}件のぶれ ±{2/math.sqrt(k2):.0%}）・クリック1回 {c2/k2:,.0f}円。昨日 → 今日の差は z={zz:.1f}（2 を超えると偶然では起きにくい）')
st_cpc = new['cpc']; mg = 8980 - g['COST']['UV歯ブラシ除菌器']
macc = sum(int(l.split(',')[7]) for l in open('scripts/daily/o1122/meta_acct_daily_1004_1122.txt') if l[0] != '#' and '2026-11-16' <= l[:10] <= '2026-11-22') / sum(MA[d][2] for d in rng('2026-11-16', '2026-11-22'))
P(f'  店全体（11/16〜22）: クリック1回 {st_cpc:.0f}円・購入÷クリック（Meta 計上）{macc:.2%}')
P(f'  UV の1個の粗利 {mg:,}円 → 倍率 1.25 には 1個あたりの広告費 {mg/1.25:,.0f}円まで ＝ クリック1回 {c2/k2:,.0f}円なら クリック {mg/1.25/(c2/k2):.1f}回に1個（購入÷クリック {(c2/k2)/(mg/1.25):.1%}）が必要')
P(f'  クリック率が今の {k2/i2:.2%} から 2.5% になれば（CPM は同じとして）クリック1回 {c2/i2/0.025:,.0f}円 → 必要な購入÷クリックは {(c2/i2/0.025)/(mg/1.25):.1%}')
open(D0 + 'eff_1123.txt', 'w').write('\n'.join(L) + '\n')
