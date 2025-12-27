"""
WeChat Annual Chat Analysis
==========================
- Yearly analysis for a single year
- GitHub-style activity heatmap
- Per-talker profiles (JSON)
- HTML report with explicit Top Talkers section
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import jieba
from wordcloud import WordCloud
from io import BytesIO
import base64
import json

# ===================== 配置 =====================
TARGET_YEAR = 2025
CSV_PATH = "messages.csv"
TOP_N_TALKERS = 5

FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
# FONT_PATH = "/System/Library/Fonts/PingFang.ttc"

# ===================== 工具函数 =====================
def set_font():
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei", "SimHei", "Arial Unicode MS"
    ]
    plt.rcParams["axes.unicode_minus"] = False


def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return img


# ===================== 数据加载 =====================
def load_data():
    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8", on_bad_lines="skip")
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_PATH, encoding="gbk", on_bad_lines="skip")

    df = df[df["Type"] == 1].copy()
    df["dt"] = pd.to_datetime(df["StrTime"], errors="coerce")
    df = df.dropna(subset=["dt"])
    df = df[df["dt"].dt.year == TARGET_YEAR]

    df["Date"] = df["dt"].dt.date
    df["Month"] = df["dt"].dt.month
    df["Hour"] = df["dt"].dt.hour
    df["Weekday"] = df["dt"].dt.weekday
    df["StrContent"] = df["StrContent"].fillna("")

    return df


# ===================== 总体统计 =====================
def summary_metrics(df):
    total = len(df)
    sent = (df["IsSender"] == 1).sum()
    received = (df["IsSender"] == 0).sum()
    active_days = df["Date"].nunique()

    return {
        "total": total,
        "sent": sent,
        "received": received,
        "avg_active": round(total / active_days, 1),
        "start": df["dt"].min().strftime("%Y-%m-%d"),
        "end": df["dt"].max().strftime("%Y-%m-%d"),
    }


# ===================== 图表模块 =====================
def monthly_trend(df):
    set_font()
    data = df.groupby("Month").size().reindex(range(1, 13), fill_value=0)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data.index, data.values, marker="o")
    ax.set_title("月度聊天趋势")
    ax.set_xlabel("月份")
    ax.set_ylabel("消息数")
    ax.set_xticks(range(1, 13))
    ax.grid(alpha=0.3)

    return fig_to_base64(fig)


def yearly_heatmap(df):
    set_font()
    daily = df.groupby("Date").size()

    year_start = pd.Timestamp(f"{TARGET_YEAR}-01-01")
    all_days = pd.date_range(year_start, f"{TARGET_YEAR}-12-31", freq="D")

    full = pd.DataFrame({"Date": all_days})
    full["count"] = full["Date"].dt.date.map(daily).fillna(0).astype(int)
    full["day_index"] = (full["Date"] - year_start).dt.days
    full["week_index"] = full["day_index"] // 7
    full["weekday"] = full["Date"].dt.weekday

    heatmap = full.pivot(
        index="weekday", columns="week_index", values="count"
    )

    fig, ax = plt.subplots(figsize=(16, 3))
    sns.heatmap(
        heatmap,
        cmap="Greens",
        linewidths=0.3,
        linecolor="white",
        ax=ax
    )

    ax.set_yticks(range(7))
    ax.set_yticklabels(
        ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], rotation=0
    )
    ax.set_title("年度聊天活跃度热力图（GitHub 风格）")
    ax.set_xlabel("Week of Year")
    ax.set_ylabel("")

    return fig_to_base64(fig)


def wordcloud_plot(df):
    text = " ".join(df["StrContent"])
    stopwords = {
        "的","了","我","是","在","也","有","就","不","人",
        "我们","哈哈","哈哈哈","图片","视频"
    }
    words = [w for w in jieba.cut(text) if len(w) > 1 and w not in stopwords]
    if not words:
        return ""

    wc = WordCloud(
        font_path=FONT_PATH,
        width=900,
        height=400,
        background_color="white"
    ).generate(" ".join(words))

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.imshow(wc)
    ax.axis("off")
    return fig_to_base64(fig)


# ===================== 聊天对象画像 =====================
def analyze_single_talker(df, talker_id):
    sub = df[df["TalkerId"] == talker_id]
    if sub.empty:
        return None

    name = sub["NickName"].value_counts().idxmax()
    daily_counts = sub.groupby("Date").size()

    return {
        "talker_id": int(talker_id),
        "name": name,
        "total_msgs": int(len(sub)),
        "active_days": int(sub["Date"].nunique()),
        "first_date": str(sub["dt"].min().date()),
        "last_date": str(sub["dt"].max().date()),
        "max_daily_msgs": int(daily_counts.max()),
    }


def analyze_all_talkers(df):
    counts = df["TalkerId"].value_counts()
    profiles = []

    for tid in counts.index:
        p = analyze_single_talker(df, tid)
        if p:
            profiles.append(p)

    return profiles


# ===================== HTML 报告 =====================
def render_top_talkers_html(top_talkers):
    blocks = []
    for i, t in enumerate(top_talkers, start=1):
        blocks.append(f"""
        <div class="card">
        <h3>#{i} {t['name']}</h3>
        <ul>
          <li>年度消息数：{t['total_msgs']}</li>
          <li>活跃天数：{t['active_days']}</li>
          <li>时间跨度：{t['first_date']} → {t['last_date']}</li>
          <li>单日最高消息数：{t['max_daily_msgs']}</li>
        </ul>
        </div>
        """)
    return "\n".join(blocks)


def generate_html(metrics, charts, top_talkers):
    top_html = render_top_talkers_html(top_talkers)

    html = f"""
