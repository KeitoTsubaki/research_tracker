"""Registry of conference award scrapers.

Add a new conference by dropping a module in this package that exposes
`scrape() -> list[AwardPaper]` (see base.py) and registering it here.
"""
from . import aaai, cvpr, icml, icra, ieee_iv, iros, itsc, neurips, rss

SCRAPERS = {
    "icra": icra,
    "cvpr": cvpr,
    "iros": iros,
    "neurips": neurips,
    "icml": icml,
    "aaai": aaai,
    "rss": rss,
    "ieee_iv": ieee_iv,
    "itsc": itsc,
}
