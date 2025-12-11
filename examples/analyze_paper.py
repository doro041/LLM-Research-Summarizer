# examples/analyze_paper.py
"""
Example script demonstrating the new citation analysis and Q&A features.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.services.citation_analyzer import CitationNetworkAnalyzer
from app.services.qa_system import ResearchQASystem
from app.loaders.pdf_loader import load_and_split

def analyze_single_paper(pdf_path: str):
    """Analyze a single research paper comprehensively."""
    
    print(f"\n📄 Analyzing: {pdf_path}\n")
    

    documents = load_and_split(pdf_path)
    print(f"✓ Loaded {len(documents)} document chunks\n")
    
    print("="*60)
    print("📚 CITATION NETWORK ANALYSIS")
    print("="*60 + "\n")
    
    analyzer = CitationNetworkAnalyzer()
    citations = analyzer.extract_citations_from_documents(documents)
    stats = analyzer.analyze_citations(citations)
    
    print(f"Found {stats.total_citations} total citations")
    print(f"  - {stats.unique_citations} unique citations")
    print(f"  - {len(stats.citation_years)} citations with years")
    print(f"  - Year range: {min(stats.citation_years)} - {max(stats.citation_years)}" if stats.citation_years else "")
    
    if stats.most_cited_authors:
        print(f"\nTop 3 most cited:")
        for author, count in stats.most_cited_authors[:3]:
            print(f"  • {author}: {count} times")
    
    if stats.key_papers:
        print(f"\nKey foundational papers identified: {len(stats.key_papers)}")

    print("\n" + "="*60)
    print("🤖 RESEARCH Q&A")
    print("="*60 + "\n")
    
    qa_system = ResearchQASystem()

    important_questions = [
        "What is the main contribution of this paper?",
        "What methodology did the authors use?",
        "What datasets were used for evaluation?",
        "What are the key results?"
    ]
    
    for question in important_questions:
        print(f"Q: {question}")
        result = qa_system.answer_question(question, documents, context_window=4)
        print(f"A: {result['answer'][:200]}...")
        print(f"   (Confidence: {result['confidence']})\n")
    

    print("="*60)
    print("🔬 RESEARCH OPPORTUNITIES")
    print("="*60 + "\n")
    
    gaps = qa_system.generate_research_gaps(documents)
    for i, gap in enumerate(gaps, 1):
        print(f"{i}. {gap}")
    
    print("\n" + "="*60)
    print("✅ Analysis complete!")
    print("="*60)

def compare_two_papers(paper1_path: str, paper2_path: str):
    """Compare two research papers."""
    
    print(f"\n🔬 Comparing two papers:\n")
    print(f"Paper 1: {paper1_path}")
    print(f"Paper 2: {paper2_path}\n")

    docs1 = load_and_split(paper1_path)
    docs2 = load_and_split(paper2_path)
    
    qa_system = ResearchQASystem()
    
    questions = [
        "What methodology did the authors use?",
        "What are the main contributions?",
        "What datasets were used?"
    ]
    
    for question in questions:
        print("="*60)
        comparison = qa_system.comparative_analysis(
            question, 
            docs1, 
            docs2,
            paper1_path,
            paper2_path
        )
        print(comparison)
        print()

def interactive_mode(pdf_path: str):
    """Start interactive Q&A session."""
    documents = load_and_split(pdf_path)
    qa_system = ResearchQASystem()
    qa_system.interactive_session(documents)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python examples/analyze_paper.py <pdf_path>")
        print("  python examples/analyze_paper.py <pdf1> <pdf2>  # Compare two papers")
        print("  python examples/analyze_paper.py -i <pdf_path>  # Interactive mode")
        sys.exit(1)
    
    if sys.argv[1] == '-i' and len(sys.argv) > 2:
        interactive_mode(sys.argv[2])
    elif len(sys.argv) == 3:
        compare_two_papers(sys.argv[1], sys.argv[2])
    else:
        analyze_single_paper(sys.argv[1])
