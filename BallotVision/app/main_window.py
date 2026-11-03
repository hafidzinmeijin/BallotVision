"""Main application chrome: sidebar, header, and stacked pages."""

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.constants import (
    APP_NAME,
    MIN_HEIGHT,
    MIN_WIDTH,
    PAGES,
    USER_NAME,
    USER_ROLE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from app.pages.audit_page import AuditPage
from app.pages.dashboard_page import DashboardPage
from app.pages.results_page import ResultsPage
from app.pages.review_page import ReviewPage
from app.pages.scan_page import ScanPage
from app.pages.settings_page import SettingsPage
from app.widgets.sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self, store) -> None:
        super().__init__()
        self.store = store
        self.setWindowTitle(f"{APP_NAME}  ·  {USER_ROLE}")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.page_chosen.connect(self.show_page)
        root_layout.addWidget(self.sidebar)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self._build_header())

        self.toast = QLabel("")
        self.toast.setObjectName("toast")
        self.toast.setVisible(False)
        self.toast.setWordWrap(True)
        toast_wrap = QWidget()
        toast_layout = QVBoxLayout(toast_wrap)
        toast_layout.setContentsMargins(24, 8, 24, 0)
        toast_layout.addWidget(self.toast)
        right_layout.addWidget(toast_wrap)

        self.stack = QStackedWidget()
        self.pages = {
            "dashboard": DashboardPage(store),
            "scan": ScanPage(store),
            "review": ReviewPage(store),
            "results": ResultsPage(store),
            "audit": AuditPage(store),
            "settings": SettingsPage(store),
        }
        self.page_index = {}
        for index, page_id in enumerate(self.pages):
            self.stack.addWidget(self.pages[page_id])
            self.page_index[page_id] = index
        right_layout.addWidget(self.stack, 1)

        root_layout.addWidget(right, 1)
        self.setCentralWidget(root)

        self.store.message.connect(self.show_message)
        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.timeout.connect(lambda: self.toast.setVisible(False))

        self.show_page("dashboard")

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(84)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(28, 16, 28, 16)

        titles = QVBoxLayout()
        titles.setSpacing(2)
        self.title_label = QLabel()
        self.title_label.setObjectName("headerTitle")
        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("headerSubtitle")
        titles.addWidget(self.title_label)
        titles.addWidget(self.subtitle_label)
        layout.addLayout(titles, 1)

        self.demo_chip = QLabel("DEMO MODE")
        self.demo_chip.setObjectName("demoChip")
        layout.addWidget(self.demo_chip)

        bell = QPushButton("i")
        bell.setObjectName("iconButton")
        bell.setToolTip("Notifications")
        bell.setFixedSize(38, 38)
        bell.clicked.connect(self._show_notifications)
        layout.addWidget(bell)

        profile = QFrame()
        profile_layout = QHBoxLayout(profile)
        profile_layout.setContentsMargins(8, 0, 0, 0)
        avatar = QLabel("AR")
        avatar.setObjectName("avatar")
        avatar.setFixedSize(34, 34)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        names = QVBoxLayout()
        names.setSpacing(0)
        names.addWidget(QLabel(USER_NAME))
        role = QLabel(USER_ROLE)
        role.setObjectName("mutedLabel")
        names.addWidget(role)
        profile_layout.addWidget(avatar)
        profile_layout.addLayout(names)
        layout.addWidget(profile)
        return header

    def show_page(self, page_id: str) -> None:
        meta = next(page for page in PAGES if page["id"] == page_id)
        self.stack.setCurrentIndex(self.page_index[page_id])
        self.sidebar.set_active(page_id)
        self.title_label.setText(meta["title"])
        self.subtitle_label.setText(meta["subtitle"])
        page = self.pages[page_id]
        if hasattr(page, "on_page_shown"):
            page.on_page_shown()

    def show_message(self, text: str, level: str) -> None:
        colors = {
            "success": ("#34D399", "rgba(52, 211, 153, 0.12)"),
            "warning": ("#FBBF24", "rgba(251, 191, 36, 0.12)"),
            "error": ("#FB7185", "rgba(251, 113, 133, 0.12)"),
            "info": ("#22D3EE", "rgba(34, 211, 238, 0.12)"),
        }
        color, background = colors.get(level, colors["info"])
        self.toast.setText(text)
        self.toast.setStyleSheet(
            f"color: {color}; background: {background}; border: 1px solid {color};"
        )
        self.toast.setVisible(True)
        self._toast_timer.start(4200)

    def _show_notifications(self) -> None:
        menu = QMenu(self)
        for item in self.store.data["notifications"]:
            action = QAction(f"{item['title']}: {item['body']}", self)
            action.setEnabled(False)
            menu.addAction(action)
        menu.exec(self.cursor().pos())

    def closeEvent(self, event) -> None:  # noqa: N802
        answer = QMessageBox.question(
            self,
            "Exit BallotVision",
            "Close the BallotVision prototype?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
