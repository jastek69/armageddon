# ============================================================================
# network/orchestrator.py
#
# PART I
#
# BASIC NETWORK SUBSYSTEM ORCHESTRATION
# ============================================================================
#
# PURPOSE
# -------
#
# The NetworkOrchestrator coordinates Agent 11 network observation and
# assessment.
#
# It answers:
#
#
#       "What does the network subsystem currently know
#        about operational connectivity from this source
#        to this destination?"
#
#
# Part I coordinates:
#
#
#       path evidence collection
#
#       path assessment
#
#
# It deliberately does NOT coordinate:
#
#
#       AI policy
#
#       model capability
#
#       AI service availability
#
#       AI service selection
#
#       AI inference
#
#       BGP configuration
#
#       SD-WAN configuration
#
#       network remediation
#
#
# ============================================================================
# CENTRAL PART I FLOW
# ============================================================================
#
#
#       source_id
#           +
#       destination_id
#           +
#       requested path types
#                   |
#                   v
#       NetworkPathEvidenceEvaluator
#                   |
#                   v
#       NetworkPathEvidence[]
#                   |
#                   v
#       NetworkPathAssessmentEvaluator
#                   |
#                   v
#       NetworkPathAssessment
#
#
# ============================================================================
# ARCHITECTURAL BOUNDARY
# ============================================================================
#
#
#       NETWORK DESCRIBES REACHABILITY.
#
#       POLICY DESCRIBES PERMISSION.
#
#       ROUTING DESCRIBES SELECTION.
#
#
# Therefore:
#
#
#       NETWORK ASSESSMENT != AUTHORIZATION
#
#       NETWORK ASSESSMENT != AI ROUTING
#
#
# ============================================================================


from datetime import datetime

from ..models.enums.network_enums import NetworkPathType

from .path import (
    NetworkPathAssessment,
    NetworkPathAssessmentEvaluator,
    NetworkPathEvidence,
    NetworkPathEvidenceEvaluator,
)


# ============================================================================
# NETWORK ORCHESTRATOR
# ============================================================================


class NetworkOrchestrator:
    """
    Coordinate Agent 11 network observation and assessment.

    Part I responsibilities:

        1. Receive a source.

        2. Receive a destination.

        3. Receive the path types that should be observed.

        4. Ask the path evidence evaluator to collect evidence.

        5. Give the collected evidence to the path assessment evaluator.

        6. Return the resulting NetworkPathAssessment.


    The NetworkOrchestrator does NOT determine:

        data authorization

        model capability

        AI service availability

        AI routing preference

        AI routing selection

        inference execution


    Core principle:

        SOURCES OBSERVE.

        EVALUATORS INTERPRET.

        MODELS REPRESENT.

        ORCHESTRATORS COORDINATE.
    """

    def __init__(
        self,
        path_evidence_evaluator: NetworkPathEvidenceEvaluator,
        path_assessment_evaluator: NetworkPathAssessmentEvaluator,
    ) -> None:
        """
        Create a network orchestrator using injected dependencies.

        The orchestrator receives already-constructed collaborators.

        It does not construct infrastructure clients itself.

        It does not load:

            cloud credentials

            Kubernetes configuration

            Cisco credentials

            router credentials

            VPN credentials

        Those responsibilities belong to the application's composition
        boundary.


        Dependency direction:

            infrastructure adapter
                    |
                    v
            evidence provider
                    |
                    v
            evidence evaluator
                    |
                    v
            NetworkOrchestrator
                    |
                    v
            assessment evaluator


        This keeps infrastructure construction outside the domain
        coordination layer.
        """

        self._path_evidence_evaluator = path_evidence_evaluator
        self._path_assessment_evaluator = path_assessment_evaluator

    # ========================================================================
    # ASSESS CONNECTIVITY
    # ========================================================================

    def assess_connectivity(
        self,
        source_id: str,
        destination_id: str,
        path_types: list[NetworkPathType],
        assessed_at: datetime,
    ) -> NetworkPathAssessment:
        """
        Assess operational connectivity from one source to one destination.

        The caller supplies the broad path types that should be observed.

        Example:

            [
                NetworkPathType.PRIVATE_LINK,
                NetworkPathType.VPN,
                NetworkPathType.INTERNET,
            ]


        Part I performs:

            OBSERVE
                |
                v
            ASSESS


        It does NOT perform:

            OBSERVE
                |
                v
            AUTHORIZE
                |
                v
            SELECT


        Authorization belongs to policy.

        AI service selection belongs to routing.
        """

        # --------------------------------------------------------------------
        # Stage 1: OBSERVE
        # --------------------------------------------------------------------
        #
        # Collect normalized path evidence for every requested path type.
        #
        # The orchestrator does not know how the evidence was obtained.
        #
        # It may eventually originate from:
        #
        #     static test data
        #
        #     synthetic probes
        #
        #     VPN infrastructure
        #
        #     private connectivity
        #
        #     SD-WAN
        #
        #     cloud networking systems
        #
        #
        # Vendor-specific complexity should terminate before reaching this
        # orchestration boundary.
        #
        # --------------------------------------------------------------------

        evidence: list[NetworkPathEvidence] = []

        for path_type in path_types:
            path_evidence = (
                self._path_evidence_evaluator.get_path_evidence(
                    source_id=source_id,
                    destination_id=destination_id,
                    path_type=path_type,
                )
            )

            evidence.append(path_evidence)

        # --------------------------------------------------------------------
        # Stage 2: ASSESS
        # --------------------------------------------------------------------
        #
        # The assessment evaluator owns interpretation of the evidence.
        #
        # The orchestrator deliberately does not duplicate assessment rules.
        #
        #
        # Do NOT write:
        #
        #     if any(
        #         item.state is NetworkPathState.AVAILABLE
        #         for item in evidence
        #     ):
        #         ...
        #
        #
        # here.
        #
        # That behavior belongs to:
        #
        #     NetworkPathAssessmentEvaluator
        #
        #
        #       ORCHESTRATION != INTERPRETATION
        #
        # --------------------------------------------------------------------

        return self._path_assessment_evaluator.assess(
            source_id=source_id,
            destination_id=destination_id,
            evidence=evidence,
            assessed_at=assessed_at,
        )


# ============================================================================
# WHY THIS CLASS IS SMALL
# ============================================================================
#
# This is intentional.
#
#
# A common architectural mistake is:
#
#
#       ORCHESTRATOR
#           =
#       PLACE WHERE EVERYTHING GOES
#
#
# That eventually creates:
#
#
#       God classes
#
#       duplicated business rules
#
#       circular dependencies
#
#       infrastructure coupling
#
#       difficult tests
#
#
# Agent 11 instead follows:
#
#
#       SOURCES OBSERVE.
#
#       EVALUATORS INTERPRET.
#
#       MODELS REPRESENT.
#
#       ORCHESTRATORS COORDINATE.
#
#
# ============================================================================


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================
#
# NetworkOrchestrator receives its dependencies.
#
#
# It does NOT do:
#
#
#       self._cisco_client = ...
#
#       self._aws_client = ...
#
#       self._azure_client = ...
#
#       self._kubernetes_client = ...
#
#
# The application composition root constructs those dependencies.
#
#
# ============================================================================
#
#
#       ORCHESTRATOR USES DEPENDENCIES.
#
#       ORCHESTRATOR DOES NOT CONSTRUCT THE WORLD.
#
#
# ============================================================================


# ============================================================================
# PATH TYPES ARE QUERIES, NOT FACTS
# ============================================================================
#
# The caller may request:
#
#
#       PRIVATE_LINK
#
#       VPN
#
#       INTERNET
#
#
# This does not mean those paths:
#
#
#       exist
#
#       are available
#
#       are authorized
#
#
# It means:
#
#
#       "Obtain evidence about these path categories."
#
#
# ============================================================================
#
#
#       QUERY != FACT
#
#
# ============================================================================


# ============================================================================
# EMPTY PATH TYPE COLLECTION
# ============================================================================
#
# Part I intentionally permits:
#
#
#       path_types = []
#
#
# This produces:
#
#
#       evidence = []
#
#
# The assessment evaluator then determines the correct assessment.
#
#
# Under the Part III-B semantics:
#
#
#       NO EVIDENCE
#           ->
#       UNKNOWN
#
#
# not:
#
#
#       UNAVAILABLE
#
#
# ============================================================================
#
#
#       UNKNOWN != UNAVAILABLE
#
#
# ============================================================================


# ============================================================================
# DUPLICATE PATH TYPES
# ============================================================================
#
# Part I does not silently deduplicate:
#
#
#       [
#           VPN,
#           VPN,
#       ]
#
#
# If supplied, both observations are requested.
#
#
# A future NetworkAssessmentRequest model may eventually enforce uniqueness
# if the domain decides duplicates are invalid.
#
#
# The orchestrator should not quietly rewrite caller intent merely because
# duplicate values appear unusual.
#
#
# ============================================================================
#
#
#       VALIDATION SHOULD BE EXPLICIT.
#
#       NORMALIZATION SHOULD BE INTENTIONAL.
#
#
# ============================================================================


# ============================================================================
# TIME IS EXPLICIT
# ============================================================================
#
# The caller supplies:
#
#
#       assessed_at
#
#
# rather than NetworkOrchestrator calling:
#
#
#       datetime.now()
#
#
# internally.
#
#
# This makes behavior deterministic and easy to test.
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
# OBSERVATION TIME != ASSESSMENT TIME
# ============================================================================
#
# Path evidence may have:
#
#
#       observed_at = T1
#
#
# while the resulting assessment has:
#
#
#       assessed_at = T2
#
#
# Those timestamps describe different events.
#
#
# Future freshness logic depends upon preserving that distinction.
#
#
# ============================================================================
#
#
#       OBSERVATION TIME != ASSESSMENT TIME
#
#
# ============================================================================


# ============================================================================
# EXPECTED OBSERVATION FAILURE
# ============================================================================
#
# Infrastructure observation can fail.
#
#
# Example:
#
#
#       VPN observer cannot obtain trustworthy evidence.
#
#
# The infrastructure/evidence boundary may translate an expected observation
# failure into:
#
#
#       NetworkPathState.UNKNOWN
#
#
# The orchestrator can continue collecting other evidence.
#
#
# ============================================================================
#
#
#       ONE OBSERVER FAILURE
#           !=
#       NETWORK ORCHESTRATION FAILURE
#
#
# ============================================================================


# ============================================================================
# PROGRAMMING FAILURE
# ============================================================================
#
# NetworkOrchestrator deliberately does NOT contain:
#
#
#       except Exception:
#
#
# around the orchestration process.
#
#
# Unexpected failures such as:
#
#
#       TypeError
#
#       AttributeError
#
#       broken dependency contracts
#
#       implementation defects
#
#
# should remain visible.
#
#
# ============================================================================
#
#
#       PROGRAMMING FAILURE
#           !=
#       NETWORK UNCERTAINTY
#
#
# ============================================================================


# ============================================================================
# PARTIAL KNOWLEDGE
# ============================================================================
#
# Agent 11 may simultaneously know:
#
#
#       PRIVATE_LINK = AVAILABLE
#
#       VPN = UNKNOWN
#
#       INTERNET = AVAILABLE
#
#
# That is valid.
#
#
# We do not need to destroy uncertainty merely to produce a simpler answer.
#
#
# ============================================================================
#
#
#       PARTIAL KNOWLEDGE IS STILL KNOWLEDGE.
#
#
# ============================================================================


# ============================================================================
# NETWORK ASSESSMENT != PATH SELECTION
# ============================================================================
#
# Suppose:
#
#
#       PRIVATE_LINK = AVAILABLE
#
#       VPN = DEGRADED
#
#       INTERNET = AVAILABLE
#
#
# A connectivity assessment may conclude:
#
#
#       AVAILABLE
#
#
# That does NOT mean NetworkOrchestrator selected:
#
#
#       PRIVATE_LINK
#
#
# or:
#
#
#       INTERNET
#
#
# ============================================================================
#
#
#       ASSESSMENT != SELECTION
#
#
# ============================================================================


# ============================================================================
# NETWORK PATH != AI ROUTE
# ============================================================================
#
# Network paths describe connectivity mechanisms.
#
#
# AI routes describe Agent 11 reasoning domains:
#
#
#       EXTERNAL_FM
#
#       COMPANY_CLOUD_LLM
#
#       COMPANY_ONPREM_LLM
#
#
# These are separate concepts.
#
#
# ============================================================================
#
#
#       NETWORK PATH != AI ROUTE
#
#
# ============================================================================


# ============================================================================
# POLICY IS DELIBERATELY ABSENT
# ============================================================================
#
# Suppose:
#
#
#       INTERNET = AVAILABLE
#
#
# NetworkOrchestrator reports that network fact.
#
#
# It does not ask:
#
#
#       Is the data E7?
#
#       Is the data E8?
#
#       Is the data E9?
#
#
# It does not turn:
#
#
#       AVAILABLE
#
#
# into:
#
#
#       UNAVAILABLE
#
#
# merely because security policy might prohibit the path.
#
#
# ============================================================================
#
#
#       PATH AVAILABLE != PATH AUTHORIZED
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ============================================================================


# ============================================================================
# SERVICE AVAILABILITY IS DELIBERATELY ABSENT
# ============================================================================
#
# A network path may work while an AI service does not.
#
#
# Example:
#
#
#       TCP connectivity:
#           AVAILABLE
#
#
#       inference service:
#           HTTP 503
#
#
# Network state may correctly remain:
#
#
#       AVAILABLE
#
#
# while service state is:
#
#
#       UNAVAILABLE
#
#
# ============================================================================
#
#
#       NETWORK SUCCESS != SERVICE SUCCESS
#
#
# ============================================================================


# ============================================================================
# MODEL CAPABILITY IS DELIBERATELY ABSENT
# ============================================================================
#
# NetworkOrchestrator does not know whether the destination model supports:
#
#
#       TEXT_GENERATION
#
#       SECURITY_ANALYSIS
#
#       CODE_REASONING
#
#       TOOL_USE
#
#
# ============================================================================
#
#
#       REACHABLE != CAPABLE
#
#
# ============================================================================


# ============================================================================
# AUTHORIZATION IS DELIBERATELY ABSENT
# ============================================================================
#
# The path may be:
#
#
#       reachable
#
#       fast
#
#       healthy
#
#
# and still prohibited.
#
#
# ============================================================================
#
#
#       REACHABLE != AUTHORIZED
#
#
# ============================================================================


# ============================================================================
# CANDIDATE EVALUATION COMES LATER
# ============================================================================
#
# Eventually a routing candidate evaluator may combine:
#
#
#       PolicyDecision --------------------+
#                                          |
#       Model capability ------------------+
#                                          |
#       Service availability --------------+--> CandidateEvaluator
#                                          |
#       Network assessment ----------------+
#                                          |
#                                          v
#                                  RoutingCandidate
#
#
# NetworkOrchestrator produces network facts for that future join.
#
#
# It does not perform the join itself.
#
#
# ============================================================================


# ============================================================================
# BGP IS DELIBERATELY ABSENT FROM PART I
# ============================================================================
#
# Part III-A established that BGP can provide:
#
#
#       ROUTE EVIDENCE
#
#
# But:
#
#
#       ROUTE EVIDENCE != PATH EVIDENCE
#
#
# and:
#
#
#       BGP ROUTE EXISTS != END-TO-END CONNECTIVITY
#
#
# Part II of this orchestrator may coordinate route evidence.
#
#
# Part I does not need it.
#
#
# ============================================================================


# ============================================================================
# SD-WAN IS DELIBERATELY ABSENT FROM PART I
# ============================================================================
#
# SD-WAN may eventually provide operational observations.
#
#
# But the NetworkOrchestrator should never become an SD-WAN controller.
#
#
# ============================================================================
#
#
#       SD-WAN OBSERVATION != SD-WAN CONTROL
#
#
# ============================================================================


# ============================================================================
# MULTI-CLOUD IS DELIBERATELY ABSENT FROM PART I
# ============================================================================
#
# The same orchestration contract should eventually work with destinations
# deployed in:
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
# None of those provider identities need to appear in Part I.
#
#
# ============================================================================
#
#
#       CLOUD PROVIDER != ROUTING DOMAIN
#
#       CLOUD PROVIDER != NETWORK PATH TYPE
#
#
# ============================================================================


