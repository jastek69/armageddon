# ============================================================================
# routing/candidate_evaluator.py
#
# PART I
#
# CORE ROUTING CANDIDATE VIABILITY
# ============================================================================
#
# PURPOSE
# -------
#
# CandidateEvaluator answers one narrow question:
#
#
#       "Given the established facts for ONE possible AI service,
#        is that service currently a viable routing candidate?"
#
#
# CandidateEvaluator is where several independently established domain facts
# meet:
#
#
#       POLICY
#           |
#           v
#       CAPABILITY
#           |
#           v
#       SERVICE AVAILABILITY
#           |
#           v
#       NETWORK AVAILABILITY
#           |
#           v
#       ROUTING CANDIDATE
#
#
# ============================================================================
# CORE VIABILITY RULE
# ============================================================================
#
#
#       VIABLE
#           =
#       PERMITTED
#           AND
#       CAPABLE
#           AND
#       SERVICE OPERATIONAL
#           AND
#       NETWORK OPERATIONAL
#
#
# This is a logical AND relationship.
#
# It is NOT a weighted score.
#
#
#       DENIED + FAST
#
# does NOT become:
#
#
#       ALLOWED
#
#
#       DENIED + CHEAP
#
# does NOT become:
#
#
#       ALLOWED
#
#
#       DENIED + AMAZING MODEL
#
# does NOT become:
#
#
#       ALLOWED
#
#
# ============================================================================
#
#
#       HARD CONSTRAINTS FIRST.
#
#       OPTIMIZATION LATER.
#
#
#       POLICY NEVER BECOMES A SCORE.
#
#
# ============================================================================
#
# RESPONSIBILITY BOUNDARY
# ============================================================================
#
# CandidateEvaluator CONSUMES facts.
#
# It does not discover those facts.
#
#
# CandidateEvaluator does NOT:
#
#       discover AI services
#
#       classify request data
#
#       evaluate organizational policy
#
#       evaluate user policy
#
#       inspect Kubernetes
#
#       query cloud APIs
#
#       perform network probes
#
#       run BGP
#
#       control SD-WAN
#
#       determine service health
#
#       select an AI model
#
#       select the winning routing candidate
#
#       perform fallback
#
#       invoke an AI model
#
#       execute MCP tools
#
#       remediate infrastructure
#
#
# ============================================================================
#
#
#       CANDIDATE EVALUATOR
#       CONSUMES FACTS.
#
#
#       IT DOES NOT
#       DISCOVER FACTS.
#
#
# ============================================================================


from ..models.ai.policy import PolicyDecision
from ..models.ai.routing import RoutingCandidate
from ..models.ai.service import AIService

from ..models.enums.network_enums import (
    NetworkPathState,
    ServiceState,
)

from ..models.enums.policy_enums import PolicyDecisionStatus

from ..models.enums.routing_enums import (
    RoutingCandidateStatus,
    RoutingRejectionReason,
)

from ..models.network.assessment import NetworkAssessmentResult


# ============================================================================
# CANDIDATE EVALUATOR
# ============================================================================


class CandidateEvaluator:
    """
    Evaluate the routing viability of one AI service.

    CandidateEvaluator receives facts that have already been established by
    other Agent 11 subsystems and determines whether all required routing
    constraints are simultaneously satisfied.

    The evaluator processes one candidate at a time.

    It does not compare candidates and it does not select the final route.

    Current SEIR-I viability dimensions:

        1. Policy permission

        2. Model capability

        3. Reasoning-service availability

        4. Network-path availability


    Output:

        RoutingCandidate


    A candidate is either:

        VIABLE

    or:

        REJECTED


    A VIABLE candidate may later participate in AIRouter selection.

    A VIABLE candidate has NOT yet been selected.
    """

    # ========================================================================
    # PUBLIC EVALUATION METHOD
    # ========================================================================

    def evaluate(
        self,
        *,
        service: AIService,
        policy_decision: PolicyDecision,
        capability_supported: bool,
        service_state: ServiceState,
        network_assessment: NetworkAssessmentResult,
    ) -> RoutingCandidate:
        """
        Evaluate one AI service as a possible routing candidate.

        Evaluation follows deterministic gate precedence:

            1. POLICY

            2. CAPABILITY

            3. SERVICE AVAILABILITY

            4. NETWORK AVAILABILITY


        The first routing-dispositive failure becomes the candidate's
        rejection reason.

        If all four gates are satisfied, the candidate is VIABLE.


        IMPORTANT
        ---------

        Rejection precedence does not erase facts from other domains.

        For example:

            policy = DENY

            capability_supported = False

            service_state = UNAVAILABLE

            network = UNAVAILABLE


        produces:

            POLICY_DENIED


        because policy is the first routing-dispositive gate.

        This does not claim that the other three dimensions succeeded.

        Their original facts remain available in their owning subsystems
        and telemetry.
        """

        # ====================================================================
        # GATE 1
        #
        # POLICY
        # ====================================================================
        #
        # Policy is evaluated first.
        #
        # A service that is prohibited by policy must not remain in the
        # routing candidate set merely because it is:
        #
        #       healthy
        #
        #       reachable
        #
        #       inexpensive
        #
        #       fast
        #
        #       powerful
        #
        #
        # --------------------------------------------------------------------
        #
        #
        #       REACHABLE != AUTHORIZED
        #
        #
        #       HEALTHY != PERMITTED
        #
        #
        # --------------------------------------------------------------------

        policy_rejection = self._evaluate_policy(
            policy_decision=policy_decision,
        )

        if policy_rejection is not None:
            return self._rejected_candidate(
                service=service,
                reason=policy_rejection,
            )

        # ====================================================================
        # GATE 2
        #
        # CAPABILITY
        # ====================================================================
        #
        # Policy permission does not establish technical capability.
        #
        # A service may be fully authorized while exposing a model that
        # cannot perform the requested work.
        #
        #
        # --------------------------------------------------------------------
        #
        #
        #       AUTHORIZED != CAPABLE
        #
        #
        # --------------------------------------------------------------------
        #
        # For current SEIR-I architecture, capability_supported is a bool.
        #
        # False means the registered model capability contract does not
        # satisfy the requested requirement.
        #
        # Future dynamic capability discovery may eventually require a richer
        # result such as:
        #
        #       SUPPORTED
        #
        #       UNSUPPORTED
        #
        #       UNKNOWN
        #
        # That richer contract has not yet earned existence.
        #
        # --------------------------------------------------------------------

        if not capability_supported:
            return self._rejected_candidate(
                service=service,
                reason=RoutingRejectionReason.CAPABILITY_MISMATCH,
            )

        # ====================================================================
        # GATE 3
        #
        # SERVICE AVAILABILITY
        # ====================================================================
        #
        # A model may be:
        #
        #       authorized
        #
        #       capable
        #
        # while the actual reasoning service exposing that model is not
        # currently operational.
        #
        #
        # --------------------------------------------------------------------
        #
        #
        #       CAPABLE != AVAILABLE
        #
        #
        # --------------------------------------------------------------------

        service_rejection = self._evaluate_service_state(
            service_state=service_state,
        )

        if service_rejection is not None:
            return self._rejected_candidate(
                service=service,
                reason=service_rejection,
            )

        # ====================================================================
        # GATE 4
        #
        # NETWORK AVAILABILITY
        # ====================================================================
        #
        # A service may be:
        #
        #       authorized
        #
        #       capable
        #
        #       operational
        #
        # while Agent 11 cannot establish an operational network path from
        # the relevant source to the destination.
        #
        #
        # --------------------------------------------------------------------
        #
        #
        #       HEALTHY != REACHABLE
        #
        #
        # --------------------------------------------------------------------

        network_rejection = self._evaluate_network(
            network_assessment=network_assessment,
        )

        if network_rejection is not None:
            return self._rejected_candidate(
                service=service,
                reason=network_rejection,
            )

        # ====================================================================
        # ALL HARD CONSTRAINTS PASSED
        # ====================================================================
        #
        # Reaching this point establishes:
        #
        #
        #       policy permission
        #
        #           AND
        #
        #       capability compatibility
        #
        #           AND
        #
        #       operational service availability
        #
        #           AND
        #
        #       operational network availability
        #
        #
        # Therefore the service may remain in the routing candidate set.
        #
        #
        # --------------------------------------------------------------------
        #
        #
        #       VIABLE != SELECTED
        #
        #
        # --------------------------------------------------------------------
        #
        # AIRouter is responsible for selecting among viable candidates.
        #
        # CandidateEvaluator does not perform that selection.
        #
        # --------------------------------------------------------------------

        return RoutingCandidate(
            service_id=service.service_id,
            routing_domain=service.routing_domain,
            status=RoutingCandidateStatus.VIABLE,
            rejection_reason=None,
        )

    # ========================================================================
    # POLICY VIABILITY
    # ========================================================================

    @staticmethod
    def _evaluate_policy(
        *,
        policy_decision: PolicyDecision,
    ) -> RoutingRejectionReason | None:
        """
        Translate an established policy decision into routing viability.

        Returns
        -------

        None
            Policy established sufficient permission for candidate
            evaluation to continue.

        RoutingRejectionReason.POLICY_DENIED
            Policy explicitly denied this routing domain.

        RoutingRejectionReason.UNKNOWN
            Policy did not establish sufficient permission for routing
            viability.


        SEIR-I policy semantics
        -----------------------

        ALLOW
            Continue.

        DENY
            Reject as POLICY_DENIED.

        RESTRICT
            Fail closed as UNKNOWN because current policy contracts do not
            yet contain typed restriction details sufficient to prove that
            this candidate satisfies the restriction.

        INDETERMINATE
            Fail closed as UNKNOWN because permission could not be
            established.


        IMPORTANT
        ---------

            RESTRICT != DENY

            INDETERMINATE != DENY

            FAIL CLOSED != FALSIFY STATE
        """

        # --------------------------------------------------------------------
        # ALLOW
        # --------------------------------------------------------------------
        #
        # Policy has explicitly established permission.
        #
        # Candidate evaluation may continue to the capability gate.
        #
        # --------------------------------------------------------------------

        if policy_decision.status is PolicyDecisionStatus.ALLOW:
            return None

        # --------------------------------------------------------------------
        # DENY
        # --------------------------------------------------------------------
        #
        # This is an explicit negative policy decision.
        #
        # The candidate cannot participate in routing.
        #
        # --------------------------------------------------------------------

        if policy_decision.status is PolicyDecisionStatus.DENY:
            return RoutingRejectionReason.POLICY_DENIED

        # --------------------------------------------------------------------
        # RESTRICT
        # --------------------------------------------------------------------
        #
        # RESTRICT means policy has imposed conditions.
        #
        # Current SEIR-I PolicyDecision does not yet carry typed restriction
        # details sufficient for CandidateEvaluator to prove those conditions
        # have been satisfied.
        #
        # Therefore routing must fail closed.
        #
        # But we must not rewrite:
        #
        #
        #       RESTRICT
        #
        # into:
        #
        #
        #       DENY
        #
        #
        # because those policy states mean different things.
        #
        # --------------------------------------------------------------------

        if policy_decision.status is PolicyDecisionStatus.RESTRICT:
            return RoutingRejectionReason.UNKNOWN

        # --------------------------------------------------------------------
        # INDETERMINATE
        # --------------------------------------------------------------------
        #
        # Policy evaluation could not establish a definitive permission
        # result.
        #
        # Candidate viability therefore cannot be established.
        #
        # Again:
        #
        #
        #       INDETERMINATE != DENY
        #
        #
        # --------------------------------------------------------------------

        if (
            policy_decision.status
            is PolicyDecisionStatus.INDETERMINATE
        ):
            return RoutingRejectionReason.UNKNOWN

        # --------------------------------------------------------------------
        # DEFENSIVE FUTURE-ENUM FALLBACK
        # --------------------------------------------------------------------
        #
        # Pydantic validation and Python enums should make this branch
        # unreachable with the current enum definition.
        #
        # It exists so that if PolicyDecisionStatus is expanded in the future
        # before CandidateEvaluator is updated, the new state does not
        # accidentally become permissive.
        #
        #
        #       UNKNOWN NEW POLICY STATE
        #           ->
        #       FAIL CLOSED
        #
        #
        # --------------------------------------------------------------------

        return RoutingRejectionReason.UNKNOWN

    # ========================================================================
    # SERVICE AVAILABILITY
    # ========================================================================

    @staticmethod
    def _evaluate_service_state(
        *,
        service_state: ServiceState,
    ) -> RoutingRejectionReason | None:
        """
        Translate reasoning-service operational state into routing viability.

        SEIR-I semantics:

            AVAILABLE
                Operationally usable.

            DEGRADED
                Operationally usable for baseline SEIR-I routing.

            UNAVAILABLE
                Reject as SERVICE_UNAVAILABLE.

            UNKNOWN
                Reject as UNKNOWN because service viability cannot currently
                be established.


        IMPORTANT
        ---------

            DEGRADED != UNAVAILABLE

            UNKNOWN != UNAVAILABLE

            FAIL CLOSED != FALSIFY STATE
        """

        # --------------------------------------------------------------------
        # AVAILABLE
        # --------------------------------------------------------------------

        if service_state is ServiceState.AVAILABLE:
            return None

        # --------------------------------------------------------------------
        # DEGRADED
        # --------------------------------------------------------------------
        #
        # DEGRADED is an operational condition.
        #
        # It does not mean the service has stopped functioning.
        #
        # Current SEIR-I baseline routing therefore permits a degraded
        # service to remain viable.
        #
        # Future workload-suitability rules may determine that a specific
        # degraded condition is unsuitable for a specific workload.
        #
        # That future rule must not redefine DEGRADED as UNAVAILABLE.
        #
        #
        #       STATE != WORKLOAD SUITABILITY
        #
        #
        # --------------------------------------------------------------------

        if service_state is ServiceState.DEGRADED:
            return None

        # --------------------------------------------------------------------
        # UNAVAILABLE
        # --------------------------------------------------------------------
        #
        # The service is conclusively not operationally usable.
        #
        # --------------------------------------------------------------------

        if service_state is ServiceState.UNAVAILABLE:
            return RoutingRejectionReason.SERVICE_UNAVAILABLE

        # --------------------------------------------------------------------
        # UNKNOWN
        # --------------------------------------------------------------------
        #
        # Agent 11 could not establish the current service state.
        #
        # This does NOT justify saying the service is unavailable.
        #
        #
        #       NOT PROVEN AVAILABLE
        #           !=
        #       PROVEN UNAVAILABLE
        #
        #
        # Candidate routing nevertheless fails closed because operational
        # viability has not been established.
        #
        # --------------------------------------------------------------------

        if service_state is ServiceState.UNKNOWN:
            return RoutingRejectionReason.UNKNOWN

        # --------------------------------------------------------------------
        # DEFENSIVE FUTURE-ENUM FALLBACK
        # --------------------------------------------------------------------

        return RoutingRejectionReason.UNKNOWN

    # ========================================================================
    # NETWORK AVAILABILITY
    # ========================================================================

    @staticmethod
    def _evaluate_network(
        *,
        network_assessment: NetworkAssessmentResult,
    ) -> RoutingRejectionReason | None:
        """
        Determine whether current network assessment establishes at least one
        operationally usable path.

        Current SEIR-I path semantics:

            AVAILABLE
                Operationally usable.

            DEGRADED
                Operationally usable for baseline SEIR-I routing.

            UNAVAILABLE
                This individual path is not usable.

            UNKNOWN
                Current usability of this individual path has not been
                established.


        Candidate-level network result:

            Any AVAILABLE path
                -> network gate passes

            Otherwise, any DEGRADED path
                -> network gate passes

            All paths UNAVAILABLE
                -> NETWORK_UNAVAILABLE

            No path assessments
                -> UNKNOWN

            UNAVAILABLE + UNKNOWN, with no usable path
                -> UNKNOWN


        IMPORTANT
        ---------

        This method evaluates operational network viability.

        It does NOT determine path authorization.

        Current SEIR-I policy primarily operates at the AI routing-domain
        level.

        Future path-specific policy must remain a separate policy concern.


            PATH AVAILABLE != PATH AUTHORIZED

            REACHABLE != AUTHORIZED
        """

        path_assessments = network_assessment.path_assessments

        # --------------------------------------------------------------------
        # CASE 1
        #
        # NO CURRENT PATH ASSESSMENTS
        # --------------------------------------------------------------------
        #
        # An empty path-assessment collection does not establish network
        # unavailability.
        #
        # It establishes that CandidateEvaluator has not received sufficient
        # current path knowledge to prove operational network viability.
        #
        #
        #       NO EVIDENCE != NEGATIVE EVIDENCE
        #
        #
        #       EMPTY KNOWLEDGE != NEGATIVE KNOWLEDGE
        #
        #
        # --------------------------------------------------------------------

        if not path_assessments:
            return RoutingRejectionReason.UNKNOWN

        # --------------------------------------------------------------------
        # CASE 2
        #
        # AT LEAST ONE AVAILABLE PATH
        # --------------------------------------------------------------------
        #
        # Current SEIR-I viability requires at least one operationally usable
        # path.
        #
        # AVAILABLE clearly satisfies that requirement.
        #
        # We intentionally do not care here whether another path is:
        #
        #       DEGRADED
        #
        #       UNAVAILABLE
        #
        #       UNKNOWN
        #
        # because one usable path is sufficient for baseline operational
        # network viability.
        #
        # --------------------------------------------------------------------

        if any(
            assessment.state is NetworkPathState.AVAILABLE
            for assessment in path_assessments
        ):
            return None

        # --------------------------------------------------------------------
        # CASE 3
        #
        # AT LEAST ONE DEGRADED PATH
        # --------------------------------------------------------------------
        #
        # No AVAILABLE path exists at this point.
        #
        # But DEGRADED remains operationally usable for SEIR-I.
        #
        # Therefore:
        #
        #
        #       DEGRADED + UNAVAILABLE
        #
        #           ->
        #
        #       NETWORK GATE PASSES
        #
        #
        # and:
        #
        #
        #       DEGRADED + UNKNOWN
        #
        #           ->
        #
        #       NETWORK GATE PASSES
        #
        #
        # because the degraded path itself has established operational
        # usability under current SEIR-I semantics.
        #
        # --------------------------------------------------------------------

        if any(
            assessment.state is NetworkPathState.DEGRADED
            for assessment in path_assessments
        ):
            return None

        # --------------------------------------------------------------------
        # CASE 4
        #
        # ALL PATHS CONCLUSIVELY UNAVAILABLE
        # --------------------------------------------------------------------
        #
        # We use NETWORK_UNAVAILABLE only when every supplied path assessment
        # establishes UNAVAILABLE.
        #
        #
        # Example:
        #
        #
        #       private-link-a = UNAVAILABLE
        #
        #       vpn-a          = UNAVAILABLE
        #
        #
        # Result:
        #
        #
        #       NETWORK_UNAVAILABLE
        #
        #
        # This is stronger than merely saying:
        #
        #
        #       no usable path was found
        #
        #
        # We possess affirmative negative evidence for every assessed path.
        #
        # --------------------------------------------------------------------

        if all(
            assessment.state is NetworkPathState.UNAVAILABLE
            for assessment in path_assessments
        ):
            return RoutingRejectionReason.NETWORK_UNAVAILABLE

        # --------------------------------------------------------------------
        # CASE 5
        #
        # UNRESOLVED NETWORK UNCERTAINTY
        # --------------------------------------------------------------------
        #
        # If execution reaches this point:
        #
        #
        #       there is no AVAILABLE path
        #
        #       there is no DEGRADED path
        #
        #       not every path is UNAVAILABLE
        #
        #
        # Therefore at least one assessment contains an unresolved state such
        # as UNKNOWN.
        #
        #
        # Example:
        #
        #
        #       private-link-a = UNAVAILABLE
        #
        #       vpn-a          = UNKNOWN
        #
        #
        # We cannot truthfully conclude:
        #
        #
        #       NETWORK_UNAVAILABLE
        #
        #
        # because vpn-a has not been established unavailable.
        #
        # But we also cannot establish a usable path.
        #
        # Therefore:
        #
        #
        #       REJECTED / UNKNOWN
        #
        #
        # --------------------------------------------------------------------
        #
        #
        #       UNKNOWN != UNAVAILABLE
        #
        #
        #       FAIL CLOSED != FALSIFY STATE
        #
        #
        # --------------------------------------------------------------------

        return RoutingRejectionReason.UNKNOWN

    # ========================================================================
    # REJECTED CANDIDATE CONSTRUCTION
    # ========================================================================

    @staticmethod
    def _rejected_candidate(
        *,
        service: AIService,
        reason: RoutingRejectionReason,
    ) -> RoutingCandidate:
        """
        Construct a rejected RoutingCandidate.

        AIService is the authoritative source of candidate identity.

        CandidateEvaluator derives:

            service_id

            routing_domain

        directly from AIService.

        The caller does not independently provide those values.


        WHY?
        ----

        This avoids constructing contradictory candidate identity such as:

            service_id
                belonging to service A

        while:

            routing_domain
                belongs to service B


        Current rule:

            AIService
                ->
            authoritative routing candidate identity
        """

        return RoutingCandidate(
            service_id=service.service_id,
            routing_domain=service.routing_domain,
            status=RoutingCandidateStatus.REJECTED,
            rejection_reason=reason,
        )


# ============================================================================
# PART I
#
# ROUTING REJECTION PRECEDENCE
# ============================================================================
#
#
#       1. POLICY
#
#       2. CAPABILITY
#
#       3. SERVICE
#
#       4. NETWORK
#
#
# ============================================================================
#
# The first routing-dispositive failure becomes:
#
#
#       RoutingCandidate.rejection_reason
#
#
# Example:
#
#
#       policy
#           = DENY
#
#
#       capability
#           = unsupported
#
#
#       service
#           = UNAVAILABLE
#
#
#       network
#           = UNAVAILABLE
#
#
# Candidate:
#
#
#       status
#           = REJECTED
#
#
#       rejection_reason
#           = POLICY_DENIED
#
#
# ============================================================================
#
# This does NOT erase the other facts.
#
#
#       REJECTION REASON
#           !=
#       COMPLETE SYSTEM DIAGNOSIS
#
#
# ============================================================================


# ============================================================================
# POLICY MATRIX
# ============================================================================
#
#
#       ALLOW
#           |
#           v
#       CONTINUE
#
#
#       DENY
#           |
#           v
#       REJECTED
#       POLICY_DENIED
#
#
#       RESTRICT
#           |
#           v
#       REJECTED
#       UNKNOWN
#
#
#       INDETERMINATE
#           |
#           v
#       REJECTED
#       UNKNOWN
#
#
# ============================================================================
#
#
#       RESTRICT != DENY
#
#       INDETERMINATE != DENY
#
#
# ============================================================================


# ============================================================================
# SERVICE MATRIX
# ============================================================================
#
#
#       AVAILABLE
#           |
#           v
#       CONTINUE
#
#
#       DEGRADED
#           |
#           v
#       CONTINUE
#
#
#       UNAVAILABLE
#           |
#           v
#       REJECTED
#       SERVICE_UNAVAILABLE
#
#
#       UNKNOWN
#           |
#           v
#       REJECTED
#       UNKNOWN
#
#
# ============================================================================
#
#
#       DEGRADED != UNAVAILABLE
#
#       UNKNOWN != UNAVAILABLE
#
#
# ============================================================================


# ============================================================================
# NETWORK MATRIX
# ============================================================================
#
#
# PATH ASSESSMENTS
#
#       [AVAILABLE]
#
#           ->
#
#       PASS
#
#
# ---------------------------------------------------------------------------
#
#
#       [UNAVAILABLE, AVAILABLE]
#
#           ->
#
#       PASS
#
#
# ---------------------------------------------------------------------------
#
#
#       [UNKNOWN, AVAILABLE]
#
#           ->
#
#       PASS
#
#
# ---------------------------------------------------------------------------
#
#
#       [DEGRADED]
#
#           ->
#
#       PASS
#
#
# ---------------------------------------------------------------------------
#
#
#       [UNAVAILABLE, DEGRADED]
#
#           ->
#
#       PASS
#
#
# ---------------------------------------------------------------------------
#
#
#       [UNKNOWN, DEGRADED]
#
#           ->
#
#       PASS
#
#
# ---------------------------------------------------------------------------
#
#
#       [UNAVAILABLE]
#
#           ->
#
#       NETWORK_UNAVAILABLE
#
#
# ---------------------------------------------------------------------------
#
#
#       [UNAVAILABLE, UNAVAILABLE]
#
#           ->
#
#       NETWORK_UNAVAILABLE
#
#
# ---------------------------------------------------------------------------
#
#
#       [UNKNOWN]
#
#           ->
#
#       UNKNOWN
#
#
# ---------------------------------------------------------------------------
#
#
#       [UNAVAILABLE, UNKNOWN]
#
#           ->
#
#       UNKNOWN
#
#
# ---------------------------------------------------------------------------
#
#
#       []
#
#           ->
#
#       UNKNOWN
#
#
# ============================================================================
#
#
#       NO USABLE PATH FOUND
#
#           !=
#
#       ALL PATHS PROVEN UNAVAILABLE
#
#
# ============================================================================


# ============================================================================
# WHY UNKNOWN MATTERS
# ============================================================================
#
# Consider:
#
#
#       private-link-a
#           = UNAVAILABLE
#
#
#       vpn-a
#           = UNKNOWN
#
#
# CandidateEvaluator must not transform this into:
#
#
#       private-link-a
#           = UNAVAILABLE
#
#
#       vpn-a
#           = UNAVAILABLE
#
#
# merely because routing must fail closed.
#
#
# ============================================================================
#
#
#       SECURITY CONSERVATISM
#       DOES NOT REQUIRE
#       EPISTEMIC DISHONESTY.
#
#
# ============================================================================
#
#
# We may safely say:
#
#
#       "I cannot establish a viable route."
#
#
# without falsely saying:
#
#
#       "I established that every route is unavailable."
#
#
# ============================================================================


# ============================================================================
# DEGRADED SEMANTICS
# ============================================================================
#
# For current SEIR-I:
#
#
#       DEGRADED SERVICE
#
#           ->
#
#       OPERATIONALLY USABLE
#
#
#       DEGRADED NETWORK PATH
#
#           ->
#
#       OPERATIONALLY USABLE
#
#
# ============================================================================
#
# This is intentionally a baseline routing rule.
#
#
# Future SEIR-II behavior may introduce:
#
#
#       WORKLOAD
#           +
#       DEGRADED CONDITION
#           |
#           v
#       SUITABILITY EVALUATION
#
#
# For example:
#
#
#       LIGHT WORKLOAD
#           +
#       DEGRADED PATH
#           ->
#       SUITABLE
#
#
# while:
#
#
#       HEAVY WORKLOAD
#           +
#       SAME DEGRADED PATH
#           ->
#       UNSUITABLE
#
#
# ============================================================================
#
# That future rule must not redefine:
#
#
#       DEGRADED
#
#
# as:
#
#
#       UNAVAILABLE
#
#
# ============================================================================
#
#
#       STATE != SUITABILITY
#
#
# ============================================================================


# ============================================================================
# NO POLICY SCORING
# ============================================================================
#
# DO NOT IMPLEMENT:
#
#
#       score = 0
#
#       if policy_allowed:
#           score += 100
#
#       if capability_supported:
#           score += 50
#
#       if service_available:
#           score += 30
#
#       if network_available:
#           score += 20
#
#
# ============================================================================
#
# Why?
#
#
# Because eventually someone will be tempted to write:
#
#
#       policy denied
#           -100
#
#       cheap model
#            +40
#
#       low latency
#            +30
#
#       amazing reasoning
#            +40
#
#       ----------------
#
#       score
#            +10
#
#
# and congratulations:
#
# Chewbacca has just discovered arithmetic-based data exfiltration.
#
#
# ============================================================================
#
#
#       POLICY IS A HARD CONSTRAINT.
#
#
#       POLICY NEVER BECOMES A SCORE.
#
#
# ============================================================================


