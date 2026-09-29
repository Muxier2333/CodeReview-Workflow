# test_workflow_run.py —— 端到端验证脚本：真实跑一遍 编码→审查→修复 流程
from workflow import CodeReviewWorkflow

task = """写一个 Python 函数 divide(a, b)，返回 a 除以 b 的结果，
然后在文件末尾调用 print(divide(10, 0)) 打印结果。"""

print("=== 开始端到端测试 ===")
wf = CodeReviewWorkflow(max_round=2)
state = wf.run(task)

print("最终状态:", state.status)
print("审查轮数:", state.round)
print("分步记录:", state.steps)
print("=== 最终代码 ===")
print(state.code)
print("=== 审查报告（前 600 字）===")
print(state.report[:600])
print("=== 端到端测试结束 ===")
