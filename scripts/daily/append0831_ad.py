# -*- coding: utf-8 -*-
"""2026-08-31 の広告費をCSVへ追記。health_check(8/02-8/31実測) − CSV(8/02-8/30実測) の差。
   窓の検証: ビジュアル耳かき（8/28開始）CSV 20,554 / HC 26,408 → 8/31 = 5,854円。"""
import csv
D = '2026-08-31'
AD = [('ナノガラス脱毛パッド',70197),('W固定スマホ車載ホルダー',32612),('快適マジックインソール',26154),
      ('カタログ全部（テスト）',17032),('ムダ毛シェーバー',15944),('むくみ取りかっさ',11515),
      ('姿勢サポートチェア',10968),('バランスケアスリッパ',10135),('2WAYシートボックス',9975),
      ('ナノバブルシャワーヘッド',7461),('ビジュアル耳かき',5854),('完全遮光・接触冷感UVハット',5484),
      ('偏光・調光サングラス',151)]
TOT = sum(v for _, v in AD); assert TOT == 223482, TOT
p = 'data/daily/daily_ad.csv'
with open(p, encoding='utf-8') as f:
    assert not any(r and r[0] == D for r in csv.reader(f)), f'{D} が既にある'
with open(p, 'a', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    for c, v in AD: w.writerow([D, c, v])
print(f'{p} に {len(AD)}行 追記 ／ 8/31 広告費合計 {TOT:,}円')
print('⚠️ 偏光・調光サングラスが 151円（日予算5,000の3.0%）＝実質配信停止。要確認')
