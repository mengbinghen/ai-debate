"""Streamlit frontend for the AI Debate system."""
import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st
from streamlit import session_state as ss
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.debate_flow import run_debate
from backend.debate_flow.state import get_default_model_config
from backend.models import DebateMessage, Role
from config import settings


# Configure page
st.set_page_config(
    page_title="AI辩论赛",
    page_icon="🎭",
    layout="wide",
)


def init_session_state() -> None:
    """Initialize session state variables."""
    if "debate_state" not in ss:
        ss.debate_state = "home"
        ss.debate_data = {}
    if "topic_widget" not in ss:
        ss.topic_widget = ""
    if "model_config" not in ss:
        ss.model_config = get_default_model_config()

    # Load API key from environment variable
    env_api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if env_api_key:
        settings.DEEPSEEK_API_KEY = env_api_key


def get_role_emoji(role: str) -> str:
    """Get emoji for a role.

    Args:
        role: The role name.

    Returns:
        An emoji representing the role.
    """
    emojis = {
        "moderator": "🎤",
        "affirmative": "🔵",
        "negative": "🔴",
        "judge": "⚖️",
    }
    return emojis.get(role.lower(), "💬")


def get_role_name(role: str) -> str:
    """Get Chinese name for a role.

    Args:
        role: The role name.

    Returns:
        Chinese name for the role.
    """
    names = {
        "moderator": "主持人",
        "affirmative": "正方",
        "negative": "反方",
        "judge": "裁判",
    }
    return names.get(role.lower(), role)


def render_home_page() -> None:
    """Render the home page where users input the debate topic."""
    st.title("🎭 AI辩论赛系统")
    st.markdown("---")

    # Sidebar with model configuration and debate rules
    with st.sidebar:
        st.header("⚙️ 模型配置")

        # Provider and model options (Chinese labels)
        provider_models = {
            "DeepSeek深度思考": {
                "deepseek-reasoner": "DeepSeek Reasoner (深度思考)",
                "deepseek-chat": "DeepSeek Chat (快速响应)"
            },
            "阿里云通义千问": {
                "qwen3-max": "Qwen3 Max",
                "qwq-plus": "QwQ Plus"
            }
        }

        # Provider mapping from Chinese display names to internal provider names
        provider_map = {
            "DeepSeek深度思考": "deepseek",
            "阿里云通义千问": "dashscope"
        }

        # Affirmative model selection
        st.subheader("🔵 正方模型")
        aff_provider = st.selectbox(
            "供应商",
            options=list(provider_models.keys()),
            key="aff_provider"
        )
        aff_model = st.selectbox(
            "模型",
            options=list(provider_models[aff_provider].keys()),
            format_func=lambda x: provider_models[aff_provider][x],
            key="aff_model"
        )

        # Negative model selection
        st.subheader("🔴 反方模型")
        neg_provider = st.selectbox(
            "供应商",
            options=list(provider_models.keys()),
            key="neg_provider"
        )
        neg_model = st.selectbox(
            "模型",
            options=list(provider_models[neg_provider].keys()),
            format_func=lambda x: provider_models[neg_provider][x],
            key="neg_model"
        )

        # Judge model selection
        st.subheader("⚖️ 裁判模型")
        judge_provider = st.selectbox(
            "供应商",
            options=list(provider_models.keys()),
            key="judge_provider"
        )
        judge_model = st.selectbox(
            "模型",
            options=list(provider_models[judge_provider].keys()),
            format_func=lambda x: provider_models[judge_provider][x],
            key="judge_model"
        )

        # Note: Moderator uses fixed deepseek-chat model
        st.caption("💡 主持人固定使用 DeepSeek Chat 模型")

        st.divider()

        st.header("📋 辩论规则")
        st.markdown("""
        1. **开篇立论** - 双方各3分钟阐述观点
        2. **攻辩环节** - 双方互相提问，共2轮
        3. **自由辩论** - 双方自由辩论，3轮交替发言
        4. **总结陈词** - 双方各2分钟总结观点

        **评分标准：**
        - 逻辑性 (30%)
        - 论据充分性 (25%)
        - 反驳有效性 (25%)
        - 表达清晰度 (20%)
        """)

        st.divider()
        st.caption("💡 提示：请设置环境变量 `DEEPSEEK_API_KEY` 和 `DASHSCOPE_API_KEY` 以使用此系统")

    st.header("请输入辩论主题")

    # Preset topics first (before text area)
    st.write("或选择预设辩题：")
    preset_topics = [
        "远程办公是否会取代传统办公？",
        "社交媒体是否让人更孤独？",
        "电动汽车是否比燃油车更环保？",
        "大学生是否应该创业？",
        "短视频是否让人变得更浅薄？",
    ]

    cols = st.columns(3)
    for i, preset in enumerate(preset_topics):
        with cols[i % 3]:
            if st.button(preset, key=f"preset_{i}"):
                st.session_state.topic_widget = preset
                st.rerun()

    # Topic input using session state
    topic = st.text_area(
        "辩题",
        placeholder="例如：人工智能发展对人类有利还是不利？",
        height=100,
        label_visibility="collapsed",
        key="topic_widget",
    )

    # Start debate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Check if API key is configured
        api_key_configured = bool(os.environ.get("DEEPSEEK_API_KEY", ""))

        if st.button(
            "🚀 开始辩论",
            type="primary",
            disabled=not topic or not api_key_configured,
            use_container_width=True,
        ):
            # Store model config in session state
            ss.model_config = {
                "affirmative": {
                    "provider": provider_map[aff_provider],
                    "model": aff_model
                },
                "negative": {
                    "provider": provider_map[neg_provider],
                    "model": neg_model
                },
                "judge": {
                    "provider": provider_map[judge_provider],
                    "model": judge_model
                },
                # Moderator always uses fixed deepseek-chat
                "moderator": {
                    "provider": "deepseek",
                    "model": "deepseek-chat"
                }
            }

            ss.debate_data["topic"] = topic
            ss.debate_data["model_config"] = ss.model_config
            ss.debate_state = "debate"
            ss.debate_data["started"] = False
            ss.debate_data["messages"] = []
            ss.debate_data["result"] = None
            st.rerun()

    # Show warning if API key is not configured
    if not api_key_configured:
        st.warning("⚠️ 请先设置环境变量 `DEEPSEEK_API_KEY` 才能开始辩论")
    elif topic:
        st.success(f"✅ 辩题已设置：{topic[:50]}..." if len(topic) > 50 else f"✅ 辩题已设置：{topic}")


