"""
Agent 11 AI Request Model
=========================

Defines the validated request contract used when a caller asks Agent 11
to perform AI reasoning.

The AIRequest model describes WHAT reasoning work is required.

It does NOT determine:

    - which AI provider should be used
    - which foundation model should be used
    - which reasoning service should be used
    - which network path should be used
    - whether the request is authorized
    - which route should be selected
    - which fallback route should be attempted
    - whether an MCP tool should be invoked

Those decisions belong to other Agent 11 architectural layers.


Core Principle
--------------

    THE REQUESTER SPECIFIES INTENT AND REQUIREMENTS.

    AGENT 11 DETERMINES IMPLEMENTATION.


The request therefore describes the workload without reaching through
the platform abstraction and selecting infrastructure.

For example:

    GOOD:

        "Analyze this security incident using heavy reasoning."

    BAD:

        "Send this security incident to External Model X
         through Internet Route Y."


The first describes a requirement.

The second attempts to make infrastructure decisions that belong to
Agent 11.


Architecture
------------

    CALLER
       │
       ▼
    AIRequest
       │
       │ describes requirements
       ▼
    POLICY
       │
       ▼
    CAPABILITY
       │
       ▼
    SERVICE
       │
       ▼
    NETWORK
       │
       ▼
    ROUTING
       │
       ▼
    AI EXECUTION


Important architectural invariants:

    REQUIREMENT != ROUTE

    CAPABILITY != MODEL

    CONTEXT != AUTHORIZATION

    VALIDATED != AUTHORIZED

    AUTHORIZED != CAPABLE

    CAPABLE != AVAILABLE

    AVAILABLE != REACHABLE

    REACHABLE != PERMITTED


An AIRequest may be perfectly valid while still being denied by policy,
unsupported by available services, unreachable through the network, or
unable to obtain a viable reasoning route.

Validation establishes that the request conforms to the request
contract.

Validation does NOT establish permission to execute it.
"""


# ===========================================================================
# Imports
# ===========================================================================

from typing import Any
from uuid import UUID, uuid4

from pydantic import Field

from ..base_model import Agent11BaseModel
from ..enums.ai_enums import AIRequestStatus, ReasoningLevel


# ===========================================================================
# AIRequest
# ===========================================================================


class AIRequest(Agent11BaseModel):
    """
    Validated request for AI reasoning within Agent 11.

    AIRequest represents the reasoning workload presented to the
    Agent 11 AI infrastructure.

    The model intentionally describes requirements rather than
    implementation choices.

    At the SEIR-I level, the request contains:

        request_id
            Unique identity for the request.

        task
            The reasoning work that should be performed.

        reasoning_level
            The expected level of reasoning complexity.

        context
            Structured information available to the reasoning process.

        estimated_tokens
            Optional estimate of the workload's token requirements.

        status
            Current lifecycle state of the request.


    Future versions of this contract may also include structured:

        data classification
        capability requirements
        user data preferences

    Those concepts are deliberately NOT implemented here until their
    corresponding Agent 11 domain models have been designed and tested.
    """

    # -----------------------------------------------------------------------
    # Request Identity
    # -----------------------------------------------------------------------

    request_id: UUID = Field(
        default_factory=uuid4,
        description=(
            "Unique identifier used to correlate the AI request with "
            "policy decisions, routing decisions, execution activity, "
            "telemetry, and the eventual response."
        ),
    )

    # -----------------------------------------------------------------------
    # Reasoning Task
    # -----------------------------------------------------------------------

    task: str = Field(
        min_length=1,
        description=(
            "The reasoning task Agent 11 is being asked to perform."
        ),
    )

    # -----------------------------------------------------------------------
    # Reasoning Requirement
    # -----------------------------------------------------------------------

    reasoning_level: ReasoningLevel = Field(
        default=ReasoningLevel.STANDARD,
        description=(
            "The level of reasoning complexity expected for the request. "
            "This describes a workload requirement and does not select "
            "a model, provider, service, or route."
        ),
    )

    # -----------------------------------------------------------------------
    # Request Context
    # -----------------------------------------------------------------------

    context: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Structured contextual information available to the reasoning "
            "process. Context may contain application, security, operational, "
            "or other domain-specific information required by the task."
        ),
    )

    # -----------------------------------------------------------------------
    # Workload Estimate
    # -----------------------------------------------------------------------

    estimated_tokens: int | None = Field(
        default=None,
        ge=0,
        strict=True,
        description=(
            "Optional estimate of the number of tokens associated with the "
            "reasoning workload. This value may later contribute to "
            "capability, capacity, performance, and cost-aware routing."
        ),
    )

    # -----------------------------------------------------------------------
    # Request Lifecycle
    # -----------------------------------------------------------------------

    status: AIRequestStatus = Field(
        default=AIRequestStatus.CREATED,
        description=(
            "Current lifecycle state of the AI request. Request status "
            "describes processing state and does not establish policy "
            "authorization, service availability, network reachability, "
            "or route viability."
        ),
    )


# ===========================================================================
# Field Architecture
# ===========================================================================

