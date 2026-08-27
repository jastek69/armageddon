"""
Agent 11 Routing Enums
======================

Defines the controlled vocabulary used by the Agent 11 routing layer.

This module answers three fundamental routing questions:

    AIRoute
        "Where could AI reasoning occur?"

    RoutingStatus
        "What did the routing evaluation decide?"

    FallbackStrategy
        "How may routing respond when the preferred route
         cannot be used?"

These are intentionally separate concepts.

Routing Enums do NOT:

    - authenticate users
    - validate credentials
    - perform MFA
    - establish identity
    - determine user permissions
    - classify data
    - create policy
    - determine service health
    - determine network reachability
    - invoke AI models
    - invoke MCP tools
    - perform orchestration

Routing consumes facts and decisions produced by other architectural
layers and determines which viable reasoning destination, if any,
should be selected.

Architecture rules:

    ROUTE != MODEL

    KNOWN ROUTE != PERMITTED ROUTE

    AVAILABLE != VIABLE

    SELECTED != AI RESPONSE SUCCESS

    BLOCKED != NO VIABLE ROUTE

    NULL != NO VIABLE ROUTE

    NO VIABLE ROUTE != ROUTER FAILURE

    FALLBACK IS RE-EVALUATION, NOT POLICY ESCAPE
"""

from .base_enum import Agent11Enum


# ===========================================================================
# AI Route
# ===========================================================================


class AIRoute(Agent11Enum):
    """
    Logical AI reasoning destinations recognized by Agent 11.

    AIRoute describes a routing DOMAIN.

    It does not identify a specific:

        - foundational model
        - LLM
        - model version
        - provider
        - inference endpoint
        - data center
        - GPU cluster

    SEIR-I recognizes three logical reasoning destinations:

    EXTERNAL_FM
        An approved external foundational-model environment.

        This could eventually contain multiple approved models or
        providers.

    COMPANY_CLOUD_LLM
        A company-controlled LLM operating in a cloud environment.

    COMPANY_ONPREM_LLM
        A company-controlled LLM operating within company-managed
        on-premises infrastructure.

    Example:

        route = AIRoute.EXTERNAL_FM

    This means:

        "External foundational-model infrastructure is the logical
         routing destination."

    It does NOT mean:

        "Use Claude."

        "Use Nova."

        "Use Gemini."

        "Use the largest available model."

    Specific model and service selection belongs to the runtime/model
    layer.

    Conceptually:

        AIRoute.EXTERNAL_FM
                |
                v
        Runtime / Model Registry
                |
                +---- Approved FM A
                |
                +---- Approved FM B
                |
                +---- Approved FM C

    Therefore:

        ROUTE != MODEL
    """

    EXTERNAL_FM = "external_fm"
    COMPANY_CLOUD_LLM = "company_cloud_llm"
    COMPANY_ONPREM_LLM = "company_onprem_llm"


# ===========================================================================
# Routing Status
# ===========================================================================


class RoutingStatus(Agent11Enum):
    """
    Describes the final outcome of an Agent 11 routing evaluation.

    SELECTED
        A viable reasoning route was found and selected.

    BLOCKED
        Routing was prevented by policy or security constraints.

    NO_VIABLE_ROUTE
        AI reasoning is required, but no candidate currently satisfies
        all viability requirements.

    NULL
        Agent 11 intentionally determined that no AI invocation and no
        downstream AI response are required.

    These outcomes are deliberately different.

    Conceptually:

                          ROUTING
                             |
             +---------------+---------------+
             |               |               |
             v               v               v
         SELECTED         BLOCKED           NULL
             |
             |
             +---------- NO_VIABLE_ROUTE

    The exact routing path will be implemented by the routing layer.
    This Enum only establishes the controlled vocabulary used to
    describe its outcome.
    """

    SELECTED = "selected"
    BLOCKED = "blocked"
    NO_VIABLE_ROUTE = "no_viable_route"
    NULL = "null"


# ===========================================================================
# Fallback Strategy
# ===========================================================================


