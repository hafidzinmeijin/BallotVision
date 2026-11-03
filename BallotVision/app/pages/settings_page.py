"""Demonstration settings with save, reset, and clear-data actions."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.core.constants import APP_NAME, APP_SUBTITLE, APP_VERSION
from app.widgets.components import Card, NoticeBar, SectionTitle


class SettingsPage(QScrollArea):
    def __init__(self, store, parent=None) -> None:
        super().__init__(parent)
        self.store = store
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setObjectName("pageScroll")

        body = QWidget()
        body.setObjectName("pageBody")
        self.setWidget(body)
        root = QVBoxLayout(body)
        root.setContentsMargins(28, 18, 28, 28)
        root.setSpacing(16)

        root.addWidget(
            NoticeBar("Settings apply to this prototype on this computer. They do not change any official SPR system.", "info")
        )

        top_actions = QHBoxLayout()
        save = QPushButton("Save Settings")
        save.setObjectName("primaryButton")
        save.clicked.connect(self._save)
        reset = QPushButton("Reset to Defaults")
        reset.clicked.connect(self._reset)
        top_actions.addWidget(save)
        top_actions.addWidget(reset)
        top_actions.addStretch()
        root.addLayout(top_actions)

        general = Card()
        general.layout.addWidget(SectionTitle("General", "Identity and display preferences"))
        general_form = QFormLayout()
        self.app_name = QLineEdit()
        self.theme = QLineEdit()
        self.theme.setReadOnly(True)
        self.time_format = QComboBox()
        self.time_format.addItems(["24-hour", "12-hour"])
        general_form.addRow("Application name", self.app_name)
        general_form.addRow("Theme", self.theme)
        general_form.addRow("Date and time", self.time_format)
        general.layout.addLayout(general_form)
        root.addWidget(general)

        processing = Card()
        processing.layout.addWidget(SectionTitle("Ballot Processing", "Demonstration controls only"))
        self.demo_mode = QCheckBox("Demo Processing Mode")
        processing.layout.addWidget(self.demo_mode)
        self.threshold_label = QLabel()
        processing.layout.addWidget(self.threshold_label)
        self.threshold = QSlider(Qt.Orientation.Horizontal)
        self.threshold.setRange(50, 99)
        self.threshold.valueChanged.connect(self._update_threshold_label)
        processing.layout.addWidget(self.threshold)
        hint = QLabel(
            "The confidence threshold is for demonstration only. "
            "It does not control a live recognition model in this version."
        )
        hint.setObjectName("hintLabel")
        hint.setWordWrap(True)
        processing.layout.addWidget(hint)
        root.addWidget(processing)

        review = Card()
        review.layout.addWidget(SectionTitle("Review Workflow", "Officer confirmation behaviour"))
        self.require_confirm = QCheckBox("Require reviewer confirmation before submit")
        review.layout.addWidget(self.require_confirm)
        review_form = QFormLayout()
        self.default_filter = QComboBox()
        self.default_filter.addItems(["All", "Pending Review", "Reviewed"])
        review_form.addRow("Default review filter", self.default_filter)
        review.layout.addLayout(review_form)
        root.addWidget(review)

        data = Card()
        data.layout.addWidget(SectionTitle("Data and Export", "Local prototype files"))
        data_form = QFormLayout()
        self.export_format = QComboBox()
        self.export_format.addItems(["CSV", "TXT"])
        data_form.addRow("Default export format", self.export_format)
        data.layout.addLayout(data_form)
        clear = QPushButton("Clear Demo Data")
        clear.setObjectName("dangerButton")
        clear.clicked.connect(self._clear_data)
        data.layout.addWidget(clear, 0, Qt.AlignmentFlag.AlignLeft)
        root.addWidget(data)

        about = Card()
        about.layout.addWidget(SectionTitle("About", "Project identity"))
        about.layout.addWidget(QLabel(APP_NAME))
        about.layout.addWidget(QLabel("FYP Prototype"))
        about.layout.addWidget(QLabel(f"Version {APP_VERSION}"))
        stack = QLabel("Python + PySide6")
        stack.setObjectName("mutedLabel")
        about.layout.addWidget(stack)
        subtitle = QLabel(APP_SUBTITLE)
        subtitle.setObjectName("hintLabel")
        subtitle.setWordWrap(True)
        about.layout.addWidget(subtitle)
        root.addWidget(about)

        root.addStretch()

        self.store.changed.connect(self.load_from_store)
        self.load_from_store()

    def _update_threshold_label(self, value: int) -> None:
        self.threshold_label.setText(f"Confidence threshold: {value}% (demonstration only)")

    def load_from_store(self) -> None:
        settings = self.store.settings()
        self.app_name.setText(settings.get("app_name", APP_NAME))
        self.theme.setText(settings.get("theme_name", "Dark Navy"))
        self.time_format.setCurrentText(settings.get("time_format", "24-hour"))
        self.demo_mode.setChecked(bool(settings.get("demo_processing_mode", True)))
        self.threshold.setValue(int(settings.get("confidence_threshold", 85)))
        self.require_confirm.setChecked(bool(settings.get("require_reviewer_confirmation", True)))
        self.default_filter.setCurrentText(settings.get("default_review_filter", "Pending Review"))
        self.export_format.setCurrentText(settings.get("export_format", "CSV"))

    def _collect(self) -> dict:
        return {
            "app_name": self.app_name.text().strip() or APP_NAME,
            "theme_name": "Dark Navy",
            "time_format": self.time_format.currentText(),
            "demo_processing_mode": self.demo_mode.isChecked(),
            "confidence_threshold": self.threshold.value(),
            "require_reviewer_confirmation": self.require_confirm.isChecked(),
            "default_review_filter": self.default_filter.currentText(),
            "export_format": self.export_format.currentText(),
        }

    def _save(self) -> None:
        self.store.data["settings"].update(self._collect())
        self.store.save_settings()

    def _reset(self) -> None:
        answer = QMessageBox.question(
            self,
            "Reset settings",
            "Restore every setting to the original demonstration defaults?",
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.store.reset_settings()
            self.load_from_store()

    def _clear_data(self) -> None:
        answer = QMessageBox.question(
            self,
            "Clear demo data",
            "Reset sample ballots, results, imported images, and the prototype audit log?\n\n"
            "Saved settings will be kept.",
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.store.reset_demo_data()
