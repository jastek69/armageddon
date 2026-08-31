"""
Agent 11 AI Service Domain Model.

This module defines the stable domain contract used to describe an
operational reasoning service known to Agent 11.

The service model intentionally remains small.

AIService identifies which operational reasoning service exists,
which logical AI model it exposes, and which Agent 11 routing domain
the service belongs to.

Changing operational facts such as service health, endpoint location,
network reachability, policy authorization, cost, and telemetry belong
to other Agent 11 domains.
"""

from pydantic import Field

from ..base_model import Agent11BaseModel
from ..enums.routing_enums import AIRoute


# ==========================================================================
# PART I — AIService DOMAIN CONTRACT
# ==========================================================================
#
# AIService answers one primary architectural question:
#
#
#     HOW IS A LOGICAL AI MODEL MADE AVAILABLE
#     AS AN OPERATIONAL REASONING SERVICE?
#
#
# The progression so far is:
#
#
#     AICapability
#         |
#         | What kind of work can be performed?
#         v
#
#     AIModel
#         |
#         | What logical reasoning model exists?
#         v
#
#     AIService
#         |
#         | What operational service exposes that model?
#         v
#
#     Runtime / Network / Policy / Routing
#
#
# AIService represents the SERVICE.
#
# It does not represent:
#
#
#     - the logical model itself,
#
#     - a deployment,
#
#     - an endpoint,
#
#     - current service health,
#
#     - current network reachability,
#
#     - authorization,
#
#     - credentials,
#
#     - cost,
#
#     - or a routing decision.
#
#
# PRIMARY INVARIANTS:
#
#
#     SERVICE != MODEL
#
#     SERVICE != DEPLOYMENT
#
#     SERVICE != ENDPOINT
#
#     SERVICE != SERVICE STATE
#
#
# ==========================================================================


class AIService(Agent11BaseModel):
    """
    Describes an operational reasoning service known to Agent 11.

    AIService identifies a service that exposes a logical AI model
    through an Agent 11 routing domain.

    It does not describe current service health, network reachability,
    policy authorization, credentials, cost, or route selection.
    """

    # ----------------------------------------------------------------------
    # service_id
    # ----------------------------------------------------------------------
    #
    # service_id identifies THIS SERVICE.
    #
    #
    # Example:
    #
    #
    #     company-security-cloud-primary
    #
    #
    # This is different from:
    #
    #
    #     company-security-llm-v1
    #
    #
    # which may be the model_id of the logical model exposed by the service.
    #
    #
    # Therefore:
    #
    #
    #     SERVICE ID != MODEL ID
    #
    #
    # Example:
    #
    #
    #     model_id
    #         company-security-llm-v1
    #
    #
    #     service_id
    #         company-security-cloud-primary
    #
    #
    # Another service may expose the exact same model:
    #
    #
    #     service_id
    #         company-security-onprem-primary
    #
    #
    #     model_id
    #         company-security-llm-v1
    #
    #
    # The service identity changes.
    #
    # The logical model identity does not.
    #
    #
    # service_id is also NOT:
    #
    #
    #     - an endpoint,
    #
    #     - a hostname,
    #
    #     - an IP address,
    #
    #     - a Kubernetes Service name by necessity,
    #
    #     - a provider API URL,
    #
    #     - or a network route.
    #
    #
    # A service identifier should remain useful even when those operational
    # details change.
    #
    # ----------------------------------------------------------------------

    service_id: str = Field(
        min_length=1,
        description=(
            "Stable machine-readable identifier for the AI service."
        ),
    )

    # ----------------------------------------------------------------------
    # display_name
    # ----------------------------------------------------------------------
    #
    # display_name exists for humans.
    #
    #
    # Example:
    #
    #
    #     service_id:
    #
    #         company-security-onprem-primary
    #
    #
    #     display_name:
    #
    #         Primary On-Prem Security Reasoning Service
    #
    #
    # The distinction remains:
    #
    #
    #     service_id
    #         =
    #     MACHINE IDENTITY
    #
    #
    #     display_name
    #         =
    #     HUMAN PRESENTATION
    #
    #
    # Routing, policy, telemetry, and registry relationships should rely on
    # stable identity rather than human-friendly labels.
    #
    #
    # Therefore:
    #
    #
    #     DISPLAY NAME != SERVICE IDENTITY
    #
    # ----------------------------------------------------------------------

    display_name: str = Field(
        min_length=1,
        description=(
            "Human-readable name of the AI service."
        ),
    )

    # ----------------------------------------------------------------------
    # model_id
    # ----------------------------------------------------------------------
    #
    # An AIService exposes a logical AIModel.
    #
    #
    # But AIService does not contain its own private copy of AIModel.
    #
    #
    # Instead:
    #
    #
    #     AIService
    #         |
    #         | model_id
    #         v
    #     AIModel
    #
    #
    # Example:
    #
    #
    #     AIModel
    #
    #         model_id =
    #             "company-security-llm-v1"
    #
    #
    #     AIService
    #
    #         service_id =
    #             "company-security-cloud-primary"
    #
    #         model_id =
    #             "company-security-llm-v1"
    #
    #
    # This is a REFERENCE relationship.
    #
    #
    #     SERVICE REFERENCES MODEL
    #
    #     SERVICE DOES NOT OWN MODEL DEFINITION
    #
    #
    # Why not simply write:
    #
    #
    #     model: AIModel
    #
    #
    # inside every AIService?
    #
    #
    # Because multiple services may expose the same logical model:
    #
    #
    #                        AIModel
    #             company-security-llm-v1
    #                           ^
    #                           |
    #               +-----------+-----------+
    #               |                       |
    #               | model_id              | model_id
    #               |                       |
    #          AIService                AIService
    #          cloud-primary            onprem-primary
    #
    #
    # Embedding independent model objects into each service risks creating
    # duplicated model definitions.
    #
    #
    # For example:
    #
    #
    #     cloud_service.model.capabilities
    #
    # could accidentally disagree with:
    #
    #
    #     onprem_service.model.capabilities
    #
    #
    # even though both services claim to expose the same logical model.
    #
    #
    # A future registry can resolve:
    #
    #
    #     model_id
    #
    #         ->
    #
    #     AIModel
    #
    #
    # and maintain one authoritative logical model definition.
    #
    #
    # IMPORTANT:
    #
    #
    # Pydantic validates that model_id is a valid non-empty string.
    #
    # Pydantic does NOT prove that the referenced model actually exists.
    #
    #
    # That is a registry / orchestration responsibility.
    #
    #
    # Therefore:
    #
    #
    #     VALID MODEL ID
    #         !=
    #     EXISTING REGISTERED MODEL
    #
    #
    # This is another example of:
    #
    #
    #     VALID TYPE
    #         !=
    #     VALID SEMANTICS
    #
    #
    # and:
    #
    #
    #     DOMAIN MODEL VALIDATION
    #         !=
    #     CROSS-RESOURCE RESOLUTION
    #
    # ----------------------------------------------------------------------

    model_id: str = Field(
        min_length=1,
        description=(
            "Identifier of the logical AI model exposed by the service."
        ),
    )

    # ----------------------------------------------------------------------
    # routing_domain
    # ----------------------------------------------------------------------
    #
    # routing_domain classifies the service into an Agent 11 routing domain.
    #
    #
    # Current SEIR-I domains are represented by AIRoute:
    #
    #
    #     EXTERNAL_FM
    #
    #     COMPANY_CLOUD_LLM
    #
    #     COMPANY_ONPREM_LLM
    #
    #
    # Example:
    #
    #
    #     AIService(
    #         ...
    #         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
    #     )
    #
    #
    # This means:
    #
    #
    #     "This service belongs to the company on-premises
    #      reasoning destination domain."
    #
    #
    # It does NOT mean:
    #
    #
    #     "Agent 11 selected this service."
    #
    #
    # Therefore:
    #
    #
    #     ROUTING DOMAIN != ROUTING DECISION
    #
    #
    # More precisely:
    #
    #
    #     AIService.routing_domain
    #
    #         answers:
    #
    #         WHAT KIND OF DESTINATION IS THIS SERVICE?
    #
    #
    # while:
    #
    #
    #     RoutingDecision
    #
    #         answers:
    #
    #         WHAT DID AGENT 11 ACTUALLY SELECT?
    #
    #
    # A service can belong to:
    #
    #
    #     COMPANY_ONPREM_LLM
    #
    #
    # while never being selected for a particular request.
    #
    #
    # Likewise, belonging to an approved-looking routing domain does not
    # independently establish authorization.
    #
    #
    # Therefore:
    #
    #
    #     ROUTING DOMAIN != AUTHORIZATION
    #
    #
    #     ROUTING DOMAIN != AVAILABILITY
    #
    #
    #     ROUTING DOMAIN != REACHABILITY
    #
    #
    #     ROUTING DOMAIN != SELECTION
    #
    #
    # AIRoute provides controlled vocabulary.
    #
    # It does not perform routing.
    #
    # ----------------------------------------------------------------------

    routing_domain: AIRoute = Field(
        description=(
            "Agent 11 routing domain associated with the AI service."
        ),
    )

    # ----------------------------------------------------------------------
    # description
    # ----------------------------------------------------------------------
    #
    # description exists for human explanation.
    #
    #
    # Example:
    #
    #
    #     "Primary on-premises service exposing the
    #      Company Security Reasoning Model."
    #
    #
    # Agent 11 must NOT infer operational semantics from description text.
    #
    #
    # Bad:
    #
    #
    #     if "secure" in service.description:
    #         allow_e8_data()
    #
    #
    # Chewbacca.
    #
    # No.
    #
    #
    # Policy must come from policy.
    #
    # Service state must come from service state.
    #
    # Network state must come from network state.
    #
    # Routing must come from routing.
    #
    #
    # Therefore:
    #
    #
    #     DESCRIPTION != POLICY
    #
    #
    #     DESCRIPTION != CAPABILITY
    #
    #
    #     DESCRIPTION != SERVICE STATE
    #
    #
    #     DESCRIPTION != ROUTING METADATA
    #
    #
    # Human-readable text is not a control-plane contract.
    #
    # ----------------------------------------------------------------------

    description: str | None = Field(
        default=None,
        description=(
            "Optional human-readable description of the AI service."
        ),
    )


# ==========================================================================
# WHY AIService CURRENTLY HAS NO MODEL VALIDATOR
# ==========================================================================
#
# AIResponse required a model validator because response status creates
# relationships between multiple fields.
#
#
# For example:
#
#
#     SUCCESS
#         requires
#     content
#
#
# AIModel required a model validator because:
#
#
#     duplicate capability types
#
#
# would create an internally ambiguous model definition.
#
#
# AIService currently has no equivalent cross-field semantic invariant.
#
#
# Each field can be validated independently by its type and Field
# constraints.
#
#
# Therefore:
#
#
#     NO VALIDATOR IS REQUIRED.
#
#
# This is intentional.
#
#
# Do not add validators merely because:
#
#
#     "We are using Pydantic."
#
#
# Validators exist to enforce actual domain invariants.
#
#
#     VALIDATION SHOULD REPRESENT A RULE.
#
#     VALIDATION SHOULD NOT BE DECORATION.
#
#
# If a future AIService contract introduces a genuine cross-field
# invariant, add a validator then.
#
# ==========================================================================


