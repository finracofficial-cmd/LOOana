# -*- coding: utf-8 -*-
"""11/25 18時台「低い水準を高くするためには？」: 新しい商品がどれだけ入ってきているか（お店に登録した日）と、登録済みでまだ広告を出していない商品があるか。
入力: products_all_1805_raw.json（Shopify の全商品・登録日・状態・値段・原価）／data/daily/daily_ad.csv（広告費）／../blanket/stopped_1125.json（広告を出した日だけの倍率）
車まわりかどうかは商品名からの Claude の判断（plan_1123.py と同じ分け方）"""
import json, re, csv, collections, datetime
B = 'scripts/daily/ic1125/pipeline/'
P = json.load(open(B + 'products_all_1805_raw.json', encoding='utf-8'))['data']['products']['nodes']
nm = lambda t: re.sub(r'【[^】]*】', '', t).replace('LOOTY', '', 1).strip()
CAR = ('車載', 'シートボックス', 'シートポケット', 'ドアポケット', 'ドアクッション', 'ワイパー', 'ガラスクリーナー', 'レインガード', '洗車', 'ヘッドレスト')
ad = collections.Counter()
for r in csv.DictReader(open('data/daily/daily_ad.csv', encoding='utf-8')): ad[re.sub(r'\s*v\d+$', '', r['campaign']).strip()] += float(r['cost'])
st = {r['n']: r for r in json.load(open('scripts/daily/ic1125/blanket/stopped_1125.json', encoding='utf-8'))}
rows = []
for p in P:
    v = p['variants']['nodes'][0]; price = float(v['price']); cost = float(v['inventoryItem']['unitCost']['amount']) if v['inventoryItem']['unitCost'] else None
    if price < 1000 or '(コピー)' in p['title'] or p['status'] in ('DRAFT', 'ARCHIVED', 'UNLISTED'): continue
    n = nm(p['title']); d = (datetime.datetime.fromisoformat(p['createdAt'].replace('Z', '+00:00')) + datetime.timedelta(hours=9)).date().isoformat()
    a = max([v2 for k, v2 in ad.items() if k and (k in n or n in k)] or [0]); s = next((r for k, r in st.items() if k in n or n in k), None)
    rows.append(dict(n=n, d=d, price=price, cost=cost, car=any(k in n for k in CAR), ad=a, m=s['m'] if s else None, gp=(s['gp'] - s['ad']) if s else None))
print(f'■ ① 公開中の商品 {len(rows)}本・うち車まわり {sum(r["car"] for r in rows)}本。広告費（6/29〜11/24）が 3,000円未満＝まだ試していない商品:')
un = [r for r in rows if r['ad'] < 3000]
for r in sorted(un, key=lambda r: r['d'], reverse=True): print(f"  {r['d']} {r['n']}｜{r['price']:,.0f}円・原価 {r['cost']:,.0f}（{r['cost'] / r['price']:.0%}）・車まわり {'○' if r['car'] else '×'}・広告費 {r['ad']:,.0f}")
print(f"  → 車まわりで未テストの商品: {sum(r['car'] for r in un)}本")
print('■ ② お店に登録した日ごとの新商品（10/1 以降・公開中のもの）')
new = sorted([r for r in rows if r['d'] >= '2026-10-01'], key=lambda r: r['d'])
for a, b, lab in (('2026-10-01', '2026-10-19', '10/1〜19'), ('2026-10-20', '2026-11-05', '10/20〜11/5'), ('2026-11-06', '2026-11-19', '11/6〜19'), ('2026-11-20', '2026-11-25', '11/20〜25')):
    w = [r for r in new if a <= r['d'] <= b]; days = (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days + 1
    hit = [r for r in w if r['gp'] is not None and r['gp'] >= 50000]
    print(f"  {lab}（{days}日）: {len(w)}本・うち車まわり {sum(r['car'] for r in w)}本・利益5万円以上 {len(hit)}本（{'・'.join(r['n'] for r in hit) or 'なし'}）")
    print('      ' + '・'.join(f"{r['d'][5:]} {r['n']}{'（車）' if r['car'] else ''} {('%.2f' % r['m']) if r['m'] is not None else '—'}" for r in w))
last = max(r['d'] for r in rows); lastcar = max(r['d'] for r in rows if r['car'])
print(f"  いちばん新しい登録: {last}・車まわりでは {lastcar}")
print('■ ③ 車まわりの商品の原価の割合と通算（広告を出した日だけ・7/17〜11/24）')
for r in sorted([r for r in rows if r['car']], key=lambda r: -(r['gp'] or -1e9)):
    print(f"  {r['n']}: {r['price']:,.0f}円・原価 {r['cost']:,.0f}（{r['cost'] / r['price']:.0%}）・倍率 {('%.2f' % r['m']) if r['m'] is not None else '—'}・利益 {format(r['gp'], '+,.0f') if r['gp'] is not None else '—'}")
print('■ ④ 原価が売値の25%までの線: ' + '・'.join(f'{p:,}円 → {p * 0.25:,.0f}円まで' for p in (3980, 4980, 5980, 6980)))
