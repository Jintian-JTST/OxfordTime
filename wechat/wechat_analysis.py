import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import jieba
from wordcloud import WordCloud
import base64
from io import BytesIO
import datetime

# ================= 配置区域 =================
# 核心过滤：只分析这一年的数据
TARGET_YEAR = 2025 

# CSV 文件路径
FILE_PATH = 'messages.csv'

# 字体路径 (根据你的系统取消注释一行)
# Windows:
FONT_PATH = 'C:/Windows/Fonts/msyh.ttc'  
# Mac:
# FONT_PATH = '/System/Library/Fonts/PingFang.ttc' 

# ================= 1. 数据加载与预处理 =================
def load_and_clean_data(filepath):
    print(f"正在加载数据并筛选 {TARGET_YEAR} 年记录...")
    try:
        df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')
    except UnicodeDecodeError:
        df = pd.read_csv(filepath, encoding='gbk', on_bad_lines='skip')

    # 1. 初步筛选 Type == 1 (仅文本)
    df = df[df['Type'] == 1].copy()
    
    # 2. 时间解析
    df['dt'] = pd.to_datetime(df['StrTime'], errors='coerce')
    df = df.dropna(subset=['dt']) 

    # ============== 关键修改：按年份过滤 ==============
    df = df[df['dt'].dt.year == TARGET_YEAR]
    
    if df.empty:
        print(f"⚠️ 警告：在 CSV 中未找到 {TARGET_YEAR} 年的数据！请检查 CSV 时间范围。")
        return df

    # 提取时间维度
    df['Month'] = df['dt'].dt.month # 改为数字便于排序
    df['Date'] = df['dt'].dt.date
    df['Hour'] = df['dt'].dt.hour
    
    # 3. 字段映射
    df['SenderType'] = df['IsSender'].map({1: '我', 0: '对方'})
    
    # 4. 内容清洗
    df['StrContent'] = df['StrContent'].fillna('')
    
    print(f"✅ {TARGET_YEAR} 年有效文本消息: {len(df)} 行")
    return df

# ================= 2. 可视化辅助函数 =================
def plot_to_base64(plt_obj):
    buf = BytesIO()
    plt_obj.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt_obj.close()
    return img_base64

def set_chinese_font():
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei', 'Heiti TC'] 
    plt.rcParams['axes.unicode_minus'] = False 

# ================= 3. 分析模块 =================

def analyze_activity_trend(df):
    """2025年月度趋势"""
    set_chinese_font()
    
    # 确保1-12月都有索引，即使某月没说话也要显示为0
    monthly_counts = df.groupby('Month').size()
    all_months = pd.Index(range(1, 13), name='Month')
    monthly_counts = monthly_counts.reindex(all_months, fill_value=0)
    
    plt.figure(figsize=(10, 5))
    monthly_counts.plot(kind='line', marker='o', linewidth=2, color='#07c160')
    plt.title(f'{TARGET_YEAR} 年月度活跃度')
    plt.xlabel('月份')
    plt.ylabel('消息数')
    plt.xticks(range(1, 13)) # 强制显示1-12月
    plt.grid(True, linestyle='--', alpha=0.5)
    return plot_to_base64(plt)

def analyze_hourly_pattern(df):
    """24小时作息分布"""
    set_chinese_font()
    
    hourly_counts = df.groupby(['Hour', 'SenderType']).size().unstack().fillna(0)
    # 确保所有小时都存在
    hourly_counts = hourly_counts.reindex(range(24), fill_value=0)
    
    plt.figure(figsize=(10, 5))
    hourly_counts.plot(kind='bar', stacked=True, width=0.8, alpha=0.85, color=['#ff9f43', '#0abde3'])
    plt.title(f'{TARGET_YEAR} 年全天作息分布')
    plt.xlabel('小时 (0-23)')
    plt.ylabel('消息数')
    plt.legend(title='来源')
    return plot_to_base64(plt)

def analyze_top_contacts(df):
    """Top 10 联系人"""
    set_chinese_font()
    
    top_talkers = df['TalkerId'].value_counts().head(10)
    
    top_data = []
    for tid in top_talkers.index:
        try:
            name = df[df['TalkerId'] == tid]['NickName'].iloc[0]
        except:
            name = "未知用户"
        count = top_talkers[tid]
        top_data.append({'Name': str(name), 'Count': count})
        
    top_df = pd.DataFrame(top_data)
    
    plt.figure(figsize=(10, 6))
    if not top_df.empty:
        sns.barplot(x='Count', y='Name', data=top_df, palette='Blues_d')
    plt.title(f'{TARGET_YEAR} 年最常联系 Top 10')
    plt.xlabel('消息数')
    plt.ylabel('')
    return plot_to_base64(plt)

