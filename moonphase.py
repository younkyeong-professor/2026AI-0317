import streamlit as st
import anthropic
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.patches as patches

# 페이지 설정
st.set_page_config(
    page_title="달의 위상변화 시뮬레이션",
    page_icon="🌙",
    layout="wide"
)

st.title("🌙 달의 위상변화 시뮬레이션 & AI 챗봇")

# 사이드바 - API 키 입력
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input(
        "Claude API 키 입력",
        type="password",
        help="https://console.anthropic.com에서 발급받으세요"
    )
    
    if api_key:
        st.success("✅ API 키가 입력되었습니다")
    else:
        st.warning("⚠️ API 키를 입력해주세요")

# 달 위상 생성 함수
def draw_moon_phase(phase_day, ax):
    """
    달의 위상을 그리는 함수
    phase_day: 0 = 신월, 7.38 = 상현, 14.76 = 보름달, 22.14 = 하현
    """
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 배경
    ax.set_facecolor('#001a33')
    
    # 달 기본 원 (검은색)
    moon_circle = patches.Circle((0, 0), 1, color='black', ec='white', linewidth=2)
    ax.add_patch(moon_circle)
    
    # 위상 계산 (한 달 = 29.53일)
    phase_ratio = (phase_day % 29.53) / 29.53
    
    if phase_ratio < 0.5:
        # 신월 → 보름달
        shadow_width = 2 * (0.5 - phase_ratio)
        # 오른쪽에서 왼쪽으로 그림자 이동
        shadow = patches.Rectangle(
            (-1, -1), shadow_width, 2,
            color='black', ec='none'
        )
    else:
        # 보름달 → 신월
        shadow_width = 2 * (phase_ratio - 0.5)
        # 왼쪽에서 오른쪽으로 그림자 이동
        shadow = patches.Rectangle(
            (1 - shadow_width, -1), shadow_width, 2,
            color='black', ec='none'
        )
    
    ax.add_patch(shadow)
    
    # 위상 이름
    phase_names = ["신월", "초승달", "상현", "보름달 전", "보름달", "보름달 후", "하현", "그믐달"]
    phase_index = int(phase_ratio * 8) % 8
    
    ax.text(0, -1.3, f"위상: {phase_names[phase_index]}\n{phase_day:.1f}일째",
            ha='center', fontsize=12, color='white', weight='bold')
    
    return phase_names[phase_index]

# 메인 콘텐츠
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 달 위상 시뮬레이션")
    
    # 슬라이더로 날짜 선택
    phase_day = st.slider(
        "달의 나이 선택 (일)",
        min_value=0.0,
        max_value=29.53,
        value=14.76,
        step=0.5,
        help="0 = 신월, 14.76 = 보름달, 29.53 = 신월"
    )
    
    # 달 위상 그리기
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='#001a33')
    phase_name = draw_moon_phase(phase_day, ax)
    st.pyplot(fig, use_container_width=True)
    
    # 위상 정보
    st.info(f"""
    **현재 달의 위상: {phase_name}**
    - 위상일: {phase_day:.2f}일
    - 음력 나이: {int(phase_day) + 1}일
    """)

with col2:
    st.subheader("🤖 AI 챗봇")
    
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 대화 표시
    chat_container = st.container(height=400)
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # 입력창
    user_input = st.chat_input("달의 위상변화에 대해 질문해보세요...")
    
    if user_input and api_key:
        # 사용자 메시지 추가
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
        
        # Claude API 호출
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            # 시스템 프롬프트
            system_prompt = f"""당신은 천문학 전문 안내 AI입니다.
사용자의 달 위상변화 관련 질문에 정확하고 흥미롭게 답변하세요.
현재 시뮬레이션 상태: 달의 나이 {phase_day:.1f}일, 위상: {phase_name}
답변은 간결하고 이해하기 쉽게 작성하세요."""
            
            # API 호출
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": msg["content"]}
                    for msg in st.session_state.messages
                ]
            )
            
            assistant_response = message.content[0].text
            
            # 응답 저장
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_response
            })
            
            with chat_container:
                with st.chat_message("assistant"):
                    st.markdown(assistant_response)
            
        except Exception as e:
            st.error(f"❌ API 오류: {str(e)}")
    
    elif user_input and not api_key:
        st.warning("⚠️ API 키를 먼저 입력해주세요")

# 하단 정보
st.divider()
st.subheader("📚 달의 위상변화 정보")

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    st.metric("신월", "0일", "태양과 같은 방향")

with info_col2:
    st.metric("보름달", "14.76일", "태양과 반대 방향")

with info_col3:
    st.metric("주기", "29.53일", "삭망월")

st.caption("🌙 달의 위상변화 시뮬레이션 v1.0 | Powered by Claude Haiku 4.5")
