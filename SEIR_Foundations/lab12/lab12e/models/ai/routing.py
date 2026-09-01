# ==========================================================================
# PART I — RoutingCandidate DOMAIN CONTRACT
# ==========================================================================
#
# RoutingCandidate represents the outcome of evaluating ONE candidate
# AI service during Agent 11 routing.
#
#
# It answers:
#
#
#     WHAT HAPPENED TO THIS CANDIDATE?
#
#
# Example:
#
#
#     AIRequest
#         |
#         v
#     Candidate Services
#         |
#         +-- Service A --> VIABLE
#         |
#         +-- Service B --> REJECTED: POLICY_DENIED
#         |
#         +-- Service C --> REJECTED: SERVICE_UNAVAILABLE
#
#
# Each service evaluation can be represented by one RoutingCandidate.
#
#
# RoutingCandidate does NOT select the final destination.
#
#
#     CANDIDATE EVALUATION != ROUTING DECISION
#
#
#     VIABLE != SELECTED
#
#
# RoutingCandidate is a domain contract.
#
# It records the result of routing evaluation.
#
# It does NOT:
#
#
#     evaluate policy,
#
#     compare capabilities,
#
#     inspect service health,
#
#     inspect network paths,
#
#     calculate routing scores,
#
#     perform fallback,
#
#     or select the final destination.
#
#
# Those behaviors belong elsewhere in Agent 11.
#
#
#     MODELS ARE NOUNS.
#
#     ROUTERS AND ORCHESTRATORS COORDINATE VERBS.
#
# ==========================================================================


from pydantic import Field, model_validator

from ..base_model import Agent11BaseModel
from ..enums.routing_enums import (
    AIRoute,
    RoutingCandidateStatus,
    RoutingRejectionReason,
)


# ==========================================================================
# ROUTING ENUM VOCABULARY
# ==========================================================================
#
# RoutingCandidate depends on two routing vocabularies defined in:
#
#
#     models/enums/routing_enums.py
#
#
# Expected SEIR-I definitions:
#
#
#     class RoutingCandidateStatus(Agent11Enum):
#         VIABLE = "viable"
#         REJECTED = "rejected"
#
#
#     class RoutingRejectionReason(Agent11Enum):
#         POLICY_DENIED = "policy_denied"
#         CAPABILITY_MISMATCH = "capability_mismatch"
#         SERVICE_UNAVAILABLE = "service_unavailable"
#         NETWORK_UNAVAILABLE = "network_unavailable"
#         UNKNOWN = "unknown"
#
#
# The enums define vocabulary.
#
# They do NOT perform routing.
#
#
#     ENUM != DECISION ENGINE
#
# ==========================================================================


# ==========================================================================
# WHY RoutingCandidateStatus IS SMALL
# ==========================================================================
#
# Candidate status answers:
#
#
#     DID THIS CANDIDATE SURVIVE VIABILITY EVALUATION?
#
#
# Therefore SEIR-I needs only:
#
#
#     VIABLE
#
#     REJECTED
#
#
# The reason for rejection belongs to:
#
#
#     RoutingRejectionReason
#
#
# Do NOT create candidate states such as:
#
#
#     POLICY_REJECTED
#
#     NETWORK_REJECTED
#
#     CAPABILITY_REJECTED
#
#     HEALTH_REJECTED
#
#
# That would mix:
#
#
#     OUTCOME
#
# with:
#
#     REASON
#
#
# Instead:
#
#
#     status = REJECTED
#
#     rejection_reason = POLICY_DENIED
#
#
# preserves two independent facts:
#
#
#     WHAT HAPPENED?
#
#         REJECTED
#
#
#     WHY?
#
#         POLICY_DENIED
#
#
#     OUTCOME != REASON
#
# ==========================================================================


# ==========================================================================
# REJECTED DOES NOT MEAN FAILED
# ==========================================================================
#
# A routing candidate may be rejected even when the underlying service
# is functioning perfectly.
#
#
# Example:
#
#
#     capability     = PASS
#
#     service state  = AVAILABLE
#
#     network path   = AVAILABLE
#
#     policy         = DENY
#
#
# Result:
#
#
#     status = REJECTED
#
#     rejection_reason = POLICY_DENIED
#
#
# Nothing necessarily failed.
#
#
# Agent 11 correctly determined that the service must not participate
# in routing for this request.
#
#
# Therefore:
#
#
#     REJECTED != FAILED
#
#
#     HEALTHY != PERMITTED
#
#
#     REACHABLE != AUTHORIZED
#
#
#     CAPABLE != AUTHORIZED
#
# ==========================================================================


# ==========================================================================
# UNKNOWN DOES NOT REPLACE OBSERVED STATE
# ==========================================================================
#
# RoutingRejectionReason.UNKNOWN is intentionally conservative.
#
#
# It means Agent 11 does not have a more specific routing-level reason
# available for why the candidate could not safely survive evaluation.
#
#
# It must NOT be used to rewrite domain observations.
#
#
# Example:
#
#
#     ServiceState = UNKNOWN
#
#
# must remain:
#
#
#     UNKNOWN
#
#
# It must not be changed to:
#
#
#     UNAVAILABLE
#
#
# merely because routing chooses to reject the candidate conservatively.
#
#
# Likewise:
#
#
#     NetworkPathState = UNKNOWN
#
#
# remains an unknown network observation.
#
#
# Routing may still decide:
#
#
#     RoutingCandidateStatus.REJECTED
#
#
# because sufficient viability could not be established.
#
#
# Therefore:
#
#
#     UNKNOWN FACT
#         !=
#     UNAVAILABLE FACT
#
#
#     FAIL CLOSED != FALSIFY OBSERVED STATE
#
#
#     DECISION BEHAVIOR != OBSERVED TRUTH
#
#
# Future Agent 11 versions may introduce richer rejection provenance
# rather than relying on a generic UNKNOWN reason.
#
# ==========================================================================


class RoutingCandidate(Agent11BaseModel):
    """
    Describes the routing evaluation outcome for one candidate AI service.

    RoutingCandidate records whether a candidate service survived Agent 11
    viability evaluation and, when rejected, the machine-readable reason
    for that rejection.

    It does not select the final routing destination and does not own the
    policy, capability, service-state, or network facts used to evaluate
    the candidate.
    """

    # ----------------------------------------------------------------------
    # service_id
    # ----------------------------------------------------------------------
    #
    # RoutingCandidate references the AIService being evaluated.
    #
    #
    #     RoutingCandidate
    #         |
    #         | service_id
    #         v
    #     AIService
    #
    #
    # It does NOT embed the entire AIService object.
    #
    #
    # Therefore:
    #
    #
    #     CANDIDATE REFERENCES SERVICE
    #
    #     CANDIDATE DOES NOT OWN SERVICE DEFINITION
    #
    #
    # As with AIService.model_id:
    #
    #
    #     VALID SERVICE ID
    #         !=
    #     EXISTING REGISTERED SERVICE
    #
    #
    # Pydantic validates the identifier as part of this domain object.
    #
    # A registry / orchestrator is responsible for determining whether
    # the identifier corresponds to a service currently known to Agent 11.
    #
    #
    #     DOMAIN VALIDATION != CROSS-RESOURCE RESOLUTION
    #
    # ----------------------------------------------------------------------

    service_id: str = Field(
        min_length=1,
        description=(
            "Identifier of the AI service evaluated as a routing candidate."
        ),
    )

    # ----------------------------------------------------------------------
    # routing_domain
    # ----------------------------------------------------------------------
    #
    # routing_domain records the Agent 11 destination class associated
    # with this candidate.
    #
    #
    # Current SEIR-I vocabulary:
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
    #     routing_domain=AIRoute.COMPANY_CLOUD_LLM
    #
    #
    # This does NOT mean:
    #
    #
    #     - the candidate is authorized,
    #
    #     - the candidate is viable,
    #
    #     - the candidate is selected,
    #
    #     - or the candidate is deployed in any specific cloud.
    #
    #
    # routing_domain is deliberately preserved directly on
    # RoutingCandidate even though a future service registry could
    # theoretically resolve it from service_id.
    #
    #
    # This makes candidate records immediately understandable and
    # preserves important routing context for logs, telemetry, debugging,
    # and historical analysis.
    #
    #
    #     PRESERVE IMPORTANT DECISION CONTEXT
    #
    #     DO NOT REQUIRE A REGISTRY LOOKUP FOR BASIC INTERPRETATION
    #
    #
    # IMPORTANT FUTURE EXPANSION:
    #
    #
    #     COMPANY_CLOUD_LLM
    #
    #
    # describes an Agent 11 routing domain.
    #
    # It does NOT mean:
    #
    #
    #     AWS ONLY
    #
    #
    # Future company-operated reasoning services may exist in:
    #
    #
    #     AWS
    #
    #     Azure
    #
    #     GCP
    #
    #     OCI
    #
    #     other cloud environments
    #
    #
    # A proprietary company model may also run in one of those clouds
    # without changing the meaning of COMPANY_CLOUD_LLM.
    #
    #
    # Cloud provider, deployment location, model origin, and service
    # operator are separate architectural facts.
    #
    #
    # Therefore:
    #
    #
    #     ROUTING DOMAIN != CLOUD PROVIDER
    #
    #     ROUTING DOMAIN != DEPLOYMENT LOCATION
    #
    #     CLOUD PROVIDER != MODEL PROVIDER
    #
    #     MODEL IDENTITY != DEPLOYMENT IDENTITY
    #
    #
    # SEIR-II expands these distinctions in Part IV.
    #
    # ----------------------------------------------------------------------

    routing_domain: AIRoute = Field(
        description=(
            "Routing domain associated with the candidate AI service."
        ),
    )

    # ----------------------------------------------------------------------
    # status
    # ----------------------------------------------------------------------
    #
    # status answers:
    #
    #
    #     DID THIS CANDIDATE SURVIVE VIABILITY EVALUATION?
    #
    #
    #     VIABLE
    #
    #         Candidate survived the evaluation.
    #
    #
    #     REJECTED
    #
    #         Candidate did not survive the evaluation.
    #
    #
    # VIABLE does NOT mean:
    #
    #
    #     SELECTED
    #
    #
    # There may be several viable candidates:
    #
    #
    #     Service A   VIABLE
    #
    #     Service B   VIABLE
    #
    #     Service C   VIABLE
    #
    #
    # RoutingDecision may ultimately select Service B.
    #
    #
    # Therefore:
    #
    #
    #     VIABLE != SELECTED
    #
    #
    #     CANDIDATE STATUS != FINAL ROUTING STATUS
    #
    #
    # The router determines candidate status.
    #
    # This model records that status.
    #
    # ----------------------------------------------------------------------

    status: RoutingCandidateStatus = Field(
        description=(
            "Outcome of viability evaluation for the candidate service."
        ),
    )

    # ----------------------------------------------------------------------
    # rejection_reason
    # ----------------------------------------------------------------------
    #
    # rejection_reason explains WHY a rejected candidate did not survive
    # viability evaluation.
    #
    #
    # SEIR-I examples:
    #
    #
    #     POLICY_DENIED
    #
    #     CAPABILITY_MISMATCH
    #
    #     SERVICE_UNAVAILABLE
    #
    #     NETWORK_UNAVAILABLE
    #
    #     UNKNOWN
    #
    #
    # These are routing-level summaries.
    #
    #
    # RoutingCandidate does NOT contain the complete:
    #
    #
    #     policy evaluation,
    #
    #     capability comparison,
    #
    #     service-health observation,
    #
    #     or network-state observation.
    #
    #
    # Those facts belong to their respective domains.
    #
    #
    # Therefore:
    #
    #
    #     REJECTION REASON
    #         !=
    #     COPY OF REJECTION EVIDENCE
    #
    #
    # Future telemetry / provenance may reference the underlying evidence
    # without turning RoutingCandidate into an audit-data warehouse.
    #
    #
    # rejection_reason is None when:
    #
    #
    #     status = VIABLE
    #
    #
    # and is required when:
    #
    #
    #     status = REJECTED
    #
    # ----------------------------------------------------------------------

    rejection_reason: RoutingRejectionReason | None = Field(
        default=None,
        description=(
            "Machine-readable reason the candidate was rejected, "
            "or None when the candidate is viable."
        ),
    )

    # ----------------------------------------------------------------------
    # Semantic validation
    # ----------------------------------------------------------------------
    #
    # Each field above can be individually type-valid while the complete
    # object is semantically contradictory.
    #
    #
    # Example:
    #
    #
    #     status = VIABLE
    #
    #     rejection_reason = POLICY_DENIED
    #
    #
    # Both enum values are individually valid.
    #
    # Together they make no sense.
    #
    #
    # Likewise:
    #
    #
    #     status = REJECTED
    #
    #     rejection_reason = None
    #
    #
    # fails to provide the required machine-readable explanation for the
    # rejection.
    #
    #
    # This is exactly where model-level validation belongs.
    #
    #
    #     FIELD VALID
    #         !=
    #     OBJECT SEMANTICALLY VALID
    #
    #
    #     VALIDATION SHOULD REPRESENT A RULE
    #
    #     VALIDATION SHOULD NOT BE DECORATION
    #
    # ----------------------------------------------------------------------

    @model_validator(mode="after")
    def validate_candidate_semantics(self) -> "RoutingCandidate":
        """
        Enforce semantic consistency between candidate status and
        rejection reason.
        """

        if self.status is RoutingCandidateStatus.VIABLE:
            if self.rejection_reason is not None:
                raise ValueError(
                    "Viable routing candidates cannot have a rejection reason."
                )

        elif self.status is RoutingCandidateStatus.REJECTED:
            if self.rejection_reason is None:
                raise ValueError(
                    "Rejected routing candidates must have a rejection reason."
                )

        return self


# ==========================================================================
# EXAMPLE — VIABLE CANDIDATE
# ==========================================================================
#
#     candidate = RoutingCandidate(
#         service_id="company-security-onprem-primary",
#         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#         status=RoutingCandidateStatus.VIABLE,
#     )
#
#
# This means:
#
#
#     "The company on-premises service survived the routing
#      viability evaluation."
#
#
# It does NOT mean:
#
#
#     "Agent 11 selected it."
#
#
#     VIABLE != SELECTED
#
# ==========================================================================


# ==========================================================================
# EXAMPLE — POLICY REJECTION
# ==========================================================================
#
#     candidate = RoutingCandidate(
#         service_id="external-reasoning-primary",
#         routing_domain=AIRoute.EXTERNAL_FM,
#         status=RoutingCandidateStatus.REJECTED,
#         rejection_reason=RoutingRejectionReason.POLICY_DENIED,
#     )
#
#
# The external service might be:
#
#
#     CAPABLE
#
#     HEALTHY
#
#     REACHABLE
#
#     CHEAP
#
#
# and still be:
#
#
#     REJECTED
#
#
# because:
#
#
#     POLICY = DENY
#
#
# Therefore:
#
#
#     REJECTED != FAILED
#
#     HEALTHY != PERMITTED
#
#     REACHABLE != AUTHORIZED
#
#     CHEAPER != PERMITTED
#
# ==========================================================================


# ==========================================================================
# EXAMPLE — CAPABILITY REJECTION
# ==========================================================================
#
#     candidate = RoutingCandidate(
#         service_id="company-cloud-light-reasoning",
#         routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#         status=RoutingCandidateStatus.REJECTED,
#         rejection_reason=(
#             RoutingRejectionReason.CAPABILITY_MISMATCH
#         ),
#     )
#
#
# Policy may permit the service.
#
# The service may be healthy.
#
# The network may reach it.
#
#
# But if the request requires:
#
#
#     SECURITY_ANALYSIS + HEAVY
#
#
# and the service cannot provide that requirement:
#
#
#     NOT VIABLE
#
#
# Therefore:
#
#
#     AUTHORIZED != CAPABLE
#
#     AVAILABLE != CAPABLE
#
#     REACHABLE != CAPABLE
#
# ==========================================================================


# ==========================================================================
# EXAMPLE — SERVICE UNAVAILABLE
# ==========================================================================
#
#     candidate = RoutingCandidate(
#         service_id="company-security-onprem-primary",
#         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#         status=RoutingCandidateStatus.REJECTED,
#         rejection_reason=(
#             RoutingRejectionReason.SERVICE_UNAVAILABLE
#         ),
#     )
#
#
# This does NOT mean the model lost its capabilities.
#
#
# It means the operational service cannot currently participate.
#
#
#     UNAVAILABLE != INCAPABLE
#
#
#     MODEL CAPABILITY != SERVICE AVAILABILITY
#
# ==========================================================================


# ==========================================================================
# EXAMPLE — NETWORK UNAVAILABLE
# ==========================================================================
#
#     candidate = RoutingCandidate(
#         service_id="company-security-onprem-primary",
#         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#         status=RoutingCandidateStatus.REJECTED,
#         rejection_reason=(
#             RoutingRejectionReason.NETWORK_UNAVAILABLE
#         ),
#     )
#
#
# The reasoning service may be perfectly healthy.
#
#
# Agent 11 simply lacks a viable network path to it.
#
#
# Therefore:
#
#
#     NETWORK UNAVAILABLE != SERVICE UNAVAILABLE
#
#
#     UNREACHABLE != UNHEALTHY
#
# ==========================================================================


# ==========================================================================
# EXAMPLE — UNKNOWN / INSUFFICIENT ROUTING EVIDENCE
# ==========================================================================
#
#     candidate = RoutingCandidate(
#         service_id="company-security-cloud-secondary",
#         routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#         status=RoutingCandidateStatus.REJECTED,
#         rejection_reason=RoutingRejectionReason.UNKNOWN,
#     )
#
#
# This means Agent 11 could not establish a more specific routing-level
# reason while still lacking sufficient evidence to allow the candidate
# to survive evaluation.
#
#
# It does NOT mean:
#
#
#     SERVICE_UNAVAILABLE
#
#
# unless service unavailability was actually established.
#
#
# It does NOT mean:
#
#
#     NETWORK_UNAVAILABLE
#
#
# unless network unavailability was actually established.
#
#
# Therefore:
#
#
#     UNKNOWN != UNAVAILABLE
#
#
#     CONSERVATIVE DECISION != FALSE OBSERVATION
#
# ==========================================================================


# ==========================================================================
# INVALID EXAMPLE — VIABLE WITH REJECTION REASON
# ==========================================================================
#
#     RoutingCandidate(
#         service_id="company-security-onprem-primary",
#         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#         status=RoutingCandidateStatus.VIABLE,
#         rejection_reason=RoutingRejectionReason.POLICY_DENIED,
#     )
#
#
# Invalid because:
#
#
#     VIABLE
#
# and:
#
#     POLICY_DENIED
#
# contradict each other.
#
#
# Pydantic rejects the object.
# ==========================================================================


# ==========================================================================
# INVALID EXAMPLE — REJECTED WITHOUT REASON
# ==========================================================================
#
#     RoutingCandidate(
#         service_id="company-security-onprem-primary",
#         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#         status=RoutingCandidateStatus.REJECTED,
#     )
#
#
# Invalid because:
#
#
#     REJECTED
#
# requires:
#
#     rejection_reason
#
#
# The routing contract requires a machine-readable reason for the
# candidate rejection.
# ==========================================================================


# ==========================================================================
# RoutingCandidate IS NOT AN EVIDENCE DUMP
# ==========================================================================
#
# Do NOT casually add:
#
#
#     endpoint
#
#     model
#
#     policy_document
#
#     policy_allowed
#
#     service_health_payload
#
#     network_path
#
#     bgp_route
#
#     latency_ms
#
#     cost_per_token
#
#     api_key
#
#     final_score
#
#     selected
#
#
# RoutingCandidate records the candidate evaluation OUTCOME.
#
#
# Other domains own the facts used to reach that outcome.
#
#
#     ROUTING CANDIDATE
#         !=
#     COPY OF EVERY INPUT USED BY ROUTING
#
#
# If future audit requirements need richer evidence linkage,
# use structured provenance / reference models.
#
#
# Do not turn this object into:
#
#
#     EnterpriseBlobObject.py
#
#
# Chewbacca does not get to solve architectural uncertainty by adding
# thirty-seven optional fields.
# ==========================================================================


# ==========================================================================
# CROSS-RESOURCE CONSISTENCY BELONGS ELSEWHERE
# ==========================================================================
#
# RoutingCandidate contains:
#
#
#     service_id
#
#     routing_domain
#
#
# A future registry may establish that:
#
#
#     service_id =
#         "company-security-onprem-primary"
#
#
# actually belongs to:
#
#
#     COMPANY_ONPREM_LLM
#
#
# Pydantic cannot establish that relationship from this object alone.
#
#
# That requires service-registry knowledge.
#
#
# Therefore:
#
#
#     VALID SERVICE ID != REGISTERED SERVICE
#
#
#     VALID ROUTING DOMAIN != CORRECT SERVICE ROUTING DOMAIN
#
#
#     DOMAIN VALIDATION != CROSS-RESOURCE RESOLUTION
#
#
# The routing orchestrator / registry integration is responsible for
# establishing cross-resource truth before constructing trustworthy
# candidate records.
# ==========================================================================


# ==========================================================================
# NATIVE PYDANTIC USAGE
# ==========================================================================
#
# RoutingCandidate remains an ordinary Pydantic domain model.
#
#
# Construct:
#
#
#     candidate = RoutingCandidate(...)
#
#
# Validate external data:
#
#
#     candidate = RoutingCandidate.model_validate(data)
#
#
# Serialize:
#
#
#     payload = candidate.model_dump()
#
#
# Serialize to JSON:
#
#
#     payload_json = candidate.model_dump_json()
#
#
# Agent 11 should not hide these operations behind unnecessary wrapper
# methods.
#
#
# Students should learn the Pydantic contract directly.
#
#
#     PYDANTIC DEFINES THE DOMAIN CONTRACT
#
#
#     ROUTING BEHAVIOR PRODUCES THE DOMAIN OBJECT
#
# ==========================================================================


# ==========================================================================
# PART I — RESPONSIBILITY MAP
# ==========================================================================
#
# AIService:
#
#     WHICH SERVICE EXISTS?
#
#
# Policy:
#
#     MAY THE REQUEST USE IT?
#
#
# Capability Evaluation:
#
#     CAN IT PERFORM THE REQUIRED WORK?
#
#
# Service State:
#
#     CAN IT CURRENTLY OPERATE?
#
#
# Network:
#
#     CAN IT CURRENTLY BE REACHED?
#
#
# RoutingCandidate:
#
#     WHAT HAPPENED TO THIS CANDIDATE
#     AFTER THOSE FACTS WERE EVALUATED?
#
#
# RoutingDecision:
#
#     WHAT DID AGENT 11 ULTIMATELY DECIDE?
#
#
# Each domain owns a different fact.
#
#
#     WHICH THING OWNS WHICH FACT?
#
# remains one of the central architectural questions in Agent 11.
# ==========================================================================


# ==========================================================================
# CHEWBACCA REVIEWS RoutingCandidate
# ==========================================================================
#
# Chewbacca:
#
#     "I found an AI service."
#
#
# Agent 11:
#
#     GOOD. EVALUATE IT.
#
#
# Chewbacca:
#
#     "It is reachable."
#
#
# Agent 11:
#
#     THAT IS ONE FACT.
#
#
# Chewbacca:
#
#     "It is healthy."
#
#
# Agent 11:
#
#     THAT IS ANOTHER FACT.
#
#
# Chewbacca:
#
#     "It is extremely cheap."
#
#
# Agent 11:
#
#     IRRELEVANT IF POLICY DENIES IT.
#
#
# Chewbacca:
#
#     "Policy denies it."
#
#
# Agent 11:
#
#     THEN RECORD:
#
#
#         REJECTED
#
#         POLICY_DENIED
#
#
# Chewbacca:
#
#     "So the service failed?"
#
#
# Agent 11:
#
#     NO.
#
#
#     THE SERVICE MAY BE PERFECTLY FUNCTIONAL.
#
#     IT WAS NOT A VIABLE CANDIDATE FOR THIS REQUEST.
#
#
# Chewbacca:
#
#     "Rejected does not mean failed?"
#
#
# Agent 11:
#
#     NOW YOU ARE ROUTING.
#
# ==========================================================================


