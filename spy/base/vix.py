import yfinance as yf
import pandas as pd

# 1. 设定标的 (^VIX 是 VIX 的代号，SPY 代表大盘)
symbols = ["SPY", "^VIX"]
start_date = "2023-01-01"
end_date = "2026-04-06"

# 2. 下载数据
df = yf.download(symbols, start=start_date, end=end_date)['Close']

# 3. 计算每日涨跌幅 (Pct Change)
df['SPY_Return'] = df['SPY'].pct_change()
df['VIX_Change'] = df['^VIX'].pct_change()

# 4. 计算相关性 (通常在 -0.7 到 -0.8 之间)
correlation = df['SPY_Return'].corr(df['VIX_Change'])

# 5. 保存并打印结果
df.dropna(inplace=True)
df.to_csv("spy_vix_comparison.csv")

print(f"--- SPY 与 VIX 关联分析 (相关性: {correlation:.2f}) ---")
print(df[['SPY', '^VIX', 'SPY_Return', 'VIX_Change']].tail(10))