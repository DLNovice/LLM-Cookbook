import os
import asyncio
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI


# 加载环境变量
load_dotenv(override=False)


async def main():
    # MCP Server 配置
    client = MultiServerMCPClient(
        {
            "psa_tools": {
                "transport": "http",
                "url": "http://localhost:4201/psa",
            }
        }
    )

    # 获取 MCP 工具
    tools = await client.get_tools()
    print(f"Tools: {tools}")

    model = ChatOpenAI(
        model=os.getenv("MODEL_NAME"),
        temperature=0.5,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url=os.getenv("BASE_URL")
    )

    # 创建 Agent
    agent = create_agent(
        model=model,
        tools=tools
    )

    response = await agent.ainvoke(
        {
            "messages": [
                {"role": "user", "content": "你有哪些工具"}
            ]
        }
    )
    print("Response:", response['messages'][-1])


if __name__ == "__main__":
    asyncio.run(main())
