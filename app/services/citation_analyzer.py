# app/services/citation_analyzer.py
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import Counter
from langchain_core.documents import Document

@dataclass
class Citation:
    """Represents a citation found in the paper."""
    authors: str
    year: Optional[int]
    title: Optional[str]
    raw_text: str
    context: str  # Surrounding text where citation appears
    section: str  # Which section it appeared in

@dataclass
class CitationStats:
    """Statistics about citations in the paper."""
    total_citations: int
    unique_citations: int
    most_cited_authors: List[tuple]
    citation_years: List[int]
    avg_citations_per_section: float
    citation_clusters: List[Dict[str, Any]]
    temporal_distribution: Dict[str, int]
    key_papers: List[Dict[str, Any]]

class CitationNetworkAnalyzer:
    """Analyzes citation patterns and networks in research papers."""
    
    def __init__(self):
        # Common citation patterns in academic papers
        self.citation_patterns = [
            r'\(([A-Z][a-zA-Z\s]+(?:\s+et\s+al\.?)?)[,\s]+(\d{4}[a-z]?)\)',  # (Author et al., 2023)
            r'\[(\d+(?:,\s*\d+)*)\]',  # [1] or [1, 2, 3]
            r'([A-Z][a-zA-Z]+\s+et\s+al\.?\s+\[(\d+)\])',  # Author et al. [1]
            r'([A-Z][a-zA-Z]+\s+and\s+[A-Z][a-zA-Z]+)[,\s]+(\d{4})',  # Author and Author, 2023
            r'([A-Z][a-zA-Z]+)\s+\((\d{4})\)',  # Author (2023)
        ]
        
    def extract_citations_from_documents(self, documents: List[Document]) -> List[Citation]:
        """Extract citations from document chunks."""
        all_citations = []
        
        for i, doc in enumerate(documents):
            section = f"Section {i+1}"
            citations = self._extract_citations_from_text(doc.page_content, section)
            all_citations.extend(citations)
        
        return all_citations
    
    def _extract_citations_from_text(self, text: str, section: str) -> List[Citation]:
        """Extract citations from text with context."""
        citations = []
        
        # Split text into sentences for context
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            # Try each citation pattern
            for pattern in self.citation_patterns:
                matches = re.finditer(pattern, sentence)
                for match in matches:
                    try:
                        groups = match.groups()
                        
                        # Handle different pattern formats
                        if len(groups) >= 2 and groups[1] and groups[1].isdigit():
                            authors = groups[0].strip()
                            year = int(groups[1][:4])  # Handle years like "2023a"
                        elif len(groups) == 1 and groups[0].isdigit():
                            # Numeric citation like [1]
                            authors = f"Citation {groups[0]}"
                            year = None
                        else:
                            authors = groups[0].strip() if groups[0] else match.group(0)
                            year = None
                        
                        citation = Citation(
                            authors=authors,
                            year=year,
                            title=None,
                            raw_text=match.group(0),
                            context=sentence.strip(),
                            section=section
                        )
                        citations.append(citation)
                    except (IndexError, ValueError) as e:
                        continue
        
        return citations
    
    def analyze_citations(self, citations: List[Citation]) -> CitationStats:
        """Analyze citation patterns and generate comprehensive statistics."""
        if not citations:
            return CitationStats(
                total_citations=0,
                unique_citations=0,
                most_cited_authors=[],
                citation_years=[],
                avg_citations_per_section=0.0,
                citation_clusters=[],
                temporal_distribution={},
                key_papers=[]
            )
        
        # Count author frequencies
        author_counter = Counter(c.authors for c in citations)
        most_cited = author_counter.most_common(10)
        
        # Extract and analyze years
        years = [c.year for c in citations if c.year and 1900 < c.year < 2030]
        temporal_dist = self._calculate_temporal_distribution(years)
        
        # Identify citation clusters (frequently co-cited papers)
        clusters = self._identify_clusters(citations)
        
        # Identify key papers
        key_papers = self._identify_key_papers(citations)
        
        # Calculate unique citations
        unique_cites = len(set(c.raw_text for c in citations))
        
        # Calculate avg per section
        sections = set(c.section for c in citations)
        avg_per_section = len(citations) / max(1, len(sections))
        
        return CitationStats(
            total_citations=len(citations),
            unique_citations=unique_cites,
            most_cited_authors=most_cited,
            citation_years=sorted(years),
            avg_citations_per_section=avg_per_section,
            citation_clusters=clusters,
            temporal_distribution=temporal_dist,
            key_papers=key_papers
        )
    
    def _calculate_temporal_distribution(self, years: List[int]) -> Dict[str, int]:
        """Calculate distribution of citations across time periods."""
        if not years:
            return {}
        
        distribution = {
            "pre_2000": 0,
            "2000_2010": 0,
            "2010_2015": 0,
            "2015_2020": 0,
            "2020_present": 0
        }
        
        for year in years:
            if year < 2000:
                distribution["pre_2000"] += 1
            elif year < 2010:
                distribution["2000_2010"] += 1
            elif year < 2015:
                distribution["2010_2015"] += 1
            elif year < 2020:
                distribution["2015_2020"] += 1
            else:
                distribution["2020_present"] += 1
        
        return distribution
    
    def _identify_clusters(self, citations: List[Citation]) -> List[Dict[str, Any]]:
        """Identify groups of papers frequently cited together."""
        clusters = []
        
        # Group citations by context (papers cited in same sentence/paragraph)
        context_groups = {}
        for citation in citations:
            # Use first 150 chars of context as key
            context_key = citation.context[:150].strip()
            if len(context_key) > 50:  # Only meaningful contexts
                if context_key not in context_groups:
                    context_groups[context_key] = []
                context_groups[context_key].append(citation)
        
        # Find contexts with multiple citations (co-citations)
        for context, cites in context_groups.items():
            if len(cites) >= 2:
                clusters.append({
                    "size": len(cites),
                    "authors": [c.authors for c in cites],
                    "years": [c.year for c in cites if c.year],
                    "context": context[:250],
                    "theme": self._infer_theme(context),
                    "section": cites[0].section
                })
        
        # Sort by cluster size and return top 10
        return sorted(clusters, key=lambda x: x["size"], reverse=True)[:10]
    
    def _infer_theme(self, context: str) -> str:
        """Infer the research theme from citation context."""
        context_lower = context.lower()
        
        themes = {
            "methodology": ["method", "approach", "technique", "algorithm", "model", "framework"],
            "dataset": ["dataset", "corpus", "benchmark", "data collection", "evaluation"],
            "related_work": ["similar", "previous", "prior", "related work", "survey"],
            "results": ["achieve", "performance", "accuracy", "improvement", "outperform", "results"],
            "theory": ["prove", "theorem", "theory", "mathematical", "formal"],
            "application": ["application", "real-world", "practical", "use case"],
            "baseline": ["baseline", "compared to", "state-of-the-art", "sota"]
        }
        
        theme_scores = {}
        for theme, keywords in themes.items():
            score = sum(1 for keyword in keywords if keyword in context_lower)
            if score > 0:
                theme_scores[theme] = score
        
        if theme_scores:
            return max(theme_scores.items(), key=lambda x: x[1])[0]
        return "general"
    
    def _identify_key_papers(self, citations: List[Citation]) -> List[Dict[str, Any]]:
        """Identify the most important cited papers based on context."""
        citation_importance = []
        
        # Keywords that indicate importance
        high_importance = ["seminal", "influential", "groundbreaking", "pioneering", "foundational", "landmark"]
        medium_importance = ["based on", "building on", "extends", "improves", "proposed", "introduced"]
        context_importance = ["state-of-the-art", "sota", "benchmark", "standard"]
        
        for citation in citations:
            context_lower = citation.context.lower()
            importance_score = 0
            reasons = []
            
            # Score based on context keywords
            if any(word in context_lower for word in high_importance):
                importance_score += 3
                reasons.append("Foundational work")
            
            if any(word in context_lower for word in medium_importance):
                importance_score += 2
                reasons.append("Methodological basis")
            
            if any(word in context_lower for word in context_importance):
                importance_score += 2
                reasons.append("Performance benchmark")
            
            # Bonus for specific mentions
            if "method" in context_lower or "approach" in context_lower:
                importance_score += 1
                reasons.append("Core methodology")
            
            if importance_score > 0:
                citation_importance.append({
                    "authors": citation.authors,
                    "year": citation.year,
                    "score": importance_score,
                    "reasons": list(set(reasons)),
                    "context": citation.context[:200]
                })
        
        # Sort by importance and return top 10
        citation_importance.sort(key=lambda x: x["score"], reverse=True)
        return citation_importance[:10]
    
    def generate_citation_report(self, stats: CitationStats) -> str:
        """Generate a human-readable citation analysis report."""
        report = []
        report.append("# 📚 Citation Network Analysis\n")
        
        # Overview
        report.append("## Overview")
        report.append(f"- **Total Citations**: {stats.total_citations}")
        report.append(f"- **Unique Citations**: {stats.unique_citations}")
        report.append(f"- **Average Citations per Section**: {stats.avg_citations_per_section:.1f}\n")
        
        # Temporal analysis
        if stats.citation_years:
            report.append("## 📅 Temporal Analysis")
            year_range = f"{min(stats.citation_years)} - {max(stats.citation_years)}"
            median_year = sorted(stats.citation_years)[len(stats.citation_years)//2]
            report.append(f"- **Citation Year Range**: {year_range}")
            report.append(f"- **Median Citation Year**: {median_year}")
            
            if stats.temporal_distribution:
                report.append("\n**Distribution:**")
                for period, count in stats.temporal_distribution.items():
                    if count > 0:
                        period_label = period.replace("_", " ").title()
                        percentage = (count / len(stats.citation_years)) * 100
                        report.append(f"  - {period_label}: {count} ({percentage:.1f}%)")
            report.append("")
        
        # Research foundation analysis
        if stats.citation_years:
            recent = sum(1 for y in stats.citation_years if y >= 2020)
            classic = sum(1 for y in stats.citation_years if y < 2015)
            total_with_years = len(stats.citation_years)
            
            report.append("## 🏗️ Research Foundation")
            report.append(f"- **Recent Work (2020+)**: {recent} citations ({(recent/total_with_years*100):.1f}%)")
            report.append(f"- **Classic Work (pre-2015)**: {classic} citations ({(classic/total_with_years*100):.1f}%)")
            
            if recent > classic:
                report.append("- **Assessment**: Building on recent advances and emerging research")
            elif classic > recent:
                report.append("- **Assessment**: Grounded in established foundations and classic works")
            else:
                report.append("- **Assessment**: Balanced mix of classic foundations and recent developments")
            report.append("")
        
        # Most cited authors
        if stats.most_cited_authors:
            report.append("## 🌟 Most Influential Citations")
            for i, (author, count) in enumerate(stats.most_cited_authors[:10], 1):
                report.append(f"{i}. **{author}** — cited {count} time{'s' if count > 1 else ''}")
            report.append("")
        
        # Key papers
        if stats.key_papers:
            report.append("## 🔑 Key Papers Identified")
            report.append("*Papers that appear to be foundational to this work:*\n")
            for i, paper in enumerate(stats.key_papers[:5], 1):
                year_str = f" ({paper['year']})" if paper['year'] else ""
                report.append(f"### {i}. {paper['authors']}{year_str}")
                report.append(f"**Importance**: {', '.join(paper['reasons'])}")
                report.append(f"**Context**: \"{paper['context']}...\"\n")
        
        # Citation clusters
        if stats.citation_clusters:
            report.append("## 🔗 Citation Clusters")
            report.append("*Groups of papers frequently cited together:*\n")
            for i, cluster in enumerate(stats.citation_clusters[:5], 1):
                report.append(f"### Cluster {i}: {cluster['theme'].replace('_', ' ').title()}")
                report.append(f"**Papers ({cluster['size']})**: {', '.join(cluster['authors'][:5])}")
                if len(cluster['authors']) > 5:
                    report.append(f"  *...and {len(cluster['authors']) - 5} more*")
                report.append(f"**Section**: {cluster['section']}")
                report.append(f"**Context**: \"{cluster['context']}...\"\n")
        
        # Research landscape insights
        report.append("## 🗺️ Research Landscape Insights")
        if stats.citation_clusters:
            themes = [c['theme'] for c in stats.citation_clusters]
            theme_counts = Counter(themes)
            report.append("**Dominant Research Areas:**")
            for theme, count in theme_counts.most_common(3):
                report.append(f"  - {theme.replace('_', ' ').title()}: {count} citation cluster(s)")
        
        report.append("\n*This analysis helps identify the research lineage, influential works, and thematic connections in the paper.*")
        
        return "\n".join(report)
