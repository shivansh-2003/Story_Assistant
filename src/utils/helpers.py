# utils/helpers.py
from typing import Dict, Any, List, Optional, Union, Tuple
import re
import json
import uuid
import hashlib
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)

# ===== TEXT PROCESSING UTILITIES =====

def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_dialogue(text: str) -> List[str]:
    """
    Extract dialogue from text content
    
    Args:
        text: Text content
        
    Returns:
        List of dialogue lines
    """
    # Pattern to match quoted dialogue
    dialogue_pattern = r'"([^"]*)"'
    
    dialogues = re.findall(dialogue_pattern, text)
    
    # Clean and filter out empty dialogues
    dialogues = [clean_text(d) for d in dialogues if d.strip()]
    
    return dialogues

def count_words(text: str) -> int:
    """
    Count words in text
    
    Args:
        text: Text content
        
    Returns:
        Word count
    """
    if not text:
        return 0
    
    # Split by whitespace and count non-empty words
    words = [word for word in text.split() if word.strip()]
    return len(words)

def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Estimate reading time in minutes
    
    Args:
        text: Text content
        words_per_minute: Average reading speed
        
    Returns:
        Estimated reading time in minutes
    """
    word_count = count_words(text)
    return max(1, round(word_count / words_per_minute))

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum allowed length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_character_names(text: str) -> List[str]:
    """
    Extract potential character names from text (simple heuristic)
    
    Args:
        text: Text content
        
    Returns:
        List of potential character names
    """
    # Pattern for capitalized words that might be names
    name_pattern = r'\b[A-Z][a-z]{2,}\b'
    
    potential_names = re.findall(name_pattern, text)
    
    # Filter out common words that aren't names
    common_words = {
        'The', 'And', 'But', 'For', 'Nor', 'Yet', 'So', 'Or',
        'Chapter', 'Once', 'Then', 'When', 'Where', 'How', 'Why',
        'This', 'That', 'These', 'Those', 'Before', 'After'
    }
    
    names = [name for name in set(potential_names) if name not in common_words]
    
    return names

# ===== CONTENT VALIDATION UTILITIES =====

def validate_story_content(content: str) -> Dict[str, Any]:
    """
    Validate story content for quality and appropriateness
    
    Args:
        content: Story content to validate
        
    Returns:
        Validation results
    """
    issues = []
    warnings = []
    
    # Check minimum length
    word_count = count_words(content)
    if word_count < 50:
        issues.append("Content too short (minimum 50 words)")
    
    # Check for repetitive content
    sentences = re.split(r'[.!?]+', content)
    if len(sentences) > 1:
        unique_sentences = set(s.strip().lower() for s in sentences if s.strip())
        if len(unique_sentences) < len(sentences) * 0.8:
            warnings.append("Content may be repetitive")
    

    
    # Check dialogue formatting
    dialogues = extract_dialogue(content)
    if dialogues and len(dialogues) > word_count * 0.5:  # More than 50% dialogue
        warnings.append("Content is heavily dialogue-based")
    
    return {
        "valid": len(issues) == 0,
        "word_count": word_count,
        "issues": issues,
        "warnings": warnings,
        "dialogue_count": len(dialogues)
    }

def check_content_appropriateness(content: str, target_audience: str = "adult") -> Dict[str, Any]:
    """
    Check content appropriateness for target audience
    
    Args:
        content: Content to check
        target_audience: Target audience (children, young_adult, adult)
        
    Returns:
        Appropriateness check results
    """
    concerns = []
    
    # Define inappropriate content patterns by audience
    inappropriate_patterns = {
        "children": [
            r'\b(?:violence|blood|death|kill)\b',
            r'\b(?:scary|frightening|terrifying)\b'
        ],
        "young_adult": [
            r'\b(?:explicit|graphic)\b'
        ],
        "adult": []  # No restrictions for adult content
    }
    
    patterns = inappropriate_patterns.get(target_audience, [])
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            concerns.append(f"Potentially inappropriate content for {target_audience}: {', '.join(set(matches))}")
    
    return {
        "appropriate": len(concerns) == 0,
        "target_audience": target_audience,
        "concerns": concerns
    }

# ===== ID AND SLUG UTILITIES =====

def generate_story_slug(title: str) -> str:
    """
    Generate URL-friendly slug from story title
    
    Args:
        title: Story title
        
    Returns:
        URL-friendly slug
    """
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'\s+', '-', slug)
    slug = slug.strip('-')
    
    # Truncate if too long
    if len(slug) > 50:
        slug = slug[:50].rstrip('-')
    
    return slug or "untitled"

def generate_task_id() -> str:
    """Generate unique task ID"""
    return str(uuid.uuid4())

def generate_short_id(length: int = 8) -> str:
    """
    Generate short unique ID
    
    Args:
        length: Length of ID
        
    Returns:
        Short unique ID
    """
    return uuid.uuid4().hex[:length]

# ===== JSON UTILITIES =====

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string
    
    Args:
        json_str: JSON string
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely serialize object to JSON
    
    Args:
        obj: Object to serialize
        default: Default JSON string if serialization fails
        
    Returns:
        JSON string
    """
    try:
        return json.dumps(obj, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return default

# ===== CACHING UTILITIES =====

def cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Cache key string
    """
    # Create a string representation of all arguments
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
    
    key_string = "|".join(key_parts)
    
    # Hash for consistent length
    return hashlib.md5(key_string.encode()).hexdigest()

def timed_cache(ttl_seconds: int):
    """
    Decorator for time-based caching
    
    Args:
        ttl_seconds: Time to live in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func):
        cache = {}
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache_key(*args, **kwargs)
            now = time.time()
            
            # Check if cached result is still valid
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    return result
            
            # Call function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            cache[key] = (result, now)
            
            # Clean old entries
            keys_to_remove = [
                k for k, (_, ts) in cache.items()
                if now - ts >= ttl_seconds
            ]
            for k in keys_to_remove:
                del cache[k]
            
            return result
        
        return wrapper
    return decorator