# ==========================================================================
# ARCHITECTURAL BOUNDARY ENFORCEMENT
# ==========================================================================
#
# AIService inherits from Agent11BaseModel.
#
#
# Agent11BaseModel configures:
#
#
#     extra="forbid"
#
#
# This means callers cannot quietly turn AIService into a dumping ground
# for unrelated operational concerns.
#
#
# For example, this should fail validation:
#
#
#     AIService(
#         service_id="company-security-onprem-primary",
#         display_name="Primary On-Prem Security Reasoning Service",
#         model_id="company-security-llm-v1",
#         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#
#         endpoint="https://whatever-endpoint.example",
#         healthy=True,
#         e8_allowed=True,
#     )
#
#
# Those fields are not merely "unsupported."
#
# They violate the current AIService domain contract.
#
#
# The correct response is not:
#
#
#     "Pydantic is being annoying."
#
#
# The correct question is:
#
#
#     "WHICH DOMAIN ACTUALLY OWNS THIS FACT?"
#
#
# endpoint
#     -> endpoint / deployment domain
#
#
# healthy
#     -> runtime service-state domain
#
#
# e8_allowed
#     -> policy domain
#
#
# Therefore:
#
#
#     extra="forbid"
#
#
# acts as a small architectural enforcement mechanism.
#
#
# Chewbacca cannot solve an architecture disagreement by adding random
# keyword arguments.
#
# ==========================================================================


# ==========================================================================
# NATIVE PYDANTIC USAGE
# ==========================================================================
#
# AIService intentionally uses normal Pydantic behavior.
#
#
# Create normally:
#
#
#     service = AIService(
#         service_id="company-security-onprem-primary",
#         display_name="Primary On-Prem Security Reasoning Service",
#         model_id="company-security-llm-v1",
#         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#     )
#
#
# Validate external data:
#
#
#     service = AIService.model_validate(service_data)
#
#
# Convert to a Python dictionary:
#
#
#     service.model_dump()
#
#
# Serialize to JSON:
#
#
#     service.model_dump_json()
#
#
# Agent 11 does not hide these operations behind unnecessary wrappers.
#
#
# Students should understand the Pydantic contract directly.
#
#
# Frameworks may later consume AIService.
#
# Frameworks do not define AIService.
#
#
#     PYDANTIC DEFINES THE DOMAIN CONTRACT.
#
#     ORCHESTRATORS USE THE DOMAIN CONTRACT.
#
# ==========================================================================


# ==========================================================================
# EXAMPLE — COMPANY CLOUD SERVICE
# ==========================================================================
#
# Conceptually:
#
#
#     AIModel
#
#         company-security-llm-v1
#
#                 ^
#                 |
#                 | model_id
#                 |
#     AIService
#
#         company-security-cloud-primary
#
#
# Example construction:
#
#
#     cloud_service = AIService(
#         service_id="company-security-cloud-primary",
#         display_name="Primary Cloud Security Reasoning Service",
#         model_id="company-security-llm-v1",
#         routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#         description=(
#             "Primary company-cloud service exposing the "
#             "Company Security Reasoning Model."
#         ),
#     )
#
#
# Notice what is NOT required:
#
#
#     endpoint
#
#     health
#
#     network path
#
#     credentials
#
#     cost
#
#     policy
#
#
# Those facts belong elsewhere.
#
# ==========================================================================


# ==========================================================================
# EXAMPLE — SAME MODEL, DIFFERENT SERVICE
# ==========================================================================
#
# The same logical model may also be exposed through an on-premises
# service:
#
#
#     onprem_service = AIService(
#         service_id="company-security-onprem-primary",
#         display_name="Primary On-Prem Security Reasoning Service",
#         model_id="company-security-llm-v1",
#         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#         description=(
#             "Primary on-premises service exposing the "
#             "Company Security Reasoning Model."
#         ),
#     )
#
#
# We now have:
#
#
#                        AIModel
#
#              company-security-llm-v1
#
#                           ^
#                           |
#               +-----------+-----------+
#               |                       |
#               | model_id              | model_id
#               |                       |
#               |                       |
#        cloud_service             onprem_service
#               |                       |
#               v                       v
#
#     COMPANY_CLOUD_LLM        COMPANY_ONPREM_LLM
#
#
# One logical model.
#
# Two operational services.
#
# Two routing domains.
#
#
# Therefore:
#
#
#     MODEL != SERVICE
#
#
#     MODEL LOCATION != MODEL IDENTITY
#
#
#     SERVICE ROUTING DOMAIN != MODEL IDENTITY
#
# ==========================================================================


# ==========================================================================
# EXAMPLE — EXTERNAL FOUNDATION MODEL SERVICE
# ==========================================================================
#
# AIService can also describe an externally available reasoning service:
#
#
#     external_service = AIService(
#         service_id="external-reasoning-primary",
#         display_name="Primary External Reasoning Service",
#         model_id="external-reasoning-model-v1",
#         routing_domain=AIRoute.EXTERNAL_FM,
#         description=(
#             "Primary externally hosted reasoning service."
#         ),
#     )
#
#
# Again:
#
#
#     EXTERNAL_FM
#
#
# describes the service's routing domain.
#
# It does not mean:
#
#
#     - the service is authorized for every request,
#
#     - the service is currently healthy,
#
#     - the service is reachable,
#
#     - or the router selected it.
#
#
# Those decisions happen elsewhere.
#
# ==========================================================================


# ==========================================================================
# EXAMPLE — WHAT AIService SHOULD REJECT
# ==========================================================================
#
# This is NOT our service contract:
#
#
#     bad_service = AIService(
#         service_id="chewbacca-super-ai",
#         display_name="Chewbacca Super AI",
#         model_id="company-security-llm-v1",
#         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#
#         endpoint="https://whatever-endpoint.example",
#         healthy=True,
#         available=True,
#         latency_ms=4,
#         cost_per_token=0.000001,
#         e8_allowed=True,
#         password="woof123",
#         bgp_route="definitely-a-route",
#     )
#
#
# With:
#
#
#     extra="forbid"
#
#
# Agent 11 rejects these extra fields.
#
#
# That rejection protects domain boundaries:
#
#
#     endpoint
#         -> endpoint / deployment
#
#     healthy
#         -> service state
#
#     available
#         -> service state
#
#     latency_ms
#         -> runtime / telemetry
#
#     cost_per_token
#         -> economics / usage / routing metadata
#
#     e8_allowed
#         -> policy
#
#     password
#         -> secrets / identity
#
#     bgp_route
#         -> network
#
#
# Chewbacca has attempted to model the entire AI Control Plane
# with one Pydantic object.
#
#
# The Pydantic object has declined.
#
# ==========================================================================


# ==========================================================================
# PART I — RESPONSIBILITY BOUNDARY
# ==========================================================================
#
# AIService knows:
#
#
#     WHO AM I?
#
#         service_id
#
#
#     WHAT SHOULD HUMANS CALL ME?
#
#         display_name
#
#
#     WHICH LOGICAL MODEL DO I EXPOSE?
#
#         model_id
#
#
#     WHICH AGENT 11 ROUTING DOMAIN DO I BELONG TO?
#
#         routing_domain
#
#
#     IS THERE OPTIONAL HUMAN EXPLANATION?
#
#         description
#
#
# AIService does NOT know:
#
#
#     WHERE EXACTLY AM I DEPLOYED?
#
#     WHAT IS MY ENDPOINT?
#
#     AM I HEALTHY RIGHT NOW?
#
#     AM I REACHABLE RIGHT NOW?
#
#     IS THIS REQUEST AUTHORIZED TO USE ME?
#
#     WHAT DOES USING ME COST RIGHT NOW?
#
#     WHAT CREDENTIAL SHOULD BE USED?
#
#     WHICH NETWORK PATH REACHES ME?
#
#     DID THE ROUTER SELECT ME?
#
#
# Those questions have different owners.
#
# ==========================================================================


# ==========================================================================
# PART I — FINAL INVARIANTS
# ==========================================================================
#
#     SERVICE != MODEL
#
#
#     SERVICE != DEPLOYMENT
#
#
#     SERVICE != ENDPOINT
#
#
#     SERVICE != SERVICE STATE
#
#
#     SERVICE ID != MODEL ID
#
#
#     DISPLAY NAME != SERVICE IDENTITY
#
#
#     SERVICE REFERENCES MODEL
#
#
#     SERVICE DOES NOT OWN MODEL DEFINITION
#
#
#     VALID MODEL ID != EXISTING REGISTERED MODEL
#
#
#     DOMAIN VALIDATION != CROSS-RESOURCE RESOLUTION
#
#
#     ROUTING DOMAIN != ROUTING DECISION
#
#
#     ROUTING DOMAIN != AUTHORIZATION
#
#
#     ROUTING DOMAIN != AVAILABILITY
#
#
#     ROUTING DOMAIN != REACHABILITY
#
#
#     ROUTING DOMAIN != SELECTION
#
#
#     DESCRIPTION != POLICY
#
#
#     DESCRIPTION != CAPABILITY
#
#
#     DESCRIPTION != SERVICE STATE
#
#
#     HUMAN-READABLE TEXT != CONTROL-PLANE CONTRACT
#
#
#     VALIDATION SHOULD REPRESENT A RULE
#
#
#     VALIDATION SHOULD NOT BE DECORATION
#
#
# ==========================================================================
# END PART I
# ==========================================================================

# ==========================================================================
# PART II — AIService OPERATIONAL BOUNDARIES
# ==========================================================================
#
# Part I answered:
#
#
#     WHAT OPERATIONAL REASONING SERVICE EXISTS?
#
#
# Part II asks:
#
#
#     WHAT OPERATIONAL FACTS SURROUND THAT SERVICE
#     WITHOUT BECOMING PART OF ITS IDENTITY?
#
#
# An AI service participates in a changing operational environment:
#
#
#                         AIService
#                             |
#          +------------------+------------------+
#          |                  |                  |
#          v                  v                  v
#      Deployment          Endpoint        Service State
#          |                  |                  |
#          v                  v                  v
#       Location         Addressability      Availability
#                             |
#                             v
#                       Network Path
#
#
# These concepts are related.
#
# They are not interchangeable.
#
#
# PRIMARY INVARIANTS:
#
#
#     SERVICE != DEPLOYMENT
#
#     SERVICE != ENDPOINT
#
#     SERVICE != SERVICE STATE
#
#     ENDPOINT != NETWORK PATH
#
#     SERVICE AVAILABILITY != NETWORK REACHABILITY
#
#
# ==========================================================================


# ==========================================================================
# SERVICE IDENTITY != OPERATIONAL OBSERVATION
# ==========================================================================
#
# AIService describes a relatively stable service identity.
#
#
# Operational observations may change continuously.
#
#
# Example:
#
#
#     10:01
#
#         company-security-onprem-primary
#         AVAILABLE
#
#
#     10:02
#
#         company-security-onprem-primary
#         DEGRADED
#
#
#     10:04
#
#         company-security-onprem-primary
#         UNAVAILABLE
#
#
#     10:05
#
#         company-security-onprem-primary
#         AVAILABLE
#
#
# Four observations occurred.
#
#
# We did NOT create four AIService objects representing four different
# logical services.
#
#
# The service identity remained:
#
#
#     company-security-onprem-primary
#
#
# What changed was:
#
#
#     OBSERVED SERVICE STATE
#
#
# Therefore:
#
#
#     SERVICE IDENTITY != SERVICE STATE
#
#
# and:
#
#
#     CHANGING STATE
#         DOES NOT REQUIRE
#     CHANGING IDENTITY
#
#
# This distinction becomes essential when Agent 11 begins receiving
# health checks, telemetry, availability signals, and runtime events.
#
# ==========================================================================


