# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
import os
import time

# 这里对应刚才 wxdump 生成的文件名
db_file = "final.db"

if not os.path.exists(db_file):
    print(f"❌ 没找到 {db_file}，请确认上一步 wxdump decrypt 命令执行成功！")
else:
    try:
        # 连接数据库
        conn = sqlite3.connect(db_file)
        
        # SQL语句：提取时间、发送者、内容
        # 并且只提取 Type=1 (文本消息)，过滤掉图片/系统消息等乱码
        query = """
        SELECT 
            datetime(CreateTime, 'unixepoch', 'localtime') as Time,
            CASE IsSender WHEN 1 THEN '我' ELSE '对方' END as Sender,
            StrContent as Content
        FROM MSG
        WHERE Type = 1
        ORDER BY CreateTime ASC
        """
        
        # 读取数据
        print("📊 正在提取聊天记录...")
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            print("⚠️ 数据库打开了，但是没有读到文本消息。")
        else:
            # 导出 CSV (Excel可打开)
            csv_name = f"聊天记录_最终版_{int(time.time())}.csv"
            df.to_csv(csv_name, index=False, encoding='utf-8-sig')
            
            print("\n" + "="*40)
            print(f"🎉 成功！聊天记录已导出！")
            print(f"📄 文件名: {csv_name}")
            print(f"🔢 共 {len(df)} 条消息")
            print("="*40)
            
        conn.close()
        
    except Exception as e:
        print(f"❌ 出错啦: {e}")