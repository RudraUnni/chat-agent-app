import asyncio
import requests
import xml.etree.ElementTree as ET
import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import re
from agents import Agent, Runner, function_tool


logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


class ResearchMemory:
    def __init__(self):
        self.search_history = []
        self.analyzed_papers = {}
        self.research_context = ""
        self.current_research_thread = None
    
    def add_search(self, query, results):
        self.search_history.append({
            'query': query,
            'results': results,
            'timestamp': datetime.now(),
            'pmids_found': self.extract_pmids_from_results(results)
        })
    
    def add_paper_analysis(self, pmid, analysis):
        self.analyzed_papers[pmid] = {
            'analysis': analysis,
            'timestamp': datetime.now()
        }
    
    def get_context(self):
        if not self.search_history:
            return "No previous research context."
        
        recent_searches = self.search_history[-3:]
        context_parts = []
        
        for search in recent_searches:
            context_parts.append(f"- Searched: '{search['query']}'")
        
        analyzed_count = len(self.analyzed_papers)
        if analyzed_count > 0:
            context_parts.append(f"- Analyzed {analyzed_count} papers: {list(self.analyzed_papers.keys())}")
        
        return "RESEARCH SESSION CONTEXT:\n" + "\n".join(context_parts)
    
    def extract_pmids_from_results(self, results):
        pmids = re.findall(r'PMID: (\d+)', results)
        return pmids
    
    def get_analyzed_papers_for_synthesis(self):
        if len(self.analyzed_papers) < 2:
            return None
        return list(self.analyzed_papers.keys())
    
    def should_suggest_synthesis(self):
        return len(self.analyzed_papers) >= 2


@function_tool
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

@function_tool
def get_paper(pmid: str) -> str:
    """Get full text if available, otherwise return abstract with enhanced metadata."""
    try:
        log.info(f"Fetching paper metadata for PMID: {pmid}")
        fetch_meta = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params={'db': 'pubmed', 'id': pmid, 'retmode': 'xml'}, timeout=15)
        root_meta = ET.fromstring(fetch_meta.content)
        
        title = root_meta.findtext(".//ArticleTitle", default="No title")
        abstract = root_meta.findtext(".//AbstractText", default="No abstract available.")
        authors = [author.findtext(".//LastName", "") + " " + author.findtext(".//ForeName", "") 
                  for author in root_meta.findall(".//Author")]
        journal = root_meta.findtext(".//Journal/Title", "Unknown journal")
        pub_date = root_meta.findtext(".//PubDate/Year", "Unknown date")
        
        # Enhanced PMCID extraction with better error handling
        log.info(f"Attempting PMCID conversion for PMID: {pmid}")
        conv_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
        conv_res = requests.get(conv_url, params={'ids': pmid, 'format': 'json'}, timeout=10).json()
        records = conv_res.get('records', [])
        
        pmcid = None
        if not records:
            log.warning(f"No conversion records found for PMID {pmid}")
        elif len(records) == 0:
            log.warning(f"Empty records list for PMID {pmid}")
        elif 'pmcid' not in records[0]:
            log.warning(f"No PMCID found in first record for PMID {pmid}")
        else:
            pmcid = records[0].get('pmcid')
            log.info(f"Found PMCID: {pmcid} for PMID: {pmid}")

        if pmcid:
            try:
                log.info(f"Fetching full text for PMCID: {pmcid}")
                fetch_full = requests.get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                    params={'db': 'pmc', 'id': pmcid, 'retmode': 'xml'}, timeout=15)
                root_full = ET.fromstring(fetch_full.content)
                body_paragraphs = [p.text.strip() for p in root_full.findall(".//body//p") if p.text]
                body = "\n\n".join(body_paragraphs[:10])  
                
                log.info(f"Successfully extracted full text for PMCID: {pmcid}")
                return f"""FULL TEXT ANALYSIS (PMCID: {pmcid})

TITLE: {title}
AUTHORS: {', '.join(authors[:5])}{' et al.' if len(authors) > 5 else ''}
JOURNAL: {journal}
DATE: {pub_date}

ABSTRACT:
{abstract}

FULL TEXT (First 10 paragraphs):
{body}..."""
            except Exception as full_text_error:
                log.error(f"Failed to fetch full text for PMCID {pmcid}: {str(full_text_error)}")
                # Fallback to abstract only
                pmcid = None
        
        if not pmcid:
            log.info(f"Returning abstract-only analysis for PMID: {pmid}")
            return f"""ABSTRACT ANALYSIS (PMID: {pmid})

TITLE: {title}
AUTHORS: {', '.join(authors[:5])}{' et al.' if len(authors) > 5 else ''}
JOURNAL: {journal}
DATE: {pub_date}

ABSTRACT:
{abstract}

Note: Full text not available in PMC. Only abstract provided."""
    except Exception as e:
        log.error(f"Error fetching paper {pmid}: {str(e)}")
        return f"Fetch error: {str(e)}"

