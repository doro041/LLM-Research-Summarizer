# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Setup Environment

```bash
# Clone and navigate
git clone https://github.com/doro041/LLM-Research-Summarizer.git
cd LLM-Research-Summarizer
python -m venv venv
venv\Scripts\activate  # Windows


# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file:
```
GOOGLE_API_KEY=your_api_key_here
```

Get your free API key: https://makersuite.google.com/app/apikey

### 3. Add Your Paper

Place your PDF in the `data/` folder:
```
data/
└── your_paper.pdf
```

### 4. Update main.py

Open `main.py` and update line 32:
```python
pdf_path = "data/your_paper.pdf"  # Change this
```

### 5. Run Analysis

```bash
python main.py
```

### 6. Review Results

The tool generates:
- ✅ `summary.md` - Paper summary
- ✅ `citation_analysis.md` - Citation network analysis
- ✅ `qa_analysis.md` - Comprehensive Q&A
- ✅ `research_gaps.md` - Future research opportunities

---

## 💡 Try These Features

### Interactive Q&A
```bash
python main.py --interactive
```
Ask questions about your paper in real-time!

### Compare Papers
```bash
python examples/analyze_paper.py paper1.pdf paper2.pdf
```

### Quick Analysis
```bash
python examples/analyze_paper.py data/your_paper.pdf
```

---

## 📚 Example Output

### Citation Analysis Shows:
- 📊 Total citations and unique references
- 🌟 Most influential papers
- 🔗 Citation clusters (co-cited papers)
- 📅 Temporal distribution
- 🎯 Key foundational papers

### Q&A Analysis Answers:
- ❓ What methodology was used?
- ❓ What datasets were evaluated?
- ❓ What are the main contributions?
- ❓ What are the limitations?
- ❓ What future work is suggested?
- ...and 10+ more questions!

### Research Gaps Identifies:
- 🔬 Unexplored research directions
- 💡 Potential improvements
- 🎯 Real-world applications
- 🚀 Extension opportunities

---

## 🎯 Use Cases

**For Researchers:**
- Quickly understand new papers
- Identify key references
- Find research gaps
- Compare methodologies

**For Literature Reviews:**
- Analyze citation networks
- Track research lineage
- Identify influential works
- Spot research trends

**For Learning:**
- Interactive Q&A with papers
- Understand complex topics
- Extract key insights
- Self-paced exploration

---

## ⚡ Tips

1. **Large Papers**: The tool handles papers of any size with intelligent chunking
2. **Multiple Papers**: Process a batch by updating the PDF path in a loop
3. **Custom Questions**: Use interactive mode for specific queries
4. **Export Formats**: Get LaTeX for papers, Markdown for websites, DOCX for editing

---

## 🆘 Troubleshooting

**"API Key Error"**
→ Check your `.env` file has `GOOGLE_API_KEY=...`

**"Rate Limit"**
→ The tool automatically handles this with retries

**"PDF Not Found"**
→ Check the file path in `main.py` line 32

**"No Citations Found"**
→ Some papers use different citation formats; results may vary

---

## 🎉 You're Ready!

Start analyzing research papers with AI-powered insights!

```bash
python main.py
```
