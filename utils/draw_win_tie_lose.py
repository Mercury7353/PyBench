#!/usr/bin/env python
# encoding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 创建数据框
data = {
    'Model': ['llama', 'llama2', 'llama3'],
    'Win': [10, 12, 9],
    'Tie': [5, 7, 6],
    'Lose': [3, 4, 5]
}
df = pd.DataFrame(data)

# 数据归一化处理
df[['Win', 'Tie', 'Lose']] = df[['Win', 'Tie', 'Lose']].div(df[['Win', 'Tie', 'Lose']].sum(axis=1), axis=0)

# 设置颜色
colors = {
    'Win': 'lightblue',
    'Tie': 'lightgrey',
    'Lose': 'lightcoral'
}

# 转换数据格式为适合堆积条形图的格式
df_melted = df.melt(id_vars='Model', var_name='Result', value_name='Count')

# 初始化绘图
fig, ax = plt.subplots(figsize=(10, 2))  # 进一步调整高度

# 绘制每一部分的条形图
bottoms = [0] * len(df)  # 用于堆积的底部位置
for result in ['Win', 'Tie', 'Lose']:
    sns.barplot(
        x='Count',
        y='Model',
        data=df_melted[df_melted['Result'] == result],
        label=result,
        color=colors[result],
        edgecolor='black',
        linewidth=0.5,
        ax=ax,
        left=bottoms
    )
    bottoms = [i + j for i, j in zip(bottoms, df[result])]

# 设置标题和标签
ax.set_title('Win-Tie-Lose Evaluation of Different Models against GPT-3.5')
ax.set_xlabel('Normalized Count')
ax.set_ylabel('Model')

# 添加图例并放在右边
ax.legend(title='Result', loc='center left', bbox_to_anchor=(1, 0.5))

# 显示图形
plt.tight_layout()
plt.show()

