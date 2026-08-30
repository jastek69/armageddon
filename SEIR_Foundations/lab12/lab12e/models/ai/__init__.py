"""
Agent 11 AI Models Package
==========================

Public entry point for Agent 11 AI domain models.

Think of this file as the ON switch and front door for the AI model layer.

This package will define the validated data contracts used to describe:

    - AI requests
    - AI responses
    - reasoning requirements
    - AI capabilities
    - reasoning services
    - routing information
    - policy information
    - data classification
    - prohibited data

These models describe AI-related state.

They do NOT:

    - invoke AI models
    - select reasoning routes
    - enforce policy
    - perform network checks
    - invoke MCP tools
    - orchestrate agents

Architecture rule:

    MODELS describe.
    PYDANTIC validates.
    POLICY permits.
    NETWORK reports reachability.
    ROUTING selects.
    SERVICES execute.
    ORCHESTRATORS coordinate.
"""


# ===========================================================================
# AI Domain Models
# ===========================================================================

# Enable these imports incrementally as each model is implemented,
# tested, and ready to become part of the public Agent 11 contract.
#
# Planned models:
#
#     AIRequest
#     AIResponse
#     AICapability
#     AIModel
#     AIService
#     ReasoningProfile
#     RoutingDecision
#     DataClassification
#     DataRoutePolicy
#     PolicyDecision
#     ProhibitedData
#
#
# Example future imports:
#
#     from .request import AIRequest
#     from .response import AIResponse
#
#
# Do not enable an import merely because the corresponding file exists.
#
# A model should first be:
#
#     implemented
#         ↓
#     validated
#         ↓
#     tested
#         ↓
#     intentionally exposed
#
# before becoming part of the public package interface.


# ===========================================================================
# Public Interface
# ===========================================================================

# __all__ defines the supported public interface of the AI model package.
#
# Add models here only after:
#
#     1. The model has been implemented.
#     2. The model imports successfully.
#     3. Pydantic validation has been tested.
#     4. The model is intended to be part of the public AI contract.
#
# Internal helper models do not automatically need to be exposed here.
#
# For now, the package is intentionally empty.
#
# The ON switch exists.
#
# We simply have not connected any validated AI domain models to it yet.

__all__: list[str] = []


# ===========================================================================
# Chewbacca's Package Commentary
# ===========================================================================

# Chewbacca:
#
#     "I pressed the ON switch."
#
#
# Agent 11:
#
#     Correct.
#
#
# Chewbacca:
#
#     "Nothing happened."
#
#
# Agent 11:
#
#     Correct.
#
#
# Chewbacca:
#
#     "Then why do we have an ON switch?"
#
#
# Agent 11:
#
#     Because the package now has a stable public entry point.
#
#     As AI domain models are implemented and tested, they will be
#     exposed through this interface.
#
#
# Chewbacca:
#
#     "So the switch works?"
#
#
# Agent 11:
#
#     Yes.
#
#
# Chewbacca:
#
#     "But nothing is connected to it?"
#
#
# Agent 11:
#
#     Correct.
#
#
# Chewbacca:
#
#     "This architecture lacks street access."
#
#
# Agent 11:
#
#     That is not an AI domain-model concern.
#
#
# Final architecture rule:
#
#
#     __init__.py OPENS THE DOOR.
#
#     IT DOES NOT BUILD THE HOUSE.
