from typing import Any, Dict, Optional
from app.workflows.base import BaseWorkflow, WorkflowContext, WorkflowResult
from .agents import orchestrate


class PubMedResearchWorkflow(BaseWorkflow):
    """Workflow wrapper that delegates to the multi-agent PubMed orchestrator."""

    def __init__(self) -> None:
        super().__init__(
            name="PubMed Research Assistant",
            description="Multi-agent PubMed search and analysis workflow",
        )

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[WorkflowContext] = None,
    ) -> WorkflowResult:
        print(f"PubMedResearchWorkflow.execute called with input_data: {input_data}")
        user_input = input_data.get("query") or input_data.get("text") or input_data.get("message") or ""
        print(f"Extracted user_input: '{user_input}'")
        if not user_input:
            return WorkflowResult(success=False, error="Missing 'query', 'text', or 'message'")

        try:
            print(f"Calling orchestrate with: '{user_input}'")
            output = await orchestrate(user_input)
            print(f"Orchestrate returned: {output}")
            return WorkflowResult(success=True, data={"output": output})
        except Exception as exc:
            print(f"Error in workflow execution: {exc}")
            import traceback
            traceback.print_exc()
            return WorkflowResult(success=False, error=str(exc))