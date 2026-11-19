# -*- coding: utf-8 -*-
"""11/19 「広告に依存してるじゃん？これをオーガニックでも増やしたい」: 広告から来た購入の割合・広告以外の入口の大きさと、検索が広告の量に連れて動くか（月別）"""
import json
R = json.load(open('raw.json'))
U = R['utm']; tot = sum(c for *_, s, c in U); paid = sum(c for a, m, s, c in U if m == 'paid')
print(f'30日（10/20〜11/18）の購入完了の来訪 {tot}: 広告（utm_medium=paid）{paid}（{paid/tot:.1%}）・それ以外 {tot-paid}（{(tot-paid)/tot:.1%}）')
for a, m, s, c in U:
    if m != 'paid' and s >= 10: print(f'  {a or "（utm なし）"} / {m or "—"}: 来訪 {s:,}・購入 {c}・購入率 {c/s:.1%}')
o = sum(x[1] for x in R['ref']); print('注文の入口（order_referrer_source）: ' + '・'.join(f'{k or "直接/不明"} {n}（{n/o:.1%}）' for k, n, *_ in R['ref']))
n, r = R['nr']; print(f'リピート: 注文 {r[1]}／{n[1]+r[1]}（{r[1]/(n[1]+r[1]):.1%}）・売上 {r[2]-r[3]:,}（{(r[2]-r[3])/(n[2]-n[3]+r[2]-r[3]):.1%}）')
M = {}
for m, k, s, c in R['month']: M.setdefault(m, {})[k] = (s, c)
print('月別（11月は18日）: SNS来訪・検索来訪（SNS比）・検索からの購入・直接来訪（SNS比）・メール来訪')
for m in sorted(M):
    so, se, di, em = M[m].get('social', (0, 0)), M[m].get('search', (0, 0)), M[m].get('direct', (0, 0)), M[m].get('email', (0, 0))
    print(f'  {m}: SNS {so[0]:,} ／ 検索 {se[0]:,}（{se[0]/so[0]:.2%}）購入 {se[1]}（購入率 {se[1]/se[0]:.1%}）／ 直接 {di[0]:,}（{di[0]/so[0]:.0%}）／ メール {em[0]}')
e = R['email_peak']; print(f"メール（Shopify Email）10/28〜11/2: 来訪 {sum(x[1] for x in e)}・購入 {sum(x[2] for x in e)}（{sum(x[2] for x in e)/sum(x[1] for x in e):.1%}）")
print(f"VIP1000（次回1,000円OFF）の使用 10/1〜11/18: {dict(R['code']).get('VIP1000')} 件")
