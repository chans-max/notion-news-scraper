{\rtf1\ansi\ansicpg949\cocoartf2865
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\froman\fcharset0 Times-Roman;}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs24 \cf0 \expnd0\expndtw0\kerning0
import feedparser\
import os  # 'os' \uc0\u46972 \u51060 \u48652 \u47084 \u47532 \u47484  \u49324 \u50857 \u54633 \u45768 \u45796 .\
from notion_client import Client\
import datetime\
import sys # \uc0\u50724 \u47448  \u48156 \u49373  \u49884  \u51333 \u47308 \u47484  \u50948 \u54632 \
\
# --- 1. \uc0\u49444 \u51221  (GitHub Actions Secret\u50640 \u49436  \u44032 \u51256 \u50724 \u46020 \u47197  \u49688 \u51221 ) ---\
# \uc0\u55357 \u56593  GitHub Actions\u51032  'Secrets'\u50640  \u51200 \u51109 \u46108  \u44050 \u51012  \u44032 \u51256 \u50741 \u45768 \u45796 .\
NOTION_API_KEY = os.environ.get('NOTION_API_KEY')\
DATABASE_ID = os.environ.get('DATABASE_ID')\
\
# \uc0\u55358 \u56598  API \u53412 \u45208  DB ID\u44032  \u50630 \u51004 \u47732  \u49828 \u53356 \u47549 \u53944  \u51473 \u51648 \
if not NOTION_API_KEY or not DATABASE_ID:\
    print("\uc0\u10060  \u50724 \u47448 : NOTION_API_KEY \u46608 \u45716  DATABASE_ID\u44032  \u49444 \u51221 \u46104 \u51648  \u50506 \u50520 \u49845 \u45768 \u45796 .")\
    sys.exit(1) # \uc0\u49828 \u53356 \u47549 \u53944  \u48708 \u51221 \u49345  \u51333 \u47308 \
\
# \uc0\u55358 \u56598  \u45432 \u49496  \u53364 \u46972 \u51060 \u50616 \u53944  \u52488 \u44592 \u54868 \
notion = Client(auth=NOTION_API_KEY)\
\
# --- 2. \uc0\u54596 \u53552 \u47553 \u54624  \u53412 \u50892 \u46300  \u47785 \u47197  \u51221 \u51032  ---\
KEYWORDS = \{\
    "AI": ["AI", "\uc0\u51064 \u44277 \u51648 \u45733 ", "\u46373 \u47084 \u45789 ", "\u47672 \u49888 \u47084 \u45789 ", "LLM", "\u49373 \u49457 \u54805 ", "ChatG"],\
    "\uc0\u47928 \u54868 /\u52629 \u51228 ": ["\u47928 \u54868 ", "\u52629 \u51228 ", "\u54168 \u49828 \u54000 \u48268 ", "\u51204 \u49884 ", "\u44277 \u50672 ", "\u53080 \u49436 \u53944 ", "\u48036 \u51648 \u52972 ", "\u48120 \u49696 \u44288 "],\
    "\uc0\u47928 \u54868 \u53080 \u53584 \u52768 ": ["\u53080 \u53584 \u52768 ", "\u50937 \u53808 ", "\u50689 \u54868 ", "\u46300 \u46972 \u47560 ", "K-POP", "\u44172 \u51076 ", "\u50528 \u45768 \u47700 \u51060 \u49496 ", "\u54620 \u47448 ", "OTT"]\
\}\
\
# --- 3. \uc0\u49688 \u51665 \u54624  RSS \u54588 \u46300  \u47785 \u47197  \u51221 \u51032  ---\
RSS_FEEDS = \{\
    "AI": "https://www.chosun.com/arc/outboundfeeds/rss/category/it-science/?outputType=xml",\
    "\uc0\u47928 \u54868 /\u52629 \u51228 ": "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=08&plink=RSSREADER",\
    "\uc0\u47928 \u54868 \u53080 \u53584 \u52768 ": "http://www.hani.co.kr/rss/culture/"\
\}\
\
# --- 4. [\uc0\u49888 \u44508 ] \u51473 \u48373  \u52404 \u53356 \u47484  \u50948 \u54644  \u44592 \u51316  URL \u44032 \u51256 \u50724 \u44592  ---\
def get_existing_urls(days_to_check=3):\
    print(f"\uc0\u51473 \u48373  \u48169 \u51648 \u47484  \u50948 \u54644  \u52572 \u44540  \{days_to_check\}\u51068 \u44036 \u51032  \u44592 \u51316  \u44592 \u49324  URL\u51012  \u51312 \u54924 \u54633 \u45768 \u45796 ...")\
    existing_urls = set()\
    start_date = (datetime.datetime.now() - datetime.timedelta(days=days_to_check)).strftime("%Y-%m-%d")\
