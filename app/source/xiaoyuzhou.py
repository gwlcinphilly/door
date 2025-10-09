"""
Xiaoyuzhou FM podcast source detection and metadata extraction module.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone


def is_xiaoyuzhou_url(url):
    """
    Check if a URL is from Xiaoyuzhou FM (podcast platform).
    
    Args:
        url (str): The URL to check
        
    Returns:
        bool: True if the URL is from Xiaoyuzhou FM
    """
    return 'xiaoyuzhoufm.com' in url.lower()


def extract_xiaoyuzhou_metadata(url):
    """
    Extract metadata from a Xiaoyuzhou FM podcast URL.
    
    Args:
        url (str): The Xiaoyuzhou FM URL
        
    Returns:
        dict: A dictionary containing podcast metadata:
            - source: 'xiaoyuzhou'
            - tag: 'podcast'
            - title: The podcast episode title (if available)
            - content: The podcast description (if available)
            - date: The publication date (if available)
    """
    result = {
        'source': 'xiaoyuzhou',
        'title': '',
        'content': '',
        'date': datetime.now(timezone.utc),
    }
    
    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title - try multiple selectors
        title_selectors = [
            'h1.episode-title',
            'h1[class*="title"]',
            'h1',
            '.episode-info h1',
            '.podcast-title',
            'title'
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element and title_element.get_text().strip():
                result['title'] = title_element.get_text().strip()
                break
        
        # If no title found, create a default one
        if not result['title']:
            episode_id = url.split('/')[-1] if '/' in url else 'Unknown'
            result['title'] = f"Xiaoyuzhou FM Podcast Episode: {episode_id}"
        
        # Extract description/content
        content_selectors = [
            '.episode-description',
            '.episode-summary',
            '.podcast-description',
            '.content',
            'meta[name="description"]'
        ]
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                if content_element.name == 'meta':
                    content_text = content_element.get('content', '').strip()
                else:
                    content_text = content_element.get_text().strip()
                
                if content_text:
                    result['content'] = content_text
                    break
        
        # If no content found, create a default description
        if not result['content']:
            result['content'] = f"Podcast episode from Xiaoyuzhou FM. URL: {url}"
        
        # Try to extract publication date
        date_selectors = [
            '.episode-date',
            '.publish-date',
            '.date',
            'time[datetime]',
            'meta[property="article:published_time"]'
        ]
        
        for selector in date_selectors:
            date_element = soup.select_one(selector)
            if date_element:
                if date_element.name == 'meta':
                    date_text = date_element.get('content', '').strip()
                elif date_element.name == 'time':
                    date_text = date_element.get('datetime', '').strip()
                else:
                    date_text = date_element.get_text().strip()
                
                if date_text:
                    try:
                        # Try to parse the date
                        from dateutil import parser
                        result['date'] = parser.parse(date_text).replace(tzinfo=timezone.utc)
                    except:
                        # If parsing fails, keep the default date
                        pass
                    break
        
        print(f"Xiaoyuzhou FM metadata extracted: {result['title']}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Xiaoyuzhou FM content: {e}")
        result['title'] = f"Xiaoyuzhou FM Podcast (Failed to fetch: {str(e)})"
        result['content'] = f"Failed to fetch podcast metadata. URL: {url}"
    except Exception as e:
        print(f"Error parsing Xiaoyuzhou FM content: {e}")
        result['title'] = f"Xiaoyuzhou FM Podcast (Parse error: {str(e)})"
        result['content'] = f"Failed to parse podcast metadata. URL: {url}"
    
    return result
