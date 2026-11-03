"""Reusable cards, badges, and section headers."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class Card(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(18, 16, 18, 16)
        self.layout.setSpacing(12)


class StatCard(Card):
    def __init__(self, label: str, value: str, hint: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("statCard")
        caption = QLabel(label)
        caption.setObjectName("mutedLabel")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("statValue")
        self.value_label.setWordWrap(True)
        self.hint_label = QLabel(hint)
        self.hint_label.setObjectName("hintLabel")
        self.hint_label.setVisible(bool(hint))
        self.layout.addWidget(caption)
        self.layout.addWidget(self.value_label)
        self.layout.addWidget(self.hint_label)
        self.layout.addStretch()

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)


class StatusBadge(QLabel):
    def __init__(self, text: str, kind: str = "info", parent=None) -> None:
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_kind(kind, text)

    def set_kind(self, kind: str, text: str | None = None) -> None:
        if text is not None:
            self.setText(text)
        self.setProperty("badge", kind)
        self.style().unpolish(self)
        self.style().polish(self)


class SectionTitle(QWidget):
    def __init__(self, title: str, subtitle: str = "", parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        heading = QLabel(title)
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setObjectName("mutedLabel")
            sub.setWordWrap(True)
            layout.addWidget(sub)


class NoticeBar(QFrame):
    def __init__(self, text: str, kind: str = "warning", parent=None) -> None:
        super().__init__(parent)
        self.setProperty("notice", kind)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        label = QLabel(text)
        label.setWordWrap(True)
        label.setObjectName("noticeText")
        layout.addWidget(label)


class EmptyState(QFrame):
    def __init__(self, title: str, body: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("emptyState")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 32, 24, 32)
        heading = QLabel(title)
        heading.setObjectName("sectionTitle")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text = QLabel(body)
        text.setObjectName("mutedLabel")
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(heading)
        layout.addWidget(text)