class FallbackStrategy(Agent11Enum):
    """
    Defines how routing may respond when a preferred routing candidate
    cannot be used.

    NONE
        Do not attempt another reasoning destination.

    NEXT_VIABLE
        Evaluate the next eligible candidate and select it only if it
        independently satisfies every viability requirement.

    NEXT_VIABLE does NOT mean:

        - next available service
        - next reachable service
        - next cheapest service
        - next fastest service
        - next healthy service
        - ignore policy and keep trying

    Every fallback candidate must independently remain viable.

    Therefore:

        FALLBACK IS RE-EVALUATION, NOT POLICY ESCAPE
    """

    NONE = "none"
    NEXT_VIABLE = "next_viable"


# ===========================================================================
# Route Viability
# ===========================================================================

# A recognized route is not automatically a viable route.
#
# Agent 11 defines route viability conceptually as:
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
# Every condition is required.
#
# This is not a weighted scoring system.
#
# For example:
#
#
#     External FM
#
#     Policy permitted       NO
#     Service capable        YES
#     Service available      YES
#     Path available         YES
#
#
# The result is:
#
#
#     NOT VIABLE
#
#
# It is not:
#
#
#     "75% viable"
#
#
# Security policy is not a weighted average.


# ===========================================================================
# Known Route Does Not Mean Permitted Route
# ===========================================================================

# AIRoute establishes recognized routing destinations.
#
# For example:
#
#
#     route = AIRoute.EXTERNAL_FM
#
#
# means:
#
#
#     "EXTERNAL_FM is a routing destination understood by Agent 11."
#
#
# It does not mean:
#
#
#     "The current request is permitted to use EXTERNAL_FM."
#
#
# A route may simultaneously be:
#
#
#     recognized       YES
#     healthy          YES
#     reachable        YES
#     capable          YES
#     permitted        NO
#
#
# In that case the route must not be selected.
#
#
# Therefore:
#
#
#     KNOWN ROUTE != PERMITTED ROUTE


# ===========================================================================
# SELECTED
# ===========================================================================

# RoutingStatus.SELECTED means Agent 11 found and selected a viable
# reasoning destination.
#
# Example:
#
#
#     COMPANY_ONPREM_LLM
#
#     Policy permitted       YES
#     Service capable        YES
#     Service available      YES
#     Path available         YES
#                            |
#                            v
#                        SELECTED
#
#
# SELECTED describes the routing outcome.
#
# It does not guarantee that the subsequent AI invocation succeeds.
#
# For example:
#
#
#     RoutingStatus.SELECTED
#             |
#             v
#       AI Invocation
#             |
#             v
#     AIResponseStatus.FAILED
#
#
# is entirely possible.
#
#
# Therefore:
#
#
#     SELECTED != AI RESPONSE SUCCESS


# ===========================================================================
# BLOCKED
# ===========================================================================

# RoutingStatus.BLOCKED indicates that policy or security constraints
# prevent routing from proceeding.
#
# Example:
#
#
#     Data Classification
#             E8
#              |
#              v
#       Organization Policy
#              |
#              v
#        External FM
#           DENIED
#              |
#              v
#     RoutingStatus.BLOCKED
#
#
# The routing layer does not create the policy decision.
#
# Conceptually:
#
#
#     POLICY
#         determines permission
#
#     ROUTING
#         respects the result
#
#
# Routing may consume a policy decision such as:
#
#
#     PolicyDecisionStatus.DENY
#
#
# and consequently produce:
#
#
#     RoutingStatus.BLOCKED
#
#
# The router is reporting the routing consequence of policy.
#
# It is not authenticating the user or establishing identity.


# ===========================================================================
# NO VIABLE ROUTE
# ===========================================================================

# RoutingStatus.NO_VIABLE_ROUTE means AI reasoning requires a route,
# but no candidate currently satisfies all viability requirements.
#
# Example:
#
#
#     COMPANY_CLOUD_LLM
#
#     Policy permitted       YES
#     Service capable        YES
#     Service available      YES
#     Path available         NO
#
#
#     COMPANY_ONPREM_LLM
#
#     Policy permitted       YES
#     Service capable        YES
#     Service available      NO
#     Path available         YES
#
#
# Neither candidate is viable.
#
# Therefore:
#
#
#     RoutingStatus.NO_VIABLE_ROUTE
#
#
# This does not necessarily mean the routing system failed.
#
# The router may have:
#
#
#     1. Evaluated the candidates correctly.
#     2. Applied policy correctly.
#     3. Evaluated capabilities correctly.
#     4. Consumed service health correctly.
#     5. Consumed network state correctly.
#     6. Correctly determined that nothing viable remains.
#
#
# Therefore:
#
#
#     NO_VIABLE_ROUTE != ROUTER FAILURE
#
#
# Sometimes refusing to route is evidence that the system is working
# correctly.


