"""Custom-painted charts. No extra packages. Colours match the QSS theme."""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

CYAN = QColor("#22D3EE")
TEAL = QColor("#2DD4BF")
GREEN = QColor("#34D399")
AMBER = QColor("#FBBF24")
ROSE = QColor("#FB7185")
MUTED = QColor("#94A3B8")
GRID = QColor("#29364B")
TEXT = QColor("#F1F5F9")
NAVY = QColor("#151F32")


class _ChartBase(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), NAVY)
        self.draw_chart(painter)
        painter.end()

    def draw_chart(self, painter: QPainter) -> None:
        raise NotImplementedError


class ActivityChart(_ChartBase):
    def __init__(self, points: list[tuple[str, int]], parent=None) -> None:
        super().__init__(parent)
        self.points = points

    def draw_chart(self, painter: QPainter) -> None:
        if not self.points:
            return
        left, top, right, bottom = 44, 16, self.width() - 16, self.height() - 36
        width = max(1, right - left)
        height = max(1, bottom - top)
        max_value = max(value for _label, value in self.points) or 1

        painter.setPen(QPen(GRID, 1))
        for step in range(5):
            y = top + height * step / 4
            painter.drawLine(left, int(y), right, int(y))
            label = int(max_value * (1 - step / 4))
            painter.setPen(MUTED)
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(QRectF(4, y - 8, 38, 16), Qt.AlignmentFlag.AlignRight, str(label))
            painter.setPen(QPen(GRID, 1))

        bar_width = width / (len(self.points) * 1.6)
        for index, (label, value) in enumerate(self.points):
            x = left + (index + 0.3) * (width / len(self.points))
            bar_h = (value / max_value) * (height - 8)
            rect = QRectF(x, bottom - bar_h, bar_width, bar_h)
            path = QPainterPath()
            path.addRoundedRect(rect, 4, 4)
            painter.fillPath(path, CYAN)
            painter.setPen(MUTED)
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(
                QRectF(x - 10, bottom + 4, bar_width + 20, 18),
                Qt.AlignmentFlag.AlignHCenter,
                label,
            )


class ClassificationChart(_ChartBase):
    def __init__(self, valid: int, rejected: int, review: int, parent=None) -> None:
        super().__init__(parent)
        self.slices = [
            ("Valid", valid, GREEN),
            ("Rejected", rejected, ROSE),
            ("Needs review", review, AMBER),
        ]

    def draw_chart(self, painter: QPainter) -> None:
        total = sum(item[1] for item in self.slices) or 1
        size = min(self.width() * 0.52, self.height() - 24)
        rect = QRectF(18, (self.height() - size) / 2, size, size)
        start = 90 * 16
        for _name, value, color in self.slices:
            span = int(value / total * 360 * 16)
            painter.setBrush(color)
            painter.setPen(QPen(NAVY, 3))
            painter.drawPie(rect, start, -span)
            start -= span

        hole = QRectF(rect.center().x() - size * 0.22, rect.center().y() - size * 0.22, size * 0.44, size * 0.44)
        painter.setBrush(NAVY)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(hole)
        painter.setPen(TEXT)
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        painter.drawText(hole, Qt.AlignmentFlag.AlignCenter, "Demo\nmix")

        legend_x = rect.right() + 18
        y = rect.center().y() - 36
        for name, value, color in self.slices:
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(legend_x, y, 10, 10), 2, 2)
            painter.setPen(TEXT)
            painter.setFont(QFont("Segoe UI", 9))
            percent = value / total * 100
            painter.drawText(
                QRectF(legend_x + 16, y - 4, self.width() - legend_x - 24, 20),
                Qt.AlignmentFlag.AlignLeft,
                f"{name}  {percent:.1f}%",
            )
            y += 26


class CandidateBarChart(_ChartBase):
    def __init__(self, candidates: list[dict], parent=None) -> None:
        super().__init__(parent)
        self.candidates = candidates

    def draw_chart(self, painter: QPainter) -> None:
        if not self.candidates:
            return
        max_votes = max(item["votes"] for item in self.candidates) or 1
        top = 12
        left = 128
        right = self.width() - 64
        row_h = (self.height() - 24) / len(self.candidates)
        for index, item in enumerate(self.candidates):
            y = top + index * row_h
            painter.setPen(TEXT)
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(
                QRectF(8, y, left - 16, row_h - 8),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                item["name"],
            )
            bar_w = (item["votes"] / max_votes) * max(1, right - left)
            rect = QRectF(left, y + 8, bar_w, row_h - 20)
            path = QPainterPath()
            path.addRoundedRect(rect, 6, 6)
            painter.fillPath(path, TEAL)
            painter.setPen(MUTED)
            painter.drawText(
                QRectF(rect.right() + 8, y, 52, row_h - 8),
                Qt.AlignmentFlag.AlignVCenter,
                f"{item['votes']:,}",
            )


def activity_chart(points: list[tuple[str, int]]) -> QWidget:
    return ActivityChart(points)


def classification_chart(valid: int, rejected: int, review: int) -> QWidget:
    return ClassificationChart(valid, rejected, review)


def candidate_bar_chart(candidates: list[dict]) -> QWidget:
    return CandidateBarChart(candidates)
