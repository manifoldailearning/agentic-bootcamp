# prompt | llm
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()  # take environment variables from .env

llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                    temperature=0.5,
                                    max_output_tokens=2048)



prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are in expert assistant. Adapt Explanations to the audience and style."
         "Prefer Short sentences and concrete examples when helpful."),
         ("user",
          """Write a {style} explainer on the topic of '{topic}' for the {audience} audience.
          Keep it {length}.
          Format: \n
          Opener: 1-2 lines \n
          Core: 2-3 Bullet points \n
          Bottom Line: Single sentece starting with 'Bottom line:'
          """
          )
    ]
)

chain = prompt | llm_gemini

variables = {
    "topic": "Quantum Computing",
    "audience": "high school students",
    "style": "engaging and simple",
    "length": "150 words"}

response = chain.invoke(variables)
print("Response from Gemini via LCEL:")
print(response.content)
