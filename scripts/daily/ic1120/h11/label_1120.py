# -*- coding: utf-8 -*-
"""11/20 12時台 「在庫セール表記でも売れてるよなあ」: 今朝（0〜10時台）を商品名の表記で分けて数えるだけ。入力は raw.txt。
表記は 11:35 の商品別クエリ（FROM sales … GROUP BY product_title）に出た商品名の先頭から。商品が違うので、表記の効き目の比較にはならない"""
import os, re, math
D0 = os.path.dirname(os.path.abspath(__file__))
LABEL = {'在庫セール': ['高見えレザーヘッドレストフック', '360°マルチクリップ車載スマホホルダー', '充電式ダブルミスト卓上加湿器', 'ナノガラス脱毛パッド'],
         '本日終了': ['伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', 'スマートノーズEMS美顔器', '4-in-1マルチクリーナー', '快適マジックインソール', 'マグネットドアクッション', 'ワイド水切りワイパー', '携帯電動シェーバー']}
PD = {}; C = {}
for l in open(os.path.join(D0, 'raw.txt')):
    p = l.strip().split(',')
    if p[0] == 'PD' and p[1] == '2026-11-20': PD[p[2]] = [int(x) for x in p[3:]]
    elif p[0] == 'C': C[re.sub(r'\s*v\d+$', '', p[1]).strip()] = int(p[2])
out = []; tot = 0
for lab, names in LABEL.items():
    o = sum(PD.get(n, [0])[0] for n in names); s = sum(PD.get(n, [0, 0, 0])[1] - PD.get(n, [0, 0, 0])[2] for n in names); ad = sum(C[n] for n in names); tot += s
    out.append(f'{lab}: {len(names)}商品・注文 {o}件・売上（値引後） {s:,}・広告費 {ad:,}・売上÷広告費 {s/ad:.2f}')
    for n in names:
        v = PD.get(n, [0, 0, 0, 0]); out.append(f'   {n}: {v[0]}件（{v[3]}個）・{v[1]-v[2]:,}・{C[n]:,}・{(v[1]-v[2])/C[n]:.2f}')
assert tot == sum(v[1] - v[2] for v in PD.values()) and set(sum(LABEL.values(), [])) | {'カタログ全部（テスト）'} == set(C)
open(os.path.join(D0, 'label_1120.txt'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
