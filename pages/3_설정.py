import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# 상위 디렉토리 경로 추가 (utils.py와 config.py 임포트를 위해)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import config

# 인증 확인
utils.check_authentication()

# 관리자만 접근 가능한 페이지인지 확인
is_admin = st.session_state.username == "admin"

# CSS 스타일 추가
st.markdown(utils.get_css(), unsafe_allow_html=True)

# 페이지 제목
st.markdown('<div class="main-header">⚙️ 설정</div>', unsafe_allow_html=True)

# 탭 생성
tabs = st.tabs(["화면 설정", "알림 설정", "계정 설정", "고급 설정"])

# 탭 1: 화면 설정
with tabs[0]:
    st.markdown('<div class="section-header">화면 설정</div>', unsafe_allow_html=True)
    
    # 화면 설정 옵션
    col1, col2 = st.columns(2)
    
    with col1:
        theme = st.selectbox(
            "테마 선택",
            ["라이트 모드", "다크 모드", "시스템 설정 따르기"],
            index=0
        )
        
        color_theme = st.color_picker("주 색상 테마", "#1E88E5")
        
        font_size = st.select_slider(
            "기본 글꼴 크기",
            options=["작게", "보통", "크게", "매우 크게"],
            value="보통"
        )
        
        chart_style = st.selectbox(
            "차트 스타일",
            ["기본", "모던", "미니멀", "클래식"],
            index=0
        )
    
    with col2:
        # 설정 미리보기
        preview_style = f"""
        <div style="padding: 20px; border-radius: 10px; background-color: {'#fff' if theme == '라이트 모드' else '#333'}; color: {'#333' if theme == '라이트 모드' else '#fff'}; margin-top: 20px;">
            <h3 style="color: {color_theme};">화면 설정 미리보기</h3>
            <p style="font-size: {'0.9rem' if font_size == '작게' else '1rem' if font_size == '보통' else '1.2rem' if font_size == '크게' else '1.4rem'};">
                이 텍스트는 선택한 설정이 적용된 미리보기입니다. 실제 적용 시에는 앱 전체에 변경사항이 반영됩니다.
            </p>
            <div style="height: 20px; background-color: {color_theme}; margin: 10px 0; border-radius: 5px;"></div>
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <button style="padding: 8px 12px; background-color: {color_theme}; color: white; border: none; border-radius: 5px; cursor: pointer;">버튼 예시</button>
                <div style="padding: 8px 12px; border: 1px solid {'#ddd' if theme == '라이트 모드' else '#555'}; border-radius: 5px;">입력 필드 예시</div>
            </div>
        </div>
        """
        
        st.markdown(preview_style, unsafe_allow_html=True)
    
    # 저장 버튼
    if st.button("화면 설정 저장", key="save_display"):
        st.success("화면 설정이 성공적으로 저장되었습니다! (데모용)")
        st.info("참고: 이 데모 앱에서는 실제로 설정이 적용되지 않습니다.")

# 탭 2: 알림 설정
with tabs[1]:
    st.markdown('<div class="section-header">알림 설정</div>', unsafe_allow_html=True)
    
    # 알림 유형
    st.markdown("### 알림 유형 선택")
    
    enable_email = st.toggle("이메일 알림", value=True)
    if enable_email:
        email = st.text_input("이메일 주소", placeholder="your.email@example.com")
    
    enable_mobile = st.toggle("모바일 앱 알림", value=True)
    
    enable_slack = st.toggle("Slack 알림", value=False)
    if enable_slack:
        slack_channel = st.text_input("Slack 채널", placeholder="#analytics")
    
    # 알림 이벤트
    st.markdown("### 알림 이벤트")
    
    notify_events = st.multiselect(
        "알림 받을 이벤트",
        options=[
            "일일 보고서", 
            "주간 요약", 
            "월간 리포트", 
            "이상치 감지", 
            "목표 달성",
            "시스템 경고"
        ],
        default=["일일 보고서", "이상치 감지"]
    )
    
    # 알림 일정
    st.markdown("### 알림 일정")
    
    if "일일 보고서" in notify_events:
        daily_time = st.time_input("일일 보고서 시간", value=datetime.strptime("09:00", "%H:%M").time())
    
    if "주간 요약" in notify_events:
        weekly_day = st.selectbox(
            "주간 요약 요일",
            options=["월요일", "화요일", "수요일", "목요일", "금요일"]
        )
    
    if "월간 리포트" in notify_events:
        monthly_day = st.slider("월간 리포트 날짜", 1, 28, 1)
    
    # 알림 임계값
    if "이상치 감지" in notify_events or "목표 달성" in notify_events:
        st.markdown("### 알림 임계값")
        
        if "이상치 감지" in notify_events:
            anomaly_threshold = st.slider(
                "이상치 감지 임계값 (표준편차)",
                1.0, 5.0, 3.0, 0.1
            )
        
        if "목표 달성" in notify_events:
            goal_percentage = st.slider(
                "목표 달성 알림 (목표 대비 %)",
                50, 100, 90, 5
            )
    
    # 저장 버튼
    if st.button("알림 설정 저장"):
        st.success("알림 설정이 성공적으로 저장되었습니다! (데모용)")
        st.info("참고: 이 데모 앱에서는 실제로 알림이 전송되지 않습니다.")

