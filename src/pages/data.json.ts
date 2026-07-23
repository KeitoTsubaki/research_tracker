import { papers } from "../lib/papers";

export async function GET() {
  return new Response(JSON.stringify(papers), {
    headers: { "Content-Type": "application/json" },
  });
}