# ============================================================================
# TESTING PART I
# ============================================================================
#
# NetworkOrchestrator should be testable entirely with deterministic evidence.
#
#
# Students should NOT need:
#
#
#       Cisco hardware
#
#       AWS
#
#       Azure
#
#       GCP
#
#       OCI
#
#       Kubernetes
#
#       a VPN
#
#       a BGP peer
#
#
# merely to test orchestration semantics.
#
#
# ============================================================================
#
#
#       DOMAIN TEST != INFRASTRUCTURE TEST
#
#
# ============================================================================


# ============================================================================
# TEST MATRIX
# ============================================================================
#
# Recommended Part I tests:
#
#
#   1. Single AVAILABLE path
#
#          -> AVAILABLE
#
#
#   2. UNAVAILABLE + AVAILABLE
#
#          -> AVAILABLE
#
#
#   3. DEGRADED only
#
#          -> DEGRADED
#
#
#   4. UNAVAILABLE + DEGRADED
#
#          -> DEGRADED
#
#
#   5. All UNAVAILABLE
#
#          -> UNAVAILABLE
#
#
#   6. UNAVAILABLE + UNKNOWN
#
#          -> UNKNOWN
#
#
#   7. UNKNOWN only
#
#          -> UNKNOWN
#
#
#   8. No requested path types
#
#          -> UNKNOWN
#
#
#   9. Expected observation failure
#
#          -> evidence UNKNOWN
#          -> orchestration continues
#
#
#  10. Unexpected programming failure
#
#          -> exception escapes
#
#
# ============================================================================


# ============================================================================
# IMPORTANT TEST:
# OBSERVER FAILURE != PATH FAILURE
# ============================================================================
#
# If a network observer cannot obtain evidence:
#
#
#       UNKNOWN
#
#
# is appropriate.
#
#
# Do not silently turn:
#
#
#       controller timeout
#
#
# into:
#
#
#       UNAVAILABLE
#
#
# ============================================================================
#
#
#       OBSERVER FAILURE != OBSERVED SYSTEM FAILURE
#
#
# ============================================================================


# ============================================================================
# IMPORTANT TEST:
# POLICY DOES NOT CHANGE NETWORK TRUTH
# ============================================================================
#
# Given:
#
#
#       INTERNET = AVAILABLE
#
#
# even if some future policy says:
#
#
#       INTERNET = DENIED FOR E9
#
#
# the network assessment remains:
#
#
#       AVAILABLE
#
#
# Policy separately says:
#
#
#       DENIED
#
#
# ============================================================================
#
#
#       NETWORK TRUTH != POLICY DECISION
#
#
# ============================================================================


# ============================================================================
# IMPORTANT TEST:
# NETWORK SUCCESS DOES NOT CREATE ROUTING SUCCESS
# ============================================================================
#
# Given:
#
#
#       PRIVATE_LINK = AVAILABLE
#
#
# Agent 11 may still have:
#
#
#       no capable model
#
#       no healthy service
#
#       policy denial
#
#
# Therefore:
#
#
#       AVAILABLE NETWORK
#           !=
#       VIABLE AI ROUTE
#
#
# ============================================================================


# ============================================================================
# PART I DEPENDENCY GRAPH
# ============================================================================
#
#
#       Path Evidence Provider
#                 |
#                 v
#       NetworkPathEvidenceEvaluator
#                 |
#                 v
#          NetworkOrchestrator
#                 |
#                 v
#       NetworkPathAssessmentEvaluator
#                 |
#                 v
#       NetworkPathAssessment
#
#
# ============================================================================


# ============================================================================
# WHY NetworkOrchestrator DOES NOT OWN STATE
# ============================================================================
#
# Avoid:
#
#
#       self.current_source
#
#       self.current_destination
#
#       self.current_evidence
#
#       self.current_assessment
#
#
# assess_connectivity() receives input and returns a result.
#
#
# This avoids hidden cross-request state.
#
#
# ============================================================================
#
#
#       INPUT
#           |
#           v
#       COORDINATION
#           |
#           v
#       NEW RESULT
#
#
# not:
#
#
#       MUTATE SHARED OBJECT
#           UNTIL IT LOOKS RIGHT
#
#
# ============================================================================


# ============================================================================
# CONCURRENCY
# ============================================================================
#
# Part I intentionally performs observations sequentially.
#
#
# Later infrastructure observation may benefit from:
#
#
#       asyncio
#
#       concurrent requests
#
#       event streams
#
#
# But concurrency does not change the domain contract.
#
#
# ============================================================================
#
#
#       EXECUTION STRATEGY != DOMAIN SEMANTICS
#
#
# ============================================================================
# TEACH THE SEMANTICS FIRST.
#
# OPTIMIZE EXECUTION LATER.
# ============================================================================


# ============================================================================
# FUTURE PART II
# ============================================================================
#
# Part II may coordinate:
#
#
#       endpoint evidence
#
#       route evidence
#
#       path evidence
#
#       path assessment
#
#
# and return a richer:
#
#
#       NetworkAssessmentResult
#
#
# rather than only:
#
#
#       NetworkPathAssessment
#
#
# ============================================================================


# ============================================================================
# FUTURE PART III / SEIR-II
# ============================================================================
#
# Later network orchestration may coordinate:
#
#
#       endpoint identity
#
#       path identity
#
#       BGP route evidence
#
#       SD-WAN evidence
#
#       multi-cloud deployments
#
#       freshness
#
#       provenance
#
#       path measurements
#
#       failure-domain information
#
#
# But it must preserve the same boundary:
#
#
#       NETWORK REPORTS NETWORK FACTS.
#
#
# ============================================================================


# ============================================================================
# FUTURE RESULT AGGREGATE
# ============================================================================
#
# Once endpoint and route evidence join the subsystem, returning only:
#
#
#       NetworkPathAssessment
#
#
# will probably become too narrow.
#
#
# A future domain aggregate may resemble:
#
#
#       NetworkAssessmentResult
#
#           source
#
#           destination
#
#           endpoint evidence
#
#           route evidence
#
#           path evidence
#
#           path assessment
#
#
# That would preserve the structured evidence chain needed for:
#
#
#       explainability
#
#       telemetry
#
#       audit
#
#       candidate evaluation
#
#
# Do not add that aggregate until Part II actually requires it.
#
#
# ============================================================================
#
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================


# ============================================================================
# routing/network_context.py
# ============================================================================
#
# The growing network subsystem makes a separate routing-owned copy of
# network state increasingly unnecessary.
#
#
# Routing should consume authoritative network results rather than maintain
# shadow network truth.
#
#
# ============================================================================
#
#
#       ONE DOMAIN FACT
#           SHOULD HAVE
#       ONE AUTHORITATIVE REPRESENTATION.
#
#
# ============================================================================


# ============================================================================
# PART I FINAL INVARIANTS
# ============================================================================
#
#
#       SOURCES OBSERVE
#
#       EVALUATORS INTERPRET
#
#       MODELS REPRESENT
#
#       ORCHESTRATORS COORDINATE
#
#
#       ORCHESTRATION != INTERPRETATION
#
#       ORCHESTRATION != OBSERVATION
#
#       ORCHESTRATION != AUTHORIZATION
#
#       ORCHESTRATION != AI ROUTING
#
#
#       QUERY != FACT
#
#       UNKNOWN != UNAVAILABLE
#
#       PARTIAL KNOWLEDGE IS STILL KNOWLEDGE
#
#
#       OBSERVER FAILURE != OBSERVED SYSTEM FAILURE
#
#       ONE OBSERVER FAILURE != NETWORK ORCHESTRATION FAILURE
#
#       PROGRAMMING FAILURE != NETWORK UNCERTAINTY
#
#
#       NETWORK ASSESSMENT != PATH SELECTION
#
#       NETWORK PATH != AI ROUTE
#
#       NETWORK SUCCESS != SERVICE SUCCESS
#
#
#       REACHABLE != CAPABLE
#
#       REACHABLE != AUTHORIZED
#
#       PATH AVAILABLE != PATH AUTHORIZED
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
#       TIME IS A DEPENDENCY
#
#       OBSERVATION TIME != ASSESSMENT TIME
#
#
#       DOMAIN TEST != INFRASTRUCTURE TEST
#
#       EXECUTION STRATEGY != DOMAIN SEMANTICS
#
#
#       VENDOR COMPLEXITY ENDS AT THE ADAPTER BOUNDARY
#
#       ONE DOMAIN FACT SHOULD HAVE ONE AUTHORITATIVE REPRESENTATION
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================
# FINAL PART I RULE
# ============================================================================
#
#
#       THE NETWORK ORCHESTRATOR
#       COORDINATES THE COLLECTION
#       AND INTERPRETATION
#       OF NETWORK EVIDENCE.
#
#
#       IT DOES NOT DECIDE
#       WHETHER AGENT 11
#       IS AUTHORIZED TO USE
#       THE RESULTING CONNECTIVITY.
#
#
# ============================================================================
# END OF PART I
# ============================================================================

# ============================================================================
# network/orchestrator.py
#
# PART II
#
# STRUCTURED NETWORK EVIDENCE ORCHESTRATION
# ============================================================================
#
# PURPOSE
# -------
#
# The NetworkOrchestrator coordinates the network subsystem.
#
# Part I coordinated:
#
#
#       path evidence
#           |
#           v
#       path assessment
#
#
# Part II coordinates:
#
#
#       endpoint evidence
#
#       route evidence
#
#       path evidence
#
#       path assessment
#
#
# and packages those facts into:
#
#
#       NetworkAssessmentResult
#
#
# ============================================================================
# CENTRAL QUESTION
# ============================================================================
#
#
#       "What does the network subsystem currently know
#        about operational connectivity
#        from this source
#        to this destination?"
#
#
# It does NOT answer:
#
#
#       "May this AI request use the destination?"
#
#
# ============================================================================
# DOMAIN BOUNDARY
# ============================================================================
#
#
#       NETWORK DESCRIBES REACHABILITY.
#
#       POLICY DESCRIBES PERMISSION.
#
#       ROUTING DESCRIBES SELECTION.
#
#
# ============================================================================
# PART II FLOW
# ============================================================================
#
#
#                ENDPOINT OBSERVATION
#                        |
#                        v
#              NetworkEndpointEvidence
#                        |
#                        |
#                        +----------------------+
#                                               |
#                  ROUTE OBSERVATION            |
#                        |                      |
#                        v                      |
#                   RouteEvidence[]             |
#                        |                      |
#                        +----------------------+
#                                               |
#                   PATH OBSERVATION            |
#                        |                      |
#                        v                      |
#              NetworkPathEvidence[]            |
#                        |                      |
#                        v                      |
#              NetworkPathAssessment            |
#                        |                      |
#                        +----------------------+
#                                               |
#                                               v
#                                  NetworkAssessmentResult
#
#
# ============================================================================
# IMPORTANT
# ============================================================================
#
#
#       ENDPOINT EVIDENCE
#           !=
#       ROUTE EVIDENCE
#           !=
#       PATH EVIDENCE
#           !=
#       PATH ASSESSMENT
#
#
# Different network layers are allowed to report different facts.
#
#
# ============================================================================


from datetime import datetime

from ..models.enums.network_enums import NetworkPathType
from ..models.network.assessment import NetworkAssessmentResult
from ..models.network.endpoint import NetworkEndpointEvidence
from ..models.network.path import (
    NetworkPathAssessment,
    NetworkPathEvidence,
)
from ..models.network.route import RouteEvidence

from .endpoint import NetworkEndpointEvaluator
from .path import (
    NetworkPathAssessmentEvaluator,
    NetworkPathEvidenceEvaluator,
)
from .route import RouteEvidenceEvaluator


# ============================================================================
# NETWORK ORCHESTRATOR
# ============================================================================


class NetworkOrchestrator:
    """
    Coordinate Agent 11 network observation and assessment.

    Part II responsibilities:

        1. Obtain normalized endpoint evidence.

        2. Obtain normalized route evidence.

        3. Obtain normalized path evidence.

        4. Ask the path assessment evaluator to interpret path evidence.

        5. Package the resulting facts into NetworkAssessmentResult.


    The orchestrator does NOT:

        evaluate AI policy

        classify request data

        evaluate model capability

        evaluate AI service availability

        select an AI service

        select an AI routing domain

        perform inference

        configure BGP

        configure SD-WAN

        modify VPN state

        modify cloud networking

        remediate network infrastructure


    Core rule:

        SOURCES OBSERVE.

        ADAPTERS NORMALIZE.

        MODELS REPRESENT.

        EVALUATORS INTERPRET.

        ORCHESTRATORS COORDINATE.
    """

    def __init__(
        self,
        endpoint_evaluator: NetworkEndpointEvaluator,
        route_evidence_evaluator: RouteEvidenceEvaluator,
        path_evidence_evaluator: NetworkPathEvidenceEvaluator,
        path_assessment_evaluator: NetworkPathAssessmentEvaluator,
    ) -> None:
        """
        Construct the orchestrator from already-created dependencies.

        NetworkOrchestrator does not construct infrastructure clients.

        It does not load:

            AWS credentials

            Azure credentials

            GCP credentials

            OCI credentials

            Kubernetes configuration

            Cisco credentials

            router credentials

            VPN credentials

        Those responsibilities belong to the application composition root.


        Dependency direction:

            infrastructure
                 |
                 v
              adapter
                 |
                 v
          evidence evaluator
                 |
                 v
        NetworkOrchestrator


        The orchestrator coordinates dependencies.

        It does not construct the world.
        """

        self._endpoint_evaluator = endpoint_evaluator
        self._route_evidence_evaluator = route_evidence_evaluator
        self._path_evidence_evaluator = path_evidence_evaluator
        self._path_assessment_evaluator = path_assessment_evaluator

    # ========================================================================
    # ASSESS NETWORK
    # ========================================================================

    def assess_network(
        self,
        source_id: str,
        destination_id: str,
        path_types: list[NetworkPathType],
        assessed_at: datetime,
    ) -> NetworkAssessmentResult:
        """
        Assess network connectivity from one source to one destination.

        Processing stages:

            ENDPOINT
                |
                v
            ROUTE
                |
                v
            PATH
                |
                v
            ASSESS
                |
                v
            PACKAGE


        These are network coordination stages.

        They are not AI routing stages.
        """

        # --------------------------------------------------------------------
        # Stage 1: ENDPOINT
        # --------------------------------------------------------------------
        #
        # Ask the endpoint subsystem what it currently knows about the
        # destination.
        #
        # The evaluator returns normalized domain evidence.
        #
        # Expected infrastructure observation failures should already have
        # become:
        #
        #       EndpointObservationState.UNKNOWN
        #
        # before reaching this orchestration layer.
        #
        #
        # The orchestrator therefore does NOT need:
        #
        #       try:
        #           ...
        #       except EndpointObservationError:
        #           ...
        #
        #
        # That translation belongs at the evidence boundary.
        #
        # --------------------------------------------------------------------

        endpoint_evidence: NetworkEndpointEvidence = (
            self._endpoint_evaluator.get_endpoint_evidence(
                destination_id=destination_id,
            )
        )

        # --------------------------------------------------------------------
        # Stage 2: ROUTE
        # --------------------------------------------------------------------
        #
        # Collect normalized route evidence.
        #
        # Route evidence describes what the routing/control plane currently
        # reports.
        #
        #
        # Examples may eventually include:
        #
        #       BGP
        #
        #       static routing
        #
        #       connected routing
        #
        #
        # But the NetworkOrchestrator does not understand vendor-specific
        # route tables.
        #
        #
        #       COORDINATE ROUTE EVIDENCE
        #           !=
        #       IMPLEMENT ROUTING PROTOCOL
        #
        # --------------------------------------------------------------------

        route_evidence: list[RouteEvidence] = (
            self._route_evidence_evaluator.get_route_evidence(
                source_id=source_id,
                destination_id=destination_id,
            )
        )

        # --------------------------------------------------------------------
        # Stage 3: PATH
        # --------------------------------------------------------------------
        #
        # Obtain operational path evidence for every requested broad path
        # type.
        #
        #
        # Examples:
        #
        #       PRIVATE_LINK
        #
        #       VPN
        #
        #       INTERNET
        #
        #       SD_WAN
        #
        #
        # The requested path type is a query.
        #
        # It is not proof that such a path exists.
        #
        #
        #       QUERY != FACT
        #
        # --------------------------------------------------------------------

        path_evidence: list[NetworkPathEvidence] = []

        for path_type in path_types:
            evidence = self._path_evidence_evaluator.get_path_evidence(
                source_id=source_id,
                destination_id=destination_id,
                path_type=path_type,
            )

            path_evidence.append(evidence)

        # --------------------------------------------------------------------
        # Stage 4: ASSESS
        # --------------------------------------------------------------------
        #
        # Interpret the path evidence.
        #
        # NetworkOrchestrator does NOT reproduce the assessment algorithm.
        #
        #
        # Do not put logic here such as:
        #
        #
        #       if any(
        #           item.state is NetworkPathState.AVAILABLE
        #           for item in path_evidence
        #       ):
        #           ...
        #
        #
        # The path assessment evaluator owns that behavior.
        #
        #
        #       ORCHESTRATION != INTERPRETATION
        #
        # --------------------------------------------------------------------

        path_assessment: NetworkPathAssessment = (
            self._path_assessment_evaluator.assess(
                source_id=source_id,
                destination_id=destination_id,
                evidence=path_evidence,
                assessed_at=assessed_at,
            )
        )

        # --------------------------------------------------------------------
        # Stage 5: PACKAGE
        # --------------------------------------------------------------------
        #
        # Preserve the evidence chain.
        #
        # We deliberately return more than:
        #
        #
        #       AVAILABLE
        #
        #
        # or:
        #
        #
        #       UNAVAILABLE
        #
        #
        # because Agent 11 needs to explain what it knew.
        #
        # --------------------------------------------------------------------

        return NetworkAssessmentResult(
            source_id=source_id,
            destination_id=destination_id,
            endpoint_evidence=endpoint_evidence,
            route_evidence=route_evidence,
            path_evidence=path_evidence,
            path_assessment=path_assessment,
            assessed_at=assessed_at,
        )