# ==========================================================================
# PART I — FINAL INVARIANTS
# ==========================================================================
#
#     CANDIDATE EVALUATION != ROUTING DECISION
#
#
#     VIABLE != SELECTED
#
#
#     REJECTED != FAILED
#
#
#     OUTCOME != REASON
#
#
#     VIABLE => NO REJECTION REASON
#
#
#     REJECTED => REJECTION REASON REQUIRED
#
#
#     CANDIDATE REFERENCES SERVICE
#
#
#     CANDIDATE DOES NOT OWN SERVICE DEFINITION
#
#
#     VALID SERVICE ID != EXISTING REGISTERED SERVICE
#
#
#     DOMAIN VALIDATION != CROSS-RESOURCE RESOLUTION
#
#
#     ROUTING DOMAIN != CLOUD PROVIDER
#
#
#     ROUTING DOMAIN != DEPLOYMENT LOCATION
#
#
#     MODEL IDENTITY != DEPLOYMENT IDENTITY
#
#
#     UNKNOWN != UNAVAILABLE
#
#
#     FAIL CLOSED != FALSIFY OBSERVED STATE
#
#
#     DECISION BEHAVIOR != OBSERVED TRUTH
#
#
#     REJECTION REASON != COPY OF REJECTION EVIDENCE
#
#
#     AUTHORIZED != CAPABLE
#
#
#     AVAILABLE != CAPABLE
#
#
#     REACHABLE != CAPABLE
#
#
#     UNAVAILABLE != INCAPABLE
#
#
#     NETWORK UNAVAILABLE != SERVICE UNAVAILABLE
#
#
#     FIELD VALID != OBJECT SEMANTICALLY VALID
#
#
#     VALIDATION SHOULD REPRESENT A RULE
#
#
#     VALIDATION SHOULD NOT BE DECORATION
#
#
#     PYDANTIC DEFINES THE DOMAIN CONTRACT
#
#
#     ROUTING BEHAVIOR PRODUCES THE DOMAIN OBJECT
#
# ==========================================================================
# END PART I
# ==========================================================================


# ==========================================================================
# PART II — RoutingDecision DOMAIN CONTRACT
# ==========================================================================
#
# Part I modeled the outcome of evaluating ONE candidate:
#
#
#     RoutingCandidate
#
#         WHAT HAPPENED TO THIS CANDIDATE?
#
#
# Part II models the final routing outcome:
#
#
#     RoutingDecision
#
#         WHAT DID AGENT 11 ULTIMATELY DECIDE?
#
#
# Example:
#
#
#     AIRequest
#         |
#         v
#     Candidate Evaluation
#         |
#         +-- External FM -------- REJECTED
#         |
#         +-- Company Cloud ------ VIABLE
#         |
#         +-- Company On-Prem ---- VIABLE
#         |
#         v
#     RoutingDecision
#         |
#         +-- status = SELECTED
#         |
#         +-- selected_service_id
#         |
#         +-- selected_routing_domain
#
#
# RoutingDecision records the OUTCOME of routing.
#
# It does not perform routing.
#
#
#     ROUTING DECISION != ROUTING ENGINE
#
#
#     DECISION MODEL != DECISION BEHAVIOR
#
#
# RoutingDecision also does NOT:
#
#
#     evaluate policy,
#
#     compare model capabilities,
#
#     inspect service health,
#
#     inspect network paths,
#
#     calculate optimization scores,
#
#     execute fallback,
#
#     invoke an AI service,
#
#     or produce an AI response.
#
#
# Those behaviors belong to other Agent 11 components.
#
#
#     MODELS DESCRIBE.
#
#     ROUTERS DECIDE.
#
#     ORCHESTRATORS COORDINATE.
#
# ==========================================================================


# ==========================================================================
# ADDITIONAL PART II IMPORTS
# ==========================================================================
#
# Part I already imported:
#
#
#     Field
#     model_validator
#     Agent11BaseModel
#     AIRoute
#     RoutingCandidateStatus
#     RoutingRejectionReason
#
#
# Part II additionally requires:
#
#
#     UUID
#     RoutingStatus
#
#
# Add these to the import section at the TOP of routing.py:
#
#
#     from uuid import UUID
#
#
# and add RoutingStatus to:
#
#
#     from ..enums.routing_enums import (...)
#
#
# Do NOT place executable imports here in the middle of the final file.
#
# This section documents the additional Part II dependencies so the
# completed routing.py can maintain one clean import block at the top.
#
# ==========================================================================


# ==========================================================================
# RoutingStatus DESCRIBES THE FINAL ROUTING OUTCOME
# ==========================================================================
#
# RoutingStatus is defined in:
#
#
#     models/enums/routing_enums.py
#
#
# Current SEIR-I vocabulary:
#
#
#     SELECTED
#
#         Agent 11 selected a viable AI service.
#
#
#     BLOCKED
#
#         Policy prevented the request from obtaining an AI route.
#
#
#     NO_VIABLE_ROUTE
#
#         AI routing was appropriate and not categorically blocked,
#         but no operationally viable destination remained.
#
#
#     NULL
#
#         AI routing was intentionally unnecessary.
#
#
# These states are deliberately different.
#
#
#     BLOCKED != NO_VIABLE_ROUTE
#
#
#     NO_VIABLE_ROUTE != NULL
#
#
#     NULL != FAILURE
#
#
#     NO_VIABLE_ROUTE != ROUTER FAILURE
#
#
# Preserving these distinctions is essential for:
#
#
#     telemetry
#
#     troubleshooting
#
#     security analysis
#
#     availability analysis
#
#     auditability
#
#
# Part III expands these semantics in detail.
#
# ==========================================================================


class RoutingDecision(Agent11BaseModel):
    """
    Describes the final routing outcome for an AI request.

    RoutingDecision records whether Agent 11 selected a viable AI service,
    blocked routing, found no viable route, or intentionally performed no
    AI routing.

    It does not perform policy evaluation, capability matching, service
    health evaluation, network evaluation, route selection, AI invocation,
    or fallback behavior.
    """

    # ----------------------------------------------------------------------
    # request_id
    # ----------------------------------------------------------------------
    #
    # Every RoutingDecision belongs to an AIRequest.
    #
    #
    #     AIRequest
    #         |
    #         | request_id
    #         v
    #     RoutingDecision
    #
    #
    # AIRequest.request_id is a UUID.
    #
    # RoutingDecision preserves that type.
    #
    #
    #     AIRequest.request_id: UUID
    #             |
    #             v
    #     RoutingDecision.request_id: UUID
    #
    #
    # Do not degrade the identifier to str merely because UUID values
    # can eventually be serialized as strings.
    #
    #
    # The identifier allows Agent 11 to correlate:
    #
    #
    #     request
    #
    #     routing decision
    #
    #     eventual AI response
    #
    #     future telemetry
    #
    #
    # without embedding the entire AIRequest object.
    #
    #
    # Therefore:
    #
    #
    #     ROUTING DECISION REFERENCES REQUEST
    #
    #     ROUTING DECISION DOES NOT OWN REQUEST
    #
    #
    # SEIR-I does not currently require a separate:
    #
    #
    #     decision_id
    #
    #
    # Future retries, fallback history, multi-stage routing, distributed
    # tracing, or provenance may justify a separate routing-decision
    # identity.
    #
    # Do not add it until its semantics are actually required.
    #
    #
    #     FUTURE-AWARE != FUTURE-BLOATED
    #
    # ----------------------------------------------------------------------

    request_id: UUID = Field(
        description=(
            "Identifier of the AI request associated with this routing decision."
        ),
    )

    # ----------------------------------------------------------------------
    # status
    # ----------------------------------------------------------------------
    #
    # status answers:
    #
    #
    #     WHAT DID ROUTING ULTIMATELY PRODUCE?
    #
    #
    # Possible SEIR-I outcomes:
    #
    #
    #     SELECTED
    #
    #     BLOCKED
    #
    #     NO_VIABLE_ROUTE
    #
    #     NULL
    #
    #
    # This is NOT the same as RoutingCandidate.status.
    #
    #
    # RoutingCandidateStatus answers:
    #
    #
    #     WHAT HAPPENED TO ONE CANDIDATE?
    #
    #
    # RoutingStatus answers:
    #
    #
    #     WHAT HAPPENED TO THE ROUTING PROCESS?
    #
    #
    # Example:
    #
    #
    #     Candidate A = REJECTED
    #
    #     Candidate B = REJECTED
    #
    #     Candidate C = VIABLE
    #
    #
    #     RoutingDecision = SELECTED
    #
    #
    # Several rejected candidates do not mean routing failed.
    #
    #
    # Likewise:
    #
    #
    #     one POLICY_DENIED candidate
    #
    # does not automatically mean:
    #
    #     RoutingStatus.BLOCKED
    #
    #
    # another policy-permitted candidate may still survive.
    #
    #
    # Therefore:
    #
    #
    #     CANDIDATE STATUS != ROUTING STATUS
    #
    #
    #     CANDIDATE REJECTION != ROUTING FAILURE
    #
    # ----------------------------------------------------------------------

    status: RoutingStatus = Field(
        description="Final outcome of the Agent 11 routing process.",
    )

    # ----------------------------------------------------------------------
    # selected_service_id
    # ----------------------------------------------------------------------
    #
    # selected_service_id identifies the concrete AIService selected by
    # Agent 11.
    #
    #
    # It is required only when:
    #
    #
    #     status = SELECTED
    #
    #
    # For:
    #
    #
    #     BLOCKED
    #
    #     NO_VIABLE_ROUTE
    #
    #     NULL
    #
    #
    # there is no selected service.
    #
    #
    # Therefore:
    #
    #
    #     SELECTED
    #         =>
    #     SELECTED SERVICE REQUIRED
    #
    #
    #     NOT SELECTED
    #         =>
    #     SELECTED SERVICE FORBIDDEN
    #
    #
    # Example of a contradiction:
    #
    #
    #     status = BLOCKED
    #
    #     selected_service_id = "external-reasoning-primary"
    #
    #
    # Agent 11 cannot simultaneously say:
    #
    #
    #     "Routing was blocked."
    #
    # and:
    #
    #     "Here is the service I selected."
    #
    #
    # Pydantic should reject that object.
    #
    # ----------------------------------------------------------------------

    selected_service_id: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Identifier of the selected AI service when routing succeeds."
        ),
    )

    # ----------------------------------------------------------------------
    # selected_routing_domain
    # ----------------------------------------------------------------------
    #
    # selected_routing_domain records the Agent 11 routing domain
    # associated with the selected service.
    #
    #
    # Example:
    #
    #
    #     selected_service_id =
    #         "company-security-cloud-primary"
    #
    #
    #     selected_routing_domain =
    #         COMPANY_CLOUD_LLM
    #
    #
    # Technically, an orchestrator could later resolve service_id through
    # the service registry and rediscover the routing domain.
    #
    #
    # RoutingDecision intentionally preserves the routing domain directly.
    #
    #
    # This makes the decision easier to:
    #
    #
    #     understand
    #
    #     audit
    #
    #     log
    #
    #     serialize
    #
    #     troubleshoot
    #
    #     analyze historically
    #
    #
    # It also preserves what Agent 11 understood at decision time if the
    # service registry changes later.
    #
    #
    # Therefore:
    #
    #
    #     PRESERVE IMPORTANT DECISION CONTEXT
    #
    #     DO NOT COPY THE ENTIRE SERVICE DEFINITION
    #
    #
    # As established in Part I:
    #
    #
    #     COMPANY_CLOUD_LLM != AWS
    #
    #
    # A selected company cloud service may eventually run in:
    #
    #
    #     AWS
    #
    #     Azure
    #
    #     GCP
    #
    #     OCI
    #
    #     another cloud environment
    #
    #
    # selected_routing_domain records the Agent 11 destination class.
    #
    # It does not identify the deployment provider.
    #
    #
    # Therefore:
    #
    #
    #     SELECTED ROUTING DOMAIN != CLOUD PROVIDER
    #
    #
    #     ROUTING DOMAIN != DEPLOYMENT LOCATION
    #
    # ----------------------------------------------------------------------

    selected_routing_domain: AIRoute | None = Field(
        default=None,
        description=(
            "Routing domain of the selected AI service when routing succeeds."
        ),
    )

    # ----------------------------------------------------------------------
    # candidates
    # ----------------------------------------------------------------------
    #
    # candidates contains RoutingCandidate records explicitly evaluated
    # during the routing process.
    #
    #
    # Example:
    #
    #
    #     candidates = [
    #
    #         external service      REJECTED
    #
    #         company cloud         REJECTED
    #
    #         company on-prem       VIABLE
    #
    #     ]
    #
    #
    # This provides a compact and auditable summary of candidate
    # evaluation.
    #
    #
    # IMPORTANT:
    #
    #
    # candidates does NOT mean:
    #
    #
    #     EVERY AI SERVICE KNOWN TO AGENT 11
    #
    #
    # It means:
    #
    #
    #     CANDIDATES EXPLICITLY EVALUATED
    #
    #
    # An empty candidate list therefore does NOT necessarily mean:
    #
    #
    #     "Agent 11 has no AI services."
    #
    #
    # Example:
    #
    #
    #     status = NULL
    #
    #
    # may mean AI reasoning was unnecessary and candidate evaluation
    # never began.
    #
    #
    # Likewise, policy may eventually terminate some requests before
    # service-level candidate evaluation.
    #
    #
    # Therefore:
    #
    #
    #     NO CANDIDATE EVALUATION
    #         !=
    #     EMPTY AI PLATFORM
    #
    #
    #     CANDIDATES ACTUALLY EVALUATED
    #         !=
    #     EVERY SERVICE KNOWN TO AGENT 11
    #
    # ----------------------------------------------------------------------

    candidates: list[RoutingCandidate] = Field(
        default_factory=list,
        description=(
            "Routing candidates explicitly evaluated during the routing process."
        ),
    )

    # ----------------------------------------------------------------------
    # reason
    # ----------------------------------------------------------------------
    #
    # reason provides an optional human-readable explanation of the final
    # routing outcome.
    #
    #
    # Example:
    #
    #
    #     "Selected the company on-premises reasoning service after
    #      external routing was denied by policy."
    #
    #
    # This field is useful for:
    #
    #
    #     humans
    #
    #     operators
    #
    #     students
    #
    #     logs
    #
    #     troubleshooting
    #
    #
    # But machine behavior must NEVER depend on parsing this field.
    #
    #
    # BAD:
    #
    #
    #     if "policy" in decision.reason:
    #         ...
    #
    #
    # Chewbacca.
    #
    # No.
    #
    #
    # Machine semantics belong to:
    #
    #
    #     RoutingStatus
    #
    #     RoutingCandidateStatus
    #
    #     RoutingRejectionReason
    #
    #
    # Therefore:
    #
    #
    #     HUMAN EXPLANATION != MACHINE CONTRACT
    #
    #
    #     REASON TEXT != ROUTING SEMANTICS
    #
    # ----------------------------------------------------------------------

    reason: str | None = Field(
        default=None,
        description=(
            "Optional human-readable explanation of the routing decision."
        ),
    )

    # ----------------------------------------------------------------------
    # Semantic validation
    # ----------------------------------------------------------------------
    #
    # RoutingDecision contains several genuine cross-field invariants.
    #
    #
    # First:
    #
    #
    #     status = SELECTED
    #
    # requires:
    #
    #
    #     selected_service_id
    #
    #     selected_routing_domain
    #
    #
    # Second:
    #
    #
    #     BLOCKED
    #
    #     NO_VIABLE_ROUTE
    #
    #     NULL
    #
    # require:
    #
    #
    #     selected_service_id = None
    #
    #     selected_routing_domain = None
    #
    #
    # Third:
    #
    #
    # when candidate records are present for a SELECTED decision:
    #
    #
    #     the selected service must appear among those candidates,
    #
    #     the selected candidate must be VIABLE,
    #
    #     and its routing domain must match selected_routing_domain.
    #
    #
    # Fourth:
    #
    #
    # each service_id may appear only once in the summarized candidate
    # list for one RoutingDecision.
    #
    #
    # These are domain consistency rules.
    #
    #
    # They do NOT calculate the routing decision.
    #
    #
    #     VALIDATION CHECKS THE CONTRACT
    #
    #     VALIDATION DOES NOT BECOME THE ROUTER
    #
    # ----------------------------------------------------------------------

    @model_validator(mode="after")
    def validate_routing_semantics(self) -> "RoutingDecision":
        """
        Enforce semantic consistency between routing status,
        selected destination, and evaluated candidates.
        """

        # ------------------------------------------------------------------
        # One summarized candidate outcome per service.
        # ------------------------------------------------------------------
        #
        # SEIR-I RoutingDecision represents a summarized routing outcome.
        #
        # Therefore this would be ambiguous:
        #
        #
        #     service-A   VIABLE
        #
        #     service-A   REJECTED
        #
        #
        # Did the service change state?
        #
        # Was it retried?
        #
        # Was it evaluated at two different times?
        #
        # Was this fallback?
        #
        #
        # Those are future event-history questions.
        #
        # SEIR-I does not encode them as duplicate candidate records.
        #
        # ------------------------------------------------------------------

        candidate_service_ids = [
            candidate.service_id
            for candidate in self.candidates
        ]

        if len(candidate_service_ids) != len(set(candidate_service_ids)):
            raise ValueError(
                "Routing candidates must have unique service identifiers."
            )

        # ------------------------------------------------------------------
        # SELECTED requires a concrete destination.
        # ------------------------------------------------------------------

        if self.status is RoutingStatus.SELECTED:
            if self.selected_service_id is None:
                raise ValueError(
                    "Selected routing decisions must identify a selected service."
                )

            if self.selected_routing_domain is None:
                raise ValueError(
                    "Selected routing decisions must identify a routing domain."
                )

            # --------------------------------------------------------------
            # Candidate records are optional.
            # --------------------------------------------------------------
            #
            # RoutingDecision may preserve only the final routing outcome
            # while detailed candidate telemetry is stored elsewhere or is
            # unavailable.
            #
            # Therefore:
            #
            #
            #     SELECTED
            #         +
            #     candidates = []
            #
            #
            # is allowed.
            #
            #
            # However:
            #
            # if candidate records ARE present, they must agree with the
            # selected destination.
            #
            #
            #     ABSENT EVIDENCE RECORD
            #         !=
            #     CONTRADICTORY EVIDENCE RECORD
            #
            #
            # Agent 11 rejects contradiction.
            #
            # Agent 11 does not invent evidence.
            #
            # --------------------------------------------------------------

            if self.candidates:
                selected_candidates = [
                    candidate
                    for candidate in self.candidates
                    if candidate.service_id == self.selected_service_id
                ]

                if not selected_candidates:
                    raise ValueError(
                        "The selected service must appear among evaluated "
                        "routing candidates when candidate records are present."
                    )

                selected_candidate = selected_candidates[0]

                # ----------------------------------------------------------
                # A rejected candidate cannot become the selected service.
                # ----------------------------------------------------------
                #
                # This prevents contradictions such as:
                #
                #
                #     candidate:
                #         REJECTED
                #         POLICY_DENIED
                #
                #
                #     decision:
                #         SELECTED
                #
                #
                # The domain contract must make that impossible.
                #
                # ----------------------------------------------------------

                if (
                    selected_candidate.status
                    is not RoutingCandidateStatus.VIABLE
                ):
                    raise ValueError(
                        "The selected service must be a viable routing candidate."
                    )

                # ----------------------------------------------------------
                # The selected routing domain must agree with the candidate.
                # ----------------------------------------------------------
                #
                # Example contradiction:
                #
                #
                #     selected_service_id =
                #         "company-security-onprem-primary"
                #
                #
                #     selected_routing_domain =
                #         EXTERNAL_FM
                #
                #
                # while the candidate record says:
                #
                #
                #     routing_domain =
                #         COMPANY_ONPREM_LLM
                #
                #
                # The service and domain recorded in the decision must agree
                # with the candidate evidence when that evidence is present.
                #
                # ----------------------------------------------------------

                if (
                    selected_candidate.routing_domain
                    is not self.selected_routing_domain
                ):
                    raise ValueError(
                        "The selected routing domain must match the routing "
                        "domain recorded for the selected candidate."
                    )

        # ------------------------------------------------------------------
        # Non-selected outcomes cannot identify a selected destination.
        # ------------------------------------------------------------------
        #
        # BLOCKED:
        #
        #     policy prevented a final AI route.
        #
        #
        # NO_VIABLE_ROUTE:
        #
        #     no viable destination remained.
        #
        #
        # NULL:
        #
        #     AI routing was intentionally unnecessary.
        #
        #
        # None of these outcomes can simultaneously claim that a service
        # was selected.
        #
        # ------------------------------------------------------------------

        else:
            if self.selected_service_id is not None:
                raise ValueError(
                    "Non-selected routing decisions cannot identify "
                    "a selected service."
                )

            if self.selected_routing_domain is not None:
                raise ValueError(
                    "Non-selected routing decisions cannot identify "
                    "a selected routing domain."
                )

        return self


# ==========================================================================
# WHY RoutingDecision HAS A MODEL VALIDATOR
# ==========================================================================
#
# Consider:
#
#
#     status = SELECTED
#
#     selected_service_id = None
#
#
# Each field may individually contain a valid type.
#
# Together the object is incomplete.
#
#
# Or:
#
#
#     status = BLOCKED
#
#     selected_service_id = "external-reasoning-primary"
#
#
# Again, the individual field types are valid.
#
# The object contradicts itself.
#
#
# Or:
#
#
#     selected candidate = REJECTED
#
#     final status       = SELECTED
#
#
# The candidate and decision records contradict each other.
#
#
# Therefore:
#
#
#     FIELD VALID
#         !=
#     OBJECT SEMANTICALLY VALID
#
#
# This is precisely where:
#
#
#     @model_validator(mode="after")
#
#
# belongs.
#
#
#     VALIDATION SHOULD REPRESENT A RULE
#
#     VALIDATION SHOULD NOT BE DECORATION
#
# ==========================================================================


# ==========================================================================
# WHAT RoutingDecision VALIDATION DOES ESTABLISH
# ==========================================================================
#
# The validator establishes internal consistency.
#
#
# It can establish:
#
#
#     selected fields are present when required,
#
#     selected fields are absent when forbidden,
#
#     candidate service IDs are unique,
#
#     a recorded selected candidate is viable,
#
#     selected routing-domain information agrees with the selected
#     candidate when candidate records are present.
#
#
# These are facts available inside the RoutingDecision object.
# ==========================================================================


# ==========================================================================
# WHAT RoutingDecision VALIDATION DOES NOT ESTABLISH
# ==========================================================================
#
# The validator cannot establish:
#
#
#     whether service_id exists in the service registry,
#
#     whether the model actually has the required capability,
#
#     whether policy was evaluated correctly,
#
#     whether organizational policy was loaded correctly,
#
#     whether user policy was applied correctly,
#
#     whether the service is actually healthy,
#
#     whether the network path actually exists,
#
#     whether BGP can reach the destination,
#
#     whether the service has sufficient capacity,
#
#     whether the selected service was optimal,
#
#     whether the selected service will accept the request,
#
#     whether inference will succeed,
#
#     whether the AI response will be correct,
#
#     or whether an eventual action is authorized.
#
#
# Therefore:
#
#
#     INTERNALLY CONSISTENT DECISION
#         !=
#     CORRECTLY COMPUTED DECISION
#
#
# Pydantic validates the decision contract.
#
# Routing behavior produces the decision.
#
#
#     PYDANTIC != ROUTING ENGINE
#
# ==========================================================================


