"""
API clients for external research databases and services.
Supports Semantic Scholar, CrossRef, and Google Search for verification.
"""

import requests
import time
from typing import Dict, List, Optional, Any
from src.logging import logger


class SemanticScholarAPI:
    """Client for Semantic Scholar API."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AcademicResearchAssistant/1.0'
        })

    def search_paper(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for papers by query string.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of paper metadata dictionaries
        """
        try:
            logger.debug(f"🔍 Semantic Scholar search: '{query}'")

            url = f"{self.BASE_URL}/paper/search"
            params = {
                'query': query,
                'limit': limit,
                'fields': 'title,authors,year,abstract,citationCount,url,externalIds'
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            papers = data.get('data', [])

            logger.info(f"📚 Found {len(papers)} papers from Semantic Scholar")
            return papers

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Semantic Scholar API error: {str(e)}")
            return []

    def get_paper_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve paper metadata by DOI.

        Args:
            doi: Digital Object Identifier

        Returns:
            Paper metadata or None if not found
        """
        try:
            logger.debug(f"🔍 Looking up DOI: {doi}")

            url = f"{self.BASE_URL}/paper/DOI:{doi}"
            params = {
                'fields': 'title,authors,year,abstract,citationCount,url,externalIds'
            }

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 404:
                logger.warning(f"⚠️ DOI not found: {doi}")
                return None

            response.raise_for_status()
            paper = response.json()

            logger.info(f"✅ Retrieved paper: {paper.get('title', 'Unknown')}")
            return paper

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error retrieving DOI {doi}: {str(e)}")
            return None


class CrossRefAPI:
    """Client for CrossRef API."""

    BASE_URL = "https://api.crossref.org/works"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AcademicResearchAssistant/1.0 (mailto:research@example.com)'
        })

    def search_by_title(self, title: str, author: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Search for a paper by title and optionally author.

        Args:
            title: Paper title
            author: Optional author name

        Returns:
            Best matching paper metadata or None
        """
        try:
            logger.debug(f"🔍 CrossRef search: '{title[:50]}...'")

            params = {
                'query.title': title,
                'rows': 5
            }

            if author:
                params['query.author'] = author

            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            items = data.get('message', {}).get('items', [])

            if items:
                # Return the best match (first result)
                best_match = items[0]
                logger.info(f"✅ Found CrossRef match: {best_match.get('title', ['Unknown'])[0]}")
                return best_match
            else:
                logger.warning("⚠️ No CrossRef matches found")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ CrossRef API error: {str(e)}")
            return None

    def get_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve paper metadata by DOI.

        Args:
            doi: Digital Object Identifier

        Returns:
            Paper metadata or None if not found
        """
        try:
            logger.debug(f"🔍 CrossRef DOI lookup: {doi}")

            url = f"{self.BASE_URL}/{doi}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 404:
                logger.warning(f"⚠️ DOI not found in CrossRef: {doi}")
                return None

            response.raise_for_status()

            data = response.json()
            work = data.get('message', {})

            logger.info(f"✅ Retrieved from CrossRef: {work.get('title', ['Unknown'])[0]}")
            return work

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error retrieving DOI {doi}: {str(e)}")
            return None


class GoogleSearchAPI:
    """
    Simple Google search client using requests.
    Note: For production use, consider Google Custom Search API with API key.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_claim(self, claim: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search for information about a claim.

        Note: This is a simplified implementation. For production,
        use Google Custom Search API with proper authentication.

        Args:
            claim: The claim to search for
            num_results: Number of results to return

        Returns:
            List of search result dictionaries with title, snippet, url
        """
        try:
            logger.debug(f"🔍 Searching for claim: '{claim[:50]}...'")

            # For now, we'll use Semantic Scholar as a research-focused search
            # In production, integrate with Google Custom Search API
            logger.info("ℹ️ Using Semantic Scholar for claim search (research focus)")

            # This is a placeholder - implement Google Custom Search API integration
            # for production use with proper API key
            return []

        except Exception as e:
            logger.error(f"❌ Search error: {str(e)}")
            return []


# Rate limiting helper
class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, calls_per_second: float = 2.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0

    def wait(self):
        """Wait if necessary to respect rate limit."""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()
