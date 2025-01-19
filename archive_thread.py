import requests
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime
import json
import re
import logging
from urllib.parse import urljoin, urlparse, parse_qs
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('thread_archiver.log'),
        logging.StreamHandler()
    ]
)

class VBulletinThreadArchiver:
    def __init__(self, output_dir="archived_threads", delay=3):
        """Initialize the thread archiver"""
        self.output_dir = output_dir
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

    def get_thread_id_from_url(self, url):
        """Extract thread ID from URL."""
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        
        # Common vBulletin URL patterns
        thread_id = None
        if 't' in query:
            thread_id = query['t'][0]
        elif 'threadid' in query:
            thread_id = query['threadid'][0]
        
        if not thread_id:
            raise ValueError("Could not extract thread ID from URL")
            
        return thread_id

    def get_base_url(self, url):
        """Extract base URL from thread URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def archive_thread(self, thread_url):
        """Archive all pages of a single thread."""
        logging.info(f"Starting to archive thread: {thread_url}")
        
        # Extract thread ID and base URL
        thread_id = self.get_thread_id_from_url(thread_url)
        self.base_url = self.get_base_url(thread_url)
        
        thread_data = {
            'title': '',
            'url': thread_url,
            'posts': [],
            'scraped_at': datetime.now().isoformat()
        }
        
        try:
            # Get first page to extract title and find total pages
            response = self.session.get(thread_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get thread title
            first_post = soup.find('li', class_=['postbitim', 'postbit'])
            if first_post:
                title_elem = first_post.find('h2', class_='posttitle')
                if title_elem:
                    thread_data['title'] = title_elem.text.strip()
                    logging.info(f"Thread title: {thread_data['title']}")
            
            # Find all page links
            page_links = set()
            page_links.add(thread_url)  # Add the base URL (this is page 1)
            
            # Look for pagination in pagetitle div which contains "Page X of Y"
            page_title = soup.find('form', {'class': 'pagination'})
            if page_title:
                # Extract total pages from the page title text
                title_text = page_title.find('span').text if page_title.find('span') else ""
                match = re.search(r'Page \d+ of (\d+)', title_text)
                if match:
                    total_pages = int(match.group(1))
                    thread_id = self.get_thread_id_from_url(thread_url)
                    logging.info(f"Found {total_pages} total pages")
                    
                    # Generate URLs for pages 2 onwards (page 1 is the base URL)
                    for page_num in range(2, total_pages + 1):
                        page_url = f"{self.base_url}/showthread.php?t={thread_id}&page={page_num}"
                        page_links.add(page_url)
                        logging.debug(f"Adding page URL: {page_url}")
            else:
                logging.warning("Could not find pagination information")
            
            # Add first page to set
            page_links.add(thread_url)
            
            # Process each page
            for page_url in sorted(page_links):
                logging.info(f"Processing page: {page_url}")
                page_posts = self.scrape_page(page_url)
                thread_data['posts'].extend(page_posts)
                time.sleep(self.delay)
            
            # Save the thread
            if thread_data['posts']:
                self.save_thread(thread_data)
                logging.info(f"Successfully archived thread with {len(thread_data['posts'])} posts")
            else:
                logging.error("No posts found in thread")
                
        except Exception as e:
            logging.error(f"Failed to archive thread: {str(e)}", exc_info=True)
            raise

    def scrape_page(self, page_url):
        """Scrape a single page of the thread."""
        posts = []
        
        try:
            response = self.session.get(page_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all posts
            post_elements = soup.find_all('li', class_=['postbitim', 'postbit'])
            
            for post in post_elements:
                try:
                    post_data = {}
                    
                    # Get timestamp
                    date_elem = post.find('span', class_='date')
                    if date_elem:
                        post_data['timestamp'] = date_elem.text.strip()
                    
                    # Get author
                    username_container = post.find('div', class_='username_container')
                    if username_container:
                        username_elem = username_container.find('a', class_='username')
                        if username_elem:
                            username = username_elem.text.strip()
                            username = re.sub(r'View Profile.*$', '', username, flags=re.DOTALL).strip()
                            post_data['author'] = username
                    
                    # Get post content
                    content_elem = post.find('div', id=lambda x: x and x.startswith('post_message_'))
                    if content_elem:
                        quote_content = content_elem.find('blockquote', class_='postcontent')
                        if quote_content:
                            # Remove quotes to avoid repetition
                            quotes = quote_content.find_all('div', class_='quote')
                            for quote in quotes:
                                quote.decompose()
                            
                            content = quote_content.get_text(strip=True, separator='\n')
                            post_data['content'] = re.sub(r'\s+', ' ', content).strip()
                    
                    if post_data:
                        posts.append(post_data)
                        
                except Exception as e:
                    logging.error(f"Error processing individual post: {e}")
                    continue
            
        except Exception as e:
            logging.error(f"Error scraping page {page_url}: {e}")
        
        return posts

    def save_thread(self, thread_data):
        """Save thread data in both JSON and formatted text files."""
        if not thread_data['title']:
            thread_id = self.get_thread_id_from_url(thread_data['url'])
            safe_title = f"thread_{thread_id}"
        else:
            # Create safe filename from title
            safe_title = re.sub(r'[^\w\s-]', '', thread_data['title'])
            safe_title = re.sub(r'[-\s]+', '-', safe_title).strip('-')
            
            # Add thread ID
            thread_id = self.get_thread_id_from_url(thread_data['url'])
            safe_title = f"{thread_id}-{safe_title}"
        
        # Save JSON version
        json_path = os.path.join(self.output_dir, f"{safe_title}.json")
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(thread_data, f, ensure_ascii=False, indent=2)
            logging.info(f"Saved JSON to {json_path}")
        except Exception as e:
            logging.error(f"Error saving JSON file: {e}")
        
        # Save text version
        txt_path = os.path.join(self.output_dir, f"{safe_title}.txt")
        try:
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"Thread Title: {thread_data['title']}\n")
                f.write(f"Thread URL: {thread_data['url']}\n")
                f.write(f"Scraped at: {thread_data['scraped_at']}\n\n")
                
                for i, post in enumerate(thread_data['posts'], 1):
                    f.write(f"--- Post #{i} ---\n")
                    f.write(f"Author: {post.get('author', 'Unknown')}\n")
                    f.write(f"Posted at: {post.get('timestamp', 'Unknown')}\n")
                    f.write("\nContent:\n")
                    f.write(post.get('content', ''))
                    f.write("\n\n")
            logging.info(f"Saved text file to {txt_path}")
        except Exception as e:
            logging.error(f"Error saving text file: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python archive_thread.py <thread_url>")
        sys.exit(1)
        
    thread_url = sys.argv[1]
    archiver = VBulletinThreadArchiver()
    
    try:
        archiver.archive_thread(thread_url)
        print("Thread archived successfully!")
    except Exception as e:
        print(f"Failed to archive thread: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
