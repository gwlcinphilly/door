"""
Xiaohongshu (Little Red Book) source detection and metadata extraction module.
"""
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone


def is_xiaohongshu_text(text):
    """
    Check if text contains Xiaohongshu content or links.
    
    Args:
        text (str): The text to check
        
    Returns:
        bool: True if the text contains Xiaohongshu content
    """
    xiaohongshu_patterns = [
        r'xiaohongshu\.com',
        r'xhslink\.com',
        r'小红书',
        r'xiaohongshu',
    ]
    
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in xiaohongshu_patterns)


def extract_xiaohongshu_link(text):
    """
    Extract Xiaohongshu link from text.
    
    Args:
        text (str): The text containing Xiaohongshu link
        
    Returns:
        str: The extracted link, or None if not found
    """
    # Pattern to match Xiaohongshu URLs (including xhslink.com)
    xiaohongshu_pattern = r'https?://[^\s]*(?:xiaohongshu\.com|xhslink\.com)[^\s]*'
    match = re.search(xiaohongshu_pattern, text)
    
    if match:
        return match.group(0)
    
    return None


def extract_xiaohongshu_metadata(text):
    """
    Extract metadata from Xiaohongshu content.
    
    Args:
        text (str): The text containing Xiaohongshu content
        
    Returns:
        dict: A dictionary containing Xiaohongshu metadata:
            - source: 'xiaohongshu'
            - tag: 'social'
            - title: The content title (if available)
            - content: The extracted content or original text
            - date: The current date
            - url: The extracted Xiaohongshu URL (if found)
    """
    result = {
        'source': 'xiaohongshu',
        'title': '',
        'content': text,
        'date': datetime.now(timezone.utc),
        'url': text,  # Default to original text
    }
    
    # Try to extract link and fetch metadata
    link = extract_xiaohongshu_link(text)
    if link:
        # Update the URL to the extracted link
        result['url'] = link
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
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to extract title from various selectors
            title_selectors = [
                'title',
                'h1',
                '.title',
                '.post-title',
                'meta[property="og:title"]'
            ]
            
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    if title_element.name == 'meta':
                        title_text = title_element.get('content', '').strip()
                    else:
                        title_text = title_element.get_text().strip()
                    
                    if title_text and title_text not in ['小红书', 'Xiaohongshu']:
                        result['title'] = title_text
                        break
            
            # If no title found, create a default one
            if not result['title']:
                result['title'] = "Xiaohongshu Post"
            
            # Update content to be more descriptive
            result['content'] = f"Xiaohongshu post: {result['title']}"
            
            print(f"Xiaohongshu metadata extracted: {result['title']}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Xiaohongshu content: {e}")
            result['title'] = "Xiaohongshu Post (Failed to fetch)"
            result['content'] = f"Failed to fetch Xiaohongshu content. URL: {link}"
        except Exception as e:
            print(f"Error parsing Xiaohongshu content: {e}")
            result['title'] = "Xiaohongshu Post (Parse error)"
            result['content'] = f"Failed to parse Xiaohongshu content. URL: {link}"
    else:
        # No link found, treat as text content
        result['title'] = "Xiaohongshu Content"
        result['content'] = text
    
    return result
