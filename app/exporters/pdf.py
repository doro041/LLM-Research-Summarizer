# app/exporters/pdf.py
from weasyprint import HTML
from app.schemas.summary import PaperSummary
from app.exporters.markdown import to_markdown
import markdown

def to_pdf(summary: PaperSummary, output_path: str) -> None:
    """Convert PaperSummary to PDF format."""
    # Convert to markdown first
    md_content = to_markdown(summary)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content)
    
    # Add basic CSS styling
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                margin-top: 30px;
                border-bottom: 1px solid #bdc3c7;
                padding-bottom: 5px;
            }}
            ul {{
                line-height: 1.8;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Generate PDF
    HTML(string=styled_html).write_pdf(output_path)
