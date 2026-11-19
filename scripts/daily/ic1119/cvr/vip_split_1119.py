# 11/19 VIP特典（0円の行）を入れ始めた前後で、1注文あたりの個数と値引きの割合が変わったか（ナノ・店全体）
# 入力: vip_split_raw.json（ShopifyQL の結果そのまま）。VIP特典の商品は 10/3 と 10/8 に作られた → 前＝8/31〜10/4 の5週、後＝10/5〜11/18
import json, os
D = json.load(open(os.path.join(os.path.dirname(__file__), 'vip_split_raw.json')))
def agg(rows, lo, hi):
    o = g = d = q = 0
    for wk, orders, gross, disc, qty in rows:
        if lo <= wk <= hi: o += int(orders); g += int(gross); d += -int(disc); q += int(qty)
    return o, g, d, q
out = []
for name, key in (('ナノガラス脱毛パッド', 'nano'), ('店全体（VIP特典の行は除く）', 'store')):
    out.append(f'■ {name}')
    out.append('  週の初日   注文  個数  個数÷注文  値引き÷売上')
    for wk, orders, gross, disc, qty in D[key]:
        out.append(f'  {wk}  {int(orders):4d}  {int(qty):4d}   {int(qty)/int(orders):.3f}     {-int(disc)/int(gross)*100:.2f}%')
    for label, lo, hi in (('前（8/31〜10/4）', '2026-08-31', '2026-09-28'), ('後（10/5〜11/18）', '2026-10-05', '2026-11-16')):
        o, g, d, q = agg(D[key], lo, hi)
        out.append(f'  {label}: 注文 {o}・個数 {q}・個数÷注文 {q/o:.3f}・値引き÷売上 {d/g*100:.2f}%')
out.append('')
out.append('VIP特典の商品（2つ）: どちらも 0円・「配送が必要」・在庫の場所は 新潟県阿賀野市里888-1。商品（ナノ）の在庫の場所は cjdropshipping')
out.append(f"  カートに入った回数の目安（在庫の数字のマイナス）: {-D['vip_products'][0]['available']} + {-D['vip_products'][1]['available']} = {-D['vip_products'][0]['available'] - D['vip_products'][1]['available']}")
out.append('決済画面（checkout_two.txt）: 2個（VIP特典の行あり）＝「ご注文の商品は2個の荷物でお届けします」「3個のアイテム」／1個（行なし）＝この文は出ない・「1個のアイテム」')
open(os.path.join(os.path.dirname(__file__), 'vip_split_1119.txt'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
