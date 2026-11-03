"""Officer review of sample flagged ballots."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.widgets.ballot_preview import SimulatedBallotView
from app.widgets.components import Card, NoticeBar, SectionTitle, StatusBadge


class ReviewPage(QScrollArea):
    def __init__(self, store, parent=None) -> None:
        super().__init__(parent)
        self.store = store
        self.selected_id = None
        self.filter_name = "All"
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
            NoticeBar(
                "Every ballot, mark, confidence score, and decision on this page is simulated.",
                "warning",
            )
        )

        columns = QHBoxLayout()
        columns.setSpacing(12)
        columns.addWidget(self._build_queue(), 5)
        columns.addWidget(self._build_detail(), 7)
        root.addLayout(columns, 1)

        self.store.changed.connect(self.refresh)
        self.refresh()

    def on_page_shown(self) -> None:
        default = self.store.settings().get("default_review_filter", "Pending Review")
        if default in self.filter_buttons:
            self.filter_buttons[default].click()

    def _build_queue(self) -> Card:
        card = Card()
        card.layout.addWidget(SectionTitle("Flagged ballot queue", "Demo subset of the 42 flagged ballots"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search ballot ID or flag reason")
        self.search.textChanged.connect(self.refresh)
        card.layout.addWidget(self.search)

        filters = QHBoxLayout()
        self.filter_group = QButtonGroup(self)
        self.filter_group.setExclusive(True)
        self.filter_buttons = {}
        for name in ("All", "Pending Review", "Reviewed"):
            button = QPushButton(name)
            button.setCheckable(True)
            button.clicked.connect(lambda _checked, value=name: self._set_filter(value))
            self.filter_group.addButton(button)
            self.filter_buttons[name] = button
            filters.addWidget(button)
        filters.addStretch()
        self.filter_buttons["All"].setChecked(True)
        card.layout.addLayout(filters)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Ballot ID", "Flag reason", "Confidence", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)
        card.layout.addWidget(self.table, 1)
        self.empty = QLabel("No ballots match this filter.")
        self.empty.setObjectName("mutedLabel")
        card.layout.addWidget(self.empty)
        return card

    def _build_detail(self) -> Card:
        card = Card()
        card.layout.addWidget(SectionTitle("Ballot inspection", "Painted sample ballot — not a camera capture"))
        self.preview = SimulatedBallotView()
        card.layout.addWidget(self.preview, 1)

        meta = QHBoxLayout()
        self.meta_id = QLabel("Ballot ID: —")
        self.meta_reason = QLabel("Flag reason: —")
        self.meta_reason.setWordWrap(True)
        meta.addWidget(self.meta_id)
        meta.addWidget(self.meta_reason, 1)
        card.layout.addLayout(meta)

        score_row = QHBoxLayout()
        self.confidence = StatusBadge("Confidence —", "warning")
        self.status_badge = StatusBadge("No selection", "neutral")
        score_row.addWidget(self.confidence)
        score_row.addWidget(self.status_badge)
        score_row.addStretch()
        card.layout.addLayout(score_row)

        card.layout.addWidget(SectionTitle("Review decision", "Choose one action before submitting"))
        self.decision_group = QButtonGroup(self)
        self.decision_group.setExclusive(True)
        decisions = QVBoxLayout()
        decisions.setSpacing(8)
        self.decision_buttons = {}
        for text in ("Confirm Detected Mark", "Mark as Rejected", "Send for Further Review"):
            button = QPushButton(text)
            button.setCheckable(True)
            button.setProperty("choice", False)
            button.clicked.connect(self._sync_decision_styles)
            self.decision_group.addButton(button)
            self.decision_buttons[text] = button
            decisions.addWidget(button)
        card.layout.addLayout(decisions)

        self.notes = QPlainTextEdit()
        self.notes.setPlaceholderText("Optional reviewer notes")
        self.notes.setFixedHeight(80)
        card.layout.addWidget(self.notes)

        submit = QPushButton("Submit Review")
        submit.setObjectName("primaryButton")
        submit.clicked.connect(self._submit)
        card.layout.addWidget(submit, 0, Qt.AlignmentFlag.AlignLeft)
        return card

    def _set_filter(self, name: str) -> None:
        self.filter_name = name
        self.refresh()

    def _filtered(self) -> list[dict]:
        query = self.search.text().strip().lower()
        rows = []
        for ballot in self.store.data["flagged"]:
            if self.filter_name != "All" and ballot["status"] != self.filter_name:
                continue
            blob = f"{ballot['id']} {ballot['reason']}".lower()
            if query and query not in blob:
                continue
            rows.append(ballot)
        return rows

    def refresh(self) -> None:
        rows = self._filtered()
        self.table.setRowCount(len(rows))
        self.empty.setVisible(not rows)
        selected_row = 0
        for index, ballot in enumerate(rows):
            values = [
                ballot["id"],
                ballot["reason"],
                f"{ballot['confidence']}%",
                ballot["status"],
            ]
            for column, value in enumerate(values):
                self.table.setItem(index, column, QTableWidgetItem(value))
            if ballot["id"] == self.selected_id:
                selected_row = index
        if rows:
            self.table.selectRow(selected_row)
            self._apply_ballot(rows[selected_row])
        else:
            self.selected_id = None
            self._apply_ballot(None)

    def _on_select(self) -> None:
        row = self.table.currentRow()
        rows = self._filtered()
        if 0 <= row < len(rows):
            self.selected_id = rows[row]["id"]
            self._apply_ballot(rows[row])

    def _apply_ballot(self, ballot: dict | None) -> None:
        self.preview.set_ballot(ballot)
        if not ballot:
            self.meta_id.setText("Ballot ID: —")
            self.meta_reason.setText("Flag reason: —")
            self.confidence.set_kind("neutral", "Confidence —")
            self.status_badge.set_kind("neutral", "No selection")
            self.notes.clear()
            return
        self.meta_id.setText(f"Ballot ID: {ballot['id']}  ·  Detected (simulated): {ballot.get('detected', '—')}")
        self.meta_reason.setText(f"Flag reason: {ballot['reason']}")
        self.confidence.set_kind("warning", f"Confidence {ballot['confidence']}%")
        kind = "success" if ballot["status"] == "Reviewed" else "warning"
        self.status_badge.set_kind(kind, ballot["status"])
        self.notes.setPlainText(ballot.get("notes", ""))
        for button in self.decision_buttons.values():
            button.setChecked(False)
        if ballot.get("decision") in self.decision_buttons:
            self.decision_buttons[ballot["decision"]].setChecked(True)
        self._sync_decision_styles()

    def _sync_decision_styles(self) -> None:
        for button in self.decision_buttons.values():
            button.setProperty("choice", button.isChecked())
            button.style().unpolish(button)
            button.style().polish(button)

    def _current_decision(self) -> str | None:
        for text, button in self.decision_buttons.items():
            if button.isChecked():
                return text
        return None

    def _submit(self) -> None:
        if not self.selected_id:
            QMessageBox.warning(self, "No ballot selected", "Choose a ballot from the queue first.")
            return
        decision = self._current_decision()
        if not decision:
            QMessageBox.warning(
                self,
                "Decision required",
                "Select Confirm Detected Mark, Mark as Rejected, or Send for Further Review.",
            )
            return
        if self.store.settings().get("require_reviewer_confirmation", True):
            answer = QMessageBox.question(
                self,
                "Confirm review",
                f"Submit “{decision}” for {self.selected_id}?\n\nThis is a simulated officer decision.",
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        self.store.submit_review(self.selected_id, decision, self.notes.toPlainText().strip())
        QMessageBox.information(
            self,
            "Review recorded",
            f"{self.selected_id} updated in the demo queue and prototype audit log.",
        )