# ==========================================================================
# WHY AIService DOES NOT CONTAIN healthy: bool
# ==========================================================================
#
# It may be tempting to add:
#
#
#     healthy: bool
#
#
# But what does:
#
#
#     healthy = False
#
#
# actually mean?
#
#
#     - completely unavailable?
#
#     - partially degraded?
#
#     - responding slowly?
#
#     - failing health checks?
#
#     - overloaded?
#
#     - refusing new requests?
#
#     - returning invalid responses?
#
#     - unknown because telemetry is unavailable?
#
#
# Those conditions are not equivalent.
#
#
# Agent 11 already anticipates richer operational states such as:
#
#
#     AVAILABLE
#
#     DEGRADED
#
#     UNAVAILABLE
#
#     UNKNOWN
#
#
# Therefore:
#
#
#     healthy: bool
#
#
# would prematurely collapse a state machine into one bit.
#
#
# Teaching principle:
#
#
#     DO NOT ADD A BOOLEAN
#     BEFORE YOU UNDERSTAND THE STATE MACHINE.
#
#
# Current service state should eventually be represented by a dedicated
# operational-state contract or runtime observation.
#
#
# It does not belong in the stable AIService identity contract.
#
# ==========================================================================


# ==========================================================================
# SERVICE STATE != NETWORK STATE
# ==========================================================================
#
# A reasoning service and the network path used to reach it have
# independent operational states.
#
#
# Example:
#
#
#     AI SERVICE
#
#         AVAILABLE
#
#
#     NETWORK PATH
#
#         UNAVAILABLE
#
#
# The service may be functioning perfectly.
#
# Agent 11 simply cannot reach it through the required path.
#
#
# The reverse is also possible:
#
#
#     AI SERVICE
#
#         UNAVAILABLE
#
#
#     NETWORK PATH
#
#         AVAILABLE
#
#
# Packets can reach the destination.
#
# The reasoning service itself is not functioning.
#
#
# Therefore:
#
#
#     SERVICE AVAILABLE != NETWORK AVAILABLE
#
#
#     SERVICE HEALTH != NETWORK HEALTH
#
#
#     REACHABLE != HEALTHY
#
#
#     HEALTHY != REACHABLE
#
#
# These conditions must remain independently observable.
#
# ==========================================================================


# ==========================================================================
# SERVICE != ENDPOINT
# ==========================================================================
#
# An endpoint answers:
#
#
#     WHERE / HOW CAN THIS SERVICE BE ADDRESSED?
#
#
# AIService answers:
#
#
#     WHICH OPERATIONAL REASONING SERVICE IS THIS?
#
#
# Those are different questions.
#
#
# Consider:
#
#
#     AIService
#
#         company-security-onprem-primary
#
#
# Today it may be addressed through:
#
#
#     https://ai-primary.internal.example
#
#
# Tomorrow infrastructure changes and it becomes:
#
#
#     https://ai-prod.internal.example
#
#
# The endpoint changed.
#
# The service identity did not necessarily change.
#
#
# Therefore:
#
#
#     ENDPOINT CHANGE
#         DOES NOT NECESSARILY MEAN
#     SERVICE IDENTITY CHANGE
#
#
# and:
#
#
#     SERVICE ID != ENDPOINT
#
#
# This is why AIService deliberately does not contain:
#
#
#     endpoint="https://whatever-endpoint.example"
#
#
# Chewbacca may know where the service lives today.
#
# That does not make the address the service's identity.
#
# ==========================================================================


# ==========================================================================
# WHY AIService DOES NOT CURRENTLY CONTAIN endpoint: AnyUrl
# ==========================================================================
#
# Pydantic provides excellent URL validation types.
#
#
# We could technically write:
#
#
#     endpoint: AnyUrl
#
#
# But type safety cannot repair an incorrect domain boundary.
#
#
# Before choosing a type, first ask:
#
#
#     DOES THIS FACT BELONG TO THIS OBJECT?
#
#
# Even if endpoint belonged directly to AIService, not every future
# reasoning service is guaranteed to be represented by an ordinary
# HTTP URL.
#
#
# Future service access mechanisms may include:
#
#
#     - HTTPS APIs,
#
#     - gRPC,
#
#     - Kubernetes service discovery,
#
#     - private service endpoints,
#
#     - local inference processes,
#
#     - Unix sockets,
#
#     - provider-specific invocation APIs,
#
#     - or other mechanisms.
#
#
# Therefore:
#
#
#     VALID URL TYPE
#         !=
#     CORRECT DOMAIN MODEL
#
#
# Pydantic helps us enforce a contract.
#
# Architecture determines what the contract should be.
#
# ==========================================================================


# ==========================================================================
# ENDPOINT != NETWORK PATH
# ==========================================================================
#
# Even after Agent 11 knows the endpoint, it still does not necessarily
# know how that endpoint can be reached.
#
#
# Example:
#
#
#     AIService
#         |
#         v
#     Endpoint
#         |
#         +-- ai-primary.internal.example
#         |
#         v
#     Network Path
#         |
#         +-- PRIVATE_LINK
#
#
# Another environment might reach the same logical service through:
#
#
#     Network Path
#         |
#         +-- VPN
#
#
# Future SEIR-II environments may introduce:
#
#
#     SD_WAN
#
#     BGP
#
#     multiple redundant paths
#
#
# Therefore:
#
#
#     ENDPOINT
#         =
#     WHERE / HOW THE SERVICE IS ADDRESSED
#
#
#     NETWORK PATH
#         =
#     HOW TRAFFIC REACHES THAT DESTINATION
#
#
# These are different facts.
#
#
#     ENDPOINT != NETWORK PATH
#
#
#     ADDRESSABLE != REACHABLE
#
# ==========================================================================


# ==========================================================================
# BGP DOES NOT BELONG IN AIService
# ==========================================================================
#
# Future SEIR-II networking may allow Agent 11 to consume information
# derived from BGP or SD-WAN systems.
#
#
# BGP may help answer:
#
#
#     HOW DO PACKETS REACH THE APPROVED
#     INFERENCE DESTINATION?
#
#
# AIService answers:
#
#
#     WHICH REASONING SERVICE IS THIS?
#
#
# Therefore:
#
#
#     SERVICE != BGP ROUTE
#
#
#     AI ROUTING != NETWORK ROUTING
#
#
# Agent 11 may eventually combine both:
#
#
#     AI ROUTING
#         |
#         | Which reasoning destination?
#         v
#     SELECTED AI SERVICE
#         |
#         v
#     NETWORK ROUTING
#         |
#         | How do packets reach it?
#         v
#     BGP / SD-WAN / OTHER PATH
#
#
# BGP information belongs to the network domain.
#
#
# Adding:
#
#
#     bgp_route="whatever"
#
#
# to AIService does not make Agent 11 network-aware.
#
# It makes AIService confused.
#
# ==========================================================================


# ==========================================================================
# SERVICE != DEPLOYMENT
# ==========================================================================
#
# A service describes an operational reasoning resource.
#
# A deployment describes how or where that service is instantiated.
#
#
# Conceptually:
#
#
#                         AIModel
#                            |
#                            v
#                        AIService
#                            |
#              +-------------+-------------+
#              |                           |
#              v                           v
#        Deployment A                Deployment B
#
#
# Future deployments may differ by:
#
#
#     - region,
#
#     - availability zone,
#
#     - data center,
#
#     - Kubernetes cluster,
#
#     - inference runtime,
#
#     - accelerator configuration,
#
#     - scaling configuration,
#
#     - or infrastructure provider.
#
#
# These are deployment concerns.
#
#
# Therefore:
#
#
#     SERVICE != DEPLOYMENT
#
#
#     SERVICE ID != DEPLOYMENT ID
#
#
#     SERVICE ROUTING DOMAIN != DEPLOYMENT LOCATION
#
#
# SEIR-I does not yet require a dedicated deployment model.
#
# Part III preserves that expansion point for SEIR-II.
#
# ==========================================================================


# ==========================================================================
# WHY AIService DOES NOT CURRENTLY CONTAIN region
# ==========================================================================
#
# It may be tempting to write:
#
#
#     region="us-east-1"
#
#
# But region immediately raises additional questions:
#
#
#     Which cloud?
#
#     Which provider?
#
#     Which account?
#
#     Which subscription?
#
#     Which project?
#
#     Which data center?
#
#     What about on-premises services?
#
#     What about multi-region services?
#
#
# A provider-specific deployment concept should not casually leak into
# the core AIService contract.
#
#
# Therefore:
#
#
#     SERVICE != REGION
#
#
#     ROUTING DOMAIN != CLOUD REGION
#
#
# Deployment topology should receive its own domain representation when
# Agent 11 actually needs it.
#
# ==========================================================================


# ==========================================================================
# AVAILABLE != AUTHORIZED
# ==========================================================================
#
# Suppose:
#
#
#     company-security-cloud-primary
#
#
# is:
#
#
#     AVAILABLE
#
#
# and:
#
#
#     REACHABLE
#
#
# That still does NOT mean the current request may use it.
#
#
# Example:
#
#
#     SERVICE
#         AVAILABLE
#
#     NETWORK
#         AVAILABLE
#
#     POLICY
#         DENY
#
#
# Result:
#
#
#     DO NOT USE THE SERVICE.
#
#
# Likewise:
#
#
#     SERVICE
#         AVAILABLE
#
#     NETWORK
#         AVAILABLE
#
#     POLICY
#         ALLOW
#
#
# still does not automatically mean:
#
#
#     SELECTED
#
#
# because another viable service may be preferred by routing.
#
#
# Therefore:
#
#
#     AVAILABLE != AUTHORIZED
#
#
#     REACHABLE != AUTHORIZED
#
#
#     AUTHORIZED != SELECTED
#
#
#     AVAILABLE != SELECTED
#
#
# Operational availability can never override security policy.
#
# ==========================================================================


# ==========================================================================
# AUTHORIZED != AVAILABLE
# ==========================================================================
#
# Policy may say:
#
#
#     COMPANY_ONPREM_LLM
#
#         ALLOWED
#
#
# while the service state says:
#
#
#     company-security-onprem-primary
#
#         UNAVAILABLE
#
#
# Authorization does not create availability.
#
#
# Likewise:
#
#
#     POLICY ALLOW
#
#
# cannot create a network path.
#
#
# Therefore:
#
#
#     AUTHORIZED != AVAILABLE
#
#
#     AUTHORIZED != REACHABLE
#
#
#     POLICY DOES NOT CREATE INFRASTRUCTURE
#
#
#     NETWORK DOES NOT CREATE AUTHORIZATION
#
#
# Each domain contributes an independent fact to the viability decision.
#
# ==========================================================================


