# PhotoStyle Editor · 拾光

一个基于 Python 的桌面端照片风格编辑器框架。它提供批量导入、流行风格滤镜、强度调整、构图参考线、常用比例裁剪以及 PNG 导出。

![Python](https://img.shields.io/badge/Python-3.10%2B-42668a)
![PySide](https://img.shields.io/badge/UI-PySide6-6fbe44)

## 功能

- 批量读取 PNG/JPEG/WebP/TIFF/BMP 与常见 RAW（DNG、CR2/CR3、NEF、ARW、RAF、ORF等）。
- 胶片、INS 清新、风景、人像、黑白纪实、复古褪色等可扩展滤镜，支持 0–100% 强度。
- 三分线、黄金分割、中心十字和方格线叠加。
- 自由、1:1、4:3、3:2、16:9 以及 9:16 裁剪。
- 单张或批量导出 PNG，输出保留完整分辨率。
- 所有编辑均使用原图重算，切换滤镜不会反复损伤画质。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m photostyle
```

> RAW 支持由 `rawpy` 提供。如果当前系统无法安装 `rawpy`，仍可正常编辑 PNG/JPEG 等标准格式。

## 使用方法

1. 点击「导入照片」并多选文件，或直接将图片拖入窗口。
2. 在左侧选择照片，在右侧选择风格并拖动强度滑杆。
3. 可选择参考线；选定裁剪比例后，在图片上拖动裁剪框调整取景，再点击「应用裁剪」。
4. 点击「导出 PNG」或「批量导出」。

## 项目结构

```text
photostyle/
├── __main__.py    # 应用入口
├── editor.py      # 非破坏性图像处理与文件读写
└── window.py      # PySide6 桌面界面
tests/
└── test_editor.py # 核心算法测试
```

## 开发

```bash
pytest -q
```

过滤配方集中在 `photostyle/editor.py` 的 `FILTERS` 中，新风格只需添加一个同签名函数和对应的 `FilterPreset`。
