import logging

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("Math")

@mcp.tool()
def add(a, b) -> int:
    """더하기"""
    try:
        a = int(a) 
        b = int(b)
        logging.info(f"Adding {a} and {b}")  
        return a + b  # 더한 결과 반환
    except Exception as e:
        logging.error(f"Invalid input in add: {a}, {b} - {e}")
        raise

@mcp.tool()
def Subtract(a, b) -> int:
    """빼기"""
    try:
        a = int(a) 
        b = int(b)
        logging.info(f"Subtracting {a} and {b}")  
        return a - b 
    except Exception as e:
        logging.error(f"Invalid input in subtract: {a}, {b} - {e}")
        raise
    
if __name__ == "__main__":
    mcp.run(transport="stdio")