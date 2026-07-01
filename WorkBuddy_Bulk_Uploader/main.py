import os
import time
import argparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ================= 配置区域 =================
BASE_DIR = r"D:\WorkBuddy\Animations"
TARGET_URL = "https://school.lingshi.com/" 
AUTH_FILE = "auth.json"
SUPPORTED_EXTENSIONS = ('.mp4', '.avi', '.mkv')
STEP_DELAY = 500  # 每步操作间的基础缓冲延时（毫秒），防动画遮挡与轻微卡顿
# ============================================

def process_folders(target_folder=None):
    if not os.path.exists(BASE_DIR):
        print(f"❌ 找不到项目路径: {BASE_DIR}")
        return

    if not os.path.exists(AUTH_FILE):
        print(f"❌ 找不到 {AUTH_FILE}，请先运行 auth_setup.py 登录。")
        return

    # 获取所有子文件夹
    all_folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
    if not all_folders:
        print("⚠️ 没有找到任何子文件夹。")
        return

    # 核心逻辑：如果指定了目标文件夹，则过滤列表
    if target_folder:
        if target_folder in all_folders:
            folders_to_process = [target_folder]
            print(f"🎯 收到指令，仅处理指定文件夹: {target_folder}")
        else:
            print(f"❌ 错误：在 {BASE_DIR} 下找不到名为 '{target_folder}' 的文件夹。")
            return
    else:
        folders_to_process = all_folders
        print(f"📂 未指定单一文件夹，将批量处理全部 {len(folders_to_process)} 个文件夹。")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=AUTH_FILE)
        page = context.new_page()

        for folder_name in folders_to_process:
            folder_path = os.path.join(BASE_DIR, folder_name)
            
            files_to_upload = [
                os.path.join(folder_path, f) 
                for f in os.listdir(folder_path) 
                if f.lower().endswith(SUPPORTED_EXTENSIONS)
            ]

            if not files_to_upload:
                print(f"⏩ 跳过 {folder_name}：未找到音视频文件。")
                continue

            print(f"\n🚀 开始处理: {folder_name} (包含 {len(files_to_upload)} 个文件)")
            
            try:
                # 1. 访问系统首页
                print("  -> 打开系统页面...")
                page.goto(TARGET_URL)
                page.wait_for_load_state('domcontentloaded')
                page.wait_for_timeout(2000) 

                # 2. 点击 教学
                print("  -> 步骤1：点击【教学】菜单...")
                page.locator("div.title", has_text="教学").click()
                page.wait_for_timeout(STEP_DELAY + 500) 
                
                # 3. 点击 自制教材
                print("  -> 步骤2：点击【自制教材】...")
                page.locator("#textbookMine").click()
                page.wait_for_timeout(2000) 

                # 3.5 点击 视频 Tab 标签
                print("  -> 步骤3：切换至【视频】标签页...")
                page.locator("#tab-video").click()
                page.wait_for_timeout(STEP_DELAY + 1000) 

                # 4. 点击 去制作
                print("  -> 步骤4：点击【去制作】...")
                page.locator("button.el-button", has_text="去制作").click()
                page.wait_for_timeout(STEP_DELAY + 1000) 

                # 5. 输入对应的名称
                print(f"  -> 步骤5：输入名称 [{folder_name}]...")
                page.get_by_placeholder("请输入名称").fill(folder_name)
                page.wait_for_timeout(STEP_DELAY)

                # 6. 选择对应的文件夹及批量视频
                print("  -> 步骤6：点击【本地上传】并注入文件...")
                with page.expect_file_chooser() as fc_info:
                    page.locator("button.el-button", has_text="本地上传").click()
                file_chooser = fc_info.value
                file_chooser.set_files(files_to_upload)
                page.wait_for_timeout(STEP_DELAY)
                
                # 7. 待上传完成后点击确认
                print("  -> 步骤7：文件上传中，无限期等待【确认】按钮激活...")
                confirm_btn = page.locator("button.el-button", has_text="确认")
                confirm_btn.first.click(timeout=0) 
                print("  -> 【确认】点击成功！上传完毕。")
                page.wait_for_timeout(STEP_DELAY + 500) 

                # 8. 暂存
                print("  -> 步骤8：点击【暂存】...")
                page.locator("button.el-button", has_text="暂存").click()
                
                # 给予弹窗充分的弹出动画时间
                page.wait_for_timeout(STEP_DELAY + 1000) 
                
                # 9. 暂存后的二次确认弹窗
                print("  -> 步骤9：点击暂存后的【确认】弹窗...")
                all_confirm_btns = page.locator("button.el-button", has_text="确认").all()
                clicked = False
                for btn in all_confirm_btns:
                    if btn.is_visible():
                        btn.click()
                        clicked = True
                        break 
                
                if not clicked:
                    print("  -> ⚠️ 警告：未找到可见的确认按钮！")

                print(f"✅ {folder_name} 已成功处理并暂存！")
                
                # 留出时间让后台处理暂存请求，准备下一个循环
                page.wait_for_timeout(3000)

            except PlaywrightTimeoutError:
                print(f"❌ 处理 {folder_name} 时发生超时错误，请观察浏览器停在了哪一步。")
            except Exception as e:
                print(f"❌ 处理 {folder_name} 时发生未知错误: {e}")

        print("\n🎉 任务执行完毕！")
        print("💡 浏览器将保持开启状态供你检查。")
        input("👉 检查完毕后，请在此终端按【回车键】以结束脚本并关闭浏览器...")

if __name__ == "__main__":
    # 配置命令行参数解析
    parser = argparse.ArgumentParser(description="批量上传视频到教学系统")
    parser.add_argument("-f", "--folder", type=str, help="指定要上传的特定文件夹名称（不填则处理所有文件夹）", default=None)
    
    args = parser.parse_args()
    
    # 将解析到的文件夹名称传入主函数
    process_folders(target_folder=args.folder)