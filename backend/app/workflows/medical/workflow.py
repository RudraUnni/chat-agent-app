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

        # Get conversation history from input_data
        conversation_history = input_data.get("conversation_history", [])

        try:
            logger.debug(f"Orchestrating input: {user_input[:100]}...")
            logger.debug(f"Conversation history length: {len(conversation_history)}")
            
            # Pass both current message and conversation history to orchestrator
            output = await orchestrate(user_input, conversation_history)
            logger.debug(f"Orchestration complete, output length: {len(output)}")
            return WorkflowResult(success=True, data={"output": output})
        except Exception as exc:
            logger.error(f"Workflow execution failed: {exc}", exc_info=True)
            return WorkflowResult(success=False, error=str(exc))