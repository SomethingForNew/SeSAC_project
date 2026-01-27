# -*- coding: utf-8 -*-
"""
01_전처리 실행 스크립트
분석데이터.csv 파일 생성
"""
import pandas as pd
import numpy as np
from collections import Counter
import warnings
import sys

warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("서울시 편의점 매출 결정요인 분석 - 데이터 전처리")
print("=" * 60)

# 데이터 로드
print("\n[1] 데이터 로드")
sales_df = pd.read_csv('../../data/processed/sales.csv', encoding='utf-8-sig')
store_df = pd.read_csv('../../data/processed/stores.csv', encoding='utf-8-sig')
pop_df = pd.read_csv('../../data/processed/population.csv', encoding='utf-8-sig')
area_df = pd.read_csv('../../data/processed/districts.csv', encoding='cp949')

print(f"  매출: {sales_df.shape[0]:,}건")
print(f"  점포: {store_df.shape[0]:,}건")
print(f"  유동인구: {pop_df.shape[0]:,}건")
print(f"  상권영역: {area_df.shape[0]:,}건")

# 편의점 필터링 및 기간 설정
print("\n[2] 편의점 필터링 (2022Q1~2025Q3)")
cvs_sales = sales_df[sales_df['서비스_업종_코드'] == 'CS300002'].copy()
cvs_store = store_df[store_df['서비스_업종_코드'] == 'CS300002'].copy()

cvs_sales = cvs_sales[(cvs_sales['기준_년분기_코드'] >= 20221) & (cvs_sales['기준_년분기_코드'] <= 20253)]
cvs_store = cvs_store[(cvs_store['기준_년분기_코드'] >= 20221) & (cvs_store['기준_년분기_코드'] <= 20253)]
pop_df = pop_df[(pop_df['기준_년분기_코드'] >= 20221) & (pop_df['기준_년분기_코드'] <= 20253)]

print(f"  편의점 매출: {len(cvs_sales):,}건")
print(f"  편의점 점포: {len(cvs_store):,}건")
print(f"  유동인구: {len(pop_df):,}건")

# 인코딩 수정
print("\n[3] 인코딩 수정 ('?' → '·')")
cvs_sales['행정동_코드_명'] = cvs_sales['행정동_코드_명'].str.replace('?', '·')
cvs_store['행정동_코드_명'] = cvs_store['행정동_코드_명'].str.replace('?', '·')
pop_df['행정동_코드_명'] = pop_df['행정동_코드_명'].str.replace('?', '·')
area_df['행정동_코드_명'] = area_df['행정동_코드_명'].str.replace('?', '·')

# 상권유형 매핑
print("\n[4] 상권유형 매핑")
type_map = {'A': '골목상권', 'D': '발달상권', 'R': '전통시장', 'U': '관광특구'}
area_df['상권유형'] = area_df['상권_구분_코드'].map(type_map)

def get_main_type(types):
    if '관광특구' in types:
        return '관광특구'
    return Counter(types).most_common(1)[0][0]

area_by_dong = area_df.groupby('행정동_코드')['상권유형'].agg(list).reset_index()
area_by_dong['주요_상권유형'] = area_by_dong['상권유형'].apply(get_main_type)
area_by_dong = area_by_dong[['행정동_코드', '주요_상권유형']]
print(f"  행정동별 상권유형: {len(area_by_dong)}개")

# 데이터 집계 및 병합
print("\n[5] 데이터 집계 및 병합")
key_cols = ['기준_년분기_코드', '행정동_코드', '행정동_코드_명']

sales_agg = cvs_sales.groupby(key_cols).agg({'당월_매출_금액': 'sum', '당월_매출_건수': 'sum'}).reset_index()
store_agg = cvs_store.groupby(key_cols).agg({'점포_수': 'sum'}).reset_index()
pop_agg = pop_df.groupby(key_cols).agg({'총_유동인구_수': 'sum'}).reset_index()

df = sales_agg.merge(store_agg, on=key_cols, how='left')
df = df.merge(pop_agg, on=key_cols, how='left')
df = df.merge(area_by_dong, on='행정동_코드', how='left')

df['연도'] = df['기준_년분기_코드'] // 10
df['분기'] = df['기준_년분기_코드'] % 10

# 결측치 처리
print("\n[6] 결측치 처리")
n_missing = df['주요_상권유형'].isnull().sum()
df['주요_상권유형'] = df['주요_상권유형'].fillna('미분류')
print(f"  상권유형 결측 {n_missing}건 → '미분류'")

# 검증
print("\n[7] 최종 데이터 검증")
print(f"  총 데이터: {len(df):,}건")
print(f"  기간: {df['기준_년분기_코드'].min()} ~ {df['기준_년분기_코드'].max()}")
print(f"  행정동: {df['행정동_코드'].nunique()}개")
print(f"  상권유형 분포:")
for t, cnt in df['주요_상권유형'].value_counts().items():
    print(f"    {t}: {cnt}건 ({cnt/len(df)*100:.1f}%)")

# 저장
df.to_csv('./분석데이터.csv', encoding='utf-8-sig', index=False)

print("\n" + "=" * 60)
print("전처리 완료!")
print("=" * 60)
print(f"저장: ./분석데이터.csv ({df.shape})")
