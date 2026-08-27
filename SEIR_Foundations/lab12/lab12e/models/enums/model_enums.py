"""
Agent 11 Model Enums
====================

Defines the controlled vocabulary used to describe the role and
operational condition of AI reasoning services.

This module answers two fundamental questions:

    ModelRole
        "What role does this reasoning resource play?"

    ServiceStatus
        "What is the current operational condition of the
         reasoning service?"

These concepts are intentionally independent.

Model Enums do NOT:

    - authenticate users
    - authorize requests
    - classify data
    - create policy
    - select routes
    - determine network reachability
    - identify specific vendors
    - identify specific model products
    - invoke AI models
    - invoke MCP tools
    - perform orchestration

Architecture rules:

    ROLE != STATUS

    PRIMARY != MANDATORY

    PRIMARY != VIABLE

    FALLBACK != POLICY EXCEPTION

    HEALTHY != AUTHORIZED

    DEGRADED != UNAVAILABLE

    UNKNOWN != HEALTHY

    UNKNOWN != UNAVAILABLE

    ROUTE != MODEL

    SERVICE REPORTS CONDITION.
    ROUTING DECIDES CONSEQUENCE.
"""

from .base_enum import Agent11Enum


# ===========================================================================
# Model Role
# ===========================================================================


class ModelRole(Agent11Enum):
    """
    Describes the role assigned to an AI reasoning resource.

    PRIMARY
        The preferred reasoning resource within the applicable
        configuration.

    FALLBACK
        An alternate reasoning resource that may be evaluated when
        the primary resource cannot be used.

    ModelRole establishes preference and candidate ordering.

    It does NOT establish:

        - policy permission
        - service capability
        - service availability
        - network reachability
        - routing viability

    Therefore:

        PRIMARY != MANDATORY

        PRIMARY != VIABLE

        FALLBACK != AUTOMATICALLY VIABLE
    """

    PRIMARY = "primary"
    FALLBACK = "fallback"


# ===========================================================================
# Service Status
# ===========================================================================


class ServiceStatus(Agent11Enum):
    """
    Describes the current operational condition of an AI reasoning
    service.

    HEALTHY
        The reasoning service is considered operational under normal
        conditions.

    DEGRADED
        The reasoning service remains operational, but one or more
        conditions are outside the expected normal operating range.

    UNAVAILABLE
        Agent 11 has information establishing that the reasoning
        service cannot currently service requests.

    UNKNOWN
        Agent 11 cannot currently establish the operational condition
        of the reasoning service.

    ServiceStatus reports operational condition.

    It does not determine whether the service is:

        - authorized
        - policy permitted
        - capable of the requested reasoning
        - reachable over the network
        - selected by routing

    Therefore:

        SERVICE REPORTS CONDITION.

        ROUTING DECIDES CONSEQUENCE.
    """

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


# ===========================================================================
# PRIMARY
# ===========================================================================

# ModelRole.PRIMARY means the reasoning resource is preferred within
# the applicable configuration.
#
# Example:
#
#
#     Company Cloud LLM
#
#     Role:
#         PRIMARY
#
#     Status:
#         HEALTHY
#
#
# This does not mean:
#
#
#     "Always use this service."
#
#
# A PRIMARY service may still be:
#
#
#     - prohibited by policy
#     - incapable of the requested work
#     - degraded
#     - unavailable
#     - unreachable
#
#
# Example:
#
#
#     Company Cloud LLM
#
#     Role                PRIMARY
#     Policy              ALLOW
#     Capability          SUFFICIENT
#     Service             UNAVAILABLE
#     Network             AVAILABLE
#
#                            |
#                            v
#
#                       NOT VIABLE
#
#
# Therefore:
#
#
#     PRIMARY != MANDATORY
#
#     PRIMARY != VIABLE


# ===========================================================================
# FALLBACK
# ===========================================================================

# ModelRole.FALLBACK means a reasoning resource may be considered as
# an alternate candidate.
#
# It does not mean the resource may automatically be used when the
# primary service fails.
#
# Example:
#
#
#     External FM
#
#     Role                FALLBACK
#     Capability          SUFFICIENT
#     Service             HEALTHY
#     Network             AVAILABLE
#     Policy              DENY
#
#                            |
#                            v
#
#                       NOT VIABLE
#
#
# FALLBACK gives the service no special security privilege.
#
#
# Therefore:
#
#
#     FALLBACK != POLICY EXCEPTION
#
#
# A fallback service is a candidate for evaluation.
#
# It is not an instruction to bypass evaluation.


# ===========================================================================
# HEALTHY
# ===========================================================================

