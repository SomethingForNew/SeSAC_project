# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
from collections import Counter

print("="*70)
print("Run EDA with Tourism District")
print("="*70)

# 1. Load Data
print("\n[Step 1] Load Data")
store_df = pd.read_csv('../mey/convenience_data/stores.csv', encoding='utf-8-sig')
sales_df = pd.read_csv('../mey/convenience_data/sales.csv', encoding='utf-8-sig')
pop_df = pd.read_csv('../mey/convenience_data/population.csv', encoding='utf-8-sig')
area_df = pd.read_csv('../mey/convenience_data/districts.csv', encoding='cp949')

print(f"Store: {store_df.shape}")
print(f"Sales: {sales_df.shape}")
print(f"Population: {pop_df.shape}")
print(f"Districts: {area_df.shape}")

# 2. Fix Encoding
print("\n[Step 2] Fix Encoding ('?' to middle dot)")
store_df['행정동_코드_명'] = store_df['행정동_코드_명'].str.replace('?', '·')
sales_df['행정동_코드_명'] = sales_df['행정동_코드_명'].str.replace('?', '·')
pop_df['행정동_코드_명'] = pop_df['행정동_코드_명'].str.replace('?', '·')
area_df['행정동_코드_명'] = area_df['행정동_코드_명'].str.replace('?', '·')
print("* Done")

# 3. Filter Convenience Store
print("\n[Step 3] Filter CVS Data")
cvs_store = store_df[store_df['서비스_업종_코드'] == 'CS300002'].copy()
cvs_sales = sales_df[sales_df['서비스_업종_코드'] == 'CS300002'].copy()
pop_df_filtered = pop_df[pop_df['기준_년분기_코드'] >= 20221].copy()
print(f"CVS Store: {len(cvs_store)}")
print(f"CVS Sales: {len(cvs_sales)}")

# 4. Map District Types (Tourism Priority)
print("\n[Step 4] Map District Types (Tourism Priority)")
area_type_map = {'A': '골목상권', 'D': '발달상권', 'R': '전통시장', 'U': '관광특구'}
area_df['상권유형'] = area_df['상권_구분_코드'].map(area_type_map)

def get_main_sangwon(sangwon_list):
    if '관광특구' in sangwon_list:
        return '관광특구'
    return Counter(sangwon_list).most_common(1)[0][0]

area_by_dong = area_df.groupby('행정동_코드')['상권유형'].agg(list).reset_index()
area_by_dong['주요_상권유형'] = area_by_dong['상권유형'].apply(get_main_sangwon)
area_by_dong = area_by_dong[['행정동_코드', '주요_상권유형']]

print("\n[District Type Count]")
print(area_df.groupby('상권유형')['행정동_코드'].nunique())

# 5. Aggregate
print("\n[Step 5] Aggregate Data")
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

# 6. Merge
print("\n[Step 6] Merge Data")
merged = cvs_sales_agg.merge(cvs_store_agg, on=['기준_년분기_코드', '행정동_코드', '행정동_코드_명'], how='left')
merged = merged.merge(pop_agg, on=['기준_년분기_코드', '행정동_코드', '행정동_코드_명'], how='left')
merged = merged.merge(area_by_dong, on='행정동_코드', how='left')

print(f"After merge: {merged.shape}")

# 7. Handle Missing (Unclassified)
print("\n[Step 7] Handle Missing Values")
missing_count = merged['주요_상권유형'].isnull().sum()
print(f"Missing count: {missing_count}")

if missing_count > 0:
    merged['주요_상권유형'] = merged['주요_상권유형'].fillna('미분류')
    print("* Created 'Unclassified' category")

# 8. Check Results
print("\n[Step 8] Final Results")
print("\nDistrict Type Distribution:")
print(merged['주요_상권유형'].value_counts().sort_index())

print("\nMissing Values:")
print(merged.isnull().sum())

# 9. Save
print("\n[Step 9] Save Merged Data")
merged.to_csv('./통합_데이터.csv', index=False, encoding='utf-8-sig')
print("* Saved: 통합_데이터.csv")

print("\n" + "="*70)
print("DONE: EDA with Tourism District")
print("="*70)