# ============================================================================
# CandidateEvaluator != AIRouter
# ============================================================================
#
# CandidateEvaluator may produce:
#
#
#       Candidate A
#           VIABLE
#
#
#       Candidate B
#           VIABLE
#
#
#       Candidate C
#           REJECTED
#
#
# CandidateEvaluator does not decide:
#
#
#       A wins
#
#
# or:
#
#
#       B wins
#
#
# ============================================================================
#
# That belongs to:
#
#
#       AIRouter
#
#
# ============================================================================
#
#
#       VIABILITY != SELECTION
#
#
# ============================================================================


# ============================================================================
# CandidateEvaluator != ModelRouter
# ============================================================================
#
# ModelRouter determines whether the model associated with a service
# satisfies the requested capability requirement.
#
#
# CandidateEvaluator receives:
#
#
#       capability_supported
#
#
# It does not perform model capability discovery itself.
#
#
# ============================================================================
#
#
#       CAPABILITY MATCHING
#           !=
#       CANDIDATE VIABILITY
#
#
# ============================================================================


# ============================================================================
# CandidateEvaluator != NetworkOrchestrator
# ============================================================================
#
# NetworkOrchestrator gathers and assesses operational network evidence.
#
#
# CandidateEvaluator receives:
#
#
#       NetworkAssessmentResult
#
#
# It does not:
#
#
#       inspect routing tables
#
#       inspect BGP
#
#       query VPN state
#
#       query SD-WAN
#
#       inspect PrivateLink
#
#       perform synthetic probes
#
#
# ============================================================================
#
#
#       NETWORK
#       ESTABLISHES NETWORK FACTS.
#
#
#       ROUTING
#       CONSUMES NETWORK FACTS.
#
#
# ============================================================================


# ============================================================================
# CandidateEvaluator != Policy Engine
# ============================================================================
#
# CandidateEvaluator receives:
#
#
#       PolicyDecision
#
#
# It does not inspect:
#
#
#       data classification rules
#
#       organization policy tables
#
#       user preferences
#
#       E7 / E8 / E9 mappings
#
#
# ============================================================================
#
#
#       POLICY
#       ESTABLISHES PERMISSION.
#
#
#       ROUTING
#       CONSUMES PERMISSION.
#
#
# ============================================================================


# ============================================================================
# CandidateEvaluator != Service Health Monitor
# ============================================================================
#
# CandidateEvaluator receives:
#
#
#       ServiceState
#
#
# It does not determine that state.
#
#
# ============================================================================
#
#
#       SERVICE AVAILABILITY
#       IS AN INPUT TO ROUTING.
#
#
#       IT IS NOT CREATED BY ROUTING.
#
#
# ============================================================================


# ============================================================================
# CandidateEvaluator != FallbackEvaluator
# ============================================================================
#
# CandidateEvaluator evaluates one candidate during one routing cycle.
#
#
# If a selected service later fails:
#
#
#       FallbackEvaluator
#
# determines whether another routing cycle may occur.
#
#
# A new routing cycle should obtain current facts and evaluate candidates
# again.
#
#
# ============================================================================
#
#
#       HISTORICAL VIABILITY
#           !=
#       CURRENT VIABILITY
#
#
# ============================================================================
#
#
# CandidateEvaluator should not have:
#
#
#       fallback_mode=True
#
#
# that weakens viability requirements.
#
#
#       FALLBACK MAY REDUCE AVAILABILITY.
#
#
#       FALLBACK MAY NOT REDUCE SECURITY POLICY.
#
#
# ============================================================================


# ============================================================================
# VIABLE != INVOKE
# ============================================================================
#
# CandidateEvaluator returning:
#
#
#       VIABLE
#
#
# means:
#
#
#       this service may participate in route selection
#
#
# It does not mean:
#
#
#       invoke this service
#
#
# ============================================================================
#
#
#       VIABLE != SELECTED
#
#       SELECTED != INVOKED
#
#       INVOKED != TRUSTED
#
#       AI OUTPUT != ACTION AUTHORITY
#
#
# ============================================================================


# ============================================================================
# PART I TEST EXPECTATIONS
# ============================================================================
#
# The following cases should eventually become unit tests.
#
#
# ---------------------------------------------------------------------------
# TEST 1
# ---------------------------------------------------------------------------
#
# Policy:
#
#       ALLOW
#
# Capability:
#
#       True
#
# Service:
#
#       AVAILABLE
#
# Network:
#
#       AVAILABLE
#
# Expected:
#
#       VIABLE
#
#
# ---------------------------------------------------------------------------
# TEST 2
# ---------------------------------------------------------------------------
#
# Policy:
#
#       DENY
#
# Everything else:
#
#       healthy / available
#
# Expected:
#
#       REJECTED
#       POLICY_DENIED
#
#
# ---------------------------------------------------------------------------
# TEST 3
# ---------------------------------------------------------------------------
#
# Policy:
#
#       ALLOW
#
# Capability:
#
#       False
#
# Expected:
#
#       REJECTED
#       CAPABILITY_MISMATCH
#
#
# ---------------------------------------------------------------------------
# TEST 4
# ---------------------------------------------------------------------------
#
# Policy:
#
#       ALLOW
#
# Capability:
#
#       True
#
# Service:
#
#       UNAVAILABLE
#
# Expected:
#
#       REJECTED
#       SERVICE_UNAVAILABLE
#
#
# ---------------------------------------------------------------------------
# TEST 5
# ---------------------------------------------------------------------------
#
# Policy:
#
#       ALLOW
#
# Capability:
#
#       True
#
# Service:
#
#       UNKNOWN
#
# Expected:
#
#       REJECTED
#       UNKNOWN
#
#
# ---------------------------------------------------------------------------
# TEST 6
# ---------------------------------------------------------------------------
#
# Network:
#
#       [UNAVAILABLE, UNAVAILABLE]
#
# Expected:
#
#       REJECTED
#       NETWORK_UNAVAILABLE
#
#
# ---------------------------------------------------------------------------
# TEST 7
# ---------------------------------------------------------------------------
#
# Network:
#
#       [UNAVAILABLE, UNKNOWN]
#
# Expected:
#
#       REJECTED
#       UNKNOWN
#
#
# ---------------------------------------------------------------------------
# TEST 8
# ---------------------------------------------------------------------------
#
# Network:
#
#       []
#
# Expected:
#
#       REJECTED
#       UNKNOWN
#
#
# ---------------------------------------------------------------------------
# TEST 9
# ---------------------------------------------------------------------------
#
# Service:
#
#       DEGRADED
#
# Network:
#
#       AVAILABLE
#
# Expected:
#
#       VIABLE
#
#
# ---------------------------------------------------------------------------
# TEST 10
# ---------------------------------------------------------------------------
#
# Service:
#
#       AVAILABLE
#
# Network:
#
#       DEGRADED
#
# Expected:
#
#       VIABLE
#
#
# ---------------------------------------------------------------------------
# TEST 11
# ---------------------------------------------------------------------------
#
# Policy:
#
#       RESTRICT
#
# Expected:
#
#       REJECTED
#       UNKNOWN
#
#
# ---------------------------------------------------------------------------
# TEST 12
# ---------------------------------------------------------------------------
#
# Policy:
#
#       INDETERMINATE
#
# Expected:
#
#       REJECTED
#       UNKNOWN
#
#
# ---------------------------------------------------------------------------
# TEST 13
# ---------------------------------------------------------------------------
#
# Policy:
#
#       DENY
#
# Capability:
#
#       False
#
# Service:
#
#       UNAVAILABLE
#
# Network:
#
#       UNAVAILABLE
#
# Expected:
#
#       REJECTED
#       POLICY_DENIED
#
#
# This proves deterministic rejection precedence.
#
#
# ============================================================================


# ============================================================================
# PART I FINAL INVARIANTS
# ============================================================================
#
#
# POLICY
# ------
#
#       PERMITTED != CAPABLE
#
#       REACHABLE != AUTHORIZED
#
#       HEALTHY != PERMITTED
#
#       RESTRICT != DENY
#
#       INDETERMINATE != DENY
#
#       POLICY NEVER BECOMES A SCORE
#
#
# CAPABILITY
# ----------
#
#       CAPABLE != AUTHORIZED
#
#       CAPABLE != AVAILABLE
#
#       CAPABILITY MATCHING != MODEL SELECTION
#
#
# SERVICE
# -------
#
#       AVAILABLE SERVICE != REACHABLE SERVICE
#
#       DEGRADED != UNAVAILABLE
#
#       UNKNOWN != UNAVAILABLE
#
#       STATE != WORKLOAD SUITABILITY
#
#
# NETWORK
# -------
#
#       PATH AVAILABLE != PATH AUTHORIZED
#
#       NO EVIDENCE != NEGATIVE EVIDENCE
#
#       EMPTY KNOWLEDGE != NEGATIVE KNOWLEDGE
#
#       NOT PROVEN AVAILABLE != PROVEN UNAVAILABLE
#
#       UNKNOWN != UNAVAILABLE
#
#
# ROUTING
# -------
#
#       REJECTION REASON != COMPLETE SYSTEM DIAGNOSIS
#
#       VIABILITY != SELECTION
#
#       VIABILITY != FALLBACK
#
#       VIABILITY != DISCOVERY
#
#
# EPISTEMICS
# -----------
#
#       FAIL CLOSED != FALSIFY STATE
#
#       SECURITY CONSERVATISM
#       DOES NOT REQUIRE
#       EPISTEMIC DISHONESTY
#
#
# AUTHORITY
# ---------
#
#       VIABLE != SELECTED
#
#       SELECTED != INVOKED
#
#       INVOKED != TRUSTED
#
#       AI OUTPUT != ACTION AUTHORITY
#
#
# ============================================================================
# FINAL PART I CONTRACT
# ============================================================================
#
#
#       CandidateEvaluator
#
#       DOES NOT CREATE:
#
#
#           POLICY TRUTH
#
#           CAPABILITY TRUTH
#
#           SERVICE TRUTH
#
#           NETWORK TRUTH
#
#
#       IT RECEIVES THOSE TRUTHS
#
#       AND ASKS:
#
#
#           "DO ALL REQUIRED CONDITIONS
#            HOLD AT THE SAME TIME
#            FOR THIS ONE SERVICE?"
#
#
#       YES
#           ->
#       VIABLE
#
#
#       NO
#           ->
#       REJECTED
#
#
# ============================================================================
# END PART I
# ============================================================================

# ============================================================================
# routing/candidate_evaluator.py
#
# COMPLETE PART II
#
# RELATIONSHIP INTEGRITY
# AND
# EPISTEMIC SEMANTICS
# ============================================================================
#
# PURPOSE
# -------
#
# Part I established the core routing viability funnel:
#
#
#       POLICY
#           |
#           v
#       CAPABILITY
#           |
#           v
#       SERVICE
#           |
#           v
#       NETWORK
#           |
#           v
#       VIABLE / REJECTED
#
#
# Part II protects that funnel.
#
#
# Before Agent 11 asks:
#
#
#       "Do these facts establish routing viability?"
#
#
# it must first ask:
#
#
#       "Do these facts actually belong together?"
#
#
# ============================================================================
# CENTRAL PART II RULE
# ============================================================================
#
#
#       VALID FACT
#           !=
#       VALID RELATIONSHIP BETWEEN FACTS
#
#
# ============================================================================
#
# Consider:
#
#
#       AIService(
#           routing_domain=COMPANY_CLOUD_LLM
#       )
#
#
# and:
#
#
#       PolicyDecision(
#           routing_domain=EXTERNAL_FM,
#           status=ALLOW,
#       )
#
#
# Each object may be perfectly valid by itself.
#
#
# But together they do NOT establish:
#
#
#       COMPANY_CLOUD_LLM is allowed
#
#
# because the PolicyDecision belongs to a different routing domain.
#
#
# ============================================================================
#
#
#       OBJECT VALIDITY
#           !=
#       CROSS-OBJECT COHERENCE
#
#
# ============================================================================
#
# This distinction becomes extremely important in distributed systems.
#
# Agent 11 will eventually receive facts from:
#
#
#       policy engines
#
#       model registries
#
#       Kubernetes
#
#       cloud APIs
#
#       service-health systems
#
#       network observers
#
#       SD-WAN
#
#       BGP
#
#       MCP services
#
#       telemetry systems
#
#
# The fact that every individual object passed Pydantic validation does not
# prove that the objects describe the same real-world thing.
#
#
# ============================================================================
#
#
#       TYPE CORRECT
#           !=
#       RELATIONSHIP CORRECT
#
#
# ============================================================================


# ============================================================================
# PART II MODIFICATION TO evaluate()
# ============================================================================
#
# Part I began immediately with:
#
#
#       GATE 1: POLICY
#
#
# Part II introduces:
#
#
#       STAGE 0: RELATIONSHIP INTEGRITY
#
#
# Therefore the complete conceptual order becomes:
#
#
#       0. RELATIONSHIP INTEGRITY
#
#       1. POLICY
#
#       2. CAPABILITY
#
#       3. SERVICE
#
#       4. NETWORK
#
#
# ============================================================================
#
#
#       COHERENCE BEFORE VIABILITY
#
#
# ============================================================================


# Add this at the beginning of CandidateEvaluator.evaluate(),
# before the Part I policy gate:


        # ====================================================================
        # STAGE 0
        #
        # RELATIONSHIP INTEGRITY
        # ====================================================================
        #
        # Every input object may be individually valid while the collection
        # of objects is logically inconsistent.
        #
        # Before performing routing viability reasoning, CandidateEvaluator
        # validates the cross-domain relationships that candidate evaluation
        # itself creates.
        #
        #
        # --------------------------------------------------------------------
        #
        #
        #       VALID INPUT OBJECTS
        #           !=
        #       VALID EVALUATION INPUT
        #
        #
        # --------------------------------------------------------------------

        self._validate_relationships(
            service=service,
            policy_decision=policy_decision,
            network_assessment=network_assessment,
        )


# ============================================================================
# RELATIONSHIP VALIDATION
# ============================================================================
#
# Add the following methods to CandidateEvaluator.
#
# ============================================================================


    @staticmethod
    def _validate_relationships(
        *,
        service: AIService,
        policy_decision: PolicyDecision,
        network_assessment: NetworkAssessmentResult,
    ) -> None:
        """
        Validate relationships among independently valid domain facts.

        This method answers:

            "Can these facts coherently participate in the same
             candidate evaluation?"


        It does NOT answer:

            "Is the candidate viable?"


        That distinction is fundamental.


        RELATIONSHIP FAILURE
        --------------------

        A relationship failure means:

            Agent 11 has been supplied with contradictory or incorrectly
            assembled facts.


        ROUTING REJECTION
        -----------------

        A routing rejection means:

            Agent 11 has coherent facts, but those facts establish that
            one or more routing requirements were not satisfied.


        These outcomes must not be confused.
        """

        # ====================================================================
        # RELATIONSHIP 1
        #
        # SERVICE ROUTING DOMAIN
        # MUST MATCH
        # POLICY DECISION ROUTING DOMAIN
        # ====================================================================
        #
        # AIService tells us the routing domain in which the service exists.
        #
        #
        # Example:
        #
        #
        #       service.routing_domain
        #           =
        #       COMPANY_CLOUD_LLM
        #
        #
        # PolicyDecision tells us the policy result for one routing domain.
        #
        #
        # Example:
        #
        #
        #       policy_decision.routing_domain
        #           =
        #       COMPANY_CLOUD_LLM
        #
        #
        # Those values must describe the same domain before the policy
        # decision may be used to evaluate this service.
        #
        # ====================================================================

        if (
            service.routing_domain
            is not policy_decision.routing_domain
        ):
            raise ValueError(
                "Policy decision routing domain does not match "
                "the candidate service routing domain."
            )

        # ====================================================================
        # NETWORK AGGREGATE COHERENCE
        # ====================================================================
        #
        # CandidateEvaluator currently receives NetworkAssessmentResult as
        # one established network fact.
        #
        # During development, we also verify that the network result is
        # internally coherent before consuming it.
        #
        #
        # IMPORTANT ARCHITECTURAL NOTE
        # ----------------------------
        #
        # These network-internal checks are educationally useful here because
        # they demonstrate relationship integrity.
        #
        # However, they are fundamentally invariants of:
        #
        #
        #       NetworkAssessmentResult
        #
        #
        # rather than invariants of routing.
        #
        #
        # The mature implementation should move these checks as close as
        # possible to the model that owns them:
        #
        #
        #       models/network/assessment.py
        #
        #
        # CandidateEvaluator should eventually be able to trust that a valid
        # NetworkAssessmentResult is internally coherent.
        #
        #
        # ====================================================================
        #
        #
        #       VALIDATE AN INVARIANT
        #       AS CLOSE AS POSSIBLE
        #       TO THE DOMAIN THAT OWNS IT.
        #
        #
        # ====================================================================

        CandidateEvaluator._validate_network_relationships(
            network_assessment=network_assessment,
        )


    # ========================================================================
    # NETWORK AGGREGATE RELATIONSHIP VALIDATION
    # ========================================================================

    @staticmethod
    def _validate_network_relationships(
        *,
        network_assessment: NetworkAssessmentResult,
    ) -> None:
        """
        Validate internal identity relationships in NetworkAssessmentResult.

        This is primarily included in CandidateEvaluator Part II to teach
        cross-object relationship integrity.

        Mature ownership should migrate these invariants to the network
        aggregate model itself.


        The enclosing NetworkAssessmentResult establishes:

            source_id

            destination_id


        Every expected path, path evidence item, and path assessment contained
        in that result must describe that same source/destination relationship.


        Otherwise we could accidentally reason over network evidence belonging
        to another destination.
        """

        source_id = network_assessment.source_id
        destination_id = network_assessment.destination_id

        # ====================================================================
        # EXPECTED PATH RELATIONSHIPS
        # ====================================================================
        #
        # Suppose the enclosing assessment says:
        #
        #
        #       source:
        #           agent11-prod
        #
        #       destination:
        #           company-llm-east
        #
        #
        # but one contained expected path says:
        #
        #
        #       source:
        #           agent11-prod
        #
        #       destination:
        #           external-model-provider
        #
        #
        # That path does not belong in this network assessment.
        #
        # ====================================================================

        for path in network_assessment.expected_paths:

            if path.source_id != source_id:
                raise ValueError(
                    "Expected network path source does not match "
                    "the enclosing network assessment source."
                )

            if path.destination_id != destination_id:
                raise ValueError(
                    "Expected network path destination does not match "
                    "the enclosing network assessment destination."
                )

        # ====================================================================
        # PATH EVIDENCE RELATIONSHIPS
        # ====================================================================
        #
        # Network evidence must describe the same source/destination pair as
        # the assessment in which it appears.
        #
        #
        # Otherwise:
        #
        #
        #       EVIDENCE FROM DESTINATION B
        #
        # could accidentally establish:
        #
        #
        #       REACHABILITY TO DESTINATION A
        #
        #
        # That would be an identity failure, not network uncertainty.
        #
        # ====================================================================

        for evidence in network_assessment.path_evidence:

            if evidence.source_id != source_id:
                raise ValueError(
                    "Network path evidence source does not match "
                    "the enclosing network assessment source."
                )

            if evidence.destination_id != destination_id:
                raise ValueError(
                    "Network path evidence destination does not match "
                    "the enclosing network assessment destination."
                )

        # ====================================================================
        # PATH ASSESSMENT RELATIONSHIPS
        # ====================================================================

        for assessment in network_assessment.path_assessments:

            if assessment.source_id != source_id:
                raise ValueError(
                    "Network path assessment source does not match "
                    "the enclosing network assessment source."
                )

            if assessment.destination_id != destination_id:
                raise ValueError(
                    "Network path assessment destination does not match "
                    "the enclosing network assessment destination."
                )


# ============================================================================
# PART II
#
# RELATIONSHIP FAILURE
# !=
# ROUTING REJECTION
# ============================================================================
#
# This distinction deserves special attention.
#
#
# ---------------------------------------------------------------------------
# CASE A
#
# VALID FACTS, NEGATIVE ROUTING OUTCOME
# ---------------------------------------------------------------------------
#
#
#       service.routing_domain
#           =
#       COMPANY_CLOUD_LLM
#
#
#       policy_decision.routing_domain
#           =
#       COMPANY_CLOUD_LLM
#
#
#       policy_decision.status
#           =
#       DENY
#
#
# These facts are coherent.
#
#
# The policy decision belongs to the service's routing domain.
#
#
# CandidateEvaluator may therefore legitimately conclude:
#
#
#       RoutingCandidate(
#           status=REJECTED,
#           rejection_reason=POLICY_DENIED,
#       )
#
#
# ============================================================================
#
# This is a normal routing outcome.
#
#
# ---------------------------------------------------------------------------
# CASE B
#
# VALID OBJECTS, INVALID RELATIONSHIP
# ---------------------------------------------------------------------------
#
#
#       service.routing_domain
#           =
#       COMPANY_CLOUD_LLM
#
#
#       policy_decision.routing_domain
#           =
#       EXTERNAL_FM
#
#
# The PolicyDecision may itself be valid.
#
#
# The AIService may itself be valid.
#
#
# But the policy decision does not belong to the service being evaluated.
#
#
# Therefore:
#
#
#       ValueError
#
#
# NOT:
#
#
#       POLICY_DENIED
#
#
# NOT:
#
#
#       UNKNOWN
#
#
# ============================================================================
#
#
#       BAD RELATIONSHIP
#           !=
#       NEGATIVE DOMAIN DECISION
#
#
# ============================================================================


# ============================================================================
# WHY THIS MUST NOT BECOME UNKNOWN
# ============================================================================
#
# It might initially seem safer to write:
#
#
#       if service.routing_domain != policy.routing_domain:
#           return rejected(UNKNOWN)
#
#
# But that destroys an extremely important distinction.
#
#
# ============================================================================
#
# UNKNOWN means:
#
#
#       "The system has a legitimate domain fact whose truth
#        could not currently be established."
#
#
# Examples:
#
#
#       PolicyDecision.INDETERMINATE
#
#       ServiceState.UNKNOWN
#
#       NetworkPathState.UNKNOWN
#
#
# ============================================================================
#
# A mismatched routing domain means something different:
#
#
#       "The software assembled facts that do not belong together."
#
#
# ============================================================================
#
#
#       UNCERTAINTY
#           !=
#       CONTRADICTION
#
#
# ============================================================================
#
# If we translate contradictions into UNKNOWN, integration defects become
# indistinguishable from legitimate uncertainty.
#
#
# That makes troubleshooting dramatically harder.
#
#
# ============================================================================


# ============================================================================
# UNKNOWN IS AN EPISTEMIC STATE
# ============================================================================
#
# "Epistemic" refers to knowledge.
#
#
# An UNKNOWN state means:
#
#
#       Agent 11 currently does not know enough
#       to establish the required fact.
#
#
# ============================================================================
#
# Example:
#
#
#       Kubernetes API
#           times out
#
#
# Agent 11 may be unable to establish service health.
#
#
# Correct:
#
#
#       ServiceState.UNKNOWN
#
#
# Incorrect:
#
#
#       ServiceState.UNAVAILABLE
#
#
# because the API timeout did not prove the service was down.
#
#
# ============================================================================
#
#
#       OBSERVER FAILURE
#           !=
#       OBSERVED RESOURCE FAILURE
#
#
# ============================================================================


# ============================================================================
# NETWORK EXAMPLE
# ============================================================================
#
# Suppose:
#
#
#       private-link-a
#           =
#       UNAVAILABLE
#
#
#       vpn-a
#           =
#       UNKNOWN
#
#
# We know:
#
#
#       private-link-a is unavailable
#
#
# We do NOT know:
#
#
#       vpn-a is unavailable
#
#
# ============================================================================
#
# Candidate routing must fail closed because no usable path has been
# established.
#
#
# But the correct candidate rejection is:
#
#
#       UNKNOWN
#
#
# not:
#
#
#       NETWORK_UNAVAILABLE
#
#
# ============================================================================
#
#
#       FAIL CLOSED
#           !=
#       INVENT CERTAINTY
#
#
# ============================================================================


# ============================================================================
# NEGATIVE KNOWLEDGE REQUIRES EVIDENCE
# ============================================================================
#
# This principle generalizes well beyond Agent 11.
#
#
# To say:
#
#
#       X IS UNAVAILABLE
#
#
# requires evidence supporting that negative conclusion.
#
#
# Merely failing to establish:
#
#
#       X IS AVAILABLE
#
#
# does not prove:
#
#
#       X IS UNAVAILABLE
#
#
# ============================================================================
#
#
#       NOT PROVEN TRUE
#           !=
#       PROVEN FALSE
#
#
# ============================================================================
#
# This distinction appears throughout:
#
#
#       distributed systems
#
#       monitoring
#
#       security
#
#       fault detection
#
#       consensus
#
#       AI reasoning
#
#       policy evaluation
#
#
# ============================================================================


# ============================================================================
# FAIL CLOSED
# !=
# CATCH EVERY EXCEPTION
# ============================================================================
#
# This is one of the most important security-engineering lessons in Part II.
#
#
# "Fail closed" does NOT mean:
#
#
#       try:
#           ...
#       except Exception:
#           deny_everything()
#
#
# ============================================================================
#
# Consider:
#
#
#       try:
#           return self.evaluate(...)
#
#       except Exception:
#           return RoutingCandidate(
#               status=REJECTED,
#               rejection_reason=UNKNOWN,
#           )
#
#
# This looks conservative.
#
#
# It is actually dangerous.
#
#
# Why?
#
#
# Because:
#
#
#       TypeError
#
#       AttributeError
#
#       broken imports
#
#       programming defects
#
#       contradictory identities
#
#       corrupted integration wiring
#
#
# would all be transformed into:
#
#
#       legitimate-looking routing outcomes
#
#
# ============================================================================
#
#
#       BUG
#           ->
#       SECURITY DECISION
#
#
# is NOT robustness.
#
#
# ============================================================================


# ============================================================================
# PROGRAMMING ERRORS SHOULD ESCAPE
# ============================================================================
#
# Domain uncertainty should be modeled explicitly.
#
#
# Example:
#
#
#       ServiceState.UNKNOWN
#
#
# should produce:
#
#
#       REJECTED / UNKNOWN
#
#
# ============================================================================
#
# But:
#
#
#       AttributeError
#
#
# caused by broken code should normally escape.
#
#
# ============================================================================
#
#
#       DOMAIN UNCERTAINTY
#           !=
#       PROGRAMMING ERROR
#
#
# ============================================================================
#
# This allows:
#
#
#       tests
#
#       telemetry
#
#       exception handling
#
#       incident response
#
#
# to correctly identify a software defect.
#
#
# ============================================================================


# ============================================================================
# PYDANTIC LESSON
#
# MODEL VALIDITY != SYSTEM VALIDITY
# ============================================================================
#
# Consider three individually valid Pydantic objects:
#
#
#       AIService
#
#       PolicyDecision
#
#       NetworkAssessmentResult
#
#
# Each may successfully execute:
#
#
#       model_validate(...)
#
#
# That proves:
#
#
#       the object satisfies its own schema and invariants
#
#
# It does NOT prove:
#
#
#       the three objects belong together
#
#
# ============================================================================
#
#
#       LOCAL VALIDITY
#           !=
#       RELATIONAL VALIDITY
#
#
# ============================================================================


# ============================================================================
# THREE LEVELS OF VALIDATION
# ============================================================================
#
# Agent 11 is beginning to expose three useful levels.
#
#
# LEVEL 1
# -------
#
# MODEL VALIDATION
#
#
# Example:
#
#
#       AIService
#
#
# validates:
#
#
#       its own fields
#
#       its own types
#
#       its own internal invariants
#
#
# ============================================================================
#
# LEVEL 2
# -------
#
# AGGREGATE VALIDATION
#
#
# Example:
#
#
#       NetworkAssessmentResult
#
#
# validates relationships among:
#
#
#       expected paths
#
#       path evidence
#
#       path assessments
#
#
# ============================================================================
#
# LEVEL 3
# -------
#
# CROSS-DOMAIN JOIN VALIDATION
#
#
# Example:
#
#
#       CandidateEvaluator
#
#
# validates relationships created when:
#
#
#       service facts
#
#       policy facts
#
#       capability facts
#
#       service-health facts
#
#       network facts
#
#
# are joined for routing.
#
#
# ============================================================================
#
#
#       MODEL
#           validates itself.
#
#
#       AGGREGATE
#           validates relationships
#           among its members.
#
#
#       JOIN POINT
#           validates relationships
#           among independently produced
#           domain facts.
#
#
# ============================================================================