# ============================================================================
# WHY THERE IS NO try/except Exception HERE
# ============================================================================
#
# Expected infrastructure observation failures should be translated at the
# evidence boundary.
#
#
# For example:
#
#
#       Cisco controller timeout
#               |
#               v
#       typed observation error
#               |
#               v
#       normalized UNKNOWN evidence
#               |
#               v
#       NetworkOrchestrator
#
#
# But:
#
#
#       AttributeError
#
#       TypeError
#
#       broken implementation
#
#
# should not silently become:
#
#
#       UNKNOWN
#
#
# ============================================================================
#
#
#       EXPECTED OBSERVATION FAILURE
#           !=
#       PROGRAMMING DEFECT
#
#
# ============================================================================


# ============================================================================
# ONE OBSERVER FAILURE != ORCHESTRATION FAILURE
# ============================================================================
#
# Imagine:
#
#
#       Endpoint:
#           PRESENT
#
#
#       BGP:
#           UNKNOWN
#
#
#       PrivateLink:
#           AVAILABLE
#
#
#       VPN:
#           UNKNOWN
#
#
# The network subsystem still possesses useful information.
#
#
# ============================================================================
#
#
#       PARTIAL KNOWLEDGE
#           IS STILL KNOWLEDGE.
#
#
# ============================================================================


# ============================================================================
# ROUTE EVIDENCE IS NOT FED DIRECTLY INTO PATH ASSESSMENT
# ============================================================================
#
# Notice carefully:
#
#
#       route_evidence
#
#
# is collected and preserved.
#
#
# But Part II does NOT pass it directly into:
#
#
#       NetworkPathAssessmentEvaluator
#
#
# This is deliberate.
#
#
# Part III-A established:
#
#
#       ROUTE PRESENT != PATH AVAILABLE
#
#
# Example:
#
#
#       BGP:
#           PRESENT
#
#
#       data-plane probe:
#           UNAVAILABLE
#
#
# Both facts can be true.
#
#
# ============================================================================
#
#
#       CONTROL PLANE != DATA PLANE
#
#
# ============================================================================


# ============================================================================
# WHY WE DO NOT "FIX" DISAGREEMENT
# ============================================================================
#
# Suppose:
#
#
#       BGP route:
#           PRESENT
#
#
#       data-plane path:
#           UNAVAILABLE
#
#
# Do not rewrite this as:
#
#
#       DEGRADED
#
#
# merely because two layers disagree.
#
#
# They are not necessarily disagreeing.
#
#
# They are describing different things.
#
#
# ============================================================================
#
#
#       DIFFERENT LAYERS
#           MAY REPORT
#       DIFFERENT FACTS
#
#
# ============================================================================


# ============================================================================
# ENDPOINT EVIDENCE
# ============================================================================
#
# Part I used a simple boolean seam.
#
#
# Part II now preserves:
#
#
#       PRESENT
#
#       ABSENT
#
#       UNKNOWN
#
#
# because endpoint state is now durable network evidence.
#
#
# ============================================================================
#
#
#       ABSENT != UNKNOWN
#
#
# ============================================================================


# ============================================================================
# ENDPOINT PRESENT != PATH AVAILABLE
# ============================================================================
#
# Example:
#
#
#       Endpoint:
#           PRESENT
#
#
#       Path:
#           UNAVAILABLE
#
#
# This means:
#
#
#       the destination exists
#
# but:
#
#
#       connectivity from this source
#       cannot currently be established
#
#
# ============================================================================


# ============================================================================
# ROUTE PRESENT != PATH AVAILABLE
# ============================================================================
#
# Example:
#
#
#       BGP:
#           PRESENT
#
#
#       PrivateLink:
#           UNAVAILABLE
#
#
# Possible explanations include:
#
#
#       forwarding failure
#
#       firewall
#
#       ACL
#
#       broken tunnel
#
#       asymmetric return path
#
#       incorrect next-hop reachability
#
#
# Route evidence alone cannot distinguish them.
#
#
# ============================================================================


# ============================================================================
# PATH AVAILABLE != SERVICE AVAILABLE
# ============================================================================
#
# Example:
#
#
#       Endpoint:
#           PRESENT
#
#
#       Route:
#           PRESENT
#
#
#       Path:
#           AVAILABLE
#
#
#       Inference:
#           HTTP 503
#
#
# Network may still correctly report:
#
#
#       AVAILABLE
#
#
# ============================================================================
#
#
#       NETWORK SUCCESS != APPLICATION SUCCESS
#
#
# ============================================================================


# ============================================================================
# PATH AVAILABLE != AUTHORIZED
# ============================================================================
#
# Suppose:
#
#
#       Internet:
#           AVAILABLE
#
#
# and a future policy says:
#
#
#       E9 data may not use Internet connectivity
#
#
# NetworkOrchestrator still reports:
#
#
#       Internet AVAILABLE
#
#
# Policy separately reports:
#
#
#       DENY
#
#
# ============================================================================
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ============================================================================


# ============================================================================
# NetworkAssessmentResult PRESERVES EXPLANATION
# ============================================================================
#
# Compare:
#
#
#       "Network unavailable."
#
#
# with:
#
#
#       Endpoint:
#           PRESENT
#
#
#       BGP:
#           PRESENT
#
#
#       PrivateLink:
#           UNAVAILABLE
#
#
#       VPN:
#           UNKNOWN
#
#
#       Overall path assessment:
#           UNKNOWN
#
#
# The structured result supports:
#
#
#       troubleshooting
#
#       explainability
#
#       telemetry
#
#       audit
#
#       candidate evaluation
#
#
# ============================================================================
#
#
#       EXPLANATION REQUIRES EVIDENCE.
#
#
# ============================================================================


# ============================================================================
# NetworkAssessmentResult IS NOT A ROUTING CANDIDATE
# ============================================================================
#
# NetworkAssessmentResult describes network facts.
#
#
# RoutingCandidate describes whether an AI service is viable.
#
#
# Eventually:
#
#
#       PolicyDecision --------------------+
#                                          |
#       Capability ------------------------+
#                                          |
#       Service availability --------------+--> CandidateEvaluator
#                                          |
#       NetworkAssessmentResult -----------+
#                                          |
#                                          v
#                                  RoutingCandidate
#
#
# ============================================================================
#
#
#       NETWORK FACT
#           !=
#       ROUTING VIABILITY
#
#
# ============================================================================


# ============================================================================
# NO POLICY IMPORTS
# ============================================================================
#
# This module should not need:
#
#
#       DataRoutePolicy
#
#       PolicyDecision
#
#       UserDataPreference
#
#       DataClassification
#
#
# If those imports appear here, the network boundary is leaking.
#
#
# ============================================================================


# ============================================================================
# NO AIRouter IMPORT
# ============================================================================
#
# NetworkOrchestrator must not import:
#
#
#       AIRouter
#
#
# The dependency direction is:
#
#
#       network
#           |
#           v
#       network facts
#           |
#           v
#       candidate evaluation
#           |
#           v
#       RoutingCandidate
#           |
#           v
#       AIRouter
#
#
# not:
#
#
#       network
#           |
#           v
#       AIRouter
#           |
#           v
#       network
#
#
# ============================================================================


# ============================================================================
# NO AI SERVICE HEALTH
# ============================================================================
#
# NetworkOrchestrator does not determine whether the inference service itself
# can perform work.
#
#
# Service availability remains a separate viability dimension.
#
#
# ============================================================================
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
# ============================================================================


# ============================================================================
# BGP BOUNDARY
# ============================================================================
#
# RouteEvidenceEvaluator may ultimately receive observations from:
#
#
#       FRRouting
#
#       GoBGP
#
#       Cisco
#
#       Juniper
#
#       cloud route systems
#
#
# NetworkOrchestrator should never know:
#
#
#       AS_PATH parsing
#
#       LOCAL_PREF
#
#       MED
#
#       route-map syntax
#
#       neighbor configuration
#
#       advertisement commands
#
#
# ============================================================================
#
#
#       BGP TELLS THE NETWORK SUBSYSTEM
#       WHAT THE CONTROL PLANE BELIEVES.
#
#
#       BGP DOES NOT SELECT
#       THE AI SERVICE.
#
#
# ============================================================================


# ============================================================================
# SD-WAN BOUNDARY
# ============================================================================
#
# Future SD-WAN evidence may originate from:
#
#
#       Cisco
#
#       another SD-WAN controller
#
#       telemetry systems
#
#
# The vendor-specific adapter should translate those observations into
# Agent 11 network vocabulary.
#
#
# ============================================================================
#
#
#       VENDOR COMPLEXITY ENDS
#       AT THE ADAPTER BOUNDARY.
#
#
# ============================================================================


# ============================================================================
# MULTI-CLOUD BOUNDARY
# ============================================================================
#
# The same network orchestration contract should survive destinations in:
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
# Provider-specific network implementations should normalize into the same
# network contracts.
#
#
# ============================================================================
#
#
#       CLOUD PROVIDER != NETWORK PATH TYPE
#
#       CLOUD PROVIDER != AI ROUTING DOMAIN
#
#       NETWORK PATH TYPE != AI ROUTING DOMAIN
#
#
# ============================================================================


# ============================================================================
# TIME
# ============================================================================
#
# assessed_at is supplied by the caller.
#
#
# The orchestrator does not call:
#
#
#       datetime.now()
#
#
# internally.
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
# OBSERVATION TIME != ASSESSMENT TIME
# ============================================================================
#
# Evidence may have been observed at:
#
#
#       T1
#       T2
#       T3
#
#
# while the aggregate is assembled at:
#
#
#       T4
#
#
# Future freshness logic depends upon retaining those distinctions.
#
#
# ============================================================================


# ============================================================================
# PART II IS SYNCHRONOUS
# ============================================================================
#
# Part II intentionally collects evidence sequentially.
#
#
# Future SEIR-II implementations may query:
#
#
#       BGP
#
#       SD-WAN
#
#       VPN
#
#       cloud networking
#
#       synthetic probes
#
#
# concurrently.
#
#
# But:
#
#
#       EXECUTION STRATEGY != DOMAIN SEMANTICS
#
#
# Async execution can be added without changing the network domain contract.
#
#
# ============================================================================


# ============================================================================
# NO REMEDIATION
# ============================================================================
#
# NetworkOrchestrator observes and assesses.
#
#
# It does not:
#
#
#       advertise routes
#
#       withdraw routes
#
#       modify LOCAL_PREF
#
#       change SD-WAN policy
#
#       restart tunnels
#
#       change firewall rules
#
#       create private endpoints
#
#
# ============================================================================
#
#
#       OBSERVE != REMEDIATE
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#       CORRECT REASONING != EXECUTION AUTHORITY
#
#
# ============================================================================


# ============================================================================
# PART II TEST MATRIX
# ============================================================================
#
# 1.
#
#       endpoint PRESENT
#       route PRESENT
#       path AVAILABLE
#
#       -> structured result preserves all three
#
#
# 2.
#
#       endpoint PRESENT
#       route PRESENT
#       path UNAVAILABLE
#
#       -> do not rewrite route state
#
#
# 3.
#
#       endpoint PRESENT
#       route ABSENT
#       path AVAILABLE
#
#       -> preserve both facts
#
#          Perhaps the observed BGP table is not the mechanism responsible
#          for this particular connectivity.
#
#
# 4.
#
#       endpoint UNKNOWN
#       route PRESENT
#       path AVAILABLE
#
#       -> orchestration succeeds with partial knowledge
#
#
# 5.
#
#       endpoint PRESENT
#       route UNKNOWN
#       path AVAILABLE
#
#       -> orchestration succeeds with partial knowledge
#
#
# 6.
#
#       endpoint PRESENT
#       route PRESENT
#       PRIVATE_LINK UNAVAILABLE
#       INTERNET AVAILABLE
#
#       -> preserve both paths
#
#       -> do NOT authorize Internet
#
#
# 7.
#
#       no requested path types
#
#       -> path evidence empty
#       -> path assessment UNKNOWN
#
#
# 8.
#
#       expected infrastructure observation failure
#
#       -> evidence boundary produces UNKNOWN
#       -> orchestration continues
#
#
# 9.
#
#       unexpected TypeError
#
#       -> exception escapes
#
#
# 10.
#
#       E9 policy would deny Internet
#
#       -> network result still reports Internet AVAILABLE
#
#
# ============================================================================


# ============================================================================
# PART II FINAL INVARIANTS
# ============================================================================
#
#
#       SOURCES OBSERVE
#
#       ADAPTERS NORMALIZE
#
#       MODELS REPRESENT
#
#       EVALUATORS INTERPRET
#
#       ORCHESTRATORS COORDINATE
#
#
#       ENDPOINT != ROUTE
#
#       ROUTE != PATH
#
#       PATH != SERVICE HEALTH
#
#
#       ENDPOINT PRESENT != PATH AVAILABLE
#
#       ROUTE PRESENT != PATH AVAILABLE
#
#       PATH AVAILABLE != SERVICE AVAILABLE
#
#       PATH AVAILABLE != PATH AUTHORIZED
#
#
#       CONTROL PLANE != DATA PLANE
#
#       DATA PLANE != APPLICATION PLANE
#
#
#       EVIDENCE != ASSESSMENT
#
#       ASSESSMENT != AUTHORIZATION
#
#       AUTHORIZATION != SELECTION
#
#
#       ABSENT != UNKNOWN
#
#       UNKNOWN != UNAVAILABLE
#
#
#       PARTIAL KNOWLEDGE IS STILL KNOWLEDGE
#
#       ONE OBSERVER FAILURE != NETWORK ORCHESTRATION FAILURE
#
#       EXPECTED OBSERVATION FAILURE != PROGRAMMING DEFECT
#
#
#       ROUTE EVIDENCE != PATH EVIDENCE
#
#       ROUTE EVIDENCE != AI ROUTING DECISION
#
#
#       NETWORK FACT != ROUTING VIABILITY
#
#       NETWORK SUCCESS != APPLICATION SUCCESS
#
#
#       REACHABLE != CAPABLE
#
#       REACHABLE != AUTHORIZED
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
#       EXPLANATION REQUIRES EVIDENCE
#
#       STRUCTURED FACTS > MYSTERY SCORE
#
#
#       COORDINATE ROUTE EVIDENCE != IMPLEMENT BGP
#
#       VENDOR COMPLEXITY ENDS AT THE ADAPTER BOUNDARY
#
#
#       OBSERVE != REMEDIATE
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#       CORRECT REASONING != EXECUTION AUTHORITY
#
#
#       TIME IS A DEPENDENCY
#
#       OBSERVATION TIME != ASSESSMENT TIME
#
#
#       EXECUTION STRATEGY != DOMAIN SEMANTICS
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================
# FINAL PART II RULE
# ============================================================================
#
#
#       THE NETWORK ORCHESTRATOR
#       COORDINATES NETWORK KNOWLEDGE.
#
#
#       IT PRESERVES THE EVIDENCE CHAIN
#       NEEDED TO EXPLAIN THAT KNOWLEDGE.
#
#
#       IT DOES NOT TURN
#       NETWORK KNOWLEDGE
#       INTO AI AUTHORIZATION.
#
#
# ============================================================================
# END OF PART II
# ============================================================================

