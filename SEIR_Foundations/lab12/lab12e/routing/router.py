"""
Agent 11 primary AI router.

This module contains the final selection behavior for initial AI routing.

The router receives routing candidates that have already been evaluated by
the appropriate Agent 11 subsystems and selects the first viable candidate
according to caller-provided preference order.

Core routing principle:

    VIABLE ROUTE
        =
    POLICY PERMITTED
        +
    SERVICE CAPABLE
        +
    SERVICE AVAILABLE
        +
    PATH AVAILABLE

The router does not determine those underlying facts.

It consumes the resulting RoutingCandidate contracts and produces a
RoutingDecision.

SEIR-I routing strategy:

    1. Candidates arrive in preference order.

    2. Select the first viable candidate.

    3. If no candidate is viable and every evaluated candidate was rejected
       by policy, return BLOCKED.

    4. Otherwise return NO_VIABLE_ROUTE.

Important invariants:

    ORDER = PREFERENCE

    PREFERENCE != VIABILITY

    PREFERENCE NEVER CREATES VIABILITY

    POLICY NEVER BECOMES A SCORE

    REACHABLE != AUTHORIZED

    AUTHORIZED != REACHABLE

    CAPABLE != AUTHORIZED

    HEALTHY != PERMITTED

    FALLBACK != POLICY ESCAPE

    NO CANDIDATES != NULL

    UNKNOWN != POLICY_DENIED

The implementation is intentionally small.

Routing complexity should remain distributed among the components that own
policy, capability, service availability, network state, and future routing
optimization rather than being concentrated inside one God Router.
"""

from uuid import UUID

from ..models.ai.routing import RoutingCandidate, RoutingDecision
from ..models.enums.routing_enums import (
    RoutingCandidateStatus,
    RoutingRejectionReason,
    RoutingStatus,
)


# ============================================================================
# AIRouter
# ============================================================================
#
# AIRouter performs final selection among already-evaluated routing
# candidates.
#
#
# INPUT
# -----
#
#       request_id
#
#       ordered list[RoutingCandidate]
#
#
# OUTPUT
# ------
#
#       RoutingDecision
#
#
# Conceptually:
#
#
#       POLICY
#          |
#          +-------------------+
#                              |
#       CAPABILITY             |
#          |                   |
#          +-------------------+
#                              |
#       SERVICE STATE          |
#          |                   |
#          +-------------------+----> RoutingCandidate[]
#                              |              |
#       NETWORK STATE          |              v
#          |                   |           AIRouter
#          +-------------------+              |
#                                             v
#                                      RoutingDecision
#
#
# AIRouter does NOT produce the underlying policy, capability, service,
# or network facts.
#
# It consumes their already-evaluated routing result.
#
#
#       ROUTER CONSUMES EVALUATED CANDIDATES
#
#       ROUTER DOES NOT RE-EVALUATE CANDIDATES
#
#
# ============================================================================