# ============================================================================
# OWNERSHIP MATTERS
# ============================================================================
#
# There is an important architectural question:
#
#
#       WHERE SHOULD A VALIDATION RULE LIVE?
#
#
# ============================================================================
#
# A useful answer is:
#
#
#       AS CLOSE AS POSSIBLE
#       TO THE DOMAIN THAT OWNS THE INVARIANT.
#
#
# ============================================================================


# ============================================================================
# EXAMPLE:
#
# NETWORK INTERNAL INVARIANT
# ============================================================================
#
# This relationship:
#
#
#       path.destination_id
#           ==
#       NetworkAssessmentResult.destination_id
#
#
# belongs fundamentally to:
#
#
#       NETWORK
#
#
# because both identities are members of the network aggregate.
#
#
# Therefore the mature implementation should validate this in:
#
#
#       models/network/assessment.py
#
#
# ============================================================================
#
# CandidateEvaluator should not permanently become the repair shop for
# malformed network aggregates.
#
#
# ============================================================================


# ============================================================================
# EXAMPLE:
#
# CROSS-DOMAIN INVARIANT
# ============================================================================
#
# This relationship:
#
#
#       AIService.routing_domain
#           ==
#       PolicyDecision.routing_domain
#
#
# is different.
#
#
# AIService does not own PolicyDecision.
#
#
# PolicyDecision does not own AIService.
#
#
# Their relationship exists because candidate evaluation joined them.
#
#
# Therefore:
#
#
#       CandidateEvaluator
#
#
# is an appropriate place to validate that relationship.
#
#
# ============================================================================
#
#
#       OWN THE VALIDATION
#       WHERE THE RELATIONSHIP
#       COMES INTO EXISTENCE.
#
#
# ============================================================================


# ============================================================================
# DO NOT VALIDATE RELATIONSHIPS WE CANNOT PROVE
# ============================================================================
#
# This is equally important.
#
#
# CandidateEvaluator currently receives:
#
#
#       AIService.service_id
#
#
# and:
#
#
#       NetworkAssessmentResult.destination_id
#
#
# It may be tempting to write:
#
#
#       if service.service_id != network_assessment.destination_id:
#           raise ValueError(...)
#
#
# DO NOT DO THIS.
#
#
# ============================================================================
#
# We have not established that:
#
#
#       SERVICE IDENTITY
#
#
# and:
#
#
#       NETWORK DESTINATION IDENTITY
#
#
# use the same namespace.
#
#
# ============================================================================
#
#
#       SIMILAR LOOKING IDENTIFIERS
#           !=
#       SAME DOMAIN IDENTITY
#
#
# ============================================================================


# ============================================================================
# FUTURE IDENTITY CHAIN
# ============================================================================
#
# The mature architecture may eventually establish:
#
#
#       AIModel
#           |
#           v
#       AIService
#           |
#           v
#       Deployment
#           |
#           v
#       NetworkEndpoint
#           |
#           v
#       destination_id
#
#
# ============================================================================
#
# Then an explicit mapping can prove:
#
#
#       this service
#
#           ->
#
#       this deployment
#
#           ->
#
#       this endpoint
#
#           ->
#
#       this network destination
#
#
# ============================================================================
#
# Until that relationship exists:
#
#
#       DO NOT GUESS IT.
#
#
# ============================================================================


# ============================================================================
# STRING EQUALITY IS NOT ARCHITECTURE
# ============================================================================
#
# Suppose:
#
#
#       service.service_id
#           =
#       "company-llm-east"
#
#
# and:
#
#
#       network.destination_id
#           =
#       "company-llm-east"
#
#
# The strings happen to match.
#
#
# That does NOT prove that:
#
#
#       AI service identity
#
#
# and:
#
#
#       network destination identity
#
#
# are intentionally the same concept.
#
#
# ============================================================================
#
#
#       MATCHING STRINGS
#           !=
#       PROVEN DOMAIN RELATIONSHIP
#
#
# ============================================================================
#
# Explicit mappings beat accidental naming conventions.
#
#
# ============================================================================


# ============================================================================
# CAPABILITY bool
# ============================================================================
#
# Part II retains:
#
#
#       capability_supported: bool
#
#
# ============================================================================
#
# Why is bool acceptable here while UNKNOWN is so important elsewhere?
#
#
# Because current capability evaluation operates against:
#
#
#       declared registered model capabilities
#
#
# ModelRouter asks:
#
#
#       "Does this registered model contract satisfy
#        the requested capability requirement?"
#
#
# ============================================================================
#
# Under that contract:
#
#
#       True
#
# means:
#
#
#       declared requirement satisfied
#
#
# and:
#
#
#       False
#
# means:
#
#
#       declared requirement not satisfied
#
#
# ============================================================================
#
# If future capability discovery becomes dynamic or uncertain, bool may no
# longer be sufficient.
#
#
# At that point:
#
#
#       SUPPORTED
#
#       UNSUPPORTED
#
#       UNKNOWN
#
#
# may earn existence.
#
#
# ============================================================================
#
#
#       MODEL THE UNCERTAINTY
#       WHEN THE DOMAIN
#       ACTUALLY CONTAINS UNCERTAINTY.
#
#
# ============================================================================


# ============================================================================
# REJECTION PRECEDENCE STILL BEGINS AFTER COHERENCE
# ============================================================================
#
# Part I established:
#
#
#       1. POLICY
#
#       2. CAPABILITY
#
#       3. SERVICE
#
#       4. NETWORK
#
#
# Part II does NOT change that.
#
#
# It adds:
#
#
#       STAGE 0
#           RELATIONSHIP INTEGRITY
#
#
# ============================================================================
#
# Therefore:
#
#
#       RELATIONSHIP INTEGRITY
#           |
#           v
#       POLICY
#           |
#           v
#       CAPABILITY
#           |
#           v
#       SERVICE
#           |
#           v
#       NETWORK
#
#
# ============================================================================


# ============================================================================
# RELATIONSHIP ERRORS DO NOT PARTICIPATE IN REJECTION PRECEDENCE
# ============================================================================
#
# Suppose:
#
#
#       service.routing_domain
#           =
#       COMPANY_CLOUD_LLM
#
#
#       policy.routing_domain
#           =
#       EXTERNAL_FM
#
#
#       policy.status
#           =
#       DENY
#
#
# ============================================================================
#
# We do NOT return:
#
#
#       POLICY_DENIED
#
#
# because we do not possess a coherent policy decision for:
#
#
#       COMPANY_CLOUD_LLM
#
#
# ============================================================================
#
# The correct result is:
#
#
#       relationship validation failure
#
#
# ============================================================================
#
#
#       FIRST PROVE
#       THE DECISION BELONGS HERE.
#
#
#       THEN INTERPRET
#       THE DECISION.
#
#
# ============================================================================


# ============================================================================
# SECURITY CONSEQUENCE
# ============================================================================
#
# Imagine the opposite mistake:
#
#
#       service
#           =
#       EXTERNAL_FM
#
#
# but CandidateEvaluator accidentally receives:
#
#
#       policy decision
#           =
#       COMPANY_CLOUD_LLM / ALLOW
#
#
# ============================================================================
#
# If routing checks only:
#
#
#       policy.status == ALLOW
#
#
# without checking:
#
#
#       policy.routing_domain
#
#
# Agent 11 could incorrectly authorize the external service.
#
#
# ============================================================================
#
# This is why relationship integrity is not merely:
#
#
#       "nice validation"
#
#
# It is part of:
#
#
#       SECURITY CORRECTNESS
#
#
# ============================================================================


# ============================================================================
# IDENTITY IS A SECURITY PROPERTY
# ============================================================================
#
# Security decisions are meaningful only when the decision is attached to
# the correct resource.
#
#
# ============================================================================
#
#
#       ALLOW
#
#
# without:
#
#
#       ALLOW WHAT?
#
#
# is incomplete.
#
#
# ============================================================================
#
# Likewise:
#
#
#       HEALTHY
#
#
# requires:
#
#
#       HEALTHY WHAT?
#
#
# ============================================================================
#
# And:
#
#
#       REACHABLE
#
#
# requires:
#
#
#       REACHABLE FROM WHERE
#       TO WHERE?
#
#
# ============================================================================
#
#
#       SECURITY DECISIONS
#       REQUIRE IDENTITY.
#
#
# ============================================================================


# ============================================================================
# UNKNOWN MUST REMAIN USEFUL
# ============================================================================
#
# Because we do NOT dump programming errors and relationship failures into
# UNKNOWN, the UNKNOWN rejection reason retains meaning.
#
#
# It tells us:
#
#
#       "A legitimate required fact could not currently
#        be established strongly enough for routing."
#
#
# ============================================================================
#
# That makes telemetry useful.
#
#
# If UNKNOWN contained:
#
#
#       network observation failure
#
#       service observation failure
#
#       policy indeterminacy
#
#       programmer typo
#
#       wrong policy object
#
#       wrong destination
#
#       malformed aggregate
#
#       broken import
#
#
# then UNKNOWN would mean almost nothing.
#
#
# ============================================================================
#
#
#       A CATEGORY THAT MEANS EVERYTHING
#       EVENTUALLY MEANS NOTHING.
#
#
# ============================================================================


# ============================================================================
# PART II TEST MATRIX
# ============================================================================
#
# These tests supplement the Part I viability tests.
#
#
# ---------------------------------------------------------------------------
# TEST 1
#
# MATCHING SERVICE/POLICY DOMAIN
# ---------------------------------------------------------------------------
#
#
#       service.routing_domain
#           =
#       COMPANY_CLOUD_LLM
#
#
#       policy.routing_domain
#           =
#       COMPANY_CLOUD_LLM
#
#
# Expected:
#
#
#       relationship validation passes
#
#
# ---------------------------------------------------------------------------
# TEST 2
#
# MISMATCHED SERVICE/POLICY DOMAIN
# ---------------------------------------------------------------------------
#
#
#       service.routing_domain
#           =
#       COMPANY_CLOUD_LLM
#
#
#       policy.routing_domain
#           =
#       EXTERNAL_FM
#
#
# Expected:
#
#
#       ValueError
#
#
# NOT:
#
#
#       UNKNOWN
#
#
# NOT:
#
#
#       POLICY_DENIED
#
#
# ---------------------------------------------------------------------------
# TEST 3
#
# MATCHING DOMAIN + POLICY DENY
# ---------------------------------------------------------------------------
#
#
#       service.routing_domain
#           =
#       COMPANY_CLOUD_LLM
#
#
#       policy.routing_domain
#           =
#       COMPANY_CLOUD_LLM
#
#
#       policy.status
#           =
#       DENY
#
#
# Expected:
#
#
#       REJECTED
#
#       POLICY_DENIED
#
#
# This proves:
#
#
#       coherent negative decision
#
#           !=
#
#       relationship failure
#
#
# ---------------------------------------------------------------------------
# TEST 4
#
# POLICY INDETERMINATE
# ---------------------------------------------------------------------------
#
#
#       matching routing domains
#
#       policy.status = INDETERMINATE
#
#
# Expected:
#
#
#       REJECTED
#
#       UNKNOWN
#
#
# ---------------------------------------------------------------------------
# TEST 5
#
# SERVICE UNKNOWN
# ---------------------------------------------------------------------------
#
#
#       coherent inputs
#
#       service_state = UNKNOWN
#
#
# Expected:
#
#
#       REJECTED
#
#       UNKNOWN
#
#
# ---------------------------------------------------------------------------
# TEST 6
#
# NETWORK UNKNOWN
# ---------------------------------------------------------------------------
#
#
#       private-link-a = UNAVAILABLE
#
#       vpn-a = UNKNOWN
#
#
# Expected:
#
#
#       REJECTED
#
#       UNKNOWN
#
#
# ---------------------------------------------------------------------------
# TEST 7
#
# NETWORK CONCLUSIVELY UNAVAILABLE
# ---------------------------------------------------------------------------
#
#
#       private-link-a = UNAVAILABLE
#
#       vpn-a = UNAVAILABLE
#
#
# Expected:
#
#
#       REJECTED
#
#       NETWORK_UNAVAILABLE
#
#
# ---------------------------------------------------------------------------
# TEST 8
#
# MALFORMED EXPECTED PATH RELATIONSHIP
# ---------------------------------------------------------------------------
#
#
# NetworkAssessmentResult:
#
#
#       source_id
#           =
#       agent11-prod
#
#
#       destination_id
#           =
#       company-llm
#
#
# contained expected path:
#
#
#       source_id
#           =
#       agent11-prod
#
#
#       destination_id
#           =
#       external-fm
#
#
# Expected:
#
#
#       ValueError
#
#
# NOT:
#
#
#       NETWORK_UNAVAILABLE
#
#
# NOT:
#
#
#       UNKNOWN
#
#
# ---------------------------------------------------------------------------
# TEST 9
#
# MALFORMED PATH EVIDENCE RELATIONSHIP
# ---------------------------------------------------------------------------
#
#
# Outer assessment destination:
#
#
#       company-llm
#
#
# Evidence destination:
#
#
#       unrelated-service
#
#
# Expected:
#
#
#       ValueError
#
#
# ---------------------------------------------------------------------------
# TEST 10
#
# MALFORMED PATH ASSESSMENT RELATIONSHIP
# ---------------------------------------------------------------------------
#
#
# Outer source:
#
#
#       agent11-prod
#
#
# Contained assessment source:
#
#
#       agent11-dev
#
#
# Expected:
#
#
#       ValueError
#
#
# ---------------------------------------------------------------------------
# TEST 11
#
# PROGRAMMING ERROR
# ---------------------------------------------------------------------------
#
#
# Simulate an unexpected programming exception.
#
#
# Expected:
#
#
#       exception escapes
#
#
# NOT:
#
#
#       REJECTED / UNKNOWN
#
#
# ---------------------------------------------------------------------------
# TEST 12
#
# REJECTION PRECEDENCE AFTER COHERENCE
# ---------------------------------------------------------------------------
#
#
# coherent relationship
#
# policy = DENY
#
# capability = False
#
# service = UNAVAILABLE
#
# network = UNAVAILABLE
#
#
# Expected:
#
#
#       REJECTED
#
#       POLICY_DENIED
#
#
# ---------------------------------------------------------------------------
# TEST 13
#
# WRONG POLICY DOMAIN + POLICY DENY
# ---------------------------------------------------------------------------
#
#
# service domain:
#
#       COMPANY_CLOUD_LLM
#
#
# policy domain:
#
#       EXTERNAL_FM
#
#
# policy status:
#
#       DENY
#
#
# Expected:
#
#
#       ValueError
#
#
# NOT:
#
#
#       POLICY_DENIED
#
#
# because the DENY does not belong to this candidate.
#
#
# ---------------------------------------------------------------------------
# TEST 14
#
# WRONG POLICY DOMAIN + POLICY ALLOW
# ---------------------------------------------------------------------------
#
#
# service domain:
#
#       EXTERNAL_FM
#
#
# policy domain:
#
#       COMPANY_CLOUD_LLM
#
#
# policy status:
#
#       ALLOW
#
#
# Expected:
#
#
#       ValueError
#
#
# This is especially important because blindly accepting the ALLOW could
# create an authorization defect.
#
#
# ============================================================================


# ============================================================================
# PART II FINAL INVARIANTS
# ============================================================================
#
#
# VALIDATION
# ----------
#
#       VALID FACT
#           !=
#       VALID RELATIONSHIP
#
#
#       OBJECT VALIDITY
#           !=
#       CROSS-OBJECT COHERENCE
#
#
#       TYPE CORRECT
#           !=
#       RELATIONSHIP CORRECT
#
#
#       LOCAL VALIDITY
#           !=
#       RELATIONAL VALIDITY
#
#
# ---------------------------------------------------------------------------
# EPISTEMICS
# ---------------------------------------------------------------------------
#
#
#       UNKNOWN
#           !=
#       UNAVAILABLE
#
#
#       UNKNOWN
#           !=
#       CONTRADICTION
#
#
#       UNKNOWN
#           !=
#       BROKEN CODE
#
#
#       NOT PROVEN TRUE
#           !=
#       PROVEN FALSE
#
#
#       FAIL CLOSED
#           !=
#       INVENT CERTAINTY
#
#
# ---------------------------------------------------------------------------
# ERRORS
# ---------------------------------------------------------------------------
#
#
#       RELATIONSHIP FAILURE
#           !=
#       ROUTING REJECTION
#
#
#       BAD RELATIONSHIP
#           !=
#       NEGATIVE DOMAIN DECISION
#
#
#       DOMAIN UNCERTAINTY
#           !=
#       PROGRAMMING ERROR
#
#
#       FAIL CLOSED
#           !=
#       CATCH EVERYTHING
#
#
# ---------------------------------------------------------------------------
# IDENTITY
# ---------------------------------------------------------------------------
#
#
#       SECURITY DECISIONS
#       REQUIRE IDENTITY
#
#
#       SERVICE ID
#           !=
#       NETWORK DESTINATION ID
#
#
#       MATCHING STRINGS
#           !=
#       PROVEN DOMAIN RELATIONSHIP
#
#
#       SIMILAR IDENTIFIERS
#           !=
#       SAME DOMAIN IDENTITY
#
#
# ---------------------------------------------------------------------------
# OWNERSHIP
# ---------------------------------------------------------------------------
#
#
#       VALIDATE AN INVARIANT
#       AS CLOSE AS POSSIBLE
#       TO THE DOMAIN THAT OWNS IT
#
#
#       OWN THE VALIDATION
#       WHERE THE RELATIONSHIP
#       COMES INTO EXISTENCE
#
#
# ---------------------------------------------------------------------------
# ROUTING
# ---------------------------------------------------------------------------
#
#
#       COHERENCE BEFORE VIABILITY
#
#
#       FIRST PROVE
#       THE DECISION BELONGS HERE
#
#
#       THEN INTERPRET
#       THE DECISION
#
#
# ============================================================================


# ============================================================================
# PART II FINAL CONTRACT
# ============================================================================
#
#
#       CandidateEvaluator
#
#       MUST NOT ASK:
#
#
#           "IS THIS SERVICE VIABLE?"
#
#
#       UNTIL IT CAN FIRST ESTABLISH:
#
#
#           "THE FACTS I AM ABOUT TO USE
#            COHERENTLY DESCRIBE
#            THIS CANDIDATE EVALUATION."
#
#
# ============================================================================
#
# WHY?
#
#
# Because:
#
#
#       CORRECT REASONING
#
#
# performed over:
#
#
#       INCORRECTLY JOINED FACTS
#
#
# still produces:
#
#
#       AN INCORRECT SYSTEM DECISION.
#
#
# ============================================================================
#
#
#       VALIDATION DOES NOT END
#       WHEN THE OBJECT CONSTRUCTOR
#       RETURNS SUCCESSFULLY.
#
#
# ============================================================================
# END COMPLETE PART II
# ============================================================================

# ============================================================================
# routing/candidate_evaluator.py
#
# COMPLETE PART III-A
#
# POLICY-COMPLIANT PATHS
# AND
# WORKLOAD SUITABILITY
# ============================================================================
#
# PURPOSE
# -------
#
# Parts I and II established:
#
#
#       PART I
#       ------
#
#       PERMITTED
#           AND
#       CAPABLE
#           AND
#       SERVICE OPERATIONAL
#           AND
#       NETWORK OPERATIONAL
#           =
#       VIABLE
#
#
#       PART II
#       -------
#
#       COHERENCE BEFORE VIABILITY
#
#
# Part III-A introduces two future pressures:
#
#
#       1. PATH-SPECIFIC POLICY
#
#       2. WORKLOAD-SPECIFIC SUITABILITY
#
#
# These pressures must NOT cause Agent 11 to corrupt the meaning of:
#
#
#       policy state
#
#       service state
#
#       network state
#
#
# ============================================================================
# CENTRAL PART III-A RULE
# ============================================================================
#
#
#       OPERATIONAL STATE
#           !=
#       AUTHORIZATION
#           !=
#       WORKLOAD SUITABILITY
#
#
# ============================================================================
#
# These dimensions may interact when CandidateEvaluator determines
# viability.
#
# But they remain independent facts.
#
#
# ============================================================================
# EXAMPLE
# ============================================================================
#
#
#       Network path:
#
#           AVAILABLE
#
#
#       Path policy:
#
#           DENY
#
#
#       Workload suitability:
#
#           SUITABLE
#
#
# Candidate result:
#
#
#       NOT VIABLE
#
#
# But the underlying facts remain:
#
#
#       AVAILABLE
#
#       DENIED
#
#       SUITABLE
#
#
# ============================================================================
#
# CandidateEvaluator does NOT rewrite:
#
#
#       AVAILABLE
#
#
# as:
#
#
#       UNAVAILABLE
#
#
# merely because policy prohibits the path.
#
#
# ============================================================================
#
#
#       FAIL CLOSED
#           !=
#       FALSIFY STATE
#
#
# ============================================================================


# ============================================================================
# SECTION 1
#
# WHY ROUTING-DOMAIN POLICY WILL EVENTUALLY BE INSUFFICIENT
# ============================================================================
#
# Current SEIR-I policy primarily answers:
#
#
#       "May this request use this AI routing domain?"
#
#
# Example:
#
#
#       classification = E9
#
#
#       routing_domain = COMPANY_ONPREM_LLM
#
#
#       policy = ALLOW
#
#
# ============================================================================
#
# That is sufficient for the current architecture.
#
#
# But eventually:
#
#
#       DESTINATION AUTHORIZED
#
#
# may not imply:
#
#
#       EVERY NETWORK PATH TO DESTINATION AUTHORIZED
#
#
# ============================================================================
#
#
#       DESTINATION AUTHORIZED
#           !=
#       EVERY PATH AUTHORIZED
#
#
# ============================================================================


# ============================================================================
# EXAMPLE:
#
# SAME DESTINATION
# DIFFERENT NETWORK PATHS
# ============================================================================
#
# Imagine:
#
#
#                   Agent 11
#                      |
#          +-----------+-----------+
#          |                       |
#          v                       v
#    PRIVATE_LINK               INTERNET
#          |                       |
#          +-----------+-----------+
#                      |
#                      v
#            COMPANY_ONPREM_LLM
#
#
# ============================================================================
#
# Operational network truth:
#
#
#       PRIVATE_LINK
#           =
#       UNAVAILABLE
#
#
#       INTERNET
#           =
#       AVAILABLE
#
#
# ============================================================================
#
# Current network assessment has done its job correctly.
#
#
# It has described operational reality.
#
#
# ============================================================================


# ============================================================================
# NOW ADD POLICY
# ============================================================================
#
# Suppose the request contains E9 data.
#
#
# Future path-specific policy may establish:
#
#
#       E9
#           x
#       COMPANY_ONPREM_LLM
#           x
#       PRIVATE_LINK
#           ->
#       ALLOW
#
#
# while:
#
#
#       E9
#           x
#       COMPANY_ONPREM_LLM
#           x
#       INTERNET
#           ->
#       DENY
#
#
# ============================================================================
#
# We now have:
#
#
#       PRIVATE_LINK
#
#           operational state:
#               UNAVAILABLE
#
#           policy:
#               ALLOW
#
#
#       INTERNET
#
#           operational state:
#               AVAILABLE
#
#           policy:
#               DENY
#
#
# ============================================================================
#
# There is:
#
#
#       an operational path
#
#
# and:
#
#
#       an authorized path
#
#
# But there is NOT:
#
#
#       an operational authorized path
#
#
# ============================================================================
#
#
#       AVAILABLE PATH EXISTS
#
#           !=
#
#       PERMITTED AVAILABLE PATH EXISTS
#
#
# ============================================================================


# ============================================================================
# THE CORRECT CANDIDATE CONCLUSION
# ============================================================================
#
#
#       PRIVATE_LINK
#           ALLOWED
#           BUT UNAVAILABLE
#
#
#       INTERNET
#           AVAILABLE
#           BUT DENIED
#
#
# Therefore:
#
#
#       NO POLICY-COMPLIANT
#       OPERATIONAL PATH EXISTS
#
#
# Therefore:
#
#
#       CANDIDATE NOT VIABLE
#
#
# ============================================================================
#
# Notice what we did NOT say:
#
#
#       "the network is unavailable"
#
#
# That would be false.
#
#
# Internet connectivity is available.
#
#
# ============================================================================
#
# Notice what we also did NOT say:
#
#
#       "the destination is denied"
#
#
# That would also be false.
#
#
# The destination may be permitted through an approved path.
#
#
# ============================================================================
#
#
#       CANDIDATE NOT VIABLE
#
# does not require:
#
#
#       NETWORK UNAVAILABLE
#
# or:
#
#       DESTINATION DENIED
#
#
# ============================================================================


# ============================================================================
# THIS IS WHY DOMAIN FACTS MUST REMAIN INDEPENDENT
# ============================================================================
#
# If we collapse policy and network state together, we lose the ability to
# describe the actual system.
#
#
# Bad model:
#
#
#       internet_path = UNAVAILABLE
#
#
# because policy denied it.
#
#
# ============================================================================
#
# Good model:
#
#
#       internet_path.state
#           =
#       AVAILABLE
#
#
#       internet_path.policy
#           =
#       DENY
#
#
# ============================================================================
#
#
#       NETWORK DESCRIBES
#       WHAT CAN BE REACHED.
#
#
#       POLICY DESCRIBES
#       WHAT MAY BE USED.
#
#
# ============================================================================


# ============================================================================
# NETWORK MUST NOT BECOME POLICY-AWARE
# ============================================================================
#
# NetworkOrchestrator should NOT begin returning:
#
#
#       NetworkPathState.POLICY_DENIED
#
#
# ============================================================================
#
# Why?
#
#
# Because:
#
#
#       POLICY_DENIED
#
#
# is not a network condition.
#
#
# ============================================================================
#
# The path may be:
#
#
#       electrically functional
#
#       routed
#
#       reachable
#
#       low latency
#
#       healthy
#
#
# and still:
#
#
#       prohibited for this request
#
#
# ============================================================================
#
#
#       NETWORK STATE
#           !=
#       POLICY STATE
#
#
# ============================================================================


# ============================================================================
# POLICY MUST NOT BECOME NETWORK-AWARENESS
# ============================================================================
#
# Likewise, the policy engine should not rewrite:
#
#
#       ALLOW
#
#
# into:
#
#
#       DENY
#
#
# merely because the approved private path is currently down.
#
#
# ============================================================================
#
# Policy may still correctly say:
#
#
#       PRIVATE_LINK
#           =
#       ALLOW
#
#
# while network correctly says:
#
#
#       PRIVATE_LINK
#           =
#       UNAVAILABLE
#
#
# ============================================================================
#
#
#       AUTHORIZED BUT BROKEN
#
#
# is a perfectly legitimate system state.
#
#
# ============================================================================


# ============================================================================
# FOUR IMPORTANT COMBINATIONS
# ============================================================================
#
#
#       PATH AVAILABLE
#       + POLICY ALLOW
#       ----------------
#       potentially usable
#
#
#       PATH AVAILABLE
#       + POLICY DENY
#       ----------------
#       operational but prohibited
#
#
#       PATH UNAVAILABLE
#       + POLICY ALLOW
#       ----------------
#       authorized but unusable
#
#
#       PATH UNAVAILABLE
#       + POLICY DENY
#       ----------------
#       prohibited and unusable
#
#
# ============================================================================
#
# All four combinations are meaningful.
#
#
# A good domain model must be able to represent all four without lying.
#
#
# ============================================================================