def analyze_wordcloud(df):
    """生成词云"""
    print("正在生成词云...")
    text = " ".join(df['StrContent'].tolist())
    
    stopwords = {'的', '了', '我', '是', '在', '也', '有', '就', '不', '人', '都', '一个', '上', '我们', 
                 '[Grin]', '[Face]', '图片', '视频', '吗', '啊', '吧', '呢', '去', '好', '要', '哈哈', '哈哈哈'}
    
    words = jieba.cut(text)
    clean_words = [word for word in words if len(word) > 1 and word not in stopwords]
    
    if not clean_words:
        return "" # 无有效词汇

    try:
        wc = WordCloud(font_path=FONT_PATH, width=800, height=400, background_color='white', colormap='tab10').generate(" ".join(clean_words))
    except:
        wc = WordCloud(width=800, height=400, background_color='white').generate(" ".join(clean_words))
        
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    return plot_to_base64(plt)

def analyze_summary_metrics(df):
    """计算核心指标"""
    total_msgs = len(df)
    my_msgs = len(df[df['IsSender'] == 1])
    other_msgs = len(df[df['IsSender'] == 0])
    
    # 2025年已过去的天数（如果还没过完2025，就按最大日期算）
    min_date = df['dt'].min()
    max_date = df['dt'].max()
    days = (max_date - min_date).days + 1 if total_msgs > 0 else 1
    
    return {
        'total': total_msgs,
        'sent': my_msgs,
        'received': other_msgs,
        'avg': round(total_msgs / days, 1) if days > 0 else 0,
        'start': min_date.strftime('%m-%d'),
        'end': max_date.strftime('%m-%d')
    }

# ================= 4. 报告生成 =================
def generate_html_report(metrics, charts):
    html_content = f"""
    <html>
    <head>
        <title>{TARGET_YEAR} 微信数据报告</title>
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, 'Microsoft YaHei', Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 40px; background-color: #f7f9fc; color: #333; }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            h1 {{ font-size: 32px; color: #2c3e50; margin-bottom: 10px; }}
            .subtitle {{ color: #7f8c8d; font-size: 16px; }}
            .card {{ background: white; padding: 30px; margin-bottom: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-2px); }}
            h2 {{ border-left: 5px solid #3498db; padding-left: 15px; margin-top: 0; margin-bottom: 25px; font-size: 20px; }}
            .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; text-align: center; }}
            .metric-item {{ background: #f8f9fa; padding: 15px; border-radius: 8px; }}
            .metric-val {{ font-size: 28px; font-weight: bold; color: #2c3e50; margin-bottom: 5px; }}
            .metric-label {{ font-size: 13px; color: #95a5a6; text-transform: uppercase; letter-spacing: 1px; }}
            img {{ max-width: 100%; height: auto; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{TARGET_YEAR} 年度微信回忆录</h1>
            <div class="subtitle">分析周期：{metrics['start']} 至 {metrics['end']}</div>
        </div>

        <div class="card">
            <h2>📊 年度核心数据</h2>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-val">{metrics['total']:,}</div>
                    <div class="metric-label">总消息数</div>
                </div>
                <div class="metric-item">
                    <div class="metric-val">{metrics['sent']:,}</div>
                    <div class="metric-label">我发出的</div>
                </div>
                <div class="metric-item">
                    <div class="metric-val">{metrics['received']:,}</div>
                    <div class="metric-label">收到的</div>
                </div>
                <div class="metric-item">
                    <div class="metric-val">{metrics['avg']}</div>
                    <div class="metric-label">日均消息</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>📅 月度活跃趋势</h2>
            <img src="data:image/png;base64,{charts['trend']}" />
        </div>

        <div class="card">
            <h2>⏰ 全天作息规律</h2>
            <img src="data:image/png;base64,{charts['hourly']}" />
        </div>

        <div class="card">
            <h2>🏆 年度 Top 10 联系人</h2>
            <img src="data:image/png;base64,{charts['contacts']}" />
        </div>
        
        <div class="card">
            <h2>💭 年度关键词云</h2>
            <img src="data:image/png;base64,{charts['wordcloud']}" />
        </div>
        
        <div style="text-align:center; color:#bdc3c7; font-size:12px; margin-top:50px;">
            Generated by Python Analysis Script
        </div>
    </body>
    </html>
    """
    
    filename = f'WeChat_Report_{TARGET_YEAR}.html'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ 报告已生成：{filename}")

# ================= 主程序入口 =================
if __name__ == "__main__":
    df = load_and_clean_data(FILE_PATH)
    
    if not df.empty:
        metrics = analyze_summary_metrics(df)
        
        charts = {}
        charts['trend'] = analyze_activity_trend(df)
        charts['hourly'] = analyze_hourly_pattern(df)
        charts['contacts'] = analyze_top_contacts(df)
        charts['wordcloud'] = analyze_wordcloud(df)
        
        generate_html_report(metrics, charts)
    else:
        print("程序结束。")