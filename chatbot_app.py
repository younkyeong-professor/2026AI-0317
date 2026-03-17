import streamlit as st
import anthropic
from datetime import datetime
import json

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
.lesson-plan-container {
    background-color: #f5f5f5;
    padding: 20px;
    border-radius: 10px;
    margin: 15px 0;
}
.lesson-section {
    background-color: white;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
    border-left: 5px solid #667eea;
}
.teacher-activity {
    background-color: #fff3cd;
    padding: 12px;
    border-radius: 6px;
    margin: 8px 0;
    border-left: 4px solid #ffc107;
}
.student-activity {
    background-color: #d1ecf1;
    padding: 12px;
    border-radius: 6px;
    margin: 8px 0;
    border-left: 4px solid #17a2b8;
}
.table-container {
    overflow-x: auto;
    margin: 15px 0;
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
    - 교사활동/학생활동 구분 수업지도안 생성
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
        - 교사활동과 학생활동의 구분
        - 상호작용적 수업 설계
        - 효과적인 실험 설계
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

if "lesson_plan" not in st.session_state:
    st.session_state.lesson_plan = None

# API 키 검증
if api_key:
    st.session_state.client = anthropic.Anthropic(api_key=api_key)
    api_status = "✅ API 연결됨"
    st.sidebar.success(api_status)
else:
    st.warning("API 키를 입력하세요.")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["💬 대화", "📋 수업지도안", "📊 활동 가이드"])

# 탭 1: 대화
with tab1:
    st.subheader("교수님과의 대화")
    
    # 대화 기록 표시
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
            placeholder="예: 고등학교 1학년 판구조론 2차시 수업지도안을 만들어주세요. 교사활동과 학생활동을 구분해서요.",
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

수업지도안 생성 시 필수 포함 항목:
- 학년/단원/차시
- 학습 목표
- 학습 내용
- 교수-학습 활동 (교사활동 vs 학생활동 명확히 구분)
- 평가 계획
- 준비물/자료

응답 원칙:
- 항상 예비교사의 입장에서 친절하고 격려하는 톤 사용
- 구체적이고 실행 가능한 조언 제공
- 교사활동과 학생활동을 명확히 구분하여 표시
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
                    
                    # 수업지도안 데이터 저장
                    if "수업지도안" in assistant_message or "지도안" in assistant_message:
                        st.session_state.lesson_plan = assistant_message
                    
                    # 페이지 새로고침
                    st.rerun()
                    
                except anthropic.APIError as e:
                    st.error(f"API 오류: {str(e)}")

# 탭 2: 수업지도안
with tab2:
    st.subheader("📋 생성된 수업지도안")
    
    if st.session_state.lesson_plan:
        st.markdown('<div class="lesson-plan-container">', unsafe_allow_html=True)
        st.markdown(st.session_state.lesson_plan)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 다운로드 버튼
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 수업지도안 다운로드 (텍스트)",
                data=st.session_state.lesson_plan,
                file_name=f"수업지도안_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        with col2:
            if st.button("🔄 수업지도안 초기화"):
                st.session_state.lesson_plan = None
                st.rerun()
    else:
        st.info("💡 대화 탭에서 수업지도안을 요청하면 여기에 표시됩니다.")
        
        # 수업지도안 템플릿 표시
        st.subheader("📌 수업지도안 구성 예시")
        
        with st.expander("표준 수업지도안 구조"):
            st.markdown("""
### 기본 정보
- **학년**: 고등학교 1학년
- **단원**: 지구의 역사
- **차시**: 2/10

### 학습 목표
- 판구조론의 증거를 이해한다
- 지진 발생 원인을 설명할 수 있다

### 교수-학습 활동

#### 도입 (5분)
**👨‍🏫 교사활동**
- 최근 지진 뉴스 영상 보여주기
- 학생들의 경험 질문하기

**👨‍🎓 학생활동**
- 지진 영상 시청
- 경험 공유하기

#### 전개 (30분)
**👨‍🏫 교사활동**
- 판의 이동 시뮬레이션 제시
- 설명 및 질의응답

**👨‍🎓 학생활동**
- 모둠별 판 모형으로 실험
- 지진 발생 원인 토론

#### 정리 (5분)
**👨‍🏫 교사활동**
- 핵심 내용 정리
- 다음 차시 예고

**👨‍🎓 학생활동**
- 학습 내용 요약
- 질문하기

### 평가 계획
- 형성평가: 토론 참여도 관찰
- 총괄평가: 개념도 작성
            """)

# 탭 3: 활동 가이드
with tab3:
    st.subheader("📊 교사활동 vs 학생활동 설계 가이드")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
### 👨‍🏫 교사활동 (Teacher Activity)

**정의**: 교사가 주도적으로 수행하는 활동

**특징**:
- 지식 전달
- 시범 시연
- 질문 제시
- 설명 및 강의
- 학습 환경 조성

**예시**:
- 개념 설명하기
- 실험 시연하기
- 동영상 재생하기
- 판서하기
- 칠판에 그려 설명하기
- 학생 의견 들어주기
- 피드백 제공하기
        """)
    
    with col2:
        st.markdown("""
### 👨‍🎓 학생활동 (Student Activity)

**정의**: 학생이 주도적으로 수행하는 활동

**특징**:
- 직접 경험
- 협력 학습
- 문제 해결
- 탐구 활동
- 표현 및 발표

**예시**:
- 실험 수행하기
- 토론하기
- 모둠활동하기
- 노트 정리하기
- 그림 그리기
- 발표하기
- 질문하기
- 개념도 만들기
        """)
    
    st.divider()
    
    st.subheader("⚖️ 균형 잡힌 수업 설계")
    
    # 단계별 활동 비율
    stages = ["도입", "전개", "정리"]
    teacher_ratio = [30, 40, 50]
    student_ratio = [70, 60, 50]
    
    col1, col2, col3 = st.columns(3)
    
    for i, stage in enumerate(stages):
        with [col1, col2, col3][i]:
            st.metric(
                f"{stage} 단계",
                f"교사 {teacher_ratio[i]}% / 학생 {student_ratio[i]}%"
            )
    
    st.info("""
    **💡 설계 팁**:
    - **도입**: 학생의 관심 유도 (학생 중심)
    - **전개**: 교사 설명 + 학생 활동 (균형)
    - **정리**: 학생 정리 + 교사 확인 (학생 중심)
    """)
    
    st.subheader("📈 효과적인 활동 조합")
    
    with st.expander("직접교수 + 협력학습"):
        st.write("""
        **교사활동**: 개념 설명 및 시범
        ↓
        **학생활동**: 모둠별 문제 해결
        ↓
        **교사활동**: 피드백 및 정리
        """)
    
    with st.expander("탐구활동 + 토론"):
        st.write("""
        **교사활동**: 문제 제시 및 기자재 준비
        ↓
        **학생활동**: 실험 수행 및 자료 수집
        ↓
        **학생활동**: 모둠 간 토론
        ↓
        **교사활동**: 의견 조정 및 개념 정리
        """)

# 하단 정보
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("총 메시지 수", len(st.session_state.messages))

with col2:
    st.metric("현재 시간", datetime.now().strftime("%H:%M"))

with col3:
    if st.button("🔄 전체 대화 초기화"):
        st.session_state.messages = []
        st.session_state.lesson_plan = None
        st.rerun()

st.caption("🌍 지구과학 교사 교육 챗봇 v2.0 - Streamlit Cloud 배포")