# ==========================================================================
# CAPABLE != AVAILABLE
# ==========================================================================
#
# The model exposed by an AIService may be fully capable of performing
# the requested reasoning task.
#
#
# Example:
#
#
#     SECURITY_ANALYSIS
#
#         HEAVY
#
#
# Capability matching may conclude:
#
#
#     CAPABLE
#
#
# But the service may currently be:
#
#
#     UNAVAILABLE
#
#
# Therefore:
#
#
#     CAPABLE != AVAILABLE
#
#
# A resource does not lose its conceptual capability merely because it
# is temporarily offline.
#
#
# Likewise:
#
#
#     UNAVAILABLE
#
#
# does not mean:
#
#
#     INCAPABLE
#
#
# Capability describes what work the reasoning resource can perform.
#
# Availability describes whether the operational service can currently
# provide access to that work.
#
# ==========================================================================


# ==========================================================================
# SEIR-I ASSUMPTION — SERVICE CAPABILITY
# ==========================================================================
#
# SEIR-I currently treats the service as exposing the capabilities of
# its referenced AIModel.
#
#
# Conceptually:
#
#
#     AIService
#         |
#         | model_id
#         v
#     AIModel
#         |
#         v
#     AICapability
#
#
# Therefore AIService does NOT currently duplicate:
#
#
#     capabilities: list[AICapability]
#
#
# This avoids maintaining two capability definitions before the
# architecture actually needs them.
#
#
# SEIR-II should revisit this assumption.
#
#
# A future deployment may expose only a subset of the logical model's
# capabilities.
#
#
# Example:
#
#
#     AIModel
#
#         SECURITY_ANALYSIS
#             STANDARD
#             HEAVY
#
#
#     Cloud Service
#
#         SECURITY_ANALYSIS
#             STANDARD
#
#
#     On-Prem Service
#
#         SECURITY_ANALYSIS
#             STANDARD
#             HEAVY
#
#
# Therefore the future architecture must preserve:
#
#
#     MODEL CAPABILITY
#         !=
#     DEPLOYED SERVICE CAPABILITY
#
#
# But SEIR-I does not need to implement that distinction yet.
#
#
#     FUTURE-AWARE != FUTURE-BLOATED
#
# ==========================================================================


# ==========================================================================
# SERVICE DESCRIPTION != SERVICE CREDENTIAL
# ==========================================================================
#
# AIService must never become a container for authentication secrets.
#
#
# Do NOT add:
#
#
#     api_key
#
#     password
#
#     access_token
#
#     secret
#
#     aws_access_key
#
#     private_key
#
#
# to this domain model.
#
#
# A future service definition may need to describe HOW authentication
# should occur.
#
#
# That is different from storing the credential itself.
#
#
# Future architecture may distinguish:
#
#
#     AIService
#         |
#         v
#     Authentication Requirement
#         |
#         v
#     Credential Reference
#         |
#         v
#     Secret Store
#
#
# Therefore:
#
#
#     SERVICE != CREDENTIAL
#
#
#     AUTHENTICATION METHOD != CREDENTIAL VALUE
#
#
#     CREDENTIAL REFERENCE != CREDENTIAL VALUE
#
#
# Secrets belong in an appropriate identity / secrets system.
#
# They do not belong in AIService.
#
#
# If Chewbacca commits:
#
#
#     password="woof123"
#
#
# to service.py, our architectural problem is no longer theoretical.
#
# ==========================================================================


# ==========================================================================
# MODEL PROVIDER != SERVICE OPERATOR
# ==========================================================================
#
# AIModel already records model provenance through its provider concept.
#
#
# That does not necessarily identify who operates the service.
#
#
# Example:
#
#
#     MODEL
#
#         Open model
#
#
#     MODEL PROVIDER
#
#         External organization
#
#
#     SERVICE
#
#         company-security-onprem-primary
#
#
#     SERVICE OPERATOR
#
#         Company AI Platform Team
#
#
#     ROUTING DOMAIN
#
#         COMPANY_ONPREM_LLM
#
#
# Therefore:
#
#
#     MODEL PROVIDER != SERVICE OPERATOR
#
#
#     MODEL PROVIDER != DEPLOYMENT LOCATION
#
#
#     MODEL PROVIDER != ROUTING DOMAIN
#
#
# SEIR-I does not yet require a service-operator field.
#
# Do not add an ambiguous second:
#
#
#     provider
#
#
# field to AIService merely because the word seems convenient.
#
# ==========================================================================


# ==========================================================================
# SERVICE != PRICE
# ==========================================================================
#
# Cost may eventually influence routing.
#
#
# But current service economics may depend on:
#
#
#     - provider pricing,
#
#     - token usage,
#
#     - reserved capacity,
#
#     - GPU amortization,
#
#     - internal chargeback,
#
#     - time,
#
#     - region,
#
#     - workload,
#
#     - or organizational accounting.
#
#
# Therefore:
#
#
#     AIService
#
# should not currently contain:
#
#
#     cost_per_token
#
#
# as though service identity and current economics were the same thing.
#
#
# Future routing may consume cost information from an economics,
# telemetry, usage, or service-metadata domain.
#
#
#     SERVICE != PRICE
#
#
#     CHEAPER != PERMITTED
#
#
#     CHEAPER != VIABLE
#
#
#     CHEAPER != SELECTED
#
#
# Cost may influence preference.
#
# Cost may never erase policy requirements.
#
# ==========================================================================


# ==========================================================================
# SERVICE != CURRENT PERFORMANCE OBSERVATION
# ==========================================================================
#
# It may be tempting to add:
#
#
#     latency_ms: int
#
#
# But latency is generally an observation.
#
#
# For example:
#
#
#     10:01    42 ms
#
#     10:02    51 ms
#
#     10:03    380 ms
#
#     10:04    47 ms
#
#
# The AIService did not change identity four times.
#
#
# Telemetry changed.
#
#
# Therefore:
#
#
#     SERVICE != LATENCY OBSERVATION
#
#
#     SERVICE IDENTITY != TELEMETRY
#
#
# Future routing may use latency.
#
# That does not make latency part of the stable service contract.
#
# ==========================================================================


# ==========================================================================
# FUTURE RUNTIME STATE SHOULD BE AN OBSERVATION
# ==========================================================================
#
# When Agent 11 introduces service-state models, state should eventually
# answer more than:
#
#
#     WHAT IS THE STATE?
#
#
# Mature operational reasoning may also need:
#
#
#     WHEN WAS IT OBSERVED?
#
#     WHO / WHAT OBSERVED IT?
#
#     HOW FRESH IS THE OBSERVATION?
#
#
# Conceptually:
#
#
#     ServiceStateObservation
#         |
#         +-- service_id
#         |
#         +-- state
#         |
#         +-- observed_at
#         |
#         +-- source
#
#
# Why?
#
#
# Because:
#
#
#     AVAILABLE
#
#
# observed thirty minutes ago is not necessarily equivalent to:
#
#
#     AVAILABLE
#
#
# observed two seconds ago.
#
#
# Therefore:
#
#
#     STATE WITHOUT TIME
#         MAY BECOME
#     STALE STATE
#
#
# and:
#
#
#     STALE OBSERVATION != CURRENT TRUTH
#
#
# SEIR-I does not need this model yet.
#
# Preserve the architectural opening for it.
#
# ==========================================================================


# ==========================================================================
# UNKNOWN != UNAVAILABLE
# ==========================================================================
#
# Suppose Agent 11 cannot obtain current health information.
#
#
# That does not prove:
#
#
#     UNAVAILABLE
#
#
# It establishes:
#
#
#     UNKNOWN
#
#
# Those states have different meanings.
#
#
#     UNAVAILABLE
#
#         =
#     We have evidence the service cannot currently provide service.
#
#
#     UNKNOWN
#
#         =
#     We do not currently have sufficient evidence to establish state.
#
#
# Therefore:
#
#
#     UNKNOWN != UNAVAILABLE
#
#
# Telemetry and routing should preserve that distinction.
#
#
# Security-sensitive routing may still fail closed when required.
#
# But:
#
#
#     FAIL-CLOSED BEHAVIOR
#         !=
#     REWRITING UNKNOWN AS UNAVAILABLE
#
#
# Decision behavior and observed truth are different concepts.
#
# ==========================================================================


# ==========================================================================
# DEGRADED != UNAVAILABLE
# ==========================================================================
#
# A DEGRADED service may still be capable of serving requests.
#
#
# Example:
#
#
#     AVAILABLE
#         normal operation
#
#
#     DEGRADED
#         reduced capacity or impaired performance
#
#
#     UNAVAILABLE
#         cannot currently provide the required service
#
#
# Whether a degraded service remains viable may depend on future routing
# requirements.
#
#
# For example:
#
#
#     LIGHT reasoning request
#
# may tolerate a degraded service while:
#
#
#     HEAVY reasoning request
#
# may not.
#
#
# That decision belongs to routing / operational policy.
#
#
# AIService itself should not decide:
#
#
#     "DEGRADED means reject."
#
#
# Therefore:
#
#
#     STATE DESCRIPTION != ROUTING BEHAVIOR
#
#
#     DEGRADED != AUTOMATICALLY UNUSABLE
#
# ==========================================================================


# ==========================================================================
# SEIR-II — FAILURE DOMAINS
# ==========================================================================
#
# Multiple services or deployments may appear redundant while sharing a
# common failure domain.
#
#
# Example:
#
#
#     Service A
#         |
#         +-- Data Center 1
#
#
#     Service B
#         |
#         +-- Data Center 1
#
#
# Two service identifiers do not automatically provide infrastructure
# redundancy.
#
#
# Likewise:
#
#
#     Service A -> Cloud Provider A
#
#     Service B -> Cloud Provider A
#
#
# may still share important dependencies.
#
#
# Future fallback reasoning may need to understand:
#
#
#     - provider failure domains,
#
#     - region failure domains,
#
#     - cluster failure domains,
#
#     - network failure domains,
#
#     - identity-provider dependencies,
#
#     - and shared model-serving infrastructure.
#
#
# Therefore:
#
#
#     MULTIPLE SERVICES != INDEPENDENT SERVICES
#
#
#     MULTIPLE ENDPOINTS != TRUE REDUNDANCY
#
#
# SEIR-II should model dependency and failure-domain relationships when
# resilient multi-model routing requires them.
#
# ==========================================================================


# ==========================================================================
# SERVICE != FALLBACK STRATEGY
# ==========================================================================
#
# AIService should not contain:
#
#
#     fallback_service_id
#
#
# or:
#
#
#     fallback_route
#
#
# merely because another service could be used if this one fails.
#
#
# Fallback is a routing behavior.
#
#
# Conceptually:
#
#
#     Service A
#         |
#         X unavailable
#         |
#         v
#     ROUTING / FALLBACK
#         |
#         v
#     independently evaluate
#     remaining candidates
#
#
# The fallback candidate must still satisfy:
#
#
#     POLICY
#
#     CAPABILITY
#
#     SERVICE AVAILABILITY
#
#     NETWORK AVAILABILITY
#
#
# Therefore:
#
#
#     FALLBACK != IGNORE POLICY
#
#
#     FALLBACK != STATIC SERVICE POINTER
#
#
#     NEXT_VIABLE
#         =
#     RE-EVALUATE VIABILITY
#
#
# AIService describes a service.
#
# Routing decides what to do when that service cannot be used.
#
# ==========================================================================


