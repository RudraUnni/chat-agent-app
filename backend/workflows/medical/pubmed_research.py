import asyncio
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from workflows.base import BaseWorkflow, WorkflowContext, WorkflowResult
from app.services.llm.factory import LLMFactory
from app.services.llm.base import Message
from app.core.config import settings
import re


class PubMedService:
    """Service for interacting with PubMed API"""
    
    @staticmethod
    def search_pubmed(query: str, max_results: int = None) -> Dict[str, any]:
        """Search PubMed and return paper summaries"""
        max_results = max_results or settings.pubmed_max_results
        
        try:
            # Search for papers
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json'
            }
            search_response = requests.get(
                search_url,
                params=search_params,
                timeout=settings.pubmed_timeout
            ).json()
            
            pmids = search_response.get('esearchresult', {}).get('idlist', [])
            if not pmids:
                return {
                    'success': False,
                    'message': 'No results found',
                    'papers': []
                }
            
            # Get summaries
            summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            summary_params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'retmode': 'json'
            }
            summaries = requests.get(
                summary_url,
                params=summary_params,
                timeout=settings.pubmed_timeout
            ).json()
            
            papers = []
            for pmid in pmids:
                paper_data = summaries['result'][pmid]
                papers.append({
                    'pmid': pmid,
                    'title': paper_data.get('title', 'No title'),
                    'authors': [author.get('name', '') for author in paper_data.get('authors', [])[:3]],
                    'journal': paper_data.get('fulljournalname', 'Unknown journal'),
                    'pub_date': paper_data.get('pubdate', 'Unknown date')
                })
            
            return {
                'success': True,
                'papers': papers,
                'total_found': len(papers)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'papers': []
            }
    
    @staticmethod
    def get_paper_details(pmid: str) -> Dict[str, any]:
        """Get detailed information about a specific paper"""
        try:
            # Fetch paper metadata
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'xml'
            }
            response = requests.get(
                fetch_url,
                params=fetch_params,
                timeout=settings.pubmed_timeout
            )
            
            root = ET.fromstring(response.content)
            
            # Extract paper details
            title = root.findtext(".//ArticleTitle", default="No title")
            abstract = root.findtext(".//AbstractText", default="No abstract available")
            
            authors = []
            for author in root.findall(".//Author")[:5]:
                last_name = author.findtext(".//LastName", "")
                first_name = author.findtext(".//ForeName", "")
                if last_name:
                    authors.append(f"{last_name} {first_name}".strip())
            
            journal = root.findtext(".//Journal/Title", "Unknown journal")
            pub_year = root.findtext(".//PubDate/Year", "Unknown year")
            
            # Try to get PMCID for full text
            pmcid = None
            try:
                conv_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
                conv_response = requests.get(
                    conv_url,
                    params={'ids': pmid, 'format': 'json'},
                    timeout=10
                ).json()
                
                records = conv_response.get('records', [])
                if records and 'pmcid' in records[0]:
                    pmcid = records[0]['pmcid']
            except:
                pass
            
            return {
                'success': True,
                'pmid': pmid,
                'pmcid': pmcid,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'journal': journal,
                'pub_year': pub_year,
                'has_full_text': pmcid is not None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'pmid': pmid
            }


