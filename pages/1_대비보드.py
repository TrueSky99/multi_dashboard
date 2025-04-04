import streamlit as st
import pandas as pd
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
    page_title="대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 추가
st.markdown(utils.get_css(), unsafe_allow_html=True)

# 페이지 제목
st.markdown('<div class="main-header">📊 실시간 대시보드</div>', unsafe_allow_html=True)

# 필터 섹션
st.sidebar.markdown("## 필터 옵션")

# 날짜 필터
today = datetime.now().date()
start_date = today - timedelta(days=30)
date_range = st.sidebar.date_input(
    "날짜 범위",
    value=(start_date, today),
    min_value=today-timedelta(days=365),
    max_value=today
)

if len(date_range) == 2:
    start_date, end_date = date_range
    date_filter = f"{start_date} ~ {end_date}"
else:
    date_filter = "전체 기간"

# 카테고리 필터
df = utils.generate_sample_data()
categories = df['카테고리'].unique().tolist()
selected_categories = st.sidebar.multiselect(
    "카테고리 선택",
    options=categories,
    default=categories
)

# 지역 필터
regions = df['지역'].unique().tolist()
selected_regions = st.sidebar.multiselect(
    "지역 선택",
    options=regions,
    default=regions
)

# 필터 적용
if selected_categories:
    df = df[df['카테고리'].isin(selected_categories)]
if selected_regions:
    df = df[df['지역'].isin(selected_regions)]
if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)]

# 데이터 없음 확인
if df.empty:
    st.warning("선택한 필터에 해당하는 데이터가 없습니다.")
    
    # 필터 리셋 버튼 추가
    if st.button("모든 필터 초기화"):
        # 세션 상태에서 필터 설정을 초기화
        st.session_state['selected_categories'] = categories
        st.session_state['selected_regions'] = regions
        st.session_state['date_range'] = (start_date, today)
        st.rerun()
    
    # 샘플 데이터를 다시 생성해 기본 화면을 표시
    df = utils.generate_sample_data()

# KPI 섹션
st.markdown("### 주요 성과 지표")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = df['매출'].sum()
    prev_total_sales = total_sales * 0.88  # 가상의 이전 데이터 (12% 증가 가정)
    sales_change = ((total_sales - prev_total_sales) / prev_total_sales) * 100
    st.metric("총 매출", f"{total_sales:,.0f}원", f"{sales_change:.1f}%")

with col2:
    total_profit = df['이익'].sum()
    prev_total_profit = total_profit * 0.92  # 가상의 이전 데이터 (8% 증가 가정)
    profit_change = ((total_profit - prev_total_profit) / prev_total_profit) * 100
    st.metric("총 이익", f"{total_profit:,.0f}원", f"{profit_change:.1f}%")

with col3:
    avg_profit_margin = (df['이익'].sum() / df['매출'].sum()) * 100
    prev_margin = avg_profit_margin * 0.95  # 가상의 이전 데이터 (5% 증가 가정)
    margin_change = avg_profit_margin - prev_margin
    st.metric("평균 이익률", f"{avg_profit_margin:.1f}%", f"{margin_change:.1f}%")

with col4:
    total_orders = len(df)
    prev_orders = total_orders * 0.85  # 가상의 이전 데이터 (15% 증가 가정)
    orders_change = ((total_orders - prev_orders) / prev_orders) * 100
    st.metric("총 주문 건수", f"{total_orders:,}건", f"{orders_change:.1f}%")

# 시계열 차트
st.markdown("### 시간별 추이")

time_unit = st.radio(
    "시간 단위",
    ["일별", "주별", "월별", "분기별"],
    horizontal=True
)

time_data = utils.aggregate_by_time(df, time_unit)

# 매출 & 이익 추이 차트
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=time_data['time_group'],
    y=time_data['매출'],
    mode='lines+markers',
    name='매출'
))
fig.add_trace(go.Scatter(
    x=time_data['time_group'],
    y=time_data['이익'],
    mode='lines+markers',
    name='이익'
))

fig.update_layout(
    title=f'{time_unit} 매출 및 이익 추이',
    xaxis_title='날짜',
    yaxis_title='금액',
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# 카테고리 및 지역 분석
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 카테고리별 분석")
    
    # 카테고리별 매출 집계
    category_data = df.groupby('카테고리').agg(
        매출=('매출', 'sum'),
        이익=('이익', 'sum'),
        주문수=('매출', 'count')
    ).reset_index()
    
    # 파이 차트
    fig = px.pie(
        category_data,
        values='매출',
        names='카테고리',
        title='카테고리별 매출 비중',
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 지역별 분석")
    
    # 지역별 매출 집계
    region_data = df.groupby('지역').agg(
        매출=('매출', 'sum'),
        이익=('이익', 'sum'),
        주문수=('매출', 'count')
    ).reset_index()
    
    # 막대 차트
    fig = px.bar(
        region_data,
        x='지역',
        y='매출',
        color='이익',
        text_auto='.2s',
        title='지역별 매출 및 이익',
        color_continuous_scale='Blues'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# 지도 시각화
st.markdown("### 지역별 매출 분포")

# 지도 데이터 생성
map_data = utils.get_map_data(df)

# 지도와 크기 조정
map_fig = px.scatter_mapbox(
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
    title="지역별 매출 분포"
)

map_fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    height=500
)

st.plotly_chart(map_fig, use_container_width=True)

# 상세 데이터 테이블
with st.expander("상세 데이터"):
    display_cols = ['날짜', '카테고리', '지역', '매출', '이익']
    st.dataframe(df[display_cols].sort_values('날짜', ascending=False), use_container_width=True)