import yfinance as yf
import pandas as pd
import numpy as np
import os

# --- 1. 读取并精准解析你的本地 FGI 数据 ---
# 你的数据行格式: 06-04-2026, 13, Extreme Fear
# 对应逻辑顺序: date, fng_value, fng_classification
file_path = 'fgi_data.csv'

if not os.path.exists(file_path):
    print(f"[错误] 找不到文件: {file_path}，请确保文件名正确。")
    exit()

try:
    # 核心修正：跳过原始不匹配的表头，手动指定正确的列名顺序
    fgi_df = pd.read_csv(
        file_path, 
        skiprows=1, 
        names=['date', 'fng_value', 'fng_classification'],
        engine='python',
        skipinitialspace=True
    )
    
    # 转换日期 (针对 06-04-2026 这种 DD-MM-YYYY 格式)
    fgi_df['Date'] = pd.to_datetime(fgi_df['date'], dayfirst=True).dt.normalize()
    fgi_df = fgi_df.set_index('Date').sort_index()
    
    print(f"[成功] 情绪数据对齐完毕。今日 (2026-04-06) FGI 指数: {fgi_df['fng_value'].iloc[-1]}")
except Exception as e:
    print(f"[错误] 解析 CSV 失败，请检查数据行是否有空格或逗号错误: {e}")
    exit()

# --- 2. 同步雅虎财经市场行情 (SPX & VIX) ---
print("正在同步雅虎财经市场实时行情...")
# 以 FGI 数据的最早日期作为起点，确保历史对齐
start_date = fgi_df.index.min().strftime('%Y-%m-%d')
end_date = "2026-04-07"

# 稳健下载，避免 MultiIndex 导致的数据错位
spx = yf.download("^SPX", start=start_date, end=end_date, progress=False)['Close']
vix = yf.download("^VIX", start=start_date, end=end_date, progress=False)['Close']

# --- 3. 物理合拢与清洗 ---
# 构造统一的时间序列框架
df = pd.DataFrame(index=spx.index)
df['SPX_Close'] = spx
df['VIX_Today'] = vix
df.index = pd.to_datetime(df.index).normalize()

# 合并本地 FGI (情绪指标)
df = df.join(fgi_df['fng_value'], how='left')
df.rename(columns={'fng_value': 'fgi_value'}, inplace=True)

# 填充非交易日（如周末）的情绪值，确保数据连续性
df['fgi_value'] = df['fgi_value'].ffill()

# --- 4. 计算量化衍生指标 ---
df['SPX_Return'] = df['SPX_Close'].pct_change()
df['VIX_Jump'] = df['VIX_Today'] - df['VIX_Today'].shift(1)
df['VIX_T-1'] = df['VIX_Today'].shift(1)

# 标记极端交易日类型
df['Type'] = "Normal"
df.loc[df['SPX_Return'] <= -0.02, 'Type'] = "Drop >= 2%"
df.loc[df['SPX_Return'] >= 0.02, 'Type'] = "Jump >= 2%"

# --- 5. 导出整合报告 ---
output_name = 'market_sentiment_master_2026.csv'
df.to_csv(output_name)

print(f"\n--- 2026-04-06 量化整合快报 ---")
# 预览最后 5 天的数据，确认对齐效果
print(df[['SPX_Close', 'VIX_Today', 'fgi_value', 'Type']].tail(5))