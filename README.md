# AI IS DOING GREAT - Blog System

A simple blog system that processes markdown files and creates a beautiful, paginated website with direct post linking.

## Features

- **Markdown Processing**: Reads all `.md` files from a specified directory
- **Duplicate Detection**: Uses SHA256 hashing to avoid processing the same file twice
- **Individual JSON Files**: Creates separate JSON files for each post for direct linking
- **Direct Post URLs**: Each post has a unique URL using anchor tags (e.g., `#post-id`)
- **Image Processing**: Automatically copies and processes images from relative paths
- **External Link Processing**: Converts external links to HTML with proper attributes
- **Beautiful UI**: Modern, responsive design with Bootstrap
- **Pagination**: Navigate through posts with URL-based pagination
- **Markdown Rendering**: Basic markdown support in the browser
- **Title from Filename**: Post titles are extracted from the markdown filename
- **Obsidian Compatibility**: Handles Obsidian-style markdown with relative paths

## File Structure

```
aiisdoinggreat.com/
├── process_markdown.py    # Python script to process markdown files
├── index.html            # Main website file
├── db/                   # Database directory
│   ├── posts.db         # Main database file
│   ├── index.json       # Index file with all post metadata
│   ├── post_[hash].json # Individual post files (one per post)
│   ├── assets/          # Processed images and assets
│   │   └── images/
│   │       └── posts/   # Copied images from markdown files
│   └── ...
└── README.md            # This file
```

## URL Structure

- **Homepage**: `/` - Shows all posts with pagination
- **Individual Post**: `/#[post-hash]` - Direct link to specific post
- **Pagination**: `/?page=2` - Navigate to specific page

## Usage

### 1. Process Markdown Files

Run the Python script to process your markdown files:

```bash
python3 process_markdown.py
```

This will:
- Scan `/Users/rsnake/Documents/Me/Me/Work/RSnake, LLC/AIISDOINGGREAT/` for `.md` files
- Create a database in `/Users/rsnake/bin/aiisdoinggreat.com/db/`
- Generate individual JSON files for each post
- Create an index file for listing all posts
- Process and copy images from relative paths
- Convert external links to HTML with proper attributes
- Avoid duplicates using file hashing

### 2. View the Website

Open `index.html` in a web browser or serve it with a local server:

```bash
# Using Python's built-in server
python3 -m http.server 8000

# Then visit http://localhost:8000
```

### 3. Direct Post Linking

Each post can be accessed directly via its hash:
- `http://localhost:8000/#[post-hash]`
- Example: `http://localhost:8000/#a607f8fd733e50f256533592b050098a159b55b0ac7d34bacd99384eea3f66c8`

### 4. Deploy to GitHub

To deploy to your GitHub repository:

1. Initialize git repository:
```bash
git init
git add .
git commit -m "Initial commit"
```

2. Add your GitHub remote:
```bash
git remote add origin https://github.com/rsnakeactual/aiisdoinggreat.com.git
git push -u origin main
```

3. Enable GitHub Pages in your repository settings

## Configuration

### Source Directory
Edit `process_markdown.py` to change the source directory:
```python
source_dir = "/path/to/your/markdown/files/"
```

### Title Extraction
Post titles are extracted from the markdown filename (removing `.md` extension):
- `1.md` becomes title "1"
- `my-post.md` becomes title "my-post"

### Website Styling
The website uses Bootstrap 5 and custom CSS. Edit the `<style>` section in `index.html` to customize the appearance.

## Image and Link Processing

### Image Processing
The system automatically processes images in markdown files:

- **Relative Paths**: Images with paths like `./assets/images/posts/image.png` are processed
- **Image Copying**: Images are copied to `db/assets/images/posts/` with unique names
- **Path Updates**: Markdown image references are updated to point to the new location
- **Missing Images**: If images don't exist, the system logs warnings but continues processing

Example markdown:
```markdown
![My Image](./assets/images/posts/my-image.png)
```

Becomes:
```markdown
![My Image](db/assets/images/posts/post-title_my-image.png)
```