# ===========================================================================
# NULL
# ===========================================================================

# RoutingStatus.NULL means Agent 11 intentionally determined that no
# AI reasoning route is required.
#
# This is not a routing failure.
#
# It is an explicit routing decision.
#
# Example:
#
#
#     Incoming Request
#            |
#            v
#     Deterministic logic
#     can handle request?
#            |
#        +---+---+
#        |       |
#       YES      NO
#        |       |
#        v       v
#      NULL    Continue
#              Routing
#
#
# A NULL routing outcome may therefore produce:
#
#
#     routing_status = RoutingStatus.NULL
#
#     AI invocation = None
#
#     AIResponse = None
#
#
# NULL is different from NO_VIABLE_ROUTE.
#
#
#     NULL
#
#         "I do not need a route."
#
#
#     NO_VIABLE_ROUTE
#
#         "I need a route, but none are viable."
#
#
#     BLOCKED
#
#         "Routing must not proceed."
#
#
#     SELECTED
#
#         "I selected a viable route."
#
#
# Therefore:
#
#
#     NULL != NO_VIABLE_ROUTE


# ===========================================================================
# Fallback
# ===========================================================================

# Fallback exists to provide operational resilience.
#
# It does not exist to weaken security policy.
#
# Example:
#
#
#     Preferred Route
#         COMPANY_CLOUD_LLM
#
#             |
#             v
#
#         UNAVAILABLE
#
#             |
#             v
#
#     FallbackStrategy.NEXT_VIABLE
#
#             |
#             v
#
#     COMPANY_ONPREM_LLM
#
#     Policy permitted       YES
#     Service capable        YES
#     Service available      YES
#     Path available         YES
#
#             |
#             v
#
#         SELECTED
#
#
# This is valid fallback behavior.
#
#
# Now consider:
#
#
#     Protected Data
#          E8
#
#           |
#           v
#
#     COMPANY_ONPREM_LLM
#        UNAVAILABLE
#
#           |
#           v
#
#     EXTERNAL_FM
#
#     Policy permitted       NO
#     Service capable        YES
#     Service available      YES
#     Path available         YES
#
#
# EXTERNAL_FM is not viable.
#
# The fact that it is healthy, capable, and reachable does not override
# policy.
#
# If no other candidate survives:
#
#
#     RoutingStatus.NO_VIABLE_ROUTE
#
#
# Agent 11 must never interpret fallback as:
#
#
#     "The secure route failed, so use an insecure route."
#
#
# The architectural invariant is:
#
#
#     FALLBACK MAY REDUCE AVAILABILITY.
#
#     FALLBACK MAY NEVER REDUCE SECURITY POLICY.
#
#
# Or more simply:
#
#
#     FALLBACK IS RE-EVALUATION,
#     NOT POLICY ESCAPE.


# ===========================================================================
# NEXT_VIABLE vs NEXT_AVAILABLE
# ===========================================================================

# Agent 11 intentionally uses:
#
#
#     FallbackStrategy.NEXT_VIABLE
#
#
# rather than:
#
#
#     NEXT_AVAILABLE
#
#
# because availability is only one part of viability.
#
# A service could be:
#
#
#     available        YES
#     healthy          YES
#     reachable        YES
#     capable          YES
#     permitted        NO
#
#
# That service is available.
#
# It is not viable.
#
#
# Therefore:
#
#
#     AVAILABLE != VIABLE


# ===========================================================================
# Routing and Authentication
# ===========================================================================

