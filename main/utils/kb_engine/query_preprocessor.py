"""
Domain-aware query preprocessor for the Endurance Training Knowledge Base.
Filters natural language conversational stopwords and expands domain terminology.
"""

from __future__ import annotations

import re

from .synonyms import STOP_WORDS, expand_synonyms


def extract_searchable_terms(raw_query: str) -> list[str]:
    """Extract filtered alphanumeric tokens from query, removing generic stop words."""
    tokens = re.findall(r"[A-Za-z0-9_'\-]+", raw_query)
    cleaned_tokens: list[str] = []

    for token in tokens:
        cleaned = token.strip("'-").lower()
        if not cleaned or len(cleaned) < 2:
            continue
        if cleaned not in STOP_WORDS:
            cleaned_tokens.append(cleaned)

    # If stop-word filtering removed all tokens, fallback to all valid tokens
    if not cleaned_tokens:
        cleaned_tokens = [t.lower() for t in tokens if len(t) > 1]

    return cleaned_tokens


def expand_domain_synonyms(terms: list[str]) -> list[str]:
    """Expand recognized endurance domain terms with high-signal synonyms."""
    return expand_synonyms(terms)


def preprocess_query(raw_query: str) -> str:
    """Preprocess natural language athlete query into optimized SQLite FTS5 syntax."""
    terms = extract_searchable_terms(raw_query)
    if not terms:
        terms = [t.lower() for t in re.findall(r"\w+", raw_query) if len(t) > 1]
    if not terms:
        return '""'

    expanded = expand_synonyms(terms)
    clauses: list[str] = []
    for term in expanded:
        clean = term.replace('"', "").strip()
        if clean:
            clauses.append(f'"{clean}"')

    return " OR ".join(clauses)
