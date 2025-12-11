# app/services/summariser.py
import google.generativeai as genai
import os
import json
import time
from app.config import TEMPERATURE
from app.schemas.summary import PaperSummary
from app.loaders.pdf_loader import load_and_split

# Configure API key
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def summarise(pdf_path: str) -> PaperSummary:
    """Summarise a PDF using Google's Generative AI."""
  
    chunks = load_and_split(pdf_path)
    print(f"Loaded {len(chunks)} chunks from PDF")
  
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash-lite',
        generation_config={'temperature': TEMPERATURE}
    )
    
    
    batch_size = 3
    batched_chunks = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        combined_text = "\n\n---PAGE BREAK---\n\n".join([d.page_content for d in batch])
        batched_chunks.append(combined_text)
    
    print(f"Batched into {len(batched_chunks)} groups")
    
    # Map phase: summarize each batch
    map_prompt_template = """Summarize the following research paper sections in concise bullet points. Focus on key findings, methods, and results.

TEXT:
{chunk}

Provide a structured summary with the main points."""
    
    partials = []
    requests_per_minute = 4  # Stay under the 5 limit
    delay_between_requests = 60.0 / requests_per_minute
    
    for i, chunk_text in enumerate(batched_chunks, 1):
        print(f"Processing batch {i}/{len(batched_chunks)}...", end=" ", flush=True)
        
        prompt = map_prompt_template.format(chunk=chunk_text)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                partials.append(response.text)
                print("✓")
                break
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    wait_time = 60  # Wait 1 minute on rate limit
                    print(f"\nRate limit hit. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    if attempt == max_retries - 1:
                        raise
                else:
                    raise
  
        if i < len(batched_chunks):
            time.sleep(delay_between_requests)
    
    print("\nCombining summaries...")
    

    reduce_prompt_template = """
You are combining summaries of a research paper.

From the summaries below, extract:
- Title
- Key contributions (bullets)
- Methodology
- Results
- Limitations

Return valid JSON matching this schema:
{schema}

SUMMARIES:
{summaries}
"""
    
    reduce_prompt = reduce_prompt_template.format(
        summaries="\n".join(partials),
        schema=PaperSummary.model_json_schema()
    )
    
    response = model.generate_content(reduce_prompt)
    combined = response.text
  
    if "```json" in combined:
        combined = combined.split("```json")[1].split("```")[0].strip()
    elif "```" in combined:
        combined = combined.split("```")[1].split("```")[0].strip()
    
    print("Done!")
    return PaperSummary(**json.loads(combined))
