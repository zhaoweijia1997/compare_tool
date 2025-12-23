# GitHub 网页上传指南

本文档说明如何在不安装 Git 的情况下，直接通过 GitHub 网页界面上传项目。

## 📦 准备上传的文件

### ✅ 必须上传的文件和文件夹：

```
compare_tool/
├── src/                    # 源代码文件夹（必须）
│   ├── __init__.py
│   ├── core/
│   ├── ui/
│   └── utils/
├── resources/              # 资源文件夹（必须）
│   ├── icons/
│   └── themes/
├── main.py                 # 主程序（必须）
├── requirements.txt        # 依赖列表（必须）
├── README.md              # 项目说明（必须）
├── README_EN.md           # 英文说明（必须）
├── LICENSE                # 许可证（必须）
├── .gitignore             # Git忽略规则（必须）
├── .gitattributes         # Git属性配置（推荐）
├── CHANGELOG.md           # 更新日志（推荐）
├── CONTRIBUTING.md        # 贡献指南（推荐）
├── build.bat              # Windows打包脚本（可选）
├── run.bat                # Windows运行脚本（可选）
└── install_and_run.bat    # 一键安装运行（可选）
```

### ❌ 不要上传的文件和文件夹：

```
❌ build/                  # PyInstaller 构建临时文件
❌ dist/                   # 打包生成的可执行文件（太大）
❌ __pycache__/            # Python 缓存
❌ .claude/                # Claude 配置文件
❌ *.spec                  # PyInstaller 规格文件（自动生成的）
❌ _nul                    # 临时文件
❌ *.pyc                   # 编译的 Python 文件
```

**注意**：`.gitignore` 文件已经配置好了，如果使用 Git 这些文件会自动被忽略。

## 🌐 GitHub 网页上传步骤

### 方式一：创建新仓库并上传（推荐）

#### 第 1 步：创建 GitHub 仓库

