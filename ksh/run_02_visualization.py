# -*- coding: utf-8 -*-
"""
02_초기시각화.ipynb 실행 스크립트
관광특구를 포함한 시각화 생성
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

print("="*70)
print("02_초기시각화.ipynb 실행 시작")
print("="*70)

# 데이터 로드
print("\n[Step 1] 데이터 로드")
merged = pd.read_csv('./통합_데이터.csv', encoding='utf-8-sig')
print(f"데이터: {merged.shape}")

# 연도/분기 파싱
merged['연도'] = (merged['기준_년분기_코드'] // 10).astype(int)
merged['분기'] = (merged['기준_년분기_코드'] % 10).astype(int)

# 색상 설정 (5개 상권)
order = ['골목상권', '발달상권', '전통시장', '관광특구', '미분류']
colors = ['#4E79A7', '#F28E2B', '#59A14F', '#E15759', '#B07AA1']
colors_map = dict(zip(order, colors))

# ============================================================================
# 그래프 1: 변수 분포
# ============================================================================
print("\n[Graph 1] 변수 분포")
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# 매출
axes[0].hist(merged['당월_매출_금액']/1e8, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
axes[0].axvline(merged['당월_매출_금액'].median()/1e8, color='red', linestyle='--', linewidth=2, label='중앙값')
axes[0].set_xlabel('매출 (억원)', fontsize=12)
axes[0].set_ylabel('빈도', fontsize=12)
axes[0].set_title('편의점 매출 분포', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].grid(alpha=0.3)

# 점포수
axes[1].hist(merged['점포_수'], bins=30, color='lightcoral', edgecolor='black', alpha=0.7)
axes[1].axvline(merged['점포_수'].median(), color='red', linestyle='--', linewidth=2, label='중앙값')
axes[1].set_xlabel('점포 수 (개)', fontsize=12)
axes[1].set_ylabel('빈도', fontsize=12)
axes[1].set_title('편의점 점포수 분포', fontsize=14, fontweight='bold')
axes[1].legend()
axes[1].grid(alpha=0.3)

# 유동인구
axes[2].hist(merged['총_유동인구_수']/1e6, bins=50, color='lightgreen', edgecolor='black', alpha=0.7)
axes[2].axvline(merged['총_유동인구_수'].median()/1e6, color='red', linestyle='--', linewidth=2, label='중앙값')
axes[2].set_xlabel('유동인구 (백만명)', fontsize=12)
axes[2].set_ylabel('빈도', fontsize=12)
axes[2].set_title('유동인구 분포', fontsize=14, fontweight='bold')
axes[2].legend()
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('./outputs/01_변수분포.png', dpi=300, bbox_inches='tight')
print("* Saved: 01_변수분포.png")
plt.close()

# ============================================================================
# 그래프 2: 연도별 트렌드
# ============================================================================
print("\n[Graph 2] 연도별 트렌드")
yearly_stats = merged.groupby('연도').agg({
    '당월_매출_금액': 'mean',
    '점포_수': 'mean',
    '총_유동인구_수': 'mean'
}).reset_index()

fig, axes = plt.subplots(3, 1, figsize=(10, 10))

# 매출
axes[0].plot(yearly_stats['연도'], yearly_stats['당월_매출_금액']/1e8, 
             marker='o', linewidth=2, markersize=8, color='#4E79A7')
axes[0].set_ylabel('평균 매출 (억원)', fontsize=12)
axes[0].set_title('연도별 평균 매출 추이', fontsize=14, fontweight='bold')
axes[0].grid(alpha=0.3)

# 점포수
axes[1].plot(yearly_stats['연도'], yearly_stats['점포_수'], 
             marker='s', linewidth=2, markersize=8, color='#F28E2B')
axes[1].set_ylabel('평균 점포수 (개)', fontsize=12)
axes[1].set_title('연도별 평균 점포수 추이', fontsize=14, fontweight='bold')
axes[1].grid(alpha=0.3)

# 유동인구
axes[2].plot(yearly_stats['연도'], yearly_stats['총_유동인구_수']/1e6, 
             marker='^', linewidth=2, markersize=8, color='#59A14F')
axes[2].set_xlabel('연도', fontsize=12)
axes[2].set_ylabel('평균 유동인구 (백만명)', fontsize=12)
axes[2].set_title('연도별 평균 유동인구 추이', fontsize=14, fontweight='bold')
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('./outputs/02_연도별_트렌드.png', dpi=300, bbox_inches='tight')
print("* Saved: 02_연도별_트렌드.png")
plt.close()

# ============================================================================
# 그래프 3: 상관관계 히트맵
# ============================================================================
print("\n[Graph 3] 상관관계")
corr_data = merged[['당월_매출_금액', '점포_수', '총_유동인구_수']].corr()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr_data, annot=True, fmt='.3f', cmap='coolwarm', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax)
ax.set_title('변수 간 상관관계', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('./outputs/03_상관관계.png', dpi=300, bbox_inches='tight')
print("* Saved: 03_상관관계.png")
plt.close()

# ============================================================================
# 그래프 4: 상권유형별 매출 박스플롯
# ============================================================================
print("\n[Graph 4] 상권유형별 매출")
fig, ax = plt.subplots(figsize=(12, 6))

type_data = merged[merged['주요_상권유형'].notna()].copy()
bp = ax.boxplot([type_data[type_data['주요_상권유형']==t]['당월_매출_금액']/1e8 
                 for t in order if t in type_data['주요_상권유형'].values],
                labels=[t for t in order if t in type_data['주요_상권유형'].values],
                patch_artist=True, showfliers=True)

# 색상 적용
for patch, color in zip(bp['boxes'], [colors_map[t] for t in order if t in type_data['주요_상권유형'].values]):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax.set_xlabel('상권유형', fontsize=12)
ax.set_ylabel('매출 (억원)', fontsize=12)
ax.set_title('상권유형별 매출 분포', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('./outputs/04_상권유형별_매출.png', dpi=300, bbox_inches='tight')
print("* Saved: 04_상권유형별_매출.png")
plt.close()

# ============================================================================
# 그래프 5: 산점도 (상권유형별)
# ============================================================================
print("\n[Graph 5] 산점도 - 상권유형별")
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 점포수 vs 매출
for sangwon in order:
    if sangwon in type_data['주요_상권유형'].values:
        subset = type_data[type_data['주요_상권유형'] == sangwon]
        axes[0].scatter(subset['점포_수'], subset['당월_매출_금액']/1e8,
                       label=sangwon, alpha=0.6, s=30, color=colors_map[sangwon])

axes[0].set_xlabel('점포수 (개)', fontsize=12)
axes[0].set_ylabel('매출 (억원)', fontsize=12)
axes[0].set_title('점포수 vs 매출 (상권유형별)', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].grid(alpha=0.3)

# 유동인구 vs 매출
for sangwon in order:
    if sangwon in type_data['주요_상권유형'].values:
        subset = type_data[type_data['주요_상권유형'] == sangwon]
        axes[1].scatter(subset['총_유동인구_수']/1e6, subset['당월_매출_금액']/1e8,
                       label=sangwon, alpha=0.6, s=30, color=colors_map[sangwon])

axes[1].set_xlabel('유동인구 (백만명)', fontsize=12)
axes[1].set_ylabel('매출 (억원)', fontsize=12)
axes[1].set_title('유동인구 vs 매출 (상권유형별)', fontsize=14, fontweight='bold')
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('./outputs/05_산점도_상권유형별.png', dpi=300, bbox_inches='tight')
print("* Saved: 05_산점도_상권유형별.png")
plt.close()

# ============================================================================
# 그래프 6: 분기별 매출 추이
# ============================================================================
print("\n[Graph 6] 분기별 매출 추이")
quarterly_stats = merged.groupby(['연도', '분기']).agg({
    '당월_매출_금액': 'mean'
}).reset_index()

fig, ax = plt.subplots(figsize=(12, 6))

for year in sorted(quarterly_stats['연도'].unique()):
    year_data = quarterly_stats[quarterly_stats['연도'] == year]
    ax.plot(year_data['분기'], year_data['당월_매출_금액']/1e8,
            marker='o', linewidth=2, markersize=8, label=f'{year}년')

ax.set_xlabel('분기', fontsize=12)
ax.set_ylabel('평균 매출 (억원)', fontsize=12)
ax.set_title('연도별 분기 매출 추이', fontsize=14, fontweight='bold')
ax.set_xticks([1, 2, 3, 4])
ax.set_xticklabels(['1Q', '2Q', '3Q', '4Q'])
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('./outputs/06_분기별_매출추이.png', dpi=300, bbox_inches='tight')
print("* Saved: 06_분기별_매출추이.png")
plt.close()

print("\n" + "="*70)
print("02_초기시각화 실행 완료 - 6개 그래프 생성")
print("="*70)
