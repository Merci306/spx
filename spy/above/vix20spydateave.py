import pandas as pd
import numpy as np
import yfinance as yf

# 1. 下载数据
symbols = ["SPY", "^VIX"]
data = yf.download(symbols, start="2000-01-01", end="2026-04-06")['Close']

# 2. 计算涨跌幅
data['SPY_Pct'] = data['SPY'].pct_change()
data.dropna(inplace=True)

# 3. 筛选 VIX > 20 的日子
high_vol_days = data[data['^VIX'] > 20].copy()

# 4. 准备保存原始筛选数据
# 增加一列：涨跌幅百分比形式，方便人类阅读
high_vol_days['SPY_Pct_Formatted'] = (high_vol_days['SPY_Pct'] * 100).round(2).astype(str) + '%'
raw_data_file = "vix_over_20_raw_data.csv"
high_vol_days.to_csv(raw_data_file)
print(f"[成功] 原始筛选数据已保存至: {raw_data_file}")

# 5. 生成统计摘要表 (Summary Metrics)
stats_summary = {
    "Metric": [
        "Total Sample Days",
        "VIX > 20 Days",
        "VIX > 20 Ratio",
        "Up Days (SPY > 0)",
        "Down Days (SPY < 0)",
        "Win Rate (%)",
        "Avg Daily Return (%)",
        "Max One-Day Drop (%)",
        "Max One-Day Jump (%)"
    ],
    "Value": [
        len(data),
        len(high_vol_days),
        f"{len(high_vol_days)/len(data):.2%}",
        len(high_vol_days[high_vol_days['SPY_Pct'] > 0]),
        len(high_vol_days[high_vol_days['SPY_Pct'] < 0]),
        f"{(len(high_vol_days[high_vol_days['SPY_Pct'] > 0]) / len(high_vol_days) * 100):.2f}%",
        f"{(high_vol_days['SPY_Pct'].mean() * 100):.3f}%",
        f"{(high_vol_days['SPY_Pct'].min() * 100):.2f}%",
        f"{(high_vol_days['SPY_Pct'].max() * 100):.2f}%"
    ]
}

df_summary = pd.DataFrame(stats_summary)
summary_file = "vix_high_vol_summary_report.csv"
df_summary.to_csv(summary_file, index=False)
print(f"[成功] 统计报告摘要已保存至: {summary_file}")

# 6. 保存区间分布数据 (Bin Distribution)
bins = [-np.inf, -0.03, -0.02, -0.01, 0, 0.01, 0.02, 0.03, np.inf]
labels = ['<-3%', '-3% to -2%', '-2% to -1%', '-1% to 0%', '0% to 1%', '1% to 2%', '2% to 3%', '>3%']
dist_series = pd.cut(high_vol_days['SPY_Pct'], bins=bins, labels=labels).value_counts().sort_index()
dist_df = dist_series.reset_index()
dist_df.columns = ['Range', 'Count']
dist_file = "vix_high_vol_distribution.csv"
dist_df.to_csv(dist_file, index=False)
print(f"[成功] 涨跌幅区间分布已保存至: {dist_file}")