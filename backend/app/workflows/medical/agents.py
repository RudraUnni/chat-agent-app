from .runtime import Agent
from .tools import search_pubmed, get_paper


search_agent = Agent(
    name="Search Agent",
    instructions=(
        "You are a specialized PubMed search agent. Provide detailed summaries including PMID, title, authors, journal, and date."
    ),
    tools=[search_pubmed],
    model="gpt-4o-mini",
)

reader_agent = Agent(
    name="Reader Agent",
    instructions=(
        "You analyze papers from PubMed by PMID and provide comprehensive summaries including methodology, key findings, and conclusions."
    ),
    tools=[get_paper],
    model="gpt-4o-mini",
)

orchestrator = Agent(
    name="Orchestrator Agent",
    instructions=(
        "Route topic queries to search and PMID-specific queries to reader; synthesize clear, actionable outputs."
    ),
    tools=[
        search_agent.as_tool("search_pubmed", "Search PubMed for papers on a topic"),
        reader_agent.as_tool("analyze_paper", "Analyze a specific paper by PMID"),
    ],
    model="gpt-4o-mini",
)


async def orchestrate(input_text: str) -> str:
    return await orchestrator.invoke(input_text)