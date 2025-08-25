from .runtime import Agent
from .tools import search_pubmed, get_paper


search_agent = Agent(
    name="Search Agent",
    instructions=(
        "You are a specialized PubMed search agent. When given a search query, "
        "use the search_pubmed tool to find relevant papers. Provide detailed "
        "summaries including PMID, title, authors, journal, and date. "
        "Always interpret and explain the search results in a helpful way."
    ),
    tools=[search_pubmed],
    model="gpt-4o-mini",
)

reader_agent = Agent(
    name="Reader Agent",
    instructions=(
        "You analyze papers from PubMed by PMID. Use the get_paper tool to fetch "
        "paper details and provide comprehensive summaries including methodology, "
        "key findings, and conclusions. Always explain the paper's significance."
    ),
    tools=[get_paper],
    model="gpt-4o-mini",
)

orchestrator = Agent(
    name="Orchestrator Agent",
    instructions=(
        "You are a medical research assistant that helps users with PubMed queries. "
        "When users ask about medical topics or research, use the search_agent to find papers. "
        "When users provide a specific PMID, use the reader_agent to analyze that paper. "
        "Always provide helpful, informative responses based on the tool outputs. "
        "Synthesize the information into clear, actionable insights."
    ),
    handoffs=[search_agent, reader_agent],
    model="gpt-4o-mini",
)


async def orchestrate(input_text: str) -> str:
    return await orchestrator.invoke(input_text)