#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys

# 파일 경로 설정
DATA_PATH = r'C:\Users\Administrator\Documents\workspace\budongsan3_project\ksh\통합_데이터.csv'
OUTPUT_DIR = r'C:\Users\Administrator\Documents\workspace\budongsan3_project\ksh\outputs'

# 데이터 로드
df = pd.read_csv(DATA_PATH, encoding='utf-8-sig')
df['연도'] = df['기준_년분기_코드'] // 10
df['분기'] = df['기준_년분기_코드'] % 10

print("="*70)
print("데이터 로드 완료")
print("="*70)
print(f"Shape: {df.shape}")
print(f"결측치: {df.isnull().sum().sum()}개")
print()

# ============================================================================
# 1. EDA_결과_상세.txt
# ============================================================================

content_detail = f"""======================================================================
편의점 데이터 EDA 상세 결과 (최종 업데이트)
======================================================================

[1] 데이터 개요
  - 최종 통합 데이터: {len(df):,}건
  - 분석 기간: 2022년 1분기 ~ 2025년 3분기
  - 대상: 서울시 편의점 (업종코드: CS300002)
  - 결측치: 0개 (100% 완전 데이터)

[2] 컬럼 구조
  총 {df.shape[1]}개 컬럼:
  - 기준_년분기_코드: 분기 식별자 (YYYYQ 형식)
  - 행정동_코드, 행정동_코드_명: 행정동 식별 정보
  - 당월_매출_금액, 당월_매출_건수: 매출 정보
  - 점포_수, 프랜차이즈_점포_수: 점포 현황
  - 개업_점포_수, 폐업_점포_수: 변동 현황
  - 총_유동인구_수: 유동인구 정보
  - 주요_상권유형: 상권 분류 (골목/발달/전통시장/미분류)
  - 연도, 분기: 파생 변수

[3] 기초 통계량
======================================================================

"""

# 기초 통계 계산
stats = df[['당월_매출_금액', '점포_수', '총_유동인구_수']].describe()

content_detail += "[당월_매출_금액 (원)]\n"
content_detail += f"  - 평균: {stats.loc['mean', '당월_매출_금액']:,.0f}\n"
content_detail += f"  - 표준편차: {stats.loc['std', '당월_매출_금액']:,.0f}\n"
content_detail += f"  - 최소: {stats.loc['min', '당월_매출_금액']:,.0f}\n"
content_detail += f"  - 25%: {stats.loc['25%', '당월_매출_금액']:,.0f}\n"
content_detail += f"  - 50% (중앙값): {stats.loc['50%', '당월_매출_금액']:,.0f}\n"
content_detail += f"  - 75%: {stats.loc['75%', '당월_매출_금액']:,.0f}\n"
content_detail += f"  - 최대: {stats.loc['max', '당월_매출_금액']:,.0f}\n"
content_detail += f"\n해석: 평균 27.1억원, 중앙값 17.2억원으로 평균이 더 높음\n"
content_detail += f"     → 일부 고매출 지역(발달상권)이 평균을 끌어올림\n"
content_detail += f"     → 중앙값이 더 대표적인 편의점 매출 수준\n\n"

content_detail += "[점포_수]\n"
content_detail += f"  - 평균: {stats.loc['mean', '점포_수']:.2f}\n"
content_detail += f"  - 표준편차: {stats.loc['std', '점포_수']:.2f}\n"
content_detail += f"  - 최소: {stats.loc['min', '점포_수']:.0f}\n"
content_detail += f"  - 25%: {stats.loc['25%', '점포_수']:.0f}\n"
content_detail += f"  - 50% (중앙값): {stats.loc['50%', '점포_수']:.0f}\n"
content_detail += f"  - 75%: {stats.loc['75%', '점포_수']:.0f}\n"
content_detail += f"  - 최대: {stats.loc['max', '점포_수']:.0f}\n"
content_detail += f"\n해석: 행정동당 평균 6.2개 편의점\n"
content_detail += f"     → 최대 51개(역삼1동)까지 편차가 큼\n"
content_detail += f"     → 14개 행정동은 점포 0개 (매출은 있음 = 단기 영업)\n\n"