# ==========================================================================
# CANDIDATE RECORDS ARE OPTIONAL
# ==========================================================================
#
# This is valid:
#
#
#     RoutingDecision(
#         request_id=request.request_id,
#         status=RoutingStatus.SELECTED,
#         selected_service_id="company-security-cloud-primary",
#         selected_routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#         candidates=[],
#     )
#
#
# It means:
#
#
#     Agent 11 recorded the final routing outcome,
#
# but:
#
#     candidate-level evaluation records are not present here.
#
#
# Candidate evidence might:
#
#
#     not have been retained,
#
#     be stored in telemetry,
#
#     be represented by future provenance records,
#
#     or come from a routing implementation that emits only the final
#     decision contract.
#
#
# RoutingDecision should not fabricate candidate evidence merely to make
# its own object larger.
#
#
# Therefore:
#
#
#     ABSENT EVIDENCE RECORD
#         !=
#     CONTRADICTORY EVIDENCE RECORD
#
#
# When candidate records are absent:
#
#
#     do not invent them.
#
#
# When candidate records are present:
#
#
#     require consistency.
# ==========================================================================


# ==========================================================================
# EXAMPLE — SELECTED
# ==========================================================================
#
#     decision = RoutingDecision(
#         request_id=request.request_id,
#         status=RoutingStatus.SELECTED,
#         selected_service_id="company-security-onprem-primary",
#         selected_routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#         candidates=[
#             RoutingCandidate(
#                 service_id="external-reasoning-primary",
#                 routing_domain=AIRoute.EXTERNAL_FM,
#                 status=RoutingCandidateStatus.REJECTED,
#                 rejection_reason=(
#                     RoutingRejectionReason.POLICY_DENIED
#                 ),
#             ),
#             RoutingCandidate(
#                 service_id="company-security-cloud-primary",
#                 routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#                 status=RoutingCandidateStatus.REJECTED,
#                 rejection_reason=(
#                     RoutingRejectionReason.CAPABILITY_MISMATCH
#                 ),
#             ),
#             RoutingCandidate(
#                 service_id="company-security-onprem-primary",
#                 routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#                 status=RoutingCandidateStatus.VIABLE,
#             ),
#         ],
#         reason=(
#             "Selected the company on-premises reasoning service "
#             "after candidate viability evaluation."
#         ),
#     )
#
#
# Result:
#
#
#     SELECTED
#         |
#         v
#     company-security-onprem-primary
#         |
#         v
#     COMPANY_ONPREM_LLM
#
#
# Two candidates were rejected.
#
# One survived.
#
# Agent 11 selected the viable service.
#
#
#     REJECTED CANDIDATES != ROUTING FAILURE
#
# ==========================================================================


# ==========================================================================
# EXAMPLE — SELECTED WITH MULTIPLE VIABLE CANDIDATES
# ==========================================================================
#
#     decision = RoutingDecision(
#         request_id=request.request_id,
#         status=RoutingStatus.SELECTED,
#         selected_service_id="company-security-cloud-primary",
#         selected_routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#         candidates=[
#             RoutingCandidate(
#                 service_id="company-security-cloud-primary",
#                 routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#                 status=RoutingCandidateStatus.VIABLE,
#             ),
#             RoutingCandidate(
#                 service_id="company-security-onprem-primary",
#                 routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#                 status=RoutingCandidateStatus.VIABLE,
#             ),
#         ],
#     )
#
#
# Both candidates survived viability evaluation.
#
#
# Agent 11 selected:
#
#
#     company-security-cloud-primary
#
#
# This demonstrates:
#
#
#     VIABLE != SELECTED
#
#
# Viability determines membership in the viable set.
#
# Selection determines which member of that set is chosen.
# ==========================================================================


# ==========================================================================
# EXAMPLE — BLOCKED
# ==========================================================================
#
#     decision = RoutingDecision(
#         request_id=request.request_id,
#         status=RoutingStatus.BLOCKED,
#         candidates=[
#             RoutingCandidate(
#                 service_id="external-reasoning-primary",
#                 routing_domain=AIRoute.EXTERNAL_FM,
#                 status=RoutingCandidateStatus.REJECTED,
#                 rejection_reason=(
#                     RoutingRejectionReason.POLICY_DENIED
#                 ),
#             ),
#         ],
#         reason=(
#             "Policy prevented the request from obtaining "
#             "a permitted AI route."
#         ),
#     )
#
#
# Notice:
#
#
#     selected_service_id = None
#
#     selected_routing_domain = None
#
#
# A blocked routing decision does not pretend a destination was selected.
#
#
# IMPORTANT:
#
#
# One candidate receiving POLICY_DENIED does not automatically imply
# RoutingStatus.BLOCKED.
#
#
# Another permitted candidate may still survive.
#
#
# Part III defines the final BLOCKED semantics more precisely.
# ==========================================================================


# ==========================================================================
# EXAMPLE — NO_VIABLE_ROUTE
# ==========================================================================
#
#     decision = RoutingDecision(
#         request_id=request.request_id,
#         status=RoutingStatus.NO_VIABLE_ROUTE,
#         candidates=[
#             RoutingCandidate(
#                 service_id="company-security-cloud-primary",
#                 routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#                 status=RoutingCandidateStatus.REJECTED,
#                 rejection_reason=(
#                     RoutingRejectionReason.SERVICE_UNAVAILABLE
#                 ),
#             ),
#             RoutingCandidate(
#                 service_id="company-security-onprem-primary",
#                 routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#                 status=RoutingCandidateStatus.REJECTED,
#                 rejection_reason=(
#                     RoutingRejectionReason.NETWORK_UNAVAILABLE
#                 ),
#             ),
#         ],
#         reason="No evaluated AI service remained viable.",
#     )
#
#
# This is not necessarily a router malfunction.
#
#
# The router may have worked perfectly and correctly concluded:
#
#
#     THERE IS NO COMPLIANT, OPERATIONALLY VIABLE ROUTE.
#
#
# Sometimes:
#
#
#     NO ROUTE
#
# is:
#
#     THE CORRECT ROUTING ANSWER
#
#
#     NO_VIABLE_ROUTE != ROUTER FAILURE
# ==========================================================================


# ==========================================================================
# EXAMPLE — NULL
# ==========================================================================
#
#     decision = RoutingDecision(
#         request_id=request.request_id,
#         status=RoutingStatus.NULL,
#         reason="The request did not require AI reasoning.",
#     )
#
#
# No service was selected.
#
# No routing failure occurred.
#
# Candidate evaluation may never have started.
#
#
# Therefore:
#
#
#     NULL != FAILURE
#
#
#     NULL != NO_VIABLE_ROUTE
#
#
#     NULL != BLOCKED
#
#
#     NO CANDIDATES != NO AI SERVICES
# ==========================================================================


# ==========================================================================
# INVALID — SELECTED WITHOUT SERVICE
# ==========================================================================
#
#     RoutingDecision(
#         request_id=request.request_id,
#         status=RoutingStatus.SELECTED,
#         selected_routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#     )
#
#
# Invalid because:
#
#
#     SELECTED
#
# requires:
#
#
#     selected_service_id
#
#
# "We selected something."
#
# "What?"
#
# "Unknown."
#
#
# Chewbacca has not completed the routing decision.
# ==========================================================================


# ==========================================================================
# INVALID — SELECTED WITHOUT ROUTING DOMAIN
# ==========================================================================
#
#     RoutingDecision(
#         request_id=request.request_id,
#         status=RoutingStatus.SELECTED,
#         selected_service_id="company-security-onprem-primary",
#     )
#
#
# Invalid because:
#
#
#     SELECTED
#
# requires:
#
#
#     selected_routing_domain
#
#
# Agent 11 preserves both:
#
#
#     precise service identity
#
# and:
#
#     routing-domain context
# ==========================================================================


# ==========================================================================
# INVALID — BLOCKED WITH SELECTED DESTINATION
# ==========================================================================
#
#     RoutingDecision(
#         request_id=request.request_id,
#         status=RoutingStatus.BLOCKED,
#         selected_service_id="external-reasoning-primary",
#         selected_routing_domain=AIRoute.EXTERNAL_FM,
#     )
#
#
# Invalid because:
#
#
#     BLOCKED
#
# and:
#
#     SELECTED DESTINATION
#
# are contradictory final outcomes.
#
#
#     BLOCKED => NO SELECTED DESTINATION
# ==========================================================================


# ==========================================================================
# INVALID — NO_VIABLE_ROUTE WITH SELECTED DESTINATION
# ==========================================================================
#
#     RoutingDecision(
#         request_id=request.request_id,
#         status=RoutingStatus.NO_VIABLE_ROUTE,
#         selected_service_id="company-security-cloud-primary",
#         selected_routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#     )
#
#
# Invalid.
#
#
# If there is:
#
#
#     NO VIABLE ROUTE
#
#
# then there cannot simultaneously be:
#
#
#     A SELECTED ROUTE
#
#
#     NO_VIABLE_ROUTE => NO SELECTED DESTINATION
# ==========================================================================


# ==========================================================================
# INVALID — NULL WITH SELECTED DESTINATION
# ==========================================================================
#
#     RoutingDecision(
#         request_id=request.request_id,
#         status=RoutingStatus.NULL,
#         selected_service_id="company-security-cloud-primary",
#         selected_routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#     )
#
#
# Invalid.
#
#
# NULL means AI routing was intentionally unnecessary.
#
#
# Therefore:
#
#
#     NULL => NO SELECTED DESTINATION
# ==========================================================================


# ==========================================================================
# INVALID — SELECTED CANDIDATE WAS REJECTED
# ==========================================================================
#
#     RoutingDecision(
#         request_id=request.request_id,
#         status=RoutingStatus.SELECTED,
#         selected_service_id="external-reasoning-primary",
#         selected_routing_domain=AIRoute.EXTERNAL_FM,
#         candidates=[
#             RoutingCandidate(
#                 service_id="external-reasoning-primary",
#                 routing_domain=AIRoute.EXTERNAL_FM,
#                 status=RoutingCandidateStatus.REJECTED,
#                 rejection_reason=(
#                     RoutingRejectionReason.POLICY_DENIED
#                 ),
#             ),
#         ],
#     )
#
#
# Translation:
#
#
#     "Policy rejected this service."
#
#                         AND
#
#     "We selected this service."
#
#
# No.
#
#
# This is exactly the kind of contradiction the domain contract exists
# to prevent.
#
#
#     REJECTED CANDIDATE != SELECTABLE CANDIDATE
#
#
#     POLICY_DENIED + SELECTED
#         =
#     INVALID DECISION CONTRACT
# ==========================================================================


# ==========================================================================
# INVALID — SELECTED SERVICE MISSING FROM RECORDED CANDIDATES
# ==========================================================================
#
#     RoutingDecision(
#         request_id=request.request_id,
#         status=RoutingStatus.SELECTED,
#         selected_service_id="service-C",
#         selected_routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#         candidates=[
#             RoutingCandidate(
#                 service_id="service-A",
#                 routing_domain=AIRoute.EXTERNAL_FM,
#                 status=RoutingCandidateStatus.REJECTED,
#                 rejection_reason=(
#                     RoutingRejectionReason.POLICY_DENIED
#                 ),
#             ),
#             RoutingCandidate(
#                 service_id="service-B",
#                 routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#                 status=RoutingCandidateStatus.VIABLE,
#             ),
#         ],
#     )
#
#
# Invalid.
#
#
# Candidate records were supplied.
#
# They claim Agent 11 evaluated:
#
#
#     service-A
#     service-B
#
#
# but the final decision claims:
#
#
#     service-C
#
#
# was selected.
#
#
# If candidate evidence is present, the selected service must appear in
# that evidence.
#
#
#     RECORDED SELECTION MUST AGREE WITH RECORDED CANDIDATES
# ==========================================================================


# ==========================================================================
# INVALID — SELECTED ROUTING DOMAIN DOES NOT MATCH CANDIDATE
# ==========================================================================
#
# Candidate:
#
#
#     service_id =
#         "company-security-onprem-primary"
#
#
#     routing_domain =
#         COMPANY_ONPREM_LLM
#
#
# Decision:
#
#
#     selected_service_id =
#         "company-security-onprem-primary"
#
#
#     selected_routing_domain =
#         EXTERNAL_FM
#
#
# Invalid.
#
#
# The decision record contradicts its candidate record.
#
#
#     SELECTED ROUTING DOMAIN
#         MUST MATCH
#     SELECTED CANDIDATE ROUTING DOMAIN
# ==========================================================================


# ==========================================================================
# INVALID — DUPLICATE SERVICE CANDIDATES
# ==========================================================================
#
#     candidates = [
#
#         service-A   VIABLE
#
#         service-A   REJECTED
#
#     ]
#
#
# What happened?
#
#
# Did the service state change?
#
# Was it evaluated twice?
#
# Was this a retry?
#
# Was this fallback?
#
# Were the observations collected at different times?
#
#
# SEIR-I RoutingDecision does not attempt to encode that history.
#
#
# Therefore:
#
#
#     ONE SERVICE
#         =>
#     ONE SUMMARIZED CANDIDATE OUTCOME
#     PER RoutingDecision
#
#
# Future SEIR-II may introduce concepts such as:
#
#
#     CandidateEvaluationEvent
#
#     RoutingAttempt
#
#     RoutingHistory
#
#
# if temporal re-evaluation requires richer representation.
#
#
#     SUMMARY STATE != EVENT HISTORY
# ==========================================================================


# ==========================================================================
# ROUTING DOMAIN CONSISTENCY HAS TWO LEVELS
# ==========================================================================
#
# RoutingDecision can validate:
#
#
#     selected_routing_domain
#         ==
#     selected candidate.routing_domain
#
#
# because both facts exist inside this decision object.
#
#
# RoutingDecision cannot independently validate:
#
#
#     candidate.routing_domain
#         ==
#     routing domain registered for candidate.service_id
#
#
# because the service registry is outside this model.
#
#
# Therefore:
#
#
#     INTERNAL OBJECT CONSISTENCY
#
# can be validated here.
#
#
#     EXTERNAL RESOURCE CONSISTENCY
#
# must be validated by the appropriate registry / orchestrator.
#
#
# This is another example of:
#
#
#     DOMAIN VALIDATION != CROSS-RESOURCE RESOLUTION
# ==========================================================================


# ==========================================================================
# ROUTING DECISION != COPY OF EVERY ROUTING INPUT
# ==========================================================================
#
# Do NOT casually add:
#
#
#     model object
#
#     endpoint
#
#     credentials
#
#     policy document
#
#     complete PolicyDecision
#
#     service health payload
#
#     network path object
#
#     BGP prefix
#
#     SD-WAN state
#
#     latency measurement
#
#     GPU utilization
#
#     queue depth
#
#     token cost
#
#     provider pricing
#
#     benchmark result
#
#     final opaque score
#
#
# merely because routing may have consumed those facts.
#
#
# RoutingDecision records:
#
#
#     WHAT AGENT 11 DECIDED
#
#
# It does not duplicate:
#
#
#     EVERYTHING AGENT 11 KNEW
#
#
# Future provenance and telemetry may reference detailed evidence through
# neighboring contracts.
#
#
#     ROUTING DECISION
#         !=
#     COPY OF EVERY INPUT USED TO MAKE THE DECISION
# ==========================================================================


# ==========================================================================
# NATIVE PYDANTIC USAGE
# ==========================================================================
#
# RoutingDecision remains an ordinary Pydantic domain model.
#
#
# Construct:
#
#
#     decision = RoutingDecision(...)
#
#
# Validate external data:
#
#
#     decision = RoutingDecision.model_validate(data)
#
#
# Serialize:
#
#
#     payload = decision.model_dump()
#
#
# Serialize to JSON:
#
#
#     payload_json = decision.model_dump_json()
#
#
# Agent 11 should not hide native Pydantic behavior behind unnecessary
# convenience wrappers.
#
#
# The purpose of these models is partly to make the domain contract
# explicit and inspectable.
#
#
#     PYDANTIC DEFINES THE DOMAIN CONTRACT
#
#
#     ROUTING BEHAVIOR PRODUCES THE DOMAIN OBJECT
# ==========================================================================


# ==========================================================================
# PART II — RESPONSIBILITY MAP
# ==========================================================================
#
# RoutingCandidate:
#
#     WHAT HAPPENED TO ONE CANDIDATE?
#
#
# RoutingDecision:
#
#     WHAT DID AGENT 11 ULTIMATELY DECIDE?
#
#
# Router:
#
#     HOW WAS THE DECISION COMPUTED?
#
#
# Policy:
#
#     WHICH DESTINATIONS ARE PERMITTED?
#
#
# Capability:
#
#     WHICH RESOURCES CAN PERFORM THE WORK?
#
#
# Service Runtime:
#
#     WHICH SERVICES CAN CURRENTLY OPERATE?
#
#
# Network:
#
#     WHICH DESTINATIONS CAN CURRENTLY BE REACHED?
#
#
# Telemetry:
#
#     WHAT SHOULD BE RECORDED ABOUT THE DECISION?
#
#
# Models describe the result.
#
# Behavior computes the result.
#
#
#     ROUTING DECISION != ROUTER
#
# ==========================================================================


# ==========================================================================
# CHEWBACCA REVIEWS RoutingDecision
# ==========================================================================
#
# Chewbacca:
#
#     "I selected company-security-onprem-primary."
#
#
# Agent 11:
#
#     ROUTING DOMAIN?
#
#
# Chewbacca:
#
#     "COMPANY_ONPREM_LLM."
#
#
# Agent 11:
#
#     GOOD.
#
#
# Chewbacca:
#
#     "The candidate record says it was rejected."
#
#
# Agent 11:
#
#     THEN YOU DID NOT SELECT IT.
#
#
# Chewbacca:
#
#     "But I really like that service."
#
#
# Agent 11:
#
#     THE VALIDATOR DOES NOT CARE ABOUT YOUR FEELINGS.
#
#
# Chewbacca:
#
#     "Fine. External FM was policy denied,
#      cloud was unavailable,
#      on-prem was viable."
#
#
# Agent 11:
#
#     AND WHICH SERVICE DID YOU SELECT?
#
#
# Chewbacca:
#
#     "On-prem."
#
#
# Agent 11:
#
#     NOW THE DECISION IS INTERNALLY CONSISTENT.
#
#
# Chewbacca:
#
#     "So Pydantic proved the router was correct?"
#
#
# Agent 11:
#
#     NO.
#
#
#     PYDANTIC PROVED THAT YOUR DECISION OBJECT
#     DOES NOT CONTRADICT ITSELF.
#
#
# Chewbacca:
#
#     "Ah."
#
#
# Agent 11:
#
#     NOW YOU ARE LEARNING THE DIFFERENCE BETWEEN
#     VALIDATION AND REASONING.
#
# ==========================================================================


# ==========================================================================
# PART II — FINAL INVARIANTS
# ==========================================================================
#
#     ROUTING DECISION != ROUTING ENGINE
#
#
#     DECISION MODEL != DECISION BEHAVIOR
#
#
#     ROUTING DECISION REFERENCES REQUEST
#
#
#     ROUTING DECISION DOES NOT OWN REQUEST
#
#
#     REQUEST IDENTITY != ROUTING BEHAVIOR
#
#
#     CANDIDATE STATUS != ROUTING STATUS
#
#
#     CANDIDATE REJECTION != ROUTING FAILURE
#
#
#     SELECTED => SELECTED SERVICE REQUIRED
#
#
#     SELECTED => SELECTED ROUTING DOMAIN REQUIRED
#
#
#     NOT SELECTED => NO SELECTED SERVICE
#
#
#     NOT SELECTED => NO SELECTED ROUTING DOMAIN
#
#
#     SELECTED CANDIDATE MUST BE VIABLE
#
#
#     SELECTED ROUTING DOMAIN
#         MUST MATCH
#     SELECTED CANDIDATE ROUTING DOMAIN
#
#
#     RECORDED SELECTION
#         MUST AGREE WITH
#     RECORDED CANDIDATES
#
#
#     ONE SERVICE
#         =>
#     ONE SUMMARIZED CANDIDATE OUTCOME
#     PER RoutingDecision
#
#
#     SUMMARY STATE != EVENT HISTORY
#
#
#     NO CANDIDATE EVALUATION != EMPTY AI PLATFORM
#
#
#     CANDIDATES ACTUALLY EVALUATED
#         !=
#     EVERY SERVICE KNOWN TO AGENT 11
#
#
#     ABSENT EVIDENCE RECORD
#         !=
#     CONTRADICTORY EVIDENCE RECORD
#
#
#     HUMAN EXPLANATION != MACHINE CONTRACT
#
#
#     REASON TEXT != ROUTING SEMANTICS
#
#
#     INTERNALLY CONSISTENT DECISION
#         !=
#     CORRECTLY COMPUTED DECISION
#
#
#     INTERNAL OBJECT CONSISTENCY
#         !=
#     EXTERNAL RESOURCE CONSISTENCY
#
#
#     DOMAIN VALIDATION != CROSS-RESOURCE RESOLUTION
#
#
#     VALIDATION DOES NOT PERFORM ROUTING
#
#
#     VALIDATION DOES NOT PERFORM POLICY
#
#
#     VALIDATION DOES NOT PERFORM CAPABILITY MATCHING
#
#
#     VALIDATION DOES NOT PERFORM NETWORK ANALYSIS
#
#
#     VALIDATION DOES NOT PROVE OPTIMALITY
#
#
#     SELECTED ROUTING DOMAIN != CLOUD PROVIDER
#
#
#     ROUTING DOMAIN != DEPLOYMENT LOCATION
#
#
#     ROUTING DECISION
#         !=
#     COPY OF EVERY INPUT USED TO MAKE THE DECISION
#
#
#     FIELD VALID != OBJECT SEMANTICALLY VALID
#
#
#     VALIDATION SHOULD REPRESENT A RULE
#
#
#     VALIDATION SHOULD NOT BE DECORATION
#
#
#     PYDANTIC DEFINES THE DOMAIN CONTRACT
#
#
#     ROUTING BEHAVIOR PRODUCES THE DOMAIN OBJECT
#
# ==========================================================================
# END PART II
# ==========================================================================

# ==========================================================================
# PART III — ROUTING SEMANTICS AND BEHAVIORAL CONTRACT
# ==========================================================================
#
# Parts I and II defined the executable routing domain contracts:
#
#
#     RoutingCandidate
#
#         WHAT HAPPENED TO ONE CANDIDATE?
#
#
#     RoutingDecision
#
#         WHAT DID AGENT 11 ULTIMATELY DECIDE?
#
#
# Part III defines the architectural semantics surrounding those models.
#
#
# THIS SECTION IS DOCUMENTATION ONLY.
#
#
# It intentionally introduces:
#
#
#     NO new Pydantic models
#
#     NO new fields
#
#     NO new validators
#
#     NO new enums
#
#     NO routing behavior
#
#
# Routing behavior belongs in:
#
#
#     routing/
#         router.py
#         model_router.py
#         fallback.py
#         network_context.py
#         orchestrator.py
#
#
# Part III exists so those future implementations share the same
# vocabulary and behavioral contract.
#
#
#     MODELS DESCRIBE THE DECISION.
#
#     ROUTING COMPONENTS PRODUCE THE DECISION.
#
# ==========================================================================


