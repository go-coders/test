import requests
import json
from datetime import datetime
import pytz

class LinuxDoDiscourse:
    def __init__(self):
        self.base_url = "https://linux.do"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_top_topics(self):
        url = f"{self.base_url}/top.json"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            topics = data.get('topic_list', {}).get('topics', [])
            
            formatted_topics = []
            for topic in topics:
                created_at_utc = datetime.fromisoformat(topic['created_at'].replace('Z', '+00:00'))
                beijing_tz = pytz.timezone('Asia/Shanghai')
                created_at_beijing = created_at_utc.astimezone(beijing_tz)
                
                formatted_topic = {
                    'id': topic['id'],
                    'title': topic['title'],
                    'created_at': created_at_beijing.isoformat(),
                    'views': topic.get('views', 0),
                    'posts_count': topic.get('posts_count', 0),
                    'url': f"{self.base_url}/t/{topic.get('slug', '')}/{topic['id']}"
                }
                formatted_topics.append(formatted_topic)
                print(f"Found top topic: {topic['title']}")
            
            return formatted_topics
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching top topics: {e}")
            return []

    def get_topic_content(self, topic_id):
        url = f"{self.base_url}/t/{topic_id}.json"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            first_post = data['post_stream']['posts'][0] if data['post_stream']['posts'] else None
            
            return {
                'first_post_content': first_post.get('cooked', '') if first_post else '',
                'author': first_post['username'] if first_post else ''
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching topic content: {e}")
            return None

def save_top_data(topics):
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(pytz.UTC).astimezone(beijing_tz)
    today = now.strftime('%Y-%m-%d')
    
    data = {
        'date': today,
        'topics': topics
    }
    
    filename = f'linux_do_top_{today}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved top topics to {filename}")

def main():
    discourse = LinuxDoDiscourse()
    top_topics = discourse.get_top_topics()
    print(f"Found {len(top_topics)} top topics")
    save_top_data(top_topics)

if __name__ == "__main__":
    main()