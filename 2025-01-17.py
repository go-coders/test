import requests
import json
from datetime import datetime
import pytz
import time

class LinuxDoDiscourse:
    def __init__(self):
        self.base_url = "https://linux.do"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_latest_topics(self, category_id=36, category_slug='welfare', tag='抽奖'):
        """Get today's latest topics from specified category with lottery tag"""
        page = 0
        all_topics = []
        
        # Get current Beijing time
        beijing_tz = pytz.timezone('Asia/Shanghai')
        utc_now = datetime.now(pytz.UTC)  # Use datetime.now(UTC) instead of utcnow()
        beijing_now = utc_now.astimezone(beijing_tz)
        today = beijing_now.strftime('%Y-%m-%d')
        
        print(f"Current Beijing time: {beijing_now}")
        print(f"Today's date: {today}")
        print(f"Fetching topics from category ID {category_id} (福利羊毛) with tag: {tag}")
        
        while True:
            url = f"{self.base_url}/c/{category_slug}/{category_id}/l/latest.json?page={page}&tags={tag}&order=created"
            try:
                print(f"\nFetching page {page}...")
                print(f"URL: {url}")
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                
                data = response.json()
                topics = data.get('topic_list', {}).get('topics', [])
                
                if not topics:
                    print(f"No topics found on page {page}")
                    break
                
                found_today_topic = False
                found_older_unpinned = False
                print(f"Found {len(topics)} topics on page {page}")
                
                for topic in topics:
                    created_at_utc = datetime.fromisoformat(topic['created_at'].replace('Z', '+00:00'))
                    created_at_beijing = created_at_utc.astimezone(beijing_tz)
                    created_date = created_at_beijing.strftime('%Y-%m-%d')
                    
                    is_pinned = topic.get('pinned', False) or topic.get('pinned_globally', False)
                    
                    print(f"\nChecking topic: {topic['title']}")
                    print(f"Created at (Beijing): {created_at_beijing}")
                    print(f"Created date: {created_date}")
                    print(f"Is pinned: {is_pinned}")
                    
                    # Skip pinned topics for date comparison
                    if is_pinned:
                        print("Skipping pinned topic...")
                        continue
                    
                    # If we find a non-pinned topic from before today, mark it
                    if created_date < today:
                        found_older_unpinned = True
                        print(f"Found older unpinned topic from {created_date}")
                    
                    if created_date == today:
                        found_today_topic = True
                        last_posted_at_utc = datetime.fromisoformat(topic['last_posted_at'].replace('Z', '+00:00')) if topic.get('last_posted_at') else created_at_utc
                        last_posted_at_beijing = last_posted_at_utc.astimezone(beijing_tz)
                        
                        formatted_topic = {
                            'id': topic['id'],
                            'title': topic['title'],
                            'created_at': created_at_beijing.isoformat(),
                            'last_posted_at': last_posted_at_beijing.isoformat(),
                            'views': topic.get('views', 0),
                            'posts_count': topic.get('posts_count', 0),
                            'likes': topic.get('like_count', 0),
                            'reply_count': topic.get('reply_count', 0),
                            'highest_post_number': topic.get('highest_post_number', 0),
                            'image_url': topic.get('image_url'),
                            'bumped': topic.get('bumped', False),
                            'bumped_at': topic.get('bumped_at'),
                            'unseen': topic.get('unseen', False),
                            'pinned': topic.get('pinned', False),
                            'pinned_globally': topic.get('pinned_globally', False),
                            'visible': topic.get('visible', True),
                            'closed': topic.get('closed', False),
                            'archived': topic.get('archived', False),
                            'bookmarked': topic.get('bookmarked'),
                            'liked': topic.get('liked'),
                            'tags': topic.get('tags', []),
                            'tags_descriptions': topic.get('tags_descriptions', {}),
                            'category_id': topic.get('category_id'),
                            'has_accepted_answer': topic.get('has_accepted_answer', False),
                            'can_have_answer': topic.get('can_have_answer', False),
                            'posters': topic.get('posters', []),
                            'participants': topic.get('participants', []),
                            'url': f"{self.base_url}/t/{topic.get('slug', '')}/{topic['id']}"
                        }
                        all_topics.append(formatted_topic)
                        print(f"Found today's lottery topic: {topic['title']} (created at {created_at_beijing.strftime('%H:%M:%S')})")
                
                # Only stop if we found an older unpinned topic and no today's topics on this page
                if found_older_unpinned and not found_today_topic:
                    print("\nFound older unpinned topics and no today's topics, stopping...")
                    break
                
                if not found_today_topic:
                    print("\nNo today's topics found on this page, continuing to next page...")
                
                page += 1
                time.sleep(1)  # Add delay to avoid rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching topics: {e}")
                if hasattr(e.response, 'text'):
                    print(f"Response text: {e.response.text}")
                break
        
        print(f"\nTotal pages fetched: {page}")
        # Sort by creation time
        all_topics.sort(key=lambda x: x['created_at'], reverse=True)
        return all_topics

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

def save_data(topics, category_id=36, category_slug='welfare', tag='抽奖'):
    # Get current Beijing time
    beijing_tz = pytz.timezone('Asia/Shanghai')
    utc_now = datetime.now(pytz.UTC)  # Use datetime.now(UTC) instead of utcnow()
    beijing_now = utc_now.astimezone(beijing_tz)
    current_time = beijing_now.strftime('%Y-%m-%d_%H-%M-%S')
    
    data = {
        'fetch_time': beijing_now.isoformat(),
        'category_id': category_id,
        'category_slug': category_slug,
        'tag': tag,
        'category_name': '福利羊毛',
        'total_topics': len(topics),
        'topics': topics
    }
    
    filename = f'linux_do_lottery.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(topics)} lottery topics to {filename}")

def main():
    discourse = LinuxDoDiscourse()
    topics = discourse.get_latest_topics(category_id=36, category_slug='welfare', tag='抽奖')
    print(f"\nFound {len(topics)} latest lottery topics in 福利羊毛 category")
    save_data(topics, category_id=36, category_slug='welfare', tag='抽奖')

if __name__ == "__main__":
    main()