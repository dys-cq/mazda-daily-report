#!/usr/bin/env python3
"""
SearXNG Search Script

Queries a SearXNG instance and returns search results in a clean format.
Supports multiple output formats: json, csv, rss, html
"""

import os
import sys
import json
import argparse
from urllib.parse import urlencode
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Default configuration from environment
SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8888")
SEARXNG_TIMEOUT = int(os.getenv("SEARXNG_TIMEOUT", "10"))


def search(query, categories=None, engines=None, language="auto", 
           pageno=1, time_range=None, format="json", safesearch=0):
    """
    Perform a search query on SearXNG.
    
    Args:
        query (str): Search query string
        categories (list, optional): List of search categories
        engines (list, optional): List of specific engines to use
        language (str): Language code (default: "auto")
        pageno (int): Page number (default: 1)
        time_range (str, optional): Time range filter (day, month, year)
        format (str): Output format (json, csv, rss, html)
        safesearch (int): Safe search level (0: None, 1: Moderate, 2: Strict)
    
    Returns:
        dict or str: Search results in requested format
    """
    # Build query parameters
    params = {
        "q": query,
        "format": format,
        "language": language,
        "pageno": pageno,
        "safesearch": safesearch,
    }
    
    # Add optional parameters
    if categories:
        params["categories"] = ",".join(categories)
    
    if engines:
        params["engines"] = ",".join(engines)
    
    if time_range:
        params["time_range"] = time_range
    
    # Make the request
    url = f"{SEARXNG_URL}/search"
    
    try:
        response = requests.post(
            url,
            data=params,
            timeout=SEARXNG_TIMEOUT,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        
        if format == "json":
            return response.json()
        else:
            return response.text
            
    except requests.exceptions.Timeout:
        return {"error": "Request timed out", "timeout": SEARXNG_TIMEOUT}
    except requests.exceptions.ConnectionError:
        return {"error": f"Cannot connect to SearXNG at {SEARXNG_URL}"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON response"}


def format_results(results, max_results=10):
    """
    Format search results for human-readable output.
    
    Args:
        results (dict): SearXNG JSON response
        max_results (int): Maximum number of results to display
    
    Returns:
        str: Formatted results as markdown
    """
    if "error" in results:
        return f"❌ Error: {results['error']}"
    
    output = []
    query = results.get("query", "Unknown query")
    number_of_results = len(results.get("results", []))
    
    output.append(f"## Search Results for: {query}\n")
    output.append(f"Found {number_of_results} results\n")
    
    results_list = results.get("results", [])[:max_results]
    
    for i, result in enumerate(results_list, 1):
        title = result.get("title", "No title")
        url = result.get("url", "")
        content = result.get("content", "")
        engine = result.get("engine", "unknown")
        
        output.append(f"### {i}. {title}")
        output.append(f"**URL:** {url}")
        output.append(f"**Source:** {engine}")
        if content:
            output.append(f"{content}\n")
    
    # Add suggestions if available
    suggestions = results.get("suggestions", [])
    if suggestions:
        output.append("\n## Suggestions")
        for suggestion in suggestions:
            output.append(f"- {suggestion}")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Search using SearXNG metasearch engine"
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "-f", "--format",
        choices=["json", "csv", "rss", "html"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "-c", "--categories",
        help="Comma-separated list of categories (e.g., general,images,videos)"
    )
    parser.add_argument(
        "-e", "--engines",
        help="Comma-separated list of engines (e.g., google,bing,duckduckgo)"
    )
    parser.add_argument(
        "-l", "--language",
        default="auto",
        help="Language code (default: auto)"
    )
    parser.add_argument(
        "-p", "--page",
        type=int,
        default=1,
        help="Page number (default: 1)"
    )
    parser.add_argument(
        "-t", "--time-range",
        choices=["day", "month", "year"],
        help="Time range filter"
    )
    parser.add_argument(
        "-s", "--safesearch",
        type=int,
        choices=[0, 1, 2],
        default=0,
        help="Safe search level: 0=None, 1=Moderate, 2=Strict"
    )
    parser.add_argument(
        "-m", "--max-results",
        type=int,
        default=10,
        help="Maximum results to display (default: 10)"
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Output raw response without formatting"
    )
    
    args = parser.parse_args()
    
    # Parse categories and engines
    categories = args.categories.split(",") if args.categories else None
    engines = args.engines.split(",") if args.engines else None
    
    # Perform search
    results = search(
        query=args.query,
        categories=categories,
        engines=engines,
        language=args.language,
        pageno=args.page,
        time_range=args.time_range,
        format=args.format,
        safesearch=args.safesearch
    )
    
    # Output results
    import sys
    import io
    # Set stdout to UTF-8 for Windows compatibility
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    if args.raw or args.format != "json":
        if isinstance(results, dict):
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(results)
    else:
        formatted = format_results(results, max_results=args.max_results)
        print(formatted)


if __name__ == "__main__":
    main()