class AIRouter:
    """
    Selects the initial AI route from evaluated routing candidates.

    Candidates must be supplied in preference order.

    The router selects the first candidate whose status is VIABLE.

    If no viable candidate exists:

        * BLOCKED is returned when every candidate was rejected because
          policy denied it.

        * NO_VIABLE_ROUTE is returned for all other cases, including an
          empty candidate list.

    AIRouter does not perform policy evaluation, capability matching,
    service-health evaluation, network-path evaluation, AI invocation,
    or runtime fallback.
    """

    def select_route(
        self,
        request_id: UUID,
        candidates: list[RoutingCandidate],
    ) -> RoutingDecision:
        """
        Select the first viable routing candidate.

        Candidate ordering represents routing preference.

        Viability has already been established before candidates reach
        this method.

        Args:
            request_id:
                Identifier of the AI request being routed.

            candidates:
                Evaluated routing candidates in preference order.

        Returns:
            RoutingDecision describing the routing outcome.

        Routing outcomes:

            SELECTED
                At least one viable candidate exists. The first viable
                candidate is selected.

            BLOCKED
                Candidates exist, none are viable, and every candidate
                was rejected because policy denied it.

            NO_VIABLE_ROUTE
                No viable candidate exists for any other reason,
                including when no candidates were supplied.

        This method does not produce RoutingStatus.NULL.

        NULL represents an intentional decision that AI routing is not
        required and therefore belongs to the broader AI orchestration
        layer rather than normal route selection.
        """

        # ====================================================================
        # STEP 1 — SELECT THE FIRST VIABLE CANDIDATE
        # ====================================================================
        #
        # Candidate order represents preference.
        #
        # Example:
        #
        #
        #       [
        #           preferred_candidate,
        #           second_choice,
        #           third_choice,
        #       ]
        #
        #
        # The first VIABLE candidate wins.
        #
        # Notice what we do NOT do here:
        #
        #
        #       calculate policy
        #
        #       check service health
        #
        #       inspect network paths
        #
        #       compare model capabilities
        #
        #       calculate weighted scores
        #
        #       modify candidate status
        #
        #
        # Those facts were already evaluated before RoutingCandidate
        # reached AIRouter.
        #
        #
        #       ORDER = PREFERENCE
        #
        #       STATUS = VIABILITY RESULT
        #
        #
        # Preference can choose between viable candidates.
        #
        # Preference cannot make a rejected candidate viable.
        #
        #
        #       PREFERENCE NEVER CREATES VIABILITY
        #
        # ====================================================================

        for candidate in candidates:
            if candidate.status is RoutingCandidateStatus.VIABLE:
                return RoutingDecision(
                    request_id=request_id,
                    status=RoutingStatus.SELECTED,
                    selected_service_id=candidate.service_id,
                    selected_routing_domain=candidate.routing_domain,
                    candidates=candidates,
                    reason=(
                        "Selected the first viable routing candidate "
                        "according to candidate preference order."
                    ),
                )

        # ====================================================================
        # STEP 2 — DETERMINE WHETHER POLICY BLOCKED EVERY CANDIDATE
        # ====================================================================
        #
        # If execution reaches this point:
        #
        #
        #       NO CANDIDATE WAS VIABLE
        #
        #
        # But there are different reasons why that may be true.
        #
        #
        # Example A:
        #
        #
        #       EXTERNAL_FM
        #           REJECTED: POLICY_DENIED
        #
        #       COMPANY_CLOUD_LLM
        #           REJECTED: POLICY_DENIED
        #
        #       COMPANY_ONPREM_LLM
        #           REJECTED: POLICY_DENIED
        #
        #
        # In this case policy categorically eliminated every routing
        # candidate.
        #
        # The aggregate routing outcome is:
        #
        #
        #       BLOCKED
        #
        #
        # Example B:
        #
        #
        #       EXTERNAL_FM
        #           REJECTED: POLICY_DENIED
        #
        #       COMPANY_CLOUD_LLM
        #           REJECTED: SERVICE_UNAVAILABLE
        #
        #       COMPANY_ONPREM_LLM
        #           REJECTED: NETWORK_UNAVAILABLE
        #
        #
        # Here policy did NOT categorically eliminate routing.
        #
        # Some otherwise relevant candidates failed for operational
        # reasons.
        #
        # The aggregate routing outcome is:
        #
        #
        #       NO_VIABLE_ROUTE
        #
        #
        # Therefore BLOCKED requires:
        #
        #
        #       candidates exist
        #
        #           AND
        #
        #       every candidate was rejected
        #
        #           AND
        #
        #       every rejection reason is POLICY_DENIED
        #
        #
        # ====================================================================

        all_candidates_policy_denied = bool(candidates) and all(
            candidate.status is RoutingCandidateStatus.REJECTED
            and candidate.rejection_reason
            is RoutingRejectionReason.POLICY_DENIED
            for candidate in candidates
        )

        if all_candidates_policy_denied:
            return RoutingDecision(
                request_id=request_id,
                status=RoutingStatus.BLOCKED,
                candidates=candidates,
                reason=(
                    "All evaluated routing candidates were denied "
                    "by policy."
                ),
            )

        # ====================================================================
        # STEP 3 — NO VIABLE ROUTE
        # ====================================================================
        #
        # If:
        #
        #
        #       no viable candidate exists
        #
        # and:
        #
        #       policy did not categorically deny every candidate
        #
        #
        # then the routing result is:
        #
        #
        #       NO_VIABLE_ROUTE
        #
        #
        # Possible causes include:
        #
        #
        #       CAPABILITY_MISMATCH
        #
        #       SERVICE_UNAVAILABLE
        #
        #       NETWORK_UNAVAILABLE
        #
        #       UNKNOWN
        #
        #       mixed rejection reasons
        #
        #       no candidates
        #
        #
        # AIRouter does not need to collapse those facts into one invented
        # explanation.
        #
        # The RoutingCandidate records preserve the individual rejection
        # reasons.
        #
        #
        #       AGGREGATE OUTCOME
        #           =
        #       NO_VIABLE_ROUTE
        #
        #
        # while:
        #
        #
        #       CANDIDATE RECORDS
        #           =
        #       WHY EACH CANDIDATE FAILED
        #
        #
        # ====================================================================

        return RoutingDecision(
            request_id=request_id,
            status=RoutingStatus.NO_VIABLE_ROUTE,
            candidates=candidates,
            reason="No viable routing candidate was available.",
        )


