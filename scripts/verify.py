# -*- coding: utf-8 -*-
"""データ検証ガード。分析スクリプトを書く前に必ずこれを通す。

使い方:
  python3 scripts/verify.py                    # CSVのカバー範囲を表示
  python3 scripts/verify.py 2026-06-08 2026-07-31   # その期間が使えるか判定

目的:
  2026-08-01のミス（ナノガラスのShopify週次売上を、クエリせずにスクリプトへ
  直接書き込んだ）を二度と起こさないための機械的ガード。

原則:
  1. 分析スクリプトに実測値をリテラルで埋め込まない
  2. 数値は必ず data/daily/*.csv から読む
  3. CSVのカバー範囲外の期間を分析しない。必要なら先に取得してCSVに追記し、
     追記後に必ず別クエリで合計を突き合わせる（transcribe検算）
"""
import csv, sys, collections, datetime

SALES = 'data/daily/daily_sales.csv'
AD    = 'data/daily/daily_ad.csv'

def load(path, keycol):
    rows = list(csv.DictReader(open(path, encoding='utf-8')))
    dates = sorted({r['date'] for r in rows})
    return rows, dates

def coverage():
    s_rows, s_dates = load(SALES, 'name')
    a_rows, a_dates = load(AD, 'campaign')
    return {
        'sales': (s_dates[0], s_dates[-1], len(s_dates), len(s_rows)),
        'ad':    (a_dates[0], a_dates[-1], len(a_dates), len(a_rows)),
        's_dates': set(s_dates), 'a_dates': set(a_dates),
    }

def daterange(a, b):
    x = datetime.date.fromisoformat(a); y = datetime.date.fromisoformat(b); out = []
    while x <= y:
        out.append(x.isoformat()); x += datetime.timedelta(days=1)
    return out

def main():
    c = coverage()
    print('=== CSVカバー範囲（これが唯一の実測データ源）===')
    print('  daily_sales.csv : %s 〜 %s（%d日・%d行）' % c['sales'])
    print('  daily_ad.csv    : %s 〜 %s（%d日・%d行）' % c['ad'])
    if len(sys.argv) < 3:
        print()
        print('※ この範囲外の期間を分析してはいけない。')
        print('   範囲外が必要なら: ①ツールで取得 → ②CSVに追記 → ③別クエリで合計を突合 → ④分析')
        return 0
    a, b = sys.argv[1], sys.argv[2]
    need = daterange(a, b)
    ms = [d for d in need if d not in c['s_dates']]
    ma = [d for d in need if d not in c['a_dates']]
    print()
    print('=== 要求期間 %s 〜 %s（%d日）===' % (a, b, len(need)))
    if not ms and not ma:
        print('  ✅ 全日カバー済み。CSVから読んで分析してよい')
        return 0
    if ms: print('  🚨 daily_sales.csv に無い日: %d日（%s 〜 %s）' % (len(ms), ms[0], ms[-1]))
    if ma: print('  🚨 daily_ad.csv に無い日: %d日（%s 〜 %s）' % (len(ma), ma[0], ma[-1]))
    print()
    print('  → この期間で分析してはいけない。先に取得してCSVへ追記すること。')
    print('  → 数字をスクリプトに直接書くのは禁止（2026-08-01のミスの原因）')
    return 1

if __name__ == '__main__':
    sys.exit(main())