# ===== DATE AND TIME UTILITIES =====

def format_timestamp(dt: datetime = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format timestamp
    
    Args:
        dt: DateTime object (defaults to now)
        format_str: Format string
        
    Returns:
        Formatted timestamp
    """
    if dt is None:
        dt = datetime.utcnow()
    
    return dt.strftime(format_str)

def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse timestamp string
    
    Args:
        timestamp_str: Timestamp string
        
    Returns:
        DateTime object or None if parsing fails
    """
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    return None

def time_ago(dt: datetime) -> str:
    """
    Get human-readable time ago string
    
    Args:
        dt: DateTime object
        
    Returns:
        Human-readable time ago string
    """
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 365:
        return f"{diff.days // 365} year{'s' if diff.days // 365 > 1 else ''} ago"
    elif diff.days > 30:
        return f"{diff.days // 30} month{'s' if diff.days // 30 > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

# ===== ERROR HANDLING UTILITIES =====

def safe_execute(func, *args, default=None, log_errors=True, **kwargs):
    """
    Safely execute function with error handling
    
    Args:
        func: Function to execute
        *args: Function arguments
        default: Default return value on error
        log_errors: Whether to log errors
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.error(f"Error executing {func.__name__}: {e}")
        return default

async def safe_execute_async(func, *args, default=None, log_errors=True, **kwargs):
    """
    Safely execute async function with error handling
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.error(f"Error executing {func.__name__}: {e}")
        return default

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator for retrying failed operations
    
    Args:
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                        await asyncio.sleep(delay * (attempt + 1))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator

# ===== PROGRESS TRACKING UTILITIES =====

class ProgressTracker:
    """Simple progress tracker for long-running operations"""
    
    def __init__(self, total_steps: int, task_id: str = None):
        self.total_steps = total_steps
        self.current_step = 0
        self.task_id = task_id or generate_task_id()
        self.start_time = time.time()
        self.step_history: List[Dict[str, Any]] = []
    
    def update(self, step_name: str = None, increment: int = 1):
        """Update progress"""
        self.current_step += increment
        
        step_info = {
            "step": self.current_step,
            "name": step_name,
            "timestamp": time.time(),
            "percentage": min(100, (self.current_step / self.total_steps) * 100)
        }
        
        self.step_history.append(step_info)
        
        if step_name:
            logger.info(f"Progress {self.task_id}: {step_info['percentage']:.1f}% - {step_name}")
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress info"""
        elapsed = time.time() - self.start_time
        percentage = min(100, (self.current_step / self.total_steps) * 100)
        
        # Estimate completion time
        if percentage > 0:
            estimated_total = elapsed / (percentage / 100)
            estimated_remaining = estimated_total - elapsed
        else:
            estimated_remaining = None
        
        return {
            "task_id": self.task_id,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "percentage": percentage,
            "elapsed_seconds": elapsed,
            "estimated_remaining_seconds": estimated_remaining,
            "latest_step": self.step_history[-1] if self.step_history else None
        }
    
    def is_complete(self) -> bool:
        """Check if progress is complete"""
        return self.current_step >= self.total_steps

# ===== FILE UTILITIES =====

def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
    """
    try:
        return Path(file_path).stat().st_size
    except FileNotFoundError:
        return 0

# ===== CONFIGURATION UTILITIES =====

def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple configuration dictionaries
    
    Args:
        *configs: Configuration dictionaries to merge
        
    Returns:
        Merged configuration
    """
    result = {}
    
    for config in configs:
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_configs(result[key], value)
            else:
                result[key] = value
    
    return result

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten nested dictionary
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)

# ===== BATCH PROCESSING UTILITIES =====

async def process_in_batches(
    items: List[Any],
    processor_func,
    batch_size: int = 10,
    max_concurrent: int = 3
) -> List[Any]:
    """
    Process items in batches with concurrency control
    
    Args:
        items: Items to process
        processor_func: Async function to process each item
        batch_size: Size of each batch
        max_concurrent: Maximum concurrent batches
        
    Returns:
        List of processed results
    """
    results = []
    
    # Create batches
    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    
    # Process batches with concurrency limit
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_batch(batch):
        async with semaphore:
            batch_results = []
            for item in batch:
                try:
                    result = await processor_func(item)
                    batch_results.append(result)
                except Exception as e:
                    logger.error(f"Failed to process item: {e}")
                    batch_results.append(None)
            return batch_results
    
    # Execute all batches
    batch_tasks = [process_batch(batch) for batch in batches]
    batch_results = await asyncio.gather(*batch_tasks)
    
    # Flatten results
    for batch_result in batch_results:
        results.extend(batch_result)
    
    return results
