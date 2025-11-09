# Example: ReAct Flow using LangGraph 
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# Step 1: Define a simple tool
@tool
def calculate_area(radius: float) -> float:
    """Calculates area of a circle."""
    return 3.14 * radius * radius

# Step 2: Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini")
# Step 3: Create the ReAct-style agent graph
graph = create_react_agent(
    llm,
    tools=[calculate_area],
)
# Step 4: Run the agent with a query
response = graph.invoke({"input": "Find the area of a circle with radius 10"})
print(response["messages"][-1].content)
