# app/prompts/reduce.py
from langchain_core.prompts import PromptTemplate

REDUCE_PROMPT = PromptTemplate(
    template="""
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
""",
    input_variables=["summaries", "schema"]
)
