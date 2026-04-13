from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv
import time


def search_youtube(query: str, output_file: str = "youtube_results.csv") -> None:
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    
    driver = webdriver.Chrome(options=options)
    
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
        
        results = []
        for item in raw_items:
            text = item.get('text', '')
            url = item.get('url', '')
            lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
            
            title = ""
            views_date = ""
            channel = ""
            
            for i, line in enumerate(lines):
                if "views" in line.lower() and i > 0:
                    title = lines[i - 1]
                    views_date = line
                    for j in range(i + 1, len(lines)):
                        if lines[j] and not lines[j][0].isdigit():
                            channel = lines[j]
                            break
                    break
            
            if not title:
                if len(lines) >= 3 and "views" in lines[1].lower():
                    title = lines[0]
                    views_date = lines[1]
                    channel = lines[3] if len(lines) > 3 else lines[2]
            
            if title and url:
                results.append({
                    "title": title,
                    "channel": channel,
                    "views": views_date,
                    "url": url
                })
        
        print(f"Found {len(results)} video elements")
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "channel", "views", "url"])
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Saved {len(results)} results to {output_file}")
        time.sleep(2)
    finally:
        driver.quit()


if __name__ == "__main__":
    search_youtube("python tutorials")