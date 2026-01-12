import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client


def fetch_data():
    load_dotenv()

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ 환경변수로 안전하게 연결!")


    all_data = []
    step = 1000  # 한 번에 가져올 row 수
    start = 0

    while True:
        end = start + step - 1
        response = supabase.table("t_temp").select("*").range(start, end).execute()
        
        rows = response.data
        if not rows:  # 더 이상 데이터 없으면 종료
            break

        all_data.extend(rows)
        print(f"{start} ~ {end} 수집 완료, 누적 {len(all_data)}건")

        start += step  # 다음 페이지로 이동

    return all_data