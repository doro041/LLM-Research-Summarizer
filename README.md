# LLM Research Summarizer

An intelligent research paper summarization tool powered by Google's Gemini AI. This application automatically processes academic PDFs and generates structured summaries with key findings, methodology, results, and limitations.

## Features

- 📄 **PDF Processing**: Automatically extracts and processes text from research papers
- 🤖 **AI-Powered Summarization**: Uses Google's Gemini 2.5 Flash model for intelligent summarization
- 📊 **Structured Output**: Extracts title, contributions, methodology, results, and limitations
- 📝 **Multiple Export Formats**: 
  - Markdown (`.md`)
  - LaTeX (`.tex`)
  - Microsoft Word (`.docx`)
  - PDF (`.pdf`) - optional, requires additional setup
- ⚡ **Batch Processing**: Efficiently handles large documents with intelligent chunking
- 🔄 **Rate Limit Handling**: Built-in retry logic and rate limiting for API stability
- 📚 **Citation Network Analysis**: Identifies key papers, research lineage, and citation patterns
- 💬 **Interactive Q&A**: Ask questions about the paper and get AI-powered answers
- 🔬 **Research Gap Identification**: Discovers future research opportunities

## Project Structure

```
LLM-Research-Summarizer/
├── app/
│   ├── chains/           # LangChain map-reduce chains
│   ├── exporters/        # Export to various formats (MD, PDF, DOCX, LaTeX)
│   ├── loaders/          # PDF loading and text splitting
│   ├── prompts/          # AI prompt templates
│   ├── schemas/          # Pydantic data models
│   ├── services/         # Core services (summarizer, citation analyzer, Q&A system)
│   └── config.py         # Configuration settings
├── data/                 # Input PDFs go here
├── examples/             # Example scripts
├── main.py              # Main entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Prerequisites

- Python 3.12
- Google Gemini API key
- GTK libraries (optional, for PDF export on Windows)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/doro041/LLM-Research-Summarizer.git
   cd LLM-Research-Summarizer
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**
   
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```
   
   Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

5. **Optional: Install GTK for PDF export** (Windows only)
   
   Download and install from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
   
   Without this, PDF export will be disabled, but all other formats will work.

## Usage

### Basic Usage (Comprehensive Analysis)

1. **Place your PDF** in the `data/` directory

2. **Update the filename** in `main.py`:
   ```python
   pdf_path = "data/your_paper.pdf"
   ```

3. **Run the comprehensive analysis**:
   ```bash
   python main.py
   ```

4. **Find your outputs**:
   
   **Summary files:**
   - `summary.md` - Markdown version
   - `summary.tex` - LaTeX version
   - `summary.docx` - Word document
   - `summary.pdf` - PDF version (if GTK is installed)
   
   **Citation Analysis:**
   - `citation_analysis.md` - Citation network analysis report
   - `citation_analysis.tex` - LaTeX version
   
   **Q&A Analysis:**
   - `qa_analysis.md` - Comprehensive Q&A about the paper
   - `qa_analysis.tex` - LaTeX version
   
   **Research Opportunities:**
   - `research_gaps.md` - Identified future research directions

### Interactive Q&A Mode

Ask questions interactively about a research paper:

```bash
python main.py --interactive
```

Then follow the prompts to ask questions like:
- "What methodology did the authors use?"
- "What datasets were used for evaluation?"
- "What are the main contributions?"
- "How does this compare to previous work?"

### Using Example Scripts

**Analyze a single paper:**
```bash
python examples/analyze_paper.py data/your_paper.pdf
```

**Compare two papers:**
```bash
python examples/analyze_paper.py paper1.pdf paper2.pdf
```

**Interactive Q&A:**
```bash
python examples/analyze_paper.py -i data/your_paper.pdf
```

## Configuration

Edit `app/config.py` to customize:

```python
GEMINI_MODEL = "gemini-2.5-flash-lite"  # AI model to use
TEMPERATURE = 0                          # 0 = deterministic, 1 = creative
CHUNK_SIZE = 4000                        # Characters per chunk
CHUNK_OVERLAP = 200                      # Overlap between chunks
MAP_KWARGS = {"max_tokens": 512}         # Tokens for initial summaries
REDUCE_KWARGS = {"max_tokens": 512}      # Tokens for final summary
```

## How It Works

1. **PDF Loading**: The PDF is loaded and split into manageable chunks
2. **Batching**: Chunks are grouped to optimize API usage
3. **Map Phase**: Each batch is summarized independently using Gemini AI
4. **Reduce Phase**: Partial summaries are combined into a structured final summary
5. **Export**: The summary is exported to multiple formats

The summarization uses a map-reduce approach:
- **Map**: Processes document chunks in parallel to create partial summaries
- **Reduce**: Combines partial summaries into a cohesive structured output

## Output Schema

The generated summary follows this structure:

```json
{
  "title": "Paper Title",
  "contributions": [
    "Key contribution 1",
    "Key contribution 2"
  ],
  "methodology": "Description of methods used",
  "results": "Main findings and outcomes",
  "limitations": [
    "Limitation 1",
    "Limitation 2"
  ]
}
```

## Rate Limits

The application includes built-in rate limiting to respect Google's API limits:
- Default: 4 requests per minute
- Automatic retry on rate limit errors
- Configurable delay between requests

## Dependencies

- **langchain**: Framework for LLM applications
- **google-generativeai**: Google's Gemini AI SDK
- **pypdf**: PDF text extraction
- **pydantic**: Data validation
- **python-docx**: Word document generation
- **markdown**: Markdown processing
- **weasyprint**: PDF generation (optional)

See `requirements.txt` for full dependency list.

## Troubleshooting

### PDF Export Not Available
If you see "PDF export unavailable", install GTK libraries:
- Windows: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
- macOS: `brew install gtk+3`
- Linux: `sudo apt-get install libgtk-3-0`

### API Rate Limit Errors
- The application automatically handles rate limits with retries
- If persistent, reduce `requests_per_minute` in `summarizer.py`

### Missing API Key
Ensure your `.env` file contains:
```
GOOGLE_API_KEY=your_actual_api_key
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by [Google Gemini AI](https://deepmind.google/technologies/gemini/)

---

**Note**: This tool is designed for academic and research purposes. Please ensure you have the right to process and summarize any documents you use with this application.
