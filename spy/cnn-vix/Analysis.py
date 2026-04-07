import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 加载数据
file_path = 'spx_vix_fgi_full_samples.csv'
df = pd.read_csv(file_path, index_col='Date', parse_dates=True)

# 2. 准备绘图数据：筛选掉 NaN 并处理百分比
plot_df = df.dropna(subset=['SPX_Return_Pct', 'VIX_Today', 'fgi_value']).copy()

# 3. 开始绘图
plt.figure(figsize=(16, 10))
plt.style.use('dark_background') # 使用深色背景，突出极端信号点

# 核心散点：X轴=涨跌幅, Y轴=VIX, 颜色=FGI指数
scatter = plt.scatter(
    plot_df['SPX_Return_Pct'], 
    plot_df['VIX_Today'], 
    c=plot_df['fgi_value'], 
    cmap='RdYlGn',        # 红(恐慌) -> 黄 -> 绿(贪婪)
    s=80,                 # 点的大小
    alpha=0.6,            # 透明度
    edgecolors='white', 
    linewidth=0.5
)

# 4. 突出显示 ±2% 和 ±3% 的极端警戒线
plt.axvline(x=-2, color='orange', linestyle='--', alpha=0.8, label='2% Alert Line')
plt.axvline(x=-3, color='red', linestyle='-', alpha=0.9, label='3% Panic Line')
plt.axvline(x=2, color='lightgreen', linestyle='--', alpha=0.8)

# 5. 装饰图表
cbar = plt.colorbar(scatter)
cbar.set_label('Fear & Greed Index (0-100)', color='white')
plt.xlabel('SPX Daily Return (%)', fontsize=12, color='white')
plt.ylabel('VIX (Implied Volatility)', fontsize=12, color='white')
plt.title('SPX Triple Sentiment Model: Return vs. VIX vs. FGI (2020-2026)', fontsize=16, pad=20)
plt.legend(facecolor='black', edgecolor='white')
plt.grid(True, linestyle=':', alpha=0.3)

# 6. 标注当前点 (2026-04-06: FGI=13)
# 假设今日 SPX 跌幅为 -2.5% (根据通牒日预估)
plt.annotate('TODAY (FGI=13)', 
             xy=(-2.5, 32), # 根据实时盘面调整坐标
             xytext=(-1.5, 45),
             arrowprops=dict(facecolor='yellow', shrink=0.05),
             color='yellow', fontsize=12, fontweight='bold')

# 保存图片
plt.savefig('sentiment_analysis_plot.png', dpi=300)
print("[成功] 可视化图表已保存为: sentiment_analysis_plot.png")

# 7. 保存极端样本统计表
summary_stats = plot_df[plot_df['Vol_Level'] != 'Normal'].sort_values(by='Date', ascending=False)
summary_stats.to_csv('extreme_case_analysis.csv')
print("[成功] 极端样本清单已保存为: extreme_case_analysis.csv")

plt.show()