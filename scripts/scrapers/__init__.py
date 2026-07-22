"""Registry of conference award scrapers.

Add a new conference by dropping a module in this package that exposes
`scrape() -> list[AwardPaper]` (see base.py) and registering it here.
"""
from . import cvpr, icra

SCRAPERS = {
    "icra": icra,
    "cvpr": cvpr,
}