# AIRequest currently has six primary fields:
#
#
#     AIRequest
#         │
#         ├── request_id
#         │       │
#         │       └── Which request is this?
#         │
#         ├── task
#         │       │
#         │       └── What reasoning work should be performed?
#         │
#         ├── reasoning_level
#         │       │
#         │       └── How much reasoning is expected?
#         │
#         ├── context
#         │       │
#         │       └── What information is available?
#         │
#         ├── estimated_tokens
#         │       │
#         │       └── How large might the reasoning workload be?
#         │
#         └── status
#                 │
#                 └── Where is the request in its lifecycle?
#
#
# Notice what is deliberately absent:
#
#     provider
#     model
#     endpoint
#     selected_route
#     fallback_route
#     network_path
#     policy_decision
#     service_status
#
#
# Those values belong to downstream architectural layers.
#
#
# The caller describes the workload.
#
# Agent 11 determines how that workload should be serviced.


# ===========================================================================
# Request Identity
# ===========================================================================

# request_id exists primarily for correlation.
#
#
# A single request may eventually produce:
#
#
#     AIRequest
#         │
#         ├── PolicyEvent
#         │
#         ├── RoutingDecision
#         │
#         ├── NetworkDecision
#         │
#         ├── ModelInvocation
#         │
#         ├── MCPInvocation
#         │
#         ├── UsageEvent
#         │
#         └── AIResponse
#
#
# request_id allows those records to be associated with the same
# reasoning request.
#
#
# IMPORTANT:
#
#     REQUEST IDENTITY != USER IDENTITY
#
#
# request_id identifies the request.
#
# It does NOT identify:
#
#     the human user
#     the calling application
#     the agent
#     the workload identity
#     the delegated authority
#
#
# Identity and authority are separate architectural concerns and will
# be handled by the appropriate Agent 11 layers.


# ===========================================================================
# Task
# ===========================================================================

# task answers:
#
#     "What reasoning work should Agent 11 perform?"
#
#
# Example:
#
#     task=(
#         "Analyze the available application, identity, and network "
#         "evidence and determine the most likely root cause."
#     )
#
#
# The task should describe the reasoning objective.
#
# It should NOT encode infrastructure instructions.
#
#
# GOOD:
#
#     "Analyze this Wiz P1 finding and determine whether the
#      reported severity is justified."
#
#
# BAD:
#
#     "Send this Wiz P1 finding to Model X using Provider Y."
#
#
# The first describes work.
#
# The second attempts to perform routing.


# ===========================================================================
# Reasoning Level
# ===========================================================================

# reasoning_level describes the expected complexity of the reasoning
# workload.
#
#
# Current vocabulary:
#
#     LIGHT
#     STANDARD
#     HEAVY
#
#
# Conceptually:
#
#
#     LIGHT
#         │
#         └── relatively simple reasoning
#
#
#     STANDARD
#         │
#         └── normal/default reasoning workload
#
#
#     HEAVY
#         │
#         └── substantial reasoning requirement
#
#
# The reasoning level does NOT directly correspond to a model.
#
#
#     HEAVY
#        !=
#     EXPENSIVE MODEL
#
#
# Nor does it correspond directly to a routing destination.
#
#
#     HEAVY
#        !=
#     COMPANY_ONPREM_LLM
#
#
# Instead:
#
#
#     AIRequest
#         │
#         └── reasoning_level = HEAVY
#                         │
#                         ▼
#                  Agent 11 evaluates
#                         │
#            ┌────────────┼────────────┐
#            ▼            ▼            ▼
#         POLICY      CAPABILITY     SERVICE
#                                      │
#                                      ▼
#                                   NETWORK
#                                      │
#                                      ▼
#                                   ROUTING
#
#
# The request describes the requirement.
#
# The platform selects the implementation.


# ===========================================================================
# Context
# ===========================================================================

# context provides structured information required by the reasoning task.
#
#
# Example:
#
#     context={
#         "finding_id": "WIZ-12345",
#         "reported_severity": "P1",
#         "resource": "prod-api",
#         "environment": "production",
#         "account": "security-prod",
#     }
#
#
# This allows Agent 11 to distinguish:
#
#
#     TASK
#
#         What should the reasoning system do?
#
#
# from:
#
#
#     CONTEXT
#
#         What information should the reasoning system consider?
#
#
# This separation becomes increasingly important as Agent 11 evolves.
#
#
# For SEIR-I:
#
#     context: dict[str, Any]
#
#
# provides a deliberately flexible interface.
#
#
# Future versions may replace or supplement generic context with typed
# governed context objects carrying information such as:
#
#     provenance
#     source
#     owner
#     classification
#     residency
#     retention
#     lineage
#
#
# That future complexity is intentionally NOT implemented here yet.
#
# We leave the architectural connection point without prematurely
# building the entire future governance system.


# ===========================================================================
# Token Estimate
# ===========================================================================

# estimated_tokens describes an expected workload characteristic.
#
# It does NOT tell Agent 11 which model to use.
#
#
# Example:
#
#     estimated_tokens = 500
#
# may represent a very different workload from:
#
#     estimated_tokens = 100_000
#
#
# Token estimates may eventually influence:
#
#     context-window compatibility
#     service capability
#     capacity
#     latency
#     throughput
#     batching
#     caching
#     GPU requirements
#     cost
#     FinOps decisions
#
#
# But:
#
#
#     TOKEN ESTIMATE != ROUTING DECISION
#
#
# Security and policy remain authoritative.
#
#
# A cheaper route is not automatically a permitted route.
#
# A route with a larger context window is not automatically an
# authorized route.
#
#
#     CHEAPER != PERMITTED
#
#     CAPABLE != AUTHORIZED


# ===========================================================================
# Request Lifecycle
# ===========================================================================

