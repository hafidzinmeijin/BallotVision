"""
In-memory demonstration data for the UI prototype.

Nothing here is a real election result or an AI prediction.
Pages share one Store so a review or export can update other screens.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from app.core.constants import CANDIDATES, DEFAULT_SETTINGS
from app.core.utils import settings_path


def _dt(days_ago: int, hour: int, minute: int) -> datetime:
    base = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    return base - timedelta(days=days_ago)


def build_sample_data() -> dict:
    """Factory values used on first launch and after Clear Demo Data."""
    flagged = [
        {
            "id": "BLT-2041",
            "batch": "BATCH-18",
            "reason": "Faint mark near box edge",
            "confidence": 71,
            "status": "Pending Review",
            "detected": "Candidate B",
            "notes": "",
        },
        {
            "id": "BLT-2048",
            "batch": "BATCH-18",
            "reason": "Possible double mark",
            "confidence": 64,
            "status": "Pending Review",
            "detected": "Candidate A",
            "notes": "",
        },
        {
            "id": "BLT-2055",
            "batch": "BATCH-19",
            "reason": "Low contrast scan",
            "confidence": 69,
            "status": "Pending Review",
            "detected": "Candidate C",
            "notes": "",
        },
        {
            "id": "BLT-2062",
            "batch": "BATCH-19",
            "reason": "Mark outside designated box",
            "confidence": 73,
            "status": "Pending Review",
            "detected": "Candidate A",
            "notes": "",
        },
        {
            "id": "BLT-2070",
            "batch": "BATCH-20",
            "reason": "Ambiguous stroke direction",
            "confidence": 66,
            "status": "Pending Review",
            "detected": "Candidate D",
            "notes": "",
        },
        {
            "id": "BLT-2077",
            "batch": "BATCH-20",
            "reason": "Fold line across candidate row",
            "confidence": 62,
            "status": "Pending Review",
            "detected": "Candidate B",
            "notes": "",
        },
        {
            "id": "BLT-1988",
            "batch": "BATCH-17",
            "reason": "Smudge near Candidate C",
            "confidence": 74,
            "status": "Reviewed",
            "detected": "Candidate C",
            "decision": "Confirm Detected Mark",
            "notes": "Officer confirmed intended mark.",
        },
        {
            "id": "BLT-1994",
            "batch": "BATCH-17",
            "reason": "Overvote suspected",
            "confidence": 58,
            "status": "Reviewed",
            "detected": "Candidate A",
            "decision": "Mark as Rejected",
            "notes": "Two marks of similar density.",
        },
    ]

    audit = [
        {
            "id": "AUD-1001",
            "time": _dt(2, 9, 12),
            "user": "Sahira",
            "action": "Imported ballot images",
            "related": "BATCH-17",
            "type": "Image Import",
            "status": "Completed",
            "detail": "120 PNG files imported for demonstration batch 17.",
        },
        {
            "id": "AUD-1002",
            "time": _dt(2, 9, 18),
            "user": "System",
            "action": "Started processing simulation",
            "related": "BATCH-17",
            "type": "Processing Simulation",
            "status": "Completed",
            "detail": "Simulated classification only. No AI model was used.",
        },
        {
            "id": "AUD-1003",
            "time": _dt(2, 9, 41),
            "user": "System",
            "action": "Flagged ballots for review",
            "related": "BATCH-17",
            "type": "Flagged Ballot",
            "status": "Completed",
            "detail": "8 sample ballots placed in the review queue.",
        },
        {
            "id": "AUD-1004",
            "time": _dt(1, 14, 5),
            "user": "Sahira",
            "action": "Confirmed detected mark",
            "related": "BLT-1988",
            "type": "Review Decision",
            "status": "Completed",
            "detail": "Decision: Confirm Detected Mark for Candidate C.",
        },
        {
            "id": "AUD-1005",
            "time": _dt(1, 14, 11),
            "user": "Sahira",
            "action": "Rejected ballot",
            "related": "BLT-1994",
            "type": "Review Decision",
            "status": "Completed",
            "detail": "Decision: Mark as Rejected due to suspected overvote.",
        },
        {
            "id": "AUD-1006",
            "time": _dt(1, 16, 22),
            "user": "Sahira",
            "action": "Imported ballot images",
            "related": "BATCH-18",
            "type": "Image Import",
            "status": "Completed",
            "detail": "86 JPG files imported for demonstration batch 18.",
        },
        {
            "id": "AUD-1007",
            "time": _dt(0, 10, 4),
            "user": "System",
            "action": "Started processing simulation",
            "related": "BATCH-20",
            "type": "Processing Simulation",
            "status": "Completed",
            "detail": "Demo processing mode was enabled.",
        },
        {
            "id": "AUD-1008",
            "time": _dt(0, 11, 30),
            "user": "Sahira",
            "action": "Exported results CSV",
            "related": "RESULTS",
            "type": "CSV Export",
            "status": "Completed",
            "detail": "Simulated results exported. File is not an official return.",
        },
        {
            "id": "AUD-1009",
            "time": _dt(0, 8, 2),
            "user": "System",
            "action": "Recognition engine check",
            "related": "SYSTEM",
            "type": "System Event",
            "status": "Warning",
            "detail": "Recognition engine is not connected in this prototype.",
        },
    ]

    return {
        "stats": {
            "total_processed": 2450,
            "valid": 2391,
            "flagged": 42,
            "accuracy": 98.4,
            "rejected": 17,
            "pending_reviews": 42,
        },
        "candidates": [
            {"name": CANDIDATES[0], "votes": 912},
            {"name": CANDIDATES[1], "votes": 754},
            {"name": CANDIDATES[2], "votes": 481},
            {"name": CANDIDATES[3], "votes": 244},
        ],
        "classification": {"valid": 2391, "rejected": 17, "needs_review": 42},
        "activity": [
            ("08:00", 180),
            ("09:00", 310),
            ("10:00", 420),
            ("11:00", 390),
            ("12:00", 210),
            ("13:00", 350),
            ("14:00", 410),
            ("15:00", 180),
        ],
        "batches": [
            {"id": "BATCH-20", "time": "Today, 10:04", "images": 94, "valid": 88, "flagged": 5, "status": "Completed"},
            {"id": "BATCH-19", "time": "Today, 09:12", "images": 110, "valid": 104, "flagged": 4, "status": "Completed"},
            {"id": "BATCH-18", "time": "Yesterday, 16:22", "images": 86, "valid": 81, "flagged": 4, "status": "Completed"},
            {"id": "BATCH-17", "time": "Yesterday, 09:18", "images": 120, "valid": 116, "flagged": 3, "status": "Reviewed"},
            {"id": "BATCH-16", "time": "13 Oct 2026", "images": 102, "valid": 99, "flagged": 2, "status": "Completed"},
        ],
        "flagged": flagged,
        "audit": audit,
        "imported": [],
        "notifications": [
            {
                "title": "Recognition engine",
                "body": "Not connected. This prototype uses simulated processing only.",
                "level": "warning",
            },
            {
                "title": "Review queue",
                "body": "Sample flagged ballots are waiting for officer review.",
                "level": "info",
            },
            {
                "title": "Demo mode",
                "body": "All counts, marks, and decisions are fictional.",
                "level": "info",
            },
        ],
        "settings": copy.deepcopy(DEFAULT_SETTINGS),
        "audit_counter": 1010,
        "ballot_counter": 3001,
    }


class Store(QObject):
    changed = Signal()
    message = Signal(str, str)  # text, level: success | warning | error | info

    def __init__(self) -> None:
        super().__init__()
        self._data = build_sample_data()
        self._load_settings()

    @property
    def data(self) -> dict:
        return self._data

    def settings(self) -> dict:
        return self._data["settings"]

    def _load_settings(self) -> None:
        path = settings_path()
        if not path.exists():
            return
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
            self._data["settings"].update(saved)
        except (OSError, json.JSONDecodeError):
            pass

    def save_settings(self) -> None:
        path = settings_path()
        path.write_text(json.dumps(self._data["settings"], indent=2), encoding="utf-8")
        self.add_audit(
            user="Sahira",
            action="Saved application settings",
            related="SETTINGS",
            event_type="System Event",
            status="Completed",
            detail="Prototype settings written to data/settings.json.",
        )
        self.message.emit("Settings saved for this demonstration.", "success")
        self.changed.emit()

    def reset_settings(self) -> None:
        self._data["settings"] = copy.deepcopy(DEFAULT_SETTINGS)
        path = settings_path()
        if path.exists():
            path.unlink()
        self.message.emit("Settings restored to defaults.", "info")
        self.changed.emit()

    def reset_demo_data(self) -> None:
        saved_settings = copy.deepcopy(self._data["settings"])
        self._data = build_sample_data()
        self._data["settings"] = saved_settings
        self.add_audit(
            user="Sahira",
            action="Cleared demonstration data",
            related="SYSTEM",
            event_type="System Event",
            status="Completed",
            detail="Sample ballots, results, and logs were reset. Not a production wipe.",
        )
        self.message.emit("Demonstration data cleared and sample records restored.", "success")
        self.changed.emit()

    def add_audit(self, user: str, action: str, related: str, event_type: str, status: str, detail: str) -> None:
        self._data["audit_counter"] += 1
        event = {
            "id": f"AUD-{self._data['audit_counter']}",
            "time": datetime.now(),
            "user": user,
            "action": action,
            "related": related,
            "type": event_type,
            "status": status,
            "detail": detail,
        }
        self._data["audit"].insert(0, event)

    def add_imported(self, paths: list[str]) -> None:
        existing = {item["path"] for item in self._data["imported"]}
        added = 0
        for path in paths:
            path = str(path)
            if path in existing:
                continue
            self._data["imported"].append({"path": path, "name": Path(path).name})
            added += 1
        if added:
            self.add_audit(
                user="Sahira",
                action="Imported ballot images",
                related="SCAN",
                event_type="Image Import",
                status="Completed",
                detail=f"{added} image file(s) added. Images are for demonstration only.",
            )
            self.message.emit(f"{added} ballot image(s) imported.", "success")
            self.changed.emit()

    def remove_imported(self, path: str) -> None:
        self._data["imported"] = [item for item in self._data["imported"] if item["path"] != path]
        self.changed.emit()

    def clear_imported(self) -> None:
        self._data["imported"] = []
        self.message.emit("Image selection cleared.", "info")
        self.changed.emit()

    def complete_simulation(self, processed_count: int) -> None:
        stats = self._data["stats"]
        stats["total_processed"] += processed_count
        flagged_new = max(1, processed_count // 4)
        valid_new = max(0, processed_count - flagged_new)
        stats["valid"] += valid_new
        stats["flagged"] += flagged_new
        stats["pending_reviews"] += flagged_new
        self._data["classification"]["valid"] = stats["valid"]
        self._data["classification"]["needs_review"] = stats["flagged"]

        for index in range(flagged_new):
            self._data["ballot_counter"] += 1
            ballot_id = f"BLT-{self._data['ballot_counter']}"
            detected = CANDIDATES[index % len(CANDIDATES)]
            self._data["flagged"].insert(
                0,
                {
                    "id": ballot_id,
                    "batch": "BATCH-DEMO",
                    "reason": "Simulated low-confidence mark",
                    "confidence": 60 + (index * 3) % 15,
                    "status": "Pending Review",
                    "detected": detected,
                    "notes": "",
                    "simulated": True,
                },
            )

        self.add_audit(
            user="System",
            action="Started processing simulation",
            related="SCAN",
            event_type="Processing Simulation",
            status="Completed",
            detail=(
                f"Simulated processing of {processed_count} image(s). "
                "Results are not AI predictions."
            ),
        )
        self.add_audit(
            user="System",
            action="Flagged ballots for review",
            related="BATCH-DEMO",
            event_type="Flagged Ballot",
            status="Completed",
            detail=f"{flagged_new} simulated ballot(s) added to the review queue.",
        )
        self.message.emit(
            "Simulated processing finished. These results are not AI predictions.",
            "warning",
        )
        self.changed.emit()

    def submit_review(self, ballot_id: str, decision: str, notes: str) -> None:
        target = None
        for ballot in self._data["flagged"]:
            if ballot["id"] == ballot_id:
                target = ballot
                break
        if target is None:
            self.message.emit("Select a ballot before submitting a review.", "error")
            return

        was_pending = target["status"] == "Pending Review"
        target["status"] = "Reviewed"
        target["decision"] = decision
        target["notes"] = notes
        if was_pending:
            self._data["stats"]["pending_reviews"] = max(0, self._data["stats"]["pending_reviews"] - 1)
            if decision == "Mark as Rejected":
                self._data["stats"]["rejected"] += 1
                self._data["classification"]["rejected"] += 1
                self._data["stats"]["flagged"] = max(0, self._data["stats"]["flagged"] - 1)
                self._data["classification"]["needs_review"] = self._data["stats"]["flagged"]
            elif decision == "Confirm Detected Mark":
                self._data["stats"]["valid"] += 1
                self._data["classification"]["valid"] += 1
                self._data["stats"]["flagged"] = max(0, self._data["stats"]["flagged"] - 1)
                self._data["classification"]["needs_review"] = self._data["stats"]["flagged"]
                for candidate in self._data["candidates"]:
                    if candidate["name"] == target.get("detected"):
                        candidate["votes"] += 1
                        break

        self.add_audit(
            user="Sahira",
            action=decision,
            related=ballot_id,
            event_type="Review Decision",
            status="Completed",
            detail=f"Simulated review recorded. Notes: {notes or 'None'}",
        )
        self.message.emit(f"Review submitted for {ballot_id}. This is a simulated decision.", "success")
        self.changed.emit()

    def record_export(self, kind: str, path: str) -> None:
        self.add_audit(
            user="Sahira",
            action=f"Exported {kind}",
            related="EXPORT",
            event_type="CSV Export" if kind.lower().endswith("csv") else "System Event",
            status="Completed",
            detail=f"Prototype file written to {path}. Not an official election record.",
        )
        self.message.emit(f"{kind} exported.", "success")
        self.changed.emit()
