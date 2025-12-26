from pywxdump import get_wx_info
import os

# 忽略烦人的 protobuf 警告
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

def main():
    print("正在尝试获取微信信息，请确保微信已登录...")
    try:
        # 核心方法：获取所有登录账号的信息（包含密钥）
        infos = get_wx_info()
        
        if not infos:
            print("未检测到运行中的微信，请先登录 PC 微信。")
            return

        print(f"\n检测到 {len(infos)} 个微信账号：")
        for i, info in enumerate(infos):
            print(f"\n--- 账号 {i+1} ---")
            print(f"昵称: {info.get('name')}")
            print(f"账号(wxid): {info.get('wxid')}")
            print(f"密钥(Key): {info.get('key')}")  # <--- 这里就是你要的 Key
            print(f"数据库路径: {info.get('db_path')}")
            
    except Exception as e:
        print(f"发生错误: {e}")
        print("建议：请尝试以【管理员身份】运行 PowerShell 再执行此脚本。")

if __name__ == "__main__":
    main()