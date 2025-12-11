# app/exporters/citation_report.py
from app.services.citation_analyzer import CitationStats

def export_citation_markdown(stats: CitationStats, output_path: str):
    """Export citation analysis as markdown."""
    from app.services.citation_analyzer import CitationNetworkAnalyzer
    
    analyzer = CitationNetworkAnalyzer()
    report = analyzer.generate_citation_report(stats)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return output_path

def export_citation_latex(stats: CitationStats, output_path: str):
    """Export citation analysis as LaTeX."""
    from app.services.citation_analyzer import CitationNetworkAnalyzer
    
    analyzer = CitationNetworkAnalyzer()
    md_report = analyzer.generate_citation_report(stats)
    
    # Convert markdown to LaTeX
    latex = []
    latex.append(r"\section{Citation Network Analysis}")
    latex.append("")
    
    lines = md_report.split('\n')
    for line in lines:
        if line.startswith('# '):
            continue  # Skip main title
        elif line.startswith('## '):
            section_title = line.replace('## ', '').replace('📚 ', '').replace('📅 ', '').replace('🌟 ', '').replace('🔑 ', '').replace('🔗 ', '').replace('🗺️ ', '').replace('🏗️ ', '')
            latex.append(f"\\subsection{{{section_title}}}")
        elif line.startswith('### '):
            subsection_title = line.replace('### ', '')
            latex.append(f"\\subsubsection{{{subsection_title}}}")
        elif line.startswith('- '):
            item = line.replace('- ', '').replace('**', '\\textbf{').replace('**', '}')
            latex.append(f"\\item {item}")
        elif line.strip().startswith('*') and not line.strip().startswith('**'):
            latex.append(f"\\textit{{{line.strip('*').strip()}}}")
        elif '**' in line:
            line = line.replace('**', '\\textbf{').replace('**', '}')
            latex.append(line)
        elif line.strip():
            latex.append(line)
        else:
            latex.append("")
    
    latex_content = '\n'.join(latex)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    return output_path