# ==========================================================================
# THE FUNDAMENTAL SEIR-I VIABILITY EQUATION
# ==========================================================================
#
# A candidate AI service is viable only when all required viability
# conditions are satisfied.
#
#
#                         VIABLE ROUTE
#
#                              =
#
#                       POLICY PERMITTED
#
#                              +
#
#                       SERVICE CAPABLE
#
#                              +
#
#                      SERVICE AVAILABLE
#
#                              +
#
#                        PATH AVAILABLE
#
#
# Conceptually:
#
#
#     POLICY
#
#         May this request use this destination?
#
#
#     CAPABILITY
#
#         Can the reasoning resource perform the required work?
#
#
#     SERVICE STATE
#
#         Can the reasoning service currently operate?
#
#
#     NETWORK
#
#         Can Agent 11 currently reach the reasoning service?
#
#
# If a required gate fails:
#
#
#     CANDIDATE IS NOT VIABLE
#
#
# This is constraint satisfaction.
#
#
# It is NOT optimization.
#
#
#     VIABILITY != PREFERENCE
#
#
#     VIABILITY != SCORE
#
#
#     VIABILITY != SELECTION
#
# ==========================================================================


# ==========================================================================
# CAPABLE DOES NOT MEAN VIABLE
# ==========================================================================
#
# Consider:
#
#
#     Service A
#
#         capability = PASS
#
#         policy = DENY
#
#
# The service can perform the work.
#
# Agent 11 is not permitted to send the request there.
#
#
# Result:
#
#
#     NOT VIABLE
#
#
# Consider:
#
#
#     Service B
#
#         capability = PASS
#
#         policy = ALLOW
#
#         service = UNAVAILABLE
#
#
# Result:
#
#
#     NOT VIABLE
#
#
# Consider:
#
#
#     Service C
#
#         capability = PASS
#
#         policy = ALLOW
#
#         service = AVAILABLE
#
#         network = UNAVAILABLE
#
#
# Result:
#
#
#     NOT VIABLE
#
#
# Therefore:
#
#
#     CAPABLE != VIABLE
#
#
#     AUTHORIZED != VIABLE
#
#
#     AVAILABLE != VIABLE
#
#
#     REACHABLE != VIABLE
#
#
# Viability is the conjunction of the required conditions.
# ==========================================================================


# ==========================================================================
# AUTHORIZATION AND REACHABILITY ARE INDEPENDENT
# ==========================================================================
#
# One of the most important Agent 11 distinctions is:
#
#
#     REACHABLE != AUTHORIZED
#
#
# Example:
#
#
#     External FM
#
#         network = AVAILABLE
#
#         service = AVAILABLE
#
#         policy = DENY
#
#
# Packets can reach it.
#
# The service can answer.
#
# Agent 11 still must not use it.
#
#
# Conversely:
#
#
#     Company On-Prem LLM
#
#         policy = ALLOW
#
#         service = AVAILABLE
#
#         network = UNAVAILABLE
#
#
# Agent 11 is permitted to use it.
#
# Agent 11 cannot currently reach it.
#
#
# Therefore:
#
#
#     AUTHORIZED != REACHABLE
#
#
#     REACHABLE != AUTHORIZED
#
#
# Network state does not grant AI authorization.
#
# AI authorization does not create a network path.
# ==========================================================================


# ==========================================================================
# SERVICE AVAILABILITY AND NETWORK AVAILABILITY ARE DIFFERENT FACTS
# ==========================================================================
#
# Example:
#
#
#     AI Service
#         |
#         | HEALTHY
#         v
#     Inference Runtime
#
#
# while:
#
#
#     Agent 11
#         |
#         X
#         |
#     Network Path
#
#
# The service may be healthy.
#
# The path may be unavailable.
#
#
# Result:
#
#
#     RoutingCandidateStatus.REJECTED
#
#     RoutingRejectionReason.NETWORK_UNAVAILABLE
#
#
# This is different from:
#
#
#     service itself unavailable
#
#
# which would produce:
#
#
#     RoutingRejectionReason.SERVICE_UNAVAILABLE
#
#
# Therefore:
#
#
#     NETWORK UNAVAILABLE != SERVICE UNAVAILABLE
#
#
#     UNREACHABLE != UNHEALTHY
#
#
#     HEALTHY != REACHABLE
#
# ==========================================================================


# ==========================================================================
# RoutingCandidate REPRESENTS THE RESULT OF VIABILITY EVALUATION
# ==========================================================================
#
# Conceptually:
#
#
#     AIService
#         |
#         v
#     POLICY
#         |
#         v
#     CAPABILITY
#         |
#         v
#     SERVICE STATE
#         |
#         v
#     NETWORK STATE
#         |
#         v
#     RoutingCandidate
#
#
# RoutingCandidate is the summarized routing-level outcome.
#
#
# It should NOT become the component that performs:
#
#
#     policy evaluation
#
#     capability matching
#
#     service health checks
#
#     network discovery
#
#
# Those behaviors belong to the domains that own those facts.
#
#
#     CANDIDATE MODEL != CANDIDATE EVALUATOR
# ==========================================================================


# ==========================================================================
# VIABLE DOES NOT MEAN SELECTED
# ==========================================================================
#
# Agent 11 may discover:
#
#
#     Service A
#         VIABLE
#
#
#     Service B
#         VIABLE
#
#
#     Service C
#         VIABLE
#
#
# The viable set is:
#
#
#     {A, B, C}
#
#
# Agent 11 may ultimately select:
#
#
#     Service B
#
#
# Therefore:
#
#
#     A = VIABLE, NOT SELECTED
#
#     B = VIABLE, SELECTED
#
#     C = VIABLE, NOT SELECTED
#
#
# There is nothing contradictory about this.
#
#
#     VIABLE != SELECTED
#
#
# Viability determines:
#
#
#     MAY THIS SERVICE PARTICIPATE?
#
#
# Selection determines:
#
#
#     WHICH VIABLE SERVICE SHOULD HANDLE THIS REQUEST?
#
# ==========================================================================


# ==========================================================================
# REJECTED DOES NOT MEAN FAILED
# ==========================================================================
#
# Consider:
#
#
#     External Service
#
#         healthy
#         reachable
#         capable
#         policy denied
#
#
# RoutingCandidate:
#
#
#     REJECTED
#
#     POLICY_DENIED
#
#
# The service did not fail.
#
# The network did not fail.
#
# Agent 11 did not fail.
#
#
# The candidate simply did not satisfy the complete routing contract.
#
#
# Therefore:
#
#
#     REJECTED != FAILED
#
#
# This distinction matters operationally.
#
# Otherwise security enforcement begins appearing in telemetry as:
#
#
#     "AI failure"
#
#
# when the system actually behaved correctly.
# ==========================================================================


# ==========================================================================
# FOUR FINAL ROUTING OUTCOMES
# ==========================================================================
#
# SEIR-I deliberately preserves four final routing outcomes:
#
#
#     SELECTED
#
#     BLOCKED
#
#     NO_VIABLE_ROUTE
#
#     NULL
#
#
# These are not cosmetic distinctions.
#
#
# They represent materially different system outcomes:
#
#
#     SELECTED
#
#         Agent 11 found and selected a viable reasoning service.
#
#
#     BLOCKED
#
#         Policy prevented the request from obtaining an AI route.
#
#
#     NO_VIABLE_ROUTE
#
#         AI reasoning was appropriate and not categorically blocked,
#         but no operationally viable service remained.
#
#
#     NULL
#
#         AI routing was intentionally unnecessary.
#
#
# Do NOT collapse these into:
#
#
#     SUCCESS
#
#     FAILED
#
#
# Agent 11 needs richer semantics than that.
# ==========================================================================


# ==========================================================================
# SELECTED
# ==========================================================================
#
# SELECTED means:
#
#
#     at least one usable destination survived the required routing
#     process,
#
#
# and:
#
#
#     Agent 11 chose a concrete AI service.
#
#
# Therefore:
#
#
#     status = SELECTED
#
# requires:
#
#
#     selected_service_id
#
#     selected_routing_domain
#
#
# Example:
#
#
#     RoutingDecision
#
#         status =
#             SELECTED
#
#         selected_service_id =
#             "company-security-cloud-primary"
#
#         selected_routing_domain =
#             COMPANY_CLOUD_LLM
#
#
# SELECTED means routing succeeded.
#
#
# It does NOT mean:
#
#
#     inference succeeded
#
#     the model answered correctly
#
#     the response was grounded
#
#     the response was safe
#
#     an action is authorized
#
#
# Therefore:
#
#
#     ROUTING SUCCESS != INFERENCE SUCCESS
#
#
#     INFERENCE SUCCESS != CORRECTNESS
#
#
#     AI OUTPUT != ACTION AUTHORITY
# ==========================================================================


# ==========================================================================
# BLOCKED
# ==========================================================================
#
# BLOCKED means:
#
#
#     POLICY PREVENTED AI ROUTING
#
#
# Example:
#
#
#     Request Data Classification:
#
#         E9
#
#
# Organization Policy:
#
#
#     EXTERNAL_FM
#         DENY
#
#     COMPANY_CLOUD_LLM
#         DENY
#
#     COMPANY_ONPREM_LLM
#         DENY
#
#
# Result:
#
#
#     RoutingStatus.BLOCKED
#
#
# There may be:
#
#
#     healthy services
#
#     capable models
#
#     available network paths
#
#
# None of those facts override policy.
#
#
#     HEALTHY != PERMITTED
#
#
#     CAPABLE != PERMITTED
#
#
#     REACHABLE != PERMITTED
#
#
#     CHEAPER != PERMITTED
#
#
#     FASTER != PERMITTED
#
#
# BLOCKED is often evidence that:
#
#
#     SECURITY ENFORCEMENT WORKED
#
#
# It must not automatically be recorded as:
#
#
#     ROUTING ERROR
#
# ==========================================================================


# ==========================================================================
# ONE POLICY-DENIED CANDIDATE DOES NOT MEAN BLOCKED
# ==========================================================================
#
# Example:
#
#
#     External FM
#
#         REJECTED
#         POLICY_DENIED
#
#
#     Company Cloud
#
#         VIABLE
#
#
#     Company On-Prem
#
#         VIABLE
#
#
# Final result:
#
#
#     SELECTED
#
#
# not:
#
#
#     BLOCKED
#
#
# because policy still permitted other viable destinations.
#
#
# Therefore:
#
#
#     CANDIDATE POLICY REJECTION
#         !=
#     FINAL ROUTING BLOCK
#
#
# BLOCKED is a final routing outcome.
#
# POLICY_DENIED is a candidate-level rejection reason.
# ==========================================================================


# ==========================================================================
# ALL POLICY-DENIED CANDIDATES MAY PRODUCE BLOCKED
# ==========================================================================
#
# Example:
#
#
#     External FM
#
#         POLICY_DENIED
#
#
#     Company Cloud
#
#         POLICY_DENIED
#
#
#     Company On-Prem
#
#         POLICY_DENIED
#
#
# No destination is permitted.
#
#
# Final result:
#
#
#     BLOCKED
#
#
# This differs from a situation where policy permits services but none
# can currently operate.
#
#
# That second situation belongs to:
#
#
#     NO_VIABLE_ROUTE
#
#
#     BLOCKED = POLICY OUTCOME
#
#
#     NO_VIABLE_ROUTE = VIABILITY / OPERATIONAL OUTCOME
# ==========================================================================


# ==========================================================================
# NO_VIABLE_ROUTE
# ==========================================================================
#
# NO_VIABLE_ROUTE means:
#
#
#     AI routing was appropriate,
#
#     policy did not categorically prevent routing,
#
# but:
#
#     no usable destination survived viability evaluation.
#
#
# Example:
#
#
#     Company Cloud
#
#         policy = ALLOW
#         capability = PASS
#         service = UNAVAILABLE
#
#
#     Company On-Prem
#
#         policy = ALLOW
#         capability = PASS
#         service = AVAILABLE
#         network = UNAVAILABLE
#
#
# Result:
#
#
#     NO_VIABLE_ROUTE
#
#
# Agent 11 may have behaved perfectly.
#
#
# It correctly determined:
#
#
#     NO SAFE / OPERATIONALLY VIABLE DESTINATION EXISTS NOW
#
#
# Therefore:
#
#
#     NO_VIABLE_ROUTE != ROUTER FAILURE
#
#
#     NO ROUTE CAN BE THE CORRECT ROUTING ANSWER
# ==========================================================================


# ==========================================================================
# NO_VIABLE_ROUTE IS NOT BLOCKED
# ==========================================================================
#
# Compare:
#
#
#     CASE A
#
#         policy = DENY
#
#
#     Result:
#
#         BLOCKED
#
#
# versus:
#
#
#     CASE B
#
#         policy = ALLOW
#         service = UNAVAILABLE
#
#
#     Result:
#
#         NO_VIABLE_ROUTE
#
#
# These should produce different telemetry.
#
#
# Why?
#
#
# CASE A says:
#
#
#     DO NOT SEND THIS REQUEST THERE.
#
#
# CASE B says:
#
#
#     YOU MAY SEND THIS REQUEST THERE,
#     BUT YOU CANNOT CURRENTLY DO SO.
#
#
# Security and operations need to distinguish these.
#
#
#     BLOCKED != NO_VIABLE_ROUTE
# ==========================================================================


# ==========================================================================
# NULL
# ==========================================================================
#
# NULL means:
#
#
#     AI ROUTING WAS INTENTIONALLY UNNECESSARY
#
#
# Example:
#
#
#     request arrives
#         |
#         v
#     orchestrator determines:
#
#         no AI reasoning required
#         |
#         v
#     RoutingDecision
#
#         status = NULL
#
#
# This is not:
#
#
#     policy denial
#
#     lack of service
#
#     lack of network
#
#     router failure
#
#     AI failure
#
#
# It is an intentional no-op routing outcome.
#
#
# Therefore:
#
#
#     NULL != FAILURE
#
#
#     NULL != BLOCKED
#
#
#     NULL != NO_VIABLE_ROUTE
#
#
#     INTENTIONAL NO ROUTE != FAILED ROUTE
# ==========================================================================


# ==========================================================================
# NULL SHOULD NOT INVOKE AI
# ==========================================================================
#
# RoutingStatus.NULL means:
#
#
#     DO NOT PERFORM AI INVOCATION
#
#
# Therefore:
#
#
#     RoutingStatus.NULL
#         |
#         v
#     AIResponse = None
#
#
# The same is true for:
#
#
#     BLOCKED
#
#     NO_VIABLE_ROUTE
#
#
# because no AI service was selected.
#
#
# Conceptually:
#
#
#     SELECTED
#         |
#         v
#     AI Invocation
#         |
#         v
#     AIResponse
#
#
# versus:
#
#
#     BLOCKED
#         |
#         v
#        None
#
#
#     NO_VIABLE_ROUTE
#         |
#         v
#        None
#
#
#     NULL
#         |
#         v
#        None
#
#
# AIResponse represents the result of an actual AI invocation.
#
#
#     NO INVOCATION => NO AIResponse
# ==========================================================================


# ==========================================================================
# AIResponseStatus.FAILED IS DIFFERENT FROM RoutingStatus.NO_VIABLE_ROUTE
# ==========================================================================
#
# Consider:
#
#
#     RoutingDecision
#
#         status = SELECTED
#
#         selected_service_id = Service A
#
#              |
#              v
#
#         invoke Service A
#
#              |
#              v
#
#         inference fails
#
#              |
#              v
#
#     AIResponse
#
#         status = FAILED
#
#
# Routing succeeded.
#
# Inference failed.
#
#
# Compare:
#
#
#     RoutingDecision
#
#         status = NO_VIABLE_ROUTE
#
#
# No service was invoked.
#
# Therefore no AIResponse exists.
#
#
#     ROUTING FAILURE SEMANTICS
#         !=
#     INFERENCE FAILURE SEMANTICS
#
#
# More precisely:
#
#
#     NO_VIABLE_ROUTE
#         !=
#     AIResponseStatus.FAILED
# ==========================================================================


# ==========================================================================
# MIXED REJECTION CAUSES
# ==========================================================================
#
# Candidate sets may contain different rejection causes.
#
#
# Example:
#
#
#     External FM
#
#         POLICY_DENIED
#
#
#     Company Cloud
#
#         SERVICE_UNAVAILABLE
#
#
#     Company On-Prem
#
#         NETWORK_UNAVAILABLE
#
#
# What should the final RoutingStatus be?
#
#
# That is ROUTING BEHAVIOR.
#
#
# It should NOT be inferred by RoutingDecision's Pydantic validator.
#
#
# The router / orchestrator must apply explicit routing semantics.
#
#
# A useful SEIR-I principle is:
#
#
#     BLOCKED
#
#         when policy prevents the request from obtaining an AI route.
#
#
#     NO_VIABLE_ROUTE
#
#         when at least one route was policy-permitted but operational
#         viability could not be established.
#
#
# In the example above:
#
#
#     Company Cloud
#
# and:
#
#     Company On-Prem
#
# were policy-permitted.
#
#
# They failed for operational viability reasons.
#
#
# Therefore the likely final outcome is:
#
#
#     NO_VIABLE_ROUTE
#
#
# But:
#
#
#     THIS RULE BELONGS IN ROUTING BEHAVIOR.
#
#
# Do not turn RoutingDecision validation into an implicit router.
# ==========================================================================


# ==========================================================================
# POLICY SHOULD BE EVALUATED BEFORE OPTIMIZATION
# ==========================================================================
#
# Consider:
#
#
#     Service A
#
#         policy = DENY
#         latency = 10 ms
#         cost = $0.001
#
#
#     Service B
#
#         policy = ALLOW
#         latency = 50 ms
#         cost = $0.005
#
#
# Agent 11 does NOT ask:
#
#
#     "Which service has the better overall score?"
#
#
# before enforcing policy.
#
#
# Service A is not eligible for optimization.
#
#
# Conceptually:
#
#
#     ALL CANDIDATES
#         |
#         v
#     REQUIRED VIABILITY GATES
#         |
#         v
#     VIABLE SET
#         |
#         v
#     SELECTION / OPTIMIZATION
#
#
# Therefore:
#
#
#     CONSTRAINTS FIRST
#
#     OPTIMIZATION SECOND
#
#
#     POLICY NEVER BECOMES A SCORE
# ==========================================================================


# ==========================================================================
# DO NOT USE A GENERIC score: float IN SEIR-I
# ==========================================================================
#
# Avoid:
#
#
#     score: float
#
#
# Why?
#
#
#     score = 0.87
#
#
# 0.87 WHAT?
#
#
# Is it:
#
#
#     quality?
#
#     latency?
#
#     cost?
#
#     availability?
#
#     capacity?
#
#     policy?
#
#     network quality?
#
#     organizational preference?
#
#
# A generic score destroys semantics.
#
#
# Worse:
#
#
#     policy
#
# must never become just another weighted component.
#
#
# Future SEIR-II routing may introduce typed optimization criteria after
# viability has already been established.
#
#
# Example:
#
#
#     quality_score
#
#     latency_score
#
#     capacity_score
#
#     cost_score
#
#
# But:
#
#
#     SCORE != VIABILITY
#
#
#     HIGHEST SCORE != POLICY OVERRIDE
#
#
# SEIR-I does not need these fields.
# ==========================================================================


# ==========================================================================
# FALLBACK SEMANTICS
# ==========================================================================
#
# Fallback exists to preserve availability while maintaining the same
# security and viability requirements.
#
#
# Conceptually:
#
#
#     Primary Candidate
#         |
#         X
#         |
#     NOT VIABLE
#         |
#         v
#     Evaluate Next Candidate
#         |
#         v
#     Apply ALL Required Gates Again
#         |
#         v
#     VIABLE?
#
#
# Therefore:
#
#
#     FALLBACK = RE-EVALUATION
#
#
# Fallback does NOT mean:
#
#
#     "Use the next service regardless."
#
#
# Fallback does NOT mean:
#
#
#     "Policy failed, so try somewhere less secure."
#
#
# Fallback does NOT mean:
#
#
#     "The primary service is unavailable, therefore external AI is
#      automatically allowed."
#
#
#     FALLBACK != POLICY ESCAPE
#
#
#     FALLBACK != STATIC SERVICE POINTER
# ==========================================================================


# ==========================================================================
# FALLBACK MAY REDUCE AVAILABILITY
# ==========================================================================
#
# Suppose:
#
#
#     Primary:
#
#         COMPANY_ONPREM_LLM
#
#         unavailable
#
#
#     Secondary:
#
#         COMPANY_CLOUD_LLM
#
#         policy denied for this request
#
#
#     Tertiary:
#
#         EXTERNAL_FM
#
#         policy denied for this request
#
#
# Correct result:
#
#
#     NO_VIABLE_ROUTE
#
#
# Incorrect result:
#
#
#     "Well, Claude is still online."
#
#
# Availability pressure does not rewrite policy.
#
#
# Therefore:
#
#
#     FALLBACK MAY REDUCE AVAILABILITY
#
#
#     FALLBACK MUST NOT REDUCE SECURITY POLICY
#
#
# Sometimes the correct fallback result is:
#
#
#     NOTHING
#
#
# Agent 11 must be able to say:
#
#
#     NO COMPLIANT ROUTE EXISTS.
# ==========================================================================


# ==========================================================================
# NEXT_VIABLE FALLBACK
# ==========================================================================
#
# SEIR-I currently defines:
#
#
#     FallbackStrategy.NONE
#
#     FallbackStrategy.NEXT_VIABLE
#
#
# NEXT_VIABLE means:
#
#
#     continue evaluating candidates until another candidate satisfies
#     the required viability conditions.
#
#
# It does NOT mean:
#
#
#     next item in list = automatically selected
#
#
# Conceptually:
#
#
#     Candidate A
#         |
#         X
#
#     Candidate B
#         |
#         v
#     RE-EVALUATE
#         |
#         X
#
#     Candidate C
#         |
#         v
#     RE-EVALUATE
#         |
#         v
#     VIABLE
#         |
#         v
#     SELECT
#
#
# Every fallback candidate must independently satisfy the routing
# contract.
#
#
#     NEXT_VIABLE != NEXT
# ==========================================================================


# ==========================================================================
# FALLBACK DOES NOT BELONG IN RoutingDecision
# ==========================================================================
#
# Avoid adding:
#
#
#     fallback_service_id
#
#     fallback_route
#
#     fallback_attempts
#
#     fallback_succeeded
#
#
# directly to RoutingDecision merely because fallback occurred.
#
#
# RoutingDecision answers:
#
#
#     WHAT WAS THE FINAL ROUTING OUTCOME?
#
#
# Fallback behavior answers:
#
#
#     HOW DID ROUTING ARRIVE AT THAT OUTCOME?
#
#
# Those are different questions.
#
#
# SEIR-I candidate records may provide enough summarized information.
#
#
# Future temporal routing may require:
#
#
#     RoutingAttempt
#
#     RoutingHistory
#
#     CandidateEvaluationEvent
#
#
# Part IV preserves those expansion points.
#
#
#     FINAL DECISION != EXECUTION HISTORY
# ==========================================================================


# ==========================================================================
# EFFECTIVE POLICY
# ==========================================================================
#
# Agent 11 may eventually combine:
#
#
#     ORGANIZATION POLICY
#
# and:
#
#     USER POLICY / USER PREFERENCE
#
#
# The security model is:
#
#
#     EFFECTIVE POLICY
#
#         =
#
#     ORGANIZATION POLICY
#
#         INTERSECTION
#
#     USER POLICY
#
#
# Conceptually:
#
#
#     ORGANIZATION ALLOWS:
#
#         External
#         Company Cloud
#         Company On-Prem
#
#
#     USER RESTRICTS:
#
#         Company On-Prem only
#
#
# Effective policy:
#
#
#         Company On-Prem only
#
#
# The user may narrow the allowed destination set.
#
# The user may not expand beyond organizational authorization.
#
#
#     USER MAY NARROW
#
#     USER MAY NOT EXPAND
#
#
# Example:
#
#
#     Organization:
#
#         EXTERNAL_FM = DENY
#
#
#     User:
#
#         "I prefer external AI."
#
#
# Effective result:
#
#
#     EXTERNAL_FM = DENY
#
#
# Preference does not override policy.
# ==========================================================================


