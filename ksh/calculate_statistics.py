# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np

# Load data
merged = pd.read_csv('./통합_데이터.csv', encoding='utf-8-sig')

print("="*70)
print("STATISTICS FOR UPDATED DATA")
print("="*70)

# 1. Basic Info
print(f"\n[1] Data Shape: {merged.shape}")
print(f"Missing Values: {merged.isnull().sum().sum()}")

# 2. District Type Distribution
print("\n[2] District Type Distribution:")
for dtype, count in merged['주요_상권유형'].value_counts().sort_index().items():
    ratio = count / len(merged) * 100
    print(f"  {dtype}: {count:,} ({ratio:.2f}%)")

# 3. Statistics by District Type
print("\n[3] Statistics by District Type:")
for dtype in ['골목상권', '발달상권', '전통시장', '관광특구', '미분류']:
    if dtype in merged['주요_상권유형'].values:
        subset = merged[merged['주요_상권유형'] == dtype]
        print(f"\n[{dtype}]")
        print(f"  Count: {len(subset):,}")
        print(f"  Avg Sales: {subset['당월_매출_금액'].mean():,.0f}")
        print(f"  Med Sales: {subset['당월_매출_금액'].median():,.0f}")
        print(f"  Std Sales: {subset['당월_매출_금액'].std():,.0f}")
        print(f"  Avg Stores: {subset['점포_수'].mean():.1f}")
        print(f"  Avg Population: {subset['총_유동인구_수'].mean():,.0f}")

# 4. Overall Statistics
print("\n[4] Overall Statistics:")
print(f"  Avg Sales: {merged['당월_매출_금액'].mean():,.0f}")
print(f"  Med Sales: {merged['당월_매출_금액'].median():,.0f}")
print(f"  Min Sales: {merged['당월_매출_금액'].min():,.0f}")
print(f"  Max Sales: {merged['당월_매출_금액'].max():,.0f}")

print(f"\n  Avg Stores: {merged['점포_수'].mean():.2f}")
print(f"  Med Stores: {merged['점포_수'].median():.0f}")
print(f"  Min Stores: {merged['점포_수'].min():.0f}")
print(f"  Max Stores: {merged['점포_수'].max():.0f}")

print(f"\n  Avg Population: {merged['총_유동인구_수'].mean():,.0f}")
print(f"  Med Population: {merged['총_유동인구_수'].median():,.0f}")
print(f"  Min Population: {merged['총_유동인구_수'].min():,.0f}")
print(f"  Max Population: {merged['총_유동인구_수'].max():,.0f}")

# 5. Correlation
print("\n[5] Correlation Matrix:")
corr_cols = ['당월_매출_금액', '점포_수', '총_유동인구_수']
corr_matrix = merged[corr_cols].corr()
print(corr_matrix)

# 6. Year Statistics
merged['연도'] = (merged['기준_년분기_코드'] // 10).astype(int)
print("\n[6] Statistics by Year:")
for year in sorted(merged['연도'].unique()):
    subset = merged[merged['연도'] == year]
    print(f"\n{year}:")
    print(f"  Avg Sales: {subset['당월_매출_금액'].mean():,.0f}")
    print(f"  Avg Stores: {subset['점포_수'].mean():.2f}")
    print(f"  Avg Population: {subset['총_유동인구_수'].mean():,.0f}")

print("\n" + "="*70)
print("DONE")
print("="*70)
