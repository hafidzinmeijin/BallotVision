"""Ballot image import and AI image classification."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QComboBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from image_classifier import ImageClassifier
from app.widgets.components import Card, SectionTitle


IMAGE_FILTER = (
    "Ballot images (*.png *.jpg *.jpeg);;"
    "All files (*.*)"
)

ALLOWED = {".png", ".jpg", ".jpeg"}


class DropZone(QFrame):
    def __init__(self, on_files, parent=None) -> None:
        super().__init__(parent)

        self.on_files = on_files

        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(170)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Drop ballot images here")
        title.setObjectName("sectionTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hint = QLabel(
            "Supported types: PNG, JPG, JPEG"
        )
        hint.setObjectName("mutedLabel")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(hint)

    def _set_active(self, active: bool) -> None:
        self.setProperty(
            "active",
            "true" if active else "false"
        )

        self.style().unpolish(self)
        self.style().polish(self)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_active(True)

    def dragLeaveEvent(self, event) -> None:
        self._set_active(False)

    def dropEvent(self, event) -> None:
        self._set_active(False)

        paths = []

        for url in event.mimeData().urls():
            path = url.toLocalFile()

            if Path(path).suffix.lower() in ALLOWED:
                paths.append(path)

        if paths:
            self.on_files(paths)

        event.acceptProposedAction()


class ScanPage(QScrollArea):

    def __init__(self, store, parent=None) -> None:
        super().__init__(parent)

        self.store = store

        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setObjectName("pageScroll")

        # Load AI model
        self.classifier = None
        self.model_loading = False

        body = QWidget()
        body.setObjectName("pageBody")
        self.setWidget(body)

        root = QVBoxLayout(body)
        root.setContentsMargins(28, 18, 28, 28)
        root.setSpacing(16)

        # =========================================================
        # IMPORT CARD
        # =========================================================

        import_card = Card()

        import_card.layout.addWidget(
            SectionTitle(
                "Import images",
                "Upload a ballot image for AI classification"
            )
        )

        self.drop_zone = DropZone(
            self._add_files
        )

        import_card.layout.addWidget(
            self.drop_zone
        )

        buttons = QHBoxLayout()

        upload = QPushButton(
            "Upload Ballot Images"
        )

        upload.setObjectName(
            "primaryButton"
        )

        upload.clicked.connect(
            self._choose_files
        )

        self.count_label = QLabel(
            "Imported images: 0"
        )

        self.count_label.setObjectName(
            "mutedLabel"
        )

        buttons.addWidget(upload)
        buttons.addWidget(self.count_label)
        buttons.addStretch()

        import_card.layout.addLayout(
            buttons
        )

        root.addWidget(import_card)

        # =========================================================
        # PREVIEW
        # =========================================================

        preview_row = QHBoxLayout()
        preview_row.setSpacing(12)

        # File list

        list_card = Card()

        list_card.layout.addWidget(
            SectionTitle(
                "Imported files",
                "Select an image to classify"
            )
        )

        self.file_list = QListWidget()

        self.file_list.currentRowChanged.connect(
            self._show_preview
        )

        list_card.layout.addWidget(
            self.file_list
        )

        list_buttons = QHBoxLayout()

        remove = QPushButton(
            "Remove image"
        )

        remove.setObjectName(
            "ghostButton"
        )

        remove.clicked.connect(
            self._remove_selected
        )

        clear = QPushButton(
            "Clear Selection"
        )

        clear.setObjectName(
            "dangerButton"
        )

        clear.clicked.connect(
            self._clear_all
        )

        list_buttons.addWidget(remove)
        list_buttons.addWidget(clear)
        list_buttons.addStretch()

        list_card.layout.addLayout(
            list_buttons
        )

        preview_row.addWidget(
            list_card,
            2
        )

        # Image preview

        preview_card = Card()

        preview_card.layout.addWidget(
            SectionTitle(
                "Image preview",
                "Selected image"
            )
        )

        self.preview = QLabel(
            "No image selected"
        )

        self.preview.setObjectName(
            "previewFrame"
        )

        self.preview.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.preview.setMinimumHeight(
            280
        )

        self.preview.setWordWrap(True)

        preview_card.layout.addWidget(
            self.preview,
            1
        )

        preview_row.addWidget(
            preview_card,
            3
        )

        root.addLayout(
            preview_row,
            1
        )

        # =========================================================
        # AI CLASSIFICATION CARD
        # =========================================================

        ai_card = Card()

        ai_card.layout.addWidget(
            SectionTitle(
                "AI Image Classification",
                "Run a pretrained image classification model"
            )
        )

        # Model selection

        model_row = QHBoxLayout()

        model_label = QLabel(
            "Classification model:"
        )

        self.model_combo = QComboBox()

        self.model_combo.addItem(
            "MobileNetV2"
        )

        model_row.addWidget(
            model_label
        )

        model_row.addWidget(
            self.model_combo
        )

        model_row.addStretch()

        ai_card.layout.addLayout(
            model_row
        )

        # Status

        self.status_label = QLabel(
            "Ready. Select an image and run classification."
        )

        self.status_label.setObjectName(
            "mutedLabel"
        )

        self.status_label.setWordWrap(
            True
        )

        ai_card.layout.addWidget(
            self.status_label
        )

        # Classify button

        self.classify_button = QPushButton(
            "Classify Image"
        )

        self.classify_button.setObjectName(
            "primaryButton"
        )

        self.classify_button.clicked.connect(
            self._classify_selected
        )

        ai_card.layout.addWidget(
            self.classify_button,
            0,
            Qt.AlignmentFlag.AlignLeft
        )

        # Results title

        results_title = QLabel(
            "Classification Results"
        )

        results_title.setObjectName(
            "sectionTitle"
        )

        ai_card.layout.addWidget(
            results_title
        )

        # Results

        self.results_label = QLabel(
            "No classification performed yet."
        )

        self.results_label.setWordWrap(
            True
        )

        self.results_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        ai_card.layout.addWidget(
            self.results_label
        )

        root.addWidget(
            ai_card
        )

        self.store.changed.connect(
            self.refresh
        )

        self.refresh()

    # =============================================================
    # FILE SELECTION
    # =============================================================

    def _choose_files(self) -> None:

        files, _filter = QFileDialog.getOpenFileNames(
            self,
            "Select ballot images",
            "",
            IMAGE_FILTER
        )

        if files:
            self._add_files(files)

    def _add_files(
        self,
        files: list[str]
    ) -> None:

        valid = [
            path
            for path in files
            if Path(path).suffix.lower()
            in ALLOWED
        ]

        skipped = len(files) - len(valid)

        if valid:
            self.store.add_imported(
                valid
            )

        if skipped:
            QMessageBox.warning(
                self,
                "Unsupported files",
                f"{skipped} file(s) were skipped. "
                "Use PNG, JPG, or JPEG."
            )

    # =============================================================
    # REMOVE FILE
    # =============================================================

    def _remove_selected(self) -> None:

        item = self.file_list.currentItem()

        if not item:

            self.store.message.emit(
                "Select an image to remove.",
                "warning"
            )

            return

        self.store.remove_imported(
            item.data(
                Qt.ItemDataRole.UserRole
            )
        )

    def _clear_all(self) -> None:

        if not self.store.data["imported"]:
            return

        answer = QMessageBox.question(
            self,
            "Clear images",
            "Remove all imported images?"
        )

        if answer == QMessageBox.StandardButton.Yes:

            self.store.clear_imported()

    # =============================================================
    # PREVIEW
    # =============================================================

    def _show_preview(
        self,
        row: int
    ) -> None:

        if (
            row < 0
            or row >= len(
                self.store.data["imported"]
            )
        ):

            self.preview.setPixmap(
                QPixmap()
            )

            self.preview.setText(
                "No image selected"
            )

            return

        path = self.store.data[
            "imported"
        ][row]["path"]

        pixmap = QPixmap(path)

        if pixmap.isNull():

            self.preview.setText(
                "Could not read this image."
            )

            return

        scaled = pixmap.scaled(
            self.preview.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.preview.setPixmap(
            scaled
        )

        self.preview.setText("")

    # =============================================================
    # AI CLASSIFICATION
    # =============================================================

    def _load_classifier(self) -> bool:

        if self.classifier is not None:
            return True

        try:

            self.status_label.setText(
                "Loading MobileNetV2 AI model..."
            )

            self.classify_button.setEnabled(
                False
            )

            # Load pretrained model
            self.classifier = ImageClassifier()

            self.status_label.setText(
                "MobileNetV2 loaded successfully."
            )

            return True

        except Exception as error:

            self.classifier = None

            QMessageBox.critical(
                self,
                "AI Model Error",
                "Could not load the image classification model.\n\n"
                f"{error}"
            )

            self.status_label.setText(
                "Failed to load AI model."
            )

            return False

        finally:

            self.classify_button.setEnabled(
                True
            )

    def _classify_selected(self) -> None:

        item = self.file_list.currentItem()

        if not item:

            QMessageBox.warning(
                self,
                "No image selected",
                "Please select an image first."
            )

            return

        image_path = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not Path(image_path).exists():

            QMessageBox.warning(
                self,
                "Image not found",
                "The selected image could not be found."
            )

            return

        # Load AI model

        if not self._load_classifier():
            return

        try:

            self.classify_button.setEnabled(
                False
            )

            self.status_label.setText(
                "AI is analyzing the image..."
            )

            # Run model

            results = self.classifier.classify(
                image_path,
                top_k=5
            )

            # Build result text

            result_lines = []

            for index, result in enumerate(
                results,
                start=1
            ):

                label = result["label"]

                confidence = result[
                    "confidence"
                ]

                result_lines.append(
                    f"{index}. {label} "
                    f"— {confidence:.2f}%"
                )

            result_text = (
                "<b>Top predictions:</b><br><br>"
                + "<br>".join(
                    result_lines
                )
            )

            self.results_label.setText(
                result_text
            )

            self.status_label.setText(
                "Classification completed successfully."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Classification Error",
                "The image could not be classified.\n\n"
                f"{error}"
            )

            self.status_label.setText(
                "Classification failed."

            )

        finally:

            self.classify_button.setEnabled(
                True
            )

    # =============================================================
    # REFRESH
    # =============================================================

    def refresh(self) -> None:

        current_path = None

        current = self.file_list.currentItem()

        if current:

            current_path = current.data(
                Qt.ItemDataRole.UserRole
            )

        self.file_list.clear()

        for item in self.store.data[
            "imported"
        ]:

            row = QListWidgetItem(
                item["name"]
            )

            row.setData(
                Qt.ItemDataRole.UserRole,
                item["path"]
            )

            self.file_list.addItem(
                row
            )

        self.count_label.setText(
            f"Imported images: "
            f"{len(self.store.data['imported'])}"
        )

        if current_path:

            for index in range(
                self.file_list.count()
            ):

                if (
                    self.file_list.item(index)
                    .data(
                        Qt.ItemDataRole.UserRole
                    )
                    == current_path
                ):

                    self.file_list.setCurrentRow(
                        index
                    )

                    break

        elif self.file_list.count():

            self.file_list.setCurrentRow(
                0
            )

        else:

            self.preview.setPixmap(
                QPixmap()
            )

            self.preview.setText(
                "No image selected"
            )

            self.results_label.setText(
                "No classification performed yet."
            )