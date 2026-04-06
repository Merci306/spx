import yfinance as yf
import pandas as pd
import numpy as np
import os

# --- 1. 读取本地 FGI 数据 ---
file_path = 'fgi_data.csv'
# 适配格式: date, fng_value, fng_classification
fgi_df = pd.read_csv(file_path, skiprows=1, names=['date', 'fng_value', 'fng_classification'], engine='python')
fgi_df['Date'] = pd.to_datetime(fgi_df['date'], dayfirst=True).dt.normalize()
fgi_df = fgi_df.set_index('Date').sort_index()

# --- 2. 获取市场历史数据 ---
print("正在同步历史行情 (2020-2026)...")
start_date = "2020-01-01" 
end_date = "2026-04-07"
data = yf.download(["^SPX", "^VIX"], start=start_date, progress=False)['Close']

# --- 3. 构造全样本矩阵 ---
df = pd.DataFrame(index=data.index)
df['SPX_Close'] = data['^SPX']
df['VIX_Today'] = data['^VIX']
df['SPX_Return_Pct'] = (df['SPX_Close'].pct_change() * 100).round(2)
df = df.join(fgi_df['fng_value'], how='left')
df.rename(columns={'fng_value': 'fgi_value'}, inplace=True)

# 关键：填充情绪缺口并确保数据完整
df['fgi_value'] = df['fgi_value'].ffill()
df = df.dropna(subset=['SPX_Return_Pct']) # 去掉第一行 NaN

# --- 4. 样本分类标记 (核心逻辑) ---
def classify_vol(ret):
    abs_ret = abs(ret)
    if abs_ret >= 3.0:
        return "Level_3 (Extreme >3%)"
    elif abs_ret >= 2.0:
        return "Level_2 (High >2%)"
    else:
        return "Normal"

df['Vol_Level'] = df['SPX_Return_Pct'].apply(classify_vol)

# --- 5. 导出文件 ---

# A. 导出全量样本 (用于深度分析)
full_sample_file = 'spx_vix_fgi_full_samples.csv'
df.to_csv(full_sample_file)

# B. 导出极端日专项表 (只包含 2% 和 3% 的日子)
extreme_samples = df[df['Vol_Level'] != "Normal"].copy()
# 增加一列：次日表现 (用于回测反抽概率)
extreme_samples['Next_Day_Return'] = df['SPX_Return_Pct'].shift(-1)
extreme_file = 'extreme_days_only_report.csv'
extreme_samples.to_csv(extreme_file)

# --- 6. 统计快报输出 ---
print("\n" + "="*40)
print("--- 历史极端波动样本统计 (2020-2026) ---")
print(df['Vol_Level'].value_counts())
print("="*40)

# 计算极端日下的平均指标
summary = extreme_samples.groupby('Vol_Level').agg({
    'VIX_Today': 'mean',
    'fgi_value': 'mean',
    'SPX_Return_Pct': 'count'
}).rename(columns={'SPX_Return_Pct': 'Occurrences'})

print(summary.round(2))
print(f"\n[成功] 全量样本已导出至: {full_sample_file}")
print(f"[成功] 极端日专项表已导出至: {extreme_file}")