# ==========================================================================
# RESTRICTION IS NOT AUTHORIZATION EXPANSION
# ==========================================================================
#
# Suppose organizational policy allows:
#
#
#     COMPANY_CLOUD_LLM
#
#     COMPANY_ONPREM_LLM
#
#
# and user policy says:
#
#
#     ONPREM_ONLY
#
#
# Effective set:
#
#
#     COMPANY_ONPREM_LLM
#
#
# Good.
#
#
# Suppose organizational policy allows only:
#
#
#     COMPANY_ONPREM_LLM
#
#
# and the user says:
#
#
#     ORGANIZATION_DEFAULT
#
#
# Effective set remains:
#
#
#     COMPANY_ONPREM_LLM
#
#
# Suppose organizational policy denies:
#
#
#     EXTERNAL_FM
#
#
# No user preference can add it back.
#
#
#     LOWER AUTHORITY MAY RESTRICT
#
#     LOWER AUTHORITY MAY NOT EXPAND
# ==========================================================================


# ==========================================================================
# INDETERMINATE POLICY MUST FAIL CLOSED
# ==========================================================================
#
# PolicyDecisionStatus may contain:
#
#
#     ALLOW
#
#     DENY
#
#     RESTRICT
#
#     INDETERMINATE
#
#
# INDETERMINATE is not equivalent to:
#
#
#     ALLOW
#
#
# If Agent 11 cannot establish that a destination is permitted:
#
#
#     DO NOT SEND THE REQUEST
#
#
# This is fail-closed behavior.
#
#
# But:
#
#
#     INDETERMINATE != DENY
#
#
# The telemetry should preserve the difference.
#
#
# DENY means:
#
#
#     policy explicitly prohibited the route.
#
#
# INDETERMINATE means:
#
#
#     authorization could not be established.
#
#
# Both may result in conservative routing behavior.
#
# They are not the same observed policy fact.
#
#
#     FAIL CLOSED != ERASE SEMANTICS
# ==========================================================================


# ==========================================================================
# UNKNOWN STATE MUST REMAIN UNKNOWN
# ==========================================================================
#
# The same principle applies to operational observations.
#
#
# Suppose:
#
#
#     ServiceState = UNKNOWN
#
#
# Agent 11 may decide not to use the service.
#
#
# That does NOT transform the observation into:
#
#
#     ServiceState = UNAVAILABLE
#
#
# Likewise:
#
#
#     NetworkPathState = UNKNOWN
#
#
# may result in conservative rejection.
#
# It must remain:
#
#
#     UNKNOWN
#
#
# in the underlying network observation.
#
#
# Therefore:
#
#
#     UNKNOWN != UNAVAILABLE
#
#
#     FAIL CLOSED != FALSIFY OBSERVED STATE
#
#
#     OBSERVATION != DECISION
# ==========================================================================


# ==========================================================================
# RoutingRejectionReason.UNKNOWN IS A ROUTING SUMMARY
# ==========================================================================
#
# Part I currently permits:
#
#
#     RoutingRejectionReason.UNKNOWN
#
#
# This is a routing-level summary used when Agent 11 cannot provide a
# more specific rejection reason.
#
#
# It should NOT overwrite richer source-domain state.
#
#
# Example:
#
#
#     ServiceStateObservation:
#
#         UNKNOWN
#
#
# Routing behavior:
#
#
#     fail closed
#
#
# RoutingCandidate:
#
#
#     REJECTED
#
#     UNKNOWN
#
#
# This preserves:
#
#
#     source observation = UNKNOWN
#
# and:
#
#     routing outcome = REJECTED
#
#
# Future Agent 11 versions may introduce richer provenance or an
# INSUFFICIENT_EVIDENCE rejection reason.
#
#
# Do not prematurely expand the SEIR-I enum until that distinction
# becomes operationally necessary.
# ==========================================================================


# ==========================================================================
# POLICY, CAPABILITY, SERVICE, AND NETWORK OWN THEIR OWN FACTS
# ==========================================================================
#
# Agent 11 routing consumes facts from several domains:
#
#
#     POLICY
#         |
#         +--> permitted?
#
#
#     CAPABILITY
#         |
#         +--> capable?
#
#
#     SERVICE
#         |
#         +--> available?
#
#
#     NETWORK
#         |
#         +--> reachable?
#
#
#                         |
#                         v
#
#                      ROUTING
#
#
# Routing should not redefine those facts.
#
#
# Examples:
#
#
#     Policy owns:
#
#         authorization
#
#
#     Capability owns:
#
#         ability to perform reasoning work
#
#
#     Service runtime owns:
#
#         operational service state
#
#
#     Network owns:
#
#         path state
#
#
#     Routing owns:
#
#         candidate outcome
#         final destination decision
#
#
# Therefore:
#
#
#     ROUTING CONSUMES DOMAIN FACTS
#
#     ROUTING DOES NOT BECOME EVERY DOMAIN
# ==========================================================================


# ==========================================================================
# ROUTING MUST NOT BECOME POLICY
# ==========================================================================
#
# Bad future router:
#
#
#     if classification == "E9":
#         deny_external = True
#
#
# Why is this dangerous?
#
#
# Because the router now owns classification-specific security rules.
#
#
# Instead:
#
#
#     Policy Engine
#         |
#         v
#     PolicyDecision
#         |
#         v
#     Router
#
#
# The router consumes the policy outcome.
#
#
# This preserves:
#
#
#     POLICY = SECURITY RULES
#
#     ROUTING = DESTINATION SELECTION
#
#
#     ROUTER != POLICY ENGINE
# ==========================================================================


# ==========================================================================
# ROUTING MUST NOT BECOME CAPABILITY LOGIC
# ==========================================================================
#
# Bad future router:
#
#
#     if model_name == "SuperModel-X":
#         heavy_reasoning = True
#
#
# The router should not accumulate vendor/model-specific assumptions.
#
#
# Instead:
#
#
#     AIModel
#         |
#         v
#     AICapability
#         |
#         v
#     Capability Evaluation
#         |
#         v
#     Router
#
#
# The router consumes capability evaluation.
#
#
#     MODEL NAME != CAPABILITY CONTRACT
#
#
#     ROUTER != MODEL KNOWLEDGE DATABASE
# ==========================================================================


# ==========================================================================
# ROUTING MUST NOT BECOME SERVICE HEALTH LOGIC
# ==========================================================================
#
# Bad future router:
#
#
#     requests.get(service.endpoint + "/health")
#
#
# buried inside generic route-selection logic.
#
#
# Service health belongs to the runtime / service-health domain.
#
#
# Conceptually:
#
#
#     Health Component
#         |
#         v
#     Service State
#         |
#         v
#     Router
#
#
# The router consumes:
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
# according to routing policy.
#
#
#     ROUTER != HEALTH CHECK IMPLEMENTATION
# ==========================================================================


# ==========================================================================
# ROUTING MUST NOT BECOME NETWORK CONTROL
# ==========================================================================
#
# Agent 11 may eventually consume:
#
#
#     VPN state
#
#     PrivateLink state
#
#     SD-WAN state
#
#     BGP state
#
#     path latency
#
#     packet loss
#
#
# But Agent 11 routing answers:
#
#
#     WHICH AI DESTINATION SHOULD BE USED?
#
#
# BGP / SD-WAN / network control answers:
#
#
#     HOW SHOULD PACKETS REACH THAT DESTINATION?
#
#
# Therefore:
#
#
#     AI ROUTING != NETWORK ROUTING
#
#
#     BGP != AI AUTHORIZATION
#
#
#     SD-WAN != AI POLICY
#
#
# Network state is an input to AI routing viability.
#
# Network control remains a separate responsibility.
# ==========================================================================


# ==========================================================================
# MODEL SELECTION, SERVICE SELECTION, AND NETWORK PATH SELECTION
# ==========================================================================
#
# These concepts are related but not identical.
#
#
#     AIModel
#
#         WHAT LOGICAL MODEL?
#
#
#     AIService
#
#         WHICH OPERATIONAL EXPOSURE OF THAT MODEL?
#
#
#     Network Path
#
#         HOW CAN THAT SERVICE BE REACHED?
#
#
#     RoutingDecision
#
#         WHICH AI SERVICE DID AGENT 11 SELECT?
#
#
# Future systems may have:
#
#
#     Model X
#         |
#         +-- Service A in AWS
#         |
#         +-- Service B in GCP
#         |
#         +-- Service C on-prem
#
#
# Selecting:
#
#
#     Model X
#
# does not uniquely identify:
#
#
#     Service A
#
#
# Likewise selecting:
#
#
#     Service A
#
# does not necessarily identify:
#
#
#     one unique network path
#
#
# Therefore:
#
#
#     MODEL SELECTION != SERVICE SELECTION
#
#
#     SERVICE SELECTION != NETWORK PATH SELECTION
#
#
#     AI ROUTING != PACKET ROUTING
# ==========================================================================


# ==========================================================================
# ROUTING DOMAIN IS NOT DEPLOYMENT PROVIDER
# ==========================================================================
#
# Current AIRoute vocabulary:
#
#
#     EXTERNAL_FM
#
#     COMPANY_CLOUD_LLM
#
#     COMPANY_ONPREM_LLM
#
#
# These describe Agent 11 routing domains.
#
#
# They do NOT mean:
#
#
#     Anthropic
#
#     AWS
#
#     Azure
#
#     GCP
#
#     OCI
#
#
# Future example:
#
#
#     proprietary company trading model
#
#         model owner:
#             COMPANY
#
#         deployment provider:
#             GCP
#
#         routing domain:
#             COMPANY_CLOUD_LLM
#
#
# Perfectly valid.
#
#
# Another:
#
#
#     company security model
#
#         deployment provider:
#             Azure
#
#         routing domain:
#             COMPANY_CLOUD_LLM
#
#
# Therefore:
#
#
#     ROUTING DOMAIN != CLOUD PROVIDER
#
#
#     ROUTING DOMAIN != MODEL PROVIDER
#
#
#     ROUTING DOMAIN != DEPLOYMENT LOCATION
#
#
# Part IV expands this heavily for SEIR-II.
# ==========================================================================


# ==========================================================================
# ROUTING DECISION IS NOT AI INVOCATION
# ==========================================================================
#
# RoutingDecision says:
#
#
#     USE SERVICE X
#
#
# It does not itself:
#
#
#     call Service X
#
#
# The orchestrator may consume the decision:
#
#
#     RoutingDecision
#         |
#         v
#     AI Orchestrator
#         |
#         v
#     Runtime Adapter
#         |
#         v
#     AI Service
#         |
#         v
#     AIResponse
#
#
# This separation matters because:
#
#
#     routing can succeed
#
# while:
#
#     invocation fails
#
#
# Therefore:
#
#
#     ROUTING DECISION != AI INVOCATION
#
#
#     SELECTED != INVOKED
#
#
#     INVOKED != SUCCESSFUL
# ==========================================================================


# ==========================================================================
# AI OUTPUT DOES NOT GRANT ACTION AUTHORITY
# ==========================================================================
#
# Agent 11 may route a request to an extremely capable reasoning model.
#
#
# The model may return:
#
#
#     "Delete the production database."
#
#
# That output is:
#
#
#     AI OUTPUT
#
#
# It is not:
#
#
#     AUTHORIZATION
#
#
# A safe agentic architecture requires separate execution governance:
#
#
#     AI Reasoning
#         |
#         v
#     Policy / Authorization
#         |
#         v
#     Scoped Execution
#         |
#         v
#     Audit
#
#
# Therefore:
#
#
#     AI OUTPUT != ACTION AUTHORITY
#
#
#     REASONING CAPABILITY != EXECUTION AUTHORITY
#
#
# Routing a request successfully must never silently expand the
# authority of the consuming agent.
# ==========================================================================


# ==========================================================================
# TELEMETRY MUST PRESERVE ROUTING SEMANTICS
# ==========================================================================
#
# Future telemetry should preserve:
#
#
#     SELECTED
#
#     BLOCKED
#
#     NO_VIABLE_ROUTE
#
#     NULL
#
#
# as different outcomes.
#
#
# Avoid:
#
#
#     routing_success = True / False
#
#
# as the only recorded semantic.
#
#
# Why?
#
#
# Because:
#
#
#     BLOCKED
#
# may represent:
#
#     successful policy enforcement
#
#
# while:
#
#
#     NO_VIABLE_ROUTE
#
# may represent:
#
#     operational unavailability
#
#
# while:
#
#
#     NULL
#
# may represent:
#
#     intentional absence of AI work
#
#
# Collapsing all three into:
#
#
#     False
#
#
# destroys useful operational meaning.
#
#
#     TELEMETRY SHOULD PRESERVE DOMAIN SEMANTICS
# ==========================================================================


# ==========================================================================
# ROUTING REASONS SHOULD REMAIN MACHINE-READABLE WHERE IMPORTANT
# ==========================================================================
#
# RoutingDecision.reason is human-readable.
#
#
# Do NOT make downstream behavior depend on:
#
#
#     "Policy denied external AI because..."
#
#
# String parsing is not a routing contract.
#
#
# Machine semantics belong in:
#
#
#     RoutingStatus
#
#     RoutingCandidateStatus
#
#     RoutingRejectionReason
#
#
# Future richer semantics may deserve:
#
#
#     typed policy rejection records
#
#     typed provenance records
#
#     typed routing evaluation records
#
#
# rather than increasingly elaborate prose.
#
#
#     HUMAN EXPLANATION != MACHINE CONTROL
# ==========================================================================


# ==========================================================================
# ROUTING SHOULD FAIL CLOSED WHEN REQUIRED FACTS CANNOT BE ESTABLISHED
# ==========================================================================
#
# Suppose Agent 11 cannot establish:
#
#
#     whether policy permits the route
#
#
# or:
#
#     whether a required network path is safe / available
#
#
# The router must not invent confidence.
#
#
# Conservative behavior may result in:
#
#
#     candidate rejection
#
#
# or:
#
#     final BLOCKED / NO_VIABLE_ROUTE
#
#
# depending on the domain fact that could not be established.
#
#
# The exact mapping belongs in routing behavior.
#
#
# The invariant is:
#
#
#     DO NOT INVENT A VIABLE ROUTE
#
#
#     UNCERTAINTY DOES NOT CREATE AUTHORIZATION
#
#
#     UNCERTAINTY DOES NOT CREATE REACHABILITY
# ==========================================================================


# ==========================================================================
# SOMETIMES REQUEST BLOCKED IS SUCCESSFUL SYSTEM BEHAVIOR
# ==========================================================================
#
# Security systems must be comfortable returning:
#
#
#     REQUEST BLOCKED
#
#
# when policy requires it.
#
#
# Example:
#
#
#     E9 data
#         |
#         v
#     external destination
#         |
#         v
#     DENY
#
#
# Agent 11 should not interpret:
#
#
#     "The user did not get an AI response."
#
#
# as automatically meaning:
#
#
#     "Agent 11 failed."
#
#
# If the request should not have left the authorized trust boundary:
#
#
#     BLOCKING IT WAS SUCCESS.
#
#
# Therefore:
#
#
#     USER DID NOT RECEIVE AI OUTPUT
#         !=
#     SYSTEM FAILURE
# ==========================================================================


# ==========================================================================
# SOMETIMES NO ROUTE IS SUCCESSFUL SYSTEM BEHAVIOR
# ==========================================================================
#
# Suppose:
#
#
#     external = policy denied
#
#     company cloud = unavailable
#
#     on-prem = unreachable
#
#
# Agent 11 returns:
#
#
#     NO_VIABLE_ROUTE
#
#
# That may be the only correct answer.
#
#
# Dangerous systems often respond to this situation by inventing an
# exception:
#
#
#     "Use the external model temporarily."
#
#
# Agent 11 must not do that unless policy explicitly permits it.
#
#
# Therefore:
#
#
#     NO ROUTE
#
# may be:
#
#     CORRECT ENFORCEMENT
#
#
#     AVAILABILITY PRESSURE != POLICY EXCEPTION
# ==========================================================================


# ==========================================================================
# DO NOT CONFUSE ROUTING WITH BUSINESS CONTINUITY POLICY
# ==========================================================================
#
# An organization may intentionally define emergency policy such as:
#
#
#     during declared disaster state,
#     permit specific alternate reasoning destinations
#
#
# If such a rule exists:
#
#
#     POLICY owns that rule.
#
#
# The router consumes the resulting authorization.
#
#
# The router must NOT independently invent:
#
#
#     "emergency mode means ignore policy"
#
#
# Therefore:
#
#
#     EMERGENCY POLICY
#         !=
#     ROUTER BYPASS
#
#
#     BUSINESS CONTINUITY
#         !=
#     SECURITY DISAPPEARS
# ==========================================================================


# ==========================================================================
# ROUTING AND AUDITABILITY
# ==========================================================================
#
# A useful routing system should eventually allow an operator to answer:
#
#
#     Which request was routed?
#
#     Which candidates were evaluated?
#
#     Which candidates were rejected?
#
#     Why were they rejected?
#
#     Which service was selected?
#
#     Which routing domain was selected?
#
#     What final routing status occurred?
#
#
# RoutingCandidate and RoutingDecision establish the SEIR-I vocabulary
# necessary to answer those questions.
#
#
# Future provenance may answer deeper questions:
#
#
#     Which policy version was used?
#
#     Which service-state observation was used?
#
#     Which network observation was used?
#
#     When were those observations collected?
#
#     Which model/deployment version existed at that time?
#
#
# Those richer facts do not need to be copied into RoutingDecision now.
#
#
#     AUDITABLE != EVERYTHING IN ONE OBJECT
# ==========================================================================


# ==========================================================================
# ROUTING DECISION != PROVENANCE RECORD
# ==========================================================================
#
# RoutingDecision describes:
#
#
#     THE DECISION
#
#
# A future provenance record may describe:
#
#
#     THE EVIDENCE AND HISTORY BEHIND THE DECISION
#
#
# These are related.
#
# They are not identical.
#
#
# Avoid turning RoutingDecision into:
#
#
#     request
#     + policy document
#     + health state
#     + network state
#     + capability state
#     + model object
#     + service object
#     + deployment object
#     + telemetry
#     + history
#
#
# That is not a routing decision.
#
# That is a small database wearing a Pydantic costume.
#
#
#     DECISION != PROVENANCE
#
#
#     REFERENCE EVIDENCE
#
#     DO NOT DUPLICATE EVIDENCE
# ==========================================================================


# ==========================================================================
# ROUTING SHOULD EXPLAIN, NOT OBFUSCATE
# ==========================================================================
#
# Good:
#
#
#     Service A
#
#         REJECTED
#         POLICY_DENIED
#
#
#     Service B
#
#         REJECTED
#         NETWORK_UNAVAILABLE
#
#
#     Service C
#
#         VIABLE
#
#
#     Final:
#
#         SELECTED Service C
#
#
# Bad:
#
#
#     score_A = 0.42
#
#     score_B = 0.61
#
#     score_C = 0.88
#
#
#     selected C
#
#
# without explaining what those numbers mean.
#
#
# Agent 11 should preserve enough semantics that humans can understand
# why a route was or was not available.
#
#
#     EXPLAINABLE ROUTING > MYSTERY NUMBER
# ==========================================================================


# ==========================================================================
# POLICY SAFE FALLBACK EXAMPLE
# ==========================================================================
#
# Request:
#
#
#     data classification = E8
#
#
# Effective policy:
#
#
#     EXTERNAL_FM
#         DENY
#
#
#     COMPANY_CLOUD_LLM
#         DENY
#
#
#     COMPANY_ONPREM_LLM
#         ALLOW
#
#
# Candidate:
#
#
#     Company On-Prem Primary
#
#         service unavailable
#
#
# Agent 11 considers fallback.
#
#
# External FM is healthy.
#
# Company Cloud is healthy.
#
#
# Both remain:
#
#
#     POLICY DENIED
#
#
# Therefore:
#
#
#     fallback result =
#
#         NO_VIABLE_ROUTE
#
#
# NOT:
#
#
#     "Use cloud because on-prem failed."
#
#
# NOT:
#
#
#     "Use external because it is all we have."
#
#
#     FALLBACK RE-EVALUATES VIABILITY
#
#     FALLBACK DOES NOT ESCAPE POLICY
# ==========================================================================


# ==========================================================================
# POLICY SAFE FALLBACK WITH A VALID ALTERNATIVE
# ==========================================================================
#
# Request:
#
#
#     data classification = E7
#
#
# Effective policy:
#
#
#     EXTERNAL_FM
#         DENY
#
#
#     COMPANY_CLOUD_LLM
#         ALLOW
#
#
#     COMPANY_ONPREM_LLM
#         ALLOW
#
#
# Primary:
#
#
#     Company On-Prem
#
#         service unavailable
#
#
# Fallback:
#
#
#     Company Cloud
#
#         policy = ALLOW
#         capability = PASS
#         service = AVAILABLE
#         network = AVAILABLE
#
#
# Result:
#
#
#     SELECTED
#
#     COMPANY_CLOUD_LLM
#
#
# This is legitimate fallback because the fallback candidate independently
# satisfies all required viability conditions.
#
#
#     FALLBACK CANDIDATE MUST EARN VIABILITY
# ==========================================================================


# ==========================================================================
# ROUTING MUST NOT SILENTLY LOWER REASONING REQUIREMENTS
# ==========================================================================
#
# Suppose:
#
#
#     AIRequest requires:
#
#         SECURITY_ANALYSIS
#
#         HEAVY reasoning
#
#
# Primary service is unavailable.
#
#
# Another service is:
#
#
#     permitted
#
#     healthy
#
#     reachable
#
#
# but supports only:
#
#
#     STANDARD reasoning
#
#
# It is not a valid fallback for the original requirement.
#
#
# The router must not silently change:
#
#
#     HEAVY
#
# into:
#
#     STANDARD
#
#
# merely to preserve availability.
#
#
# Therefore:
#
#
#     FALLBACK != REQUIREMENT DEGRADATION
#
#
# If future systems allow graceful degradation:
#
#
#     that must be an explicit policy / workload contract.
#
#
# It must not be an accidental router behavior.
# ==========================================================================


# ==========================================================================
# ROUTING MUST NOT SILENTLY CHANGE REQUIRED CAPABILITIES
# ==========================================================================
#
# Suppose a request requires:
#
#
#     STRUCTURED_OUTPUT
#
#     SECURITY_ANALYSIS
#
#
# A fallback service supports:
#
#
#     TEXT_GENERATION
#
#     SUMMARIZATION
#
#
# It is not equivalent.
#
#
# The fact that:
#
#
#     "It can produce text."
#
#
# does not mean:
#
#
#     "It can satisfy the request."
#
#
# Therefore:
#
#
#     SOME AI CAPABILITY
#         !=
#     REQUIRED AI CAPABILITY
#
#
#     FALLBACK MUST PRESERVE REQUEST REQUIREMENTS
# ==========================================================================


# ==========================================================================
# REQUEST REQUIREMENTS BELONG TO THE REQUEST / CAPABILITY DOMAIN
# ==========================================================================
#
# RoutingCandidate should not begin accumulating:
#
#
#     required_reasoning_level
#
#     required_capabilities
#
#     task
#
#     context
#
#
# merely so routing can remember the request.
#
#
# Those facts belong to AIRequest and related requirement contracts.
#
#
# Routing consumes them.
#
#
#     ROUTING INPUT != ROUTING OWNERSHIP
# ==========================================================================


# ==========================================================================
# SELECTED SERVICE ID IS THE OPERATIONAL DESTINATION
# ==========================================================================
#
# RoutingDecision selects:
#
#
#     AIService
#
#
# not merely:
#
#
#     AIModel
#
#
# Why?
#
#
# A logical model may have several operational exposures:
#
#
#     Model X
#         |
#         +-- company-cloud-east
#         |
#         +-- company-cloud-west
#         |
#         +-- company-onprem-primary
#
#
# Agent 11 eventually needs an operational destination.
#
#
# Therefore:
#
#
#     RoutingDecision.selected_service_id
#
#
# identifies the selected service.
#
#
# The service can resolve:
#
#
#     model identity
#
#     runtime/deployment information
#
#     endpoint information
#
#
# through neighboring domains.
#
#
#     SERVICE SELECTION != MODEL IDENTITY
# ==========================================================================


