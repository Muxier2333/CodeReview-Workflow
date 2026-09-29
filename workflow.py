# workflow.py —— 编排器（小总管）：编码 → 审查 → (有问题→修复→复审，最多3轮)
import logging
from coding_agent import CodingAgent
from fix_agent import FixAgent
from agent import CodeReviewAgent

# 执行日志：所有步骤写进 workflow.log
logging.basicConfig(
    filename="workflow.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)


class WorkflowState:
    """状态管理：各阶段产物 + 进度，网页展示用。"""
    def __init__(self):
        self.task = ""
        self.code = ""       # 当前代码（编码产出 → 修复后代码）
        self.report = ""     # 最近一次审查报告
        self.round = 0       # 审查轮数
        self.status = "PENDING"  # PASS / FAIL / MAX_ROUND
        self.steps = []      # 分步记录


class CodeReviewWorkflow:
    def __init__(self, max_round: int = 3):
        self.coder = CodingAgent()      # 小A
        self.reviewer = CodeReviewAgent()  # 小B（项目一现成！）
        self.fixer = FixAgent()         # 小C
        self.max_round = max_round

    def run(self, task: str, progress=None) -> WorkflowState:
        """progress 可选：每步进度回调，供网页实时显示。"""
        state = WorkflowState()
        state.task = task

        def report(msg: str):
            logging.info(msg)
            if progress:
                progress(msg)

        # 第 1 步：小A 写代码
        report("[ENCODE] 小A 正在写代码……")
        state.code = self.coder.generate(task)
        state.steps.append({"stage": "ENCODE", "round": 0, "info": "编码完成"})
        report(f"[ENCODE] 编码完成（{len(state.code)} 字符）")

        # 第 2 步起：小B 审查 → 有问题小C 修 → 送回复审
        while True:
            state.round += 1
            report(f"[REVIEW] 小B 第 {state.round} 轮审查中……")
            state.report = self.reviewer.review(state.code)
            state.steps.append({"stage": "REVIEW", "round": state.round, "info": "审查完成"})

            # 小B 说没问题 → 结束
            if "审查结论: FAIL" not in state.report:
                state.status = "PASS"
                report(f"[REVIEW] 第 {state.round} 轮：通过，流程结束")
                break

            # 修太多次还不行 → 强制结束，防止死循环
            if state.round > self.max_round:
                state.status = "MAX_ROUND"
                report(f"[REVIEW] 第 {state.round} 轮仍 FAIL，超过 {self.max_round} 轮，强制结束")
                break

            # 小C 修代码
            report(f"[REVIEW] 第 {state.round} 轮发现问题，小C 修复中……")
            state.code = self.fixer.fix(state.code, state.report)
            state.steps.append({"stage": "FIX", "round": state.round, "info": "修复完成"})
            report(f"[FIX] 修复完成（{len(state.code)} 字符），送回复审")

        return state