def render_debate_page() -> None:
    """Render the debate page where the debate is displayed."""
    topic = ss.debate_data.get("topic", "")

    st.title("🎭 AI辩论赛")
    st.markdown(f"### 辩题：{topic}")
    st.markdown("---")

    # Start button if not started
    if not ss.debate_data.get("started", False):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("▶️ 开始辩论", type="primary", use_container_width=True):
                ss.debate_data["started"] = True
                ss.debate_data["messages"] = []
                st.rerun()
    else:
        # Check if result exists
        if ss.debate_data.get("result") is None:
            # Create placeholder for messages
            message_placeholder = st.container()
            status_placeholder = st.empty()

            messages_list = ss.debate_data.get("messages", [])

            # Display existing messages
            with message_placeholder:
                for msg in messages_list:
                    role = msg.role if isinstance(msg.role, str) else msg.role.value
                    with st.chat_message(role):
                        emoji = get_role_emoji(role)
                        name = get_role_name(role)
                        st.markdown(f"{emoji} **{name}**")
                        st.markdown(msg.content)

            # Run the debate with streaming (manual step-by-step)
            try:
                async def run_manual_streaming_debate():
                    from backend.debate_flow.nodes import (
                        closing_affirmative,
                        closing_negative,
                        cross_examination_round_1,
                        cross_examination_round_2,
                        final_judgment,
                        free_debate_round,
                        initialize_debate,
                        opening_affirmative,
                        opening_negative,
                        score_opening,
                        should_continue_free_debate,
                    )
                    from backend.debate_flow.state import create_initial_state, get_default_model_config

                    # Get model config from session state
                    model_config = ss.debate_data.get("model_config", get_default_model_config())

                    # Create initial state with model config
                    state = create_initial_state(
                        topic=topic,
                        model_config=model_config
                    )

                    # Helper to display message
                    def display_message(msg):
                        nonlocal messages_list
                        role = msg.role if isinstance(msg.role, str) else msg.role.value
                        messages_list.append(msg)
                        ss.debate_data["messages"] = messages_list

                        with message_placeholder:
                            with st.chat_message(role):
                                emoji = get_role_emoji(role)
                                name = get_role_name(role)
                                st.markdown(f"{emoji} **{name}**")
                                st.markdown(msg.content)

                    # Initialize
                    status_placeholder.info("🔄 初始化辩论...")
                    state = {**state, **await initialize_debate(state)}
                    for msg in state.get("debate_messages", []):
                        display_message(msg)

                    # Opening affirmative
                    status_placeholder.info("🔄 开篇立论（正方）...")
                    state = {**state, **await opening_affirmative(state)}
                    for msg in state.get("debate_messages", [])[len(messages_list):]:
                        display_message(msg)

                    # Opening negative
                    status_placeholder.info("🔄 开篇立论（反方）...")
                    state = {**state, **await opening_negative(state)}
                    for msg in state.get("debate_messages", [])[len(messages_list):]:
                        display_message(msg)

                    # Score opening
                    status_placeholder.info("🔄 评分...")
                    state = {**state, **await score_opening(state)}

                    # Cross examination round 1
                    status_placeholder.info("🔄 攻辩环节（第1轮）...")
                    state = {**state, **await cross_examination_round_1(state)}
                    for msg in state.get("debate_messages", [])[len(messages_list):]:
                        display_message(msg)

                    # Cross examination round 2
                    status_placeholder.info("🔄 攻辩环节（第2轮）...")
                    state = {**state, **await cross_examination_round_2(state)}
                    for msg in state.get("debate_messages", [])[len(messages_list):]:
                        display_message(msg)

                    # Free debate rounds
                    max_rounds = state.get("max_free_debate_rounds", 3)
                    for i in range(max_rounds):
                        status_placeholder.info(f"🔄 自由辩论（第{i+1}轮）...")
                        state = {**state, **await free_debate_round(state)}
                        for msg in state.get("debate_messages", [])[len(messages_list):]:
                            display_message(msg)

                        # Check if should continue
                        if should_continue_free_debate(state) == "end":
                            break

                    # Closing affirmative
                    status_placeholder.info("🔄 总结陈词（正方）...")
                    state = {**state, **await closing_affirmative(state)}
                    for msg in state.get("debate_messages", [])[len(messages_list):]:
                        display_message(msg)

                    # Closing negative
                    status_placeholder.info("🔄 总结陈词（反方）...")
                    state = {**state, **await closing_negative(state)}
                    for msg in state.get("debate_messages", [])[len(messages_list):]:
                        display_message(msg)

                    # Final judgment
                    status_placeholder.info("🔄 最终判决...")
                    state = {**state, **await final_judgment(state)}

                    # Store result
                    result = {
                        "topic": topic,
                        "messages": state.get("debate_messages", []),
                        "final_verdict": state.get("final_verdict"),
                        "scores": state.get("scores", []),
                        "opening_statements": state.get("opening_statements", {}),
                        "cross_examinations": state.get("cross_examinations", []),
                        "closing_statements": state.get("closing_statements", {}),
                    }
                    ss.debate_data["result"] = result
                    status_placeholder.success("✅ 辩论完成！")

                # Run the async function
                asyncio.run(run_manual_streaming_debate())

                # Auto-redirect to results after a short delay
                import time
                time.sleep(1)
                ss.debate_state = "result"
                st.rerun()

            except Exception as e:
                import traceback
                st.error(f"辩论过程中出现错误：{str(e)}")
                st.error(traceback.format_exc())
                if st.button("返回首页"):
                    ss.debate_state = "home"
                    st.rerun()
        else:
            # Display messages
            messages = ss.debate_data.get("messages", [])

            # Create a container for messages
            message_container = st.container()

            with message_container:
                for msg in messages:
                    role = msg.role if isinstance(msg.role, str) else msg.role.value
                    with st.chat_message(role):
                        emoji = get_role_emoji(role)
                        name = get_role_name(role)
                        st.markdown(f"{emoji} **{name}**")
                        st.markdown(msg.content)

            # View results button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🏆 查看结果", type="primary", use_container_width=True):
                    ss.debate_state = "result"
                    st.rerun()

    # Back button
    if st.button("← 返回首页"):
        ss.debate_state = "home"
        st.rerun()