1. 登录 GitHub (https://github.com)
2. 点击右上角的 "+" → "New repository"
3. 填写仓库信息：
   - **Repository name**: `PyCompare` 或 `pycompare`
   - **Description**: `A powerful file and folder comparison tool | 强大的文件与文件夹比较工具`
   - **Public** 或 **Private**（推荐选 Public）
   - ⚠️ **不要勾选** "Add a README file"（我们已经有了）
   - ⚠️ **不要选择** .gitignore 和 license（我们已经有了）
4. 点击 "Create repository"

#### 第 2 步：准备要上传的文件

**方法 A：手动整理文件夹（简单）**

1. 创建一个新文件夹，命名为 `PyCompare-Upload`
2. 复制以下文件和文件夹到新文件夹：
   ```
   ✅ src/ 文件夹（整个）
   ✅ resources/ 文件夹（整个）
   ✅ main.py
   ✅ requirements.txt
   ✅ README.md
   ✅ README_EN.md
   ✅ LICENSE
   ✅ .gitignore
   ✅ .gitattributes
   ✅ CHANGELOG.md
   ✅ CONTRIBUTING.md
   ✅ build.bat
   ✅ run.bat
   ✅ install_and_run.bat
   ```
3. **不要复制**：`build/`、`dist/`、`.claude/`、`__pycache__/`、`*.spec`、`_nul`

**方法 B：使用压缩包（推荐）**

- 直接压缩当前项目为 zip，然后解压到新文件夹，手动删除不需要的文件

#### 第 3 步：上传到 GitHub

**选项 1：拖拽上传（最简单）**

1. 进入刚创建的空仓库页面
2. 点击 "uploading an existing file" 链接
3. 把准备好的所有文件和文件夹拖拽到网页中
4. 等待上传完成
5. 在底部填写：
   - Commit message: `Initial commit: PyCompare v1.0.0`
6. 点击 "Commit changes"

**选项 2：逐个上传**

1. 在仓库页面点击 "Add file" → "Upload files"
2. 拖拽文件到页面，或点击 "choose your files"
3. GitHub 支持一次上传多个文件，包括文件夹
4. 填写 commit message 并提交

⚠️ **注意**：GitHub 网页上传单个文件不能超过 25MB，整个上传不能超过 100 个文件。你的项目应该远小于这个限制。

#### 第 4 步：完善仓库信息

1. **添加 Topics（标签）**
   - 在仓库主页右侧，点击 "About" 旁边的齿轮图标
   - 添加 topics：`python`, `pyside6`, `diff-tool`, `file-comparison`, `developer-tools`

2. **编辑 About 描述**
   - 在同一个设置框中，填写简短描述
   - 可以选择添加项目网站（如果有）

#### 第 5 步：创建 Release（发布版本）

1. 在仓库页面右侧找到 "Releases" → 点击 "Create a new release"
2. 填写信息：
   - **Choose a tag**: 输入 `v1.0.0`（会自动创建）
   - **Release title**: `PyCompare v1.0.0 - Initial Release 🎉`
   - **Description**:
     ```markdown
     ## 🎉 首次发布

     PyCompare 是一个强大的文件与文件夹比较工具，类似 Beyond Compare。

     ### ✨ 主要功能
     - 文件逐行比较，字符级差异高亮
     - 文件夹递归比较
     - 现代化深色主题 UI
     - 语法高亮支持
     - 多种编码格式自动检测

     ### 📦 使用方法

     **方式一：下载可执行文件（Windows）**
     - 下载下方的 `PyCompare.exe`（如果你上传了）
     - 直接运行，无需安装 Python

     **方式二：源码运行**
     ```bash
     pip install -r requirements.txt
     python main.py
     ```

     查看 [README.md](README.md) 了解更多信息。
     ```
3. **附加文件**（可选）：
   - 如果你想提供可执行文件，可以上传 `dist/PyCompare.exe`
   - ⚠️ 注意：这个文件约 45MB，上传可能需要一些时间
4. 点击 "Publish release"

### 方式二：使用 GitHub Desktop（图形化工具）

如果觉得网页上传不方便，也可以使用 GitHub Desktop（无需命令行）：

1. 下载并安装 [GitHub Desktop](https://desktop.github.com/)
2. 登录你的 GitHub 账号
3. File → New Repository
4. 选择你的项目文件夹
5. Publish repository

## 📸 添加截图（强烈推荐）

截图可以让用户更直观地了解你的项目：

1. 运行 `python main.py`
2. 截取以下场景：
   - 主界面/欢迎页面
   - 文件比较视图（显示差异高亮）
   - 文件夹比较视图
3. 在仓库中创建 `screenshots` 文件夹
4. 上传截图（命名如：`main-window.png`, `file-diff.png`, `folder-diff.png`）
5. 编辑 README.md，在 "## 📸 截图" 部分添加：
   ```markdown
   ### 主界面
   ![Main Window](screenshots/main-window.png)

   ### 文件比较
   ![File Comparison](screenshots/file-diff.png)

   ### 文件夹比较
   ![Folder Comparison](screenshots/folder-diff.png)
   ```

## ✅ 上传检查清单

上传完成后，确认以下内容：

- [ ] README.md 显示正确
- [ ] 源代码文件夹（src/）已上传
- [ ] requirements.txt 存在
- [ ] LICENSE 文件存在
- [ ] .gitignore 文件存在（注意：以点开头的文件在 Windows 可能不可见）
- [ ] 没有上传 build/、dist/、__pycache__ 等临时文件
- [ ] 仓库描述和 Topics 已添加
- [ ] （可选）创建了第一个 Release

## 🎯 后续维护

### 如何更新代码

**方法 1：网页编辑单个文件**
1. 在仓库中找到要编辑的文件
2. 点击文件，然后点击铅笔图标（Edit）
3. 编辑后填写 commit message
4. 点击 "Commit changes"

**方法 2：上传新版本文件**
1. 在本地修改代码
2. 使用 "Add file" → "Upload files"
3. 上传修改过的文件（会自动覆盖）

### 如何发布新版本

1. 修改 CHANGELOG.md，记录更新内容
2. 在 Releases 页面创建新的 release
3. 使用新的标签号，如 `v1.1.0`

## ❓ 常见问题

**Q: 以点开头的文件（.gitignore）在 Windows 看不到怎么办？**
A: 在文件管理器的查看选项中，勾选 "显示隐藏的文件、文件夹和驱动器"。或者直接用记事本打开文件夹，可以看到所有文件。

**Q: 上传的文件太多怎么办？**
A: GitHub 网页上传限制是 100 个文件。如果超过，建议：
   - 使用 GitHub Desktop（无限制）
   - 或者分批上传，先上传文档和主文件，再上传 src/ 文件夹

**Q: 要不要上传 dist/PyCompare.exe？**
A:
   - ✅ 在 Release 中作为附件上传：推荐，方便用户直接下载使用
   - ❌ 不要提交到代码仓库：可执行文件太大（45MB），不适合版本控制

**Q: 如果以后想用 Git 怎么办？**
A: 可以随时切换：
   ```bash
   git clone https://github.com/your-username/pycompare.git
   cd pycompare
   # 之后就可以用 Git 命令了
   ```

## 📝 总结

最简单的上传流程：
1. ✅ 在 GitHub 创建新仓库（不要初始化任何文件）
2. ✅ 整理要上传的文件（删除 build/、dist/ 等）
3. ✅ 拖拽上传所有文件到 GitHub
4. ✅ 添加仓库描述和 Topics
5. ✅ （可选）创建 Release 并上传可执行文件

就这么简单！🎉
