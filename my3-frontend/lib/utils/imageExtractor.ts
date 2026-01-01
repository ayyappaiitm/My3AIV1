/**
 * Client-side utility for extracting Open Graph images from URLs.
 * Used as a fallback when backend doesn't provide image_url.
 */

export async function extractOgImage(url: string): Promise<string | null> {
  if (!url) return null

  try {
    // Use a CORS proxy or direct fetch (may fail due to CORS)
    // For production, this should ideally be done server-side
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      },
      mode: 'cors',
    })

    if (!response.ok) {
      return null
    }

    const html = await response.text()
    
    // Parse HTML to find og:image
    const ogImageMatch = html.match(/<meta\s+property=["']og:image["']\s+content=["']([^"']+)["']/i)
    if (ogImageMatch && ogImageMatch[1]) {
      const imageUrl = ogImageMatch[1]
      // Make absolute URL if relative
      if (imageUrl.startsWith('http')) {
        return imageUrl
      }
      try {
        const baseUrl = new URL(url)
        return new URL(imageUrl, baseUrl.origin).href
      } catch {
        return imageUrl
      }
    }

    // Try Twitter card image as fallback
    const twitterImageMatch = html.match(/<meta\s+name=["']twitter:image["']\s+content=["']([^"']+)["']/i)
    if (twitterImageMatch && twitterImageMatch[1]) {
      const imageUrl = twitterImageMatch[1]
      if (imageUrl.startsWith('http')) {
        return imageUrl
      }
      try {
        const baseUrl = new URL(url)
        return new URL(imageUrl, baseUrl.origin).href
      } catch {
        return imageUrl
      }
    }

    return null
  } catch (error) {
    // CORS or other errors - return null, will use fallback
    console.warn('Failed to extract OG image:', error)
    return null
  }
}

/**
 * Get Unsplash image URL for a category (fallback)
 */
export function getUnsplashImageUrl(category: string, title: string): string {
  const searchTerm = category || title || 'gift'
  // Using Unsplash Source API (no key required for basic usage)
  return `https://source.unsplash.com/400x300/?${encodeURIComponent(searchTerm)}`
}

