import os
import argparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ================= 配置区域 =================
BASE_DIR = r"D:\WorkBuddy\Animations"
TARGET_URL = "https://school.lingshi.com/" 
AUTH_FILE = "auth.json"
SUPPORTED_EXTENSIONS = ('.mp4', '.avi', '.mkv')
STEP_DELAY = 500  # 每步操作间的基础缓冲延时（毫秒），防动画遮挡与轻微卡顿
# ============================================

def process_folders(target_course, target_folder=None):
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

            print(f"\n🚀 开始处理: {folder_name} (包含 {len(files_to_upload)} 个文件) -> 目标教材: {target_course}")
            
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

                # 4. 在搜索框中输入项目名称并搜索
                print(f"  -> 步骤3：在搜索框输入教材关键词 [{target_course}]...")
                page.get_by_placeholder("请输入教材名称").fill(target_course)
                page.wait_for_timeout(STEP_DELAY)
                
                # 点击搜索图标
                print("  -> 步骤4：点击【搜索】图标...")
                page.locator(".el-input__suffix .ls-icon").first.click()
                page.wait_for_timeout(2000)

                # 5. 多关键词匹配逻辑：检索满足所有关键词的标题并点击
                print("  -> 步骤5：检索并进入符合要求的教材...")
                keywords = target_course.split()
                # 基础定位器，寻找包含第一个关键词的元素
                course_locator = page.locator("div, span, a").filter(has_text=keywords[0])
                # 链式过滤后续关键词
                for kw in keywords[1:]:
                    course_locator = course_locator.filter(has_text=kw)
                # 点击匹配结果中的第一个
                course_locator.first.click()
                page.wait_for_timeout(STEP_DELAY + 1000)

                # 6. 点击 添加单元
                print("  -> 步骤6：点击【添加单元】...")
                page.locator("button.el-button", has_text="添加单元").click()
                page.wait_for_timeout(STEP_DELAY + 500)

                # 7. 输入单元名称（以当前文件夹命名）并确认
                print(f"  -> 步骤7：输入单元名称 [{folder_name}] 并确认...")
                page.get_by_placeholder("请输入名称，限制50字内").fill(folder_name)
                page.wait_for_timeout(STEP_DELAY)
                # 寻找弹窗内的确认按钮并点击
                page.locator("button.el-button", has_text="确认").click()
                page.wait_for_timeout(STEP_DELAY + 1000)

                # 8. 在新增的单元行中点击“本地上传”
                print("  -> 步骤8：在对应单元行点击【本地上传】并注入文件...")
                # 精准定位：找到包含文件夹名称的那一行
                unit_row = page.locator("div.el-tree-node__content").filter(has_text=folder_name).first
                
                with page.expect_file_chooser() as fc_info:
                    unit_row.locator("button.el-button", has_text="本地上传").click()
                file_chooser = fc_info.value
                file_chooser.set_files(files_to_upload)
                page.wait_for_timeout(STEP_DELAY)
                
                # 9. 待上传完成后点击确认（复用原有逻辑）
                print("  -> 步骤9：文件上传中，无限期等待【确认】按钮激活...")
                confirm_btn = page.locator("button.el-button", has_text="确认")
                confirm_btn.first.click(timeout=0) 
                print("  -> 【确认】点击成功！上传完毕。")
                page.wait_for_timeout(STEP_DELAY + 500) 

                # 10. 暂存
                print("  -> 步骤10：点击【暂存】...")
                page.locator("button.el-button", has_text="暂存").click()
                page.wait_for_timeout(STEP_DELAY + 1000) 
                
                # 11. 暂存后的二次确认弹窗
                print("  -> 步骤11：点击暂存后的【确认】弹窗...")
                all_confirm_btns = page.locator("button.el-button", has_text="确认").all()
                clicked = False
                for btn in all_confirm_btns:
                    if btn.is_visible():
                        btn.click()
                        clicked = True
                        break 
                
                if not clicked:
                    print("  -> ⚠️ 警告：未找到可见的确认按钮！")

                print(f"✅ {folder_name} 已成功作为单元添加并暂存！")
                page.wait_for_timeout(3000)

            except PlaywrightTimeoutError:
                print(f"❌ 处理 {folder_name} 时发生超时错误，请观察浏览器停在了哪一步。")
            except Exception as e:
                print(f"❌ 处理 {folder_name} 时发生未知错误: {e}")

        print("\n🎉 任务执行完毕！")
        print("💡 浏览器将保持开启状态供你检查。")
        input("👉 检查完毕后，请在此终端按【回车键】以结束脚本并关闭浏览器...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="指定教材新建单元并上传视频")
    # 新增了教材名称的强制参数
    parser.add_argument("-c", "--course", type=str, required=True, help="要搜索并上传至的目标教材名称 (支持多关键词空格分隔，如 'CBBC 2026')")
    parser.add_argument("-f", "--folder", type=str, help="指定要上传的特定文件夹名称（不填则处理所有文件夹）", default=None)
    
    args = parser.parse_args()
    
    process_folders(target_course=args.course, target_folder=args.folder)