# ============================================================================
# ROUTING ALGORITHM SUMMARY
# ============================================================================
#
# The executable routing algorithm is intentionally simple:
#
#
#       FOR EACH CANDIDATE IN PREFERENCE ORDER:
#
#           IF VIABLE:
#
#               SELECT IT
#
#
#       IF EVERY CANDIDATE WAS POLICY DENIED:
#
#           BLOCKED
#
#
#       OTHERWISE:
#
#           NO_VIABLE_ROUTE
#
#
# This simplicity is possible because other Agent 11 components establish
# the facts before AIRouter receives the candidates.
#
#
#       COMPLEX DOMAIN
#           !=
#       COMPLEX FINAL SELECTOR
#
#
# ============================================================================


# ============================================================================
# WHY CANDIDATES ARE ORDERED
# ============================================================================
#
# SEIR-I does not require a generalized optimization engine.
#
# Instead:
#
#
#       list position
#           =
#       preference
#
#
# Example:
#
#
#       candidates = [
#           candidate_a,
#           candidate_b,
#           candidate_c,
#       ]
#
#
# means:
#
#
#       prefer A
#
#       otherwise B
#
#       otherwise C
#
#
# but only when each candidate is independently viable.
#
#
# If:
#
#
#       A = REJECTED
#       B = VIABLE
#       C = VIABLE
#
#
# then:
#
#
#       B
#
#
# is selected.
#
#
# The router does not ask whether A was "almost viable."
#
#
#       REJECTED != LOW SCORE
#
#
# ============================================================================


# ============================================================================
# HARD CONSTRAINTS BEFORE OPTIMIZATION
# ============================================================================
#
# Future routing may eventually optimize:
#
#
#       cost
#
#       latency
#
#       model quality
#
#       token efficiency
#
#       GPU capacity
#
#       queue depth
#
#       geographic proximity
#
#       failure domains
#
#
# But optimization must occur only among viable candidates.
#
#
#       ALL CANDIDATES
#            |
#            v
#       HARD CONSTRAINTS
#            |
#            v
#       VIABLE SET
#            |
#            v
#       PREFERENCE / OPTIMIZATION
#            |
#            v
#       SELECTED ROUTE
#
#
# Never:
#
#
#       score everything
#           |
#           v
#       choose highest score
#           |
#           v
#       discover afterward that policy prohibited it
#
#
# Therefore:
#
#
#       FILTER BY CONSTRAINTS FIRST
#
#       OPTIMIZE SECOND
#
#
# ============================================================================


# ============================================================================
# POLICY NEVER BECOMES A SCORE
# ============================================================================
#
# Future engineers may be tempted to create:
#
#
#       score = 0
#
#       score += latency_score
#       score += cost_score
#       score += capability_score
#       score += policy_score
#
#
# Do not do this.
#
# Policy is not a preference.
#
#
#       POLICY PERMITTED
#
#
# is a hard eligibility requirement.
#
#
#       POLICY DENIED
#
#
# means the candidate is not in the viable set.
#
#
# No amount of:
#
#
#       low cost
#
#       low latency
#
#       high quality
#
#       available GPU capacity
#
#
# may compensate for policy denial.
#
#
#       POLICY NEVER BECOMES A SCORE
#
#
# ============================================================================