# ==========================================================================
# ROUTING DOMAIN IS PRESERVED FOR INTERPRETABILITY
# ==========================================================================
#
# Both:
#
#
#     RoutingCandidate
#
# and:
#
#     RoutingDecision
#
#
# preserve routing-domain context.
#
#
# This intentionally allows an operator to see:
#
#
#     selected service:
#
#         company-trading-reasoner-02
#
#
#     routing domain:
#
#         COMPANY_CLOUD_LLM
#
#
# without first consulting a registry.
#
#
# This is particularly useful when service names become:
#
#
#     opaque
#
#     historical
#
#     renamed
#
#     vendor-neutral
#
#
# or when the service registry changes after the decision was recorded.
#
#
#     DECISION CONTEXT HAS VALUE
# ==========================================================================


# ==========================================================================
# ROUTING DOMAIN STILL DOES NOT DEFINE CLOUD TOPOLOGY
# ==========================================================================
#
# Preserving routing_domain does NOT mean the field should expand into:
#
#
#     COMPANY_AWS_LLM
#
#     COMPANY_AZURE_LLM
#
#     COMPANY_GCP_LLM
#
#     COMPANY_OCI_LLM
#
#
# Those are deployment facts.
#
#
# The routing domain remains:
#
#
#     COMPANY_CLOUD_LLM
#
#
# Future deployment contracts may answer:
#
#
#     WHERE?
#
#
# Routing domain answers:
#
#
#     WHAT KIND OF AGENT 11 DESTINATION?
#
#
#     ROUTING DOMAIN != DEPLOYMENT TOPOLOGY
# ==========================================================================


# ==========================================================================
# ROUTING SEMANTICS SHOULD SURVIVE FRAMEWORK CHANGES
# ==========================================================================
#
# Agent 11 may eventually be called by:
#
#
#     ordinary Python
#
#     LangGraph
#
#     CrewAI
#
#     Bedrock AgentCore
#
#     MCP-integrated agents
#
#     future orchestration frameworks
#
#
# None of those frameworks should redefine:
#
#
#     VIABLE
#
#     REJECTED
#
#     SELECTED
#
#     BLOCKED
#
#     NO_VIABLE_ROUTE
#
#     NULL
#
#
# Those are Agent 11 domain semantics.
#
#
#     FRAMEWORKS MAY CHANGE
#
#     DOMAIN SEMANTICS SHOULD SURVIVE
# ==========================================================================


# ==========================================================================
# REASONING ROUTING AND MCP REMAIN DIFFERENT
# ==========================================================================
#
# Agent 11 may eventually support:
#
#
#     Reasoning Request
#         |
#         v
#     AI Model / Service Routing
#
#
# and:
#
#
#     Tool Request
#         |
#         v
#     MCP Service / Tool Resolution
#
#
# These concerns may cooperate.
#
# They are not the same routing problem.
#
#
#     AI SERVICE != MCP TOOL
#
#
#     REASONING ROUTING != TOOL ROUTING
#
#
# RoutingDecision in this file describes AI reasoning routing.
#
# It should not silently become the universal routing object for every
# Agent 11 subsystem.
# ==========================================================================


# ==========================================================================
# PART III — COMPLETE SEIR-I ROUTING FLOW
# ==========================================================================
#
#
#                         AIRequest
#                             |
#                             v
#                    REQUEST REQUIREMENTS
#                             |
#                             v
#                    CANDIDATE SERVICES
#                             |
#             +---------------+---------------+
#             |               |               |
#             v               v               v
#          Service A       Service B       Service C
#             |               |               |
#             v               v               v
#           POLICY          POLICY          POLICY
#             |               |               |
#             v               v               v
#         CAPABILITY       CAPABILITY       CAPABILITY
#             |               |               |
#             v               v               v
#       SERVICE STATE    SERVICE STATE    SERVICE STATE
#             |               |               |
#             v               v               v
#       NETWORK STATE    NETWORK STATE    NETWORK STATE
#             |               |               |
#             v               v               v
#       RoutingCandidate RoutingCandidate RoutingCandidate
#             |               |               |
#             +---------------+---------------+
#                             |
#                             v
#                         VIABLE SET
#                             |
#                             v
#                          SELECT
#                             |
#                             v
#                     RoutingDecision
#                             |
#             +---------------+---------------+
#             |               |               |
#             v               v               v
#          SELECTED      BLOCKED / NVR        NULL
#             |               |               |
#             v               v               v
#       AI INVOCATION        None             None
#             |
#             v
#        AIResponse
#
#
# NVR = NO_VIABLE_ROUTE
#
#
# This diagram is conceptual.
#
# It describes responsibility and flow.
#
# It does not require every future router implementation to execute
# literally in this exact procedural sequence.
# ==========================================================================


# ==========================================================================
# CHEWBACCA REVIEWS ROUTING SEMANTICS
# ==========================================================================
#
# Chewbacca:
#
#     "External FM is healthy."
#
#
# Agent 11:
#
#     POLICY?
#
#
# Chewbacca:
#
#     "Denied."
#
#
# Agent 11:
#
#     REJECT IT.
#
#
# Chewbacca:
#
#     "Company Cloud is healthy."
#
#
# Agent 11:
#
#     POLICY?
#
#
# Chewbacca:
#
#     "Allowed."
#
#
# Agent 11:
#
#     CAPABILITY?
#
#
# Chewbacca:
#
#     "Yes."
#
#
# Agent 11:
#
#     NETWORK?
#
#
# Chewbacca:
#
#     "Unavailable."
#
#
# Agent 11:
#
#     REJECT IT.
#
#
# Chewbacca:
#
#     "Company On-Prem is allowed, capable, healthy,
#      and reachable."
#
#
# Agent 11:
#
#     VIABLE.
#
#
# Chewbacca:
#
#     "So select it?"
#
#
# Agent 11:
#
#     IF ROUTING BEHAVIOR CHOOSES IT FROM THE VIABLE SET.
#
#
# Chewbacca:
#
#     "Could I use the external service instead?
#      It is 30 milliseconds faster."
#
#
# Agent 11:
#
#     NO.
#
#
# Chewbacca:
#
#     "Five cents cheaper?"
#
#
# Agent 11:
#
#     NO.
#
#
# Chewbacca:
#
#     "Better benchmark?"
#
#
# Agent 11:
#
#     POLICY DENIED IT.
#
#
# Chewbacca:
#
#     "What if the on-prem service fails?"
#
#
# Agent 11:
#
#     RE-EVALUATE ANOTHER CANDIDATE.
#
#
# Chewbacca:
#
#     "And if every remaining candidate is denied
#      or unavailable?"
#
#
# Agent 11:
#
#     NO VIABLE ROUTE.
#
#
# Chewbacca:
#
#     "So I return nothing?"
#
#
# Agent 11:
#
#     YOU RETURN A RoutingDecision.
#
#
# Chewbacca:
#
#     "But no AIResponse?"
#
#
# Agent 11:
#
#     CORRECT.
#
#
# Chewbacca:
#
#     "That feels like failure."
#
#
# Agent 11:
#
#     SOMETIMES REFUSING TO INVENT A ROUTE
#     IS THE SYSTEM WORKING CORRECTLY.
#
# ==========================================================================


# ==========================================================================
# PART III — ROUTING SEMANTIC MATRIX
# ==========================================================================
#
#
#     ---------------------------------------------------------------
#     CONDITION                           CANDIDATE / FINAL MEANING
#     ---------------------------------------------------------------
#
#     Policy denied candidate             REJECTED / POLICY_DENIED
#
#     Capability insufficient             REJECTED / CAPABILITY_MISMATCH
#
#     Service unavailable                 REJECTED / SERVICE_UNAVAILABLE
#
#     Network unavailable                 REJECTED / NETWORK_UNAVAILABLE
#
#     All required gates satisfied        VIABLE
#
#     Viable candidate chosen             SELECTED
#
#     Policy prevents AI routing          BLOCKED
#
#     Permitted route exists in theory,
#     but none is operationally viable    NO_VIABLE_ROUTE
#
#     AI routing intentionally unused     NULL
#
#
# Remember:
#
#
#     CANDIDATE OUTCOME != FINAL ROUTING OUTCOME
# ==========================================================================


# ==========================================================================
# PART III — FINAL SEIR-I ROUTING INVARIANTS
# ==========================================================================
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
#     CONSTRAINTS FIRST
#
#     OPTIMIZATION SECOND
#
#
#     POLICY NEVER BECOMES A SCORE
#
#
#     SCORE != VIABILITY
#
#
#     CAPABLE != VIABLE
#
#
#     AUTHORIZED != VIABLE
#
#
#     AVAILABLE != VIABLE
#
#
#     REACHABLE != VIABLE
#
#
#     VIABLE != SELECTED
#
#
#     REJECTED != FAILED
#
#
#     CANDIDATE STATUS != ROUTING STATUS
#
#
#     CANDIDATE POLICY REJECTION != FINAL ROUTING BLOCK
#
#
#     BLOCKED != NO_VIABLE_ROUTE
#
#
#     NO_VIABLE_ROUTE != NULL
#
#
#     NULL != FAILURE
#
#
#     NO_VIABLE_ROUTE != ROUTER FAILURE
#
#
#     INTENTIONAL NO ROUTE != FAILED ROUTE
#
#
#     REACHABLE != AUTHORIZED
#
#
#     AUTHORIZED != REACHABLE
#
#
#     HEALTHY != PERMITTED
#
#
#     HEALTHY != REACHABLE
#
#
#     UNREACHABLE != UNHEALTHY
#
#
#     NETWORK UNAVAILABLE != SERVICE UNAVAILABLE
#
#
#     CHEAPER != PERMITTED
#
#
#     FASTER != PERMITTED
#
#
#     UNKNOWN != UNAVAILABLE
#
#
#     INDETERMINATE != DENY
#
#
#     FAIL CLOSED != ERASE SEMANTICS
#
#
#     FAIL CLOSED != FALSIFY OBSERVED STATE
#
#
#     OBSERVATION != DECISION
#
#
#     USER MAY NARROW POLICY
#
#     USER MAY NOT EXPAND POLICY
#
#
#     FALLBACK = RE-EVALUATION
#
#
#     FALLBACK != POLICY ESCAPE
#
#
#     FALLBACK != STATIC SERVICE POINTER
#
#
#     NEXT_VIABLE != NEXT
#
#
#     FALLBACK MUST NOT REDUCE SECURITY POLICY
#
#
#     FALLBACK != REQUIREMENT DEGRADATION
#
#
#     FALLBACK MUST PRESERVE REQUEST REQUIREMENTS
#
#
#     MODEL SELECTION != SERVICE SELECTION
#
#
#     SERVICE SELECTION != NETWORK PATH SELECTION
#
#
#     ROUTING DOMAIN != CLOUD PROVIDER
#
#
#     ROUTING DOMAIN != MODEL PROVIDER
#
#
#     ROUTING DOMAIN != DEPLOYMENT LOCATION
#
#
#     ROUTER != POLICY ENGINE
#
#
#     ROUTER != MODEL KNOWLEDGE DATABASE
#
#
#     ROUTER != HEALTH CHECK IMPLEMENTATION
#
#
#     AI ROUTING != NETWORK ROUTING
#
#
#     BGP != AI AUTHORIZATION
#
#
#     SD-WAN != AI POLICY
#
#
#     ROUTING DECISION != AI INVOCATION
#
#
#     SELECTED != INVOKED
#
#
#     INVOKED != SUCCESSFUL
#
#
#     ROUTING SUCCESS != INFERENCE SUCCESS
#
#
#     INFERENCE SUCCESS != CORRECTNESS
#
#
#     AI OUTPUT != ACTION AUTHORITY
#
#
#     REASONING CAPABILITY != EXECUTION AUTHORITY
#
#
#     NO INVOCATION => NO AIResponse
#
#
#     BLOCKED => NO AIResponse
#
#
#     NO_VIABLE_ROUTE => NO AIResponse
#
#
#     NULL => NO AIResponse
#
#
#     ROUTING CONSUMES DOMAIN FACTS
#
#     ROUTING DOES NOT BECOME EVERY DOMAIN
#
#
#     ROUTING INPUT != ROUTING OWNERSHIP
#
#
#     DECISION != PROVENANCE
#
#
#     AUDITABLE != EVERYTHING IN ONE OBJECT
#
#
#     HUMAN EXPLANATION != MACHINE CONTROL
#
#
#     TELEMETRY SHOULD PRESERVE DOMAIN SEMANTICS
#
#
#     AVAILABILITY PRESSURE != POLICY EXCEPTION
#
#
#     EMERGENCY POLICY != ROUTER BYPASS
#
#
#     NO ROUTE CAN BE THE CORRECT ROUTING ANSWER
#
#
#     FRAMEWORKS MAY CHANGE
#
#     DOMAIN SEMANTICS SHOULD SURVIVE
#
# ==========================================================================
# END PART III
# ==========================================================================

# ==========================================================================
# PART IV — SEIR-II EXPANSION MARKER — DO NOT DELETE
# ==========================================================================
#
# This section is intentionally documentation only.
#
#
#     SEIR-II EXPANSION MARKER — DO NOT DELETE
#
#
# Parts I through III establish the SEIR-I routing contract.
#
# Part IV documents where that contract is expected to grow.
#
#
# It exists for the engineer who opens this file later and asks:
#
#
#     "Why didn't they just add cloud_provider to AIRoute?"
#
#
#     "Why isn't policy part of the routing score?"
#
#
#     "Why can't fallback just call Claude?"
#
#
#     "Why don't we put latency, cost, GPU utilization, BGP state,
#      policy evidence, deployment information, and model quality
#      directly into RoutingCandidate?"
#
#
#     "Why do we need a RoutingPlan if RoutingDecision already exists?"
#
#
# Because those apparently convenient changes collapse architectural
# boundaries that SEIR-II will need.
#
#
# This section preserves those boundaries before the requirements arrive.
#
#
#     FUTURE REQUIREMENTS SHOULD EXTEND THE CONTRACT
#
#     FUTURE REQUIREMENTS SHOULD NOT DESTROY THE CONTRACT
#
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 1 — VIABILITY BEFORE OPTIMIZATION
# ==========================================================================
#
# SEIR-I establishes:
#
#
#                         VIABLE ROUTE
#
#                              =
#
#                       POLICY PERMITTED
#
#                              +
#
#                       SERVICE CAPABLE
#
#                              +
#
#                      SERVICE AVAILABLE
#
#                              +
#
#                        PATH AVAILABLE
#
#
# SEIR-II will likely introduce optimization after those constraints.
#
#
# Future routing may consider:
#
#
#     quality
#
#     latency
#
#     capacity
#
#     cost
#
#     locality
#
#     organizational preference
#
#     failure-domain diversity
#
#     model specialization
#
#     deployment efficiency
#
#
# But the order remains:
#
#
#     ALL CANDIDATES
#          |
#          v
#     REQUIRED CONSTRAINTS
#          |
#          v
#       VIABLE SET
#          |
#          v
#      OPTIMIZATION
#          |
#          v
#       SELECTION
#
#
# Never:
#
#
#     ALL CANDIDATES
#          |
#          v
#     GIANT WEIGHTED SCORE
#          |
#          v
#     HIGHEST NUMBER WINS
#
#
# because that eventually creates:
#
#
#     "Policy denied the destination,
#      but it had an excellent latency score."
#
#
# No.
#
#
#     CONSTRAINTS FIRST
#
#     OPTIMIZATION SECOND
#
#
#     POLICY NEVER BECOMES A SCORE
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 2 — TYPED OPTIMIZATION CRITERIA
# ==========================================================================
#
# SEIR-I deliberately does NOT define:
#
#
#     score: float
#
#
# Future engineers may be tempted to add:
#
#
#     score = 0.91
#
#
# But:
#
#
#     0.91 WHAT?
#
#
# A future evaluation contract should preserve meaning.
#
#
# Possible future concepts:
#
#
#     RoutingEvaluation
#
#         quality_score
#
#         latency_score
#
#         capacity_score
#
#         cost_score
#
#         locality_score
#
#
# The exact fields should be designed when those requirements become
# real.
#
#
# The important architectural rule is:
#
#
#     TYPED CRITERIA > OPAQUE NUMBER
#
#
# Even if a future optimizer eventually computes a composite ranking,
# the component semantics should remain inspectable.
#
#
# Most importantly:
#
#
#     HIGHEST SCORE != POLICY OVERRIDE
#
#
# A rejected candidate does not return to the viable set because its
# optimization score is attractive.
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 3 — CAPACITY-AWARE ROUTING
# ==========================================================================
#
# A service can be:
#
#
#     policy permitted
#
#     capable
#
#     healthy
#
#     reachable
#
#
# while simultaneously being:
#
#
#     overloaded
#
#
# Future routing may need to consider:
#
#
#     queue depth
#
#     concurrent requests
#
#     token throughput
#
#     GPU utilization
#
#     memory pressure
#
#     admission-control state
#
#     tenant quotas
#
#     rate limits
#
#     reserved capacity
#
#
# But capacity semantics require care.
#
#
# Example:
#
#
#     queue_depth = 100
#
#
# Is that:
#
#
#     unavailable?
#
#     degraded?
#
#     merely slower?
#
#     perfectly normal for that service?
#
#
# Therefore:
#
#
#     CAPACITY != SIMPLE BOOLEAN
#
#
# SEIR-II must decide whether capacity is:
#
#
#     a hard viability constraint
#
# or:
#
#     an optimization preference
#
#
# depending on the service and workload contract.
#
#
# Do not prematurely encode:
#
#
#     has_capacity: bool
#
#
# without defining what capacity actually means.
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 4 — INFERENCE ENGINEERING
# ==========================================================================
#
# As Agent 11 begins routing to company-hosted inference infrastructure,
# routing may consume inference-engineering telemetry.
#
#
# Examples:
#
#
#     tokens per second
#
#     time to first token
#
#     batching efficiency
#
#     batch size
#
#     KV-cache utilization
#
#     context utilization
#
#     GPU memory utilization
#
#     accelerator utilization
#
#     tensor parallelism
#
#     pipeline parallelism
#
#     quantization
#
#     model-serving runtime
#
#     warm / cold state
#
#     context-window pressure
#
#     inference queue depth
#
#
# These observations may influence:
#
#
#     capacity
#
#     latency
#
#     cost
#
#     quality
#
#     destination preference
#
#
# But:
#
#
#     ROUTING INPUT
#         !=
#     ROUTING DECISION FIELD
#
#
# Do not automatically copy every inference metric into RoutingDecision.
#
#
# Future telemetry and runtime-state contracts should own those facts.
#
#
# Routing consumes the facts necessary to make a decision.
#
#
#     ROUTING != INFERENCE TELEMETRY DATABASE
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 5 — NETWORK-AWARE AI ROUTING
# ==========================================================================
#
# SEIR-I network viability may begin with:
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
# and path types such as:
#
#
#     LOCAL
#
#     INTERNET
#
#     VPN
#
#     PRIVATE_LINK
#
#     SD_WAN
#
#     BGP
#
#     STREET_ACCESS
#
#
# Yes.
#
# STREET_ACCESS remains legitimate.
#
# Chewbacca may still be carrying the packets across the street.
#
#
# SEIR-II may need richer network observations:
#
#
#     latency
#
#     jitter
#
#     packet loss
#
#     path health
#
#     path preference
#
#     private connectivity state
#
#     SD-WAN SLA state
#
#     BGP route availability
#
#     prefix reachability
#
#     route withdrawal
#
#     transit dependency
#
#     network failure domain
#
#
# These facts can influence whether an approved AI destination is
# operationally usable.
#
#
# But:
#
#
#     AI ROUTING != NETWORK ROUTING
#
#
# Agent 11 answers:
#
#
#     WHICH APPROVED AI SERVICE SHOULD HANDLE THIS REQUEST?
#
#
# BGP / SD-WAN answer:
#
#
#     HOW DO PACKETS REACH THAT DESTINATION?
#
#
# Therefore:
#
#
#     BGP REACHABILITY != AI AUTHORIZATION
#
#
#     SD-WAN PREFERENCE != AI POLICY
#
#
#     NETWORK PATH != AI SERVICE
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 6 — FAILURE-DOMAIN-AWARE ROUTING
# ==========================================================================
#
# Future Agent 11 deployments may register several AI services:
#
#
#     Service A
#
#     Service B
#
#     Service C
#
#
# This looks redundant.
#
#
# It may not be.
#
#
# Example:
#
#
#     Service A
#         Azure region 1
#
#
#     Service B
#         Azure region 1
#
#
#     Service C
#         Azure region 1
#
#
# All three may share:
#
#
#     cloud provider
#
#     region
#
#     identity provider
#
#     private network
#
#     GPU cluster
#
#     inference runtime
#
#     storage
#
#     model artifact
#
#
# One failure may remove all three.
#
#
# Therefore:
#
#
#     MULTIPLE SERVICES != TRUE REDUNDANCY
#
#
# Future failure-domain modeling may need:
#
#
#     cloud provider
#
#     region
#
#     availability zone
#
#     inference cluster
#
#     identity dependency
#
#     network dependency
#
#     model-serving dependency
#
#     control-plane dependency
#
#
# Routing may eventually prefer destinations with independent failure
# domains.
#
#
# This belongs in future deployment/runtime topology contracts.
#
#
# Do not encode it into AIRoute.
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 7 — MULTI-CLOUD COMPANY LLM ROUTING
# ==========================================================================
#
# THIS IS A MAJOR FUTURE EXPANSION POINT.
#
#
# SEIR-I defines:
#
#
#     COMPANY_CLOUD_LLM
#
#
# This is intentionally provider-neutral.
#
#
# It must NEVER silently become:
#
#
#     AWS_COMPANY_LLM
#
#
# because future enterprise environments may look like:
#
#
#                         AGENT 11
#                            |
#                            v
#                   COMPANY_CLOUD_LLM
#                            |
#          +-----------------+-----------------+
#          |                 |                 |
#          v                 v                 v
#         AWS              AZURE              GCP
#          |                 |                 |
#          v                 v                 v
#     Company LLM       Company LLM       Company LLM
#          |
#          +-----------------------------+
#                                        |
#                                        v
#                                       OCI
#
#
# And later:
#
#
#     sovereign cloud
#
#     specialized AI cloud
#
#     colocation environment
#
#     future provider
#
#
# These may all remain:
#
#
#     COMPANY_CLOUD_LLM
#
#
# because AIRoute describes the Agent 11 routing domain.
#
#
# It does not describe the physical deployment provider.
#
#
#     ROUTING DOMAIN != CLOUD PROVIDER
# ==========================================================================


# ==========================================================================
# SEIR-II MULTI-CLOUD EXAMPLE
# ==========================================================================
#
# Imagine a company with:
#
#
#     Agent 11 control plane
#         running in AWS
#
#
#     proprietary trading model
#         deployed through GCP infrastructure
#
#
#     security reasoning service
#         deployed in Azure
#
#
#     document model
#         deployed in OCI
#
#
#     sensitive internal model
#         deployed on-premises
#
#
# Agent 11 may see:
#
#
#     Trading Service
#
#         routing_domain =
#             COMPANY_CLOUD_LLM
#
#         cloud_provider =
#             GCP
#
#
#     Security Service
#
#         routing_domain =
#             COMPANY_CLOUD_LLM
#
#         cloud_provider =
#             AZURE
#
#
#     Document Service
#
#         routing_domain =
#             COMPANY_CLOUD_LLM
#
#         cloud_provider =
#             OCI
#
#
#     Sensitive Internal Service
#
#         routing_domain =
#             COMPANY_ONPREM_LLM
#
#
# Nothing about this requires AIRoute to become cloud-specific.
#
#
# That separation is deliberate.
#
#
#     ROUTING DOMAIN
#
# answers:
#
#     WHAT TRUST / OPERATIONAL DESTINATION CLASS IS THIS?
#
#
# Deployment metadata answers:
#
#     WHERE IS THIS INSTANCE ACTUALLY RUNNING?
# ==========================================================================


