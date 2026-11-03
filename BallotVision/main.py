"""
BallotVision entry point.

Run this file to open the native Windows desktop prototype.
"""

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from app.core.store import Store
from app.core.utils import project_root
from app.main_window import MainWindow


def load_stylesheet() -> str:
    qss_path = project_root() / "app" / "styles" / "theme.qss"
    if qss_path.exists():
        return qss_path.read_text(encoding="utf-8")
    return ""


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("BallotVision")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(load_stylesheet())

    store = Store()
    window = MainWindow(store)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
