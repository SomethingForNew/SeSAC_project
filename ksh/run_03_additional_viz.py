# -*- coding: utf-8 -*-
"""
03_심층분석 추가 시각화
- VIF 다중공선성
- 회귀계수 영향력
- 상권유형 매출비교
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

print("="*70)
print("03_심층분석 추가 시각화 생성")
print("="*70)

# ============================================================================
# 데이터 로드 및 회귀분석
# ============================================================================
print("\n[Step 1] 데이터 로드 및 회귀분석")
merged = pd.read_csv('./통합_데이터.csv', encoding='utf-8-sig')

# 더미변수 생성
dummies = pd.get_dummies(merged['주요_상권유형'], drop_first=False, dtype=float)
dummies = dummies.drop('골목상권', axis=1)
merged_reg = pd.concat([merged, dummies], axis=1)

# 회귀분석
X = merged_reg[['점포_수', '총_유동인구_수', '관광특구', '발달상권', '전통시장', '미분류']].astype(float)
y = merged_reg['당월_매출_금액'].astype(float)
X_with_const = sm.add_constant(X)
model = sm.OLS(y, X_with_const).fit()

print("회귀분석 완료")
print(f"R-squared: {model.rsquared:.4f}")

# ============================================================================
# 그래프 1: VIF 다중공선성
# ============================================================================
print("\n[Graph 1] VIF 다중공선성")

# 간단한 VIF 계산 (상관계수 기반)
corr_matrix = X.corr()
vif_approx = []
for col in X.columns:
    other_cols = [c for c in X.columns if c != col]
    r_squared = corr_matrix.loc[col, other_cols].abs().max()
    vif = 1 / (1 - r_squared**2) if r_squared < 0.99 else 999
    vif_approx.append({'Variable': col, 'VIF': vif})

vif_df = pd.DataFrame(vif_approx)

fig, ax = plt.subplots(figsize=(10, 6))
colors = ['green' if v < 5 else ('orange' if v < 10 else 'red') for v in vif_df['VIF']]
bars = ax.barh(vif_df['Variable'], vif_df['VIF'], color=colors, alpha=0.7)

# VIF 값 표시
for i, (var, vif) in enumerate(zip(vif_df['Variable'], vif_df['VIF'])):
    ax.text(vif + 0.1, i, f'{vif:.2f}', va='center', fontsize=11, fontweight='bold')

ax.axvline(5, color='orange', linestyle='--', linewidth=2, label='VIF=5 (주의)')
ax.axvline(10, color='red', linestyle='--', linewidth=2, label='VIF=10 (심각)')
ax.set_xlabel('VIF 값', fontsize=12)
ax.set_ylabel('변수', fontsize=12)
ax.set_title('VIF 분석 - 다중공선성 검증', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('./outputs/09_VIF_다중공선성.png', dpi=300, bbox_inches='tight')
print("* Saved: 09_VIF_다중공선성.png")
plt.close()

# ============================================================================
# 그래프 2: 회귀계수 영향력
# ============================================================================
print("\n[Graph 2] 회귀계수 영향력")

# 계수 데이터 준비 (절편 제외)
coef_data = pd.DataFrame({
    'Variable': model.params.index[1:],  # 절편 제외
    'Coefficient': model.params.values[1:],
    'P-value': model.pvalues.values[1:]
})

# 정렬
coef_data = coef_data.sort_values('Coefficient', ascending=True)

# 유의성에 따른 색상
colors = ['red' if p < 0.001 else ('orange' if p < 0.01 else 'gray') 
          for p in coef_data['P-value']]

fig, ax = plt.subplots(figsize=(10, 8))
bars = ax.barh(coef_data['Variable'], coef_data['Coefficient']/1e8, color=colors, alpha=0.7)

# 계수 값 표시
for i, (var, coef) in enumerate(zip(coef_data['Variable'], coef_data['Coefficient'])):
    x_pos = coef/1e8 + (5 if coef > 0 else -5)
    ax.text(x_pos, i, f'{coef/1e8:.1f}억', va='center', fontsize=10, fontweight='bold')

ax.axvline(0, color='black', linewidth=1)
ax.set_xlabel('회귀계수 (억원)', fontsize=12)
ax.set_ylabel('변수', fontsize=12)
ax.set_title('회귀계수 영향력 분석', fontsize=14, fontweight='bold')

# 범례
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='red', alpha=0.7, label='p < 0.001 (***) - 매우 유의'),
    Patch(facecolor='orange', alpha=0.7, label='p < 0.01 (**) - 유의'),
    Patch(facecolor='gray', alpha=0.7, label='p ≥ 0.01 - 약한 유의성')
]
ax.legend(handles=legend_elements, loc='lower right')
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('./outputs/07_회귀계수_영향력.png', dpi=300, bbox_inches='tight')
print("* Saved: 07_회귀계수_영향력.png")
plt.close()

# ============================================================================
# 그래프 3: 상권유형별 매출 비교 (평균 + 오차막대)
# ============================================================================
print("\n[Graph 3] 상권유형별 매출 비교")

# 상권별 통계
sangwon_stats = merged.groupby('주요_상권유형').agg({
    '당월_매출_금액': ['mean', 'std', 'count']
}).reset_index()
sangwon_stats.columns = ['상권유형', '평균', '표준편차', '개수']
sangwon_stats['표준오차'] = sangwon_stats['표준편차'] / np.sqrt(sangwon_stats['개수'])

# 정렬 (매출 높은 순)
sangwon_stats = sangwon_stats.sort_values('평균', ascending=True)

# 색상 매핑
color_map = {
    '골목상권': '#4E79A7',
    '발달상권': '#F28E2B',
    '전통시장': '#59A14F',
    '관광특구': '#E15759',
    '미분류': '#B07AA1'
}
colors = [color_map[s] for s in sangwon_stats['상권유형']]

fig, ax = plt.subplots(figsize=(10, 8))

# 막대 그래프
bars = ax.barh(sangwon_stats['상권유형'], sangwon_stats['평균']/1e8, 
               color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

# 오차막대 (표준오차)
ax.errorbar(sangwon_stats['평균']/1e8, range(len(sangwon_stats)),
            xerr=sangwon_stats['표준오차']/1e8, fmt='none', 
            color='black', capsize=5, capthick=2, alpha=0.5)

# 값 표시
for i, (sangwon, mean, count) in enumerate(zip(sangwon_stats['상권유형'], 
                                                 sangwon_stats['평균'], 
                                                 sangwon_stats['개수'])):
    ax.text(mean/1e8 + 3, i, f'{mean/1e8:.1f}억\n(n={int(count)})', 
            va='center', fontsize=11, fontweight='bold')

ax.set_xlabel('평균 매출 (억원)', fontsize=12)
ax.set_ylabel('상권유형', fontsize=12)
ax.set_title('상권유형별 평균 매출 비교 (오차막대: 표준오차)', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('./outputs/10_상권유형_매출비교.png', dpi=300, bbox_inches='tight')
print("* Saved: 10_상권유형_매출비교.png")
plt.close()

# ============================================================================
# 그래프 4: 잔차 분석 (상세)
# ============================================================================
print("\n[Graph 4] 잔차 분석 (상세)")

y_pred = model.predict(X_with_const)
residuals = y - y_pred
standardized_residuals = (residuals - residuals.mean()) / residuals.std()

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# 1. 잔차 vs 예측값
axes[0, 0].scatter(y_pred/1e8, residuals/1e8, alpha=0.3, s=10)
axes[0, 0].axhline(0, color='red', linestyle='--', linewidth=2)
axes[0, 0].set_xlabel('예측 매출 (억원)', fontsize=11)
axes[0, 0].set_ylabel('잔차 (억원)', fontsize=11)
axes[0, 0].set_title('잔차 vs 예측값\n(등분산성 검정)', fontsize=12, fontweight='bold')
axes[0, 0].grid(alpha=0.3)

# 2. 표준화 잔차 vs 예측값
axes[0, 1].scatter(y_pred/1e8, standardized_residuals, alpha=0.3, s=10)
axes[0, 1].axhline(0, color='red', linestyle='--', linewidth=2)
axes[0, 1].axhline(2, color='orange', linestyle='--', linewidth=1, alpha=0.5)
axes[0, 1].axhline(-2, color='orange', linestyle='--', linewidth=1, alpha=0.5)
axes[0, 1].set_xlabel('예측 매출 (억원)', fontsize=11)
axes[0, 1].set_ylabel('표준화 잔차', fontsize=11)
axes[0, 1].set_title('표준화 잔차\n(이상치 검출: |z|>2)', fontsize=12, fontweight='bold')
axes[0, 1].grid(alpha=0.3)

# 3. 잔차 히스토그램
axes[0, 2].hist(residuals/1e8, bins=50, edgecolor='black', alpha=0.7, color='skyblue')
axes[0, 2].axvline(0, color='red', linestyle='--', linewidth=2)
axes[0, 2].set_xlabel('잔차 (억원)', fontsize=11)
axes[0, 2].set_ylabel('빈도', fontsize=11)
axes[0, 2].set_title('잔차 분포\n(정규성 검정)', fontsize=12, fontweight='bold')
axes[0, 2].grid(alpha=0.3)

# 4. Q-Q Plot
sm.qqplot(residuals, line='s', ax=axes[1, 0])
axes[1, 0].set_title('Q-Q Plot\n(정규성 검정)', fontsize=12, fontweight='bold')
axes[1, 0].grid(alpha=0.3)

# 5. 실제 vs 예측
axes[1, 1].scatter(y/1e8, y_pred/1e8, alpha=0.3, s=10)
axes[1, 1].plot([y.min()/1e8, y.max()/1e8], [y.min()/1e8, y.max()/1e8], 
                'r--', linewidth=2, label='Perfect Fit')
axes[1, 1].set_xlabel('실제 매출 (억원)', fontsize=11)
axes[1, 1].set_ylabel('예측 매출 (억원)', fontsize=11)
axes[1, 1].set_title('실제 vs 예측\n(R²=' + f'{model.rsquared:.3f})', fontsize=12, fontweight='bold')
axes[1, 1].legend()
axes[1, 1].grid(alpha=0.3)

# 6. 잔차 vs 점포수
axes[1, 2].scatter(merged_reg['점포_수'], residuals/1e8, alpha=0.3, s=10)
axes[1, 2].axhline(0, color='red', linestyle='--', linewidth=2)
axes[1, 2].set_xlabel('점포수 (개)', fontsize=11)
axes[1, 2].set_ylabel('잔차 (억원)', fontsize=11)
axes[1, 2].set_title('잔차 vs 점포수\n(선형성 검정)', fontsize=12, fontweight='bold')
axes[1, 2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('./outputs/08_잔차분석.png', dpi=300, bbox_inches='tight')
print("* Saved: 08_잔차분석.png")
plt.close()

print("\n" + "="*70)
print("추가 시각화 생성 완료 - 4개 그래프")
print("="*70)
print("\n생성된 파일:")
print("  - 07_회귀계수_영향력.png")
print("  - 08_잔차분석.png")
print("  - 09_VIF_다중공선성.png")
print("  - 10_상권유형_매출비교.png")
