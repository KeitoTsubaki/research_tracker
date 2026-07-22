import rawPapers from "../../data/papers.json";
import type { Paper } from "./types";

export const papers = rawPapers as Paper[];

export const sortedByDate = (list: Paper[] = papers) =>
  [...list].sort((a, b) => b.published_date.localeCompare(a.published_date));

export const categories = [...new Set(papers.map((p) => p.category))].sort();

export const conferences = [...new Set(papers.map((p) => p.conference).filter((c): c is string => !!c))].sort();

// Keyword groups shown as top-level filter toggles. Must stay in sync with
// the tag slugs assigned by scripts/lib/keywords.py.
export const KEYWORD_GROUPS = [
  { slug: "marl", label: "MARL" },
  { slug: "cooperative-transport", label: "協調ロボット搬送" },
  { slug: "autonomous-driving", label: "自動運転" },
] as const;
