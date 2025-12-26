from langgraph.graph import StateGraph, END
from app.graph.state import My3State
from app.graph.nodes import (
    greeting_node,
    profiling_node,
    recommending_node,
    confirming_node,
    done_node
)


def create_workflow():
    """Create and compile the My3 LangGraph workflow."""
    workflow = StateGraph(My3State)
    
    # Add nodes
    workflow.add_node("greeting", greeting_node)
    workflow.add_node("profiling", profiling_node)
    workflow.add_node("recommending", recommending_node)
    workflow.add_node("confirming", confirming_node)
    workflow.add_node("done", done_node)
    
    # Set entry point
    workflow.set_entry_point("greeting")
    
    # Add edges (simplified for now - will be enhanced with conditional routing)
    workflow.add_edge("greeting", "profiling")
    workflow.add_edge("profiling", "recommending")
    workflow.add_edge("recommending", "confirming")
    workflow.add_edge("confirming", "done")
    workflow.add_edge("done", END)
    
    # Compile graph
    app = workflow.compile()
    return app


# Create workflow instance
workflow_app = create_workflow()