<html>
<head>
<meta charset="utf-8">
<title>{TARGET_YEAR} 微信年度报告</title>
<style>
body {{
  font-family: 'Microsoft YaHei', Arial;
  max-width: 900px;
  margin: auto;
  padding: 40px;
  background: #f7f9fc;
}}
.card {{
  background: white;
  padding: 30px;
  margin-bottom: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}}
h1 {{ text-align: center; }}
h2 {{ border-left: 5px solid #2ecc71; padding-left: 12px; }}
h3 {{ margin-top: 0; }}
img {{ max-width: 100%; }}
</style>
</head>

<body>

<h1>{TARGET_YEAR} 年度微信回忆录</h1>

<div class="card">
<h2>📊 核心统计</h2>
<ul>
<li>总消息数：{metrics["total"]}</li>
<li>我发送：{metrics["sent"]} ｜ 收到：{metrics["received"]}</li>
<li>活跃日均消息：{metrics["avg_active"]}</li>
</ul>
</div>

<div class="card"><h2>🏆 年度最常联系的聊天对象</h2>
{top_html}
</div>

<div class="card"><h2>📅 月度趋势</h2>
<img src="data:image/png;base64,{charts['monthly']}"></div>

<div class="card"><h2>🟩 年度热力图</h2>
<img src="data:image/png;base64,{charts['heatmap']}"></div>

<div class="card"><h2>💭 年度关键词</h2>
<img src="data:image/png;base64,{charts['wordcloud']}"></div>

<p style="text-align:center;color:#aaa;font-size:12px;">
Generated by Python · Chat Analysis
</p>

</body>
</html>
"""

    filename = f"WeChat_Report_{TARGET_YEAR}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML 报告生成完成：{filename}")


# ===================== 主程序 =====================
if __name__ == "__main__":
    df = load_data()
    if df.empty:
        print("⚠️ 该年份无数据")
        exit()

    metrics = summary_metrics(df)
    all_profiles = analyze_all_talkers(df)

    # 排序，选 Top N
    top_talkers = sorted(
        all_profiles,
        key=lambda x: x["total_msgs"],
        reverse=True
    )[:TOP_N_TALKERS]

    charts = {
        "monthly": monthly_trend(df),
        "heatmap": yearly_heatmap(df),
        "wordcloud": wordcloud_plot(df),
    }

    generate_html(metrics, charts, top_talkers)

    with open(
        f"talker_profiles_{TARGET_YEAR}.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(all_profiles, f, ensure_ascii=False, indent=2)

    print(f"✅ 已生成 talker_profiles_{TARGET_YEAR}.json")