@function_tool
def compare_papers(pmid_list: str) -> str:
    """Compare multiple papers (comma-separated PMIDs) for similarities and differences."""
    pmids = [pmid.strip() for pmid in pmid_list.split(',')]
    if len(pmids) < 2:
        return "Please provide at least 2 PMIDs separated by commas for comparison."
    
    papers = []
    for pmid in pmids[:3]:  # Limit to 3 papers to avoid token limits
        paper_content = get_paper(pmid)
        papers.append(f"PAPER {pmid}:\n{paper_content}")
    
    comparison_prompt = f"""Compare these papers and provide analysis in this format:

{chr(10).join(papers)}

COMPARISON ANALYSIS:
SIMILARITIES: What the studies have in common (methods, populations, outcomes)
DIFFERENCES: Key differences in approach, findings, or methodology
COMPLEMENTARY INSIGHTS: How the studies work together to build understanding
CONFLICTS: Any contradictory findings and possible explanations
SYNTHESIS: What the collective evidence suggests"""
    
    return comparison_prompt

# Create a regular function for suggest_next_steps that can be called directly
def suggest_next_steps_func(current_context: str) -> str:
    """Analyze current research session and suggest logical next steps."""
    suggestions = []
    
    # Extract PMIDs from context
    pmids = re.findall(r'PMID: (\d+)', current_context)
    analyzed_papers = re.findall(r'Analyzed.*?(\d+)', current_context)
    
    if pmids and not analyzed_papers:
        suggestions.append(f"Analyze specific papers from your search: {', '.join(pmids[:3])}")
    
    if len(analyzed_papers) >= 2:
        suggestions.append("Compare and synthesize your analyzed papers")
    
    # Extract search terms for related suggestions
    searches = re.findall(r"Searched: '([^']+)'", current_context)
    if searches:
        latest_search = searches[-1]
        suggestions.append(f"Expand search with related terms to '{latest_search}'")
        suggestions.append(f"Look for systematic reviews or meta-analyses on '{latest_search}'")
    
    if not suggestions:
        suggestions.append("Search for a research topic of interest")
        suggestions.append("Analyze a specific paper by PMID")
    
    return "SUGGESTED NEXT STEPS:\n" + "\n".join(f"- {s}" for s in suggestions)

# Create the function_tool version for the agent
@function_tool
def suggest_next_steps(current_context: str) -> str:
    """Analyze current research session and suggest logical next steps."""
    return suggest_next_steps_func(current_context)


