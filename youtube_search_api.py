import os
import sys
import csv
import time
import requests


# =============================================================================
# IMPORTANT: YouTube Data API Limitation for Related Videos
# =============================================================================
# The YouTube Data API's 'relatedToVideoId' parameter was DEPRECATED by Google
# in August 2023. This endpoint now returns empty results and CANNOT be used
# to fetch related/recommended videos.
#
# See: https://developers.google.com/youtube/v3/revision_history#june-12,-2023
#
# This file exists for:
# - Initial search (search_videos): WORKS
# - Video details (get_video_details): WORKS
# - Related videos (get_related_videos): DOES NOT WORK (returns empty)
#
# To get actual "related videos" from YouTube, you must use:
# - Selenium-based scraping: python3 youtube_search.py
# - Direct innerTube API: Advanced (not implemented here)
# =============================================================================

YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"


CATEGORY_NAMES = {
    '1': 'Film & Animation',
    '2': 'Autos & Vehicles',
    '10': 'Music',
    '15': 'Pets & Animals',
    '17': 'Sports',
    '18': 'Short Movies',
    '19': 'Travel & Events',
    '20': 'Gaming',
    '21': 'Videoblogging',
    '22': 'People & Blogs',
    '23': 'Comedy',
    '24': 'Entertainment',
    '25': 'News & Politics',
    '26': 'Howto & Style',
    '27': 'Education',
    '28': 'Science & Technology',
    '29': 'Nonprofits & Activism',
    '30': 'Movies',
    '31': 'Anime/Animation',
    '32': 'Action/Adventure',
    '33': 'Classics',
    '34': 'Comedy',
    '35': 'Documentary',
    '36': 'Drama',
    '37': 'Family',
    '38': 'Foreign',
    '39': 'Horror',
    '40': 'Sci-Fi/Fantasy',
    '41': 'Thriller',
    '42': 'Shorts',
    '43': 'Shows',
    '44': 'Trailers',
}

OUTPUT_FILE_ENRICHED = "youtube_results_enriched.csv"


def load_category_names():
    """Load category names from file"""
    try:
        with open('category_ids.txt', 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    CATEGORY_NAMES[parts[0]] = parts[1]
    except FileNotFoundError:
        pass


def get_api_key():
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set")
        print("  Set it with: export YOUTUBE_API_KEY='your_api_key'")
        print("  Get API key from: https://console.cloud.google.com/apis/credentials")
        sys.exit(1)
    return api_key


def search_videos(api_key, query, max_results=10):
    """Search for videos using YouTube Data API"""
    url = f"{YOUTUBE_API_BASE_URL}/search"
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_results,
        'key': api_key
    }
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    videos = []
    if 'items' in data:
        for item in data['items']:
            video_id = item['id']['videoId']
            snippet = item['snippet']
            videos.append({
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'channel': snippet.get('channelTitle', ''),
                'description': snippet.get('description', ''),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'published_at': snippet.get('publishedAt', '')
            })
    
    return videos


