import logging
from typing import Any, Dict, Optional
from app.workflows.base import BaseWorkflow, WorkflowContext, WorkflowResult
from .agents import orchestrate

logger = logging.getLogger(__name__)


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
        user_input = input_data.get("query") or input_data.get("text") or input_data.get("message") or ""
        if not user_input:
            return WorkflowResult(success=False, error="Missing 'query', 'text', or 'message'")

        try:
            logger.debug(f"Orchestrating input: {user_input[:100]}...")
            output = await orchestrate(user_input)
            logger.debug(f"Orchestration complete, output length: {len(output)}")
            return WorkflowResult(success=True, data={"output": output})
        except Exception as exc:
            logger.error(f"Workflow execution failed: {exc}", exc_info=True)
            return WorkflowResult(success=False, error=str(exc))