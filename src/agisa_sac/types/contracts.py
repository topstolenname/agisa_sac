"""
Core Types and Contracts for AGISA-SAC

This module defines the core data structures and contracts for the distributed agent system,
including tools, messages, loop results, and guardrail structures.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class ToolType(Enum):
    """Classification of tool types for agent capabilities"""

    DATA = "data"  # Read-only data retrieval tools
    ACTION = "action"  # State-changing action tools
    ORCHESTRATION = "orchestration"  # Agent coordination tools


class LoopExit(Enum):
    """Exit conditions for agent execution loop"""

    SATISFIED = "satisfied"  # Task completed successfully
    HANDOFF = "handoff"  # Handed off to another agent
    ERROR = "error"  # Error occurred during execution
    MAX_ITERS = "max_iters"  # Maximum iterations reached
    GUARDRAIL_BLOCK = "guardrail_block"  # Blocked by guardrails


class MessageType(Enum):
    """Types of messages in the distributed system"""

    INTENTION = "Intention"  # Agent intention broadcast
    HANDOFF_OFFER = "HandoffOffer"  # Offer to handoff task
    HANDOFF_CLAIM = "HandoffClaim"  # Claim of handoff offer
    TOOL_INVOCATION = "ToolInvocation"  # Tool execution record
    TOPOLOGY_ALERT = "TopologyAlert"  # Topology change notification


@dataclass
class Tool:
    """
    Agent tool definition with MCP (Model Context Protocol) compatibility.

    Attributes:
        name: Unique tool identifier
        type: Tool classification (DATA, ACTION, ORCHESTRATION)
        function: Callable implementation
        description: Human-readable tool description
        risk_level: Risk classification (low, medium, high)
        parameters: Parameter specifications for MCP format
    """

    name: str
    type: ToolType
    function: Callable[..., Any]
    description: str
    risk_level: str  # "low", "medium", "high"
    parameters: Dict[str, Any]

    def _py_to_json_type(self, py_type: Any) -> str:
        """Map Python types to JSON Schema types"""
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }
        if isinstance(py_type, str):
            return py_type
        return type_map.get(py_type, "string")

    def to_mcp_format(self) -> Dict[str, Any]:
        """
        Convert to valid MCP/JSON Schema tool definition.

        Returns:
            MCP-compliant tool definition with inputSchema
        """
        properties = {}
        required = []

        for param_name, param_spec in self.parameters.items():
            if isinstance(param_spec, dict):
                properties[param_name] = param_spec
                if param_spec.get("required", False):
                    required.append(param_name)
            else:
                properties[param_name] = {"type": self._py_to_json_type(param_spec)}
                if param_spec is not None:
                    required.append(param_name)

        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "additionalProperties": False,
                "properties": properties,
                "required": required,
            },
        }


@dataclass
class GuardrailResult:
    """
    Result of guardrail evaluation.

    Attributes:
        passed: Whether the guardrail check passed
        reason: Human-readable reason for failure
        risk_level: Risk classification of the violation
        violations: List of specific violations detected
        metadata: Additional context about the evaluation
    """

    passed: bool
    reason: Optional[str] = None
    risk_level: str = "low"
    violations: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class LoopResult:
    """
    Result of an agent execution loop.

    Attributes:
        exit: How the loop terminated
        payload: Result data
        iterations: Number of iterations executed
        total_tokens: Total tokens consumed
        tool_calls: Number of tool invocations
        errors: List of errors encountered
    """

    exit: LoopExit
    payload: Dict[str, Any]
    iterations: int
    total_tokens: int = 0
    tool_calls: int = 0
    errors: List[str] = field(default_factory=list)


@dataclass
class IntentionMessage:
    """
    Message broadcast to workspace about agent intentions.

    Attributes:
        msg_type: Message type identifier
        run_id: Unique run identifier
        source_agent: Agent that generated the message
        timestamp: ISO 8601 timestamp
        attention_weight: Importance weight (0.0-1.0)
        payload: Message content
    """

    msg_type: str = "Intention"
    run_id: str = ""
    source_agent: str = ""
    timestamp: str = ""
    attention_weight: float = 0.0
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_pubsub(self) -> bytes:
        """Serialize to Pub/Sub message format"""
        return json.dumps(self.__dict__).encode("utf-8")


@dataclass
class HandoffOffer:
    """
    Offer to hand off a task to another agent.

    Attributes:
        msg_type: Message type identifier
        run_id: Unique run identifier
        from_agent: Agent making the offer
        to_capabilities: Required capabilities for claiming
        task_signature: Task metadata and signature
        context_ref: GCS URI to context data
        expires_at: ISO 8601 expiration timestamp
    """

    msg_type: str = "HandoffOffer"
    run_id: str = ""
    from_agent: str = ""
    to_capabilities: List[str] = field(default_factory=list)
    task_signature: Dict[str, Any] = field(default_factory=dict)
    context_ref: str = ""  # GCS URI
    expires_at: str = ""

    def to_pubsub(self) -> bytes:
        """Serialize to Pub/Sub message format"""
        return json.dumps(self.__dict__).encode("utf-8")


@dataclass
class HandoffClaim:
    """
    Claim of a handoff offer by an agent.

    Attributes:
        msg_type: Message type identifier
        run_id: Unique run identifier
        claimant_agent: Agent claiming the offer
        claim_reason: Reason for claiming
        accepted: Whether the claim was accepted
    """

    msg_type: str = "HandoffClaim"
    run_id: str = ""
    claimant_agent: str = ""
    claim_reason: str = ""
    accepted: bool = False

    def to_pubsub(self) -> bytes:
        """Serialize to Pub/Sub message format"""
        return json.dumps(self.__dict__).encode("utf-8")


@dataclass
class ToolInvocation:
    """
    Record of a tool execution for auditing.

    Attributes:
        msg_type: Message type identifier
        run_id: Unique run identifier
        agent_id: Agent that invoked the tool
        tool: Tool name
        args: Tool arguments
        risk_level: Risk classification
    """

    msg_type: str = "ToolInvocation"
    run_id: str = ""
    agent_id: str = ""
    tool: str = ""
    args: Dict[str, Any] = field(default_factory=dict)
    risk_level: str = "low"

    def to_pubsub(self) -> bytes:
        """Serialize to Pub/Sub message format"""
        return json.dumps(self.__dict__).encode("utf-8")