# ============================================================================
# network/orchestrator.py
#
# PART III-A
#
# PATH IDENTITY AND MULTI-OBSERVER PROVENANCE
# ============================================================================
#
# SEIR-II changes the unit of network reasoning.
#
#
# SEIR-I:
#
#       service_id + path_type
#
#
# SEIR-II:
#
#       source
#           |
#           v
#       specific path instance
#           |
#           v
#       destination
#
#
# ============================================================================
#
#
#       PATH TYPE != PATH INSTANCE
#
#
# ============================================================================


from datetime import datetime, timedelta
from typing import Protocol

from ..models.enums.network_enums import (
    NetworkPathState,
    NetworkPathType,
)

from ..models.network.assessment import NetworkAssessmentResult
from ..models.network.endpoint import NetworkEndpointEvidence

from ..models.network.path import (
    NetworkPathAssessment,
    NetworkPathEvidence,
    NetworkPathIdentity,
)

from ..models.network.route import RouteEvidence

from .endpoint import NetworkEndpointEvaluator
from .path import (
    NetworkPathAssessmentEvaluator,
    NetworkPathEvidenceEvaluator,
)
from .route import RouteEvidenceEvaluator


# ============================================================================
# PATH INVENTORY
# ============================================================================
#
# NetworkOrchestrator should not invent network paths.
#
#
# Something authoritative must answer:
#
#
#       "Which path instances are expected
#        between this source and destination?"
#
#
# Examples:
#
#
#       private-link-tokyo-a
#
#       vpn-tokyo-a
#
#       vpn-tokyo-b
#
#       sdwan-tokyo-primary
#
#       internet-tokyo-a
#
#
# ============================================================================


class NetworkPathInventory(Protocol):
    """
    Provide the expected network path identities for a relationship.

    Inventory describes expected topology.

    It does NOT describe current operational state.
    """

    def get_paths(
        self,
        source_id: str,
        destination_id: str,
    ) -> list[NetworkPathIdentity]:
        ...


# ============================================================================
# STATIC INVENTORY
# ============================================================================
#
# Useful for:
#
#
#       unit tests
#
#       labs
#
#       deterministic demonstrations
#
#
# ============================================================================


class StaticNetworkPathInventory:
    """
    Deterministic path inventory for testing and training.
    """

    def __init__(
        self,
        paths: list[NetworkPathIdentity],
    ) -> None:
        self._paths = list(paths)

    def get_paths(
        self,
        source_id: str,
        destination_id: str,
    ) -> list[NetworkPathIdentity]:

        return [
            path
            for path in self._paths
            if path.source_id == source_id
            and path.destination_id == destination_id
        ]


# ============================================================================
# WHY PATH INVENTORY EXISTS
# ============================================================================
#
# Suppose we observe:
#
#
#       vpn-a = UNAVAILABLE
#
#
# Can we conclude:
#
#
#       all VPN connectivity is unavailable
#
#
# ?
#
#
# Not unless we know whether:
#
#
#       vpn-b
#
#       vpn-c
#
#
# were also expected.
#
#
# ============================================================================
#
#
#       OBSERVED PATH SET
#           !=
#       EXPECTED PATH SET
#
#
# ============================================================================


# ============================================================================
# PATH IDENTITY
# ============================================================================
#
# The expected model contract is intentionally small:
#
#
#   NetworkPathIdentity
#
#       path_id
#       source_id
#       destination_id
#       path_type
#
#
# Example:
#
#
#       path_id:
#           vpn-tokyo-a
#
#       source_id:
#           agent11-tokyo
#
#       destination_id:
#           company-cloud-primary
#
#       path_type:
#           VPN
#
#
# ============================================================================
#
#
#       PATH IDENTITY != PATH STATE
#
#
# ============================================================================


# ============================================================================
# MULTIPLE PATH INSTANCES
# ============================================================================
#
# Consider:
#
#
#       vpn-tokyo-a
#           AVAILABLE
#
#
#       vpn-tokyo-b
#           UNAVAILABLE
#
#
# Both have:
#
#
#       path_type = VPN
#
#
# Therefore:
#
#
#       VPN
#
#
# is insufficient as resource identity.
#
#
# ============================================================================
#
#
#       COLLECTION POSITION != RESOURCE IDENTITY
#
#
# ============================================================================


# ============================================================================
# PROVENANCE
# ============================================================================
#
# SEIR-II may observe one path using several independent systems.
#
#
# Example:
#
#
#       vpn-tokyo-a
#
#           Cisco SD-WAN controller
#               -> AVAILABLE
#
#           synthetic probe
#               -> AVAILABLE
#
#           cloud monitor
#               -> UNKNOWN
#
#
# These are:
#
#
#       THREE OBSERVATIONS
#
#
# of:
#
#
#       ONE PATH
#
#
# ============================================================================
#
#
#       OBSERVATION IDENTITY != PATH IDENTITY
#
#
# ============================================================================


class NetworkPathEvidenceCollector(Protocol):
    """
    Collect zero or more normalized observations for one path instance.

    A mature implementation may aggregate evidence from:

        SD-WAN telemetry

        synthetic probes

        cloud monitoring

        VPN controllers

        network monitoring systems

    The collector does not authorize the path.
    """

    def collect(
        self,
        path: NetworkPathIdentity,
    ) -> list[NetworkPathEvidence]:
        ...


# ============================================================================
# WHY list[NetworkPathEvidence]
# ============================================================================
#
# Earlier:
#
#
#       one path query
#           ->
#       one evidence object
#
#
# SEIR-II:
#
#
#       one path
#           ->
#       zero or more evidence objects
#
#
# This permits:
#
#
#       observer-a -> AVAILABLE
#
#       observer-b -> UNAVAILABLE
#
#
# without pretending there are two paths.
#
#
# ============================================================================
#
#
#       TWO OBSERVATIONS != TWO PATHS
#
#
# ============================================================================


# ============================================================================
# PARALLEL PATH DIFFERENCE
# ============================================================================
#
#
#       vpn-a -> AVAILABLE
#
#       vpn-b -> UNAVAILABLE
#
#
# means:
#
#
#       TWO PATHS HAVE DIFFERENT STATES
#
#
# ============================================================================
# OBSERVER DISAGREEMENT
# ============================================================================
#
#
#       observer-a:
#           vpn-a -> AVAILABLE
#
#       observer-b:
#           vpn-a -> UNAVAILABLE
#
#
# means:
#
#
#       TWO OBSERVERS DISAGREE ABOUT ONE PATH
#
#
# ============================================================================
#
#
#       PARALLEL PATH DIFFERENCE
#           !=
#       OBSERVER DISAGREEMENT
#
#
# ============================================================================


# ============================================================================
# PROVENANCE REQUIREMENT
# ============================================================================
#
# For the distinction above to work, mature NetworkPathEvidence should retain:
#
#
#       path_id
#
#       observer_id
#
#
# alongside:
#
#
#       source_id
#
#       destination_id
#
#       path_type
#
#       state
#
#       observed_at
#
#
# ============================================================================
#
#
#       VALID EVIDENCE
#           WITHOUT PROVENANCE
#       MAY STILL BE
#       INSUFFICIENT EVIDENCE.
#
#
# ============================================================================


# ============================================================================
# TRUST
# ============================================================================
#
# Provenance does NOT automatically imply trust.
#
#
# An evidence object saying:
#
#
#       observer_id = "cisco-controller"
#
#
# does not prove that Cisco produced it.
#
#
# ============================================================================
#
#
#       CLAIMED SOURCE != AUTHENTICATED SOURCE
#
#
#       VALID PYDANTIC MODEL != TRUSTED EVIDENCE
#
#
# ============================================================================
#
# Future systems may need:
#
#
#       authenticated observer identity
#
#       signed telemetry
#
#       protected transport
#
#       authorization around evidence publication
#
#       audit records
#
#
# Those concerns are not implemented merely because observer_id exists.
#
#
# ============================================================================


# ============================================================================
# DO NOT ADD confidence: float
# ============================================================================
#
# Tempting:
#
#
#       confidence = 0.87
#
#
# But:
#
#
#       87% of what?
#
#
# Unless the domain defines exactly what the number means, the apparent
# precision is misleading.
#
#
# ============================================================================
#
#
#       DECIMAL PRECISION != EPISTEMIC PRECISION
#
#
# ============================================================================


# ============================================================================
# PART III-A INVARIANTS
# ============================================================================
#
#
#       PATH TYPE != PATH INSTANCE
#
#       PATH IDENTITY != PATH STATE
#
#       OBSERVED PATH SET != EXPECTED PATH SET
#
#       TWO OBSERVATIONS != TWO PATHS
#
#       PARALLEL PATH DIFFERENCE != OBSERVER DISAGREEMENT
#
#       CLAIMED SOURCE != AUTHENTICATED SOURCE
#
#       VALID PYDANTIC MODEL != TRUSTED EVIDENCE
#
#       DECIMAL PRECISION != EPISTEMIC PRECISION
#
#
# ============================================================================

# ============================================================================
# network/orchestrator.py
#
# PART III-B
#
# FRESHNESS, MEASUREMENTS, EVIDENCE SELECTION,
# AND PER-PATH ASSESSMENT
# ============================================================================
#
# PURPOSE
# -------
#
# Part III-A established:
#
#
#       PATH IDENTITY
#
#       OBSERVER PROVENANCE
#
#
# Part III-B answers:
#
#
#       "Which observations are current enough
#        to participate in a network assessment?"
#
#
# and:
#
#
#       "Given the currently usable evidence
#        for one specific path,
#        what operational state should we conclude?"
#
#
# ============================================================================
# PART III-B BOUNDARY
# ============================================================================
#
#
#       HISTORICAL EVIDENCE
#              |
#              v
#       FRESHNESS EVALUATION
#              |
#              v
#       CURRENTLY USABLE EVIDENCE
#              |
#              v
#       PER-PATH ASSESSMENT
#
#
# ============================================================================
#
# Part III-B does NOT:
#
#
#       authorize paths
#
#       select paths
#
#       select AI services
#
#       select AIRoute
#
#       configure SD-WAN
#
#       interpret BGP
#
#       remediate infrastructure
#
#
# ============================================================================


from datetime import datetime, timedelta

from ..models.network.path import (
    NetworkPathAssessment,
    NetworkPathEvidence,
    NetworkPathIdentity,
)

from .path import NetworkPathAssessmentEvaluator


# ============================================================================
# FRESHNESS EVALUATOR
# ============================================================================


class NetworkEvidenceFreshnessEvaluator:
    """
    Evaluate whether historical network evidence is recent enough to
    participate in a current assessment.

    This class does NOT modify evidence.

    Evidence remains a historical statement:

        "Observer X reported state Y at time Z."

    Freshness is a current interpretation of that historical statement.
    """

    def __init__(
        self,
        maximum_age: timedelta,
    ) -> None:
        """
        Create a freshness evaluator.

        maximum_age defines how old evidence may become before it is no
        longer considered usable for the current assessment.

        Example:

            maximum_age = timedelta(seconds=30)

        means:

            evidence observed 20 seconds ago
                -> fresh

            evidence observed 90 seconds ago
                -> stale for current assessment


        A negative maximum age is nonsensical and therefore rejected.
        """

        if maximum_age < timedelta(0):
            raise ValueError(
                "maximum_age cannot be negative."
            )

        self._maximum_age = maximum_age

    def is_fresh(
        self,
        observed_at: datetime,
        assessed_at: datetime,
    ) -> bool:
        """
        Determine whether an observation is sufficiently recent.

        This method deliberately answers only a temporal question.

        It does NOT determine whether:

            the evidence is trusted

            the observer is authoritative

            the path is available

            the path is authorized

            the path is suitable for an AI workload
        """

        age = assessed_at - observed_at

        # --------------------------------------------------------------------
        # Evidence apparently observed in the future cannot be safely treated
        # as current evidence.
        #
        # Possible causes include:
        #
        #       clock skew
        #
        #       incorrect timestamps
        #
        #       serialization bugs
        #
        #       observer clock problems
        #
        #
        # Part III-B does not attempt to diagnose which cause occurred.
        #
        # --------------------------------------------------------------------

        if age < timedelta(0):
            return False

        return age <= self._maximum_age


# ============================================================================
# WHY FRESHNESS IS NOT STORED ON THE EVIDENCE OBJECT
# ============================================================================
#
# Consider:
#
#
#       NetworkPathEvidence
#
#           state = AVAILABLE
#
#           observed_at = 12:00:00
#
#
# At:
#
#
#       12:00:05
#
#
# it may be:
#
#
#       FRESH
#
#
# At:
#
#
#       12:30:00
#
#
# it may be:
#
#
#       STALE
#
#
# The evidence object itself did not change.
#
#
# ============================================================================
#
#
#       EVIDENCE IS HISTORICAL.
#
#       FRESHNESS IS RELATIVE.
#
#
# ============================================================================
#
# Storing:
#
#
#       freshness = FRESH
#
#
# directly inside the evidence object would create derived state that
# becomes incorrect merely because time passes.
#
#
# ============================================================================


# ============================================================================
# OBSERVED_AT != FRESHNESS
# ============================================================================
#
# observed_at is a fact:
#
#
#       "This observation occurred at T1."
#
#
# freshness is an evaluation:
#
#
#       "At T2, T1 is recent enough for this purpose."
#
#
# ============================================================================
#
#
#       OBSERVED_AT = FACT
#
#       FRESHNESS = INTERPRETATION
#
#
# ============================================================================


# ============================================================================
# STALE != FALSE
# ============================================================================
#
# Suppose:
#
#
#       12:00
#
#       vpn-a = AVAILABLE
#
#
# At 12:30 that observation may be stale.
#
#
# We must NOT rewrite history as:
#
#
#       vpn-a was NOT AVAILABLE at 12:00
#
#
# The correct statement is:
#
#
#       vpn-a WAS observed AVAILABLE at 12:00
#
#
# but:
#
#
#       that observation is no longer sufficient
#       to establish CURRENT availability.
#
#
# ============================================================================
#
#
#       STALE EVIDENCE != FALSE EVIDENCE
#
#
# ============================================================================


# ============================================================================
# FUTURE TIMESTAMP != FRESH
# ============================================================================
#
# Suppose:
#
#
#       assessed_at = 12:00
#
#
#       observed_at = 12:05
#
#
# It would be tempting to calculate:
#
#
#       age = -5 minutes
#
#
# and accidentally conclude:
#
#
#       -5 <= 30 seconds
#
#
# therefore:
#
#
#       FRESH
#
#
# That would be wrong.
#
#
# ============================================================================
#
#
#       TEMPORALLY IMPOSSIBLE EVIDENCE
#           !=
#       VERY FRESH EVIDENCE
#
#
# ============================================================================


# ============================================================================
# TIMEZONE-AWARE DATETIMES
# ============================================================================
#
# Production Agent 11 should strongly prefer timezone-aware datetime values.
#
#
# For example:
#
#
#       datetime.now(timezone.utc)
#
#
# rather than:
#
#
#       datetime.now()
#
#
# A future network base contract may enforce timezone awareness centrally.
#
#
# We do not silently repair naive timestamps here.
#
#
# ============================================================================
#
#
#       AMBIGUOUS TIME != RELIABLE EVIDENCE TIME
#
#
# ============================================================================


