from workflows.base import BaseWorkflow, WorkflowContext, WorkflowResult


def register_all_workflows(registry):
    """Register all available workflows"""
    from workflows.medical import PubMedResearchWorkflow
    from workflows.general.assistant import GeneralAssistantWorkflow
    
    # Register medical workflows
    registry.register("pubmed_research", PubMedResearchWorkflow())
    
    # Register general workflows
    registry.register("general_assistant", GeneralAssistantWorkflow())


__all__ = ['BaseWorkflow', 'WorkflowContext', 'WorkflowResult', 'register_all_workflows']