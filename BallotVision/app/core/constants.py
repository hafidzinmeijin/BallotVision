"""Shared names, colours, and page titles used across BallotVision."""

APP_NAME = "BallotVision"
APP_VERSION = "1.0"
APP_SUBTITLE = "AI-Powered Automated Recognition and Vote Counting System"
USER_ROLE = "Election Officer"
USER_NAME = "Sahira"
WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 900
MIN_WIDTH = 1180
MIN_HEIGHT = 760

CANDIDATES = (
    "Candidate A",
    "Candidate B",
    "Candidate C",
    "Candidate D",
)

PAGES = (
    {
        "id": "dashboard",
        "nav": "Dashboard",
        "title": "Election Overview",
        "subtitle": "Monitor ballot processing and counting activity.",
    },
    {
        "id": "scan",
        "nav": "Scan Ballots",
        "title": "Scan Ballots",
        "subtitle": "Import ballot images and run a simulated processing workflow.",
    },
    {
        "id": "review",
        "nav": "Review Flagged Ballots",
        "title": "Review Flagged Ballots",
        "subtitle": "Inspect uncertain ballots and record an officer decision.",
    },
    {
        "id": "results",
        "nav": "Vote Results",
        "title": "Vote Results",
        "subtitle": "View simulated vote totals for this demonstration session.",
    },
    {
        "id": "audit",
        "nav": "Audit Trail",
        "title": "Audit Trail",
        "subtitle": "Prototype activity log for imports, reviews, and exports.",
    },
    {
        "id": "settings",
        "nav": "Settings",
        "title": "Settings",
        "subtitle": "Configure demonstration preferences for this prototype.",
    },
)

DEFAULT_SETTINGS = {
    "app_name": APP_NAME,
    "theme_name": "Dark Navy",
    "time_format": "24-hour",
    "demo_processing_mode": True,
    "confidence_threshold": 85,
    "require_reviewer_confirmation": True,
    "default_review_filter": "Pending Review",
    "export_format": "CSV",
}
