import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:

    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

from app.services.summarizer import summarise
from app.services.qa_system import ResearchQASystem
from app.services.text_to_speech import generate_audio_summary
from app.loaders.pdf_loader import load_and_split
from app.exporters.markdown import to_markdown
from app.exporters.docx import to_docx
from app.exporters.latex import to_latex
from app.exporters.qa_report import export_qa_markdown, export_qa_latex, export_research_gaps_markdown

try:
    from app.exporters.pdf import to_pdf
    PDF_AVAILABLE = True
except (ImportError, OSError):
    PDF_AVAILABLE = False


def get_pdf_path():
    """Get PDF path from user input, supporting drag-and-drop."""
    print("\n📄 Enter PDF path (you can drag and drop the file here):")
    pdf_path = input("Path: ").strip()
    
    
    pdf_path = pdf_path.strip('"').strip("'")
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f" File not found: {pdf_path}")
        return None
    
    if not pdf_path.lower().endswith('.pdf'):
        print(f" File must be a PDF")
        return None
    
    return pdf_path


def select_features():
    """Let user select which features to run."""
    print("\n🎯 SELECT FEATURES TO RUN:")
    print("=" * 50)
    print("1. ✅ Paper Summary (required)")
    print("2. 🔊 Audio Summary (Text-to-Speech)")
    print("3. 💬 Q&A Analysis (15+ questions)")
    print("4. 🔬 Research Gap Identification")
    print("5. 🎯 All Features")
    print("=" * 50)
    
    choice = input("\nEnter your choice (1-5, or comma-separated like '1,2,3'): ").strip()
    
    features = {
        'summary': True,  
        'audio': False,
        'qa': False,
        'gaps': False
    }
    
    if '5' in choice:
        features = {k: True for k in features}
    else:
        if '2' in choice:
            features['audio'] = True
        if '3' in choice:
            features['qa'] = True
        if '4' in choice:
            features['gaps'] = True
    
    return features


def select_export_formats():
    """Let user select which export formats to generate."""
    print("\n📦 SELECT EXPORT FORMATS:")
    print("=" * 50)
    print("1. 📝 Markdown (.md)")
    print("2. 📄 LaTeX (.tex)")
    print("3. 📘 Word Document (.docx)")
    if PDF_AVAILABLE:
        print("4. 📕 PDF (.pdf)")
    else:
        print("4. 📕 PDF (.pdf) - UNAVAILABLE (install GTK)")
    print("5. 🎯 All Available Formats")
    print("=" * 50)
    
    choice = input("\nEnter your choice (1-5, or comma-separated like '1,2,3'): ").strip()
    
    formats = {
        'markdown': False,
        'latex': False,
        'docx': False,
        'pdf': False
    }
    
    if '5' in choice:
        formats = {k: True for k in formats}
        if not PDF_AVAILABLE:
            formats['pdf'] = False
    else:
        if '1' in choice:
            formats['markdown'] = True
        if '2' in choice:
            formats['latex'] = True
        if '3' in choice:
            formats['docx'] = True
        if '4' in choice and PDF_AVAILABLE:
            formats['pdf'] = True
    
    if not any(formats.values()):
        print("⚠️  No format selected, defaulting to Markdown")
        formats['markdown'] = True
    
    return formats


