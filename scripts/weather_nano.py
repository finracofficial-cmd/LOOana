"""ナノガラス脱毛パッドの日別個数と気温の照合（参考データ。判定ルール5dは変えない）
気温: Open-Meteo archive（47都道府県庁所在地）をナノの注文分布（8/1〜10/29 shipping_region）で加重平均
使い方: python3 scripts/weather_nano.py [終了日]  ※ CSV の範囲内で使う
"""
import json, subprocess, os, sys
P = {
'Hokkaidō':(43.06,141.35,111),'Aomori':(40.82,140.74,21),'Iwate':(39.70,141.15,35),'Miyagi':(38.27,140.87,57),
'Akita':(39.72,140.10,20),'Yamagata':(38.24,140.36,29),'Fukushima':(37.75,140.47,40),'Ibaraki':(36.34,140.45,76),
'Tochigi':(36.57,139.88,56),'Gunma':(36.39,139.06,38),'Saitama':(35.86,139.65,198),'Chiba':(35.61,140.12,191),
'Tōkyō':(35.69,139.69,539),'Kanagawa':(35.45,139.64,276),'Niigata':(37.90,139.02,50),'Toyama':(36.70,137.21,19),
'Ishikawa':(36.59,136.63,28),'Fukui':(36.07,136.22,23),'Yamanashi':(35.66,138.57,22),'Nagano':(36.65,138.18,53),
'Gifu':(35.39,136.72,59),'Shizuoka':(34.98,138.38,93),'Aichi':(35.18,136.91,217),'Mie':(34.73,136.51,42),
'Shiga':(35.00,135.87,36),'Kyōto':(35.02,135.76,60),'Ōsaka':(34.69,135.52,271),'Hyōgo':(34.69,135.18,148),
'Nara':(34.69,135.83,33),'Wakayama':(34.23,135.17,13),'Tottori':(35.50,134.24,9),'Shimane':(35.47,133.05,13),
'Okayama':(34.66,133.93,33),'Hiroshima':(34.40,132.46,75),'Yamaguchi':(34.19,131.47,35),'Tokushima':(34.07,134.56,13),
'Kagawa':(34.34,134.04,22),'Ehime':(33.84,132.77,31),'Kōchi':(33.56,133.53,20),'Fukuoka':(33.61,130.42,136),
'Saga':(33.25,130.30,20),'Nagasaki':(32.74,129.87,29),'Kumamoto':(32.79,130.74,41),'Ōita':(33.24,131.61,19),
'Miyazaki':(31.91,131.42,16),'Kagoshima':(31.56,130.56,35),'Okinawa':(26.21,127.68,55)}
END = sys.argv[1] if len(sys.argv) > 1 else '2026-10-29'
names = list(P)
lat = ','.join(str(P[n][0]) for n in names); lon = ','.join(str(P[n][1]) for n in names)
url = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date=2026-06-29&end_date={END}"
       "&daily=temperature_2m_max,temperature_2m_mean,temperature_2m_min,precipitation_sum&timezone=Asia%2FTokyo")
data = json.loads(subprocess.run(['curl', '-sS', '-m', '120', url], capture_output=True, text=True).stdout)
assert isinstance(data, list) and len(data) == 47
import csv, datetime as dt, statistics as st
days = data[0]['daily']['time']
tw = sum(P[n][2] for n in names)
def wavg(key, i): return sum(P[n][2]*data[k]['daily'][key][i] for k, n in enumerate(names)) / tw
T = {d: (wavg('temperature_2m_mean', i), wavg('temperature_2m_max', i), wavg('temperature_2m_min', i), wavg('precipitation_sum', i)) for i, d in enumerate(days)}
HOL = {'2026-07-20','2026-08-11','2026-09-21','2026-09-22','2026-09-23','2026-10-12'}
nano, tot, ad = {}, {}, {}
for r in csv.DictReader(open('data/daily/daily_sales.csv')):
    tot[r['date']] = tot.get(r['date'], 0) + int(r['gross'])
    if r['name'] == 'ナノガラス脱毛パッド': nano[r['date']] = int(r['gross']) / 3980