# AIRequestStatus describes where the request is in its processing
# lifecycle.
#
#
# Typical progression:
#
#
#     CREATED
#        │
#        ▼
#     VALIDATED
#        │
#        ▼
#     PROCESSING
#        │
#        ├──────────────────► FAILED
#        │
#        ├──────────────────► CANCELLED
#        │
#        ▼
#     COMPLETED
#
#
# IMPORTANT:
#
# Request lifecycle and security authorization are separate concepts.
#
#
#     VALIDATED
#         !=
#     AUTHORIZED
#
#
# A VALIDATED request means the request successfully passed the
# applicable request-validation stage.
#
# It does NOT mean:
#
#     policy approved the request
#     data may leave a security boundary
#     a model is authorized
#     a service is capable
#     a service is healthy
#     a network path is available
#     a route has been selected
#
#
# This would therefore be architecturally dangerous:
#
#
#     if request.status is AIRequestStatus.VALIDATED:
#         send_to_model()
#
#
# Validation is only one gate.
#
#
# The correct conceptual progression is:
#
#
#     VALID REQUEST
#          │
#          ▼
#       POLICY
#          │
#          ▼
#     CAPABILITY
#          │
#          ▼
#       SERVICE
#          │
#          ▼
#       NETWORK
#          │
#          ▼
#       ROUTING
#          │
#          ▼
#      EXECUTION
#
#
# Each layer answers a different question.


# ===========================================================================
# Architecture Boundary
# ===========================================================================

# AIRequest is deliberately framework-independent.
#
# This module should NOT depend on:
#
#     LangGraph
#     CrewAI
#     Langfuse
#     Amazon Bedrock SDKs
#     model-provider SDKs
#     MCP implementations
#     orchestration frameworks
#
#
# Those technologies may consume AIRequest.
#
# AIRequest should not depend on them.
#
#
# Conceptually:
#
#
#                         AIRequest
#                            │
#                            ▼
#                       Agent 11
#                            │
#          ┌─────────────────┼─────────────────┐
#          │                 │                 │
#          ▼                 ▼                 ▼
#      LangGraph          CrewAI        Future Framework
#
#
# If the orchestration framework changes, the domain contract should
# survive.
#
#
#     FRAMEWORKS CHANGE.
#
#     DOMAIN CONTRACTS SHOULD SURVIVE THEM.
#
#
# Python provides the language.
#
# Pydantic provides the validated contract.
#
# Orchestration frameworks operate above that contract.


# ===========================================================================
# Core Architecture Invariants
# ===========================================================================

# Keep these distinctions explicit throughout Agent 11:
#
#
#     REQUEST != ROUTE
#
#     REQUIREMENT != IMPLEMENTATION
#
#     REASONING LEVEL != MODEL
#
#     CAPABILITY != MODEL
#
#     CONTEXT != AUTHORIZATION
#
#     VALIDATED != AUTHORIZED
#
#     AUTHORIZED != CAPABLE
#
#     CAPABLE != AVAILABLE
#
#     AVAILABLE != REACHABLE
#
#     REACHABLE != PERMITTED
#
#     HEALTHY != AUTHORIZED
#
#     CHEAPER != PERMITTED
#
#     FASTER != PERMITTED
#
#
# AIRequest tells Agent 11 what is being requested.
#
# It does not give the caller authority to decide how Agent 11
# satisfies that request.

# ===========================================================================
# AIRequest Usage
# ===========================================================================

# The simplest possible AIRequest requires only a task.
#
# Pydantic and the model defaults provide:
#
#     request_id
#     reasoning_level
#     context
#     estimated_tokens
#     status
#
#
# Example:
#
#
#     request = AIRequest(
#         task="Summarize the application error.",
#     )
#
#
# Conceptually:
#
#
#     AIRequest
#         │
#         ├── request_id        automatically generated
#         ├── task              supplied by caller
#         ├── reasoning_level   STANDARD
#         ├── context           {}
#         ├── estimated_tokens  None
#         └── status            CREATED
#
#
# The caller does not need to understand:
#
#     providers
#     models
#     endpoints
#     network topology
#     routing
#     fallback
#
#
# Those concerns are intentionally hidden behind Agent 11.


# ===========================================================================
# Example: Light Reasoning
# ===========================================================================

# A caller may explicitly describe a relatively simple reasoning
# workload:
#
#
#     request = AIRequest(
#         task="Summarize these CloudWatch errors.",
#         reasoning_level=ReasoningLevel.LIGHT,
#         estimated_tokens=2_000,
#     )
#
#
# This means:
#
#     "The workload requires LIGHT reasoning."
#
#
# It does NOT mean:
#
#     "Use the cheapest model."
#
#     "Use the smallest model."
#
#     "Use an external model."
#
#     "Use the company cloud model."
#
#
# ReasoningLevel describes a requirement.
#
# Agent 11 remains responsible for determining how that requirement
# should be satisfied.


# ===========================================================================
# Example: Heavy Reasoning
# ===========================================================================