# ============================================================================
# FUTURE POLICY-COMPLIANT PATH EVALUATION
# ============================================================================
#
# CandidateEvaluator should NOT eventually contain:
#
#
#       if classification == DataClassificationLevel.E9:
#
#           if path.path_type is NetworkPathType.INTERNET:
#
#               reject()
#
#
# ============================================================================
#
# That would place organizational policy implementation inside:
#
#
#       routing/
#
#
# ============================================================================
#
#
#       ROUTING CONSUMES POLICY.
#
#
#       ROUTING DOES NOT INVENT POLICY.
#
#
# ============================================================================


# ============================================================================
# BETTER FUTURE SHAPE
# ============================================================================
#
# Future architecture should resemble:
#
#
#       DATA CLASSIFICATION
#               |
#               v
#       ORGANIZATION POLICY
#               |
#               v
#       USER POLICY
#               |
#               v
#       PATH POLICY EVALUATION
#               |
#               v
#       PATH POLICY DECISIONS
#
#
# while independently:
#
#
#       NETWORK OBSERVATION
#               |
#               v
#       NETWORK ASSESSMENT
#               |
#               v
#       PATH OPERATIONAL STATES
#
#
# Then:
#
#
#       PATH POLICY DECISIONS
#               +
#       PATH OPERATIONAL STATES
#               |
#               v
#       POLICY-COMPLIANT
#       OPERATIONAL PATH SET
#
#
# ============================================================================
#
# CandidateEvaluator can consume the normalized conclusion.
#
#
# ============================================================================


# ============================================================================
# POSSIBLE FUTURE CONCEPT
#
# PolicyCompliantPathSet
# ============================================================================
#
# This is a conceptual future contract.
#
#
# DO NOT IMPLEMENT IT YET.
#
#
# Example:
#
#
# class PolicyCompliantPathSet(Agent11BaseModel):
#
#     source_id: str
#
#     destination_id: str
#
#     usable_path_ids: list[str]
#
#
# ============================================================================
#
# CandidateEvaluator would not need to understand:
#
#
#       why a path was allowed
#
#       why a path was denied
#
#       E7 / E8 / E9 rules
#
#       Internet policy
#
#       private-link requirements
#
#       contractual restrictions
#
#       residency restrictions
#
#
# It would ask something conceptually simple:
#
#
#       "Does at least one policy-compliant
#        operational path exist?"
#
#
# ============================================================================


# ============================================================================
# IMPORTANT:
#
# DO NOT CREATE PolicyCompliantPathSet YET
# ============================================================================
#
# We are documenting architectural pressure.
#
#
# We are NOT automatically creating another model because:
#
#
#       "we might need it someday."
#
#
# ============================================================================
#
#
#       FUTURE-AWARE
#           !=
#       FUTURE-BLOATED
#
#
# ============================================================================
#
# The model earns existence when actual path-specific policy behavior is
# implemented.
#
#
# ============================================================================


# ============================================================================
# PATH IDENTITY BECOMES CRITICAL
# ============================================================================
#
# Path-specific policy also explains why:
#
#
#       NetworkPathType
#
#
# alone is not enough.
#
#
# ============================================================================
#
# Suppose:
#
#
#       vpn-a
#           type = VPN
#
#
#       vpn-b
#           type = VPN
#
#
# One may be approved for E9 traffic.
#
#
# The other may not be.
#
#
# ============================================================================
#
#
#       PATH TYPE
#           !=
#       PATH INSTANCE
#
#
# ============================================================================
#
# Therefore:
#
#
#       path_id
#
#
# becomes an important durable identity.
#
#
# ============================================================================


# ============================================================================
# PATH POLICY ALSO EXPLAINS WHY BGP IS NOT A PATH TYPE
# ============================================================================
#
# BGP may provide evidence concerning:
#
#
#       how a destination prefix is learned
#
#
#       which next hop is selected
#
#
#       whether a route is present
#
#
# But:
#
#
#       BGP
#
#
# is not itself the policy-relevant connectivity mechanism in the same sense
# as:
#
#
#       INTERNET
#
#       VPN
#
#       PRIVATE_LINK
#
#       SD_WAN
#
#
# ============================================================================
#
#
#       ROUTING PROTOCOL
#           !=
#       NETWORK PATH TYPE
#
#
# ============================================================================
#
# CandidateEvaluator must never need to know:
#
#
#       AS_PATH
#
#       LOCAL_PREF
#
#       MED
#
#       NEXT_HOP
#
#       BGP communities
#
#
# Those belong below the normalized network assessment boundary.
#
#
# ============================================================================


# ============================================================================
# SECTION 2
#
# WORKLOAD SUITABILITY
# ============================================================================
#
# Part I intentionally established:
#
#
#       ServiceState.DEGRADED
#           ->
#       operationally usable
#
#
# and:
#
#
#       NetworkPathState.DEGRADED
#           ->
#       operationally usable
#
#
# ============================================================================
#
# This remains correct.
#
#
# But SEIR-II introduces another question:
#
#
#       "Operationally usable FOR WHAT?"
#
#
# ============================================================================


# ============================================================================
# DEGRADED IS A STATE
#
# NOT A UNIVERSAL DECISION
# ============================================================================
#
# Suppose:
#
#
#       service_state
#           =
#       DEGRADED
#
#
# That tells us:
#
#
#       the service remains operational
#
#       but some aspect of normal operation is impaired
#
#
# ============================================================================
#
# It does NOT tell us:
#
#
#       whether a specific workload should use it
#
#
# ============================================================================
#
#
#       DEGRADED
#           !=
#       UNSUITABLE
#
#
#       DEGRADED
#           !=
#       SUITABLE
#
#
# ============================================================================


# ============================================================================
# EXAMPLE:
#
# SAME DEGRADED SERVICE
# DIFFERENT WORKLOADS
# ============================================================================
#
# Service:
#
#
#       state
#           =
#       DEGRADED
#
#
# Suppose the degradation means:
#
#
#       reduced token throughput
#
#
# ============================================================================
#
# REQUEST A:
#
#
#       reasoning_level
#           =
#       LIGHT
#
#
#       estimated_tokens
#           =
#       2,000
#
#
# Result:
#
#
#       perhaps SUITABLE
#
#
# ============================================================================
#
# REQUEST B:
#
#
#       reasoning_level
#           =
#       HEAVY
#
#
#       estimated_tokens
#           =
#       500,000
#
#
# Result:
#
#
#       perhaps UNSUITABLE
#
#
# ============================================================================
#
# Same service.
#
# Same service state.
#
# Different workload relationship.
#
#
# ============================================================================
#
#
#       RESOURCE STATE
#           !=
#       REQUEST-RESOURCE SUITABILITY
#
#
# ============================================================================


# ============================================================================
# THIS IS A RELATIONSHIP
# ============================================================================
#
# Suitability is not purely a property of:
#
#
#       the request
#
#
# and not purely a property of:
#
#
#       the service
#
#
# ============================================================================
#
# It is a relationship:
#
#
#       REQUEST REQUIREMENTS
#               +
#       RESOURCE CONDITIONS
#               |
#               v
#       SUITABILITY
#
#
# ============================================================================
#
#
#       SUITABILITY
#       EXISTS BETWEEN THINGS.
#
#
# ============================================================================


# ============================================================================
# NETWORK SUITABILITY HAS THE SAME PROBLEM
# ============================================================================
#
# Suppose:
#
#
#       NetworkPathState.DEGRADED
#
#
# because:
#
#
#       latency increased
#
#       packet loss increased
#
#       available bandwidth decreased
#
#
# ============================================================================
#
# A small classification request may still work perfectly well.
#
#
# A massive multimodal reasoning request may not.
#
#
# ============================================================================
#
#
#       PATH OPERATIONAL
#           !=
#       PATH SUITABLE FOR EVERY WORKLOAD
#
#
# ============================================================================


# ============================================================================
# DO NOT PUT WORKLOAD POLICY INTO NetworkPathState
# ============================================================================
#
# Bad:
#
#
#       if reasoning_level is HEAVY:
#
#           degraded_path.state = UNAVAILABLE
#
#
# ============================================================================
#
# Why is this wrong?
#
#
# Because the path did not become unavailable.
#
#
# The relationship between:
#
#
#       this workload
#
#
# and:
#
#
#       this path condition
#
#
# became unsuitable.
#
#
# ============================================================================
#
# Correct conceptual facts:
#
#
#       path.state
#           =
#       DEGRADED
#
#
#       workload_suitability
#           =
#       UNSUITABLE
#
#
# ============================================================================
#
#
#       FAIL CLOSED
#           !=
#       REWRITE REALITY
#
#
# ============================================================================


# ============================================================================
# MEASUREMENTS ARE NOT SUITABILITY
# ============================================================================
#
# Future network evidence may include:
#
#
#       latency
#
#       jitter
#
#       packet loss
#
#       bandwidth
#
#       retransmissions
#
#
# Future service evidence may include:
#
#
#       token throughput
#
#       queue depth
#
#       inference latency
#
#       concurrency
#
#       capacity
#
#
# ============================================================================
#
# Those are measurements.
#
#
# They are not themselves suitability decisions.
#
#
# ============================================================================
#
#
#       MEASUREMENT
#           !=
#       ASSESSMENT
#
#
#       ASSESSMENT
#           !=
#       SUITABILITY
#
#
# ============================================================================


# ============================================================================
# EXAMPLE
# ============================================================================
#
#
#       latency
#           =
#       250 ms
#
#
# This number alone does not mean:
#
#
#       GOOD
#
#       BAD
#
#       SUITABLE
#
#       UNSUITABLE
#
#
# ============================================================================
#
# Whether 250 ms is acceptable depends on:
#
#
#       workload requirements
#
#       service expectations
#
#       policy
#
#       SLOs
#
#       application semantics
#
#
# ============================================================================
#
#
#       FACT
#           !=
#       INTERPRETATION
#
#
# ============================================================================


# ============================================================================
# THRESHOLDS ARE ALSO NOT POLICY
# ============================================================================
#
# Suppose:
#
#
#       latency <= 100 ms
#
#
# is required for a particular interactive workload.
#
#
# That threshold may contribute to suitability evaluation.
#
#
# It is still different from:
#
#
#       "E9 data may not traverse Internet paths."
#
#
# ============================================================================
#
#
#       PERFORMANCE THRESHOLD
#           !=
#       SECURITY POLICY
#
#
# ============================================================================


# ============================================================================
# POSSIBLE FUTURE SUITABILITY CONTRACT
# ============================================================================
#
# Again, conceptual only.
#
#
# DO NOT IMPLEMENT YET.
#
#
# Something like:
#
#
# class WorkloadSuitabilityStatus(Agent11Enum):
#
#     SUITABLE = "suitable"
#
#     UNSUITABLE = "unsuitable"
#
#     UNKNOWN = "unknown"
#
#
# ============================================================================
#
# A future evaluator might consume:
#
#
#       AIRequest
#
#       service operational facts
#
#       network operational facts
#
#
# and produce:
#
#
#       WorkloadSuitability
#
#
# ============================================================================
#
# CandidateEvaluator would consume the conclusion.
#
#
# ============================================================================


# ============================================================================
# WHY UNKNOWN WOULD MATTER HERE TOO
# ============================================================================
#
# Suppose:
#
#
#       service is DEGRADED
#
#
# but the telemetry required to determine whether that degradation affects
# the current workload is missing.
#
#
# ============================================================================
#
# We should not automatically claim:
#
#
#       UNSUITABLE
#
#
# ============================================================================
#
# We may instead have:
#
#
#       suitability
#           =
#       UNKNOWN
#
#
# ============================================================================
#
# Candidate routing may still fail closed.
#
#
# But:
#
#
#       UNKNOWN SUITABILITY
#           !=
#       PROVEN UNSUITABILITY
#
#
# ============================================================================
#
#
#       FAIL CLOSED
#           !=
#       FALSIFY STATE
#
#
# appears again.
#
#
# ============================================================================


# ============================================================================
# THREE DIFFERENT QUESTIONS
# ============================================================================
#
# As Agent 11 matures, these questions must remain separate.
#
#
# QUESTION 1
# ----------
#
#       "Is the resource operational?"
#
#
# Examples:
#
#
#       AVAILABLE
#
#       DEGRADED
#
#       UNAVAILABLE
#
#       UNKNOWN
#
#
# ============================================================================
#
# QUESTION 2
# ----------
#
#       "May this request use the resource/path?"
#
#
# Examples:
#
#
#       ALLOW
#
#       DENY
#
#       RESTRICT
#
#       INDETERMINATE
#
#
# ============================================================================
#
# QUESTION 3
# ----------
#
#       "Is this operational resource suitable
#        for this particular workload?"
#
#
# Examples:
#
#
#       SUITABLE
#
#       UNSUITABLE
#
#       UNKNOWN
#
#
# ============================================================================
#
#
#       OPERATION
#
#       AUTHORIZATION
#
#       SUITABILITY
#
#
# are three separate axes.
#
#
# ============================================================================


# ============================================================================
# WHY THIS MATTERS TO CandidateEvaluator
# ============================================================================
#
# CandidateEvaluator eventually becomes the place where these independently
# established conclusions are joined.
#
#
# Conceptually:
#
#
#       DESTINATION POLICY
#               |
#               v
#            ALLOW
#               |
#               |
#       CAPABILITY
#               |
#               v
#          SUPPORTED
#               |
#               |
#       SERVICE STATE
#               |
#               v
#          AVAILABLE
#               |
#               |
#       POLICY-COMPLIANT PATH
#               |
#               v
#            EXISTS
#               |
#               |
#       WORKLOAD SUITABILITY
#               |
#               v
#          SUITABLE
#               |
#               v
#            VIABLE
#
#
# ============================================================================
#
# CandidateEvaluator joins the conclusions.
#
#
# It does not become the subsystem that creates every conclusion.
#
#
# ============================================================================


# ============================================================================
# FUTURE VIABILITY EQUATION
# ============================================================================
#
# Current:
#
#
#       VIABLE
#           =
#       PERMITTED
#           AND
#       CAPABLE
#           AND
#       SERVICE_OPERATIONAL
#           AND
#       NETWORK_OPERATIONAL
#
#
# ============================================================================
#
# Future SEIR-II may conceptually refine this to:
#
#
#       VIABLE
#           =
#       DESTINATION_PERMITTED
#           AND
#       CAPABLE
#           AND
#       SERVICE_OPERATIONALLY_USABLE
#           AND
#       POLICY_COMPLIANT_OPERATIONAL_PATH_EXISTS
#           AND
#       WORKLOAD_SUITABLE
#
#
# ============================================================================
#
# Notice:
#
#
#       MORE PRECISE FACTS
#
#
# not:
#
#
#       ONE GIANT ROUTING SCORE
#
#
# ============================================================================


# ============================================================================
# HARD CONSTRAINTS STILL REMAIN HARD
# ============================================================================
#
# Suppose:
#
#
#       destination policy
#           =
#       ALLOW
#
#
#       capability
#           =
#       SUPPORTED
#
#
#       service
#           =
#       AVAILABLE
#
#
#       path
#           =
#       AVAILABLE
#
#
#       path policy
#           =
#       DENY
#
#
#       workload suitability
#           =
#       SUITABLE
#
#
# ============================================================================
#
# Candidate:
#
#
#       NOT VIABLE
#
#
# ============================================================================
#
# We do NOT calculate:
#
#
#       +100 destination allowed
#
#       +100 capability supported
#
#       +100 service available
#
#       +100 path available
#
#       -100 path denied
#
#       +100 workload suitable
#
#       ------------------------
#
#       +300
#
#
# therefore:
#
#
#       VIABLE!
#
#
# ============================================================================
#
# No.
#
#
# Chewbacca does not get to outvote the security policy because he collected
# enough bonus points elsewhere.
#
#
# ============================================================================
#
#
#       HARD CONSTRAINT
#           !=
#       WEIGHTED PREFERENCE
#
#
# ============================================================================


# ============================================================================
# FILTER FIRST
#
# OPTIMIZE SECOND
# ============================================================================
#
# Future architecture:
#
#
#                         ALL CANDIDATES
#                               |
#                               v
#                      DESTINATION POLICY
#                               |
#                               v
#                         CAPABILITY
#                               |
#                               v
#                     SERVICE USABILITY
#                               |
#                               v
#                  POLICY-COMPLIANT PATH
#                               |
#                               v
#                   WORKLOAD SUITABILITY
#                               |
#                               v
#                       VIABLE SET
#                               |
#                               v
#                        OPTIMIZATION
#                               |
#                               v
#                         SELECTION
#
#
# ============================================================================
#
#
#       FILTER FIRST.
#
#
#       OPTIMIZE SECOND.
#
#
# ============================================================================


# ============================================================================
# COST DOES NOT BELONG IN III-A VIABILITY
# ============================================================================
#
# Suppose:
#
#
#       external model
#
#           cost:
#               $0.0001
#
#           latency:
#               10 ms
#
#           quality:
#               spectacular
#
#           policy:
#               DENY
#
#
# ============================================================================
#
# It is not:
#
#
#       "an attractive candidate with a policy penalty."
#
#
# It is:
#
#
#       NOT A VIABLE CANDIDATE
#
#
# ============================================================================
#
#
#       DENIED != EXPENSIVE
#
#
#       DENIED != SLOW
#
#
#       DENIED != LOW SCORE
#
#
# ============================================================================


# ============================================================================
# MULTIPLE AVAILABLE PATHS
# ============================================================================
#
# Suppose:
#
#
#       private-link-a
#           AVAILABLE
#
#
#       vpn-a
#           AVAILABLE
#
#
#       internet-a
#           AVAILABLE
#
#
# ============================================================================
#
# Path policy:
#
#
#       private-link-a
#           ALLOW
#
#
#       vpn-a
#           ALLOW
#
#
#       internet-a
#           DENY
#
#
# ============================================================================
#
# CandidateEvaluator does NOT need to select:
#
#
#       private-link-a
#
# versus:
#
#       vpn-a
#
#
# merely to establish:
#
#
#       at least one policy-compliant operational path exists
#
#
# ============================================================================
#
#
#       EXISTENCE
#           !=
#       PATH SELECTION
#
#
# ============================================================================


# ============================================================================
# IMPORTANT FUTURE QUESTION:
#
# WHO SELECTS THE ACTUAL PATH?
# ============================================================================
#
# Agent 11 may eventually know that several compliant paths exist.
#
#
# That does not necessarily mean Agent 11 controls which physical path the
# network uses.
#
#
# ============================================================================
#
# The network may select forwarding through:
#
#
#       routing tables
#
#       ECMP
#
#       SD-WAN policy
#
#       BGP
#
#       operating-system routing
#
#       cloud networking
#
#
# ============================================================================
#
#
#       AI ROUTING SELECTION
#           !=
#       PACKET FORWARDING SELECTION
#
#
# ============================================================================


# ============================================================================
# THIS CREATES A FUTURE REALIZED-PATH PROBLEM
# ============================================================================
#
# Agent 11 may believe:
#
#
#       private-link-a is permitted
#
#
# while actual traffic unexpectedly realizes through:
#
#
#       internet-a
#
#
# ============================================================================
#
# That is not merely:
#
#
#       path unavailable
#
#
# It may be:
#
#
#       PATH DRIFT
#
#
# or:
#
#
#       EXPECTED PATH != REALIZED PATH
#
#
# ============================================================================
#
# We have already identified this architectural pressure.
#
#
# But:
#
#
#       RealizedNetworkPath
#
#
# has NOT yet earned implementation.
#
#
# ============================================================================
#
# Why?
#
#
# Because we do not yet possess reliable adapters capable of establishing
# realized forwarding semantics across:
#
#
#       cloud networks
#
#       VPNs
#
#       SD-WAN
#
#       BGP
#
#       ECMP
#
#
# ============================================================================
#
#
#       MODEL WHAT WE CAN PROVE.
#
#
#       DO NOT MODEL
#       WHAT WE MERELY WISH
#       WE COULD PROVE.
#
#
# ============================================================================


# ============================================================================
# EXPECTED PATH != REALIZED PATH
# ============================================================================
#
# This distinction will eventually matter for policy assurance.
#
#
# ============================================================================
#
# EXPECTED PATH
# -------------
#
#
#       "The architecture says this workload
#        should traverse this path."
#
#
# ============================================================================
#
# REALIZED PATH
# -------------
#
#
#       "The infrastructure evidence establishes
#        that this traffic actually traversed this path."
#
#
# ============================================================================
#
#
#       INTENDED CONNECTIVITY
#           !=
#       OBSERVED CONNECTIVITY
#
#
# ============================================================================


# ============================================================================
# NETWORK WORKING
# !=
# NETWORK WORKING AS INTENDED
# ============================================================================
#
# Example:
#
#
#       application request succeeds
#
#
# but:
#
#
#       traffic bypassed approved private connectivity
#
#
# ============================================================================
#
# Availability says:
#
#
#       success
#
#
# Policy assurance may say:
#
#
#       failure
#
#
# ============================================================================
#
#
#       NETWORK WORKING
#           !=
#       NETWORK WORKING AS INTENDED
#
#
# ============================================================================


# ============================================================================
# OBSERVABILITY REQUIREMENT
# ============================================================================
#
# As path-specific policy emerges, telemetry should eventually be able to
# explain:
#
#
#       which destination was considered
#
#       which paths were operational
#
#       which paths were authorized
#
#       which paths were unsuitable
#
#       whether a compliant operational path existed
#
#       why the candidate was rejected
#
#
# ============================================================================
#
# But CandidateEvaluator should not become the telemetry backend.
#
#
# It should produce structured decisions that telemetry can observe.
#
#
# ============================================================================
#
#
#       DECISION
#           !=
#       TELEMETRY TRANSPORT
#
#
# ============================================================================


# ============================================================================
# PART III-A FUTURE TEST MATRIX
# ============================================================================
#
# These are architecture-contract tests.
#
# Some cannot be implemented until the corresponding future domain contracts
# exist.
#
#
# ---------------------------------------------------------------------------
# TEST 1
#
# AVAILABLE + ALLOW
# ---------------------------------------------------------------------------
#
#
# Path:
#
#       AVAILABLE
#
#
# Path policy:
#
#       ALLOW
#
#
# Expected:
#
#
#       operationally policy-compliant
#
#
# ---------------------------------------------------------------------------
# TEST 2
#
# AVAILABLE + DENY
# ---------------------------------------------------------------------------
#
#
# Path:
#
#       AVAILABLE
#
#
# Path policy:
#
#       DENY
#
#
# Expected:
#
#
#       path remains AVAILABLE
#
#       path is not usable for this request
#
#
# ---------------------------------------------------------------------------
# TEST 3
#
# UNAVAILABLE + ALLOW
# ---------------------------------------------------------------------------
#
#
# Path:
#
#       UNAVAILABLE
#
#
# Path policy:
#
#       ALLOW
#
#
# Expected:
#
#
#       path remains authorized
#
#       path is not operationally usable
#
#
# ---------------------------------------------------------------------------
# TEST 4
#
# PRIVATE UNAVAILABLE
# INTERNET AVAILABLE
#
# PRIVATE ALLOW
# INTERNET DENY
# ---------------------------------------------------------------------------
#
#
# Expected:
#
#
#       no policy-compliant operational path
#
#       candidate rejected
#
#
# Network truth remains:
#
#
#       Internet AVAILABLE
#
#
# Policy truth remains:
#
#
#       Internet DENY
#
#
# ---------------------------------------------------------------------------
# TEST 5
#
# MULTIPLE COMPLIANT PATHS
# ---------------------------------------------------------------------------
#
#
# private-link-a:
#
#       AVAILABLE / ALLOW
#
#
# vpn-a:
#
#       AVAILABLE / ALLOW
#
#
# Expected:
#
#
#       candidate network/path constraint satisfied
#
#
# CandidateEvaluator does not need to choose the packet forwarding path.
#
#
# ---------------------------------------------------------------------------
# TEST 6
#
# DEGRADED SERVICE + LIGHT WORKLOAD
# ---------------------------------------------------------------------------
#
#
# Service:
#
#       DEGRADED
#
#
# Suitability:
#
#       SUITABLE
#
#
# Expected:
#
#
#       service may remain viable
#
#
# ---------------------------------------------------------------------------
# TEST 7
#
# DEGRADED SERVICE + HEAVY WORKLOAD
# ---------------------------------------------------------------------------
#
#
# Service:
#
#       DEGRADED
#
#
# Suitability:
#
#       UNSUITABLE
#
#
# Expected:
#
#
#       candidate rejected
#
#
# Service state remains:
#
#
#       DEGRADED
#
#
# NOT:
#
#
#       UNAVAILABLE
#
#
# ---------------------------------------------------------------------------
# TEST 8
#
# DEGRADED SERVICE + UNKNOWN SUITABILITY
# ---------------------------------------------------------------------------
#
#
# Expected:
#
#
#       candidate fails closed
#
#
# Suitability remains:
#
#
#       UNKNOWN
#
#
# NOT:
#
#
#       UNSUITABLE
#
#
# ---------------------------------------------------------------------------
# TEST 9
#
# DEGRADED PATH + SUITABLE WORKLOAD
# ---------------------------------------------------------------------------
#
#
# Expected:
#
#
#       path may remain usable
#
#
# ---------------------------------------------------------------------------
# TEST 10
#
# DEGRADED PATH + UNSUITABLE WORKLOAD
# ---------------------------------------------------------------------------
#
#
# Expected:
#
#
#       path not usable for this workload
#
#
# Path remains:
#
#
#       DEGRADED
#
#
# ---------------------------------------------------------------------------
# TEST 11
#
# EXCELLENT PERFORMANCE + POLICY DENY
# ---------------------------------------------------------------------------
#
#
# Path:
#
#       AVAILABLE
#
#
# latency:
#
#       excellent
#
#
# cost:
#
#       excellent
#
#
# policy:
#
#       DENY
#
#
# Expected:
#
#
#       not viable
#
#
# ---------------------------------------------------------------------------
# TEST 12
#
# POLICY ALLOW + PATH FAILURE
# ---------------------------------------------------------------------------
#
#
# Path policy:
#
#       ALLOW
#
#
# Path:
#
#       UNAVAILABLE
#
#
# Expected:
#
#
#       policy remains ALLOW
#
#       path remains UNAVAILABLE
#
#       candidate cannot use that path
#
#
# ---------------------------------------------------------------------------
# TEST 13
#
# AVAILABLE INTERNET PATH FOR E9
#
# INTERNET PATH POLICY DENIED
# ---------------------------------------------------------------------------
#
#
# Expected:
#
#
#       network subsystem reports AVAILABLE
#
#       policy subsystem reports DENY
#
#       candidate evaluation does not use the path
#
#
# ---------------------------------------------------------------------------
# TEST 14
#
# UNKNOWN PATH POLICY
# ---------------------------------------------------------------------------
#
#
# Path:
#
#       AVAILABLE
#
#
# Path policy:
#
#       INDETERMINATE
#
#
# Expected:
#
#
#       fail closed
#
#
# Path remains:
#
#
#       AVAILABLE
#
#
# Policy remains:
#
#
#       INDETERMINATE
#
#
# ---------------------------------------------------------------------------
# TEST 15
#
# UNKNOWN NETWORK STATE + ALLOW
# ---------------------------------------------------------------------------
#
#
# Path:
#
#       UNKNOWN
#
#
# Policy:
#
#       ALLOW
#
#
# Expected:
#
#
#       cannot establish operationally compliant path
#
#
# Network remains:
#
#
#       UNKNOWN
#
#
# ---------------------------------------------------------------------------
# TEST 16
#
# REALIZED PATH DIFFERS FROM EXPECTED PATH
# ---------------------------------------------------------------------------
#
#
# Future only.
#
#
# Expected:
#
#
#       do not silently claim intended path was used
#
#       surface path drift / assurance failure
#
#
# ============================================================================


