"""
YouTube source detection and metadata extraction module.
"""
import re
import yt_dlp
from datetime import datetime, timezone


def is_youtube_url(url):
    """
    Check if a URL is from YouTube.
    
    Args:
        url (str): The URL to check
        
    Returns:
        bool: True if the URL is from YouTube
    """
    youtube_patterns = [
        r'youtube\.com/watch\?v=',
        r'youtu\.be/',
        r'youtube\.com/embed/',
        r'youtube\.com/v/',
        r'youtube\.com/shorts/',
    ]
    
    return any(re.search(pattern, url, re.IGNORECASE) for pattern in youtube_patterns)


def extract_youtube_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    
    Args:
        url (str): The YouTube URL
        
    Returns:
        str: The video ID, or None if not found
    """
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def extract_youtube_metadata(url):
    """
    Extract metadata from a YouTube URL using yt-dlp.
    
    Args:
        url (str): The YouTube URL
        
    Returns:
        dict: A dictionary containing YouTube metadata:
            - source: 'youtube'
            - title: The video title (if available)
            - channel: The channel name (if available)
            - date: The publication date (if available)
    """
    result = {
        'source': 'youtube',
        'title': '',
        'content': '',
        'date': datetime.now(timezone.utc),
    }
    
    video_id = extract_youtube_video_id(url)
    if not video_id:
        result['title'] = f"YouTube Video: {video_id or 'Unknown'} +++++ Unknown Channel"
        return result
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'ignoreerrors': True,  # Ignore format errors
            'no_check_certificate': True,  # Skip certificate verification
            'extractor_retries': 3,  # Retry extraction up to 3 times
            'writethumbnail': False,  # Don't write thumbnail
            'writeinfojson': False,  # Don't write info json
            'skip_download': True,  # Skip downloading any files
            'format': 'best[height<=720]',  # Prefer formats with height <= 720p
            'prefer_insecure': False,  # Use HTTPS when possible
            'socket_timeout': 30,  # Increase timeout
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info:
                # Extract title
                title = info.get('title', '')
                if title:
                    result['title'] = title
                else:
                    result['title'] = f"YouTube Video: {video_id}"
                
                # Extract channel name
                channel = info.get('uploader', '')
                if channel:
                    result['content'] = f"Channel: {channel}"
                
                # Extract description
                description = info.get('description', '')
                if description:
                    # Limit description length
                    if len(description) > 500:
                        description = description[:500] + "..."
                    result['content'] = f"Channel: {channel}\n\nDescription: {description}" if channel else f"Description: {description}"
                
                # Extract upload date
                upload_date = info.get('upload_date')
                if upload_date:
                    try:
                        # Convert YYYYMMDD format to datetime
                        date_obj = datetime.strptime(upload_date, '%Y%m%d')
                        result['date'] = date_obj.replace(tzinfo=timezone.utc)
                    except:
                        pass
                
                print(f"YouTube metadata extracted: {result['title']}")
            else:
                result['title'] = f"YouTube Video: {video_id} +++++ Unknown Channel"
                result['content'] = f"Failed to extract metadata for YouTube video: {url}"
                
    except Exception as e:
        error_msg = str(e)
        print(f"Error extracting YouTube metadata: {error_msg}")
        
        # Try to extract basic info even if detailed extraction fails
        result['title'] = f"YouTube Video: {video_id}"
        result['content'] = f"Channel: Unknown\n\nError: {error_msg}"
        
        # If it's a format error, try with more lenient options
        if any(keyword in error_msg.lower() for keyword in ["format", "not available", "requested format", "unavailable"]):
            try:
                print(f"Retrying with lenient options for video: {video_id}")
                ydl_opts_fallback = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,  # Use flat extraction as fallback
                    'ignoreerrors': True,
                    'no_check_certificate': True,
                    'socket_timeout': 30,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts_fallback) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info and info.get('title'):
                        result['title'] = info.get('title', f"YouTube Video: {video_id}")
                        result['content'] = f"Channel: {info.get('uploader', 'Unknown')}"
                        print(f"Fallback extraction successful: {result['title']}")
                        return result  # Return early on successful fallback
            except Exception as fallback_error:
                print(f"Fallback extraction also failed: {fallback_error}")
                # Try one more time with the most basic extraction
                try:
                    print(f"Trying basic extraction for video: {video_id}")
                    ydl_opts_basic = {
                        'quiet': True,
                        'no_warnings': True,
                        'extract_flat': True,
                        'ignoreerrors': True,
                        'no_check_certificate': True,
                        'socket_timeout': 10,
                        'format': 'worst',  # Try the worst quality format
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts_basic) as ydl:
                        info = ydl.extract_info(url, download=False)
                        if info:
                            result['title'] = info.get('title', f"YouTube Video: {video_id}")
                            result['content'] = f"Channel: {info.get('uploader', 'Unknown')}"
                            print(f"Basic extraction successful: {result['title']}")
                            return result
                except Exception as basic_error:
                    print(f"Basic extraction also failed: {basic_error}")
                
                result['content'] = f"Channel: Unknown\n\nError: {error_msg}\nFallback failed: {str(fallback_error)}"
        else:
            # For other types of errors, provide a more helpful message
            result['content'] = f"Channel: Unknown\n\nError: {error_msg}"
    
    return result


def extract_clean_youtube_url(text):
    """
    Extract a clean YouTube URL from text.
    
    Args:
        text (str): The text containing YouTube URL
        
    Returns:
        str: Clean YouTube URL, or None if not found
    """
    # Pattern to match YouTube URLs
    youtube_pattern = r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})'
    match = re.search(youtube_pattern, text)
    
    if match:
        video_id = match.group(1)
        # Return clean YouTube URL
        return f"https://www.youtube.com/watch?v={video_id}"
    
    return None
