from playwright.sync_api import sync_playwright

def setup_auth():
    with sync_playwright() as p:
        # 启动浏览器（有头模式，方便手动操作）
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("请在弹出的浏览器中完成登录操作...")
        page.goto("https://school.lingshi.com/")
        
        # 等待60秒让你有足够的时间手动登录
        page.wait_for_timeout(60000) 
        
        # 保存登录状态到 auth.json
        context.storage_state(path="auth.json")
        print("登录状态已保存至 auth.json，你可以关闭此窗口了。")
        browser.close()

if __name__ == "__main__":
    setup_auth()