# ==========================================================================
# SERVICE VIABILITY EXAMPLES
# ==========================================================================
#
# Example A:
#
#
#     CAPABLE        YES
#     POLICY         ALLOW
#     SERVICE        AVAILABLE
#     NETWORK        AVAILABLE
#
#     RESULT:
#
#         VIABLE CANDIDATE
#
#
# --------------------------------------------------------------------------
#
# Example B:
#
#
#     CAPABLE        YES
#     POLICY         DENY
#     SERVICE        AVAILABLE
#     NETWORK        AVAILABLE
#
#     RESULT:
#
#         NOT VIABLE
#
#
# --------------------------------------------------------------------------
#
# Example C:
#
#
#     CAPABLE        YES
#     POLICY         ALLOW
#     SERVICE        UNAVAILABLE
#     NETWORK        AVAILABLE
#
#     RESULT:
#
#         NOT VIABLE
#
#
# --------------------------------------------------------------------------
#
# Example D:
#
#
#     CAPABLE        YES
#     POLICY         ALLOW
#     SERVICE        AVAILABLE
#     NETWORK        UNAVAILABLE
#
#     RESULT:
#
#         NOT VIABLE
#
#
# --------------------------------------------------------------------------
#
# Example E:
#
#
#     CAPABLE        NO
#     POLICY         ALLOW
#     SERVICE        AVAILABLE
#     NETWORK        AVAILABLE
#
#     RESULT:
#
#         NOT VIABLE
#
#
# --------------------------------------------------------------------------
#
# This gives Agent 11 its fundamental rule:
#
#
#     VIABLE ROUTE
#         =
#     POLICY PERMITTED
#         +
#     SERVICE CAPABLE
#         +
#     SERVICE AVAILABLE
#         +
#     PATH AVAILABLE
#
#
# No single domain may manufacture the other three facts.
#
# ==========================================================================


# ==========================================================================
# REACHABLE != TRUSTED
# ==========================================================================
#
# Network discovery may determine that Agent 11 can reach:
#
#
#     some-ai-service.example
#
#
# That establishes a network fact.
#
#
# It does NOT establish:
#
#
#     - model identity,
#
#     - service registration,
#
#     - organizational trust,
#
#     - policy authorization,
#
#     - or permission to send data.
#
#
# Therefore:
#
#
#     DISCOVERED != REGISTERED
#
#
#     REGISTERED != TRUSTED
#
#
#     REACHABLE != AUTHORIZED
#
#
#     REACHABLE != TRUSTED
#
#
# Network connectivity must never become an accidental authorization
# mechanism.
#
#
#     "I can connect to it."
#
#
# is not equivalent to:
#
#
#     "I am allowed to send company data to it."
#
# ==========================================================================


# ==========================================================================
# PART II — OPERATIONAL RESPONSIBILITY MAP
# ==========================================================================
#
# AIService:
#
#     WHICH OPERATIONAL REASONING SERVICE EXISTS?
#
#
# Deployment:
#
#     WHERE / HOW IS THAT SERVICE INSTANTIATED?
#
#
# Endpoint:
#
#     HOW IS THAT DEPLOYMENT ADDRESSED?
#
#
# Service State:
#
#     CAN THE REASONING SERVICE CURRENTLY OPERATE?
#
#
# Network Path:
#
#     CAN TRAFFIC CURRENTLY REACH THE DESTINATION?
#
#
# Policy:
#
#     MAY THIS REQUEST USE THE DESTINATION?
#
#
# Telemetry:
#
#     WHAT HAS BEEN OBSERVED ABOUT OPERATION?
#
#
# Routing:
#
#     WHICH VIABLE DESTINATION SHOULD BE SELECTED?
#
#
# Fallback:
#
#     WHICH REMAINING CANDIDATE IS VIABLE
#     AFTER CONDITIONS CHANGE?
#
#
# These domains cooperate.
#
# They do not own each other's facts.
#
# ==========================================================================


# ==========================================================================
# CHEWBACCA'S OPERATIONAL SERVICE REVIEW
# ==========================================================================
#
# Chewbacca:
#
#     "The service is healthy."
#
#
# Agent 11:
#
#     ACCORDING TO WHICH OBSERVATION?
#
#
# Chewbacca:
#
#     "Fine. I put healthy=True on AIService."
#
#
# Agent 11:
#
#     REMOVE IT.
#
#
# Chewbacca:
#
#     "The endpoint is whatever-endpoint."
#
#
# Agent 11:
#
#     WHERE IS THE ENDPOINT MODEL?
#
#
# Chewbacca:
#
#     "I put it on AIService."
#
#
# Agent 11:
#
#     REMOVE IT.
#
#
# Chewbacca:
#
#     "I added us-east-1."
#
#
# Agent 11:
#
#     DEPLOYMENT CONCERN.
#
#
# Chewbacca:
#
#     "Latency is 4 milliseconds."
#
#
# Agent 11:
#
#     FOR HOW LONG?
#
#
# Chewbacca:
#
#     "Okay. But it is definitely E8 approved."
#
#
# Agent 11:
#
#     POLICY CONCERN.
#
#
# Chewbacca:
#
#     "The BGP route is—"
#
#
# Agent 11:
#
#     NETWORK.
#
#
# Chewbacca:
#
#     "Password is woof123."
#
#
# Agent 11:
#
#     SECURITY INCIDENT.
#
#
# Chewbacca:
#
#     "So AIService basically tells us which service exists,
#      which model it exposes, and which routing domain it belongs to?"
#
#
# Agent 11:
#
#     YES.
#
#
# Chewbacca:
#
#     "And everything changing around it gets its own domain?"
#
#
# Agent 11:
#
#     NOW YOU ARE ARCHITECTING.
#
# ==========================================================================


# ==========================================================================
# PART II — FINAL INVARIANTS
# ==========================================================================
#
#     SERVICE IDENTITY != OPERATIONAL OBSERVATION
#
#
#     SERVICE != DEPLOYMENT
#
#
#     SERVICE != ENDPOINT
#
#
#     SERVICE != SERVICE STATE
#
#
#     SERVICE != NETWORK PATH
#
#
#     SERVICE != CREDENTIAL
#
#
#     SERVICE != PRICE
#
#
#     SERVICE != CURRENT PERFORMANCE OBSERVATION
#
#
#     SERVICE != FALLBACK STRATEGY
#
#
#     SERVICE HEALTH != NETWORK HEALTH
#
#
#     SERVICE AVAILABLE != NETWORK AVAILABLE
#
#
#     AVAILABLE != AUTHORIZED
#
#
#     AUTHORIZED != AVAILABLE
#
#
#     AUTHORIZED != REACHABLE
#
#
#     REACHABLE != AUTHORIZED
#
#
#     REACHABLE != HEALTHY
#
#
#     HEALTHY != REACHABLE
#
#
#     CAPABLE != AVAILABLE
#
#
#     UNAVAILABLE != INCAPABLE
#
#
#     ENDPOINT != NETWORK PATH
#
#
#     ADDRESSABLE != REACHABLE
#
#
#     VALID URL TYPE != CORRECT DOMAIN MODEL
#
#
#     MODEL PROVIDER != SERVICE OPERATOR
#
#
#     SERVICE ROUTING DOMAIN != DEPLOYMENT LOCATION
#
#
#     MODEL CAPABILITY != DEPLOYED SERVICE CAPABILITY
#
#
#     UNKNOWN != UNAVAILABLE
#
#
#     DEGRADED != UNAVAILABLE
#
#
#     STATE DESCRIPTION != ROUTING BEHAVIOR
#
#
#     STALE OBSERVATION != CURRENT TRUTH
#
#
#     MULTIPLE SERVICES != INDEPENDENT SERVICES
#
#
#     MULTIPLE ENDPOINTS != TRUE REDUNDANCY
#
#
#     DISCOVERED != REGISTERED
#
#
#     REGISTERED != TRUSTED
#
#
#     REACHABLE != TRUSTED
#
#
#     FALLBACK != IGNORE POLICY
#
#
#     NEXT_VIABLE = RE-EVALUATE VIABILITY
#
#
# ==========================================================================
# END PART II
# ==========================================================================

# ==========================================================================
# PART III — SEIR-II EXPANSION AND AGENT 11 INTEGRATION
# ==========================================================================
#
# SEIR-I deliberately keeps AIService small:
#
#
#     AIService
#         |
#         +-- service_id
#         |
#         +-- display_name
#         |
#         +-- model_id
#         |
#         +-- routing_domain
#         |
#         +-- description
#
#
# This is enough to answer:
#
#
#     WHICH OPERATIONAL REASONING SERVICE EXISTS?
#
#     WHICH LOGICAL MODEL DOES IT EXPOSE?
#
#     WHICH ROUTING DOMAIN DOES IT BELONG TO?
#
#
# SEIR-II will surround this contract with richer operational domains.
#
#
# The important word is:
#
#
#     SURROUND
#
#
# Future operational complexity does not automatically justify adding
# more fields to AIService.
#
#
# Before extending AIService, always ask:
#
#
#     DOES THIS FACT DESCRIBE THE SERVICE'S IDENTITY?
#
#                         OR
#
#     DOES THIS FACT DESCRIBE SOMETHING AROUND THE SERVICE?
#
#
# This preserves a central Agent 11 design principle:
#
#
#     FUTURE-AWARE != FUTURE-BLOATED
#
#
# ==========================================================================


# ==========================================================================
# SEIR-II — SERVICE ECOSYSTEM
# ==========================================================================
#
# Future Agent 11 architecture may evolve toward:
#
#
#                         AIService
#                             |
#          +------------------+------------------+
#          |                  |                  |
#          v                  v                  v
#      Deployment        Runtime State       Governance
#          |
#          +----------+----------+
#          |          |          |
#          v          v          v
#       Endpoint   Runtime    Compute
#          |
#          v
#     Network Path
#
#
# Additional neighboring domains may include:
#
#
#     - service discovery,
#
#     - authentication requirements,
#
#     - effective service capabilities,
#
#     - capacity,
#
#     - economics,
#
#     - telemetry,
#
#     - failure domains,
#
#     - provenance,
#
#     - evaluation,
#
#     - and lifecycle governance.
#
#
# These concepts are important.
#
#
# They should NOT automatically become AIService fields.
#
#
# Architecture is largely the discipline of deciding:
#
#
#     WHICH THING OWNS WHICH FACT?
#
#
# ==========================================================================


# ==========================================================================
# SEIR-II — DEPLOYMENT
# ==========================================================================
#
# Future AI services may have one or more deployments:
#
#
#                       AIService
#                           |
#              +------------+------------+
#              |                         |
#              v                         v
#        Cloud Deployment          On-Prem Deployment
#
#
# Deployment may eventually describe:
#
#
#     - cloud location,
#
#     - data-center location,
#
#     - region,
#
#     - availability zone,
#
#     - Kubernetes cluster,
#
#     - inference runtime,
#
#     - accelerator configuration,
#
#     - scaling configuration,
#
#     - deployment-specific limits,
#
#     - and infrastructure provider.
#
#
# Those facts describe an operational instantiation.
#
#
# They do not necessarily describe the stable service identity.
#
#
# Therefore:
#
#
#     SERVICE != DEPLOYMENT
#
#
#     SERVICE IDENTITY != DEPLOYMENT TOPOLOGY
#
#
#     SERVICE ID != DEPLOYMENT ID
#
#
# A future Deployment model should own deployment facts when Agent 11
# actually requires that distinction.
#
# ==========================================================================


