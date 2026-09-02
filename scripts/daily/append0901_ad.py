# -*- coding: utf-8 -*-
"""2026-09-01 の広告費をCSVへ追記。health_check(8/03-9/01実測) − CSV(8/03-8/31実測) の差。
   窓の検証: むくみ取りかっさ（8/23開始）CSV 86,010 / HC 97,836 → 9/1 = 11,826円。
   ビジュアル耳かきは8/31停止のため 9/1 = 0円（AD行なし）。"""
import csv
D = '2026-09-01'
AD = [('ナノガラス脱毛パッド',77091),('W固定スマホ車載ホルダー',33740),('快適マジックインソール',30140),
      ('カタログ全部（テスト）',17269),('ムダ毛シェーバー',16359),('姿勢サポートチェア',11953),
      ('バランスケアスリッパ',11882),('むくみ取りかっさ',11826),('2WAYシートボックス',7417),
      ('ナノバブルシャワーヘッド',7285),('完全遮光・接触冷感UVハット',5677),('偏光・調光サングラス',124)]
TOT = sum(v for _, v in AD); assert TOT == 230763, TOT
p = 'data/daily/daily_ad.csv'
with open(p, encoding='utf-8') as f:
    assert not any(r and r[0] == D for r in csv.reader(f)), f'{D} が既にある'
with open(p, 'a', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    for c, v in AD: w.writerow([D, c, v])
print(f'{p} に {len(AD)}行 追記 ／ 9/1 広告費合計 {TOT:,}円')
print('⚠️ 偏光・調光サングラス 124円（前日151円に続き2日連続でほぼゼロ）＝Metaが配信をやめた')
