"""
Service for extracting product images from URLs.
Supports Open Graph image extraction and fallback strategies.
"""
import logging
from typing import Optional
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


async def extract_og_image(url: str, timeout: float = 5.0) -> Optional[str]:
    """
    Extract Open Graph image from a product URL.
    
    Args:
        url: Product page URL
        timeout: Request timeout in seconds
        
    Returns:
        Image URL if found, None otherwise
    """
    if not url:
        return None
    
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            logger.warning(f"Invalid URL format: {url}")
            return None
        
        # Fetch the page
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Try Open Graph image first
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                image_url = og_image.get('content')
                # Make absolute URL if relative
                if not urlparse(image_url).netloc:
                    image_url = urljoin(url, image_url)
                logger.info(f"Found OG image for {url}: {image_url}")
                return image_url
            
            # Try Twitter Card image as fallback
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                image_url = twitter_image.get('content')
                if not urlparse(image_url).netloc:
                    image_url = urljoin(url, image_url)
                logger.info(f"Found Twitter image for {url}: {image_url}")
                return image_url
            
            # Try to find a large image in the page
            # Look for common product image patterns
            img_tags = soup.find_all('img', src=True)
            for img in img_tags:
                src = img.get('src', '')
                # Skip small images, icons, logos
                if any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'thumb']):
                    continue
                # Prefer images with product-related classes/ids
                classes = img.get('class', [])
                img_id = img.get('id', '')
                if any(keyword in str(classes).lower() or keyword in img_id.lower() 
                       for keyword in ['product', 'main', 'hero', 'featured']):
                    image_url = src
                    if not urlparse(image_url).netloc:
                        image_url = urljoin(url, image_url)
                    logger.info(f"Found product image for {url}: {image_url}")
                    return image_url
            
            logger.warning(f"No image found for {url}")
            return None
            
    except httpx.TimeoutException:
        logger.warning(f"Timeout fetching image from {url}")
        return None
    except httpx.HTTPError as e:
        logger.warning(f"HTTP error fetching image from {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error extracting image from {url}: {e}", exc_info=True)
        return None


async def get_product_image(url: Optional[str], image_url: Optional[str] = None) -> Optional[str]:
    """
    Get product image using multiple strategies.
    
    Priority:
    1. Use provided image_url if available
    2. Extract OG image from URL
    3. Return None (frontend will handle fallback)
    
    Args:
        url: Product page URL
        image_url: Direct image URL (from LLM)
        
    Returns:
        Image URL if found, None otherwise
    """
    # First priority: Use LLM-provided image URL
    if image_url:
        logger.info(f"Using LLM-provided image URL: {image_url}")
        return image_url
    
    # Second priority: Extract from product URL
    if url:
        return await extract_og_image(url)
    
    return None

