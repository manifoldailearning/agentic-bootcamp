from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

load_dotenv()  # take environment variables from .env.

llm_openai = ChatOpenAI(
    model="gpt-4.1-nano",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

template = PromptTemplate.from_template(
    """Answer the following quesiton using the context below.
    If the question cannot be answered using the context, say "I don't know"."
    Context: {context}
    Question: {question}
    Answer: """
)

# template_object = template.invoke(
#     {"context": "The capital of France is Paris.", 
#      "question": "What is the capital of France?"}
# )

template_object = template.invoke(
    {"context": "The capital of France is Paris.", 
     "question": "What is the capital of India?"}
)
print("Template Object:")
print(template_object)
response_openai = llm_openai.invoke(template_object)
response_gemini = llm_gemini.invoke(template_object)

print("Response from OpenAI:")
print(response_openai.content)

print("Response from Gemini:")
print(response_gemini.content)

