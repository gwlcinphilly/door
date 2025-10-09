"""
Standalone source detection module for FastAPI application.
This module provides comprehensive metadata extraction from various sources including YouTube, Xiaohongshu, Xiaoyuzhou FM, and general web content.
"""
from datetime import datetime, timezone
from typing import Dict, Optional
from .config import is_render
from .source import (
    is_youtube_url,
    extract_youtube_metadata,
    extract_clean_youtube_url,
    is_xiaohongshu_text,
    extract_xiaohongshu_metadata,
    is_xiaoyuzhou_url,
    extract_xiaoyuzhou_metadata,
    extract_web_metadata,
    extract_clean_url
)


def detect_source(url: str) -> Dict:
    """
    Detect the source type of a given URL and extract relevant metadata.
    
    Args:
        url (str): The URL or text to analyze
        
    Returns:
        dict: A dictionary containing metadata about the URL:
            - success: Whether the detection was successful
            - source: The source type (youtube, xiaohongshu, xiaoyuzhou, web)
            - tag: The content tag
            - title: The extracted title (if available)
            - content: The extracted content (if available)
            - date: The publication date (if available)
            - url: The final URL used (extracted or original)
            - error: Error message if detection failed
    """
    try:
        # Default values for all URLs
        result = {
            'success': True,
            'source': 'web',
            'tag': 'news',
            'title': '',
            'content': '',
            'date': datetime.now(timezone.utc),
            'url': url,  # Default to original URL
        }
        
        # STEP 1: Extract the correct URL from the input string
        final_url = url
        
        # Try to extract clean URL from text (handles cases like Xiaohongshu content)
        clean_url = extract_clean_url(url)
        if clean_url:
            final_url = clean_url
            result['url'] = final_url
            print(f"Extracted clean URL: {url} -> {final_url}")
        
        # Try to extract YouTube URL if it's a YouTube link
        if is_youtube_url(url):
            youtube_url = extract_clean_youtube_url(url)
            if youtube_url:
                final_url = youtube_url
                result['url'] = final_url
                print(f"Extracted YouTube URL: {url} -> {final_url}")
        
        # Check if running on Render - skip metadata extraction if so
        if is_render():
            print("Running on Render - skipping metadata extraction, saving URL only")
            result['url'] = final_url
            result['title'] = f"Entry from {final_url}"
            result['content'] = f"URL saved from Render: {final_url}"
            return result
        
        # STEP 2: Extract metadata based on the final URL
        # Check if URL contains Xiaohongshu link
        if is_xiaohongshu_text(final_url):
            xiaohongshu_data = extract_xiaohongshu_metadata(final_url)
            if xiaohongshu_data:
                result.update({
                    'title': xiaohongshu_data.get('title', ''),
                    'content': xiaohongshu_data.get('content', ''),
                    'url': xiaohongshu_data.get('url', final_url)
                })
        
        # Check if URL is from YouTube
        elif is_youtube_url(final_url):
            youtube_data = extract_youtube_metadata(final_url)
            if youtube_data:
                result.update({
                    'title': youtube_data.get('title', ''),
                    'content': youtube_data.get('content', ''),
                    'url': final_url
                })
        
        # Check if URL is from Xiaoyuzhou FM
        elif is_xiaoyuzhou_url(final_url):
            xiaoyuzhou_data = extract_xiaoyuzhou_metadata(final_url)
            if xiaoyuzhou_data:
                result.update({
                    'title': xiaoyuzhou_data.get('title', ''),
                    'content': xiaoyuzhou_data.get('content', ''),
                    'url': final_url
                })
        
        # For all other URLs, try to extract web metadata
        else:
            web_data = extract_web_metadata(final_url)
            if web_data:
                result.update({
                    'title': web_data.get('title', ''),
                    'content': web_data.get('content', ''),
                    'url': final_url
                })
            else:
                # If no URL found, treat as text content
                result['title'] = "Text Content"
                result['content'] = url
                result['source'] = 'text'
                result['tag'] = 'note'
        
        return result
        
    except Exception as e:
        print(f"Error in detect_source: {e}")
        return {
            'success': False,
            'source': 'unknown',
            'tag': 'error',
            'title': f"Error processing URL: {str(e)}",
            'content': f"Failed to process URL: {url}",
            'date': datetime.now(timezone.utc),
            'url': url,
            'error': str(e)
        }
