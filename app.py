import os
import streamlit as st
# ==============================
# 应用配置（方便修改）
# ==============================
APP_TITLE = "🤖 HolmesGPT 智能诊断助手"
APP_VERSION = "poc2-HolmesGPT AIOps, 9 Jul 2026, 20:40AM"

# 关键：解决 kubectl 内存限制
os.environ["TOOL_MEMORY_LIMIT_MB"] = "2048"
from holmes.config import Config
from holmes.core.prompt import build_initial_ask_messages
# ==============================
# 初始化 Agent（只加载一次）
# ==============================
@st.cache_resource
def get_holmes_agent():
    config = Config(
        api_key="sk-ddcf3acb915b4a01ab3a58af7c60ea14",
        model="deepseek/deepseek-chat"
    )
    ai = config.create_toolcalling_llm(enable_all_toolsets_possible=True)
    return ai
ai_agent = get_holmes_agent()
# ==============================
# 不同功能的提示词
# ==============================
PROMPTS = {
    "自然语言转 PromQL": """
你是PromQL专家，请将用户输入转为标准PromQL，只输出PromQL语句。
用户问题：{query}
""",
    "K3s 异常 Pod 根因分析": """
请检查集群所有异常Pod，输出：
1. 异常原因
2. 根因分析
3. 修复方案
""",
    "查询 Prometheus 指标": """
第一步：将用户问题转为PromQL
第二步：调用Prometheus查询
第三步：返回结果+简单分析
用户问题：{query}
""",
    "集群整体健康检查": """
请对K3s集群做全面健康检查：节点、Pod、资源、风险。
输出专业报告。
"""
}
# ==============================
# Streamlit 页面布局
# ==============================
st.set_page_config(page_title="HolmesGPT AIOps", layout="wide")
st.title("🤖 HolmesGPT K8s 智能诊断助手")
st.divider()
# 功能选择：自动读取字典key，避免文字不匹配
task_type = st.selectbox(
    "请选择诊断功能",
    list(PROMPTS.keys())
)
# 输入框
user_input = st.text_input("输入你的问题", placeholder="例如：查看最近5分钟CPU使用率")
# 历史消息
if "messages" not in st.session_state:
    st.session_state.messages = []
# 显示历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
# ==============================
# 发送按钮
# ==============================
if st.button("开始分析") and user_input:
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 【修复段】安全读取模板，彻底解决KeyError
    template = PROMPTS.get(task_type.strip(), "请描述你的K8s集群问题，我将为你诊断")
    if "{query}" in template:
        prompt = template.format(query=user_input)
    else:
        prompt = template

    # AI 回复
    with st.chat_message("assistant"):
        with st.spinner("🔍 正在诊断中..."):
            messages = build_initial_ask_messages(
                initial_user_prompt=prompt,
                file_paths=None,
                tool_executor=ai_agent.tool_executor
            )
            response = ai_agent.call(messages)
            result = response.result
            st.markdown(result)
            st.session_state.messages.append({"role": "assistant", "content": result})