def run_analysis(pdf_path, features, export_formats):
    """Run selected analyses and export in chosen formats."""
    print("\n" + "=" * 70)
    print("🚀 LLM RESEARCH SUMMARIZER - ANALYSIS")
    print("=" * 70)
    print(f"\n📄 Processing: {pdf_path}\n")
    
    results = {}
    outputs = []
    
    # Always load documents for all features
    print("📖 Loading document...")
    documents = load_and_split(pdf_path)
    print(f"✓ Loaded {len(documents)} sections\n")
    
    print("1️⃣  Generating summary...")
    summary = summarise(pdf_path)
    results['summary'] = summary
    print("✓ Summary complete!\n")


    if features['audio']:
        print("2️⃣  Generating audio summary (Text-to-Speech)...")
        audio_path = generate_audio_summary(summary)
        if audio_path:
            results['audio'] = audio_path
            print(f"✓ Audio generated: {audio_path}\n")
        else:
            print("✗ Audio generation failed (install gTTS: pip install gTTS)\n")
    
    if features['qa']:
        print("3️⃣  Running comprehensive Q&A analysis...")
        qa_system = ResearchQASystem()
        qa_results = qa_system.answer_predefined_questions(documents)
        results['qa'] = qa_results
        print("✓ Q&A complete!\n")
    
    if features['gaps']:
        print("4️⃣  Identifying research gaps...")
        if 'qa_system' not in locals():
            qa_system = ResearchQASystem()
        research_gaps = qa_system.generate_research_gaps(documents)
        results['gaps'] = research_gaps
        print(f"✓ Found {len(research_gaps)} opportunities!\n")
    

    print("=" * 70)
    print("📦 EXPORTING RESULTS")
    print("=" * 70 + "\n")
    

    print("Summary exports:")
    if export_formats['markdown']:
        with open("summary.md", "w", encoding="utf-8") as f:
            f.write(to_markdown(summary))
        outputs.append("  ✓ summary.md")
    
    if export_formats['latex']:
        to_latex(summary, "summary.tex")
        outputs.append("  ✓ summary.tex")
    
    if export_formats['docx']:
        to_docx(summary, "summary.docx")
        outputs.append("  ✓ summary.docx")
    
    if export_formats['pdf'] and PDF_AVAILABLE:
        to_pdf(summary, "summary.pdf")
        outputs.append("  ✓ summary.pdf")
    
    # Audio Summary
    if features['audio'] and 'audio' in results:
        print("\nAudio summary:")
        outputs.append(f"  ✓ {results['audio']}")
    
    # Export Q&A
    if features['qa']:
        print("\nQ&A analysis exports:")
        if export_formats['markdown']:
            export_qa_markdown(qa_results, "qa_analysis.md")
            outputs.append("  ✓ qa_analysis.md")
        if export_formats['latex']:
            export_qa_latex(qa_results, "qa_analysis.tex")
            outputs.append("  ✓ qa_analysis.tex")
    
    # Export Research Gaps
    if features['gaps']:
        print("\nResearch opportunities exports:")
        if export_formats['markdown']:
            export_research_gaps_markdown(research_gaps, "research_gaps.md")
            outputs.append("  ✓ research_gaps.md")
    
    # Print Summary
    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 70)
    print("\n📊 Generated files:")
    for output in outputs:
        print(output)
    
    print("\n💡 Key Insights:")
    print(f"  • Paper: {summary.title}")
    if features['audio']:
        print(f"  • Audio summary: Available")
    if features['qa']:
        print(f"  • Questions answered: {len(qa_results)}")
    if features['gaps']:
        print(f"  • Research opportunities identified: {len(research_gaps)}")
    print("\n" + "=" * 70)


def main():
    """Interactive main menu."""
    print("\n" + "=" * 70)
    print("🤖 LLM RESEARCH SUMMARIZER")
    print("=" * 70)
    
    # Get PDF path
    pdf_path = get_pdf_path()
    if not pdf_path:
        return
    
    # Select features
    features = select_features()
    
    # Select export formats
    export_formats = select_export_formats()
    
    # Confirm and run
    print("\n" + "=" * 70)
    print("📋 CONFIGURATION SUMMARY")
    print("=" * 70)
    print(f"📄 PDF: {os.path.basename(pdf_path)}")
    print(f"🎯 Features: {', '.join([k.title() for k, v in features.items() if v])}")
    print(f"📦 Formats: {', '.join([k.upper() for k, v in export_formats.items() if v])}")
    print("=" * 70)
    
    confirm = input("\n▶️  Proceed with analysis? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Analysis cancelled.")
        return
    
    # Run the analysis
    run_analysis(pdf_path, features, export_formats)

def interactive_qa_mode():
    """Start interactive Q&A mode for a paper."""
    pdf_path = input("📄 Enter path to PDF: ").strip()
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    print(f"\n🔄 Loading {pdf_path}...")
    documents = load_and_split(pdf_path)
    print(f"✓ Loaded {len(documents)} sections\n")
    
    qa_system = ResearchQASystem()
    qa_system.interactive_session(documents)

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-i', '--interactive', 'interactive']:
            # Interactive Q&A mode
            interactive_qa_mode()
        elif sys.argv[1].endswith('.pdf'):
            # PDF path provided directly
            pdf_path = sys.argv[1]
            if os.path.exists(pdf_path):
                # Quick run with all features and markdown export
                features = {k: True for k in ['summary', 'audio', 'qa', 'gaps']}
                export_formats = {'markdown': True, 'latex': False, 'docx': False, 'pdf': False}
                run_analysis(pdf_path, features, export_formats)
            else:
                print(f"❌ File not found: {pdf_path}")
        else:
            print("Usage:")
            print("  python main.py                    # Interactive menu")
            print("  python main.py paper.pdf          # Quick analysis with all features")
            print("  python main.py -i                 # Interactive Q&A mode")
    else:
        # Interactive menu mode
        main()