# 탭 3: 계정 설정
with tabs[2]:
    st.markdown('<div class="section-header">계정 설정</div>', unsafe_allow_html=True)
    
    # 현재 로그인한 사용자 정보 표시
    st.markdown(f"### {st.session_state.username} 계정 정보")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # 프로필 이미지 (더미)
        st.image("https://via.placeholder.com/150", caption="프로필 이미지")
        st.button("이미지 변경", disabled=True)
    
    with col2:
        # 사용자 정보
        user_name = st.text_input("이름", value="사용자 이름", disabled=not is_admin)
        user_email = st.text_input("이메일", value="user@example.com", disabled=not is_admin)
        user_dept = st.text_input("부서", value="데이터 분석팀", disabled=not is_admin)
        user_role = st.selectbox(
            "역할",
            options=["관리자", "분석가", "일반 사용자", "게스트"],
            index=0 if st.session_state.username == "admin" else 2,
            disabled=not is_admin
        )
    
    # 비밀번호 변경
    st.markdown("### 비밀번호 변경")
    
    with st.form("password_change_form"):
        current_pwd = st.text_input("현재 비밀번호", type="password")
        new_pwd = st.text_input("새 비밀번호", type="password")
        confirm_pwd = st.text_input("새 비밀번호 확인", type="password")
        
        submit_pwd = st.form_submit_button("비밀번호 변경")
        
        if submit_pwd:
            if current_pwd and new_pwd and confirm_pwd:
                if new_pwd == confirm_pwd:
                    # 실제로는 여기서 비밀번호 변경 로직이 들어갑니다
                    st.success("비밀번호가 성공적으로 변경되었습니다! (데모용)")
                else:
                    st.error("새 비밀번호와 확인이 일치하지 않습니다.")
            else:
                st.error("모든 필드를 입력해주세요.")

# 탭 4: 고급 설정 (관리자 전용)
with tabs[3]:
    st.markdown('<div class="section-header">고급 설정</div>', unsafe_allow_html=True)
    
    if not is_admin:
        st.warning("이 설정은 관리자만 접근할 수 있습니다.")
        st.info(f"현재 계정: {st.session_state.username} (관리자 권한 없음)")
        st.stop()
    
    # 관리자만 볼 수 있는 내용
    st.markdown("### 시스템 설정")
    
    # 데이터 설정
    st.markdown("#### 데이터 설정")
    data_refresh = st.select_slider(
        "데이터 자동 갱신 주기",
        options=["사용 안함", "5분", "15분", "30분", "1시간", "3시간", "6시간", "12시간", "24시간"],
        value="1시간"
    )
    
    data_retention = st.slider("데이터 보존 기간 (일)", 30, 365, 90)
    
    # 사용자 관리
    st.markdown("#### 사용자 관리")
    max_users = st.number_input("최대 동시 접속 사용자 수", 1, 100, 10)
    
    session_timeout = st.slider("세션 만료 시간 (분)", 5, 240, 60)
    
    # 백업 설정
    st.markdown("#### 백업 설정")
    backup_freq = st.selectbox(
        "자동 백업 주기",
        options=["사용 안함", "일일", "주간", "월간"],
        index=2
    )
    
    backup_retention = st.slider("백업 보존 기간 (일)", 7, 365, 30)
    
    # 고급 보안 설정
    st.markdown("#### 보안 설정")
    
    enable_2fa = st.toggle("2단계 인증 필수화", value=False)
    password_expiry = st.slider("비밀번호 만료 기간 (일)", 0, 180, 90, help="0은 만료되지 않음을 의미합니다")
    min_pwd_length = st.slider("최소 비밀번호 길이", 6, 24, 8)
    
    # API 설정
    st.markdown("#### API 설정")
    enable_api = st.toggle("API 활성화", value=True)
    
    if enable_api:
        rate_limit = st.number_input("API 요청 제한 (분당)", 10, 1000, 100)
        api_key_expiry = st.slider("API 키 만료 기간 (일)", 1, 365, 30)
        
        st.info("API 키 관리는 여기서 합니다. (데모용)")
        
        # API 키 관리 예시 테이블
        api_keys_df = pd.DataFrame({
            "키 이름": ["분석 API", "읽기 전용 API", "테스트 API"],
            "생성일": ["2023-01-15", "2023-03-20", "2023-05-10"],
            "만료일": ["2023-07-15", "2023-09-20", "2023-11-10"],
            "상태": ["활성", "활성", "만료됨"]
        })
        
        st.dataframe(api_keys_df, use_container_width=True)
    
    # 저장 버튼
    if st.button("고급 설정 저장"):
        st.success("고급 설정이 성공적으로 저장되었습니다! (데모용)")
        st.info("참고: 이 데모 앱에서는 실제로 설정이 적용되지 않습니다.")