# A more complex request might look like:
#
#
#     request = AIRequest(
#         task=(
#             "Analyze the available application, identity, and network "
#             "evidence and determine the most likely root cause."
#         ),
#         reasoning_level=ReasoningLevel.HEAVY,
#         estimated_tokens=75_000,
#     )
#
#
# The request tells Agent 11:
#
#
#     WORKLOAD
#         │
#         ├── substantial reasoning required
#         │
#         └── estimated workload approximately 75,000 tokens
#
#
# Agent 11 may later evaluate:
#
#
#     DATA POLICY
#          │
#          ▼
#     REQUIRED CAPABILITIES
#          │
#          ▼
#     AVAILABLE SERVICES
#          │
#          ▼
#     NETWORK PATHS
#          │
#          ▼
#     ROUTING
#
#
# The caller still does not select the model.


# ===========================================================================
# Example: Structured Context
# ===========================================================================

# context separates the reasoning instruction from the information
# being reasoned about.
#
#
# Example:
#
#
#     request = AIRequest(
#         task=(
#             "Evaluate whether this security finding justifies "
#             "P1 severity."
#         ),
#         reasoning_level=ReasoningLevel.HEAVY,
#         context={
#             "finding_id": "WIZ-12345",
#             "reported_severity": "P1",
#             "resource": "prod-api",
#             "environment": "production",
#             "account": "security-prod",
#         },
#         estimated_tokens=20_000,
#     )
#
#
# This produces a useful separation:
#
#
#     TASK
#         │
#         └── Evaluate whether the finding justifies P1 severity.
#
#
#     CONTEXT
#         │
#         ├── finding_id
#         ├── reported_severity
#         ├── resource
#         ├── environment
#         └── account
#
#
# This is preferable to encoding all available structured information
# into one large unstructured task string.
#
#
# Structured context also creates a future connection point for:
#
#     classification
#     provenance
#     lineage
#     retention
#     residency
#     source trust
#
#
# Those concepts will become increasingly important as Agent 11 moves
# from SEIR-I into SEIR-II.


# ===========================================================================
# Native Pydantic Interface
# ===========================================================================

# Agent 11 intentionally exposes Pydantic rather than hiding it behind
# custom serialization and validation wrappers.
#
#
# Pydantic is part of the architecture.
#
#
# Common operations include:
#
#
#     model_validate()
#
#     model_validate_json()
#
#     model_dump()
#
#     model_dump_json()
#
#     model_copy()
#
#     model_json_schema()
#
#
# Students should learn these APIs directly.
#
#
# We do NOT need:
#
#
#     request.to_dict()
#
#     request.to_json()
#
#     AIRequest.from_dict()
#
#
# merely to rename functionality Pydantic already provides.


# ===========================================================================
# Pydantic: model_dump()
# ===========================================================================

# AIRequest can be converted into a Python dictionary using:
#
#
#     request = AIRequest(
#         task="Analyze the security finding.",
#         reasoning_level=ReasoningLevel.HEAVY,
#     )
#
#
#     data = request.model_dump()
#
#
# model_dump() produces a representation suitable for additional
# application processing.
#
#
# This may eventually be useful when passing request information into:
#
#     workflow state
#     telemetry
#     APIs
#     queues
#     persistence layers
#     evaluation systems


# ===========================================================================
# Pydantic: model_dump_json()
# ===========================================================================

# AIRequest can also be serialized to JSON:
#
#
#     json_data = request.model_dump_json(indent=2)
#
#
# JSON becomes especially important when Agent 11 components cross
# process, service, or network boundaries.
#
#
# Conceptually:
#
#
#     Python Object
#          │
#          ▼
#      AIRequest
#          │
#          ▼
#     Pydantic Contract
#          │
#          ▼
#         JSON
#          │
#          ▼
#     API / SERVICE / QUEUE
#
#
# The domain model remains the contract even when the transport
# representation changes.


# ===========================================================================
# Pydantic: model_validate()
# ===========================================================================

# External or previously serialized data can be validated directly:
#
#
#     payload = {
#         "task": "Analyze the security finding.",
#         "reasoning_level": "heavy",
#         "estimated_tokens": 15_000,
#     }
#
#
#     request = AIRequest.model_validate(payload)
#
#
# Pydantic validates the payload against the AIRequest contract.
#
#
# For example:
#
#
#     "heavy"
#
#         becomes
#
#     ReasoningLevel.HEAVY
#
#
# because ReasoningLevel is a validated enum field.
#
#
# This is one of the reasons enums are valuable at system boundaries.
#
# The caller cannot simply invent arbitrary reasoning levels.


# ===========================================================================
# Pydantic: model_validate_json()
# ===========================================================================

# JSON can also be validated directly:
#
#
#     payload = '''
#     {
#         "task": "Analyze the security finding.",
#         "reasoning_level": "heavy",
#         "estimated_tokens": 15000
#     }
#     '''
#
#
#     request = AIRequest.model_validate_json(payload)
#
#
# Again:
#
#
#     TRANSPORT DATA
#          │
#          ▼
#     PYDANTIC VALIDATION
#          │
#          ▼
#     VALIDATED DOMAIN MODEL
#
#
# This pattern becomes useful as Agent 11 begins accepting requests
# from services rather than only local Python callers.


# ===========================================================================
# Pydantic: model_json_schema()
# ===========================================================================

# Pydantic can describe the AIRequest contract programmatically:
#
#
#     schema = AIRequest.model_json_schema()
#
#
# This capability becomes extremely useful for AI platform engineering.
#
#
# The same domain contract can contribute to:
#
#     API documentation
#     structured AI outputs
#     tool contracts
#     service validation
#     MCP integration
#     testing
#     interoperability
#
#
# This is another reason Agent 11 does not hide Pydantic behind custom
# helper methods.


