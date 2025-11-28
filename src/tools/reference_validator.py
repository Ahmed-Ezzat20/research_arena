"""
Reference extraction and validation module.
Validates citations, DOIs, and reference metadata against academic databases.
"""

import re
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from src.config import GEMINI_MODEL_NAME
from src.logging import logger
from src.utils.api_clients import SemanticScholarAPI, CrossRefAPI, RateLimiter


class ReferenceExtractor:
    """Extract references from academic documents."""

    def __init__(self):
        self.model = genai.GenerativeModel(model_name=GEMINI_MODEL_NAME)

    def extract_references(self, document_text: str) -> List[Dict[str, str]]:
        """
        Extract all references from a document using LLM.

        Args:
            document_text: Full document text

        Returns:
            List of reference dictionaries with parsed components
        """
        logger.info("📚 Extracting references from document...")

        try:
            extraction_prompt = f"""
Extract ALL references/citations from this academic document.

For each reference, identify:
1. **citation_text**: The full citation as it appears in the document
2. **title**: Paper/book title
3. **authors**: Author names (comma-separated)
4. **year**: Publication year
5. **doi**: DOI if present (format: 10.xxxx/xxxx)
6. **url**: URL if present
7. **venue**: Journal/conference name if present

Format your response as a JSON array of objects with these fields.
If a field is not found, use empty string "".

Only extract references from the References/Bibliography section.
Do not extract in-text citations.

Document text (last 8000 chars, likely containing references):
{document_text[-8000:]}
"""

            logger.debug("📤 LLM REQUEST: Reference extraction")
            response = self.model.generate_content(extraction_prompt)
            logger.info("📥 LLM RESPONSE: References extracted")

            # Parse JSON response
            import json
            text = response.text.strip()

            # Extract JSON from markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            references = json.loads(text)
            logger.info(f"✅ Extracted {len(references)} references")

            return references

        except Exception as e:
            logger.error(f"❌ Error extracting references: {str(e)}")
            # Fallback: try regex-based extraction
            return self._fallback_extraction(document_text)

    def _fallback_extraction(self, document_text: str) -> List[Dict[str, str]]:
        """Fallback regex-based reference extraction."""
        logger.info("⚠️ Using fallback regex extraction")

        references = []
        # Simple DOI extraction
        doi_pattern = r'10\.\d{4,}/[^\s]+'
        dois = re.findall(doi_pattern, document_text[-8000:])

        for doi in dois[:20]:  # Limit to 20 references
            references.append({
                'citation_text': f"Reference with DOI: {doi}",
                'title': '',
                'authors': '',
                'year': '',
                'doi': doi,
                'url': '',
                'venue': ''
            })

        logger.info(f"⚠️ Fallback extracted {len(references)} DOIs")
        return references


