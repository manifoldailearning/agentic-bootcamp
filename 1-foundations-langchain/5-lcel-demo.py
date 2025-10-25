# prompt | llm
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

load_dotenv()  # take environment variables from .env.

llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

template = PromptTemplate.from_template(
    """Answer the following quesiton using the context below.
    If the question cannot be answered using the context, say "I don't know"."
    Context: {context}
    Question: {question}
    Answer: """
)

#lcel composition

chain = template | llm_gemini

response = chain.invoke({"context": "The capital of France is Paris.", 
     "question": "What is the capital of France?"})

print("Response from Gemini via LCEL:")
print(response.content)