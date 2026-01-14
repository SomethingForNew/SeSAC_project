import pandas as pd # 데이터 분석 필수 라이브러리
from collections import Counter # 단어 개수 세기 도구
import re # 텍스트 정제용 정규표현식

# 1. 수집했던 원본 데이터 파일 불러오기
# (경로가 다를 경우 'ysy/dessert/dessert_trend_2016_2025.csv' 처럼 수정해 주세요)
try:
    df = pd.read_csv("dessert_trend_2016_2025.csv")
    print("데이터 파일을 성공적으로 불러왔습니다.")
except FileNotFoundError:
    print("파일을 찾을 수 없습니다. 경로를 확인해주세요.")

def get_top_keywords(text_list):
    """텍스트 리스트에서 의미 있는 단어 10개를 뽑는 기능"""
    # 텍스트 합치고 한글만 남기기
    all_text = " ".join(map(str, text_list))
    clean_text = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣\s]', ' ', all_text)
    
    # 단어 쪼개기 및 2글자 이상 단어만 추출
    words = [w for w in clean_text.split() if len(w) > 1]
    
    # 가장 많이 언급된 단어 10개 반환
    return Counter(words).most_common(10)

# 2. 분석 결과를 담을 리스트 (나중에 표로 만들 용도)
analysis_results = []

# 3. 연도별로 루프를 돌며 키워드 추출
years = sorted(df['target_year'].unique())

for year in years:
    year_df = df[df['target_year'] == year]
    
    # 제목(title)과 본문요약(description) 모두 활용하여 분석
    combined_text = year_df['title'].tolist() + year_df['description'].tolist()
    top_words = get_top_keywords(combined_text)
    
    # 분석 결과를 리스트에 차곡차곡 담기
    for rank, (word, count) in enumerate(top_words, 1):
        analysis_results.append({
            '연도': year,
            '순위': rank,
            '키워드': word,
            '언급횟수': count
        })

# 4. 분석 결과 리스트를 판다스 표(DataFrame)로 변환
summary_df = pd.DataFrame(analysis_results)

# 5. 최종 결과물 파일로 저장 (한글 깨짐 방지 utf-8-sig)
summary_df.to_csv("dessert_keyword_analysis.csv", index=False, encoding='utf-8-sig')

print("\n분석 완료! 'dessert_keyword_analysis.csv' 파일이 생성되었습니다. 🎉")
# 상위 일부 결과 미리보기
print(summary_df.head(10))