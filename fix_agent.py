# fix_agent.py —— 修复 Agent（小C）：根据审查报告改代码
import re
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from prompts import FIXING_SYSTEM_PROMPT
from config import settings


class FixAgent:
    """修复 Agent：纯 LLM 改代码（不需要工具，一次请求搞定，速度快）。"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.model,
            api_key=settings.api_key,
            base_url=settings.base_url or None,
            temperature=0.2,
            max_retries=2,
        )

    def fix(self, code: str, report: str) -> str:
        """输入：原代码 + 审查报告，返回：修复后的代码。"""
        prompt = f"""待修复代码：
```python
{code}
```

审查报告：
{report}

请按你的工作指令输出修复后的完整代码。"""
        response = self.llm.invoke([
            SystemMessage(content=FIXING_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        text = response.content
        if isinstance(text, list):
            text = "\n".join(
                item.get("text", str(item)) if isinstance(item, dict) else str(item)
                for item in text
            )
        return _extract_code(text)


def _extract_code(text: str) -> str:
    """同 coding_agent.py，复制过来的。"""
    m = re.search(r"```(?:python)?\s*\n?(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()