# ============================================================================
# BLOCKED != NO_VIABLE_ROUTE
# ============================================================================
#
# These outcomes intentionally remain distinct.
#
#
# BLOCKED:
#
#
#       policy eliminated every evaluated candidate
#
#
# NO_VIABLE_ROUTE:
#
#
#       no candidate is currently viable for some other or mixed reason
#
#
# Examples:
#
#
#       [POLICY_DENIED, POLICY_DENIED]
#
#           ->
#
#       BLOCKED
#
#
#       [POLICY_DENIED, SERVICE_UNAVAILABLE]
#
#           ->
#
#       NO_VIABLE_ROUTE
#
#
#       [NETWORK_UNAVAILABLE, SERVICE_UNAVAILABLE]
#
#           ->
#
#       NO_VIABLE_ROUTE
#
#
#       [CAPABILITY_MISMATCH]
#
#           ->
#
#       NO_VIABLE_ROUTE
#
#
#       [UNKNOWN]
#
#           ->
#
#       NO_VIABLE_ROUTE
#
#
# This distinction improves:
#
#
#       auditability
#
#       troubleshooting
#
#       telemetry
#
#       security reasoning
#
#
# ============================================================================


# ============================================================================
# UNKNOWN != POLICY_DENIED
# ============================================================================
#
# RoutingRejectionReason.UNKNOWN represents unresolved or insufficient
# routing-level evidence.
#
# It must not be silently converted into:
#
#
#       POLICY_DENIED
#
#
# merely because Agent 11 should fail closed.
#
#
# Example:
#
#
#       Candidate A
#           UNKNOWN
#
#       Candidate B
#           POLICY_DENIED
#
#
# Result:
#
#
#       NO_VIABLE_ROUTE
#
#
# not:
#
#
#       BLOCKED
#
#
# Agent 11 may behave conservatively without falsifying the reason.
#
#
#       FAIL CLOSED
#           !=
#       FALSIFY STATE
#
#
# ============================================================================


# ============================================================================
# EMPTY CANDIDATE LIST
# ============================================================================
#
# An empty candidate list is valid input.
#
#
#       candidates = []
#
#
# means:
#
#
#       routing was requested
#
#       but no routing candidates were available for selection
#
#
# Therefore:
#
#
#       []
#
#           ->
#
#       NO_VIABLE_ROUTE
#
#
# It does NOT mean:
#
#
#       NULL
#
#
# because NULL has different semantics.
#
#
#       NO CANDIDATES != NULL
#
#
# ============================================================================


# ============================================================================
# WHY AIRouter DOES NOT PRODUCE NULL
# ============================================================================
#
# RoutingStatus.NULL means:
#
#
#       AI ROUTING IS INTENTIONALLY UNNECESSARY
#
#
# If AI routing is unnecessary, there is nothing for AIRouter to select.
#
# That determination belongs to the broader AI behavior layer.
#
#
# Conceptually:
#
#
#       AI ORCHESTRATOR
#             |
#             +---------------------------+
#             |                           |
#             v                           v
#       AI REQUIRED                  AI NOT REQUIRED
#             |                           |
#             v                           v
#         AIRouter                 RoutingStatus.NULL
#
#
# Therefore:
#
#
#       NULL
#           =
#       ROUTING BYPASS OUTCOME
#
#
# not:
#
#
#       NULL
#           =
#       ROUTER FAILED TO FIND A CANDIDATE
#
#
# ============================================================================


# ============================================================================
# AIRouter DOES NOT RE-EVALUATE RoutingCandidate
# ============================================================================
#
# RoutingCandidate already represents evaluated routing state.
#
#
#       RoutingCandidateStatus.VIABLE
#
#
# means the candidate passed the routing viability evaluation performed
# before final selection.
#
#
#       RoutingCandidateStatus.REJECTED
#
#
# means it did not.
#
#
# AIRouter should never attempt to reconstruct candidate status from:
#
#
#       rejection_reason
#
#       service identifiers
#
#       routing domains
#
#       naming conventions
#
#       provider names
#
#
# For example, do NOT write:
#
#
#       if candidate.rejection_reason is None:
#           candidate.status = VIABLE
#
#
# The candidate contract already owns that relationship.
#
#
#       DOMAIN MODEL VALIDATES ITS OWN SEMANTICS
#
#       ROUTER CONSUMES THE VALIDATED RESULT
#
#
# ============================================================================


