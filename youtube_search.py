from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv
import time


def parse_video_item(item, current_url):
    text = item.get('text', '')
    url = item.get('url', '')
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    
    title = ""
    views = ""
    channel = ""
    
    for i, line in enumerate(lines):
        if 'views' in line.lower():
            if i > 0:
                title = lines[i - 1]
            views = line
            for j in range(i + 1, len(lines)):
                if lines[j] and not lines[j][0].isdigit():
                    channel = lines[j]
                    break
            break
    
    if not title and len(lines) >= 3:
        if 'views' in lines[1].lower():
            title = lines[0]
            views = lines[1]
            channel = lines[2]
        else:
            title = lines[0]
            views = lines[1]
            channel = lines[2] if len(lines) > 2 else ""
    
    if not title and len(lines) >= 2:
        title = lines[0]
        views = lines[1]
        channel = ""
    
    if title and url and url != current_url:
        return {"title": title, "channel": channel, "views": views, "url": url}
    return None


def search_youtube(query: str, output_file: str = "youtube_results.csv", max_initial: int = 10, max_recommendations: int = 10) -> None:
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    
    driver = webdriver.Chrome(options=options)
    
    all_results = []
    
    try:
        driver.get(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
        time.sleep(8)
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        raw_items = driver.execute_script("""
            var results = [];
            var items = document.querySelectorAll('ytd-video-renderer');
            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                var links = item.querySelectorAll('a');
                var url = '';
                for (var j = 0; j < links.length; j++) {
                    if (links[j].href && links[j].href.indexOf('watch?v=') > -1) {
                        url = links[j].href.split('&')[0];
                        break;
                    }
                }
                results.push({text: item.innerText, url: url});
            }
            return results;
        """)
        
        initial_videos = []
        for item in raw_items:
            parsed = parse_video_item(item, "")
            if parsed:
                parsed["depth"] = 0
                parsed["recommended_from"] = "initial"
                initial_videos.append(parsed)
        
        initial_videos = initial_videos[:max_initial]
        all_results.extend(initial_videos)
        
        print(f"Found {len(initial_videos)} initial videos")
        
        for video in initial_videos:
            print(f"Getting recommendations from: {video['title'][:50]}...")
            
            try:
                driver.get(video["url"])
                time.sleep(6)
                
                try:
                    driver.execute_script("window.scrollTo(0, 300);")
                    time.sleep(2)
                    driver.execute_script("window.scrollTo(0, 800);")
                    time.sleep(2)
                except:
                    pass
                
                rec_raw = driver.execute_script("""
                    var results = [];
                    var containers = document.querySelectorAll('#secondary, ytd-watch-next-secondary-results-renderer, #related');
                    for (var c = 0; c < containers.length; c++) {
                        var links = containers[c].querySelectorAll('a[href*="/watch?v="]');
                        for (var i = 0; i < links.length; i++) {
                            if (links[i].href && links[i].href.indexOf('watch?v=') > -1) {
                                var url = links[i].href.split('&')[0];
                                results.push({text: links[i].innerText, url: url});
                            }
                        }
                    }
                    return results;
                """)
                
                rec_count = 0
                seen_urls = set()
                
                for item in rec_raw:
                    if rec_count >= max_recommendations:
                        break
                    
                    text = item.get('text', '')
                    url = item.get('url', '')
                    
                    text_clean = text.replace('\xa0', ' ').replace('\n', ' ').strip()
                    
                    if len(text_clean) < 15:
                        continue
                    
                    if text_clean[:5].isdigit():
                        continue
                    
                    if ':' in text_clean[:15]:
                        continue
                    
                    if url == video["url"] or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    parsed = parse_video_item(item, video["url"])
                    if parsed:
                        parsed["depth"] = 1
                        parsed["recommended_from"] = video["title"]
                        all_results.append(parsed)
                        rec_count += 1
                
                print(f"  Found {rec_count} recommendations")
                
            except Exception as e:
                print(f"  Error: {e}")
        
        print(f"Total: {len(all_results)} video elements")
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "channel", "views", "url", "depth", "recommended_from"])
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"Saved {len(all_results)} results to {output_file}")
        time.sleep(2)
    finally:
        driver.quit()


if __name__ == "__main__":
    search_youtube("python tutorials")