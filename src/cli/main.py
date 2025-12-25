"""
Command-line interface for Web Extractor Agent.

This module provides a comprehensive CLI for extracting data from websites
with both interactive and command-line argument modes.
"""

import sys
import json
import io
from pathlib import Path
import argparse
from typing import List, Optional

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.web_extractor import WebExtractionAgent


# ============================================================================
# Interactive Mode Functions
# ============================================================================

def print_header():
    """Print CLI header."""
    print("\n" + "="*70)
    print("*** SEMANTIC WEB EXTRACTION CLI ***")
    print("🤖 Powered by AI - Supports natural language queries")
    print("="*70)


def print_separator():
    """Print separator line."""
    print("-" * 70)


def get_url_input():
    """Get URL(s) from user."""
    while True:
        url_input = input("\n>> Enter website URL(s) (comma-separated for multiple): ").strip()
        if url_input:
            # Split by comma and clean up
            urls = [u.strip() for u in url_input.split(',') if u.strip()]
            # Add https:// prefix if missing
            urls = [u if u.startswith(('http://', 'https://')) else 'https://' + u for u in urls]
            if urls:
                return urls
        print("❌ At least one URL is required. Please try again.")


def get_extraction_mode():
    """Ask user if they want to extract from a single page or entire site."""
    print("\n*** Extraction Mode:")
    print("  1. Single page(s) - Extract from specific URL(s)")
    print("  2. Entire site - Extract from all pages of a website")
    
    while True:
        choice = input("\nSelect mode (1 or 2) [default: 1]: ").strip()
        
        # Accept empty input or '1' for single page mode
        if not choice or choice == '' or choice == '1':
            return 'single'
        # Accept '2' for site mode
        elif choice == '2':
            return 'site'
        # Handle common variations
        elif choice.lower() in ['single', 's', 'page']:
            return 'single'
        elif choice.lower() in ['site', 'entire', 'all']:
            return 'site'
        else:
            print("Invalid choice. Please press Enter for default (1) or type '2' for site-wide extraction.")


def get_crawl_settings():
    """Get crawl settings for site-wide extraction."""
    print("\n*** Crawl Settings:")
    
    # Max pages
    while True:
        max_pages_input = input("  Max pages to crawl (default=50): ").strip()
        if not max_pages_input:
            max_pages = 50
            break
        try:
            max_pages = int(max_pages_input)
            if max_pages > 0:
                break
            print("  ❌ Please enter a positive number.")
        except ValueError:
            print("  ❌ Please enter a valid number.")
    
    # Max depth
    while True:
        max_depth_input = input("  Max crawl depth (default=3): ").strip()
        if not max_depth_input:
            max_depth = 3
            break
        try:
            max_depth = int(max_depth_input)
            if max_depth > 0:
                break
            print("  ❌ Please enter a positive number.")
        except ValueError:
            print("  ❌ Please enter a valid number.")
    
    return max_pages, max_depth


def get_query_input():
    """Get search query from user - supports both keywords and natural language."""
    print("\n*** Search Query")
    print("💡 You can enter:")
    print("   • Keywords: AI, technology, startup")
    print("   • Natural language: 'Give me all details about this'")
    print("   • Specific request: 'Find pricing and features information'")
    
    while True:
        query_input = input("\n>> Enter your search query: ").strip()
        if query_input:
            return query_input
        print("❌ Query is required. Please try again.")


def get_llm_preference():
    """Ask if user wants LLM enhancement."""
    print("\n*** LLM Enhancement (Recommended)")
    print("💡 LLM provides:")
    print("   • Semantic understanding of your query")
    print("   • Better relevance scoring")
    print("   • Higher quality results")
    choice = input("\n>> Use LLM for semantic search? (y/n) [default: y]: ").strip().lower()
    return choice != 'n' and choice != 'no'


