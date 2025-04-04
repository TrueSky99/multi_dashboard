import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config

# CSS 스타일 정의
def get_css():
    return """
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
            margin-bottom: 1rem;
        }
        .section-header {
            font-size: 1.8rem;
            color: #0D47A1;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1E88E5;
        }
        .metric-label {
            font-size: 1.2rem;
            color: #424242;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #f0f2f6;
            padding: 10px 20px;
            border-radius: 5px 5px 0 0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1E88E5;
            color: white;
        }
        div[data-testid="stSidebarNav"] li div a {
            margin-left: 1rem;
            padding: 1rem;
            width: 100%;
        }
        div[data-testid="stSidebarNav"] li div::before {
            content: "📄 ";
            margin-right: 0.5rem;
        }
        div[data-testid="metric-container"] {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 10px 15px;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        }
    </style>
    """

# 인증 확인 함수
def check_authentication():
    if not st.session_state.get('authenticated', False):
        st.error("로그인이 필요합니다. 메인 페이지로 이동하여 로그인해주세요.")
        st.stop()
    return True

# 샘플 데이터 생성 함수
@st.cache_data
def generate_sample_data(n=1000):
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=n//10, freq='D')
    
    data = []
    for _ in range(n):
        date = np.random.choice(dates)
        category = np.random.choice(['제품A', '제품B', '제품C', '제품D'])
        region = np.random.choice(['북부', '남부', '동부', '서부', '중부'])
        sales = np.random.randint(1000, 10000)
        profit = sales * np.random.uniform(0.1, 0.3)
        
        data.append({
            '날짜': date,
            '카테고리': category,
            '지역': region,
            '매출': sales,
            '이익': profit
        })
    
    return pd.DataFrame(data)

# 지역 좌표 데이터 변환 함수
def get_map_data(df):
    """판매 데이터에서 지도 시각화를 위한 데이터프레임 생성"""
    # 지역별 판매 집계
    region_sales = df.groupby('지역').agg(
        매출합계=('매출', 'sum'),
        이익합계=('이익', 'sum'),
        거래수=('매출', 'count')
    ).reset_index()
    
    # 지도 데이터 생성
    map_data = []
    for _, row in region_sales.iterrows():
        region = row['지역']
        if region in config.MAP_REGION_COORDINATES:
            coords = config.MAP_REGION_COORDINATES[region]
            map_data.append({
                'lat': coords['lat'],
                'lon': coords['lon'],
                'region': region,
                'sales': row['매출합계'],
                'profit': row['이익합계'],
                'count': row['거래수']
            })
    
    return pd.DataFrame(map_data)

# 시간 단위별 데이터 집계 함수
def aggregate_by_time(df, time_unit):
    """시간 단위별로 데이터 집계"""
    if time_unit == "일별":
        df['time_group'] = df['날짜'].dt.date
    elif time_unit == "주별":
        df['time_group'] = df['날짜'].dt.to_period('W').dt.start_time
    elif time_unit == "월별":
        df['time_group'] = df['날짜'].dt.to_period('M').dt.start_time
    else:
        df['time_group'] = df['날짜'].dt.to_period('Q').dt.start_time
    
    agg_data = df.groupby('time_group').agg(
        매출=('매출', 'sum'),
        이익=('이익', 'sum'),
        거래수=('매출', 'count')
    ).reset_index()
    
    return agg_data