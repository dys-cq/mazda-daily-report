---
name: searxng-search
description: |
  Privacy-focused web search using SearXNG metasearch engine. Aggregates results from 242+ search services without tracking or profiling.
  Use when: performing web searches with privacy protection, searching multiple engines simultaneously, needing unbiased results, avoiding filter bubbles,
  searching specific categories (images, videos, news, science, it, music, files), or API-based programmatic search.
  Supports formats: json, csv, rss. Triggers on: "search for", "look up", "find information about", "searxng", "private search", "metasearch".
---

# SearXNG Search

Privacy-focused metasearch using your local SearXNG instance.

## Quick Start

```bash
# Basic search
uv run python scripts/searxng_search.py "machine learning"

# Search with specific format
uv run python scripts/searxng_search.py "python tutorial" --format json

# Search in specific categories
uv run python scripts/searxng_search.py "climate change" --categories news,science

# Use specific engines
uv run python scripts/searxng_search.py "openclaw" --engines google,bing,duckduckgo

# Time-filtered search
uv run python scripts/searxng_search.py "AI news" --time-range day

# Safe search enabled
uv run python scripts/searxng_search.py "general knowledge" --safesearch 1
```

## Configuration

### Environment Variables

Create a `.env` file in the skill directory:

```bash
SEARXNG_URL=http://localhost:8888    # Your SearXNG instance URL
SEARXNG_TIMEOUT=10                    # Request timeout in seconds
```

### Default Instance

By default, the skill uses your local Docker SearXNG instance at `http://localhost:8888`.

To use a different instance:
- Public instances: https://searx.space
- Or deploy your own (see SearXNG documentation)

## Usage Patterns

### Basic Search

```python
from scripts.searxng_search import search, format_results

# Simple search
results = search("quantum computing")
print(format_results(results))
```

### Category-Specific Search

Available categories:
- `general` - General web search
- `images` - Image search
- `videos` - Video search
- `news` - News articles
- `science` - Scientific papers
- `it` - IT/programming
- `music` - Music
- `files` - Files/torrents
- `social media` - Social media posts

```python
# Search only news and science
results = search(
    "renewable energy",
    categories=["news", "science"]
)
```

### Engine Selection

Disable specific engines or use only trusted ones:

```python
# Use only privacy-focused engines
results = search(
    "privacy tools",
    engines=["duckduckgo", "startpage", "qwant"]
)
```

### Time-Range Filtering

```python
# Recent results only
results = search(
    "latest AI developments",
    time_range="day"  # or "month", "year"
)
```

### Pagination

```python
# Get second page of results
results = search("python", pageno=2)
```

## Output Formats

### JSON (default)

Structured data for programmatic use:

```json
{
  "query": "search term",
  "number_of_results": 10,
  "results": [
    {
      "title": "Result Title",
      "url": "https://example.com",
      "content": "Snippet...",
      "engine": "google",
      "score": 9.0
    }
  ],
  "suggestions": ["related search"]
}
```

### CSV

For spreadsheet analysis:

```bash
uv run python scripts/searxng_search.py "data science" --format csv
```

### RSS

For feed readers:

```bash
uv run python scripts/searxng_search.py "tech news" --format rss
```

## Command Line Options

```
usage: searxng_search.py [-h] [-f {json,csv,rss,html}] [-c CATEGORIES]
                         [-e ENGINES] [-l LANGUAGE] [-p PAGE]
                         [-t {day,month,year}] [-s {0,1,2}] [-m MAX_RESULTS]
                         [--raw]
                         query

positional arguments:
  query                 Search query

optional arguments:
  -h, --help            show this help message and exit
  -f, --format          Output format (json/csv/rss/html)
  -c, --categories      Comma-separated categories
  -e, --engines         Comma-separated engines
  -l, --language        Language code (default: auto)
  -p, --page            Page number
  -t, --time-range      Time range (day/month/year)
  -s, --safesearch      Safe search level (0/1/2)
  -m, --max-results     Max results to display
  --raw                 Raw output without formatting
```

## Integration Examples

### OpenClaw Tool Integration

The skill integrates with OpenClaw's tool system. When users ask to search:

1. "Search for quantum computing tutorials"
2. "Find recent AI news"
3. "Look up Python documentation"
4. "Search images of mountain landscapes"

The skill automatically:
- Queries your local SearXNG instance
- Aggregates results from multiple engines
- Returns privacy-protected results
- Formats output for readability

### Python API Usage

```python
from scripts.searxng_search import search

# Academic search
academic = search(
    "transformer architecture",
    categories=["science", "it"],
    time_range="year"
)

# Image search
images = search(
    "sunset photography",
    categories=["images"],
    engines=["unsplash", "pexels", "pixabay"]
)

# News aggregation
news = search(
    "climate summit",
    categories=["news"],
    time_range="week",
    engines=["google news", "bing news", "duckduckgo news"]
)
```

## Troubleshooting

### Connection Errors

**Error:** `Cannot connect to SearXNG at http://localhost:8888`

**Solution:**
1. Check if Docker container is running: `docker ps | grep searxng`
2. Start if needed: `docker start searxng`
3. Verify URL in `.env` file

### Timeout Errors

**Error:** `Request timed out`

**Solution:**
- Increase timeout: `SEARXNG_TIMEOUT=30` in `.env`
- Check network connectivity
- Try fewer engines or categories

### No Results

**Possible causes:**
- Query too specific
- All engines disabled
- Safe search too strict
- Category filter too narrow

**Solution:**
- Broaden query
- Enable more engines in SearXNG config
- Adjust safe search level
- Remove category filters

## Privacy Notes

✅ **What SearXNG protects:**
- No user tracking
- No search history
- No profiling
- No cookies (by default)
- Encrypted connections (HTTPS)
- Optional Tor access

⚠️ **Limitations:**
- Some engines may still track (depends on engine)
- Public instances may log (use self-hosted for full privacy)
- Image proxy recommended for image searches

## Advanced Configuration

### Custom SearXNG Settings

Edit your SearXNG `settings.yml`:
- Location: `C:\Users\Administrator\.openclaw\workspace\searxng\config\settings.yml`
- Enable/disable engines
- Configure categories
- Set default privacy options
- Add custom engines

### Engine-Specific Options

Some engines support additional parameters. See SearXNG documentation:
- https://docs.searxng.org/dev/engines/index.html

## Resources

- **SearXNG Docs:** https://docs.searxng.org
- **Public Instances:** https://searx.space
- **GitHub:** https://github.com/searxng/searxng
- **Search Syntax:** https://docs.searxng.org/user/search-syntax.html