# ============================================================================
# AIRouter DOES NOT MODIFY CANDIDATES
# ============================================================================
#
# AIRouter treats RoutingCandidate objects as routing evidence.
#
# It does not mutate:
#
#
#       candidate.status
#
#       candidate.rejection_reason
#
#       candidate.routing_domain
#
#       candidate.service_id
#
#
# Selection produces a new RoutingDecision.
#
#
#       EVALUATED CANDIDATE
#            |
#            v
#       ROUTER READS
#            |
#            v
#       RoutingDecision
#
#
# not:
#
#
#       ROUTER REWRITES EVIDENCE
#
#
# ============================================================================


# ============================================================================
# ROUTER != POLICY ENGINE
# ============================================================================
#
# The policy subsystem determines whether a routing destination is
# permitted.
#
# AIRouter may observe:
#
#
#       RoutingRejectionReason.POLICY_DENIED
#
#
# It does not determine whether policy should have denied the candidate.
#
#
#       POLICY ENGINE
#            |
#            v
#       POLICY RESULT
#            |
#            v
#       CANDIDATE EVALUATION
#            |
#            v
#       RoutingCandidate
#            |
#            v
#       AIRouter
#
#
# AIRouter deriving:
#
#
#       all candidates policy denied
#           ->
#       RoutingStatus.BLOCKED
#
#
# is aggregation of existing routing evidence.
#
# It is not policy evaluation.
#
#
# ============================================================================


# ============================================================================
# ROUTER != CAPABILITY MATCHER
# ============================================================================
#
# AIRouter does not determine whether:
#
#
#       LIGHT
#
#       STANDARD
#
#       HEAVY
#
#
# reasoning can be satisfied by a model.
#
# It does not inspect AICapability collections.
#
# It does not decide whether a model supports:
#
#
#       CODE_REASONING
#
#       SECURITY_ANALYSIS
#
#       STRUCTURED_OUTPUT
#
#       TOOL_USE
#
#
# Those concerns belong to candidate evaluation / model-routing behavior.
#
#
# AIRouter sees the result:
#
#
#       VIABLE
#
# or:
#
#       CAPABILITY_MISMATCH
#
#
# ============================================================================


# ============================================================================
# ROUTER != SERVICE HEALTH MONITOR
# ============================================================================
#
# AIRouter does not:
#
#
#       ping inference endpoints
#
#       query cloud health APIs
#
#       inspect GPU processes
#
#       check Kubernetes pods
#
#       measure queue depth
#
#
# Service-health components establish service availability.
#
# Candidate evaluation converts relevant service state into routing
# viability.
#
# AIRouter consumes the result.
#
#
#       SERVICE HEALTH
#           !=
#       ROUTE SELECTION
#
#
# ============================================================================


# ============================================================================
# ROUTER != NETWORK MONITOR
# ============================================================================
#
# AIRouter does not:
#
#
#       inspect routes
#
#       inspect BGP
#
#       query SD-WAN
#
#       establish VPN state
#
#       test PrivateLink
#
#       determine Internet reachability
#
#       inspect STREET_ACCESS
#
#
# Network components establish path state.
#
# Candidate evaluation converts relevant network state into routing
# viability.
#
# AIRouter consumes the result.
#
#
#       NETWORK TRUTH
#           !=
#       ROUTING SELECTION
#
#
# ============================================================================


# ============================================================================
# ROUTER != SERVICE REGISTRY
# ============================================================================
#
# AIRouter does not determine which AI services exist.
#
# Service/deployment registries may eventually provide:
#
#
#       service identity
#
#       model identity
#
#       deployment location
#
#       cloud provider
#
#       region
#
#       endpoint
#
#       operational state
#
#
# Those systems produce information used before final selection.
#
#
#       DISCOVERED != TRUSTED
#
#       REGISTERED != AUTHORIZED
#
#       AVAILABLE != SELECTED
#
#
# ============================================================================


