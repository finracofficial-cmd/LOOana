# -*- coding: utf-8 -*-
"""11/23「CVR・同時購入を最大限に」: 決済画面まで来て買わなかった記録（abandoned checkouts・直近100件＝11/15〜22）を、同じお客さんの注文と突き合わせる。
入力: abandoned_customers_1115_1122_raw.json（100件・お客さんの最後の注文の時刻つき）・abandoned_after_order_customers_raw.json（注文の直後に記録が出た32人の最後の注文の金額と決済方法）・abandoned_examples_raw.json（6件の中身）・payments_gateway_1115_1122_raw.json。メールアドレスなどは取っていない"""
import json, datetime, collections, os
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'
A = json.load(open(D0 + 'abandoned_customers_1115_1122_raw.json'))['data']['abandonedCheckouts']['nodes']
C = {n['id']: n['lastOrder'] for n in json.load(open(D0 + 'abandoned_after_order_customers_raw.json'))['data']['nodes']}
T = lambda s: datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
secs = collections.Counter(T(n['createdAt']).second for n in A)
P(f'■ 記録の時刻の「秒」: {dict(sorted(secs.items()))} ＝ 全部 0〜3秒か 30〜33秒（30秒おきの処理が記録を作っている。お客さんが決済画面を開いた時刻ではない）')
cat = collections.OrderedDict((k, []) for k in ('注文なし', '注文の直前に止めた決済（記録は注文の4〜10分後）', 'あとで注文した', '前に買った人（今回は買っていない）'))
for n in A:
    lo = n['customer']['lastOrder']; t = T(n['createdAt'])
    if lo is None: cat['注文なし'].append(n)
    else:
        d = (t - T(lo['createdAt'])).total_seconds() / 60
        cat['注文の直前に止めた決済（記録は注文の4〜10分後）' if 0 <= d <= 30 else ('あとで注文した' if d < 0 else '前に買った人（今回は買っていない）')].append((n, d))
P(f'■ 直近100件（{A[-1]["createdAt"][:10]}〜{A[0]["createdAt"][:10]} UTC）の内訳: ' + '・'.join(f'{k} {len(v)}件' for k, v in cat.items()))
gap = sorted(round(d) for n, d in cat['注文の直前に止めた決済（記録は注文の4〜10分後）'])
P(f'  注文から記録までの分: {gap}（10分を超えるものが無い＝「最後に触ってから10分」で記録になり、最後に触ったのは注文の0〜6分前）')
# 止めた決済の金額 と 実際の注文の金額
per = {}
for n, d in cat['注文の直前に止めた決済（記録は注文の4〜10分後）']:
    cid = n['customer']['id']; per.setdefault(cid, []).append(float(n['totalPriceSet']['shopMoney']['amount']))
kinds = collections.Counter(); diff = 0; ex = []
for cid, tots in per.items():
    o = float(C[cid]['currentTotalPriceSet']['shopMoney']['amount']); m = max(tots)
    k = '止めた決済のほうが高い（2個→1個など）' if m > o + 1 else ('同じ金額' if abs(m - o) <= 1 else '止めた決済のほうが安い')
    kinds[k] += 1
    if m > o + 1: diff += m - o; ex.append((int(o), int(m)))
