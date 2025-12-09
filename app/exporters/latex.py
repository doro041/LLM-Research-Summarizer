# app/exporters/latex.py
from app.schemas.summary import PaperSummary

def to_latex(summary: PaperSummary, output_path: str) -> None:
    """Convert PaperSummary to LaTeX format."""
    
    # Escape special LaTeX characters
    def escape_latex(text: str) -> str:
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '\\': r'\textbackslash{}',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    latex_content = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}
\usepackage{enumitem}
\usepackage{hyperref}

\title{""" + escape_latex(summary.title) + r"""}
\date{}

\begin{document}
\maketitle

\section{Key Contributions}
\begin{itemize}
"""
    
    for contrib in summary.contributions:
        latex_content += f"\\item {escape_latex(contrib)}\n"
    
    latex_content += r"""\end{itemize}

\section{Methodology}
""" + escape_latex(summary.methodology) + r"""

\section{Results}
""" + escape_latex(summary.results) + r"""

\section{Limitations}
\begin{itemize}
"""
    
    for limitation in summary.limitations:
        latex_content += f"\\item {escape_latex(limitation)}\n"
    
    latex_content += r"""\end{itemize}

\end{document}
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)