# ============================================================================
# ROUTER != MODEL INVOCATION
# ============================================================================
#
# A selected route means:
#
#
#       Agent 11 has chosen a viable service destination.
#
#
# It does not mean:
#
#
#       the model has already been called
#
#
# or:
#
#
#       inference succeeded
#
#
# Therefore:
#
#
#       RoutingStatus.SELECTED
#           |
#           v
#       AI INVOCATION
#           |
#           v
#       AIResponse
#
#
#       SELECTED != INVOKED
#
#       INVOKED != SUCCESSFUL
#
#
# ============================================================================


# ============================================================================
# INITIAL ROUTING != RUNTIME FALLBACK
# ============================================================================
#
# AIRouter performs initial selection.
#
#
# Example:
#
#
#       Candidate A = REJECTED
#       Candidate B = VIABLE
#       Candidate C = VIABLE
#
#
# Selecting Candidate B is not runtime fallback.
#
# Candidate A was never selected or invoked.
#
#
# Runtime fallback is different:
#
#
#       Candidate A = VIABLE
#            |
#            v
#       SELECT A
#            |
#            v
#       INVOCATION FAILS
#            |
#            v
#       SHOULD AGENT 11 TRY ANOTHER SERVICE?
#
#
# That belongs to fallback behavior.
#
#
#       router.py
#           =
#       INITIAL SELECTION
#
#
#       fallback.py
#           =
#       POST-SELECTION RECOVERY / RE-EVALUATION
#
#
# ============================================================================


# ============================================================================
# FALLBACK MUST RE-EVALUATE VIABILITY
# ============================================================================
#
# A candidate that was viable during initial routing may not remain viable.
#
#
#       T0:
#
#           Candidate B = VIABLE
#
#
#       T1:
#
#           Candidate A invocation fails
#
#
#       T2:
#
#           Candidate B may now be:
#
#               policy denied
#
#               service unavailable
#
#               network unavailable
#
#               otherwise unsuitable
#
#
# Therefore runtime fallback must not simply select the next historical
# VIABLE record without appropriate re-evaluation.
#
#
#       WAS VIABLE
#           !=
#       IS VIABLE NOW
#
#
# ============================================================================


# ============================================================================
# MULTI-CLOUD ROUTING
# ============================================================================
#
# AIRouter selects services.
#
# It does not need provider-specific selection branches.
#
#
# Avoid:
#
#
#       if provider == AWS:
#           ...
#
#       elif provider == AZURE:
#           ...
#
#       elif provider == GCP:
#           ...
#
#       elif provider == OCI:
#           ...
#
#
# A company-controlled cloud routing domain may contain services deployed
# across several providers.
#
#
#       COMPANY_CLOUD_LLM
#            |
#            +--> AWS deployment
#            |
#            +--> Azure deployment
#            |
#            +--> GCP deployment
#            |
#            +--> OCI deployment
#
#
# The selected RoutingCandidate already identifies the service and routing
# domain.
#
# Deployment/provider details belong to the appropriate service/runtime
# contracts.
#
#
#       ROUTING DOMAIN != CLOUD PROVIDER
#
#       SERVICE ID != MODEL ID
#
#       MODEL != SERVICE != DEPLOYMENT
#
#
# ============================================================================


# ============================================================================
# FUTURE OPTIMIZATION
# ============================================================================
#
# SEIR-II may eventually need richer selection behavior.
#
# Examples:
#
#
#       cost optimization
#
#       latency optimization
#
#       token efficiency
#
#       reasoning quality
#
#       capacity management
#
#       geographic affinity
#
#       failure-domain diversity
#
#       workload placement
#
#
# If that happens, preserve the fundamental ordering:
#
#
#       STEP 1
#           establish eligibility / viability
#
#
#       STEP 2
#           optimize among viable candidates
#
#
# Never:
#
#
#       optimization
#           ->
#       authorization
#
#
# Instead:
#
#
#       authorization / viability
#           ->
#       optimization
#
#
# ============================================================================