\
    try:\
        response = notion.databases.query(\
            database_id=DATABASE_ID,\
            filter=\{"property": "\uc0\u49688 \u51665 \u51068 ", "date": \{"on_or_after": start_date\}\},\
            page_size=100\
        )\
        results = response.get("results", [])\
        \
        for page in results:\
            properties = page.get("properties", \{\})\
            url_data = properties.get("URL", \{\})\
            if url_data and url_data.get("url"):\
                existing_urls.add(url_data.get("url"))\
                \
        print(f"\uc0\u52509  \{len(existing_urls)\}\u44060 \u51032  \u44592 \u51316  URL\u51012  \u47196 \u46300 \u54664 \u49845 \u45768 \u45796 .")\
        return existing_urls\
    except Exception as e:\
        print(f"\uc0\u10060  \u44592 \u51316  URL \u47196 \u46300  \u51473  \u50724 \u47448  \u48156 \u49373 : \{e\}")\
        return existing_urls\
\
# --- 5. \uc0\u45432 \u49496  \u50629 \u47196 \u46300  \u54632 \u49688  ---\
def add_to_notion(title, url, category):\
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")\
    try:\
        new_page = \{\
            "\uc0\u51228 \u47785 ": \{"title": [\{"text": \{"content": title\}\}]\},\
            "URL": \{"url": url\},\
            "\uc0\u48516 \u47448 ": \{"multi_select": [\{"name": category\}]\},\
            "\uc0\u49688 \u51665 \u51068 ": \{"date": \{"start": today_str\}\}\
        \}\
        notion.pages.create(parent=\{"database_id": DATABASE_ID\}, properties=new_page)\
        print(f"\uc0\u9989  [\u50629 \u47196 \u46300  \u49457 \u44277 !] \u52852 \u53580 \u44256 \u47532 : \{category\} | \u51228 \u47785 : \{title\}")\
    except Exception as e:\
        print(f"\uc0\u10060  [\u50629 \u47196 \u46300  \u49892 \u54056 ] \u51228 \u47785 : \{title\} | \u50724 \u47448 : \{e\}")\
        pass\
\
# --- 6. \uc0\u47700 \u51064  \u49892 \u54665  \u47196 \u51649  ---\
def fetch_and_filter_news():\
    print("="*30)\
    print("\uc0\u55357 \u56560  \u45684 \u49828  \u49688 \u51665  \u48143  \u54596 \u53552 \u47553 \u51012  \u49884 \u51089 \u54633 \u45768 \u45796 ...")\
    print("="*30)\
    \
    existing_urls = get_existing_urls(days_to_check=3) \
    total_uploaded = 0\
    total_skipped = 0\
    \
    for category_guess, rss_url in RSS_FEEDS.items():\
        feed = feedparser.parse(rss_url)\
        print(f"\\n--- [\{category_guess\}] \uc0\u52852 \u53580 \u44256 \u47532  \u54588 \u46300  \u54869 \u51064  \u51473 ... ---")\
        if not feed.entries:\
            print("  (\uc0\u49688 \u51665 \u46108  \u44592 \u49324  \u50630 \u51020 )")\
            continue\
\
        for item in feed.entries:\
            title = item.title\
            link = item.link\
            \
            if link in existing_urls:\
                total_skipped += 1\
                continue \
\
            summary = item.get("summary", "") \
            content_to_check = title + " " + summary\
            \
            found_category = None\
            for category_name, keywords_list in KEYWORDS.items():\
                if any(keyword.lower() in content_to_check.lower() for keyword in keywords_list):\
                    found_category = category_name\
                    break \
            \
            if found_category:\
                add_to_notion(title, link, found_category)\
                existing_urls.add(link)\
                total_uploaded += 1\
            \
    print("\\n" + "="*30)\
    print(f"\uc0\u55356 \u57225  \u47784 \u46304  \u51089 \u50629  \u50756 \u47308 .")\
    print(f"  - \uc0\u49888 \u44508  \u50629 \u47196 \u46300 : \{total_uploaded\}\u44060 ")\
    print(f"  - \uc0\u51473 \u48373  \u49828 \u53429 : \{total_skipped\}\u44060 ")\
    print("="*30)\
\
# --- \uc0\u55357 \u56960  \u49828 \u53356 \u47549 \u53944  \u49892 \u54665  ---\
if __name__ == "__main__":\
    fetch_and_filter_news()}