"""
Agent 11 Enum Package
=====================

Public entry point for the Agent 11 controlled-vocabulary layer.

Think of this file as the ON switch and front door for Agent 11 Enums.

The enums package will define the controlled vocabulary used throughout
Agent 11 for:

    - AI reasoning
    - routing
    - policy
    - reasoning services
    - network paths

Enums define allowed vocabulary.

They do NOT:

    - make policy decisions
    - select AI routes
    - determine service availability
    - determine network reachability
    - invoke AI services
    - invoke MCP tools
    - perform orchestration

Architecture rule:

    ENUMS define vocabulary.
    MODELS describe state.
    PYDANTIC validates.
    POLICY permits.
    NETWORK reports reachability.
    ROUTING selects.
    SERVICES execute.
    ORCHESTRATORS coordinate.
"""


# ===========================================================================
# Base Enum
# ===========================================================================

# Agent11Enum will become the common foundation for Agent 11 controlled
# vocabulary.
#
# Enable when base_enum.py is implemented:
#
# from .base_enum import Agent11Enum


# ===========================================================================
# Domain Enums
# ===========================================================================

# Domain-specific Enums will be enabled as their corresponding files
# are implemented and tested.
#
# Planned modules:
#
#     ai_enums.py
#     routing_enums.py
#     policy_enums.py
#     model_enums.py
#     network_enums.py
#
# Eventually this package will allow clean imports such as:
#
#     from agent11.models.enums import (
#         AIRoute,
#         NetworkPathType,
#         PathStatus,
#         ReasoningLevel,
#         RoutingStatus,
#         ServiceStatus,
#     )
#
# rather than requiring the rest of Agent 11 to know the physical
# location of every Enum definition.


# ===========================================================================
# Public Interface
# ===========================================================================

# __all__ defines the supported public vocabulary exposed by this package.
#
# Add an Enum only after:
#
#     1. The Enum has been implemented.
#     2. The Enum imports successfully.
#     3. Its values have been reviewed.
#     4. It is intended to be part of the Agent 11 public vocabulary.

__all__: list[str] = [
    # "Agent11Enum",
]