# ============================================================================
# FUTURE ROUTING STRATEGIES
# ============================================================================
#
# Operational evidence may eventually justify explicit routing strategies.
#
# Possible future concepts might include:
#
#
#       ordered preference
#
#       lowest latency
#
#       lowest cost
#
#       highest capability
#
#       capacity aware
#
#       failure-domain aware
#
#
# Those are not implemented here.
#
#
# SEIR-I uses:
#
#
#       FIRST VIABLE CANDIDATE
#
#
# because it is:
#
#
#       deterministic
#
#       explainable
#
#       testable
#
#       easy to audit
#
#       sufficient for current requirements
#
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================


# ============================================================================
# DETERMINISM
# ============================================================================
#
# Given the same:
#
#
#       request_id
#
#       ordered candidates
#
#
# AIRouter should produce the same RoutingDecision.
#
#
# It does not:
#
#
#       call external APIs
#
#       read current time
#
#       generate random values
#
#       inspect environment variables
#
#       query databases
#
#       perform network requests
#
#
# This makes the router straightforward to unit test.
#
#
#       SAME INPUT
#           ->
#       SAME ROUTING DECISION
#
#
# ============================================================================


# ============================================================================
# EXPLAINABILITY
# ============================================================================
#
# RoutingDecision preserves:
#
#
#       selected service
#
#       selected routing domain
#
#       evaluated candidates
#
#       candidate rejection reasons
#
#       aggregate routing status
#
#       human-readable reason
#
#
# This allows Agent 11 to explain:
#
#
#       WHAT WAS SELECTED?
#
#       WHICH CANDIDATES WERE CONSIDERED?
#
#       WHICH WERE REJECTED?
#
#       WHY WERE THEY REJECTED?
#
#       WAS THE REQUEST BLOCKED?
#
#       OR WAS NO VIABLE ROUTE AVAILABLE?
#
#
# The human-readable reason is explanatory.
#
# Machine behavior should continue to use typed fields.
#
#
#       HUMAN EXPLANATION != MACHINE CONTRACT
#
#
# ============================================================================


# ============================================================================
# TESTING TARGETS
# ============================================================================
#
# Unit tests for AIRouter should include at least:
#
#
# CASE 1
#
#       first candidate viable
#
#       ->
#
#       SELECTED first candidate
#
#
# CASE 2
#
#       first rejected
#       second viable
#
#       ->
#
#       SELECTED second candidate
#
#
# CASE 3
#
#       several viable candidates
#
#       ->
#
#       SELECTED first viable candidate
#
#
# CASE 4
#
#       all POLICY_DENIED
#
#       ->
#
#       BLOCKED
#
#
# CASE 5
#
#       all SERVICE_UNAVAILABLE
#
#       ->
#
#       NO_VIABLE_ROUTE
#
#
# CASE 6
#
#       all NETWORK_UNAVAILABLE
#
#       ->
#
#       NO_VIABLE_ROUTE
#
#
# CASE 7
#
#       all CAPABILITY_MISMATCH
#
#       ->
#
#       NO_VIABLE_ROUTE
#
#
# CASE 8
#
#       mixed POLICY_DENIED and SERVICE_UNAVAILABLE
#
#       ->
#
#       NO_VIABLE_ROUTE
#
#
# CASE 9
#
#       mixed POLICY_DENIED and NETWORK_UNAVAILABLE
#
#       ->
#
#       NO_VIABLE_ROUTE
#
#
# CASE 10
#
#       UNKNOWN rejection
#
#       ->
#
#       NO_VIABLE_ROUTE
#
#
# CASE 11
#
#       empty candidate list
#
#       ->
#
#       NO_VIABLE_ROUTE
#
#
# CASE 12
#
#       selected RoutingDecision contains the same candidate evidence
#
#       ->
#
#       candidate history preserved
#
#
# ============================================================================


# ============================================================================
# WHAT SHOULD NOT APPEAR IN AIRouter TESTS
# ============================================================================
#
# AIRouter unit tests should not need:
#
#
#       AWS credentials
#
#       Azure credentials
#
#       GCP credentials
#
#       OCI credentials
#
#       live LLMs
#
#       Kubernetes
#
#       VPN
#
#       BGP
#
#       SD-WAN
#
#       MCP servers
#
#       databases
#
#
# If a unit test for AIRouter requires those systems, the router has likely
# absorbed responsibilities belonging elsewhere.
#
#
# ============================================================================


