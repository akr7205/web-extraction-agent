"""CLI and API interface for the Web Extraction Agent."""
import json
import argparse
import sys
from typing import Optional
from pathlib import Path

from agent.web_extractor import create_agent


def extract_from_url(
    url: str,
    profile: str = "news",
    output_format: str = "json"
) -> dict:
    """
    Extract data from a URL.
    
    Args:
        url: URL to extract from
        profile: Extraction profile (news, filing, product)
        output_format: Output format (json, pretty)
        
    Returns:
        Extraction result dictionary
    """
    agent = create_agent()
    try:
        result = agent.extract(url, extraction_profile=profile)
        return result
    finally:
        agent.close()


def extract_from_file(
    file_path: str,
    url: str,
    profile: str = "news"
) -> dict:
    """
    Extract data from HTML file.
    
    Args:
        file_path: Path to HTML file
        url: URL to associate with extraction
        profile: Extraction profile
        
    Returns:
        Extraction result dictionary
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    agent = create_agent()
    try:
        result = agent.extract(url, raw_html=html_content, extraction_profile=profile)
        return result
    finally:
        agent.close()


def format_output(result: dict, format_type: str = "json") -> str:
    """
    Format extraction result for output.
    
    Args:
        result: Extraction result dictionary
        format_type: Output format (json, pretty, brief)
        
    Returns:
        Formatted string
    """
    if format_type == "pretty":
        return json.dumps(result, indent=2, ensure_ascii=False)
    elif format_type == "brief":
        return (
            f"URL: {result['metadata']['source_url']}\n"
            f"Title: {result['title']}\n"
            f"Content Length: {len(result['content'])} chars\n"
            f"Entities Found: {len(result['entities'])}\n"
            f"Processing Time: {result['trace']['duration_ms']}ms\n"
            f"Errors: {len(result['trace']['errors'])}"
        )
    else:  # json (compact)
        return json.dumps(result, separators=(',', ':'), ensure_ascii=False)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Web Extraction Agent - Extract structured data from web pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py extract-url https://example.com
  python app.py extract-url https://example.com --profile news --format pretty
  python app.py extract-file page.html https://example.com --profile product
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Extract from URL command
    extract_url_parser = subparsers.add_parser(
        "extract-url",
        help="Extract from a URL"
    )
    extract_url_parser.add_argument(
        "url",
        help="URL to extract from"
    )
    extract_url_parser.add_argument(
        "--profile",
        choices=["news", "filing", "product"],
        default="news",
        help="Extraction profile (default: news)"
    )
    extract_url_parser.add_argument(
        "--format",
        choices=["json", "pretty", "brief"],
        default="json",
        help="Output format (default: json)"
    )
    extract_url_parser.add_argument(
        "--output",
        help="Output file (default: stdout)"
    )
    
    # Extract from file command
    extract_file_parser = subparsers.add_parser(
        "extract-file",
        help="Extract from an HTML file"
    )
    extract_file_parser.add_argument(
        "file",
        help="HTML file path"
    )
    extract_file_parser.add_argument(
        "url",
        help="URL to associate with extraction"
    )
    extract_file_parser.add_argument(
        "--profile",
        choices=["news", "filing", "product"],
        default="news",
        help="Extraction profile (default: news)"
    )
    extract_file_parser.add_argument(
        "--format",
        choices=["json", "pretty", "brief"],
        default="json",
        help="Output format (default: json)"
    )
    extract_file_parser.add_argument(
        "--output",
        help="Output file (default: stdout)"
    )
    
    # Version command
    subparsers.add_parser("version", help="Show version")
    
    # Help command
    subparsers.add_parser("help", help="Show help")
    
    args = parser.parse_args()
    
    try:
        if args.command == "extract-url":
            print(f"Extracting from: {args.url}")
            result = extract_from_url(args.url, args.profile, args.format)
            output = format_output(result, args.format)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"Result saved to: {args.output}")
            else:
                print(output)
        
        elif args.command == "extract-file":
            print(f"Extracting from file: {args.file}")
            result = extract_from_file(args.file, args.url, args.profile)
            output = format_output(result, args.format)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"Result saved to: {args.output}")
            else:
                print(output)
        
        elif args.command == "version":
            print("Web Extraction Agent v1.0.0")
        
        else:
            parser.print_help()
    
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


class WebExtractionAPI:
    """Simple in-process API for the Web Extraction Agent."""
    
    def __init__(self):
        """Initialize API."""
        self.agent = create_agent()
    
    def extract(
        self,
        url: str,
        raw_html: Optional[str] = None,
        extraction_profile: str = "news"
    ) -> dict:
        """
        Extract structured data from web page.
        
        Args:
            url: URL of the page
            raw_html: Optional pre-fetched HTML
            extraction_profile: Profile to use (news, filing, product)
            
        Returns:
            Extraction result with title, entities, content, metadata, trace
        """
        return self.agent.extract(url, raw_html, extraction_profile)
    
    def close(self):
        """Close the API and clean up resources."""
        self.agent.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    main()
