"""
Agent 11 fallback eligibility behavior.

This module contains the SEIR-I fallback eligibility component used by the
Agent 11 routing subsystem.

The current FallbackEvaluator answers one deliberately narrow question:

    "MAY AGENT 11 BEGIN ANOTHER ROUTING CYCLE AFTER AN ATTEMPT?"

It does NOT answer:

    "Which service should Agent 11 use next?"

It does NOT answer:

    "Which previously viable candidate should Agent 11 invoke?"

It does NOT perform:

    policy evaluation
    capability evaluation
    service-health evaluation
    network-path evaluation
    model selection
    route selection
    model invocation
    retry execution

Those responsibilities belong elsewhere.

The central SEIR-I fallback principle is:

    HISTORICAL VIABILITY != CURRENT VIABILITY

A RoutingCandidate that was viable during an earlier routing evaluation
must not automatically be considered viable during fallback.

Fallback therefore permits a NEW routing cycle.

It does not reuse an old routing decision as current authorization.

Important invariants:

    FALLBACK != RETRY

    FALLBACK != ROUTE SELECTION

    FALLBACK != POLICY ESCAPE

    FALLBACK != SECURITY DOWNGRADE

    FALLBACK != REQUIREMENT REDUCTION

    ATTEMPTED SERVICE != FAILED SERVICE

    UNATTEMPTED CANDIDATE != VIABLE CANDIDATE

    CAN ATTEMPT FALLBACK != FALLBACK WILL SUCCEED

    WAS VIABLE != IS VIABLE NOW

    FALLBACK MAY REDUCE AVAILABILITY.
    FALLBACK MUST NEVER REDUCE SECURITY POLICY.
"""

from ..models.ai.routing import RoutingCandidate
from ..models.enums.routing_enums import FallbackStrategy


# ============================================================================
# PART I
#
# FALLBACK EVALUATOR — SEIR-I FALLBACK ELIGIBILITY
# ============================================================================
#
# FallbackEvaluator is a recovery-eligibility component.
#
# It is NOT a router.
#
#
#       FallbackEvaluator
#           =
#       "MAY ANOTHER ROUTING CYCLE BE ATTEMPTED?"
#
#
#       AIRouter
#           =
#       "WHICH CURRENTLY VIABLE ROUTE SHOULD BE SELECTED?"
#
#
# These responsibilities must remain separate.
#
#
# ============================================================================
# WHERE FALLBACK BEGINS
# ============================================================================
#
# Normal routing:
#
#
#       RoutingCandidate[]
#               |
#               v
#           AIRouter
#               |
#               v
#       RoutingDecision(SELECTED)
#               |
#               v
#          AI INVOCATION
#
#
# If the selected service is attempted and the invocation does not produce
# the required result, higher-level orchestration may consider fallback.
#
#
#       SELECTED SERVICE
#               |
#               v
#            ATTEMPT
#               |
#               X
#        ATTEMPT NOT USABLE
#               |
#               v
#       FallbackEvaluator
#
#
# FallbackEvaluator does not determine why the attempt was unusable.
#
# That distinction is important because:
#
#
#       INVOCATION FAILURE
#           !=
#       SERVICE FAILURE
#
#
# The service itself may still be healthy.
#
#
# ============================================================================
# ATTEMPTED SERVICE != FAILED SERVICE
# ============================================================================
#
# This module deliberately uses:
#
#
#       attempted_service_ids
#
#
# rather than:
#
#
#       failed_service_ids
#
#
# because Agent 11 does not yet have a complete invocation-attempt domain
# model.
#
# An attempted service might have participated in an unsuccessful attempt
# because of:
#
#
#       timeout
#
#       cancellation
#
#       connection interruption
#
#       malformed model output
#
#       provider-side rejection
#
#       another future invocation condition
#
#
# None of those automatically proves:
#
#
#       THE SERVICE ITSELF FAILED
#
#
# Therefore:
#
#
#       ATTEMPTED SERVICE
#
#
# is the narrower and more accurate SEIR-I concept.
#
#
# ============================================================================
# THE QUESTION ANSWERED BY FallbackEvaluator
# ============================================================================
#
# The current evaluator receives:
#
#
#       fallback strategy
#
#       services already attempted
#
#       original routing candidates
#
#
# and answers:
#
#
#       "DOES THE CONFIGURED STRATEGY PERMIT ANOTHER ROUTING CYCLE,
#        AND DOES AT LEAST ONE UNATTEMPTED SERVICE EXIST?"
#
#
# The answer is:
#
#
#       True
#
# or:
#
#       False
#
#
# This is deliberately a permission / eligibility question.
#
#
#       True
#
#
# means:
#
#
#       ANOTHER ROUTING CYCLE MAY BE ATTEMPTED
#
#
# It does NOT mean:
#
#
#       another viable route exists
#
#       another authorized route exists
#
#       another reachable route exists
#
#       another healthy service exists
#
#       fallback will succeed
#
#
# ============================================================================


class FallbackEvaluator:
    """
    Evaluates whether SEIR-I fallback may begin another routing cycle.

    FallbackEvaluator does not select a replacement service.

    It determines only whether the configured fallback strategy permits
    another routing attempt and whether at least one previously identified
    candidate service has not already been attempted.

    Historical RoutingCandidate status is deliberately ignored when making
    this decision.

    A candidate that was previously VIABLE must be freshly evaluated before
    it can participate in another route-selection decision.

    Therefore:

        WAS VIABLE != IS VIABLE NOW

    and:

        CAN ATTEMPT FALLBACK != FALLBACK WILL SUCCEED
    """

    def can_attempt_fallback(
        self,
        strategy: FallbackStrategy,
        attempted_service_ids: set[str],
        candidates: list[RoutingCandidate],
    ) -> bool:
        """
        Determine whether another routing cycle may be attempted.

        Args:
            strategy:
                The configured fallback behavior.

            attempted_service_ids:
                Service identifiers that have already participated in an
                invocation attempt for the current processing lifecycle.

                These services are excluded from the current fallback
                eligibility check.

            candidates:
                Routing candidates from the earlier routing evaluation.

                IMPORTANT:

                This collection is used only to identify the known candidate
                service universe.

                The candidate status and rejection reason recorded during the
                earlier evaluation are NOT treated as current routing facts.

        Returns:
            True when:

                1. the configured strategy permits fallback, and

                2. at least one candidate service has not already been
                   attempted.

            False when:

                1. fallback is disabled, or

                2. no unattempted candidate service remains.

        Raises:
            ValueError:
                If the supplied fallback strategy is not implemented by this
                evaluator.

        Important:

            Returning True does not authorize any destination.

            Returning True does not declare any candidate viable.

            Returning True means only:

                "There is another known service that may be subjected to
                 fresh routing evaluation."
        """

        # ====================================================================
        # STRATEGY: NONE
        # ====================================================================
        #
        # NONE means exactly what it says:
        #
        #
        #       DO NOT BEGIN A FALLBACK ROUTING CYCLE
        #
        #
        # We do not inspect candidate status.
        #
        # We do not search for alternatives.
        #
        # We do not attempt to improve availability.
        #
        # The configured recovery strategy has explicitly disabled fallback.
        #
        #
        #       FALLBACK DISABLED
        #           ->
        #       False
        #
        #
        # ====================================================================

        if strategy is FallbackStrategy.NONE:
            return False

        # ====================================================================
        # STRATEGY: NEXT_VIABLE
        # ====================================================================
        #
        # The name NEXT_VIABLE requires careful interpretation.
        #
        # It does NOT mean:
        #
        #
        #       "Find the next candidate whose OLD status is VIABLE."
        #
        #
        # That would incorrectly reuse historical routing evidence.
        #
        #
        # Instead, NEXT_VIABLE means:
        #
        #
        #       "If another unattempted candidate service exists,
        #        permit the routing subsystem to freshly evaluate
        #        the remaining options."
        #
        #
        # After fresh evaluation, AIRouter may select the next service that
        # is CURRENTLY viable.
        #
        #
        # Therefore:
        #
        #
        #       NEXT_VIABLE
        #           !=
        #       NEXT HISTORICALLY VIABLE CANDIDATE
        #
        #
        # Instead:
        #
        #
        #       NEXT_VIABLE
        #           =
        #       PERMIT FRESH EVALUATION OF REMAINING SERVICES
        #
        #
        # ====================================================================

        if strategy is FallbackStrategy.NEXT_VIABLE:

            # ================================================================
            # FIND AN UNATTEMPTED SERVICE
            # ================================================================
            #
            # Notice what this expression checks:
            #
            #
            #       candidate.service_id not in attempted_service_ids
            #
            #
            # Notice what it deliberately does NOT check:
            #
            #
            #       candidate.status is RoutingCandidateStatus.VIABLE
            #
            #
            # That omission is intentional.
            #
            #
            # Example:
            #
            #
            #       Earlier evaluation:
            #
            #           Service A -> VIABLE
            #           Service B -> VIABLE
            #           Service C -> REJECTED
            #
            #
            #       AIRouter selected:
            #
            #           Service A
            #
            #
            #       Service A was attempted.
            #
            #
            # FallbackEvaluator must NOT conclude:
            #
            #
            #       "Service B is still viable."
            #
            #
            # It may conclude only:
            #
            #
            #       "Service B and Service C have not yet been attempted."
            #
            #
            # Both may therefore be eligible for FRESH evaluation by the
            # routing subsystem.
            #
            #
            # Why include Service C?
            #
            # Because its earlier rejection may have depended upon a dynamic
            # fact that has since changed.
            #
            # Conversely, Service B's earlier viability may also have changed.
            #
            #
            # Therefore:
            #
            #
            #       OLD VIABLE
            #           !=
            #       CURRENT VIABLE
            #
            #
            # and:
            #
            #
            #       OLD REJECTED
            #           !=
            #       CURRENT REJECTED
            #
            #
            # The previous candidate collection tells us which services were
            # considered.
            #
            # It does not provide fresh authorization, health, capability, or
            # reachability evidence.
            #
            # ================================================================

            return any(
                candidate.service_id not in attempted_service_ids
                for candidate in candidates
            )

        # ====================================================================
        # UNSUPPORTED FUTURE STRATEGY
        # ====================================================================
        #
        # FallbackStrategy currently contains:
        #
        #
        #       NONE
        #
        #       NEXT_VIABLE
        #
        #
        # It may eventually gain additional strategies.
        #
        # If that happens, this evaluator should not silently convert an
        # unknown future strategy into:
        #
        #
        #       False
        #
        #
        # because that would hide the fact that executable behavior has not
        # been implemented for the newly introduced strategy.
        #
        #
        # Example future mistake:
        #
        #
        #       class FallbackStrategy(...):
        #           NONE = "none"
        #           NEXT_VIABLE = "next_viable"
        #           SOME_NEW_STRATEGY = "some_new_strategy"
        #
        #
        # If this file is not updated, we want an explicit failure rather than
        # silently pretending that SOME_NEW_STRATEGY means NONE.
        #
        #
        #       NEW ENUM VALUE
        #           !=
        #       IMPLEMENTED BEHAVIOR
        #
        #
        # Failing explicitly makes architectural drift visible.
        #
        # ====================================================================

        raise ValueError(
            f"Unsupported fallback strategy: {strategy}"
        )


# ============================================================================
# PART I — EXECUTABLE SEMANTICS
# ============================================================================
#
# The entire current SEIR-I algorithm is:
#
#
#       FALLBACK STRATEGY
#               |
#               v
#       +----------------+
#       |                |
#      NONE         NEXT_VIABLE
#       |                |
#       v                v
#     False      UNATTEMPTED SERVICE?
#                        |
#                   +----+----+
#                   |         |
#                  YES        NO
#                   |         |
#                   v         v
#                  True      False
#
#
# Any unsupported future strategy:
#
#
#       -> ValueError
#
#
# ============================================================================
# WHAT True MEANS
# ============================================================================
#
# True means:
#
#
#       ANOTHER ROUTING CYCLE MAY BE ATTEMPTED
#
#
# More precisely:
#
#
#       THE CONFIGURED STRATEGY PERMITS FALLBACK
#
#           +
#
#       AT LEAST ONE KNOWN SERVICE HAS NOT BEEN ATTEMPTED
#
#
# It does NOT mean:
#
#
#       POLICY PERMITTED
#
#       MODEL CAPABLE
#
#       SERVICE AVAILABLE
#
#       PATH AVAILABLE
#
#       ROUTE VIABLE
#
#       FALLBACK SELECTED
#
#       FALLBACK WILL SUCCEED
#
#
# ============================================================================
# WHAT False MEANS
# ============================================================================
#
# False means either:
#
#
#       FALLBACK IS DISABLED
#
#
# or:
#
#
#       NO UNATTEMPTED KNOWN CANDIDATE SERVICE REMAINS
#
#
# It does NOT mean:
#
#
#       request failed
#
#       service failed
#
#       model failed
#
#       policy blocked
#
#       network failed
#
#
# Higher-level orchestration determines what the absence of another fallback
# attempt means for the complete request lifecycle.
#
#
# ============================================================================
# WHY OLD CANDIDATE STATUS IS IGNORED
# ============================================================================
#
# Suppose the original routing evaluation produced:
#
#
#       A -> VIABLE
#       B -> VIABLE
#       C -> REJECTED / NETWORK_UNAVAILABLE
#
#
# A was selected and attempted.
#
# Time passes.
#
# During that time:
#
#
#       B may lose policy authorization.
#
#       B may become unavailable.
#
#       B may lose network reachability.
#
#       C's network path may recover.
#
#
# Therefore fallback must not treat:
#
#
#       B -> OLD VIABLE
#
#
# as:
#
#
#       B -> CURRENT VIABLE
#
#
# nor:
#
#
#       C -> OLD REJECTED
#
#
# as:
#
#
#       C -> CURRENT REJECTED
#
#
# Both require fresh evaluation.
#
#
#       HISTORICAL ROUTING EVIDENCE
#           !=
#       CURRENT ROUTING EVIDENCE
#
#
# ============================================================================
# FRESH EVALUATION REMAINS SOMEONE ELSE'S JOB
# ============================================================================
#
# FallbackEvaluator deliberately does NOT perform the fresh evaluation.
#
#
# It does not import:
#
#
#       policy evaluators
#
#       service-health evaluators
#
#       network-path evaluators
#
#       provider SDKs
#
#       model clients
#
#
# It merely permits another routing cycle.
#
#
# Conceptually:
#
#
#       FallbackEvaluator
#               |
#               v
#             True
#               |
#               v
#       ROUTING COORDINATION
#               |
#       +-------+-------+-------+-------+
#       |       |       |       |       |
#       v       v       v       v       |
#     POLICY  MODEL   SERVICE NETWORK   |
#       |       |       |       |       |
#       +-------+-------+-------+-------+
#                       |
#                       v
#              FRESH RoutingCandidate[]
#                       |
#                       v
#                    AIRouter
#
#
# ============================================================================
# FALLBACK DOES NOT SELECT
# ============================================================================
#
# FallbackEvaluator never returns:
#
#
#       service_id
#
#       routing_domain
#
#       RoutingCandidate
#
#       RoutingDecision
#
#
# because those would imply route-selection authority.
#
#
# Its result is deliberately:
#
#
#       bool
#
#
# because its question is deliberately:
#
#
#       MAY ANOTHER ROUTING CYCLE BEGIN?
#
#
# ============================================================================
# FALLBACK DOES NOT RETRY
# ============================================================================
#
# SEIR-I distinguishes:
#
#
#       RETRY
#           =
#       TRY THE SAME SERVICE AGAIN
#
#
# from:
#
#
#       FALLBACK
#           =
#       CONSIDER ANOTHER SERVICE THROUGH
#       A NEW ROUTING CYCLE
#
#
# Retry behavior is not implemented here.
#
#
# ============================================================================
# FALLBACK DOES NOT AUTHORIZE
# ============================================================================
#
# Returning True grants no destination permission.
#
#
#       FALLBACK PERMISSION
#           !=
#       DATA-ROUTING AUTHORIZATION
#
#
# Every alternative must still satisfy current policy.
#
#
# ============================================================================
# FALLBACK DOES NOT REDUCE REQUIREMENTS
# ============================================================================
#
# If the request requires:
#
#
#       SECURITY_ANALYSIS
#           +
#       HEAVY reasoning
#
#
# fallback does not change that to:
#
#
#       TEXT_GENERATION
#           +
#       STANDARD reasoning
#
#
# merely because another service is available.
#
#
#       AVAILABILITY PRESSURE
#           !=
#       PERMISSION TO CHANGE REQUESTER INTENT
#
#
# ============================================================================
# FALLBACK DOES NOT TRUST YESTERDAY
# ============================================================================
#
# Or five minutes ago.
#
# Or five seconds ago.
#
#
#       PREVIOUSLY AUTHORIZED
#           !=
#       CURRENTLY AUTHORIZED
#
#
#       PREVIOUSLY HEALTHY
#           !=
#       CURRENTLY HEALTHY
#
#
#       PREVIOUSLY REACHABLE
#           !=
#       CURRENTLY REACHABLE
#
#
#       PREVIOUSLY VIABLE
#           !=
#       CURRENTLY VIABLE
#
#
# ============================================================================
# CHEWBACCA REVIEW
# ============================================================================
#
# Engineer:
#
#       "Service B was viable when we routed the request."
#
# Chewbacca:
#
#       "When?"
#
#
# Engineer:
#
#       "Before Service A failed."
#
# Chewbacca:
#
#       "Then you know what B was."
#
#
# Engineer:
#
#       "Not what B is."
#
# Chewbacca:
#
#       "Now you are routing."
#
#
# ============================================================================
# PART I FINAL INVARIANTS
# ============================================================================
#
#       FALLBACK != RETRY
#
#
#       FALLBACK != ROUTER
#
#       FALLBACK != ROUTE SELECTION
#
#
#       ATTEMPTED SERVICE != FAILED SERVICE
#
#
#       UNATTEMPTED SERVICE != VIABLE SERVICE
#
#
#       HISTORICAL VIABILITY != CURRENT VIABILITY
#
#       WAS VIABLE != IS VIABLE NOW
#
#
#       OLD REJECTED != CURRENT REJECTED
#
#
#       CAN ATTEMPT FALLBACK
#           !=
#       FALLBACK WILL SUCCEED
#
#
#       FALLBACK PERMISSION
#           !=
#       DATA-ROUTING AUTHORIZATION
#
#
#       PREVIOUSLY AUTHORIZED
#           !=
#       CURRENTLY AUTHORIZED
#
#
#       FALLBACK != POLICY ESCAPE
#
#       FALLBACK != SECURITY DOWNGRADE
#
#       FALLBACK != CAPABILITY REDUCTION
#
#       FALLBACK != REASONING REDUCTION
#
#       FALLBACK != REQUIREMENT REDUCTION
#
#
#       FALLBACK MAY REDUCE AVAILABILITY.
#
#       FALLBACK MUST NEVER REDUCE SECURITY POLICY.
#
#
#       NEW ENUM VALUE
#           !=
#       IMPLEMENTED BEHAVIOR
#
#
# ============================================================================
# END PART I
# ============================================================================

