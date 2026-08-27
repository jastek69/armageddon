"""
Agent 11 AI Enums
=================

Defines the controlled vocabulary used to describe AI reasoning
requirements and AI request/response lifecycle state.

This module answers three fundamental questions:

    ReasoningLevel
        "What level of reasoning does the request require?"

    AIRequestStatus
        "What is happening to the AI request?"

    AIResponseStatus
        "What happened during the AI invocation?"

These are intentionally separate concepts.

AI Enums do NOT:

    - select a model
    - select a provider
    - authorize data movement
    - determine data classification
    - determine network reachability
    - determine service health
    - invoke AI models
    - invoke MCP tools
    - perform orchestration

Architecture rule:

    REQUIREMENT != ROUTE

    VALIDATED != AUTHORIZED

    COMPLETED != AI MODEL INVOKED

    FAILED REQUEST != NO VIABLE ROUTE

    NO RESPONSE != FAILED RESPONSE
"""

from .base_enum import Agent11Enum


# ===========================================================================
# Reasoning Level
# ===========================================================================


class ReasoningLevel(Agent11Enum):
    """
    Describes the general level of AI reasoning requested.

    ReasoningLevel describes the WORK.

    It does not determine the infrastructure that performs the work.

    LIGHT
        Lightweight reasoning suitable for relatively simple analysis,
        classification, transformation, or other low-complexity tasks.

    STANDARD
        Normal reasoning requirements for typical Agent 11 workloads.

    HEAVY
        More demanding reasoning requiring greater reasoning capability,
        context, computation, or other resources.

    Example:

        reasoning_level = ReasoningLevel.HEAVY

    This means:

        "The request requires heavy reasoning."

    It does NOT mean:

        "Use the company on-premises LLM."

    It does NOT mean:

        "Use an external foundational model."

    It does NOT mean:

        "Use the largest model available."

    The actual reasoning destination will eventually depend upon
    additional architectural state, including:

        - data classification
        - organization policy
        - user policy
        - required capabilities
        - service capability
        - service availability
        - network-path availability
        - routing policy

    Conceptually:

        Reasoning Requirement
                |
                v
        Capability Evaluation
                |
                v
          Policy Evaluation
                |
                v
          Service Health
                |
                v
          Network State
                |
                v
             Routing

    Therefore:

        REASONING LEVEL != ROUTING DECISION
    """

    LIGHT = "light"
    STANDARD = "standard"
    HEAVY = "heavy"


# ===========================================================================
# AI Request Status
# ===========================================================================


class AIRequestStatus(Agent11Enum):
    """
    Describes the lifecycle state of an AI reasoning request.

    This Enum answers:

        "What is happening to the request?"

    It does not describe:

        - policy outcome
        - routing outcome
        - model selection
        - AI response outcome
        - service health
        - network availability

    A typical lifecycle may resemble:

        CREATED
            |
            v
        VALIDATED
            |
            v
        PROCESSING
            |
            +----------> FAILED
            |
            +----------> CANCELLED
            |
            v
        COMPLETED

    Not every future workflow is required to traverse every state.
    The Enum establishes the recognized lifecycle vocabulary.
    """

    CREATED = "created"
    VALIDATED = "validated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ===========================================================================
# AI Response Status
# ===========================================================================


class AIResponseStatus(Agent11Enum):
    """
    Describes the outcome of an actual AI reasoning invocation.

    This Enum answers:

        "What happened during the AI invocation?"

    SUCCESS
        The reasoning service successfully produced the expected
        response.

    PARTIAL
        The reasoning service produced usable output, but the result
        did not completely satisfy the expected response contract.

    FAILED
        The AI invocation occurred but failed to produce the required
        usable response.

    AIResponseStatus is intentionally separate from AIRequestStatus.

    For example:

        AIRequestStatus.PROCESSING
                |
                v
        RoutingStatus.SELECTED
                |
                v
          AI Invocation
                |
                v
        AIResponseStatus.SUCCESS
                |
                v
        AIRequestStatus.COMPLETED

    The request lifecycle and response outcome describe different
    architectural facts.
    """

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


# ===========================================================================
# Architecture Commentary
# ===========================================================================

# ---------------------------------------------------------------------------
# VALIDATED does not mean AUTHORIZED
# ---------------------------------------------------------------------------
#
# A request may be structurally valid:
#
#     request_status = AIRequestStatus.VALIDATED
#
# while policy still prohibits the requested operation.
#
# Example:
#
#     Request structure:
#         VALID
#
#     Data classification:
#         E8
#
#     Requested destination:
#         External FM
#
#     Policy:
#         DENIED
#
# Nothing was necessarily wrong with the structure of the request.
#
# Policy simply determined that the requested data movement was not
# permitted.
#
# Therefore:
#
#     VALIDATED != AUTHORIZED
#
# Validation and authorization must remain separate architectural
# responsibilities.


# ---------------------------------------------------------------------------
# COMPLETED does not mean an AI model was invoked
# ---------------------------------------------------------------------------
#
# A request can complete its Agent 11 processing lifecycle without
# requiring AI inference.
#
# For example:
#
#     AIRequestStatus.PROCESSING
#             |
#             v
#     RoutingStatus.NULL
#             |
#             v
#       No AI Invocation
#             |
#             v
#     AIRequestStatus.COMPLETED
#
# Agent 11 successfully examined the request and determined that no
# AI reasoning was required.
#
# Therefore:
#
#     COMPLETED != AI MODEL INVOKED
#
# This distinction becomes important for:
#
#     - cost control
#     - deterministic processing
#     - policy enforcement
#     - unnecessary inference prevention
#     - telemetry
#     - auditability