# ============================================================================
# TIME IS A DEPENDENCY
# ============================================================================
#
# Notice that is_fresh() receives:
#
#
#       assessed_at
#
#
# It does not call:
#
#
#       datetime.now()
#
#
# internally.
#
#
# This gives us:
#
#
#       deterministic tests
#
#       replayable assessments
#
#       historical analysis
#
#       easier incident reconstruction
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
# ONE TTL FOR PART III-B
# ============================================================================
#
# This implementation intentionally uses:
#
#
#       one maximum_age
#
#
# for one freshness evaluator.
#
#
# Future systems may require:
#
#
#       synthetic probe TTL
#
#       SD-WAN telemetry TTL
#
#       route evidence TTL
#
#       endpoint evidence TTL
#
#
# to differ.
#
#
# That does not require making this class complicated today.
#
#
# The composition layer could eventually create different evaluator
# instances for different evidence categories.
#
#
# ============================================================================
#
#
#       CONFIGURATION DIFFERENCE
#           DOES NOT AUTOMATICALLY REQUIRE
#       DOMAIN COMPLEXITY.
#
#
# ============================================================================


# ============================================================================
# CURRENT PATH EVIDENCE SELECTOR
# ============================================================================
#
# We now need to answer:
#
#
#       "Which evidence belongs to THIS path
#        and is CURRENTLY usable?"
#
#
# That is not yet path assessment.
#
#
# ============================================================================


class CurrentPathEvidenceSelector:
    """
    Select currently usable evidence for one specific path identity.

    Selection checks:

        path identity

        source identity

        destination identity

        path type

        temporal freshness


    It does NOT interpret the selected evidence.

    Therefore it does not produce:

        AVAILABLE

        DEGRADED

        UNAVAILABLE

        UNKNOWN
    """

    def __init__(
        self,
        freshness_evaluator: NetworkEvidenceFreshnessEvaluator,
    ) -> None:
        self._freshness_evaluator = freshness_evaluator

    def select(
        self,
        path: NetworkPathIdentity,
        evidence: list[NetworkPathEvidence],
        assessed_at: datetime,
    ) -> list[NetworkPathEvidence]:
        """
        Return evidence that:

            belongs to the requested path

            and

            is sufficiently fresh for current assessment.
        """

        selected: list[NetworkPathEvidence] = []

        for item in evidence:

            # ----------------------------------------------------------------
            # PATH ID
            # ----------------------------------------------------------------
            #
            # path_id is the primary path-instance identity.
            #
            # ----------------------------------------------------------------

            if item.path_id != path.path_id:
                continue

            # ----------------------------------------------------------------
            # SOURCE
            # ----------------------------------------------------------------
            #
            # A path is relational.
            #
            # Evidence about:
            #
            #       source-a -> destination
            #
            # is not automatically evidence about:
            #
            #       source-b -> destination
            #
            # ----------------------------------------------------------------

            if item.source_id != path.source_id:
                continue

            # ----------------------------------------------------------------
            # DESTINATION
            # ----------------------------------------------------------------

            if item.destination_id != path.destination_id:
                continue

            # ----------------------------------------------------------------
            # PATH TYPE
            # ----------------------------------------------------------------
            #
            # path_id should normally make this redundant.
            #
            # But checking it protects the domain against contradictory
            # evidence identity.
            #
            # Example:
            #
            #       path_id = vpn-a
            #
            # inventory:
            #       path_type = VPN
            #
            # evidence:
            #       path_type = INTERNET
            #
            #
            # That evidence should not silently participate in the assessment.
            #
            # ----------------------------------------------------------------

            if item.path_type is not path.path_type:
                continue

            # ----------------------------------------------------------------
            # FRESHNESS
            # ----------------------------------------------------------------

            if not self._freshness_evaluator.is_fresh(
                observed_at=item.observed_at,
                assessed_at=assessed_at,
            ):
                continue

            selected.append(item)

        return selected


# ============================================================================
# WHY THIS BECAME A CLASS
# ============================================================================
#
# In the sample Part III-B this behavior was a helper function.
#
#
# It has now earned a named responsibility:
#
#
#       CurrentPathEvidenceSelector
#
#
# because:
#
#
#       freshness evaluation
#
#       path identity matching
#
#       current-evidence selection
#
#
# are distinct from:
#
#
#       path-state interpretation
#
#
# ============================================================================
#
#
#       SELECTION != INTERPRETATION
#
#
# ============================================================================


# ============================================================================
# IMPORTANT:
# SELECTOR != AI ROUTER
# ============================================================================
#
# The word "selector" here means:
#
#
#       select evidence belonging to a path
#
#
# It does NOT mean:
#
#
#       select an AI service
#
#
# or:
#
#
#       select a network path for traffic
#
#
# ============================================================================
#
#
#       EVIDENCE SELECTION != ROUTE SELECTION
#
#
# ============================================================================


# ============================================================================
# WRONG-PATH EVIDENCE
# ============================================================================
#
# Suppose evidence collection contains:
#
#
#       vpn-a
#       vpn-b
#       internet-a
#
#
# When assessing:
#
#
#       vpn-a
#
#
# only evidence belonging to:
#
#
#       vpn-a
#
#
# participates.
#
#
# ============================================================================
#
#
#       COLLECTION MEMBERSHIP
#           !=
#       ASSESSMENT RELEVANCE
#
#
# ============================================================================


# ============================================================================
# STALE EVIDENCE IS FILTERED, NOT DESTROYED
# ============================================================================
#
# CurrentPathEvidenceSelector returns only currently usable evidence.
#
#
# It does NOT mutate:
#
#
#       all_path_evidence
#
#
# Therefore the larger NetworkAssessmentResult can still preserve historical
# evidence for:
#
#
#       telemetry
#
#       audit
#
#       incident reconstruction
#
#       troubleshooting
#
#
# ============================================================================
#
#
#       EXCLUDE FROM CURRENT ASSESSMENT
#           !=
#       DELETE FROM HISTORY
#
#
# ============================================================================


# ============================================================================
# PER-PATH ASSESSMENT COORDINATOR
# ============================================================================
#
# Part III-B now has enough behavior to justify a small coordinator around:
#
#
#       evidence selection
#
#       path assessment
#
#
# This prevents NetworkOrchestrator from needing to know the mechanics of
# freshness filtering.
#
#
# ============================================================================


class CurrentPathAssessmentEvaluator:
    """
    Produce a current assessment for one path instance.

    This class coordinates:

        current-evidence selection

        path-state assessment


    It does not:

        collect infrastructure evidence

        authorize paths

        choose between paths

        evaluate AI workload suitability
    """

    def __init__(
        self,
        evidence_selector: CurrentPathEvidenceSelector,
        path_assessment_evaluator: NetworkPathAssessmentEvaluator,
    ) -> None:

        self._evidence_selector = evidence_selector
        self._path_assessment_evaluator = path_assessment_evaluator

    def assess(
        self,
        path: NetworkPathIdentity,
        evidence: list[NetworkPathEvidence],
        assessed_at: datetime,
    ) -> NetworkPathAssessment:
        """
        Assess one specific path using currently usable evidence.
        """

        current_evidence = self._evidence_selector.select(
            path=path,
            evidence=evidence,
            assessed_at=assessed_at,
        )

        return self._path_assessment_evaluator.assess_path(
            source_id=path.source_id,
            destination_id=path.destination_id,
            path_id=path.path_id,
            path_type=path.path_type,
            evidence=current_evidence,
            assessed_at=assessed_at,
        )


# ============================================================================
# THE ORCHESTRATION LAYER JUST GOT CLEANER
# ============================================================================
#
# Without CurrentPathAssessmentEvaluator:
#
#
#       NetworkOrchestrator
#
# would need to know:
#
#
#       how to match evidence
#
#       how to check freshness
#
#       how to call the path evaluator
#
#
# With it:
#
#
#       NetworkOrchestrator
#
# can eventually say:
#
#
#       assessment = current_path_assessor.assess(
#           path=path,
#           evidence=all_path_evidence,
#           assessed_at=assessed_at,
#       )
#
#
# ============================================================================
#
#
#       ORCHESTRATOR COORDINATES.
#
#       SPECIALIZED COMPONENTS OWN RULES.
#
#
# ============================================================================


# ============================================================================
# NO CURRENT EVIDENCE
# ============================================================================
#
# Suppose:
#
#
#       vpn-a
#
#
# is in expected path inventory.
#
#
# But:
#
#
#       no observer produced evidence
#
#
# or:
#
#
#       every observation is stale.
#
#
# CurrentPathEvidenceSelector returns:
#
#
#       []
#
#
# The path assessment evaluator should conclude:
#
#
#       UNKNOWN
#
#
# ============================================================================
#
#
#       NO CURRENT EVIDENCE != UNAVAILABLE
#
#
# ============================================================================


# ============================================================================
# MULTIPLE CURRENT OBSERVATIONS
# ============================================================================
#
# Suppose:
#
#
#       observer-a
#           vpn-a AVAILABLE
#
#
#       observer-b
#           vpn-a AVAILABLE
#
#
# Both observations may participate in assessment.
#
#
# ============================================================================
#
# But suppose:
#
#
#       observer-a
#           vpn-a AVAILABLE
#
#
#       observer-b
#           vpn-a UNAVAILABLE
#
#
# This is an epistemic disagreement.
#
#
# Do NOT automatically call the path:
#
#
#       DEGRADED
#
#
# ============================================================================
#
#
#       DISAGREEMENT != DEGRADATION
#
#
# ============================================================================


# ============================================================================
# WHY DEGRADED MUST REMAIN OPERATIONAL
# ============================================================================
#
# DEGRADED should mean something like:
#
#
#       connectivity exists
#
#       but operational quality/capacity is impaired
#
#
# It should not become:
#
#
#       "We don't know because observers disagree."
#
#
# ============================================================================
#
#
#       DEGRADED = OPERATIONAL CONDITION
#
#       UNKNOWN = EPISTEMIC CONDITION
#
#
# ============================================================================
#
# Mixing those concepts would destroy telemetry value.
#
#
# ============================================================================


# ============================================================================
# OBSERVER DISAGREEMENT
# ============================================================================
#
# The underlying NetworkPathAssessmentEvaluator should eventually understand
# multi-observer evidence.
#
#
# A conservative initial rule may be:
#
#
#       no evidence
#           -> UNKNOWN
#
#
#       all AVAILABLE
#           -> AVAILABLE
#
#
#       all DEGRADED
#           -> DEGRADED
#
#
#       all UNAVAILABLE
#           -> UNAVAILABLE
#
#
#       conflicting operational states
#           -> UNKNOWN
#
#
# But this must be implemented in:
#
#
#       NetworkPathAssessmentEvaluator
#
#
# not:
#
#
#       NetworkOrchestrator
#
#
# ============================================================================
#
#
#       ORCHESTRATION != EVIDENCE FUSION
#
#
# ============================================================================


# ============================================================================
# IMPORTANT:
# DIFFERENT EVIDENCE TYPES MAY NOT CONFLICT
# ============================================================================
#
# Imagine:
#
#
#       SD-WAN controller:
#           DEGRADED
#
#
#       TCP probe:
#           AVAILABLE
#
#
# Are they contradictory?
#
#
# Not necessarily.
#
#
# The controller may be saying:
#
#
#       packet loss exceeds preferred SLA
#
#
# while the probe says:
#
#
#       TCP connectivity succeeds
#
#
# ============================================================================
#
#
#       DIFFERENT OBSERVATIONS
#           !=
#       SAME SEMANTIC CLAIM
#
#
# ============================================================================


# ============================================================================
# THIS CREATES FUTURE PRESSURE FOR evidence_type
# ============================================================================
#
# Mature NetworkPathEvidence may eventually need:
#
#
#       observer_id
#
#       evidence_type
#
#
# Example:
#
#
#       observer_id:
#           cisco-sdwan-tokyo
#
#
#       evidence_type:
#           CONTROL_PLANE
#
#
# versus:
#
#
#       observer_id:
#           synthetic-probe-01
#
#
#       evidence_type:
#           DATA_PLANE
#
#
# But we do not add the enum merely because we can imagine it.
#
#
# ============================================================================
#
#
#       DOMAIN PRESSURE CREATES MODELS.
#
#
# ============================================================================


# ============================================================================
# MEASUREMENTS
# ============================================================================
#
# Network observations may eventually include quantitative measurements:
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
#
# These are useful facts.
#
#
# They are not themselves assessments.
#
#
# ============================================================================
#
#
#       MEASUREMENT != ASSESSMENT
#
#
# ============================================================================


# ============================================================================
# FUTURE NETWORK PATH MEASUREMENTS
# ============================================================================
#
# A future model may look like:
#
#
#   class NetworkPathMeasurements(Agent11BaseModel):
#
#       latency_ms: float | None
#
#       jitter_ms: float | None
#
#       packet_loss_percent: float | None
#
#       available_bandwidth_mbps: float | None
#
#
# But Part III-B deliberately does not activate this model yet.
#
#
# Why?
#
#
# Because a measurement model is useful only after we establish:
#
#
#       which observers provide which measurements
#
#       which units are canonical
#
#       which values are instantaneous
#
#       which values are aggregates
#
#       over what measurement window
#
#       which measurements influence state
#
#
# ============================================================================
#
#
#       METRIC DUMPING != DOMAIN MODELING
#
#
# ============================================================================


# ============================================================================
# LATENCY EXAMPLE
# ============================================================================
#
# Suppose:
#
#
#       latency_ms = 120
#
#
# What state is the path?
#
#
# We cannot answer from the number alone.
#
#
# A configured rule might later say:
#
#
#       <= 100 ms
#           AVAILABLE
#
#
#       100-250 ms
#           DEGRADED
#
#
#       > 250 ms
#           UNAVAILABLE
#
#
# But those thresholds are domain configuration.
#
#
# They are not universal truths.
#
#
# ============================================================================
#
#
#       MEASUREMENT != THRESHOLD
#
#
# ============================================================================


# ============================================================================
# THRESHOLD != POLICY
# ============================================================================
#
# Even if:
#
#
#       latency is excellent
#
#
# the path may still be:
#
#
#       prohibited
#
#
# for sensitive data.
#
#
# ============================================================================
#
#
#       FAST != AUTHORIZED
#
#
# ============================================================================


# ============================================================================
# PATH STATE != WORKLOAD SUITABILITY
# ============================================================================
#
# Suppose:
#
#
#       vpn-a = DEGRADED
#
#
# That does not automatically mean:
#
#
#       unusable
#
#
# for every AI request.
#
#
# A long-running asynchronous security analysis may tolerate a path that an
# interactive workload would not.
#
#
# ============================================================================
#
#
#       DEGRADED != UNIVERSALLY UNUSABLE
#
#
# ============================================================================


# ============================================================================
# WHERE WORKLOAD SUITABILITY BELONGS
# ============================================================================
#
# Eventually candidate evaluation may combine:
#
#
#       path assessment
#
#       workload requirements
#
#       service capability
#
#       policy
#
#
# NetworkPathAssessment itself should not know:
#
#
#       ReasoningLevel
#
#       AIRequest
#
#       model capability
#
#
# ============================================================================
#
#
#       NETWORK FACT != WORKLOAD DECISION
#
#
# ============================================================================


# ============================================================================
# CONNECTIVITY != CAPACITY
# ============================================================================
#
# A path may successfully pass traffic while having insufficient capacity
# for a particular workload.
#
#
# ============================================================================
#
#
#       CONNECTED != ADEQUATELY PROVISIONED
#
#
# ============================================================================
#
# This may eventually produce separate capacity evidence rather than
# overloading:
#
#
#       NetworkPathState
#
#
# ============================================================================


# ============================================================================
# CURRENT PATH ASSESSMENT != HISTORICAL PATH ASSESSMENT
# ============================================================================
#
# The same evidence can be replayed at different assessment times.
#
#
# Example:
#
#
#       observation:
#           12:00 AVAILABLE
#
#
# Assessment:
#
#
#       12:00:10
#           AVAILABLE
#
#
# Replay:
#
#
#       13:00
#           UNKNOWN
#
#
# because the evidence is now stale.
#
#
# ============================================================================
#
#
#       SAME HISTORY
#           CAN SUPPORT
#       DIFFERENT CURRENT CONCLUSIONS
#           AT DIFFERENT TIMES
#
#
# ============================================================================


