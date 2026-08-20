"""Modern PySide6 user interface for PhotoStyle Editor."""

from __future__ import annotations

from pathlib import Path

from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QDragEnterEvent, QDropEvent, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QMainWindow, QMessageBox, QPushButton, QScrollArea, QSlider,
    QStatusBar, QVBoxLayout, QWidget,
)

from .editor import FILTERS, SUPPORTED_EXTENSIONS, PhotoDocument

RATIOS = {"自由 / 原始": None, "1 : 1": (1, 1), "4 : 3": (4, 3), "3 : 2": (3, 2), "16 : 9": (16, 9), "9 : 16": (9, 16)}

STYLE = """
* { font-family: "Noto Sans CJK SC", "Microsoft YaHei", sans-serif; color: #e9e7e1; }
QMainWindow, QWidget#root { background: #171918; }
QFrame#topbar { background: #202321; border-bottom: 1px solid #323632; }
QLabel#brand { font-size: 21px; font-weight: 700; color: #f5f1e7; }
QLabel#brandMark { background: #c8ff71; color: #182015; font-size: 18px; font-weight: 900; border-radius: 7px; padding: 6px 9px; }
QLabel#eyebrow { color: #8b928c; font-size: 10px; font-weight: 700; }
QLabel#section { font-size: 14px; font-weight: 700; color: #f2f0eb; }
QLabel#muted, QLabel#meta { color: #858b86; font-size: 11px; }
QFrame#sidebar, QFrame#inspector { background: #1c1f1d; }
QFrame#canvas { background: #111312; border: 1px solid #292c2a; border-radius: 10px; }
QPushButton { background: #292d2a; border: 1px solid #383d39; border-radius: 7px; padding: 8px 14px; font-weight: 600; }
QPushButton:hover { background: #343a35; border-color: #4a514b; }
QPushButton#primary { background: #c8ff71; color: #172010; border: 0; padding: 9px 16px; }
QPushButton#primary:hover { background: #d4ff91; }
QPushButton#filter { text-align: left; padding: 10px; background: #242725; border: 1px solid #303431; }
QPushButton#filter:checked { background: #31372f; border: 1px solid #9dc95c; color: #eaffcb; }
QListWidget { background: transparent; border: 0; outline: 0; }
QListWidget::item { background: #252826; border-radius: 7px; margin: 3px 5px; padding: 10px; }
QListWidget::item:selected { background: #343a34; border-left: 3px solid #c8ff71; }
QComboBox { background: #272a28; border: 1px solid #383c39; border-radius: 6px; padding: 7px 9px; }
QComboBox::drop-down { border: 0; width: 22px; }
QComboBox QAbstractItemView { background: #252825; selection-background-color: #3d4639; }
QSlider::groove:horizontal { height: 4px; background: #3b403c; border-radius: 2px; }
QSlider::handle:horizontal { width: 16px; margin: -6px 0; background: #c8ff71; border-radius: 8px; }
QSlider::sub-page:horizontal { background: #a5d65c; }
QStatusBar { background: #1d201e; color: #858b86; }
QScrollArea { border: 0; background: transparent; }
"""