def display_results(result, url_index=None, total_urls=None):
    """Display extraction results in a formatted way."""
    print("\n" + "="*70)
    if url_index is not None and total_urls is not None:
        print(f"📊 EXTRACTION RESULTS [{url_index}/{total_urls}]")
    else:
        print("📊 EXTRACTION RESULTS")
    print("="*70)
    
    # Basic info
    print(f"\n📄 Title: {result.get('title', 'N/A')}")
    print(f"🔗 URL: {result['metadata']['source_url']}")
    print(f"🎯 Keywords: {', '.join(result['keywords'])}")
    
    print_separator()
    
    # Extraction stats
    kw_extraction = result['keyword_extraction']
    print(f"\n📈 Extraction Statistics:")
    print(f"  ⭐ Relevance Score: {kw_extraction['relevance_score']:.3f}/1.000")
    print(f"  📊 Total Matches: {kw_extraction['total_matches']}")
    print(f"  ⏱️  Processing Time: {result['trace']['duration_ms']}ms")
    print(f"  🤖 LLM Used: {'Yes' if result['trace']['llm_used'] else 'No'}")
    
    # Matched sections
    if kw_extraction['matched_sections']:
        print(f"\n📑 Top Matched Sections:")
        for i, section in enumerate(kw_extraction['matched_sections'][:5], 1):
            print(f"\n  {i}. Relevance: {section['relevance_score']:.3f}")
            print(f"     Keywords: {', '.join(section['matched_keywords'])}")
            print(f"     Tag: <{section['tag']}>")
            
            # Show preview of content
            text = section['text']
            if len(text) > 150:
                text = text[:147] + "..."
            print(f"     Preview: {text}")
    
    # Keyword entities
    if result.get('keyword_entities'):
        print(f"\n🔍 Entities by Keyword:")
        for keyword, entities in result['keyword_entities'].items():
            if entities:
                # Show first 5 entities per keyword
                entity_list = ', '.join(entities[:5])
                if len(entities) > 5:
                    entity_list += f" (+{len(entities)-5} more)"
                print(f"  • {keyword}: {entity_list}")
    
    # Summary
    if kw_extraction['summary']:
        print(f"\n📝 Summary:")
        summary = kw_extraction['summary']
        if len(summary) > 400:
            summary = summary[:397] + "..."
        print(f"  {summary}")
    
    # LLM insights (if available)
    if 'llm_extraction' in result and result['llm_extraction']:
        llm_data = result['llm_extraction']
        if 'summary' in llm_data and llm_data['summary']:
            print(f"\n🧠 LLM Summary:")
            llm_summary = llm_data['summary']
            if len(llm_summary) > 300:
                llm_summary = llm_summary[:297] + "..."
            print(f"  {llm_summary}")
        
        if 'keywords_found' in llm_data:
            print(f"\n  Keywords Found by LLM: {', '.join(llm_data['keywords_found'])}")
    
    # Errors/warnings
    if result['trace']['errors']:
        print(f"\n⚠️  Warnings/Errors:")
        for error in result['trace']['errors']:
            print(f"  - {error}")
    
    print("\n" + "="*70)


def display_site_results(result):
    """Display site-wide extraction results."""
    print("\n" + "="*70)
    print("📊 SITE-WIDE EXTRACTION RESULTS")
    print("="*70)
    
    # Basic info
    print(f"\n🌐 Start URL: {result['start_url']}")
    print(f"📄 Total Pages Crawled: {result['total_pages_crawled']}")
    print(f"✅ Successful: {result['successful_extractions']}")
    print(f"❌ Failed: {result['failed_extractions']}")
    
    if result.get('keywords'):
        print(f"🎯 Keywords: {', '.join(result['keywords'])}")
    
    print_separator()
    
    # Summary
    summary = result.get('summary', {})
    if summary:
        print(f"\n📈 Summary Statistics:")
        if result.get('keywords'):
            print(f"  ⭐ Average Relevance: {summary.get('avg_relevance', 0):.3f}/1.000")
            print(f"  📊 Total Matches: {summary.get('total_matches', 0)}")
            
            # Top relevant pages
            top_pages = summary.get('top_relevant_pages', [])
            if top_pages:
                print(f"\n🏆 Top {len(top_pages)} Most Relevant Pages:")
                for i, page in enumerate(top_pages, 1):
                    print(f"\n  {i}. {page['title'][:50]}")
                    print(f"     URL: {page['url']}")
                    print(f"     Relevance: {page['relevance']:.3f}")
                    print(f"     Matches: {page['matches']}")
        else:
            print(f"  🔢 Total Entities: {summary.get('total_entities', 0)}")
            print(f"  📝 Pages with Content: {summary.get('pages_with_content', 0)}")
            
            entity_types = summary.get('entity_types', {})
            if entity_types:
                print(f"\n  Entity Types Found:")
                for etype, count in sorted(entity_types.items(), key=lambda x: x[1], reverse=True):
                    print(f"    - {etype}: {count}")
    
    print(f"\n⏱️  Total Processing Time: {result['metadata']['total_duration_ms']}ms")
    print("\n💡 Tip: Results contain data from {0} pages".format(len(result.get('pages', []))))


def save_results(result, url_index=None, base_filename="extraction_result"):
    """Save results to JSON file."""
    if url_index is not None:
        filename = f"{base_filename}_{url_index}.json"
    else:
        filename = f"{base_filename}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return filename


