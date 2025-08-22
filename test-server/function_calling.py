from dotenv import load_dotenv
import os

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool

@tool
def add(a: int, b: int) -> int:
    """두 숫자를 더합니다."""
    return a + b

@tool
def subtract(a: int, b: int) -> int:
    """두 숫자를 뺍니다."""
    return a - b

tools = [add, subtract]

llm = ChatOpenAI(model="gpt-4o", temperature=0)

agent = initialize_agent(
    tools=tools,                      # 사용할 툴 목록
    llm=llm,                          # 사용할 LLM (GPT-4o)
    agent=AgentType.OPENAI_FUNCTIONS,  # Function Calling 기반 에이전트 사용
    verbose=True                      # 실행 과정을 출력
)

response = agent.invoke("7에서 3을 빼줘")

print("응답:", response)
