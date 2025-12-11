# app/services/qa_system.py
import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from langchain_core.documents import Document
from app.config import TEMPERATURE

class ResearchQASystem:
    """Interactive Q&A system for research papers."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=self.api_key)
        
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-lite',  # Better rate limits than 2.5
            generation_config={'temperature': TEMPERATURE}
        )
        
        # Predefined comprehensive question templates
        self.question_templates = {
            "methodology": "What methodology, approach, or technique did the authors use in this research?",
            "dataset": "What datasets, benchmarks, or data sources were used in this research?",
            "results": "What were the main results, findings, and performance metrics?",
            "limitations": "What limitations, weaknesses, or constraints does this study have?",
            "novelty": "What is novel, unique, or innovative about this research?",
            "comparison": "How does this work compare to previous research or state-of-the-art methods?",
            "applications": "What are the practical applications or real-world use cases of this research?",
            "future_work": "What future work, open problems, or research directions do the authors suggest?",
            "reproduce": "What information is provided for reproducing this work (code, data, hyperparameters)?",
            "metrics": "What evaluation metrics and benchmarks were used to assess performance?",
            "architecture": "What model architecture, system design, or technical framework was used?",
            "contributions": "What are the main contributions or key takeaways of this paper?",
            "related_work": "What related work or prior research is discussed and how does this differ?",
            "ablation": "Were ablation studies performed? What components were most important?",
            "compute": "What computational resources, training time, or hardware requirements were needed?"
        }
    
    def answer_question(
        self, 
        question: str, 
        documents: List[Document],
        context_window: int = 5
    ) -> Dict[str, Any]:
        """Answer a specific question about the research paper."""
        
        relevant_chunks = self._find_relevant_chunks(question, documents, context_window)
        
        context = "\n\n---\n\n".join([doc.page_content for doc in relevant_chunks])
        
        prompt = f"""You are an expert research assistant analyzing an academic paper.
Answer the following question based ONLY on the provided context from the paper.

Guidelines:
- Be specific and detailed in your answer
- Quote relevant parts when possible
- If the information is not in the context, state: "This information is not explicitly provided in the paper."
- Cite which section the information comes from when possible

Context from paper:
{context}

Question: {question}

Answer:"""
        
        # Get answer from model
        response = self.model.generate_content(prompt)
        answer_text = response.text
        
        return {
            "question": question,
            "answer": answer_text,
            "relevant_sections": [
                {
                    "text": doc.page_content[:300] + "...",
                    "relevance_score": score
                }
                for score, doc in zip(
                    range(len(relevant_chunks), 0, -1),
                    relevant_chunks[:3]
                )
            ],
            "confidence": self._estimate_confidence(answer_text),
            "source_chunks_used": len(relevant_chunks)
        }
    
    def answer_predefined_questions(self, documents: List[Document]) -> Dict[str, Any]:
        """Answer a comprehensive set of questions about the paper."""
        print("🤔 Answering comprehensive questions about the paper...")
        results = {}
        
        for i, (key, question) in enumerate(self.question_templates.items(), 1):
            print(f"  [{i}/{len(self.question_templates)}] {key}...", end=" ", flush=True)
            try:
                answer = self.answer_question(question, documents, context_window=4)
                results[key] = answer
                print("✓")
            except Exception as e:
                print(f"✗ ({str(e)[:50]})")
                results[key] = {
                    "question": question,
                    "answer": f"Error: {str(e)}",
                    "relevant_sections": [],
                    "confidence": "low",
                    "source_chunks_used": 0
                }
        
        print(" All questions answered!\n")
        return results
    
    def ask_custom_question(self, question: str, documents: List[Document]) -> str:
        """Ask a single custom question and get a formatted answer."""
        result = self.answer_question(question, documents)
        
        output = []
        output.append(f"❓ **Question**: {result['question']}\n")
        output.append(f"💡 **Answer**: {result['answer']}\n")
        output.append(f"📊 **Confidence**: {result['confidence']}")
        output.append(f"📄 **Sources used**: {result['source_chunks_used']} document sections\n")
        
        if result['relevant_sections']:
            output.append("**Relevant context:**")
            for i, section in enumerate(result['relevant_sections'][:2], 1):
                output.append(f"{i}. \"{section['text']}\"")
        
        return "\n".join(output)
    
    def comparative_analysis(
        self, 
        question: str,
        paper1_docs: List[Document],
        paper2_docs: List[Document],
        paper1_title: str = "Paper 1",
        paper2_title: str = "Paper 2"
    ) -> str:
        """Compare two papers based on a specific question."""
        
        print(f"🔬 Comparing papers on: {question}")
        
    
        answer1 = self.answer_question(question, paper1_docs)
        answer2 = self.answer_question(question, paper2_docs)
        
        # Create comparison prompt
        comparison_prompt = f"""You are comparing two research papers.

Question: {question}

{paper1_title}: {answer1['answer']}

{paper2_title}: {answer2['answer']}

Provide a comprehensive comparative analysis:
1. Key similarities between the approaches
2. Key differences and trade-offs
3. Which approach might be more effective and why
4. Potential synergies or ways to combine insights

Comparison:"""
        
        response = self.model.generate_content(comparison_prompt)
        
        return f"""# 🔍 Comparative Analysis

## Question
{question}

## Comparison
{response.text}

