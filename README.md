# PhotoStyle Editor · 拾光

> 一款轻量、非破坏性的桌面照片风格编辑器。

[简体中文](README.md) | [English](README_EN.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-42668a)
![PySide6](https://img.shields.io/badge/PySide6-6.6%2B-41cd52)
![License](https://img.shields.io/badge/license-not%20specified-lightgrey)

PhotoStyle Editor（拾光）使用 Python、PySide6 和 Pillow 构建，提供从照片导入、风格调整、构图与裁剪到 PNG 导出的完整桌面工作流。编辑参数始终应用于原图，不会因反复切换滤镜而逐次降低画质。

## ✨ 功能亮点

- **批量导入**：支持拖放或文件选择，可一次导入多张照片。
- **常用图片格式**：支持 PNG、JPEG、WebP、TIFF 和 BMP。
- **RAW 照片读取**：支持 DNG、CR2/CR3、NEF、ARW、RAF、ORF、RW2 和 PEF。
- **7 种风格预设**：原图、胶片、INS 清新、风景、人像、黑白纪实和复古褪色。
- **可调滤镜强度**：在 0–100% 范围内控制风格效果。
- **构图辅助**：提供三分线、黄金分割、方格线和中心十字。
- **非破坏性裁剪**：支持自由比例、1:1、4:3、3:2、16:9 和 9:16，并可拖动裁剪框调整取景位置。
- **高分辨率导出**：可导出当前照片或批量导出 PNG；参考线仅用于预览，不会写入图片。

## 📋 环境要求

- Python 3.10 或更高版本
- 支持桌面图形界面的 Windows、macOS 或 Linux 环境
- 项目依赖：Pillow、PySide6、rawpy

> `rawpy` 用于读取 RAW 文件。标准格式的图像处理本身不依赖 RAW 解码，但使用项目提供的依赖文件安装时会一并安装 `rawpy`。

## 🚀 快速开始

### 1. 获取项目

```bash
git clone <repository-url>
cd PhotoStyleEditor
```

请将 `<repository-url>` 替换为本仓库的实际地址。如果已经下载项目，可直接进入项目目录。

### 2. 创建并激活虚拟环境

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. 安装依赖并启动

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m photostyle
```

安装项目后，也可以使用命令行入口启动：

```bash
python -m pip install -e .
photostyle
```

## 🖼️ 使用指南

1. 点击 **导入照片** 选择一个或多个文件，也可以把图片直接拖入窗口。
2. 从左侧照片库选择要编辑的照片。
3. 在右侧选择风格预设，并通过滑杆调整滤镜强度。
4. 按需启用构图参考线；参考线不会出现在导出文件中。
5. 选择裁剪比例，在预览区拖动裁剪框，然后点击 **应用裁剪**。
6. 点击 **导出当前 PNG** 保存当前照片，或点击 **批量导出** 将照片库中的全部照片输出到同一目录。

## 🧩 工作原理

每张已导入照片由 `PhotoDocument` 保存原图及滤镜、强度、裁剪比例和裁剪位置等编辑参数。预览和导出时，应用会根据这些参数从原图重新渲染，因此滤镜切换和裁剪都不会直接修改源文件。导出结果统一保存为 PNG。

## 📁 项目结构

```text
PhotoStyleEditor/
├── photostyle/
│   ├── __init__.py    # 包信息
│   ├── __main__.py    # 应用入口
│   ├── editor.py      # 图像读取、滤镜、裁剪与导出
│   └── window.py      # PySide6 桌面界面与交互
├── tests/
│   └── test_editor.py # 核心图像处理测试
├── pyproject.toml     # 项目元数据与打包配置
├── requirements.txt  # 运行依赖
├── README.md          # 中文说明
└── README_EN.md       # English documentation
```

## 🛠️ 开发与测试

安装项目及测试工具：

```bash
python -m pip install -e .
python -m pip install pytest
```

运行测试：

```bash
pytest -q
```

添加新滤镜时，在 `photostyle/editor.py` 中编写一个接收并返回 `PIL.Image.Image` 的转换函数，然后将对应的 `FilterPreset` 注册到 `FILTERS`。核心图像逻辑应尽量保持与图形界面解耦，并为新增行为补充测试。

## ⚠️ 当前限制

- 仅支持导出 PNG。
- 编辑参数只在当前运行期间保留，尚不支持保存和恢复项目。
- 批量导出会分别使用每张照片当前保存的编辑参数。
- 仓库目前未声明开源许可证；在复制、修改或分发代码前，请先向项目维护者确认授权方式。

## 🤝 参与贡献

欢迎通过 Issue 提交问题或建议，也欢迎提交 Pull Request。贡献代码前，请先运行测试并确保现有功能正常。