# ============================================================================
# PART II
#
# SEIR-I FALLBACK SEMANTICS + DESIGN RATIONALE
# ============================================================================
#
# Part I implemented a deliberately small amount of executable behavior:
#
#
#       FallbackEvaluator.can_attempt_fallback(...)
#
#
# answers:
#
#
#       "MAY AGENT 11 BEGIN ANOTHER ROUTING CYCLE?"
#
#
# It does NOT answer:
#
#
#       "WHICH SERVICE SHOULD AGENT 11 USE NEXT?"
#
#
# It does NOT answer:
#
#
#       "IS ANOTHER ROUTE CURRENTLY VIABLE?"
#
#
# It does NOT answer:
#
#
#       "SHOULD THE SAME SERVICE BE RETRIED?"
#
#
# Those are different architectural questions.
#
#
# Part II documents the SEIR-I fallback contract and the boundaries that must
# remain intact as Agent 11 becomes more sophisticated.
#
#
# ============================================================================
# THE CENTRAL FALLBACK PRINCIPLE
# ============================================================================
#
# Fallback exists because a previously selected route may no longer produce
# a usable result.
#
#
#       ROUTE SELECTED
#             |
#             v
#       SERVICE ATTEMPTED
#             |
#             X
#       ATTEMPT NOT USABLE
#             |
#             v
#       RECOVERY QUESTION
#
#
# The recovery question is NOT:
#
#
#       "What was the second-best route earlier?"
#
#
# It is:
#
#
#       "May we begin another routing cycle using the remaining
#        unattempted services?"
#
#
# This distinction is fundamental.
#
#
# ============================================================================
# FALLBACK IS A NEW ROUTING CYCLE
# ============================================================================
#
# SEIR-I defines fallback conceptually as:
#
#
#       PREVIOUS ATTEMPT
#             |
#             v
#       FALLBACK ELIGIBILITY
#             |
#             v
#       FRESH ROUTING EVALUATION
#             |
#             v
#       NEW RoutingCandidate[]
#             |
#             v
#          AIRouter
#
#
# Therefore:
#
#
#       FALLBACK
#           !=
#       WALK DOWN THE OLD CANDIDATE LIST
#
#
# and:
#
#
#       FALLBACK
#           !=
#       REUSE THE PREVIOUS ROUTING DECISION
#
#
# ============================================================================
# WHY FRESH EVALUATION IS REQUIRED
# ============================================================================
#
# RoutingCandidate is a statement about a candidate at the time the candidate
# was evaluated.
#
#
# It is not a permanent property of the service.
#
#
# Suppose the original evaluation produced:
#
#
#       Service A -> VIABLE
#
#       Service B -> VIABLE
#
#       Service C -> REJECTED / NETWORK_UNAVAILABLE
#
#
# AIRouter selects Service A.
#
# Service A is attempted.
#
# The attempt does not produce a usable result.
#
#
# At fallback time, the following may now be true:
#
#
#       Service B -> POLICY_DENIED
#
#       Service C -> NETWORK RECOVERED
#
#
# Therefore:
#
#
#       B WAS VIABLE
#           !=
#       B IS VIABLE
#
#
# and:
#
#
#       C WAS REJECTED
#           !=
#       C IS REJECTED
#
#
# The entire viability equation must be considered again.
#
#
# ============================================================================
# VIABILITY IS TEMPORAL
# ============================================================================
#
# The Agent 11 viability equation is:
#
#
#       VIABLE ROUTE
#           =
#       POLICY PERMITTED
#           +
#       SERVICE CAPABLE
#           +
#       SERVICE AVAILABLE
#           +
#       PATH AVAILABLE
#
#
# Some of these facts may be relatively stable.
#
# Others may change quickly.
#
#
#       policy may change
#
#       service state may change
#
#       network state may change
#
#       deployment state may change
#
#
# Therefore a routing candidate should be understood as:
#
#
#       AN EVALUATED ROUTING FACT
#
#
# rather than:
#
#
#       A PERMANENT ATTRIBUTE OF THE SERVICE
#
#
# ============================================================================
# HISTORICAL EVIDENCE != CURRENT EVIDENCE
# ============================================================================
#
# This is the central temporal invariant of fallback:
#
#
#       HISTORICAL ROUTING EVIDENCE
#           !=
#       CURRENT ROUTING EVIDENCE
#
#
# Specifically:
#
#
#       PREVIOUSLY PERMITTED
#           !=
#       CURRENTLY PERMITTED
#
#
#       PREVIOUSLY CAPABLE
#           !=
#       CURRENTLY CAPABLE
#
#
#       PREVIOUSLY AVAILABLE
#           !=
#       CURRENTLY AVAILABLE
#
#
#       PREVIOUSLY REACHABLE
#           !=
#       CURRENTLY REACHABLE
#
#
#       PREVIOUSLY VIABLE
#           !=
#       CURRENTLY VIABLE
#
#
# This is why FallbackEvaluator deliberately ignores the historical status
# stored on RoutingCandidate.
#
#
# ============================================================================
# WHY THE OLD CANDIDATE LIST IS STILL USEFUL
# ============================================================================
#
# If historical status cannot be trusted, why pass the original candidates
# into FallbackEvaluator at all?
#
#
# Because the original candidate list still identifies:
#
#
#       THE KNOWN SERVICE UNIVERSE
#
#
# considered during the earlier routing cycle.
#
#
# For example:
#
#
#       candidates:
#
#           Service A
#           Service B
#           Service C
#
#
#       attempted_service_ids:
#
#           Service A
#
#
# FallbackEvaluator may determine:
#
#
#       Service B has not been attempted.
#
#       Service C has not been attempted.
#
#
# That is enough to establish:
#
#
#       ANOTHER ROUTING CYCLE MAY BE WORTH ATTEMPTING
#
#
# It is NOT enough to establish:
#
#
#       B OR C IS CURRENTLY VIABLE
#
#
# ============================================================================
# CANDIDATE UNIVERSE != CURRENT VIABILITY
# ============================================================================
#
# This distinction should remain explicit:
#
#
#       ORIGINAL CANDIDATE COLLECTION
#           =
#       KNOWN ALTERNATIVE SERVICES
#
#
#       ORIGINAL CANDIDATE STATUS
#           =
#       HISTORICAL EVALUATION RESULT
#
#
# FallbackEvaluator uses the first.
#
# It deliberately does not trust the second.
#
#
# ============================================================================
# WHY PREVIOUSLY REJECTED SERVICES MAY BE RE-EVALUATED
# ============================================================================
#
# A previously rejected candidate is not automatically excluded from future
# fallback evaluation.
#
#
# Example:
#
#
#       Service C
#
#       earlier rejection:
#
#           NETWORK_UNAVAILABLE
#
#
# If the network path later recovers, Service C may become viable.
#
#
# Therefore:
#
#
#       PREVIOUSLY REJECTED
#           !=
#       PERMANENTLY DISQUALIFIED
#
#
# This is especially important for operational rejection reasons.
#
#
# ============================================================================
# IMPORTANT POLICY QUALIFICATION
# ============================================================================
#
# Re-evaluation does NOT mean that Agent 11 ignores the reason for an earlier
# rejection.
#
#
# If Service C was previously:
#
#
#       POLICY_DENIED
#
#
# it still receives fresh policy evaluation before it can become viable.
#
#
# Fallback does not say:
#
#
#       "The candidate is getting a second chance."
#
#
# It says:
#
#
#       "The candidate's CURRENT routing facts must be evaluated."
#
#
# If policy still denies the candidate:
#
#
#       it remains rejected.
#
#
# ============================================================================
# RE-EVALUATION != AUTHORIZATION RESET
# ============================================================================
#
# Beginning another routing cycle does not reset security state.
#
#
# It does not mean:
#
#
#       clear classification
#
#       clear prohibited-data findings
#
#       clear organization policy
#
#       clear user restrictions
#
#
# The same request remains subject to its security requirements.
#
#
#       NEW ROUTING CYCLE
#           !=
#       NEW SECURITY IDENTITY
#
#
# ============================================================================
# FALLBACK != POLICY ESCAPE
# ============================================================================
#
# Consider:
#
#
#       External FM
#           -> capable
#           -> healthy
#           -> reachable
#           -> POLICY DENIED
#
#
#       Company On-Prem LLM
#           -> selected
#           -> invocation fails
#
#
# Fallback must NOT conclude:
#
#
#       "The authorized service failed, so now we can use
#        the external foundation model."
#
#
# The external model remains policy denied.
#
#
#       FAILURE OF AN AUTHORIZED ROUTE
#           DOES NOT
#       AUTHORIZE A PROHIBITED ROUTE
#
#
# ============================================================================
# AVAILABILITY PRESSURE DOES NOT CHANGE POLICY
# ============================================================================
#
# This is one of the most important recovery principles in Agent 11.
#
#
# Suppose:
#
#
#       E9 data
#
#
# may only use:
#
#
#       COMPANY_ONPREM_LLM
#
#
# and the approved on-premises service becomes unavailable.
#
#
# The correct outcome may be:
#
#
#       NO VIABLE ROUTE
#
#
# rather than:
#
#
#       send the request to an external FM
#
#
# simply to maintain availability.
#
#
#       FALLBACK MAY REDUCE AVAILABILITY.
#
#       FALLBACK MUST NEVER REDUCE SECURITY POLICY.
#
#
# ============================================================================
# NO FALLBACK CAN BE A SUCCESSFUL SECURITY OUTCOME
# ============================================================================
#
# A routing system does not succeed only when inference occurs.
#
#
# If every remaining route violates policy, then refusing to invoke another
# service is correct enforcement.
#
#
#       NO COMPLIANT FALLBACK
#
#
# may therefore represent:
#
#
#       SUCCESSFUL SECURITY BEHAVIOR
#
#
# even though:
#
#
#       REQUEST AVAILABILITY WAS NOT PRESERVED
#
#
# ============================================================================
# FALLBACK != CAPABILITY REDUCTION
# ============================================================================
#
# Suppose the request requires:
#
#
#       SECURITY_ANALYSIS
#
#           +
#
#       HEAVY reasoning
#
#
# The selected service is attempted and cannot complete the work.
#
#
# Another service supports:
#
#
#       SECURITY_ANALYSIS
#
#           +
#
#       STANDARD reasoning
#
#
# Fallback must not silently decide:
#
#
#       "STANDARD is better than nothing."
#
#
# The original requirement remains:
#
#
#       HEAVY
#
#
# Therefore:
#
#
#       FALLBACK
#           !=
#       REASONING DOWNGRADE
#
#
# ============================================================================
# FALLBACK != REQUIREMENT NEGOTIATION
# ============================================================================
#
# Recovery pressure does not give the routing subsystem authority to rewrite
# requester intent.
#
#
# It must not silently change:
#
#
#       capability requirements
#
#       reasoning requirements
#
#       structured-output requirements
#
#       future modality requirements
#
#       future assurance requirements
#
#
# merely because the preferred service failed.
#
#
#       AVAILABILITY PRESSURE
#           !=
#       PERMISSION TO CHANGE THE REQUEST
#
#
# ============================================================================
# FALLBACK != DATA-CLASSIFICATION REDUCTION
# ============================================================================
#
# Fallback must never transform:
#
#
#       E9
#
#
# into:
#
#
#       E8
#
#
# or:
#
#
#       E7
#
#
# or:
#
#
#       NORMAL
#
#
# merely to make more routes available.
#
#
#       ROUTING FAILURE
#           !=
#       DECLASSIFICATION EVENT
#
#
# ============================================================================
# FALLBACK != USER-POLICY REDUCTION
# ============================================================================
#
# If a user has legitimately narrowed routing through:
#
#
#       COMPANY_ONLY
#
#
# or:
#
#
#       ONPREM_ONLY
#
#
# fallback must preserve that restriction.
#
#
# Remember:
#
#
#       EFFECTIVE POLICY
#           =
#       ORGANIZATION POLICY
#           INTERSECTION
#       USER POLICY
#
#
# The user's restriction does not disappear because the first selected
# service became unusable.
#
#
# ============================================================================
# FALLBACK != RETRY
# ============================================================================
#
# SEIR-I deliberately distinguishes two recovery concepts.
#
#
#       RETRY
#           =
#       TRY THE SAME SERVICE AGAIN
#
#
#       FALLBACK
#           =
#       CONSIDER ANOTHER SERVICE THROUGH
#       A NEW ROUTING CYCLE
#
#
# Example:
#
#
#       Service A attempt 1 -> timeout
#
#
# A retry might mean:
#
#
#       Service A attempt 2
#
#
# A fallback might mean:
#
#
#       freshly evaluate B and C
#
#       select B
#
#       attempt B
#
#
# These are different recovery mechanisms.
#
#
# ============================================================================
# WHY RETRY IS NOT IMPLEMENTED HERE
# ============================================================================
#
# Retry eventually requires questions such as:
#
#
#       Is the failure retryable?
#
#       How many retries are permitted?
#
#       Is backoff required?
#
#       Does the provider recommend retry-after?
#
#       Is the operation idempotent?
#
#       Will retry duplicate cost?
#
#       Will retry duplicate side effects?
#
#
# Those questions do not belong in the current FallbackEvaluator.
#
#
# ============================================================================
# FALLBACK != FAILOVER
# ============================================================================
#
# The word "failover" may eventually describe a different operational
# behavior.
#
#
# For example:
#
#
#       SAME LOGICAL MODEL
#
#       deployment A -> unavailable
#
#       deployment B -> healthy
#
#
# Moving between redundant deployments may eventually be considered:
#
#
#       FAILOVER
#
#
# rather than:
#
#
#       MODEL FALLBACK
#
#
# SEIR-I does not need to settle that vocabulary yet.
#
#
# It should simply avoid pretending that all recovery is the same thing.
#
#
# ============================================================================
# FALLBACK != DISASTER RECOVERY
# ============================================================================
#
# Likewise, fallback is not the same as recovering from:
#
#
#       region loss
#
#       cloud-provider outage
#
#       data-center failure
#
#       control-plane failure
#
#       major network partition
#
#
# Those may eventually require broader disaster-recovery behavior.
#
#
#       ONE FAILED INVOCATION
#           !=
#       DISASTER
#
#
# ============================================================================
# WHY WE USE attempted_service_ids
# ============================================================================
#
# The current evaluator needs to prevent an immediate routing cycle from
# selecting from an unchanged universe that contains only services already
# attempted during this recovery sequence.
#
#
# Therefore it receives:
#
#
#       attempted_service_ids
#
#
# This is intentionally a set.
#
#
# Membership is the relevant question:
#
#
#       HAS THIS SERVICE ALREADY BEEN ATTEMPTED?
#
#
# SEIR-I does not currently need:
#
#
#       attempt order
#
#       attempt count
#
#       attempt timestamps
#
#       failure causes
#
#       retry count
#
#
# Those may eventually justify an InvocationAttempt model.
#
#
# ============================================================================
# attempted_service_ids IS NOT ATTEMPT HISTORY
# ============================================================================
#
# This distinction matters.
#
#
#       {"service-a", "service-b"}
#
#
# tells us:
#
#
#       A was attempted.
#
#       B was attempted.
#
#
# It does not tell us:
#
#
#       which was first
#
#       how many times either was attempted
#
#       why either attempt ended
#
#       whether either service was actually unhealthy
#
#
# Therefore:
#
#
#       ATTEMPTED SERVICE SET
#           !=
#       INVOCATION HISTORY
#
#
# ============================================================================
# WHY FallbackEvaluator DOES NOT MUTATE attempted_service_ids
# ============================================================================
#
# The evaluator answers a question.
#
# It does not record an invocation.
#
#
# Therefore it should not perform:
#
#
#       attempted_service_ids.add(...)
#
#
# That mutation belongs to the layer managing actual invocation attempts.
#
#
#       EVALUATING RECOVERY
#           !=
#       RECORDING EXECUTION
#
#
# ============================================================================
# WHY FallbackEvaluator DOES NOT MUTATE candidates
# ============================================================================
#
# Historical RoutingCandidate objects describe a previous routing
# evaluation.
#
#
# FallbackEvaluator should not rewrite them to pretend that they contain
# fresh state.
#
#
# Never:
#
#
#       candidate.status = ...
#
#
# inside this evaluator.
#
#
# Fresh evaluation should produce fresh routing evidence.
#
#
#       NEW EVALUATION
#           SHOULD PRODUCE
#       NEW EVALUATION RESULT
#
#
# ============================================================================
# OLD RoutingCandidate OBJECTS ARE HISTORICAL FACTS
# ============================================================================
#
# Once a routing cycle has completed, its candidate records may become useful
# for:
#
#
#       explanation
#
#       telemetry
#
#       audit
#
#       debugging
#
#
# Mutating them during fallback would destroy that historical meaning.
#
#
# Conceptually:
#
#
#       ROUTING CYCLE 1
#
#           A -> VIABLE
#           B -> VIABLE
#           C -> REJECTED
#
#
#       ROUTING CYCLE 2
#
#           B -> REJECTED
#           C -> VIABLE
#
#
# These are two different evaluated states.
#
#
# They should not be represented by mutating cycle 1 until it looks like
# cycle 2.
#
#
# ============================================================================
# STATE EVOLUTION != HISTORY REWRITING
# ============================================================================
#
# This principle appears throughout Agent 11:
#
#
#       CURRENT STATE MAY CHANGE
#
#
# but:
#
#
#       HISTORICAL EVIDENCE SHOULD NOT BE REWRITTEN
#
#
# Future telemetry and durable workflow systems may preserve this distinction
# more formally.
#
#
# ============================================================================
# WHY FallbackEvaluator DOES NOT ACCEPT RoutingDecision
# ============================================================================
#
# A reviewer may ask why the method accepts:
#
#
#       candidates
#
#
# rather than the entire:
#
#
#       RoutingDecision
#
#
# The evaluator currently needs only:
#
#
#       candidate service identifiers
#
#
# together with:
#
#
#       attempted service identifiers
#
#
# Passing RoutingDecision would expose additional information that the
# evaluator does not need:
#
#
#       selected_service_id
#
#       selected_routing_domain
#
#       routing status
#
#       reason
#
#
# Keeping the input narrow reinforces the current responsibility.
#
#
#       MINIMUM REQUIRED INPUT
#           >
#       CONVENIENT LARGE OBJECT
#
#
# ============================================================================
# WHY FallbackEvaluator DOES NOT ACCEPT AIRequest
# ============================================================================
#
# FallbackEvaluator does not need:
#
#
#       task
#
#       context
#
#       estimated tokens
#
#       reasoning level
#
#       request status
#
#
# to determine whether another unattempted service exists.
#
#
# Those facts will matter during fresh candidate evaluation.
#
#
# They do not matter to the narrow fallback-eligibility question.
#
#
# ============================================================================
# WHY FallbackEvaluator DOES NOT ACCEPT DataClassification
# ============================================================================
#
# Data classification matters enormously to policy.
#
#
# It does not determine whether another service identifier exists in the
# known candidate universe.
#
#
# Therefore:
#
#
#       DataClassification
#
#
# belongs in the fresh policy/routing evaluation, not in fallback eligibility.
#
#
# ============================================================================
# WHY FallbackEvaluator DOES NOT ACCEPT PolicyDecision
# ============================================================================
#
# Historical policy decisions are precisely the sort of state that must not
# be silently reused as current authorization.
#
#
# FallbackEvaluator should not inspect:
#
#
#       previous ALLOW
#
#       previous DENY
#
#       previous RESTRICT
#
#       previous INDETERMINATE
#
#
# to decide current route viability.
#
#
# Fresh policy evaluation belongs to the next routing cycle.
#
#
# ============================================================================
# WHY FallbackEvaluator DOES NOT ACCEPT SERVICE HEALTH
# ============================================================================
#
# Service health is dynamic routing evidence.
#
#
# FallbackEvaluator does not decide current viability.
#
#
# Therefore:
#
#
#       service health
#
#
# belongs in fresh candidate evaluation.
#
#
# ============================================================================
# WHY FallbackEvaluator DOES NOT ACCEPT NETWORK STATE
# ============================================================================
#
# Network state is also dynamic routing evidence.
#
#
# It may include future facts involving:
#
#
#       Internet
#
#       VPN
#
#       PrivateLink
#
#       SD-WAN
#
#       BGP
#
#       Street Access
#
#
# FallbackEvaluator should know none of those details.
#
#
# Its question remains:
#
#
#       IS THERE AN UNATTEMPTED SERVICE
#       THAT MAY BE RE-EVALUATED?
#
#
# ============================================================================
# WHY FallbackEvaluator DOES NOT ACCEPT AIModel
# ============================================================================
#
# Model capability is evaluated elsewhere.
#
#
# FallbackEvaluator does not determine whether an alternative model can
# satisfy the request.
#
#
# That belongs to:
#
#
#       ModelRouter
#
#
# and eventually broader candidate evaluation.
#
#
# ============================================================================
# WHY FallbackEvaluator DOES NOT CALL AIRouter
# ============================================================================
#
# FallbackEvaluator determines whether another routing cycle may begin.
#
#
# AIRouter selects from evaluated candidates.
#
#
# If FallbackEvaluator called AIRouter itself, it would begin coordinating:
#
#
#       eligibility
#
#       fresh evaluation
#
#       route selection
#
#
# and would quickly become a routing orchestrator.
#
#
# That is not its role.
#
#
#       FallbackEvaluator != RoutingOrchestrator
#
#
# ============================================================================
# WHY FallbackEvaluator DOES NOT PRODUCE RoutingDecision
# ============================================================================
#
# A RoutingDecision requires evaluated routing evidence.
#
#
# FallbackEvaluator does not possess that evidence.
#
#
# Therefore it cannot legitimately produce:
#
#
#       SELECTED
#
#       BLOCKED
#
#       NO_VIABLE_ROUTE
#
#       NULL
#
#
# Those statuses belong to actual routing decisions.
#
#
# ============================================================================
# FALLBACK ELIGIBILITY HAS NO RoutingStatus
# ============================================================================
#
# The result:
#
#
#       True
#
#
# is not:
#
#
#       RoutingStatus.SELECTED
#
#
# The result:
#
#
#       False
#
#
# is not:
#
#
#       RoutingStatus.NO_VIABLE_ROUTE
#
#
# or:
#
#
#       RoutingStatus.BLOCKED
#
#
# Fallback eligibility and routing outcome are separate domains.
#
#
# ============================================================================
# WHY bool IS SUFFICIENT FOR SEIR-I
# ============================================================================
#
# The current question is binary:
#
#
#       MAY ANOTHER ROUTING CYCLE BE ATTEMPTED?
#
#
# The current reasons are simple:
#
#
#       strategy disables fallback
#
# or:
#
#       no unattempted service remains
#
#
# SEIR-I does not yet require a richer result contract.
#
#
# A future system may need to distinguish:
#
#
#       fallback disabled
#
#       attempt budget exhausted
#
#       no alternatives
#
#       workflow cancelled
#
#       recovery policy denied
#
#
# If those semantics become real, a richer result may become justified.
#
#
# ============================================================================
# DO NOT CREATE FallbackDecision JUST BECAUSE IT SOUNDS ENTERPRISE
# ============================================================================
#
# A future class such as:
#
#
#       FallbackDecision
#
#
# may eventually be useful.
#
#
# But SEIR-I currently has:
#
#
#       one binary question
#
#
# and:
#
#
#       one binary answer
#
#
# Creating a five-field model around that answer would not increase
# correctness.
#
#
#       MORE STRUCTURE != MORE SEMANTICS
#
#
# ============================================================================
# FallbackStrategy IS CONFIGURATION, NOT CURRENT VIABILITY
# ============================================================================
#
# FallbackStrategy says how the system is configured to behave after an
# unsuccessful attempt.
#
#
# It does not describe:
#
#
#       service health
#
#       policy authorization
#
#       network reachability
#
#       model capability
#
#
# Therefore:
#
#
#       FallbackStrategy.NEXT_VIABLE
#
#
# does not assert:
#
#
#       A NEXT VIABLE SERVICE EXISTS
#
#
# It asserts only that the system is configured to consider one if fresh
# routing evaluation can find one.
#
#
# ============================================================================
# THE SEMANTICS OF NEXT_VIABLE
# ============================================================================
#
# The enum name:
#
#
#       NEXT_VIABLE
#
#
# could easily be misread as:
#
#
#       "Pick the next candidate whose status == VIABLE."
#
#
# That interpretation is explicitly rejected.
#
#
# SEIR-I defines NEXT_VIABLE as:
#
#
#       PERMIT A NEW ROUTING EVALUATION AMONG
#       UNATTEMPTED CANDIDATE SERVICES
#
#       AND, IF THAT EVALUATION PRODUCES VIABLE CANDIDATES,
#       ALLOW NORMAL ROUTING TO SELECT ONE.
#
#
# In shorthand:
#
#
#       NEXT_VIABLE
#           =
#       NEXT NEWLY EVALUATED VIABLE ROUTE
#
#
# not:
#
#
#       NEXT OLD VIABLE ENTRY
#
#
# ============================================================================
# WHY NONE RETURNS False IMMEDIATELY
# ============================================================================
#
# If:
#
#
#       strategy == NONE
#
#
# then the organization/application has explicitly configured:
#
#
#       NO FALLBACK ROUTING
#
#
# The evaluator therefore does not need to inspect whether alternatives
# exist.
#
#
# This is an example of:
#
#
#       CONFIGURED RECOVERY POLICY
#           BEFORE
#       RECOVERY OPPORTUNITY
#
#
# ============================================================================
# WHY NEXT_VIABLE REQUIRES AN UNATTEMPTED SERVICE
# ============================================================================
#
# Suppose:
#
#
#       candidates = [A]
#
#       attempted_service_ids = {A}
#
#
# Another routing cycle over the same known service universe cannot produce a
# different service.
#
#
# Therefore:
#
#
#       False
#
#
# is the appropriate SEIR-I answer.
#
#
# This avoids pointless routing cycles.
#
#
# ============================================================================
# WHY NEXT_VIABLE DOES NOT REQUIRE A PREVIOUSLY VIABLE SERVICE
# ============================================================================
#
# Suppose:
#
#
#       A -> VIABLE
#
#       B -> NETWORK_UNAVAILABLE
#
#
# A is attempted.
#
# The network changes.
#
#
# B may now be reachable.
#
#
# Therefore requiring:
#
#
#       previous candidate.status == VIABLE
#
#
# would incorrectly prevent B from being reconsidered.
#
#
# ============================================================================
# WHY ATTEMPTED SERVICES ARE EXCLUDED
# ============================================================================
#
# In the current SEIR-I fallback semantics, fallback means considering a
# different service.
#
#
# Therefore a service already attempted in the current recovery sequence is
# excluded from fallback eligibility.
#
#
# If Agent 11 later wants to attempt that same service again:
#
#
#       THAT IS RETRY
#
#
# not fallback.
#
#
# ============================================================================
# EXCLUSION != PERMANENT QUARANTINE
# ============================================================================
#
# An attempted service is excluded from the current fallback sequence.
#
#
# That does NOT mean:
#
#
#       permanently unhealthy
#
#       permanently prohibited
#
#       permanently removed from registry
#
#       permanently incapable
#
#
# The exclusion is scoped to the current processing/recovery lifecycle.
#
#
# ============================================================================
# INVOCATION FAILURE != SERVICE FAILURE
# ============================================================================
#
# This deserves repetition because future recovery logic can easily get this
# wrong.
#
#
# Example:
#
#
#       Service A is healthy.
#
#       Request X times out.
#
#
# That does not prove:
#
#
#       Service A is unhealthy.
#
#
# It proves:
#
#
#       Request X did not complete successfully through that attempt.
#
#
# Future service-health systems may independently determine whether A's
# health state should change.
#
#
# ============================================================================
# INVOCATION FAILURE != MODEL FAILURE
# ============================================================================
#
# Likewise, one unsuccessful attempt does not prove:
#
#
#       the logical AI model is broken
#
#
# The failure could exist at:
#
#
#       request
#
#       client
#
#       service
#
#       deployment
#
#       network
#
#       provider
#
#       output-processing
#
#
# layers.
#
#
# Do not attach failure to a broader object than the evidence supports.
#
#
# ============================================================================
# FAILURE PROVENANCE MATTERS
# ============================================================================
#
# SEIR-I does not yet model detailed invocation failure provenance.
#
#
# That is another reason this module uses:
#
#
#       attempted_service_ids
#
#
# rather than trying to describe:
#
#
#       why the attempt failed
#
#
# before Agent 11 has the appropriate domain contract.
#
#
# ============================================================================
# FALLBACK DOES NOT DETERMINE REQUEST LIFECYCLE STATUS
# ============================================================================
#
# If:
#
#
#       can_attempt_fallback(...) == False
#
#
# FallbackEvaluator does not change:
#
#
#       AIRequest.status
#
#
# to:
#
#
#       FAILED
#
#
# or:
#
#
#       COMPLETED
#
#
# That belongs to broader orchestration semantics.
#
#
# This preserves the distinction:
#
#
#       NO MORE FALLBACK
#           !=
#       REQUEST FAILED
#
#
# ============================================================================
# FALLBACK DOES NOT CREATE AIResponse
# ============================================================================
#
# No AI invocation occurs inside FallbackEvaluator.
#
#
# Therefore this module cannot create:
#
#
#       AIResponse.SUCCESS
#
#       AIResponse.PARTIAL
#
#       AIResponse.FAILED
#
#
# AIResponse exists only when AI invocation actually occurred.
#
#
# ============================================================================
# FALLBACK DOES NOT REWRITE THE PREVIOUS AIResponse
# ============================================================================
#
# If a previous invocation produced a failed or partial response, fallback
# should not mutate that response into the result of another attempt.
#
#
# Future invocation-attempt modeling may preserve multiple attempt results.
#
#
# For SEIR-I:
#
#
#       PREVIOUS INVOCATION RESULT
#           !=
#       FUTURE INVOCATION RESULT
#
#
# ============================================================================
# FALLBACK DOES NOT REWRITE RoutingDecision
# ============================================================================
#
# Similarly:
#
#
#       RoutingDecision for cycle 1
#
#
# should not be mutated until it appears to describe:
#
#
#       routing cycle 2
#
#
# The first decision answered:
#
#
#       "What did Agent 11 select then?"
#
#
# A future decision answers:
#
#
#       "What did Agent 11 select after reevaluation?"
#
#
# Those are different facts.
#
#
# ============================================================================
# ROUTING CYCLE != INVOCATION ATTEMPT
# ============================================================================
#
# These concepts may become explicit in SEIR-II.
#
#
# A routing cycle determines:
#
#
#       WHAT SHOULD BE ATTEMPTED?
#
#
# An invocation attempt records:
#
#
#       WHAT WAS ACTUALLY ATTEMPTED?
#
#
# Therefore:
#
#
#       ROUTING DECISION
#           !=
#       INVOCATION ATTEMPT
#
#
# ============================================================================
# SELECTED != ATTEMPTED
# ============================================================================
#
# Even this distinction may matter later.
#
#
# A service may be selected and then never invoked because:
#
#
#       the request was cancelled
#
#       policy changed before invocation
#
#       orchestration stopped
#
#       another pre-invocation gate failed
#
#
# Therefore:
#
#
#       SELECTED SERVICE
#           !=
#       ATTEMPTED SERVICE
#
#
# This is another reason fallback should operate on explicit attempted-service
# information rather than merely reading selected_service_id.
#
#
# ============================================================================
# ATTEMPTED != SUCCESSFULLY CONTACTED
# ============================================================================
#
# Likewise:
#
#
#       attempt began
#
#
# does not necessarily mean:
#
#
#       provider received request
#
#
# Future invocation telemetry may need to distinguish these states.
#
#
# SEIR-I does not need to solve that here.
#
#
# ============================================================================
# WHY NO FALLBACK COUNT EXISTS YET
# ============================================================================
#
# FallbackEvaluator currently knows:
#
#
#       which services were attempted
#
#
# It does not know:
#
#
#       how many total attempts occurred
#
#       how many retries occurred
#
#       how many routing cycles occurred
#
#
# SEIR-I does not yet have recovery-budget semantics.
#
#
# Those belong in SEIR-II investigation.
#
#
# ============================================================================
# WHY NO TIMEOUT EXISTS HERE
# ============================================================================
#
# Timeout belongs to invocation or workflow execution.
#
#
# It is not part of:
#
#
#       "Does another unattempted candidate exist?"
#
#
# Therefore FallbackEvaluator contains no timeout configuration.
#
#
# ============================================================================
# WHY NO BACKOFF EXISTS HERE
# ============================================================================
#
# Backoff primarily concerns retry/recovery timing.
#
#
# FallbackEvaluator does not sleep.
#
# It does not schedule.
#
# It does not inspect clocks.
#
#
# ============================================================================
# WHY NO COST LIMIT EXISTS HERE
# ============================================================================
#
# Future recovery may need:
#
#
#       maximum recovery cost
#
#       maximum token budget
#
#       maximum invocation count
#
#
# But those concepts have not yet earned domain representation.
#
#
# The current evaluator therefore does not invent them.
#
#
# ============================================================================
# WHY NO PROVIDER-SPECIFIC FALLBACK EXISTS
# ============================================================================
#
# Never:
#
#
#       if failed_provider == AWS:
#           use Azure
#
#
# inside FallbackEvaluator.
#
#
# Provider placement and failure-domain reasoning belong elsewhere.
#
#
# A provider switch may eventually be one consequence of fresh routing.
#
#
# It is not the definition of fallback.
#
#
# ============================================================================
# FALLBACK != CLOUD SWITCH
# ============================================================================
#
# A fallback may:
#
#
#       remain in the same cloud
#
#       move to another cloud
#
#       move on-premises
#
#       move from on-premises to company cloud
#
#
# if policy and current viability permit.
#
#
# Therefore:
#
#
#       FALLBACK
#           !=
#       CLOUD SWITCH
#
#
# ============================================================================
# FALLBACK != MODEL SWITCH
# ============================================================================
#
# Likewise, fallback may eventually select:
#
#
#       a different service exposing the same model
#
#
# or:
#
#
#       a service exposing a different model
#
#
# depending upon future deployment architecture.
#
#
# Therefore:
#
#
#       FALLBACK
#           !=
#       MODEL SWITCH
#
#
# ============================================================================
# FALLBACK != ROUTING-DOMAIN SWITCH
# ============================================================================
#
# A replacement service might remain within:
#
#
#       COMPANY_CLOUD_LLM
#
#
# or move between permitted routing domains.
#
#
# Therefore fallback should not be encoded as:
#
#
#       EXTERNAL -> CLOUD -> ONPREM
#
#
# or any other fixed domain ladder.
#
#
# ============================================================================
# NO HARDCODED "SAFER" ROUTE
# ============================================================================
#
# It may be tempting to assume:
#
#
#       ONPREM is always safer than CLOUD
#
#
# or:
#
#
#       COMPANY CLOUD is always safer than EXTERNAL
#
#
# But policy determines authorization.
#
#
# Routing should not invent a universal security ordering among AIRoute
# values.
#
#
#       ENUM ORDER != SECURITY ORDER
#
#
# ============================================================================
# NO HARDCODED ROUTE ESCALATION
# ============================================================================
#
# Do not implement:
#
#
#       external failed -> company cloud
#
#       company cloud failed -> on-prem
#
#
# as universal fallback semantics.
#
#
# Candidate preference belongs to routing configuration/evaluation.
#
#
# ============================================================================
# NO HARDCODED ROUTE DE-ESCALATION
# ============================================================================
#
# Likewise, do not implement:
#
#
#       on-prem failed -> company cloud
#
#       company cloud failed -> external
#
#
# without fresh policy evaluation.
#
#
# ============================================================================
# ROUTING DOMAIN != FALLBACK PRIORITY
# ============================================================================
#
# AIRoute values identify routing domains.
#
#
# They do not inherently define:
#
#
#       first choice
#
#       second choice
#
#       emergency choice
#
#
# Candidate order currently carries SEIR-I preference.
#
#
# ============================================================================
# WHY FALLBACK DOES NOT SCORE
# ============================================================================
#
# Fallback should not introduce a second optimization system.
#
#
# Never:
#
#
#       fallback_score = ...
#
#
# unless future architecture explicitly requires a distinct recovery
# selection strategy.
#
#
# In SEIR-I:
#
#
#       FALLBACK PERMITS FRESH ROUTING
#
#
# and normal routing performs selection.
#
#
# ============================================================================
# ONE ROUTER, NOT TWO
# ============================================================================
#
# We should avoid:
#
#
#       normal_router()
#
# with one set of security semantics,
#
# and:
#
#
#       fallback_router()
#
# with another.
#
#
# The preferred conceptual architecture is:
#
#
#       INITIAL ROUTING
#           |
#           v
#       AIRouter
#
#
# and:
#
#
#       FALLBACK
#           |
#           v
#       FRESH EVALUATION
#           |
#           v
#       AIRouter
#
#
# This keeps selection semantics consistent.
#
#
# ============================================================================
# FALLBACK DOES NOT SOLVE MULTI-FM SELECTION
# ============================================================================
#
# Suppose fresh evaluation produces:
#
#
#       Claude      -> VIABLE
#
#       Gemini      -> VIABLE
#
#       Company FM  -> VIABLE
#
#
# FallbackEvaluator does not decide:
#
#
#       which model is best
#
#
# merely because the decision occurs during recovery.
#
#
# The multi-foundation-model selection problem remains deliberately deferred
# to SEIR-II.
#
#
#       FALLBACK
#           MUST NOT CREATE
#       A SECOND MODEL-SELECTION ALGORITHM
#
#
# ============================================================================
# SEIR-I PREFERENCE ORDER STILL APPLIES
# ============================================================================
#
# Current AIRouter semantics are:
#
#
#       SELECT THE FIRST VIABLE CANDIDATE
#       ACCORDING TO CANDIDATE ORDER
#
#
# Therefore fresh fallback evaluation may produce a new ordered candidate
# collection and AIRouter applies the same current rule.
#
#
# No special fallback ranking is required.
#
#
# ============================================================================
# HARD CONSTRAINTS STILL COME FIRST
# ============================================================================
#
# Even during recovery:
#
#
#       policy
#
#       capability
#
#       service availability
#
#       network availability
#
#
# remain hard viability dimensions.
#
#
# Candidate preference operates only after those constraints have been
# evaluated.
#
#
#       FILTER BY CONSTRAINTS FIRST
#
#       SELECT SECOND
#
#
# ============================================================================
# POLICY NEVER BECOMES A RECOVERY SCORE
# ============================================================================
#
# Never:
#
#
#       fallback_score =
#           model_quality
#           + availability
#           + policy
#
#
# A policy-denied candidate is not:
#
#
#       less preferred
#
#
# It is:
#
#
#       NOT PERMITTED
#
#
# ============================================================================
# UNKNOWN MUST REMAIN UNKNOWN
# ============================================================================
#
# Suppose fresh network evaluation returns:
#
#
#       UNKNOWN
#
#
# Fallback must not rewrite that as:
#
#
#       AVAILABLE
#
#
# merely because the system needs another route.
#
#
# Likewise:
#
#
#       UNKNOWN != UNAVAILABLE
#
#
# unless the relevant domain explicitly defines that mapping.
#
#
# Preserve uncertainty while still failing closed where required.
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ============================================================================
# FALLBACK CANNOT INVENT A ROUTE
# ============================================================================
#
# If no remaining candidate becomes viable after fresh evaluation:
#
#
#       STOP.
#
#
# Do not:
#
#
#       invent another provider
#
#       weaken classification
#
#       lower reasoning level
#
#       ignore network evidence
#
#       bypass user restrictions
#
#
# Sometimes:
#
#
#       NO ROUTE
#
#
# is the correct result.
#
#
# ============================================================================
# NO_VIABLE_ROUTE DURING FALLBACK IS NOT ROUTER FAILURE
# ============================================================================
#
# A fresh routing cycle may correctly produce:
#
#
#       RoutingStatus.NO_VIABLE_ROUTE
#
#
# because alternatives exist but none currently satisfy all viability
# requirements.
#
#
# That is a valid routing result.
#
#
#       NO_VIABLE_ROUTE
#           !=
#       ROUTER MALFUNCTION
#
#
# ============================================================================
# BLOCKED DURING FALLBACK IS NOT ROUTER FAILURE
# ============================================================================
#
# Likewise, if all freshly evaluated alternatives are policy denied:
#
#
#       RoutingStatus.BLOCKED
#
#
# is correct.
#
#
# Security enforcement remains valid during recovery.
#
#
# ============================================================================
# NULL DOES NOT MEAN "NO FALLBACK"
# ============================================================================
#
# RoutingStatus.NULL means AI routing was intentionally unnecessary.
#
#
# It is not a synonym for:
#
#
#       fallback unavailable
#
#
# FallbackEvaluator should not produce or reinterpret NULL.
#
#
# ============================================================================
# FALLBACK IS NOT AN EXCUSE TO BYPASS ORCHESTRATION
# ============================================================================
#
# A common implementation shortcut would be:
#
#
#       try:
#           invoke(selected)
#       except:
#           invoke(second_service)
#
#
# That bypasses:
#
#
#       policy reevaluation
#
#       capability reevaluation
#
#       service reevaluation
#
#       network reevaluation
#
#       normal route selection
#
#
# and therefore bypasses the Agent 11 architecture.
#
#
# ============================================================================
# THE DANGEROUS FIVE-LINE FALLBACK
# ============================================================================
#
# Never reduce fallback to:
#
#
#       for candidate in candidates:
#           if candidate.status is VIABLE:
#               if candidate.service_id != failed_service:
#                   invoke(candidate)
#
#
# This code appears convenient.
#
# Architecturally it is wrong because:
#
#
#       candidate.status is historical
#
#       policy may have changed
#
#       service state may have changed
#
#       network state may have changed
#
#       invocation bypasses AIRouter
#
#
# ============================================================================
# FALLBACK MUST RETURN TO THE ROUTING PIPELINE
# ============================================================================
#
# The correct conceptual path is:
#
#
#       ATTEMPT UNUSABLE
#              |
#              v
#       FallbackEvaluator
#              |
#          +---+---+
#          |       |
#        False    True
#          |       |
#          v       v
#        STOP   REMOVE / EXCLUDE
#               ATTEMPTED SERVICES
#                    |
#                    v
#              FRESH EVALUATION
#                    |
#       +------------+------------+------------+
#       |            |            |            |
#       v            v            v            v
#     POLICY       MODEL       SERVICE       NETWORK
#       |            |            |            |
#       +------------+------------+------------+
#                    |
#                    v
#            RoutingCandidate[]
#                    |
#                    v
#                 AIRouter
#                    |
#             +------+------+
#             |             |
#          SELECTED     BLOCKED /
#             |        NO_VIABLE_ROUTE
#             v
#        NEW ATTEMPT
#
#
# ============================================================================
# WHERE DOES FRESH CANDIDATE EVALUATION LIVE?
# ============================================================================
#
# SEIR-I has not yet finalized this responsibility.
#
#
# We currently have:
#
#
#       ModelRouter
#           -> capability suitability
#
#
#       policy subsystem
#           -> authorization
#
#
#       runtime/service subsystem
#           -> service availability
#
#
#       network subsystem
#           -> path availability
#
#
# Something must combine those facts into:
#
#
#       RoutingCandidate
#
#
# That responsibility should NOT be forced into:
#
#
#       AIRouter
#
# or:
#
#       FallbackEvaluator
#
#
# merely because those classes already exist.
#
#
# ============================================================================
# CANDIDATE-EVALUATION GAP
# ============================================================================
#
# The current architecture therefore contains a deliberately visible design
# question:
#
#
#       WHO COMBINES:
#
#           POLICY
#
#           CAPABILITY
#
#           SERVICE STATE
#
#           NETWORK STATE
#
#       INTO:
#
#           RoutingCandidate
#
#
# Possible future answers include:
#
#
#       routing/orchestrator.py
#
# or:
#
#       routing/candidate_evaluator.py
#
#
# SEIR-I should decide this based on responsibility clarity rather than
# forcing the behavior into the initial directory plan.
#
#
#       INITIAL FILE TREE
#           !=
#       ARCHITECTURAL LAW
#
#
# ============================================================================
# DO NOT TURN RoutingOrchestrator INTO A GOD OBJECT
# ============================================================================
#
# If routing/orchestrator.py eventually:
#
#
#       evaluates policy
#
#       evaluates capabilities
#
#       checks service health
#
#       checks BGP
#
#       queries cloud providers
#
#       creates candidates
#
#       selects routes
#
#       invokes models
#
#       handles retries
#
#       handles fallback
#
#
# then the architecture has merely moved the God Object problem into a file
# named orchestrator.py.
#
#
# Coordination is not ownership of every behavior.
#
#
# ============================================================================
# ORCHESTRATOR SHOULD COORDINATE COLLABORATORS
# ============================================================================
#
# Conceptually:
#
#
#       RoutingOrchestrator
#              |
#       +------+------+------+------+
#       |      |      |      |      |
#       v      v      v      v      v
#     POLICY  MODEL SERVICE NETWORK CANDIDATE
#                                      |
#                                      v
#                                   AIRouter
#
#
# Exact SEIR-I collaborators remain to be finalized.
#
#
# ============================================================================
# FALLBACK AND THE CANDIDATE-EVALUATION GAP
# ============================================================================
#
# Fallback makes this missing responsibility more obvious because recovery
# requires:
#
#
#       FRESH RoutingCandidate[]
#
#
# rather than:
#
#
#       REUSED RoutingCandidate[]
#
#
# That is useful architectural evidence.
#
#
# Do not hide the gap.
#
# Solve it deliberately when we reach routing orchestration.
#
#
# ============================================================================
# WHY FallbackEvaluator IS AN ORDINARY PYTHON CLASS
# ============================================================================
#
# FallbackEvaluator represents behavior.
#
#
# It is not:
#
#
#       persisted state
#
#       API payload
#
#       domain record
#
#       configuration object
#
#
# Therefore it does not inherit:
#
#
#       Agent11BaseModel
#
#
# Pydantic belongs to the contracts passed into and out of behavior.
#
#
#       MODEL = NOUN / CONTRACT
#
#       EVALUATOR = BEHAVIOR
#
#
# ============================================================================
# WHY THERE IS NO INTERNAL STATE
# ============================================================================
#
# FallbackEvaluator currently stores no:
#
#
#       attempted services
#
#       counters
#
#       previous decisions
#
#       service state
#
#       policy state
#
#
# Everything needed for the current question is supplied explicitly.
#
#
# This makes the evaluator deterministic and easy to test.
#
#
# ============================================================================
# DETERMINISM
# ============================================================================
#
# Given the same:
#
#
#       FallbackStrategy
#
#       attempted_service_ids
#
#       RoutingCandidate[]
#
#
# FallbackEvaluator returns the same result.
#
#
# It does not inspect:
#
#
#       current time
#
#       environment variables
#
#       databases
#
#       cloud APIs
#
#       network state
#
#       provider APIs
#
#       random values
#
#
# ============================================================================
# PURE DECISION LOGIC
# ============================================================================
#
# The evaluator:
#
#
#       does not mutate inputs
#
#       does not perform I/O
#
#       does not invoke AI
#
#       does not change policy
#
#       does not modify request state
#
#
# This keeps fallback eligibility testable without infrastructure.
#
#
# ============================================================================
# FRAMEWORK INDEPENDENCE
# ============================================================================
#
# FallbackEvaluator does not care whether higher-level execution uses:
#
#
#       plain Python
#
#       LangGraph
#
#       CrewAI
#
#       Amazon Bedrock AgentCore
#
#       Kubernetes controllers
#
#       a future durable workflow engine
#
#
# Its semantic question remains unchanged.
#
#
#       TOOLS CHANGE.
#
#       RECOVERY INVARIANTS SHOULD SURVIVE THEM.
#
#
# ============================================================================
# MULTI-CLOUD INDEPENDENCE
# ============================================================================
#
# FallbackEvaluator contains no assumptions about:
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
#       on-premises infrastructure
#
#
# A fallback may ultimately move between any permitted viable services.
#
#
# The evaluator itself does not need to know where they run.
#
#
# ============================================================================
# ROUTING DOMAIN != CLOUD PROVIDER
# ============================================================================
#
# Preserve the existing Agent 11 distinction:
#
#
#       COMPANY_CLOUD_LLM
#
#
# is a routing domain.
#
#
# It is not:
#
#
#       AWS
#
#
# and it is not:
#
#
#       Azure
#
#
# and it is not:
#
#
#       GCP
#
#
# and it is not:
#
#
#       OCI
#
#
# Fallback must not accidentally collapse those concepts.
#
#
# ============================================================================
# MODEL PROVIDER != FALLBACK TARGET
# ============================================================================
#
# FallbackEvaluator also does not reason:
#
#
#       Claude failed -> Gemini
#
#
# or:
#
#
#       Gemini failed -> proprietary model
#
#
# Those are model-selection decisions.
#
#
# SEIR-I does not encode them.
#
#
# ============================================================================
# FAILURE DOMAIN != MODEL IDENTITY
# ============================================================================
#
# Even before SEIR-II formally models failure domains, preserve this
# conceptual distinction.
#
#
# Two different models may depend on:
#
#
#       the same cloud
#
#       the same region
#
#       the same network
#
#       the same cluster
#
#
# Therefore:
#
#
#       DIFFERENT MODEL
#           !=
#       INDEPENDENT RECOVERY PATH
#
#
# ============================================================================
# SAME MODEL != SAME FAILURE DOMAIN
# ============================================================================
#
# Conversely, the same logical model may eventually be exposed through:
#
#
#       independent services
#
#       independent regions
#
#       independent cloud providers
#
#
# Therefore:
#
#
#       SAME MODEL
#           !=
#       SAME OPERATIONAL FAILURE DOMAIN
#
#
# This is one reason model, service, and deployment must remain distinct.
#
#
# ============================================================================
# FALLBACK AND BGP
# ============================================================================
#
# Future BGP integration may affect whether a freshly evaluated service has
# a viable network path.
#
#
# But BGP remains downstream evidence for:
#
#
#       PATH AVAILABLE?
#
#
# It does not determine:
#
#
#       MAY FALLBACK BEGIN?
#
#
# and it does not grant:
#
#
#       POLICY AUTHORIZATION
#
#
# ============================================================================
# FALLBACK AND SD-WAN
# ============================================================================
#
# The same separation applies to SD-WAN.
#
#
# SD-WAN may influence fresh path viability.
#
#
# FallbackEvaluator should not contain SD-WAN logic.
#
#
# ============================================================================
# FALLBACK AND MCP
# ============================================================================
#
# MCP tool execution is not AI reasoning fallback.
#
#
# If a model invocation fails, Agent 11 must not automatically decide:
#
#
#       "Use an MCP tool instead."
#
#
# That would change:
#
#
#       reasoning
#
#
# into:
#
#
#       tool execution
#
#
# and potentially change authority.
#
#
#       AI REASONING != TOOL EXECUTION
#
#
# ============================================================================
# FALLBACK DOES NOT INCREASE EXECUTION AUTHORITY
# ============================================================================
#
# Recovery pressure must not expand what Agent 11 may execute.
#
#
# If the original reasoning route fails:
#
#
#       NO NEW EXECUTION AUTHORITY IS CREATED
#
#
# by that failure.
#
#
# ============================================================================
# FALLBACK AND SUCCESSFUL REASONING
# ============================================================================
#
# Even if fallback eventually finds a service and receives a successful
# AIResponse:
#
#
#       SUCCESSFUL AI RESPONSE
#
#
# still does not mean:
#
#
#       DOWNSTREAM ACTION AUTHORIZED
#
#
# Preserve:
#
#
#       REASONING AUTHORIZATION
#           !=
#       EXECUTION AUTHORIZATION
#
#
# ============================================================================
# SECURITY BEFORE AVAILABILITY
# ============================================================================
#
# Fallback exists to improve resilience.
#
#
# But resilience operates within security constraints.
#
#
# Therefore:
#
#
#       SECURITY CONSTRAINTS
#           BOUND
#       AVAILABILITY RECOVERY
#
#
# not:
#
#
#       AVAILABILITY RECOVERY
#           OVERRIDES
#       SECURITY CONSTRAINTS
#
#
# ============================================================================
# AVAILABILITY IS NOT ABSOLUTE
# ============================================================================
#
# A secure AI system must be willing to say:
#
#
#       "No permitted service is currently available."
#
#
# That is preferable to:
#
#
#       "Something was available, so we sent the data there."
#
#
# ============================================================================
# FAIL CLOSED WITHOUT LYING
# ============================================================================
#
# Suppose fresh evaluation cannot determine whether a route is safe.
#
#
# Agent 11 may fail closed.
#
#
# But it should preserve the actual reason:
#
#
#       INDETERMINATE
#
#       UNKNOWN
#
#
# rather than rewriting uncertainty as:
#
#
#       DENY
#
#       UNAVAILABLE
#
#
# unless the relevant domain semantics explicitly say so.
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ============================================================================
# FALLBACK SHOULD REMAIN EXPLAINABLE
# ============================================================================
#
# Operators should eventually be able to understand:
#
#
#       why fallback was allowed
#
#       which services had already been attempted
#
#       why another routing cycle occurred
#
#       why alternatives were rejected
#
#       what route was subsequently selected
#
#
# The current small evaluator supports that future by avoiding hidden
# heuristics.
#
#
# ============================================================================
# CURRENT LIMITATION: NO InvocationAttempt MODEL
# ============================================================================
#
# SEIR-I currently represents attempted services as:
#
#
#       set[str]
#
#
# This is deliberately minimal.
#
#
# It cannot represent:
#
#
#       attempt number
#
#       start time
#
#       end time
#
#       failure reason
#
#       provider response
#
#       retryability
#
#       cost
#
#       token usage
#
#
# Those may eventually justify:
#
#
#       InvocationAttempt
#
#
# in SEIR-II.
#
#
# ============================================================================
# CURRENT LIMITATION: NO RETRY SEMANTICS
# ============================================================================
#
# SEIR-I fallback does not decide whether an attempted service may be retried.
#
#
# Therefore:
#
#
#       attempted_service_ids
#
#
# currently excludes that service from fallback.
#
#
# A future retry subsystem may independently permit another attempt against
# the same service.
#
#
# ============================================================================
# CURRENT LIMITATION: NO RECOVERY BUDGET
# ============================================================================
#
# SEIR-I does not currently limit fallback by:
#
#
#       attempt count
#
#       elapsed time
#
#       token usage
#
#       monetary cost
#
#
# This is a known limitation.
#
#
# It should not be "fixed" by adding arbitrary constants here.
#
#
# ============================================================================
# CURRENT LIMITATION: NO FAILURE CLASSIFICATION
# ============================================================================
#
# FallbackEvaluator currently does not know whether the preceding attempt
# ended because of:
#
#
#       timeout
#
#       network failure
#
#       service error
#
#       model error
#
#       malformed response
#
#       cancellation
#
#
# Therefore it cannot make failure-type-specific recovery decisions.
#
#
# That is deliberate in SEIR-I.
#
#
# ============================================================================
# CURRENT LIMITATION: NO CORRELATED-FAILURE AWARENESS
# ============================================================================
#
# SEIR-I does not currently know whether two services share:
#
#
#       provider
#
#       region
#
#       cluster
#
#       network path
#
#       power domain
#
#       model deployment
#
#
# Therefore fallback cannot yet optimize for independent failure domains.
#
#
# ============================================================================
# CURRENT LIMITATION: NO DYNAMIC CANDIDATE DISCOVERY
# ============================================================================
#
# Part I uses the original candidate collection as the known service universe.
#
#
# This means SEIR-I fallback does not currently discover a completely new
# service that was absent from the original routing evaluation.
#
#
# This is an important limitation.
#
#
# Future routing may decide that fallback should rediscover the service
# universe before reevaluation.
#
#
# That question is intentionally deferred.
#
#
# ============================================================================
# KNOWN UNIVERSE != ALL POSSIBLE SERVICES
# ============================================================================
#
# Because fallback currently receives the original candidates:
#
#
#       candidates
#
#
# means:
#
#
#       SERVICES KNOWN TO THIS ROUTING CYCLE
#
#
# not:
#
#
#       EVERY SERVICE THAT COULD POSSIBLY EXIST NOW
#
#
# SEIR-II should revisit this when runtime registries and dynamic service
# discovery become mature.
#
#
# ============================================================================
# CURRENT LIMITATION: NO POLICY-CHANGE EVENT
# ============================================================================
#
# SEIR-I requires fresh policy evaluation conceptually.
#
#
# It does not yet model:
#
#
#       "Policy changed while the request was executing."
#
#
# as an explicit event.
#
#
# That may become important for long-running workflows.
#
#
# ============================================================================
# CURRENT LIMITATION: NO DURABLE RECOVERY STATE
# ============================================================================
#
# attempted_service_ids currently exists only as supplied runtime state.
#
#
# If the process crashes during recovery, SEIR-I has not yet defined how
# recovery history is reconstructed.
#
#
# Durable workflow behavior belongs to later architecture.
#
#
# ============================================================================
# CURRENT LIMITATION: NO CONCURRENT ATTEMPTS
# ============================================================================
#
# SEIR-I currently assumes a simple sequential mental model:
#
#
#       select A
#
#       attempt A
#
#       A unusable
#
#       consider fallback
#
#       select B
#
#
# It does not model:
#
#
#       speculative parallel invocation
#
#       hedged requests
#
#       race-to-first-success
#
#
# Those introduce substantially different cost, cancellation, policy, and
# telemetry semantics.
#
#
# ============================================================================
# CURRENT LIMITATION: NO FALLBACK-SPECIFIC MODEL SELECTION
# ============================================================================
#
# This is deliberate.
#
#
# SEIR-I does not answer:
#
#
#       "Which alternative FM is the best fallback?"
#
#
# That is part of the broader SEIR-II multi-model selection problem.
#
#
# ============================================================================
# CURRENT LIMITATION: NO RECOVERY TELEMETRY CONTRACT
# ============================================================================
#
# Future telemetry may need to record:
#
#
#       original selected service
#
#       attempted services
#
#       recovery trigger
#
#       fallback strategy
#
#       fresh routing decision
#
#       eventual outcome
#
#
# SEIR-I does not yet define that event model.
#
#
# ============================================================================
# CURRENT LIMITATION: NO RECOVERY PROVENANCE
# ============================================================================
#
# SEIR-I does not yet preserve a complete chain such as:
#
#
#       attempt 1
#           |
#           v
#       timeout
#           |
#           v
#       fallback eligibility
#           |
#           v
#       routing cycle 2
#           |
#           v
#       attempt 2
#
#
# That may eventually be important for audit and incident analysis.
#
#
# ============================================================================
# CURRENT LIMITATION: NO RECOVERY POLICY OBJECT
# ============================================================================
#
# FallbackStrategy currently provides only:
#
#
#       NONE
#
#       NEXT_VIABLE
#
#
# SEIR-I does not have a larger:
#
#
#       RecoveryPolicy
#
#
# containing:
#
#
#       retries
#
#       fallback count
#
#       time budget
#
#       cost budget
#
#       provider diversity
#
#       regional diversity
#
#
# That richer object may eventually become useful.
#
#
# It has not earned existence yet.
#
#
# ============================================================================
# REVIEWER NOTE — THE bool IS NOT NAIVE
# ============================================================================
#
# A reviewer may see:
#
#
#       can_attempt_fallback(...) -> bool
#
#
# and conclude:
#
#
#       "This is too simple for enterprise recovery."
#
#
# Correct:
#
#
#       it is too simple for the final recovery architecture.
#
#
# But it is sufficient for the current SEIR-I question.
#
#
# The simplicity prevents this component from prematurely owning:
#
#
#       retry
#
#       failure classification
#
#       route selection
#
#       policy
#
#       network
#
#       model selection
#
#       provider behavior
#
#
# ============================================================================
# REVIEWER NOTE — THE METHOD DOES NOT PROVE FALLBACK EXISTS
# ============================================================================
#
# Returning True proves only:
#
#
#       an unattempted known service exists
#
#       and strategy permits another routing cycle
#
#
# It does not prove:
#
#
#       a compliant alternative exists
#
#
# That fact can be established only through fresh evaluation.
#
#
# ============================================================================
# REVIEWER NOTE — RE-EVALUATING REJECTED CANDIDATES IS INTENTIONAL
# ============================================================================
#
# A reviewer may notice that Part I does not filter:
#
#
#       candidate.status == REJECTED
#
#
# from fallback eligibility.
#
#
# This is deliberate.
#
#
# Historical rejection may have depended upon dynamic state.
#
#
# The fresh routing cycle determines whether the candidate remains rejected.
#
#
# ============================================================================
# REVIEWER NOTE — THIS IS NOT POLICY RETRY
# ============================================================================
#
# Re-evaluating a previously policy-denied candidate does not mean:
#
#
#       "Keep asking policy until it says yes."
#
#
# It means:
#
#
#       "Evaluate current policy as part of the new routing cycle."
#
#
# If policy is unchanged:
#
#
#       the result remains denied.
#
#
# ============================================================================
# REVIEWER NOTE — FALLBACK DOES NOT GUARANTEE HIGH AVAILABILITY
# ============================================================================
#
# Agent 11 intentionally prioritizes compliant routing over unconditional
# availability.
#
#
# There may be circumstances where:
#
#
#       no compliant alternative exists.
#
#
# That is an expected system state.
#
#
# ============================================================================
# REVIEWER NOTE — NO SECURITY DOWNGRADE PATH EXISTS HERE
# ============================================================================
#
# FallbackEvaluator contains no mechanism for:
#
#
#       changing DataClassification
#
#       changing UserDataPreference
#
#       changing PolicyDecision
#
#       changing ReasoningLevel
#
#       changing capability requirements
#
#
# This absence is intentional.
#
#
# ============================================================================
# REVIEWER NOTE — NO PROVIDER PREFERENCE EXISTS HERE
# ============================================================================
#
# FallbackEvaluator does not know whether a service belongs to:
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
#       an on-premises environment
#
#
# Provider-specific recovery belongs to later deployment/runtime architecture.
#
#
# ============================================================================
# REVIEWER NOTE — FALLBACK IS NOT A SECOND ROUTER
# ============================================================================
#
# The architecture intentionally returns recovery back to normal routing.
#
#
#       ONE ROUTING SEMANTIC
#
#
# is preferable to:
#
#
#       NORMAL ROUTING RULES
#
#           +
#
#       SPECIAL EMERGENCY ROUTING RULES
#
#
# unless future operational evidence proves that distinct recovery selection
# semantics are necessary.
#
#
# ============================================================================
# SEIR-I FALLBACK DECISION RECORD
# ============================================================================
#
# CURRENT QUESTION:
#
#
#       MAY ANOTHER ROUTING CYCLE BE ATTEMPTED?
#
#
# CURRENT INPUT:
#
#
#       FallbackStrategy
#
#       attempted_service_ids
#
#       original RoutingCandidate collection
#
#
# CURRENT OUTPUT:
#
#
#       bool
#
#
# CURRENT STRATEGIES:
#
#
#       NONE
#
#           -> no fallback
#
#
#       NEXT_VIABLE
#
#           -> permit fresh routing if at least one
#              known service remains unattempted
#
#
# CURRENT EXCLUSION:
#
#
#       services already attempted during the
#       current recovery lifecycle
#
#
# CURRENT CANDIDATE STATUS BEHAVIOR:
#
#
#       historical candidate status is ignored
#
#
# CURRENT FRESHNESS RULE:
#
#
#       remaining services require new viability evaluation
#
#
# CURRENT NON-GOALS:
#
#
#       retry
#
#       route selection
#
#       model selection
#
#       policy evaluation
#
#       capability evaluation
#
#       service-health evaluation
#
#       network evaluation
#
#       provider selection
#
#       cloud selection
#
#       invocation
#
#       request lifecycle management
#
#       attempt history
#
#       recovery budgets
#
#       failure classification
#
#       durable recovery
#
#
# ============================================================================
# PART II FINAL INVARIANTS
# ============================================================================
#
#       FALLBACK = NEW ROUTING CYCLE
#
#
#       FALLBACK != RETRY
#
#       FALLBACK != FAILOVER
#
#       FALLBACK != DISASTER RECOVERY
#
#
#       FALLBACK != ROUTER
#
#       FALLBACK != ROUTE SELECTION
#
#       FALLBACK != MODEL SELECTION
#
#
#       FALLBACK != CLOUD SWITCH
#
#       FALLBACK != MODEL SWITCH
#
#       FALLBACK != ROUTING-DOMAIN SWITCH
#
#
#       ATTEMPTED SERVICE != FAILED SERVICE
#
#       ATTEMPTED SERVICE SET != INVOCATION HISTORY
#
#
#       SELECTED != ATTEMPTED
#
#       ATTEMPTED != SUCCESSFULLY CONTACTED
#
#
#       INVOCATION FAILURE != SERVICE FAILURE
#
#       INVOCATION FAILURE != MODEL FAILURE
#
#
#       ROUTING CYCLE != INVOCATION ATTEMPT
#
#
#       CANDIDATE UNIVERSE != CURRENT VIABILITY
#
#
#       OLD VIABLE != CURRENT VIABLE
#
#       OLD REJECTED != CURRENT REJECTED
#
#
#       PREVIOUSLY AUTHORIZED != CURRENTLY AUTHORIZED
#
#       PREVIOUSLY HEALTHY != CURRENTLY HEALTHY
#
#       PREVIOUSLY REACHABLE != CURRENTLY REACHABLE
#
#
#       HISTORICAL EVIDENCE != CURRENT EVIDENCE
#
#
#       NEW EVALUATION
#           SHOULD PRODUCE
#       NEW EVALUATION RESULT
#
#
#       STATE EVOLUTION != HISTORY REWRITING
#
#
#       RE-EVALUATION != AUTHORIZATION RESET
#
#
#       FALLBACK != POLICY ESCAPE
#
#       FALLBACK != SECURITY DOWNGRADE
#
#       FALLBACK != CAPABILITY REDUCTION
#
#       FALLBACK != REASONING REDUCTION
#
#       FALLBACK != REQUIREMENT REDUCTION
#
#       FALLBACK != DATA-CLASSIFICATION REDUCTION
#
#       FALLBACK != USER-POLICY REDUCTION
#
#
#       ROUTING FAILURE != DECLASSIFICATION EVENT
#
#
#       FAILURE OF AN AUTHORIZED ROUTE
#           DOES NOT
#       AUTHORIZE A PROHIBITED ROUTE
#
#
#       AVAILABILITY PRESSURE
#           !=
#       PERMISSION TO CHANGE REQUESTER INTENT
#
#
#       FALLBACK MAY REDUCE AVAILABILITY.
#
#       FALLBACK MUST NEVER REDUCE SECURITY POLICY.
#
#
#       NO COMPLIANT FALLBACK
#           MAY BE
#       SUCCESSFUL SECURITY ENFORCEMENT
#
#
#       CAN ATTEMPT FALLBACK
#           !=
#       FALLBACK AVAILABLE
#
#       CAN ATTEMPT FALLBACK
#           !=
#       FALLBACK WILL SUCCEED
#
#
#       UNATTEMPTED CANDIDATE
#           !=
#       VIABLE CANDIDATE
#
#
#       FallbackStrategy.NEXT_VIABLE
#           !=
#       NEXT HISTORICALLY VIABLE CANDIDATE
#
#
#       NEXT_VIABLE
#           =
#       PERMIT FRESH EVALUATION
#       OF UNATTEMPTED SERVICES
#
#
#       FALLBACK PERMISSION
#           !=
#       DATA-ROUTING AUTHORIZATION
#
#
#       POLICY DENIED
#           !=
#       LESS PREFERRED
#
#
#       POLICY NEVER BECOMES A SCORE
#
#
#       ENUM ORDER != SECURITY ORDER
#
#
#       UNKNOWN != NEGATIVE
#
#       FAIL CLOSED != FALSIFY STATE
#
#
#       NO_VIABLE_ROUTE != ROUTER FAILURE
#
#       BLOCKED != ROUTER FAILURE
#
#
#       ONE ROUTER
#           >
#       NORMAL ROUTER + SECRET FALLBACK ROUTER
#
#
#       FALLBACK
#           MUST NOT CREATE
#       A SECOND MODEL-SELECTION ALGORITHM
#
#
#       DIFFERENT MODEL
#           !=
#       INDEPENDENT FAILURE DOMAIN
#
#
#       SAME MODEL
#           !=
#       SAME OPERATIONAL FAILURE DOMAIN
#
#
#       ROUTING DOMAIN != CLOUD PROVIDER
#
#
#       AI REASONING != TOOL EXECUTION
#
#
#       REASONING AUTHORIZATION
#           !=
#       EXECUTION AUTHORIZATION
#
#
#       MODEL = NOUN / CONTRACT
#
#       EVALUATOR = BEHAVIOR
#
#
#       MORE STRUCTURE != MORE SEMANTICS
#
#
#       INITIAL FILE TREE != ARCHITECTURAL LAW
#
#
#       TOOLS CHANGE.
#
#       RECOVERY INVARIANTS SHOULD SURVIVE THEM.
#
#
# ============================================================================
# END PART II
# ============================================================================

