from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()  # take environment variables from .env.

# https://python.langchain.com/docs/integrations/chat/openai/
# https://python.langchain.com/api_reference/google_genai/chat_models/langchain_google_genai.chat_models.ChatGoogleGenerativeAI.html#langchain_google_genai.chat_models.ChatGoogleGenerativeAI


llm_openai = ChatOpenAI(
    model="gpt-4.1-nano",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

system_msg= SystemMessage(content="You are a helpful funny assistant that answers the questions in a humorous way.")
human_msg= HumanMessage(content="Who is the president of the United States as of october 2023?")

message = [system_msg, human_msg]

response_openai = llm_openai.invoke(message)
response_gemini = llm_gemini.invoke(message)

print("Response from OpenAI:")
print(response_openai.content)

print("Response from Gemini:")
print(response_gemini.content)

