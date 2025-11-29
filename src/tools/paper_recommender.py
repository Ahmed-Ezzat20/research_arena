"""
Similar Paper Recommender Tool - Refactored with async and provider abstraction
Suggests contextually similar research papers using Semantic Scholar and arXiv.
"""

import re
import asyncio
from typing import List, Dict, Any, Optional
from src.logging import logger
from src.providers.base import BaseLLMProvider
from src.utils.api_clients import SemanticScholarAPI


class PaperRecommender:
    """Recommend similar papers based on paper ID, title, or content."""
    
    def __init__(self, provider: BaseLLMProvider):
        self.semantic_scholar = SemanticScholarAPI()
        self.provider = provider
    
    async def get_recommendations_by_id(self, paper_id: str, id_type: str = "doi", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get paper recommendations by paper ID.
        
        Args:
            paper_id: Paper identifier (DOI, arXiv ID, Semantic Scholar ID)
            id_type: Type of ID (doi, arxiv, s2)
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended paper dictionaries
        """
        logger.info(f"🔍 Getting recommendations for {id_type}: {paper_id}")
        
        try:
            # Format the paper ID based on type
            if id_type == "doi":
                paper_id_formatted = f"DOI:{paper_id}"
            elif id_type == "arxiv":
                paper_id_formatted = f"ARXIV:{paper_id}"
            else:
                paper_id_formatted = paper_id
            
            # Run API call in executor
            loop = asyncio.get_event_loop()
            recommendations = await loop.run_in_executor(
                None,
                lambda: self.semantic_scholar.get_recommendations(paper_id_formatted, limit=limit)
            )
            
            if recommendations:
                logger.info(f"✅ Found {len(recommendations)} recommendations")
                return recommendations
            else:
                logger.warning("⚠️ No recommendations found from Semantic Scholar")
                return []
        
        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {str(e)}")
            return []
    
    async def get_recommendations_by_title(self, title: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recommendations by searching for a paper by title first.
        
        Args:
            title: Paper title to search for
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended paper dictionaries
        """
        logger.info(f"🔍 Getting recommendations for title: '{title[:50]}...'")
        
        try:
            # First, find the paper by title
            loop = asyncio.get_event_loop()
            search_results = await loop.run_in_executor(
                None,
                lambda: self.semantic_scholar.search_paper(title, limit=1)
            )
            
            if not search_results:
                logger.warning("⚠️ Paper not found by title")
                return []
            
            # Get the paper ID
            paper = search_results[0]
            paper_id = paper.get('paperId')
            
            if not paper_id:
                logger.warning("⚠️ No Semantic Scholar ID found")
                return []
            
            logger.info(f"📚 Found paper: {paper.get('title', 'Unknown')}")
            
            # Get recommendations for this paper
            recommendations = await loop.run_in_executor(
                None,
                lambda: self.semantic_scholar.get_recommendations(paper_id, limit=limit)
            )
            
            if recommendations:
                logger.info(f"✅ Found {len(recommendations)} recommendations")
                return recommendations
            else:
                logger.warning("⚠️ No recommendations available for this paper")
                return []
        
        except Exception as e:
            logger.error(f"❌ Error getting recommendations by title: {str(e)}")
            return []
    
    async def get_recommendations_by_content(self, paper_content: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recommendations by analyzing paper content with LLM.
        
        Uses LLM to extract key topics and then searches for similar papers.
        
        Args:
            paper_content: Paper text content (abstract or full text)
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended paper dictionaries
        """
        logger.info(f"🔍 Getting recommendations based on content ({len(paper_content)} chars)")
        
        try:
            # Use LLM to extract key topics and generate search query
            logger.debug("📤 LLM REQUEST: Extracting key topics for similar paper search")
            
            topic_prompt = f"""
Analyze this research paper and extract the key topics, methods, and research areas.
Generate a focused search query (5-10 words) that would find similar papers.

Paper content (first 3000 chars):
{paper_content[:3000]}

Provide only the search query, no explanation.
"""
            
            response = await self.provider.generate_simple(topic_prompt, temperature=0.3)
            search_query = response.strip().strip('"')
            
            logger.info(f"🔍 Generated search query: '{search_query}'")
            
            # Search for similar papers
            loop = asyncio.get_event_loop()
            similar_papers = await loop.run_in_executor(
                None,
                lambda: self.semantic_scholar.search_paper(search_query, limit=limit)
            )
            
            if similar_papers:
                logger.info(f"✅ Found {len(similar_papers)} similar papers")
                return similar_papers
            else:
                logger.warning("⚠️ No similar papers found")
                return []
        
        except Exception as e:
            logger.error(f"❌ Error getting content-based recommendations: {str(e)}")
            return []
    
    def extract_paper_id_from_text(self, text: str) -> Optional[Dict[str, str]]:
        """
        Extract paper identifier (DOI or arXiv ID) from text.
        
        Args:
            text: Text containing potential paper identifiers
            
        Returns:
            Dictionary with 'id' and 'type' keys, or None if not found
        """
        # Try to find DOI
        doi_pattern = r'10\.\d{4,}/[^\s]+'
        doi_match = re.search(doi_pattern, text)
        
        if doi_match:
            return {'id': doi_match.group(0), 'type': 'doi'}
        
        # Try to find arXiv ID
        arxiv_pattern = r'arXiv:(\d{4}\.\d{4,5})'
        arxiv_match = re.search(arxiv_pattern, text, re.IGNORECASE)
        
        if arxiv_match:
            return {'id': arxiv_match.group(1), 'type': 'arxiv'}
        
        return None


async def recommend_similar_papers(
    paper_info: str,
    provider: BaseLLMProvider,
    num_recommendations: int = 10
) -> str:
    """
    Main function to recommend similar papers.
    
    Automatically detects paper ID in input or uses content-based matching.
    
    Args:
        paper_info: Paper information (DOI, title, or content)
        provider: LLM provider instance
        num_recommendations: Number of recommendations to return (default: 10)
        
    Returns:
        Formatted list of recommended papers
    """
    logger.info("="*80)
    logger.info("🔍 SIMILAR PAPER RECOMMENDER - Starting paper discovery")
    logger.info("="*80)
    
    recommender = PaperRecommender(provider)
    
    # Try to extract paper ID
    paper_id_info = recommender.extract_paper_id_from_text(paper_info)
    
    recommendations = []
    
    if paper_id_info:
        # Use ID-based recommendations
        logger.info(f"📋 Found {paper_id_info['type'].upper()}: {paper_id_info['id']}")
        recommendations = await recommender.get_recommendations_by_id(
            paper_id_info['id'],
            paper_id_info['type'],
            limit=num_recommendations
        )
    
    if not recommendations:
        # Try title-based search (check if input looks like a title)
        if len(paper_info) < 200 and not '\n\n' in paper_info:
            logger.info("📋 Treating input as paper title")
            recommendations = await recommender.get_recommendations_by_title(paper_info, limit=num_recommendations)
    
    if not recommendations:
        # Fall back to content-based recommendations
        logger.info("📋 Using content-based similarity search")
        recommendations = await recommender.get_recommendations_by_content(paper_info, limit=num_recommendations)
    
    # Format the results
    if not recommendations:
        logger.warning("⚠️ No recommendations found")
        return """⚠️ No similar papers found.

This could be because:
- The paper is very new or not yet indexed
- The search query was too specific
- The paper is in a very niche area

Try:
- Providing a DOI or arXiv ID for better results
- Using a more general description of the research area
- Checking if the paper title is spelled correctly
"""
    
    # Generate formatted output
    report = _format_recommendations(recommendations)
    
    logger.info(f"✅ Recommendation complete: {len(recommendations)} papers found")
    return report


def _format_recommendations(recommendations: List[Dict[str, Any]]) -> str:
    """Format recommendations into a readable report."""
    
    lines = []
    
    lines.append("=" * 80)
    lines.append("🔍 SIMILAR PAPER RECOMMENDATIONS")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Found {len(recommendations)} similar papers:")
    lines.append("")
    
    for i, paper in enumerate(recommendations, 1):
        lines.append("-" * 80)
        lines.append(f"[{i}] {paper.get('title', 'Unknown Title')}")
        lines.append("")
        
        # Authors
        authors = paper.get('authors', [])
        if authors:
            author_names = []
            for author in authors[:5]:  # Limit to first 5 authors
                if isinstance(author, dict):
                    author_names.append(author.get('name', ''))
                else:
                    author_names.append(str(author))
            
            author_str = ', '.join(author_names)
            if len(authors) > 5:
                author_str += f', et al. ({len(authors)} total authors)'
            
            lines.append(f"📝 Authors: {author_str}")
        
        # Year
        year = paper.get('year')
        if year:
            lines.append(f"📅 Year: {year}")
        
        # Venue
        venue = paper.get('venue') or paper.get('journal', {}).get('name')
        if venue:
            lines.append(f"📚 Venue: {venue}")
        
        # Citation count
        citations = paper.get('citationCount')
        if citations is not None:
            lines.append(f"🔗 Citations: {citations:,}")
        
        # Abstract
        abstract = paper.get('abstract')
        if abstract:
            # Truncate long abstracts
            if len(abstract) > 400:
                abstract = abstract[:400] + "..."
            lines.append(f"\n📄 Abstract:")
            lines.append(f"   {abstract}")
        
        # Links
        paper_id = paper.get('paperId')
        doi = paper.get('externalIds', {}).get('DOI') if isinstance(paper.get('externalIds'), dict) else None
        arxiv_id = paper.get('externalIds', {}).get('ArXiv') if isinstance(paper.get('externalIds'), dict) else None
        
        links = []
        if doi:
            links.append(f"DOI: https://doi.org/{doi}")
        if arxiv_id:
            links.append(f"arXiv: https://arxiv.org/abs/{arxiv_id}")
        if paper_id:
            links.append(f"Semantic Scholar: https://www.semanticscholar.org/paper/{paper_id}")
        
        if links:
            lines.append("\n🔗 Links:")
            for link in links:
                lines.append(f"   {link}")
        
        lines.append("")
    
    lines.append("=" * 80)
    lines.append("💡 Tips:")
    lines.append("  • Click the links to access full papers")
    lines.append("  • Check citation counts for impact assessment")
    lines.append("  • Review abstracts to gauge relevance")
    lines.append("  • Use DOI or arXiv links for reliable access")
    lines.append("")
    
    return "\n".join(lines)


async def quick_recommend(
    doi_or_arxiv: str,
    provider: BaseLLMProvider,
    num_papers: int = 5
) -> str:
    """
    Quick recommendation by DOI or arXiv ID.
    
    Args:
        doi_or_arxiv: DOI or arXiv ID
        provider: LLM provider instance
        num_papers: Number of papers to recommend (default: 5)
        
    Returns:
        Formatted recommendations
    """
    logger.info(f"🔍 Quick recommendation for: {doi_or_arxiv}")
    return await recommend_similar_papers(doi_or_arxiv, provider, num_recommendations=num_papers)
