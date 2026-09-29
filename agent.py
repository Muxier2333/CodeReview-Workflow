from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from tools import execute_python
from prompts import SYSTEM_PROMPT
from config import settings


class CodeReviewAgent:
    """代码审查 Agent：LLM 推理 + Python Tool + 轻量上下文记忆。"""

    def __init__(self):
        if not settings.api_key:
            raise RuntimeError(
                "未检测到 API Key。请复制 .env.example 为 .env，并填写 OPENAI_API_KEY。"
            )

        self.llm = ChatOpenAI(
            model=settings.model,
            api_key=settings.api_key,
            base_url=settings.base_url or None,
            temperature=0.1,
            max_retries=2,
        )

        self.agent = create_agent(
            model=self.llm,
            tools=[execute_python],
            system_prompt=SYSTEM_PROMPT,
        )

        self.last_code = None
        self.last_result = None

    def review(self, code: str, language: str = "Python") -> str:
        prompt = f"""
请审查下面的 {language} 代码。

【待审查代码】
```{language.lower()}
{code}
```

要求：
1. 判断语法错误、运行时错误、逻辑错误和明显代码质量问题。
2. 如果是 Python 代码且运行验证有助于确认问题，可以调用 execute_python。
3. 不要为了调用工具而调用工具。
4. 最终必须给出结构化中文审查报告。
5. 如果没有明显问题，也要明确说明。
6. 不要声称执行过代码，除非确实调用过工具。

报告格式：
## 1. 总体评价
## 2. 发现的问题
## 3. 工具验证结果
## 4. 修改建议
## 5. 参考修改代码
"""

        try:
            response = self.agent.invoke({
                "messages": [HumanMessage(content=prompt)]
            })
            messages = response.get("messages", [])
            if not messages:
                raise RuntimeError("Agent 没有返回有效消息。")

            result = messages[-1].content
            if isinstance(result, list):
                result = "\n".join(
                    item.get("text", str(item)) if isinstance(item, dict) else str(item)
                    for item in result
                )

            self.last_code = code
            self.last_result = result
            return result

        except Exception as e:
            raise RuntimeError(f"Agent 执行失败：{e}") from e