# ==========================================================================
# SEIR-II MULTI-CLOUD DEPLOYMENT CONTRACT
# ==========================================================================
#
# A future deployment/runtime model may eventually need facts such as:
#
#
#     deployment_id
#
#     service_id
#
#     cloud_provider
#
#     region
#
#     availability_zone
#
#     account
#
#     subscription
#
#     project
#
#     tenancy
#
#     cluster
#
#     namespace
#
#     private_connectivity
#
#     data_residency
#
#     sovereignty_boundary
#
#     failure_domain
#
#
# Do NOT add those fields to RoutingCandidate merely because routing
# may eventually consume them.
#
#
# They describe:
#
#
#     DEPLOYMENT REALITY
#
#
# not:
#
#
#     CANDIDATE OUTCOME
#
#
# Future shape may conceptually become:
#
#
#     AIModel
#         |
#         v
#     AIService
#         |
#         v
#     Deployment
#         |
#         v
#     Runtime State
#         |
#         v
#     Routing Evaluation
#
#
# The exact SEIR-II model should be designed when deployment routing is
# implemented.
#
#
#     MODEL != SERVICE != DEPLOYMENT != ROUTING DECISION
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 8 — MODEL PROVIDER IS NOT DEPLOYMENT PROVIDER
# ==========================================================================
#
# Future enterprise AI makes this distinction increasingly important.
#
#
# A model may originate from:
#
#
#     Anthropic
#
#     OpenAI
#
#     Google
#
#     Meta
#
#     Mistral
#
#     company internal research
#
#     another model provider
#
#
# while being exposed through infrastructure operated by:
#
#
#     AWS
#
#     Azure
#
#     GCP
#
#     OCI
#
#     company on-premises infrastructure
#
#     another environment
#
#
# Therefore:
#
#
#     MODEL PROVIDER != DEPLOYMENT PROVIDER
#
#
#     MODEL PROVIDER != ROUTING DOMAIN
#
#
#     DEPLOYMENT PROVIDER != ROUTING DOMAIN
#
#
#     MODEL IDENTITY != DEPLOYMENT IDENTITY
#
#
# Preserve these distinctions.
#
#
# Future enterprise architectures will make them more important,
# not less.
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 9 — DATA RESIDENCY AND SOVEREIGNTY
# ==========================================================================
#
# Multi-cloud routing may eventually need to respect:
#
#
#     geographic residency
#
#     legal jurisdiction
#
#     sovereign-cloud requirements
#
#     contractual boundaries
#
#     customer-specific restrictions
#
#     regulated-industry requirements
#
#
# Example:
#
#
#     COMPANY_CLOUD_LLM
#
#
# may contain two otherwise equivalent services:
#
#
#     Service A
#         region = US
#
#
#     Service B
#         region = EU
#
#
# A request may be permitted to use:
#
#
#     COMPANY_CLOUD_LLM
#
#
# while still being prohibited from:
#
#
#     Service A
#
#
# because the deployment location violates a residency rule.
#
#
# Therefore:
#
#
#     ROUTING DOMAIN AUTHORIZATION
#         MAY NOT BE SUFFICIENT
#
#
# Future policy may evaluate deployment attributes as part of
# authorization.
#
#
# This still does not mean:
#
#
#     policy belongs inside AIRoute.
#
#
#     ROUTING DOMAIN != COMPLETE POLICY DECISION
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 10 — COST-AWARE ROUTING
# ==========================================================================
#
# Future routing may consider:
#
#
#     input-token cost
#
#     output-token cost
#
#     reserved inference capacity
#
#     accelerator cost
#
#     egress cost
#
#     cross-cloud transfer cost
#
#     private-connectivity cost
#
#     internal chargeback
#
#     tenant budget
#
#
# Cost can influence selection among viable candidates.
#
#
# Cost cannot make a prohibited candidate viable.
#
#
# Example:
#
#
#     External Service A
#
#         policy = DENY
#         cost = $0.001
#
#
#     Company Service B
#
#         policy = ALLOW
#         cost = $0.010
#
#
# Result:
#
#
#     Service A is not a bargain.
#
#     Service A is not eligible.
#
#
# Therefore:
#
#
#     CHEAP != PERMITTED
#
#
#     COST OPTIMIZATION != AUTHORIZATION
#
#
#     CONSTRAINT FIRST
#
#     OPTIMIZATION SECOND
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 11 — QUALITY-AWARE ROUTING
# ==========================================================================
#
# Future routing may compare model/service quality.
#
#
# But:
#
#
#     "BEST MODEL"
#
#
# is usually incomplete.
#
#
# Best at:
#
#
#     code?
#
#     mathematics?
#
#     security analysis?
#
#     summarization?
#
#     structured output?
#
#     long context?
#
#     tool use?
#
#     financial reasoning?
#
#
# Quality is task-relative.
#
#
# Therefore:
#
#
#     MODEL QUALITY IS TASK-RELATIVE
#
#
# Future quality evaluation may consume:
#
#
#     benchmark results
#
#     organization-specific evaluations
#
#     task-specific evaluations
#
#     historical success metrics
#
#     hallucination measurements
#
#     structured-output reliability
#
#     safety evaluations
#
#
# These should remain typed and attributable.
#
#
#     QUALITY != UNIVERSAL SCALAR TRUTH
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 12 — EVALUATION DATA MUST HAVE PROVENANCE
# ==========================================================================
#
# Suppose future routing says:
#
#
#     Model A quality = 0.94
#
#
# An engineer should eventually be able to ask:
#
#
#     according to which evaluation?
#
#     against which task?
#
#     using which dataset?
#
#     using which model version?
#
#     measured when?
#
#
# Otherwise:
#
#
#     0.94
#
#
# becomes another mystery number.
#
#
# Future routing optimization should therefore be compatible with:
#
#
#     evaluation provenance
#
#     model versioning
#
#     benchmark versioning
#
#     measurement timestamps
#
#
#     SCORE WITHOUT CONTEXT != TRUSTWORTHY EVIDENCE
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 13 — POLICY REJECTION MAY NEED RICHER DETAIL
# ==========================================================================
#
# SEIR-I currently summarizes candidate policy rejection as:
#
#
#     POLICY_DENIED
#
#
# This is intentionally compact.
#
#
# Future policy systems may need to explain:
#
#
#     which policy denied the route
#
#     which policy version
#
#     which data classification
#
#     which user restriction
#
#     which residency requirement
#
#     which organizational rule
#
#     whether the result was explicit DENY or INDETERMINATE
#
#
# Do not respond by adding fifteen policy fields to RoutingCandidate.
#
#
# Future architecture may introduce:
#
#
#     PolicyRejection
#
# or:
#
#     PolicyDecision reference
#
#
# while RoutingCandidate retains:
#
#
#     rejection_reason = POLICY_DENIED
#
#
# This preserves:
#
#
#     ROUTING SUMMARY
#
# separately from:
#
#     POLICY EVIDENCE
#
#
#     REJECTION REASON != REJECTION EVIDENCE
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 14 — CANDIDATE EVALUATION PROVENANCE
# ==========================================================================
#
# Future audit requirements may need to reconstruct:
#
#
#     WHY WAS THIS CANDIDATE CONSIDERED VIABLE?
#
#
# A future CandidateEvaluation concept may reference:
#
#
#     service
#
#     model
#
#     deployment
#
#     capability evaluation
#
#     policy decision
#
#     service-state observation
#
#     network observation
#
#     evaluation timestamp
#
#     final candidate outcome
#
#
# Conceptually:
#
#
#     CandidateEvaluation
#
#         +-- service reference
#
#         +-- policy evidence reference
#
#         +-- capability evidence reference
#
#         +-- service observation reference
#
#         +-- network observation reference
#
#         +-- outcome
#
#
# This is preferable to:
#
#
#     RoutingCandidate
#         with forty optional fields
#
#
#     PROVENANCE SHOULD LINK EVIDENCE
#
#     PROVENANCE SHOULD NOT CREATE EnterpriseBlobObject.py
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 15 — TIME MATTERS
# ==========================================================================
#
# SEIR-I intentionally avoids adding timestamps everywhere.
#
#
# Future routing will eventually care about:
#
#
#     when policy was evaluated
#
#     when service health was observed
#
#     when network state was observed
#
#     when capacity was measured
#
#     when routing occurred
#
#     when fallback occurred
#
#     how long evidence remains valid
#
#
# Example:
#
#
#     network = AVAILABLE
#
#
# observed:
#
#
#     45 minutes ago
#
#
# may not be useful evidence for:
#
#
#     current routing
#
#
# Therefore future contracts may need:
#
#
#     observed_at
#
#     evaluated_at
#
#     valid_until
#
#     freshness window
#
#
# But:
#
#
#     TIMESTAMP != FRESHNESS
#
#
# Freshness is a semantic rule applied to time.
#
#
#     OLD OBSERVATION != CURRENT TRUTH
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 16 — STALE EVIDENCE
# ==========================================================================
#
# Future Agent 11 routing must distinguish:
#
#
#     OBSERVED AVAILABLE
#
# from:
#
#     CURRENTLY KNOWN AVAILABLE
#
#
# Example:
#
#
#     service health observation:
#
#         AVAILABLE
#
#         observed 30 minutes ago
#
#
# Depending on the service contract, that observation may now be stale.
#
#
# Therefore:
#
#
#     STALE OBSERVATION != CURRENT TRUTH
#
#
# Routing may need evidence-freshness requirements before declaring a
# candidate viable.
#
#
# Do not solve this by changing:
#
#
#     AVAILABLE
#
# into:
#
#     UNAVAILABLE
#
#
# The original observation remains what it was.
#
#
# Routing decides whether that evidence is still sufficient.
#
#
#     OBSERVATION != EVIDENCE SUFFICIENCY
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 17 — UNKNOWN-STATE POLICY
# ==========================================================================
#
# SEIR-I preserves:
#
#
#     UNKNOWN != UNAVAILABLE
#
#
# SEIR-II may need explicit rules for how UNKNOWN observations affect
# routing.
#
#
# Possible future behaviors may include:
#
#
#     fail closed
#
#     probe before use
#
#     use only for low-risk workloads
#
#     use last-known-good evidence within a validity window
#
#     require alternate verification
#
#
# The exact rule belongs to routing / policy behavior.
#
#
# Do NOT redefine:
#
#
#     UNKNOWN
#
# as:
#
#     UNAVAILABLE
#
#
# merely because the conservative action is rejection.
#
#
#     OBSERVED STATE != DECISION RULE
#
#
#     UNKNOWN REMAINS UNKNOWN
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 18 — GOVERNANCE LIFECYCLE
# ==========================================================================
#
# Future AI resources may have governance states such as:
#
#
#     experimental
#
#     evaluating
#
#     approved
#
#     production
#
#     deprecated
#
#     retired
#
#
# A model/service can be:
#
#
#     technically capable
#
#     operationally healthy
#
#     network reachable
#
#
# while still being:
#
#
#     NOT APPROVED FOR PRODUCTION
#
#
# Therefore:
#
#
#     TECHNICALLY VIABLE
#         MAY NOT EQUAL
#     GOVERNANCE ELIGIBLE
#
#
# Future viability may gain another required gate:
#
#
#     GOVERNANCE ELIGIBLE
#
#
# if the organization requires it.
#
#
# The important point is to preserve the distinction.
#
#
#     TECHNICAL CAPABILITY != GOVERNANCE APPROVAL
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 19 — MULTI-MODEL EXECUTION
# ==========================================================================
#
# SEIR-I RoutingDecision selects one operational AI service.
#
#
# Future workflows may intentionally use several models.
#
#
# Example:
#
#
#     AIRequest
#         |
#         +--> Model A
#         |
#         +--> Model B
#         |
#         +--> Evaluator Model C
#
#
# This is not ordinary fallback.
#
#
# All three may be intentionally invoked.
#
#
# Future use cases:
#
#
#     parallel reasoning
#
#     model comparison
#
#     evaluator models
#
#     critic models
#
#     voting
#
#     consensus
#
#     specialized subproblems
#
#     adversarial review
#
#
# Therefore:
#
#
#     MULTI-MODEL EXECUTION != FALLBACK
#
#
#     FAN-OUT != FALLBACK
#
#
#     CONSENSUS != RETRY
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 20 — RoutingDecision VS RoutingPlan
# ==========================================================================
#
# If one request eventually requires multiple coordinated destinations,
# do not force RoutingDecision to mean two different things.
#
#
# A future abstraction may be:
#
#
#     RoutingDecision
#
#         one atomic destination decision
#
#
#     RoutingPlan
#
#         coordinated collection of routing decisions
#
#
# Example:
#
#
#     RoutingPlan
#         |
#         +-- Decision A --> Security Model
#         |
#         +-- Decision B --> Code Model
#         |
#         +-- Decision C --> Evaluator Model
#
#
# This preserves the clean SEIR-I meaning of RoutingDecision.
#
#
#     ROUTING DECISION = ATOMIC DECISION
#
#
#     ROUTING PLAN = COORDINATED DECISIONS
#
#
# Do not turn selected_service_id into:
#
#
#     selected_service_ids: list[str]
#
#
# merely because multi-model execution arrives.
#
#
# That would change the meaning of the existing contract.
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 21 — FAN-OUT AND FALLBACK ARE DIFFERENT
# ==========================================================================
#
# FALLBACK:
#
#
#     Try A
#
#     if A is not viable / cannot continue,
#
#     evaluate B
#
#
# FAN-OUT:
#
#
#     Intentionally invoke A and B
#
#
# These are fundamentally different execution semantics.
#
#
# Likewise:
#
#
# RETRY:
#
#
#     attempt the same intended operation again
#
#
# CONSENSUS:
#
#
#     intentionally collect multiple reasoning results
#
#
# Therefore:
#
#
#     FAN-OUT != FALLBACK
#
#
#     CONSENSUS != RETRY
#
#
# Future telemetry and orchestration should preserve those distinctions.
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 22 — AGENTIC ROUTING
# ==========================================================================
#
# Future agents should generally express:
#
#
#     WHAT THEY NEED
#
#
# rather than:
#
#
#     WHICH PROVIDER THEY WANT
#
#
# Example:
#
#
# Better:
#
#
#     "I require:
#
#         SECURITY_ANALYSIS
#         HEAVY reasoning
#         STRUCTURED_OUTPUT"
#
#
# Worse:
#
#
#     "Send this to Provider X."
#
#
# Agent 11 should retain authority over destination selection according
# to policy and platform state.
#
#
# Therefore:
#
#
#     AGENT REQUESTS CAPABILITY
#
#     AGENT DOES NOT NECESSARILY CHOOSE PROVIDER
#
#
# This allows:
#
#
#     provider replacement
#
#     multi-cloud deployment
#
#     failover
#
#     cost optimization
#
#     policy changes
#
#     model upgrades
#
#
# without rewriting every consuming agent.
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 23 — AGENT REQUEST DOES NOT GRANT AUTHORITY
# ==========================================================================
#
# An agent may request:
#
#
#     EXTERNAL_FM
#
#
# or:
#
#     TOOL_USE
#
#
# or:
#
#     HEAVY reasoning
#
#
# That request is:
#
#
#     INTENT
#
#
# not:
#
#     AUTHORIZATION
#
#
# Agent 11 still applies:
#
#
#     organizational policy
#
#     user restrictions
#
#     capability requirements
#
#     service state
#
#     network state
#
#     future governance requirements
#
#
# Therefore:
#
#
#     REQUEST != AUTHORIZATION
#
#
#     AGENT INTENT != POLICY DECISION
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 24 — FRAMEWORK INDEPENDENCE
# ==========================================================================
#
# Agent 11 may eventually be called from:
#
#
#     Python
#
#     LangGraph
#
#     CrewAI
#
#     Bedrock AgentCore
#
#     MCP-aware agents
#
#     custom orchestrators
#
#     frameworks that do not exist yet
#
#
# The framework may ask Agent 11:
#
#
#     "Route this reasoning request."
#
#
# Agent 11 returns its own domain objects.
#
#
# The framework should not redefine:
#
#
#     RoutingCandidate
#
#     RoutingDecision
#
#     RoutingStatus
#
#     AIRoute
#
#
# merely because its own API uses different terminology.
#
#
# Adapter code should translate.
#
#
# Domain contracts should survive.
#
#
#     FRAMEWORKS CHANGE
#
#     DOMAIN CONTRACTS SHOULD SURVIVE THEM
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 25 — CONTROL PLANE VS INFERENCE PLANE
# ==========================================================================
#
# Agent 11 increasingly resembles an AI control-plane component.
#
#
# It may coordinate:
#
#
#     policy
#
#     routing
#
#     service discovery
#
#     governance
#
#     lifecycle
#
#     telemetry
#
#     provenance
#
#
# But the control plane generally does not need to become the inference
# engine itself.
#
#
# Conceptually:
#
#
#                  AI CONTROL PLANE
#
#                +------------------+
#                |     Agent 11     |
#                |                  |
#                | policy           |
#                | routing          |
#                | governance       |
#                | coordination     |
#                +--------+---------+
#                         |
#                         v
#
#                  INFERENCE PLANE
#
#              +----------+----------+
#              |          |          |
#              v          v          v
#             AWS       Azure       GCP
#              |          |          |
#              v          v          v
#             LLM        LLM        LLM
#
#
# This separation supports multi-cloud inference without requiring the
# Agent 11 control plane to live beside every inference service.
#
#
#     CONTROL PLANE != INFERENCE PLANE
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 26 — CROSS-CLOUD NETWORK REALITY
# ==========================================================================
#
# Multi-cloud AI routing introduces real network dependencies.
#
#
# Example:
#
#
#     Agent 11
#         AWS
#
#          |
#          v
#
#     proprietary trading inference
#         GCP
#
#
# Authorization may say:
#
#
#     ALLOW
#
#
# Capability may say:
#
#
#     PASS
#
#
# Service health may say:
#
#
#     AVAILABLE
#
#
# But cross-cloud connectivity may say:
#
#
#     UNAVAILABLE
#
#
# Therefore:
#
#
#     NO VIABLE ROUTE
#
#
# Future connectivity may involve:
#
#
#     public Internet
#
#     site-to-site VPN
#
#     private interconnect
#
#     cloud exchange
#
#     SD-WAN
#
#     BGP
#
#     service mesh
#
#     private service endpoints
#
#
# Again:
#
#
#     AUTHORIZATION != CONNECTIVITY
#
#
#     CONNECTIVITY != AUTHORIZATION
#
#
# Multi-cloud makes this distinction more important.
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 27 — CROSS-CLOUD COST IS NOT JUST TOKEN COST
# ==========================================================================
#
# Future optimization may need to consider:
#
#
#     inference cost
#
#     network egress
#
#     cross-region transfer
#
#     cross-cloud transfer
#
#     private connectivity
#
#     accelerator reservation
#
#     storage access
#
#     observability ingestion
#
#
# A model that appears cheaper per token may produce a more expensive
# end-to-end execution path.
#
#
# Therefore:
#
#
#     MODEL PRICE != TOTAL ROUTE COST
#
#
# Future cost models should be explicit about what they measure.
#
#
# Again:
#
#
#     COST DOES NOT OVERRIDE POLICY
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 28 — IDENTITY AND ACCESS DEPENDENCIES
# ==========================================================================
#
# Future routing may select a service that is:
#
#
#     permitted
#
#     capable
#
#     healthy
#
#     network reachable
#
#
# while authentication to that service is unavailable.
#
#
# Examples:
#
#
#     expired workload identity
#
#     unavailable token service
#
#     broken federation
#
#     cloud IAM outage
#
#     secret rotation problem
#
#
# This raises a future architectural question:
#
#
#     Is authentication readiness part of service availability?
#
# or:
#
#     Does Agent 11 need an explicit access-readiness gate?
#
#
# Do not answer by casually adding:
#
#
#     credentials_work: bool
#
#
# to RoutingCandidate.
#
#
# Model the domain when the requirement arrives.
#
#
#     IDENTITY STATE != NETWORK STATE
#
#
#     NETWORK REACHABLE != AUTHENTICATABLE
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 29 — ROUTING HISTORY
# ==========================================================================
#
# SEIR-I RoutingDecision contains one summarized candidate outcome per
# service.
#
#
# Future routing may require:
#
#
#     Candidate A evaluated at T1
#
#     Candidate A becomes unavailable at T2
#
#     Candidate B evaluated at T3
#
#     Candidate B selected at T4
#
#     Candidate B invocation fails at T5
#
#     Candidate C selected at T6
#
#
# Do NOT represent this by placing:
#
#
#     Candidate A
#     Candidate A
#     Candidate B
#     Candidate B
#     Candidate C
#
#
# ambiguously into RoutingDecision.candidates.
#
#
# Future temporal concepts may include:
#
#
#     RoutingAttempt
#
#     CandidateEvaluationEvent
#
#     RoutingHistory
#
#     FallbackEvent
#
#
#     SUMMARY STATE != EVENT HISTORY
#
#
#     FINAL DECISION != TEMPORAL EXECUTION TRACE
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 30 — ROUTING DECISION IDENTITY
# ==========================================================================
#
# SEIR-I does not currently define:
#
#
#     routing_decision_id
#
#
# because request_id is sufficient for the current contract.
#
#
# Future requirements may include:
#
#
#     several routing decisions for one request
#
#     retries
#
#     fallback
#
#     multi-stage workflows
#
#     nested agents
#
#     distributed tracing
#
#     historical replay
#
#
# At that point:
#
#
#     decision_id
#
# may become meaningful.
#
#
# Add it when:
#
#
#     ONE REQUEST
#         CAN HAVE
#     MULTIPLE DISTINCT ROUTING DECISIONS
#
#
# Do not add identity merely because UUIDs are fashionable.
#
#
#     IDENTITY SHOULD REPRESENT SOMETHING
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 31 — MODEL VERSIONING
# ==========================================================================
#
# Future AIModel identity may need to distinguish:
#
#
#     logical model family
#
#     model version
#
#     fine-tune version
#
#     quantization
#
#     checkpoint
#
#     deployment revision
#
#
# Routing and provenance may eventually need to know exactly which
# model artifact handled a request.
#
#
# But:
#
#
#     MODEL VERSION
#         !=
#     SERVICE IDENTITY
#
#
#     SERVICE REVISION
#         !=
#     MODEL REVISION
#
#
# Preserve these concepts independently.
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 32 — REPRODUCIBILITY
# ==========================================================================
#
# Future regulated or high-assurance AI environments may ask:
#
#
#     "Why did Agent 11 route this request to this service
#      on this date?"
#
#
# Answering that may require:
#
#
#     request version
#
#     policy version
#
#     model version
#
#     service/deployment version
#
#     capability evidence
#
#     network evidence
#
#     health evidence
#
#     routing configuration
#
#     evaluation metrics
#
#     timestamps
#
#
# That is a provenance problem.
#
#
# Do not solve reproducibility by turning RoutingDecision into a complete
# snapshot of the enterprise.
#
#
#     REPRODUCIBILITY REQUIRES PROVENANCE
#
#     PROVENANCE != GIANT ROUTING OBJECT
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 33 — DYNAMIC SERVICE DISCOVERY
# ==========================================================================
#
# SEIR-I may begin with a relatively static service registry.
#
#
# Future Agent 11 may discover reasoning services dynamically through:
#
#
#     cloud control planes
#
#     Kubernetes
#
#     service registries
#
#     inference platforms
#
#     deployment controllers
#
#     internal catalogs
#
#
# Discovery means:
#
#
#     A SERVICE WAS FOUND
#
#
# It does NOT mean:
#
#
#     THE SERVICE IS TRUSTED
#
#
#     THE SERVICE IS AUTHORIZED
#
#
#     THE SERVICE IS CAPABLE
#
#
#     THE SERVICE IS HEALTHY
#
#
# Therefore:
#
#
#     DISCOVERED != TRUSTED
#
#
#     DISCOVERED != PERMITTED
#
#
# Discovery creates a potential candidate.
#
# Agent 11 still evaluates it.
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 34 — MODEL / SERVICE REGISTRY TRUST
# ==========================================================================
#
# Future service registries may contain:
#
#
#     stale entries
#
#     experimental services
#
#     unauthorized deployments
#
#     deprecated models
#
#     duplicated services
#
#     misconfigured metadata
#
#
# Therefore:
#
#
#     REGISTERED != APPROVED
#
#
# A registry answers:
#
#
#     WHAT DOES THE PLATFORM KNOW ABOUT?
#
#
# Governance / policy answer:
#
#
#     WHAT MAY BE USED?
#
#
# Routing answers:
#
#
#     WHICH ELIGIBLE RESOURCE SHOULD BE USED NOW?
#
#
# Preserve those responsibilities.
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 35 — OBSERVABILITY SHOULD EXPLAIN ROUTING
# ==========================================================================
#
# Future Langfuse or other observability integration may capture:
#
#
#     request
#
#     candidate evaluations
#
#     final decision
#
#     inference call
#
#     token usage
#
#     latency
#
#     cost
#
#     response
#
#     evaluation result
#
#
# But observability should consume Agent 11 semantics.
#
#
# Agent 11 should not redefine its domain model around whichever
# observability product happens to be installed.
#
#
#     OBSERVABILITY TOOL != DOMAIN CONTRACT
#
#
#     TELEMETRY ADAPTER != ROUTING MODEL
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 36 — POLICY MUST REMAIN EXPLICIT UNDER PRESSURE
# ==========================================================================
#
# Future production incidents will create pressure:
#
#
#     "The preferred model is down."
#
#
#     "The customer is waiting."
#
#
#     "The external service is available."
#
#
#     "Just route it there temporarily."
#
#
# Agent 11 must not interpret urgency as authorization.
#
#
# If the organization wants emergency routing:
#
#
#     define emergency policy.
#
#
# Then Agent 11 can evaluate that policy.
#
#
# Never:
#
#
#     if outage:
#         ignore_policy()
#
#
# That is how:
#
#
#     AVAILABILITY ENGINEERING
#
# becomes:
#
#     DATA EXFILTRATION ENGINEERING
#
#
#     URGENCY != AUTHORIZATION
#
#
#     OUTAGE != POLICY BYPASS
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 37 — SAFE AGENTIC EXECUTION
# ==========================================================================
#
# Routing becomes more consequential when AI output can trigger actions.
#
#
# Unsafe architecture:
#
#
#     AI CAPABILITY
#          +
#     UNBOUNDED AUTHORITY
#          +
#     AUTOMATED EXECUTION
#          +
#     POOR GOVERNANCE
#          =
#     JUDGMENT DAY AS CODE
#
#
# Agent 11 should participate in a safer chain:
#
#
#     REASONING
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
# and where required:
#
#
#     HUMAN APPROVAL
#
#
# Routing to an intelligent model does not grant the model operational
# authority.
#
#
#     INTELLIGENCE != AUTHORITY
#
#
#     ROUTING != EXECUTION AUTHORIZATION
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 38 — CONTROL-PLANE INTEGRATION
# ==========================================================================
#
# Future Agent 11 may integrate with:
#
#
#     cloud AI control planes
#
#     Kubernetes control planes
#
#     service meshes
#
#     identity systems
#
#     policy engines
#
#     observability platforms
#
#     network controllers
#
#     inference schedulers
#
#
# Each integration should contribute domain facts.
#
#
# Example:
#
#
#     Kubernetes
#         contributes deployment/runtime state
#
#
#     Policy Engine
#         contributes authorization
#
#
#     Network Controller
#         contributes path state
#
#
#     Inference Platform
#         contributes capacity
#
#
#     Evaluation Platform
#         contributes quality evidence
#
#
# Agent 11 coordinates these facts for AI routing.
#
#
# It should not attempt to replace every control plane.
#
#
#     COORDINATION != OWNERSHIP OF EVERYTHING
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 39 — ROUTING SCOPE
# ==========================================================================
#
# SEIR-I routing is request-oriented.
#
#
# Future routing may operate at several scopes:
#
#
#     request
#
#     session
#
#     workflow
#
#     agent
#
#     tool
#
#     multi-agent system
#
#
# Example:
#
#
#     keep one conversational session on the same model
#
#
# may be desirable for:
#
#
#     cache locality
#
#     context continuity
#
#     predictable behavior
#
#
# while another workload may route every independent request dynamically.
#
#
# Do not overload RoutingDecision with all future scope semantics.
#
#
# Future RoutingPlan / RoutingContext concepts may own them.
#
#
#     REQUEST ROUTING != WORKFLOW ROUTING
# ==========================================================================