def get_related_videos(api_key, video_id, max_results=10):
    """Get related videos using YouTube Data API.
    
    IMPORTANT: The YouTube Data API's 'relatedToVideoId' parameter was deprecated
    by Google in August 2023. This endpoint now returns empty results.
    
    This function will return an empty list - there is no workaround using the
    official YouTube Data API. To get related videos, you must use:
    - Selenium-based scraping (youtube_search.py), OR
    - Direct scraping of YouTube's innerTube API endpoints (advanced)
    """
    url = f"{YOUTUBE_API_BASE_URL}/search"
    params = {
        'part': 'snippet',
        'relatedToVideoId': video_id,
        'type': 'video',
        'maxResults': max_results,
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'error' in data:
            print(f"    API Error: {data['error']}")
            return []
        
        videos = []
        if 'items' in data:
            for item in data['items']:
                if item['id'].get('videoId') == video_id:
                    continue
                if 'videoId' not in item['id']:
                    continue
                    
                rel_video_id = item['id']['videoId']
                snippet = item['snippet']
                videos.append({
                    'video_id': rel_video_id,
                    'title': snippet.get('title', ''),
                    'channel': snippet.get('channelTitle', ''),
                    'description': snippet.get('description', ''),
                    'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'published_at': snippet.get('publishedAt', '')
                })
        
        return videos
        
    except Exception as e:
        print(f"    Exception: {e}")
        return []


def get_video_details(api_key, video_ids):
    """Batch fetch video details using YouTube Data API"""
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
                vid = item['id']
                snippet = item.get('snippet', {})
                statistics = item.get('statistics', {})
                
                view_count = statistics.get('viewCount', '0')
                if view_count:
                    view_count = f"{int(view_count):,}"
                
                tags = snippet.get('tags', [])
                tags_str = ','.join(tags) if tags else ''
                
                thumbnails = snippet.get('thumbnails', {})
                thumbnail_url = thumbnails.get('maxres', {}).get('url', '') or \
                               thumbnails.get('high', {}).get('url', '') or \
                               thumbnails.get('medium', {}).get('url', '')
                
                video_details[vid] = {
                    'channel': snippet.get('channelTitle', ''),
                    'views': f"{view_count} views" if view_count else '',
                    'category_id': snippet.get('categoryId', ''),
                    'tags': tags_str,
                    'thumbnail_url': thumbnail_url,
                    'description': snippet.get('description', ''),
                    'duration': item.get('contentDetails', {}).get('duration', '')
                }
            
            if i + batch_size < len(video_ids):
                time.sleep(0.1)
                
        except Exception as e:
            print(f"  Error fetching batch: {e}")
            break
    
    return video_details


def build_video_url(video_id):
    return f"https://www.youtube.com/watch?v={video_id}"


def search_youtube_api(query, max_initial=1, max_recommendations=2, depth=6, output_file=OUTPUT_FILE_ENRICHED):
    """Main function to search and collect video recommendations using API"""
    api_key = get_api_key()
    load_category_names()
    
    all_results = []
    processed_video_ids = set()
    current_depth_videos = []
    
    # Step 1: Get initial search results (depth 0)
    print(f"Searching for: {query}")
    initial_videos = search_videos(api_key, query, max_results=max_initial)
    print(f"Found {len(initial_videos)} initial videos")
    
    for video in initial_videos:
        video['depth'] = 0
        video['recommended_from'] = 'initial'
        current_depth_videos.append(video)
        processed_video_ids.add(video['video_id'])
        all_results.append(video)
    
    # Step 2: Get video details for initial videos (batch)
    video_ids_to_fetch = [v['video_id'] for v in all_results]
    video_details = get_video_details(api_key, video_ids_to_fetch)
    
    # Merge details
    for result in all_results:
        vid = result['video_id']
        if vid in video_details:
            details = video_details[vid]
            result['views'] = details.get('views', '')
            result['category_id'] = details.get('category_id', '')
            result['tags'] = details.get('tags', '')
            result['thumbnail_url'] = details.get('thumbnail_url', '')
            result['category_name'] = CATEGORY_NAMES.get(str(details.get('category_id', '')), 'Unknown')
        else:
            result['category_id'] = ''
            result['tags'] = ''
            result['thumbnail_url'] = ''
            result['category_name'] = 'Unknown'
    
    # Step 3: Process each depth level
    for current_depth in range(1, depth + 1):
        print(f"\nProcessing depth {current_depth}...")
        next_depth_videos = []
        
        for video in current_depth_videos:
            print(f"  Getting recommendations from: {video['title'][:50]}...")
            
            related = get_related_videos(api_key, video['video_id'], max_results=max_recommendations)
            print(f"    Found {len(related)} related videos")
            
            new_count = 0
            for rel_video in related:
                if rel_video['video_id'] in processed_video_ids:
                    continue
                
                rel_video['depth'] = current_depth
                rel_video['recommended_from'] = video['title']
                processed_video_ids.add(rel_video['video_id'])
                next_depth_videos.append(rel_video)
                all_results.append(rel_video)
                new_count += 1
            
            print(f"    Added {new_count} new videos")
        
        # Batch fetch details for current depth videos
        if next_depth_videos:
            video_ids_to_fetch = [v['video_id'] for v in next_depth_videos]
            new_details = get_video_details(api_key, video_ids_to_fetch)
            
            for result in next_depth_videos:
                vid = result['video_id']
                if vid in new_details:
                    details = new_details[vid]
                    result['views'] = details.get('views', '')
                    result['category_id'] = details.get('category_id', '')
                    result['tags'] = details.get('tags', '')
                    result['thumbnail_url'] = details.get('thumbnail_url', '')
                    result['category_name'] = CATEGORY_NAMES.get(str(details.get('category_id', '')), 'Unknown')
                else:
                    result['category_id'] = ''
                    result['tags'] = ''
                    result['thumbnail_url'] = ''
                    result['category_name'] = 'Unknown'
        
        current_depth_videos = next_depth_videos
        
        if not current_depth_videos:
            print("No more videos to process")
            break
    
    # Step 4: Write to CSV
    print(f"\nTotal videos collected: {len(all_results)}")
    
    fieldnames = ['title', 'channel', 'views', 'url', 'depth', 'recommended_from', 
                  'category_id', 'category_name', 'tags', 'thumbnail_url']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in all_results:
            writer.writerow({
                'title': result.get('title', ''),
                'channel': result.get('channel', ''),
                'views': result.get('views', ''),
                'url': build_video_url(result.get('video_id', '')),
                'depth': result.get('depth', 0),
                'recommended_from': result.get('recommended_from', ''),
                'category_id': result.get('category_id', ''),
                'category_name': result.get('category_name', ''),
                'tags': result.get('tags', ''),
                'thumbnail_url': result.get('thumbnail_url', '')
            })
    
    print(f"Saved enriched results to: {output_file}")
    
    # Print summary
    depth_counts = {}
    for r in all_results:
        d = r['depth']
        depth_counts[d] = depth_counts.get(d, 0) + 1
    
    print("\nVideos by depth:")
    for d in sorted(depth_counts.keys()):
        print(f"  Depth {d}: {depth_counts[d]}")


def main():
    from settings import SEARCH_QUERY, MAX_INITIAL, MAX_RECOMMENDATIONS, DEPTH
    
    print(f"Starting YouTube API search...")
    print(f"Query: {SEARCH_QUERY}")
    print(f"Max initial: {MAX_INITIAL}, Max recs per video: {MAX_RECOMMENDATIONS}, Depth: {DEPTH}")
    print(f"Output: {OUTPUT_FILE_ENRICHED}")
    print()
    
    print("WARNING: YouTube Data API's relatedToVideoId endpoint was deprecated in Aug 2023")
    print("         and returns empty results. This script will NOT collect related videos.")
    print("         Only the initial search results will be saved.")
    print()
    
    search_youtube_api(
        query=SEARCH_QUERY,
        max_initial=MAX_INITIAL,
        max_recommendations=MAX_RECOMMENDATIONS,
        depth=DEPTH,
        output_file=OUTPUT_FILE_ENRICHED
    )


if __name__ == '__main__':
    main()