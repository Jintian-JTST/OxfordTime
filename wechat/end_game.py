# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
import os
import time

# 目标还是那个 60MB 的解密文件
target_db = "de_MSG0.db"

print(f"🚀 正在启动透视模式，读取: {target_db}")

if not os.path.exists(target_db):
    print(f"❌ 找不到 {target_db}，请确认文件在当前目录下！")
else:
    try:
        conn = sqlite3.connect(target_db)
        
        # SQL升级：增加了 StrTalker 字段
        print("📊 正在分类提取聊天记录（包含群聊ID）...")
        query = """
        SELECT 
            StrTalker as ChatID,
            datetime(CreateTime, 'unixepoch', 'localtime') as Time,
            CASE IsSender 
                WHEN 1 THEN '我' 
                ELSE '对方/群友' 
            END as Sender,
            StrContent as Content
        FROM MSG
        WHERE Type = 1
        ORDER BY StrTalker, CreateTime ASC
        """
        
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            print("⚠️ 没有找到消息。")
        else:
            # 简单处理一下，把群聊和私聊标记出来
            def get_type(chat_id):
                if str(chat_id).endswith('@chatroom'):
                    return '[群聊]'
                elif str(chat_id).startswith('gh_'):
                    return '[公众号]'
                else:
                    return '[私聊]'

            df['Type'] = df['ChatID'].apply(get_type)
            
            # 调整列顺序，把类型放最前面
            df = df[['Type', 'ChatID', 'Time', 'Sender', 'Content']]
            
            csv_name = f"微信聊天记录_透视版_{int(time.time())}.csv"
            df.to_csv(csv_name, index=False, encoding='utf-8-sig')
            
            print("\n" + "🎉"*15)
            print(f" 导出成功！")
            print(f" 📅 共 {len(df)} 条记录")
            print(f" 💾 文件名: {csv_name}")
            print(" 💡 使用技巧：打开Excel后，使用'筛选'功能，在 ChatID 一列勾选你想看的群ID。")
            print("🎉"*15)
            
        conn.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")