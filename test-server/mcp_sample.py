from mcp.server.fastmcp import FastMCP  
import logging                         
import asyncio                       

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """두 숫자를 더합니다."""
    logging.info(f"Adding {a} + {b}")  
    return a + b                      

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """두 숫자를 뺍니다."""
    logging.info(f"Subtracting {a} - {b}")  
    return a - b                          

if __name__ == "__main__":
    asyncio.run(mcp.run(transport="stdio")) 