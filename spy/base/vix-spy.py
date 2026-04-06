import pandas as pd
import numpy as np
import yfinance as yf

# 1. 加载并清洗 SPX 数据
file_path = 'spx_data.csv' 
df_spx = pd.read_csv(file_path, skiprows=[1, 2])
df_spx.rename(columns={df_spx.columns[0]: 'Date'}, inplace=True)
df_spx['Date'] = pd.to_datetime(df_spx['Date'])
df_spx.sort_values('Date', inplace=True)
df_spx.set_index('Date', inplace=True)
df_spx['Daily_Pct'] = df_spx['Close'].pct_change()

# 2. 获取 VIX 数据
print("正在获取 VIX 数据...")
# 下载 ^VIX 并确保只取 'Close' 列
vix_raw = yf.download("^VIX", start=df_spx.index.min(), end=df_spx.index.max())

if not vix_raw.empty:
    # 关键修正：yfinance 有时返回多级索引，这里强制取 Close 并重命名
    if isinstance(vix_raw.columns, pd.MultiIndex):
        vix_series = vix_raw['Close']['^VIX']
    else:
        vix_series = vix_raw['Close']
    
    vix_series.name = 'VIX_Close'
    
    # 3. 合并数据
    df_combined = df_spx.join(vix_series, how='inner')
    
    # 4. 筛选：涨跌幅 >= 2% 的日子
    extreme_days = df_combined[(df_combined['Daily_Pct'] >= 0.02) | (df_combined['Daily_Pct'] <= -0.02)].copy()
    
    # 5. 格式化输出
    if not extreme_days.empty:
        extreme_days['Type'] = np.where(extreme_days['Daily_Pct'] >= 0.02, '大涨(Jump)', '大跌(Drop)')
        
        print(f"\n--- SPX 极端波动日统计 (共 {len(extreme_days)} 天) ---")
        # 修正 KeyError：确保只访问存在的列
        show_cols = ['Type', 'Close', 'Daily_Pct', 'VIX_Close']
        print(extreme_days[show_cols].tail(15))
        
        # 导出结果
        extreme_days.to_csv("spx_vix_extreme_analysis.csv")
        print("\n[成功] 分析结果已保存至: spx_vix_extreme_analysis.csv")
    else:
        print("未发现跌幅超过 2% 的日子。")
else:
    print("[失败] 未能下载到 VIX 数据，请检查网络或 yfinance 库版本。")