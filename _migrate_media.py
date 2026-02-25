"""
Migrate Blogger-hosted images to local storage.
Downloads images from blogger.googleusercontent.com and bp.blogspot.com,
saves them locally, and updates all post references.
"""

import os
import re
import hashlib
import urllib.request
import urllib.error
import time
import ssl

POSTS_DIR = r"c:\Users\edwab\OneDrive - Natural History Museum\Documents\GitHub\edwbaker.github.io\_posts"
IMGS_DIR = r"c:\Users\edwab\OneDrive - Natural History Museum\Documents\GitHub\edwbaker.github.io\imgs\blogger"
LOCAL_PREFIX = "/imgs/blogger/"

# Match URLs from Blogger/Google image hosting
URL_PATTERN = re.compile(
    r'(https?://(?:blogger\.googleusercontent\.com|[0-9]+\.bp\.blogspot\.com|bp\.blogspot\.com)/[^\s"\'<>]+)'
)

# Create a SSL context that doesn't verify (some old blogger URLs may have cert issues)
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


def url_to_filename(url):
    """Generate a unique filename from a URL, preserving the original extension."""
    # Try to extract original filename from URL
    path = url.split('?')[0]
    basename = os.path.basename(path)
    
    # Clean up the basename
    basename = re.sub(r'[^\w\.\-]', '_', basename)
    
    # If no good extension, default to .jpg
    _, ext = os.path.splitext(basename)
    if ext.lower() not in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'):
        ext = '.jpg'
        basename = basename + ext
    
    # Add hash prefix to avoid collisions
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{url_hash}_{basename}"


def download_image(url, filepath):
    """Download an image from URL to local filepath."""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as response:
            with open(filepath, 'wb') as f:
                f.write(response.read())
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, Exception) as e:
        print(f"  FAILED to download {url}: {e}")
        return False


def main():
    os.makedirs(IMGS_DIR, exist_ok=True)
    
    # Phase 1: Collect all unique URLs across all posts
    print("Phase 1: Scanning posts for Blogger image URLs...")
    all_urls = set()
    post_files = []
    
    for root, dirs, files in os.walk(POSTS_DIR):
        for fname in files:
            if fname.endswith('.html'):
                fpath = os.path.join(root, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                urls = URL_PATTERN.findall(content)
                if urls:
                    post_files.append(fpath)
                    all_urls.update(urls)
    
    print(f"  Found {len(all_urls)} unique URLs across {len(post_files)} posts")
    
    # Phase 2: Download all images
    print("\nPhase 2: Downloading images...")
    url_map = {}  # url -> local path
    downloaded = 0
    failed = 0
    skipped = 0
    
    for i, url in enumerate(sorted(all_urls), 1):
        filename = url_to_filename(url)
        filepath = os.path.join(IMGS_DIR, filename)
        local_url = LOCAL_PREFIX + filename
        
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            url_map[url] = local_url
            skipped += 1
            continue
        
        print(f"  [{i}/{len(all_urls)}] Downloading: {filename}")
        if download_image(url, filepath):
            url_map[url] = local_url
            downloaded += 1
        else:
            failed += 1
            # Still map it so we don't leave broken references
            # but mark it with a comment
            url_map[url] = url  # keep original if download failed
        
        # Be polite
        if i % 10 == 0:
            time.sleep(0.5)
    
    print(f"\n  Downloaded: {downloaded}, Skipped (exists): {skipped}, Failed: {failed}")
    
    # Phase 3: Update posts
    print("\nPhase 3: Updating post references...")
    updated_posts = 0
    
    for root, dirs, files in os.walk(POSTS_DIR):
        for fname in files:
            if fname.endswith('.html'):
                fpath = os.path.join(root, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original = content
                for url, local_path in url_map.items():
                    if url != local_path:  # only replace if we have a local version
                        content = content.replace(url, local_path)
                
                if content != original:
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated_posts += 1
    
    print(f"  Updated {updated_posts} posts")
    
    # Summary
    print(f"\nDone!")
    print(f"  Images saved to: {IMGS_DIR}")
    print(f"  Total unique URLs: {len(all_urls)}")
    print(f"  Successfully migrated: {downloaded + skipped}")
    print(f"  Failed downloads: {failed}")
    

if __name__ == '__main__':
    main()
