import feedparser
import os
from notion_client import Client
import datetime
import sys

# --- 1. 설정 (GitHub Actions Secret에서 가져오도록 수정) ---
NOTION_API_KEY = os.environ.get('NOTION_API_KEY')
DATABASE_ID = os.environ.get('DATABASE_ID')

if not NOTION_API_KEY or not DATABASE_ID:
    print("❌ 오류: NOTION_API_KEY 또는 DATABASE_ID가 설정되지 않았습니다.")
    sys.exit(1)

notion = Client(auth=NOTION_API_KEY)

# --- 2. 필터링할 키워드 목록 정의 ---
KEYWORDS = {
    "AI": ["AI", "인공지능", "딥러닝", "머신러닝", "LLM", "생성형", "ChatG"],
    "문화/축제": ["문화", "축제", "페스티벌", "전시", "공연", "콘서트", "뮤지컬", "미술관"],
    "문화콘텐츠": ["콘텐츠", "웹툰", "영화", "드라마", "K-POP", "게임", "애니메이션", "한류", "OTT"]
}

# --- 3. 수집할 RSS 피드 목록 정의 ---
RSS_FEEDS = {
    "AI_조선IT": "https://www.chosun.com/arc/outboundfeeds/rss/category/it-science/?outputType=xml",
    "문화_SBS": "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=08&plink=RSSREADER",
    "문화_한겨레": "http://www.hani.co.kr/rss/culture/",
    "AI_전문(AI타임즈)": "https://www.aitimes.com/rss/all.xml",
    "AI_IT(ZDNet)": "https://www.zdnet.co.kr/rss/ittrend.xml",
    "콘텐츠_게임(게임메카)": "https://www.gamemeca.com/rss/all.xml",
    "콘텐츠_영화(씨네21)": "http://www.cine21.com/rss/news.xml",
    "콘텐츠_산업(KOCCA)": "https://www.kocca.kr/kocca/bbs/rss.do?bbsId=B0000137&searchBbsId=B0000137"
}

# --- 4. [수정됨] 중복 체크를 위해 기존 URL 가져오기 ---
def get_existing_urls(days_to_check=3):
    print(f"중복 방지를 위해 최근 {days_to_check}일간의 기존 기사 URL을 조회합니다...")
    existing_urls = set()
    start_date = (datetime.datetime.now() - datetime.timedelta(days=days_to_check)).strftime("%Y-%m-%d")

    try:
        response = notion.databases.query(
            database_id=DATABASE_ID,
            filter={"property": "수집일", "date": {"on_or_after": start_date}},
            page_size=100
        )
        results = response.get("results", [])
        
        for page in results:
            properties = page.get("properties", {})
            url_data = properties.get("URL", {}) # 노션의 "URL" 속성
            if url_data and url_data.get("url"):
                existing_urls.add(url_data.get("url"))
                
        print(f"총 {len(existing_urls)}개의 기존 URL을 로드했습니다.")
        return existing_urls
    except Exception as e:
        print(f"❌ 기존 URL 로드 중 오류 발생: {e} (중복 체크가 실패할 수 있습니다)")
        return existing_urls # 오류 시 빈 set 반환 (중복 저장될 수 있음)

# --- 5. [수정됨] 노션 업로드 함수 (요약 추가) ---
def add_to_notion(title, url, category, summary): 
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    try:
        summary_text = summary[:2000] if summary else "요약 없음"

        new_page = {
            "제목": {"title": [{"text": {"content": title}}]},
            "URL": {"url": url},
            "분류": {"multi_select": [{"name": category}]},
            "수집일": {"date": {"start": today_str}},
            "요약": {"rich_text": [{"text": {"content": summary_text}}]}
        }
        notion.pages.create(parent={"database_id": DATABASE_ID}, properties=new_page)
        print(f"✅ [업로드 성공!] 카테고리: {category} | 제목: {title}")
    except Exception as e:
        print(f"❌ [업로드 실패] 제목: {title} | 오류: {e}")
        pass

# --- 6. [수정됨] 메인 실행 로직 (안정성 강화) ---
def fetch_and_filter_news():
    print("="*30)
    print("📰 뉴스 수집 및 필터링을 시작합니다...")
    print("="*30)
    
    existing_urls = get_existing_urls(days_to_check=3) 
    total_uploaded = 0
    total_skipped = 0
    
    for category_guess, rss_url in RSS_FEEDS.items():
        print(f"\n--- [{category_guess}] 카테고리 피드 확인 중... ---")
        
        # 🔽🔽🔽 [핵심 수정] 🔽🔽🔽
        # RSS 피드 하나가 오류나도 전체 스크립트가 멈추지 않도록 try...except로 감쌉니다.
        try:
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                print("  (수집된 기사 없음)")
                continue

            for item in feed.entries:
                title = item.title
                link = item.link
                
                if link in existing_urls:
                    total_skipped += 1
                    continue 

                summary = item.get("summary", "") 
                content_to_check = title + " " + summary
                
                found_category = None
                for category_name, keywords_list in KEYWORDS.items():
                    if any(keyword.lower() in content_to_check.lower() for keyword in keywords_list):
                        found_category = category_name
                        break 
                
                if found_category:
                    add_to_notion(title, link, found_category, summary)
                    existing_urls.add(link)
                    total_uploaded += 1
        
        except Exception as e:
            print(f"❌ [피드 오류!] '{category_guess}' 피드 처리 중 오류 발생: {e}")
            print("  (다음 피드로 계속 진행합니다.)")
            pass # 이 피드는 건너뛰고 다음 피드로 넘어감
        # 🔼🔼🔼 [핵심 수정] 🔼🔼🔼
            
    print("\n" + "="*30)
    print(f"🎉 모든 작업 완료.")
    print(f"  - 신규 업로드: {total_uploaded}개")
    print(f"  - 중복 스킵: {total_skipped}개")
    print("="*30)

# --- 🚀 스크립트 실행 ---
if __name__ == "__main__":
    fetch_and_filter_news()