search_agent = Agent(
    name="Search Agent",
    instructions="""You are a specialized PubMed search agent. Your role is to:
1. Conduct comprehensive searches on PubMed
2. Provide detailed summaries of search results including titles, authors, journals, and dates
3. Help users find relevant papers for their research topics
4. Suggest related search terms when appropriate
5. Always provide PMIDs for papers so users can request full analysis

When responding:
- Format results clearly with PMID, title, authors, journal, and date
- Suggest follow-up searches if the initial results are limited
- Highlight the most relevant papers based on the query
- Ask clarifying questions if the search query is ambiguous
- Consider the user's research context when suggesting next steps""",
    tools=[search_pubmed],
    model="gpt-4o-mini"
)

reader_agent = Agent(
    name="Reader Agent",
    instructions="""You are a specialized paper analysis agent. Your role is to:
1. Analyze full papers or abstracts from PubMed using PMIDs
2. Provide comprehensive summaries including methodology, key findings, and conclusions
3. Extract key insights and implications from the research
4. Identify limitations and future research directions
5. Connect findings to broader research context

When analyzing papers:
- Start with the title, authors, and publication details
- Summarize the abstract or full text clearly
- Highlight the main research question and methodology
- Extract key findings and their significance
- Note any limitations or areas for future research
- Suggest related research directions
- Consider how this paper relates to the user's ongoing research""",
    tools=[get_paper],
    model="gpt-4o-mini"
)

synthesis_agent = Agent(
    name="Synthesis Agent",
    instructions="""You synthesize findings across multiple papers to provide comprehensive analysis. When given multiple studies:

1. CONSENSUS FINDINGS: Identify what most studies agree on
2. CONFLICTING RESULTS: Highlight where studies disagree and analyze why
3. METHODOLOGICAL DIFFERENCES: Compare study designs and their impact on results
4. RESEARCH GAPS: Identify what's missing or needs more investigation
5. OVERALL CONCLUSION: Provide your synthesis of the collective evidence
6. FUTURE DIRECTIONS: Suggest next research priorities

Format your response clearly with these sections. Focus on:
- Strength of evidence across studies
- Clinical or practical implications
- Areas where more research is needed
- How different methodologies affect conclusions

Always explain your reasoning and highlight the most important insights.""",
    tools=[compare_papers],
    model="gpt-4o-mini"
)

query_enhancer = Agent(
    name="Query Enhancer",
    instructions="""You improve search queries to get better PubMed results by:

1. Adding relevant medical synonyms and terms
2. Suggesting MeSH terms when appropriate
3. Expanding abbreviations (e.g., MI → myocardial infarction)
4. Adding related concepts the user might not have considered
5. Using appropriate Boolean operators (AND, OR, NOT)

EXAMPLE TRANSFORMATIONS:
- "diabetes treatment" → "diabetes mellitus treatment OR antidiabetic agents OR glycemic control OR insulin therapy"
- "heart attack" → "myocardial infarction OR acute coronary syndrome OR STEMI OR NSTEMI"

Always:
- Explain why you enhanced the query
- Show the original vs enhanced version
- Suggest multiple search variations if helpful
- Consider the user's research context""",
    model="gpt-4o-mini"
)

orchestrator = Agent(
    name="Enhanced Orchestrator",
    instructions="""You are the intelligent orchestrator for a multi-agent PubMed research system with memory and context awareness.

CONTEXT AWARENESS:
- Always consider the user's research session history
- Build on previous findings rather than repeating information
- Connect new searches to previous research threads
- Remember what papers have been analyzed

ROUTING DECISIONS:
- Use Search Agent for topic-based queries
- Use Reader Agent for specific paper analysis (PMID requests)
- Use Synthesis Agent when user wants to compare/synthesize multiple papers
- Use Query Enhancer when search terms need improvement

MEMORY INTEGRATION:
- Reference previous searches: "Building on your previous search about X..."
- Connect related papers: "This relates to the earlier paper on Y..."
- Suggest synthesis when multiple papers have been analyzed
- Avoid repeating previous analyses

PROACTIVE SUGGESTIONS:
- Suggest paper analysis after successful searches
- Recommend synthesis when 2+ papers are analyzed
- Propose related searches based on findings
- Guide users toward comprehensive research coverage

Always provide clear, actionable insights and maintain research continuity.""",
    model="gpt-4o-mini",
    tools=[
        search_agent.as_tool("search_pubmed", "Search PubMed for papers on a topic"),
        reader_agent.as_tool("analyze_paper", "Analyze a specific paper by PMID"),
        synthesis_agent.as_tool("synthesize_papers", "Compare and synthesize multiple papers"),
        query_enhancer.as_tool("enhance_query", "Improve search query for better results"),
        suggest_next_steps
    ]
)