# ============================================================================
# PART III-A OWNERSHIP TABLE
# ============================================================================
#
#
# NETWORK SUBSYSTEM
# -----------------
#
# Owns:
#
#
#       path identity
#
#       path operational evidence
#
#       path operational assessment
#
#       network reachability
#
#
# Does NOT own:
#
#
#       data authorization
#
#       workload authorization
#
#       AI routing selection
#
#
# ---------------------------------------------------------------------------
# POLICY SUBSYSTEM
# ---------------------------------------------------------------------------
#
# Owns:
#
#
#       whether data may use a destination
#
#       future path-specific authorization
#
#       organizational restrictions
#
#       user restrictions
#
#
# Does NOT own:
#
#
#       whether the path is operational
#
#
# ---------------------------------------------------------------------------
# SUITABILITY EVALUATION
# ---------------------------------------------------------------------------
#
# Future responsibility:
#
#
#       interpret workload requirements
#
#           against
#
#       operational resource conditions
#
#
# Does NOT redefine:
#
#
#       service state
#
#       network state
#
#
# ---------------------------------------------------------------------------
# CandidateEvaluator
# ---------------------------------------------------------------------------
#
# Owns:
#
#
#       joining established conclusions
#
#       determining single-candidate viability
#
#
# Does NOT own:
#
#
#       creating those conclusions
#
#
# ============================================================================


# ============================================================================
# PART III-A FINAL INVARIANTS
# ============================================================================
#
#
# POLICY
# ------
#
#
#       DESTINATION AUTHORIZED
#           !=
#       EVERY PATH AUTHORIZED
#
#
#       ROUTING CONSUMES POLICY
#
#       ROUTING DOES NOT INVENT POLICY
#
#
#       POLICY DENIED
#           !=
#       NETWORK UNAVAILABLE
#
#
# ---------------------------------------------------------------------------
# NETWORK
# ---------------------------------------------------------------------------
#
#
#       PATH AVAILABLE
#           !=
#       PATH AUTHORIZED
#
#
#       AVAILABLE BUT PROHIBITED
#       IS A VALID SYSTEM STATE
#
#
#       AUTHORIZED BUT UNAVAILABLE
#       IS A VALID SYSTEM STATE
#
#
#       ROUTING PROTOCOL
#           !=
#       NETWORK PATH TYPE
#
#
#       PATH TYPE
#           !=
#       PATH INSTANCE
#
#
#       EXPECTED PATH
#           !=
#       REALIZED PATH
#
#
#       NETWORK WORKING
#           !=
#       NETWORK WORKING AS INTENDED
#
#
# ---------------------------------------------------------------------------
# SUITABILITY
# ---------------------------------------------------------------------------
#
#
#       RESOURCE STATE
#           !=
#       REQUEST-RESOURCE SUITABILITY
#
#
#       DEGRADED
#           !=
#       UNSUITABLE
#
#
#       DEGRADED
#           !=
#       SUITABLE
#
#
#       PATH OPERATIONAL
#           !=
#       PATH SUITABLE FOR EVERY WORKLOAD
#
#
#       UNKNOWN SUITABILITY
#           !=
#       PROVEN UNSUITABILITY
#
#
# ---------------------------------------------------------------------------
# MEASUREMENTS
# ---------------------------------------------------------------------------
#
#
#       MEASUREMENT
#           !=
#       ASSESSMENT
#
#
#       ASSESSMENT
#           !=
#       SUITABILITY
#
#
#       PERFORMANCE THRESHOLD
#           !=
#       SECURITY POLICY
#
#
# ---------------------------------------------------------------------------
# ROUTING
# ---------------------------------------------------------------------------
#
#
#       AVAILABLE PATH EXISTS
#           !=
#       PERMITTED AVAILABLE PATH EXISTS
#
#
#       EXISTENCE
#           !=
#       PATH SELECTION
#
#
#       AI ROUTING SELECTION
#           !=
#       PACKET FORWARDING SELECTION
#
#
#       HARD CONSTRAINT
#           !=
#       WEIGHTED PREFERENCE
#
#
#       FILTER FIRST
#
#       OPTIMIZE SECOND
#
#
# ---------------------------------------------------------------------------
# EPISTEMICS
# ---------------------------------------------------------------------------
#
#
#       FAIL CLOSED
#           !=
#       FALSIFY STATE
#
#
#       FAIL CLOSED
#           !=
#       INVENT CERTAINTY
#
#
#       MODEL WHAT WE CAN PROVE
#
#
#       DO NOT MODEL
#       WHAT WE MERELY WISH
#       WE COULD PROVE
#
#
# ---------------------------------------------------------------------------
# ARCHITECTURE
# ---------------------------------------------------------------------------
#
#
#       OPERATIONAL STATE
#           !=
#       AUTHORIZATION
#           !=
#       WORKLOAD SUITABILITY
#
#
#       FUTURE-AWARE
#           !=
#       FUTURE-BLOATED
#
#
#       BETTER NORMALIZED FACTS
#           >
#       MORE INFRASTRUCTURE LOGIC
#       INSIDE CandidateEvaluator
#
#
# ============================================================================


# ============================================================================
# PART III-A FINAL CONTRACT
# ============================================================================
#
#
# As Agent 11 matures, CandidateEvaluator may need to know:
#
#
#       whether an operational path exists
#
#
#       whether an authorized operational path exists
#
#
#       whether that authorized operational path is suitable
#       for the current workload
#
#
# ============================================================================
#
# But CandidateEvaluator should NOT learn:
#
#
#       how BGP chose the route
#
#       how SD-WAN steered the traffic
#
#       how Kubernetes discovered the endpoint
#
#       why E9 prohibits Internet transit
#
#       how latency was measured
#
#       how workload thresholds were calculated
#
#
# ============================================================================
#
# Those subsystems should provide:
#
#
#       BETTER FACTS
#
#
# CandidateEvaluator should continue asking:
#
#
#       "DO THE ESTABLISHED FACTS
#        PROVE THAT THIS ONE SERVICE
#        MAY AND CAN SATISFY
#        THIS REQUEST?"
#
#
# ============================================================================
#
#
#       OPERATIONAL
#
#           +
#
#       AUTHORIZED
#
#           +
#
#       SUITABLE
#
#           =
#
#       POTENTIALLY USABLE
#
#
# ============================================================================
#
# And only after every other candidate requirement is also satisfied:
#
#
#       POTENTIALLY USABLE
#
#           +
#
#       POLICY PERMITTED
#
#           +
#
#       CAPABLE
#
#           +
#
#       SERVICE OPERATIONAL
#
#           =
#
#       VIABLE ROUTING CANDIDATE
#
#
# ============================================================================
# END COMPLETE PART III-A
# ============================================================================

# ============================================================================
# routing/candidate_evaluator.py
#
# COMPLETE PART III-B
#
# RICHER FACTS,
# MULTI-DEPLOYMENT IDENTITY,
# AND
# WHEN SIMPLE TYPES STOP BEING ENOUGH
# ============================================================================
#
# PURPOSE
# -------
#
# Part III-A established three independent dimensions:
#
#
#       OPERATIONAL STATE
#           !=
#       AUTHORIZATION
#           !=
#       WORKLOAD SUITABILITY
#
#
# Part III-B asks:
#
#
#       "What happens when the facts CandidateEvaluator consumes
#        become more sophisticated?"
#
#
# Current SEIR-I inputs are intentionally simple:
#
#
#       AIService
#
#       PolicyDecision
#
#       capability_supported: bool
#
#       ServiceState
#
#       NetworkAssessmentResult
#
#
# This is GOOD.
#
#
# ============================================================================
# CENTRAL RULE
# ============================================================================
#
#
#       SIMPLE IS NOT IMMATURE.
#
#
#       SIMPLE IS CORRECT
#       WHEN THE DOMAIN IS SIMPLE.
#
#
# ============================================================================
#
# We should not replace:
#
#
#       bool
#
#
# with:
#
#
#       seven classes,
#       twelve enums,
#       three protocols,
#       and a factory
#
#
# merely because:
#
#
#       "enterprise architecture."
#
#
# ============================================================================
#
# But the opposite mistake is equally dangerous.
#
#
# Once the domain contains distinctions that the current type cannot
# represent, keeping the simple type destroys information.
#
#
# ============================================================================
#
#
#       DO NOT MODEL COMPLEXITY
#       BEFORE IT EXISTS.
#
#
#       DO NOT HIDE COMPLEXITY
#       AFTER IT EXISTS.
#
#
# ============================================================================


# ============================================================================
# SECTION 1
#
# WHEN bool STOPS BEING ENOUGH
# ============================================================================
#
# Current CandidateEvaluator receives:
#
#
#       capability_supported: bool
#
#
# Current meaning:
#
#
#       True
#           =
#       the registered model capability contract satisfies
#       the requested requirement
#
#
#       False
#           =
#       the registered model capability contract does not satisfy
#       the requested requirement
#
#
# ============================================================================
#
# This is sufficient because current capability evaluation is deterministic
# over registered capability declarations.
#
#
# ============================================================================


# ============================================================================
# WHY bool IS GOOD RIGHT NOW
# ============================================================================
#
# Suppose the model registry declares:
#
#
#       CODE_REASONING
#
#           LIGHT
#           STANDARD
#           HEAVY
#
#
# The request requires:
#
#
#       CODE_REASONING
#
#       STANDARD
#
#
# ModelRouter can answer:
#
#
#       True
#
#
# ============================================================================
#
# If the model declares only:
#
#
#       SUMMARIZATION
#
#
# ModelRouter can answer:
#
#
#       False
#
#
# ============================================================================
#
# There is no missing epistemic state.
#
#
# Therefore:
#
#
#       bool
#
#
# accurately represents the current domain.
#
#
# ============================================================================
#
#
#       SMALL TYPE
#           +
#       COMPLETE SEMANTICS
#           =
#       GOOD MODEL
#
#
# ============================================================================


# ============================================================================
# FUTURE CAPABILITY PRESSURE
# ============================================================================
#
# Now imagine SEIR-II introduces:
#
#
#       dynamically discovered models
#
#       provider feature negotiation
#
#       model-version drift
#
#       temporary feature disablement
#
#       deployment-specific capability differences
#
#       context-window restrictions
#
#       tool-use restrictions
#
#       structured-output schema limitations
#
#
# ============================================================================
#
# Suddenly:
#
#
#       False
#
#
# becomes ambiguous.
#
#
# Does False mean:
#
#
#       "The model definitely does not support this."
#
#
# or:
#
#
#       "Agent 11 could not determine whether it supports this."
#
#
# ============================================================================
#
#
#       UNSUPPORTED
#           !=
#       UNKNOWN
#
#
# ============================================================================


# ============================================================================
# BOOLEAN INFORMATION COLLAPSE
# ============================================================================
#
# Suppose the real domain contains:
#
#
#       SUPPORTED
#
#       UNSUPPORTED
#
#       UNKNOWN
#
#
# but we insist on storing:
#
#
#       bool
#
#
# We must collapse three states into two.
#
#
# ============================================================================
#
# Option A:
#
#
#       SUPPORTED
#           -> True
#
#       UNSUPPORTED
#           -> False
#
#       UNKNOWN
#           -> False
#
#
# ============================================================================
#
# This is safe for routing availability:
#
#
#       UNKNOWN fails closed
#
#
# but it destroys epistemic information.
#
#
# Telemetry can no longer distinguish:
#
#
#       model definitely incapable
#
#
# from:
#
#
#       capability observation failed
#
#
# ============================================================================
#
#
#       SAFE DISPOSITION
#           !=
#       COMPLETE REPRESENTATION
#
#
# ============================================================================


# ============================================================================
# THE TYPE HAS BECOME LOSSY
# ============================================================================
#
# At that point:
#
#
#       capability_supported: bool
#
#
# no longer represents the domain faithfully.
#
#
# ============================================================================
#
#
#       TYPE TOO SMALL
#           ->
#       INFORMATION LOSS
#
#
# ============================================================================
#
# That is when a richer type has earned existence.
#
#
# ============================================================================


# ============================================================================
# POSSIBLE FUTURE CAPABILITY STATUS
# ============================================================================
#
# CONCEPTUAL ONLY.
#
# DO NOT IMPLEMENT YET.
#
#
# class CapabilityEvaluationStatus(Agent11Enum):
#
#     SUPPORTED = "supported"
#
#     UNSUPPORTED = "unsupported"
#
#     UNKNOWN = "unknown"
#
#
# ============================================================================
#
# CandidateEvaluator could then distinguish:
#
#
#       UNSUPPORTED
#
#           ->
#
#       CAPABILITY_MISMATCH
#
#
# from:
#
#
#       UNKNOWN
#
#           ->
#
#       UNKNOWN
#
#
# ============================================================================
#
# Both fail candidate viability.
#
#
# But they fail for different reasons.
#
#
# ============================================================================
#
#
#       SAME ROUTING DISPOSITION
#           !=
#       SAME DOMAIN TRUTH
#
#
# ============================================================================


# ============================================================================
# POSSIBLE FUTURE CAPABILITY EVALUATION
# ============================================================================
#
# Eventually status alone may also become insufficient.
#
#
# We might need to know:
#
#
#       capability requested
#
#       reasoning level requested
#
#       model evaluated
#
#       status
#
#       evidence source
#
#       observed version
#
#       timestamp
#
#
# ============================================================================
#
# At that point a noun such as:
#
#
#       CapabilityEvaluation
#
#
# may earn existence.
#
#
# ============================================================================
#
# Again:
#
#
#       MAY EARN EXISTENCE
#
#
# not:
#
#
#       SHOULD BE CREATED TODAY
#
#
# ============================================================================


# ============================================================================
# THE GENERAL RULE
# ============================================================================
#
# Start with:
#
#
#       bool
#
#
# if the domain truly has two meaningful states.
#
#
# Move to:
#
#
#       enum
#
#
# when the domain gains additional named states.
#
#
# Move to:
#
#
#       model
#
#
# when the domain gains meaningful relationships and metadata around the
# state.
#
#
# ============================================================================
#
#
#       BOOL
#           ->
#       ENUM
#           ->
#       MODEL
#
#
# should be driven by:
#
#
#       DOMAIN PRESSURE
#
#
# not:
#
#
#       ARCHITECTURAL FASHION
#
#
# ============================================================================


# ============================================================================
# SECTION 2
#
# MODEL != SERVICE
# ============================================================================
#
# We already established:
#
#
#       AIModel
#           =
#       WHAT MODEL IS
#
#
#       AIService
#           =
#       HOW MODEL IS EXPOSED
#
#
# ============================================================================
#
# Example:
#
#
#       AIModel
#
#           model_id:
#               company-security-reasoner-v4
#
#
#       AIService
#
#           service_id:
#               company-security-reasoning
#
#           model_id:
#               company-security-reasoner-v4
#
#           routing_domain:
#               COMPANY_CLOUD_LLM
#
#
# ============================================================================
#
#
#       MODEL IDENTITY
#           !=
#       SERVICE IDENTITY
#
#
# ============================================================================


# ============================================================================
# WHY THE DISTINCTION MATTERS
# ============================================================================
#
# The same logical model may be exposed through:
#
#
#       multiple services
#
#
# or:
#
#
#       one service may eventually change which model version it exposes
#
#
# without changing the service identity used by callers.
#
#
# ============================================================================
#
# Example:
#
#
#       service:
#           company-security-reasoning
#
#
# today:
#
#
#       model:
#           security-reasoner-v4
#
#
# next month:
#
#
#       model:
#           security-reasoner-v5
#
#
# ============================================================================
#
# Therefore:
#
#
#       service_id
#
#
# should not secretly mean:
#
#
#       model_id
#
#
# ============================================================================
#
#
#       MODEL != SERVICE
#
#
# ============================================================================


# ============================================================================
# SECTION 3
#
# SERVICE != DEPLOYMENT
# ============================================================================
#
# SEIR-II introduces the next identity layer.
#
#
# One logical AIService may have multiple physical or cloud deployments.
#
#
# ============================================================================
#
# Example:
#
#
#       AIService
#
#           company-security-reasoning
#
#
# may have:
#
#
#       Deployment A
#
#           Azure
#           East US
#
#
#       Deployment B
#
#           GCP
#           us-central1
#
#
#       Deployment C
#
#           AWS
#           us-east-1
#
#
# ============================================================================
#
# All three may expose:
#
#
#       THE SAME LOGICAL SERVICE
#
#
# ============================================================================
#
#
#       SERVICE
#           !=
#       DEPLOYMENT
#
#
# ============================================================================


# ============================================================================
# IDENTITY CHAIN
# ============================================================================
#
# We now begin to see a durable conceptual hierarchy:
#
#
#       AIModel
#           |
#           v
#       AIService
#           |
#           v
#       Deployment
#           |
#           v
#       NetworkEndpoint
#           |
#           v
#       NetworkPath
#
#
# ============================================================================
#
# Each answers a different question.
#
#
# AIModel
# -------
#
#       WHAT reasoning model is this?
#
#
# AIService
# ---------
#
#       HOW is that model logically exposed to Agent 11?
#
#
# Deployment
# ----------
#
#       WHERE and in what runtime environment
#       does this service instance exist?
#
#
# NetworkEndpoint
# ---------------
#
#       WHAT network destination exposes that deployment?
#
#
# NetworkPath
# -----------
#
#       HOW can Agent 11 reach that destination?
#
#
# ============================================================================
#
#
#       WHAT
#           !=
#       HOW EXPOSED
#           !=
#       WHERE DEPLOYED
#           !=
#       WHERE REACHED
#           !=
#       HOW REACHED
#
#
# ============================================================================


# ============================================================================
# WHY DEPLOYMENT IDENTITY WILL MATTER
# ============================================================================
#
# Suppose:
#
#
#       service:
#           company-security-reasoning
#
#
# has:
#
#
#       azure-east
#
#       gcp-central
#
#
# ============================================================================
#
# Azure may currently be:
#
#
#       AVAILABLE
#
#
# while GCP is:
#
#
#       UNAVAILABLE
#
#
# ============================================================================
#
# If health is stored only at:
#
#
#       AIService
#
#
# level, what is the service state?
#
#
#       AVAILABLE?
#
#       DEGRADED?
#
#       UNAVAILABLE?
#
#
# ============================================================================
#
# We have discovered additional domain pressure.
#
#
# Deployment-level operational state may eventually need to exist.
#
#
# ============================================================================
#
#
#       SERVICE HEALTH
#           !=
#       DEPLOYMENT HEALTH
#
#
# ============================================================================


# ============================================================================
# THIS DOES NOT MEAN SERVICE HEALTH DISAPPEARS
# ============================================================================
#
# A service-level assessment may still be useful.
#
#
# Example:
#
#
#       deployment A = AVAILABLE
#
#       deployment B = UNAVAILABLE
#
#
# service-level assessment:
#
#
#       AVAILABLE
#
#
# because at least one deployment can satisfy requests.
#
#
# ============================================================================
#
# But:
#
#
#       deployment-level fact
#
#
# and:
#
#
#       service-level assessment
#
#
# are different layers.
#
#
# ============================================================================
#
#
#       COMPONENT STATE
#           !=
#       AGGREGATE STATE
#
#
# ============================================================================


# ============================================================================
# DEPLOYMENT IS ALSO WHERE CLOUD LOCATION BELONGS
# ============================================================================
#
# Future Deployment might eventually carry facts such as:
#
#
#       deployment_id
#
#       service_id
#
#       cloud_provider
#
#       region
#
#       account / subscription / project
#
#       runtime type
#
#       endpoint reference
#
#
# ============================================================================
#
# These are deployment facts.
#
#
# They do NOT belong in:
#
#
#       AIRoute
#
#
# ============================================================================


# ============================================================================
# CLOUD PROVIDER != ROUTING DOMAIN
# ============================================================================
#
# This is critical for Agent 11.
#
#
# Current AIRoute:
#
#
#       EXTERNAL_FM
#
#       COMPANY_CLOUD_LLM
#
#       COMPANY_ONPREM_LLM
#
#
# ============================================================================
#
# COMPANY_CLOUD_LLM is intentionally:
#
#
#       PROVIDER NEUTRAL
#
#
# ============================================================================
#
# A company-owned cloud reasoning service may be deployed in:
#
#
#       AWS
#
#       Azure
#
#       GCP
#
#       OCI
#
#       another future cloud
#
#
# and still belong to:
#
#
#       COMPANY_CLOUD_LLM
#
#
# ============================================================================
#
#
#       CLOUD PROVIDER
#           !=
#       ROUTING DOMAIN
#
#
# ============================================================================


# ============================================================================
# EXAMPLE
# ============================================================================
#
#
#       Azure deployment
#           |
#           v
#       COMPANY_CLOUD_LLM
#
#
#       GCP deployment
#           |
#           v
#       COMPANY_CLOUD_LLM
#
#
#       AWS deployment
#           |
#           v
#       COMPANY_CLOUD_LLM
#
#
# ============================================================================
#
# AIRoute answers:
#
#
#       "What trust / ownership routing domain
#        does this reasoning destination belong to?"
#
#
# Cloud provider answers:
#
#
#       "Where is this deployment hosted?"
#
#
# ============================================================================
#
#
#       TRUST DOMAIN
#           !=
#       HOSTING PROVIDER
#
#
# ============================================================================


# ============================================================================
# WHY WE MUST NOT ADD CLOUD-SPECIFIC AIRoutes
# ============================================================================
#
# Avoid:
#
#
#       COMPANY_AZURE_LLM
#
#       COMPANY_GCP_LLM
#
#       COMPANY_AWS_LLM
#
#       COMPANY_OCI_LLM
#
#
# ============================================================================
#
# unless organizational policy genuinely defines those as separate routing
# trust domains.
#
#
# Otherwise we would be encoding:
#
#
#       infrastructure topology
#
#
# into:
#
#
#       policy/routing vocabulary
#
#
# ============================================================================
#
#
#       DEPLOYMENT TOPOLOGY
#           !=
#       ROUTING POLICY DOMAIN
#
#
# ============================================================================


# ============================================================================
# LOCATION != AUTHORIZATION
# ============================================================================
#
# A deployment being in:
#
#
#       Azure East US
#
#
# does not itself tell us:
#
#
#       whether E9 data may use it
#
#
# ============================================================================
#
# Likewise:
#
#
#       GCP us-central1
#
#
# does not inherently mean:
#
#
#       allowed
#
#
# or:
#
#
#       denied
#
#
# ============================================================================
#
# Policy may use location as one input.
#
#
# But location itself is not the policy conclusion.
#
#
# ============================================================================
#
#
#       LOCATION
#           !=
#       AUTHORIZATION
#
#
# ============================================================================


# ============================================================================
# WHERE IT RUNS != HOW WE REACH IT
# ============================================================================
#
# Suppose a model is deployed in Azure.
#
#
# Agent 11 might reach it through:
#
#
#       INTERNET
#
#       VPN
#
#       PRIVATE_LINK
#
#       SD_WAN
#
#
# ============================================================================
#
# Therefore:
#
#
#       cloud_provider = AZURE
#
#
# does not imply:
#
#
#       path_type = INTERNET
#
#
# or:
#
#
#       path_type = PRIVATE_LINK
#
#
# ============================================================================
#
#
#       WHERE IT RUNS
#           !=
#       HOW WE REACH IT
#
#
# ============================================================================


# ============================================================================
# CLOUD PROVIDER != PATH TYPE
# ============================================================================
#
# This means we should never create:
#
#
#       NetworkPathType.AZURE
#
#       NetworkPathType.GCP
#
#       NetworkPathType.AWS
#
#
# ============================================================================
#
# Those are not network path mechanisms.
#
#
# ============================================================================
#
#
#       PROVIDER
#           !=
#       CONNECTIVITY MECHANISM
#
#
# ============================================================================


# ============================================================================
# SECTION 4
#
# SERVICE -> DEPLOYMENT -> ENDPOINT
# ============================================================================
#
# Part II deliberately refused to assert:
#
#
#       AIService.service_id
#           ==
#       NetworkAssessmentResult.destination_id
#
#
# ============================================================================
#
# III-B explains why that refusal was correct.
#
#
# The likely future relationship is:
#
#
#       AIService
#           |
#           v
#       Deployment
#           |
#           v
#       NetworkEndpoint
#           |
#           v
#       destination_id
#
#
# ============================================================================
#
# The service itself may not be the network destination.
#
#
# One service may have:
#
#
#       multiple deployments
#
#
# and each deployment may expose:
#
#
#       one or more endpoints
#
#
# ============================================================================
#
#
#       SERVICE IDENTITY
#           !=
#       NETWORK DESTINATION IDENTITY
#
#
# ============================================================================


# ============================================================================
# EXAMPLE
# ============================================================================
#
#
# AIService:
#
#       service_id
#           =
#       company-security-reasoning
#
#
# Deployment:
#
#       deployment_id
#           =
#       company-security-reasoning-azure-east
#
#
# NetworkEndpoint:
#
#       endpoint_id
#           =
#       inference-private-east-01
#
#
# NetworkAssessmentResult:
#
#       destination_id
#           =
#       inference-private-east-01
#
#
# ============================================================================
#
# None of those IDs need to be equal.
#
#
# They are connected through explicit relationships.
#
#
# ============================================================================
#
#
#       RELATIONSHIP
#           >
#       STRING COINCIDENCE
#
#
# ============================================================================


# ============================================================================
# THIS SOLVES A PART II PROBLEM PROPERLY
# ============================================================================
#
# In Part II we said:
#
#
#       DO NOT WRITE:
#
#
#       service.service_id == network.destination_id
#
#
# because the architecture had not established that invariant.
#
#
# ============================================================================
#
# III-B shows the future solution:
#
#
#       DO NOT FORCE THE IDS TO MATCH.
#
#
#       MODEL THE RELATIONSHIP.
#
#
# ============================================================================


# ============================================================================
# SECTION 5
#
# ONE SERVICE, MULTIPLE DEPLOYMENTS
# ============================================================================
#
# Suppose:
#
#
#       AIService
#           =
#       company-trading-reasoner
#
#
# has:
#
#
#       deployment-azure-east
#
#       deployment-gcp-central
#
#
# ============================================================================
#
# Both may expose the same:
#
#
#       AIModel
#
#
# ============================================================================
#
# Or perhaps:
#
#
#       Azure
#           exposes model version 7.2
#
#
#       GCP
#           exposes model version 7.1
#
#
# during a rolling deployment.
#
#
# ============================================================================
#
# Now identity and capability become more interesting.
#
#
# ============================================================================


# ============================================================================
# MODEL CAPABILITY MAY EVENTUALLY BECOME DEPLOYMENT-SENSITIVE
# ============================================================================
#
# Current:
#
#
#       capability
#
# belongs naturally to:
#
#
#       AIModel
#
#
# ============================================================================
#
# But future infrastructure may impose deployment-specific restrictions.
#
#
# Example:
#
#
#       model supports TOOL_USE
#
#
# but:
#
#
#       deployment A
#           tool use enabled
#
#
#       deployment B
#           tool use disabled
#
#
# ============================================================================
#
# This does NOT necessarily mean the logical model changed.
#
#
# It may mean:
#
#
#       deployment capability
#
#
# is constrained by:
#
#
#       runtime configuration
#
#
# ============================================================================
#
#
#       MODEL CAPABILITY
#           !=
#       DEPLOYMENT-EXPOSED CAPABILITY
#
#
# ============================================================================


# ============================================================================
# DO NOT SOLVE THIS TODAY
# ============================================================================
#
# Current SEIR-I:
#
#
#       AIModel.capabilities
#
#
# is sufficient.
#
#
# ============================================================================
#
# We should not introduce:
#
#
#       deployment capability overlays
#
#
# until the runtime architecture actually needs them.
#
#
# ============================================================================
#
#
#       RECOGNIZE THE PRESSURE.
#
#
#       DO NOT PREMATURELY
#       IMPLEMENT THE PRESSURE.
#
#
# ============================================================================


# ============================================================================
# SECTION 6
#
# SHOULD CandidateEvaluator SELECT A DEPLOYMENT?
# ============================================================================
#
# No.
#
#
# CandidateEvaluator answers:
#
#
#       "Is this candidate viable?"
#
#
# ============================================================================
#
# It should not quietly become:
#
#
#       DeploymentSelector
#
#
# ============================================================================
#
# If one AIService has several deployments, another runtime/routing behavior
# should determine which deployment facts participate in the candidate
# evaluation.
#
#
# ============================================================================
#
#
#       CANDIDATE VIABILITY
#           !=
#       DEPLOYMENT SELECTION
#
#
# ============================================================================