def render_result_page() -> None:
    """Render the results page with scores and verdict."""
    result = ss.debate_data.get("result")
    if not result:
        st.error("没有辩论结果")
        if st.button("返回首页"):
            ss.debate_state = "home"
            st.rerun()
        return

    st.title("🏆 辩论结果")
    st.markdown("---")

    # Verdict
    verdict = result.get("final_verdict")
    if verdict:
        winner = verdict.winner
        winner_name = {
            "affirmative": "正方",
            "negative": "反方",
            "draw": "平局",
        }.get(winner, winner)

        if winner == "draw":
            st.info(f"🤝 **结果：平局**")
        else:
            emoji = "🔵" if winner == "affirmative" else "🔴"
            st.success(f"{emoji} **获胜方：{winner_name}**")

        # Scores
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="🔵 正方总分",
                value=f"{verdict.affirmative_total:.1f}",
            )
        with col2:
            st.metric(
                label="🔴 反方总分",
                value=f"{verdict.negative_total:.1f}",
            )

        # Judge's comment
        st.markdown("---")
        st.subheader("⚖️ 裁判点评")
        st.markdown(verdict.comment)

    # Detailed scores by round
    st.markdown("---")
    st.subheader("📊 详细评分")

    scores = result.get("scores", [])
    if scores:
        # Group scores by round
        rounds = {}
        for score in scores:
            round_type = score.round_type.value if hasattr(score.round_type, 'value') else score.round_type
            if round_type not in rounds:
                rounds[round_type] = {}
            rounds[round_type][score.position] = score

        round_names = {
            "opening": "开篇立论",
            "cross_examination": "攻辩环节",
            "free_debate": "自由辩论",
            "closing": "总结陈词",
        }

        for round_type, round_scores in rounds.items():
            st.markdown(f"### {round_names.get(round_type, round_type)}")

            col1, col2 = st.columns(2)

            with col1:
                aff_score = round_scores.get("affirmative")
                if aff_score:
                    st.markdown("🔵 **正方**")
                    st.markdown(f"- 逻辑性: {aff_score.logic:.1f}")
                    st.markdown(f"- 论据: {aff_score.evidence:.1f}")
                    st.markdown(f"- 反驳: {aff_score.rebuttal:.1f}")
                    st.markdown(f"- 表达: {aff_score.expression:.1f}")
                    st.markdown(f"- **总分: {aff_score.total:.1f}**")
                    if aff_score.comment:
                        st.caption(f"💬 {aff_score.comment}")

            with col2:
                neg_score = round_scores.get("negative")
                if neg_score:
                    st.markdown("🔴 **反方**")
                    st.markdown(f"- 逻辑性: {neg_score.logic:.1f}")
                    st.markdown(f"- 论据: {neg_score.evidence:.1f}")
                    st.markdown(f"- 反驳: {neg_score.rebuttal:.1f}")
                    st.markdown(f"- 表达: {neg_score.expression:.1f}")
                    st.markdown(f"- **总分: {neg_score.total:.1f}**")
                    if neg_score.comment:
                        st.caption(f"💬 {neg_score.comment}")

            st.markdown("---")

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("查看辩论过程", use_container_width=True):
            ss.debate_state = "debate"
            st.rerun()

    with col2:
        if st.button("新辩论", use_container_width=True):
            ss.debate_state = "home"
            ss.debate_data = {}
            st.rerun()


def main() -> None:
    """Main entry point for the Streamlit app."""
    init_session_state()

    # Route to appropriate page
    if ss.debate_state == "home":
        render_home_page()
    elif ss.debate_state == "debate":
        render_debate_page()
    elif ss.debate_state == "result":
        render_result_page()
    else:
        ss.debate_state = "home"
        render_home_page()


if __name__ == "__main__":
    main()