# ============================================================================
# INCIDENT RECONSTRUCTION
# ============================================================================
#
# Explicit:
#
#
#       observed_at
#
#       assessed_at
#
# allows Agent 11 telemetry to answer:
#
#
#       What was observed?
#
#       When was it observed?
#
#       What evidence was considered current?
#
#       What conclusion was made?
#
#       When was that conclusion made?
#
#
# This becomes important when investigating:
#
#
#       network incidents
#
#       routing decisions
#
#       fallback behavior
#
#       security enforcement
#
#
# ============================================================================


# ============================================================================
# CLOCK SKEW
# ============================================================================
#
# Future timestamps may indicate:
#
#
#       observer clock drift
#
#       ingestion timestamp differences
#
#       telemetry delay
#
#
# Mature evidence may eventually distinguish:
#
#
#       observed_at
#
#       received_at
#
#
# ============================================================================
#
#
#       EVENT TIME != INGESTION TIME
#
#
# ============================================================================
#
# Do not add received_at until telemetry behavior requires it.
#
#
# ============================================================================


# ============================================================================
# FRESHNESS AND TRUST
# ============================================================================
#
# Fresh evidence is not necessarily trustworthy.
#
#
# Trusted evidence is not necessarily fresh.
#
#
# ============================================================================
#
#
#       FRESH != TRUSTED
#
#       TRUSTED != FRESH
#
#
# ============================================================================


# ============================================================================
# FRESHNESS AND CORRECTNESS
# ============================================================================
#
# A five-second-old observation can still be wrong.
#
#
# ============================================================================
#
#
#       FRESH != CORRECT
#
#
# ============================================================================


# ============================================================================
# MULTIPLE OBSERVERS AND INDEPENDENCE
# ============================================================================
#
# Suppose:
#
#
#       observer-a
#           AVAILABLE
#
#
#       observer-b
#           AVAILABLE
#
#
# Does that give us two independent confirmations?
#
#
# Not necessarily.
#
#
# Both observers may consume:
#
#
#       the same controller API
#
#
#       the same telemetry pipeline
#
#
#       the same upstream probe
#
#
# ============================================================================
#
#
#       OBSERVER COUNT != INDEPENDENT EVIDENCE COUNT
#
#
# ============================================================================


# ============================================================================
# PROVENANCE WITHOUT TOPOLOGY GRAPH
# ============================================================================
#
# We do not need to build a giant evidence-dependency graph yet.
#
#
# It is enough to preserve:
#
#
#       observer identity
#
#
# and avoid claiming independence that we cannot prove.
#
#
# ============================================================================
#
#
#       DO NOT MODEL WHAT YOU CANNOT YET USE CORRECTLY.
#
#
# ============================================================================


# ============================================================================
# NO CONFIDENCE FLOAT
# ============================================================================
#
# Still no:
#
#
#       confidence = 0.81
#
#
# because:
#
#
#       fresh
#
#       trusted
#
#       independent
#
#       consistent
#
#       operational
#
#
# are separate dimensions.
#
#
# Compressing all of them into one decimal would hide useful information.
#
#
# ============================================================================
#
#
#       STRUCTURED UNCERTAINTY > MYSTERY NUMBER
#
#
# ============================================================================


# ============================================================================
# FAIL CLOSED
# ============================================================================
#
# Candidate evaluation may later fail closed when path state is:
#
#
#       UNKNOWN
#
#
# But the network subsystem must still report:
#
#
#       UNKNOWN
#
#
# rather than rewriting it:
#
#
#       UNAVAILABLE
#
#
# ============================================================================
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ============================================================================


# ============================================================================
# EXAMPLE:
# STALE PRIVATE PATH + CURRENT INTERNET PATH
# ============================================================================
#
#
#       private-link-a
#
#           last observation:
#               AVAILABLE
#
#           age:
#               10 minutes
#
#           permitted freshness:
#               30 seconds
#
#
#       internet-a
#
#           last observation:
#               AVAILABLE
#
#           age:
#               5 seconds
#
#
# Current path assessments:
#
#
#       private-link-a
#           UNKNOWN
#
#
#       internet-a
#           AVAILABLE
#
#
# ============================================================================
# IMPORTANT
# ============================================================================
#
# Network still does NOT say:
#
#
#       "Use Internet."
#
#
# It says:
#
#
#       "Current evidence establishes Internet availability.
#
#        Current evidence does not establish PrivateLink availability."
#
#
# Policy and candidate evaluation decide what happens next.
#
#
# ============================================================================


# ============================================================================
# EXAMPLE:
# TWO STALE AVAILABLE OBSERVATIONS
# ============================================================================
#
#
#       observer-a:
#           vpn-a AVAILABLE at 11:00
#
#
#       observer-b:
#           vpn-a AVAILABLE at 11:01
#
#
#       assessment:
#           12:00
#
#
# Both may be historically valid.
#
#
# Neither may be usable for current state.
#
#
# Result:
#
#
#       vpn-a UNKNOWN
#
#
# ============================================================================
#
#
#       MORE OLD EVIDENCE
#           !=
#       CURRENT KNOWLEDGE
#
#
# ============================================================================


# ============================================================================
# EXAMPLE:
# CURRENT OBSERVER DISAGREEMENT
# ============================================================================
#
#
#       observer-a:
#           vpn-a AVAILABLE
#
#
#       observer-b:
#           vpn-a UNAVAILABLE
#
#
# both current
#
#
# Conservative result:
#
#
#       UNKNOWN
#
#
# not:
#
#
#       DEGRADED
#
#
# ============================================================================
#
#
#       UNCERTAINTY != DEGRADATION
#
#
# ============================================================================


# ============================================================================
# EXAMPLE:
# CURRENT DEGRADED EVIDENCE
# ============================================================================
#
#
#       observer-a:
#           vpn-a DEGRADED
#
#
#       observer-b:
#           vpn-a DEGRADED
#
#
# Current result:
#
#
#       DEGRADED
#
#
# ============================================================================
#
# This is operational degradation, not uncertainty.
#
#
# ============================================================================


# ============================================================================
# EXAMPLE:
# NO OBSERVERS
# ============================================================================
#
# Inventory says:
#
#
#       vpn-a expected
#
#
# Evidence:
#
#
#       []
#
#
# Current assessment:
#
#
#       UNKNOWN
#
#
# ============================================================================
#
#
#       EXPECTED BUT UNOBSERVED
#           !=
#       UNAVAILABLE
#
#
# ============================================================================


# ============================================================================
# TEST MATRIX
# ============================================================================
#
# TEST 1
#
# Evidence age:
#       5 seconds
#
# maximum_age:
#       30 seconds
#
# Expected:
#       fresh
#
#
# ---------------------------------------------------------------------------
#
# TEST 2
#
# Evidence age:
#       60 seconds
#
# maximum_age:
#       30 seconds
#
# Expected:
#       stale
#
#
# ---------------------------------------------------------------------------
#
# TEST 3
#
# Evidence timestamp:
#       future relative to assessed_at
#
# Expected:
#       not fresh
#
#
# ---------------------------------------------------------------------------
#
# TEST 4
#
# maximum_age:
#       negative
#
# Expected:
#       ValueError
#
#
# ---------------------------------------------------------------------------
#
# TEST 5
#
# Evidence:
#       correct path_id
#       correct source
#       correct destination
#       correct type
#       fresh
#
# Expected:
#       selected
#
#
# ---------------------------------------------------------------------------
#
# TEST 6
#
# Evidence:
#       wrong path_id
#
# Expected:
#       excluded
#
#
# ---------------------------------------------------------------------------
#
# TEST 7
#
# Evidence:
#       correct path_id
#       wrong source
#
# Expected:
#       excluded
#
#
# ---------------------------------------------------------------------------
#
# TEST 8
#
# Evidence:
#       correct path_id
#       wrong destination
#
# Expected:
#       excluded
#
#
# ---------------------------------------------------------------------------
#
# TEST 9
#
# Evidence:
#       correct path_id
#       wrong path_type
#
# Expected:
#       excluded
#
#
# ---------------------------------------------------------------------------
#
# TEST 10
#
# Evidence:
#       correct identity
#       stale
#
# Expected:
#       excluded from current assessment
#
#       historical evidence preserved elsewhere
#
#
# ---------------------------------------------------------------------------
#
# TEST 11
#
# Expected path:
#       vpn-a
#
# Current evidence:
#       []
#
# Expected assessment:
#       UNKNOWN
#
#
# ---------------------------------------------------------------------------
#
# TEST 12
#
# Two current observations:
#       AVAILABLE
#       AVAILABLE
#
# Expected:
#       AVAILABLE
#
#
# ---------------------------------------------------------------------------
#
# TEST 13
#
# Two current observations:
#       UNAVAILABLE
#       UNAVAILABLE
#
# Expected:
#       UNAVAILABLE
#
#
# ---------------------------------------------------------------------------
#
# TEST 14
#
# Two current observations:
#       AVAILABLE
#       UNAVAILABLE
#
# Expected:
#       UNKNOWN
#
# assuming conservative same-semantic evidence fusion
#
#
# ---------------------------------------------------------------------------
#
# TEST 15
#
# Historical evidence:
#       AVAILABLE
#
# Current evidence:
#       none
#
# Expected:
#       historical evidence remains AVAILABLE
#
#       current assessment UNKNOWN
#
#
# ---------------------------------------------------------------------------
#
# TEST 16
#
# Network assessment:
#       Internet AVAILABLE
#
# Future policy:
#       Internet DENIED
#
# Expected from Part III-B:
#       Internet remains AVAILABLE
#
#
# ============================================================================


# ============================================================================
# PART III-B FINAL INVARIANTS
# ============================================================================
#
#
# TIME
# ----
#
#       TIME IS A DEPENDENCY
#
#       OBSERVED_AT = FACT
#
#       FRESHNESS = INTERPRETATION
#
#       OBSERVED_AT != FRESHNESS
#
#       EVIDENCE STATE != EVIDENCE FRESHNESS
#
#       FUTURE TIMESTAMP != VERY FRESH EVIDENCE
#
#       EVENT TIME != INGESTION TIME
#
#
# HISTORY
# -------
#
#       STALE != FALSE
#
#       STALE EVIDENCE != FALSE EVIDENCE
#
#       HISTORICAL EVIDENCE != CURRENTLY USABLE EVIDENCE
#
#       EXCLUDE FROM CURRENT ASSESSMENT != DELETE FROM HISTORY
#
#
# SELECTION
# ---------
#
#       COLLECTION MEMBERSHIP != ASSESSMENT RELEVANCE
#
#       EVIDENCE SELECTION != EVIDENCE INTERPRETATION
#
#       EVIDENCE SELECTION != ROUTE SELECTION
#
#
# ASSESSMENT
# ----------
#
#       NO CURRENT EVIDENCE != UNAVAILABLE
#
#       EXPECTED BUT UNOBSERVED != UNAVAILABLE
#
#       DISAGREEMENT != DEGRADATION
#
#       DEGRADED = OPERATIONAL CONDITION
#
#       UNKNOWN = EPISTEMIC CONDITION
#
#       ORCHESTRATION != EVIDENCE FUSION
#
#
# PROVENANCE
# ----------
#
#       DIFFERENT OBSERVATIONS != SAME SEMANTIC CLAIM
#
#       OBSERVER COUNT != INDEPENDENT EVIDENCE COUNT
#
#       FRESH != TRUSTED
#
#       TRUSTED != FRESH
#
#       FRESH != CORRECT
#
#
# MEASUREMENTS
# ------------
#
#       MEASUREMENT != ASSESSMENT
#
#       MEASUREMENT != THRESHOLD
#
#       THRESHOLD != POLICY
#
#       METRIC DUMPING != DOMAIN MODELING
#
#
# WORKLOADS
# ---------
#
#       PATH STATE != WORKLOAD SUITABILITY
#
#       DEGRADED != UNIVERSALLY UNUSABLE
#
#       CONNECTED != ADEQUATELY PROVISIONED
#
#       NETWORK FACT != WORKLOAD DECISION
#
#
# SECURITY
# --------
#
#       FAST != AUTHORIZED
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# UNCERTAINTY
# -----------
#
#       STRUCTURED UNCERTAINTY > MYSTERY NUMBER
#
#
# ARCHITECTURE
# ------------
#
#       DOMAIN PRESSURE CREATES MODELS
#
#       DO NOT MODEL WHAT YOU CANNOT YET USE CORRECTLY
#
#       CONFIGURATION DIFFERENCE
#           DOES NOT AUTOMATICALLY REQUIRE
#       DOMAIN COMPLEXITY
#
#
# ============================================================================
# FINAL PART III-B RULE
# ============================================================================
#
#
#       EVIDENCE TELLS US
#       WHAT WAS OBSERVED.
#
#
#       FRESHNESS TELLS US
#       WHETHER THAT OBSERVATION
#       IS CURRENT ENOUGH TO USE.
#
#
#       ASSESSMENT TELLS US
#       WHAT WE CURRENTLY CONCLUDE
#       ABOUT ONE SPECIFIC PATH.
#
#
#       NONE OF THOSE
#       TELLS US WHETHER
#       THE AI REQUEST
#       IS AUTHORIZED TO USE IT.
#
#
# ============================================================================
# END PART III-B
# ============================================================================

# ============================================================================
# network/orchestrator.py
#
# PART III-C
#
# SD-WAN, BGP CONVERGENCE, MULTI-CLOUD,
# PATH REALIZATION, FAILURE DOMAINS,
# AND AUTHORITY BOUNDARIES
# ============================================================================
#
# PURPOSE
# -------
#
# Part III-A established:
#
#       path identity
#       observer provenance
#
#
# Part III-B established:
#
#       freshness
#       current-evidence selection
#       per-path assessment
#
#
# Part III-C establishes how those abstractions survive:
#
#       SD-WAN
#
#       BGP convergence
#
#       dynamic failover
#
#       path drift
#
#       multi-cloud
#
#       shared failure domains
#
#       network automation
#
#
# ============================================================================
# CENTRAL RULE
# ============================================================================
#
#
#       NETWORK CONVERGENCE
#           !=
#       POLICY-COMPLIANT RECOVERY
#
#
# ============================================================================
#
# The network subsystem may correctly restore connectivity.
#
# Agent 11 may correctly refuse to use that connectivity.
#
#
# Both can be successful simultaneously.
#
#
# ============================================================================


from datetime import datetime

from ..models.network.assessment import NetworkAssessmentResult
from ..models.network.endpoint import NetworkEndpointEvidence
from ..models.network.path import (
    NetworkPathAssessment,
    NetworkPathEvidence,
    NetworkPathIdentity,
)
from ..models.network.route import RouteEvidence

from .endpoint import NetworkEndpointEvaluator
from .route import RouteEvidenceEvaluator

# These responsibilities were established in Parts III-A and III-B.
from .path import NetworkPathEvidenceCollector
from .path_inventory import NetworkPathInventory
from .freshness import CurrentPathAssessmentEvaluator


# ============================================================================
# NETWORK ORCHESTRATOR
# ============================================================================


