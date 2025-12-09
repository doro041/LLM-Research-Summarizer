# app/chains/map_chain.py
from langchain.chains import LLMChain
from app.prompts.map import MAP_PROMPT

def create_map_chain(llm):
    return LLMChain(llm=llm, prompt=MAP_PROMPT)
