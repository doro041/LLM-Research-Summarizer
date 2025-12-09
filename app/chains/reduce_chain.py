# app/chains/reduce_chain.py
from langchain.chains import LLMChain
from app.prompts.reduce import REDUCE_PROMPT

def create_reduce_chain(llm):
    return LLMChain(llm=llm, prompt=REDUCE_PROMPT)