class NetworkOrchestrator:
    """
    Coordinate enterprise network knowledge for Agent 11.

    Part III-C does not turn NetworkOrchestrator into:

        a BGP controller

        an SD-WAN controller

        a cloud network manager

        a policy engine

        an AI router

        a remediation engine


    It remains a coordinator.

    Its responsibility is to preserve enough normalized network knowledge
    for downstream systems to make correct decisions.
    """

    def __init__(
        self,
        endpoint_evaluator: NetworkEndpointEvaluator,
        route_evidence_evaluator: RouteEvidenceEvaluator,
        path_inventory: NetworkPathInventory,
        path_evidence_collector: NetworkPathEvidenceCollector,
        current_path_assessor: CurrentPathAssessmentEvaluator,
    ) -> None:

        self._endpoint_evaluator = endpoint_evaluator
        self._route_evidence_evaluator = route_evidence_evaluator
        self._path_inventory = path_inventory
        self._path_evidence_collector = path_evidence_collector
        self._current_path_assessor = current_path_assessor

    def assess_network(
        self,
        source_id: str,
        destination_id: str,
        assessed_at: datetime,
    ) -> NetworkAssessmentResult:
        """
        Produce a structured enterprise network assessment.

        Pipeline:

            DISCOVER EXPECTED TOPOLOGY
                    |
                    v
            OBSERVE ENDPOINT
                    |
                    v
            OBSERVE ROUTING
                    |
                    v
            OBSERVE PATHS
                    |
                    v
            ASSESS EACH PATH
                    |
                    v
            PRESERVE NETWORK KNOWLEDGE
                    |
                    v
            NetworkAssessmentResult


        No AI authorization occurs here.
        """

        # --------------------------------------------------------------------
        # Stage 1: ENDPOINT
        # --------------------------------------------------------------------

        endpoint_evidence: NetworkEndpointEvidence = (
            self._endpoint_evaluator.get_endpoint_evidence(
                destination_id=destination_id,
            )
        )

        # --------------------------------------------------------------------
        # Stage 2: ROUTING / CONTROL PLANE
        # --------------------------------------------------------------------
        #
        # Route evidence may come from:
        #
        #       BGP
        #       static routing
        #       connected routes
        #       cloud routing systems
        #
        # But the orchestrator receives normalized RouteEvidence.
        #
        # It does not parse vendor route tables.
        #
        # --------------------------------------------------------------------

        route_evidence: list[RouteEvidence] = (
            self._route_evidence_evaluator.get_route_evidence(
                source_id=source_id,
                destination_id=destination_id,
            )
        )

        # --------------------------------------------------------------------
        # Stage 3: EXPECTED PATH INVENTORY
        # --------------------------------------------------------------------

        expected_paths: list[NetworkPathIdentity] = (
            self._path_inventory.get_paths(
                source_id=source_id,
                destination_id=destination_id,
            )
        )

        # --------------------------------------------------------------------
        # Stage 4: PATH OBSERVATION
        # --------------------------------------------------------------------
        #
        # One path may produce multiple observations.
        #
        # Example:
        #
        #       vpn-tokyo-a
        #
        #           SD-WAN controller
        #               DEGRADED
        #
        #           synthetic probe
        #               AVAILABLE
        #
        #
        # Both observations are preserved.
        #
        # --------------------------------------------------------------------

        path_evidence: list[NetworkPathEvidence] = []

        for path in expected_paths:

            observations = self._path_evidence_collector.collect(
                path=path,
            )

            path_evidence.extend(observations)

        # --------------------------------------------------------------------
        # Stage 5: CURRENT PER-PATH ASSESSMENT
        # --------------------------------------------------------------------
        #
        # III-B owns:
        #
        #       identity matching
        #       freshness
        #       evidence selection
        #       path-state interpretation
        #
        #
        # Therefore the enterprise orchestrator does not reproduce those
        # rules.
        #
        # --------------------------------------------------------------------

        path_assessments: list[NetworkPathAssessment] = []

        for path in expected_paths:

            assessment = self._current_path_assessor.assess(
                path=path,
                evidence=path_evidence,
                assessed_at=assessed_at,
            )

            path_assessments.append(assessment)

        # --------------------------------------------------------------------
        # Stage 6: PACKAGE
        # --------------------------------------------------------------------
        #
        # Preserve:
        #
        #       expected topology
        #
        #       endpoint evidence
        #
        #       route evidence
        #
        #       raw normalized path evidence
        #
        #       current per-path assessments
        #
        #
        # Do NOT collapse:
        #
        #       private-link-a = UNAVAILABLE
        #       internet-a     = AVAILABLE
        #
        # into:
        #
        #       NETWORK = AVAILABLE
        #
        #
        # Downstream policy may care WHICH path is available.
        #
        # --------------------------------------------------------------------

        return NetworkAssessmentResult(
            source_id=source_id,
            destination_id=destination_id,
            endpoint_evidence=endpoint_evidence,
            route_evidence=route_evidence,
            expected_paths=expected_paths,
            path_evidence=path_evidence,
            path_assessments=path_assessments,
            assessed_at=assessed_at,
        )


# ============================================================================
# WHY III-C DOES NOT MAKE NetworkOrchestrator BIGGER
# ============================================================================
#
# This is one of the most important architectural outcomes.
#
#
# SEIR-II adds:
#
#       BGP
#
#       SD-WAN
#
#       cloud networking
#
#       multiple paths
#
#       multiple observers
#
#       freshness
#
#       failover
#
#
# Yet NetworkOrchestrator itself remains small.
#
#
# Why?
#
#
#       SOURCES OBSERVE
#
#       ADAPTERS NORMALIZE
#
#       EVALUATORS INTERPRET
#
#       ORCHESTRATORS COORDINATE
#
#
# ============================================================================
#
#
#       SYSTEM COMPLEXITY
#       DOES NOT REQUIRE
#       ORCHESTRATOR COMPLEXITY.
#
#
# ============================================================================


# ============================================================================
# SD-WAN
# ============================================================================
#
# An SD-WAN system may dynamically steer traffic among:
#
#
#       MPLS
#
#       private connectivity
#
#       VPN
#
#       broadband Internet
#
#       cellular
#
#       cloud interconnect
#
#
# Agent 11 does not reproduce the SD-WAN controller.
#
#
# Instead:
#
#
#       SD-WAN CONTROLLER
#               |
#               v
#       vendor adapter
#               |
#               v
#       normalized path evidence
#               |
#               v
#       Agent 11 network subsystem
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
# SD-WAN FAILOVER
# ============================================================================
#
# Consider:
#
#
#       private-link-a
#           AVAILABLE
#
#               |
#               X
#             FAILS
#
#               |
#               v
#
#       SD-WAN CONTROLLER
#
#               |
#               v
#
#       internet-a
#           AVAILABLE
#
#
# From the network controller's perspective:
#
#
#       CONNECTIVITY RESTORED
#
#
# This may be entirely correct.
#
#
# ============================================================================
#
#
#       NETWORK FAILOVER = SUCCESS
#
#
# does NOT imply:
#
#
#       AI REQUEST MAY USE NEW PATH
#
#
# ============================================================================


# ============================================================================
# POLICY-COMPLIANT RECOVERY
# ============================================================================
#
# Imagine the request contains:
#
#
#       E9
#
#
# and future path-aware policy says:
#
#
#       PRIVATE_LINK
#           ALLOW
#
#
#       INTERNET
#           DENY
#
#
# After SD-WAN failover:
#
#
#       NETWORK:
#           internet-a AVAILABLE
#
#
#       POLICY:
#           Internet DENIED
#
#
#       CANDIDATE EVALUATION:
#           no compliant path
#
#
#       AI ROUTING:
#           NO VIABLE ROUTE
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
# DO NOT BLAME THE NETWORK
# ============================================================================
#
# In that scenario the network subsystem should NOT rewrite:
#
#
#       internet-a AVAILABLE
#
#
# into:
#
#
#       internet-a UNAVAILABLE
#
#
# merely because AI policy prohibits its use.
#
#
# ============================================================================
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ============================================================================


# ============================================================================
# PATH REALIZATION
# ============================================================================
#
# Enterprise networking introduces a subtle distinction:
#
#
#       EXPECTED PATH
#
#       OBSERVED PATH
#
#       REALIZED PATH
#
#
# Example:
#
#
# Expected:
#
#       private-link-a
#
#
# Observed inventory:
#
#       private-link-a
#       internet-a
#
#
# Realized forwarding:
#
#       internet-a
#
#
# ============================================================================
#
#
#       EXPECTED PATH != REALIZED PATH
#
#
# ============================================================================


# ============================================================================
# PATH DRIFT
# ============================================================================
#
# If the network was expected to use:
#
#
#       private-link-a
#
#
# but is actually using:
#
#
#       internet-a
#
#
# connectivity may still be:
#
#
#       AVAILABLE
#
#
# Yet the network has drifted from intended topology.
#
#
# ============================================================================
#
#
#       PATH DRIFT != PATH FAILURE
#
#
# ============================================================================


# ============================================================================
# DO WE NEED RealizedPath YET?
# ============================================================================
#
# Not necessarily.
#
#
# III-C identifies real domain pressure for it.
#
#
# But before creating:
#
#
#       RealizedNetworkPath
#
#
# we should first determine:
#
#
#       which adapters can establish realized forwarding
#
#       whether realization is per-flow
#
#       whether it changes during an assessment
#
#       how ECMP is represented
#
#       how SD-WAN reports active forwarding
#
#
# ============================================================================
#
#
#       KNOWN FUTURE NEED
#           !=
#       CURRENTLY EARNED MODEL
#
#
# ============================================================================


# ============================================================================
# BGP
# ============================================================================
#
# BGP belongs to routing/control-plane evidence.
#
#
# It does NOT belong in NetworkPathType.
#
#
# ============================================================================
#
#
#       PATH TYPE != ROUTING PROTOCOL
#
#
# ============================================================================
#
# Correct conceptual separation:
#
#
#       NetworkPathType
#
#           VPN
#           PRIVATE_LINK
#           INTERNET
#           SD_WAN
#
#
#       NetworkRoutingProtocol
#
#           BGP
#           STATIC
#           CONNECTED
#           OSPF
#
#
# ============================================================================


# ============================================================================
# BGP ROUTE PRESENT
# ============================================================================
#
# Suppose:
#
#
#       route:
#           PRESENT
#
#
#       protocol:
#           BGP
#
#
# This means the observed routing system reports a qualifying route.
#
#
# It does NOT prove:
#
#
#       forwarding succeeds
#
#       return traffic succeeds
#
#       firewall permits traffic
#
#       TLS succeeds
#
#       inference service responds
#
#
# ============================================================================
#
#
#       BGP ROUTE PRESENT != END-TO-END CONNECTIVITY
#
#
# ============================================================================


# ============================================================================
# BGP ABSENT != BGP UNKNOWN
# ============================================================================
#
# ABSENT:
#
#       successful observation established
#       that the qualifying route is absent
#
#
# UNKNOWN:
#
#       route state could not be established
#
#
# ============================================================================
#
#
#       NEGATIVE OBSERVATION
#           !=
#       FAILED OBSERVATION
#
#
# ============================================================================


# ============================================================================
# BGP CONVERGENCE
# ============================================================================
#
# Example:
#
#
#       Route A withdrawn
#
#               |
#               v
#
#       BGP convergence
#
#               |
#               v
#
#       Route B selected
#
#               |
#               v
#
#       forwarding resumes
#
#
# Network success:
#
#
#       YES
#
#
# AI authorization:
#
#
#       NOT YET ANSWERED
#
#
# ============================================================================


# ============================================================================
# BGP BEST PATH != AI BEST ROUTE
# ============================================================================
#
# BGP may select based upon:
#
#
#       LOCAL_PREF
#
#       AS_PATH
#
#       origin
#
#       MED
#
#       eBGP/iBGP rules
#
#       IGP cost
#
#
# Agent 11 may select based upon:
#
#
#       policy permission
#
#       model capability
#
#       service availability
#
#       network viability
#
#       later optimization
#
#
# ============================================================================
#
#
#       BGP LOCAL_PREF != AI ROUTING PREFERENCE
#
#
# ============================================================================


# ============================================================================
# NO BGP INTERNALS IN AIRouter
# ============================================================================
#
# AIRouter should never need:
#
#
#       AS_PATH
#
#       MED
#
#       LOCAL_PREF
#
#       NEXT_HOP
#
#       BGP communities
#
#
# AIRouter receives:
#
#
#       RoutingCandidate
#
#
# ============================================================================
#
#
#       INFRASTRUCTURE DETAIL
#       SHOULD NOT LEAK
#       INTO AI SELECTION.
#
#
# ============================================================================


# ============================================================================
# MULTI-CLOUD
# ============================================================================
#
# Enterprise topology may look like:
#
#
#                         Agent 11
#                            |
#          +-----------------+-----------------+
#          |                 |                 |
#          v                 v                 v
#         AWS              Azure              GCP
#          |                 |                 |
#          v                 v                 v
#      Deployment A      Deployment B      Deployment C
#
#                            |
#                            +
#                            |
#                            v
#                           OCI
#
#
# plus:
#
#
#                       ON-PREMISES
#
#
# ============================================================================


# ============================================================================
# CLOUD PROVIDER != ROUTING DOMAIN
# ============================================================================
#
# Agent 11 routing domain:
#
#
#       COMPANY_CLOUD_LLM
#
#
# may eventually contain deployments in:
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
# ============================================================================
#
#
#       COMPANY_CLOUD_LLM
#       IS NOT
#       "AWS LLM"
#
#
# ============================================================================


# ============================================================================
# DEPLOYMENT LOCATION != AUTHORIZATION
# ============================================================================
#
# Knowing:
#
#
#       deployment is in Azure
#
#
# does not tell us:
#
#
#       whether E9 may use it
#
#
# ============================================================================
#
#
#       LOCATION != AUTHORIZATION
#
#
# ============================================================================


# ============================================================================
# CLOUD PROVIDER != PATH TYPE
# ============================================================================
#
# A destination in Azure might be reached through:
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
# A destination in GCP might also be reached through:
#
#
#       INTERNET
#
#       VPN
#
#       PRIVATE connectivity
#
#       SD_WAN
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
# MULTI-CLOUD != RESILIENCE
# ============================================================================
#
# Suppose:
#
#
#       deployment-a = Azure
#
#       deployment-b = GCP
#
#
# Are they independent?
#
#
# Maybe.
#
#
# But both may depend upon:
#
#
#       same corporate DNS
#
#       same identity provider
#
#       same SD-WAN controller
#
#       same office firewall
#
#       same carrier
#
#       same transit hub
#
#
# ============================================================================
#
#
#       DIFFERENT CLOUDS != INDEPENDENT FAILURE
#
#
# ============================================================================


# ============================================================================
# FAILURE DOMAINS
# ============================================================================
#
# III-C establishes a requirement to eventually reason about:
#
#
#       router
#
#       firewall
#
#       carrier
#
#       tunnel concentrator
#
#       cloud region
#
#       availability zone
#
#       transit gateway
#
#       identity provider
#
#       DNS dependency
#
#       shared physical infrastructure
#
#
# ============================================================================
#
#
#       PATH COUNT != FAILURE-DOMAIN COUNT
#
#
# ============================================================================


# ============================================================================
# TWO VPNs
# ============================================================================
#
# Example:
#
#
#       vpn-a
#           carrier = Carrier X
#
#
#       vpn-b
#           carrier = Carrier X
#
#
# These are:
#
#
#       two path instances
#
#
# but possibly:
#
#
#       one carrier failure domain
#
#
# ============================================================================
#
#
#       MULTI-PATH != RESILIENCE
#
#
# ============================================================================


# ============================================================================
# DO NOT CREATE FailureDomain YET
# ============================================================================
#
# We now know the concept matters.
#
#
# But we still do not have enough concrete behavior to decide whether the
# mature model should represent:
#
#
#       hierarchical domains
#
#       dependency edges
#
#       shared-resource IDs
#
#       provider-defined domains
#
#       physical domains
#
#       logical domains
#
#
# ============================================================================
#
#
#       DOMAIN PRESSURE HAS ARRIVED.
#
#       MODEL SHAPE HAS NOT.
#
#
# ============================================================================
#
# Document the pressure.
#
# Do not invent the ontology prematurely.
#
#
# ============================================================================


# ============================================================================
# SIMULTANEOUS FAILURE
# ============================================================================
#
# Suppose:
#
#
#       vpn-a fails at 12:01
#
#       vpn-b fails at 12:01
#
#
# That may suggest shared cause.
#
#
# It does not prove shared cause.
#
#
# ============================================================================
#
#
#       CORRELATION != PROVEN DEPENDENCY
#
#
# ============================================================================


# ============================================================================
# CONTROL PLANE / DATA PLANE / APPLICATION
# ============================================================================
#
#
#       ROUTE
#       PRESENT
#          |
#          v
#       PACKETS
#       FORWARDED
#          |
#          v
#       TCP
#       CONNECTED
#          |
#          v
#       TLS
#       ESTABLISHED
#          |
#          v
#       APPLICATION
#       RESPONDS
#          |
#          v
#       AI SERVICE
#       PERFORMS WORK
#
#
# Every arrow is a possible failure boundary.
#
#
# ============================================================================
#
#
#       ROUTE SUCCESS != DATA-PLANE SUCCESS
#
#       DATA-PLANE SUCCESS != TRANSPORT SUCCESS
#
#       TRANSPORT SUCCESS != TLS SUCCESS
#
#       TLS SUCCESS != APPLICATION SUCCESS
#
#       APPLICATION SUCCESS != CORRECT AI OUTPUT
#
#
# ============================================================================


