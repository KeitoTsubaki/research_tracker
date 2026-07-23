export interface Paper {
  id: string;
  title: string;
  authors: string[];
  source: "arxiv" | "conference_award";
  category: string;
  conference: string | null;
  award: string | null;
  url: string;
  abstract: string;
  published_date: string;
  fetched_at: string;
  tags: string[];
  memo: string;
  memo_updated_at: string | null;
  /** Whether the paper is known to be accepted/published somewhere, or
   * still just a preprint. For arxiv papers this is a heuristic guess
   * based on the author-provided arXiv comment/journal-ref metadata
   * (see scripts/lib/venue.py); conference_award papers are always
   * "published" since being an award winner implies acceptance. */
  venue_status?: "published" | "preprint";
  /** Raw arXiv comment text the venue_status guess was based on, shown
   * to let the user judge the heuristic for themselves (e.g. "Accepted
   * to CVPR 2025"). Null/absent for conference_award papers and for
   * older arxiv entries not yet backfilled. */
  venue_note?: string | null;
}