class PubMedResearchWorkflow(BaseWorkflow):
    """Workflow for PubMed research with multi-agent capabilities"""
    
    def __init__(self):
        super().__init__(
            name="PubMed Research Assistant",
            description="Advanced PubMed search and analysis workflow"
        )
        self.pubmed_service = PubMedService()
    
    async def execute(
        self,
        input_data: Dict[str, any],
        context: Optional[WorkflowContext] = None
    ) -> WorkflowResult:
        """Execute PubMed research workflow"""
        
        try:
            action = input_data.get('action', 'search')
            
            if action == 'search':
                return await self._handle_search(input_data, context)
            elif action == 'analyze':
                return await self._handle_analysis(input_data, context)
            elif action == 'compare':
                return await self._handle_comparison(input_data, context)
            elif action == 'synthesize':
                return await self._handle_synthesis(input_data, context)
            else:
                return WorkflowResult(
                    success=False,
                    error=f"Unknown action: {action}"
                )
                
        except Exception as e:
            return WorkflowResult(
                success=False,
                error=str(e)
            )
    
    async def _handle_search(
        self,
        input_data: Dict[str, any],
        context: WorkflowContext
    ) -> WorkflowResult:
        """Handle search queries"""
        query = input_data.get('query', '')
        if not query:
            return WorkflowResult(
                success=False,
                error="Search query is required"
            )
        
        # Enhance query if requested
        if input_data.get('enhance_query', False):
            enhanced_query = await self._enhance_search_query(query)
            query = enhanced_query
        
        # Search PubMed
        results = self.pubmed_service.search_pubmed(query)
        
        if not results['success']:
            return WorkflowResult(
                success=False,
                error=results.get('error', 'Search failed')
            )
        
        # Format results with LLM
        formatted_results = await self._format_search_results(results['papers'], query)
        
        return WorkflowResult(
            success=True,
            data={
                'query': query,
                'papers': results['papers'],
                'formatted_summary': formatted_results,
                'total_found': results['total_found']
            }
        )
    
    async def _handle_analysis(
        self,
        input_data: Dict[str, any],
        context: WorkflowContext
    ) -> WorkflowResult:
        """Handle paper analysis"""
        pmid = input_data.get('pmid', '')
        if not pmid:
            return WorkflowResult(
                success=False,
                error="PMID is required for analysis"
            )
        
        # Get paper details
        paper = self.pubmed_service.get_paper_details(pmid)
        
        if not paper['success']:
            return WorkflowResult(
                success=False,
                error=paper.get('error', 'Failed to fetch paper')
            )
        
        # Analyze with LLM
        analysis = await self._analyze_paper(paper)
        
        return WorkflowResult(
            success=True,
            data={
                'pmid': pmid,
                'paper': paper,
                'analysis': analysis
            }
        )
    
    async def _handle_comparison(
        self,
        input_data: Dict[str, any],
        context: WorkflowContext
    ) -> WorkflowResult:
        """Handle multiple paper comparison"""
        pmids = input_data.get('pmids', [])
        if len(pmids) < 2:
            return WorkflowResult(
                success=False,
                error="At least 2 PMIDs required for comparison"
            )
        
        # Fetch all papers
        papers = []
        for pmid in pmids[:3]:  # Limit to 3 papers
            paper = self.pubmed_service.get_paper_details(pmid)
            if paper['success']:
                papers.append(paper)
        
        if len(papers) < 2:
            return WorkflowResult(
                success=False,
                error="Could not fetch enough papers for comparison"
            )
        
        # Compare with LLM
        comparison = await self._compare_papers(papers)
        
        return WorkflowResult(
            success=True,
            data={
                'papers': papers,
                'comparison': comparison
            }
        )
    
    async def _handle_synthesis(
        self,
        input_data: Dict[str, any],
        context: WorkflowContext
    ) -> WorkflowResult:
        """Handle research synthesis"""
        papers = input_data.get('papers', [])
        topic = input_data.get('topic', 'research findings')
        
        if not papers:
            return WorkflowResult(
                success=False,
                error="No papers provided for synthesis"
            )
        
        # Synthesize findings
        synthesis = await self._synthesize_research(papers, topic)
        
        return WorkflowResult(
            success=True,
            data={
                'synthesis': synthesis,
                'paper_count': len(papers)
            }
        )
    
    async def _enhance_search_query(self, query: str) -> str:
        """Enhance search query with medical terms"""
        llm = LLMFactory.create(settings.default_llm_provider)
        
        messages = [
            Message(
                role="system",
                content="You are a medical search query enhancer. Expand queries with relevant medical terms, MeSH terms, and synonyms."
            ),
            Message(
                role="user",
                content=f"Enhance this PubMed search query: {query}"
            )
        ]
        
        response = await llm.generate(messages, temperature=0.3)
        return response.content
    
    async def _format_search_results(self, papers: List[Dict], query: str) -> str:
        """Format search results with LLM"""
        llm = LLMFactory.create(settings.default_llm_provider)
        
        papers_text = "\n".join([
            f"- {p['title']} (PMID: {p['pmid']}, {p['pub_date']})"
            for p in papers
        ])
        
        messages = [
            Message(
                role="system",
                content="You are a medical research assistant. Summarize PubMed search results clearly and concisely."
            ),
            Message(
                role="user",
                content=f"Summarize these search results for '{query}':\n{papers_text}"
            )
        ]
        
        response = await llm.generate(messages, temperature=0.3)
        return response.content
    
    async def _analyze_paper(self, paper: Dict) -> str:
        """Analyze a paper with LLM"""
        llm = LLMFactory.create(settings.default_llm_provider)
        
        messages = [
            Message(
                role="system",
                content="You are a medical research analyst. Provide clear, structured analysis of research papers."
            ),
            Message(
                role="user",
                content=f"""Analyze this paper:
                Title: {paper['title']}
                Abstract: {paper['abstract']}
                
                Provide:
                1. Key findings
                2. Methodology
                3. Clinical implications
                4. Limitations"""
            )
        ]
        
        response = await llm.generate(messages, temperature=0.3)
        return response.content
    
    async def _compare_papers(self, papers: List[Dict]) -> str:
        """Compare multiple papers"""
        llm = LLMFactory.create(settings.default_llm_provider)
        
        papers_text = "\n\n".join([
            f"Paper {i+1} (PMID: {p['pmid']}):\nTitle: {p['title']}\nAbstract: {p['abstract']}"
            for i, p in enumerate(papers)
        ])
        
        messages = [
            Message(
                role="system",
                content="You are a medical research analyst. Compare research papers systematically."
            ),
            Message(
                role="user",
                content=f"""Compare these papers:
                {papers_text}
                
                Provide:
                1. Similarities
                2. Differences
                3. Complementary insights
                4. Overall synthesis"""
            )
        ]
        
        response = await llm.generate(messages, temperature=0.3)
        return response.content
    
    async def _synthesize_research(self, papers: List[Dict], topic: str) -> str:
        """Synthesize research findings"""
        llm = LLMFactory.create(settings.default_llm_provider)
        
        messages = [
            Message(
                role="system",
                content="You are a medical research synthesizer. Create comprehensive research summaries."
            ),
            Message(
                role="user",
                content=f"Synthesize {len(papers)} papers on {topic}. Focus on consensus findings, gaps, and future directions."
            )
        ]
        
        response = await llm.generate(messages, temperature=0.3)
        return response.content