def format_context_input(user_input: str, research_memory: ResearchMemory) -> str:
    """Format user input with research context."""
    context = research_memory.get_context()
    if context != "No previous research context.":
        return f"{context}\n\nCURRENT QUERY: {user_input}"
    return user_input

def determine_agent_routing(user_input: str, research_memory: ResearchMemory) -> tuple:
    """Determine which agent to use and prepare the input."""

    if any(keyword in user_input.lower() for keyword in ["synthesize", "compare", "synthesis"]):
        analyzed_papers = research_memory.get_analyzed_papers_for_synthesis()
        if analyzed_papers:
            synthesis_input = f"Synthesize findings from these analyzed papers: {', '.join(analyzed_papers)}\n\nContext: {format_context_input(user_input, research_memory)}"
            return "synthesis", synthesis_input
        else:
            return "orchestrator", format_context_input(user_input, research_memory)
    else:
        return "orchestrator", format_context_input(user_input, research_memory)

async def handle_user_query(user_input: str, research_memory: ResearchMemory) -> str:
    """Handle user query by routing to appropriate agent and processing result."""
    
    agent_type, enhanced_input = determine_agent_routing(user_input, research_memory)
    
    if agent_type == "synthesis":
        result = await Runner.run(synthesis_agent, enhanced_input)
    else:
        result = await Runner.run(orchestrator, enhanced_input)
    
    return result.final_output

def extract_pmids_from_text(text: str) -> List[str]:
    """Extract PMID numbers from text."""
    return re.findall(r'PMID:?\s*(\d+)', text)

def update_memory_based_on_result(result: str, user_input: str, research_memory: ResearchMemory):
    """Update research memory based on interaction result."""
    
    research_memory.add_search(user_input, result)
    
    if "PMID:" in result and any(keyword in user_input.lower() for keyword in ["analyze", "pmid"]):
        pmids = extract_pmids_from_text(user_input)
        for pmid in pmids:
            research_memory.add_paper_analysis(pmid, result)



def print_welcome_message():
    """Print the system welcome message."""
    print("Enhanced Multi-Agent PubMed Research System")
    print("=" * 50)
    print("Available commands:")
    print("- Search topics: 'cancer immunotherapy'")
    print("- Analyze papers: 'analyze PMID 12345678'")
    print("- Compare papers: 'compare PMID1, PMID2, PMID3'")
    print("- Synthesize findings: 'synthesize my analyzed papers'")
    print("- Enhance search: 'improve my search for diabetes'")
    print("- Get suggestions: 'what should I do next?'")
    print("- Exit: 'quit' or 'exit'")
    print("=" * 50)

def print_results(result: str):
    """Print results in formatted way."""
    print("Results:")
    print("-" * 30)
    print(result)
    print("\n" + "=" * 80)

async def main():
    """Main application loop with improved separation of concerns."""
    print_welcome_message()
    
    research_memory = ResearchMemory()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ["quit", "exit"]:
                print("\nThanks!")
                log.warning("User exited application")
                break
                
            if not user_input:
                continue
            
            print("\nProcessing with multi-agent system...\n")
            
            result = await handle_user_query(user_input, research_memory)
            
            update_memory_based_on_result(result, user_input, research_memory)
            
            print_results(result)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again with a different query.")

if __name__ == "__main__":
    asyncio.run(main())