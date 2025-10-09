"""
General web source detection and metadata extraction module.
This handles URLs that don't match any specific platform.
"""
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone


def extract_web_metadata(url):
    """
    Extract metadata from a general web URL.
    
    Args:
        url (str): The web URL
        
    Returns:
        dict: A dictionary containing web metadata:
            - source: 'web'
            - tag: 'news'
            - title: The page title (if available)
            - content: The page description (if available)
            - date: The current date
    """
    result = {
        'source': 'web',
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
            'title',
            'h1',
            '.title',
            '.post-title',
            '.article-title',
            'meta[property="og:title"]',
            'meta[name="title"]'
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                if title_element.name == 'meta':
                    title_text = title_element.get('content', '').strip()
                else:
                    title_text = title_element.get_text().strip()
                
                if title_text and len(title_text) > 0:
                    result['title'] = title_text
                    break
        
        # If no title found, create a default one
        if not result['title']:
            domain = re.sub(r'https?://(www\.)?', '', url).split('/')[0]
            result['title'] = f"Web Content from {domain}"
        
        # Extract description/content
        content_selectors = [
            'meta[name="description"]',
            'meta[property="og:description"]',
            '.description',
            '.summary',
            '.content',
            '.article-content',
            'p'
        ]
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                if content_element.name == 'meta':
                    content_text = content_element.get('content', '').strip()
                else:
                    content_text = content_element.get_text().strip()
                
                if content_text and len(content_text) > 10:
                    # Limit content length
                    if len(content_text) > 500:
                        content_text = content_text[:500] + "..."
                    result['content'] = content_text
                    break
        
        # If no content found, create a default description
        if not result['content']:
            result['content'] = f"Web content from {url}"
        
        # Try to extract publication date
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            'time[datetime]',
            '.date',
            '.publish-date',
            '.article-date'
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
        
        print(f"Web metadata extracted: {result['title']}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching web content: {e}")
        domain = re.sub(r'https?://(www\.)?', '', url).split('/')[0]
        result['title'] = f"Web Content from {domain} (Failed to fetch)"
        result['content'] = f"Failed to fetch web content. URL: {url}"
    except Exception as e:
        print(f"Error parsing web content: {e}")
        domain = re.sub(r'https?://(www\.)?', '', url).split('/')[0]
        result['title'] = f"Web Content from {domain} (Parse error)"
        result['content'] = f"Failed to parse web content. URL: {url}"
    
    return result


def extract_clean_url(text):
    """
    Extract a clean URL from text.
    
    Args:
        text (str): The text containing URL
        
    Returns:
        str: Clean URL, or None if not found
    """
    # Pattern to match http/https URLs
    url_pattern = r'https?://[^\s]+'
    match = re.search(url_pattern, text)
    
    if match:
        url = match.group(0)
        # Remove trailing punctuation
        url = re.sub(r'[.,;:!?]+$', '', url)
        return url
    
    return None
