"""Election overview with sample metrics, charts, and system status."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.utils import format_number, format_percent
from app.widgets.charts import activity_chart, classification_chart
from app.widgets.components import Card, NoticeBar, SectionTitle, StatCard, StatusBadge


class DashboardPage(QScrollArea):
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

        self.root.addWidget(
            NoticeBar("All dashboard figures are fictional demonstration values.", "info")
        )

        stats_row = QGridLayout()
        stats_row.setHorizontalSpacing(12)
        self.card_total = StatCard("Total Ballots Processed", "0", "Cumulative demo count")
        self.card_valid = StatCard("Valid Ballots", "0", "Accepted in this prototype")
        self.card_flagged = StatCard("Flagged for Review", "0", "Need officer attention")
        self.card_accuracy = StatCard("Processing Accuracy", "0%", "Simulated metric")
        for column, card in enumerate(
            (self.card_total, self.card_valid, self.card_flagged, self.card_accuracy)
        ):
            stats_row.addWidget(card, 0, column)
            stats_row.setColumnStretch(column, 1)
        self.root.addLayout(stats_row)

        charts = QHBoxLayout()
        charts.setSpacing(12)
        self.activity_card = Card()
        self.activity_card.layout.addWidget(SectionTitle("Processing Activity", "Hourly demo throughput"))
        self.activity_holder = QVBoxLayout()
        self.activity_card.layout.addLayout(self.activity_holder, 1)
        self.class_card = Card()
        self.class_card.layout.addWidget(SectionTitle("Ballot Classification", "Valid, rejected, and needs review"))
        self.class_holder = QVBoxLayout()
        self.class_card.layout.addLayout(self.class_holder, 1)
        charts.addWidget(self.activity_card, 3)
        charts.addWidget(self.class_card, 2)
        self.root.addLayout(charts, 1)

        bottom = QHBoxLayout()
        bottom.setSpacing(12)

        table_card = Card()
        table_card.layout.addWidget(SectionTitle("Recent Processing Batches", "Latest demonstration batches"))
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Batch ID", "Time", "Images", "Valid", "Flagged", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(220)
        table_card.layout.addWidget(self.table)
        bottom.addWidget(table_card, 3)

        status_card = Card()
        status_card.layout.addWidget(SectionTitle("System Status", "Prototype health checks"))
        self.status_grid = QGridLayout()
        self.status_grid.setHorizontalSpacing(12)
        self.status_grid.setVerticalSpacing(14)
        self._status_rows = []
        rows = (
            ("Scanner", "Demo Mode", "info"),
            ("Recognition Engine", "Not Connected", "warning"),
            ("Audit Log", "Available", "success"),
        )
        for index, (label, value, kind) in enumerate(rows):
            name = QLabel(label)
            name.setObjectName("mutedLabel")
            badge = StatusBadge(value, kind)
            self.status_grid.addWidget(name, index, 0)
            self.status_grid.addWidget(badge, index, 1, Qt.AlignmentFlag.AlignRight)
        note = QLabel("Engine connection is intentionally off until the AI stage is built.")
        note.setObjectName("hintLabel")
        note.setWordWrap(True)
        status_card.layout.addLayout(self.status_grid)
        status_card.layout.addWidget(note)
        status_card.layout.addStretch()
        bottom.addWidget(status_card, 2)
        self.root.addLayout(bottom)

        self.store.changed.connect(self.refresh)
        self.refresh()

    def _replace_chart(self, holder: QVBoxLayout, widget: QWidget) -> None:
        while holder.count():
            item = holder.takeAt(0)
            old = item.widget()
            if old is not None:
                old.deleteLater()
        holder.addWidget(widget)

    def refresh(self) -> None:
        stats = self.store.data["stats"]
        self.card_total.set_value(format_number(stats["total_processed"]))
        self.card_valid.set_value(format_number(stats["valid"]))
        self.card_flagged.set_value(format_number(stats["flagged"]))
        self.card_accuracy.set_value(format_percent(stats["accuracy"]))

        classification = self.store.data["classification"]
        self._replace_chart(self.activity_holder, activity_chart(self.store.data["activity"]))
        self._replace_chart(
            self.class_holder,
            classification_chart(
                classification["valid"],
                classification["rejected"],
                classification["needs_review"],
            ),
        )

        batches = self.store.data["batches"]
        self.table.setRowCount(len(batches))
        for row, batch in enumerate(batches):
            values = [
                batch["id"],
                batch["time"],
                str(batch["images"]),
                str(batch["valid"]),
                str(batch["flagged"]),
                batch["status"],
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                self.table.setItem(row, column, item)
