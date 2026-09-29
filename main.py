# main.py —— 代码审查 Workflow 网页界面（项目二版）
import streamlit as st
from workflow import CodeReviewWorkflow

st.set_page_config(page_title="代码审查 Workflow", page_icon="🔍", layout="wide")

@st.cache_resource
def get_workflow():
    return CodeReviewWorkflow(max_round=3)

default_task = """写一个 Python 函数 divide(a, b)，返回 a 除以 b 的结果，
然后在文件末尾调用 print(divide(10, 0)) 打印结果。"""

st.title("🔍 代码审查 Workflow（编码 → 审查 → 修复）")

with st.sidebar:
    st.header("使用说明")
    st.markdown("""
1. 输入任务描述
2. 点击「运行流程」
3. 小A 写代码 → 小B 审查 → 有问题小C 修复 → 复审（最多 3 轮）
4. 看每一步产物和 workflow.log
""")

task = st.text_area("任务描述", value=default_task, height=160)

if st.button("运行流程", type="primary"):
    wf = get_workflow()
    try:
        with st.status("三个 Agent 接力中……", expanded=True) as status:
            def progress(msg: str):
                status.write(msg)
            state = wf.run(task, progress=progress)
            status.update(label="流程完成", state="complete")
    except Exception as e:
        st.error(f"流程执行失败：{e}")
        st.stop()

    st.subheader("流程结果")
    status_map = {"PASS": "通过 ✔", "FAIL": "未通过 ✘", "MAX_ROUND": "达到最大轮数"}
    st.info(f"最终状态：{status_map[state.status]} ｜ 审查轮数：{state.round}")

    tab1, tab2, tab3, tab4 = st.tabs(["分步记录", "最终代码", "审查报告", "执行日志"])
    with tab1:
        for s in state.steps:
            st.write(f"第 {s['round']} 轮 · {s['stage']} · {s['info']}")
    with tab2:
        st.code(state.code, language="python")
    with tab3:
        st.markdown(state.report)
    with tab4:
        try:
            with open("workflow.log", encoding="utf-8") as f:
                st.code(f.read(), language="text")
        except FileNotFoundError:
            st.write("暂无日志")
