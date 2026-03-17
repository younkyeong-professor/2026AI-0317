import streamlit as st
import anthropic
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="지구과학 교사 교육 챗봇",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 스타일 설정
st.markdown("""
<style>
.teacher-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    margin-bottom: 20px;
}
.role-badge {
    background-color: #4CAF50;
    color: white;
    padding: 8px 12px;
    border-radius: 5px;
    display: inline-block;
    font-size: 12px;
    margin-bottom: 10px;
}
.message-teacher {
    background-color: #e3f2fd;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
    border-left: 4px solid #2196F3;
}
.message-user {
    background-color: #f3e5f5;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
    border-left: 4px solid #9c27b0;
}
</style>
""", unsafe_allow_html=True)

# 제목
st.markdown("""
<div class="teacher-header">
    <h1>🌍 지구과학 교사 교육 챗봇</h1>
    <p><span class="role-badge">역할: 대학 지구과학 교사 교육 교수</span></p>
    <p>예비교사들을 위한 수업지도안 생성 및 교육 지원 플랫폼</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # API 키 입력
    api_key = st.text_input(
        "Claude API 키",
        type="password",
        help="Anthropic의 Claude API 키를 입력하세요"
    )
    
    st.divider()
    st.subheader("📋 챗봇 정보")
    st.info("""
    **역할**: 대학 지구과학 교사 교육 교수
    
    **지원 기능**:
    - 수업지도안 생성
    - 교육 자료 제작 조언
    - 학습 목표 설정
    - 평가 도구 개발
    - 예비교사 상담
    
    **사용 모델**: Claude Haiku 4.5
    """)
    
    st.divider()
    st.subheader("💡 활용 예시")
    with st.expander("수업지도안 작성"):
        st.write("""
        - 주제: 판구조론
        - 학년: 고등학교 1학년
        - 차시: 2차시
        - 학습 목표를 포함한 전체 지도안 생성 요청
        """)
    
    with st.expander("교수-학습 방법"):
        st.write("""
        - 지구과학 기본 개념 수업 전략
        - 효과적인 실험 설계
        - 디지털 자료 활용법
        """)
    
    with st.expander("평가 계획"):
        st.write("""
        - 형성평가 도구 개발
        - 총괄평가 설계
        - 루브릭(Rubric) 작성
        """)

# 메인 콘텐츠
st.subheader("📝 수업지도안 생성 및 교육 상담")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "client" not in st.session_state:
    st.session_state.client = None

# API 키 검증
if api_key:
    st.session_state.client = anthropic.Anthropic(api_key=api_key)
    api_status = "✅ API 연결됨"
    st.sidebar.success(api_status)
else:
    st.warning("API 키를 입력하세요.")

# 대화 기록 표시
st.subheader("💬 대화")
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.markdown(
            f'<div class="message-user"><b>👨‍🎓 예비교사:</b><br>{message["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="message-teacher"><b>👨‍🏫 교수:</b><br>{message["content"]}</div>',
            unsafe_allow_html=True
        )

# 입력 필드 및 버튼
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "질문을 입력하세요:",
        placeholder="예: 고등학교 1학년 판구조론 2차시 수업지도안을 만들어주세요",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("📤 전송", use_container_width=True)

# 메시지 전송 및 응답 처리
if send_button and user_input:
    if not api_key:
        st.error("API 키를 먼저 입력해주세요.")
    else:
        # 사용자 메시지 추가
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # 시스템 프롬프트
        system_prompt = """당신은 대학에서 지구과학 예비교사들을 교육하는 교수입니다.

당신의 역할과 책임:
1. 예비교사들의 수업지도안 생성 지원
2. 효과적인 지구과학 교수-학습 방법 제시
3. 평가 도구 및 루브릭 개발 조언
4. 학습 목표 설정 및 성취기준 연계
5. 현장 교육 경험 바탕의 실용적 조언 제공

응답 원칙:
- 항상 예비교사의 입장에서 친절하고 격려하는 톤 사용
- 구체적이고 실행 가능한 조언 제공
- 필요시 수업지도안의 전체 구조 제시
- 지구과학의 핵심 개념과 교육과정 기준 반영
- 학생들의 흥미와 참여도를 높이는 방법 강조"""
        
        # API 호출
        with st.spinner("교수님께서 답변을 준비 중입니다..."):
            try:
                response = st.session_state.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2048,
                    system=system_prompt,
                    messages=st.session_state.messages
                )
                
                assistant_message = response.content[0].text
                
                # 어시스턴트 응답 추가
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                # 페이지 새로고침
                st.rerun()
                
            except anthropic.APIError as e:
                st.error(f"API 오류: {str(e)}")

# 하단 정보
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("총 메시지 수", len(st.session_state.messages))

with col2:
    st.metric("현재 시간", datetime.now().strftime("%H:%M"))

with col3:
    if st.button("🔄 대화 초기화"):
        st.session_state.messages = []
        st.rerun()

st.caption("🌍 지구과학 교사 교육 챗봇 v1.0 - Streamlit Cloud 배포")