# ============================================================================
# SERVICE HEALTH REMAINS OUTSIDE NETWORK
# ============================================================================
#
# This is now even clearer.
#
#
# Network may establish:
#
#
#       endpoint PRESENT
#
#       path AVAILABLE
#
#
# while:
#
#
#       AI service = UNAVAILABLE
#
#
# ============================================================================
#
#
#       NETWORK AVAILABILITY
#           !=
#       SERVICE AVAILABILITY
#
#
# ============================================================================
#
# Therefore AI service health should not become the responsibility of this
# orchestrator merely because Kubernetes or cloud networking exposes some
# related telemetry.
#
#
# ============================================================================


# ============================================================================
# PATH-SPECIFIC POLICY
# ============================================================================
#
# III-C now proves that future policy may need more than:
#
#
#       classification
#       +
#       AIRoute
#
#
# It may eventually require:
#
#
#       classification
#       +
#       AIRoute
#       +
#       path
#
#
# Example:
#
#
#       E9
#       COMPANY_ONPREM_LLM
#       PRIVATE_LINK
#
#           ALLOW
#
#
#       E9
#       COMPANY_ONPREM_LLM
#       INTERNET
#
#           DENY
#
#
# ============================================================================
#
# But:
#
#
#       DO NOT MODIFY DataRoutePolicy HERE.
#
#
# Policy owns policy evolution.
#
#
# ============================================================================


# ============================================================================
# DESTINATION AUTHORIZED != EVERY PATH AUTHORIZED
# ============================================================================
#
# A service may be an approved destination.
#
#
# That does not imply:
#
#
#       every network path
#
#
# to that destination is approved for:
#
#
#       every data classification.
#
#
# ============================================================================


# ============================================================================
# CANDIDATE EVALUATION
# ============================================================================
#
# The eventual viability join now looks approximately like:
#
#
#       DATA POLICY ----------------------------+
#                                              |
#       PATH POLICY ----------------------------+
#                                              |
#       MODEL CAPABILITY -----------------------+
#                                              |
#       SERVICE AVAILABILITY -------------------+
#                                              |
#       NETWORK ASSESSMENT ---------------------+
#                                              |
#                                              v
#                                      CandidateEvaluator
#                                              |
#                                              v
#                                      RoutingCandidate
#                                              |
#                                              v
#                                          AIRouter
#
#
# ============================================================================
#
#
#       HARD CONSTRAINTS FIRST.
#
#       OPTIMIZATION SECOND.
#
#
# ============================================================================


# ============================================================================
# POLICY NEVER BECOMES A SCORE
# ============================================================================
#
# Do NOT calculate:
#
#
#       policy = 100 points
#
#       latency = 80 points
#
#       cost = 90 points
#
#
# and allow:
#
#
#       low latency
#
#
# to compensate for:
#
#
#       policy DENY
#
#
# ============================================================================
#
#
#       DENY + FAST != ALLOW
#
#
# ============================================================================


# ============================================================================
# NETWORK METRIC != AI ROUTING SCORE
# ============================================================================
#
# SD-WAN may report:
#
#
#       latency
#
#       jitter
#
#       loss
#
#
# Those may later help rank otherwise viable choices.
#
#
# But:
#
#
#       HARD VIABILITY
#
#
# must be established first.
#
#
# ============================================================================
#
#
#       FILTER FIRST.
#
#       OPTIMIZE SECOND.
#
#
# ============================================================================


# ============================================================================
# FALLBACK
# ============================================================================
#
# Suppose:
#
#
#       service-a
#
#
# was selected.
#
#
# Invocation fails.
#
#
# Agent 11 considers:
#
#
#       service-b
#
#
# Runtime fallback must re-evaluate CURRENT facts.
#
#
# ============================================================================
#
#
#       HISTORICAL VIABILITY != CURRENT VIABILITY
#
#
# ============================================================================


# ============================================================================
# WHY NETWORK EVIDENCE MUST BE REOBSERVED
# ============================================================================
#
# During failure:
#
#
#       BGP may converge
#
#       SD-WAN may steer
#
#       VPN may reconnect
#
#       cloud route may change
#
#
# Therefore:
#
#
#       candidate-b was viable earlier
#
#
# does not prove:
#
#
#       candidate-b is viable now.
#
#
# ============================================================================


# ============================================================================
# NO NETWORK REMEDIATION
# ============================================================================
#
# NetworkOrchestrator remains observational.
#
#
# It does NOT:
#
#
#       restart VPN
#
#       advertise BGP prefixes
#
#       withdraw BGP prefixes
#
#       change LOCAL_PREF
#
#       change SD-WAN policy
#
#       change cloud routes
#
#       modify firewalls
#
#       create private endpoints
#
#
# ============================================================================
#
#
#       OBSERVER != CONTROLLER
#
#
# ============================================================================


# ============================================================================
# FUTURE CONTROL PLANE
# ============================================================================
#
# Agent 11 may eventually be permitted to propose infrastructure changes.
#
#
# A safe pattern is:
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
#
#       CORRECT REASONING != EXECUTION AUTHORITY
#
#
# ============================================================================


# ============================================================================
# EXECUTION SUCCESS != OUTCOME SUCCESS
# ============================================================================
#
# Suppose an authorized automation successfully changes:
#
#
#       SD-WAN policy
#
#
# API result:
#
#
#       200 OK
#
#
# That proves:
#
#
#       command accepted
#
#
# It does NOT prove:
#
#
#       desired network condition exists.
#
#
# ============================================================================
#
#
#       EXECUTION SUCCESS != OUTCOME SUCCESS
#
#
# ============================================================================
#
# Therefore future control should:
#
#
#       execute
#           |
#           v
#       reobserve
#           |
#           v
#       reassess
#           |
#           v
#       re-evaluate
#
#
# ============================================================================


# ============================================================================
# CONCURRENCY
# ============================================================================
#
# Enterprise evidence collection will eventually benefit from concurrent
# observation.
#
#
# For example:
#
#
#       endpoint observer -------+
#                                |
#       route observer ----------+
#                                |
#       SD-WAN observer ---------+--> gather
#                                |
#       synthetic probes --------+
#
#
# But concurrency remains an implementation strategy.
#
#
# ============================================================================
#
#
#       EXECUTION STRATEGY != DOMAIN SEMANTICS
#
#
# ============================================================================


# ============================================================================
# OBSERVER FAILURE
# ============================================================================
#
# Expected infrastructure failures should be normalized at adapter/evidence
# boundaries.
#
#
# Example:
#
#
#       Cisco API timeout
#
#           ->
#
#       observation unavailable
#
#           ->
#
#       normalized uncertainty
#
#
# ============================================================================
#
#
#       OBSERVER FAILURE != OBSERVED NETWORK FAILURE
#
#
# ============================================================================


# ============================================================================
# TELEMETRY
# ============================================================================
#
# III-C network telemetry should eventually be able to answer:
#
#
#       What paths were expected?
#
#       What paths were observed?
#
#       Which evidence was fresh?
#
#       Which observer produced it?
#
#       What path state was concluded?
#
#       What route evidence existed?
#
#       Did SD-WAN steer?
#
#       Did BGP converge?
#
#       Did the realized path differ from expected topology?
#
#
# ============================================================================
#
#
#       STRUCTURED FACTS FIRST.
#
#       HUMAN EXPLANATION SECOND.
#
#
# ============================================================================


# ============================================================================
# SEIR-II LAB SCENARIO 1
#
# PRIVATE -> INTERNET FAILOVER
# ============================================================================
#
# Initial:
#
#
#       private-link-a
#           AVAILABLE
#
#       internet-a
#           AVAILABLE
#
#
# Policy:
#
#
#       E9:
#           private allowed
#           Internet denied
#
#
# Failure:
#
#
#       private-link-a
#           UNAVAILABLE
#
#
# SD-WAN:
#
#
#       realizes internet-a
#
#
# Network:
#
#
#       CONNECTIVITY AVAILABLE
#
#
# Policy:
#
#
#       INTERNET DENIED
#
#
# Candidate evaluation:
#
#
#       NO POLICY-COMPLIANT PATH
#
#
# ============================================================================
#
#
#       NETWORK SUCCESS
#           +
#       POLICY SUCCESS
#           =
#       AI REQUEST BLOCKED
#
#
# ============================================================================
#
# Blocking is not necessarily system failure.
#
#
# ============================================================================


# ============================================================================
# SEIR-II LAB SCENARIO 2
#
# TWO AUTHORIZED PATHS
# ============================================================================
#
#
#       private-a
#           AVAILABLE
#           20 ms
#
#
#       vpn-a
#           AVAILABLE
#           80 ms
#
#
# Both:
#
#
#       policy allowed
#
#
# Only after hard constraints are satisfied may optimization prefer:
#
#
#       private-a
#
#
# ============================================================================
#
#
#       FILTER FIRST.
#
#       OPTIMIZE SECOND.
#
#
# ============================================================================


# ============================================================================
# SEIR-II LAB SCENARIO 3
#
# FALSE REDUNDANCY
# ============================================================================
#
#
#       vpn-a
#
#       vpn-b
#
#
# Both use:
#
#
#       Carrier X
#
#
# Carrier X fails.
#
#
# Both disappear.
#
#
# Lesson:
#
#
#       TWO PATHS != TWO FAILURE DOMAINS
#
#
# ============================================================================


# ============================================================================
# SEIR-II LAB SCENARIO 4
#
# CONTROL PLANE / DATA PLANE CONFLICT
# ============================================================================
#
#
#       SD-WAN controller:
#           AVAILABLE
#
#
#       synthetic probe:
#           UNAVAILABLE
#
#
# Do NOT automatically call:
#
#
#       DEGRADED
#
#
# The observations may concern different layers or may genuinely conflict.
#
#
# ============================================================================
#
#
#       DISAGREEMENT != DEGRADATION
#
#
# ============================================================================


# ============================================================================
# SEIR-II LAB SCENARIO 5
#
# PATH DRIFT WITHOUT OUTAGE
# ============================================================================
#
# Expected:
#
#
#       private-a
#
#
# Realized:
#
#
#       internet-a
#
#
# Connectivity:
#
#
#       AVAILABLE
#
#
# Outage:
#
#
#       NONE
#
#
# Security significance:
#
#
#       POTENTIALLY HIGH
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
# PART III-C TEST MATRIX
# ============================================================================
#
# TEST 1
#
#       private path fails
#       Internet path works
#
# Expected:
#
#       preserve private UNAVAILABLE
#       preserve Internet AVAILABLE
#       no authorization decision
#
#
# ---------------------------------------------------------------------------
#
# TEST 2
#
#       BGP route PRESENT
#       data-plane path UNAVAILABLE
#
# Expected:
#
#       preserve both
#
#
# ---------------------------------------------------------------------------
#
# TEST 3
#
#       BGP route ABSENT
#       alternate path AVAILABLE
#
# Expected:
#
#       preserve both
#
#
# ---------------------------------------------------------------------------
#
# TEST 4
#
#       Azure destination
#       PrivateLink AVAILABLE
#
# Expected:
#
#       cloud provider does not alter path semantics
#
#
# ---------------------------------------------------------------------------
#
# TEST 5
#
#       GCP destination
#       VPN AVAILABLE
#
# Expected:
#
#       same normalized network model
#
#
# ---------------------------------------------------------------------------
#
# TEST 6
#
#       two paths
#       same carrier
#
# Expected:
#
#       no automatic independence claim
#
#
# ---------------------------------------------------------------------------
#
# TEST 7
#
#       expected private path
#       realized Internet path
#
# Expected:
#
#       connectivity may remain AVAILABLE
#       do not rewrite Internet as unavailable
#
#
# ---------------------------------------------------------------------------
#
# TEST 8
#
#       SD-WAN convergence succeeds
#
# Expected:
#
#       no automatic AI authorization
#
#
# ---------------------------------------------------------------------------
#
# TEST 9
#
#       BGP convergence succeeds
#
# Expected:
#
#       no automatic AI route selection
#
#
# ---------------------------------------------------------------------------
#
# TEST 10
#
#       network control API succeeds
#
# Expected:
#
#       future controller must reobserve
#       before claiming desired outcome
#
#
# ============================================================================
# PART III-C FINAL INVARIANTS
# ============================================================================
#
#
# SD-WAN
# -------
#
#       SD-WAN BEST PATH != AGENT 11 BEST AI ROUTE
#
#       NETWORK FAILOVER != POLICY FAILOVER
#
#       NETWORK CONVERGENCE != POLICY-COMPLIANT RECOVERY
#
#
# BGP
# ---
#
#       PATH TYPE != ROUTING PROTOCOL
#
#       BGP ROUTE PRESENT != END-TO-END CONNECTIVITY
#
#       BGP BEST PATH != AGENT 11 BEST AI ROUTE
#
#       BGP LOCAL_PREF != AI ROUTING PREFERENCE
#
#       NEGATIVE OBSERVATION != FAILED OBSERVATION
#
#
# PATH REALIZATION
# ----------------
#
#       EXPECTED PATH != OBSERVED PATH
#
#       EXPECTED PATH != REALIZED PATH
#
#       PATH DRIFT != PATH FAILURE
#
#       NETWORK WORKING != NETWORK WORKING AS INTENDED
#
#
# MULTI-CLOUD
# -----------
#
#       CLOUD PROVIDER != ROUTING DOMAIN
#
#       CLOUD PROVIDER != PATH TYPE
#
#       LOCATION != AUTHORIZATION
#
#       WHERE IT RUNS != HOW WE REACH IT
#
#       DIFFERENT CLOUDS != INDEPENDENT FAILURE
#
#
# RESILIENCE
# ----------
#
#       PATH COUNT != FAILURE-DOMAIN COUNT
#
#       MULTI-PATH != RESILIENCE
#
#       CORRELATION != PROVEN DEPENDENCY
#
#
# LAYERS
# ------
#
#       ROUTE SUCCESS != DATA-PLANE SUCCESS
#
#       DATA-PLANE SUCCESS != TRANSPORT SUCCESS
#
#       TRANSPORT SUCCESS != TLS SUCCESS
#
#       TLS SUCCESS != APPLICATION SUCCESS
#
#       NETWORK AVAILABILITY != SERVICE AVAILABILITY
#
#
# POLICY
# ------
#
#       DESTINATION AUTHORIZED != EVERY PATH AUTHORIZED
#
#       FAST != AUTHORIZED
#
#       DENY + FAST != ALLOW
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ROUTING
# -------
#
#       NETWORK FACT != ROUTING VIABILITY
#
#       HARD CONSTRAINTS FIRST
#
#       OPTIMIZATION SECOND
#
#       FILTER FIRST
#
#       OPTIMIZE SECOND
#
#       HISTORICAL VIABILITY != CURRENT VIABILITY
#
#
# AUTHORITY
# ---------
#
#       OBSERVER != CONTROLLER
#
#       OBSERVE != REMEDIATE
#
#       CORRECT REASONING != EXECUTION AUTHORITY
#
#       EXECUTION SUCCESS != OUTCOME SUCCESS
#
#
# ARCHITECTURE
# ------------
#
#       SOURCES OBSERVE
#
#       ADAPTERS NORMALIZE
#
#       MODELS REPRESENT
#
#       EVALUATORS INTERPRET
#
#       ORCHESTRATORS COORDINATE
#
#       SYSTEM COMPLEXITY
#           DOES NOT REQUIRE
#       ORCHESTRATOR COMPLEXITY
#
#       VENDOR COMPLEXITY ENDS
#       AT THE ADAPTER BOUNDARY
#
#
# ============================================================================
# FINAL PART III-C RULE
# ============================================================================
#
#
#       THE NETWORK MAY FIND
#       A WORKING PATH.
#
#
#       THAT DOES NOT MEAN
#       AGENT 11 MAY USE IT.
#
#
#       THE NETWORK SUBSYSTEM
#       REPORTS WHAT CONNECTIVITY EXISTS.
#
#
#       POLICY DETERMINES
#       WHAT CONNECTIVITY IS PERMITTED.
#
#
#       CANDIDATE EVALUATION DETERMINES
#       WHAT AI DESTINATIONS REMAIN VIABLE.
#
#
#       AIRouter SELECTS
#       AMONG THOSE VIABLE DESTINATIONS.
#
#
# ============================================================================
# END PART III-C
# ============================================================================
