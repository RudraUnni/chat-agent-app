import re
from typing import Any, Awaitable, Callable, Dict, Optional


class RunnerResult:
    def __init__(self, final_output: str):
        self.final_output = final_output


def function_tool(func: Callable[..., str]) -> Callable[..., str]:
    func._is_tool = True  # type: ignore[attr-defined]
    return func


class Agent:
    def __init__(
        self,
        name: str,
        instructions: str,
        tools: Optional[list] = None,
        model: Optional[str] = None,
    ) -> None:
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model = model

    async def invoke(self, user_input: str, **kwargs: Any) -> str:
        # Default behavior: if a single tool is provided, try to call it with the raw input
        if not self.tools:
            return user_input

        # Heuristic routing for two known tools: search_pubmed(query) and get_paper(pmid)
        tool_names = {getattr(t, "__name__", str(i)): t for i, t in enumerate(self.tools)}

        if "get_paper" in tool_names:
            pmid = _extract_pmid(user_input) or kwargs.get("pmid")
            if pmid:
                return tool_names["get_paper"](pmid=str(pmid))

        if "search_pubmed" in tool_names:
            query = (user_input or "").strip()
            if query:
                return tool_names["search_pubmed"](query=query)

        # Fallback: call the first tool with raw input as query
        tool = self.tools[0]
        try:
            return tool(user_input)  # type: ignore[misc]
        except Exception:
            return str(user_input)

    def as_tool(self, name: str, description: str) -> Callable[[str], str]:
        def _tool(user_input: str) -> str:
            # Simple sync wrapper around invoke for tooling composition
            import asyncio
            try:
                # Try to get the current event loop
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, create a new one
                return asyncio.run(self.invoke(user_input))
            else:
                # There is a running loop, we need to run in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.invoke(user_input))
                    return future.result()
        _tool.__name__ = name  # type: ignore[attr-defined]
        _tool.__doc__ = description
        return _tool


class Runner:
    @staticmethod
    async def run(agent: Agent, user_input: str) -> RunnerResult:
        output = await agent.invoke(user_input)
        return RunnerResult(final_output=output)


def _extract_pmid(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    # Match patterns like: PMID 12345678 or pmid:12345678 or just digits of length 7-9
    m = re.search(r"(?i)pmid[:\s]*([0-9]{4,12})", text)
    if m:
        return m.group(1)
    m = re.search(r"\b([0-9]{7,12})\b", text)
    if m:
        return m.group(1)
    return None