### External Link Processing
External links are automatically converted to HTML with proper attributes:

- **Regular Markdown Links**: Links like `[text](url)` get `target="_blank"` and `rel="noopener noreferrer"`
- **Bare URLs in Brackets**: URLs like `[https://example.com]` are converted to clickable links
- **Internal Links**: Internal links remain as markdown for processing by the browser

Example markdown:
```markdown
[Google](https://www.google.com)
[https://www.example.com/]
```

Becomes:
```html
<a href="https://www.google.com" target="_blank" rel="noopener noreferrer">Google</a>
<a href="https://www.example.com/" target="_blank" rel="noopener noreferrer">https://www.example.com/</a>
```

### Obsidian Compatibility
The system is designed to work with Obsidian-style markdown:
- Handles relative image paths (`./assets/images/posts/`)
- Processes external links automatically
- Maintains internal link structure
- Supports Obsidian's markdown extensions

## Database Schema

Each post in the database contains:
- `id`: SHA256 hash of the file content (used for direct linking)
- `title`: Extracted from filename (without .md extension)
- `excerpt`: First paragraph of content
- `content`: Full markdown content (with processed images and links)
- `filename`: Original filename
- `slug`: URL-friendly version of title
- `created_at`: Processing timestamp
- `updated_at`: Processing timestamp

## File Structure Details

### Individual Post Files
Each post gets its own JSON file named `post_[hash].json`:
```json
{
  "post": {
    "id": "a607f8fd733e50f256533592b050098a159b55b0ac7d34bacd99384eea3f66c8",
    "title": "1",
    "excerpt": "Post excerpt...",
    "content": "Full markdown content with processed images and links...",
    "filename": "1.md",
    "slug": "1",
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
  },
  "last_updated": "2024-01-01T12:00:00"
}
```

### Index File
The `index.json` file contains metadata for all posts:
```json
{
  "posts": [
    {
      "id": "post-hash",
      "title": "Post Title",
      "excerpt": "Post excerpt...",
      "filename": "filename.md",
      "slug": "post-title",
      "created_at": "2024-01-01T12:00:00"
    }
  ],
  "total_posts": 11,
  "last_updated": "2024-01-01T12:00:00"
}
```

## Markdown Support

The website supports basic markdown features:
- Headers (`#`, `##`, `###`)
- Bold (`**text**`) and italic (`*text*`)
- Code blocks (``` ``` ```)
- Inline code (`code`)
- Links (`[text](url)`) - external links open in new tabs
- Images (`![alt](path)`) - with responsive styling
- Line breaks

## Technical Details

- **Backend**: Python 3 with standard library
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Bootstrap 5
- **Database**: Individual JSON files
- **Pagination**: URL-based with browser history support
- **Direct Linking**: Hash-based URLs for individual posts
- **Image Processing**: Automatic copying and path updating
- **Link Processing**: External links with security attributes

## Future Enhancements

- Image optimization and compression
- Categories and tags
- Search functionality
- RSS feed generation
- SEO optimization
- Comments system
- Social media sharing
- Custom slug generation
- Post categories and filtering
- Image lazy loading
- Advanced markdown extensions

## Troubleshooting

### No posts found
- Check that the source directory exists and contains `.md` files
- Verify file permissions
- Check console for error messages

### Website not loading posts
- Ensure the `db/` directory contains `index.json` and individual post files
- Check browser console for JavaScript errors
- Verify file paths are correct

### Direct links not working
- Ensure individual post JSON files exist in the `db/` directory
- Check that the post hash in the URL matches a file
- Verify the post file format is correct

### Images not displaying
- Check that images exist in the source directory
- Verify image paths in markdown files are correct
- Ensure images are copied to `db/assets/images/posts/`
- Check browser console for image loading errors

### External links not working
- Verify that external links start with `http://` or `https://`
- Check that the link processing is working correctly
- Ensure the website is served over HTTPS for secure links

### Styling issues
- Ensure internet connection for Bootstrap CDN
- Check browser compatibility
- Clear browser cache 