# app/exporters/qa_report.py
from typing import Dict, Any

def export_qa_markdown(qa_results: Dict[str, Any], output_path: str):
    """Export Q&A results as markdown."""
    from app.services.qa_system import ResearchQASystem
    
    qa_system = ResearchQASystem()
    report = qa_system.generate_qa_report(qa_results)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return output_path

def export_qa_latex(qa_results: Dict[str, Any], output_path: str):
    """Export Q&A results as LaTeX."""
    from app.services.qa_system import ResearchQASystem
    
    qa_system = ResearchQASystem()
    md_report = qa_system.generate_qa_report(qa_results)
    
    # Convert markdown to LaTeX
    latex = []
    latex.append(r"\section{Research Paper Q\&A Analysis}")
    latex.append("")
    
    lines = md_report.split('\n')
    in_answer = False
    
    for line in lines:
        if line.startswith('# '):
            continue  # Skip main title
        elif line.startswith('## '):
            section_title = line.replace('## ', '').replace('🤖 ', '')
            latex.append(f"\\subsection{{{section_title}}}")
            in_answer = False
        elif line.startswith('### '):
            question = line.replace('### ', '')
            latex.append(f"\\subsubsection{{{question}}}")
            in_answer = True
        elif line.strip().startswith('*Confidence:'):
            # Metadata line
            meta = line.strip('*').strip()
            latex.append(f"\\\\\\textit{{{meta}}}")
            latex.append("")
            in_answer = False
        elif '**' in line:
            line = line.replace('**', '\\textbf{').replace('**', '}')
            latex.append(line)
        elif line.strip():
            if in_answer:
                latex.append(line)
            else:
                latex.append(line)
        else:
            latex.append("")
    
    latex_content = '\n'.join(latex)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    return output_path

def export_research_gaps_markdown(gaps: list, output_path: str):
    """Export research gaps as markdown."""
    report = []
    report.append("# 🔬 Research Gaps & Future Opportunities\n")
    report.append("*Potential research directions identified from the paper:*\n")
    
    for i, gap in enumerate(gaps, 1):
        report.append(f"{i}. {gap}")
    
    report.append("\n---")
    report.append("*These opportunities were identified through analysis of the paper's limitations, future work section, and methodological discussions.*")
    
    content = '\n'.join(report)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path
