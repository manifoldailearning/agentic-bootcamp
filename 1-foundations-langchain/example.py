from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()  # take environment variables from .env.


llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

message = "tell me what is agentic ai?"
response_gemini = llm_gemini.invoke(message)

print("Response from Gemini:")
print(response_gemini.content)

