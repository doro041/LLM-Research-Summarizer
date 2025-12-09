import os

# Load environment variables FIRST before any other imports
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Manually load from .env if dotenv not installed
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

from app.services.summarizer import summarise
from app.exporters.markdown import to_markdown
from app.exporters.docx import to_docx
from app.exporters.latex import to_latex

# Try to import PDF exporter (requires system libraries on Windows)
try:
    from app.exporters.pdf import to_pdf
    PDF_AVAILABLE = True
except (ImportError, OSError):
    PDF_AVAILABLE = False
    print("Note: PDF export unavailable (WeasyPrint requires GTK libraries)")
    print("Install from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer\n")

def main():
    summary = summarise("data/2512.07235v1.pdf")
    with open("summary.md", "w", encoding="utf-8") as f:
        f.write(to_markdown(summary))
    if PDF_AVAILABLE:
        to_pdf(summary, "summary.pdf")
    
    to_docx(summary, "summary.docx")
    to_latex(summary, "summary.tex")
    
    print("\n✓ Summary generated successfully!")
    print("  - summary.md")
    if PDF_AVAILABLE:
        print("  - summary.pdf")
    print("  - summary.docx")
    print("  - summary.tex")

if __name__ == "__main__":
    main()