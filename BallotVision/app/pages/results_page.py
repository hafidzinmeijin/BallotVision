"""Simulated vote totals with CSV and summary export."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.utils import format_number, format_percent
from app.services.export_service import export_results_csv, export_results_summary
from app.widgets.charts import candidate_bar_chart, classification_chart
from app.widgets.components import Card, NoticeBar, SectionTitle, StatCard


class ResultsPage(QScrollArea):
    def __init__(self, store, parent=None) -> None:
        super().__init__(parent)
        self.store = store
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setObjectName("pageScroll")

        body = QWidget()
        body.setObjectName("pageBody")
        self.setWidget(body)
        self.root = QVBoxLayout(body)
        self.root.setContentsMargins(28, 18, 28, 28)
        self.root.setSpacing(16)

        notice = NoticeBar("SIMULATED RESULTS — NOT OFFICIAL", "error")
        self.root.addWidget(notice)

        stats = QGridLayout()
        stats.setHorizontalSpacing(12)
        stats.setVerticalSpacing(12)
        self.total = StatCard("Total Ballots Counted", "0")
        self.valid = StatCard("Valid Votes", "0")
        self.rejected = StatCard("Rejected Ballots", "0")
        self.pending = StatCard("Pending Reviews", "0")
        for column, card in enumerate((self.total, self.valid, self.rejected, self.pending)):
            stats.addWidget(card, 0, column)
            stats.setColumnStretch(column, 1)
        self.root.addLayout(stats)

        actions = QHBoxLayout()
        refresh = QPushButton("Refresh Results")
        refresh.clicked.connect(self.refresh)
        export_csv = QPushButton("Export CSV")
        export_csv.setObjectName("primaryButton")
        export_csv.clicked.connect(self._export_csv)
        export_summary = QPushButton("Export Summary")
        export_summary.clicked.connect(self._export_summary)
        actions.addWidget(refresh)
        actions.addWidget(export_csv)
        actions.addWidget(export_summary)
        actions.addStretch()
        note = QLabel("Exports include a simulated-results notice. No winner is declared.")
        note.setObjectName("mutedLabel")
        actions.addWidget(note)
        self.root.addLayout(actions)

        middle = QHBoxLayout()
        middle.setSpacing(12)
        table_card = Card()
        table_card.layout.addWidget(SectionTitle("Candidate Vote Summary", "Fictional totals for supervisor demonstration"))
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Candidate", "Votes", "Share of valid votes"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        table_card.layout.addWidget(self.table)
        middle.addWidget(table_card, 2)

        self.bar_card = Card()
        self.bar_card.layout.addWidget(SectionTitle("Horizontal comparison", "Visual share of simulated valid votes"))
        self.bar_holder = QVBoxLayout()
        self.bar_card.layout.addLayout(self.bar_holder, 1)
        middle.addWidget(self.bar_card, 3)
        self.root.addLayout(middle, 1)

        class_card = Card()
        class_card.layout.addWidget(SectionTitle("Ballot classification summary", "Valid, rejected, and still in review"))
        self.class_holder = QVBoxLayout()
        class_card.layout.addLayout(self.class_holder, 1)
        self.root.addWidget(class_card)

        self.store.changed.connect(self.refresh)
        self.refresh()

    def _replace(self, holder: QVBoxLayout, widget: QWidget) -> None:
        while holder.count():
            item = holder.takeAt(0)
            old = item.widget()
            if old is not None:
                old.deleteLater()
        holder.addWidget(widget)

    def refresh(self) -> None:
        stats = self.store.data["stats"]
        valid = stats["valid"] or 1
        self.total.set_value(format_number(stats["total_processed"]))
        self.valid.set_value(format_number(stats["valid"]))
        self.rejected.set_value(format_number(stats["rejected"]))
        self.pending.set_value(format_number(stats["pending_reviews"]))

        candidates = self.store.data["candidates"]
        self.table.setRowCount(len(candidates))
        for row, item in enumerate(candidates):
            share = item["votes"] / valid * 100
            values = [item["name"], format_number(item["votes"]), format_percent(share)]
            for column, value in enumerate(values):
                table_item = QTableWidgetItem(value)
                if column > 0:
                    table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, column, table_item)

        self._replace(self.bar_holder, candidate_bar_chart(candidates))
        classification = self.store.data["classification"]
        self._replace(
            self.class_holder,
            classification_chart(
                classification["valid"],
                classification["rejected"],
                classification["needs_review"],
            ),
        )

    def _export_csv(self) -> None:
        path, _filter = QFileDialog.getSaveFileName(
            self,
            "Export simulated results",
            "ballotvision_simulated_results.csv",
            "CSV files (*.csv)",
        )
        if not path:
            return
        export_results_csv(path, self.store.data)
        self.store.record_export("results CSV", path)

    def _export_summary(self) -> None:
        path, _filter = QFileDialog.getSaveFileName(
            self,
            "Export simulated summary",
            "ballotvision_simulated_summary.txt",
            "Text files (*.txt)",
        )
        if not path:
            return
        export_results_summary(path, self.store.data)
        self.store.record_export("results summary", path)