P(f'■ 注文の直前に止めた決済があった {len(per)}人: ' + '・'.join(f'{k} {v}人' for k, v in kinds.items()))
P(f'  「高い決済を止めて安く買った」人の 注文額 → 止めた決済の額: {collections.Counter(ex).most_common()}・差の合計 {diff:,.0f}円')
gw = collections.Counter(C[cid]['paymentGatewayNames'][0] for cid in per)
allgw = {r[0]: int(r[1]) for r in json.load(open(D0 + 'payments_gateway_1115_1122_raw.json'))['rows']}
P(f'  その注文の決済方法: {dict(gw)}｜同じ期間の全部の決済: {allgw}')
days = (T(A[0]['createdAt']) - T(A[-1]['createdAt'])).total_seconds() / 86400; orders = sum(allgw.values())
dn = kinds['止めた決済のほうが高い（2個→1個など）']
P(f'  期間 {days:.1f}日・決済 {orders}件 → 「高い決済を止めて安く買った」は {dn}人（注文の {dn/orders:.1%}・{dn/days:.1f}人/日）。全員が止めた決済のまま買っていたら 売上 +{diff:,.0f}円（{diff/days:,.0f}円/日）')
no = cat['注文なし']; ppl = {n['customer']['id'] for n in no}
P(f'■ 注文なし {len(no)}件・{len(ppl)}人（{len(ppl)/days:.1f}人/日）: 住所まで入れた {sum(1 for n in no if n["shippingAddress"])}件・メールを送ってよい人 {sum(1 for n in no if n["customer"]["defaultEmailAddress"] and n["customer"]["defaultEmailAddress"]["marketingState"]=="SUBSCRIBED")}件・送れない人 {sum(1 for n in no if not (n["customer"]["defaultEmailAddress"] and n["customer"]["defaultEmailAddress"]["marketingState"]=="SUBSCRIBED"))}件')
P('■ 中身の例（abandoned_examples_raw.json）')
E = json.load(open(D0 + 'abandoned_examples_raw.json'))['data']
for a in E['ab']:
    P(f"  止めた決済 {a['createdAt'][5:16]}: " + ' ＋ '.join(f"{l['variantTitle'] or '（種類なし）'}×{l['quantity']}＝{float(l['discountedTotalPriceSet']['shopMoney']['amount']):,.0f}円（定価 {float(l['originalTotalPriceSet']['shopMoney']['amount']):,.0f}）" for l in a['lineItems']['nodes']) + f"｜合計 {float(a['totalPriceSet']['shopMoney']['amount']):,.0f}")
for o in E['orders']['nodes']:
    P(f"  注文 {o['name']} {o['createdAt'][5:16]}: " + ' ＋ '.join(f"{l['variantTitle'] or '（種類なし）'}×{l['quantity']}＝{float(l['discountedTotalSet']['shopMoney']['amount']):,.0f}円" for l in o['lineItems']['nodes']) + f"｜合計 {float(o['currentTotalPriceSet']['shopMoney']['amount']):,.0f}")
open(D0 + 'downgrade_1123.txt', 'w').write('\n'.join(out) + '\n')
# ---- 止めた決済の中身の形（行の数量）: 2つの取得は同じ100件・同じ順なので時刻で突き合わせる
L = json.load(open(D0 + 'abandoned_lines_1115_1122_raw.json'))['data']['abandonedCheckouts']['nodes']
assert [n['createdAt'] for n in L] == [n['createdAt'] for n in A]
def shape(n):
    q = [l['quantity'] for l in n['lineItems']['nodes']]; tot = float(n['totalPriceSet']['shopMoney']['amount'])
    if len(q) == 1: return '1行（%d個）' % q[0]
    if len(q) == 2 and sorted(q) == [1, 1]: return '1個ずつ2行'
    if len(q) == 2 and sorted(q) == [1, 2]: return 'VIP特典＋同じ種類2個（か 1個＋2個）'
    return '3行以上'
out2 = []
def P2(*x):
    s = ' '.join(str(i) for i in x); print(s); out2.append(s)
down = set(); same = set()
for cid, tots in per.items():
    o = float(C[cid]['currentTotalPriceSet']['shopMoney']['amount']); (down if max(tots) > o + 1 else same).add(cid)
P2('■ 止めた決済の形')
for lab, pick in (('高い決済を止めて安く買った人の、止めた決済', lambda n, a: a['customer']['id'] in down and a['customer']['lastOrder'] and 0 <= (T(a['createdAt']) - T(a['customer']['lastOrder']['createdAt'])).total_seconds() / 60 <= 30),
                  ('同じ金額で買った人の、止めた決済', lambda n, a: a['customer']['id'] in same and a['customer']['lastOrder'] and 0 <= (T(a['createdAt']) - T(a['customer']['lastOrder']['createdAt'])).total_seconds() / 60 <= 30),
                  ('注文なしの人の決済', lambda n, a: a['customer']['lastOrder'] is None)):
    c = collections.Counter(shape(n) for n, a in zip(L, A) if pick(n, a)); P2(f'  {lab}: {dict(c)}')
open(D0 + 'downgrade_1123.txt', 'a').write('\n'.join(out2) + '\n')
