# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based news content management system that supports both Markdown and HTML file formats. The system provides a web interface for viewing news articles and an authenticated editor for content management.

## Architecture

### Core Components
- **Flask Application** (`app.py`): Main web server with routing, authentication, and file management
- **Content Storage**: News files stored in `/news` directory as `.md` or `.html` files
- **Template System**: Jinja2 templates in `/templates` for web interface
- **Static Assets**: CSS, JS, images stored in `/static`
- **Authentication**: Session-based login system with configurable admin credentials

### Key Features
- Dual format support: Markdown files are converted to HTML; HTML files are served directly
- Date-based file naming convention (YYYYMMDD format)
- Pagination for news listings (5 items per page)
- File conflict detection and rename operations
- Session-based authentication with 1-year expiration

## Development Commands

### Local Development
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
flask run
# or
python app.py
```

### Testing
```bash
# Run tests (requires pytest)
pip install pytest
pytest tests/

# Run specific test
pytest tests/test_app.py::test_index_page
```

### Docker Development
```bash
# Build and run with Docker Compose
docker-compose up -d --build

# View logs
docker logs news-docms

# Stop containers
docker-compose down
```

## Configuration

### Environment Variables
- `FLASK_SECRET_KEY`: Session encryption key (auto-generated if not set)
- `NEWS_DIR`: News files directory (default: 'news')
- `ADMIN_USERNAME`: Admin login username (default: 'admin')
- `ADMIN_PASSWORD`: Admin login password (default: 'admin')
- `NEWS_FILE_PATH`: Docker volume mount path for news files

### File Structure
```
news/                    # News content directory
├── YYYYMMDD.md         # Markdown news files
├── YYYYMMDD.html       # HTML news files
└── ...

templates/              # Jinja2 templates
├── index.html          # News listing page
├── news.html           # News article view
├── editor.html         # Content editor
└── login.html          # Authentication page

static/                 # Static assets
└── images/            # Image files
```

## API Endpoints

### Content Management (Requires Authentication)
- `POST /api/save`: Save/update news file
  - Supports both new files and renames
  - Handles conflict detection
  - Accepts `filename`, `content`, `file_type`, `original_filename`

- `POST /api/delete/<filename>`: Delete news file
  - Removes both .md and .html versions if they exist

### Public Routes
- `GET /`: News listing with pagination
- `GET /page/<int:page>`: Paginated news listing
- `GET /<filename>`: View specific news article
- `GET /login`: Authentication page
- `GET /logout`: Session logout
- `GET /editor/<filename>`: Content editor (authenticated)

## Content Management

### File Naming Convention
- Use date-based naming: `YYYYMMDD.md` or `YYYYMMDD.html`
- Files without dates: Use descriptive names
- Automatic timestamp generation for new files if no name provided

### Title Extraction
- Markdown: Extracts first `# Title` line
- HTML: Extracts `<title>` tag content
- Fallback: Uses filename without extension

### Content Types
- **Markdown files**: Processed with Python-Markdown library
- **HTML files**: Served directly with full HTML structure

## Testing Considerations

- Tests use isolated `test_news` directory
- Authentication tests use environment variables for credentials
- File operations are tested in isolation with proper cleanup
- Both markdown and HTML file handling is covered

## Deployment

The application is containerized using Docker:
- Production server: Gunicorn on port 8009
- Development server: Flask built-in server on port 8080
- Volume mounting for persistent news content storage
- Configurable through environment variables and docker-compose.yml