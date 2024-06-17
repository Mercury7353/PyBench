#!/usr/bin/env python
# encoding: utf-8
import pandas as pd
import matplotlib.pyplot as plt

# 创建数据框
data = {
    'Model': ['GPT-4', 'GPT-3.5','Llama3-8b-instruct', 'CodeQwen7b-chat', "CodeActAgent-Llama-2-7b", "CodeActAgent-Mistral-7b-v0.1", "OpenCodeInterpreter-DS-6.7b", "Qwen2-7B-Instruct", "Py-Llama3-v3","Llama3-70b-Instruct"],
    'Win': [117, 71.5, 67, 77, 42, 44, 54, 85, 74,100],
    'Tie': [3, 0, 1, 2, 2, 3, 1, 2, 3,1],
    'Lose': [23, 71.5, 75, 64, 99, 96, 88, 56, 53,42]
}
df = pd.DataFrame(data)

# 按Lose的数量降序排列
df.sort_values(by='Lose', inplace=True, ascending=False)

# 数据归一化处理
df[['Win', 'Tie', 'Lose']] = df[['Win', 'Tie', 'Lose']].div(df[['Win', 'Tie', 'Lose']].sum(axis=1), axis=0)

# 设置颜色，并增加透明度
colors = ['#1E90FF', 'lightgrey', '#FF4500']

# 初始化绘图，调整figsize以增大条形图的宽度
fig, ax = plt.subplots(figsize=(10, 6))

# 绘制堆积条形图
bottom = [0] * len(df)
for i, col in enumerate(['Win', 'Tie', 'Lose']):
    bars = ax.barh(df['Model'], df[col], left=bottom, color=colors[i], label=col)
    bottom = bottom + df[col]
    if col == 'Win':
        for bar, value in zip(bars, df[col]):
            # 计算文本位置
            text_x = bar.get_x() + bar.get_width() / 2
            ax.text(text_x, bar.get_y() + bar.get_height()/2, f"{value:.1%}", va='center', ha='center')

# 设置标题和标签
ax.set_title('Win-Tie-Lose Evaluation of Different Models against GPT-3.5')
ax.set_xlabel('Percentage')
ax.set_ylabel('Model')

# 设置X轴为百分比
ax.set_xlim(0, 1)
ax.set_xticklabels(['{:.0%}'.format(x) for x in ax.get_xticks()])

# 去掉图的边框
for spine in ax.spines.values():
    spine.set_visible(False)

# 添加图例并放在右边
ax.legend(title='Result', loc='center left', bbox_to_anchor=(1, 0.5))

# 显示图形
plt.tight_layout()
plt.savefig("./WLRate.png")
