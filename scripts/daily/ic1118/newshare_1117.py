# -*- coding: utf-8 -*-
"""11/18 「昨日の悪い原因はカート率。これも新商品の割合が低かったから？」
①日ごとの広告費のうち「出して（出し直して）14日以内の商品」に使った割合（data/daily/daily_ad.csv）
②11/17 の入口ページ別の来訪の内訳に、各ページの 11/3〜16 のカート率を当てた期待（＝顔ぶれだけで決まるカート率）と、11/3〜16 の実際を比べる（o1117/landing_1117_raw.json）"""
import csv, json, collections, datetime
START = {  # 出した日（出し直しは新しいキャンペーンの開始日）。daily_ad.csv のキャンペーン名で
 '伸縮ワックス洗車ブラシ': '2026-10-23', 'マグネットドアクッション': '2026-10-31', 'ワイド水切りワイパー': '2026-11-04', 'クリアビューレインガードフィルム': '2026-11-05',
 '防風あったか裏起毛パンツ': '2026-11-11', '2WAYシートボックス': '2026-11-11', '3WAY着る電気ブランケット': '2026-11-13', 'スマートノーズEMS美顔器v2': '2026-11-14', '携帯電動シェーバーv2': '2026-11-14',
 '高見えレザーヘッドレストフックv2': '2026-11-15', '高見えレザーヘッドレストフックv3': '2026-11-16', '高見えレザーヘッドレストフックv4': '2026-11-16', '快適マジックインソールv2': '2026-11-16', '快適マジックインソール v3': '2026-11-16',
 '360°マルチクリップ車載スマホホルダー': '2026-11-16', '裏起毛タッチ防寒グローブ': '2026-11-17', 'ポータブルヒートシーラー': '2026-10-12', 'コードレスダブルミスト加湿器': '2026-10-20', '高見えレザードアポケット': '2026-10-22',
 'UV歯ブラシ除菌器': '2026-11-12', 'すき間収納シートポケット': '2026-11-12'}
AD = collections.defaultdict(dict)
for r in csv.DictReader(open('data/daily/daily_ad.csv')): AD[r['date']][r['campaign']] = AD[r['date']].get(r['campaign'], 0) + float(r['cost'])
print('■ 広告費のうち、出して（出し直して）14日以内の商品の割合（カタログは除く）')
for d in sorted(AD):
    if d < '2026-11-03': continue
    tot = sum(v for c, v in AD[d].items() if not c.startswith('カタログ'))
    new = sum(v for c, v in AD[d].items() if c in START and 0 <= (datetime.date.fromisoformat(d) - datetime.date.fromisoformat(START[c])).days <= 13)
    print(f'  {d[5:]}: {new/tot*100:.0f}%（{new:,.0f}／{tot:,.0f}）')
L = json.load(open('scripts/daily/o1117/landing_1117_raw.json'))
A = {r[0]: [int(x) for x in r[1:]] for r in L['rows17']}; B = {r[0]: [int(x) for x in r[1:]] for r in L['rowsb']}
ks = [k for k in A if k in B]
base = sum(B[k][1] for k in ks) / sum(B[k][0] for k in ks)
exp = sum(A[k][0] * B[k][1] / B[k][0] for k in ks) / sum(A[k][0] for k in ks)
act = sum(A[k][1] for k in ks) / sum(A[k][0] for k in ks)
print(f'■ 入口ページ別（過去のある {len(ks)} ページ）: 11/3〜16 の実際のカート率 {base*100:.2f}%／11/17 の来訪の内訳に各ページのふだんの率を当てた期待 {exp*100:.2f}%（顔ぶれの分 {exp/base-1:+.0%}）／11/17 の実際 {act*100:.2f}%（同じページの中で下がった分 {act/exp-1:+.0%}）')
