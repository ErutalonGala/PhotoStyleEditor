# PhotoStyle Editor · 拾光

> A lightweight, non-destructive desktop editor for styling photos.

[简体中文](README.md) | [English](README_EN.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-42668a)
![PySide6](https://img.shields.io/badge/PySide6-6.6%2B-41cd52)
![License](https://img.shields.io/badge/license-not%20specified-lightgrey)

PhotoStyle Editor is built with Python, PySide6, and Pillow. It provides a focused desktop workflow that covers importing photos, applying styles, composing and cropping, and exporting PNG files. Every edit is rendered from the original image, so switching presets repeatedly does not progressively degrade image quality.

## ✨ Highlights

- **Batch import:** add multiple photos through the file picker or drag and drop.
- **Common image formats:** open PNG, JPEG, WebP, TIFF, and BMP files.
- **RAW decoding:** open DNG, CR2/CR3, NEF, ARW, RAF, ORF, RW2, and PEF files.
- **Seven style presets:** Original, Film, INS Fresh, Landscape, Portrait, Documentary B&W, and Faded Vintage.
- **Adjustable intensity:** blend each preset from 0% to 100%.
- **Composition guides:** overlay a rule-of-thirds grid, golden-ratio grid, square grid, or center cross.
- **Non-destructive cropping:** choose Free/Original, 1:1, 4:3, 3:2, 16:9, or 9:16 and drag the crop area into position.
- **Full-resolution output:** export the current image or a whole batch as PNG. Guides are preview-only and never appear in exported files.

## 📋 Requirements

- Python 3.10 or later
- Windows, macOS, or Linux with a graphical desktop environment
- Project dependencies: Pillow, PySide6, and rawpy

> `rawpy` provides RAW file support. Processing standard image formats does not itself require RAW decoding, although `rawpy` is installed when you use the dependency files included in this project.

## 🚀 Quick Start

### 1. Get the project

```bash
git clone <repository-url>
cd PhotoStyleEditor
```

Replace `<repository-url>` with the actual repository URL. If you already downloaded the project, simply open its directory.

### 2. Create and activate a virtual environment

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

### 3. Install dependencies and launch

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m photostyle
```

After installing the project, you can also use its command-line entry point:

```bash
python -m pip install -e .
photostyle
```

## 🖼️ How to Use

1. Select **Import Photos** and choose one or more files, or drag image files directly into the window.
2. Select the photo you want to edit from the library on the left.
3. Choose a style preset on the right and adjust its intensity with the slider.
4. Enable a composition guide if needed. Guides are not included in the exported image.
5. Select an aspect ratio, drag the crop frame in the preview, and select **Apply Crop**.
6. Select **Export Current PNG** to save one photo, or **Batch Export** to write every photo in the library to one directory.

> The current application interface uses Simplified Chinese labels. The English button names above describe their Chinese counterparts in the UI.

## 🧩 How It Works

Each imported photo is represented by a `PhotoDocument`, which retains the original pixels along with the selected filter, intensity, crop ratio, and crop position. Previews and exports are rendered again from the original using those settings. Filters and crops therefore leave the source file untouched. All exported images are written as PNG files.

## 📁 Project Layout

```text
PhotoStyleEditor/
├── photostyle/
│   ├── __init__.py    # Package metadata
│   ├── __main__.py    # Application entry point
│   ├── editor.py      # Loading, filters, cropping, and export
│   └── window.py      # PySide6 desktop UI and interactions
├── tests/
│   └── test_editor.py # Core image-processing tests
├── pyproject.toml     # Package metadata and build configuration
├── requirements.txt  # Runtime dependencies
├── README.md          # Chinese documentation
└── README_EN.md       # English documentation
```

## 🛠️ Development and Testing

Install the project and the test runner:

```bash
python -m pip install -e .
python -m pip install pytest
```

Run the test suite:

```bash
pytest -q
```

To add a filter, define a transform in `photostyle/editor.py` that accepts and returns a `PIL.Image.Image`, then register a matching `FilterPreset` in `FILTERS`. Keep core image logic independent from the GUI where possible, and add tests for new behavior.

## ⚠️ Current Limitations

- PNG is the only export format.
- Editing settings only last for the current session; projects cannot yet be saved and reopened.
- Batch export uses the editing settings currently stored for each individual photo.
- This repository does not currently declare an open-source license. Ask the maintainer about permission before copying, modifying, or distributing the code.

## 🤝 Contributing

Issues and suggestions are welcome, as are pull requests. Before submitting code, run the test suite and confirm that existing behavior still works.
