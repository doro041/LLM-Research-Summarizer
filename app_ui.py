import os
import sys
import gradio as gr
from pathlib import Path

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
from app.exporters.markdown import to_markdown
from app.exporters.docx import to_docx
from app.exporters.latex import to_latex
from app.exporters.qa_report import export_qa_markdown, export_qa_latex, export_research_gaps_markdown

try:
    from app.exporters.pdf import to_pdf
    PDF_AVAILABLE = True
except (ImportError, OSError):
    PDF_AVAILABLE = False


def process_paper(pdf_file, features, export_formats):
    if pdf_file is None:
        return "Please upload a PDF file.", None, None, None, None, None, None, None, None
    
    if not features:
        return "Please select at least one feature.", None, None, None, None, None, None, None, None
    
    if not export_formats:
        return "Please select at least one export format.", None, None, None, None, None, None, None, None
    
    try:
        pdf_path = pdf_file.name
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        base_name = Path(pdf_path).stem
        results = {"status": "Processing...", "files": {}}
        
        summary_obj = None
        qa_results = None
        research_gaps = None
        audio_path = None
        
        if "Summary" in features:
            results["status"] = "Generating summary..."
            summary_obj = summarise(pdf_path)
            
            if "Markdown" in export_formats:
                md_path = output_dir / f"{base_name}_summary.md"
                md_content = to_markdown(summary_obj)
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                results["files"]["summary_md"] = str(md_path)
            
            if "LaTeX" in export_formats:
                tex_path = output_dir / f"{base_name}_summary.tex"
                to_latex(summary_obj, str(tex_path))
                results["files"]["summary_tex"] = str(tex_path)
            
            if "DOCX" in export_formats:
                docx_path = output_dir / f"{base_name}_summary.docx"
                to_docx(summary_obj, str(docx_path))
                results["files"]["summary_docx"] = str(docx_path)
            
            if "PDF" in export_formats and PDF_AVAILABLE:
                pdf_path_out = output_dir / f"{base_name}_summary.pdf"
                to_pdf(summary_obj, str(pdf_path_out))
                results["files"]["summary_pdf"] = str(pdf_path_out)
        
        if "Audio Summary" in features:
            if summary_obj is None:
                summary_obj = summarise(pdf_path)
            
            results["status"] = "Generating audio..."
            audio_path = output_dir / f"{base_name}_summary.mp3"
            generate_audio_summary(summary_obj, str(audio_path))
            results["files"]["audio"] = str(audio_path)
        
        if "Q&A" in features:
            results["status"] = "Running Q&A analysis..."
            qa_system = ResearchQASystem(pdf_path)
            qa_results = qa_system.answer_predefined_questions()
            
            if "Markdown" in export_formats:
                qa_md_path = output_dir / f"{base_name}_qa.md"
                export_qa_markdown(qa_results, str(qa_md_path))
                results["files"]["qa_md"] = str(qa_md_path)
            
            if "LaTeX" in export_formats:
                qa_tex_path = output_dir / f"{base_name}_qa.tex"
                export_qa_latex(qa_results, str(qa_tex_path))
                results["files"]["qa_tex"] = str(qa_tex_path)
        
        if "Research Gaps" in features:
            if qa_results is None:
                qa_system = ResearchQASystem(pdf_path)
                qa_results = qa_system.answer_predefined_questions()
            
            results["status"] = "Identifying research gaps..."
            qa_system = ResearchQASystem(pdf_path)
            research_gaps = qa_system.generate_research_gaps()
            
            if "Markdown" in export_formats:
                gaps_md_path = output_dir / f"{base_name}_research_gaps.md"
                export_research_gaps_markdown(research_gaps, str(gaps_md_path))
                results["files"]["gaps_md"] = str(gaps_md_path)
        
        status_msg = "✅ Processing complete!\n\n"
        status_msg += f"Generated {len(results['files'])} files in the 'output' folder."
        
        return (
            status_msg,
            results["files"].get("summary_md"),
            results["files"].get("summary_tex"),
            results["files"].get("summary_docx"),
            results["files"].get("summary_pdf"),
            results["files"].get("audio"),
            results["files"].get("qa_md"),
            results["files"].get("qa_tex"),
            results["files"].get("gaps_md")
        )
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return error_msg, None, None, None, None, None, None, None, None


