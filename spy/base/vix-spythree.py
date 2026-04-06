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
print("正在同步获取 VIX 历史数据...")
vix_raw = yf.download("^VIX", start=df_spx.index.min(), end=df_spx.index.max())

if not vix_raw.empty:
    # 处理 MultiIndex
    if isinstance(vix_raw.columns, pd.MultiIndex):
        vix_series = vix_raw['Close']['^VIX']
    else:
        vix_series = vix_raw['Close']
    
    # --- 关键修改：计算 VIX 历史平移数据 ---
    vix_df = pd.DataFrame(vix_series)
    vix_df.columns = ['VIX_Today']
    vix_df['VIX_T-1'] = vix_df['VIX_Today'].shift(1) # 前 1 天
    vix_df['VIX_T-2'] = vix_df['VIX_Today'].shift(2) # 前 2 天
    vix_df['VIX_T-3'] = vix_df['VIX_Today'].shift(3) # 前 3 天
    
    # 3. 合并数据
    df_combined = df_spx.join(vix_df, how='inner')
    
    # 4. 筛选：SPX 涨跌幅 >= 2% 的日子
    extreme_days = df_combined[(df_combined['Daily_Pct'] >= 0.02) | (df_combined['Daily_Pct'] <= -0.02)].copy()
    
    # 5. 格式化输出
    if not extreme_days.empty:
        extreme_days['Type'] = np.where(extreme_days['Daily_Pct'] >= 0.02, '大涨(Jump)', '大跌(Drop)')
        
        # 计算 VIX 在大波动当天的变动情况
        extreme_days['VIX_Jump'] = extreme_days['VIX_Today'] - extreme_days['VIX_T-1']

        print(f"\n--- SPX 极端波动日统计：包含 VIX 前 3 天数值 ---")
        # 定义展示列：包含前三天的 VIX
        show_cols = ['Type', 'Daily_Pct', 'VIX_T-3', 'VIX_T-2', 'VIX_T-1', 'VIX_Today', 'VIX_Jump']
        
        # 打印最近 15 个极端交易日
        print(extreme_days[show_cols].tail(15))
        
        # 导出结果
        extreme_days.to_csv("spx_vix_3day_trend_analysis.csv")
        print("\n[成功] 趋势分析已保存至: spx_vix_3day_trend_analysis.csv")
    else:
        print("未发现 SPX 涨跌幅超过 2% 的交易日。")
else:
    print("[错误] VIX 下载失败。")