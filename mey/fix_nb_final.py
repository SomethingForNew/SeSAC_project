import json
import os

notebook_path = r"c:\Users\Administrator\Documents\workspace\budongsan3_project\mey\news.crawling.ipynb"
target_cell_id = "b862f5ac"

new_source_code = [
    "# 구별 상관계수 계산\n",
    "regional_correlation = []\n",
    "\n",
    "for region in REGIONS:\n",
    "    region_sent = regional_sentiment[regional_sentiment['region'] == region]\n",
    "    region_price = price_df[price_df['region'] == region]\n",
    "    \n",
    "    # 날짜 매칭 문제 해결: year_month 기준으로 병합\n",
    "    region_merged = pd.merge(\n",
    "        region_sent[['year_month', 'avg_sentiment']],\n",
    "        region_price[['year_month', 'avg_price']],\n",
    "        on='year_month',\n",
    "        how='inner'\n",
    "    )\n",
    "    \n",
    "    if len(region_merged) >= 5:\n",
    "        corr, p_val = pearsonr(region_merged['avg_sentiment'], region_merged['avg_price'])\n",
    "        \n",
    "        regional_correlation.append({\n",
    "            'region': region,\n",
    "            'correlation': corr,\n",
    "            'p_value': p_val,\n",
    "            'sensitivity': abs(corr),\n",
    "            'significant': '✅' if p_val < 0.05 else ''\n",
    "        })\n",
    "\n",
    "sensitivity_df = pd.DataFrame(regional_correlation)\n",
    "\n",
    "# 데이터가 없을 경우 처리 (KeyError 방지)\n",
    "if not sensitivity_df.empty:\n",
    "    sensitivity_df = sensitivity_df.sort_values('correlation', ascending=False)\n",
    "else:\n",
    "    # 데이터가 없을 경우 빈 DataFrame 생성 (컬럼 정의)\n",
    "    sensitivity_df = pd.DataFrame(columns=['region', 'correlation', 'p_value', 'sensitivity', 'significant'])\n",
    "\n",
    "print(\"📊 강남3구 뉴스 민감도 비교:\")\n",
    "print(sensitivity_df.to_string(index=False))\n",
    "\n",
    "if len(sensitivity_df) > 0:\n",
    "    print(f\"\\n🏆 가장 민감한 지역: {sensitivity_df.iloc[0]['region']}\")\n",
    "else:\n",
    "    print(\"\\n⚠️ 분석 가능한 충분한 데이터가 없습니다 (매칭된 데이터 부족).\")"
]

def fix_notebook():
    if not os.path.exists(notebook_path):
        print(f"Error: File not found at {notebook_path}")
        return

    with open(notebook_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for cell in data['cells']:
        if cell.get('id') == target_cell_id:
            cell['source'] = new_source_code
            print(f"Found and replaced cell {target_cell_id}.")
            break
            
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    print("Notebook saved successfully.")

if __name__ == "__main__":
    fix_notebook()