# ===========================================================================
# Validation: Unknown Fields
# ===========================================================================

# Agent11BaseModel uses:
#
#
#     extra="forbid"
#
#
# Therefore this request should fail validation:
#
#
#     request = AIRequest(
#         task="Analyze the finding.",
#         reasoning_level=ReasoningLevel.HEAVY,
#         use_skynet=True,
#     )
#
#
# "use_skynet" is not part of the AIRequest contract.
#
#
# This behavior is important.
#
# Agent 11 should not silently accept unexpected fields at an important
# architectural boundary.
#
#
# Consider:
#
#
#     {
#         "task": "Analyze the incident.",
#         "model": "caller-selected-model"
#     }
#
#
# If "model" is not part of AIRequest, validation should reject it.
#
#
# The caller does not gain infrastructure control simply by inventing
# a field.


# ===========================================================================
# Validation: Token Estimate
# ===========================================================================

# estimated_tokens has two important validation constraints:
#
#
#     ge=0
#
#     strict=True
#
#
# Therefore:
#
#
#     AIRequest(
#         task="Analyze logs.",
#         estimated_tokens=50_000,
#     )
#
#
# is valid.
#
#
# But:
#
#
#     AIRequest(
#         task="Analyze logs.",
#         estimated_tokens=-50_000,
#     )
#
#
# is invalid because token estimates cannot be negative.
#
#
# And:
#
#
#     AIRequest(
#         task="Analyze logs.",
#         estimated_tokens="50000",
#     )
#
#
# is invalid because estimated_tokens is intentionally strict.
#
#
# Pydantic is not allowed to silently convert the string:
#
#
#     "50000"
#
# into:
#
#     50000
#
#
# for this field.
#
#
# This demonstrates an important Agent 11 modeling principle:
#
#
#     STRICTNESS IS PART OF THE DOMAIN CONTRACT.
#
#
# Strictness should be applied where the semantics justify it rather
# than globally enabling strict behavior everywhere.


# ===========================================================================
# Validation: Task
# ===========================================================================

# task requires:
#
#
#     min_length=1
#
#
# Therefore:
#
#
#     AIRequest(
#         task="Analyze the incident.",
#     )
#
#
# is valid.
#
#
# While:
#
#
#     AIRequest(
#         task="",
#     )
#
#
# is invalid.
#
#
# NOTE:
#
# min_length=1 prevents an empty string.
#
# It does NOT currently prevent a whitespace-only task such as:
#
#
#     task="     "
#
#
# We are deliberately NOT adding custom task validators yet.
#
# If future requirements establish that task normalization or
# whitespace validation is necessary, that behavior can be introduced
# intentionally rather than automatically expanding the first version
# of the contract.


# ===========================================================================
# Assignment Validation
# ===========================================================================

# Agent11BaseModel enables:
#
#
#     validate_assignment=True
#
#
# Therefore validation continues after object creation.
#
#
# For example:
#
#
#     request = AIRequest(
#         task="Analyze the P1 finding.",
#     )
#
#
#     request.status = AIRequestStatus.VALIDATED
#
#
# is valid.
#
#
# But assigning an invalid value to a validated field should trigger
# Pydantic validation rather than silently corrupting the model.
#
#
# This becomes useful because AIRequest currently carries lifecycle
# state.
#
#
# IMPORTANT:
#
# The fact that status can change does not mean every caller should
# have unrestricted authority to change request lifecycle state.
#
# The model validates representation.
#
# Higher architectural layers determine who is permitted to perform
# lifecycle transitions.


# ===========================================================================
# Representation Validation vs Authorization
# ===========================================================================

# This distinction deserves special attention.
#
#
# PYDANTIC asks:
#
#     "Is this a valid AIRequest?"
#
#
# POLICY asks:
#
#     "May this AIRequest proceed?"
#
#
# These are completely different questions.
#
#
# Example:
#
#
#     AIRequest(
#         task="Analyze restricted company information.",
#         reasoning_level=ReasoningLevel.HEAVY,
#     )
#
#
# may be perfectly valid according to Pydantic.
#
# Yet organizational policy may later determine that only a particular
# class of company-controlled reasoning service may process the data.
#
#
# Therefore:
#
#
#     VALID DATA
#         !=
#     AUTHORIZED OPERATION
#
#
# Pydantic protects the contract.
#
# Policy protects the boundary.


# ===========================================================================
# Request Lifecycle Example
# ===========================================================================

# A normal request may move through:
#
#
#     request.status = AIRequestStatus.CREATED
#
#                    │
#                    ▼
#
#     request.status = AIRequestStatus.VALIDATED
#
#                    │
#                    ▼
#
#     request.status = AIRequestStatus.PROCESSING
#
#                    │
#                    ▼
#
#     request.status = AIRequestStatus.COMPLETED
#
#
# Failure may instead produce:
#
#
#     PROCESSING
#         │
#         ▼
#       FAILED
#
#
# Cancellation may produce:
#
#
#     CREATED / VALIDATED / PROCESSING
#                  │
#                  ▼
#              CANCELLED
#
#
# The precise transition rules do not belong in this model.
#
# AIRequest stores lifecycle state.
#
# An orchestrator or lifecycle service should eventually control valid
# state transitions.
#
#
# This maintains our fundamental rule:
#
#
#     MODELS DESCRIBE.
#
#     ORCHESTRATORS COORDINATE.


# ===========================================================================
# AI May Not Be Required
# ===========================================================================