# ServiceStatus.HEALTHY means the reasoning service is considered
# operational according to the available health information.
#
# Example:
#
#
#     External FM
#
#     Service Status:
#         HEALTHY
#
#     Policy:
#         DENY
#
#
# There is no contradiction.
#
# The service can be technically healthy while policy prohibits the
# current request from using it.
#
#
# Therefore:
#
#
#     HEALTHY != AUTHORIZED
#
#     HEALTHY != PERMITTED
#
#     HEALTHY != SELECTED


# ===========================================================================
# DEGRADED
# ===========================================================================

# ServiceStatus.DEGRADED means the service remains operational, but
# one or more operating conditions are outside the expected normal
# range.
#
# Examples might eventually include:
#
#
#     - elevated latency
#     - increased error rate
#     - reduced capacity
#     - partial dependency degradation
#
#
# DEGRADED does not automatically mean:
#
#
#     DO NOT USE
#
#
# Example:
#
#
#     Company Cloud LLM
#         PRIMARY
#         DEGRADED
#
#     Company On-Prem LLM
#         FALLBACK
#         HEALTHY
#
#
# Routing may prefer the healthy fallback.
#
#
# But consider:
#
#
#     Company Cloud LLM
#         DEGRADED
#
#     Company On-Prem LLM
#         UNAVAILABLE
#
#     External FM
#         DENIED
#
#
# The degraded service may still remain a candidate depending upon
# routing rules and the nature of the degradation.
#
#
# Therefore:
#
#
#     DEGRADED != UNAVAILABLE
#
#
# The service layer reports the condition.
#
# The routing layer determines its consequence.


# ===========================================================================
# UNAVAILABLE
# ===========================================================================

# ServiceStatus.UNAVAILABLE means Agent 11 has information establishing
# that the reasoning service cannot currently service requests.
#
# Example:
#
#
#     Health Check
#         |
#         v
#     Service Failure
#         |
#         v
#     ServiceStatus.UNAVAILABLE
#
#
# Even if:
#
#
#     Policy              ALLOW
#     Capability          SUFFICIENT
#     Network             AVAILABLE
#
#
# the service is not currently viable.
#
#
# Routing consumes this operational state.
#
# Routing does not create it.


# ===========================================================================
# UNKNOWN
# ===========================================================================

# ServiceStatus.UNKNOWN means Agent 11 cannot currently establish the
# operational condition of the reasoning service.
#
# This is intentionally different from UNAVAILABLE.
#
#
#     UNAVAILABLE
#
#         "We have established that the service cannot currently
#          service requests."
#
#
#     UNKNOWN
#
#         "We cannot currently establish whether the service can
#          service requests."
#
#
# These states should remain distinguishable for:
#
#
#     - telemetry
#     - troubleshooting
#     - auditing
#     - routing analysis
#
#
# Therefore:
#
#
#     UNKNOWN != UNAVAILABLE
#
#     UNKNOWN != HEALTHY
#
#
# Code should not accidentally define acceptable state as merely:
#
#
#     status != UNAVAILABLE
#
#
# because that would allow UNKNOWN to behave like HEALTHY.
#
#
# Prefer explicit handling of known states.


# ===========================================================================
# Role and Status Are Independent
# ===========================================================================

# ModelRole and ServiceStatus describe different dimensions.
#
# Valid combinations include:
#
#
#     PRIMARY + HEALTHY
#
#     PRIMARY + DEGRADED
#
#     PRIMARY + UNAVAILABLE
#
#     PRIMARY + UNKNOWN
#
#     FALLBACK + HEALTHY
#
#     FALLBACK + DEGRADED
#
#     FALLBACK + UNAVAILABLE
#
#     FALLBACK + UNKNOWN
#
#
# Agent 11 intentionally does not create combined Enum values such as:
#
#
#     PRIMARY_HEALTHY
#
#     PRIMARY_UNAVAILABLE
#
#     FALLBACK_HEALTHY
#
#
# because role and operational state are independent facts.
#
#
# Pydantic models will eventually compose these facts into validated
# service state.


# ===========================================================================
# Route Does Not Mean Model
# ===========================================================================

# AIRoute identifies a logical reasoning destination.
#
# It does not identify a specific reasoning service or model.
#
# For example:
#
#
#     AIRoute.COMPANY_ONPREM_LLM
#
#                    |
#                    +---- llama-cluster-a
#                    |
#                    +---- llama-cluster-b
#                    |
#                    +---- future-cluster-c
#
#
# Multiple reasoning services may exist within the same logical route.
#
# Each service may have its own:
#
#
#     - role
#     - status
#     - capabilities
#     - endpoint
#     - model configuration
#
#
# Therefore:
#
#
#     ROUTE != MODEL
#
#     ROUTE != SERVICE


# ===========================================================================
# Vendors and Model Names
# ===========================================================================

