from .base import BaseWorkflow, WorkflowContext, WorkflowResult


def register_all_workflows(registry):
    """Register all available workflows"""
    from .medical import PubMedResearchWorkflow
    
    # Register medical workflows - this is now the default and only workflow
    registry.register("pubmed_research", PubMedResearchWorkflow())


__all__ = ['BaseWorkflow', 'WorkflowContext', 'WorkflowResult', 'register_all_workflows']