# ============================================================================
# PART III
#
# NOTES TO FUTURE SELF — SEIR-II RECOVERY ARCHITECTURE
# ============================================================================
#
# Dear Future Self:
#
# If you are reading this, Agent 11 has probably become more complicated.
#
# There may now be:
#
#       multiple foundation models
#
#       multiple proprietary models
#
#       multiple cloud providers
#
#       multiple regions
#
#       multiple deployments of the same logical model
#
#       dynamic service discovery
#
#       retries
#
#       failover
#
#       circuit breakers
#
#       recovery budgets
#
#       durable workflows
#
#       richer telemetry
#
#       BGP / SD-WAN integration
#
#       and several meetings explaining why all of this is necessary.
#
#
# Before changing fallback.py, remember what SEIR-I deliberately established:
#
#
#       FALLBACK
#           =
#       PERMISSION TO BEGIN ANOTHER ROUTING CYCLE
#
#
# It was intentionally NOT:
#
#
#       route selection
#
#       model selection
#
#       retry
#
#       failover
#
#       disaster recovery
#
#       policy override
#
#       service-health management
#
#       network recovery
#
#       invocation execution
#
#
# Do not expand this file merely because recovery has become complicated.
#
#
# ============================================================================
# FUTURE-AWARE != FUTURE-BLOATED
# ============================================================================
#
# SEIR-I intentionally did not attempt to predict the complete recovery
# architecture.
#
#
# Future requirements should earn future contracts.
#
#
#       POSSIBLE FUTURE COMPLEXITY
#           !=
#       REQUIRED CURRENT COMPLEXITY
#
#
# If SEIR-II needs additional objects, create them because operational
# evidence demonstrates a real domain concept.
#
#
# Do not create them merely because their names sound plausible.
#
#
# ============================================================================
# START WITH OPERATIONAL EVIDENCE
# ============================================================================
#
# Before expanding fallback behavior, examine actual SEIR-I telemetry.
#
#
# Ask:
#
#
#       Why did invocations fail?
#
#       How frequently did fallback occur?
#
#       Which failures recovered successfully?
#
#       Which alternatives were selected?
#
#       How often did policy prevent fallback?
#
#       How often did network state prevent fallback?
#
#       How often did service availability prevent fallback?
#
#       How often were all remaining models incapable?
#
#       How often did fallback increase latency?
#
#       How much did fallback increase cost?
#
#       Were failures correlated across services?
#
#       Did the same service repeatedly fail?
#
#
# Build SEIR-II recovery around observed failure modes.
#
#
#       TELEMETRY BEFORE TAXONOMY
#
#
# ============================================================================
# FUTURE QUESTION — DO WE NEED InvocationAttempt?
# ============================================================================
#
# SEIR-I represents attempted services with:
#
#
#       set[str]
#
#
# This answers only:
#
#
#       "HAS THIS SERVICE ALREADY BEEN ATTEMPTED?"
#
#
# SEIR-II may discover that this is insufficient.
#
#
# A future invocation-attempt concept might need to represent:
#
#
#       request identifier
#
#       service identifier
#
#       attempt identifier
#
#       attempt number
#
#       start time
#
#       end time
#
#       outcome
#
#       failure category
#
#       retryability
#
#       token usage
#
#       cost
#
#       latency
#
#
# But:
#
#
#       DO NOT ADD InvocationAttempt
#       UNTIL THE SYSTEM ACTUALLY NEEDS IT.
#
#
# The name is intentionally not locked as a current contract.
#
#
# ============================================================================
# AN ATTEMPT MAY EVENTUALLY BECOME FIRST-CLASS
# ============================================================================
#
# A future request may conceptually look like:
#
#
#       REQUEST
#          |
#          +--> Attempt 1
#          |       |
#          |       +--> Service A
#          |       +--> timeout
#          |
#          +--> Attempt 2
#          |       |
#          |       +--> Service B
#          |       +--> network interruption
#          |
#          +--> Attempt 3
#                  |
#                  +--> Service C
#                  +--> success
#
#
# If the system needs to explain or reconstruct this sequence, a set of
# service identifiers will no longer be sufficient.
#
#
# ============================================================================
# ATTEMPT HISTORY != CURRENT PROCESSING STATE
# ============================================================================
#
# If invocation attempts become first-class, do not automatically place an
# unlimited attempt history inside AIProcessingState.
#
#
# Remember:
#
#
#       CURRENT STATE != EVENT HISTORY
#
#
# A durable execution system, telemetry system, or audit system may be the
# correct owner of historical attempts.
#
#
# ============================================================================
# FUTURE QUESTION — WHAT ACTUALLY COUNTS AS AN ATTEMPT?
# ============================================================================
#
# SEIR-I deliberately leaves this imprecise.
#
#
# Future systems may need to distinguish:
#
#
#       service selected
#
#       invocation prepared
#
#       connection attempted
#
#       request transmitted
#
#       provider acknowledged request
#
#       inference started
#
#       tokens generated
#
#       response received
#
#       response validated
#
#
# These are not necessarily equivalent.
#
#
#       SELECTED != ATTEMPTED
#
#       ATTEMPTED != TRANSMITTED
#
#       TRANSMITTED != ACCEPTED
#
#       ACCEPTED != COMPLETED
#
#       COMPLETED != USABLE
#
#
# Do not collapse them unless the operational model truly permits it.
#
#
# ============================================================================
# FUTURE QUESTION — FAILURE CLASSIFICATION
# ============================================================================
#
# SEIR-II may need to distinguish why an invocation did not produce a usable
# result.
#
#
# Possible categories may include:
#
#
#       connection failure
#
#       DNS failure
#
#       TLS failure
#
#       network timeout
#
#       provider timeout
#
#       provider throttling
#
#       capacity exhaustion
#
#       authentication failure
#
#       authorization failure
#
#       service rejection
#
#       model inference failure
#
#       malformed response
#
#       schema-validation failure
#
#       output-policy rejection
#
#       cancellation
#
#       infrastructure failure
#
#
# Do not assume these all deserve the same recovery behavior.
#
#
# ============================================================================
# FAILURE LOCATION MATTERS
# ============================================================================
#
# A failed request may indicate a problem with:
#
#
#       the request
#
#       the model
#
#       the service
#
#       the deployment
#
#       the provider
#
#       the network path
#
#       authentication
#
#       authorization
#
#       output processing
#
#       orchestration
#
#
# Therefore:
#
#
#       FAILURE OBSERVED
#           !=
#       FAILURE LOCATION KNOWN
#
#
# Do not attach failure to a broader domain object than the evidence supports.
#
#
# ============================================================================
# FUTURE QUESTION — RETRYABILITY
# ============================================================================
#
# Some failures may justify retrying the same service.
#
#
# Others may not.
#
#
# Examples:
#
#
#       transient timeout
#           -> perhaps retry
#
#
#       provider throttling
#           -> perhaps retry after delay
#
#
#       malformed request
#           -> probably do not retry unchanged
#
#
#       explicit policy denial
#           -> do not retry as an availability problem
#
#
#       authentication failure
#           -> retrying repeatedly may make things worse
#
#
# SEIR-II may therefore need explicit retryability semantics.
#
#
# ============================================================================
# RETRY != FALLBACK
# ============================================================================
#
# Preserve this distinction.
#
#
#       RETRY
#           =
#       ANOTHER ATTEMPT USING THE SAME SERVICE
#
#
#       FALLBACK
#           =
#       CONSIDER A DIFFERENT SERVICE THROUGH
#       ANOTHER ROUTING CYCLE
#
#
# Example:
#
#
#       Service A
#           |
#           X timeout
#           |
#           +--> retry A
#           |
#           X timeout
#           |
#           +--> fallback
#                   |
#                   v
#               evaluate B, C
#
#
# Do not hide retry inside FallbackEvaluator.
#
#
# ============================================================================
# FUTURE QUESTION — RETRY BUDGET
# ============================================================================
#
# If retry exists, define limits.
#
#
# Otherwise:
#
#
#       while True:
#           invoke(service)
#
#
# eventually becomes:
#
#
#       while money:
#           invoke(service)
#
#
# and the cloud provider sends a very nice holiday card.
#
#
# Future retry policy may need:
#
#
#       maximum retries per service
#
#       maximum retries per request
#
#       maximum elapsed retry time
#
#       maximum retry cost
#
#       maximum retry token consumption
#
#
# ============================================================================
# RETRY BUDGET != FALLBACK BUDGET
# ============================================================================
#
# A recovery sequence might become:
#
#
#       attempt A
#
#       retry A
#
#       retry A
#
#       fallback to B
#
#       retry B
#
#       fallback to C
#
#
# Therefore:
#
#
#       NUMBER OF RETRIES
#           !=
#       NUMBER OF FALLBACKS
#
#
# Future recovery policy may need to govern them separately.
#
#
# ============================================================================
# FUTURE QUESTION — FALLBACK BUDGET
# ============================================================================
#
# SEIR-II may need to limit:
#
#
#       number of alternative services attempted
#
#       number of routing cycles
#
#       total recovery latency
#
#       total token consumption
#
#       total monetary cost
#
#
# Without such limits, a large service registry could turn one user request
# into a very expensive tour of the AI industry.
#
#
# ============================================================================
# RECOVERY BUDGET != ROUTING AUTHORIZATION
# ============================================================================
#
# Even if a recovery budget permits another attempt:
#
#
#       POLICY
#
#       CAPABILITY
#
#       SERVICE AVAILABILITY
#
#       NETWORK AVAILABILITY
#
#
# must still establish current viability.
#
#
#       BUDGET AVAILABLE
#           !=
#       ROUTE AUTHORIZED
#
#
# ============================================================================
# FUTURE QUESTION — BACKOFF
# ============================================================================
#
# Retry behavior may eventually require:
#
#
#       fixed delay
#
#       exponential backoff
#
#       jitter
#
#       provider retry-after guidance
#
#
# These are timing/execution concerns.
#
#
# Do not place:
#
#
#       sleep(...)
#
#
# inside FallbackEvaluator.
#
#
# ============================================================================
# FUTURE QUESTION — CIRCUIT BREAKERS
# ============================================================================
#
# If repeated attempts against a service fail, SEIR-II may need a circuit
# breaker.
#
#
# Conceptually:
#
#
#       CLOSED
#           -> normal traffic
#
#       OPEN
#           -> temporarily reject new attempts
#
#       HALF-OPEN
#           -> cautiously test recovery
#
#
# This is service-resilience behavior.
#
#
# It should not automatically become fallback behavior merely because
# fallback consumes service state.
#
#
# ============================================================================
# CIRCUIT BREAKER STATE != POLICY
# ============================================================================
#
# An open circuit may make a service operationally unavailable.
#
#
# It does not make that service:
#
#
#       unauthorized
#
#
# Likewise, closing a circuit does not make a service:
#
#
#       authorized
#
#
# Preserve:
#
#
#       HEALTH != POLICY
#
#
# ============================================================================
# FUTURE QUESTION — HEALTH DECAY
# ============================================================================
#
# Service availability may eventually become more sophisticated than:
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
# SEIR-II may use observations over time to influence service health.
#
#
# But remember:
#
#
#       HEALTH SIGNAL
#           !=
#       ROUTING AUTHORIZATION
#
#
# ============================================================================
# FUTURE QUESTION — FAILURE DOMAINS
# ============================================================================
#
# Multi-model systems create an important trap:
#
#
#       DIFFERENT MODEL
#           !=
#       INDEPENDENT FAILURE DOMAIN
#
#
# Example:
#
#
#       Model A
#           -> AWS us-east-1
#
#       Model B
#           -> AWS us-east-1
#
#       Model C
#           -> Azure Japan
#
#
# If AWS us-east-1 has a regional outage:
#
#
#       A -> B
#
#
# may provide very little resilience.
#
#
# ============================================================================
# MODEL DIVERSITY != INFRASTRUCTURE DIVERSITY
# ============================================================================
#
# Different model names do not guarantee independent:
#
#
#       regions
#
#       providers
#
#       clusters
#
#       network paths
#
#       identity systems
#
#       control planes
#
#
# SEIR-II recovery may eventually need explicit failure-domain awareness.
#
#
# ============================================================================
# SAME MODEL MAY HAVE USEFUL REDUNDANCY
# ============================================================================
#
# Conversely:
#
#
#       SAME LOGICAL MODEL
#
#
# may eventually exist through:
#
#
#       Service A -> AWS
#
#       Service B -> Azure
#
#       Service C -> on-premises
#
#
# or through multiple independent regional deployments.
#
#
# Therefore:
#
#
#       SAME MODEL
#           !=
#       SAME FAILURE DOMAIN
#
#
# ============================================================================
# REMEMBER THE MODEL / SERVICE / DEPLOYMENT DISTINCTION
# ============================================================================
#
# SEIR-I deliberately separated:
#
#
#       AIModel
#           =
#       WHAT THE MODEL IS
#
#
#       AIService
#           =
#       HOW THE MODEL IS EXPOSED TO AGENT 11
#
#
# Future runtime/deployment contracts may describe:
#
#
#       WHERE AND HOW THE SERVICE IS ACTUALLY DEPLOYED
#
#
# Recovery architecture will depend heavily on preserving those distinctions.
#
#
#       MODEL != SERVICE != DEPLOYMENT
#
#
# ============================================================================
# FUTURE QUESTION — FAILOVER
# ============================================================================
#
# SEIR-II may need a clearer distinction between:
#
#
#       FALLBACK
#
#
# and:
#
#
#       FAILOVER
#
#
# One useful conceptual boundary may become:
#
#
#       FALLBACK
#           =
#       ROUTE TO A DIFFERENT SUITABLE SERVICE
#
#
#       FAILOVER
#           =
#       MOVE TO AN ALTERNATE OPERATIONAL DEPLOYMENT
#       OF THE SAME OR EQUIVALENT SERVICE CAPABILITY
#
#
# Do not lock this definition merely because it appears in these notes.
#
#
# Let the actual deployment architecture determine the final contract.
#
#
# ============================================================================
# FUTURE QUESTION — REGIONAL FAILOVER
# ============================================================================
#
# If a company model exists in:
#
#
#       Azure East US
#
#       Azure Japan East
#
#
# or:
#
#       AWS us-east-1
#
#       AWS ap-northeast-1
#
#
# regional failover may occur below, within, or above Agent 11 depending upon
# the runtime architecture.
#
#
# Do not duplicate cloud-native failover unnecessarily.
#
#
# ============================================================================
# AGENT 11 != CLOUD LOAD BALANCER
# ============================================================================
#
# If the infrastructure layer can transparently maintain service availability
# across deployments, Agent 11 may not need to understand every deployment
# transition.
#
#
# Conversely, if deployment location affects:
#
#
#       policy
#
#       residency
#
#       jurisdiction
#
#       cost
#
#       capability
#
#
# Agent 11 may need explicit awareness.
#
#
# Determine this from requirements, not fashion.
#
#
# ============================================================================
# FUTURE QUESTION — DISASTER RECOVERY
# ============================================================================
#
# Recovery from:
#
#
#       one unusable invocation
#
#
# is not the same problem as recovery from:
#
#
#       regional cloud outage
#
#       provider outage
#
#       data-center loss
#
#       identity-plane outage
#
#       control-plane failure
#
#       network partition
#
#
# Future disaster-recovery architecture may operate at a much broader layer.
#
#
#       FALLBACK != DISASTER RECOVERY
#
#
# ============================================================================
# FUTURE QUESTION — CORRELATED FAILURES
# ============================================================================
#
# If multiple services depend upon the same:
#
#
#       provider
#
#       region
#
#       identity system
#
#       DNS service
#
#       network path
#
#       Kubernetes cluster
#
#       gateway
#
#
# then failures may be correlated.
#
#
# A sophisticated recovery system should avoid repeatedly selecting
# alternatives that share the suspected failure domain.
#
#
# But:
#
#
#       SUSPECTED CORRELATION
#           !=
#       POLICY AUTHORIZATION
#
#
# Failure-domain reasoning still occurs only among permitted alternatives.
#
#
# ============================================================================
# FUTURE QUESTION — MULTI-CLOUD
# ============================================================================
#
# Agent 11 may eventually route among deployments across:
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
#       other clouds
#
#       company data centers
#
#
# Do not encode:
#
#
#       CLOUD PROVIDER
#
#
# into:
#
#
#       AIRoute
#
#
# unless the routing-domain contract genuinely changes.
#
#
# ============================================================================
# COMPANY_CLOUD_LLM REMAINS PROVIDER-NEUTRAL
# ============================================================================
#
# Preserve:
#
#
#       COMPANY_CLOUD_LLM
#
#
# as a routing domain.
#
#
# A company-cloud service might eventually run on:
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
#
# or several simultaneously.
#
#
#       ROUTING DOMAIN != CLOUD PROVIDER
#
#
# ============================================================================
# FUTURE QUESTION — MULTIPLE FOUNDATION MODELS
# ============================================================================
#
# SEIR-I intentionally deferred the harder question:
#
#
#       "WHAT IF MULTIPLE FOUNDATION MODELS
#        ARE ALL CAPABLE AND VIABLE?"
#
#
# SEIR-II may have:
#
#
#       Claude
#
#       Gemini
#
#       proprietary model A
#
#       proprietary model B
#
#       future models not yet known
#
#
# Recovery does not make this selection problem disappear.
#
#
# ============================================================================
# FALLBACK MUST NOT INVENT A SECOND MODEL SELECTOR
# ============================================================================
#
# If SEIR-II introduces sophisticated model selection, do not create:
#
#
#       normal_model_selector()
#
#
# and:
#
#
#       fallback_model_selector()
#
#
# with unrelated semantics unless evidence proves that recovery genuinely
# requires a distinct optimization objective.
#
#
# Prefer:
#
#
#       FRESH CONSTRAINT EVALUATION
#               |
#               v
#       NORMAL MODEL / ROUTE SELECTION
#
#
# ============================================================================
# ELIGIBILITY != RANKING
# ============================================================================
#
# SEIR-I ModelRouter asks:
#
#
#       "CAN THIS SPECIFIC MODEL/SERVICE PAIR
#        SATISFY THIS EXPLICIT REQUIREMENT?"
#
#
# SEIR-II may additionally need:
#
#
#       "WHICH OF THE ELIGIBLE MODELS
#        IS BEST FOR THIS REQUEST?"
#
#
# Those remain separate questions during fallback.
#
#
#       CAPABILITY MATCHING != MODEL SELECTION
#
#
# ============================================================================
# "BEST" IS MULTIDIMENSIONAL
# ============================================================================
#
# Future model selection may consider:
#
#
#       reasoning quality
#
#       workload specialization
#
#       context-window fit
#
#       latency
#
#       cost
#
#       capacity
#
#       organizational preference
#
#       historical performance
#
#       deployment constraints
#
#       service-level objectives
#
#
# But hard constraints still come first.
#
#
# ============================================================================
# HARD CONSTRAINTS BEFORE OPTIMIZATION
# ============================================================================
#
# Future recovery must preserve:
#
#
#       POLICY PERMITTED
#
#       SERVICE CAPABLE
#
#       SERVICE AVAILABLE
#
#       PATH AVAILABLE
#
#
# before optimization.
#
#
# Only viable alternatives may participate in preference/ranking.
#
#
#       FILTER BY CONSTRAINTS FIRST.
#
#       OPTIMIZE SECOND.
#
#
# ============================================================================
# POLICY NEVER BECOMES A SCORE
# ============================================================================
#
# Future-you may be tempted to create:
#
#
#       score =
#           quality_weight
#           + latency_weight
#           + cost_weight
#           + policy_weight
#
#
# Do not.
#
#
# Policy is not:
#
#
#       0.7 preferred
#
#
# Policy is:
#
#
#       permitted
#
# or:
#
#       not permitted
#
# or another explicit policy state.
#
#
#       POLICY NEVER BECOMES A SCORE
#
#
# ============================================================================
# SECURITY DOES NOT BECOME OPTIONAL DURING INCIDENTS
# ============================================================================
#
# Operational incidents create pressure.
#
#
# Pressure produces sentences such as:
#
#
#       "Just send it somewhere that works."
#
#
# Agent 11 exists partly to prevent that sentence from becoming architecture.
#
#
#       INCIDENT != POLICY SUSPENSION
#
#
# ============================================================================
# BREAK-GLASS ACCESS IS NOT FALLBACK
# ============================================================================
#
# If SEIR-II eventually introduces formally authorized emergency or
# break-glass procedures:
#
#
#       BREAK-GLASS AUTHORIZATION
#
#
# must be modeled as an explicit security/governance concept.
#
#
# Never implement it as:
#
#
#       if nothing_worked:
#           ignore_policy()
#
#
# ============================================================================
# FALLBACK MAY REDUCE AVAILABILITY
# ============================================================================
#
# Preserve the flagship SEIR-I rule:
#
#
#       FALLBACK MAY REDUCE AVAILABILITY.
#
#       FALLBACK MUST NEVER REDUCE SECURITY POLICY.
#
#
# If no compliant recovery path exists:
#
#
#       STOP.
#
#
# ============================================================================
# FUTURE QUESTION — POLICY CHANGES DURING EXECUTION
# ============================================================================
#
# Long-running workflows may experience policy changes while processing.
#
#
# Example:
#
#
#       T0:
#           Service B allowed
#
#
#       T1:
#           Service A selected
#
#
#       T2:
#           organization policy changes
#
#
#       T3:
#           Service A attempt fails
#
#
#       T4:
#           fallback evaluates Service B
#
#
# The policy used at T0 must not automatically authorize B at T4.
#
#
# ============================================================================
# AUTHORIZATION HAS A TIME DIMENSION
# ============================================================================
#
# This was already implicit in SEIR-I:
#
#
#       PREVIOUSLY AUTHORIZED
#           !=
#       CURRENTLY AUTHORIZED
#
#
# SEIR-II may eventually need explicit:
#
#
#       policy version
#
#       evaluation timestamp
#
#       provenance
#
#
# if audit requirements demand them.
#
#
# Do not add those fields here merely because they might someday be useful.
#
#
# ============================================================================
# FUTURE QUESTION — DATA RESIDENCY
# ============================================================================
#
# Multi-cloud recovery may make residency especially important.
#
#
# A service may be:
#
#
#       capable
#
#       healthy
#
#       reachable
#
#
# while its deployment location makes it impermissible for a particular
# request.
#
#
# Residency therefore remains part of policy/deployment viability.
#
#
# It must not be bypassed during fallback.
#
#
# ============================================================================
# REGION AVAILABLE != REGION PERMITTED
# ============================================================================
#
# A healthy deployment in another region does not automatically create a
# compliant failover destination.
#
#
#       AVAILABLE REGION
#           !=
#       AUTHORIZED REGION
#
#
# ============================================================================
# FUTURE QUESTION — DYNAMIC SERVICE DISCOVERY
# ============================================================================
#
# SEIR-I fallback considers the original candidate universe.
#
#
# Future runtime registries may make services appear or disappear dynamically.
#
#
# SEIR-II must decide whether fallback:
#
#
#       re-evaluates only previously discovered services
#
#
# or:
#
#
#       performs fresh service discovery before routing
#
#
# This is currently unresolved.
#
#
# ============================================================================
# DISCOVERY != TRUST
# ============================================================================
#
# If dynamic discovery is introduced:
#
#
#       DISCOVERED SERVICE
#           !=
#       TRUSTED SERVICE
#
#
# and:
#
#
#       DISCOVERED SERVICE
#           !=
#       AUTHORIZED SERVICE
#
#
# Discovery expands awareness.
#
# It does not expand authority.
#
#
# ============================================================================
# FUTURE QUESTION — REGISTRY CHANGES
# ============================================================================
#
# Suppose:
#
#
#       Service B
#
#
# existed during initial routing but has been removed from the runtime
# registry before fallback.
#
#
# Fresh routing should use current runtime truth.
#
#
# Do not resurrect B merely because it exists in historical candidates.
#
#
# ============================================================================
# HISTORICAL CANDIDATE != CURRENT DEPLOYMENT
# ============================================================================
#
# This is another expression of:
#
#
#       HISTORICAL EVIDENCE != CURRENT EVIDENCE
#
#
# The candidate record proves that B was considered.
#
#
# It does not prove that B still exists.
#
#
# ============================================================================
# FUTURE QUESTION — NETWORK RECOVERY
# ============================================================================
#
# SEIR-II network integration may include:
#
#
#       Internet
#
#       VPN
#
#       PrivateLink
#
#       SD-WAN
#
#       BGP
#
#       Street Access
#
#
# A path may disappear or recover between routing cycles.
#
#
# Fresh routing must consume current network evidence.
#
#
# ============================================================================
# BGP DOES NOT AUTHORIZE AI
# ============================================================================
#
# Preserve:
#
#
#       BGP
#           =
#       HOW PACKETS MAY REACH AN APPROVED ENDPOINT
#
#
# Agent 11 policy answers:
#
#
#       WHETHER THE REQUEST MAY BE SENT THERE
#
#
# Therefore:
#
#
#       BGP REACHABLE != AI AUTHORIZED
#
#
# ============================================================================
# SD-WAN DOES NOT AUTHORIZE AI
# ============================================================================
#
# Likewise:
#
#
#       SD-WAN PATH AVAILABLE
#           !=
#       DATA PERMITTED ON DESTINATION
#
#
# ============================================================================
# POLICY DOES NOT CREATE NETWORK PATHS
# ============================================================================
#
# The reverse remains true:
#
#
#       AUTHORIZED
#           !=
#       REACHABLE
#
#
# Recovery needs both.
#
#
# ============================================================================
# FUTURE QUESTION — HEDGED REQUESTS
# ============================================================================
#
# SEIR-II may eventually consider sending requests to multiple services
# concurrently and accepting the first valid result.
#
#
# This is sometimes called:
#
#
#       hedging
#
#
# or:
#
#
#       speculative execution
#
#
# That is NOT ordinary fallback.
#
#
# ============================================================================
# PARALLEL INVOCATION CHANGES THE SECURITY MODEL
# ============================================================================
#
# If a request is sent simultaneously to:
#
#
#       Service A
#
#       Service B
#
#       Service C
#
#
# then data has been disclosed to all three destinations.
#
#
# Even if only one response is used.
#
#
# Therefore:
#
#
#       FIRST RESPONSE WINS
#           !=
#       ONLY ONE SERVICE RECEIVED DATA
#
#
# This matters greatly for policy, privacy, residency, and cost.
#
#
# ============================================================================
# PARALLEL RECOVERY != SEQUENTIAL FALLBACK
# ============================================================================
#
# SEIR-I assumes a sequential recovery model.
#
#
# If SEIR-II introduces parallel recovery:
#
#
#       concurrency
#
#       cancellation
#
#       duplicate cost
#
#       duplicate disclosure
#
#       telemetry
#
#       output reconciliation
#
#
# all require explicit design.
#
#
# Do not hide this inside FallbackEvaluator.
#
#
# ============================================================================
# FUTURE QUESTION — STREAMING
# ============================================================================
#
# Streaming creates another difficult boundary.
#
#
# Suppose:
#
#
#       Service A emits 500 tokens
#
#
# and then:
#
#
#       connection fails
#
#
# Should Agent 11:
#
#
#       retry A?
#
#       fallback to B?
#
#       discard the partial response?
#
#       continue from the partial response?
#
#       expose the partial response?
#
#
# Those are not simple fallback questions.
#
#
# ============================================================================
# PARTIAL OUTPUT != SAFE CONTINUATION POINT
# ============================================================================
#
# A second model may not be able to safely or coherently continue another
# model's partial output.
#
#
# Future streaming recovery requires explicit semantics.
#
#
# ============================================================================
# FUTURE QUESTION — STRUCTURED OUTPUT
# ============================================================================
#
# A model may return:
#
#
#       syntactically invalid JSON
#
#
# or:
#
#
#       structurally valid but semantically invalid output
#
#
# Whether that triggers:
#
#
#       repair
#
#       retry
#
#       fallback
#
#       request failure
#
#
# belongs to future execution/recovery policy.
#
#
# ============================================================================
# OUTPUT FAILURE != ROUTE FAILURE
# ============================================================================
#
# If a service successfully returns output that later fails validation:
#
#
#       NETWORK MAY HAVE WORKED
#
#       SERVICE MAY HAVE WORKED
#
#       MODEL MAY HAVE RESPONDED
#
#
# The unusable result may exist at a later validation boundary.
#
#
# Do not automatically label the route itself as failed.
#
#
# ============================================================================
# FUTURE QUESTION — OUTPUT POLICY
# ============================================================================
#
# An AI response may be generated successfully and then rejected by:
#
#
#       output policy
#
#       prohibited-data inspection
#
#       schema validation
#
#       downstream safety controls
#
#
# SEIR-II must decide which recovery actions are appropriate.
#
#
# ============================================================================
# SUCCESSFUL INFERENCE != USABLE RESULT
# ============================================================================
#
# Preserve:
#
#
#       MODEL RETURNED OUTPUT
#           !=
#       WORKFLOW MAY USE OUTPUT
#
#
# and:
#
#
#       AIResponse.SUCCESS
#           !=
#       FINAL USER OUTCOME
#
#
# ============================================================================
# FUTURE QUESTION — MCP FAILURE
# ============================================================================
#
# MCP introduces a separate recovery domain.
#
#
# A model may reason successfully and then:
#
#
#       MCP tool unavailable
#
#       MCP tool denied
#
#       MCP tool times out
#
#
# That does not necessarily justify selecting another AI model.
#
#
#       TOOL FAILURE
#           !=
#       MODEL FAILURE
#
#
# ============================================================================
# MCP FALLBACK != AI FALLBACK
# ============================================================================
#
# If tool redundancy eventually exists:
#
#
#       tool A unavailable
#
#       tool B equivalent
#
#
# that may justify a separate MCP/tool-routing recovery mechanism.
#
#
# Do not put it in routing/fallback.py merely because both use the English
# word "fallback."
#
#
# ============================================================================
# AI REASONING != TOOL EXECUTION
# ============================================================================
#
# Preserve this boundary during recovery.
#
#
# A reasoning failure does not automatically authorize:
#
#
#       tool execution
#
#
# and a tool failure does not automatically justify:
#
#
#       changing the reasoning route
#
#
# ============================================================================
# FUTURE QUESTION — MULTI-AGENT WORKFLOWS
# ============================================================================
#
# If Agent 11 eventually coordinates multiple reasoning agents:
#
#
#       planner
#
#       analyst
#
#       critic
#
#       executor
#
#
# failure may occur at one agent stage without invalidating the entire
# workflow.
#
#
# Recovery may need to understand workflow boundaries.
#
#
# ============================================================================
# AGENT HANDOFF != SECURITY RESET
# ============================================================================
#
# If recovery transfers work to another agent:
#
#
#       classification persists
#
#       policy persists
#
#       user restrictions persist
#
#       prohibited-data findings persist as appropriate
#
#
#       AGENT HANDOFF != NEW TRUST DOMAIN
#
#
# ============================================================================
# FUTURE QUESTION — DURABLE WORKFLOWS
# ============================================================================
#
# If Agent 11 eventually runs long-lived workflows, recovery state may need
# durable persistence.
#
#
# A process restart should not necessarily forget:
#
#
#       which services were attempted
#
#       which routing decisions occurred
#
#       which outputs were received
#
#       which approvals were granted
#
#
# But durable workflow state is not the responsibility of FallbackEvaluator.
#
#
# ============================================================================
# PROCESS MEMORY != DURABLE RECOVERY STATE
# ============================================================================
#
# An in-memory:
#
#
#       set[str]
#
#
# disappears when the process disappears.
#
#
# SEIR-II may eventually require a durable execution engine or persistence
# layer.
#
#
# Do not solve persistence by turning this evaluator into a database client.
#
#
# ============================================================================
# FUTURE QUESTION — IDEMPOTENCY
# ============================================================================
#
# Retry and recovery become particularly dangerous when downstream operations
# have side effects.
#
#
# If an AI invocation indirectly causes:
#
#
#       database mutation
#
#       ticket creation
#
#       message sending
#
#       cloud-resource changes
#
#       financial operations
#
#
# retry semantics require careful idempotency controls.
#
#
# ============================================================================
# REASONING RETRY != ACTION RETRY
# ============================================================================
#
# Generating reasoning again may be relatively safe.
#
#
# Re-executing an action may not be.
#
#
#       AI REASONING
#           !=
#       SIDE-EFFECTING EXECUTION
#
#
# ============================================================================
# RECOVERY MUST NOT EXPAND EXECUTION AUTHORITY
# ============================================================================
#
# If a workflow fails:
#
#
#       failure does not create new permissions
#
#
# for:
#
#
#       MCP tools
#
#       APIs
#
#       infrastructure changes
#
#       databases
#
#       external systems
#
#
# ============================================================================
# FUTURE QUESTION — HUMAN REVIEW
# ============================================================================
#
# Some failures may eventually require:
#
#
#       human approval
#
#       human route selection
#
#       manual override
#
#       incident escalation
#
#
# If introduced, these must have explicit authorization semantics.
#
#
# ============================================================================
# HUMAN OVERRIDE != UNBOUNDED AUTHORITY
# ============================================================================
#
# A human operator should not automatically be able to bypass:
#
#
#       organizational policy
#
#       legal restrictions
#
#       residency requirements
#
#
# merely because automated recovery failed.
#
#
# Human review is another control boundary, not absence of controls.
#
#
# ============================================================================
# FUTURE QUESTION — EXPLAINABILITY
# ============================================================================
#
# SEIR-II operators may need to answer:
#
#
#       Why was fallback attempted?
#
#       Why was retry attempted instead?
#
#       Why was Service B excluded?
#
#       Why was Service C selected?
#
#       Why did recovery stop?
#
#       Why did policy prevent a route?
#
#
# Recovery decisions should remain explainable.
#
#
# ============================================================================
# EXPLAINABILITY != RAW SECRET LOGGING
# ============================================================================
#
# Explain the decision without copying:
#
#
#       credentials
#
#       authentication tokens
#
#       private keys
#
#       protected payloads
#
#
# into telemetry.
#
#
# ============================================================================
# FUTURE QUESTION — TELEMETRY
# ============================================================================
#
# Future recovery telemetry may need events such as:
#
#
#       invocation started
#
#       invocation ended
#
#       retry requested
#
#       fallback permitted
#
#       fallback unavailable
#
#       routing reevaluation started
#
#       alternative selected
#
#       recovery exhausted
#
#
# Exact event contracts should be designed with telemetry requirements.
#
#
# ============================================================================
# TELEMETRY != DOMAIN STATE
# ============================================================================
#
# Do not add telemetry-only fields to fallback domain behavior simply because
# dashboards want them.
#
#
# Emit telemetry from the appropriate orchestration boundary.
#
#
# ============================================================================
# FUTURE QUESTION — AUDIT
# ============================================================================
#
# Audit may require reconstruction of:
#
#
#       what was known
#
#       what was permitted
#
#       what was selected
#
#       what was attempted
#
#       what failed
#
#       what was reevaluated
#
#       what happened next
#
#
# This strengthens the SEIR-I decision not to mutate historical candidate
# records.
#
#
# ============================================================================
# AUDITABILITY REWARDS IMMUTABLE HISTORY
# ============================================================================
#
# Conceptually:
#
#
#       Routing Cycle 1
#           -> Decision 1
#
#       Invocation Attempt 1
#           -> Outcome 1
#
#       Routing Cycle 2
#           -> Decision 2
#
#       Invocation Attempt 2
#           -> Outcome 2
#
#
# is much easier to audit than:
#
#
#       one mutable object
#       repeatedly rewritten
#       until it describes the final outcome
#
#
# ============================================================================
# FUTURE QUESTION — CORRELATION
# ============================================================================
#
# Distributed recovery will eventually need correlation among:
#
#
#       request
#
#       routing cycle
#
#       routing decision
#
#       invocation attempt
#
#       model response
#
#       fallback event
#
#       MCP activity
#
#       downstream execution
#
#
# Do not solve correlation by making every model own every identifier.
#
#
# ============================================================================
# FUTURE QUESTION — OBSERVABILITY FEEDBACK
# ============================================================================
#
# Historical telemetry may eventually influence future model/service
# selection.
#
#
# Example:
#
#
#       Service B has experienced elevated latency
#       during the last ten minutes.
#
#
# That may become useful routing evidence.
#
#
# But:
#
#
#       TELEMETRY-DERIVED PREFERENCE
#           !=
#       POLICY AUTHORIZATION
#
#
# ============================================================================
# LEARNED ROUTING MUST NOT BYPASS POLICY
# ============================================================================
#
# SEIR-II may eventually experiment with:
#
#
#       learned selectors
#
#       adaptive routing
#
#       historical-performance ranking
#
#
# If so:
#
#
#       learned system
#
#
# must operate only among candidates that satisfy hard constraints.
#
#
# Never train a model to "balance" policy against quality.
#
#
# ============================================================================
# AI MUST NOT NEGOTIATE ITS OWN SECURITY BOUNDARY
# ============================================================================
#
# If an AI-based selector is introduced:
#
#
#       AI recommendation
#           !=
#       authorization
#
#
# Deterministic policy gates must remain authoritative.
#
#
# ============================================================================
# FUTURE QUESTION — MODEL DRIFT
# ============================================================================
#
# A model/service that historically performed well may change because of:
#
#
#       model upgrade
#
#       model replacement
#
#       provider behavior changes
#
#       fine-tuning changes
#
#       deployment changes
#
#
# Therefore historical success does not permanently establish future
# suitability.
#
#
# ============================================================================
# HISTORICAL QUALITY != CURRENT QUALITY
# ============================================================================
#
# This mirrors the existing fallback principle:
#
#
#       HISTORICAL VIABILITY != CURRENT VIABILITY
#
#
# Future model-selection telemetry must account for version and deployment
# drift.
#
#
# ============================================================================
# FUTURE QUESTION — CANARY AND A/B DEPLOYMENTS
# ============================================================================
#
# SEIR-II may use:
#
#
#       canary models
#
#       A/B deployments
#
#       shadow deployments
#
#
# Recovery must not accidentally route protected production traffic into an
# experimental deployment merely because it exists.
#
#
#       DEPLOYED != APPROVED FOR THIS WORKLOAD
#
#
# ============================================================================
# FUTURE QUESTION — CAPACITY AND QUOTAS
# ============================================================================
#
# A service may be:
#
#
#       healthy
#
#       reachable
#
#       authorized
#
#       capable
#
#
# yet unable to accept another request because of:
#
#
#       quota exhaustion
#
#       concurrency limits
#
#       GPU saturation
#
#       provider capacity
#
#
# SEIR-II may need richer operational viability evidence.
#
#
# ============================================================================
# CAPACITY != CAPABILITY
# ============================================================================
#
# Preserve:
#
#
#       MODEL CAN DO THE WORK
#           !=
#       SERVICE CAN ACCEPT THE WORK NOW
#
#
# ============================================================================
# FUTURE QUESTION — COST
# ============================================================================
#
# Recovery can multiply cost.
#
#
# A single logical request might eventually consume:
#
#
#       initial invocation
#
#       retry
#
#       fallback invocation
#
#       another retry
#
#
# SEIR-II may need cost-aware recovery budgets.
#
#
# ============================================================================
# CHEAPER != PERMITTED
# ============================================================================
#
# Cost remains an optimization dimension.
#
#
# It never overrides policy.
#
#
#       CHEAPER != PERMITTED
#
#
# ============================================================================
# FUTURE QUESTION — LATENCY
# ============================================================================
#
# Recovery also consumes time.
#
#
# A future request may have:
#
#
#       latency SLO
#
#       deadline
#
#       user-facing timeout
#
#
# Recovery may need to stop when useful completion is no longer possible.
#
#
# ============================================================================
# FASTER != PERMITTED
# ============================================================================
#
# As always:
#
#
#       FASTEST ROUTE
#
#
# must still be:
#
#
#       AUTHORIZED
#
#       CAPABLE
#
#       AVAILABLE
#
#       REACHABLE
#
#
# ============================================================================
# FUTURE QUESTION — RECOVERY OBJECTIVE
# ============================================================================
#
# Eventually SEIR-II may need to answer:
#
#
#       What is recovery optimizing?
#
#
# Possibilities include:
#
#
#       probability of success
#
#       latency
#
#       cost
#
#       model quality
#
#       failure-domain diversity
#
#       SLO compliance
#
#
# "Best fallback" is therefore contextual.
#
#
# ============================================================================
# BEST != UNIVERSALLY BEST
# ============================================================================
#
# The best recovery destination for:
#
#
#       interactive chat
#
#
# may differ from:
#
#
#       batch security analysis
#
#
# or:
#
#
#       long-running code reasoning
#
#
# Future selection should understand workload requirements rather than
# assuming one global model ordering.
#
#
# ============================================================================
# FUTURE QUESTION — RECOVERY POLICY
# ============================================================================
#
# If enough recovery dimensions emerge, SEIR-II may eventually justify a
# typed recovery-policy contract.
#
#
# It might someday describe concepts such as:
#
#
#       retry allowance
#
#       fallback allowance
#
#       attempt budget
#
#       time budget
#
#       cost budget
#
#       failure-domain requirements
#
#
# But:
#
#
#       DO NOT IMPLEMENT THAT OBJECT
#       FROM THIS COMMENT.
#
#
# Wait until requirements are concrete.
#
#
# ============================================================================
# POSSIBLE FUTURE CONTRACTS ARE NOT CURRENT CONTRACTS
# ============================================================================
#
# These notes mention possible concepts such as:
#
#
#       InvocationAttempt
#
#       RecoveryPolicy
#
#       richer model-selection decisions
#
#       deployment/failure-domain contracts
#
#
# Their names and shapes are intentionally NOT locked.
#
#
#       DOCUMENTED POSSIBILITY
#           !=
#       APPROVED DOMAIN MODEL
#
#
# ============================================================================
# FUTURE QUESTION — WHERE SHOULD RECOVERY COORDINATION LIVE?
# ============================================================================
#
# SEIR-I intentionally saves routing/orchestrator.py until the routing
# components are understood.
#
#
# Preserve that discipline in SEIR-II.
#
#
# Do not automatically put every recovery concern into:
#
#
#       RoutingOrchestrator
#
#
# merely because it coordinates routing.
#
#
# ============================================================================
# COORDINATION != OWNERSHIP
# ============================================================================
#
# A future routing orchestrator may coordinate:
#
#
#       candidate evaluation
#
#       route selection
#
#       fallback eligibility
#
#
# But collaborators should continue owning their domain behaviors.
#
#
#       ORCHESTRATOR
#           =
#       COORDINATES BEHAVIOR
#
#
# not:
#
#
#       ORCHESTRATOR
#           =
#       IMPLEMENTS EVERYTHING
#
#
# ============================================================================
# WATCH FOR THE GOD ORCHESTRATOR
# ============================================================================
#
# If routing/orchestrator.py eventually knows how to:
#
#
#       evaluate PII
#
#       interpret organization policy
#
#       rank Claude against Gemini
#
#       query AWS
#
#       query Azure
#
#       query GCP
#
#       inspect BGP
#
#       change SD-WAN paths
#
#       invoke models
#
#       execute MCP tools
#
#       perform retries
#
#       perform fallback
#
#       write telemetry
#
#       send incident notifications
#
#
# then the architecture has failed regardless of how impressive the class
# name sounds.
#
#
# ============================================================================
# FUTURE QUESTION — CANDIDATE EVALUATION
# ============================================================================
#
# SEIR-I deliberately leaves one routing responsibility visible:
#
#
#       POLICY -----------+
#                         |
#       CAPABILITY -------+
#                         |
#       SERVICE STATE ----+----> ??? ----> RoutingCandidate
#                         |
#       NETWORK STATE ----+
#
#
# Do not solve this gap inside fallback.py.
#
#
# By the time routing/orchestrator.py is designed, there should be enough
# evidence to determine whether:
#
#
#       candidate evaluation
#
#
# is small orchestration logic or deserves its own behavioral component.
#
#
# ============================================================================
# DO NOT HIDE THE GAP WITH A PRIVATE HELPER
# ============================================================================
#
# Future-you may be tempted to write:
#
#
#       def _build_candidate(...):
#           ...
#
#
# containing 150 lines of:
#
#
#       policy
#
#       capability
#
#       service
#
#       network
#
#       rejection precedence
#
#
# inside RoutingOrchestrator.
#
#
# If that happens:
#
#
#       candidate evaluation
#
#
# has probably earned its own architectural identity.
#
#
# ============================================================================
# FUTURE QUESTION — MULTIPLE REJECTION REASONS
# ============================================================================
#
# SEIR-I RoutingCandidate currently records:
#
#
#       rejection_reason
#
#
# as one reason.
#
#
# A candidate may eventually fail several viability dimensions at once:
#
#
#       POLICY_DENIED
#
#       SERVICE_UNAVAILABLE
#
#       NETWORK_UNAVAILABLE
#
#
# SEIR-II may need richer rejection provenance.
#
#
# Do not overload fallback.py to solve that.
#
#
# ============================================================================
# REJECTION PRECEDENCE IS NOT FALLBACK POLICY
# ============================================================================
#
# If candidate evaluation eventually chooses one primary rejection reason,
# the precedence belongs to candidate-evaluation semantics.
#
#
# Fallback merely consumes the resulting routing universe and permits fresh
# reevaluation when appropriate.
#
#
# ============================================================================
# FUTURE QUESTION — RECOVERY AFTER BLOCKED
# ============================================================================
#
# SEIR-I fallback begins after an attempted selected route becomes unusable.
#
#
# A:
#
#
#       BLOCKED
#
#
# routing decision means no route was selected because all evaluated
# candidates were policy denied.
#
#
# That is not an invocation failure.
#
#
# Therefore do not automatically treat:
#
#
#       BLOCKED
#
#
# as a fallback trigger.
#
#
# ============================================================================
# POLICY BLOCK != OPERATIONAL FAILURE
# ============================================================================
#
# If routing was blocked:
#
#
#       there was nothing to invoke.
#
#
# Repeated fallback cycles must not become:
#
#
#       keep asking until policy changes.
#
#
# ============================================================================
# FUTURE QUESTION — RECOVERY AFTER NO_VIABLE_ROUTE
# ============================================================================
#
# NO_VIABLE_ROUTE is more subtle.
#
#
# Future orchestration may eventually decide that some conditions can change:
#
#
#       network recovery
#
#       service recovery
#
#       capacity recovery
#
#
# and therefore a workflow might wait and reevaluate.
#
#
# But that would be:
#
#
#       ROUTING RE-EVALUATION / WORKFLOW RECOVERY
#
#
# not ordinary post-invocation fallback.
#
#
# Keep the distinction explicit.
#
#
# ============================================================================
# FUTURE QUESTION — RECOVERY AFTER NULL
# ============================================================================
#
# NULL means AI routing was intentionally unnecessary.
#
#
# There is therefore no failed AI route to fall back from.
#
#
#       NULL != FALLBACK TRIGGER
#
#
# ============================================================================
# ROUTING OUTCOME != RECOVERY TRIGGER
# ============================================================================
#
# Do not assume every non-SELECTED routing status means:
#
#
#       "try fallback"
#
#
# Recovery depends on what actually occurred.
#
#
# ============================================================================
# FUTURE QUESTION — CANCELLATION
# ============================================================================
#
# If a user or workflow cancels a request:
#
#
#       CANCELLED
#
#
# should not automatically trigger fallback.
#
#
# Recovery must respect intentional termination.
#
#
# ============================================================================
# USER CANCELLED != SERVICE FAILED
# ============================================================================
#
# Preserve causal accuracy.
#
#
# A cancellation is not evidence that:
#
#
#       model failed
#
#       service failed
#
#       network failed
#
#
# ============================================================================
# FUTURE QUESTION — REQUEST LIFECYCLE
# ============================================================================
#
# SEIR-I intentionally leaves some lifecycle semantics unresolved:
#
#
#       Does BLOCKED produce FAILED?
#
#       Does NO_VIABLE_ROUTE remain recoverable?
#
#       When does fallback exhaustion produce FAILED?
#
#       Can a request wait for infrastructure recovery?
#
#
# Do not answer these questions accidentally inside fallback.py.
#
#
# ============================================================================
# RECOVERY OUTCOME != REQUEST STATUS
# ============================================================================
#
# Preserve:
#
#
#       FALLBACK EXHAUSTED
#           !=
#       AUTOMATICALLY FAILED
#
#
# until the broader lifecycle contract explicitly decides otherwise.
#
#
# ============================================================================
# FUTURE QUESTION — WORKFLOW DEADLINES
# ============================================================================
#
# A durable workflow might decide:
#
#
#       no route now
#
#       wait five minutes
#
#       evaluate again
#
#
# Another request might require:
#
#
#       fail immediately
#
#
# These are workflow semantics.
#
#
# FallbackEvaluator should not become a scheduler.
#
#
# ============================================================================
# FUTURE QUESTION — SECURITY EVENTS DURING RECOVERY
# ============================================================================
#
# Suppose prohibited data is discovered after an initial invocation but before
# fallback.
#
#
# Fresh routing must consume the current security state.
#
#
# Recovery must not rely solely on the classification/policy facts known at
# initial selection.
#
#
# ============================================================================
# NEW SECURITY EVIDENCE != IGNORABLE BECAUSE ROUTING ALREADY STARTED
# ============================================================================
#
# A long-running request may accumulate new information.
#
#
# If that information changes authorization:
#
#
#       CURRENT POLICY STATE WINS
#
#
# subject to the final SEIR-II policy model.
#
#
# ============================================================================
# FUTURE QUESTION — OUTPUT CLASSIFICATION
# ============================================================================
#
# Future Agent 11 may classify model output separately from request input.
#
#
# If fallback uses prior model output as context for another model:
#
#
#       OUTPUT MAY BECOME NEW INPUT
#
#
# That may require classification and policy evaluation of the derived
# context.
#
#
# ============================================================================
# FALLBACK CONTEXT != AUTOMATICALLY SAFE CONTEXT
# ============================================================================
#
# Do not assume:
#
#
#       "Agent 11 generated it"
#
#
# means:
#
#
#       "Agent 11 may send it anywhere."
#
#
#       AI-GENERATED != SAFE
#
#
# ============================================================================
# FUTURE QUESTION — CONTEXT ACCUMULATION
# ============================================================================
#
# Repeated attempts may accumulate:
#
#
#       prompts
#
#       partial outputs
#
#       tool results
#
#       error messages
#
#       intermediate reasoning artifacts
#
#
# Future recovery must decide what may be forwarded to another service.
#
#
# ============================================================================
# FALLBACK != COPY EVERYTHING TO THE NEXT MODEL
# ============================================================================
#
# A replacement service should receive only context that is:
#
#
#       required
#
#       permitted
#
#       appropriately classified
#
#
# Recovery must not become uncontrolled context replication.
#
#
# ============================================================================
# FUTURE QUESTION — PROVENANCE
# ============================================================================
#
# When one model's output becomes another model's input, provenance may matter.
#
#
# Future systems may need to know:
#
#
#       user supplied
#
#       application supplied
#
#       model generated
#
#       MCP supplied
#
#       organization metadata
#
#
# Again:
#
#
#       PROVENANCE != AUTHORIZATION
#
#
# but provenance may inform policy.
#
#
# ============================================================================
# FUTURE QUESTION — DATA MINIMIZATION
# ============================================================================
#
# Fallback may tempt the system to forward the entire previous execution
# context to the next service.
#
#
# Resist that default.
#
#
#       RECOVERY
#           SHOULD NOT
#       MAXIMIZE DATA DISCLOSURE
#
#
# ============================================================================
# FUTURE QUESTION — PRIVACY AND JURISDICTION
# ============================================================================
#
# A technically viable fallback may cross:
#
#
#       cloud provider
#
#       geographic region
#
#       legal jurisdiction
#
#       organizational boundary
#
#
# Those changes may affect authorization.
#
#
# Fresh policy evaluation is therefore essential.
#
#
# ============================================================================
# FUTURE QUESTION — MODEL VERSION
# ============================================================================
#
# If:
#
#
#       Service A -> Model X version 4
#
#       Service B -> Model X version 5
#
#
# are they equivalent fallback destinations?
#
#
# Maybe.
#
# Maybe not.
#
#
# Future capability/assurance contracts should answer that.
#
#
# Fallback should not infer equivalence from model names.
#
#
# ============================================================================
# FUTURE QUESTION — QUALITY FLOORS
# ============================================================================
#
# Recovery should not necessarily accept any model capable of producing an
# answer.
#
#
# Some workloads may eventually require:
#
#
#       minimum quality
#
#       minimum assurance
#
#       validated benchmark performance
#
#       certification
#
#
# If those become real requirements, represent them explicitly.
#
#
# ============================================================================
# CAPABLE != ACCEPTABLE QUALITY
# ============================================================================
#
# SEIR-I capability matching is intentionally binary.
#
#
# SEIR-II may need richer selection semantics.
#
#
# Do not retrofit quality scoring into FallbackEvaluator.
#
#
# ============================================================================
# FUTURE QUESTION — SERVICE EQUIVALENCE
# ============================================================================
#
# Two services may expose:
#
#
#       the same model
#
#
# but differ in:
#
#
#       configuration
#
#       guardrails
#
#       fine-tuning
#
#       context limits
#
#       regional deployment
#
#       logging policy
#
#       data retention
#
#
# Therefore:
#
#
#       SAME MODEL ID
#           !=
#       OPERATIONALLY EQUIVALENT SERVICE
#
#
# ============================================================================
# FUTURE QUESTION — PROVIDER RETENTION
# ============================================================================
#
# Different providers or deployments may have different:
#
#
#       data retention
#
#       training usage
#
#       logging
#
#       contractual
#
#       privacy
#
#       residency
#
# characteristics.
#
#
# These are policy/deployment concerns.
#
#
# Fallback must not ignore them.
#
#
# ============================================================================
# FUTURE QUESTION — CONTROL PLANE FAILURE
# ============================================================================
#
# What happens if:
#
#
#       model services are healthy
#
#
# but:
#
#
#       Agent 11 policy service is unavailable?
#
#
# The answer must not be:
#
#
#       "Skip policy so availability remains high."
#
#
# ============================================================================
# CONTROL PLANE FAILURE != PERMISSION
# ============================================================================
#
# Preserve:
#
#
#       CANNOT DETERMINE AUTHORIZATION
#           !=
#       AUTHORIZED
#
#
# This may require fail-closed behavior.
#
#
# ============================================================================
# FUTURE QUESTION — POLICY SERVICE REDUNDANCY
# ============================================================================
#
# SEIR-II may need resilience not only for inference services but also for:
#
#
#       policy
#
#       identity
#
#       classification
#
#       service registry
#
#       network state
#
#
# Recovery of Agent 11's control plane is a separate architectural problem.
#
#
# ============================================================================
# CONTROL-PLANE RECOVERY != MODEL FALLBACK
# ============================================================================
#
# If policy evaluation itself is unavailable, selecting another model does
# not solve the problem.
#
#
# ============================================================================
# FUTURE QUESTION — SECURITY DETECTOR FAILURE
# ============================================================================
#
# If prohibited-data detection is unavailable:
#
#
#       "No findings"
#
#
# must not be fabricated.
#
#
# The correct state may be:
#
#
#       detector unavailable
#
#
# or another explicit future uncertainty state.
#
#
# ============================================================================
# FAIL CLOSED WITHOUT FALSIFYING STATE
# ============================================================================
#
# Preserve this everywhere:
#
#
#       UNKNOWN != SAFE
#
#       UNKNOWN != DENIED
#
#       UNKNOWN != UNAVAILABLE
#
#
# Enforcement may fail closed while telemetry preserves what is actually
# known.
#
#
# ============================================================================
# FUTURE QUESTION — POLICY CACHE
# ============================================================================
#
# SEIR-II may eventually cache policy results for performance or resilience.
#
#
# If so, define:
#
#
#       validity
#
#       expiration
#
#       policy version
#
#       invalidation
#
#
# explicitly.
#
#
# Never interpret:
#
#
#       CACHED ALLOW
#
#
# as:
#
#
#       PERMANENT AUTHORIZATION
#
#
# ============================================================================
# FUTURE QUESTION — NETWORK CACHE
# ============================================================================
#
# Likewise, cached reachability may become stale.
#
#
#       PATH WAS AVAILABLE
#           !=
#       PATH IS AVAILABLE
#
#
# Freshness requirements may differ by evidence type.
#
#
# ============================================================================
# FUTURE QUESTION — SERVICE-HEALTH CACHE
# ============================================================================
#
# Service-health observations also age.
#
#
# Future candidate evaluation may need timestamps or freshness windows.
#
#
# Do not put them in fallback unless fallback itself truly owns them.
#
#
# ============================================================================
# EVIDENCE FRESHNESS MAY BECOME DOMAIN-SPECIFIC
# ============================================================================
#
# Future-you may discover:
#
#
#       policy authorization
#           valid for X
#
#       network state
#           valid for Y
#
#       service health
#           valid for Z
#
#
# There may be no universal:
#
#
#       fresh = True
#
#
# flag.
#
#
# ============================================================================
# FUTURE QUESTION — RECOVERY AND TRANSACTIONS
# ============================================================================
#
# If Agent 11 coordinates workflows that modify systems, recovery may need to
# understand:
#
#
#       commit
#
#       rollback
#
#       compensation
#
#       idempotency
#
#
# Those are workflow/execution concepts.
#
#
# Do not confuse them with inference fallback.
#
#
# ============================================================================
# FUTURE QUESTION — HUMAN-FACING ERROR SEMANTICS
# ============================================================================
#
# Operators and users may need different explanations.
#
#
# Example:
#
#
#       internal:
#           all compliant model services unavailable
#
#
#       user-facing:
#           AI service temporarily unavailable
#
#
# Error presentation belongs above FallbackEvaluator.
#
#
# ============================================================================
# INTERNAL EXPLANATION != DATA LEAK
# ============================================================================
#
# Do not expose:
#
#
#       internal service names
#
#       provider topology
#
#       security-policy details
#
#       network topology
#
#
# to callers who are not authorized to receive them.
#
#
# ============================================================================
# FUTURE QUESTION — RECOVERY SLOs
# ============================================================================
#
# SEIR-II may eventually define:
#
#
#       maximum recovery time
#
#       maximum recovery attempts
#
#       target availability
#
#       recovery success rate
#
#
# These may influence orchestration.
#
#
# They do not change security constraints.
#
#
# ============================================================================
# SLO != AUTHORIZATION
# ============================================================================
#
# Missing a latency or availability target does not authorize:
#
#
#       prohibited route
#
#
#       SLO PRESSURE != POLICY OVERRIDE
#
#
# ============================================================================
# FUTURE QUESTION — TESTING
# ============================================================================
#
# SEIR-II should test recovery under:
#
#
#       policy changes
#
#       service failures
#
#       network failures
#
#       provider failures
#
#       regional failures
#
#       model capability mismatches
#
#       quota exhaustion
#
#       timeouts
#
#       malformed responses
#
#       detector failures
#
#       control-plane failures
#
#
# Recovery architecture is only believable if failure is tested.
#
#
# ============================================================================
# TEST THE BAD PATH
# ============================================================================
#
# Happy-path testing proves very little about fallback.
#
#
# Explicitly test:
#
#
#       preferred service fails
#
#       alternative loses authorization
#
#       alternative loses reachability
#
#       previously rejected route recovers
#
#       all alternatives become blocked
#
#       all alternatives become operationally unavailable
#
#       recovery budget is exhausted
#
#
# ============================================================================
# TEST SECURITY UNDER FAILURE
# ============================================================================
#
# One of the most important future tests:
#
#
#       DOES THE SYSTEM BECOME LESS SECURE
#       WHEN SOMETHING BREAKS?
#
#
# The answer must be:
#
#
#       NO
#
#
# ============================================================================
# FAILURE SHOULD EXERCISE POLICY, NOT DISABLE IT
# ============================================================================
#
# Recovery tests should verify:
#
#
#       policy remains active
#
#       classification remains active
#
#       user restrictions remain active
#
#       execution authority remains scoped
#
#
# throughout failure scenarios.
#
#
# ============================================================================
# FUTURE QUESTION — CHAOS TESTING
# ============================================================================
#
# When Agent 11 becomes sufficiently mature, controlled failure injection may
# help validate:
#
#
#       service redundancy
#
#       routing behavior
#
#       network recovery
#
#       policy consistency
#
#       telemetry
#
#
# But chaos testing should test the architecture.
#
#
# It should not substitute for having one.
#
#
# ============================================================================
# FUTURE QUESTION — SCHEMA VERSIONING
# ============================================================================
#
# If recovery contracts become persisted or exchanged across services,
# schema evolution may eventually matter.
#
#
# Do not prematurely add:
#
#
#       schema_version
#
#
# to every SEIR-I object.
#
#
# Add explicit versioning when there is an actual compatibility boundary.
#
#
# ============================================================================
# FUTURE QUESTION — DISTRIBUTED TRUST
# ============================================================================
#
# In a distributed multi-cloud Agent 11, routing evidence may come from
# different systems.
#
#
# Future-you may need to ask:
#
#
#       Who produced this policy decision?
#
#       Who produced this health state?
#
#       Who produced this network state?
#
#       Is this evidence authentic?
#
#       Is it current?
#
#
# Those are trust/provenance concerns.
#
#
# ============================================================================
# VALID PAYLOAD != TRUSTED PAYLOAD
# ============================================================================
#
# Pydantic can establish:
#
#
#       STRUCTURAL VALIDITY
#
#
# It cannot establish:
#
#
#       SOURCE TRUST
#
#
# or:
#
#
#       EVIDENCE AUTHENTICITY
#
#
# Preserve that distinction as Agent 11 becomes distributed.
#
#
# ============================================================================
# FUTURE QUESTION — CONCURRENCY
# ============================================================================
#
# SEIR-I fallback assumes simple sequential execution.
#
#
# Distributed workflows may eventually have concurrent state changes.
#
#
# Example:
#
#
#       fallback evaluation begins
#
#       while policy changes
#
#       while service health changes
#
#       while request cancellation arrives
#
#
# This may require transactional or workflow-engine semantics.
#
#
# ============================================================================
# PYDANTIC VALIDATION != CONCURRENCY CONTROL
# ============================================================================
#
# Pydantic validates data.
#
#
# It does not provide:
#
#
#       locks
#
#       transactions
#
#       compare-and-swap
#
#       distributed consensus
#
#       workflow serialization
#
#
# Do not ask it to.
#
#
# ============================================================================
# FUTURE QUESTION — IMMUTABLE TRANSITIONS
# ============================================================================
#
# SEIR-II may eventually prefer creating new validated state snapshots rather
# than mutating existing aggregate state.
#
#
# This becomes especially useful for:
#
#
#       audit
#
#       concurrency
#
#       rollback
#
#       durable workflows
#
#
# That is broader than fallback.py.
#
#
# ============================================================================
# FUTURE QUESTION — RECOVERY AS A STATE MACHINE
# ============================================================================
#
# If recovery eventually contains:
#
#
#       retrying
#
#       waiting
#
#       rerouting
#
#       escalating
#
#       exhausted
#
#       cancelled
#
#
# it may earn an explicit state machine.
#
#
# Do not fake that state machine using:
#
#
#       five booleans
#
#
# if the domain becomes genuinely stateful.
#
#
# ============================================================================
# BUT DO NOT BUILD THE STATE MACHINE EARLY
# ============================================================================
#
# SEIR-I currently needs:
#
#
#       NONE
#
#       NEXT_VIABLE
#
#
# and:
#
#
#       can_attempt_fallback(...)
#
#
# That is enough.
#
#
# ============================================================================
# FUTURE QUESTION — WHO OWNS RECOVERY?
# ============================================================================
#
# Eventually the answer may span:
#
#
#       routing subsystem
#
#       AI orchestration
#
#       runtime infrastructure
#
#       workflow engine
#
#       network control plane
#
#
# That is acceptable.
#
#
# A distributed problem does not need to be forced into one class.
#
#
# ============================================================================
# RECOVERY IS A COLLABORATION
# ============================================================================
#
# Future architecture may resemble:
#
#
#       AI Orchestrator
#             |
#             +--> invocation
#             |
#             +--> detects unusable attempt
#                     |
#                     v
#              recovery coordination
#                     |
#              +------+------+
#              |             |
#            retry        fallback
#                            |
#                            v
#                   routing subsystem
#                            |
#                   fresh evaluation
#                            |
#                            v
#                        AIRouter
#
#
# Exact ownership remains intentionally open.
#
#
# ============================================================================
# FALLBACK.PY SHOULD REMAIN BORING
# ============================================================================
#
# This is a feature.
#
#
# If future fallback.py contains:
#
#
#       boto3
#
#       Azure SDK
#
#       Google Cloud SDK
#
#       OCI SDK
#
#       model invocation clients
#
#       Kubernetes clients
#
#       BGP configuration
#
#       MCP execution
#
#       database persistence
#
#       telemetry exporters
#
#
# stop.
#
#
# Something has crossed an architectural boundary.
#
#
# ============================================================================
# CHEWBACCA FUTURE REVIEW #1
# ============================================================================
#
# Future Engineer:
#
#       "The first model failed, so I sent the E9 data
#        to the external model."
#
# Chewbacca:
#
#       "Was the external model authorized?"
#
#
# Future Engineer:
#
#       "No, but it was available."
#
# Chewbacca:
#
#       "Then you did not implement fallback.
#        You implemented an incident."
#
#
# ============================================================================
# CHEWBACCA FUTURE REVIEW #2
# ============================================================================
#
# Future Engineer:
#
#       "Service B was viable thirty seconds ago."
#
# Chewbacca:
#
#       "Excellent historical information."
#
#
# Future Engineer:
#
#       "So I invoked it."
#
# Chewbacca:
#
#       "That was not the question."
#
#
# ============================================================================
# CHEWBACCA FUTURE REVIEW #3
# ============================================================================
#
# Future Engineer:
#
#       "Claude failed, so fallback.py ranks Gemini,
#        our proprietary model, and three Azure deployments."
#
# Chewbacca:
#
#       "Why does fallback.py contain a model-selection system?"
#
#
# Future Engineer:
#
#       "Because this is fallback."
#
# Chewbacca:
#
#       "No. This is architecture hiding behind a filename."
#
#
# ============================================================================
# CHEWBACCA FUTURE REVIEW #4
# ============================================================================
#
# Future Engineer:
#
#       "The policy service was unavailable,
#        so we skipped policy during recovery."
#
# Chewbacca:
#
#       "And what authorized the destination?"
#
#
# Future Engineer:
#
#       "Availability."
#
# Chewbacca:
#
#       "I am calling Security."
#
#
# ============================================================================
# CHEWBACCA FUTURE REVIEW #5
# ============================================================================
#
# Future Engineer:
#
#       "I put retries, fallback, model selection,
#        BGP, provider failover, MCP recovery,
#        and telemetry in RoutingOrchestrator."
#
# Chewbacca:
#
#       "So what does the rest of the project do?"
#
#
# ============================================================================
# NOTE TO FUTURE SELF — BEFORE ADDING CODE HERE
# ============================================================================
#
# Before expanding FallbackEvaluator, ask:
#
#
#       Is this truly fallback eligibility?
#
#
#       Or is it retry?
#
#
#       Or route selection?
#
#
#       Or model selection?
#
#
#       Or service health?
#
#
#       Or deployment failover?
#
#
#       Or network recovery?
#
#
#       Or workflow recovery?
#
#
#       Or policy?
#
#
#       Or telemetry?
#
#
#       Or execution?
#
#
# If the answer is anything other than fallback eligibility:
#
#
#       IT PROBABLY BELONGS SOMEWHERE ELSE.
#
#
# ============================================================================
# NOTE TO FUTURE SELF — DO NOT SOLVE FAILURE BY REMOVING CONSTRAINTS
# ============================================================================
#
# When recovery becomes difficult, the easiest implementation is often:
#
#
#       remove one constraint
#
#
# until something works.
#
#
# Agent 11 must do the opposite:
#
#
#       PRESERVE THE CONSTRAINTS
#
#       SEARCH FOR ANOTHER VIABLE SOLUTION
#
#       OR STOP
#
#
# ============================================================================
# NOTE TO FUTURE SELF — AVAILABILITY IS NOT THE ONLY SUCCESS METRIC
# ============================================================================
#
# A request that refuses to disclose protected data to an unauthorized model
# during an outage may look like:
#
#
#       an availability failure
#
#
# while actually representing:
#
#
#       successful security enforcement
#
#
# Both facts can be true.
#
#
# ============================================================================
# NOTE TO FUTURE SELF — KEEP THE EVIDENCE HONEST
# ============================================================================
#
# Do not rewrite:
#
#
#       UNKNOWN -> UNAVAILABLE
#
#       INDETERMINATE -> DENY
#
#       INVOCATION FAILURE -> SERVICE FAILURE
#
#       SERVICE FAILURE -> MODEL FAILURE
#
#
# merely because simplified states are easier to route.
#
#
#       FAIL CLOSED.
#
#       DO NOT FALSIFY STATE.
#
#
# ============================================================================
# NOTE TO FUTURE SELF — KEEP HISTORY HONEST
# ============================================================================
#
# Do not mutate old routing evidence until it describes the present.
#
#
# Preserve:
#
#
#       what was known then
#
#
# separately from:
#
#
#       what is known now
#
#
# This will matter enormously when debugging distributed failures.
#
#
# ============================================================================
# NOTE TO FUTURE SELF — KEEP AUTHORITY HONEST
# ============================================================================
#
# Recovery does not grant:
#
#
#       new data permissions
#
#       new routing permissions
#
#       new tool permissions
#
#       new execution permissions
#
#
# Failure is not an authorization mechanism.
#
#
# ============================================================================
# NOTE TO FUTURE SELF — KEEP THE ROUTER HONEST
# ============================================================================
#
# AIRouter selects among evaluated candidates.
#
#
# It should not become:
#
#
#       policy engine
#
#       model evaluator
#
#       network monitor
#
#       recovery engine
#
#
# Keep routing decisions based upon explicit evidence.
#
#
# ============================================================================
# NOTE TO FUTURE SELF — KEEP FALLBACK HONEST
# ============================================================================
#
# FallbackEvaluator answers:
#
#
#       MAY ANOTHER ROUTING CYCLE BEGIN?
#
#
# If you need it to answer:
#
#
#       WHAT SHOULD HAPPEN NEXT IN THE ENTIRE SYSTEM?
#
#
# then you are probably asking the wrong component.
#
#
# ============================================================================
# SEIR-II QUESTIONS TO REVISIT
# ============================================================================
#
# Revisit these when operational evidence exists:
#
#
#       1. Do invocation attempts need a first-class contract?
#
#       2. Which failure categories are retryable?
#
#       3. Do retries need independent budgets?
#
#       4. Do fallbacks need independent budgets?
#
#       5. How should total recovery cost be bounded?
#
#       6. How should total recovery latency be bounded?
#
#       7. Do we need circuit breakers?
#
#       8. Do we need backoff?
#
#       9. Do we need failure-domain modeling?
#
#      10. How should regional failover work?
#
#      11. How should provider failover work?
#
#      12. What belongs to cloud-native infrastructure instead?
#
#      13. Should fallback rediscover services?
#
#      14. How fresh must policy evidence be?
#
#      15. How fresh must network evidence be?
#
#      16. How fresh must service-health evidence be?
#
#      17. How should multiple viable FMs be ranked?
#
#      18. Should recovery use the same model-selection strategy
#          as initial routing?
#
#      19. How should model/version drift affect recovery?
#
#      20. How should capacity and quotas affect viability?
#
#      21. How should residency constrain regional recovery?
#
#      22. How should partial streaming output be handled?
#
#      23. How should malformed structured output be handled?
#
#      24. How should output-policy rejection affect recovery?
#
#      25. How should MCP failures be recovered?
#
#      26. How should multi-agent workflows recover?
#
#      27. What recovery state must be durable?
#
#      28. What recovery evidence must be auditable?
#
#      29. How should human intervention work?
#
#      30. What is the candidate-evaluation component?
#
#
# Do not answer all thirty merely because this list exists.
#
#
# ============================================================================
# PART III FINAL INVARIANTS
# ============================================================================
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
#       OPERATIONAL EVIDENCE
#           SHOULD DRIVE
#       FUTURE RECOVERY CONTRACTS
#
#
#       DOCUMENTED POSSIBILITY
#           !=
#       APPROVED DOMAIN MODEL
#
#
#       FALLBACK
#           =
#       PERMISSION TO BEGIN
#       ANOTHER ROUTING CYCLE
#
#
#       FALLBACK != RETRY
#
#       FALLBACK != FAILOVER
#
#       FALLBACK != DISASTER RECOVERY
#
#       FALLBACK != WORKFLOW RECOVERY
#
#
#       RETRY BUDGET != FALLBACK BUDGET
#
#
#       FAILURE OBSERVED
#           !=
#       FAILURE LOCATION KNOWN
#
#
#       INVOCATION FAILURE != SERVICE FAILURE
#
#       INVOCATION FAILURE != MODEL FAILURE
#
#
#       DIFFERENT MODEL
#           !=
#       INDEPENDENT FAILURE DOMAIN
#
#
#       MODEL DIVERSITY
#           !=
#       INFRASTRUCTURE DIVERSITY
#
#
#       SAME MODEL
#           !=
#       SAME FAILURE DOMAIN
#
#
#       MODEL != SERVICE != DEPLOYMENT
#
#
#       ROUTING DOMAIN != CLOUD PROVIDER
#
#
#       COMPANY_CLOUD_LLM
#           !=
#       AWS
#
#       COMPANY_CLOUD_LLM
#           !=
#       AZURE
#
#       COMPANY_CLOUD_LLM
#           !=
#       GCP
#
#       COMPANY_CLOUD_LLM
#           !=
#       OCI
#
#
#       CAPABILITY MATCHING != MODEL SELECTION
#
#
#       FALLBACK
#           MUST NOT CREATE
#       A SECOND MODEL-SELECTION ALGORITHM
#
#
#       HARD CONSTRAINTS BEFORE OPTIMIZATION
#
#
#       POLICY NEVER BECOMES A SCORE
#
#
#       INCIDENT != POLICY SUSPENSION
#
#
#       BREAK-GLASS ACCESS != FALLBACK
#
#
#       BUDGET AVAILABLE != ROUTE AUTHORIZED
#
#
#       AVAILABLE REGION != AUTHORIZED REGION
#
#
#       DISCOVERED != TRUSTED
#
#       DISCOVERED != AUTHORIZED
#
#
#       BGP REACHABLE != AI AUTHORIZED
#
#       SD-WAN AVAILABLE != AI AUTHORIZED
#
#       AUTHORIZED != REACHABLE
#
#
#       PARALLEL INVOCATION
#           !=
#       SEQUENTIAL FALLBACK
#
#
#       FIRST RESPONSE WINS
#           !=
#       ONLY ONE SERVICE RECEIVED DATA
#
#
#       SUCCESSFUL INFERENCE != USABLE RESULT
#
#
#       OUTPUT FAILURE != ROUTE FAILURE
#
#
#       TOOL FAILURE != MODEL FAILURE
#
#       MCP FALLBACK != AI FALLBACK
#
#
#       AI REASONING != TOOL EXECUTION
#
#
#       AGENT HANDOFF != SECURITY RESET
#
#
#       PROCESS MEMORY != DURABLE RECOVERY STATE
#
#
#       REASONING RETRY != ACTION RETRY
#
#
#       HUMAN OVERRIDE != UNBOUNDED AUTHORITY
#
#
#       TELEMETRY != DOMAIN STATE
#
#
#       AUDITABILITY REWARDS IMMUTABLE HISTORY
#
#
#       TELEMETRY-DERIVED PREFERENCE
#           !=
#       POLICY AUTHORIZATION
#
#
#       AI RECOMMENDATION != AUTHORIZATION
#
#
#       HISTORICAL QUALITY != CURRENT QUALITY
#
#
#       DEPLOYED != APPROVED FOR THIS WORKLOAD
#
#
#       CAPACITY != CAPABILITY
#
#
#       CHEAPER != PERMITTED
#
#       FASTER != PERMITTED
#
#
#       BEST != UNIVERSALLY BEST
#
#
#       CONTROL PLANE FAILURE != PERMISSION
#
#
#       CONTROL-PLANE RECOVERY != MODEL FALLBACK
#
#
#       UNKNOWN != SAFE
#
#       UNKNOWN != DENIED
#
#       UNKNOWN != UNAVAILABLE
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
#       CACHED ALLOW != PERMANENT AUTHORIZATION
#
#
#       VALID PAYLOAD != TRUSTED PAYLOAD
#
#
#       PYDANTIC VALIDATION != CONCURRENCY CONTROL
#
#
#       RECOVERY IS A COLLABORATION
#
#
#       COORDINATION != OWNERSHIP
#
#
#       ROUTING ORCHESTRATOR != GOD OBJECT
#
#
#       CANDIDATE EVALUATION != FALLBACK
#
#
#       REJECTION PRECEDENCE != FALLBACK POLICY
#
#
#       POLICY BLOCK != OPERATIONAL FAILURE
#
#
#       NULL != FALLBACK TRIGGER
#
#
#       USER CANCELLED != SERVICE FAILED
#
#
#       RECOVERY OUTCOME != REQUEST STATUS
#
#
#       OUTPUT MAY BECOME NEW INPUT
#
#
#       AI-GENERATED != SAFE
#
#
#       FALLBACK != COPY EVERYTHING TO THE NEXT MODEL
#
#
#       PROVENANCE != AUTHORIZATION
#
#
#       SAME MODEL ID
#           !=
#       OPERATIONALLY EQUIVALENT SERVICE
#
#
#       SLO PRESSURE != POLICY OVERRIDE
#
#
#       FAILURE SHOULD EXERCISE POLICY,
#       NOT DISABLE IT
#
#
#       FAILURE IS NOT
#       AN AUTHORIZATION MECHANISM
#
#
#       FALLBACK MAY REDUCE AVAILABILITY.
#
#       FALLBACK MUST NEVER REDUCE SECURITY POLICY.
#
#
# ============================================================================
# FINAL NOTE TO FUTURE SELF
# ============================================================================
#
# If Agent 11 is now routing among:
#
#
#       Claude
#
#       Gemini
#
#       proprietary company models
#
#       AWS deployments
#
#       Azure deployments
#
#       GCP deployments
#
#       OCI deployments
#
#       on-premises GPU clusters
#
#
# while responding to:
#
#
#       service failures
#
#       regional outages
#
#       network changes
#
#       policy changes
#
#       capacity changes
#
#       model changes
#
#
# then congratulations:
#
#
#       THE SIMPLE SEIR-I ARCHITECTURE SURVIVED
#       LONG ENOUGH TO BECOME A REAL PROBLEM.
#
#
# That does not mean fallback.py should become complicated.
#
#
# It means the surrounding architecture has earned additional components.
#
#
# Keep this file responsible for the smallest coherent recovery question
# that actually belongs here.
#
#
# If Chewbacca opens fallback.py and discovers:
#
#
#       model ranking
#
#       BGP configuration
#
#       cloud SDK calls
#
#       MCP execution
#
#       policy overrides
#
#       a database
#
#       and a while True loop
#
#
# Future Self has some explaining to do.
#
#
# ============================================================================
# END PART III
# ============================================================================