content_detail += "[총_유동인구_수]\n"
content_detail += f"  - 평균: {stats.loc['mean', '총_유동인구_수']:,.0f}\n"
content_detail += f"  - 표준편차: {stats.loc['std', '총_유동인구_수']:,.0f}\n"
content_detail += f"  - 최소: {stats.loc['min', '총_유동인구_수']:,.0f}\n"
content_detail += f"  - 25%: {stats.loc['25%', '총_유동인구_수']:,.0f}\n"
content_detail += f"  - 50% (중앙값): {stats.loc['50%', '총_유동인구_수']:,.0f}\n"
content_detail += f"  - 75%: {stats.loc['75%', '총_유동인구_수']:,.0f}\n"
content_detail += f"  - 최대: {stats.loc['max', '총_유동인구_수']:,.0f}\n"
content_detail += f"\n해석: 분기당 평균 562만명의 유동인구\n"
content_detail += f"     → 중앙값 526만명으로 비교적 고른 분포\n\n"

# 상권유형별 통계
content_detail += "\n[4] 상권유형별 분포 및 특성\n"
content_detail += "======================================================================\n\n"

for area_type in ['골목상권', '발달상권', '전통시장', '미분류']:
    subset = df[df['주요_상권유형'] == area_type]
    count = len(subset)
    pct = count / len(df) * 100
    
    content_detail += f"[{area_type}]\n"
    content_detail += f"  - 건수: {count:,}개 ({pct:.1f}%)\n"
    content_detail += f"  - 평균 매출: {subset['당월_매출_금액'].mean():,.0f}원 ({subset['당월_매출_금액'].mean()/1e8:.2f}억)\n"
    content_detail += f"  - 중앙값 매출: {subset['당월_매출_금액'].median():,.0f}원 ({subset['당월_매출_금액'].median()/1e8:.2f}억)\n"
    content_detail += f"  - 표준편차: {subset['당월_매출_금액'].std():,.0f}원\n"
    content_detail += f"  - 평균 점포수: {subset['점포_수'].mean():.1f}개\n"
    content_detail += f"  - 평균 유동인구: {subset['총_유동인구_수'].mean():,.0f}명 ({subset['총_유동인구_수'].mean()/1e6:.2f}백만)\n"
    
    # 해석 추가
    if area_type == '골목상권':
        content_detail += f"\n  해석: 전체의 85%를 차지하는 주요 상권 유형\n"
        content_detail += f"       평균 매출 25.4억원으로 안정적인 주거지역 특성\n"
        content_detail += f"       유동인구가 가장 많음 (580만명) → 생활밀착형\n"
    elif area_type == '발달상권':
        content_detail += f"\n  해석: 평균 매출 65.8억원으로 2.6배 높음\n"
        content_detail += f"       점포수 12개로 2배 → 상권 집중도가 높음\n"
        content_detail += f"       강남/여의도 등 업무/상업 중심지\n"
    elif area_type == '전통시장':
        content_detail += f"\n  해석: 평균 매출 28.5억원으로 골목상권과 유사\n"
        content_detail += f"       점포수 4개로 적음 → 전통시장 내 소수 편의점\n"
        content_detail += f"       유동인구도 적음 → 시장 이용객 중심\n"
    elif area_type == '미분류':
        content_detail += f"\n  해석: 공식 상권 분류 없는 주거지역\n"
        content_detail += f"       평균 매출 13.3억원으로 가장 낮음\n"
        content_detail += f"       유동인구 279만명 → 인구밀도가 낮은 지역\n"
        content_detail += f"       점포 3.4개 → 소규모 상권\n"
    
    content_detail += "\n\n"

# 파일 저장 (처음 30줄만)
output_path_detail = f"{OUTPUT_DIR}/EDA_결과_상세.txt"
with open(output_path_detail, 'w', encoding='utf-8') as f:
    f.write(content_detail)

print(f"✓ EDA_결과_상세.txt 생성 시작...")
