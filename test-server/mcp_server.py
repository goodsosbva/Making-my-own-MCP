from mcp.server.fastmcp import FastMCP, Context  
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

mcp = FastMCP("GPT-4o MCP")

@mcp.tool()
async def ask_gpt(ctx: Context, question: str) -> str:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    return llm.invoke(question)

if __name__ == "__main__":
    mcp.run(transport="stdio")