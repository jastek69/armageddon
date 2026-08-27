"""
Agent 11 Base Enum
==================

Provides the common Enum foundation used by Agent 11.

Agent 11 uses Enums to establish controlled vocabulary across the
architecture.

Examples of controlled vocabulary include:

    - AI reasoning levels
    - AI routing destinations
    - routing outcomes
    - policy decisions
    - model/service states
    - network-path types
    - network-path states

The purpose of this base class is intentionally simple:

    Give Agent 11 Enums a common string-based Enum foundation.

Enums define vocabulary.

They do NOT:

    - make policy decisions
    - authorize data movement
    - select AI routes
    - determine service health
    - determine network reachability
    - invoke AI models
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

from enum import StrEnum


class Agent11Enum(StrEnum):
    """
    Common string-based Enum foundation for Agent 11.

    All Agent 11 controlled-vocabulary Enums should normally inherit
    from Agent11Enum.

    Example:

        class AIRoute(Agent11Enum):
            EXTERNAL_FM = "external_fm"
            COMPANY_CLOUD_LLM = "company_cloud_llm"
            COMPANY_ONPREM_LLM = "company_onprem_llm"

    This allows Agent 11 to work with strongly defined Enum members
    inside Python:

        route = AIRoute.COMPANY_ONPREM_LLM

        if route is AIRoute.COMPANY_ONPREM_LLM:
            ...

    rather than passing uncontrolled strings throughout the system:

        route = "company onprem"
        route = "on-prem"
        route = "onprem"
        route = "company_onprem"

    Controlled vocabulary reduces ambiguity and makes invalid states
    easier to detect.


    -------------------------------------------------------------------
    Why StrEnum?
    -------------------------------------------------------------------

    Agent 11 data will eventually cross many boundaries:

        Python
            ↓
        Pydantic
            ↓
        JSON
            ↓
        APIs
            ↓
        MCP
            ↓
        AI Services
            ↓
        Telemetry

    StrEnum allows an Enum member to remain a real Enum inside Python
    while also having a clean string representation suitable for
    serialization.

    For example:

        AIRoute.COMPANY_ONPREM_LLM

    can have the serialized value:

        "company_onprem_llm"

    This is particularly useful when Agent 11 models are serialized
    through Pydantic.


    -------------------------------------------------------------------
    Explicit Values
    -------------------------------------------------------------------

    Agent 11 Enums should normally use explicit string values.

    Preferred:

        COMPANY_ONPREM_LLM = "company_onprem_llm"

    Rather than automatically generating values.

    Enum values may eventually become part of:

        - JSON contracts
        - API contracts
        - MCP messages
        - telemetry records
        - audit records
        - persisted data

    Explicit values therefore make those contracts easier to review,
    understand, and maintain.


    -------------------------------------------------------------------
    Important Architecture Rule
    -------------------------------------------------------------------

    The existence of an Enum member does NOT establish authorization,
    availability, capability, or objective truth.

    For example:

        AIRoute.EXTERNAL_FM

    means:

        "External FM is a recognized routing destination."

    It does NOT mean:

        "External FM is authorized for this request."


    Likewise:

        NetworkPathType.BGP

    means:

        "BGP is a recognized network-path type."

    It does NOT mean:

        "A usable BGP path currently exists."


    Likewise:

        ServiceStatus.HEALTHY

    means:

        "The service has been reported as healthy."

    It does NOT mean:

        "Policy permits this data to be sent to that service."


    Agent 11 deliberately separates these concerns:

        POLICY
            May the request go there?

        SERVICE
            Can the service perform the work?

        NETWORK
            Can the destination currently be reached?

        ROUTING
            Which remaining viable destination should be selected?


    -------------------------------------------------------------------
    Pydantic
    -------------------------------------------------------------------

    Agent11Enum is designed to work naturally with Agent11BaseModel.

    Example:

        class RoutingDecision(Agent11BaseModel):
            route: AIRoute

        decision = RoutingDecision(
            route=AIRoute.COMPANY_ONPREM_LLM,
        )

    Inside Python:

        decision.route is AIRoute.COMPANY_ONPREM_LLM

    Pydantic can then serialize the model for external systems using
    the Enum's string value.

    This allows Agent 11 to maintain controlled vocabulary internally
    while still producing clean machine-readable data externally.
    """

    pass


# ===========================================================================
# Chewbacca's Architecture Commentary
# ===========================================================================

# Chewbacca has reviewed the Agent11Enum architecture and has submitted
# the following proposed controlled vocabulary:
#
#
#     class IdentityType(Agent11Enum):
#         WOOKIEE = "wookiee"
#         INTEGER = "integer"
#
#
# Chewbacca then submitted:
#
#
#     identity = IdentityType.INTEGER
#
#
# and announced:
#
#     "I am now strongly typed."
#
#
# The Architecture Review Board rejected this interpretation.
#
# Defining INTEGER as valid controlled vocabulary establishes only that
# the word "integer" is recognized by the system.
#
# It does not establish that Chewbacca is mathematically an integer.
#
#
# This demonstrates an important Agent 11 principle:
#
#
#     ENUM VALUE != OBJECTIVE REALITY
#
#
# More generally:
#
#
#     RECOGNIZED != AUTHORIZED
#
#     AUTHORIZED != AVAILABLE
#
#     AVAILABLE != REACHABLE
#
#     REACHABLE != PERMITTED
#
#     HEALTHY != AUTHORIZED
#
#     CAPABLE != AUTHORIZED
#
#
# Enums provide vocabulary.
#
# Other architectural layers determine what that vocabulary means
# within a specific request and operational context.
#
#
# Chewbacca has appealed the ruling and requested an integration test:
#
#
#     result = Chewbacca * 7
#
#
# The request has been assigned:
#
#     RoutingStatus.NULL
#
#
# No foundational model resources will be consumed.
