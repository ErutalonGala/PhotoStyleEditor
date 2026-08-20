from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .window import EditorWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("拾光 · PhotoStyle")
    app.setStyle("Fusion")
    window = EditorWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
