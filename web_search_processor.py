"""
Web search processor for VoxaAi Assistant.

Library: duckduckgo-search (pip install duckduckgo-search)

Flow:
  1. Extract the search query from the command
  2. Query DuckDuckGo for top results
  3. Feed results to LLM to synthesize a spoken answer
  4. Return a concise, speech-friendly response
"""

import re
from typing import Optional

from processors.base_processor import BaseProcessor, ProcessorContext
from utils.logger import get_logger

logger = get_logger(__name__)


class WebSearchProcessor(BaseProcessor):
    name = "web_search"
    description = "Search the web via DuckDuckGo and summarize results"
    triggers = [
        r"\bsearch (?:the web |online |internet )?for\b",
        r"\blook up\b",
        r"\bgoogle\b",
        r"\bwhat(?:'s| is) (?:the latest|happening with|going on with|new with)\b",
        r"\bwho (?:is|was|are|were)\b.{3,40}\?",
        r"\bwhen (?:did|was|is|will)\b",
        r"\bwhere (?:is|was|are|can)\b",
        r"\bhow (?:do|does|did|to|can)\b.{5,}",
        r"\bwhat caused\b",
        r"\btell me about\b",
        r"\bfind (?:info|information|details) (?:about|on)\b",
        r"\bnews (?:about|on)\b",
        r"\blatest (?:news|updates?|info)\b",
    ]

    def __init__(self, config: dict, llm_client=None):
        super().__init__(config)
        self.llm = llm_client
        self.max_results: int = config.get("max_results", 5)

    def process(self, text: str, context: ProcessorContext) -> str:
        if not self.llm and context.llm:
            self.llm = context.llm

        query = self._extract_query(text)
        if not query:
            return "What would you like me to search for?"

        logger.info(f"Web search: '{query}'")

        try:
            results = self._search(query)
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"I couldn't search the web right now. Error: {str(e)[:100]}"

        if not results:
            return f"I couldn't find any results for '{query}'."

        # Synthesize results with LLM
        if self.llm:
            return self._synthesize_answer(query, results)
        else:
            # Fallback: return first result snippet
            first = results[0]
            return f"Here's what I found about {query}: {first.get('body', 'No information available.')}."

    def _extract_query(self, text: str) -> Optional[str]:
        """Extract the search query from the command."""
        patterns = [
            r"search (?:the web |online |internet )?for (.+)",
            r"look up (.+)",
            r"google (.+)",
            r"find (?:info(?:rmation)? )?(?:about|on) (.+)",
            r"tell me about (.+)",
            r"(?:latest )?news (?:about|on) (.+)",
            r"who (?:is|was|are|were) (.+?)(?:\?|$)",
            r"what(?:'s| is) (.+?)(?:\?|$)",
            r"when (?:did|was|is|will) (.+?)(?:\?|$)",
            r"where (?:is|was|are|can) (.+?)(?:\?|$)",
            r"how (?:do|does|did|to|can) (.+?)(?:\?|$)",
        ]

        text_stripped = text.strip().rstrip("?.,!")
        for pattern in patterns:
            match = re.search(pattern, text_stripped, re.IGNORECASE)
            if match:
                q = match.group(1).strip().rstrip("?.,!")
                if len(q) > 2:
                    return q

        # If no pattern matched but text is a question, use it as-is
        if "?" in text or any(text.lower().startswith(w) for w in
                               ["who", "what", "when", "where", "why", "how"]):
            return text_stripped

        return text_stripped  # Use full text as query

    def _search(self, query: str) -> list[dict]:
        """Perform DuckDuckGo search and return results."""
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=self.max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "body": r.get("body", ""),
                        "url": r.get("href", ""),
                    })
            return results

        except ImportError:
            logger.error("duckduckgo-search not installed. Run: pip install duckduckgo-search")
            return []
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []

    def _synthesize_answer(self, query: str, results: list[dict]) -> str:
        """Use LLM to synthesize search results into a spoken answer."""
        # Build a context string from the results
        context_parts = []
        for i, r in enumerate(results[:3], 1):
            title = r.get("title", "")
            body = r.get("body", "")[:400]  # Limit each snippet
            if title or body:
                context_parts.append(f"Result {i} - {title}: {body}")

        context_str = "\n\n".join(context_parts)

        prompt = (
            f"Based on these web search results, answer the question: '{query}'\n\n"
            f"Search results:\n{context_str}\n\n"
            f"Give a concise, spoken answer (2-4 sentences). "
            f"Don't mention 'search results' or 'according to'. "
            f"Just answer naturally as if you know the answer. "
            f"If results are outdated or unclear, say so briefly."
        )

        try:
            answer = self.llm.generate_simple(prompt)
            return answer or f"I found some results for {query} but couldn't summarize them."
        except Exception as e:
            logger.error(f"LLM synthesis error: {e}")
            # Fallback to first result
            return results[0].get("body", "No results available.")[:300]

    def instant_answer(self, query: str) -> Optional[str]:
        """Get a DuckDuckGo instant answer (when available)."""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                answers = list(ddgs.answers(query))
                if answers:
                    return answers[0].get("text", "")
        except Exception:
            pass
        return None