def save_site_results(result, base_filename="site_extraction"):
    """Save site-wide results to JSON file."""
    timestamp = result['metadata']['fetched_at'].replace(':', '-').split('.')[0]
    filename = f"{base_filename}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return filename


def interactive_mode():
    """Run interactive CLI mode."""
    print_header()
    
    # Get extraction mode
    mode = get_extraction_mode()
    
    if mode == 'site':
        # Site-wide extraction
        url = get_url_input()[0]  # Get single URL for site extraction
        query = get_query_input()
        max_pages, max_depth = get_crawl_settings()
        use_llm = get_llm_preference()
        
        # Summary of inputs
        print(f"\n✅ Configuration:")
        print(f"  Mode: Entire Site Extraction")
        print(f"  Start URL: {url}")
        print(f"  Query: {query}")
        print(f"  Max Pages: {max_pages}")
        print(f"  Max Depth: {max_depth}")
        print(f"  LLM: {'Enabled' if use_llm else 'Disabled'}")
        
        # Confirm
        confirm = input("\n🚀 Start site-wide extraction? (y/n, default=y): ").strip().lower()
        if confirm == 'n':
            print("\n❌ Extraction cancelled.")
            return
        
        # Initialize agent and extract
        print(f"\n🔄 Initializing extraction agent...")
        try:
            agent = WebExtractionAgent(use_llm=use_llm)
            print("✅ Agent initialized")
            print(f"\n{'='*70}")
            print(f"🕷️  Crawling and extracting from: {url}")
            print(f"{'='*70}")
            print("⏳ This may take a while... Please wait...")
            
            result = agent.extract_from_site_semantic(
                start_url=url,
                query=query,
                max_pages=max_pages,
                max_depth=max_depth,
                use_llm=use_llm
            )
            
            # Display results
            display_site_results(result)
            
            # Save to file
            save_choice = input("\n💾 Save results to file? (y/n, default=y): ").strip().lower()
            if save_choice != 'n':
                filename = save_site_results(result)
                print(f"✅ Results saved to: {filename}")
            
            print("\n✨ Site-wide extraction completed!")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Extraction interrupted by user.")
        except Exception as e:
            print(f"\n❌ Error during extraction: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        # Single page extraction
        urls = get_url_input()
        query = get_query_input()
        use_llm = get_llm_preference()
        
        # Summary of inputs
        print(f"\n✅ Configuration:")
        print(f"  Mode: Single Page Extraction")
        print(f"  URLs: {len(urls)}")
        for i, url in enumerate(urls, 1):
            print(f"    {i}. {url}")
        print(f"  Query: {query}")
        print(f"  LLM: {'Enabled' if use_llm else 'Disabled'}")
        
        # Confirm
        confirm = input("\n🚀 Start extraction? (y/n, default=y): ").strip().lower()
        if confirm == 'n':
            print("\n❌ Extraction cancelled.")
            return
        
        # Initialize agent and extract
        print(f"\n🔄 Initializing extraction agent...")
        try:
            agent = WebExtractionAgent(use_llm=use_llm)
            print("✅ Agent initialized")
            
            results = []
            successful = 0
            failed = 0
            
            # Process each URL
            for i, url in enumerate(urls, 1):
                print(f"\n{'='*70}")
                print(f"🔍 Processing URL {i}/{len(urls)}: {url}")
                print(f"{'='*70}")
                print("⏳ Please wait...")
                
                try:
                    result = agent.extract_by_semantic_query(
                        url=url,
                        query=query,
                        use_llm=use_llm
                    )
                    
                    # Display results
                    display_results(result, i, len(urls))
                    results.append((url, result, True))
                    successful += 1
                    
                except Exception as e:
                    print(f"\n❌ Error extracting from {url}: {e}")
                    results.append((url, None, False))
                    failed += 1
                    continue
            
            # Summary
            print(f"\n{'='*70}")
            print(f"📈 EXTRACTION SUMMARY")
            print(f"{'='*70}")
            print(f"  ✅ Successful: {successful}/{len(urls)}")
            print(f"  ❌ Failed: {failed}/{len(urls)}")
            
            # Save to file(s)
            if successful > 0:
                save_choice = input("\n💾 Save results to file(s)? (y/n, default=y): ").strip().lower()
                if save_choice != 'n':
                    saved_files = []
                    for i, (url, result, success) in enumerate(results, 1):
                        if success and result:
                            filename = save_results(result, i if len(urls) > 1 else None)
                            saved_files.append(filename)
                            print(f"✅ Results for URL {i} saved to: {filename}")
                    
                    if len(saved_files) > 1:
                        print(f"\n📁 Total files saved: {len(saved_files)}")
            
            print("\n✨ Extraction completed!")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Extraction interrupted by user.")
        except Exception as e:
            print(f"\n❌ Error during extraction: {e}")
            print("\n💡 Tips:")
            print("  - Check your internet connection")
            print("  - Verify the URLs are accessible")
            print("  - Try with --no-llm for faster extraction")
            print("  - Check if LLM service (LiteLLM) is configured properly")
    
    # Ask if user wants to extract again
    again = input("\n🔄 Extract again? (y/n): ").strip().lower()
    if again == 'y':
        interactive_mode()  # Recursive call for another extraction
    else:
        print("\n👋 Thank you for using Semantic Web Extraction CLI!")
        print("="*70 + "\n")


# ============================================================================
# Argument Mode Functions
# ============================================================================


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Web Extractor Agent - Extract structured data from websites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  web-extractor
  
  # Extract from single URL
  web-extractor --url https://example.com --keywords "AI, technology"
  
  # Extract from multiple URLs
  web-extractor --url url1.com,url2.com --keywords "startup, funding"
  
  # Site-wide extraction
  web-extractor --url https://example.com --site --keywords "AI" --max-pages 10
  
  # Semantic query
  web-extractor --url https://example.com --query "Find all pricing information"
  
  # Save results to file
  web-extractor --url https://example.com --keywords "AI" --output results.json
"""
    )
    
    parser.add_argument(
        '--url', '-u',
        type=str,
        help='URL(s) to extract from (comma-separated for multiple)'
    )
    
    parser.add_argument(
        '--keywords', '-k',
        type=str,
        help='Keywords to search for (comma-separated)'
    )
    
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Semantic query (natural language)'
    )
    
    parser.add_argument(
        '--site', '-s',
        action='store_true',
        help='Extract from entire site (not just single page)'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=50,
        help='Maximum pages to crawl (default: 50)'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=3,
        help='Maximum crawl depth (default: 3)'
    )
    
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Disable LLM enhancement (faster but less accurate)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file for results (JSON format)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Web Extractor Agent v1.0.0'
    )
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # If no arguments provided, run interactive mode
    if len(sys.argv) == 1:
        interactive_mode()
        return
    
    # Parse URLs
    urls = []
    if args.url:
        urls = [u.strip() for u in args.url.split(',')]
        # Add https:// prefix if missing
        urls = [u if u.startswith(('http://', 'https://')) else 'https://' + u for u in urls]
    
    if not urls:
        print("❌ Error: URL is required")
        parser.print_help()
        sys.exit(1)
    
    # Parse keywords or query
    keywords = []
    query = None
    
    if args.query:
        query = args.query
    elif args.keywords:
        keywords = [k.strip() for k in args.keywords.split(',')]
    else:
        print("❌ Error: Either --keywords or --query is required")
        parser.print_help()
        sys.exit(1)
    
    use_llm = not args.no_llm
    
    try:
        agent = WebExtractionAgent(use_llm=use_llm)
        
        if args.site:
            # Site-wide extraction
            print(f"🕷️  Crawling site: {urls[0]}")
            print(f"📊 Max pages: {args.max_pages}, Max depth: {args.max_depth}")
            
            result = agent.extract_from_site_semantic(
                start_url=urls[0],
                query=query or ', '.join(keywords),
                max_pages=args.max_pages,
                max_depth=args.max_depth,
                use_llm=use_llm
            )
            
            print(f"\n✅ Crawled {result['total_pages_crawled']} pages")
            print(f"✅ Successful: {result['successful_extractions']}")
            
        else:
            # Single or multiple page extraction
            results = []
            
            for i, url in enumerate(urls, 1):
                print(f"\n🔍 Processing URL {i}/{len(urls)}: {url}")
                
                if query:
                    result = agent.extract_by_semantic_query(
                        url=url,
                        query=query,
                        use_llm=use_llm
                    )
                else:
                    result = agent.extract_by_keywords(
                        url=url,
                        keywords=keywords,
                        use_llm=use_llm
                    )
                
                results.append(result)
                
                # Show summary
                if 'keyword_extraction' in result:
                    kw_ext = result['keyword_extraction']
                    print(f"   ⭐ Relevance: {kw_ext['relevance_score']:.3f}")
                    print(f"   📊 Matches: {kw_ext['total_matches']}")
                print(f"   ⏱️  Time: {result['trace']['duration_ms']}ms")
            
            result = results[0] if len(results) == 1 else results
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {args.output}")
        
        # Print verbose output if requested
        if args.verbose:
            print(f"\n📄 Detailed Results:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\n✨ Extraction completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
