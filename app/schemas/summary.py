# app/schemas/summary.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PaperSummary(BaseModel):
    title: str
    contributions: List[str]
    methodology: str
    results: str
    limitations: List[str]

class CitationAnalysisResult(BaseModel):
    """Schema for citation network analysis results."""
    total_citations: int
    unique_citations: int
    most_cited_authors: List[tuple]
    citation_years: List[int]
    temporal_distribution: Dict[str, int]
    key_papers: List[Dict[str, Any]]
    citation_clusters: List[Dict[str, Any]]
    citation_report: str

class QAResult(BaseModel):
    """Schema for Q&A analysis results."""
    question: str
    answer: str
    confidence: str
    source_chunks_used: int
    relevant_sections: List[Dict[str, Any]]

class ComprehensiveAnalysis(BaseModel):
    """Complete analysis including summary, citations, and Q&A."""
    summary: PaperSummary
    citation_analysis: Optional[CitationAnalysisResult] = None
    qa_results: Optional[Dict[str, QAResult]] = None
    research_gaps: Optional[List[str]] = None