# ============================================================================
# POSSIBLE FUTURE FLOW
# ============================================================================
#
#
#       AIService
#           |
#           v
#       Deployment Registry
#           |
#           v
#       Eligible Deployments
#           |
#           v
#       Deployment / Endpoint Assessment
#           |
#           v
#       Normalized Candidate Facts
#           |
#           v
#       CandidateEvaluator
#
#
# ============================================================================
#
# CandidateEvaluator should receive:
#
#
#       conclusions
#
#
# rather than learning:
#
#
#       Azure APIs
#
#       GCP APIs
#
#       AWS APIs
#
#       OCI APIs
#
#       Kubernetes APIs
#
#
# ============================================================================


# ============================================================================
# VENDOR COMPLEXITY MUST END BELOW THIS BOUNDARY
# ============================================================================
#
# Bad future CandidateEvaluator:
#
#
#       if deployment.provider == AZURE:
#           query_azure(...)
#
#       elif deployment.provider == GCP:
#           query_gcp(...)
#
#       elif deployment.provider == AWS:
#           query_aws(...)
#
#
# ============================================================================
#
# Good:
#
#
#       deployment/runtime subsystem
#           |
#           v
#       normalized operational facts
#           |
#           v
#       CandidateEvaluator
#
#
# ============================================================================
#
#
#       VENDOR COMPLEXITY
#       ENDS AT THE
#       ADAPTER BOUNDARY.
#
#
# ============================================================================


# ============================================================================
# SECTION 7
#
# MULTI-CLOUD != RESILIENCE
# ============================================================================
#
# Suppose:
#
#
#       deployment A
#           =
#       Azure
#
#
#       deployment B
#           =
#       GCP
#
#
# ============================================================================
#
# It is tempting to say:
#
#
#       "Excellent. Independent redundancy."
#
#
# Not necessarily.
#
#
# ============================================================================
#
# Both may depend on:
#
#
#       the same corporate identity provider
#
#       the same DNS provider
#
#       the same carrier
#
#       the same SD-WAN controller
#
#       the same secret store
#
#       the same CI/CD pipeline
#
#       the same upstream data source
#
#
# ============================================================================
#
#
#       DIFFERENT CLOUDS
#           !=
#       INDEPENDENT FAILURE
#
#
# ============================================================================


# ============================================================================
# PATH COUNT != FAILURE-DOMAIN COUNT
# ============================================================================
#
# Likewise:
#
#
#       three network paths
#
#
# does not necessarily mean:
#
#
#       three independent failure domains
#
#
# ============================================================================
#
# They may all traverse:
#
#
#       the same carrier
#
#       the same router
#
#       the same building
#
#       the same tunnel concentrator
#
#
# ============================================================================
#
#
#       MULTI-PATH
#           !=
#       RESILIENCE
#
#
# ============================================================================


# ============================================================================
# SHOULD CandidateEvaluator REASON ABOUT CORRELATED FAILURE?
# ============================================================================
#
# Usually no.
#
#
# CandidateEvaluator evaluates:
#
#
#       ONE candidate
#
#
# ============================================================================
#
# Correlated failure asks:
#
#
#       "How independent is candidate A
#        from candidate B?"
#
#
# ============================================================================
#
# That requires:
#
#
#       MULTIPLE candidates
#
#
# ============================================================================
#
#
#       SINGLE-CANDIDATE VIABILITY
#           !=
#       CROSS-CANDIDATE RESILIENCE
#
#
# ============================================================================
#
# This belongs later in selection / resilience reasoning.
#
#
# ============================================================================


# ============================================================================
# SECTION 8
#
# PARAMETER PRESSURE
# ============================================================================
#
# Current CandidateEvaluator signature:
#
#
#       evaluate(
#           *,
#           service,
#           policy_decision,
#           capability_supported,
#           service_state,
#           network_assessment,
#       )
#
#
# ============================================================================
#
# This is GOOD.
#
#
# It is explicit.
#
#
# Students can see the viability dimensions directly.
#
#
# ============================================================================


# ============================================================================
# FUTURE SIGNATURE PRESSURE
# ============================================================================
#
# SEIR-II might eventually require:
#
#
#       service
#
#       deployment
#
#       destination_policy
#
#       path_policy_results
#
#       capability_evaluation
#
#       service_state
#
#       deployment_state
#
#       network_assessment
#
#       workload_suitability
#
#       endpoint identity
#
#       ...
#
#
# ============================================================================
#
# At some point:
#
#
#       explicit parameters
#
#
# may stop improving clarity.
#
#
# ============================================================================
#
# That is architectural pressure.
#
#
# ============================================================================


# ============================================================================
# WHEN AN AGGREGATE EARNS EXISTENCE
# ============================================================================
#
# A future model such as:
#
#
#       CandidateEvaluationFacts
#
#
# may eventually become justified.
#
#
# ============================================================================
#
# But NOT because:
#
#
#       "five arguments looks ugly."
#
#
# ============================================================================
#
# It becomes justified when:
#
#
#       the inputs form a stable domain concept
#
#
# and:
#
#
#       relationships among those inputs
#       need their own validation
#
#
# ============================================================================
#
#
#       PARAMETER PRESSURE
#       CAN EARN A MODEL.
#
#
#       AESTHETIC DISCOMFORT
#       DOES NOT.
#
#
# ============================================================================


# ============================================================================
# POSSIBLE FUTURE MODEL
# ============================================================================
#
# CONCEPTUAL ONLY.
#
# DO NOT IMPLEMENT YET.
#
#
# class CandidateEvaluationFacts(Agent11BaseModel):
#
#     service: AIService
#
#     deployment: AIDeployment
#
#     policy_decision: PolicyDecision
#
#     capability_evaluation: CapabilityEvaluation
#
#     service_state: ServiceState
#
#     deployment_state: DeploymentState
#
#     network_assessment: NetworkAssessmentResult
#
#     path_policy: PolicyCompliantPathSet
#
#     workload_suitability: WorkloadSuitability
#
#
# ============================================================================
#
# The important part is not reducing parameter count.
#
#
# The important part is that this object could validate:
#
#
#       deployment belongs to service
#
#       endpoint belongs to deployment
#
#       policy belongs to routing domain
#
#       network assessment belongs to endpoint
#
#       capability evaluation belongs to model
#
#       suitability belongs to request/resource relationship
#
#
# ============================================================================
#
# That is a real aggregate.
#
#
# ============================================================================


# ============================================================================
# WHY THIS WOULD BE DIFFERENT FROM A "CONTEXT BAG"
# ============================================================================
#
# Bad:
#
#
#       class Context:
#           anything: dict[str, Any]
#
#
# ============================================================================
#
# That merely hides parameters.
#
#
# It does not model relationships.
#
#
# ============================================================================
#
# Good:
#
#
#       CandidateEvaluationFacts
#
#
# has:
#
#
#       typed members
#
#       explicit identity
#
#       explicit relationships
#
#       validators proving those relationships
#
#
# ============================================================================
#
#
#       PARAMETER BAG
#           !=
#       DOMAIN AGGREGATE
#
#
# ============================================================================


# ============================================================================
# PART II RETURNS
# ============================================================================
#
# Remember Part II:
#
#
#       VALID OBJECTS
#           !=
#       VALID RELATIONSHIP
#
#
# ============================================================================
#
# As CandidateEvaluator gains richer facts, the number of relationships
# grows.
#
#
# Example:
#
#
#       AIService
#           |
#           v
#       Deployment
#           |
#           v
#       NetworkEndpoint
#           |
#           v
#       NetworkAssessment
#
#
# ============================================================================
#
# A future CandidateEvaluationFacts model may therefore earn existence not
# merely because there are many facts, but because:
#
#
#       THE RELATIONSHIPS THEMSELVES
#       BECOME A DOMAIN CONCEPT.
#
#
# ============================================================================


# ============================================================================
# SECTION 9
#
# IDENTITY MUST REMAIN EXPLICIT
# ============================================================================
#
# As the system becomes distributed, identity mistakes become increasingly
# dangerous.
#
#
# ============================================================================
#
# Imagine:
#
#
#       service A
#
#           deployment A1
#
#
#       service B
#
#           deployment B1
#
#
# ============================================================================
#
# If network evidence for:
#
#
#       B1
#
#
# is accidentally attached to:
#
#
#       A1
#
#
# CandidateEvaluator may make a perfectly logical decision over the wrong
# facts.
#
#
# ============================================================================
#
#
#       CORRECT REASONING
#           +
#       WRONG IDENTITY
#           =
#       WRONG DECISION
#
#
# ============================================================================


# ============================================================================
# IDs ARE NOT DECORATION
# ============================================================================
#
# Fields such as:
#
#
#       model_id
#
#       service_id
#
#       deployment_id
#
#       endpoint_id
#
#       path_id
#
#
# are not merely convenient labels.
#
#
# They allow Agent 11 to establish:
#
#
#       WHAT FACT BELONGS TO WHAT RESOURCE
#
#
# ============================================================================
#
#
#       IDENTITY
#       IS PART OF
#       DECISION CORRECTNESS.
#
#
# ============================================================================


# ============================================================================
# IDs ALSO NEED SCOPING
# ============================================================================
#
# Future distributed systems may discover that:
#
#
#       "prod"
#
#
# exists in:
#
#
#       Azure
#
#       GCP
#
#       AWS
#
#
# ============================================================================
#
# Therefore human-friendly names are often insufficient as durable identity.
#
#
# ============================================================================
#
#
#       DISPLAY NAME
#           !=
#       RESOURCE IDENTITY
#
#
# ============================================================================
#
# This is another reason:
#
#
#       explicit IDs
#
#
# and:
#
#
#       explicit relationships
#
#
# matter.
#
#
# ============================================================================


# ============================================================================
# SECTION 10
#
# FRESHNESS BECOMES MORE IMPORTANT AS FACTS MULTIPLY
# ============================================================================
#
# Suppose:
#
#
#       policy decision
#           observed/evaluated now
#
#
#       service health
#           observed 10 seconds ago
#
#
#       network assessment
#           observed 20 seconds ago
#
#
#       capability data
#           loaded yesterday
#
#
# ============================================================================
#
# CandidateEvaluator is joining facts from different times.
#
#
# ============================================================================
#
#
#       SAME CANDIDATE
#           !=
#       SAME OBSERVATION TIME
#
#
# ============================================================================


# ============================================================================
# HISTORICAL TRUTH MAY NO LONGER BE CURRENT TRUTH
# ============================================================================
#
# Example:
#
#
#       10:00:00
#
#           network AVAILABLE
#
#
#       10:00:05
#
#           network fails
#
#
#       10:00:30
#
#           candidate evaluation uses old evidence
#
#
# ============================================================================
#
# The old evidence was not false.
#
#
# It was:
#
#
#       STALE
#
#
# ============================================================================
#
#
#       STALE
#           !=
#       FALSE
#
#
# ============================================================================


# ============================================================================
# CANDIDATE EVALUATOR SHOULD NOT INVENT FRESHNESS RULES
# ============================================================================
#
# Network already owns:
#
#
#       network evidence freshness
#
#
# Service/runtime should own:
#
#
#       service evidence freshness
#
#
# Policy may eventually own:
#
#
#       policy decision validity / lifetime
#
#
# ============================================================================
#
# CandidateEvaluator should receive facts that their owning subsystems have
# established as usable for current evaluation.
#
#
# ============================================================================
#
#
#       FACT OWNER
#       SHOULD OWN
#       FACT FRESHNESS SEMANTICS.
#
#
# ============================================================================


# ============================================================================
# TIME IS STILL A DEPENDENCY
# ============================================================================
#
# If future cross-domain coherence requires an evaluation timestamp:
#
#
#       assessed_at
#
#
# should be explicit.
#
#
# Avoid hiding:
#
#
#       datetime.now()
#
#
# throughout domain logic.
#
#
# ============================================================================
#
#
#       TIME IS A DEPENDENCY.
#
#
# ============================================================================


# ============================================================================
# SECTION 11
#
# RICHER FACTS SHOULD MAKE CandidateEvaluator SMALLER
# ============================================================================
#
# This may initially sound backwards.
#
#
# ============================================================================
#
# As infrastructure becomes more complex:
#
#
#       capability evaluation becomes richer
#
#       service assessment becomes richer
#
#       deployment assessment appears
#
#       network assessment becomes richer
#
#       path policy appears
#
#       workload suitability appears
#
#
# ============================================================================
#
# CandidateEvaluator should NOT gain equivalent amounts of logic.
#
#
# Instead, it should receive better normalized conclusions.
#
#
# ============================================================================
#
#
#       MORE SOPHISTICATED SYSTEM
#
#           SHOULD PRODUCE
#
#       BETTER FACTS
#
#           NOT
#
#       A BIGGER GOD OBJECT
#
#
# ============================================================================


# ============================================================================
# BAD FUTURE
# ============================================================================
#
# CandidateEvaluator:
#
#
#       query Azure
#
#       query GCP
#
#       inspect Kubernetes
#
#       parse BGP
#
#       calculate latency
#
#       evaluate E9
#
#       inspect user preference
#
#       determine capability
#
#       calculate health
#
#       select deployment
#
#       select path
#
#       calculate cost
#
#       select model
#
#       perform fallback
#
#
# ============================================================================
#
# That is not:
#
#
#       CandidateEvaluator
#
#
# anymore.
#
#
# That is:
#
#
#       Agent11EntirePlatform.py
#
#
# ============================================================================


# ============================================================================
# GOOD FUTURE
# ============================================================================
#
#
#       Policy subsystem
#           |
#           v
#       normalized policy conclusion
#
#
#       Capability subsystem
#           |
#           v
#       normalized capability conclusion
#
#
#       Runtime subsystem
#           |
#           v
#       normalized service/deployment conclusion
#
#
#       Network subsystem
#           |
#           v
#       normalized network conclusion
#
#
#       Suitability subsystem
#           |
#           v
#       normalized suitability conclusion
#
#
#               +-------------------+
#               |
#               v
#       CandidateEvaluator
#               |
#               v
#       RoutingCandidate
#
#
# ============================================================================
#
#
#       BETTER FACTS IN.
#
#
#       SMALL DECISION OUT.
#
#
# ============================================================================


# ============================================================================
# PART III-B FUTURE TEST MATRIX
# ============================================================================
#
# These are architecture-contract tests.
#
# Some require future models that do not yet exist.
#
#
# ---------------------------------------------------------------------------
# TEST 1
#
# CURRENT BOOLEAN CAPABILITY
# ---------------------------------------------------------------------------
#
#
# capability_supported:
#
#       True
#
#
# Expected:
#
#
#       capability gate passes
#
#
# ---------------------------------------------------------------------------
# TEST 2
#
# CURRENT BOOLEAN CAPABILITY FAILURE
# ---------------------------------------------------------------------------
#
#
# capability_supported:
#
#       False
#
#
# Expected:
#
#
#       CAPABILITY_MISMATCH
#
#
# ---------------------------------------------------------------------------
# TEST 3
#
# FUTURE UNSUPPORTED CAPABILITY
# ---------------------------------------------------------------------------
#
#
# capability:
#
#       UNSUPPORTED
#
#
# Expected:
#
#
#       candidate rejected
#
#       CAPABILITY_MISMATCH
#
#
# ---------------------------------------------------------------------------
# TEST 4
#
# FUTURE UNKNOWN CAPABILITY
# ---------------------------------------------------------------------------
#
#
# capability:
#
#       UNKNOWN
#
#
# Expected:
#
#
#       candidate rejected
#
#       UNKNOWN
#
#
# NOT:
#
#
#       CAPABILITY_MISMATCH
#
#
# ---------------------------------------------------------------------------
# TEST 5
#
# ONE SERVICE / TWO DEPLOYMENTS
# ---------------------------------------------------------------------------
#
#
# service:
#
#       company-reasoning
#
#
# deployments:
#
#       azure-east
#
#       gcp-central
#
#
# Expected:
#
#
#       both retain the same logical service identity
#
#       deployments retain separate deployment identity
#
#
# ---------------------------------------------------------------------------
# TEST 6
#
# MULTI-CLOUD SAME ROUTING DOMAIN
# ---------------------------------------------------------------------------
#
#
# Azure deployment:
#
#       COMPANY_CLOUD_LLM
#
#
# GCP deployment:
#
#       COMPANY_CLOUD_LLM
#
#
# Expected:
#
#
#       no new AIRoute merely because provider differs
#
#
# ---------------------------------------------------------------------------
# TEST 7
#
# DIFFERENT DEPLOYMENT HEALTH
# ---------------------------------------------------------------------------
#
#
# Azure:
#
#       AVAILABLE
#
#
# GCP:
#
#       UNAVAILABLE
#
#
# Expected:
#
#
#       deployment facts remain independent
#
#
# ---------------------------------------------------------------------------
# TEST 8
#
# SERVICE ID != ENDPOINT ID
# ---------------------------------------------------------------------------
#
#
# service_id:
#
#       company-reasoning
#
#
# endpoint_id:
#
#       inference-private-east-01
#
#
# Expected:
#
#
#       relationship established explicitly
#
#       no equality requirement
#
#
# ---------------------------------------------------------------------------
# TEST 9
#
# CLOUD PROVIDER != PATH TYPE
# ---------------------------------------------------------------------------
#
#
# provider:
#
#       AZURE
#
#
# path:
#
#       PRIVATE_LINK
#
#
# Expected:
#
#
#       both facts coexist independently
#
#
# ---------------------------------------------------------------------------
# TEST 10
#
# AZURE OVER INTERNET
# ---------------------------------------------------------------------------
#
#
# provider:
#
#       AZURE
#
#
# path:
#
#       INTERNET
#
#
# Expected:
#
#
#       valid combination
#
#
# ---------------------------------------------------------------------------
# TEST 11
#
# GCP OVER VPN
# ---------------------------------------------------------------------------
#
#
# provider:
#
#       GCP
#
#
# path:
#
#       VPN
#
#
# Expected:
#
#
#       valid combination
#
#
# ---------------------------------------------------------------------------
# TEST 12
#
# MULTI-CLOUD SHARED FAILURE DOMAIN
# ---------------------------------------------------------------------------
#
#
# Azure candidate:
#
#       Carrier X
#
#
# GCP candidate:
#
#       Carrier X
#
#
# Expected:
#
#
#       CandidateEvaluator evaluates each individually
#
#       cross-candidate resilience belongs elsewhere
#
#
# ---------------------------------------------------------------------------
# TEST 13
#
# WRONG DEPLOYMENT/SERVICE RELATIONSHIP
# ---------------------------------------------------------------------------
#
#
# deployment.service_id:
#
#       service-b
#
#
# Candidate facts service:
#
#       service-a
#
#
# Expected:
#
#
#       relationship validation failure
#
#
# NOT:
#
#
#       routing rejection
#
#
# ---------------------------------------------------------------------------
# TEST 14
#
# WRONG ENDPOINT/DEPLOYMENT RELATIONSHIP
# ---------------------------------------------------------------------------
#
#
# endpoint belongs to:
#
#       deployment-b
#
#
# candidate deployment:
#
#       deployment-a
#
#
# Expected:
#
#
#       relationship validation failure
#
#
# ---------------------------------------------------------------------------
# TEST 15
#
# STALE NETWORK FACT
# ---------------------------------------------------------------------------
#
#
# network evidence:
#
#       historically AVAILABLE
#
#
# freshness:
#
#       expired
#
#
# Expected:
#
#
#       owning network subsystem does not present it
#       as current AVAILABLE evidence
#
#
# ---------------------------------------------------------------------------
# TEST 16
#
# MANY INPUT FACTS FORM STABLE AGGREGATE
# ---------------------------------------------------------------------------
#
#
# CandidateEvaluationFacts:
#
#       service
#       deployment
#       policy
#       capability
#       service state
#       network
#       suitability
#
#
# Expected:
#
#
#       aggregate validates relationships
#
#       CandidateEvaluator receives coherent facts
#
#
# ---------------------------------------------------------------------------
# TEST 17
#
# GENERIC CONTEXT BAG
# ---------------------------------------------------------------------------
#
#
# context:
#
#       dict[str, Any]
#
#
# Expected architectural conclusion:
#
#
#       NOT an acceptable substitute
#       for typed CandidateEvaluationFacts
#
#
# ============================================================================


# ============================================================================
# PART III-B IDENTITY TABLE
# ============================================================================
#
#
# AIModel
# -------
#
# Question:
#
#       WHAT model is this?
#
#
# Identity:
#
#       model_id
#
#
# ---------------------------------------------------------------------------
# AIService
# ---------------------------------------------------------------------------
#
# Question:
#
#       HOW is the model logically exposed?
#
#
# Identity:
#
#       service_id
#
#
# ---------------------------------------------------------------------------
# Deployment
# ---------------------------------------------------------------------------
#
# Question:
#
#       WHERE / in what runtime does the service instance exist?
#
#
# Future identity:
#
#       deployment_id
#
#
# ---------------------------------------------------------------------------
# NetworkEndpoint
# ---------------------------------------------------------------------------
#
# Question:
#
#       WHAT network destination exposes the deployment?
#
#
# Future/current identity:
#
#       endpoint_id / destination_id
#
#
# ---------------------------------------------------------------------------
# NetworkPath
# ---------------------------------------------------------------------------
#
# Question:
#
#       HOW is that destination reached?
#
#
# Identity:
#
#       path_id
#
#
# ============================================================================
#
#
#       MODEL ID
#           !=
#       SERVICE ID
#           !=
#       DEPLOYMENT ID
#           !=
#       ENDPOINT ID
#           !=
#       PATH ID
#
#
# ============================================================================


# ============================================================================
# PART III-B FINAL INVARIANTS
# ============================================================================
#
#
# TYPES
# -----
#
#
#       SIMPLE IS NOT IMMATURE
#
#
#       SIMPLE IS CORRECT
#       WHEN THE DOMAIN IS SIMPLE
#
#
#       DO NOT MODEL COMPLEXITY
#       BEFORE IT EXISTS
#
#
#       DO NOT HIDE COMPLEXITY
#       AFTER IT EXISTS
#
#
#       TYPE TOO SMALL
#           ->
#       INFORMATION LOSS
#
#
#       SAME ROUTING DISPOSITION
#           !=
#       SAME DOMAIN TRUTH
#
#
#       BOOL -> ENUM -> MODEL
#       WHEN DOMAIN PRESSURE EARNS IT
#
#
# ---------------------------------------------------------------------------
# IDENTITY
# ---------------------------------------------------------------------------
#
#
#       MODEL != SERVICE
#
#
#       SERVICE != DEPLOYMENT
#
#
#       DEPLOYMENT != ENDPOINT
#
#
#       ENDPOINT != PATH
#
#
#       SERVICE HEALTH
#           !=
#       DEPLOYMENT HEALTH
#
#
#       COMPONENT STATE
#           !=
#       AGGREGATE STATE
#
#
#       SERVICE IDENTITY
#           !=
#       NETWORK DESTINATION IDENTITY
#
#
#       RELATIONSHIP
#           >
#       STRING COINCIDENCE
#
#
#       DISPLAY NAME
#           !=
#       RESOURCE IDENTITY
#
#
#       IDENTITY
#       IS PART OF
#       DECISION CORRECTNESS
#
#
# ---------------------------------------------------------------------------
# MULTI-CLOUD
# ---------------------------------------------------------------------------
#
#
#       CLOUD PROVIDER
#           !=
#       ROUTING DOMAIN
#
#
#       TRUST DOMAIN
#           !=
#       HOSTING PROVIDER
#
#
#       DEPLOYMENT TOPOLOGY
#           !=
#       ROUTING POLICY DOMAIN
#
#
#       LOCATION
#           !=
#       AUTHORIZATION
#
#
#       WHERE IT RUNS
#           !=
#       HOW WE REACH IT
#
#
#       CLOUD PROVIDER
#           !=
#       PATH TYPE
#
#
#       DIFFERENT CLOUDS
#           !=
#       INDEPENDENT FAILURE
#
#
#       MULTI-PATH
#           !=
#       RESILIENCE
#
#
# ---------------------------------------------------------------------------
# CAPABILITY
# ---------------------------------------------------------------------------
#
#
#       UNSUPPORTED
#           !=
#       UNKNOWN
#
#
#       SAFE DISPOSITION
#           !=
#       COMPLETE REPRESENTATION
#
#
#       MODEL CAPABILITY
#           !=
#       DEPLOYMENT-EXPOSED CAPABILITY
#
#
# ---------------------------------------------------------------------------
# AGGREGATES
# ---------------------------------------------------------------------------
#
#
#       PARAMETER PRESSURE
#       CAN EARN A MODEL
#
#
#       AESTHETIC DISCOMFORT
#       DOES NOT
#
#
#       PARAMETER BAG
#           !=
#       DOMAIN AGGREGATE
#
#
#       THE RELATIONSHIPS THEMSELVES
#       CAN BECOME A DOMAIN CONCEPT
#
#
# ---------------------------------------------------------------------------
# TIME
# ---------------------------------------------------------------------------
#
#
#       SAME CANDIDATE
#           !=
#       SAME OBSERVATION TIME
#
#
#       STALE
#           !=
#       FALSE
#
#
#       FACT OWNER
#       SHOULD OWN
#       FACT FRESHNESS SEMANTICS
#
#
#       TIME IS A DEPENDENCY
#
#
# ---------------------------------------------------------------------------
# ROUTING
# ---------------------------------------------------------------------------
#
#
#       CANDIDATE VIABILITY
#           !=
#       DEPLOYMENT SELECTION
#
#
#       SINGLE-CANDIDATE VIABILITY
#           !=
#       CROSS-CANDIDATE RESILIENCE
#
#
# ---------------------------------------------------------------------------
# ARCHITECTURE
# ---------------------------------------------------------------------------
#
#
#       VENDOR COMPLEXITY
#       ENDS AT THE
#       ADAPTER BOUNDARY
#
#
#       MORE SOPHISTICATED SYSTEM
#       SHOULD PRODUCE
#       BETTER FACTS
#
#
#       NOT
#
#
#       A BIGGER GOD OBJECT
#
#
#       BETTER FACTS IN
#
#       SMALL DECISION OUT
#
#
# ============================================================================


# ============================================================================
# PART III-B FINAL CONTRACT
# ============================================================================
#
#
# As Agent 11 grows:
#
#
#       bool
#
# may become:
#
#
#       enum
#
#
# and later:
#
#
#       domain model
#
#
# ============================================================================
#
# A service may become:
#
#
#       one logical service
#
#           |
#           +---- deployment A
#           |
#           +---- deployment B
#           |
#           +---- deployment C
#
#
# ============================================================================
#
# Each deployment may have:
#
#
#       different provider
#
#       different region
#
#       different health
#
#       different endpoint
#
#       different network paths
#
#
# while still belonging to:
#
#
#       THE SAME AI ROUTING DOMAIN
#
#
# ============================================================================
#
# CandidateEvaluator must not respond to this complexity by learning:
#
#
#       Azure
#
#       GCP
#
#       AWS
#
#       OCI
#
#       Kubernetes
#
#       BGP
#
#       SD-WAN
#
#
# ============================================================================
#
# Instead:
#
#
#       RUNTIME / DEPLOYMENT SYSTEMS
#           produce
#       BETTER RUNTIME FACTS
#
#
#       NETWORK SYSTEMS
#           produce
#       BETTER NETWORK FACTS
#
#
#       CAPABILITY SYSTEMS
#           produce
#       BETTER CAPABILITY FACTS
#
#
#       POLICY SYSTEMS
#           produce
#       BETTER POLICY FACTS
#
#
# ============================================================================
#
# CandidateEvaluator continues doing something intentionally boring:
#
#
#       RECEIVE
#       COHERENT
#       NORMALIZED
#       DOMAIN FACTS
#
#           |
#           v
#
#       DETERMINE
#       SINGLE-CANDIDATE
#       VIABILITY
#
#
# ============================================================================
#
#
#       INFRASTRUCTURE COMPLEXITY
#       SHOULD INCREASE
#       THE QUALITY OF THE FACTS
#
#
#       NOT
#
#
#       THE NUMBER OF INFRASTRUCTURE
#       RESPONSIBILITIES INSIDE
#       CandidateEvaluator
#
#
# ============================================================================
# END COMPLETE PART III-B
# ============================================================================