# ==========================================================================
# SEIR-II — SERVICE DISCOVERY AND ENDPOINTS
# ==========================================================================
#
# Future Agent 11 environments may discover how a service can be
# addressed through mechanisms such as:
#
#
#     - HTTPS,
#
#     - gRPC,
#
#     - Kubernetes service discovery,
#
#     - private endpoints,
#
#     - local inference,
#
#     - provider APIs,
#
#     - Unix sockets,
#
#     - or other service-discovery mechanisms.
#
#
# Conceptually:
#
#
#     AIService
#         |
#         v
#     Deployment
#         |
#         v
#     Endpoint / Discovery
#         |
#         v
#     Network Path
#
#
# These layers answer different questions:
#
#
#     AIService
#
#         WHICH SERVICE IS THIS?
#
#
#     Deployment
#
#         WHERE / HOW IS IT INSTANTIATED?
#
#
#     Endpoint
#
#         HOW IS IT ADDRESSED?
#
#
#     Network Path
#
#         HOW CAN TRAFFIC REACH IT?
#
#
# Therefore:
#
#
#     SERVICE != ENDPOINT
#
#
#     ENDPOINT != NETWORK PATH
#
#
#     DISCOVERY != REACHABILITY
#
#
#     DISCOVERY != AUTHORIZATION
#
#
# Discovering a service does not establish permission to use it.
#
# ==========================================================================


# ==========================================================================
# SEIR-II — EFFECTIVE SERVICE CAPABILITY
# ==========================================================================
#
# SEIR-I assumes that an AIService exposes the capabilities declared by
# its referenced AIModel.
#
#
# That is intentionally simple.
#
#
# SEIR-II may need a richer relationship:
#
#
#     AIModel
#         |
#         | theoretical / logical capability
#         v
#     Deployment
#         |
#         | operational constraints
#         v
#     Effective Service Capability
#
#
# Example:
#
#
#     AIModel
#
#         SECURITY_ANALYSIS
#             STANDARD
#             HEAVY
#
#
#     Cloud Deployment
#
#         SECURITY_ANALYSIS
#             STANDARD
#
#
#     On-Prem Deployment
#
#         SECURITY_ANALYSIS
#             STANDARD
#             HEAVY
#
#
# The logical model may support HEAVY reasoning.
#
# A particular deployment may not expose it.
#
#
# Therefore:
#
#
#     MODEL CAPABILITY
#         !=
#     DEPLOYED SERVICE CAPABILITY
#
#
# and:
#
#
#     THEORETICAL CAPABILITY
#         !=
#     OPERATIONALLY EXPOSED CAPABILITY
#
#
# Do not duplicate capability state in SEIR-I before this distinction is
# operationally required.
#
#
#     FUTURE-AWARE != FUTURE-BLOATED
#
# ==========================================================================


# ==========================================================================
# SEIR-II — RUNTIME OBSERVATIONS
# ==========================================================================
#
# Future operational state should be modeled as observation rather than
# stable service identity.
#
#
# Possible relationship:
#
#
#     AIService
#         |
#         v
#     ServiceStateObservation
#         |
#         +-- service_id
#         |
#         +-- state
#         |
#         +-- observed_at
#         |
#         +-- source
#
#
# This allows Agent 11 to reason about states such as:
#
#
#     AVAILABLE
#
#     DEGRADED
#
#     UNAVAILABLE
#
#     UNKNOWN
#
#
# without modifying the underlying service identity every time
# operational conditions change.
#
#
# Mature state observations may eventually need to answer:
#
#
#     WHAT WAS OBSERVED?
#
#     WHEN WAS IT OBSERVED?
#
#     WHO OR WHAT OBSERVED IT?
#
#     HOW FRESH IS THE OBSERVATION?
#
#
# Therefore:
#
#
#     SERVICE IDENTITY != SERVICE STATE
#
#
#     STATE != IDENTITY
#
#
#     UNKNOWN != UNAVAILABLE
#
#
#     STALE OBSERVATION != CURRENT TRUTH
#
# ==========================================================================


# ==========================================================================
# SEIR-II — CAPACITY AND PERFORMANCE
# ==========================================================================
#
# Future routing may consider operational information such as:
#
#
#     - available capacity,
#
#     - queue depth,
#
#     - latency,
#
#     - throughput,
#
#     - concurrency,
#
#     - accelerator utilization,
#
#     - token throughput,
#
#     - rate limits,
#
#     - and saturation.
#
#
# These values may change continuously.
#
#
# Therefore:
#
#
#     SERVICE IDENTITY != CAPACITY
#
#
#     SERVICE IDENTITY != PERFORMANCE
#
#
#     CAPABLE != CAPACITY AVAILABLE
#
#
#     LOW LATENCY != AUTHORIZED
#
#
#     HIGH CAPACITY != PERMITTED
#
#
# Runtime information may influence routing among already viable
# candidates.
#
#
# Runtime information does not redefine the service.
#
# ==========================================================================


# ==========================================================================
# SEIR-II — SERVICE ECONOMICS
# ==========================================================================
#
# Future Agent 11 routing may consider:
#
#
#     - token cost,
#
#     - inference cost,
#
#     - reserved capacity,
#
#     - GPU amortization,
#
#     - internal chargeback,
#
#     - provider pricing,
#
#     - workload economics,
#
#     - or organizational cost policy.
#
#
# Cost may help rank already viable candidates.
#
#
# Cost may NOT create viability.
#
#
# Example:
#
#
#     External Service
#
#         cost = very cheap
#
#         policy = DENY
#
#
# Result:
#
#
#     STILL DENIED
#
#
# Therefore:
#
#
#     CHEAPER != PERMITTED
#
#
#     CHEAPER != CAPABLE
#
#
#     CHEAPER != AVAILABLE
#
#
#     CHEAPER != REACHABLE
#
#
#     CHEAPER != VIABLE
#
#
# POLICY-SAFE ROUTING
#     comes before
# COST OPTIMIZATION.
#
#
# Economics may influence preference.
#
# Economics may never erase security policy.
#
# ==========================================================================


# ==========================================================================
# SEIR-II — SERVICE AUTHENTICATION
# ==========================================================================
#
# Future services may require:
#
#
#     - workload identity,
#
#     - IAM roles,
#
#     - managed identity,
#
#     - service accounts,
#
#     - certificates,
#
#     - OAuth tokens,
#
#     - signed requests,
#
#     - or other authentication mechanisms.
#
#
# A future relationship may look like:
#
#
#     AIService
#         |
#         v
#     Authentication Requirement
#         |
#         v
#     Credential Reference
#         |
#         v
#     Identity / Secret System
#
#
# These are deliberately separate concepts.
#
#
# Therefore:
#
#
#     SERVICE != CREDENTIAL
#
#
#     AUTHENTICATION METHOD != CREDENTIAL VALUE
#
#
#     CREDENTIAL REFERENCE != CREDENTIAL VALUE
#
#
#     CREDENTIAL REFERENCE != SECRET
#
#
# AIService should never become a secret store.
#
#
# The service contract may eventually describe what kind of identity is
# required.
#
# The actual secret belongs somewhere designed to protect secrets.
#
# ==========================================================================


# ==========================================================================
# SEIR-II — REDUNDANCY AND FAILURE DOMAINS
# ==========================================================================
#
# Future Agent 11 may know several apparently equivalent services:
#
#
#                         AIModel
#                            |
#                +-----------+-----------+
#                |           |           |
#                v           v           v
#            Service A   Service B   Service C
#
#
# At first glance this appears redundant.
#
#
# But redundancy requires understanding shared dependencies.
#
#
# Two or more services may share:
#
#
#     - the same model provider,
#
#     - the same cloud provider,
#
#     - the same region,
#
#     - the same Kubernetes cluster,
#
#     - the same identity provider,
#
#     - the same network,
#
#     - the same DNS infrastructure,
#
#     - the same inference runtime,
#
#     - the same accelerator pool,
#
#     - or the same underlying service provider.
#
#
# Therefore:
#
#
#     MULTIPLE SERVICES != TRUE REDUNDANCY
#
#
#     MULTIPLE ENDPOINTS != INDEPENDENT FAILURE DOMAINS
#
#
#     DIFFERENT SERVICE IDS != INDEPENDENT INFRASTRUCTURE
#
#
# Future fallback may need to understand dependency independence before
# claiming that a set of services provides meaningful resilience.
#
# ==========================================================================


# ==========================================================================
# SEIR-II — NETWORK-AWARE SERVICE SELECTION
# ==========================================================================
#
# Future Agent 11 may consume network information from systems such as:
#
#
#     - health monitors,
#
#     - VPN state,
#
#     - private connectivity,
#
#     - SD-WAN,
#
#     - BGP,
#
#     - service mesh telemetry,
#
#     - or other network-control systems.
#
#
# The separation remains:
#
#
#     AGENT 11
#
#         "Which AI destination may and should be used?"
#
#
#     NETWORK CONTROL
#
#         "How can packets reach that destination?"
#
#
# Therefore:
#
#
#     AI ROUTING != NETWORK ROUTING
#
#
#     AI AUTHORIZATION != NETWORK REACHABILITY
#
#
#     NETWORK REACHABILITY != AI AUTHORIZATION
#
#
# Future integration may look like:
#
#
#     APPROVED AI SERVICE
#             |
#             v
#     APPROVED ENDPOINT
#             |
#             v
#     AVAILABLE NETWORK PATH
#             |
#             v
#     BGP / SD-WAN / VPN / PRIVATE LINK
#
#
# BGP may help determine:
#
#
#     HOW DO PACKETS REACH THE APPROVED INFERENCE ENDPOINT?
#
#
# BGP must never determine:
#
#
#     MAY E8 DATA BE SENT TO THIS AI SERVICE?
#
#
# That remains an Agent 11 policy question.
#
# ==========================================================================


# ==========================================================================
# SEIR-II — SERVICE GOVERNANCE
# ==========================================================================
#
# Mature AI platforms may eventually govern service lifecycle:
#
#
#     DISCOVERED
#         |
#         v
#     REGISTERED
#         |
#         v
#     EVALUATED
#         |
#         v
#     APPROVED
#         |
#         v
#     ACTIVE
#         |
#         v
#     DEPRECATED
#         |
#         v
#     RETIRED
#
#
# This lifecycle is illustrative.
#
# Do not convert it into an enum until the actual governance state
# machine has been designed.
#
#
# Remember:
#
#
#     DO NOT ADD A BOOLEAN
#     BEFORE YOU UNDERSTAND THE STATE MACHINE.
#
#
# Especially avoid fields such as:
#
#
#     approved: bool
#
#
#     trusted: bool
#
#
#     production: bool
#
#
# before defining what those states actually mean.
#
#
# Governance may eventually determine whether a service is eligible to
# participate in routing.
#
#
# But:
#
#
#     SERVICE GOVERNANCE
#         !=
#     REQUEST AUTHORIZATION
#
#
# A generally approved service may still be forbidden for a particular
# data classification or user.
#
# ==========================================================================


