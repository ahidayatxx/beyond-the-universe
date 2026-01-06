#!/usr/bin/env python3
"""
APA 7th Edition Citation Formatter

Formats PubMed articles in APA 7th edition style for EBM analysis reports.

APA 7th Edition Format:
Author, A. A., & Author, B. B. (Year). Title of article. *Journal Name*, *Volume*(Issue), pages. DOI

Usage:
    from apa_formatter import APAFormatter

    formatter = APAFormatter()
    citation = formatter.format_article(article_dict, index=1)
    # Returns: "**Smith et al.** (2020). Article title. *Journal*, *10*(2), 123-45. https://doi.org/...
"""

from typing import Dict, List, Optional


class APAFormatter:
    """Format citations in APA 7th edition style."""

    def format_article(self, article: Dict, index: Optional[int] = None) -> str:
        """
        Format a single article in APA 7th edition style.

        Args:
            article: PubMed article dictionary with fields:
                - authors: List of author dicts with lastName, initials
                - firstAuthor: Fallback first author name
                - pubYear: Publication year
                - title: Article title
                - journal: Journal name
                - journalVolume: Volume number
                - journalIssue: Issue number
                - pages: Page numbers
                - doi: DOI or URL
            index: Optional reference number for numbered lists

        Returns:
            Formatted APA citation with markdown bolding for authors
        """
        # Get authors
        authors = self._format_authors(article)

        # Get year
        year = article.get('pubYear', 'n.d.')

        # Get title
        title = article.get('title', '')
        if title:
            title = title.rstrip('.')

        # Get journal
        journal = article.get('journal', 'Unknown Journal')

        # Build citation
        if index:
            citation = f"{index}. **{authors}** ({year}). {title}. *{journal}*"
        else:
            citation = f"**{authors}** ({year}). {title}. *{journal}*"

        # Add volume and issue
        volume = article.get('journalVolume', '')
        issue = article.get('journalIssue', '')

        if volume:
            citation += f", *{volume}*"
            if issue:
                citation += f"({issue})"

        # Add pages
        pages = article.get('pages', '')
        if pages:
            citation += f", {pages}"

        # Add DOI
        doi = article.get('doi', '')
        if doi:
            if not doi.startswith('http'):
                doi = f'https://doi.org/{doi}'
            citation += f". {doi}"

        return citation

    def _format_authors(self, article: Dict) -> str:
        """
        Format author list in APA 7th edition style.

        APA 7th Rules:
        - 1 author: Author, A. A.
        - 2 authors: Author, A. A., & Author, B. B.
        - 3-20 authors: List all, with & before last
        - 21+ authors: List first 19, then ..., then last author

        Args:
            article: Article dictionary with authors field

        Returns:
            Formatted author string
        """
        authors = article.get('authors', [])

        if not authors:
            # Fallback to firstAuthor field
            first_author = article.get('firstAuthor', 'Unknown Author')
            return first_author

        # Format up to 20 authors (APA 7th rule)
        if len(authors) <= 20:
            formatted_authors = []
            for author in authors:
                if 'lastName' in author and 'initials' in author:
                    last = author['lastName']
                    initials = author['initials']
                    formatted_authors.append(f"{last}, {initials}")
                elif 'name' in author:
                    formatted_authors.append(author['name'])

            if not formatted_authors:
                return article.get('firstAuthor', 'Unknown Author')

            if len(formatted_authors) == 1:
                return formatted_authors[0]
            elif len(formatted_authors) == 2:
                return f"{formatted_authors[0]} & {formatted_authors[1]}"
            else:
                return ', '.join(formatted_authors[:-1]) + f", & {formatted_authors[-1]}"
        else:
            # More than 20 authors: list first 19, then ..., then last
            first_19 = authors[:19]
            last_author = authors[-1]

            formatted_first = []
            for author in first_19:
                if 'lastName' in author and 'initials' in author:
                    formatted_first.append(f"{author['lastName']}, {author['initials']}")

            if not formatted_first:
                return article.get('firstAuthor', 'Unknown Authors')

            last_name = last_author.get('lastName', '')
            last_initials = last_author.get('initials', '')
            last_formatted = f"{last_name}, {last_initials}"

            return ', '.join(formatted_first) + f", ... , {last_formatted}"

    def format_references(self, articles: List[Dict]) -> str:
        """
        Format a list of articles as a complete references section.

        Args:
            articles: List of article dictionaries

        Returns:
            Complete references section with numbered citations
        """
        references = []
        for i, article in enumerate(articles, 1):
            citation = self.format_article(article, index=i)
            references.append(citation)

        return '\n\n'.join(references)


def main():
    """Command-line interface for testing APA formatting."""
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        description='Format PubMed articles in APA 7th edition style'
    )
    parser.add_argument(
        '--article',
        type=str,
        help='JSON string with article data'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='JSON file with article data'
    )
    parser.add_argument(
        '--index',
        type=int,
        help='Reference number (optional)'
    )

    args = parser.parse_args()

    # Get article data
    if args.file:
        with open(args.file, 'r') as f:
            article = json.load(f)
    elif args.article:
        article = json.loads(args.article)
    else:
        parser.error("Must provide --article or --file")

    # Format citation
    formatter = APAFormatter()
    citation = formatter.format_article(article, index=args.index)

    print(citation)


if __name__ == '__main__':
    main()
