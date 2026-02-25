"""
Import Blogger posts from Google Takeout Atom feed into Jekyll _posts/ directory.
Imports only LIVE posts (skips drafts and comments).
Adds redirect_from for old Blogger URLs.
"""

import xml.etree.ElementTree as ET
import os
import re
import html

FEED_PATH = r"C:\Users\edwab\Downloads\takeout-20260225T115701Z-3-001\Takeout\Blogger\Blogs\Ed_s Blog\feed.atom"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_posts")
BLOGGER_DOMAIN = "pblog.ebaker.me.uk"
SOURCE_NAME = "pblog"  # Identifies which blog these posts came from

NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'blogger': 'http://schemas.google.com/blogger/2018',
}


def slugify(title):
    """Create a URL-friendly slug from a title."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug


def get_text(entry, tag, default=''):
    """Get text content of a child element."""
    el = entry.find(tag, NS)
    if el is not None and el.text:
        return el.text.strip()
    return default


def parse_feed(feed_path):
    """Parse the Atom feed and yield post data."""
    tree = ET.parse(feed_path)
    root = tree.getroot()

    for entry in root.findall('atom:entry', NS):
        entry_type = get_text(entry, 'blogger:type')
        entry_status = get_text(entry, 'blogger:status')

        # Only import LIVE POSTs
        if entry_type != 'POST' or entry_status != 'LIVE':
            continue

        title = get_text(entry, 'atom:title', 'Untitled')
        content = get_text(entry, 'atom:content', '')
        published = get_text(entry, 'atom:published')
        updated = get_text(entry, 'atom:updated')
        blogger_filename = get_text(entry, 'blogger:filename')

        # Parse categories/tags
        tags = []
        for cat in entry.findall('atom:category', NS):
            term = cat.get('term', '')
            if term:
                tags.append(term)

        yield {
            'title': title,
            'content': content,
            'published': published,
            'updated': updated,
            'blogger_filename': blogger_filename,
            'tags': tags,
        }


def create_post(post_data, output_dir):
    """Create a Jekyll post file from parsed post data."""
    published = post_data['published']

    # Parse date: 2009-09-17T12:58:00.003Z
    date_match = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2}:\d{2})', published)
    if not date_match:
        print(f"  Skipping (bad date): {post_data['title']}")
        return None

    year = date_match.group(1)
    month = date_match.group(2)
    day = date_match.group(3)
    time = date_match.group(4)
    date_str = f"{year}-{month}-{day}"

    # Derive slug from blogger_filename or title
    blogger_filename = post_data['blogger_filename']
    if blogger_filename:
        # e.g., /2009/09/prince-william-of-wales.html -> prince-william-of-wales
        slug = os.path.splitext(os.path.basename(blogger_filename))[0]
    else:
        slug = slugify(post_data['title'])

    if not slug:
        slug = slugify(post_data['title']) or 'untitled'

    # Create year subdirectory
    year_dir = os.path.join(output_dir, year)
    os.makedirs(year_dir, exist_ok=True)

    # Build filename
    filename = f"{date_str}-{slug}.html"
    filepath = os.path.join(year_dir, filename)

    # Handle duplicates
    counter = 1
    while os.path.exists(filepath):
        filename = f"{date_str}-{slug}-{counter}.html"
        filepath = os.path.join(year_dir, filename)
        counter += 1

    # Escape title for YAML (wrap in quotes, escape internal quotes)
    safe_title = post_data['title'].replace('"', '\\"')

    # Build front matter
    front_matter = '---\n'
    front_matter += 'layout: post\n'
    front_matter += f'title: "{safe_title}"\n'
    front_matter += f'date: {date_str} {time}\n'
    front_matter += f'source: {SOURCE_NAME}\n'

    if post_data['tags']:
        tag_list = ', '.join(f'"{t}"' for t in post_data['tags'])
        front_matter += f'tags: [{tag_list}]\n'

    # Add redirect_from for old Blogger URL
    if blogger_filename:
        front_matter += f'redirect_from:\n'
        front_matter += f'  - "{blogger_filename}"\n'

    front_matter += '---\n'

    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(front_matter)
        f.write('\n')
        f.write(post_data['content'])
        f.write('\n')

    return filepath


def main():
    print(f"Parsing feed: {FEED_PATH}")
    posts = list(parse_feed(FEED_PATH))
    print(f"Found {len(posts)} live posts")

    created = 0
    skipped = 0
    for post in posts:
        result = create_post(post, OUTPUT_DIR)
        if result:
            created += 1
            print(f"  Created: {os.path.basename(result)}")
        else:
            skipped += 1

    print(f"\nDone! Created {created} posts, skipped {skipped}")
    print(f"Posts written to: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
