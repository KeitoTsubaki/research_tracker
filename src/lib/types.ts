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
}
