import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# --- 1. 自定义设置 ---
input_file = 'spx_vix_3day_trend_analysis.csv' # 你计算好的分析结果
output_image = 'spx_vix_trend_chart.png'     # 保存的文件名

# 2. 加载并清洗数据
if not os.path.exists(input_file):
    print(f"[错误] 未能在当前目录下找到文件: {input_file}，请确保已运行之前的分析脚本。")
    exit()

try:
    # 修正参数名 index_col，并指定日期格式
    df = pd.read_csv(input_file, index_col='Date', parse_dates=True)
    df.sort_index(inplace=True)  # 确保日期升序

    print(f"成功读取数据，共 {len(df)} 行。正在生成图表...")

    # --- 3. 初始化绘图 (设置高 DPI) ---
    plt.style.use('seaborn-v0_8-darkgrid') # 2026 年兼容的新绘图风格
    fig, ax1 = plt.subplots(figsize=(16, 9), dpi=120)

    # --- 绘制 SPX 价格走势 (左轴 - 蓝色) ---
    ax1.set_xlabel('Date (Historical Data to 2026)', fontsize=12)
    ax1.set_ylabel('SPX Close Price', color='royalblue', fontsize=14)
    # 使用 alpha=0.4 让背景价格线更淡，突出 VIX 尖峰
    ax1.plot(df.index, df['Close'], color='royalblue', alpha=0.4, linewidth=1.2, label='SPX Close')
    ax1.tick_params(axis='y', labelcolor='royalblue', labelsize=10)

    # --- 绘制 VIX 恐慌指标 (右轴 - 红色) ---
    ax2 = ax1.twinx()
    ax2.set_ylabel('VIX Index Today', color='crimson', fontsize=14)
    # 绘制当日 VIX
    ax2.plot(df.index, df['VIX_Today'], color='crimson', linewidth=1.6, alpha=0.8, label='VIX Today')
    # 绘制前三天的 VIX 数据作为参考（使用不同点划线）
    ax2.plot(df.index, df['VIX_T-3'], color='orange', linewidth=0.8, linestyle='--', alpha=0.5, label='VIX T-3 (Historical)')
    ax2.tick_params(axis='y', labelcolor='crimson', labelsize=10)

    # --- 4. 标注极端波动点 (2% 以上) ---
    # 筛选大跌
    drops = df[df['Daily_Pct'] <= -0.02]
    # 使用向下黑色箭头
    ax1.scatter(drops.index, drops['Close'], color='black', marker='v', s=100, label='Drop >= 2%')
    
    # 筛选大涨
    jumps = df[df['Daily_Pct'] >= 0.02]
    # 使用向上绿色箭头
    ax1.scatter(jumps.index, jumps['Close'], color='darkgreen', marker='^', s=100, label='Jump >= 2%')

    # --- 5. 美化图表与日期格式 ---
    plt.title('SPX Market Crashes vs VIX Fear Spikes (with T-3 Day Trend)', fontsize=18, pad=25)
    
    # 日期轴格式化
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate(rotation=45) # 日期倾斜 45 度

    # 合并并显示图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    # 将 VIX Today 放在图例最前
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11, frameon=True, shadow=True)

    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    fig.tight_layout()

    # --- 6. 核心修正：保存为图片 ---
    plt.savefig(output_image, bbox_inches='tight')
    plt.close(fig) # 释放内存

    print(f"\n[成功] 图表已保存为高清图片: {output_image}")
    print(f"你可以将此文件下载到本地查看（例如使用 FTP、SCP 或在 Jupyter 中直接点击）。")

except Exception as e:
    print(f"[错误] 绘图失败: {e}")