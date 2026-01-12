import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time


# def crwl_joongang_realestate(start_page=1, end_page=5):
def crwl_joongang_realestate():
    """
    중앙일보 부동산 섹션 크롤링

    Parameters:
    - start_page: 시작 페이지 (1부터 시작)
    - end_page: 종료 페이지
    """

    # User-Agent 설정
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # BASE_URL = 'https://www.joongang.co.kr/realestate'
    BASE_URL = 'https://www.joongang.co.kr/realestate/news'

    # 검색 키워드
    KEYWORDS = ['부동산', '아파트', '집값']

    all_news = []

    # for page in range(start_page, end_page + 1):
    #     if page == 1:
    #         url = BASE_URL
    #     else:
    #         url = f"{BASE_URL}?page={page}"
        
    
    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            print(f"실패: {response.status_code}")
            # continue

        soup = BeautifulSoup(response.content, 'html.parser')

        # print(soup.select('h2.headline'))


        cards = soup.select('li.card')

        print(f"총 {len(cards)}개 카드 찾음!")

        
        news_list = []

        for card in cards:
            headline = card.select_one('h2.headline')
            date = card.select_one('p.date')
            link = card.select_one('a')

            if headline:  # 제목이 있을 때만
                news_list.append({
                    '제목': headline.get_text(strip=True),
                    '날짜': date.get_text(strip=True) if date else '',
                    'URL': link['href'] if link else ''
                })
    
    except Exception as e:
        print(e)

    for i, news in enumerate(news_list, 1):
        print(f"{i}. {news['제목']}")
        print(f"   날짜: {news['날짜']}")
        print(f"   URL: {news['URL']}")