# ==========================================================================
# SEIR-II PRINCIPLE 40 — ROUTING SHOULD REMAIN EXPLAINABLE
# ==========================================================================
#
# As optimization grows more sophisticated, resist creating a routing
# system that can only say:
#
#
#     "The algorithm selected Service C."
#
#
# Operators should eventually be able to understand:
#
#
#     why candidates were rejected
#
#     why candidates were viable
#
#     which constraints applied
#
#     which optimization criteria mattered
#
#     which evidence was used
#
#     which service was selected
#
#
# This does not require every detail inside RoutingDecision.
#
#
# It requires:
#
#
#     meaningful domain objects
#
#     typed evidence
#
#     provenance
#
#     telemetry
#
#
#     EXPLAINABLE != SIMPLE
#
#
#     COMPLEX != OPAQUE
# ==========================================================================


# ==========================================================================
# SEIR-II — POSSIBLE FUTURE DOMAIN OBJECTS
# ==========================================================================
#
# DO NOT IMPLEMENT THESE MERELY BECAUSE THEY ARE LISTED HERE.
#
#
# They are architectural placeholders for concepts that may become
# necessary.
#
#
# Possible future contracts:
#
#
#     RoutingEvaluation
#
#         typed optimization evaluation
#
#
#     CandidateEvaluation
#
#         richer evidence-backed candidate evaluation
#
#
#     RoutingPlan
#
#         coordinated multi-destination routing
#
#
#     RoutingAttempt
#
#         temporal routing attempt
#
#
#     RoutingHistory
#
#         sequence of routing events
#
#
#     Deployment
#
#         concrete runtime/deployment identity
#
#
#     DeploymentLocation
#
#         cloud / region / zone / environment
#
#
#     CapacityObservation
#
#         inference-capacity state
#
#
#     PolicyRejection
#
#         detailed policy rejection evidence
#
#
#     ModelEvaluation
#
#         task-specific quality evidence
#
#
#     CandidateEvaluationEvent
#
#         temporal candidate evaluation
#
#
# These names are NOT commitments.
#
#
# They preserve architectural concepts.
#
#
#     CONCEPTUAL TRAPDOOR != REQUIRED IMPLEMENTATION
# ==========================================================================


# ==========================================================================
# SEIR-II — DO NOT TURN AIRoute INTO A CLOUD ENUM
# ==========================================================================
#
# Future engineer:
#
#
#     "We have an Azure deployment.
#      I'll add COMPANY_AZURE_LLM."
#
#
# Stop.
#
#
# Another engineer:
#
#
#     "Now we have GCP.
#      I'll add COMPANY_GCP_LLM."
#
#
# Stop.
#
#
# Six months later:
#
#
#     COMPANY_AWS_LLM
#
#     COMPANY_AZURE_LLM
#
#     COMPANY_GCP_LLM
#
#     COMPANY_OCI_LLM
#
#     COMPANY_AZURE_EU_LLM
#
#     COMPANY_AWS_GOVCLOUD_LLM
#
#     COMPANY_GCP_TRADING_LLM
#
#
# AIRoute has now become:
#
#
#     deployment topology
#
#     + provider taxonomy
#
#     + geography
#
#     + workload taxonomy
#
#
# instead of:
#
#
#     routing domain
#
#
# Do not do this.
#
#
# Keep:
#
#
#     COMPANY_CLOUD_LLM
#
#
# and model deployment facts separately.
#
#
#     ROUTING DOMAIN SHOULD REMAIN A ROUTING DOMAIN
# ==========================================================================


# ==========================================================================
# SEIR-II — DO NOT TURN RoutingCandidate INTO A DATABASE
# ==========================================================================
#
# Future engineer:
#
#
#     "Routing needs latency."
#
#
# Good.
#
#
# That does not automatically mean:
#
#
#     RoutingCandidate.latency_ms
#
#
# Future engineer:
#
#
#     "Routing needs GPU utilization."
#
#
# Good.
#
#
# That does not automatically mean:
#
#
#     RoutingCandidate.gpu_utilization
#
#
# Future engineer:
#
#
#     "Routing needs BGP state."
#
#
# Good.
#
#
# That does not automatically mean:
#
#
#     RoutingCandidate.bgp_prefix
#
#
# Ask:
#
#
#     WHICH DOMAIN OWNS THIS FACT?
#
#
# Then let routing consume or reference it.
#
#
#     INPUT TO ROUTING
#         !=
#     PROPERTY OF ROUTING CANDIDATE
# ==========================================================================


# ==========================================================================
# SEIR-II — DO NOT TURN RoutingDecision INTO AN EXECUTION ENGINE
# ==========================================================================
#
# Future engineer:
#
#
#     decision.execute()
#
#
# No.
#
#
# RoutingDecision describes:
#
#
#     WHAT WAS DECIDED
#
#
# An orchestrator performs:
#
#
#     WHAT HAPPENS NEXT
#
#
# Keeping those separate enables:
#
#
#     testing
#
#     replay
#
#     audit
#
#     dry runs
#
#     simulation
#
#     policy review
#
#     deterministic validation
#
#
#     DECISION != EXECUTION
#
#
# A noun does not need to become a verb merely because Python allows
# methods.
# ==========================================================================


# ==========================================================================
# SEIR-II — DO NOT LET FRAMEWORKS LEAK INTO DOMAIN CONTRACTS
# ==========================================================================
#
# Avoid future fields such as:
#
#
#     langgraph_node_id
#
#     crewai_agent_name
#
#     agentcore_runtime_id
#
#
# inside generic Agent 11 routing contracts unless the domain itself
# truly requires them.
#
#
# Framework-specific adapters may own those identifiers.
#
#
# Otherwise:
#
#
#     framework migration
#
# becomes:
#
#     domain-model migration
#
#
# unnecessarily.
#
#
#     FRAMEWORK METADATA != ROUTING SEMANTICS
# ==========================================================================


# ==========================================================================
# SEIR-II — ROUTING MATURITY MODEL
# ==========================================================================
#
# A possible evolution:
#
#
#     LEVEL 1
#
#         policy-aware destination routing
#
#
#     LEVEL 2
#
#         policy + capability + availability + network routing
#
#
#     LEVEL 3
#
#         capacity / latency / cost-aware optimization
#
#
#     LEVEL 4
#
#         quality-aware and failure-domain-aware routing
#
#
#     LEVEL 5
#
#         multi-cloud, multi-model, provenance-aware routing
#
#
#     LEVEL 6
#
#         adaptive agentic AI control-plane routing
#
#
# The maturity increases.
#
#
# The original invariants should remain.
#
#
#     MORE INTELLIGENCE
#         SHOULD NOT MEAN
#     LESS ARCHITECTURAL DISCIPLINE
# ==========================================================================


# ==========================================================================
# SEIR-II — THE MULTI-CLOUD TEST
# ==========================================================================
#
# When evaluating a future change, ask:
#
#
#     WOULD THIS DESIGN STILL MAKE SENSE IF:
#
#
#         Agent 11 runs in AWS,
#
#         the selected proprietary model runs in GCP,
#
#         telemetry runs in Azure,
#
#         identity comes from Entra ID,
#
#         another approved model runs in OCI,
#
#         the sensitive fallback model runs on-premises,
#
#         and BGP / SD-WAN determine current reachability?
#
#
# If the answer is:
#
#
#     "No, because COMPANY_CLOUD_LLM secretly means AWS,"
#
#
# then the abstraction has failed.
#
#
# If the answer is:
#
#
#     "Yes. Routing domain, deployment provider, identity,
#      telemetry, network path, and model identity remain separate,"
#
#
# then the architecture is surviving.
# ==========================================================================


# ==========================================================================
# SEIR-II — THE POLICY TEST
# ==========================================================================
#
# Ask:
#
#
#     CAN ANY OPTIMIZATION FEATURE CAUSE A POLICY-DENIED CANDIDATE
#     TO BECOME SELECTABLE?
#
#
# If:
#
#
#     YES
#
#
# the routing architecture is broken.
#
#
# Cost cannot do it.
#
# Latency cannot do it.
#
# Quality cannot do it.
#
# Capacity cannot do it.
#
# Provider preference cannot do it.
#
# Network performance cannot do it.
#
#
# Only a legitimate policy decision can establish authorization.
#
#
#     OPTIMIZATION NEVER CREATES AUTHORIZATION
# ==========================================================================


# ==========================================================================
# SEIR-II — THE UNKNOWN TEST
# ==========================================================================
#
# Ask:
#
#
#     DOES CONSERVATIVE ROUTING CHANGE UNKNOWN OBSERVATIONS
#     INTO FALSE FACTS?
#
#
# Example:
#
#
#     NetworkPathState.UNKNOWN
#
#
# Conservative decision:
#
#
#     do not use route
#
#
# Incorrect mutation:
#
#
#     NetworkPathState.UNAVAILABLE
#
#
# Do not rewrite reality merely because the action is conservative.
#
#
#     UNKNOWN REMAINS UNKNOWN
#
#
#     DECISION != OBSERVATION
# ==========================================================================


# ==========================================================================
# SEIR-II — THE FALLBACK TEST
# ==========================================================================
#
# Ask:
#
#
#     DOES FALLBACK RE-EVALUATE THE SAME REQUIRED CONSTRAINTS?
#
#
# If:
#
#
#     YES
#
# good.
#
#
# If fallback means:
#
#
#     "Primary failed, so use whatever still responds."
#
#
# stop.
#
#
#     FALLBACK RE-EVALUATES VIABILITY
#
#
#     FALLBACK DOES NOT RELAX POLICY
#
#
#     FALLBACK DOES NOT SILENTLY REDUCE CAPABILITY REQUIREMENTS
# ==========================================================================


# ==========================================================================
# SEIR-II — THE OWNERSHIP TEST
# ==========================================================================
#
# Before adding a field to routing.py, ask:
#
#
#     WHICH DOMAIN OWNS THIS FACT?
#
#
# Examples:
#
#
#     model capability
#         -> model / capability domain
#
#
#     authorization
#         -> policy domain
#
#
#     service health
#         -> runtime / health domain
#
#
#     network reachability
#         -> network domain
#
#
#     cloud region
#         -> deployment domain
#
#
#     GPU utilization
#         -> inference runtime / telemetry domain
#
#
#     final candidate outcome
#         -> routing domain
#
#
#     selected service
#         -> routing domain
#
#
# This question will prevent a large percentage of future architectural
# mistakes.
#
#
#     WHICH THING OWNS WHICH FACT?
# ==========================================================================


# ==========================================================================
# SEIR-II — THE JUDGMENT DAY AS CODE TEST
# ==========================================================================
#
# Before increasing agent autonomy, ask:
#
#
#     DOES THIS CHANGE COMBINE:
#
#
#         AI CAPABILITY
#
#         UNBOUNDED AUTHORITY
#
#         AUTOMATED EXECUTION
#
#         POOR GOVERNANCE
#
#
# If yes:
#
#
#     STOP.
#
#
# The target architecture is:
#
#
#     reasoning
#
#         |
#         v
#
#     policy
#
#         |
#         v
#
#     scoped authority
#
#         |
#         v
#
#     approved execution
#
#         |
#         v
#
#     telemetry / provenance
#
#
# Agent 11 should make intelligent systems more governable,
# not merely more autonomous.
# ==========================================================================


# ==========================================================================
# CHEWBACCA READS THE LETTER FROM 2026
# ==========================================================================
#
# Future Chewbacca:
#
#     "We added GCP."
#
#
# Agent 11:
#
#     GOOD.
#
#
# Chewbacca:
#
#     "I created COMPANY_GCP_LLM."
#
#
# Agent 11:
#
#     DELETE IT.
#
#
# Chewbacca:
#
#     "But the model is in GCP."
#
#
# Agent 11:
#
#     DEPLOYMENT PROVIDER != ROUTING DOMAIN.
#
#
# Chewbacca:
#
#     "Fine. COMPANY_CLOUD_LLM.
#      I also gave it a score of 0.98."
#
#
# Agent 11:
#
#     0.98 WHAT?
#
#
# Chewbacca:
#
#     "Everything."
#
#
# Agent 11:
#
#     THAT IS NOT A UNIT.
#
#
# Chewbacca:
#
#     "It is cheaper and faster than on-prem."
#
#
# Agent 11:
#
#     POLICY?
#
#
# Chewbacca:
#
#     "Denied for this request."
#
#
# Agent 11:
#
#     THEN IT IS NOT A CANDIDATE FOR OPTIMIZATION.
#
#
# Chewbacca:
#
#     "But 0.98."
#
#
# Agent 11:
#
#     POLICY NEVER BECOMES A SCORE.
#
#
# Chewbacca:
#
#     "What if I call it fallback?"
#
#
# Agent 11:
#
#     FALLBACK DOES NOT ESCAPE POLICY.
#
#
# Chewbacca:
#
#     "What if I put all the policy, GPU, BGP,
#      cloud, telemetry, cost, and deployment fields
#      into RoutingCandidate?"
#
#
# Agent 11:
#
#     EnterpriseBlobObject.py.
#
#
# Chewbacca:
#
#     "Ah."
#
#
# Agent 11:
#
#     READ THE LETTER FROM 2026 AGAIN.
# ==========================================================================


# ==========================================================================
# PART IV — SEIR-II FINAL EXPANSION INVARIANTS
# ==========================================================================
#
#     CONSTRAINTS FIRST
#
#     OPTIMIZATION SECOND
#
#
#     POLICY NEVER BECOMES A SCORE
#
#
#     OPTIMIZATION NEVER CREATES AUTHORIZATION
#
#
#     HIGHEST SCORE != POLICY OVERRIDE
#
#
#     TYPED CRITERIA > OPAQUE NUMBER
#
#
#     SCORE != VIABILITY
#
#
#     CAPACITY != SIMPLE BOOLEAN
#
#
#     ROUTING != INFERENCE TELEMETRY DATABASE
#
#
#     AI ROUTING != NETWORK ROUTING
#
#
#     BGP REACHABILITY != AI AUTHORIZATION
#
#
#     SD-WAN PREFERENCE != AI POLICY
#
#
#     MULTIPLE SERVICES != TRUE REDUNDANCY
#
#
#     ROUTING DOMAIN != CLOUD PROVIDER
#
#
#     ROUTING DOMAIN != DEPLOYMENT LOCATION
#
#
#     ROUTING DOMAIN != MODEL PROVIDER
#
#
#     MODEL PROVIDER != DEPLOYMENT PROVIDER
#
#
#     MODEL IDENTITY != DEPLOYMENT IDENTITY
#
#
#     MODEL != SERVICE != DEPLOYMENT != ROUTING DECISION
#
#
#     ROUTING DOMAIN != COMPLETE POLICY DECISION
#
#
#     CHEAP != PERMITTED
#
#
#     MODEL PRICE != TOTAL ROUTE COST
#
#
#     COST OPTIMIZATION != AUTHORIZATION
#
#
#     MODEL QUALITY IS TASK-RELATIVE
#
#
#     QUALITY != UNIVERSAL SCALAR TRUTH
#
#
#     SCORE WITHOUT CONTEXT != TRUSTWORTHY EVIDENCE
#
#
#     REJECTION REASON != REJECTION EVIDENCE
#
#
#     PROVENANCE SHOULD LINK EVIDENCE
#
#
#     PROVENANCE SHOULD NOT CREATE EnterpriseBlobObject.py
#
#
#     OLD OBSERVATION != CURRENT TRUTH
#
#
#     STALE OBSERVATION != CURRENT TRUTH
#
#
#     OBSERVATION != EVIDENCE SUFFICIENCY
#
#
#     UNKNOWN REMAINS UNKNOWN
#
#
#     OBSERVED STATE != DECISION RULE
#
#
#     TECHNICAL CAPABILITY != GOVERNANCE APPROVAL
#
#
#     MULTI-MODEL EXECUTION != FALLBACK
#
#
#     FAN-OUT != FALLBACK
#
#
#     CONSENSUS != RETRY
#
#
#     ROUTING DECISION = ATOMIC DECISION
#
#
#     ROUTING PLAN = COORDINATED DECISIONS
#
#
#     AGENT REQUESTS CAPABILITY
#
#     AGENT DOES NOT NECESSARILY CHOOSE PROVIDER
#
#
#     REQUEST != AUTHORIZATION
#
#
#     AGENT INTENT != POLICY DECISION
#
#
#     FRAMEWORKS CHANGE
#
#     DOMAIN CONTRACTS SHOULD SURVIVE THEM
#
#
#     CONTROL PLANE != INFERENCE PLANE
#
#
#     AUTHORIZATION != CONNECTIVITY
#
#
#     CONNECTIVITY != AUTHORIZATION
#
#
#     IDENTITY STATE != NETWORK STATE
#
#
#     NETWORK REACHABLE != AUTHENTICATABLE
#
#
#     SUMMARY STATE != EVENT HISTORY
#
#
#     FINAL DECISION != TEMPORAL EXECUTION TRACE
#
#
#     IDENTITY SHOULD REPRESENT SOMETHING
#
#
#     MODEL VERSION != SERVICE IDENTITY
#
#
#     SERVICE REVISION != MODEL REVISION
#
#
#     REPRODUCIBILITY REQUIRES PROVENANCE
#
#
#     DISCOVERED != TRUSTED
#
#
#     DISCOVERED != PERMITTED
#
#
#     REGISTERED != APPROVED
#
#
#     OBSERVABILITY TOOL != DOMAIN CONTRACT
#
#
#     TELEMETRY ADAPTER != ROUTING MODEL
#
#
#     URGENCY != AUTHORIZATION
#
#
#     OUTAGE != POLICY BYPASS
#
#
#     INTELLIGENCE != AUTHORITY
#
#
#     ROUTING != EXECUTION AUTHORIZATION
#
#
#     COORDINATION != OWNERSHIP OF EVERYTHING
#
#
#     REQUEST ROUTING != WORKFLOW ROUTING
#
#
#     EXPLAINABLE != SIMPLE
#
#
#     COMPLEX != OPAQUE
#
#
#     CONCEPTUAL TRAPDOOR != REQUIRED IMPLEMENTATION
#
#
#     ROUTING DOMAIN SHOULD REMAIN A ROUTING DOMAIN
#
#
#     INPUT TO ROUTING != PROPERTY OF RoutingCandidate
#
#
#     DECISION != EXECUTION
#
#
#     FRAMEWORK METADATA != ROUTING SEMANTICS
#
#
#     MORE INTELLIGENCE
#         SHOULD NOT MEAN
#     LESS ARCHITECTURAL DISCIPLINE
#
#
#     FALLBACK RE-EVALUATES VIABILITY
#
#
#     FALLBACK DOES NOT RELAX POLICY
#
#
#     FALLBACK DOES NOT SILENTLY REDUCE REQUIREMENTS
#
#
#     WHICH THING OWNS WHICH FACT?
#
#
#     TOOLS CHANGE.
#
#     FOUNDATIONS DON'T.
#
# ==========================================================================
# END PART IV
# ==========================================================================