# ============================================================================
# CHEWBACCA REVIEWS THE ROUTER
# ============================================================================
#
# Engineer:
#
#       "The external model is much cheaper."
#
# Chewbacca:
#
#       "Is it permitted?"
#
#
# Engineer:
#
#       "No."
#
# Chewbacca:
#
#       "Then its price is zero percent relevant."
#
#
# ---------------------------------------------------------------------------
#
# Engineer:
#
#       "The endpoint responds to ping."
#
# Chewbacca:
#
#       "Good."
#
#
# Engineer:
#
#       "So I selected it."
#
# Chewbacca:
#
#       "REACHABLE is not AUTHORIZED."
#
#
# ---------------------------------------------------------------------------
#
# Engineer:
#
#       "There were no candidates, so I returned NULL."
#
# Chewbacca:
#
#       "Was AI intentionally unnecessary?"
#
#
# Engineer:
#
#       "No. I just couldn't find anything."
#
# Chewbacca:
#
#       "Then you did not find a viable route."
#
#
# ---------------------------------------------------------------------------
#
# Engineer:
#
#       "Candidate A failed, so I used Candidate B."
#
# Chewbacca:
#
#       "Did you re-evaluate Candidate B?"
#
#
# Engineer:
#
#       "It was viable five minutes ago."
#
# Chewbacca:
#
#       "So was my dinner."
#
#
# ============================================================================


# ============================================================================
# FINAL ROUTER CONTRACT
# ============================================================================
#
# AIRouter answers one question:
#
#
#       "WHICH ALREADY-EVALUATED VIABLE CANDIDATE
#        SHOULD BE SELECTED?"
#
#
# For SEIR-I:
#
#
#       FIRST VIABLE
#           ->
#       SELECTED
#
#
#       NONE VIABLE
#       +
#       ALL POLICY_DENIED
#           ->
#       BLOCKED
#
#
#       NONE VIABLE
#       +
#       ANY OTHER CONDITION
#           ->
#       NO_VIABLE_ROUTE
#
#
#       EMPTY CANDIDATES
#           ->
#       NO_VIABLE_ROUTE
#
#
#       NULL
#           ->
#       NOT PRODUCED BY AIRouter
#
#
# Permanent invariants:
#
#
#       ORDER = PREFERENCE
#
#       PREFERENCE != VIABILITY
#
#       PREFERENCE NEVER CREATES VIABILITY
#
#
#       ROUTER CONSUMES EVALUATED CANDIDATES
#
#       ROUTER DOES NOT RE-EVALUATE CANDIDATES
#
#
#       ROUTER READS EVIDENCE
#
#       ROUTER DOES NOT REWRITE EVIDENCE
#
#
#       FILTER BY CONSTRAINTS FIRST
#
#       OPTIMIZE SECOND
#
#
#       POLICY NEVER BECOMES A SCORE
#
#
#       REJECTED != LOW SCORE
#
#
#       BLOCKED != NO_VIABLE_ROUTE
#
#       NO CANDIDATES != NULL
#
#       UNKNOWN != POLICY_DENIED
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
#       REACHABLE != AUTHORIZED
#
#       AUTHORIZED != REACHABLE
#
#       CAPABLE != AUTHORIZED
#
#       HEALTHY != PERMITTED
#
#
#       SELECTED != INVOKED
#
#       INVOKED != SUCCESSFUL
#
#
#       INITIAL ROUTING != RUNTIME FALLBACK
#
#       WAS VIABLE != IS VIABLE NOW
#
#
#       FALLBACK != POLICY ESCAPE
#
#       FALLBACK != REQUIREMENT REDUCTION
#
#
#       ROUTING DOMAIN != CLOUD PROVIDER
#
#       MODEL != SERVICE != DEPLOYMENT
#
#
#       SAME INPUT -> SAME ROUTING DECISION
#
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================
# END router.py
# ============================================================================
