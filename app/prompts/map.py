# app/prompts/map.py
from langchain_core.prompts import PromptTemplate

MAP_PROMPT = PromptTemplate(
    template="""
Summarise the following research paper excerpt in 3 concise,
technical bullet points. Focus only on factual content.


TEXT:
{chunk}
""",
    input_variables=["chunk"]
)
