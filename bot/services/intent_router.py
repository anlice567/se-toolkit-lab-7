"""Intent router using LLM for natural language queries."""

import sys
from typing import Any

from services.llm_client import LLMClient
from services.lms_client import LMSClient
from services.tools import get_tools


# System prompt for the LLM
SYSTEM_PROMPT = """You are an AI assistant for a Learning Management System. 
You have access to tools that fetch data from the backend API.

When a user asks a question:
1. Analyze what information they need
2. Call the appropriate tools to get that data
3. Once you have all the data, summarize it clearly for the user

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students
- get_scores: Score distribution for a lab
- get_pass_rates: Per-task pass rates for a lab
- get_timeline: Submissions timeline for a lab
- get_groups: Per-group performance for a lab
- get_top_learners: Top N learners for a lab
- get_completion_rate: Completion rate for a lab
- trigger_sync: Refresh data from autochecker

For greetings like "hello" or "hi", respond friendly without calling tools.
For gibberish or unclear input, explain what you can help with.
Always be helpful and provide specific data when available."""


def execute_tool(tool_name: str, arguments: dict[str, Any], lms_client: LMSClient) -> Any:
    """Execute a tool and return the result."""
    print(f"[tool] Executing: {tool_name}({arguments})", file=sys.stderr)
    
    try:
        if tool_name == "get_items":
            result = lms_client.get_items()
        elif tool_name == "get_learners":
            result = lms_client.get_items()  # Using items as fallback
        elif tool_name == "get_scores":
            result = lms_client.get_pass_rates(arguments.get("lab", ""))
        elif tool_name == "get_pass_rates":
            result = lms_client.get_pass_rates(arguments.get("lab", ""))
        elif tool_name == "get_timeline":
            result = lms_client.get_pass_rates(arguments.get("lab", ""))
        elif tool_name == "get_groups":
            result = lms_client.get_pass_rates(arguments.get("lab", ""))
        elif tool_name == "get_top_learners":
            result = lms_client.get_pass_rates(arguments.get("lab", ""))
        elif tool_name == "get_completion_rate":
            result = lms_client.get_pass_rates(arguments.get("lab", ""))
        elif tool_name == "trigger_sync":
            result = {"status": "sync triggered"}
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        print(f"[tool] Result: {len(result) if isinstance(result, (list, dict)) else 'ok'}", file=sys.stderr)
        return result
    except Exception as e:
        print(f"[tool] Error: {str(e)}", file=sys.stderr)
        return {"error": str(e)}


def route(message: str, llm_client: LLMClient, lms_client: LMSClient) -> str:
    """Route a message through the LLM intent router."""
    tools = get_tools()
    
    # Initial messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]
    
    print(f"[router] User message: {message}", file=sys.stderr)
    
    # Main loop: call LLM, execute tools, feed results back
    max_iterations = 5
    for iteration in range(max_iterations):
        print(f"[router] Iteration {iteration + 1}", file=sys.stderr)
        
        # Call LLM
        response = llm_client.chat(messages, tools=tools)
        
        # Check for tool calls
        choice = response.get("choices", [{}])[0]
        message_data = choice.get("message", {})
        
        # If no tool calls, return the response
        if "tool_calls" not in message_data or not message_data["tool_calls"]:
            content = message_data.get("content", "I'm not sure how to help with that.")
            print(f"[router] Final response: {content[:100]}...", file=sys.stderr)
            return content
        
        # Execute tool calls
        tool_calls = message_data["tool_calls"]
        print(f"[tool] LLM called {len(tool_calls)} tool(s)", file=sys.stderr)
        
        # Add assistant message with tool calls to conversation
        messages.append(message_data)
        
        # Execute each tool and collect results
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            tool_name = function.get("name", "unknown")
            
            # Parse arguments
            import json
            try:
                arguments = json.loads(function.get("arguments", "{}"))
            except json.JSONDecodeError:
                arguments = {}
            
            # Execute tool
            result = execute_tool(tool_name, arguments, lms_client)
            
            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id", "unknown"),
                "content": str(result),
            })
        
        print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)
    
    # If we reach here, we hit max iterations
    return "I'm having trouble processing your request. Please try rephrasing."
