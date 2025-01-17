import requests
import json
from datetime import datetime, timedelta
import pytz
import time
import os

# Configuration
DAYS = 3  # Number of days to fetch topics from
CATEGORY_ID = 36
TAG = '抽奖'
OUTPUT_FILE = 'linux_do_lottery.json'
CATEGORY_SLUG = 'welfare'

class LinuxDoDiscourse:
    def __init__(self):
        self.base_url = "https://linux.do"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }

    def fetch_topics(self):
        """Fetch topics from linux.do"""
        try:
            topics = []
            # First fetch all topics from the category
            response = self.session.get(
                f"{self.base_url}/c/{CATEGORY_SLUG}/{CATEGORY_ID}/l/latest.json",
                headers=self.headers,
                params={
                    'page': 1,
                    'order': 'created'
                }
            )
            response.raise_for_status()
            
            # Get all topics and filter by date and tag
            all_topics = response.json()['topic_list']['topics']
            beijing_tz = pytz.timezone('Asia/Shanghai')
            now = datetime.now(beijing_tz)
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = today - timedelta(days=DAYS-1)  # Include today
            
            filtered_topics = []
            for topic in all_topics:
                created_at = datetime.strptime(topic.get('created_at'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
                created_at_beijing = created_at.astimezone(beijing_tz)
                
                if (TAG in topic.get('title', '') and created_at_beijing >= cutoff_date):
                    # Keep only key fields
                    filtered_topic = {
                        'id': topic.get('id'),
                        'title': topic.get('title'),
                        'created_at': topic.get('created_at'),
                        'url': f"{self.base_url}/t/{topic.get('slug')}/{topic.get('id')}",
                        'posts_count': topic.get('posts_count'),
                        'views': topic.get('views'),
                        'like_count': topic.get('like_count'),
                        'reply_count': topic.get('reply_count', 0),
                        'closed': topic.get('closed', False),
                        'archived': topic.get('archived', False),
                        'tags': topic.get('tags', [])
                    }
                    filtered_topics.append(filtered_topic)
            
            topics.extend(filtered_topics)
            
            # Save topics to file
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(topics, f, ensure_ascii=False, indent=2)
            
            print(f"Successfully fetched {len(topics)} topics")
            print(f"Date range: {cutoff_date.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"Failed to fetch topics: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.content.decode('utf-8')}")

def main():
    client = LinuxDoDiscourse()
    client.fetch_topics()

if __name__ == "__main__":
    main()
 