# ==========================================================================
# SEIR-II — DISCOVERED, REGISTERED, TRUSTED, AND AUTHORIZED
# ==========================================================================
#
# Future service discovery creates another important progression:
#
#
#     DISCOVERED
#         |
#         v
#     REGISTERED
#         |
#         v
#     EVALUATED
#         |
#         v
#     TRUSTED / APPROVED
#         |
#         v
#     REQUEST-SPECIFIC AUTHORIZATION
#
#
# These states are not synonyms.
#
#
# A service may be discoverable on the network without being registered.
#
#
# A service may be registered without being approved.
#
#
# A service may be approved for general use without being authorized
# for a particular request.
#
#
# Therefore:
#
#
#     DISCOVERED != REGISTERED
#
#
#     REGISTERED != TRUSTED
#
#
#     TRUSTED != AUTHORIZED FOR ALL DATA
#
#
#     SERVICE APPROVAL != REQUEST AUTHORIZATION
#
#
# Discovery must never silently become trust.
#
# ==========================================================================


# ==========================================================================
# SEIR-II — TELEMETRY AND PROVENANCE
# ==========================================================================
#
# Future Agent 11 telemetry may record:
#
#
#     - which service was considered,
#
#     - which service was selected,
#
#     - which model the service exposed,
#
#     - observed service state,
#
#     - observed network state,
#
#     - policy decision,
#
#     - fallback behavior,
#
#     - latency,
#
#     - token usage,
#
#     - cost,
#
#     - and final outcome.
#
#
# AIService contributes stable identity to those records.
#
#
# It should not absorb the telemetry itself.
#
#
# Therefore:
#
#
#     SERVICE != TELEMETRY EVENT
#
#
#     SERVICE IDENTITY != USAGE RECORD
#
#
#     SERVICE IDENTITY != ROUTING EVENT
#
#
#     SERVICE IDENTITY != POLICY EVENT
#
#
# Stable identity allows changing observations and decisions to refer
# back to the same service over time.
#
# ==========================================================================


# ==========================================================================
# SEIR-II — AIService AND MCP
# ==========================================================================
#
# Agent 11 will also integrate MCP.
#
#
# Do not collapse MCP tools and AI reasoning services into one concept.
#
#
# Agent 11 has at least two different operational paths:
#
#
#     REASONING REQUEST
#         |
#         v
#     AIModel / AIService
#
#
# and:
#
#
#     TOOL REQUEST
#         |
#         v
#     MCP Service / Tool Registry
#
#
# Therefore:
#
#
#     AI SERVICE != MCP TOOL
#
#
#     MODEL CAPABILITY != TOOL CAPABILITY
#
#
#     REASONING ROUTING != TOOL ROUTING
#
#
# A reasoning service may eventually support tool use.
#
# That does not make the reasoning service itself the tool.
#
# ==========================================================================


# ==========================================================================
# SEIR-II — AIService AND JUDGMENT DAY AS CODE
# ==========================================================================
#
# AIService makes reasoning operationally available.
#
#
# Operational availability must not be confused with execution authority.
#
#
# Dangerous architecture:
#
#
#     AIService
#         |
#         v
#     AI OUTPUT
#         |
#         v
#     UNBOUNDED EXECUTION
#
#
# This creates the Agent 11 anti-pattern:
#
#
#     AI CAPABILITY
#         +
#     UNBOUNDED AUTHORITY
#         +
#     AUTOMATED EXECUTION
#         +
#     POOR GOVERNANCE
#         =
#     JUDGMENT DAY AS CODE
#
#
# Safer architecture:
#
#
#     AI REASONING
#         |
#         v
#     POLICY GATES
#         |
#         v
#     SCOPED AUTHORITY
#         |
#         v
#     APPROVED EXECUTION
#         |
#         v
#     AUDIT / PROVENANCE
#
#
# Some actions may additionally require:
#
#
#     HUMAN APPROVAL
#
#
# Therefore:
#
#
#     SERVICE AVAILABILITY != EXECUTION AUTHORITY
#
#
#     MODEL OUTPUT != ACTION AUTHORITY
#
#
#     REASONING ACCESS != UNBOUNDED DELEGATION
#
# ==========================================================================


# ==========================================================================
# SEIR-II — SERVICE SELECTION VS ROUTE SELECTION
# ==========================================================================
#
# As Agent 11 grows, routing may eventually operate at several levels.
#
#
# Example:
#
#
#     REQUEST
#         |
#         v
#     ROUTING DOMAIN
#         |
#         +-- COMPANY_ONPREM_LLM
#         |
#         v
#     CANDIDATE SERVICES
#         |
#         +-- onprem-primary
#         |
#         +-- onprem-secondary
#         |
#         v
#     VIABILITY
#         |
#         v
#     SELECTED SERVICE
#
#
# Therefore:
#
#
#     ROUTING DOMAIN SELECTION
#         !=
#     SERVICE SELECTION
#
#
# and:
#
#
#     SERVICE SELECTION
#         !=
#     NETWORK PATH SELECTION
#
#
# Mature Agent 11 routing may coordinate all three.
#
#
# It should not pretend they are the same decision.
#
# ==========================================================================


# ==========================================================================
# AIService INSIDE THE FUTURE AI CONTROL PLANE
# ==========================================================================
#
#                        AI CONTROL PLANE
#                               |
#       +-----------+-----------+-----------+-----------+
#       |           |           |           |           |
#       v           v           v           v           v
#     MODELS     SERVICES     POLICY      NETWORK    GOVERNANCE
#       |           |
#       |           +-- deployments
#       |           +-- runtime state
#       |           +-- capacity
#       |           +-- telemetry
#       |           +-- economics
#       |
#       +-- capabilities
#       +-- provenance
#       +-- evaluation
#
#                               |
#                               v
#                            ROUTING
#
#
# AIService contributes one precise set of facts:
#
#
#     WHICH SERVICE EXISTS?
#
#     WHICH MODEL DOES IT EXPOSE?
#
#     WHICH ROUTING DOMAIN DOES IT BELONG TO?
#
#
# It does not become the entire AI Control Plane.
#
#
#     SERVICE PROVIDES FACTS.
#
#     ORCHESTRATORS COORDINATE BEHAVIOR.
#
#
# This follows the broader Agent 11 rule:
#
#
#     MODELS ARE NOUNS.
#
#     ORCHESTRATORS COORDINATE VERBS.
#
# ==========================================================================


# ==========================================================================
# AIService INSIDE THE AGENT 11 DECISION PIPELINE
# ==========================================================================
#
# AIService participates in a larger decision:
#
#
#                         AIRequest
#                             |
#                             v
#                  REQUEST REQUIREMENTS
#                             |
#                             v
#                     CAPABILITY MATCH
#                             |
#                             v
#                         AIModel
#                             |
#                             v
#                        AIService
#                             |
#              +--------------+--------------+
#              |              |              |
#              v              v              v
#           POLICY       SERVICE STATE     NETWORK
#              |              |              |
#              +--------------+--------------+
#                             |
#                             v
#                      VIABILITY CHECK
#                             |
#                             v
#                          ROUTING
#                             |
#                             v
#                         SELECTED
#
#
# AIService contributes:
#
#
#     SERVICE IDENTITY
#
#     MODEL REFERENCE
#
#     ROUTING DOMAIN
#
#
# Other domains contribute:
#
#
#     CAPABILITY
#
#     AUTHORIZATION
#
#     AVAILABILITY
#
#     REACHABILITY
#
#     PREFERENCE
#
#
# No single object should manufacture the complete decision.
#
# ==========================================================================


# ==========================================================================
# AGENT 11 VIABILITY REMINDER
# ==========================================================================
#
# Agent 11's fundamental viability rule remains:
#
#
#     VIABLE ROUTE
#         =
#     POLICY PERMITTED
#         +
#     SERVICE CAPABLE
#         +
#     SERVICE AVAILABLE
#         +
#     PATH AVAILABLE
#
#
# AIService participates in this decision.
#
#
# AIService does NOT make this decision.
#
#
# Examples:
#
#
#     CAPABLE
#         +
#     AVAILABLE
#         +
#     REACHABLE
#         +
#     POLICY DENY
#
#         =
#
#     NOT VIABLE
#
#
# --------------------------------------------------------------------------
#
#     CAPABLE
#         +
#     POLICY ALLOW
#         +
#     REACHABLE
#         +
#     SERVICE UNAVAILABLE
#
#         =
#
#     NOT VIABLE
#
#
# --------------------------------------------------------------------------
#
#     CAPABLE
#         +
#     POLICY ALLOW
#         +
#     AVAILABLE
#         +
#     PATH UNAVAILABLE
#
#         =
#
#     NOT VIABLE
#
#
# --------------------------------------------------------------------------
#
#     INCAPABLE
#         +
#     POLICY ALLOW
#         +
#     AVAILABLE
#         +
#     REACHABLE
#
#         =
#
#     NOT VIABLE
#
#
# --------------------------------------------------------------------------
#
#     CAPABLE
#         +
#     POLICY ALLOW
#         +
#     AVAILABLE
#         +
#     REACHABLE
#
#         =
#
#     VIABLE CANDIDATE
#
#
# Notice:
#
#
#     VIABLE CANDIDATE != SELECTED
#
#
# Routing still decides among viable candidates.
#
# ==========================================================================


# ==========================================================================
# SEIR-II EXPANSION MARKER — DO NOT DELETE
# ==========================================================================
#
# SEIR-I intentionally defines AIService with only:
#
#
#     service_id
#
#     display_name
#
#     model_id
#
#     routing_domain
#
#     description
#
#
# Future SEIR-II requirements may introduce neighboring contracts for:
#
#
# --------------------------------------------------------------------------
# DEPLOYMENT
# --------------------------------------------------------------------------
#
#     deployment identity
#
#     cloud / on-prem location
#
#     region / data center
#
#     cluster
#
#     inference runtime
#
#     deployment configuration
#
#
# --------------------------------------------------------------------------
# ENDPOINT / DISCOVERY
# --------------------------------------------------------------------------
#
#     address
#
#     protocol
#
#     service discovery
#
#     private endpoint relationships
#
#
# --------------------------------------------------------------------------
# RUNTIME STATE
# --------------------------------------------------------------------------
#
#     availability
#
#     degradation
#
#     observation time
#
#     observation source
#
#     freshness
#
#
# --------------------------------------------------------------------------
# EFFECTIVE CAPABILITY
# --------------------------------------------------------------------------
#
#     deployment-specific capability
#
#     configured reasoning limits
#
#     runtime feature exposure
#
#
# --------------------------------------------------------------------------
# CAPACITY / PERFORMANCE
# --------------------------------------------------------------------------
#
#     concurrency
#
#     queue depth
#
#     latency
#
#     throughput
#
#     accelerator utilization
#
#
# --------------------------------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------------------------------
#
#     authentication requirements
#
#     workload identity
#
#     credential references
#
#
# --------------------------------------------------------------------------
# ECONOMICS
# --------------------------------------------------------------------------
#
#     token cost
#
#     compute cost
#
#     internal chargeback
#
#     capacity economics
#
#
# --------------------------------------------------------------------------
# RESILIENCE
# --------------------------------------------------------------------------
#
#     failure domains
#
#     dependency relationships
#
#     redundancy
#
#     fallback independence
#
#
# --------------------------------------------------------------------------
# GOVERNANCE
# --------------------------------------------------------------------------
#
#     registration
#
#     evaluation
#
#     approval
#
#     lifecycle
#
#     provenance
#
#
# --------------------------------------------------------------------------
# TELEMETRY
# --------------------------------------------------------------------------
#
#     routing events
#
#     service observations
#
#     usage
#
#     cost
#
#     performance
#
#
# These future requirements should NOT automatically become fields on
# AIService.
#
#
# Ask first:
#
#
#     WHICH DOMAIN OWNS THIS FACT?
#
#
#     DOES AIService NEED THIS FACT?
#
#
#     OR DOES AN ORCHESTRATOR NEED TO COMBINE THIS FACT
#     WITH AIService?
#
#
# Simple today should not mean impossible tomorrow.
#
#
#     SIMPLE TODAY SHOULD NOT MEAN IMPOSSIBLE TOMORROW.
#
#
# ==========================================================================


