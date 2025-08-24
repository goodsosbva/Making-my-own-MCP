import asyncio  
import sys     
import json   
import os

from mcp import ClientSession  
from mcp.client.sse import sse_client 

async def main():
    default_url = os.getenv("SSE_URL", "http://127.0.0.1:3000/sse")
    url = sys.argv[1] if len(sys.argv) >= 2 else default_url
    print(f"[클라이언트] 서버에 SSE 연결 시도 중... ({url})")

    async with sse_client(url) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()  

            print("MCP Chat Client 시작됨. 'quit' 입력 시 종료됩니다.")
            
            while True:
                user_input = input("\nQuery: ").strip() 
                if user_input.lower() == "quit":
                    break

                try:
                    response = await session.call_tool("chat", {"input": user_input})

                    if isinstance(response.content, str):
                        try:
                            data = json.loads(response.content) 
                            print("\n GPT-4o 응답:\n" + data["content"])  
                        except json.JSONDecodeError:
                            print("\n GPT-4o 응답:\n" + response.content)
                    elif isinstance(response.content, dict):
                        print("\n GPT-4o 응답:\n" + response.content.get("content", 
                                                            str(response.content)))
                    else:
                        print("\n GPT-4o 응답:\n" + str(response.content))

                except Exception as e:
                    print(f"오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())