# Agent 11 intentionally does not define vendor names or specific
# model products in this Enum module.
#
# Avoid architecture such as:
#
#
#     class ModelProvider(Agent11Enum):
#         AWS = "aws"
#         ANTHROPIC = "anthropic"
#         GOOGLE = "google"
#
#
# or:
#
#
#     class ModelName(Agent11Enum):
#         MODEL_A = "model_a"
#         MODEL_B = "model_b"
#
#
# Providers and specific model identifiers belong in runtime registry
# and configuration data.
#
# This prevents the foundational Agent 11 vocabulary from changing
# every time:
#
#
#     - a provider is added
#     - a provider is removed
#     - a model is upgraded
#     - a model is replaced
#
#
# The architecture should outlive the current vendor landscape.


# ===========================================================================
# Service Status vs Network Status
# ===========================================================================

# ServiceStatus describes the AI reasoning service.
#
# It does not describe the network path to that service.
#
# These states can legitimately differ.
#
#
# Example 1:
#
#
#     Reasoning Service:
#         HEALTHY
#
#     Network Path:
#         UNAVAILABLE
#
#
# The service works.
#
# Agent 11 cannot currently reach it.
#
#
# Example 2:
#
#
#     Reasoning Service:
#         UNAVAILABLE
#
#     Network Path:
#         AVAILABLE
#
#
# The network works.
#
# The reasoning service does not.
#
#
# This separation becomes increasingly important as Agent 11 later
# incorporates:
#
#
#     - VPN state
#     - private connectivity
#     - SD-WAN
#     - BGP
#     - multiple data centers
#
#
# Therefore:
#
#
#     SERVICE STATUS != NETWORK STATUS


# ===========================================================================
# Future Pydantic Composition
# ===========================================================================

# These Enums will eventually be composed by Pydantic models.
#
# A simplified future example may resemble:
#
#
#     class ReasoningService(Agent11BaseModel):
#         service_id: str
#         route: AIRoute
#         role: ModelRole
#         status: ServiceStatus
#
#
# Example:
#
#
#     service = ReasoningService(
#         service_id="company-cloud-reasoning",
#         route=AIRoute.COMPANY_CLOUD_LLM,
#         role=ModelRole.PRIMARY,
#         status=ServiceStatus.HEALTHY,
#     )
#
#
# This produces four separate facts:
#
#
#     SERVICE
#         company-cloud-reasoning
#
#     ROUTE
#         COMPANY_CLOUD_LLM
#
#     ROLE
#         PRIMARY
#
#     STATUS
#         HEALTHY
#
#
# This demonstrates:
#
#
#     ENUMS
#         describe individual controlled facts
#
#
#     PYDANTIC MODELS
#         compose those facts into validated state


# ===========================================================================
# Chewbacca's Architecture Commentary
# ===========================================================================

# Chewbacca has reviewed ModelRole.PRIMARY.
#
#
# Chewbacca:
#
#     "PRIMARY means I have priority."
#
#
# Agent 11:
#
#     It means the reasoning resource is preferred.
#
#
# Chewbacca:
#
#     "Exactly."
#
#
#     "Therefore I have STREET_ACCESS."
#
#
# Agent 11:
#
#     STREET_ACCESS is not a ModelRole.
#
#
# Chewbacca:
#
#     "It should be a legitimate value somewhere."
#
#
# Agent 11 Architecture Review:
#
#     Agreed.
#
#
#     STREET_ACCESS may eventually be legitimate controlled vocabulary
#     within an access, entitlement, or authorization domain.
#
#
#     It does not belong in model_enums.py.
#
#
# Chewbacca then attempts:
#
#
#     role = ModelRole.PRIMARY
#
#     service_status = ServiceStatus.HEALTHY
#
#
# and concludes:
#
#
#     street_access = True
#
#
# Agent 11:
#
#     No.
#
#
# PRIMARY describes preference.
#
# HEALTHY describes operational condition.
#
# Neither establishes authorization.
#
#
# Chewbacca:
#
#     "But both values are positive."
#
#
# Agent 11:
#
#     SECURITY ARCHITECTURE IS NOT SENTIMENT ANALYSIS.
#
#
# Chewbacca then asks whether a FALLBACK service can be used after the
# PRIMARY service becomes unavailable.
#
#
# Agent 11:
#
#     Maybe.
#
#
# Chewbacca:
#
#     "That's not very deterministic."
#
#
# Agent 11:
#
#     The role is deterministic.
#
#     The service state is deterministic.
#
#     The policy decision is deterministic.
#
#     The network state is deterministic.
#
#     Routing composes those facts.
#
#
# Conceptually:
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
# A FALLBACK resource must independently satisfy those requirements.
#
#
# Final ruling:
#
#
#     PRIMARY != ROYAL DECREE
#
#     FALLBACK != POLICY EXCEPTION
#
#     HEALTHY != AUTHORIZED
#
#     UNKNOWN != GOOD ENOUGH
#
#
# Chewbacca has requested STREET_ACCESS again.
#
# The request has been forwarded to the correct architectural layer.
