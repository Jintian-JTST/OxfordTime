# -*- coding: utf-8 -*-
import os
import sys

# 忽略 protobuf 警告
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

def main():
    print("正在尝试读取微信信息，请保持微信窗口在前台...")
    
    try:
        from pywxdump import get_wx_info
        
        # 获取信息
        infos = get_wx_info()
        
        if not infos:
            print("\n❌ 未检测到微信，请确认微信已登录。")
            return

        print(f"\n🔎 检测到 {len(infos)} 个微信进程。")
        
        found_key = False
        
        for i, info in enumerate(infos):
            print(f"\n-------- 进程 {i+1} --------")
            pid = info.get('pid', '未知')
            name = info.get('name', '未知')
            key = info.get('key')
            db_path = info.get('db_path', '未找到')
            
            print(f"PID (进程ID): {pid}")
            print(f"昵称: {name}")
            print(f"数据库路径: {db_path}")
            
            if key:
                print(f"✅ 【密钥 (Key)】: {key}")
                found_key = True
                # 保存 Key 到文件
                with open("key.txt", "w", encoding="utf-8") as f:
                    f.write(key)
                print("   (密钥已保存到 key.txt)")
            else:
                print("❌ 此进程未读取到密钥 (可能是僵尸进程或权限不足)")
                
        print("\n-----------------------------")
        if found_key:
            print("🎉 成功！请使用上面的 Key 修改您的导出脚本。")
        else:
            print("⚠️ 依然没有拿到 Key？")
            print("请尝试：右键点击 PowerShell -> 以管理员身份运行，再次执行本脚本。")

    except ImportError:
        print("未安装 pywxdump")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()