import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# --- 1. 自定义设置 ---
input_file = 'spx_vix_3day_trend_analysis.csv' 
output_image = 'spx_vix_trend_scatter_combined.png'

if not os.path.exists(input_file):
    print(f"[错误] 找不到文件: {input_file}")
    exit()

try:
    # 加载数据并确保日期索引
    df = pd.read_csv(input_file, index_col='Date', parse_dates=True)
    df.sort_index(inplace=True)

    print(f"成功读取数据，正在生成“趋势+历史散点”复合图表...")

    # --- 2. 初始化绘图 ---
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax1 = plt.subplots(figsize=(16, 10), dpi=130)

    # --- A. 绘制 SPX 价格走势 (左轴 - 蓝色背景线) ---
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('SPX Close Price', color='royalblue', fontsize=14)
    ax1.plot(df.index, df['Close'], color='royalblue', alpha=0.3, linewidth=1.2, label='SPX Price')
    ax1.tick_params(axis='y', labelcolor='royalblue')

    # --- B. 绘制 VIX 核心轴 (右轴) ---
    ax2 = ax1.twinx()
    ax2.set_ylabel('VIX Index Value', color='crimson', fontsize=14)

    # 1. 绘制当日 VIX 趋势线 (实线)
    ax2.plot(df.index, df['VIX_Today'], color='crimson', linewidth=2, alpha=0.7, label='VIX Today (Line)')

    # 2. 叠加前三天的 VIX 散点 (关键修改点)
    # T-1: 深红色圆点
    ax2.scatter(df.index, df['VIX_T-1'], color='darkred', s=25, alpha=0.6, label='VIX T-1 (Point)', marker='o')
    # T-2: 橙色点
    ax2.scatter(df.index, df['VIX_T-2'], color='darkorange', s=20, alpha=0.5, label='VIX T-2 (Point)', marker='s')
    # T-3: 黄色点
    ax2.scatter(df.index, df['VIX_T-3'], color='gold', s=15, alpha=0.4, label='VIX T-3 (Point)', marker='^')

    # --- C. 标注极端波动日 (大跌/大涨符号) ---
    drops = df[df['Daily_Pct'] <= -0.02]
    ax1.scatter(drops.index, drops['Close'], color='black', marker='v', s=120, label='Crash (>= 2%)', zorder=5)
    
    jumps = df[df['Daily_Pct'] >= 0.02]
    ax1.scatter(jumps.index, jumps['Close'], color='green', marker='^', s=120, label='Jump (>= 2%)', zorder=5)

    # --- 3. 美化与日期处理 ---
    plt.title('SPX Movements vs. Multi-Day VIX Scatter Trend', fontsize=18, pad=25)
    
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate(rotation=45)

    # 合并图例并优化位置
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10, frameon=True, shadow=True)

    plt.grid(True, which='both', linestyle='--', alpha=0.4)
    fig.tight_layout()

    # --- 4. 保存图片 ---
    plt.savefig(output_image, bbox_inches='tight')
    plt.close(fig)

    print(f"\n[成功] 复合散点趋势图已保存为: {output_image}")

except Exception as e:
    print(f"[错误] 绘图失败: {e}")