"""
Source detection modules for different platforms.
This package contains individual modules for detecting and extracting metadata from various sources.
"""

from .youtube import is_youtube_url, extract_youtube_metadata, extract_clean_youtube_url
from .xiaohongshu import is_xiaohongshu_text, extract_xiaohongshu_metadata
from .xiaoyuzhou import is_xiaoyuzhou_url, extract_xiaoyuzhou_metadata
from .web import extract_web_metadata, extract_clean_url

__all__ = [
    'is_youtube_url',
    'extract_youtube_metadata', 
    'extract_clean_youtube_url',
    'is_xiaohongshu_text',
    'extract_xiaohongshu_metadata',
    'is_xiaoyuzhou_url',
    'extract_xiaoyuzhou_metadata',
    'extract_web_metadata',
    'extract_clean_url'
]