# Agent 11 exists within a larger engineering philosophy:
#
#
#     DO WE NEED AI AT ALL?
#
#
# Not every operational task requires AI reasoning.
#
#
# Conceptually:
#
#
#     BUSINESS / TECHNICAL TASK
#               │
#               ▼
#     CAN NORMAL CODE, RULES,
#     OR AUTOMATION SOLVE IT?
#               │
#          ┌────┴────┐
#          │         │
#        YES         NO
#          │         │
#          ▼         ▼
#     AUTOMATION   DOES AI
#                  ADD VALUE?
#                      │
#                      ▼
#                  AI REQUEST
#
#
# AIRequest therefore does not need to represent every deterministic
# operation in the system.
#
# If a task can be completed safely and reliably without AI, the
# architecture should remain free to do so.
#
#
#     AI IS A CAPABILITY.
#
#     AI IS NOT A REQUIREMENT FOR EVERY WORKFLOW.


# ===========================================================================
# Fields Deliberately Excluded from AIRequest
# ===========================================================================

# The following fields should NOT currently appear in AIRequest:
#
#
#     provider
#
#         The caller should not normally select an AI provider.
#
#
#     model
#
#         The caller describes reasoning requirements rather than
#         selecting a specific model.
#
#
#     endpoint
#
#         Service endpoints belong to runtime/service infrastructure.
#
#
#     selected_route
#
#         Routing decisions belong to the routing layer.
#
#
#     fallback_route
#
#         Fallback belongs to routing and must be independently
#         re-evaluated for viability.
#
#
#     network_path
#
#         Network path information belongs to the network layer.
#
#
#     policy_decision
#
#         Policy decisions are outputs of policy evaluation.
#
#
#     service_status
#
#         Runtime/service health belongs to service infrastructure.
#
#
#     ai_response
#
#         The response is a separate domain object.
#
#
# The absence of these fields is not an omission.
#
# It is architectural separation.


# ===========================================================================
# Incorrect Request Architecture
# ===========================================================================

# Avoid request contracts resembling:
#
#
#     AIRequest(
#         task="Analyze this incident.",
#         provider="some-provider",
#         model="some-model",
#         route="external_fm",
#         endpoint="https://some-endpoint.example",
#         network_path="internet",
#         fallback_model="some-other-model",
#     )
#
#
# Such a request would allow the caller to reach through the AI
# platform abstraction and make infrastructure decisions.
#
#
# Conceptually:
#
#
#     CALLER
#        │
#        ├──────────────► PROVIDER
#        ├──────────────► MODEL
#        ├──────────────► NETWORK
#        └──────────────► FALLBACK
#
#
# Agent 11 would no longer be operating as a control layer.
#
#
# Instead:
#
#
#     CALLER
#        │
#        ▼
#     AIRequest
#        │
#        ▼
#     AGENT 11
#        │
#        ├── policy
#        ├── capability
#        ├── service state
#        ├── network state
#        └── routing
#                │
#                ▼
#           IMPLEMENTATION
#
#
# This preserves the abstraction.


# ===========================================================================
# Future Extension: Data Classification
# ===========================================================================

# AIRequest will eventually need structured information describing the
# classification of data associated with the reasoning request.
#
#
# Future concept:
#
#
#     data_classification: DataClassification
#
#
# We are deliberately NOT implementing this field until:
#
#
#     models/ai/data_classification.py
#
#
# has been designed and tested.
#
#
# Data classification will eventually contribute to policy evaluation:
#
#
#     AIRequest
#         │
#         ▼
#     DataClassification
#         │
#         ▼
#       POLICY
#         │
#         ├── route allowed
#         ├── route restricted
#         └── route denied
#
#
# IMPORTANT:
#
#
#     CLASSIFICATION != POLICY
#
#
# Classification describes the data.
#
# Policy determines what may be done with that classification.


# ===========================================================================
# Future Extension: Required Capabilities
# ===========================================================================

# AIRequest will eventually be able to express capabilities required
# by the reasoning workload.
#
#
# Future concept:
#
#
#     required_capabilities: set[AICapability]
#
#
# Example:
#
#
#     required_capabilities={
#         AICapability.CODE_REASONING,
#         AICapability.LONG_CONTEXT,
#     }
#
#
# Capability requirements allow Agent 11 to ask:
#
#
#     "Which reasoning services can actually perform this work?"
#
#
# Conceptually:
#
#
#     REQUEST
#        │
#        ├── CODE_REASONING
#        └── LONG_CONTEXT
#                 │
#                 ▼
#         SERVICE REGISTRY
#                 │
#          ┌──────┴──────┐
#          ▼             ▼
#      SERVICE A      SERVICE B
#        ✓   ✓          ✓   ✗
#          │
#          ▼
#       CAPABLE
#
#
# But capability remains only one part of viability.
#
#
#     CAPABLE != AUTHORIZED
#
#     CAPABLE != AVAILABLE
#
#     CAPABLE != REACHABLE
#
#
# The capability model should therefore be designed independently
# before being incorporated into AIRequest.


# ===========================================================================
# Future Extension: User Data Preference
# ===========================================================================

