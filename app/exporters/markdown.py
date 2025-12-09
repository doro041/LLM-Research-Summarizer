# app/exporters/markdown.py
from app.schemas.summary import PaperSummary

def to_markdown(summary: PaperSummary) -> str:
    """Convert PaperSummary to Markdown format."""
    md = f"# {summary.title}\n\n"
    
    md += "## Key Contributions\n\n"
    for contrib in summary.contributions:
        md += f"- {contrib}\n"
    
    md += "\n## Methodology\n\n"
    md += f"{summary.methodology}\n\n"
    
    md += "## Results\n\n"
    md += f"{summary.results}\n\n"
    
    md += "## Limitations\n\n"
    for limitation in summary.limitations:
        md += f"- {limitation}\n"
    
    return md
