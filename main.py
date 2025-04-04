import streamlit as st
import pandas as pd
import time
from datetime import datetime
import config  # 설정 파일 임포트
import os
import utils

# 페이지 설정
st.set_page_config(
    page_title="멀티페이지 앱 예시",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'login_time' not in st.session_state:
    st.session_state.login_time = None

# CSS 스타일 추가
st.markdown(utils.get_css(), unsafe_allow_html=True)

# 로그인 함수
def login(username, password):
    if username in config.USERS and config.USERS[username] == password:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.login_time = datetime.now()
        return True
    else:
        return False

# 로그아웃 함수
def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.login_time = None

# 로그인 상태가 아닌 경우 로그인 폼 표시
if not st.session_state.authenticated:
    st.markdown('<div class="main-header">📊 비즈니스 인텔리전스 대시보드</div>', unsafe_allow_html=True)
    
    # 로그인 컨테이너 스타일링
    login_container = st.container()
    
    with login_container:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="section-header">로그인</div>', unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("사용자 이름")
                password = st.text_input("비밀번호", type="password")
                submit = st.form_submit_button("로그인")
                
                if submit:
                    if login(username, password):
                        st.success("로그인 성공! 잠시 후 대시보드로 이동합니다.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("사용자 이름 또는 비밀번호가 올바르지 않습니다.")
            
            # 데모 사용자 정보 표시
            st.markdown("---")
            st.markdown("#### 데모 계정")
            st.markdown("- 관리자: `admin` / 비밀번호: `admin123`")
            st.markdown("- 사용자: `user` / 비밀번호: `user123`")
else:
    # 로그인된 경우, 앱의 메인 기능 표시
    
    # 사이드바에 로그인 정보 표시
    with st.sidebar:
        st.markdown(f"### 환영합니다, {st.session_state.username}님!")
        if st.session_state.login_time:
            login_time_str = st.session_state.login_time.strftime("%Y-%m-%d %H:%M:%S")
            st.markdown(f"로그인 시간: {login_time_str}")
        
        # 로그아웃 버튼
        if st.button("로그아웃"):
            logout()
            st.experimental_rerun()
    
    # 메인 페이지 내용
    st.markdown('<div class="main-header">📊 비즈니스 인텔리전스 대시보드</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🏠 홈</div>', unsafe_allow_html=True)
    
    # 시작 페이지 메시지
    st.markdown("""
    안녕하세요! 이 앱은 Streamlit 멀티페이지 대시보드의 예시입니다.
    
    왼쪽의 사이드바에서 다양한 페이지를 선택하여 살펴보세요:
    
    - **대시보드**: 주요 성과 지표와 분석 결과를 확인하세요.
    - **데이터 분석**: 카테고리별, 지역별, 시계열 분석을 수행하세요.
    - **설정**: 화면, 알림 및 계정 설정을 관리하세요.
    """)
    
    # 샘플 데이터 생성
    df = utils.generate_sample_data()
    
    # KPI 표시
    st.markdown("### 주요 성과 지표")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 매출", f"{df['매출'].sum():,.0f}원", "+12%")
    
    with col2:
        st.metric("총 이익", f"{df['이익'].sum():,.0f}원", "+8%")
    
    with col3:
        st.metric("제품 수", f"{df['카테고리'].nunique()}개", "0")
    
    with col4:
        st.metric("지역 수", f"{df['지역'].nunique()}개", "0")
    
    # 앱 정보
    with st.expander("앱 정보"):
        st.markdown("""
        **Streamlit 멀티페이지 대시보드** v1.0
        
        이 대시보드는 Streamlit의 멀티페이지 기능을 활용한 예시 애플리케이션입니다.
        로그인 기능과 다양한 페이지를 포함하고 있습니다.
        
        © 2023 Example Corp.
        """)