# AIRequest may eventually carry a user-level data-routing constraint.
#
#
# Future concept:
#
#
#     user_data_preference: UserDataPreference
#
#
# Possible examples include:
#
#
#     ORGANIZATION_DEFAULT
#
#     COMPANY_ONLY
#
#     ONPREM_ONLY
#
#
# User policy may restrict organizational policy.
#
# User policy may NEVER expand organizational policy.
#
#
# Therefore:
#
#
#     EFFECTIVE POLICY
#
#         =
#
#     ORGANIZATION POLICY
#
#         ∩
#
#     USER POLICY
#
#
# Never:
#
#
#     ORGANIZATION POLICY
#
#         ∪
#
#     USER POLICY
#
#
# A user may close additional doors.
#
# A user may not open a door the organization has already locked.
#
#
# Example:
#
#
#     ORGANIZATION:
#
#         External FM          DENIED
#         Company Cloud LLM    ALLOWED
#         Company On-Prem LLM  ALLOWED
#
#
#     USER:
#
#         ONPREM_ONLY
#
#
#     EFFECTIVE:
#
#         External FM          DENIED
#         Company Cloud LLM    DENIED
#         Company On-Prem LLM  ALLOWED
#
#
# User preference is therefore a constraint.
#
# It is NOT a routing command.
#
#
#     CONSTRAINT != ROUTE SELECTION


# ===========================================================================
# Future SEIR-II: Governed Context
# ===========================================================================

# SEIR-I intentionally begins with:
#
#
#     context: dict[str, Any]
#
#
# This makes the request model easy to understand and useful while the
# surrounding Agent 11 architecture is being developed.
#
#
# SEIR-II may introduce richer governed context.
#
#
# Conceptually:
#
#
#     AIRequest
#         │
#         ▼
#     GovernedContext
#         │
#         ├── payload
#         │
#         ├── source
#         │
#         ├── owner
#         │
#         ├── provenance
#         │
#         ├── classification
#         │
#         ├── residency
#         │
#         ├── retention
#         │
#         ├── lineage
#         │
#         └── trust metadata
#
#
# This allows Agent 11 to evolve from:
#
#
#     "Here is some context."
#
#
# toward:
#
#
#     "Here is context whose origin, sensitivity, ownership,
#      movement, and lifecycle are understood."
#
#
# That distinction becomes extremely important at enterprise scale.
#
#
# The SEIR-I model does not need to solve that entire problem today.
#
# It only needs to avoid preventing that evolution tomorrow.


# ===========================================================================
# Future SEIR-II: Capability-Based Requests
# ===========================================================================

# As Agent 11 matures, callers should increasingly request platform
# capabilities rather than infrastructure products.
#
#
# Example future request:
#
#
#     capability="security_reasoning"
#
#     reasoning_level=ReasoningLevel.HEAVY
#
#     data_classification=<classification>
#
#     required_capabilities=<requirements>
#
#
# The platform may then determine:
#
#
#                         REQUEST
#                            │
#                            ▼
#                      CONTROL PLANE
#                            │
#              ┌─────────────┼─────────────┐
#              │             │             │
#              ▼             ▼             ▼
#           POLICY        REGISTRY      NETWORK
#              │             │             │
#              └─────────────┼─────────────┘
#                            ▼
#                         ROUTING
#                            │
#              ┌─────────────┼─────────────┐
#              ▼             ▼             ▼
#        EXTERNAL FM   COMPANY CLOUD   COMPANY ON-PREM
#
#
# The caller expresses intent.
#
# The control plane resolves implementation.


# ===========================================================================
# Agent 11 Route Viability
# ===========================================================================

# AIRequest does not calculate route viability.
#
# However, it supplies information that downstream layers may use when
# calculating viability.
#
#
# Agent 11's conceptual viability rule remains:
#
#
#     VIABLE ROUTE
#
#         =
#
#     POLICY PERMITTED
#
#         +
#
#     SERVICE CAPABLE
#
#         +
#
#     SERVICE AVAILABLE
#
#         +
#
#     PATH AVAILABLE
#
#
# Every component matters.
#
#
# A model may be capable but prohibited.
#
# A service may be authorized but unavailable.
#
# A service may be healthy but unreachable.
#
# A network path may exist to a destination that policy forbids.
#
#
# Therefore:
#
#
#     REACHABLE DOES NOT MEAN AUTHORIZED.
#
#     AUTHORIZED DOES NOT MEAN REACHABLE.
#
#     HEALTHY DOES NOT MEAN PERMITTED.
#
#     CAPABLE DOES NOT MEAN AUTHORIZED.


# ===========================================================================
# Policy-Safe Fallback
# ===========================================================================

# AIRequest does not select fallback behavior.
#
# Fallback belongs to the routing architecture.
#
#
# The critical Agent 11 rule is:
#
#
#     FALLBACK MAY REDUCE AVAILABILITY.
#
#     FALLBACK MAY NEVER REDUCE SECURITY POLICY.
#
#
# If a preferred reasoning service becomes unavailable, Agent 11 may
# search for another viable route.
#
# But every fallback candidate must independently satisfy:
#
#
#     policy
#     capability
#     service availability
#     network availability
#
#
# Fallback does NOT mean:
#
#
#     "The approved service failed, so send the data somewhere else."
#
#
# It means:
#
#
#     "The preferred viable route failed.
#      Find another independently viable route."
#
#
# If no compliant route exists:
#
#
#     NO VIABLE ROUTE
#
#
# is the correct result.
#
#
# Sometimes refusing to invoke AI is successful security enforcement.


# ===========================================================================
# Framework Independence
# ===========================================================================