class ReferenceValidator:
    """Validate references against academic databases."""

    def __init__(self):
        self.semantic_scholar = SemanticScholarAPI()
        self.crossref = CrossRefAPI()
        self.rate_limiter = RateLimiter(calls_per_second=2.0)

    def validate_reference(self, reference: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate a single reference.

        Args:
            reference: Reference dictionary with parsed components

        Returns:
            Validation result with status, matched metadata, and issues
        """
        logger.debug(f"🔍 Validating: {reference.get('title', 'Unknown')[:50]}...")

        result = {
            'original_reference': reference,
            'validation_status': 'Unknown',
            'matched_metadata': None,
            'issues': [],
            'confidence_score': 0.0,
            'doi_verified': False,
            'metadata_match': False,
            'url_accessible': False
        }

        # Step 1: Validate DOI if present
        if reference.get('doi'):
            self.rate_limiter.wait()
            doi_result = self._validate_doi(reference['doi'], reference)
            result.update(doi_result)

        # Step 2: If no DOI or DOI validation failed, try title search
        elif reference.get('title'):
            self.rate_limiter.wait()
            title_result = self._validate_by_title(reference)
            result.update(title_result)

        # Step 3: Check URL accessibility
        if reference.get('url'):
            url_status = self._check_url(reference['url'])
            result['url_accessible'] = url_status

        # Determine final validation status
        result['validation_status'] = self._determine_status(result)

        return result

    def _validate_doi(self, doi: str, reference: Dict[str, str]) -> Dict[str, Any]:
        """Validate reference by DOI."""
        result = {
            'doi_verified': False,
            'matched_metadata': None,
            'issues': [],
            'metadata_match': False
        }

        # Try Semantic Scholar first
        paper = self.semantic_scholar.get_paper_by_doi(doi)

        # If not found, try CrossRef
        if not paper:
            crossref_data = self.crossref.get_by_doi(doi)
            if crossref_data:
                paper = self._convert_crossref_to_standard(crossref_data)

        if paper:
            result['doi_verified'] = True
            result['matched_metadata'] = paper

            # Check metadata consistency
            metadata_issues = self._compare_metadata(reference, paper)
            result['issues'].extend(metadata_issues)
            result['metadata_match'] = len(metadata_issues) == 0

        else:
            result['issues'].append(f"DOI not found: {doi}")
            logger.warning(f"⚠️ DOI not found: {doi}")

        return result

    def _validate_by_title(self, reference: Dict[str, str]) -> Dict[str, Any]:
        """Validate reference by title search."""
        result = {
            'matched_metadata': None,
            'issues': [],
            'metadata_match': False
        }

        title = reference.get('title', '')
        if not title or len(title) < 10:
            result['issues'].append("Title too short or missing")
            return result

        # Try CrossRef search
        author = reference.get('authors', '').split(',')[0] if reference.get('authors') else None
        crossref_match = self.crossref.search_by_title(title, author)

        if crossref_match:
            result['matched_metadata'] = self._convert_crossref_to_standard(crossref_match)

            # Check metadata consistency
            metadata_issues = self._compare_metadata(reference, result['matched_metadata'])
            result['issues'].extend(metadata_issues)
            result['metadata_match'] = len(metadata_issues) == 0

        else:
            result['issues'].append("No database match found for title")
            logger.warning(f"⚠️ No match found for: {title[:50]}")

        return result

    def _compare_metadata(self, reference: Dict[str, str], matched: Dict[str, Any]) -> List[str]:
        """Compare reference metadata with database match."""
        issues = []

        # Compare title (fuzzy match)
        ref_title = reference.get('title', '').lower().strip()
        matched_title = ''

        if isinstance(matched.get('title'), list):
            matched_title = matched['title'][0].lower().strip() if matched['title'] else ''
        else:
            matched_title = str(matched.get('title', '')).lower().strip()

        if ref_title and matched_title:
            # Simple similarity check
            common_words = set(ref_title.split()) & set(matched_title.split())
            similarity = len(common_words) / max(len(ref_title.split()), len(matched_title.split()))

            if similarity < 0.5:
                issues.append(f"Title mismatch (similarity: {similarity:.0%})")

        # Compare year
        ref_year = reference.get('year', '')
        matched_year = str(matched.get('year', ''))

        if ref_year and matched_year and ref_year != matched_year:
            issues.append(f"Year mismatch: cited {ref_year}, actual {matched_year}")

        # Compare authors (basic check)
        ref_authors = reference.get('authors', '').lower()
        matched_authors = ''

        if 'authors' in matched and matched['authors']:
            if isinstance(matched['authors'], list):
                matched_authors = ' '.join([a.get('name', '') for a in matched['authors']]).lower()
            else:
                matched_authors = str(matched['authors']).lower()

        if ref_authors and matched_authors:
            # Check if any author name appears
            ref_author_list = [a.strip() for a in ref_authors.split(',')]
            if ref_author_list and not any(author in matched_authors for author in ref_author_list[:2]):
                issues.append("Author mismatch detected")

        return issues

    def _check_url(self, url: str) -> bool:
        """Check if URL is accessible."""
        try:
            import requests
            response = requests.head(url, timeout=5, allow_redirects=True)
            accessible = response.status_code < 400
            if accessible:
                logger.debug(f"✅ URL accessible: {url}")
            else:
                logger.warning(f"⚠️ URL not accessible ({response.status_code}): {url}")
            return accessible
        except Exception as e:
            logger.warning(f"⚠️ URL check failed: {url} - {str(e)}")
            return False

    def _convert_crossref_to_standard(self, crossref_data: Dict) -> Dict[str, Any]:
        """Convert CrossRef data format to standard format."""
        return {
            'title': crossref_data.get('title', [''])[0] if isinstance(crossref_data.get('title'), list) else crossref_data.get('title', ''),
            'authors': crossref_data.get('author', []),
            'year': crossref_data.get('published-print', {}).get('date-parts', [[None]])[0][0] or
                    crossref_data.get('published-online', {}).get('date-parts', [[None]])[0][0],
            'doi': crossref_data.get('DOI', ''),
            'url': crossref_data.get('URL', ''),
            'venue': crossref_data.get('container-title', [''])[0] if isinstance(crossref_data.get('container-title'), list) else crossref_data.get('container-title', '')
        }

    def _determine_status(self, result: Dict[str, Any]) -> str:
        """Determine overall validation status."""
        if result['doi_verified'] and result['metadata_match']:
            return '✅ Verified'
        elif result['doi_verified'] and not result['metadata_match']:
            return '⚠️ DOI Valid, Metadata Issues'
        elif result['matched_metadata']:
            return '⚠️ Matched, Minor Issues'
        elif len(result['issues']) > 0:
            return '❌ Validation Failed'
        else:
            return '❓ Could Not Verify'


def validate_all_references(document_text: str) -> Dict[str, Any]:
    """
    Main function to extract and validate all references in a document.

    Args:
        document_text: Full document text

    Returns:
        Dictionary with extraction and validation results
    """
    logger.info("🔍 Starting reference validation pipeline...")

    extractor = ReferenceExtractor()
    validator = ReferenceValidator()

    # Extract references
    references = extractor.extract_references(document_text)

    if not references:
        logger.warning("⚠️ No references extracted")
        return {
            'total_references': 0,
            'references': [],
            'validation_results': [],
            'summary': {
                'verified': 0,
                'with_issues': 0,
                'failed': 0,
                'unverifiable': 0
            }
        }

    # Validate each reference
    validation_results = []
    for i, ref in enumerate(references, 1):
        logger.info(f"📋 Validating reference {i}/{len(references)}...")
        result = validator.validate_reference(ref)
        validation_results.append(result)

    # Generate summary
    summary = {
        'verified': sum(1 for r in validation_results if r['validation_status'] == '✅ Verified'),
        'with_issues': sum(1 for r in validation_results if '⚠️' in r['validation_status']),
        'failed': sum(1 for r in validation_results if '❌' in r['validation_status']),
        'unverifiable': sum(1 for r in validation_results if '❓' in r['validation_status'])
    }

    logger.info(f"✅ Reference validation complete: {summary['verified']} verified, {summary['with_issues']} with issues, {summary['failed']} failed")

    return {
        'total_references': len(references),
        'references': references,
        'validation_results': validation_results,
        'summary': summary
    }