# ============================================================================
# routing/candidate_evaluator.py
#
# COMPLETE PART III-C
#
# ARCHITECTURAL CONTAINMENT,
# SELECTION BOUNDARIES,
# FALLBACK,
# PROVENANCE,
# AND
# KEEPING CandidateEvaluator SMALL
# ============================================================================
#
# PURPOSE
# -------
#
# Parts III-A and III-B introduced significant future complexity.
#
#
# PART III-A
# ----------
#
# introduced:
#
#       path-specific policy
#
#       policy-compliant operational paths
#
#       workload suitability
#
#       measurements
#
#       expected vs realized paths
#
#
# PART III-B
# ----------
#
# introduced:
#
#       richer capability facts
#
#       deployment identity
#
#       multi-cloud deployments
#
#       endpoint identity
#
#       deployment-specific health
#
#       richer cross-domain relationships
#
#
# ============================================================================
#
# All of those concepts are legitimate.
#
#
# But they create a dangerous architectural temptation:
#
#
#       "CandidateEvaluator already has all these facts.
#
#        Why don't we just let it decide everything?"
#
#
# ============================================================================
#
# NO.
#
#
# That is exactly how small domain components become God objects.
#
#
# ============================================================================
# CENTRAL PART III-C RULE
# ============================================================================
#
#
#       CandidateEvaluator
#
#       ANSWERS ONE QUESTION:
#
#
#       "IS THIS ONE CANDIDATE VIABLE?"
#
#
# ============================================================================
#
# It does NOT answer:
#
#
#       "Which candidate should win?"
#
#
#       "Which model should we deploy?"
#
#
#       "Which cloud should we prefer?"
#
#
#       "Which packet path should the network use?"
#
#
#       "Should we retry the failed service?"
#
#
#       "Should we fall back to another service?"
#
#
#       "Which candidate gives us the best resilience?"
#
#
#       "Which candidate is cheapest?"
#
#
#       "Which candidate is fastest?"
#
#
# ============================================================================
#
#
#       VIABILITY
#           !=
#       SELECTION
#           !=
#       OPTIMIZATION
#           !=
#       FALLBACK
#           !=
#       RESILIENCE
#
#
# ============================================================================


# ============================================================================
# SECTION 1
#
# CandidateEvaluator != AIRouter
# ============================================================================
#
# CandidateEvaluator receives facts about:
#
#
#       ONE possible AI service
#
#
# and produces:
#
#
#       ONE RoutingCandidate
#
#
# ============================================================================
#
# Conceptually:
#
#
#       SERVICE A FACTS
#             |
#             v
#       CandidateEvaluator
#             |
#             v
#       RoutingCandidate A
#
#
#       SERVICE B FACTS
#             |
#             v
#       CandidateEvaluator
#             |
#             v
#       RoutingCandidate B
#
#
#       SERVICE C FACTS
#             |
#             v
#       CandidateEvaluator
#             |
#             v
#       RoutingCandidate C
#
#
# ============================================================================
#
# Only after those candidates exist does AIRouter receive:
#
#
#       A
#       B
#       C
#
#
# and answer:
#
#
#       "Which viable candidate should be selected?"
#
#
# ============================================================================
#
#
#       CandidateEvaluator
#           =
#       VIABILITY
#
#
#       AIRouter
#           =
#       SELECTION
#
#
# ============================================================================


# ============================================================================
# WHY CandidateEvaluator MUST NOT SELECT
# ============================================================================
#
# Suppose CandidateEvaluator receives:
#
#
#       service A
#
#
# It cannot know whether:
#
#
#       service B
#
#
#       service C
#
#
#       service D
#
#
# are better alternatives unless we give it information about those
# candidates too.
#
#
# ============================================================================
#
# The moment CandidateEvaluator starts comparing candidates, it is no longer
# evaluating one candidate.
#
#
# It has become a router.
#
#
# ============================================================================
#
#
#       SINGLE-CANDIDATE REASONING
#           !=
#       CROSS-CANDIDATE REASONING
#
#
# ============================================================================


# ============================================================================
# CURRENT AIRouter CONTRACT
# ============================================================================
#
# Current SEIR-I AIRouter intentionally receives already evaluated:
#
#
#       RoutingCandidate
#
#
# objects.
#
#
# It does NOT independently rerun:
#
#
#       policy
#
#       capability
#
#       service health
#
#       network reachability
#
#
# ============================================================================
#
# CandidateEvaluator establishes:
#
#
#       VIABLE
#
#
# or:
#
#
#       REJECTED
#
#
# AIRouter selects among:
#
#
#       VIABLE candidates
#
#
# ============================================================================
#
#
#       EVALUATE FIRST.
#
#
#       SELECT SECOND.
#
#
# ============================================================================


# ============================================================================
# SECTION 2
#
# HARD CONSTRAINTS != OPTIMIZATION
# ============================================================================
#
# CandidateEvaluator is primarily concerned with:
#
#
#       HARD CONSTRAINTS
#
#
# ============================================================================
#
# Examples:
#
#
#       policy permitted?
#
#       capability supported?
#
#       service operational?
#
#       compliant operational path exists?
#
#       workload suitable?
#
#
# ============================================================================
#
# These determine whether the candidate belongs in:
#
#
#       THE VIABLE SET
#
#
# ============================================================================


# ============================================================================
# OPTIMIZATION COMES LATER
# ============================================================================
#
# Once a viable set exists, another routing component may eventually compare:
#
#
#       cost
#
#       latency
#
#       token price
#
#       expected reasoning quality
#
#       queue depth
#
#       geographic preference
#
#       capacity
#
#       reliability
#
#       organizational preference
#
#
# ============================================================================
#
# Those properties may help choose:
#
#
#       WHICH VIABLE CANDIDATE
#
#
# should win.
#
#
# They must not resurrect:
#
#
#       A NON-VIABLE CANDIDATE
#
#
# ============================================================================
#
#
#       OPTIMIZATION
#       OPERATES INSIDE
#       THE VIABLE SET.
#
#
# ============================================================================


# ============================================================================
# THE WRONG MODEL
# ============================================================================
#
# Imagine:
#
#
#       External FM
#
#           policy:
#               DENY
#
#           capability:
#               excellent
#
#           latency:
#               20 ms
#
#           cost:
#               $0.01
#
#
#       Company On-Prem LLM
#
#           policy:
#               ALLOW
#
#           capability:
#               adequate
#
#           latency:
#               150 ms
#
#           cost:
#               $0.10
#
#
# ============================================================================
#
# A weighted score might calculate:
#
#
#       EXTERNAL:
#
#           policy        -100
#           capability     +50
#           latency        +40
#           cost           +40
#
#           TOTAL           +30
#
#
#       ON-PREM:
#
#           policy         +20
#           capability     +20
#           latency         +5
#           cost            +5
#
#           TOTAL           +50
#
#
# ============================================================================
#
# This particular weighting happened to choose on-prem.
#
#
# But change the weights slightly and the denied route might win.
#
#
# That means the model is fundamentally wrong.
#
#
# ============================================================================
#
#
#       POLICY IS NOT A PREFERENCE.
#
#
# ============================================================================


# ============================================================================
# CORRECT MODEL
# ============================================================================
#
#
#       ALL CANDIDATES
#             |
#             v
#       HARD CONSTRAINTS
#             |
#             v
#       VIABLE SET
#             |
#             v
#       SOFT PREFERENCES
#             |
#             v
#       OPTIMIZATION
#             |
#             v
#       SELECTION
#
#
# ============================================================================
#
#
#       FILTER FIRST.
#
#
#       OPTIMIZE SECOND.
#
#
# ============================================================================


# ============================================================================
# POLICY NEVER BECOMES A SCORE
# ============================================================================
#
# This invariant must survive every future routing optimization system.
#
#
# ============================================================================
#
#
#       DENY + FAST
#           !=
#       ALLOW
#
#
#       DENY + CHEAP
#           !=
#       ALLOW
#
#
#       DENY + BETTER MODEL
#           !=
#       ALLOW
#
#
#       DENY + LOW LATENCY
#           !=
#       ALLOW
#
#
# ============================================================================
#
# Chewbacca cannot collect enough latency, cost, and GPU bonus points to
# unlock an E9 Internet route.
#
#
# ============================================================================
#
#
#       POLICY NEVER BECOMES A SCORE.
#
#
# ============================================================================


# ============================================================================
# SECTION 3
#
# REJECTION REASON != COMPLETE DIAGNOSIS
# ============================================================================
#
# Current RoutingCandidate contains:
#
#
#       status
#
#       rejection_reason
#
#
# ============================================================================
#
# The rejection reason is intentionally singular.
#
#
# Example:
#
#
#       POLICY_DENIED
#
#
# ============================================================================
#
# This tells AIRouter:
#
#
#       why this candidate failed the deterministic viability funnel
#
#
# ============================================================================
#
# It does NOT necessarily describe every problem with the candidate.
#
#
# ============================================================================


# ============================================================================
# EXAMPLE
# ============================================================================
#
# Candidate facts:
#
#
#       policy:
#           DENY
#
#
#       capability:
#           unsupported
#
#
#       service:
#           UNAVAILABLE
#
#
#       network:
#           UNAVAILABLE
#
#
# ============================================================================
#
# Current deterministic precedence:
#
#
#       POLICY
#           ->
#       CAPABILITY
#           ->
#       SERVICE
#           ->
#       NETWORK
#
#
# Therefore:
#
#
#       rejection_reason
#           =
#       POLICY_DENIED
#
#
# ============================================================================
#
# Does that mean:
#
#
#       capability was supported?
#
#
# No.
#
#
# Does it mean:
#
#
#       service was healthy?
#
#
# No.
#
#
# Does it mean:
#
#
#       network was available?
#
#
# No.
#
#
# ============================================================================
#
#
#       ROUTING-DISPOSITIVE REASON
#           !=
#       COMPLETE SYSTEM DIAGNOSIS
#
#
# ============================================================================


# ============================================================================
# WHY KEEP ONE REJECTION REASON FOR SEIR-I?
# ============================================================================
#
# Because AIRouter does not need:
#
#
#       a forensic incident report
#
#
# to determine:
#
#
#       whether this candidate is viable
#
#
# ============================================================================
#
# One deterministic rejection reason gives us:
#
#
#       predictable behavior
#
#       simple tests
#
#       understandable telemetry
#
#       stable routing semantics
#
#
# ============================================================================
#
# The detailed evidence already exists in the owning subsystems.
#
#
# ============================================================================


# ============================================================================
# FUTURE RICHER PROVENANCE
# ============================================================================
#
# SEIR-II may eventually need richer explanation.
#
#
# For example:
#
#
#       candidate rejected
#
#
#       routing-dispositive reason:
#           POLICY_DENIED
#
#
#       additional observations:
#
#           capability mismatch
#
#           service unavailable
#
#           private path unavailable
#
#
# ============================================================================
#
# That does NOT require changing:
#
#
#       rejection_reason
#
#
# into:
#
#
#       list[RoutingRejectionReason]
#
#
# immediately.
#
#
# ============================================================================
#
# A richer provenance object may eventually earn existence.
#
#
# ============================================================================


# ============================================================================
# POSSIBLE FUTURE CONCEPT
#
# CandidateEvaluationTrace
# ============================================================================
#
# CONCEPTUAL ONLY.
#
# DO NOT IMPLEMENT YET.
#
#
# Something like:
#
#
# class CandidateEvaluationTrace(Agent11BaseModel):
#
#     service_id: str
#
#     routing_disposition: RoutingCandidateStatus
#
#     routing_reason: RoutingRejectionReason | None
#
#     policy_result: ...
#
#     capability_result: ...
#
#     service_result: ...
#
#     network_result: ...
#
#     suitability_result: ...
#
#
# ============================================================================
#
# This would preserve:
#
#
#       ROUTING DISPOSITION
#
#
# separately from:
#
#
#       DIAGNOSTIC PROVENANCE
#
#
# ============================================================================
#
#
#       DECISION
#           !=
#       EXPLANATION RECORD
#
#
# ============================================================================


# ============================================================================
# WHY NOT list[rejection_reason]?
# ============================================================================
#
# Suppose:
#
#
#       [
#           POLICY_DENIED,
#           CAPABILITY_MISMATCH,
#           SERVICE_UNAVAILABLE,
#           NETWORK_UNAVAILABLE,
#       ]
#
#
# ============================================================================
#
# Now another component has to ask:
#
#
#       "Which one actually determined routing behavior?"
#
#
# ============================================================================
#
# We have weakened the meaning of:
#
#
#       rejection_reason
#
#
# ============================================================================
#
# Better:
#
#
#       routing_reason
#           =
#       POLICY_DENIED
#
#
# while detailed evidence remains available separately.
#
#
# ============================================================================
#
#
#       PRIMARY DECISION REASON
#           !=
#       ALL OBSERVED PROBLEMS
#
#
# ============================================================================


# ============================================================================
# SECTION 4
#
# CandidateEvaluator != RESILIENCE ENGINE
# ============================================================================
#
# Part III-B introduced:
#
#
#       Azure deployment
#
#       GCP deployment
#
#       AWS deployment
#
#
# ============================================================================
#
# It also established:
#
#
#       DIFFERENT CLOUDS
#           !=
#       INDEPENDENT FAILURE
#
#
# ============================================================================
#
# CandidateEvaluator cannot determine:
#
#
#       cross-candidate resilience
#
#
# while evaluating:
#
#
#       one candidate
#
#
# ============================================================================


# ============================================================================
# EXAMPLE
# ============================================================================
#
#
#       Candidate A
#           Azure
#           Carrier X
#
#
#       Candidate B
#           GCP
#           Carrier X
#
#
#       Candidate C
#           On-Prem
#           Carrier Y
#
#
# ============================================================================
#
# Each candidate may individually be:
#
#
#       VIABLE
#
#
# ============================================================================
#
# But if we are choosing:
#
#
#       PRIMARY
#
#
# and:
#
#
#       FALLBACK
#
#
# we might prefer:
#
#
#       A + C
#
#
# rather than:
#
#
#       A + B
#
#
# because A and B share a failure domain.
#
#
# ============================================================================
#
# That requires comparing candidates.
#
#
# Therefore:
#
#
#       NOT CandidateEvaluator
#
#
# ============================================================================


# ============================================================================
# FAILURE DOMAIN IS A CROSS-CANDIDATE CONCERN
# ============================================================================
#
# Possible future facts:
#
#
#       cloud provider
#
#       region
#
#       identity provider
#
#       carrier
#
#       DNS dependency
#
#       control plane
#
#       secret store
#
#       upstream data source
#
#
# ============================================================================
#
# But:
#
#
#       CORRELATION
#
#
# must not be inferred merely because two strings look similar.
#
#
# ============================================================================
#
#
#       SHARED ATTRIBUTE
#           !=
#       PROVEN SHARED FAILURE DOMAIN
#
#
# ============================================================================
#
# Likewise:
#
#
#       different provider
#
#
# does not prove:
#
#
#       independent failure
#
#
# ============================================================================
#
#
#       CORRELATION
#           !=
#       PROVEN DEPENDENCY
#
#
# ============================================================================


# ============================================================================
# FAILURE-DOMAIN MODELING MUST BE EARNED
# ============================================================================
#
# We have architectural pressure for:
#
#
#       FailureDomain
#
#
# or:
#
#
#       DependencyRelationship
#
#
# ============================================================================
#
# But those models have NOT yet earned implementation.
#
#
# Why?
#
#
# Because we currently lack sufficiently established runtime relationships
# to prove those dependencies.
#
#
# ============================================================================
#
#
#       PATH COUNT
#           !=
#       FAILURE-DOMAIN COUNT
#
#
#       MULTI-CLOUD
#           !=
#       RESILIENCE
#
#
# ============================================================================


# ============================================================================
# SECTION 5
#
# FALLBACK != INITIAL SELECTION
# ============================================================================
#
# This distinction is critical.
#
#
# Suppose the initial candidate list is:
#
#
#       A = REJECTED
#
#       B = VIABLE
#
#       C = VIABLE
#
#
# AIRouter selects:
#
#
#       B
#
#
# ============================================================================
#
# Did Agent 11 "fall back" from A to B?
#
#
# No.
#
#
# ============================================================================
#
# A was never selected.
#
#
# The router simply selected the first viable candidate.
#
#
# ============================================================================
#
#
#       SKIPPING A REJECTED CANDIDATE
#           !=
#       RUNTIME FALLBACK
#
#
# ============================================================================


# ============================================================================
# WHAT FALLBACK ACTUALLY MEANS
# ============================================================================
#
# Runtime fallback occurs after:
#
#
#       candidate B was selected
#
#
# and:
#
#
#       an invocation or runtime attempt failed
#
#
# ============================================================================
#
# Now Agent 11 may ask:
#
#
#       "May we begin another routing attempt
#        using another candidate?"
#
#
# ============================================================================
#
# That is fallback.
#
#
# ============================================================================


# ============================================================================
# FallbackEvaluator HAS A SMALL CONTRACT TOO
# ============================================================================
#
# Current conceptual responsibility:
#
#
#       "Is another routing cycle permitted
#        under the configured fallback strategy?"
#
#
# ============================================================================
#
# It does NOT answer:
#
#
#       "Which candidate should be selected?"
#
#
# ============================================================================
#
# That remains AIRouter's responsibility after fresh candidate evaluation.
#
#
# ============================================================================
#
#
#       FALLBACK ELIGIBILITY
#           !=
#       FALLBACK SELECTION
#
#
# ============================================================================


# ============================================================================
# WHY FALLBACK MUST RE-EVALUATE
# ============================================================================
#
# Suppose at:
#
#
#       10:00:00
#
#
# Candidate C was:
#
#
#       VIABLE
#
#
# ============================================================================
#
# Candidate B is selected.
#
#
# Invocation B fails at:
#
#
#       10:00:30
#
#
# ============================================================================
#
# Can we simply use the old:
#
#
#       C = VIABLE
#
#
# result?
#
#
# Not safely.
#
#
# ============================================================================
#
# During those 30 seconds:
#
#
#       policy may have changed
#
#       user restrictions may have changed
#
#       service C may have failed
#
#       network C may have failed
#
#       deployment C may have changed
#
#       path policy may have changed
#
#       workload suitability may have changed
#
#
# ============================================================================
#
#
#       HISTORICAL VIABILITY
#           !=
#       CURRENT VIABILITY
#
#
# ============================================================================


# ============================================================================
# CORRECT FALLBACK LOOP
# ============================================================================
#
#
#       SELECT B
#           |
#           v
#       INVOKE B
#           |
#           v
#       FAILURE
#           |
#           v
#       FALLBACK ALLOWED?
#           |
#           v
#       REOBSERVE / RE-EVALUATE
#           |
#           v
#       NEW RoutingCandidates
#           |
#           v
#       AIRouter
#           |
#           v
#       SELECT NEXT VIABLE
#
#
# ============================================================================
#
#
#       FALLBACK
#       REUSES THE RULES.
#
#
#       FALLBACK
#       DOES NOT BYPASS THE RULES.
#
#
# ============================================================================


# ============================================================================
# FALLBACK NEVER LOWERS SECURITY
# ============================================================================
#
# Imagine:
#
#
#       E9 request
#
#
# Initial:
#
#
#       COMPANY_ONPREM_LLM
#           =
#       selected
#
#
# On-prem fails.
#
#
# ============================================================================
#
# Available alternatives:
#
#
#       COMPANY_CLOUD_LLM
#
#       EXTERNAL_FM
#
#
# ============================================================================
#
# If policy says:
#
#
#       E9:
#
#           COMPANY_CLOUD_LLM = DENY
#
#           EXTERNAL_FM       = DENY
#
#
# then fallback result is:
#
#
#       NO VIABLE ROUTE
#
#
# ============================================================================
#
# NOT:
#
#
#       "Well, this is an emergency.
#        Let's use the external FM."
#
#
# ============================================================================
#
#
#       FALLBACK MODE
#           !=
#       LOWER SECURITY MODE
#
#
# ============================================================================


# ============================================================================
# AVAILABILITY MAY DECREASE
#
# POLICY DOES NOT
# ============================================================================
#
# A secure failover design sometimes means:
#
#
#       the request fails
#
#
# ============================================================================
#
# That may be the correct system behavior.
#
#
# ============================================================================
#
#
#       AVAILABILITY LOSS
#           CAN BE
#       SUCCESSFUL POLICY ENFORCEMENT
#
#
# ============================================================================


# ============================================================================
# NO ROUTE CAN BE SUCCESS
# ============================================================================
#
# From an application perspective:
#
#
#       NO_VIABLE_ROUTE
#
#
# may look like failure.
#
#
# From a security-control perspective:
#
#
#       refusing to send E9 data to a prohibited external service
#
#
# is successful enforcement.
#
#
# ============================================================================
#
#
#       REQUEST FAILURE
#           !=
#       CONTROL FAILURE
#
#
# ============================================================================


# ============================================================================
# RETRY != FALLBACK
# ============================================================================
#
# Suppose:
#
#
#       service B
#
#
# returns a transient error.
#
#
# Retrying:
#
#
#       service B
#
#
# is:
#
#
#       RETRY
#
#
# ============================================================================
#
# Trying:
#
#
#       service C
#
#
# is:
#
#
#       FALLBACK
#
#
# ============================================================================
#
#
#       RETRY SAME TARGET
#           !=
#       FALLBACK DIFFERENT TARGET
#
#
# ============================================================================


# ============================================================================
# INVOCATION FAILURE != SERVICE FAILURE
# ============================================================================
#
# This is why our fallback state should remember:
#
#
#       attempted_service_ids
#
#
# rather than automatically calling them:
#
#
#       failed_service_ids
#
#
# ============================================================================
#
# One invocation may fail because of:
#
#
#       malformed request
#
#       transient timeout
#
#       provider rejection
#
#       token limit
#
#       application error
#
#
# without proving:
#
#
#       THE SERVICE IS DOWN
#
#
# ============================================================================
#
#
#       ATTEMPT FAILED
#           !=
#       SERVICE FAILED
#
#
# ============================================================================


# ============================================================================
# SECTION 6
#
# NETWORK FAILOVER != AI FALLBACK
# ============================================================================
#
# Suppose:
#
#
#       private-link-a
#
#
# fails.
#
#
# SD-WAN or ordinary routing may steer traffic onto:
#
#
#       vpn-a
#
#
# ============================================================================
#
# That may happen without Agent 11 changing:
#
#
#       AIService
#
#
# at all.
#
#
# ============================================================================
#
# This is:
#
#
#       NETWORK FAILOVER
#
#
# not necessarily:
#
#
#       AI ROUTING FALLBACK
#
#
# ============================================================================
#
#
#       NETWORK FAILOVER
#           !=
#       AI FALLBACK
#
#
# ============================================================================


# ============================================================================
# NETWORK CONVERGENCE != POLICY-COMPLIANT RECOVERY
# ============================================================================
#
# Imagine:
#
#
#       approved private path fails
#
#
# Network converges onto:
#
#
#       Internet
#
#
# Connectivity is restored.
#
#
# ============================================================================
#
# But E9 policy prohibits Internet transit.
#
#
# ============================================================================
#
# From the network's perspective:
#
#
#       RECOVERED
#
#
# From Agent 11's policy perspective:
#
#
#       NOT ACCEPTABLE
#
#
# ============================================================================
#
#
#       NETWORK CONVERGENCE
#           !=
#       POLICY-COMPLIANT RECOVERY
#
#
# ============================================================================


# ============================================================================
# SD-WAN BEST PATH != AGENT 11 BEST AI ROUTE
# ============================================================================
#
# SD-WAN may optimize:
#
#
#       latency
#
#       jitter
#
#       loss
#
#       circuit preference
#
#
# ============================================================================
#
# Agent 11 may optimize:
#
#
#       policy compliance
#
#       capability
#
#       model suitability
#
#       service availability
#
#       cost
#
#       AI quality
#
#
# ============================================================================
#
# They are different decision domains.
#
#
# ============================================================================
#
#
#       SD-WAN BEST PATH
#           !=
#       AGENT 11 BEST AI ROUTE
#
#
# ============================================================================


# ============================================================================
# BGP BEST PATH != AGENT 11 BEST AI ROUTE
# ============================================================================
#
# BGP may choose a route based on:
#
#
#       LOCAL_PREF
#
#       AS_PATH
#
#       MED
#
#       route policy
#
#       next-hop reachability
#
#
# ============================================================================
#
# Agent 11 must not interpret those as AI routing preferences.
#
#
# ============================================================================
#
#
#       BGP LOCAL_PREF
#           !=
#       AI ROUTING PREFERENCE
#
#
#       BGP BEST PATH
#           !=
#       AI BEST CANDIDATE
#
#
# ============================================================================


# ============================================================================
# SECTION 7
#
# ROUTE SUCCESS != APPLICATION SUCCESS
# ============================================================================
#
# Future Agent 11 troubleshooting must preserve several layers.
#
#
# ============================================================================
#
#
#       ROUTE PRESENT
#           |
#           v
#       DATA-PLANE CONNECTIVITY
#           |
#           v
#       TRANSPORT
#           |
#           v
#       TLS
#           |
#           v
#       APPLICATION
#           |
#           v
#       AI SERVICE
#
#
# ============================================================================
#
# Success at one layer does not prove success at the next.
#
#
# ============================================================================


# ============================================================================
# IMPORTANT INVARIANTS
# ============================================================================
#
#
#       ROUTE SUCCESS
#           !=
#       DATA-PLANE SUCCESS
#
#
#       DATA-PLANE SUCCESS
#           !=
#       TRANSPORT SUCCESS
#
#
#       TRANSPORT SUCCESS
#           !=
#       TLS SUCCESS
#
#
#       TLS SUCCESS
#           !=
#       APPLICATION SUCCESS
#
#
#       NETWORK AVAILABILITY
#           !=
#       SERVICE AVAILABILITY
#
#
# ============================================================================
#
# This is another reason CandidateEvaluator should consume normalized facts
# rather than troubleshooting the entire stack itself.
#
#
# ============================================================================


# ============================================================================
# SECTION 8
#
# TELEMETRY != DECISION LOGIC
# ============================================================================
#
# Agent 11 should eventually record:
#
#
#       request identity
#
#       classification
#
#       policy decisions
#
#       candidate evaluations
#
#       rejection reasons
#
#       selected service
#
#       fallback attempts
#
#       network assessments
#
#       service assessments
#
#       invocation results
#
#
# ============================================================================
#
# This is extremely valuable.
#
#
# But telemetry should observe:
#
#
#       decisions
#
#
# rather than secretly becoming:
#
#
#       the decision engine
#
#
# ============================================================================
#
#
#       TELEMETRY
#           !=
#       CONTROL LOGIC
#
#
# ============================================================================


# ============================================================================
# STRUCTURED FACTS FIRST
#
# HUMAN EXPLANATION SECOND
# ============================================================================
#
# Bad telemetry:
#
#
#       "The AI route wasn't good enough."
#
#
# ============================================================================
#
# Better:
#
#
#       candidate_status:
#           REJECTED
#
#
#       rejection_reason:
#           POLICY_DENIED
#
#
#       service_id:
#           external-fm-primary
#
#
#       routing_domain:
#           EXTERNAL_FM
#
#
# ============================================================================
#
# Then a human explanation can be generated:
#
#
#       "The external reasoning service was rejected because
#        organizational policy prohibits this routing domain
#        for the request's data classification."
#
#
# ============================================================================
#
#
#       STRUCTURED FACT
#           FIRST
#
#
#       HUMAN NARRATIVE
#           SECOND
#
#
# ============================================================================