# ==========================================================================
# DO NOT TURN AIService INTO THE ENTIRE AI PLATFORM
# ==========================================================================
#
# A future developer may eventually propose:
#
#
#     class AIService:
#
#         service_id
#         display_name
#         model_id
#         routing_domain
#         description
#         endpoint
#         region
#         cluster
#         health
#         latency
#         cost
#         api_key
#         token
#         capacity
#         gpu_type
#         bgp_route
#         sdwan_path
#         e7_allowed
#         e8_allowed
#         e9_allowed
#         fallback_service
#         approved
#         trusted
#         selected
#         ...
#
#
# Stop.
#
#
# That is no longer an AIService domain model.
#
#
# That is an attempted AI platform compressed into one object.
#
#
# Large systems become understandable by preserving ownership
# boundaries.
#
#
# The solution to:
#
#
#     "Agent 11 needs all of these facts."
#
#
# is NOT:
#
#
#     "AIService must own all of these facts."
#
#
# Instead:
#
#
#     AIService
#         +
#     AIModel
#         +
#     Deployment
#         +
#     Runtime State
#         +
#     Policy
#         +
#     Network
#         +
#     Telemetry
#         +
#     Governance
#         +
#     Routing
#
#         =
#
#     COORDINATED AI PLATFORM
#
#
#     MODEL COMPLETENESS
#         !=
#     PUT EVERYTHING IN ONE MODEL
#
# ==========================================================================


# ==========================================================================
# CHEWBACCA'S SEIR-II SERVICE REVIEW
# ==========================================================================
#
# Chewbacca:
#
#     "I added endpoint."
#
#
# Agent 11:
#
#     DEPLOYMENT / ENDPOINT DOMAIN.
#
#
# Chewbacca:
#
#     "Okay. I added healthy=True."
#
#
# Agent 11:
#
#     RUNTIME OBSERVATION.
#
#
# Chewbacca:
#
#     "region='us-east-1'?"
#
#
# Agent 11:
#
#     DEPLOYMENT.
#
#
# Chewbacca:
#
#     "latency_ms=4?"
#
#
# Agent 11:
#
#     TELEMETRY.
#
#
# Chewbacca:
#
#     "cost_per_token?"
#
#
# Agent 11:
#
#     ECONOMICS.
#
#
# Chewbacca:
#
#     "api_key?"
#
#
# Agent 11:
#
#     SECURITY INCIDENT.
#
#
# Chewbacca:
#
#     "e8_allowed=True?"
#
#
# Agent 11:
#
#     POLICY.
#
#
# Chewbacca:
#
#     "bgp_route?"
#
#
# Agent 11:
#
#     NETWORK.
#
#
# Chewbacca:
#
#     "fallback_service_id?"
#
#
# Agent 11:
#
#     ROUTING.
#
#
# Chewbacca:
#
#     "gpu_type?"
#
#
# Agent 11:
#
#     DEPLOYMENT / COMPUTE.
#
#
# Chewbacca:
#
#     "So what exactly am I allowed to put in AIService?"
#
#
# Agent 11:
#
#     WHICH SERVICE?
#
#     WHAT HUMAN NAME?
#
#     WHICH MODEL?
#
#     WHICH ROUTING DOMAIN?
#
#     OPTIONAL DESCRIPTION.
#
#
# Chewbacca:
#
#     "Five fields?"
#
#
# Agent 11:
#
#     FIVE FIELDS.
#
#
# Chewbacca:
#
#     "And everything else gets an owner?"
#
#
# Agent 11:
#
#     NOW YOU UNDERSTAND THE ASSIGNMENT.
#
# ==========================================================================


# ==========================================================================
# PART III — RESPONSIBILITY MAP
# ==========================================================================
#
# AIModel
#
#     WHAT LOGICAL REASONING MODEL EXISTS?
#
#     WHAT CAN THAT MODEL DO?
#
#
# AIService
#
#     WHAT OPERATIONAL REASONING SERVICE EXISTS?
#
#     WHICH MODEL DOES IT EXPOSE?
#
#     WHICH ROUTING DOMAIN DOES IT BELONG TO?
#
#
# Deployment
#
#     WHERE / HOW IS THE SERVICE INSTANTIATED?
#
#
# Endpoint
#
#     HOW IS THE DEPLOYMENT ADDRESSED?
#
#
# Runtime State
#
#     CAN THE SERVICE CURRENTLY OPERATE?
#
#
# Network
#
#     CAN THE DESTINATION CURRENTLY BE REACHED?
#
#
# Policy
#
#     MAY THIS REQUEST USE THE DESTINATION?
#
#
# Governance
#
#     IS THE RESOURCE ACCEPTABLE FOR ORGANIZATIONAL USE?
#
#
# Telemetry
#
#     WHAT HAS BEEN OBSERVED?
#
#
# Economics
#
#     WHAT DOES USE OF THE RESOURCE COST?
#
#
# Routing
#
#     WHICH VIABLE DESTINATION SHOULD BE SELECTED?
#
#
# Orchestration
#
#     HOW ARE THESE DOMAINS COORDINATED?
#
#
# Architecture is largely the discipline of deciding:
#
#
#     WHICH THING OWNS WHICH FACT?
#
# ==========================================================================


# ==========================================================================
# PART III — FINAL INVARIANTS
# ==========================================================================
#
#     SERVICE != MODEL
#
#
#     SERVICE != DEPLOYMENT
#
#
#     SERVICE != ENDPOINT
#
#
#     SERVICE != SERVICE STATE
#
#
#     SERVICE != NETWORK PATH
#
#
#     SERVICE != CREDENTIAL
#
#
#     SERVICE != ECONOMICS
#
#
#     SERVICE != TELEMETRY
#
#
#     SERVICE != GOVERNANCE
#
#
#     SERVICE != ROUTING DECISION
#
#
#     SERVICE != FALLBACK STRATEGY
#
#
#     SERVICE != AI CONTROL PLANE
#
#
#     SERVICE IDENTITY != DEPLOYMENT TOPOLOGY
#
#
#     SERVICE IDENTITY != CAPACITY
#
#
#     SERVICE IDENTITY != PERFORMANCE
#
#
#     SERVICE IDENTITY != USAGE RECORD
#
#
#     SERVICE IDENTITY != ROUTING EVENT
#
#
#     SERVICE IDENTITY != POLICY EVENT
#
#
#     MODEL CAPABILITY != DEPLOYED SERVICE CAPABILITY
#
#
#     THEORETICAL CAPABILITY != OPERATIONALLY EXPOSED CAPABILITY
#
#
#     ENDPOINT != NETWORK PATH
#
#
#     DISCOVERY != REACHABILITY
#
#
#     DISCOVERY != AUTHORIZATION
#
#
#     DISCOVERED != REGISTERED
#
#
#     REGISTERED != TRUSTED
#
#
#     TRUSTED != AUTHORIZED FOR ALL DATA
#
#
#     SERVICE APPROVAL != REQUEST AUTHORIZATION
#
#
#     SERVICE HEALTH != NETWORK HEALTH
#
#
#     AVAILABLE != AUTHORIZED
#
#
#     AUTHORIZED != AVAILABLE
#
#
#     REACHABLE != AUTHORIZED
#
#
#     CAPABLE != AVAILABLE
#
#
#     CAPABLE != VIABLE
#
#
#     VIABLE != SELECTED
#
#
#     LOW LATENCY != AUTHORIZED
#
#
#     HIGH CAPACITY != PERMITTED
#
#
#     CHEAPER != PERMITTED
#
#
#     CHEAPER != VIABLE
#
#
#     MULTIPLE SERVICES != TRUE REDUNDANCY
#
#
#     MULTIPLE ENDPOINTS != INDEPENDENT FAILURE DOMAINS
#
#
#     DIFFERENT SERVICE IDS != INDEPENDENT INFRASTRUCTURE
#
#
#     ROUTING DOMAIN SELECTION != SERVICE SELECTION
#
#
#     SERVICE SELECTION != NETWORK PATH SELECTION
#
#
#     AI ROUTING != NETWORK ROUTING
#
#
#     SERVICE AVAILABILITY != EXECUTION AUTHORITY
#
#
#     MODEL OUTPUT != ACTION AUTHORITY
#
#
#     AI SERVICE != MCP TOOL
#
#
#     SERVICE PROVIDES FACTS
#
#
#     ORCHESTRATORS COORDINATE BEHAVIOR
#
#
#     SIMPLE TODAY SHOULD NOT MEAN IMPOSSIBLE TOMORROW
#
#
#     FUTURE-AWARE != FUTURE-BLOATED
#
# ==========================================================================


# ==========================================================================
# FINAL AI SERVICE ECOSYSTEM
# ==========================================================================
#
#                            AIRequest
#                                |
#                                v
#                     REQUEST REQUIREMENTS
#                                |
#                                v
#                          AICapability
#                                |
#                                v
#                            AIModel
#                                |
#                                | model_id
#                                v
#                           AIService
#                                |
#              +-----------------+-----------------+
#              |                 |                 |
#              v                 v                 v
#         Deployment        Runtime State        Policy
#              |
#              v
#           Endpoint
#              |
#              v
#        Network Path
#
#              \                 |                 /
#               \                |                /
#                +---------------+---------------+
#                                |
#                                v
#                         VIABILITY CHECK
#                                |
#                                v
#                             ROUTING
#                                |
#                                v
#                            SELECTED
#
#
# AIService contributes:
#
#
#     IDENTITY
#
#     MODEL REFERENCE
#
#     ROUTING DOMAIN
#
#
# It deliberately does not own the entire decision.
#
#
# SEIR-I asks:
#
#
#     WHICH OPERATIONAL REASONING SERVICE EXISTS?
#
#
# SEIR-II may additionally ask:
#
#
#     WHERE IS IT DEPLOYED?
#
#     HOW IS IT ADDRESSED?
#
#     WHAT CAPABILITIES DOES THIS DEPLOYMENT ACTUALLY EXPOSE?
#
#     WHAT IS ITS CURRENT STATE?
#
#     HOW FRESH IS THAT STATE?
#
#     WHAT CAPACITY REMAINS?
#
#     WHAT DOES IT COST?
#
#     HOW IS IT AUTHENTICATED?
#
#     WHAT FAILURE DOMAIN DOES IT BELONG TO?
#
#     IS IT ORGANIZATIONALLY APPROVED?
#
#     CAN THE NETWORK CURRENTLY REACH IT?
#
#
# Those are not reasons to turn AIService into a forty-field object.
#
#
# They are reasons to build the surrounding architecture correctly.
#
#
# Five fields.
#
# Zero unnecessary validators.
#
# Everything else gets an owner.
#
#
# ==========================================================================
# END PART III
# ==========================================================================
