"""
Agent 11 Models Package
=======================

Public entry point for the Agent 11 domain-model layer.

Think of this file as the ON switch and front door for models.

The models package defines the validated data contracts used by
Agent 11 for:

    - AI requests and responses
    - data classification
    - policy decisions
    - prohibited data
    - reasoning services
    - routing decisions
    - network-path information

This package describes state.

It does NOT:

    - select AI models
    - enforce routing policy
    - invoke foundational models
    - invoke company LLMs
    - manage MCP tools
    - inspect BGP
    - control SD-WAN
    - perform network health checks

Those responsibilities belong to the appropriate Agent 11
orchestrators and service layers.

Architecture rule:

    MODELS describe.
    POLICY permits.
    NETWORK reports reachability.
    ROUTING selects.
    SERVICES execute.
    ORCHESTRATORS coordinate.
"""


# ===========================================================================
# Base Model
# ===========================================================================

# Agent11BaseModel will become the common Pydantic foundation for
# Agent 11 models.
#
# Enable when base_model.py is implemented:
#
# from .base_model import Agent11BaseModel


# ===========================================================================
# AI Domain Models
# ===========================================================================

# These imports form the public interface to the Agent 11 AI model layer.
#
# Enable each model as its corresponding implementation becomes available.
#
# Keeping these imports here allows the rest of Agent 11 to eventually use:
#
#     from agent11.models import AIRequest
#
# instead of depending upon the internal package structure:
#
#     from agent11.models.ai.request import AIRequest
#
# This keeps consumers dependent upon the public model contract rather
# than the physical location of individual model files.

# from .ai import (
#     AIRequest,
#     AIResponse,
#     DataClassification,
#     DataRoutePolicy,
#     PolicyDecision,
#     ProhibitedData,
#     ReasoningProfile,
#     RoutingDecision,
# )


# ===========================================================================
# Public Interface
# ===========================================================================

# __all__ explicitly defines the supported public interface of this package.
#
# Models should be added here only after:
#
#     1. The model has been implemented.
#     2. The model can be imported successfully.
#     3. Basic validation has been tested.
#     4. The model is intended to be part of the public Agent 11 contract.
#
# Internal helper models do not automatically need to be exposed here.

__all__: list[str] = [
    # Base
    # "Agent11BaseModel",

    # Requests / Responses
    # "AIRequest",
    # "AIResponse",

    # Data Policy
    # "DataClassification",
    # "DataRoutePolicy",
    # "PolicyDecision",
    # "ProhibitedData",

    # Reasoning
    # "ReasoningProfile",

    # Routing
    # "RoutingDecision",
]
