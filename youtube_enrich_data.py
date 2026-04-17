import csv
import os
import sys
import requests
import time
import urllib.parse


YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"


def get_api_key():
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set")
        print("  Set it with: export YOUTUBE_API_KEY='your_api_key'")
        print("  Get API key from: https://console.cloud.google.com/apis/credentials")
        sys.exit(1)
    return api_key


def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    return query.get('v', [None])[0]


def get_video_details(api_key, video_ids):
    """Fetch video details from YouTube Data API"""
    if not video_ids:
        return {}
    
    video_details = {}
    batch_size = 50
    
    for i in range(0, len(video_ids), batch_size):
        batch = video_ids[i:i + batch_size]
        ids_string = ','.join(batch)
        
        url = f"{YOUTUBE_API_BASE_URL}/videos"
        params = {
            'part': 'snippet,statistics,contentDetails',
            'id': ids_string,
            'key': api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'error' in data:
                print(f"  API Error: {data['error']['message']}")
                break
            
            for item in data.get('items', []):
                video_id = item['id']
                snippet = item.get('snippet', {})
                statistics = item.get('statistics', {})
                
                channel_name = snippet.get('channelTitle', '')
                
                view_count = statistics.get('viewCount', '')
                
                category_id = snippet.get('categoryId', '')
                
                tags = snippet.get('tags', [])
                tags_str = ','.join(tags) if tags else ''
                
                thumbnails = snippet.get('thumbnails', {})
                thumbnail_url = ''
                for key in ['maxres', 'high', 'medium', 'default']:
                    if key in thumbnails:
                        thumbnail_url = thumbnails[key]['url']
                        break
                
                video_details[video_id] = {
                    'title': snippet.get('title', ''),
                    'channel': channel_name,
                    'views': view_count,
                    'category_id': category_id,
                    'tags': tags_str,
                    'thumbnail_url': thumbnail_url
                }
            
            if i + batch_size < len(video_ids):
                time.sleep(0.1)
                
        except Exception as e:
            print(f"  Error fetching batch: {e}")
            break
    
    return video_details


def enrich_csv(input_file, output_file=None):
    if output_file is None:
        output_file = input_file.replace('.csv', '_enriched.csv')
    
    api_key = get_api_key()
    
    print(f"Reading: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Found {len(rows)} videos")
    
    video_ids = []
    for row in rows:
        video_id = extract_video_id(row['url'])
        if video_id:
            video_ids.append(video_id)
    
    unique_ids = list(set(video_ids))
    print(f"Unique video IDs: {len(unique_ids)}")
    
    if not unique_ids:
        print("No valid YouTube video URLs found")
        return
    
    print("Fetching video details from YouTube API...")
    video_details = get_video_details(api_key, unique_ids)
    print(f"Retrieved details for {len(video_details)} videos")
    
    # Add new columns to each row
    for row in rows:
        video_id = extract_video_id(row['url'])
        if video_id and video_id in video_details:
            details = video_details[video_id]
            # Update title, channel and views from API (more accurate)
            if details.get('title'):
                row['title'] = details['title']
            if details.get('channel'):
                row['channel'] = details['channel']
            if details.get('views'):
                row['views'] = details['views'] + ' views'
            row['category_id'] = details.get('category_id', '')
            row['tags'] = details.get('tags', '')
            row['thumbnail_url'] = details.get('thumbnail_url', '')
        else:
            row['category_id'] = ''
            row['tags'] = ''
            row['thumbnail_url'] = ''
    
    # Write enriched CSV
    fieldnames = ['title', 'channel', 'views', 'url', 'depth', 'recommended_from', 'category_id', 'tags', 'thumbnail_url']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Saved enriched data to: {output_file}")


def main():
    input_file = 'youtube_results.csv'
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        enrich_csv(input_file, output_file)
    else:
        enrich_csv(input_file)


if __name__ == '__main__':
    main()