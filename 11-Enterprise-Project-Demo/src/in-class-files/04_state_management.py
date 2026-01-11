"""
 State Management in LangGraph

This example demonstrates:
- Immutable state updates
- Partial state returns
- State merging
- Error handling in state

"""

from typing import Dict, Any, TypedDict


# ============================================================================
# STEP 1: Understanding State Updates
# ============================================================================

class WorkflowState(TypedDict):
    """Workflow state."""
    data: str
    processed: bool
    errors: list


def demonstrate_wrong_way():
    """Show the WRONG way to update state."""
    print("=" * 70)
    print("State Management - WRONG Way")
    print("=" * 70)
    
    state = {"data": "test", "processed": False, "errors": []}
    print("\n❌ WRONG: Mutating state directly")
    print("   state['processed'] = True  # This will cause errors!")
    print("   return state  # LangGraph will reject this")
    
    print("\n   Why it's wrong:")
    print("   - LangGraph expects immutable updates")
    print("   - Direct mutation breaks parallel execution")
    print("   - Can't track what changed")
    print("   - Causes InvalidUpdateError")


def demonstrate_right_way():
    """Show the RIGHT way to update state."""
    print("\n" + "=" * 70)
    print("State Management - RIGHT Way")
    print("=" * 70)
    
    state: WorkflowState = {
        "data": "test",
        "processed": False,
        "errors": []
    }
    
    print("\n✅ RIGHT: Return only what changed")
    print("   return {'processed': True} # This is a valid update")
    print("   LangGraph merges: {**state, **returned} # This is a valid merge")
    
    # Simulate what LangGraph does
    update = {"processed": True}
    new_state = {**state, **update}
    
    print(f"\n   Old state: {state}")
    print(f"   Update:    {update}")
    print(f"   New state: {new_state}")
    
    print("\n   Why it's right:")
    print("   - Immutable (doesn't change original)")
    print("   - Clear what changed")
    print("   - Works with parallel execution")
    print("   - LangGraph can track changes")


# ============================================================================
# STEP 2: Node Examples
# ============================================================================

def correct_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Correct node implementation.
    
    Notice:
    - Reads from state
    - Returns only what changed
    - Doesn't mutate state
    """
    data = state["data"]
    processed_data = f"PROCESSED: {data}"
    
    # Return only what changed
    return {"data": processed_data, "processed": True}


def node_with_error(state: WorkflowState) -> Dict[str, Any]:
    """
    Node that handles errors correctly.
    
    Notice:
    - Errors are added to errors list
    - We create a new list (immutable)
    - Return error in state, don't raise exception
    """
    try:
        # Some processing that might fail
        result = "success"
        return {"data": result}
    except Exception as e:
        # Add error to state, don't crash
        current_errors = state.get("errors", [])
        return {"errors": current_errors + [f"Error: {str(e)}"]}


# ============================================================================
# STEP 3: State Merging Demonstration
# ============================================================================

def demonstrate_merging():
    """Show how state merging works."""
    print("\n" + "=" * 70)
    print("State Merging Demonstration")
    print("=" * 70)
    
    # Initial state
    state: WorkflowState = {
        "data": "initial",
        "processed": False,
        "errors": []
    }
    
    print(f"\n📊 Initial State: {state}")
    
    # Node 1 returns update
    update1 = {"data": "updated by node1"}
    state = {**state, **update1}
    print(f"   After node1: {state}")
    
    # Node 2 returns update
    update2 = {"processed": True}
    state = {**state, **update2}
    print(f"   After node2: {state}")
    
    # Node 3 adds to list (immutable)
    update3 = {"errors": state["errors"] + ["warning"]}
    state = {**state, **update3}
    print(f"   After node3: {state}")
    
    print("\n💡 Key Points:")
    print("   1. Each node returns partial update")
    print("   2. LangGraph merges: {**old, **new}")
    print("   3. Lists need new list: old + [item]")
    print("   4. Original state never changes (immutable)")


# ============================================================================
# STEP 4: Common Patterns
# ============================================================================

def demonstrate_patterns():
    """Show common state update patterns."""
    print("\n" + "=" * 70)
    print("Common State Update Patterns")
    print("=" * 70)
    
    state: WorkflowState = {
        "data": "test",
        "processed": False,
        "errors": []
    }
    
    print("\n📋 Pattern 1: Simple Update")
    print("   return {'processed': True}")
    
    print("\n📋 Pattern 2: Update Based on Existing")
    print("   return {'data': state['data'] + ' enhanced'}")
    
    print("\n📋 Pattern 3: Add to List")
    print("   return {'errors': state.get('errors', []) + [new_error]}")
    
    print("\n📋 Pattern 4: Conditional Update")
    print("   if condition:")
    print("       return {'processed': True}")
    print("   return {}  # No update")
    
    print("\n📋 Pattern 5: Error Handling")
    print("   try:")
    print("       result = process()")
    print("       return {'data': result}")
    print("   except Exception as e:")
    print("       return {'errors': state['errors'] + [str(e)]}")


if __name__ == "__main__":
    demonstrate_wrong_way()
    demonstrate_right_way()
    demonstrate_merging()
    demonstrate_patterns()
    
    print("\n" + "=" * 70)
    print("Key Takeaway: Always return partial updates, never mutate state!")
    print("=" * 70)


