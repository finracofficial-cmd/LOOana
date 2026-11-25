# -*- coding: utf-8 -*-
"""11/25「LOOTYで過去だしたもので復活して売れそうなものアルケ？」（11/24 の表を 11/24 まで延ばし、直近14日の広告なしの個数を足した）: 6/29〜11/24 に広告費があった全商品の、広告を出した日だけの数字。
入力: w1124.py（売上・原価・広告費の積み直し）。バリエーションで原価が違う商品（ナノ・ディスペンサー）の日別の内訳が 7/17 からなので、7/17〜11/24 で見る（それより前に出して止めた商品は途中から）。広告を出していない日の売上は ⑤ で別に数える。種類（車まわり等）と季節は Claude の判断"""
import io, contextlib, collections, csv, datetime, json
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1124.py').read(), g)
A, ALLD, agg, WIN, MAP, MULTI, PRICE = g['A'], g['ALLD'], g['agg'], g['WIN'], g['MAP'], g['MULTI'], g['PRICE']
camps = lambda n: MULTI.get(n, (MAP.get(n, n),))
ALLD = [d for d in ALLD if d >= '2026-07-17']
names = sorted({n for n in set(PRICE) | set(MAP) | set(MULTI) if any(A([d], n) for d in ALLD)})
DAY = {}
for d in ALLD:
    WIN['d' + d] = [d]; N1, D1, Q1, K1 = agg([d], 'd' + d); DAY[d] = (N1, K1)
def gp_day(n, d): N1, K1 = DAY[d]; return N1.get(n, 0) - K1.get(n, 0)
rows = []
for n in names:
    ds = [d for d in ALLD if A([d], n) > 0]
    a = [A([d], n) for d in ds]; p = [gp_day(n, d) for d in ds]
    def win(ix): aa = sum(a[i] for i in ix); return sum(p[i] for i in ix) / aa if aa else 0
    best = max(win(range(i, i + 7)) for i in range(max(1, len(ds) - 6))) if len(ds) >= 7 else win(range(len(ds)))
    last = ds[-1]; rest = (datetime.date(2026, 11, 24) - datetime.date.fromisoformat(last)).days
    noad = [d for d in ALLD if d >= '2026-10-25' and not A([d], n)]
    WIN['na' + n] = noad; Nn, Dn, Qn, Kn = agg(noad, 'na' + n) if noad else ({}, {}, {}, {})
    q30 = Qn.get(n, 0)
    noad14 = [d for d in noad if d >= '2026-11-11']
    WIN['nb' + n] = noad14; Nb, Db, Qb, Kb = agg(noad14, 'nb' + n) if noad14 else ({}, {}, {}, {})
    q14 = Qb.get(n, 0)
    rows.append(dict(n=n, first=ds[0], last=last, days=len(ds), ad=sum(a), gp=sum(p), m=sum(p) / sum(a), m7a=win(range(min(7, len(ds)))), best=best,
                     m7z=win(range(max(0, len(ds) - 7), len(ds))), rest=rest, noad=q30, noad14=q14, noad14days=len(noad14), price=PRICE.get(n)))
json.dump(rows, open('scripts/daily/ic1125/blanket/stopped_1125.json', 'w'), ensure_ascii=False, indent=1)
print('商品（7/17〜11/24）: 最初〜最後に広告を出した日（日数）｜広告費・利益・通算の倍率｜最初の7日・いちばん良い7日・最後の7日｜止めてからの日数（11/24 まで）｜10/25〜11/24 の広告なしの日の個数（うち 11/11〜24・その日数）｜売価')
for r in sorted(rows, key=lambda r: -(r['gp'] - r['ad'])):
    st = '配信中' if r['last'] == '2026-11-24' else f"止めて{r['rest']}日"
    print(f"  {r['n']}: {r['first'][5:]}〜{r['last'][5:]}（{r['days']}日）｜{r['ad']:,.0f}・{r['gp']-r['ad']:+,.0f}・{r['m']:.2f}｜{r['m7a']:.2f}・{r['best']:.2f}・{r['m7z']:.2f}｜{st}｜広告なし {r['noad']}個（{r['noad14']}個／{r['noad14days']}日）｜{r['price']}")
