# -*- coding: utf-8 -*-
"""
01_EDA_분석.ipynb 실행 스크립트
관광특구를 포함한 EDA 분석 실행
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

print("="*70)
print("01_EDA_분석.ipynb 실행 시작")
print("="*70)

# ============================================================================
# 1. 데이터 로드
# ============================================================================
print("\n[Step 1] 데이터 로드")
store_df = pd.read_csv('../mey/convenience_data/stores.csv', encoding='utf-8-sig')
sales_df = pd.read_csv('../mey/convenience_data/sales.csv', encoding='utf-8-sig')
pop_df = pd.read_csv('../mey/convenience_data/population.csv', encoding='utf-8-sig')
area_df = pd.read_csv('../mey/convenience_data/districts.csv', encoding='cp949')

print(f"점포: {store_df.shape}")
print(f"매출: {sales_df.shape}")
print(f"유동인구: {pop_df.shape}")
print(f"상권영역: {area_df.shape}")

# ============================================================================
# 2. 인코딩 수정
# ============================================================================
print("\n[Step 2] 인코딩 수정")
store_df['행정동_코드_명'] = store_df['행정동_코드_명'].str.replace('?', '·')
sales_df['행정동_코드_명'] = sales_df['행정동_코드_명'].str.replace('?', '·')
pop_df['행정동_코드_명'] = pop_df['행정동_코드_명'].str.replace('?', '·')
area_df['행정동_코드_명'] = area_df['행정동_코드_명'].str.replace('?', '·')
print("* Done")

# ============================================================================
# 3. 편의점 필터링
# ============================================================================
print("\n[Step 3] 편의점 데이터 필터링")
cvs_store = store_df[store_df['서비스_업종_코드'] == 'CS300002'].copy()
cvs_sales = sales_df[sales_df['서비스_업종_코드'] == 'CS300002'].copy()
pop_df_filtered = pop_df[pop_df['기준_년분기_코드'] >= 20221].copy()
print(f"편의점 점포: {len(cvs_store)}건")
print(f"편의점 매출: {len(cvs_sales)}건")

# ============================================================================
# 4. 상권유형 매핑 (관광특구 우선순위)
# ============================================================================
print("\n[Step 4] 상권유형 매핑 (관광특구 우선순위 적용)")
area_type_map = {'A': '골목상권', 'D': '발달상권', 'R': '전통시장', 'U': '관광특구'}
area_df['상권유형'] = area_df['상권_구분_코드'].map(area_type_map)

def get_main_sangwon(sangwon_list):
    """관광특구가 있으면 최우선, 없으면 최빈값"""
    if '관광특구' in sangwon_list:
        return '관광특구'
    return Counter(sangwon_list).most_common(1)[0][0]

area_by_dong = area_df.groupby('행정동_코드')['상권유형'].agg(list).reset_index()
area_by_dong['주요_상권유형'] = area_by_dong['상권유형'].apply(get_main_sangwon)
area_by_dong = area_by_dong[['행정동_코드', '주요_상권유형']]

print("\n[상권유형별 행정동 수]")
print(area_df.groupby('상권유형')['행정동_코드'].nunique())

# ============================================================================
# 5. 데이터 집계
# ============================================================================
print("\n[Step 5] 데이터 집계")
cvs_store_agg = cvs_store.groupby(['기준_년분기_코드', '행정동_코드', '행정동_코드_명']).agg({
    '점포_수': 'sum',
    '프랜차이즈_점포_수': 'sum',
    '개업_점포_수': 'sum',
    '폐업_점포_수': 'sum'
}).reset_index()

cvs_sales_agg = cvs_sales.groupby(['기준_년분기_코드', '행정동_코드', '행정동_코드_명']).agg({
    '당월_매출_금액': 'sum',
    '당월_매출_건수': 'sum'
}).reset_index()

pop_agg = pop_df_filtered.groupby(['기준_년분기_코드', '행정동_코드', '행정동_코드_명']).agg({
    '총_유동인구_수': 'sum'
}).reset_index()

# ============================================================================
# 6. 데이터 병합
# ============================================================================
print("\n[Step 6] 데이터 병합")
merged = cvs_sales_agg.merge(cvs_store_agg, on=['기준_년분기_코드', '행정동_코드', '행정동_코드_명'], how='left')
merged = merged.merge(pop_agg, on=['기준_년분기_코드', '행정동_코드', '행정동_코드_명'], how='left')
merged = merged.merge(area_by_dong, on='행정동_코드', how='left')

print(f"병합 후: {merged.shape}")

# ============================================================================
# 7. 미분류 처리
# ============================================================================
print("\n[Step 7] 미분류 처리")
missing_count = merged['주요_상권유형'].isnull().sum()
print(f"결측 개수: {missing_count}개")

if missing_count > 0:
    merged['주요_상권유형'] = merged['주요_상권유형'].fillna('미분류')
    print("* Created 'Unclassified' category")

# ============================================================================
# 8. 최종 데이터 저장
# ============================================================================
print("\n[Step 8] 최종 데이터 저장")
merged.to_csv('./통합_데이터.csv', index=False, encoding='utf-8-sig')
print("* Saved: 통합_데이터.csv")

print("\n상권유형 분포:")
print(merged['주요_상권유형'].value_counts().sort_index())

print("\n" + "="*70)
print("01_EDA_분석 실행 완료")
print("="*70)
