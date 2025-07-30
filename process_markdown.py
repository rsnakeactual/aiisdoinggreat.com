#!/usr/bin/env python3
"""
Markdown to JSON Database Processor
Reads markdown files from /Users/rsnake/Documents/Me/Me/Work/RSnake, LLC/AIISDOINGGREAT/
and creates individual JSON files for each post in /Users/rsnake/bin/aiisdoinggreat.com/db/
"""

import os
import json
import hashlib
import glob
import shutil
from datetime import datetime
from pathlib import Path
import re

class MarkdownProcessor:
    def __init__(self, source_dir, db_dir):
        self.source_dir = Path(source_dir)
        self.db_dir = Path(db_dir)
        self.db_file = self.db_dir / "posts.db"
        self.posts = []
        self.existing_posts = {}
        
        # Ensure db directory exists
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        # Create assets directory for images
        self.assets_dir = self.db_dir / "assets" / "images" / "posts"
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
    def load_existing_database(self):
        """Load existing posts from database to avoid duplicates"""
        if self.db_file.exists():
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for post in data.get('posts', []):
                        self.existing_posts[post['id']] = post
                print(f"Loaded {len(self.existing_posts)} existing posts")
            except Exception as e:
                print(f"Error loading existing database: {e}")
    
    def calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of file content"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def extract_title_from_filename(self, filename):
        """Extract title from filename (remove .md extension)"""
        return filename.replace('.md', '')
    
    def create_slug_from_title(self, title, created_at):
        """Create a slug from title with date stamp"""
        # Convert to lowercase and replace spaces with dashes
        slug = title.lower().replace(' ', '-').replace('_', '-')
        
        # Remove non-alphanumeric characters except dashes
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        
        # Remove multiple consecutive dashes
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading/trailing dashes
        slug = slug.strip('-')
        
        # Parse the created_at date and format it
        try:
            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            date_stamp = date_obj.strftime('%Y%m%d')
        except:
            date_stamp = datetime.now().strftime('%Y%m%d')
        
        # Combine slug with date
        return f"{slug}-{date_stamp}"
    
    def extract_excerpt(self, content, max_length=200):
        """Extract excerpt from content (return full content)"""
        # Return the full processed content as the excerpt
        return content
    
    def process_images(self, content, source_file_path):
        """Process images in markdown content and copy them to assets directory"""
        processed_content = content
        source_dir = source_file_path.parent
        
        # Find all image references in markdown
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(image_pattern, content)
        
        for alt_text, image_path in matches:
            # Handle relative paths
            if image_path.startswith('./'):
                image_path = image_path[2:]  # Remove './'
            
            # Construct full path to image
            full_image_path = source_dir / image_path
            
            if full_image_path.exists():
                # Create a unique filename for the image
                image_filename = f"{source_file_path.stem}_{full_image_path.name}"
                target_path = self.assets_dir / image_filename
                
                # Copy image to assets directory
                try:
                    shutil.copy2(full_image_path, target_path)
                    print(f"  📸 Copied image: {image_path} → {target_path}")
                    
                    # Update the markdown to reference the new location
                    new_image_path = f"db/assets/images/posts/{image_filename}"
                    processed_content = processed_content.replace(
                        f'![{alt_text}]({image_path})',
                        f'![{alt_text}]({new_image_path})'
                    )
                except Exception as e:
                    print(f"  ⚠️  Error copying image {image_path}: {e}")
            else:
                print(f"  ⚠️  Image not found: {full_image_path}")
        
        return processed_content
    
    def process_links(self, content):
        """Process external links in markdown content"""
        # First, handle bare URLs in square brackets like [https://example.com]
        bare_url_pattern = r'\[(https?://[^\]]+)\]'
        
        def bare_url_replacer(match):
            url = match.group(1)
            return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'
        
        content = re.sub(bare_url_pattern, bare_url_replacer, content)
        
        # Then handle regular markdown links [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def link_replacer(match):
            text = match.group(1)
            url = match.group(2)
            
            # If it's an external link (starts with http/https), add target="_blank"
            if url.startswith(('http://', 'https://')):
                return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{text}</a>'
            else:
                # Internal links remain as markdown
                return match.group(0)
        
        content = re.sub(link_pattern, link_replacer, content)
        
        # Finally, handle plain URLs in text (without brackets or HTML tags)
        # This matches URLs that are not already in HTML tags or markdown links
        plain_url_pattern = r'(?<![\[<"\w])(https?://[^\s<>\[\]"]+)(?![\]>"\w])'
        
        def plain_url_replacer(match):
            url = match.group(1)
            return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'
        
        processed_content = re.sub(plain_url_pattern, plain_url_replacer, content)
        return processed_content
    
    def process_markdown_file(self, file_path):
        """Process a single markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate file hash for duplicate detection
            file_hash = self.calculate_file_hash(file_path)
            
            # Check if this file has already been processed
            if file_hash in self.existing_posts:
                print(f"Skipping {file_path.name} - already processed")
                return None
            
            # Extract metadata
            title = self.extract_title_from_filename(file_path.name)
            print(f"Title: {title}")
            
            # Process images and links FIRST, before extracting excerpt
            print(f"  Processing images and links for {file_path.name}...")
            processed_content = self.process_images(content, file_path)
            processed_content = self.process_links(processed_content)
            
            # Now extract excerpt from processed content
            excerpt = self.extract_excerpt(processed_content)
            
            # Create timestamp for slug generation
            created_at = datetime.now().isoformat()
            
            # Create post object
            post = {
                'id': file_hash,
                'title': title,
                'excerpt': excerpt,
                'content': processed_content,
                'filename': file_path.name,
                'slug': self.create_slug_from_title(title, created_at),
                'created_at': created_at,
                'updated_at': created_at
            }
            
            print(f"Processed: {file_path.name} - {title}")
            return post
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
    
    def scan_markdown_files(self):
        """Scan for all markdown files in source directory"""
        pattern = self.source_dir / "**/*.md"
        md_files = list(glob.glob(str(pattern), recursive=True))
        print(f"Found {len(md_files)} markdown files")
        return md_files
    
    def save_database(self):
        """Save all posts to database file"""
        data = {
            'posts': list(self.existing_posts.values()),
            'total_posts': len(self.existing_posts),
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved database with {len(self.existing_posts)} posts")
    
    def create_individual_json_files(self):
        """Create individual JSON files for each post"""
        # Remove old individual JSON files
        for json_file in self.db_dir.glob("post_*.json"):
            json_file.unlink()
            print(f"Deleted old file: {json_file}")
        
        # Create individual files for each post
        for post in self.existing_posts.values():
            filename = self.db_dir / f"post_{post['id']}.json"
            data = {
                'post': post,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"Created individual file: {filename}")
    
    def create_paginated_index_files(self):
        """Create paginated index files with 10 posts each"""
        # Remove old paginated index files
        for json_file in self.db_dir.glob("index_*.json"):
            json_file.unlink()
            print(f"Deleted old paginated file: {json_file}")
        
        # Get all posts sorted by creation date (newest first)
        all_posts = list(self.existing_posts.values())
        all_posts.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Create lightweight versions for the index
        posts_list = []
        for post in all_posts:
            # Ensure slug exists for older posts
            if 'slug' not in post:
                post['slug'] = self.create_slug_from_title(post['title'], post['created_at'])
            
            # Create a lightweight version for the index
            posts_list.append({
                'id': post['id'],
                'title': post['title'],
                'excerpt': post['excerpt'],
                'filename': post['filename'],
                'slug': post['slug'],
                'created_at': post['created_at']
            })
        
        # Split into pages of 10 posts each
        posts_per_page = 10
        total_posts = len(posts_list)
        total_pages = (total_posts + posts_per_page - 1) // posts_per_page  # Ceiling division
        
        for page_num in range(total_pages):
            start_idx = page_num * posts_per_page
            end_idx = min(start_idx + posts_per_page, total_posts)
            page_posts = posts_list[start_idx:end_idx]
            
            # Create page data
            page_data = {
                'posts': page_posts,
                'page': page_num + 1,
                'total_pages': total_pages,
                'total_posts': total_posts,
                'posts_per_page': posts_per_page,
                'has_next': page_num + 1 < total_pages,
                'has_prev': page_num > 0,
                'next_page': page_num + 2 if page_num + 1 < total_pages else None,
                'prev_page': page_num if page_num > 0 else None,
                'last_updated': datetime.now().isoformat()
            }
            
            # Save page file
            if page_num == 0:
                # First page is the main index
                filename = self.db_dir / "index.json"
            else:
                filename = self.db_dir / f"index_{page_num + 1}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False)
            
            print(f"Created paginated file: {filename} with {len(page_posts)} posts")
    
    def run(self):
        """Main processing function"""
        print("Starting markdown processing...")
        
        # Load existing database
        self.load_existing_database()
        
        # Scan for markdown files
        md_files = self.scan_markdown_files()
        
        if not md_files:
            print("No markdown files found!")
            return
        
        # Process each file
        new_posts = 0
        for file_path in md_files:
            post = self.process_markdown_file(Path(file_path))
            if post:
                self.existing_posts[post['id']] = post
                new_posts += 1
        
        print(f"Processed {new_posts} new posts")
        
        # Save database
        self.save_database()
        
        # Create individual JSON files
        self.create_individual_json_files()
        
        # Create paginated index files
        self.create_paginated_index_files()
        
        print("Processing complete!")

def main():
    source_dir = "/Users/rsnake/Documents/Me/Me/Work/RSnake, LLC/AIISDOINGGREAT/"
    db_dir = "/Users/rsnake/bin/aiisdoinggreat.com/db/"
    
    processor = MarkdownProcessor(source_dir, db_dir)
    processor.run()

if __name__ == "__main__":
    main() 