import streamlit as st
from agent import CodeReviewAgent

st.set_page_config(page_title="CodeReview Agent", page_icon="🔍", layout="wide")

@st.cache_resource
def get_agent():
    return CodeReviewAgent()

st.title("🔍 CodeReview Agent")
st.caption("基于 LangChain + LLM + Python Tool 的智能代码审查助手")

with st.sidebar:
    st.header("使用说明")
    st.markdown("""
1. 输入待审查代码
2. 选择代码语言
3. 点击“开始审查”
4. Agent 会分析代码，并在需要时调用 Python 执行工具
5. 查看问题、风险、修改建议和改进代码
""")
    st.divider()
    st.markdown("**项目特点**")
    st.markdown("- LangChain Agent 架构")
    st.markdown("- Python 代码执行工具")
    st.markdown("- 对话上下文记忆")
    st.markdown("- 错误处理与重试")
    st.markdown("- Streamlit Web 界面")

default_code = '''def divide(a, b):
    return a / b

print(divide(10, 0))
'''

code = st.text_area("待审查代码", value=default_code, height=330)
language = st.selectbox("代码语言", ["Python"])

col1, col2 = st.columns(2)
with col1:
    review = st.button("🚀 开始审查", type="primary", use_container_width=True)
with col2:
    clear = st.button("🧹 清空", use_container_width=True)

if clear:
    st.rerun()

if review:
    if not code.strip():
        st.warning("请输入需要审查的代码。")
    else:
        agent = get_agent()
        with st.spinner("Agent 正在分析代码……"):
            try:
                result = agent.review(code, language)
                st.markdown("## 审查结果")
                st.markdown(result)
            except Exception as e:
                st.error(f"审查失败：{e}")

st.divider()
st.caption("CodeReview Agent · Course Project")
