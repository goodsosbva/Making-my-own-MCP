import asyncio
from mcp_server import ask_gpt

async def client():
    question = "mcp와 agent의 관계는?"
    result = await ask_gpt(None, question)  
    print("답변:", result)

asyncio.run(client())