class PreviewCanvas(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("canvas")
        self.setMinimumSize(560, 420)
        self._pixmap: QPixmap | None = None
        self.guide = "无"

    def set_image(self, image) -> None:
        qimage = QImage(ImageQt(image))
        self._pixmap = QPixmap.fromImage(qimage)
        self.update()

    def clear_image(self) -> None:
        self._pixmap = None
        self.update()

    def image_rect(self):
        if not self._pixmap:
            return None
        scaled = self._pixmap.size().scaled(self.size(), Qt.KeepAspectRatio)
        x, y = (self.width() - scaled.width()) // 2, (self.height() - scaled.height()) // 2
        return x, y, scaled.width(), scaled.height()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        rect = self.image_rect()
        if not self._pixmap or not rect:
            painter.setPen(QColor("#737a74"))
            painter.drawText(self.rect(), Qt.AlignCenter, "导入一组照片\n开始你的创作")
            return
        x, y, w, h = rect
        painter.drawPixmap(x, y, w, h, self._pixmap)
        if self.guide == "无":
            return
        painter.setPen(QPen(QColor(255, 255, 255, 185), 1))
        vertical, horizontal = [], []
        if self.guide == "三分线":
            vertical, horizontal = [1 / 3, 2 / 3], [1 / 3, 2 / 3]
        elif self.guide == "黄金分割":
            vertical, horizontal = [0.382, 0.618], [0.382, 0.618]
        elif self.guide == "方格线":
            vertical = horizontal = [i / 6 for i in range(1, 6)]
        elif self.guide == "中心十字":
            vertical, horizontal = [0.5], [0.5]
        for position in vertical:
            painter.drawLine(round(x + w * position), y, round(x + w * position), y + h)
        for position in horizontal:
            painter.drawLine(x, round(y + h * position), x + w, round(y + h * position))

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update()


class EditorWindow(QMainWindow):
    documents_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.documents: list[PhotoDocument] = []
        self.current_index = -1
        self.setWindowTitle("拾光 · PhotoStyle Editor")
        self.resize(1440, 900)
        self.setMinimumSize(1080, 700)
        self.setAcceptDrops(True)
        self.setStyleSheet(STYLE)
        self._build_ui()
        self._set_controls_enabled(False)

    @property
    def current(self) -> PhotoDocument | None:
        return self.documents[self.current_index] if 0 <= self.current_index < len(self.documents) else None

    def _build_ui(self) -> None:
        root = QWidget(objectName="root")
        outer = QVBoxLayout(root); outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)
        topbar = QFrame(objectName="topbar"); topbar.setFixedHeight(70)
        top = QHBoxLayout(topbar); top.setContentsMargins(20, 12, 20, 12)
        mark = QLabel("拾", objectName="brandMark"); brand = QLabel("拾光  PhotoStyle", objectName="brand")
        top.addWidget(mark); top.addWidget(brand); top.addStretch()
        self.batch_button = QPushButton("批量导出"); self.batch_button.clicked.connect(self.export_batch)
        import_button = QPushButton("＋  导入照片", objectName="primary"); import_button.clicked.connect(self.choose_files)
        top.addWidget(self.batch_button); top.addWidget(import_button); outer.addWidget(topbar)
        content = QHBoxLayout(); content.setContentsMargins(0, 0, 0, 0); content.setSpacing(0)
        content.addWidget(self._build_library())
        center = QWidget(); center_layout = QVBoxLayout(center); center_layout.setContentsMargins(22, 18, 22, 16)
        crumb = QHBoxLayout(); self.filename = QLabel("未选择照片", objectName="section"); self.dimensions = QLabel("", objectName="meta")
        crumb.addWidget(self.filename); crumb.addStretch(); crumb.addWidget(self.dimensions); center_layout.addLayout(crumb)
        self.canvas = PreviewCanvas(); center_layout.addWidget(self.canvas, 1)
        tip = QLabel("预览参考线不会写入导出图片", objectName="muted"); tip.setAlignment(Qt.AlignCenter); center_layout.addWidget(tip)
        content.addWidget(center, 1); content.addWidget(self._build_inspector()); outer.addLayout(content, 1)
        self.setCentralWidget(root); self.setStatusBar(QStatusBar()); self.statusBar().showMessage("就绪 · 支持拖放导入")

    def _build_library(self) -> QWidget:
        panel = QFrame(objectName="sidebar"); panel.setFixedWidth(235)
        layout = QVBoxLayout(panel); layout.setContentsMargins(14, 18, 14, 14)
        title = QLabel("照片库", objectName="section"); self.count_label = QLabel("0 张照片", objectName="muted")
        layout.addWidget(title); layout.addWidget(self.count_label)
        self.library = QListWidget(); self.library.currentRowChanged.connect(self.select_document); layout.addWidget(self.library, 1)
        add = QPushButton("＋  继续添加"); add.clicked.connect(self.choose_files); layout.addWidget(add)
        return panel

    def _build_inspector(self) -> QWidget:
        panel = QFrame(objectName="inspector"); panel.setFixedWidth(310)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        body = QWidget(); layout = QVBoxLayout(body); layout.setContentsMargins(18, 18, 18, 24); layout.setSpacing(10)
        layout.addWidget(QLabel("风格滤镜", objectName="section"))
        self.filter_group = QButtonGroup(self); self.filter_group.setExclusive(True); self.filter_buttons = []
        for preset in FILTERS:
            button = QPushButton(f"●  {preset.name}    {preset.description}", objectName="filter"); button.setCheckable(True)
            button.setProperty("filter_key", preset.key); button.clicked.connect(self.change_filter); self.filter_group.addButton(button); self.filter_buttons.append(button); layout.addWidget(button)
        self.filter_buttons[0].setChecked(True)
        row = QHBoxLayout(); row.addWidget(QLabel("滤镜强度", objectName="section")); row.addStretch(); self.intensity_value = QLabel("70%", objectName="meta"); row.addWidget(self.intensity_value); layout.addLayout(row)
        self.intensity = QSlider(Qt.Horizontal); self.intensity.setRange(0, 100); self.intensity.setValue(70); self.intensity.valueChanged.connect(self.change_intensity); layout.addWidget(self.intensity)
        layout.addSpacing(8); layout.addWidget(QLabel("构图参考线", objectName="section")); self.guide = QComboBox(); self.guide.addItems(["无", "三分线", "黄金分割", "方格线", "中心十字"]); self.guide.currentTextChanged.connect(self.change_guide); layout.addWidget(self.guide)
        layout.addSpacing(8); layout.addWidget(QLabel("裁剪比例", objectName="section")); self.ratio = QComboBox(); self.ratio.addItems(RATIOS); layout.addWidget(self.ratio)
        self.crop_button = QPushButton("应用居中裁剪"); self.crop_button.clicked.connect(self.apply_crop); layout.addWidget(self.crop_button)
        layout.addSpacing(8); self.export_button = QPushButton("导出当前 PNG", objectName="primary"); self.export_button.clicked.connect(self.export_current); layout.addWidget(self.export_button); layout.addStretch()
        scroll.setWidget(body); wrapper = QVBoxLayout(panel); wrapper.setContentsMargins(0, 0, 0, 0); wrapper.addWidget(scroll); return panel

    def _set_controls_enabled(self, enabled: bool) -> None:
        for widget in [self.batch_button, self.intensity, self.guide, self.ratio, self.crop_button, self.export_button, *self.filter_buttons]: widget.setEnabled(enabled)

    def choose_files(self) -> None:
        pattern = " ".join(f"*{ext}" for ext in sorted(SUPPORTED_EXTENSIONS))
        paths, _ = QFileDialog.getOpenFileNames(self, "导入照片", "", f"支持的图片 ({pattern});;所有文件 (*)")
        self.add_files(paths)

    def add_files(self, paths) -> None:
        errors = []
        for value in paths:
            path = Path(value)
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS or any(d.path == path for d in self.documents): continue
            try: document = PhotoDocument.open(path)
            except Exception as exc: errors.append(f"{path.name}: {exc}"); continue
            self.documents.append(document); item = QListWidgetItem(f"{path.name}\n{document.original.width} × {document.original.height}"); item.setToolTip(str(path)); self.library.addItem(item)
        self.count_label.setText(f"{len(self.documents)} 张照片"); self._set_controls_enabled(bool(self.documents))
        if self.current_index < 0 and self.documents: self.library.setCurrentRow(0)
        if errors: QMessageBox.warning(self, "部分文件无法读取", "\n".join(errors))
        self.statusBar().showMessage(f"已导入 {len(self.documents)} 张照片", 3000)

    def select_document(self, index: int) -> None:
        if not 0 <= index < len(self.documents): return
        self.current_index = index; doc = self.current
        self.filename.setText(doc.path.name); self.dimensions.setText(f"{doc.original.width} × {doc.original.height}  ·  RGB")
        self.intensity.blockSignals(True); self.intensity.setValue(doc.intensity); self.intensity.blockSignals(False); self.intensity_value.setText(f"{doc.intensity}%")
        for button in self.filter_buttons: button.setChecked(button.property("filter_key") == doc.filter_key)
        self.refresh_preview()

    def refresh_preview(self) -> None:
        if self.current: self.canvas.set_image(self.current.render((1200, 900)))

    def change_filter(self) -> None:
        if not self.current: return
        button = self.sender(); self.current.filter_key = button.property("filter_key"); self.refresh_preview()

    def change_intensity(self, value: int) -> None:
        self.intensity_value.setText(f"{value}%")
        if self.current: self.current.intensity = value; self.refresh_preview()

    def change_guide(self, value: str) -> None:
        self.canvas.guide = value; self.canvas.update()

    def apply_crop(self) -> None:
        if self.current: self.current.crop_ratio = RATIOS[self.ratio.currentText()]; self.refresh_preview(); self.statusBar().showMessage("已应用非破坏性裁剪", 2500)

    def export_current(self) -> None:
        if not self.current: return
        default = str(self.current.path.with_name(f"{self.current.path.stem}_styled.png"))
        target, _ = QFileDialog.getSaveFileName(self, "导出 PNG", default, "PNG 图片 (*.png)")
        if target:
            try: output = self.current.export_png(target)
            except Exception as exc: QMessageBox.critical(self, "导出失败", str(exc)); return
            self.statusBar().showMessage(f"已导出：{output}", 5000)

    def export_batch(self) -> None:
        if not self.documents: return
        folder = QFileDialog.getExistingDirectory(self, "选择批量导出文件夹")
        if not folder: return
        try:
            for doc in self.documents: doc.export_png(Path(folder) / f"{doc.path.stem}_styled.png")
        except Exception as exc: QMessageBox.critical(self, "导出失败", str(exc)); return
        self.statusBar().showMessage(f"已导出 {len(self.documents)} 张 PNG", 5000)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        self.add_files([url.toLocalFile() for url in event.mimeData().urls()]); event.acceptProposedAction()
