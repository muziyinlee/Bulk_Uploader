from playwright.sync_api import sync_playwright

def setup_auth():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("🌐 浏览器已启动，正在打开目标网站...")
        page.goto("https://school.lingshi.com/")
        
        print("\n==================================================")
        print("🚨 请在弹出的浏览器中手动完成登录。")
        print("🚨 重点：一定要等到页面完全跳转，并能看到【后台首页】后，再进行下一步！")
        print("==================================================\n")
        
        # 核心修改：无限期暂停，等待你在终端按下回车键
        input("👉 登录完成后，请在此终端（命令行）按【回车键】以保存状态...")
        
        print("正在抓取并保存凭证，请稍候...")
        # 缓冲 2 秒，确保浏览器的异步 Cookie 写入彻底完成
        page.wait_for_timeout(2000) 
        
        # 保存登录状态到 auth.json
        context.storage_state(path="auth.json")
        print("✅ 登录状态抓取成功！已保存至 auth.json，你可以愉快地使用上传脚本了。")
        
        browser.close()

if __name__ == "__main__":
    setup_auth()