for r in csv.DictReader(open('data/daily/daily_ad.csv')):
    if r['campaign'] == 'ナノガラス脱毛パッド': ad[r['date']] = ad.get(r['date'], 0) + float(r['cost'])
D = sorted(d for d in nano if '2026-06-29' <= d <= END)
def D_(s): return dt.date.fromisoformat(s)
# 期待値: 同じ曜日の直前4回（祝日除く）の平均。個数とナノ比率（ナノ売上÷全店）
def expect(series, d):
    prev = [x for x in D if x < d and D_(x).weekday() == D_(d).weekday() and x not in HOL][-4:]
    return st.mean(series[x] for x in prev) if len(prev) == 4 else None
share = {d: nano[d]*3980 / tot[d] for d in D}
rows = []
for i, d in enumerate(D):
    prev7 = [T[x][0] for x in days if D_(d) - dt.timedelta(days=7) <= D_(x) < D_(d)]
    anom = T[d][0] - st.mean(prev7) if len(prev7) == 7 else None
    eu, es = expect(nano, d), expect(share, d)
    rows.append(dict(d=d, t=T[d][0], tmax=T[d][1], tmin=T[d][2], pr=T[d][3], anom=anom, u=nano[d], ad=ad.get(d, 0),
                     ru=(nano[d]/eu - 1) if eu else None, rs=(share[d]/es - 1) if es else None, hol=d in HOL))
# 一定予算の期間（8/9〜10/29）
R = [r for r in rows if '2026-08-09' <= r['d'] <= '2026-10-29' and not r['hol'] and r['ru'] is not None and r['anom'] is not None]
print('対象日数', len(R), ' 広告費/日 min-max', round(min(r['ad'] for r in R)), round(max(r['ad'] for r in R)))
def corr(a, b):
    ma, mb = st.mean(a), st.mean(b); 
    return sum((x-ma)*(y-mb) for x, y in zip(a, b)) / (sum((x-ma)**2 for x in a)**.5 * sum((y-mb)**2 for y in b)**.5)
print('相関 平均気温×個数の曜日比', round(corr([r['t'] for r in R], [r['ru'] for r in R]), 2),
      ' 前7日比の気温差×個数の曜日比', round(corr([r['anom'] for r in R], [r['ru'] for r in R]), 2),
      ' 気温差×ナノ比率の曜日比', round(corr([r['anom'] for r in R], [r['rs'] for r in R]), 2))
print('\n気温が低い順（顧客分布で加重した全国平均気温）')
for r in sorted(R, key=lambda r: r['t'])[:10]:
    print(f"{r['d']} 平均{r['t']:.1f}℃ 最高{r['tmax']:.1f} 前7日比{r['anom']:+.1f} 雨{r['pr']:.1f}mm 個数{r['u']:.0f} 曜日比{r['ru']:+.0%} ナノ比率の曜日比{r['rs']:+.0%}")
print('\n前7日より急に冷えた順')
for r in sorted(R, key=lambda r: r['anom'])[:10]:
    print(f"{r['d']} 平均{r['t']:.1f}℃ 前7日比{r['anom']:+.1f} 雨{r['pr']:.1f}mm 個数{r['u']:.0f} 曜日比{r['ru']:+.0%} ナノ比率の曜日比{r['rs']:+.0%}")
print('\n気温帯別（平均気温）')
for lo, hi in [(26,40),(24,26),(22,24),(20,22),(18,20),(0,18)]:
    g = [r for r in R if lo <= r['t'] < hi]
    if g: print(f"{lo}-{hi}℃ {len(g)}日 個数の曜日比 平均{st.mean(r['ru'] for r in g):+.0%} ナノ比率の曜日比 平均{st.mean(r['rs'] for r in g):+.0%}")
print('\n直近')
for r in rows[-12:]:
    print(f"{r['d']} 平均{r['t']:.1f}℃ 最高{r['tmax']:.1f} 最低{r['tmin']:.1f} 前7日比{r['anom']:+.1f} 個数{r['u']:.0f} 曜日比{r['ru']:+.0%} ナノ比率{r['rs']:+.0%}")