# ---------------------------------------------------------------------------
# FAILED does not mean NO_VIABLE_ROUTE
# ---------------------------------------------------------------------------
#
# AIRequestStatus.FAILED should describe a failure in request processing.
#
# Examples may eventually include:
#
#     - invalid internal state
#     - unexpected processing exception
#     - required dependency failure
#     - orchestration failure
#
# RoutingStatus.NO_VIABLE_ROUTE is conceptually different.
#
# Agent 11 may successfully determine:
#
#     1. The request is valid.
#     2. The request has been evaluated.
#     3. Policy restrictions have been applied.
#     4. Service capability has been evaluated.
#     5. Service health has been evaluated.
#     6. Network reachability has been evaluated.
#     7. No compliant viable destination remains.
#
# That is not necessarily a system failure.
#
# Agent 11 may have worked exactly as designed.
#
# Therefore:
#
#     FAILED REQUEST != NO VIABLE ROUTE


# ---------------------------------------------------------------------------
# Why AIResponseStatus does not contain NULL
# ---------------------------------------------------------------------------
#
# Agent 11 intentionally does NOT define:
#
#     AIResponseStatus.NULL
#
# RoutingStatus.NULL has a different meaning:
#
#     Agent 11 evaluated the request and intentionally determined that
#     no AI invocation and no downstream AI response are required.
#
# Conceptually:
#
#     RoutingStatus.NULL
#             |
#             v
#       AI Invocation
#           NONE
#             |
#             v
#        AIResponse
#           None
#
# There is no AIResponseStatus because there is no AIResponse object.
#
# This is different from:
#
#     AIResponseStatus.FAILED
#
# A FAILED response means an AI invocation occurred and the resulting
# response did not satisfy the required outcome.
#
# Therefore:
#
#     NO RESPONSE != FAILED RESPONSE


# ---------------------------------------------------------------------------
# Why AI Capability is not defined here yet
# ---------------------------------------------------------------------------
#
# Agent 11 will eventually need to describe capabilities such as:
#
#     - text reasoning
#     - code reasoning
#     - structured output
#     - tool use
#     - MCP support
#     - multimodal reasoning
#     - long-context reasoning
#
# Capability requirements may eventually become combinations of Enums
# and Pydantic models.
#
# Those contracts should be designed alongside:
#
#     models/ai/capability.py
#
# rather than prematurely freezing the capability architecture here.
#
# The current AI Enum layer therefore remains intentionally small.


# ===========================================================================
# Chewbacca's Architecture Commentary
# ===========================================================================

# Chewbacca has reviewed ReasoningLevel and submitted the following
# architectural enhancement:
#
#
#     class ReasoningLevel(Agent11Enum):
#         LIGHT = "light"
#         STANDARD = "standard"
#         HEAVY = "heavy"
#         CHEWBACCA = "chewbacca"
#
#
# His justification:
#
#     "HEAVY is insufficient to represent my intellectual workload."
#
#
# The Architecture Review Board rejected the proposal.
#
# ReasoningLevel describes the requirements of a REQUEST.
#
# It does not describe Chewbacca's opinion of himself.
#
#
# Chewbacca then submitted:
#
#
#     reasoning_level = ReasoningLevel.HEAVY
#
#
# and instructed Agent 11:
#
#     "Use the largest and most expensive foundational model."
#
#
# Agent 11 rejected this interpretation.
#
# HEAVY establishes a reasoning requirement.
#
# It does not establish:
#
#     - authorization
#     - provider selection
#     - model selection
#     - network-path selection
#     - budget approval
#
#
# Agent 11 must still determine:
#
#
#     POLICY PERMITTED
#             +
#     SERVICE CAPABLE
#             +
#     SERVICE AVAILABLE
#             +
#     PATH AVAILABLE
#             =
#         VIABLE ROUTE
#
#
# Chewbacca then submitted another request:
#
#
#     "Determine whether Chewbacca is an integer."
#
#
# Request lifecycle:
#
#
#     CREATED
#        |
#        v
#     VALIDATED
#        |
#        v
#     PROCESSING
#
#
# Routing evaluation:
#
#
#     RoutingStatus.NULL
#
#
# AI invocation:
#
#
#     None
#
#
# AI response:
#
#
#     None
#
#
# Final request lifecycle:
#
#
#     COMPLETED
#
#
# Chewbacca objected:
#
#     "How can the request be completed when no AI answered me?"
#
#
# Agent 11 responded:
#
#     Determining that no AI processing is necessary can itself be
#     a successful processing outcome.
#
#
# Chewbacca has therefore learned:
#
#
#     REQUIREMENT != ROUTE
#
#     VALIDATED != AUTHORIZED
#
#     COMPLETED != AI MODEL INVOKED
#
#     FAILED REQUEST != NO VIABLE ROUTE
#
#     NO RESPONSE != FAILED RESPONSE
#
#
# Chewbacca remains dissatisfied.