# ============================================================================
# WHY THIS MATTERS FOR AI-GENERATED EXPLANATIONS
# ============================================================================
#
# Eventually Agent 11 may use an LLM to explain:
#
#
#       why a route was selected
#
#
# ============================================================================
#
# The LLM should explain:
#
#
#       established structured facts
#
#
# rather than inventing:
#
#
#       the routing decision itself
#
#
# ============================================================================
#
#
#       AI EXPLANATION
#           !=
#       AI AUTHORIZATION
#
#
# ============================================================================


# ============================================================================
# SECTION 9
#
# CandidateEvaluator != ORCHESTRATOR
# ============================================================================
#
# CandidateEvaluator evaluates:
#
#
#       ONE candidate
#
#
# ============================================================================
#
# Something else must coordinate:
#
#
#       policy evaluation
#
#       capability evaluation
#
#       service observation
#
#       network observation
#
#       candidate evaluation
#
#       routing
#
#       invocation
#
#       fallback
#
#       telemetry
#
#
# ============================================================================
#
# That responsibility belongs to:
#
#
#       orchestrators
#
#
# ============================================================================


# ============================================================================
# ROUTING ORCHESTRATOR
# ============================================================================
#
# Future routing coordination may conceptually resemble:
#
#
#       for service in candidate_services:
#
#           gather established facts
#
#           candidate = candidate_evaluator.evaluate(...)
#
#           candidates.append(candidate)
#
#
#       decision = router.select(candidates)
#
#
# ============================================================================
#
# The orchestrator controls:
#
#
#       SEQUENCE
#
#
# CandidateEvaluator controls:
#
#
#       VIABILITY SEMANTICS
#
#
# AIRouter controls:
#
#
#       SELECTION SEMANTICS
#
#
# ============================================================================
#
#
#       ORCHESTRATION
#           !=
#       DOMAIN DECISION
#
#
# ============================================================================


# ============================================================================
# TOP-LEVEL AGENT 11 ORCHESTRATOR
# ============================================================================
#
# Eventually:
#
#
#       agent11/orchestrator.py
#
#
# coordinates the complete request lifecycle.
#
#
# ============================================================================
#
# Conceptually:
#
#
#       REQUEST
#           |
#           v
#       CLASSIFICATION
#           |
#           v
#       POLICY
#           |
#           v
#       SERVICE / MODEL FACTS
#           |
#           v
#       NETWORK FACTS
#           |
#           v
#       CANDIDATE EVALUATION
#           |
#           v
#       ROUTING
#           |
#           v
#       INVOCATION
#           |
#           v
#       RESPONSE
#
#
# ============================================================================
#
# CandidateEvaluator remains one small box in that larger system.
#
#
# ============================================================================


# ============================================================================
# SECTION 10
#
# OBSERVATION != REMEDIATION
# ============================================================================
#
# Agent 11 may eventually discover:
#
#
#       service unavailable
#
#       route missing
#
#       path degraded
#
#       Kubernetes deployment unhealthy
#
#
# ============================================================================
#
# That does NOT mean CandidateEvaluator should:
#
#
#       restart pods
#
#       modify BGP
#
#       change SD-WAN policy
#
#       create cloud endpoints
#
#       modify firewall rules
#
#
# ============================================================================
#
#
#       OBSERVE
#           !=
#       EXECUTE
#
#
# ============================================================================


# ============================================================================
# SAFE FUTURE CONTROL LOOP
# ============================================================================
#
# If Agent 11 eventually receives remediation authority, the architecture
# should resemble:
#
#
#       OBSERVE
#           |
#           v
#       REASON
#           |
#           v
#       PROPOSE
#           |
#           v
#       POLICY GATE
#           |
#           v
#       APPROVAL
#           |
#           v
#       SCOPED EXECUTION
#           |
#           v
#       VERIFY
#           |
#           v
#       AUDIT
#
#
# ============================================================================
#
# Not:
#
#
#       "LLM thinks BGP looks funny."
#
#           |
#           v
#
#       CHANGE PRODUCTION ROUTING
#
#
# ============================================================================
#
#
#       CORRECT REASONING
#           !=
#       EXECUTION AUTHORITY
#
#
# ============================================================================


# ============================================================================
# EXECUTION SUCCESS != OUTCOME SUCCESS
# ============================================================================
#
# Suppose a future remediation tool successfully executes:
#
#
#       restart deployment
#
#
# ============================================================================
#
# Tool result:
#
#
#       command succeeded
#
#
# ============================================================================
#
# That does not prove:
#
#
#       AI service recovered
#
#
# ============================================================================
#
# Therefore the control loop requires:
#
#
#       VERIFY
#
#
# ============================================================================
#
#
#       EXECUTION SUCCESS
#           !=
#       OUTCOME SUCCESS
#
#
# ============================================================================


# ============================================================================
# SECTION 11
#
# UNKNOWN MUST NOT BECOME AN OPTIMIZATION PENALTY
# ============================================================================
#
# Suppose:
#
#
#       candidate A:
#           network AVAILABLE
#
#
#       candidate B:
#           network UNKNOWN
#
#
# ============================================================================
#
# Do NOT calculate:
#
#
#       A network score = 100
#
#       B network score = 30
#
#
# and allow B to compensate through:
#
#
#       lower cost
#
#       better model
#
#       lower latency
#
#
# ============================================================================
#
# If network viability cannot be established:
#
#
#       candidate B is not in the viable set
#
#
# ============================================================================
#
#
#       UNKNOWN HARD CONSTRAINT
#           !=
#       LOW SOFT SCORE
#
#
# ============================================================================


# ============================================================================
# RESTRICT MUST NOT BECOME A PENALTY EITHER
# ============================================================================
#
# Current policy:
#
#
#       RESTRICT
#
#
# cannot establish viability because typed restriction details have not yet
# been modeled.
#
#
# ============================================================================
#
# Do NOT interpret:
#
#
#       RESTRICT
#
#
# as:
#
#
#       "ALLOW, but subtract 20 points."
#
#
# ============================================================================
#
#
#       RESTRICT
#           !=
#       WEAK ALLOW
#
#
# ============================================================================


# ============================================================================
# SECTION 12
#
# CONCURRENCY CHANGES EXECUTION
#
# NOT SEMANTICS
# ============================================================================
#
# Current educational implementations may evaluate candidates sequentially.
#
#
# Future production Agent 11 may gather:
#
#
#       service facts
#
#       network facts
#
#       capability facts
#
#
# concurrently.
#
#
# ============================================================================
#
# That is an execution optimization.
#
#
# It does not change:
#
#
#       policy precedence
#
#       viability semantics
#
#       relationship integrity
#
#       fail-closed behavior
#
#
# ============================================================================
#
#
#       EXECUTION STRATEGY
#           !=
#       DOMAIN SEMANTICS
#
#
# ============================================================================


# ============================================================================
# EXAMPLE
# ============================================================================
#
# Sequential:
#
#
#       evaluate A
#
#       evaluate B
#
#       evaluate C
#
#
# ============================================================================
#
# Concurrent:
#
#
#       +--> evaluate A
#
#       +--> evaluate B
#
#       +--> evaluate C
#
#
# ============================================================================
#
# Both should produce equivalent:
#
#
#       RoutingCandidate
#
#
# facts given equivalent inputs.
#
#
# ============================================================================


# ============================================================================
# SECTION 13
#
# ADAPTER FAILURE != DOMAIN FAILURE
# ============================================================================
#
# Future adapters may query:
#
#
#       Kubernetes
#
#       Azure
#
#       AWS
#
#       GCP
#
#       OCI
#
#       SD-WAN controllers
#
#       routing systems
#
#
# ============================================================================
#
# Vendor-specific failures should be normalized at:
#
#
#       ADAPTER / EVIDENCE BOUNDARIES
#
#
# ============================================================================
#
# Example:
#
#
#       Kubernetes API timeout
#
#
# may become:
#
#
#       service observation UNKNOWN
#
#
# ============================================================================
#
# But CandidateEvaluator should never catch:
#
#
#       KubernetesApiException
#
#
# because CandidateEvaluator should not know Kubernetes exists.
#
#
# ============================================================================
#
#
#       INFRASTRUCTURE FAILURE
#       SHOULD BECOME
#       DOMAIN EVIDENCE
#       BEFORE REACHING ROUTING.
#
#
# ============================================================================


# ============================================================================
# PROGRAMMING ERRORS STILL ESCAPE
# ============================================================================
#
# Do not convert:
#
#
#       AttributeError
#
#       TypeError
#
#       broken invariant
#
#       impossible identity relationship
#
#
# into:
#
#
#       UNKNOWN
#
#
# ============================================================================
#
# This Part II invariant remains.
#
#
# ============================================================================
#
#
#       DOMAIN UNCERTAINTY
#           !=
#       PROGRAMMING FAILURE
#
#
# ============================================================================


# ============================================================================
# SECTION 14
#
# THE SMALLNESS TEST
# ============================================================================
#
# As CandidateEvaluator evolves, ask:
#
#
#       "Does this new logic help answer:
#
#        IS THIS ONE CANDIDATE VIABLE?"
#
#
# ============================================================================
#
# If YES:
#
#
#       CandidateEvaluator may be appropriate.
#
#
# If the new logic instead answers:
#
#
#       Which candidate wins?
#
#       Which deployment should be selected?
#
#       Which packet path should be used?
#
#       How should we retry?
#
#       How should we remediate?
#
#       Which cloud is cheapest?
#
#       Which pair gives best redundancy?
#
#
# ============================================================================
#
# then:
#
#
#       IT BELONGS SOMEWHERE ELSE.
#
#
# ============================================================================


# ============================================================================
# THE INFRASTRUCTURE-IMPORT TEST
# ============================================================================
#
# Another useful warning sign:
#
#
# If candidate_evaluator.py eventually imports:
#
#
#       boto3
#
#       azure.*
#
#       google.cloud.*
#
#       kubernetes
#
#       Cisco SDKs
#
#       BGP parsers
#
#
# ============================================================================
#
# something has almost certainly gone wrong architecturally.
#
#
# ============================================================================
#
# CandidateEvaluator should understand:
#
#
#       DOMAIN FACTS
#
#
# not:
#
#
#       VENDOR IMPLEMENTATIONS
#
#
# ============================================================================


# ============================================================================
# THE SCORING TEST
# ============================================================================
#
# If CandidateEvaluator starts containing:
#
#
#       score += ...
#
#
# ask:
#
#
#       "Are we evaluating hard viability
#        or optimizing among viable choices?"
#
#
# ============================================================================
#
# If it is optimization:
#
#
#       MOVE IT DOWNSTREAM.
#
#
# ============================================================================


# ============================================================================
# THE MULTIPLE-CANDIDATE TEST
# ============================================================================
#
# If a piece of logic requires knowledge of:
#
#
#       candidate A
#
# and:
#
#       candidate B
#
#
# to make its decision:
#
#
# it probably does NOT belong in CandidateEvaluator.
#
#
# ============================================================================
#
#
#       ONE-CANDIDATE FACT
#           ->
#       CandidateEvaluator MAY own it.
#
#
#       CROSS-CANDIDATE FACT
#           ->
#       CandidateEvaluator probably DOES NOT.
#
#
# ============================================================================


# ============================================================================
# THE CONTROL TEST
# ============================================================================
#
# If code:
#
#
#       changes infrastructure
#
#
# it definitely does not belong in:
#
#
#       CandidateEvaluator
#
#
# ============================================================================
#
#
#       EVALUATION
#           !=
#       REMEDIATION
#
#
# ============================================================================


# ============================================================================
# PART III-C FUTURE TEST MATRIX
# ============================================================================
#
#
# ---------------------------------------------------------------------------
# TEST 1
#
# TWO VIABLE CANDIDATES
# ---------------------------------------------------------------------------
#
#
# A:
#
#       VIABLE
#
#
# B:
#
#       VIABLE
#
#
# Expected:
#
#
#       CandidateEvaluator evaluates independently
#
#       AIRouter selects
#
#
# ---------------------------------------------------------------------------
# TEST 2
#
# DENIED BUT CHEAPER
# ---------------------------------------------------------------------------
#
#
# A:
#
#       policy DENY
#       cost excellent
#
#
# B:
#
#       policy ALLOW
#       cost higher
#
#
# Expected:
#
#
#       A rejected before optimization
#
#
# ---------------------------------------------------------------------------
# TEST 3
#
# DENIED BUT FASTER
# ---------------------------------------------------------------------------
#
#
# Expected:
#
#
#       DENY remains DENY
#
#
# ---------------------------------------------------------------------------
# TEST 4
#
# MULTIPLE FAILURES
# ---------------------------------------------------------------------------
#
#
# Candidate:
#
#       policy DENY
#       capability mismatch
#       service unavailable
#       network unavailable
#
#
# Expected:
#
#
#       routing rejection reason:
#           POLICY_DENIED
#
#
# Detailed subsystem evidence may retain all other facts.
#
#
# ---------------------------------------------------------------------------
# TEST 5
#
# INITIAL REJECTED CANDIDATE SKIPPED
# ---------------------------------------------------------------------------
#
#
# A:
#
#       REJECTED
#
#
# B:
#
#       VIABLE
#
#
# Expected:
#
#
#       B selected
#
#       this is NOT runtime fallback
#
#
# ---------------------------------------------------------------------------
# TEST 6
#
# SELECTED SERVICE INVOCATION FAILS
# ---------------------------------------------------------------------------
#
#
# B:
#
#       selected
#
#       invocation attempted
#       invocation fails
#
#
# Expected:
#
#
#       fallback may now be considered
#
#
# ---------------------------------------------------------------------------
# TEST 7
#
# FALLBACK WITH STALE HISTORICAL CANDIDATE
# ---------------------------------------------------------------------------
#
#
# C:
#
#       VIABLE 30 seconds ago
#
#
# Expected:
#
#
#       do not trust historical viability
#
#       reobserve / reevaluate
#
#
# ---------------------------------------------------------------------------
# TEST 8
#
# FALLBACK WOULD REQUIRE POLICY VIOLATION
# ---------------------------------------------------------------------------
#
#
# Initial on-prem service fails.
#
#
# External FM:
#
#       AVAILABLE
#       policy DENY
#
#
# Expected:
#
#
#       NO VIABLE ROUTE
#
#
# ---------------------------------------------------------------------------
# TEST 9
#
# RETRY SAME SERVICE
# ---------------------------------------------------------------------------
#
#
# B fails once.
#
# B attempted again.
#
#
# Expected:
#
#
#       retry
#
#       not fallback to another service
#
#
# ---------------------------------------------------------------------------
# TEST 10
#
# INVOCATION FAILURE
# ---------------------------------------------------------------------------
#
#
# B invocation fails.
#
#
# Expected:
#
#
#       record B as attempted
#
#       do not automatically assert
#       ServiceState.UNAVAILABLE
#
#
# ---------------------------------------------------------------------------
# TEST 11
#
# NETWORK FAILOVER
# ---------------------------------------------------------------------------
#
#
# private path fails
#
# SD-WAN moves traffic to VPN
#
# same AI service remains selected
#
#
# Expected:
#
#
#       network failover
#
#       not necessarily AI fallback
#
#
# ---------------------------------------------------------------------------
# TEST 12
#
# NETWORK CONVERGES TO PROHIBITED PATH
# ---------------------------------------------------------------------------
#
#
# Internet path becomes operational route.
#
# E9 policy prohibits Internet.
#
#
# Expected:
#
#
#       network may report operational recovery
#
#       Agent 11 does not treat it as compliant recovery
#
#
# ---------------------------------------------------------------------------
# TEST 13
#
# MULTI-CLOUD SHARED FAILURE DOMAIN
# ---------------------------------------------------------------------------
#
#
# A:
#
#       Azure
#
# B:
#
#       GCP
#
# Both:
#
#       shared dependency
#
#
# Expected:
#
#
#       individual CandidateEvaluator results unaffected
#
#       resilience comparison belongs elsewhere
#
#
# ---------------------------------------------------------------------------
# TEST 14
#
# UNKNOWN HARD CONSTRAINT + EXCELLENT COST
# ---------------------------------------------------------------------------
#
#
# network:
#
#       UNKNOWN
#
# cost:
#
#       excellent
#
#
# Expected:
#
#
#       rejected
#
#       cost cannot compensate
#
#
# ---------------------------------------------------------------------------
# TEST 15
#
# TELEMETRY FAILURE
# ---------------------------------------------------------------------------
#
#
# Candidate evaluation succeeds.
#
# telemetry transport fails.
#
#
# Expected architecture:
#
#
#       telemetry failure handled according to system policy
#
#       telemetry does not retroactively rewrite routing truth
#
#
# ---------------------------------------------------------------------------
# TEST 16
#
# VENDOR ADAPTER TIMEOUT
# ---------------------------------------------------------------------------
#
#
# Kubernetes observer times out.
#
#
# Expected:
#
#
#       adapter/evidence layer normalizes legitimate observation failure
#
#       CandidateEvaluator receives domain-level UNKNOWN
#
#
# ---------------------------------------------------------------------------
# TEST 17
#
# PROGRAMMING ERROR
# ---------------------------------------------------------------------------
#
#
# CandidateEvaluator raises AttributeError due to defect.
#
#
# Expected:
#
#
#       programming error escapes
#
#       not converted to RoutingRejectionReason.UNKNOWN
#
#
# ---------------------------------------------------------------------------
# TEST 18
#
# CONCURRENT VS SEQUENTIAL EVALUATION
# ---------------------------------------------------------------------------
#
#
# Same established facts.
#
#
# Expected:
#
#
#       equivalent candidate semantics
#
#
# ---------------------------------------------------------------------------
# TEST 19
#
# FUTURE REMEDIATION
# ---------------------------------------------------------------------------
#
#
# Agent 11 observes service unavailable.
#
#
# Expected:
#
#
#       CandidateEvaluator rejects candidate
#
#       CandidateEvaluator does NOT restart infrastructure
#
#
# ---------------------------------------------------------------------------
# TEST 20
#
# NO COMPLIANT FALLBACK
# ---------------------------------------------------------------------------
#
#
# All remaining candidates:
#
#       policy denied
#
# or:
#
#       otherwise non-viable
#
#
# Expected:
#
#
#       request stops
#
#       no route invented
#
#
# ============================================================================
# END TEST MATRIX
# ============================================================================


# ============================================================================
# PART III-C RESPONSIBILITY TABLE
# ============================================================================
#
#
# CandidateEvaluator
# ------------------
#
# Question:
#
#       CAN THIS ONE CANDIDATE PARTICIPATE?
#
#
# Owns:
#
#       single-candidate viability
#
#       hard-gate interpretation
#
#       deterministic rejection precedence
#
#
# Does NOT own:
#
#       winner selection
#       scoring
#       fallback selection
#       cross-candidate resilience
#       infrastructure discovery
#       remediation
#
#
# ---------------------------------------------------------------------------
# AIRouter
# ---------------------------------------------------------------------------
#
# Question:
#
#       WHICH VIABLE CANDIDATE SHOULD WIN?
#
#
# Owns:
#
#       candidate selection
#
#
# Does NOT own:
#
#       policy evaluation
#       network observation
#       service observation
#       inference
#
#
# ---------------------------------------------------------------------------
# FallbackEvaluator
# ---------------------------------------------------------------------------
#
# Question:
#
#       MAY ANOTHER ROUTING CYCLE BE ATTEMPTED?
#
#
# Owns:
#
#       fallback eligibility
#
#
# Does NOT own:
#
#       replacement selection
#       policy bypass
#       historical viability assumptions
#
#
# ---------------------------------------------------------------------------
# NetworkOrchestrator
# ---------------------------------------------------------------------------
#
# Question:
#
#       WHAT DOES THE NETWORK CURRENTLY KNOW?
#
#
# Owns:
#
#       network evidence coordination
#       path assessments
#       network facts
#
#
# Does NOT own:
#
#       AI authorization
#       AI candidate selection
#
#
# ---------------------------------------------------------------------------
# Telemetry
# ---------------------------------------------------------------------------
#
# Question:
#
#       WHAT HAPPENED?
#
#
# Owns:
#
#       structured observations
#       audit facts
#       decision provenance
#
#
# Does NOT own:
#
#       routing semantics
#
#
# ---------------------------------------------------------------------------
# Orchestrators
# ---------------------------------------------------------------------------
#
# Question:
#
#       WHAT HAPPENS NEXT?
#
#
# Own:
#
#       coordination
#       lifecycle
#       sequencing
#
#
# Do NOT redefine:
#
#       domain semantics owned by components
#
#
# ============================================================================


# ============================================================================
# PART III-C FINAL INVARIANTS
# ============================================================================
#
#
# VIABILITY / SELECTION
# ---------------------
#
#
#       CandidateEvaluator
#           =
#       VIABILITY
#
#
#       AIRouter
#           =
#       SELECTION
#
#
#       SINGLE-CANDIDATE REASONING
#           !=
#       CROSS-CANDIDATE REASONING
#
#
#       EVALUATE FIRST
#
#       SELECT SECOND
#
#
# ---------------------------------------------------------------------------
# HARD CONSTRAINTS / OPTIMIZATION
# ---------------------------------------------------------------------------
#
#
#       OPTIMIZATION
#       OPERATES INSIDE
#       THE VIABLE SET
#
#
#       POLICY IS NOT A PREFERENCE
#
#
#       POLICY NEVER BECOMES A SCORE
#
#
#       DENY + FAST
#           !=
#       ALLOW
#
#
#       UNKNOWN HARD CONSTRAINT
#           !=
#       LOW SOFT SCORE
#
#
#       RESTRICT
#           !=
#       WEAK ALLOW
#
#
#       FILTER FIRST
#
#       OPTIMIZE SECOND
#
#
# ---------------------------------------------------------------------------
# PROVENANCE
# ---------------------------------------------------------------------------
#
#
#       ROUTING-DISPOSITIVE REASON
#           !=
#       COMPLETE SYSTEM DIAGNOSIS
#
#
#       PRIMARY DECISION REASON
#           !=
#       ALL OBSERVED PROBLEMS
#
#
#       DECISION
#           !=
#       EXPLANATION RECORD
#
#
# ---------------------------------------------------------------------------
# RESILIENCE
# ---------------------------------------------------------------------------
#
#
#       SINGLE-CANDIDATE VIABILITY
#           !=
#       CROSS-CANDIDATE RESILIENCE
#
#
#       DIFFERENT CLOUDS
#           !=
#       INDEPENDENT FAILURE
#
#
#       PATH COUNT
#           !=
#       FAILURE-DOMAIN COUNT
#
#
#       MULTI-PATH
#           !=
#       RESILIENCE
#
#
#       CORRELATION
#           !=
#       PROVEN DEPENDENCY
#
#
# ---------------------------------------------------------------------------
# FALLBACK
# ---------------------------------------------------------------------------
#
#
#       SKIPPING REJECTED CANDIDATE
#           !=
#       RUNTIME FALLBACK
#
#
#       FALLBACK ELIGIBILITY
#           !=
#       FALLBACK SELECTION
#
#
#       HISTORICAL VIABILITY
#           !=
#       CURRENT VIABILITY
#
#
#       FALLBACK
#       REUSES THE RULES
#
#
#       FALLBACK
#       DOES NOT BYPASS THE RULES
#
#
#       FALLBACK MODE
#           !=
#       LOWER SECURITY MODE
#
#
#       RETRY SAME TARGET
#           !=
#       FALLBACK DIFFERENT TARGET
#
#
#       ATTEMPT FAILED
#           !=
#       SERVICE FAILED
#
#
# ---------------------------------------------------------------------------
# NETWORK
# ---------------------------------------------------------------------------
#
#
#       NETWORK FAILOVER
#           !=
#       AI FALLBACK
#
#
#       NETWORK CONVERGENCE
#           !=
#       POLICY-COMPLIANT RECOVERY
#
#
#       SD-WAN BEST PATH
#           !=
#       AGENT 11 BEST AI ROUTE
#
#
#       BGP BEST PATH
#           !=
#       AI BEST CANDIDATE
#
#
#       BGP LOCAL_PREF
#           !=
#       AI ROUTING PREFERENCE
#
#
# ---------------------------------------------------------------------------
# LAYERS
# ---------------------------------------------------------------------------
#
#
#       ROUTE SUCCESS
#           !=
#       DATA-PLANE SUCCESS
#
#
#       DATA-PLANE SUCCESS
#           !=
#       TRANSPORT SUCCESS
#
#
#       TRANSPORT SUCCESS
#           !=
#       TLS SUCCESS
#
#
#       TLS SUCCESS
#           !=
#       APPLICATION SUCCESS
#
#
#       NETWORK AVAILABILITY
#           !=
#       SERVICE AVAILABILITY
#
#
# ---------------------------------------------------------------------------
# TELEMETRY
# ---------------------------------------------------------------------------
#
#
#       TELEMETRY
#           !=
#       CONTROL LOGIC
#
#
#       STRUCTURED FACT
#           FIRST
#
#
#       HUMAN NARRATIVE
#           SECOND
#
#
#       AI EXPLANATION
#           !=
#       AI AUTHORIZATION
#
#
# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
#
#
#       ORCHESTRATION
#           !=
#       DOMAIN DECISION
#
#
#       EXECUTION STRATEGY
#           !=
#       DOMAIN SEMANTICS
#
#
# ---------------------------------------------------------------------------
# CONTROL
# ---------------------------------------------------------------------------
#
#
#       OBSERVE
#           !=
#       EXECUTE
#
#
#       CORRECT REASONING
#           !=
#       EXECUTION AUTHORITY
#
#
#       EXECUTION SUCCESS
#           !=
#       OUTCOME SUCCESS
#
#
# ---------------------------------------------------------------------------
# ERRORS
# ---------------------------------------------------------------------------
#
#
#       INFRASTRUCTURE FAILURE
#       SHOULD BECOME
#       DOMAIN EVIDENCE
#       BEFORE REACHING ROUTING
#
#
#       DOMAIN UNCERTAINTY
#           !=
#       PROGRAMMING FAILURE
#
#
# ============================================================================


# ============================================================================
# PART III-C FINAL ARCHITECTURAL TEST
# ============================================================================
#
# Whenever someone proposes adding new behavior to CandidateEvaluator,
# ask four questions.
#
#
# QUESTION 1
# ----------
#
#       Does this behavior determine whether
#       ONE candidate is viable?
#
#
# If no:
#
#       probably belongs elsewhere.
#
#
# ============================================================================
# QUESTION 2
# ============================================================================
#
#       Does this behavior compare
#       MULTIPLE candidates?
#
#
# If yes:
#
#       it belongs downstream in routing,
#       optimization, or resilience logic.
#
#
# ============================================================================
# QUESTION 3
# ============================================================================
#
#       Does this behavior query or modify
#       infrastructure?
#
#
# If yes:
#
#       it belongs behind an observer,
#       adapter, runtime service,
#       network subsystem,
#       or controlled execution boundary.
#
#
# ============================================================================
# QUESTION 4
# ============================================================================
#
#       Does this behavior turn a hard constraint
#       into a score?
#
#
# If yes:
#
#       STOP.
#
#
# ============================================================================
#
#
#       CandidateEvaluator
#
#       SHOULD REMAIN BORING.
#
#
# ============================================================================
#
# Boring here is a feature.
#
#
# A routing-security component whose behavior can be explained as:
#
#
#       POLICY
#           AND
#       CAPABILITY
#           AND
#       SERVICE
#           AND
#       NETWORK
#           AND
#       FUTURE SUITABILITY
#
#           ->
#
#       VIABLE / REJECTED
#
#
# is easier to:
#
#
#       test
#
#       audit
#
#       explain
#
#       secure
#
#       extend
#
#       troubleshoot
#
#
# than a component that:
#
#
#       discovers infrastructure
#
#       scores models
#
#       selects clouds
#
#       changes routes
#
#       performs fallback
#
#       retries requests
#
#       emits telemetry
#
#       restarts Kubernetes
#
#       and occasionally evaluates candidates
#
#
# ============================================================================
#
#
#       SOPHISTICATION AROUND
#       A SMALL CORE
#
#
#       IS BETTER THAN
#
#
#       SOPHISTICATION INSIDE
#       AN UNBOUNDED CORE.
#
#
# ============================================================================
# END COMPLETE PART III-C
# ============================================================================
