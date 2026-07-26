# -*- coding: utf-8 -*-
"""LOOTY日次レポートのExcel生成。使い方: python3 report_xlsx.py <data.json> <out.xlsx>
data.json: {"date":"YYYY-MM-DD(曜)", "headline":[[label,昨日,同曜日,3日,7日,30日,vs7日],...],
 "summary":[[期間,売上,原価,広告費,利益,利益率,手数料,控除後利益,控除後率],...],
 "products":[[商品,7日売上,7日原価,7日広告,7日利益,前日売上,前日利益,前日率,3日利益,30日利益,MER,分岐,余裕,判定,予算],...],
 "notes":[str,...]}"""
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

data = json.load(open(sys.argv[1]))
wb = Workbook()
TH = Font(name="Arial", bold=True, color="FFFFFF", size=10)
TD = Font(name="Arial", size=10)
NEG = Font(name="Arial", size=10, color="CC0000")
HEAD = PatternFill("solid", fgColor="305496")
ALT = PatternFill("solid", fgColor="F2F6FC")
YELLOW = PatternFill("solid", fgColor="FFF2A8")
GREEN = PatternFill("solid", fgColor="D6EFD8")
RED = PatternFill("solid", fgColor="FADBD8")
thin = Border(*[Side(style="thin", color="CCCCCC")]*4)

def style_header(ws, row, ncols):
    for c in range(1, ncols+1):
        cell = ws.cell(row, c); cell.font = TH; cell.fill = HEAD; cell.border = thin
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

# ---- Sheet1: 全体サマリー ----
ws = wb.active; ws.title = "全体サマリー"
ws["A1"] = f"LOOTY 日次損益レポート {data['date']}"
ws["A1"].font = Font(name="Arial", bold=True, size=13)
r = 3
ws.cell(r, 1, "■ 昨日の全体実績 × 期間比較").font = Font(name="Arial", bold=True, size=11)
r += 1
hh = ["指標", "昨日", "同曜日平均", "3日平均/日", "7日平均/日", "30日平均/日", "昨日vs7日平均"]
for c, v in enumerate(hh, 1): ws.cell(r, c, v)
style_header(ws, r, len(hh))
for row in data["headline"]:
    r += 1
    for c, v in enumerate(row, 1):
        cell = ws.cell(r, c, v); cell.font = TD; cell.border = thin
        # 実績期間比較の数値はカンマ表記（ユーザー指定 2026-07-26）
        if isinstance(v, (int, float)) and not isinstance(v, bool) and c in (2,3,4,5,6):
            cell.number_format = "#,##0"
            cell.alignment = Alignment(horizontal="right")
r += 2
ws.cell(r, 1, "■ 期間別サマリー（カタログ広告費込み・全商品）").font = Font(name="Arial", bold=True, size=11)
r += 1
sh = ["期間", "売上(gross−値引)", "原価", "広告費", "利益", "利益率", "手数料(3.49%)", "控除後利益", "控除後利益率"]
for c, v in enumerate(sh, 1): ws.cell(r, c, v)
style_header(ws, r, len(sh))
for row in data["summary"]:
    r += 1
    for c, v in enumerate(row, 1):
        cell = ws.cell(r, c, v); cell.font = TD; cell.border = thin
        if isinstance(v, (int, float)) and c in (2,3,4,5,7,8): cell.number_format = "#,##0"
        if isinstance(v, (int, float)) and c in (6,9): cell.number_format = "0.0%"
r += 2
for note in data.get("notes", []):
    ws.cell(r, 1, "・" + note).font = Font(name="Arial", size=9, color="606060")
    r += 1
for col, w in zip("ABCDEFGHI", [22,14,12,12,12,9,12,12,12]): ws.column_dimensions[col].width = w
ws.freeze_panes = "A5"

# ---- Sheet2: 商品別 ----
ws2 = wb.create_sheet("商品別")
ph = ["商品",
      "7日売上", "7日原価", "7日広告費", "7日利益", "7日利益率", "原価率", "広告費率",
      "3日売上", "3日原価", "3日広告費", "3日利益", "3日利益率",
      "前日売上", "前日原価", "前日広告費", "前日利益", "前日利益率",
      "30日利益", "MER(7日)", "分岐", "目標MER", "余裕", "増分MER",
      "現日予算(円)", "判定", "推奨アクション"]
for c, v in enumerate(ph, 1): ws2.cell(1, c, v)
style_header(ws2, 1, len(ph))
ws2.row_dimensions[1].height = 30
MONEY  = (2,3,4,5, 9,10,11,12, 14,15,16,17, 19, 25)
PCT    = (6,7,8, 13, 18)
RATIO  = (20,21,22,23,24)
PROFIT = (5,12,17,19)        # 赤字を赤字表示する利益列
MARGIN = (6,13,18)           # 利益率列（<30%黄・赤字は赤）
for i, row in enumerate(data["products"]):
    r = i + 2
    for c, v in enumerate(row, 1):
        cell = ws2.cell(r, c, v); cell.border = thin
        cell.font = NEG if (isinstance(v,(int,float)) and v < 0 and c in PROFIT+MARGIN) else TD
        if isinstance(v, (int, float)):
            if c in MONEY: cell.number_format = "#,##0"
            if c in PCT:   cell.number_format = "0.0%"
            if c in RATIO: cell.number_format = "0.00"
        if i % 2 == 1: cell.fill = ALT
        if c == 27: cell.alignment = Alignment(wrap_text=True, vertical="top")
        if not isinstance(v, (int, float)): continue
        if c in MARGIN and v < 0.30: cell.fill = RED if v < 0 else YELLOW
        if c == 7 and v > 0.33: cell.fill = RED        # 原価率>33%
        if c == 8 and v > 0.40: cell.fill = RED        # 広告費率>40%
        if c == 24: cell.fill = GREEN if v >= 2.91 else (RED if v < 1.44 else YELLOW)
# MER vs 目標MER: 目標を超えていれば緑、下回れば赤（商品ごとの目標で判定）
for i, row in enumerate(data["products"]):
    r = i + 2
    mer, tgt = row[19], row[21]
    if isinstance(mer,(int,float)) and isinstance(tgt,(int,float)):
        ws2.cell(r, 20).fill = GREEN if mer >= tgt else RED
WIDTHS = [34, 11,10,11,11,9, 8,9, 10,10,10,10,9, 10,10,10,10,9, 11, 9,7,8,7,8, 11, 22, 52]
for c, w in enumerate(WIDTHS, 1): ws2.column_dimensions[ws2.cell(1,c).column_letter].width = w
ws2.freeze_panes = "B2"  # ヘッダー行＋商品列を固定（ユーザー指定）
wb.save(sys.argv[2])
print("saved", sys.argv[2])
