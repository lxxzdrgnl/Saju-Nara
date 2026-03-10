"""
rag — RAG 검색 모듈.
ChromaDB(lib.db) + 검색 핸들러(search.py) + 인덱싱(ingest.py) 통합.
"""

from rag.db import search as vector_search, search_multi, COLLECTIONS, get_collection
from rag.search import (
    handle_search_by_context,
    handle_get_ilju_profile,
    handle_get_ten_god_profile,
    handle_get_structure_pattern,
    handle_get_sin_sal_profile,
)
