# -*- coding: utf-8 -*-
"""
03_심층분석.ipynb 실행 스크립트 (수정)
관광특구를 포함한 회귀분석
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

print("="*70)
print("03_심층분석.ipynb 실행 시작 (회귀분석)")
print("="*70)

# ============================================================================
# 1. 데이터 로드
# ============================================================================
print("\n[Step 1] 데이터 로드")
merged = pd.read_csv('./통합_데이터.csv', encoding='utf-8-sig')
print(f"데이터: {merged.shape}")
print(f"결측치: {merged.isnull().sum().sum()}")

# ============================================================================
# 2. 더미변수 생성
# ============================================================================
print("\n[Step 2] 더미변수 생성")
# 골목상권을 기준(baseline)으로 설정
dummies = pd.get_dummies(merged['주요_상권유형'], drop_first=False, dtype=float)
dummies = dummies.drop('골목상권', axis=1)  # 골목상권 제거 (기준 범주)

merged_reg = pd.concat([merged, dummies], axis=1)
print(f"더미변수: {list(dummies.columns)}")

# ============================================================================
# 3. 회귀분석 데이터 준비
# ============================================================================
print("\n[Step 3] 회귀분석 데이터 준비")
X = merged_reg[['점포_수', '총_유동인구_수', '관광특구', '발달상권', '전통시장', '미분류']].astype(float)
y = merged_reg['당월_매출_금액'].astype(float)

print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")
print(f"X dtypes:\n{X.dtypes}")

# ============================================================================
# 4. VIF 분석 (간소화)
# ============================================================================
print("\n[Step 4] VIF 분석 (다중공선성 검증)")
print("\n상관계수 매트릭스로 다중공선성 확인:")
print("="*50)
corr_matrix = X.corr()
print(corr_matrix)
print("\n해석: 상관계수가 0.8 이상이면 다중공선성 의심")
print("="*50)

# ============================================================================
# 5. 회귀분석 (statsmodels)
# ============================================================================
print("\n[Step 5] 회귀분석 실행")
X_with_const = sm.add_constant(X)
model = sm.OLS(y, X_with_const).fit()

print("\n" + "="*70)
print("회귀분석 결과 요약")
print("="*70)
print(model.summary())

# ============================================================================
# 6. 결과 저장
# ============================================================================
print("\n[Step 6] 결과 정리")

# 주요 지표
r2 = model.rsquared
adj_r2 = model.rsquared_adj
f_stat = model.fvalue
f_pvalue = model.f_pvalue

print(f"\nR-squared: {r2:.4f}")
print(f"Adjusted R-squared: {adj_r2:.4f}")
print(f"F-statistic: {f_stat:.2f}")
print(f"F p-value: {f_pvalue:.2e}")

# 계수 정리
coef_df = pd.DataFrame({
    '변수': model.params.index,
    '계수': model.params.values,
    '표준오차': model.bse.values,
    't값': model.tvalues.values,
    'p-value': model.pvalues.values
})

print("\n회귀계수:")
print("="*70)
for idx, row in coef_df.iterrows():
    sig = '***' if row['p-value'] < 0.001 else ('**' if row['p-value'] < 0.01 else ('*' if row['p-value'] < 0.05 else ''))
    print(f"{row['변수']:15s}: {row['계수']:>15,.0f}  (p={row['p-value']:.4f}) {sig}")
print("="*70)

# ============================================================================
# 7. 예측 및 잔차
# ============================================================================
print("\n[Step 7] 예측 및 잔차 분석")
y_pred = model.predict(X_with_const)
residuals = y - y_pred

# 성능 지표
rmse = np.sqrt(mean_squared_error(y, y_pred))
mae = mean_absolute_error(y, y_pred)
mape = np.mean(np.abs((y - y_pred) / y)) * 100

print(f"\nRMSE: {rmse:,.0f}원 ({rmse/1e8:.2f}억원)")
print(f"MAE: {mae:,.0f}원 ({mae/1e8:.2f}억원)")
print(f"MAPE: {mape:.2f}%")

# ============================================================================
# 8. 잔차 플롯
# ============================================================================
print("\n[Step 8] 잔차 플롯 생성")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 잔차 vs 예측값
axes[0, 0].scatter(y_pred/1e8, residuals/1e8, alpha=0.5, s=10)
axes[0, 0].axhline(0, color='red', linestyle='--', linewidth=2)
axes[0, 0].set_xlabel('예측 매출 (억원)', fontsize=12)
axes[0, 0].set_ylabel('잔차 (억원)', fontsize=12)
axes[0, 0].set_title('잔차 vs 예측값', fontsize=14, fontweight='bold')
axes[0, 0].grid(alpha=0.3)

# 잔차 히스토그램
axes[0, 1].hist(residuals/1e8, bins=50, edgecolor='black', alpha=0.7)
axes[0, 1].set_xlabel('잔차 (억원)', fontsize=12)
axes[0, 1].set_ylabel('빈도', fontsize=12)
axes[0, 1].set_title('잔차 분포', fontsize=14, fontweight='bold')
axes[0, 1].grid(alpha=0.3)

# Q-Q 플롯
sm.qqplot(residuals, line='s', ax=axes[1, 0])
axes[1, 0].set_title('Q-Q 플롯 (정규성 검정)', fontsize=14, fontweight='bold')
axes[1, 0].grid(alpha=0.3)

# 실제 vs 예측
axes[1, 1].scatter(y/1e8, y_pred/1e8, alpha=0.5, s=10)
axes[1, 1].plot([y.min()/1e8, y.max()/1e8], [y.min()/1e8, y.max()/1e8], 
                'r--', linewidth=2, label='Perfect Prediction')
axes[1, 1].set_xlabel('실제 매출 (억원)', fontsize=12)
axes[1, 1].set_ylabel('예측 매출 (억원)', fontsize=12)
axes[1, 1].set_title('실제 vs 예측', fontsize=14, fontweight='bold')
axes[1, 1].legend()
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('./outputs/07_회귀분석_잔차.png', dpi=300, bbox_inches='tight')
print("* Saved: 07_회귀분석_잔차.png")
plt.close()

# ============================================================================
# 9. 상권별 예측 비교
# ============================================================================
print("\n[Step 9] 상권별 예측 매출 계산")

# 각 상권별 평균 조건
sangwon_stats = merged.groupby('주요_상권유형').agg({
    '점포_수': 'mean',
    '총_유동인구_수': 'mean',
    '당월_매출_금액': 'mean'
}).reset_index()

print("\n상권별 실제 평균:")
print("="*70)
for idx, row in sangwon_stats.iterrows():
    print(f"{row['주요_상권유형']:8s}: 매출={row['당월_매출_금액']/1e8:6.1f}억, "
          f"점포={row['점포_수']:5.1f}개, 유동인구={row['총_유동인구_수']/1e6:5.1f}백만명")
print("="*70)

print("\n" + "="*70)
print("03_심층분석 실행 완료")
print("="*70)
