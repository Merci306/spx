import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# --- 1. 读取本地 FGI 数据 ---
file_path = 'fgi_data.csv'
# 强制指定列名顺序: date, fng_value, fng_classification
fgi_df = pd.read_csv(file_path, skiprows=1, names=['date', 'fng_value', 'fng_classification'], engine='python')
fgi_df['Date'] = pd.to_datetime(fgi_df['date'], dayfirst=True).dt.normalize()
fgi_df = fgi_df.set_index('Date').sort_index()

# --- 2. 获取市场历史数据 (拉长周期以获取更多 3% 样本) ---
print("正在同步历史行情...")
# 建议下载 2020 至今的数据，否则 3% 的日子太少
start_date = "2020-01-01" 
end_date = "2026-04-07"
data = yf.download(["^SPX", "^VIX"], start=start_date, progress=False)['Close']

# --- 3. 数据合拢与清洗 ---
df = pd.DataFrame(index=data.index)
df['SPX_Close'] = data['^SPX']
df['VIX_Today'] = data['^VIX']
df['SPX_Return'] = df['SPX_Close'].pct_change()
df = df.join(fgi_df['fng_value'], how='left')
df.rename(columns={'fng_value': 'fgi_value'}, inplace=True)
df['fgi_value'] = df['fgi_value'].ffill() # 填充情绪缺口

# --- 4. 统计核心：筛选涨跌幅绝对值 > 3% 的日子 ---
extreme_days = df[df['SPX_Return'].abs() >= 0.03].copy()

# 分类统计：大跌 vs 大涨
big_down = extreme_days[extreme_days['SPX_Return'] <= -0.03]
big_up = extreme_days[extreme_days['SPX_Return'] >= 0.03]

# --- 5. 生成统计报表 ---
stats_summary = {
    "类别": ["大跌 (<= -3%)", "大涨 (>= +3%)", "全极端样本"],
    "天数": [len(big_down), len(big_up), len(extreme_days)],
    "VIX 均值": [big_down['VIX_Today'].mean(), big_up['VIX_Today'].mean(), extreme_days['VIX_Today'].mean()],
    "VIX 范围": [f"{big_down['VIX_Today'].min():.1f}-{big_down['VIX_Today'].max():.1f}", 
                 f"{big_up['VIX_Today'].min():.1f}-{big_up['VIX_Today'].max():.1f}", 
                 f"{extreme_days['VIX_Today'].min():.1f}-{extreme_days['VIX_Today'].max():.1f}"],
    "FGI 均值": [big_down['fgi_value'].mean(), big_up['fgi_value'].mean(), extreme_days['fgi_value'].mean()],
    "FGI 范围": [f"{big_down['fgi_value'].min():.0f}-{big_down['fgi_value'].max():.0f}", 
                 f"{big_up['fgi_value'].min():.0f}-{big_up['fgi_value'].max():.0f}", 
                 f"{extreme_days['fgi_value'].min():.0f}-{extreme_days['fgi_value'].max():.0f}"]
}

report_df = pd.DataFrame(stats_summary)
report_df.to_csv('extreme_volatility_stats.csv', index=False)

# --- 6. 绘图：极端波动下的情绪分布图 ---
plt.figure(figsize=(14, 8))
plt.style.use('ggplot')

# 绘制所有样本点
plt.scatter(df['SPX_Return'] * 100, df['VIX_Today'], c=df['fgi_value'], cmap='RdYlGn', alpha=0.3, label='Normal Days')

# 突出显示极端波动点
plt.scatter(extreme_days['SPX_Return'] * 100, extreme_days['VIX_Today'], 
            c=extreme_days['fgi_value'], cmap='RdYlGn', s=100, edgecolors='black', linewidth=1.5, label='Extreme Days (|Ret| > 3%)')

# 标记 3% 边界线
plt.axvline(x=3, color='blue', linestyle='--', alpha=0.5)
plt.axvline(x=-3, color='blue', linestyle='--', alpha=0.5)

plt.colorbar(label='Fear & Greed Index (Red=Fear, Green=Greed)')
plt.xlabel('SPX Daily Return (%)', fontsize=12)
plt.ylabel('VIX Value', fontsize=12)
plt.title('SPX Extreme Volatility vs. VIX & FGI (2020-2026)', fontsize=15)
plt.legend()
plt.savefig('extreme_vol_plot.png')

print("\n--- 统计摘要 ---")
print(report_df)
print(f"\n[成功] 统计报告已保存至 extreme_volatility_stats.csv")
print(f"[成功] 可视化图表已保存至 extreme_vol_plot.png")