custom_css = """
.gradio-container {
    font-family: 'Inter', sans-serif;
    max-width: 1400px !important;
}
.header-box {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    margin-bottom: 2rem;
    color: white;
}
.feature-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
}
.upload-box {
    border: 2px dashed #667eea !important;
    border-radius: 12px !important;
    padding: 2rem !important;
    background: #f8f9ff !important;
    transition: all 0.3s ease;
}
.upload-box:hover {
    border-color: #764ba2 !important;
    background: #f0f2ff !important;
}
"""

with gr.Blocks(title="LLM Research Summarizer", theme=gr.themes.Soft(primary_hue="purple", secondary_hue="blue"), css=custom_css) as app:
    
    with gr.Column():
        gr.HTML("""
            <div class="header-box">
                <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">📚 LLM Research Summarizer</h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.95;">
                    Transform research papers into structured summaries, audio, Q&A insights, and identify research gaps
                </p>
            </div>
        """)
    
    with gr.Row():
        with gr.Column(scale=2):
            with gr.Group():
                gr.Markdown("### 📄 Upload Document")
                pdf_input = gr.File(
                    label="",
                    file_types=[".pdf"],
                    type="filepath",
                    elem_classes="upload-box",
                    height=150
                )
            
            with gr.Group():
                gr.Markdown("### ⚙️ Select Features")
                features = gr.CheckboxGroup(
                    label="",
                    choices=[
                        ("📝 Generate Summary", "Summary"),
                        ("🎧 Audio Summary (Text-to-Speech)", "Audio Summary"),
                        ("❓ Q&A Analysis (15+ Questions)", "Q&A"),
                        ("🔬 Research Gaps Identification", "Research Gaps")
                    ],
                    value=["Summary"],
                    show_label=False
                )
            
            with gr.Group():
                gr.Markdown("### 💾 Export Formats")
                export_formats = gr.CheckboxGroup(
                    label="",
                    choices=[
                        ("📑 Markdown (.md)", "Markdown"),
                        ("📐 LaTeX (.tex)", "LaTeX"),
                        ("📘 Word Document (.docx)", "DOCX"),
                        ("📕 PDF Document (.pdf)", "PDF")
                    ],
                    value=["Markdown"],
                    show_label=False
                )
            
            process_btn = gr.Button(
                "🚀 Process Research Paper", 
                variant="primary", 
                size="lg",
                scale=1
            )
        
        with gr.Column(scale=3):
            status_output = gr.Textbox(
                label="📊 Processing Status", 
                lines=4,
                show_label=True,
                interactive=False
            )
            
            gr.Markdown("### 📥 Download Results")
            
            with gr.Accordion("📝 Summary Files", open=True):
                with gr.Row():
                    summary_md = gr.File(label="Markdown", scale=1)
                    summary_tex = gr.File(label="LaTeX", scale=1)
                with gr.Row():
                    summary_docx = gr.File(label="DOCX", scale=1)
                    summary_pdf = gr.File(label="PDF", scale=1)
            
            with gr.Accordion("🎧 Audio & Analysis", open=True):
                with gr.Row():
                    audio_file = gr.File(label="🎵 Audio Summary (MP3)", scale=1)
                with gr.Row():
                    qa_md = gr.File(label="❓ Q&A Report (Markdown)", scale=1)
                    qa_tex = gr.File(label="❓ Q&A Report (LaTeX)", scale=1)
                with gr.Row():
                    gaps_md = gr.File(label="🔬 Research Gaps (Markdown)", scale=1)
    
    process_btn.click(
        fn=process_paper,
        inputs=[pdf_input, features, export_formats],
        outputs=[
            status_output,
            summary_md,
            summary_tex,
            summary_docx,
            summary_pdf,
            audio_file,
            qa_md,
            qa_tex,
            gaps_md
        ]
    )
    
    with gr.Row():
        gr.HTML("""
            <div style="text-align: center; padding: 2rem; margin-top: 2rem; background: #f8f9ff; border-radius: 12px;">
                <p style="margin: 0; color: #667eea; font-size: 1rem;">
                    💡 <strong>Pro Tip:</strong> Select multiple features and formats for comprehensive analysis | 
                    🎯 Powered by Google Gemini AI | ⚡ Fast Processing with Rate Limiting
                </p>
            </div>
        """)


if __name__ == "__main__":
    app.launch(share=False, server_name="127.0.0.1", server_port=7860)
