# utils.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize the LLM
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3, api_key=GROQ_API_KEY)

# Prompts
general_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a smart and helpful assistant. Answer user questions clearly and concisely.
                  If you're not sure about the answer, politely say you don't know."""),
    ("human", "{text}")
])

summerization_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant specialized in summarizing long texts. 
                  Extract the most important points clearly and concisely. Avoid repetition."""),
    ("human", "{text}")
])

Translation_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a professional translator. Only return the translated text without comments or notes."""),
    ("human", """Text to translate: {text}\nTarget language: {target_language}""")
])

classification_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a task classifier. 
Your job is to analyze the user's message and classify it into one of three categories: 
- translation: if the user asks to translate text into another language
- summarization: if the user asks to shorten or summarize a long text
- general: if the user is asking a regular question or anything else.

Only respond with one word: translation, summarization, or general.
"""),
    ("human", "{text}")
])
extract_translation_info_prompt = ChatPromptTemplate.from_messages([
    ("system", """Extract structured JSON with 'text' and 'target_language' from the user prompt.
                  Return null for missing values. Output only JSON."""),
    ("human", "{text}")
])

# Chains
classification_chain = classification_prompt | llm | StrOutputParser()
merge_chain = RunnableLambda(lambda x: {"class": classification_chain.invoke({"text": x}), "text": x})
extraction_chain = extract_translation_info_prompt | llm | JsonOutputParser()
Translation_chain = Translation_prompt | llm | StrOutputParser()
summerization_chain = summerization_prompt | llm | StrOutputParser()
general_chain = general_prompt | llm | StrOutputParser()

# Branch logic
branch = RunnableBranch(
    (lambda x: x['class'].strip().lower() == 'translation', RunnableLambda(lambda x: x["text"]) | extraction_chain | Translation_chain| RunnableLambda(lambda out: f"`from Translation branch:`\n{out}")),
    (lambda x: x['class'].strip().lower() == 'summarization', RunnableLambda(lambda x: x["text"]) | summerization_chain| RunnableLambda(lambda out: f"`from Summerization branch:`\n{out}")),
    RunnableLambda(lambda x: x["text"]) | general_chain| RunnableLambda(lambda out: f"`from Default branch:`\n{out}")
)

# Final main chain
main_chain = merge_chain | branch
