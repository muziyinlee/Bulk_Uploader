# 批量上传视频到教学系统 (Bulk Uploader)

## 技能描述 (Description)
这个技能用于自动化处理本地文件夹中的视频文件（支持mp4/mkv等），将它们上传至指定的教学系统后台。
支持“批量上传全部”和“精准上传单个指定文件夹”两种模式。

## 适用场景 (When to use)
1. 当用户要求“上传指定视频”、“把 [某个具体的动画片] 传到后台”时，提取用户提到的文件夹名称并作为参数传入。
2. 当用户要求“全部上传”、“把本地所有视频都上传”时，不加参数直接运行。

## 运行环境与依赖 (Requirements)
1. 依赖 Python 3.8+ 环境。
2. 运行前需要执行 `pip install -r requirements.txt` 和 `playwright install chromium` 安装环境。
3. 首次使用前需引导用户手动运行 `python auth_setup.py` 生成 `auth.json` 登录凭证。

## 执行指令 (Execution Command)
1. **上传特定文件夹（推荐）**：如果用户指定了文件夹名称（例如用户说“上传测试动画”），则提取名称并执行：
   `python main.py --folder "测试动画"`
2. **上传所有文件夹**：如果用户要求全部上传，则执行：
   `python main.py`

## 预期结果 (Expected Result)
脚本将自动拉起浏览器进行无头或有头操作，完成后控制台会打印“任务执行完毕”。