# AIRequest is designed to survive framework changes.
#
#
# Today:
#
#     Python
#     Pydantic
#     LangGraph
#     CrewAI
#     Langfuse
#
#
# Tomorrow:
#
#     Python
#     Pydantic
#     SomeNewOrchestrator
#     SomeNewAgentFramework
#     SomeNewObservabilityPlatform
#
#
# The orchestration and tooling ecosystem may change.
#
# AIRequest should remain recognizable.
#
#
# This is why this file does not import:
#
#
#     langgraph
#     crewai
#     langfuse
#
#
# Those frameworks operate around the domain model.
#
#
# The model should not become a hostage to the framework.


# ===========================================================================
# Architectural Summary
# ===========================================================================

# AIRequest currently answers six questions:
#
#
#     1. WHICH REQUEST?
#
#            request_id
#
#
#     2. WHAT NEEDS TO BE DONE?
#
#            task
#
#
#     3. HOW MUCH REASONING IS EXPECTED?
#
#            reasoning_level
#
#
#     4. WHAT INFORMATION IS AVAILABLE?
#
#            context
#
#
#     5. HOW LARGE MIGHT THE WORKLOAD BE?
#
#            estimated_tokens
#
#
#     6. WHERE IS THE REQUEST IN ITS LIFECYCLE?
#
#            status
#
#
# Future versions will additionally answer:
#
#
#     7. WHAT KIND OF DATA IS INVOLVED?
#
#            data_classification
#
#
#     8. WHAT MUST THE REASONING SERVICE BE ABLE TO DO?
#
#            required_capabilities
#
#
#     9. HAS THE USER NARROWED WHERE THEIR DATA MAY GO?
#
#            user_data_preference
#
#
# None of these questions should become:
#
#
#     "Which specific model does the caller want?"
#
#
# That is deliberately a platform decision.


# ===========================================================================
# Chewbacca's AIRequest Commentary
# ===========================================================================

# Chewbacca has reviewed the AIRequest architecture.
#
#
# Chewbacca:
#
#     "I would like to submit an AI request."
#
#
# Agent 11:
#
#     Proceed.
#
#
# Chewbacca:
#
#     AIRequest(
#         task="Determine whether Chewbacca requires street access.",
#         estimated_tokens="Chewbacca",
#     )
#
#
# Pydantic:
#
#     ValidationError
#
#
# Chewbacca:
#
#     "There appears to be a problem with Pydantic."
#
#
# Agent 11:
#
#     There is not.
#
#
# Chewbacca:
#
#     "I identify as an integer."
#
#
# Pydantic:
#
#     You are still not an integer.
#
#
# Chewbacca then attempts:
#
#
#     AIRequest(
#         task="Approve street access.",
#         reasoning_level=ReasoningLevel.HEAVY,
#         provider="whatever approves street access",
#         model="street-access-9000",
#         route="external_fm",
#     )
#
#
# Pydantic:
#
#     Extra inputs are not permitted.
#
#
# Chewbacca:
#
#     "The requester should be allowed to choose the model."
#
#
# Agent 11:
#
#     No.
#
#
# Chewbacca:
#
#     "The requester should at least be allowed to choose the route."
#
#
# Agent 11:
#
#     Also no.
#
#
# Chewbacca:
#
#     "What exactly am I allowed to choose?"
#
#
# Agent 11:
#
#     You may describe:
#
#         what you need
#         the context
#         the reasoning requirement
#
#     Later you may also describe legitimate constraints such as:
#
#         data classification
#         capability requirements
#         user data restrictions
#
#
# Chewbacca:
#
#     "And Agent 11 chooses where the request goes?"
#
#
# Agent 11:
#
#     After evaluating:
#
#         policy
#         capability
#         service availability
#         network availability
#         routing rules
#
#
# Chewbacca:
#
#     "What if none of the routes approve street access?"
#
#
# Agent 11:
#
#     NO_VIABLE_ROUTE.
#
#
# Chewbacca:
#
#     "Can fallback ignore policy?"
#
#
# Agent 11:
#
#     Absolutely not.
#
#
# Chewbacca:
#
#     "Can I change my user preference to allow something the
#      organization prohibited?"
#
#
# Agent 11:
#
#     No.
#
#
# Chewbacca:
#
#     "This system seems deliberately designed to prevent me from
#      making infrastructure decisions."
#
#
# Agent 11:
#
#     Correct.
#
#
# Chewbacca:
#
#     "I want to speak to the AI Platform Architect."
#
#
# Agent 11:
#
#     They designed it this way.
#
#
# ---------------------------------------------------------------------------
# Final Lesson
# ---------------------------------------------------------------------------
#
#
#     AIRequest DESCRIBES THE WORK.
#
#     IT DOES NOT SELECT THE INFRASTRUCTURE.
#
#
# The caller expresses:
#
#     intent
#     requirements
#     context
#     legitimate constraints
#
#
# Agent 11 evaluates:
#
#     policy
#     capability
#     service state
#     network state
#     routing
#
#
# and only then determines where, how, or whether AI reasoning occurs.
#
#
#     REQUEST != ROUTE
#
#     REQUIREMENT != IMPLEMENTATION
#
#     VALIDATED != AUTHORIZED
#
#     CAPABLE != PERMITTED
#
#     FALLBACK != POLICY ESCAPE
#
#
# And finally:
#
#
#     IF NO COMPLIANT ROUTE EXISTS,
#
#     DO NOT INVENT ONE.
