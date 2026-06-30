# 批量上传视频到教学系统 (Bulk Uploader)

## 技能描述 (Description)
这个技能用于自动化处理本地文件夹中的视频文件（支持mp4/mkv等），将它们批量上传至指定的教学系统后台，并自动完成“去制作”、“切换视频Tab”、“暂存”等一系列复杂的网页端点击操作。

## 适用场景 (When to use)
当用户要求“上传视频”、“批量上传视频到后台”、“把D盘的视频上传到校区系统”时，触发此技能。

## 运行环境与依赖 (Requirements)
1. 依赖 Python 3.8+ 环境。
2. 运行前需要执行 `pip install -r requirements.txt` 和 `playwright install chromium` 安装环境。
3. 首次使用前需引导用户手动运行 `python auth_setup.py` 生成 `auth.json` 登录凭证。

## 执行指令 (Execution Command)
使用系统终端直接运行核心脚本：
`python main.py`

## 预期结果 (Expected Result)
脚本将自动拉起浏览器进行无头或有头操作，完成后控制台会打印“全部文件夹批量处理完毕”。