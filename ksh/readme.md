## 수집단계

### 1. 실거래가 데이터 `[api]`

- api call 이후 정제 하여 supbase 에 저장
- csv 파일 백업

<br>

### 2. 감성분석(뉴스만 사용) `[크롤링]`

- 뉴스 크롤링 후 긍정/부정 추출 후 점수 계산
- 계산된 점수를 일자별로 supabase에 저장
- 추출데이터/점수계산 데이터를 csv 파일 백업

## supabase에 저장 할 데이터

- 정제된 실거래가 데이터
- 긍정/부정 키워드 및 일자별로 계산 된 점수
- 감성분석 결과
- 일별 요약

### 네이버 뉴스 api

https://developers.naver.com/docs/serviceapi/search/news/news.md

(중앙일보)
https://www.joongang.co.kr/robots.txt

---

https://www.joongang.co.kr/realestate?page=4
위와 같이 page라는 쿼리스트링으로 페이징이 되어있어서 상대적으로 쉽게 크롤링이 가능할것으로 보임