---
*Based on analysis of {paper1_title} and {paper2_title}*
"""
    
    def generate_research_gaps(self, documents: List[Document]) -> List[str]:
        """Identify potential research gaps and future directions."""
        
        print("🔎 Identifying research gaps and opportunities...")
        
        # Use conclusion and discussion sections (typically at the end)
        context_parts = []
        
        # Get last chunks (conclusions)
        context_parts.append("CONCLUSIONS AND FUTURE WORK:\n" + "\n".join([
            doc.page_content for doc in documents[-3:]
        ]))
        
        # Get some middle chunks (methodology and results discussion)
        middle_idx = len(documents) // 2
        context_parts.append("METHODOLOGY AND RESULTS:\n" + "\n".join([
            doc.page_content for doc in documents[middle_idx:middle_idx+2]
        ]))
        
        context = "\n\n---\n\n".join(context_parts)
        
        prompt = f"""You are a research strategist identifying opportunities for future research.

Based on the paper content below, identify specific research gaps, limitations that could be addressed, and promising future research directions.

Paper content:
{context}

Provide 5-7 specific, actionable research opportunities in the following format:
1. [Specific research gap or opportunity]
2. [Another specific research gap or opportunity]
...

Focus on:
- Unexplored areas mentioned by authors
- Limitations that could be overcome
- Extensions or generalizations of the work
- Real-world applications not yet tested
- Methodological improvements

Research Opportunities:"""
        
        response = self.model.generate_content(prompt)
        
        # Parse response into list
        lines = response.text.split("\n")
        gaps = []
        for line in lines:
            line = line.strip()
            # Match numbered lines like "1.", "1)", or "- "
            if re.match(r'^[\d\-\*]+[\.\)]\s+', line) or line.startswith("- "):
                clean_line = re.sub(r'^[\d\-\*]+[\.\)]\s+', '', line).strip("- ").strip()
                if clean_line and len(clean_line) > 20:
                    gaps.append(clean_line)
        
        print(f"✓ Identified {len(gaps)} research opportunities\n")
        return gaps[:7]
    
    def generate_qa_report(self, qa_results: Dict[str, Any]) -> str:
        """Generate a comprehensive Q&A report."""
        report = []
        report.append("# 🤖 Research Paper Q&A Analysis\n")
       
        categories = {
            "Core Research": ["contributions", "novelty", "methodology", "architecture"],
            "Experimental Setup": ["dataset", "metrics", "ablation", "compute"],
            "Results & Comparison": ["results", "comparison", "related_work"],
            "Critical Analysis": ["limitations", "future_work", "applications"],
            "Reproducibility": ["reproduce"]
        }
        
        for category, keys in categories.items():
            report.append(f"## {category}\n")
            
            for key in keys:
                if key in qa_results:
                    qa = qa_results[key]
                    report.append(f"### {qa['question']}")
                    report.append(f"{qa['answer']}")
                    report.append(f"*Confidence: {qa['confidence']} | Sources: {qa.get('source_chunks_used', 'N/A')}*\n")
        
        return "\n".join(report)
    
    def _find_relevant_chunks(
        self, 
        question: str, 
        documents: List[Document],
        top_k: int = 5
    ) -> List[Document]:
        """Find most relevant document chunks for the question using keyword matching."""
        # Extract keywords from question
        question_lower = question.lower()
        question_words = set(re.findall(r'\b\w+\b', question_lower))
        
        # Remove common stop words
        stop_words = {'what', 'how', 'why', 'when', 'where', 'which', 'who', 'is', 'are', 
                     'was', 'were', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
                     'to', 'for', 'of', 'with', 'by', 'from', 'this', 'that', 'these', 'those'}
        keywords = question_words - stop_words
        
        # Score each document
        scored_docs = []
        for doc in documents:
            doc_lower = doc.page_content.lower()
            doc_words = set(re.findall(r'\b\w+\b', doc_lower))
            
            # Calculate overlap score
            overlap = len(keywords & doc_words)
            
            # Boost score if keywords appear close together
            proximity_bonus = 0
            for keyword in keywords:
                if keyword in doc_lower:
                    proximity_bonus += doc_lower.count(keyword)
            
            total_score = overlap * 2 + proximity_bonus
            scored_docs.append((total_score, doc))
        
        # Sort by relevance and return top_k
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        return [doc for _, doc in scored_docs[:top_k]]
    
    def _estimate_confidence(self, answer: str) -> str:
        """Estimate confidence level of the answer."""
        answer_lower = answer.lower()
        
        # Low confidence indicators
        low_confidence = [
            "not stated", "not mentioned", "not explicitly", "unclear", 
            "does not specify", "not provided", "not discussed", "insufficient information",
            "not clear", "ambiguous"
        ]
        
        # High confidence indicators
        high_confidence = [
            "specifically", "clearly states", "explicitly", "details", 
            "demonstrates", "shows that", "proves", "indicates",
            "according to", "as stated"
        ]
        
        if any(phrase in answer_lower for phrase in low_confidence):
            return "low"
        elif any(phrase in answer_lower for phrase in high_confidence):
            return "high"
        else:
            return "medium"
    
    def interactive_session(self, documents: List[Document]):
        """Start an interactive Q&A session in the terminal."""
        print("\n" + "="*70)
        print("🔍 RESEARCH PAPER Q&A SYSTEM")
        print("="*70)
        print("\nAsk questions about the paper (type 'quit' or 'exit' to stop)\n")
        print("💡 Example questions:")
        print("  • What methodology did the authors use?")
        print("  • What datasets were used for evaluation?")
        print("  • What are the main contributions of this paper?")
        print("  • How does this compare to previous work?")
        print("  • What are the limitations?")
        print("="*70 + "\n")
        
        while True:
            try:
                question = input("❓ Your question: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', 'q', 'stop']:
                    print("\n👋 Goodbye!\n")
                    break
                
                print("\n🤔 Analyzing paper...\n")
                result = self.answer_question(question, documents)
                
                print(f"💡 Answer:\n{result['answer']}\n")
                print(f"📊 Confidence: {result['confidence']}")
                print(f"📄 Based on {result['source_chunks_used']} document sections\n")
                print("-" * 70 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")

import re
