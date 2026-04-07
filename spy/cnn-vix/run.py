import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time

# --- 1. 下载市场基础数据 (SPX & VIX) ---
print("正在从 Yahoo Finance 下载 SPX 和 VIX 数据...")
start_date = "2023-01-01"
end_date = "2026-04-07" 
symbols = ["^SPX", "^VIX"]

try:
    raw_data = yf.download(symbols, start=start_date, end=end_date)['Close']
    df = raw_data.copy()
    # 适配不同版本的 yfinance 列名
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(1)
    df.columns = ['SPX_Close', 'VIX_Today']
    df.index.name = 'Date'
except Exception as e:
    print(f"[错误] 下载基础数据失败: {e}")
    exit()

# --- 2. 计算涨跌幅与 VIX 趋势 ---
df['SPX_Return'] = df['SPX_Close'].pct_change()
df['VIX_T-1'] = df['VIX_Today'].shift(1)
df['VIX_T-2'] = df['VIX_Today'].shift(2)
df['VIX_T-3'] = df['VIX_Today'].shift(3)
df['VIX_Jump'] = df['VIX_Today'] - df['VIX_T-1']

# --- 3. 核心修正：CNN 恐惧与贪婪指数抓取 ---
print("正在获取 CNN 恐惧与贪婪指数...")
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.cnn.com/markets/fear-and-greed'
}
cnn_url = "https://production.dataviz.cnn.io/index/feargreed/graph/data"

df['fgi_value'] = np.nan # 预设空值

try:
    response = requests.get(cnn_url, headers=headers, timeout=15)
    r_json = response.json()
    
    # 增加健壮的路径检查
    if 'data' in r_json and 'series' in r_json['data'] and len(r_json['data']['series']) > 0:
        fgi_list = r_json['data']['series'][0]['data']
        fgi_df = pd.DataFrame(fgi_list, columns=['timestamp', 'fgi_value'])
        fgi_df['Date'] = pd.to_datetime(fgi_df['timestamp'], unit='ms').dt.normalize()
        fgi_df = fgi_df.drop_duplicates('Date').set_index('Date')
        
        # 合并
        df.update(fgi_df[['fgi_value']])
        df['fgi_value'] = df['fgi_value'].ffill() 
        print("[成功] CNN 指数已对齐。")
    else:
        print("[警告] CNN 接口返回数据结构不符合预期，跳过情緒指标。")
except Exception as e:
    print(f"[警告] 网络抓取失败: {e}")

# --- 4. 修复 Numpy DTypePromotionError ---
# 使用 pd.Series.where 或强制转换类型
df['Type'] = "Normal" # 先全部设为字符串
df.loc[df['SPX_Return'] <= -0.02, 'Type'] = "Drop >= 2%"
df.loc[df['SPX_Return'] >= 0.02, 'Type'] = "Jump >= 2%"

# --- 5. 导出并预览 ---
output_file = 'spx_vix_cnn_final_v2.csv'
df.to_csv(output_file)

print(f"\n--- 整合数据预览 (最近 5 个交易日) ---")
# 仅显示存在的列
cols = [c for c in ['SPX_Close', 'SPX_Return', 'VIX_Today', 'fgi_value', 'Type'] if c in df.columns]
print(df[cols].tail(5))