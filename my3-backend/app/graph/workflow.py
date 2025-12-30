from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.graph.state import AgentState
from app.graph.nodes import (
    router_node,
    extract_person_node,
    check_recipient_node,
    process_relationships_node,
    generate_gifts_node,
    compose_response_node,
    execute_actions_node
)


def create_my3_workflow():
    """Create and compile the My3 LangGraph workflow with conditional routing."""
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("router", router_node)
    workflow.add_node("extract_person", extract_person_node)
    workflow.add_node("check_recipient", check_recipient_node)
    workflow.add_node("process_relationships", process_relationships_node)
    workflow.add_node("generate_gifts", generate_gifts_node)
    workflow.add_node("compose_response", compose_response_node)
    workflow.add_node("execute_actions", execute_actions_node)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Define conditional routing functions
    def route_after_router(state: AgentState) -> str:
        """Route after router node based on intent."""
        intent = state.get("current_intent")
        if intent in ["gift_search", "add_recipient", "update_info"]:
            return "extract_person"
        else:
            return "compose_response"
    
    def route_after_check(state: AgentState) -> str:
        """Route after check_recipient node based on intent."""
        intent = state.get("current_intent")
        if intent == "gift_search":
            return "generate_gifts"
        else:
            return "compose_response"
    
    def route_after_compose(state: AgentState) -> str:
        """Route after compose_response node based on state."""
        if state.get("requires_confirmation"):
            return END  # Wait for user confirmation
        elif state.get("pending_actions"):
            return "execute_actions"
        else:
            return END
    
    # Add edges with conditional routing
    workflow.add_conditional_edges("router", route_after_router)
    workflow.add_edge("extract_person", "check_recipient")
    workflow.add_edge("check_recipient", "process_relationships")
    workflow.add_conditional_edges("process_relationships", route_after_check)
    workflow.add_edge("generate_gifts", "compose_response")
    workflow.add_conditional_edges("compose_response", route_after_compose)
    workflow.add_edge("execute_actions", END)
    
    # Add memory for conversation persistence
    memory = MemorySaver()
    
    # Compile graph with checkpointer
    return workflow.compile(checkpointer=memory)


# Export compiled graph
my3_graph = create_my3_workflow()
