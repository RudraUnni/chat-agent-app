import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from .runtime import function_tool


@function_tool(
    name="search_pubmed",
    description="Search PubMed and return paper summaries with enhanced metadata."
)
def search_pubmed(query: str, max_results: int = 5) -> str:
    """Search PubMed and return paper summaries with enhanced metadata."""
    try:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {'db': 'pubmed', 'term': query, 'retmax': max_results, 'retmode': 'json'}
        res = requests.get(url, params=params, timeout=15).json()
        pmids = res.get('esearchresult', {}).get('idlist', [])
        if not pmids:
            return "No results found for the given query."

        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        summary_params = {'db': 'pubmed', 'id': ','.join(pmids), 'retmode': 'json'}
        summaries = requests.get(summary_url, params=summary_params, timeout=15).json()

        output = []
        for pmid in pmids:
            paper = summaries['result'][pmid]
            title = paper.get('title', 'No title')
            authors = paper.get('authors', [])
            pub_date = paper.get('pubdate', 'Unknown date')
            journal = paper.get('fulljournalname', 'Unknown journal')
            
            author_list = ", ".join([author.get('name', '') for author in authors[:3]])
            if len(authors) > 3:
                author_list += f" et al. ({len(authors)} authors)"
            
            output.append(f"PMID: {pmid}\nTitle: {title}\nAuthors: {author_list}\nJournal: {journal}\nDate: {pub_date}\n")
        
        return "\n".join(output)
    except Exception as e:
        return f"Search error: {str(e)}"


@function_tool(
    name="get_paper",
    description="Get full text if available, otherwise return abstract with enhanced metadata."
)
def get_paper(pmid: str) -> str:
    """Get full text if available, otherwise return abstract with enhanced metadata."""
    try:
        fetch_meta = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params={'db': 'pubmed', 'id': pmid, 'retmode': 'xml'}, timeout=15)
        root_meta = ET.fromstring(fetch_meta.content)
        
        title = root_meta.findtext(".//ArticleTitle", default="No title")
        abstract = root_meta.findtext(".//AbstractText", default="No abstract available.")
        authors = [
            (author.findtext(".//LastName", "") + " " + author.findtext(".//ForeName", "")).strip()
            for author in root_meta.findall(".//Author")
        ]
        journal = root_meta.findtext(".//Journal/Title", "Unknown journal")
        pub_date = root_meta.findtext(".//PubDate/Year", "Unknown date")
        
        conv_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
        conv_res = requests.get(conv_url, params={'ids': pmid, 'format': 'json'}, timeout=10).json()
        records = conv_res.get('records', [])
        pmcid = records[0].get('pmcid') if records else None

        if pmcid:
            fetch_full = requests.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                params={'db': 'pmc', 'id': pmcid, 'retmode': 'xml'}, timeout=15)
            root_full = ET.fromstring(fetch_full.content)
            body_paragraphs = [p.text.strip() for p in root_full.findall(".//body//p") if p.text]
            body = "\n\n".join(body_paragraphs[:10])  
            
            return f"""FULL TEXT ANALYSIS (PMCID: {pmcid})

TITLE: {title}
AUTHORS: {', '.join(authors[:5])}{' et al.' if len(authors) > 5 else ''}
JOURNAL: {journal}
DATE: {pub_date}

ABSTRACT:
{abstract}

FULL TEXT (First 10 paragraphs):
{body}..."""
        else:
            return f"""ABSTRACT ANALYSIS (PMID: {pmid})

TITLE: {title}
AUTHORS: {', '.join(authors[:5])}{' et al.' if len(authors) > 5 else ''}
JOURNAL: {journal}
DATE: {pub_date}

ABSTRACT:
{abstract}

Note: Full text not available in PMC. Only abstract provided."""
    except Exception as e:
        return f"Fetch error: {str(e)}"