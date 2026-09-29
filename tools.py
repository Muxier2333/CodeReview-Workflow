from langchain_core.tools import tool
import io
import contextlib
import traceback


@tool
def execute_python(code: str) -> str:
    """执行 Python 代码，用于验证语法和运行时行为。"""
    stdout = io.StringIO()

    safe_builtins = {
        "abs": abs, "all": all, "any": any, "bool": bool,
        "dict": dict, "enumerate": enumerate, "float": float,
        "int": int, "len": len, "list": list, "max": max,
        "min": min, "print": print, "range": range, "round": round,
        "set": set, "sorted": sorted, "str": str, "sum": sum,
        "tuple": tuple, "type": type, "zip": zip,
    }
    namespace = {"__builtins__": safe_builtins}

    try:
        with contextlib.redirect_stdout(stdout):
            exec(code, namespace, namespace)

        output = stdout.getvalue().strip()
        return f"执行成功。标准输出：\n{output}" if output else "执行成功，没有产生标准输出。"

    except Exception:
        return f"代码执行出现异常：\n{traceback.format_exc()}"