# This module does not perform authentication.
#
# The broader conceptual separation is:
#
#
#     AUTHENTICATION
#         Who are you, and can you prove it?
#
#             |
#             v
#
#     IDENTITY
#         What identity has been established?
#
#             |
#             v
#
#     POLICY / AUTHORIZATION
#         What is this identity and data permitted to do?
#
#             |
#             v
#
#     CAPABILITY
#         Which services can perform the requested work?
#
#             |
#             v
#
#     SERVICE HEALTH
#         Which services are operational?
#
#             |
#             v
#
#     NETWORK
#         Which destinations are reachable?
#
#             |
#             v
#
#     ROUTING
#         Which remaining viable destination should be selected?
#
#
# Routing may consume the consequences of authentication and policy.
#
# Routing does not perform authentication itself.


# ===========================================================================
# Future RoutingDecision Model
# ===========================================================================

# These Enums will eventually be composed by a Pydantic model such as:
#
#
#     class RoutingDecision(Agent11BaseModel):
#         status: RoutingStatus
#         preferred_route: AIRoute | None = None
#         selected_route: AIRoute | None = None
#         fallback_strategy: FallbackStrategy
#         fallback_used: bool = False
#
#
# Example:
#
#
#     decision = RoutingDecision(
#         status=RoutingStatus.SELECTED,
#         preferred_route=AIRoute.COMPANY_CLOUD_LLM,
#         selected_route=AIRoute.COMPANY_ONPREM_LLM,
#         fallback_strategy=FallbackStrategy.NEXT_VIABLE,
#         fallback_used=True,
#     )
#
#
# This would communicate:
#
#
#     Routing Status:
#         SELECTED
#
#     Preferred Route:
#         COMPANY_CLOUD_LLM
#
#     Actual Route:
#         COMPANY_ONPREM_LLM
#
#     Fallback:
#         USED
#
#
# This illustrates another Agent 11 architecture principle:
#
#
#     ENUMS describe individual controlled facts.
#
#     PYDANTIC MODELS compose those facts into meaningful state.


# ===========================================================================
# Chewbacca's Architecture Commentary
# ===========================================================================

# Chewbacca has reviewed:
#
#
#     FallbackStrategy.NEXT_VIABLE
#
#
# and has interpreted it to mean:
#
#
#     "Keep trying things until somebody says yes."
#
#
# Agent 11:
#
#     No.
#
#
# Chewbacca submits the following routing scenario:
#
#
#     Preferred Route:
#         COMPANY_ONPREM_LLM
#
#     Service Status:
#         UNAVAILABLE
#
#
# Chewbacca:
#
#     "Fine. Use the external foundational model."
#
#
# Agent 11 evaluates:
#
#
#     EXTERNAL_FM
#
#     Service capable        YES
#     Service available      YES
#     Path available         YES
#     Policy permitted       NO
#
#
# Chewbacca:
#
#     "That's three out of four."
#
#
#     "75%."
#
#
#     "Passing grade."
#
#
# Agent 11:
#
#
#     SECURITY POLICY
#     IS NOT A WEIGHTED AVERAGE.
#
#
# A route with:
#
#
#     POLICY PERMITTED = FALSE
#
#
# is not:
#
#
#     75% viable
#
#
# It is:
#
#
#     0% viable
#
#
# Chewbacca then proposes:
#
#
#     "What if I authenticate twice?"
#
#
# Agent 11:
#
#
#     WRONG LAYER.
#
#
# Authentication can establish who Chewbacca is.
#
# It cannot transform:
#
#
#     PolicyDecisionStatus.DENY
#
#
# into:
#
#
#     PolicyDecisionStatus.ALLOW
#
#
# simply because Chewbacca is very enthusiastic about the destination.
#
#
# Chewbacca then proposes:
#
#
#     "Call the prohibited route a fallback."
#
#
# Agent 11:
#
#
#     DENIED + DIFFERENT LABEL
#             =
#         STILL DENIED
#
#
# The final ruling:
#
#
#     FALLBACK CHANGES WHICH VIABLE CANDIDATE WE TRY.
#
#     FALLBACK DOES NOT CHANGE THE DEFINITION OF VIABLE.
#
#
# Chewbacca has appealed the decision to the GPU Allocation Committee.
#
# The GPU Allocation Committee has responded:
#
#
#     RoutingStatus.NULL
