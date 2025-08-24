from typing import Dict, Optional, List

from app.workflows.base import BaseWorkflow


class WorkflowRegistry:
    """Registry for managing available workflows"""
    
    def __init__(self):
        self._workflows: Dict[str, BaseWorkflow] = {}
    
    def register(self, name: str, workflow: BaseWorkflow):
        """Register a new workflow"""
        if name in self._workflows:
            raise ValueError(f"Workflow '{name}' already registered")
        self._workflows[name] = workflow
    
    def get_workflow(self, name: str) -> Optional[BaseWorkflow]:
        """Get a workflow by name"""
        return self._workflows.get(name)
    
    def list_workflows(self) -> List[Dict[str, str]]:
        """List all available workflows"""
        return [
            {
                'name': name,
                'description': workflow.description
            }
            for name, workflow in self._workflows.items()
        ]
    
    def workflow_exists(self, name: str) -> bool:
        """Check if a workflow exists"""
        return name in self._workflows