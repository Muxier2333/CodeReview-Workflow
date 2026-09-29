# coding_agent.py —— 编码 Agent（小A）：根据任务描述生成第一版代码
import re
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from prompts import CODING_SYSTEM_PROMPT
from config import settings


class CodingAgent:
    """编码 Agent：纯 LLM 生成代码（不需要工具，一次请求搞定，速度快）。"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.model,
            api_key=settings.api_key,
            base_url=settings.base_url or None,
            temperature=0.2,
            max_retries=2,
        )

    def generate(self, task: str) -> str:
        """输入任务描述，返回生成的代码。"""
        response = self.llm.invoke([
            SystemMessage(content=CODING_SYSTEM_PROMPT),
            HumanMessage(content=f"任务描述：\n{task}"),
        ])
        text = response.content
        if isinstance(text, list):
            text = "\n".join(
                item.get("text", str(item)) if isinstance(item, dict) else str(item)
                for item in text
            )
        return _extract_code(text)


def _extract_code(text: str) -> str:
    """从回复里把代码抠出来（LLM 喜欢加 ```python 围栏，要剥掉）。"""
    m = re.search(r"```(?:python)?\s*\n?(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()
