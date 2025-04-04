import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# 상위 디렉토리 경로 추가 (utils.py와 config.py 임포트를 위해)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import config

# 인증 확인
utils.check_authentication()

# 페이지 설정
st.set_page_config(
    page_title="데이터 분석",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 추가
st.markdown(utils.get_css(), unsafe_allow_html=True)

# 페이지 제목
st.markdown('<div class="main-header">📈 데이터 분석</div>', unsafe_allow_html=True)

# 데이터 로드
df = utils.generate_sample_data()

# 탭 생성
tabs = st.tabs(["카테고리 분석", "지역 분석", "시계열 분석", "데이터 탐색"])

# 탭 1: 카테고리 분석
with tabs[0]:
    st.markdown('<div class="section-header">카테고리별 분석</div>', unsafe_allow_html=True)
    
    # 카테고리 선택
    categories = sorted(df['카테고리'].unique())
    selected_categories = st.multiselect(
        "분석할 카테고리 선택",
        options=categories,
        default=categories
    )
    
    if not selected_categories:
        st.warning("분석할 카테고리를 하나 이상 선택하세요.")
    else:
        filtered_df = df[df['카테고리'].isin(selected_categories)]
        
        # 카테고리별 집계 데이터
        category_data = filtered_df.groupby('카테고리').agg(
            매출합계=('매출', 'sum'),
            이익합계=('이익', 'sum'),
            이익률=('이익', lambda x: np.sum(x) / filtered_df.loc[x.index, '매출'].sum() * 100),
            거래수=('매출', 'count'),
            평균매출=('매출', 'mean')
        ).reset_index()
        
        # 카테고리별 시각화
        col1, col2 = st.columns(2)
        
        with col1:
            # 매출 및 이익 비교
            bar_fig = px.bar(
                category_data,
                x='카테고리',
                y=['매출합계', '이익합계'],
                barmode='group',
                title="카테고리별 매출 및 이익",
                color_discrete_sequence=['#1E88E5', '#5E35B1']
            )
            
            st.plotly_chart(bar_fig, use_container_width=True)
            
            # 데이터 테이블
            st.markdown("#### 카테고리별 상세 데이터")
            
            # 표시용 데이터 포맷팅
            display_data = category_data.copy()
            display_data['매출합계'] = display_data['매출합계'].apply(lambda x: f"{x:,.0f}원")
            display_data['이익합계'] = display_data['이익합계'].apply(lambda x: f"{x:,.0f}원")
            display_data['이익률'] = display_data['이익률'].apply(lambda x: f"{x:.2f}%")
            display_data['평균매출'] = display_data['평균매출'].apply(lambda x: f"{x:,.0f}원")
            
            st.dataframe(display_data, use_container_width=True)
        
        with col2:
            # 파이 차트
            pie_fig = px.pie(
                category_data,
                values='매출합계',
                names='카테고리',
                title="카테고리별 매출 비중",
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            pie_fig.update_traces(textposition='inside', textinfo='percent+label')
            
            st.plotly_chart(pie_fig, use_container_width=True)
            
            # 이익률 차트
            profit_fig = px.bar(
                category_data,
                x='카테고리',
                y='이익률',
                title="카테고리별 이익률",
                color_discrete_sequence=['#5E35B1'],
                text_auto='.2f'
            )
            profit_fig.update_layout(yaxis_title="이익률 (%)")
            
            st.plotly_chart(profit_fig, use_container_width=True)

# 탭 2: 지역 분석
with tabs[1]:
    st.markdown('<div class="section-header">지역별 분석</div>', unsafe_allow_html=True)
    
    # 지역 선택
    regions = sorted(df['지역'].unique())
    selected_regions = st.multiselect(
        "분석할 지역 선택",
        options=regions,
        default=regions
    )
    
    if not selected_regions:
        st.warning("분석할 지역을 하나 이상 선택하세요.")
    else:
        filtered_df = df[df['지역'].isin(selected_regions)]
        
        # 지역별 집계 데이터
        region_data = filtered_df.groupby('지역').agg(
            매출합계=('매출', 'sum'),
            이익합계=('이익', 'sum'),
            이익률=('이익', lambda x: np.sum(x) / filtered_df.loc[x.index, '매출'].sum() * 100),
            거래수=('매출', 'count'),
            평균매출=('매출', 'mean')
        ).reset_index()
        
        # 지역별 시각화
        col1, col2 = st.columns(2)
        
        with col1:
            # 매출 및 이익 비교
            bar_fig = px.bar(
                region_data,
                x='지역',
                y=['매출합계', '이익합계'],
                barmode='group',
                title="지역별 매출 및 이익",
                color_discrete_sequence=['#1E88E5', '#5E35B1']
            )
            
            st.plotly_chart(bar_fig, use_container_width=True)
            
            # 이익률 차트
            profit_fig = px.bar(
                region_data,
                x='지역',
                y='이익률',
                title="지역별 이익률",
                color_discrete_sequence=['#5E35B1'],
                text_auto='.2f'
            )
            profit_fig.update_layout(yaxis_title="이익률 (%)")
            
            st.plotly_chart(profit_fig, use_container_width=True)
        
        with col2:
            # 지도 시각화
            st.markdown("#### 지역별 매출 분포")
            
            # 지도 데이터 생성
            map_data = utils.get_map_data(filtered_df)
            
            # 매출 기준 지도
            fig = px.scatter_mapbox(
                map_data,
                lat="lat",
                lon="lon",
                color="sales",
                size="sales",
                hover_name="region",
                hover_data={"sales": True, "profit": True, "count": True, "lat": False, "lon": False},
                color_continuous_scale=px.colors.sequential.Blues,
                size_max=30,
                zoom=6,
                mapbox_style="open-street-map"
            )
            
            fig.update_layout(
                height=500,
                margin={"r": 0, "t": 0, "l": 0, "b": 0}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 데이터 테이블
            st.markdown("#### 지역별 상세 데이터")
            
            # 표시용 데이터 포맷팅
            display_data = region_data.copy()
            display_data['매출합계'] = display_data['매출합계'].apply(lambda x: f"{x:,.0f}원")
            display_data['이익합계'] = display_data['이익합계'].apply(lambda x: f"{x:,.0f}원")
            display_data['이익률'] = display_data['이익률'].apply(lambda x: f"{x:.2f}%")
            display_data['평균매출'] = display_data['평균매출'].apply(lambda x: f"{x:,.0f}원")
            
            st.dataframe(display_data, use_container_width=True)

# 탭 3: 시계열 분석
with tabs[2]:
    st.markdown('<div class="section-header">시계열 분석</div>', unsafe_allow_html=True)
    
    # 필터 옵션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        time_unit = st.radio(
            "시간 단위",
            ["일별", "주별", "월별", "분기별"],
            horizontal=True
        )
    
    with col2:
        metrics = st.multiselect(
            "표시할 지표",
            options=["매출", "이익", "거래수"],
            default=["매출", "이익"]
        )
    
    with col3:
        show_ma = st.checkbox("이동평균 표시", value=False)
        if show_ma:
            ma_window = st.slider("이동평균 기간", 2, 10, 3)
    
    # 시계열 데이터 집계
    time_data = utils.aggregate_by_time(df, time_unit)
    
    # 이동평균 계산
    if show_ma and len(time_data) > ma_window:
        for metric in metrics:
            time_data[f"{metric}_MA"] = time_data[metric].rolling(window=ma_window).mean()
    
    # 시계열 차트
    fig = go.Figure()
    
    # 원본 데이터 추가
    for metric in metrics:
        fig.add_trace(go.Scatter(
            x=time_data['time_group'],
            y=time_data[metric],
            mode='lines+markers',
            name=metric
        ))
        
        # 이동평균 추가
        if show_ma and len(time_data) > ma_window:
            fig.add_trace(go.Scatter(
                x=time_data['time_group'][ma_window-1:],
                y=time_data[f"{metric}_MA"][ma_window-1:],
                mode='lines',
                line=dict(dash='dash'),
                name=f"{metric} {ma_window}기간 이동평균"
            ))
    
    fig.update_layout(
        title=f"{time_unit} 추이 분석",
        xaxis_title="기간",
        yaxis_title="값",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 월별/요일별 히트맵
    st.markdown("### 패턴 분석")
    
    if len(df) > 0:
        # 요일별 데이터 준비
        df['요일'] = df['날짜'].dt.day_name()
        df['월'] = df['날짜'].dt.month
        
        # 요일 순서 지정
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df['요일_정렬'] = pd.Categorical(df['요일'], categories=weekday_order, ordered=True)
        
        # 월-요일별 집계
        heatmap_data = df.groupby(['월', '요일_정렬']).agg(
            매출=('매출', 'sum')
        ).reset_index()
        
        # 피봇 테이블 생성
        pivot_data = heatmap_data.pivot(index='요일_정렬', columns='월', values='매출')
        
        # 히트맵 차트
        heatmap_fig = px.imshow(
            pivot_data,
            labels=dict(x="월", y="요일", color="매출액"),
            x=pivot_data.columns,
            y=pivot_data.index,
            color_continuous_scale="Blues",
            aspect="auto",
            title="월-요일별 매출 패턴"
        )
        
        heatmap_fig.update_layout(height=400)
        st.plotly_chart(heatmap_fig, use_container_width=True)

# 탭 4: 데이터 탐색
with tabs[3]:
    st.markdown('<div class="section-header">데이터 탐색</div>', unsafe_allow_html=True)
    
    # 검색 및 필터 옵션
    st.markdown("### 데이터 필터링")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_category = st.multiselect(
            "카테고리 필터",
            options=sorted(df['카테고리'].unique()),
            default=[]
        )
    
    with col2:
        search_region = st.multiselect(
            "지역 필터",
            options=sorted(df['지역'].unique()),
            default=[]
        )
    
    with col3:
        min_sales = st.number_input("최소 매출액", value=0)
    
    # 필터 적용
    filtered_df = df.copy()
    if search_category:
        filtered_df = filtered_df[filtered_df['카테고리'].isin(search_category)]
    if search_region:
        filtered_df = filtered_df[filtered_df['지역'].isin(search_region)]
    if min_sales > 0:
        filtered_df = filtered_df[filtered_df['매출'] >= min_sales]
    
    # 정렬 옵션
    sort_col = st.selectbox(
        "정렬 기준",
        options=["날짜", "매출", "이익", "카테고리", "지역"],
        index=0
    )
    
    sort_order = st.radio(
        "정렬 방향",
        options=["내림차순", "오름차순"],
        horizontal=True,
        index=0
    )
    
    # 정렬 적용
    if sort_order == "내림차순":
        filtered_df = filtered_df.sort_values(sort_col, ascending=False)
    else:
        filtered_df = filtered_df.sort_values(sort_col)
    
    # 페이지네이션
    rows_per_page = st.slider("페이지당 행 수", 10, 100, 20)
    page_number = st.number_input("페이지 번호", min_value=1, value=1)
    
    # 총 페이지 수 계산
    total_pages = (len(filtered_df) - 1) // rows_per_page + 1
    st.write(f"총 {len(filtered_df)}개 항목 중 {rows_per_page}개씩 표시 (총 {total_pages}페이지)")
    
    # 페이지네이션 적용
    start_idx = (page_number - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, len(filtered_df))
    paged_df = filtered_df.iloc[start_idx:end_idx]
    
    # 테이블 표시
    st.dataframe(paged_df, use_container_width=True)
    
    # CSV 다운로드 버튼
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="CSV로 다운로드",
        data=csv,
        file_name=f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )