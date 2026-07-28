# -*- coding: utf-8 -*-
"""実験レジストリ: data/budget-snapshots.csv の日次差分から予算実験を自動導出する。
手作業のEXP辞書が単一の誤り源だった（2026-07-28: P1窓とデータ被覆のズレで誤判定）ため、
変更検知・P1/P2窓・判定日・V1〜V10ガードをすべてここから機械生成する。
使い方: python3 scripts/experiments.py [基準日 YYYY-MM-DD]"""
import csv, sys, datetime, collections

HOLIDAYS = {'2026-07-20'}          # 祝日・天候ショック日はここに追記（V6/V10）
MIN_DELTA = 3000                    # V1: 円/日
JUDGE_AFTER_DAYS = 3                # 変更からN日後を判定日にする（P2に3クリーン日を確保）

def load(path='data/budget-snapshots.csv'):
    daily = collections.defaultdict(lambda: collections.defaultdict(int))
    for r in csv.reader(open(path)):
        if len(r) >= 4 and r[0][:4].isdigit():
            daily[r[0]][r[1]] += int(r[3])   # キャンペーン単位に合算
    return daily

def experiments(asof=None):
    daily = load()
    days = sorted(daily)
    if asof: days = [d for d in days if d <= asof]
    out = []
    prev = None
    for d in days:
        if prev is not None:
            camps = set(daily[d]) | set(daily[prev])
            for c in camps:
                b0, b1 = daily[prev].get(c, 0), daily[d].get(c, 0)
                if b0 != b1 and b0 and b1:
                    out.append({'campaign': c, 'date': d, 'from': b0, 'to': b1,
                                'dir': '増額' if b1 > b0 else '減額'})
        prev = d
    # 同一キャンペーンは最新の変更のみが有効な実験（S1b③: 実験消費）
    latest = {}
    for e in out: latest[e['campaign']] = e
    res = []
    for e in latest.values():
        chg = datetime.date(*map(int, e['date'].split('-')))
        p2 = []
        dt = chg
        while len(p2) < 4:
            if dt.isoformat() > days[-1]: break
            if dt.isoformat() not in HOLIDAYS: p2.append(dt.isoformat())
            dt += datetime.timedelta(days=1)
        p1 = []
        dt = chg - datetime.timedelta(days=1)
        while len(p1) < 4 and dt.isoformat() >= days[0]:
            if dt.isoformat() not in HOLIDAYS: p1.append(dt.isoformat())
            dt -= datetime.timedelta(days=1)
        e['P1'] = sorted(p1); e['P2'] = p2
        e['判定日'] = (chg + datetime.timedelta(days=JUDGE_AFTER_DAYS)).isoformat()
        e['V1目安'] = abs(e['to'] - e['from']) >= MIN_DELTA
        res.append(e)
    return sorted(res, key=lambda x: x['date'], reverse=True)

if __name__ == '__main__':
    asof = sys.argv[1] if len(sys.argv) > 1 else None
    for e in experiments(asof):
        print(f"{e['date']}  {e['campaign'][:26]:28s} {e['from']:>7,}→{e['to']:>7,} ({e['dir']}) "
              f"判定日{e['判定日'][5:]}  P1={[x[5:] for x in e['P1']]} P2={[x[5:] for x in e['P2']]} "
              f"{'V1:OK' if e['V1目安'] else 'V1:設定差<3,000→測定不能見込み'}")
    print('\n※広告費の実測Δ・購入件数(V9)・データ被覆(V5)は日次ビルドで検証する。祝日・天候日はHOLIDAYSに追記')
