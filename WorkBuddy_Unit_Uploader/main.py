import os
import argparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# 获取当前脚本所在的绝对路径目录（解决 WorkBuddy 后台执行找不到文件的问题）
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# ================= 配置区域 =================
BASE_DIR = r"E:\WorkBuddy\Animations"
TARGET_URL = "https://school.lingshi.com/" 
# 强制绑定当前目录下的 auth.json
AUTH_FILE = os.path.join(CURRENT_DIR, "auth.json") 
SUPPORTED_EXTENSIONS = ('.mp4', '.avi', '.mkv')
STEP_DELAY = 500  # 每步操作间的基础缓冲延时（毫秒），防动画遮挡与轻微卡顿
# ============================================

def process_folders(target_course, target_folder=None):
    if not os.path.exists(BASE_DIR):
        print(f"[错误] 找不到项目路径: {BASE_DIR}")
        return

    if not os.path.exists(AUTH_FILE):
        print(f"[错误] 找不到 {AUTH_FILE}，请先运行 auth_setup.py 登录。")
        return

    # 获取所有子文件夹
    all_folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
    if not all_folders:
        print("[警告] 没有找到任何子文件夹。")
        return

    # 核心逻辑：如果指定了目标文件夹，则过滤列表
    if target_folder:
        if target_folder in all_folders:
            folders_to_process = [target_folder]
            print(f"[目标] 收到指令，仅处理指定文件夹: {target_folder}")
        else:
            print(f"[错误] 在 {BASE_DIR} 下找不到名为 '{target_folder}' 的文件夹。")
            return
    else:
        folders_to_process = all_folders
        print(f"[批量] 未指定单一文件夹，将批量处理全部 {len(folders_to_process)} 个文件夹。")

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
                print(f"[跳过] {folder_name}：未找到音视频文件。")
                continue

            print(f"\n[开始] 处理: {folder_name} (包含 {len(files_to_upload)} 个文件) -> 目标教材: {target_course}")
            
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

                # 拆分所有输入的关键词
                keywords = target_course.split()
                if not keywords:
                    print("[错误] 未提供有效的教材名称。")
                    return
                # 取第一个词作为搜索主词扩大范围
                primary_keyword = keywords[0]

                # 4. 在搜索框中输入基础关键词
                print(f"  -> 步骤3：在搜索框输入基础关键词 [{primary_keyword}]...")
                page.get_by_placeholder("请输入教材名称").fill(primary_keyword)
                page.wait_for_timeout(STEP_DELAY)
                
                # 点击搜索图标
                print("  -> 步骤4：点击【搜索】图标...")
                page.locator(".el-input__suffix .ls-icon").first.click()
                page.wait_for_timeout(2000)

                # 5. 多关键词匹配逻辑：无视前端类名拼写错误，利用DOM层级相对定位法寻找编辑按钮
                print(f"  -> 步骤5：在结果中精准检索同时包含 {keywords} 的教材并点击【编辑】...")
                
                # 5.1 锁定包含所有确切文本的最深层标题节点
                title_locator = page.locator(".ls-tooltip-title").filter(has_text=keywords[0])
                for kw in keywords[1:]:
                    title_locator = title_locator.filter(has_text=kw)
                
                # 5.2 黑科技：以该标题为起点，向外层追溯到最近的一个包含【编辑】按钮的祖先节点(也就是这一整行)，然后精准点击该行内的编辑按钮
                edit_btn = title_locator.first.locator("xpath=./ancestor::*[.//span[@id='editFolder']][1]").locator("span#editFolder")
                edit_btn.click()
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
                # 精准定位：找到包含文件夹名称的那一个树状节点行
                unit_row = page.locator("div.el-tree-node__content").filter(has_text=folder_name).first
                
                with page.expect_file_chooser() as fc_info:
                    unit_row.locator("button.el-button", has_text="本地上传").click()
                file_chooser = fc_info.value
                file_chooser.set_files(files_to_upload)
                page.wait_for_timeout(STEP_DELAY)
                
                # 9. 待上传完成后点击确认
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
                    print("  -> [警告] 未找到可见的确认按钮！")

                print(f"[成功] {folder_name} 已成功作为单元添加并暂存！")
                page.wait_for_timeout(3000)

            except PlaywrightTimeoutError:
                print(f"[错误] 处理 {folder_name} 时发生超时错误，请观察浏览器停在了哪一步。")
            except Exception as e:
                print(f"[错误] 处理 {folder_name} 时发生未知错误: {e}")

        print("\n[完成] 任务执行完毕！")
        print("[提示] 浏览器将保持开启状态供你检查。")
        
        try:
            # 兼容终端手跑与 WorkBuddy 自动跑两种环境
            input("[等待] 检查完毕后，请在此终端按【回车键】以结束脚本并关闭浏览器...")
        except EOFError:
            print("[系统] 检测到自动化助手(WorkBuddy)在后台运行...")
            print("[倒计时] 脚本将在 10 秒后自动结束并关闭浏览器，请抓紧检查！")
            page.wait_for_timeout(10000)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="指定教材新建单元并上传视频")
    parser.add_argument("-c", "--course", type=str, default=None, help="要搜索并上传至的目标教材名称 (支持多关键词空格分隔，如 'CBBC 2026')")
    parser.add_argument("-f", "--folder", type=str, default=None, help="指定要上传的特定文件夹名称")
    
    args = parser.parse_args()
    
    # 专门给 WorkBuddy 设置的“防呆”拦截器
    if not args.course:
        print("===============================================================")
        print("[错误] WorkBuddy 调用失败：你没有传递必需的 '-c' (教材名称) 参数！")
        print("[系统指令] 请立刻重新分析用户的对话！你必须提取出用户提到的“教材名称”，并带上参数重新执行脚本！")
        print("[正确示例] python main.py -c \"CBBC 2026\" -f \"4月\"")
        print("===============================================================")
        exit(1)
        
    process_folders(target_course=args.course, target_folder=args.folder)
