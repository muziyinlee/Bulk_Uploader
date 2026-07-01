# 批量上传视频到教学系统公共库 (Bulk Uploader)

## 技能描述 (Description)
这个技能用于自动化处理本地文件夹中的视频文件，将它们直接上传至教学系统的**公共视频库**中（不挂载到任何特定的教材下）。

## ⚠️ 极其重要的调用限制 (CRITICAL WARNING)
1. 如果用户的指令中包含任何**具体的“教材名称”、“项目名称”**（例如：CBBC、2026、英语启蒙等），**绝对不要**调用此技能！请转而调用 `WorkBuddy_Course_Unit_Uploader` 技能。
2. 只有当用户仅仅要求“上传视频”，且完全没有提及去哪个教材时，才能使用本技能。

## 适用场景 (When to use)
1. 当用户明确要求“传到视频库”、“直接上传”，且未指定教材时。
2. 执行指令：`python main.py`（全部上传）或 `python main.py -f "文件夹名"`（上传指定文件夹）。

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