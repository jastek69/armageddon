#note to Cursor AI: Please look at this---> "One small refinement from the sample: I would validate the static source's inputs at construction time enough to prevent accidental mutation from outside by copying the mapping. I would not add elaborate validators or a Pydantic configuration object."



============================================================================
# network/path.py
#
# PART I
#
# NETWORK PATH SEMANTICS + INFRASTRUCTURE-NEUTRAL BEHAVIOR
# ============================================================================
#
# PURPOSE
# -------
#
# path.py answers:
#
#
#       "WHAT OPERATIONAL NETWORK PATH EVIDENCE
#        DO WE HAVE BETWEEN AGENT 11
#        AND A DESTINATION?"
#
#
# path.py does NOT answer:
#
#
#       "May this request use that destination?"
#
#       "Should this AI service be selected?"
#
#       "Does the model support the requested capability?"
#
#       "Is the AI service itself healthy?"
#
#
# Those responsibilities belong elsewhere.
#
#
# ============================================================================
# CORE SEPARATION
# ============================================================================
#
#       endpoint.py
#           -> destination existence
#
#       health.py
#           -> service operational condition
#
#       path.py
#           -> network connectivity condition
#
#       policy/
#           -> authorization
#
#       routing/
#           -> AI service selection
#
#
# Therefore:
#
#
#       ENDPOINT EXISTS != PATH AVAILABLE
#
#       SERVICE HEALTHY != PATH AVAILABLE
#
#       PATH AVAILABLE != AUTHORIZED
#
#       AUTHORIZED != PATH AVAILABLE
#
#       REACHABLE != AUTHORIZED
#
#
# ============================================================================
# CENTRAL RULE
# ============================================================================
#
# An AVAILABLE path is an operational fact.
#
# It is NOT a security decision.
#
#
# Example:
#
#
#       INTERNET
#           AVAILABLE
#
#
# means:
#
#
#       network evidence supports Internet connectivity
#
#
# It does NOT mean:
#
#
#       restricted data may use the Internet.
#
#
# ============================================================================
# SEIR-I SCOPE
# ============================================================================
#
# Part I intentionally keeps path evaluation small.
#
# We need:
#
#
#       1. a path type
#
#       2. a path state
#
#       3. a source of path evidence
#
#       4. an evaluator that consumes that source
#
#       5. a static implementation for teaching and testing
#
#
# We do NOT yet need:
#
#
#       BGP route tables
#
#       SD-WAN controllers
#
#       cloud SDKs
#
#       VPN APIs
#
#       latency measurements
#
#       jitter measurements
#
#       packet-loss measurements
#
#       bandwidth measurements
#
#       path authorization
#
#       path scoring
#
#       automatic failover
#
#       endpoint identity
#
#       deployment identity
#
#       path-instance identity
#
#       evidence provenance
#
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================


from typing import Protocol

from ..models.enums.network_enums import (
    NetworkPathState,
    NetworkPathType,
)


# ============================================================================
# PATH EVIDENCE SOURCE
# ============================================================================
#
# PathEvidenceSource is a BEHAVIORAL CONTRACT.
#
# It is not a Pydantic domain model.
#
#
# It describes something capable of answering:
#
#
#       "What operational state does this source currently report
#        for this service and path type?"
#
#
# Today:
#
#
#       StaticPathEvidenceSource
#
#
# Later:
#
#
#       VPN evidence source
#
#       cloud private-connectivity evidence source
#
#       SD-WAN evidence source
#
#       Internet reachability evidence source
#
#
# Potentially:
#
#
#       BGP route evidence
#
#
# but BGP deserves separate architectural treatment because:
#
#
#       PATH TYPE != ROUTING PROTOCOL
#
#
# ============================================================================


class PathEvidenceSource(Protocol):
    """
    Behavioral contract for network-path evidence providers.

    Implementations translate infrastructure-specific observations into
    Agent 11's infrastructure-neutral NetworkPathState vocabulary.

    The caller supplies:

        service_id

        path_type

    The source returns the currently observed path state.

    This interface intentionally does not expose infrastructure SDK objects.

    It does not expose:

        AWS SDK objects

        Azure SDK objects

        GCP SDK objects

        OCI SDK objects

        Kubernetes objects

        VPN appliance objects

        SD-WAN controller objects

        BGP route objects

    Infrastructure adapters translate those technologies into this contract.
    """

    def get_state(
        self,
        service_id: str,
        path_type: NetworkPathType,
    ) -> NetworkPathState:
        """
        Return current observed state for the requested network path.

        Implementations must preserve uncertainty.

        If current path state cannot be established, the implementation
        should report:

            NetworkPathState.UNKNOWN

        rather than inventing:

            NetworkPathState.UNAVAILABLE


        Important:

            UNKNOWN != UNAVAILABLE

            OBSERVATION FAILURE != PATH FAILURE

            FAIL CLOSED != FALSIFY STATE
        """
        ...


# ============================================================================
# STATIC PATH EVIDENCE SOURCE
# ============================================================================
#
# SEIR-I needs a deterministic implementation that requires:
#
#
#       no cloud account
#
#       no Kubernetes cluster
#
#       no VPN
#
#       no SD-WAN controller
#
#       no BGP peer
#
#       no network appliance
#
#
# This allows students to understand the domain boundary before connecting
# Agent 11 to real infrastructure.
#
#
# It also gives us a simple test double for later components.
#
#
# ============================================================================


class StaticPathEvidenceSource:
    """
    Simple in-memory network-path evidence source for SEIR-I.

    Path states are keyed by:

        (service_id, path_type)

    Example:

        {
            (
                "company-cloud-primary",
                NetworkPathType.PRIVATE_LINK,
            ): NetworkPathState.AVAILABLE,

            (
                "external-primary",
                NetworkPathType.INTERNET,
            ): NetworkPathState.AVAILABLE,
        }


    The source reports operational evidence.

    It does NOT determine:

        whether the destination is authorized

        whether the path is authorized

        whether the model is capable

        whether the service is healthy

        whether the service should be selected

        whether another path should be used
    """

    def __init__(
        self,
        path_states: dict[
            tuple[str, NetworkPathType],
            NetworkPathState,
        ],
    ) -> None:
        """
        Store static network-path observations.

        A defensive copy is retained so that callers cannot accidentally
        mutate this evidence source by later changing the dictionary passed
        to the constructor.

        Absence from the mapping means:

            UNKNOWN

        It does NOT mean:

            UNAVAILABLE


        Therefore:

            ABSENCE OF EVIDENCE
                !=
            EVIDENCE OF ABSENCE
        """

        self._path_states = dict(path_states)

    def get_state(
        self,
        service_id: str,
        path_type: NetworkPathType,
    ) -> NetworkPathState:
        """
        Return configured path evidence.

        If no evidence exists for the requested service/path combination,
        preserve uncertainty by returning UNKNOWN.

        This is intentionally:

            missing evidence
                ->
            UNKNOWN

        rather than:

            missing evidence
                ->
            UNAVAILABLE
        """

        return self._path_states.get(
            (service_id, path_type),
            NetworkPathState.UNKNOWN,
        )


# ============================================================================
# NETWORK PATH EVALUATOR
# ============================================================================
#
# NetworkPathEvaluator owns the generic Agent 11 behavior for asking a path
# evidence source about a network path.
#
#
# It does NOT:
#
#
#       discover AI services
#
#       discover endpoints
#
#       inspect model capabilities
#
#       determine service health
#
#       evaluate data policy
#
#       authorize a network path
#
#       select a network path
#
#       select an AI service
#
#       perform failover
#
#       perform fallback
#
#       modify network infrastructure
#
#
# This distinction is deliberate.
#
#
#       PATH EVALUATION != AI ROUTING
#
#
# ============================================================================


class NetworkPathEvaluator:
    """
    Evaluates network-path state using an injected evidence source.

    The evaluator depends upon the PathEvidenceSource abstraction rather than
    any particular infrastructure technology.


    Dependency direction:

        NetworkPathEvaluator
                |
                v
        PathEvidenceSource
                ^
                |
        infrastructure adapter


    The evaluator USES its dependency.

    It does not CHOOSE or CONSTRUCT its dependency.


        COMPONENT USES DEPENDENCY
            !=
        COMPONENT CHOOSES DEPENDENCY
    """

    def __init__(
        self,
        path_source: PathEvidenceSource,
    ) -> None:
        """
        Inject the path-evidence source.

        Dependency construction belongs to application composition.

        SEIR-I:

            source = StaticPathEvidenceSource(...)

            evaluator = NetworkPathEvaluator(
                path_source=source,
            )


        Future infrastructure may instead inject:

            VpnPathEvidenceSource

            PrivateConnectivityEvidenceSource

            SdWanPathEvidenceSource

            InternetPathEvidenceSource


        without changing NetworkPathEvaluator.
        """

        self._path_source = path_source

    def get_path_state(
        self,
        service_id: str,
        path_type: NetworkPathType,
    ) -> NetworkPathState:
        """
        Return current operational state reported for a network path.

        This method deliberately returns NetworkPathState rather than bool.

        A bool would collapse:

            AVAILABLE

            DEGRADED

            UNAVAILABLE

            UNKNOWN

        into:

            True

            False


        That would destroy meaningful operational information.

        In particular:

            UNKNOWN != UNAVAILABLE

        and:

            DEGRADED != UNAVAILABLE


        This method also deliberately does not return:

            RoutingCandidateStatus

            PolicyDecisionStatus

            bool


        because this component reports path state rather than making a
        routing or authorization decision.
        """

        return self._path_source.get_state(
            service_id=service_id,
            path_type=path_type,
        )


# ============================================================================
# EXAMPLE: BASIC PATH EVIDENCE
# ============================================================================
#
# Suppose:
#
#
#       company-cloud-primary
#
#
# currently has:
#
#
#       PRIVATE_LINK
#           AVAILABLE
#
#       INTERNET
#           AVAILABLE
#
#       VPN
#           DEGRADED
#
#
# Those facts can be represented independently:
#
#
#     source = StaticPathEvidenceSource(
#         path_states={
#             (
#                 "company-cloud-primary",
#                 NetworkPathType.PRIVATE_LINK,
#             ): NetworkPathState.AVAILABLE,
#
#             (
#                 "company-cloud-primary",
#                 NetworkPathType.INTERNET,
#             ): NetworkPathState.AVAILABLE,
#
#             (
#                 "company-cloud-primary",
#                 NetworkPathType.VPN,
#             ): NetworkPathState.DEGRADED,
#         }
#     )
#
#
#     evaluator = NetworkPathEvaluator(
#         path_source=source,
#     )
#
#
#     private_state = evaluator.get_path_state(
#         service_id="company-cloud-primary",
#         path_type=NetworkPathType.PRIVATE_LINK,
#     )
#
#
#     assert private_state is NetworkPathState.AVAILABLE
#
#
# ============================================================================
# UNKNOWN EXAMPLE
# ============================================================================
#
# Suppose no SD-WAN evidence was configured:
#
#
#     sdwan_state = evaluator.get_path_state(
#         service_id="company-cloud-primary",
#         path_type=NetworkPathType.SD_WAN,
#     )
#
#
#     assert sdwan_state is NetworkPathState.UNKNOWN
#
#
# Agent 11 did not establish:
#
#
#       SD-WAN unavailable.
#
#
# It established:
#
#
#       SD-WAN state unknown.
#
#
# ============================================================================
# OPERATIONAL STATE != AUTHORIZATION
# ============================================================================
#
# Suppose:
#
#
#       PRIVATE_LINK
#           AVAILABLE
#
#
#       INTERNET
#           AVAILABLE
#
#
# path.py reports both operational facts.
#
#
# It does NOT decide:
#
#
#       "PrivateLink is authorized."
#
#
# It does NOT decide:
#
#
#       "Internet is prohibited."
#
#
# Those are policy questions.
#
#
# ============================================================================
# FUTURE PATH-SPECIFIC POLICY
# ============================================================================
#
# SEIR-I policy primarily reasons about:
#
#
#       DataClassification
#           x
#       AIRoute
#
#
# Future policy may eventually need:
#
#
#       DataClassification
#           x
#       AIRoute
#           x
#       NetworkPathType
#
#
# Example:
#
#
#       E9
#           +
#       COMPANY_CLOUD_LLM
#           +
#       PRIVATE_LINK
#           ->
#       ALLOW
#
#
# while:
#
#
#       E9
#           +
#       COMPANY_CLOUD_LLM
#           +
#       INTERNET
#           ->
#       DENY
#
#
# Do NOT add path-specific authorization to SEIR-I merely because the future
# architecture may require it.
#
#
# Preserve the distinction:
#
#
#       DESTINATION AUTHORIZED
#           !=
#       EVERY PATH TO DESTINATION AUTHORIZED
#
#
# ============================================================================
# DEGRADED
# ============================================================================
#
# path.py preserves DEGRADED as an operational state.
#
#
# It does NOT automatically translate:
#
#
#       DEGRADED
#           ->
#       REJECTED
#
#
# Why?
#
#
# DEGRADED may still mean useful connectivity exists.
#
#
# Examples:
#
#
#       one redundant VPN tunnel failed
#
#       latency increased
#
#       bandwidth decreased
#
#       packet loss increased but traffic still flows
#
#
# A future request-specific evaluator may decide whether the degraded path is
# suitable for a particular workload.
#
#
# For example:
#
#
#       LIGHT reasoning
#
#
# may tolerate a condition that:
#
#
#       latency-sensitive inference
#
#
# cannot.
#
#
# Therefore:
#
#
#       DEGRADED != UNAVAILABLE
#
#       DEGRADED != REJECTED
#
#       PATH STATE != WORKLOAD SUITABILITY
#
#
# ============================================================================
# UNKNOWN
# ============================================================================
#
# UNKNOWN must remain first-class.
#
#
# Example:
#
#
#       VPN telemetry cannot currently be obtained.
#
#
# Correct:
#
#
#       VPN
#           UNKNOWN
#
#
# Incorrect:
#
#
#       VPN
#           UNAVAILABLE
#
#
# Agent 11 has not established that the VPN failed.
#
#
# Candidate evaluation may later decide:
#
#
#       UNKNOWN path state is insufficient
#       to establish candidate viability.
#
#
# That is compatible with preserving:
#
#
#       NetworkPathState.UNKNOWN
#
#
# in the network subsystem.
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ============================================================================
# NO is_path_available() METHOD
# ============================================================================
#
# Part I deliberately does NOT provide:
#
#
#       is_path_available() -> bool
#
#
# because that method would force this component to decide:
#
#
#       Does DEGRADED count as available?
#
#       Does UNKNOWN count as unavailable?
#
#
# Those interpretations may depend upon the purpose for which the evidence is
# being consumed.
#
#
# The network subsystem should preserve the state.
#
#
# A later viability evaluator can interpret it.
#
#
#       PATH STATE != PATH SUITABILITY
#
#
# ============================================================================
# MULTIPLE PATHS
# ============================================================================
#
# One AI service may have multiple possible network paths:
#
#
#                     company-cloud-primary
#                         /      |       \
#                        /       |        \
#                       v        v         v
#                 PRIVATE_LINK  VPN     INTERNET
#
#
# Their states may be:
#
#
#       PRIVATE_LINK
#           AVAILABLE
#
#       VPN
#           DEGRADED
#
#       INTERNET
#           AVAILABLE
#
#
# Part I preserves those facts independently.
#
#
# It does NOT decide:
#
#
#       "Choose PrivateLink."
#
#
# or:
#
#
#       "Choose Internet."
#
#
# because path choice may eventually depend upon:
#
#
#       authorization
#
#       workload requirements
#
#       residency
#
#       latency
#
#       cost
#
#       failure domains
#
#
# ============================================================================
# AVAILABLE ALTERNATE PATH != AUTHORIZED ALTERNATE PATH
# ============================================================================
#
# Suppose:
#
#
#       PRIVATE_LINK
#           UNAVAILABLE
#
#
# while:
#
#
#       INTERNET
#           AVAILABLE
#
#
# A network system may correctly observe:
#
#
#       "An Internet path exists."
#
#
# Agent 11 must NOT automatically infer:
#
#
#       "Use the Internet."
#
#
# Policy may prohibit that path for the current data.
#
#
# Therefore:
#
#
#       AVAILABLE ALTERNATE PATH
#           !=
#       AUTHORIZED ALTERNATE PATH
#
#
# ============================================================================
# NETWORK FAILOVER != POLICY FAILOVER
# ============================================================================
#
# Infrastructure may discover another route.
#
# That does not reduce security requirements.
#
#
#       NETWORK FAILOVER
#           MUST NOT
#       CREATE POLICY FAILOVER
#
#
# This follows the broader Agent 11 fallback invariant:
#
#
#       FALLBACK MAY REDUCE AVAILABILITY.
#
#       FALLBACK NEVER REDUCES SECURITY POLICY.
#
#
# ============================================================================
# PATH IS RELATIONAL
# ============================================================================
#
# Service health often describes the destination.
#
# Path state describes a relationship.
#
#
# Conceptually:
#
#
#       SOURCE
#           |
#           v
#         PATH
#           |
#           v
#       DESTINATION
#
#
# A destination may be reachable from one Agent 11 location and unreachable
# from another.
#
#
# Example:
#
#
#       Agent 11 / Tokyo
#           |
#           v
#       private endpoint
#
#           AVAILABLE
#
#
# while:
#
#
#       Agent 11 / Virginia
#           |
#           X
#           |
#       same private endpoint
#
#           UNAVAILABLE
#
#
# The destination did not necessarily fail.
#
# The network relationship differs.
#
#
# ============================================================================
# CURRENT SEIR-I CORRELATION
# ============================================================================
#
# Part I intentionally identifies a path using:
#
#
#       service_id
#           +
#       path_type
#
#
# This is a simplification.
#
#
# It gives SEIR-I enough information to express:
#
#
#       "What do we know about the VPN path
#        to company-cloud-primary?"
#
#
# without prematurely introducing:
#
#
#       source_id
#
#       endpoint_id
#
#       deployment_id
#
#       path_id
#
#       cluster_id
#
#       region_id
#
#
# ============================================================================
# SERVICE != ENDPOINT
# ============================================================================
#
# The current service_id correlation is not a permanent statement that:
#
#
#       SERVICE == ENDPOINT
#
#
# Future services may expose:
#
#
#       public endpoint
#
#       private endpoint
#
#       regional endpoint
#
#       gateway endpoint
#
#
# Therefore:
#
#
#       SERVICE != ENDPOINT
#
#
# endpoint.py and future path requirements should determine when a first-class
# NetworkEndpoint model is actually required.
#
#
# ============================================================================
# PATH TYPE != PATH INSTANCE
# ============================================================================
#
# SEIR-I reasons using broad connectivity types.
#
#
# Example:
#
#
#       VPN
#
#
# Future infrastructure may expose:
#
#
#       VPN-TOKYO-01
#
#       VPN-TOKYO-02
#
#       VPN-VIRGINIA-01
#
#
# Each could have independent:
#
#
#       state
#
#       latency
#
#       failure domain
#
#       destination
#
#
# Therefore:
#
#
#       PATH TYPE != PATH INSTANCE
#
#
# Part I does not yet need path-instance identity.
#
#
# ============================================================================
# PATH TYPE != ROUTING PROTOCOL
# ============================================================================
#
# BGP requires special care.
#
#
# Connectivity mechanisms such as:
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
# are not conceptually identical to:
#
#
#       BGP
#
#
# BGP is fundamentally a routing protocol and control-plane mechanism.
#
#
# A VPN may use routes learned through BGP.
#
#
# A private network connection may use routes learned through BGP.
#
#
# Therefore:
#
#
#       PATH TYPE != ROUTING PROTOCOL
#
#
# Part I does not implement BGP observation.
#
#
# If BGP currently remains in NetworkPathType for curriculum continuity,
# path.py should NOT build behavior that assumes:
#
#
#       BGP == VPN
#
#
# or:
#
#
#       BGP == PRIVATE_LINK
#
#
# SEIR-II should revisit whether BGP becomes a separate route-evidence
# dimension.
#
#
# ============================================================================
# BGP ANSWERS A DIFFERENT QUESTION
# ============================================================================
#
# BGP may help answer:
#
#
#       "What route information exists for reaching this destination?"
#
#
# Agent 11 policy answers:
#
#
#       "May this request use this destination/path?"
#
#
# Therefore:
#
#
#       BGP REACHABLE != AI AUTHORIZED
#
#
# ============================================================================
# SD-WAN
# ============================================================================
#
# SD-WAN can reasonably remain a logical connectivity mechanism from Agent
# 11's perspective.
#
#
# The SD-WAN system itself may select among:
#
#
#       Internet
#
#       MPLS
#
#       private circuits
#
#       cellular
#
#
# Agent 11 does not need to reproduce the complete underlying network topology
# merely to consume path evidence.
#
#
#       INFRASTRUCTURE COMPLEXITY
#           SHOULD BE TRANSLATED,
#           NOT REPLICATED.
#
#
# ============================================================================
# LOCAL
# ============================================================================
#
# LOCAL may represent connectivity where Agent 11 and the destination share
# sufficiently local infrastructure that no external network mechanism is
# being modeled for the current abstraction.
#
#
# LOCAL still does not mean:
#
#
#       authorized
#
#
# or:
#
#
#       secure
#
#
# Therefore:
#
#
#       LOCAL != AUTHORIZED
#
#
# ============================================================================
# STREET_ACCESS
# ============================================================================
#
# STREET_ACCESS is intentionally unusual but pedagogically useful.
#
#
# If:
#
#
#       STREET_ACCESS
#           AVAILABLE
#
#
# Agent 11 has learned only:
#
#
#       physical access to the destination is operationally possible.
#
#
# It has NOT learned:
#
#
#       restricted data may be physically transported there.
#
#
# Therefore:
#
#
#       PHYSICAL REACHABILITY != DATA AUTHORIZATION
#
#
# Chewbacca may successfully walk to the inference machine.
#
# Chewbacca still does not get to rewrite the data policy.
#
#
# ============================================================================
# DEPENDENCY INVERSION
# ============================================================================
#
# NetworkPathEvaluator depends upon:
#
#
#       PathEvidenceSource
#
#
# rather than:
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
#       Kubernetes SDK
#
#       Cisco SDK
#
#       VPN vendor SDK
#
#
# This keeps generic path behavior infrastructure-neutral.
#
#
# ============================================================================
# INVERSION OF CONTROL
# ============================================================================
#
# Application composition chooses the implementation:
#
#
#       source = StaticPathEvidenceSource(...)
#
#
#       evaluator = NetworkPathEvaluator(
#           path_source=source,
#       )
#
#
# Later:
#
#
#       source = SomeInfrastructurePathEvidenceSource(...)
#
#
#       evaluator = NetworkPathEvaluator(
#           path_source=source,
#       )
#
#
# NetworkPathEvaluator itself does not decide:
#
#
#       which cloud exists
#
#       which VPN vendor exists
#
#       which Kubernetes cluster exists
#
#       which credentials should be loaded
#
#
#       COMPONENT USES DEPENDENCY
#           !=
#       COMPONENT CHOOSES DEPENDENCY
#
#
# ============================================================================
# DEPENDENCY INJECTION != DI FRAMEWORK
# ============================================================================
#
# Constructor injection is sufficient.
#
#
# Agent 11 does not require a dependency-injection container merely to
# practice dependency inversion.
#
#
# ============================================================================
# APPLICATION COMPOSITION
# ============================================================================
#
# The application's composition/bootstrap layer eventually owns:
#
#
#       infrastructure configuration
#
#       credentials
#
#       SDK clients
#
#       concrete evidence sources
#
#       evaluator construction
#
#
# Generic path behavior should not load credentials or choose infrastructure.
#
#
# ============================================================================
# TESTING: AVAILABLE
# ============================================================================
#
# Example:
#
#
#     source = StaticPathEvidenceSource(
#         path_states={
#             (
#                 "service-a",
#                 NetworkPathType.VPN,
#             ): NetworkPathState.AVAILABLE,
#         }
#     )
#
#
#     evaluator = NetworkPathEvaluator(
#         path_source=source,
#     )
#
#
#     state = evaluator.get_path_state(
#         service_id="service-a",
#         path_type=NetworkPathType.VPN,
#     )
#
#
#     assert state is NetworkPathState.AVAILABLE
#
#
# ============================================================================
# TESTING: DEGRADED
# ============================================================================
#
#     source = StaticPathEvidenceSource(
#         path_states={
#             (
#                 "service-a",
#                 NetworkPathType.VPN,
#             ): NetworkPathState.DEGRADED,
#         }
#     )
#
#
#     evaluator = NetworkPathEvaluator(source)
#
#
#     assert (
#         evaluator.get_path_state(
#             "service-a",
#             NetworkPathType.VPN,
#         )
#         is NetworkPathState.DEGRADED
#     )
#
#
# ============================================================================
# TESTING: UNAVAILABLE
# ============================================================================
#
#     source = StaticPathEvidenceSource(
#         path_states={
#             (
#                 "service-a",
#                 NetworkPathType.PRIVATE_LINK,
#             ): NetworkPathState.UNAVAILABLE,
#         }
#     )
#
#
#     evaluator = NetworkPathEvaluator(source)
#
#
#     assert (
#         evaluator.get_path_state(
#             "service-a",
#             NetworkPathType.PRIVATE_LINK,
#         )
#         is NetworkPathState.UNAVAILABLE
#     )
#
#
# ============================================================================
# TESTING: UNKNOWN
# ============================================================================
#
#     source = StaticPathEvidenceSource(
#         path_states={}
#     )
#
#
#     evaluator = NetworkPathEvaluator(source)
#
#
#     assert (
#         evaluator.get_path_state(
#             "service-a",
#             NetworkPathType.VPN,
#         )
#         is NetworkPathState.UNKNOWN
#     )
#
#
# ============================================================================
# TESTING SHOULD NOT REQUIRE REAL NETWORK INFRASTRUCTURE
# ============================================================================
#
# Generic NetworkPathEvaluator tests should not require:
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
#       Kubernetes
#
#       Cisco
#
#       a VPN
#
#       a BGP peer
#
#       an SD-WAN controller
#
#
# If generic path tests require all of those systems, the abstraction has
# collapsed.
#
#
# ============================================================================
# QUERY COLLECTION != ASSERT OBJECT PAIR
# ============================================================================
#
# Future path evaluation may inspect collections of path evidence.
#
#
# When searching a collection for evidence relevant to:
#
#
#       service-a
#
#
# unrelated evidence should normally be filtered rather than treated as a
# programming error.
#
#
# This differs from an explicit object-pair assertion such as:
#
#
#       AIService.model_id
#           must match
#       AIModel.model_id
#
#
# in ModelRouter.
#
#
# Therefore:
#
#
#       QUERY COLLECTION != ASSERT OBJECT PAIR
#
#
# ============================================================================
# PATH.PY DOES NOT OWN ROUTING
# ============================================================================
#
# There are two meanings of "routing" in this system.
#
#
# NETWORK ROUTING:
#
#
#       How do packets reach a destination?
#
#
# AGENT 11 AI ROUTING:
#
#
#       Which AI service should receive the request?
#
#
# They are related.
#
# They are not the same responsibility.
#
#
# ============================================================================
# PATH.PY DOES NOT SELECT AI SERVICES
# ============================================================================
#
# The intended future flow is:
#
#
#       network path evidence
#               |
#               v
#       candidate evaluation
#               |
#               v
#       RoutingCandidate
#               |
#               v
#           AIRouter
#
#
# not:
#
#
#       network/path.py
#               |
#               v
#           AIRouter
#
#
# ============================================================================
# AIRouter SHOULD NOT KNOW BGP
# ============================================================================
#
# AIRouter receives already evaluated RoutingCandidate objects.
#
#
# It should not need to know:
#
#
#       VPN
#
#       BGP
#
#       SD-WAN
#
#       PrivateLink
#
#       packet loss
#
#       latency
#
#
# Those facts should already have been interpreted by the appropriate
# upstream responsibilities.
#
#
# ============================================================================
# CANDIDATE EVALUATION
# ============================================================================
#
# The eventual viability equation remains:
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
# path.py contributes:
#
#
#       PATH EVIDENCE
#
#
# It does not calculate the entire equation.
#
#
# ============================================================================
# NO PATH SCORING
# ============================================================================
#
# Part I deliberately does not assign:
#
#
#       VPN = 90
#
#       PRIVATE_LINK = 100
#
#       INTERNET = 50
#
#
# Path type alone does not create universal preference.
#
#
# A future optimization system may consider:
#
#
#       latency
#
#       cost
#
#       reliability
#
#       bandwidth
#
#       residency
#
#
# only AFTER hard constraints are satisfied.
#
#
#       FILTER BY CONSTRAINTS FIRST.
#
#       OPTIMIZE SECOND.
#
#
# ============================================================================
# NO POLICY SCORING
# ============================================================================
#
# Even if future path optimization uses scores:
#
#
#       POLICY NEVER BECOMES A SCORE.
#
#
# A forbidden Internet path does not become permissible because it is:
#
#
#       faster
#
#       cheaper
#
#       healthier
#
#       lower latency
#
#
# ============================================================================
# NO AUTOMATIC FAILOVER
# ============================================================================
#
# Part I does not implement:
#
#
#       PRIVATE_LINK failed
#           ->
#       automatically use INTERNET
#
#
# because alternate-path use may require independent authorization.
#
#
# ============================================================================
# NO REMEDIATION
# ============================================================================
#
# NetworkPathEvaluator does not:
#
#
#       restart VPNs
#
#       modify routes
#
#       modify BGP advertisements
#
#       patch firewalls
#
#       modify SD-WAN policy
#
#       create PrivateLink endpoints
#
#
# Observation authority is not mutation authority.
#
#
#       OBSERVE != REMEDIATE
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#
# ============================================================================
# PART II PREVIEW
# ============================================================================
#
# Part II can introduce real infrastructure evidence while preserving this
# contract.
#
#
# Likely topics:
#
#
#       Internet reachability
#
#       VPN evidence
#
#       private connectivity
#
#       SD-WAN evidence
#
#       infrastructure adapters
#
#       dependency injection
#
#       observation failure
#
#       cloud networking
#
#
# BGP should be treated carefully as routing/control-plane evidence rather
# than casually equated with a transport path.
#
#
# ============================================================================
# PART III PREVIEW
# ============================================================================
#
# SEIR-II will eventually pressure this model with:
#
#
#       multiple Agent 11 origins
#
#       multiple endpoints
#
#       multiple deployments
#
#       multiple path instances
#
#       multiple clouds
#
#       multiple regions
#
#       multiple observers
#
#       BGP route evidence
#
#       SD-WAN telemetry
#
#       latency
#
#       jitter
#
#       packet loss
#
#       bandwidth
#
#       evidence freshness
#
#       evidence provenance
#
#       failure domains
#
#       path-specific policy
#
#
# At that point:
#
#
#       service_id + path_type -> NetworkPathState
#
#
# may become too lossy.
#
#
# That is when Agent 11 may earn:
#
#
#       NetworkEndpoint
#
#       NetworkPathEvidence
#
#       NetworkPathAssessment
#
#       NetworkPathIdentity
#
#
# or similar domain nouns.
#
#
# Those names are future possibilities.
#
# They are not current commitments.
#
#
# ============================================================================
# WHEN models/network/ EARNS EXISTENCE
# ============================================================================
#
# Do not create:
#
#
#       models/network/
#
#
# merely because path.py exists.
#
#
# Create it when network facts become durable contracts shared by multiple
# behaviors.
#
#
# For example:
#
#
#       NetworkEndpoint
#
#       HealthEvidence
#
#       HealthAssessment
#
#       NetworkPathEvidence
#
#       NetworkPathAssessment
#
#
# may eventually justify that package.
#
#
#       NOUNS / CONTRACTS -> models/
#
#       BEHAVIOR          -> network/
#
#
# ============================================================================
# REVISIT routing/network_context.py
# ============================================================================
#
# After endpoint.py, health.py, and path.py are complete, revisit:
#
#
#       routing/network_context.py
#
#
# Ask:
#
#
#       "What responsibility remains for this file?"
#
#
# If network/ already produces the evidence needed by candidate evaluation,
# routing/network_context.py may be redundant.
#
#
# Do not preserve a file merely because it appeared in the original tree.
#
#
#       FILE EXISTS != DOMAIN RESPONSIBILITY
#
#
# ============================================================================
# PART I FINAL ARCHITECTURE
# ============================================================================
#
#
#                  StaticPathEvidenceSource
#                           |
#                           |
#                           v
#                   PathEvidenceSource
#                           |
#                           v
#                  NetworkPathEvaluator
#                           |
#                           |
#                           v
#                  NetworkPathState
#
#
# Later:
#
#
#       Infrastructure Adapter
#               |
#               v
#       PathEvidenceSource
#               |
#               v
#       NetworkPathEvaluator
#               |
#               v
#       NetworkPathState
#               |
#               v
#       Candidate Evaluation
#               |
#               v
#       RoutingCandidate
#               |
#               v
#           AIRouter
#
#
# ============================================================================
# PART I FINAL INVARIANTS
# ============================================================================
#
#       ENDPOINT EXISTS != PATH AVAILABLE
#
#       SERVICE HEALTHY != PATH AVAILABLE
#
#       PATH AVAILABLE != AUTHORIZED
#
#       AUTHORIZED != PATH AVAILABLE
#
#       REACHABLE != AUTHORIZED
#
#       AVAILABLE != ACCEPTABLE
#
#       UNKNOWN != UNAVAILABLE
#
#       DEGRADED != UNAVAILABLE
#
#       DEGRADED != REJECTED
#
#       OBSERVATION FAILURE != PATH FAILURE
#
#       ABSENCE OF EVIDENCE != EVIDENCE OF ABSENCE
#
#       PATH STATE != WORKLOAD SUITABILITY
#
#       PATH TYPE != PATH INSTANCE
#
#       PATH TYPE != ROUTING PROTOCOL
#
#       SERVICE != ENDPOINT
#
#       AVAILABLE ALTERNATE PATH != AUTHORIZED ALTERNATE PATH
#
#       NETWORK FAILOVER != POLICY FAILOVER
#
#       PHYSICAL REACHABILITY != DATA AUTHORIZATION
#
#       BGP REACHABLE != AI AUTHORIZED
#
#       LOCAL != AUTHORIZED
#
#       OBSERVE != REMEDIATE
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#       COMPONENT USES DEPENDENCY
#           !=
#       COMPONENT CHOOSES DEPENDENCY
#
#       QUERY COLLECTION != ASSERT OBJECT PAIR
#
#       FILTER BY CONSTRAINTS FIRST
#
#       OPTIMIZE SECOND
#
#       POLICY NEVER BECOMES A SCORE
#
#       FAIL CLOSED != FALSIFY STATE
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================
# FINAL NOTE
# ============================================================================
#
# path.py reports:
#
#
#       CONNECTIVITY CONDITION
#
#
# It does not report:
#
#
#       AUTHORIZATION
#
#
# It does not perform:
#
#
#       AI SERVICE SELECTION
#
#
# It does not create:
#
#
#       POLICY FAILOVER
#
#
# The network subsystem tells Agent 11 what the network appears capable of
# doing.
#
# Policy tells Agent 11 what it is permitted to do.
#
# Candidate evaluation combines those facts.
#
# AIRouter selects among candidates that have already survived those
# evaluations.
#
#
#       NETWORK DESCRIBES REACHABILITY.
#
#       POLICY DESCRIBES PERMISSION.
#
#       ROUTING DESCRIBES SELECTION.
#
#
# Keep them separate.
#
#
# ============================================================================
# END OF PART I
# ============================================================================

# ============================================================================
# network/path.py
#
# PART II
#
# REAL INFRASTRUCTURE PATH EVIDENCE
# ============================================================================
#
# Part I established:
#
#
#       NetworkPathEvaluator
#               |
#               v
#       PathEvidenceSource
#               ^
#               |
#       StaticPathEvidenceSource
#
#
# Part II asks:
#
#
#       "HOW DOES REAL INFRASTRUCTURE BECOME
#        PATH EVIDENCE WITHOUT LEAKING
#        INFRASTRUCTURE IMPLEMENTATION DETAILS
#        INTO AGENT 11?"
#
#
# The intended architecture is:
#
#
#       REAL INFRASTRUCTURE
#               |
#               v
#       infrastructure observer
#               |
#               | infrastructure-specific observations
#               v
#       infrastructure path adapter
#               |
#               | Agent 11 vocabulary
#               v
#       NetworkPathState
#
#
# ============================================================================
# IMPORTANT
# ============================================================================
#
# The infrastructure adapter TRANSLATES evidence.
#
# It does not:
#
#
#       authorize the path
#
#       select the path
#
#       select an AI service
#
#       change routing tables
#
#       repair the network
#
#       create VPN tunnels
#
#       modify BGP
#
#
#       OBSERVE != REMEDIATE
#
#
# ============================================================================


from typing import Protocol

from ..models.enums.network_enums import (
    NetworkPathState,
    NetworkPathType,
)


# ============================================================================
# INFRASTRUCTURE OBSERVATION
# ============================================================================
#
# We deliberately create a narrow behavioral interface here rather than
# importing a vendor SDK directly into NetworkPathEvaluator.
#
#
# A real implementation might obtain evidence from:
#
#
#       VPN controller
#
#       cloud networking API
#
#       SD-WAN controller
#
#       internal network-monitoring platform
#
#       synthetic reachability probe
#
#
# But the generic Agent 11 path behavior should not care which one.
#
#
# ============================================================================


class PathObservationError(RuntimeError):
    """
    Raised when infrastructure path state cannot be established.

    This exception is NOT equivalent to:

        NetworkPathState.UNAVAILABLE

    It means:

        the observer could not establish current path state.

    The path adapter may therefore translate this condition into:

        NetworkPathState.UNKNOWN


        OBSERVATION FAILURE != PATH FAILURE
    """


class InfrastructurePathObserver(Protocol):
    """
    Behavioral contract for a real infrastructure path observer.

    The observer answers a deliberately narrow question:

        "Does current infrastructure evidence establish
         the operational condition of this path?"

    The observer is still below Agent 11's generic path semantics.

    Vendor-specific implementations may use:

        cloud APIs

        VPN APIs

        SD-WAN APIs

        monitoring systems

        synthetic probes

    without exposing those APIs above this boundary.
    """

    def observe_path(
        self,
        service_id: str,
        path_type: NetworkPathType,
    ) -> NetworkPathState:
        """
        Observe current infrastructure path state.

        Implementations should return a NetworkPathState when the
        infrastructure evidence can be interpreted reliably.

        If observation itself fails, implementations should raise:

            PathObservationError

        rather than falsely reporting:

            NetworkPathState.UNAVAILABLE
        """
        ...


# ============================================================================
# INFRASTRUCTURE PATH EVIDENCE SOURCE
# ============================================================================
#
# This class adapts an infrastructure observer to the PathEvidenceSource
# contract established in Part I.
#
#
#       InfrastructurePathObserver
#                   |
#                   v
#       InfrastructurePathEvidenceSource
#                   |
#                   v
#            PathEvidenceSource
#
#
# This creates an anti-corruption boundary between:
#
#
#       infrastructure-specific observation
#
# and:
#
#
#       Agent 11 path semantics
#
#
# ============================================================================


class InfrastructurePathEvidenceSource:
    """
    Path-evidence source backed by a real infrastructure observer.

    This class converts infrastructure observation failures into Agent 11's
    explicit UNKNOWN state.

    It does NOT convert observation failures into UNAVAILABLE.
    """

    def __init__(
        self,
        observer: InfrastructurePathObserver,
    ) -> None:
        self._observer = observer

    def get_state(
        self,
        service_id: str,
        path_type: NetworkPathType,
    ) -> NetworkPathState:
        """
        Obtain current path state from infrastructure.

        Successful observation:

            return the observed NetworkPathState

        Observation failure:

            return NetworkPathState.UNKNOWN

        This preserves the distinction:

            "The path is unavailable."

        from:

            "I cannot currently establish whether the path is available."
        """

        try:
            return self._observer.observe_path(
                service_id=service_id,
                path_type=path_type,
            )
        except PathObservationError:
            return NetworkPathState.UNKNOWN


# ============================================================================
# WHY NOT except Exception?
# ============================================================================
#
# Do NOT write:
#
#
#       try:
#           ...
#       except Exception:
#           return NetworkPathState.UNKNOWN
#
#
# in the generic adapter.
#
#
# That would hide programming errors such as:
#
#
#       AttributeError
#
#       TypeError
#
#       KeyError caused by defective implementation
#
#       malformed internal state
#
#
# Those are not network uncertainty.
#
#
# Infrastructure integrations should translate EXPECTED observation failures
# into PathObservationError.
#
#
# Unexpected programming failures should remain visible.
#
#
#       EXPECTED INFRASTRUCTURE FAILURE
#           !=
#       PROGRAMMING DEFECT
#
#
# ============================================================================


# ============================================================================
# EXAMPLE: SYNTHETIC REACHABILITY PROBE
# ============================================================================
#
# A useful first real-world observer is a synthetic probe.
#
#
# Conceptually:
#
#
#       Agent 11
#           |
#           | attempt connection/probe
#           v
#       destination
#
#
# This is particularly valuable because path state is SOURCE-RELATIVE.
#
#
#       SOURCE -> DESTINATION
#
#
# A probe performed from Tokyo tells us something about:
#
#
#       Tokyo -> destination
#
#
# It does not automatically tell us:
#
#
#       Virginia -> destination
#
#
# ============================================================================


class ReachabilityProbe(Protocol):
    """
    Low-level contract for performing a reachability observation.

    The implementation might eventually use:

        TCP connection testing

        HTTP connectivity

        HTTPS connectivity

        internal synthetic monitoring

        cloud reachability tooling

    The probe is intentionally NOT implemented here.
    """

    def can_reach(
        self,
        service_id: str,
        path_type: NetworkPathType,
    ) -> bool:
        """
        Return True when the probe successfully establishes reachability.

        Return False when the probe successfully establishes that the
        requested connectivity test failed.

        Raise PathObservationError when the probe itself cannot establish
        trustworthy evidence.
        """
        ...


class SyntheticReachabilityObserver:
    """
    Infrastructure path observer backed by a synthetic reachability probe.

    This is deliberately simple for SEIR-I / early SEIR-II.

    A successful probe becomes:

        AVAILABLE

    A successfully executed but failed probe becomes:

        UNAVAILABLE

    An observation error propagates as:

        PathObservationError

    which InfrastructurePathEvidenceSource later translates to:

        UNKNOWN
    """

    def __init__(
        self,
        probe: ReachabilityProbe,
    ) -> None:
        self._probe = probe

    def observe_path(
        self,
        service_id: str,
        path_type: NetworkPathType,
    ) -> NetworkPathState:
        reachable = self._probe.can_reach(
            service_id=service_id,
            path_type=path_type,
        )

        if reachable:
            return NetworkPathState.AVAILABLE

        return NetworkPathState.UNAVAILABLE


# ============================================================================
# LIMITATION OF THE SIMPLE PROBE
# ============================================================================
#
# Notice what the bool probe cannot represent:
#
#
#       DEGRADED
#
#
# That is intentional for this simple adapter.
#
#
# A basic connectivity probe can establish:
#
#
#       reachable
#
#       unreachable
#
#
# but it cannot honestly infer:
#
#
#       degraded
#
#
# without richer evidence.
#
#
# Later evidence may include:
#
#
#       latency
#
#       packet loss
#
#       jitter
#
#       tunnel redundancy
#
#       route instability
#
#       bandwidth
#
#
# Then the observer may legitimately produce:
#
#
#       NetworkPathState.DEGRADED
#
#
# Do not fabricate DEGRADED merely because the enum contains it.
#
#
#       VOCABULARY EXISTS != EVIDENCE EXISTS
#
#
# ============================================================================


# ============================================================================
# EXAMPLE TEST PROBE
# ============================================================================
#
# We can demonstrate infrastructure composition without needing an actual
# network appliance.
#
#
# ============================================================================


class StaticReachabilityProbe:
    """
    Deterministic teaching implementation of ReachabilityProbe.

    This represents low-level probe results rather than Agent 11 path-state
    configuration.

    It is useful for demonstrating the Part II adapter chain.
    """

    def __init__(
        self,
        reachable_paths: set[
            tuple[str, NetworkPathType]
        ],
    ) -> None:
        self._reachable_paths = set(reachable_paths)

    def can_reach(
        self,
        service_id: str,
        path_type: NetworkPathType,
    ) -> bool:
        return (
            service_id,
            path_type,
        ) in self._reachable_paths


# ============================================================================
# COMPOSITION EXAMPLE
# ============================================================================
#
# Application composition:
#
#
#       probe
#           |
#           v
#       SyntheticReachabilityObserver
#           |
#           v
#       InfrastructurePathEvidenceSource
#           |
#           v
#       NetworkPathEvaluator
#
#
# Example:
#
#
#     probe = StaticReachabilityProbe(
#         reachable_paths={
#             (
#                 "company-cloud-primary",
#                 NetworkPathType.PRIVATE_LINK,
#             ),
#         }
#     )
#
#
#     observer = SyntheticReachabilityObserver(
#         probe=probe,
#     )
#
#
#     source = InfrastructurePathEvidenceSource(
#         observer=observer,
#     )
#
#
#     evaluator = NetworkPathEvaluator(
#         path_source=source,
#     )
#
#
#     state = evaluator.get_path_state(
#         service_id="company-cloud-primary",
#         path_type=NetworkPathType.PRIVATE_LINK,
#     )
#
#
#     assert state is NetworkPathState.AVAILABLE
#
#
# ============================================================================
# IMPORTANT: THE COMPOSITION ROOT CHOOSES
# ============================================================================
#
# None of these classes should do:
#
#
#       boto3.client(...)
#
#       Azure credential construction
#
#       Google credential construction
#
#       Kubernetes config loading
#
#       Cisco authentication
#
#       VPN credential loading
#
#
# Application composition owns those concerns.
#
#
#       APPLICATION
#           |
#           | constructs dependencies
#           v
#       INFRASTRUCTURE ADAPTER
#           |
#           v
#       AGENT 11 BEHAVIOR
#
#
#       COMPONENT USES DEPENDENCY
#           !=
#       COMPONENT CHOOSES DEPENDENCY
#
#
# ============================================================================


# ============================================================================
# INTERNET PATH EVIDENCE
# ============================================================================
#
# Internet connectivity is an excellent example of why operational state and
# authorization must remain separate.
#
#
# Infrastructure may establish:
#
#
#       INTERNET
#           AVAILABLE
#
#
# Agent 11 policy may independently establish:
#
#
#       request
#           ->
#       EXTERNAL_FM
#           ->
#       DENY
#
#
# Both facts are simultaneously true.
#
#
#       INTERNET AVAILABLE
#           !=
#       EXTERNAL FM AUTHORIZED
#
#
# ============================================================================


# ============================================================================
# PRIVATE CONNECTIVITY
# ============================================================================
#
# Future adapters may observe technologies such as:
#
#
#       AWS PrivateLink
#
#       Azure Private Link / Private Endpoint
#
#       Google Cloud Private Service Connect
#
#       OCI private networking
#
#
# But those provider-specific names should not become routing domains.
#
#
# Agent 11 still reasons at the higher level:
#
#
#       COMPANY_CLOUD_LLM
#
#
# while network evidence describes how the destination may be reached.
#
#
# Therefore:
#
#
#       ROUTING DOMAIN != CLOUD PROVIDER
#
#       ROUTING DOMAIN != NETWORK PATH TYPE
#
#       CLOUD PROVIDER != NETWORK PATH TYPE
#
#
# ============================================================================


# ============================================================================
# PRIVATE != AUTHORIZED
# ============================================================================
#
# A private connection may be:
#
#
#       AVAILABLE
#
#
# and the destination may still be prohibited for the current data.
#
#
# Likewise, a public network path may be operationally available while policy
# prohibits its use.
#
#
# Therefore:
#
#
#       PRIVATE != AUTHORIZED
#
#       PUBLIC != AUTOMATICALLY AUTHORIZED
#
#       NETWORK EXPOSURE != POLICY DECISION
#
#
# ============================================================================


# ============================================================================
# VPN EVIDENCE
# ============================================================================
#
# A future VPN observer may obtain facts such as:
#
#
#       tunnel up/down
#
#       redundant tunnel count
#
#       route availability
#
#       packet loss
#
#       tunnel telemetry
#
#
# Example:
#
#
#       two expected tunnels
#       two healthy
#
#           -> AVAILABLE
#
#
#       two expected tunnels
#       one healthy
#
#           -> perhaps DEGRADED
#
#
#       two expected tunnels
#       zero healthy
#
#           -> perhaps UNAVAILABLE
#
#
#       controller unreachable
#
#           -> UNKNOWN
#
#
# But those translations belong in the VPN-specific adapter.
#
#
# NetworkPathEvaluator should not know what a VPN tunnel is.
#
#
# ============================================================================


# ============================================================================
# SD-WAN EVIDENCE
# ============================================================================
#
# A future SD-WAN adapter might consume:
#
#
#       overlay health
#
#       SLA state
#
#       path availability
#
#       circuit health
#
#       packet loss
#
#       latency
#
#       jitter
#
#
# and translate that infrastructure evidence into:
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
# Agent 11 should not need the vendor's complete topology model merely to
# reason about AI route viability.
#
#
#       INFRASTRUCTURE COMPLEXITY
#           SHOULD BE TRANSLATED,
#           NOT REPLICATED.
#
#
# ============================================================================


# ============================================================================
# KUBERNETES
# ============================================================================
#
# Kubernetes deserves careful treatment here.
#
#
# endpoint.py may use Kubernetes to establish:
#
#
#       "A qualifying endpoint exists."
#
#
# health.py may use Kubernetes to establish evidence such as:
#
#
#       "The backing workload has available replicas."
#
#
# path.py asks something different:
#
#
#       "Can Agent 11 reach the destination?"
#
#
# Kubernetes Service existence does not answer that question.
#
#
#       KUBERNETES SERVICE EXISTS
#           !=
#       CALLER CAN REACH SERVICE
#
#
#       ENDPOINTSLICE READY
#           !=
#       CALLER CAN REACH ENDPOINT
#
#
#       POD READY
#           !=
#       NETWORK PATH AVAILABLE
#
#
# ============================================================================


# ============================================================================
# KUBERNETES NETWORKPOLICY
# ============================================================================
#
# Kubernetes NetworkPolicy may influence connectivity.
#
#
# But:
#
#
#       NetworkPolicy
#
#
# is not:
#
#
#       Agent 11 DataRoutePolicy
#
#
# A NetworkPolicy may permit packets while Agent 11 policy prohibits data
# disclosure.
#
#
# Or Agent 11 policy may permit a destination while Kubernetes networking
# prevents connectivity.
#
#
# Therefore:
#
#
#       KUBERNETES NETWORK POLICY
#           !=
#       AGENT 11 DATA POLICY
#
#
#       PACKETS PERMITTED
#           !=
#       DATA AUTHORIZED
#
#
# ============================================================================


# ============================================================================
# CONTROL PLANE != DATA PLANE
# ============================================================================
#
# Suppose a VPN controller API is unavailable.
#
#
# That does not necessarily prove:
#
#
#       VPN data plane unavailable.
#
#
# Likewise:
#
#
#       Kubernetes API unavailable
#
#
# does not necessarily prove:
#
#
#       application traffic unavailable.
#
#
# Therefore:
#
#
#       CONTROL-PLANE FAILURE
#           !=
#       DATA-PLANE FAILURE
#
#
# This is another reason observation failure should often become:
#
#
#       UNKNOWN
#
#
# rather than:
#
#
#       UNAVAILABLE
#
#
# ============================================================================


# ============================================================================
# SYNTHETIC PROBE != COMPLETE NETWORK TRUTH
# ============================================================================
#
# A successful synthetic probe provides evidence.
#
# It does not establish every network property.
#
#
# Example:
#
#
#       TCP 443 reachable
#
#
# does not prove:
#
#
#       application inference succeeds
#
#       TLS identity is correct
#
#       service is healthy
#
#       destination is authorized
#
#
# Therefore:
#
#
#       PROBE SUCCESS != SERVICE HEALTH
#
#       PROBE SUCCESS != AUTHORIZATION
#
#
# ============================================================================


# ============================================================================
# DNS
# ============================================================================
#
# DNS may be part of reaching a destination.
#
#
# But:
#
#
#       DNS RESOLUTION SUCCESS
#           !=
#       PATH AVAILABLE
#
#
# DNS may resolve while packets cannot reach the destination.
#
#
# Likewise:
#
#
#       DNS FAILURE
#
#
# may make the destination unusable from the caller's perspective even when
# lower-level IP connectivity exists.
#
#
# Part II does not yet model DNS as a separate evidence dimension.
#
#
# ============================================================================


# ============================================================================
# TLS
# ============================================================================
#
# Similar distinction:
#
#
#       TCP CONNECTIVITY
#           !=
#       TLS SUCCESS
#
#
#       TLS SUCCESS
#           !=
#       AI AUTHORIZATION
#
#
# A future path or endpoint assessment may need to distinguish these layers.
#
# Part II does not yet require that complexity.
#
#
# ============================================================================


# ============================================================================
# SOURCE RELATIVITY
# ============================================================================
#
# Real infrastructure makes the relational nature of path evidence obvious.
#
#
# A synthetic probe executed in:
#
#
#       Tokyo
#
#
# establishes evidence about:
#
#
#       Tokyo -> destination
#
#
# It does not automatically establish evidence about:
#
#
#       Virginia -> destination
#
#
# Therefore the current:
#
#
#       service_id + path_type
#
#
# correlation remains intentionally incomplete.
#
#
# Part III should revisit explicit source identity.
#
#
# ============================================================================


# ============================================================================
# BGP
# ============================================================================
#
# Part II intentionally does NOT create:
#
#
#       BgpPathEvidenceSource
#
#
# yet.
#
#
# Why?
#
#
# Because BGP does not fit cleanly beside:
#
#
#       INTERNET
#
#       VPN
#
#       PRIVATE_LINK
#
#
# BGP supplies routing/control-plane evidence.
#
#
# For example:
#
#
#       PRIVATE CONNECTIVITY
#               |
#               +---- route learned via BGP
#
#
# The eventual architecture may look more like:
#
#
#       BGP route evidence
#               |
#               v
#       path assessment
#
#
# rather than:
#
#
#       BGP == PATH
#
#
# ============================================================================
# BGP ROUTE EXISTS != END-TO-END CONNECTIVITY
# ============================================================================
#
# Even when a BGP route exists:
#
#
#       firewall may block traffic
#
#       security policy may prohibit use
#
#       downstream route may fail
#
#       endpoint may be unhealthy
#
#       application may be unavailable
#
#
# Therefore:
#
#
#       BGP ROUTE EXISTS
#           !=
#       END-TO-END PATH AVAILABLE
#
#
# and certainly:
#
#
#       BGP ROUTE EXISTS
#           !=
#       AI AUTHORIZED
#
#
# ============================================================================


# ============================================================================
# OBSERVATION FAILURE
# ============================================================================
#
# This is one of the most important Part II rules.
#
#
# Suppose:
#
#
#       cloud networking API times out
#
#
# or:
#
#
#       VPN controller returns 503
#
#
# or:
#
#
#       monitoring system cannot be queried
#
#
# Correct:
#
#
#       UNKNOWN
#
#
# Incorrect:
#
#
#       UNAVAILABLE
#
#
# unless independent evidence actually establishes path failure.
#
#
#       OBSERVER FAILURE != OBSERVED SYSTEM FAILURE
#
#
# ============================================================================


# ============================================================================
# FAIL CLOSED WITHOUT LYING
# ============================================================================
#
# A later candidate evaluator may decide:
#
#
#       UNKNOWN path evidence
#           ->
#       candidate rejected
#
#
# That is fail-closed behavior.
#
#
# But path.py should continue to report:
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
# Therefore:
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ============================================================================


# ============================================================================
# AUTHENTICATION
# ============================================================================
#
# Real infrastructure adapters will need credentials.
#
#
# Examples:
#
#
#       cloud workload identity
#
#       service accounts
#
#       managed identities
#
#       API tokens
#
#       certificates
#
#
# Those credentials should be provided by application/infrastructure
# composition.
#
#
# Do NOT put:
#
#
#       passwords
#
#       API tokens
#
#       private keys
#
#       kubeconfig contents
#
#
# into Agent 11 path domain objects.
#
#
# ============================================================================


# ============================================================================
# OBSERVATION AUTHORITY != MUTATION AUTHORITY
# ============================================================================
#
# The identity used by a path observer should normally receive only the
# permissions required to observe the relevant infrastructure.
#
#
# It should not automatically receive authority to:
#
#
#       change routes
#
#       modify VPN tunnels
#
#       change firewall rules
#
#       modify SD-WAN policy
#
#       create private endpoints
#
#
# Therefore:
#
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#
# ============================================================================


# ============================================================================
# NO AUTOMATIC NETWORK REPAIR
# ============================================================================
#
# If Agent 11 observes:
#
#
#       VPN
#           UNAVAILABLE
#
#
# path.py should not immediately:
#
#
#       restart VPN
#
#       change routes
#
#       open firewall
#
#       advertise new BGP route
#
#
# That would cross:
#
#
#       observation
#
# into:
#
#
#       execution authority
#
#
# A safer future architecture is:
#
#
#       OBSERVE
#           ->
#       REASON
#           ->
#       RECOMMEND
#           ->
#       POLICY / APPROVAL
#           ->
#       AUTHORIZED EXECUTION
#
#
# ============================================================================


# ============================================================================
# TESTING THE INFRASTRUCTURE BOUNDARY
# ============================================================================
#
# We should be able to test:
#
#
#       NetworkPathEvaluator
#
#
# using:
#
#
#       StaticPathEvidenceSource
#
#
# without infrastructure.
#
#
# We should be able to test:
#
#
#       SyntheticReachabilityObserver
#
#
# using:
#
#
#       fake ReachabilityProbe
#
#
# without infrastructure.
#
#
# Vendor-specific observers should then be tested separately.
#
#
# This gives:
#
#
#       DOMAIN TESTS
#
#       ADAPTER TESTS
#
#       INFRASTRUCTURE INTEGRATION TESTS
#
#
# rather than one giant test requiring the entire network.
#
#
# ============================================================================


# ============================================================================
# EXAMPLE OBSERVATION FAILURE TEST
# ============================================================================
#
#
#     class FailingProbe:
#
#         def can_reach(
#             self,
#             service_id: str,
#             path_type: NetworkPathType,
#         ) -> bool:
#             raise PathObservationError(
#                 "Synthetic probe could not obtain evidence."
#             )
#
#
#     probe = FailingProbe()
#
#
#     observer = SyntheticReachabilityObserver(
#         probe=probe,
#     )
#
#
#     source = InfrastructurePathEvidenceSource(
#         observer=observer,
#     )
#
#
#     evaluator = NetworkPathEvaluator(
#         path_source=source,
#     )
#
#
#     state = evaluator.get_path_state(
#         service_id="company-cloud-primary",
#         path_type=NetworkPathType.PRIVATE_LINK,
#     )
#
#
#     assert state is NetworkPathState.UNKNOWN
#
#
# ============================================================================
# PART II INVARIANTS
# ============================================================================
#
#       REAL INFRASTRUCTURE != AGENT 11 DOMAIN
#
#       INFRASTRUCTURE OBSERVATION != AUTHORIZATION
#
#       PATH EVIDENCE != ROUTING DECISION
#
#       PATH EVIDENCE != SERVICE HEALTH
#
#       PATH EVIDENCE != MODEL CAPABILITY
#
#       PATH EVIDENCE != POLICY DECISION
#
#       PRIVATE != AUTHORIZED
#
#       PUBLIC != AUTOMATICALLY AUTHORIZED
#
#       KUBERNETES SERVICE EXISTS != CALLER CAN REACH SERVICE
#
#       ENDPOINTSLICE READY != CALLER CAN REACH ENDPOINT
#
#       POD READY != NETWORK PATH AVAILABLE
#
#       KUBERNETES NETWORK POLICY != AGENT 11 DATA POLICY
#
#       PACKETS PERMITTED != DATA AUTHORIZED
#
#       CONTROL-PLANE FAILURE != DATA-PLANE FAILURE
#
#       SYNTHETIC PROBE SUCCESS != SERVICE HEALTH
#
#       DNS RESOLUTION SUCCESS != PATH AVAILABLE
#
#       TCP CONNECTIVITY != TLS SUCCESS
#
#       BGP ROUTE EXISTS != END-TO-END CONNECTIVITY
#
#       BGP ROUTE EXISTS != AI AUTHORIZED
#
#       OBSERVATION FAILURE != PATH FAILURE
#
#       OBSERVER FAILURE != OBSERVED SYSTEM FAILURE
#
#       UNKNOWN != UNAVAILABLE
#
#       FAIL CLOSED != FALSIFY STATE
#
#       OBSERVE != REMEDIATE
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#       COMPONENT USES DEPENDENCY
#           !=
#       COMPONENT CHOOSES DEPENDENCY
#
#
# ============================================================================
# END OF PART II SAMPLE
# ============================================================================


# ============================================================================
# network/path.py
#
# PART III-A
#
# ROUTE EVIDENCE + BGP
# ============================================================================
#
# PURPOSE
# -------
#
# Parts I and II established operational network-path evidence.
#
#
# Part III-A introduces a DIFFERENT category of evidence:
#
#
#       ROUTE EVIDENCE
#
#
# Route evidence describes what the network CONTROL PLANE currently knows
# about reaching a destination.
#
#
# It does NOT by itself establish:
#
#
#       end-to-end connectivity
#
#       application availability
#
#       service health
#
#       model capability
#
#       data authorization
#
#       AI routing selection
#
#
# ============================================================================
# CENTRAL DISTINCTION
# ============================================================================
#
#
#       ROUTE EVIDENCE
#           !=
#       PATH EVIDENCE
#
#
#       PATH EVIDENCE
#           !=
#       SERVICE HEALTH
#
#
#       SERVICE HEALTH
#           !=
#       AUTHORIZATION
#
#
#       AUTHORIZATION
#           !=
#       AI ROUTING SELECTION
#
#
# ============================================================================
# BGP
# ============================================================================
#
# BGP is fundamentally a ROUTING PROTOCOL.
#
#
# It is not equivalent to:
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
# Those describe broad connectivity mechanisms.
#
#
# BGP exchanges information used by routers to determine how destinations
# may be reached.
#
#
# Therefore:
#
#
#       PATH TYPE != ROUTING PROTOCOL
#
#
# ============================================================================
# EXAMPLE
# ============================================================================
#
#
#       Agent 11
#           |
#           v
#       VPN
#           |
#           | routes learned using BGP
#           v
#       corporate network
#           |
#           v
#       inference endpoint
#
#
# Here:
#
#
#       VPN
#
#
# describes the connectivity mechanism.
#
#
#       BGP
#
#
# describes one mechanism through which routing information was learned.
#
#
# ============================================================================
# IMPORTANT
# ============================================================================
#
# A BGP route can exist while the data plane is broken.
#
#
# A BGP route can disappear while the destination remains healthy.
#
#
# BGP can select a network best path that Agent 11 policy may not permit
# for the current request.
#
#
# Therefore:
#
#
#       BGP ROUTE EXISTS != END-TO-END CONNECTIVITY
#
#       BGP BEST PATH != AGENT 11 BEST AI ROUTE
#
#       NETWORK CONVERGENCE != POLICY-COMPLIANT RECOVERY
#
#
# ============================================================================


from datetime import datetime, timezone
from enum import StrEnum
from typing import Protocol

from pydantic import Field, model_validator

from ..models.base_model import Agent11BaseModel


# ============================================================================
# NOTE ABOUT THESE ENUMS
# ============================================================================
#
# The enums below are shown here so Part III-A can be understood as one
# complete teaching block.
#
#
# In the actual Agent 11 project they should live with the existing network
# vocabulary in:
#
#
#       models/enums/network_enums.py
#
#
# and inherit:
#
#
#       Agent11Enum
#
#
# rather than defining another local enum hierarchy.
#
#
# Do not duplicate these definitions in production.
#
#
# ============================================================================


class RouteObservationState(StrEnum):
    """
    SAMPLE vocabulary describing what route observation established.

    PRESENT
        A successful observation established that a qualifying route exists.

    ABSENT
        A successful observation established that no qualifying route exists.

    UNKNOWN
        Current route state could not be established.

    STALE
        Route evidence exists, but it is too old to establish current state.
    """

    PRESENT = "present"
    ABSENT = "absent"
    UNKNOWN = "unknown"
    STALE = "stale"


class NetworkRoutingProtocol(StrEnum):
    """
    SAMPLE vocabulary describing how routing information was learned.

    BGP is explicitly separated from NetworkPathType.

    STATIC and CONNECTED are included because not every useful route is
    learned dynamically through BGP.

    OSPF is included as an example of another routing protocol that Agent 11
    may encounter in enterprise/on-prem infrastructure.

    UNKNOWN preserves uncertainty rather than inventing provenance.
    """

    BGP = "bgp"
    STATIC = "static"
    CONNECTED = "connected"
    OSPF = "ospf"
    UNKNOWN = "unknown"


# ============================================================================
# WHY PRESENT / ABSENT / UNKNOWN / STALE?
# ============================================================================
#
# A simple:
#
#
#       route_present: bool
#
#
# looks attractive.
#
#
# But:
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
#       observer successfully checked and found no route?
#
#
# or:
#
#
#       router API timed out?
#
#
# or:
#
#
#       evidence is 45 minutes old?
#
#
# or:
#
#
#       observer lacked permission?
#
#
# Those are not equivalent.
#
#
# Therefore:
#
#
#       ABSENT != UNKNOWN
#
#       UNKNOWN != STALE
#
#       STALE != ABSENT
#
#
# ============================================================================
# EPISTEMIC RULE
# ============================================================================
#
#
#       FAILED OBSERVATION
#           !=
#       NEGATIVE OBSERVATION
#
#
# ============================================================================
# FAIL-CLOSED RULE
# ============================================================================
#
# Candidate evaluation may eventually decide:
#
#
#       UNKNOWN
#           ->
#       insufficient evidence for viability
#
#
# or:
#
#
#       STALE
#           ->
#       insufficient evidence for viability
#
#
# But route evidence must preserve what is actually known.
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ============================================================================


# ============================================================================
# ROUTE EVIDENCE
# ============================================================================
#
# One RouteEvidence object represents one normalized observation about
# routing/control-plane state.
#
#
# It does NOT contain:
#
#
#       prompt data
#
#       AI response data
#
#       credentials
#
#       private keys
#
#       authorization decisions
#
#       AI routing decisions
#
#
# ============================================================================


class RouteEvidence(Agent11BaseModel):
    """
    Normalized evidence about a route to a destination.

    This model represents control-plane evidence.

    It does not establish end-to-end reachability.
    """

    source_id: str = Field(
        min_length=1,
        description=(
            "Logical identity of the location from which route "
            "state was observed."
        ),
    )

    destination: str = Field(
        min_length=1,
        description=(
            "Logical destination or destination prefix represented "
            "by this route evidence."
        ),
    )

    protocol: NetworkRoutingProtocol = Field(
        description=(
            "Routing mechanism associated with the observed route."
        ),
    )

    state: RouteObservationState = Field(
        description=(
            "What the route observation established."
        ),
    )

    observed_at: datetime = Field(
        description=(
            "Time at which the route state was observed."
        ),
    )


# ============================================================================
# IMPORTANT MODELING CHOICE
# ============================================================================
#
# RouteEvidence does NOT contain:
#
#
#       authorized: bool
#
#
# because route observation cannot establish authorization.
#
#
# It does NOT contain:
#
#
#       path_available: bool
#
#
# because route observation cannot establish end-to-end path availability.
#
#
# It does NOT contain:
#
#
#       service_healthy: bool
#
#
# because route observation cannot establish AI service health.
#
#
# ============================================================================
# ROUTE EVIDENCE DESCRIBES ONLY ITS OWN DOMAIN
# ============================================================================


# ============================================================================
# TIMESTAMPS
# ============================================================================
#
# Route evidence is temporal.
#
#
#       ROUTE OBSERVED THEN
#           !=
#       ROUTE CONFIRMED NOW
#
#
# observed_at records when the observation was made.
#
#
# It does NOT itself decide whether the evidence is stale.
#
#
# Freshness is assessment behavior.
#
#
# ============================================================================
# HISTORICAL EVIDENCE SHOULD REMAIN HISTORICAL
# ============================================================================
#
# Suppose:
#
#
#       10:00
#           route PRESENT
#
#
#       10:20
#           evidence now considered stale
#
#
# We should not rewrite the original evidence:
#
#
#       PRESENT
#           ->
#       STALE
#
#
# if the evidence object represents what was actually observed at 10:00.
#
#
# A richer future design may distinguish:
#
#
#       OBSERVATION STATE
#
# from:
#
#
#       EVIDENCE FRESHNESS
#
#
# This sample keeps STALE in the vocabulary to make the concept visible,
# but the production model should revisit whether freshness deserves its own
# dimension.
#
#
#       STALE EVIDENCE != FALSE EVIDENCE
#
#
# ============================================================================


# ============================================================================
# IMPORTANT DESIGN QUESTION FOR FUTURE SELF
# ============================================================================
#
# There are two possible mature designs:
#
#
# DESIGN A
#
#       RouteObservationState
#           PRESENT
#           ABSENT
#           UNKNOWN
#           STALE
#
#
# DESIGN B
#
#       RouteObservationState
#           PRESENT
#           ABSENT
#           UNKNOWN
#
#       EvidenceFreshness
#           FRESH
#           STALE
#
#
# Design B is semantically cleaner because:
#
#
#       PRESENT + STALE
#
#
# is meaningful.
#
#
# It means:
#
#
#       "A route was observed,
#        but the observation is no longer current enough."
#
#
# Do not add the second dimension until freshness behavior is actually
# implemented.
#
#
# ============================================================================


# ============================================================================
# ROUTE OBSERVATION ERROR
# ============================================================================
#
# Infrastructure observation failures must remain distinct from:
#
#
#       route ABSENT
#
#
# Examples:
#
#
#       router API timeout
#
#       FRRouting API unavailable
#
#       GoBGP connection failed
#
#       authorization failure
#
#       malformed infrastructure response
#
#
# These are observation problems.
#
#
# They are not proof that the destination route disappeared.
#
#
# ============================================================================


class RouteObservationError(RuntimeError):
    """
    Expected failure while attempting to obtain route evidence.

    This represents inability to establish current route state.

    It does not mean that the route is absent.
    """


# ============================================================================
# ROUTE EVIDENCE PROVIDER
# ============================================================================
#
# Generic Agent 11 behavior should depend upon:
#
#
#       RouteEvidenceProvider
#
#
# rather than:
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


class RouteEvidenceProvider(Protocol):
    """
    Behavioral contract for collecting normalized route evidence.

    Infrastructure-specific implementations translate their native routing
    state into Agent 11's route-evidence vocabulary.
    """

    def collect_route_evidence(
        self,
        source_id: str,
        destination: str,
    ) -> RouteEvidence:
        """
        Collect current route evidence.

        A successful observation should return RouteEvidence.

        Expected infrastructure observation failures should raise:

            RouteObservationError

        Programming defects should not be silently converted into UNKNOWN.
        """
        ...


# ============================================================================
# ROUTE EVIDENCE EVALUATOR
# ============================================================================
#
# This evaluator provides a generic Agent 11 boundary around route evidence.
#
#
# It does NOT know:
#
#
#       BGP CLI syntax
#
#       router vendor
#
#       cloud provider
#
#       network credentials
#
#       AS_PATH
#
#       LOCAL_PREF
#
#       MED
#
#
# ============================================================================


class RouteEvidenceEvaluator:
    """
    Generic behavior for obtaining route evidence from an injected provider.

    Dependency direction:

        RouteEvidenceEvaluator
                |
                v
        RouteEvidenceProvider
                ^
                |
        infrastructure adapter
    """

    def __init__(
        self,
        route_provider: RouteEvidenceProvider,
    ) -> None:
        self._route_provider = route_provider

    def get_route_evidence(
        self,
        source_id: str,
        destination: str,
    ) -> RouteEvidence:
        """
        Obtain normalized route evidence.

        Expected observation failure becomes explicit UNKNOWN evidence.

        Unexpected programming errors remain visible.
        """

        try:
            return self._route_provider.collect_route_evidence(
                source_id=source_id,
                destination=destination,
            )

        except RouteObservationError:
            return RouteEvidence(
                source_id=source_id,
                destination=destination,
                protocol=NetworkRoutingProtocol.UNKNOWN,
                state=RouteObservationState.UNKNOWN,
                observed_at=datetime.now(timezone.utc),
            )


# ============================================================================
# WHY CATCH ONLY RouteObservationError?
# ============================================================================
#
# Do NOT write:
#
#
#       except Exception:
#           return UNKNOWN
#
#
# That can hide:
#
#
#       TypeError
#
#       AttributeError
#
#       broken mapping logic
#
#       malformed application state
#
#       programmer mistakes
#
#
# Those should normally fail loudly during testing.
#
#
# ============================================================================
# EXPECTED INFRASTRUCTURE FAILURE != PROGRAMMING DEFECT
# ============================================================================


# ============================================================================
# STATIC ROUTE PROVIDER
# ============================================================================
#
# Students should be able to learn route semantics before touching a router.
#
#
# This also provides deterministic unit-test evidence.
#
#
# ============================================================================


class StaticRouteEvidenceProvider:
    """
    Deterministic in-memory route-evidence provider.

    Evidence is keyed by:

        (source_id, destination)

    Missing evidence produces UNKNOWN rather than ABSENT.

    Why?

        No configured evidence
            !=
        route successfully observed as absent
    """

    def __init__(
        self,
        route_evidence: dict[
            tuple[str, str],
            RouteEvidence,
        ],
    ) -> None:
        self._route_evidence = dict(route_evidence)

    def collect_route_evidence(
        self,
        source_id: str,
        destination: str,
    ) -> RouteEvidence:
        evidence = self._route_evidence.get(
            (source_id, destination)
        )

        if evidence is None:
            return RouteEvidence(
                source_id=source_id,
                destination=destination,
                protocol=NetworkRoutingProtocol.UNKNOWN,
                state=RouteObservationState.UNKNOWN,
                observed_at=datetime.now(timezone.utc),
            )

        if evidence.source_id != source_id:
            raise ValueError(
                "Stored route evidence does not match "
                "the requested source."
            )

        if evidence.destination != destination:
            raise ValueError(
                "Stored route evidence does not match "
                "the requested destination."
            )

        return evidence


# ============================================================================
# STATIC EXAMPLE
# ============================================================================
#
#
#     evidence = RouteEvidence(
#         source_id="agent11-tokyo",
#         destination="10.50.0.0/16",
#         protocol=NetworkRoutingProtocol.BGP,
#         state=RouteObservationState.PRESENT,
#         observed_at=datetime.now(timezone.utc),
#     )
#
#
#     provider = StaticRouteEvidenceProvider(
#         route_evidence={
#             (
#                 "agent11-tokyo",
#                 "10.50.0.0/16",
#             ): evidence,
#         }
#     )
#
#
#     evaluator = RouteEvidenceEvaluator(
#         route_provider=provider,
#     )
#
#
#     result = evaluator.get_route_evidence(
#         source_id="agent11-tokyo",
#         destination="10.50.0.0/16",
#     )
#
#
#     assert result.state is RouteObservationState.PRESENT
#
#
# ============================================================================
# WHAT DID WE ESTABLISH?
# ============================================================================
#
#
#       route evidence says PRESENT
#
#
# We did NOT establish:
#
#
#       endpoint reachable
#
#       TCP reachable
#
#       TLS works
#
#       AI service healthy
#
#       AI request authorized
#
#
# ============================================================================


# ============================================================================
# BGP ADAPTER BOUNDARY
# ============================================================================
#
# Now we can introduce the actual BGP seam.
#
#
#       FRRouting / GoBGP / Router API
#                    |
#                    v
#              BGP reader
#                    |
#                    v
#       BgpRouteEvidenceProvider
#                    |
#                    v
#              RouteEvidence
#
#
# The low-level reader understands BGP implementation details.
#
#
# The provider translates those details into Agent 11 evidence.
#
#
# ============================================================================


class BgpRouteReader(Protocol):
    """
    Low-level behavioral contract for reading BGP route state.

    This is intentionally below Agent 11's normalized route-evidence model.

    A future implementation might use:

        FRRouting

        GoBGP

        router REST API

        router gRPC API

        network controller

        cloud route telemetry
    """

    def route_exists(
        self,
        destination: str,
    ) -> bool:
        """
        Return True when a successful BGP observation establishes that
        a qualifying route exists.

        Return False when a successful observation establishes that no
        qualifying route exists.

        Raise RouteObservationError when current route state cannot be
        established.
        """
        ...


# ============================================================================
# SIMPLE BGP ROUTE EVIDENCE PROVIDER
# ============================================================================
#
# This is deliberately the FIRST BGP implementation.
#
#
# It asks only:
#
#
#       "Does a qualifying BGP route exist?"
#
#
# It does NOT yet expose:
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
#       communities
#
#       best-path reason
#
#       RIB/FIB distinction
#
#
# Those concepts come later only when Agent 11 actually needs them.
#
#
# ============================================================================


class BgpRouteEvidenceProvider:
    """
    Translate low-level BGP route observation into Agent 11 RouteEvidence.

    This provider does not interpret BGP route existence as end-to-end
    connectivity.
    """

    def __init__(
        self,
        source_id: str,
        bgp_reader: BgpRouteReader,
    ) -> None:
        self._source_id = source_id
        self._bgp_reader = bgp_reader

    def collect_route_evidence(
        self,
        source_id: str,
        destination: str,
    ) -> RouteEvidence:
        """
        Collect normalized BGP route evidence.

        The provider is configured for one logical observation source.

        Supplying a different source_id is treated as a caller/configuration
        error rather than silently querying the wrong network location.
        """

        if source_id != self._source_id:
            raise ValueError(
                "The requested source does not match the "
                "configured BGP observation source."
            )

        route_exists = self._bgp_reader.route_exists(
            destination=destination,
        )

        state = (
            RouteObservationState.PRESENT
            if route_exists
            else RouteObservationState.ABSENT
        )

        return RouteEvidence(
            source_id=source_id,
            destination=destination,
            protocol=NetworkRoutingProtocol.BGP,
            state=state,
            observed_at=datetime.now(timezone.utc),
        )


# ============================================================================
# WHY SOURCE IDENTITY IS CONFIGURED
# ============================================================================
#
# Route state is observer-relative.
#
#
# Example:
#
#
#       Tokyo router
#           ->
#       10.50.0.0/16
#           PRESENT
#
#
#       Virginia router
#           ->
#       10.50.0.0/16
#           ABSENT
#
#
# Both observations may be correct.
#
#
# Therefore:
#
#
#       ROUTE STATE IS SOURCE-RELATIVE
#
#
# ============================================================================
# SOURCE A != SOURCE B
# ============================================================================
#
# A BGP provider configured for:
#
#
#       agent11-tokyo
#
#
# should not silently answer a query claiming to represent:
#
#
#       agent11-virginia
#
#
# That would corrupt evidence provenance.
#
#
# ============================================================================


# ============================================================================
# SAMPLE LOW-LEVEL BGP READER
# ============================================================================
#
# This remains deterministic so students can understand the BGP adapter
# before connecting FRRouting or another implementation.
#
#
# ============================================================================


class StaticBgpRouteReader:
    """
    Deterministic teaching implementation of BgpRouteReader.

    The set contains destinations for which the simulated BGP observer
    currently reports a route.
    """

    def __init__(
        self,
        known_routes: set[str],
    ) -> None:
        self._known_routes = set(known_routes)

    def route_exists(
        self,
        destination: str,
    ) -> bool:
        return destination in self._known_routes


# ============================================================================
# COMPLETE BGP TEACHING CHAIN
# ============================================================================
#
#
#       StaticBgpRouteReader
#               |
#               v
#       BgpRouteEvidenceProvider
#               |
#               v
#       RouteEvidenceEvaluator
#               |
#               v
#          RouteEvidence
#
#
# Example:
#
#
#     bgp_reader = StaticBgpRouteReader(
#         known_routes={
#             "10.50.0.0/16",
#         }
#     )
#
#
#     provider = BgpRouteEvidenceProvider(
#         source_id="agent11-tokyo",
#         bgp_reader=bgp_reader,
#     )
#
#
#     evaluator = RouteEvidenceEvaluator(
#         route_provider=provider,
#     )
#
#
#     result = evaluator.get_route_evidence(
#         source_id="agent11-tokyo",
#         destination="10.50.0.0/16",
#     )
#
#
#     assert result.protocol is NetworkRoutingProtocol.BGP
#
#     assert result.state is RouteObservationState.PRESENT
#
#
# ============================================================================
# AGAIN: WHAT DID THIS PROVE?
# ============================================================================
#
#
#       BGP route observed.
#
#
# Period.
#
#
# ============================================================================


# ============================================================================
# BGP ROUTE EXISTS != END-TO-END CONNECTIVITY
# ============================================================================
#
# Suppose:
#
#
#       BGP
#           route PRESENT
#
#
# but:
#
#
#       synthetic TCP probe
#           fails
#
#
# This is not automatically contradictory.
#
#
# The observers measure different layers.
#
#
# ============================================================================
# POSSIBLE CAUSES
# ============================================================================
#
#
#       firewall
#
#       ACL
#
#       downstream route failure
#
#       tunnel failure
#
#       black hole
#
#       asymmetric routing
#
#       endpoint failure
#
#       transport failure
#
#
# Therefore:
#
#
#       ROUTE PRESENT != PATH AVAILABLE
#
#
# ============================================================================


# ============================================================================
# CONTROL PLANE != DATA PLANE
# ============================================================================
#
# BGP primarily contributes CONTROL-PLANE evidence.
#
#
# Synthetic reachability contributes DATA-PLANE evidence.
#
#
# Conceptually:
#
#
#       CONTROL PLANE
#
#           BGP says:
#
#               "I know how this destination should be reached."
#
#
#                   |
#                   v
#
#       DATA PLANE
#
#           probe says:
#
#               "Traffic actually reaches the destination."
#
#
#                   |
#                   v
#
#       APPLICATION PLANE
#
#           AI service says:
#
#               "Inference actually works."
#
#
# ============================================================================
# THREE DIFFERENT QUESTIONS
# ============================================================================
#
#
#       ROUTE KNOWN?
#
#       PACKETS FLOW?
#
#       APPLICATION WORKS?
#
#
# Do not collapse them.
#
#
# ============================================================================


# ============================================================================
# BGP RIB / FIB
# ============================================================================
#
# Students will eventually encounter another distinction:
#
#
#       RIB
#           Routing Information Base
#
#
#       FIB
#           Forwarding Information Base
#
#
# A route may be learned by BGP without becoming the route actually used for
# forwarding.
#
#
# Therefore:
#
#
#       BGP LEARNED ROUTE
#           !=
#       FORWARDING ENTRY
#
#
# ============================================================================
# FUTURE QUESTION
# ============================================================================
#
# Does Agent 11 need:
#
#
#       route learned?
#
#       route selected?
#
#       route installed?
#
#       route forwarded?
#
#
# Maybe.
#
#
# But not yet.
#
#
# The first implementation asks only:
#
#
#       "Did our BGP observer establish
#        a qualifying route?"
#
#
# ============================================================================


# ============================================================================
# BGP BEST PATH
# ============================================================================
#
# BGP may receive multiple routes for the same prefix.
#
#
# It applies BGP selection rules to choose a preferred network route.
#
#
# Agent 11 must not confuse that with AI-service selection.
#
#
#       BGP BEST PATH
#           !=
#       AGENT 11 BEST AI ROUTE
#
#
# ============================================================================
# DIFFERENT OPTIMIZATION DOMAINS
# ============================================================================
#
# BGP cares about network routing semantics.
#
#
# Agent 11 cares about:
#
#
#       policy
#
#       capability
#
#       service availability
#
#       network viability
#
#       potentially cost
#
#       potentially latency
#
#
# The two systems solve different problems.
#
#
# ============================================================================


# ============================================================================
# LOCAL_PREF
# ============================================================================
#
# BGP LOCAL_PREF can influence which network route is preferred.
#
#
# It must not become:
#
#
#       Agent 11 AI service preference
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
# ============================================================================


# ============================================================================
# AS_PATH
# ============================================================================
#
# BGP may expose an AS_PATH such as:
#
#
#       64512 64520 64530
#
#
# This may be operationally important for network routing.
#
#
# It does NOT tell Agent 11:
#
#
#       which model is better
#
#       which service is cheaper
#
#       which destination is authorized
#
#       which inference result is safer
#
#
# ============================================================================
# SHORTER AS_PATH != BETTER AI DESTINATION
# ============================================================================


# ============================================================================
# MED
# ============================================================================
#
# MULTI_EXIT_DISC / MED may influence route preference between neighboring
# autonomous systems.
#
#
# It is not:
#
#
#       model score
#
#       security score
#
#       policy score
#
#
# ============================================================================
# NETWORK METRIC != AI POLICY
# ============================================================================


# ============================================================================
# BGP COMMUNITIES
# ============================================================================
#
# BGP communities can encode network-routing intent or operational metadata.
#
#
# Future Agent 11 infrastructure adapters might consume selected community
# information.
#
#
# But:
#
#
#       BGP COMMUNITY
#           !=
#       AGENT 11 AUTHORIZATION
#
#
# unless an explicit, trusted policy integration is deliberately designed.
#
#
# ============================================================================
# METADATA != AUTHORITY
# ============================================================================
#
# If infrastructure metadata ever influences security decisions:
#
#
#       who may write it?
#
#       who may modify it?
#
#       how is it authenticated?
#
#       how is it audited?
#
#
# must become part of the trust model.
#
#
# ============================================================================


# ============================================================================
# NEXT HOP
# ============================================================================
#
# A BGP route may advertise a next hop.
#
#
# A next hop being present does not prove:
#
#
#       next hop reachable
#
#       downstream path works
#
#       destination works
#
#
# ============================================================================
#
#
#       NEXT HOP KNOWN != NEXT HOP REACHABLE
#
#       NEXT HOP REACHABLE != DESTINATION REACHABLE
#
#
# ============================================================================


# ============================================================================
# ROUTE RECURSION
# ============================================================================
#
# Networks may require recursive resolution:
#
#
#       destination
#           ->
#       next hop
#           ->
#       route to next hop
#           ->
#       interface
#
#
# Agent 11 does not need to become a router implementation merely because
# routers perform this work.
#
#
# ============================================================================
#
#
#       AGENT 11 CONSUMES NETWORK EVIDENCE.
#
#       AGENT 11 DOES NOT REIMPLEMENT THE NETWORK STACK.
#
#
# ============================================================================


# ============================================================================
# BGP SESSION STATE
# ============================================================================
#
# Future observers may inspect BGP peer state:
#
#
#       IDLE
#
#       CONNECT
#
#       ACTIVE
#
#       OPEN_SENT
#
#       OPEN_CONFIRM
#
#       ESTABLISHED
#
#
# But:
#
#
#       BGP SESSION ESTABLISHED
#           !=
#       REQUIRED ROUTE PRESENT
#
#
# A session may be established while the desired prefix is absent.
#
#
# Likewise:
#
#
#       BGP SESSION DOWN
#           !=
#       DESTINATION UNREACHABLE
#
#
# another route may exist.
#
#
# ============================================================================


# ============================================================================
# ROUTE WITHDRAWAL
# ============================================================================
#
# Suppose:
#
#
#       BGP route to inference network
#           PRESENT
#
#
# then:
#
#
#       route withdrawn
#
#
# That establishes a change in route evidence.
#
#
# It does NOT establish:
#
#
#       AI service crashed
#
#
# ============================================================================
#
#
#       ROUTE WITHDRAWAL != SERVICE FAILURE
#
#
# ============================================================================


# ============================================================================
# DESTINATION HEALTH CAN REMAIN PERFECT
# ============================================================================
#
#
#       AI service
#           AVAILABLE
#
#
# while:
#
#
#       caller route
#           ABSENT
#
#
# Both are valid.
#
#
# ============================================================================
#
#
#       SERVICE AVAILABLE
#           +
#       PATH UNAVAILABLE
#           =
#       ROUTE NOT VIABLE FROM THIS CALLER
#
#
# Eventually candidate evaluation interprets that.
#
#
# ============================================================================


# ============================================================================
# MULTIPLE BGP ROUTES
# ============================================================================
#
# One destination may have several BGP routes.
#
#
# Example:
#
#
#       10.50.0.0/16
#
#           route A
#               next hop X
#
#           route B
#               next hop Y
#
#
# Our first RouteEvidence contract deliberately does not represent each
# individual BGP path.
#
#
# Why?
#
#
# Because SEIR-I / early SEIR-II only needs:
#
#
#       qualifying route present?
#
#
# ============================================================================
# FUTURE-AWARE != FUTURE-BLOATED
# ============================================================================


# ============================================================================
# WHEN MULTIPLE ROUTES BECOME DOMAIN-RELEVANT
# ============================================================================
#
# Agent 11 may eventually need richer evidence when:
#
#
#       routes correspond to different failure domains
#
#       routes correspond to different jurisdictions
#
#       routes correspond to different network exposures
#
#       routes correspond to different cloud connections
#
#       path-specific policy exists
#
#
# At that point a richer model may be earned.
#
#
# Possible future concepts:
#
#
#       BgpRouteEvidence
#
#       RoutePath
#
#       RouteCandidate
#
#       NextHopEvidence
#
#
# None are commitments today.
#
#
# ============================================================================


# ============================================================================
# BGP CONVERGENCE
# ============================================================================
#
# BGP convergence is one of the most important future failure scenarios for
# Agent 11.
#
#
# Suppose:
#
#
#       PRIVATE PATH
#           preferred
#
#
# fails.
#
#
# BGP converges.
#
#
# Another route becomes available.
#
#
# Network engineers may correctly say:
#
#
#       "Connectivity recovered."
#
#
# But Agent 11 must still ask:
#
#
#       "Is the newly realized path permitted
#        for this request?"
#
#
# ============================================================================
# CRITICAL
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
# EXAMPLE: DANGEROUS SUCCESS
# ============================================================================
#
#
#       BEFORE FAILURE
#
#
#       Agent 11
#           |
#           | private connection
#           v
#       company inference
#
#
#       E9 permitted
#
#
# ---------------------------------------------------------------------------
#
#
#       PRIVATE ROUTE WITHDRAWN
#
#
# ---------------------------------------------------------------------------
#
#
#       BGP CONVERGES
#
#
#       Agent 11
#           |
#           | Internet
#           v
#       company inference
#
#
# Network:
#
#
#       SUCCESS
#
#
# Agent 11 policy:
#
#
#       POSSIBLY DENIED
#
#
# ============================================================================
# THE DESTINATION DID NOT CHANGE.
#
# THE REALIZED NETWORK PATH DID.
# ============================================================================
#
# This is why future path-specific authorization may become necessary.
#
#
# ============================================================================


# ============================================================================
# BGP DOES NOT REDUCE POLICY
# ============================================================================
#
# Network failover may increase operational availability.
#
#
# It must not silently reduce security requirements.
#
#
# ============================================================================
#
#
#       FALLBACK MAY REDUCE AVAILABILITY.
#
#       FALLBACK NEVER REDUCES SECURITY POLICY.
#
#
# ============================================================================


# ============================================================================
# ROUTE LEAKS
# ============================================================================
#
# BGP introduces another future security scenario:
#
#
#       route leak
#
#
# A route may become visible somewhere it was not intended to be visible.
#
#
# Therefore:
#
#
#       ROUTE PRESENT
#
#
# does not necessarily mean:
#
#
#       ROUTE INTENDED
#
#
# ============================================================================
#
#
#       DISCOVERED != TRUSTED
#
#
#       ROUTE PRESENT != ROUTE AUTHORIZED
#
#
# ============================================================================


# ============================================================================
# BGP HIJACKING
# ============================================================================
#
# Similar reasoning applies to route hijacking.
#
#
# Agent 11 must not eventually interpret:
#
#
#       route exists
#
#
# as:
#
#
#       destination identity verified
#
#
# ============================================================================
#
#
#       ROUTE REACHABILITY != DESTINATION IDENTITY
#
#
# ============================================================================


# ============================================================================
# NETWORK SECURITY BOUNDARY
# ============================================================================
#
# Future network evidence may therefore interact with:
#
#
#       route origin validation
#
#       RPKI
#
#       expected prefixes
#
#       trusted peers
#
#       expected AS paths
#
#
# But those should become explicit security/evidence requirements rather than
# hidden assumptions inside:
#
#
#       route_exists()
#
#
# ============================================================================


# ============================================================================
# RPKI
# ============================================================================
#
# Future BGP security may introduce:
#
#
#       VALID
#
#       INVALID
#
#       NOT_FOUND
#
#
# route-origin validation states.
#
#
# Those are NOT:
#
#
#       AVAILABLE
#
#       UNAVAILABLE
#
#
# They describe a different dimension.
#
#
# ============================================================================
#
#
#       ROUTE ORIGIN VALIDITY
#           !=
#       ROUTE AVAILABILITY
#
#
# ============================================================================


# ============================================================================
# MULTI-CLOUD BGP
# ============================================================================
#
# Agent 11 may eventually observe routing across:
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
#       on-prem
#
#
# BGP may participate in several of those connections.
#
#
# Example:
#
#
#       on-prem
#          |
#          +---- AWS Direct Connect
#          |        |
#          |        +---- BGP
#          |
#          +---- Azure ExpressRoute
#          |        |
#          |        +---- BGP
#          |
#          +---- GCP Cloud Interconnect
#                   |
#                   +---- BGP
#
#
# BGP remains network evidence.
#
#
# It does not redefine:
#
#
#       AIRoute.COMPANY_CLOUD_LLM
#
#
# ============================================================================
#
#
#       ROUTING DOMAIN != CLOUD PROVIDER
#
#       CLOUD PROVIDER != ROUTING PROTOCOL
#
#       ROUTING PROTOCOL != NETWORK PATH TYPE
#
#
# ============================================================================


# ============================================================================
# MULTI-CLOUD ROUTE EVIDENCE
# ============================================================================
#
# Future adapters may gather route evidence from:
#
#
#       AWS networking
#
#       Azure networking
#
#       GCP Cloud Router
#
#       OCI DRG
#
#       physical routers
#
#       FRRouting
#
#       GoBGP
#
#
# They should normalize only the information Agent 11 actually needs.
#
#
# ============================================================================
#
#
#       INFRASTRUCTURE COMPLEXITY
#           SHOULD BE TRANSLATED,
#           NOT REPLICATED.
#
#
# ============================================================================


# ============================================================================
# ROUTE EVIDENCE PROVENANCE
# ============================================================================
#
# Eventually Agent 11 may need to know:
#
#
#       which observer produced the evidence?
#
#       which router?
#
#       which cluster?
#
#       which region?
#
#       which controller?
#
#       which account?
#
#
# Current:
#
#
#       source_id
#
#
# is intentionally simple.
#
#
# Do not add twelve provenance fields until the trust model actually requires
# them.
#
#
# ============================================================================


# ============================================================================
# SOURCE KNOWN != SOURCE TRUSTED
# ============================================================================
#
# Knowing:
#
#
#       source_id = "tokyo-router"
#
#
# does not establish:
#
#
#       evidence is trustworthy.
#
#
# Future evidence trust may require:
#
#
#       authenticated observer identity
#
#       protected telemetry
#
#       signed evidence
#
#       access control
#
#       audit
#
#
# ============================================================================
#
#
#       SOURCE KNOWN != SOURCE AUTHORITATIVE
#
#       VALID PYDANTIC MODEL != TRUSTED EVIDENCE
#
#
# ============================================================================


# ============================================================================
# BGP API AUTHORITY
# ============================================================================
#
# Agent 11's BGP observer should normally receive READ authority.
#
#
# It does not need:
#
#
#       route advertisement authority
#
#       neighbor configuration authority
#
#       prefix withdrawal authority
#
#       router configuration authority
#
#
# ============================================================================
#
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#
# ============================================================================


# ============================================================================
# OBSERVE != REMEDIATE
# ============================================================================
#
# If Agent 11 observes:
#
#
#       route ABSENT
#
#
# it must not automatically:
#
#
#       advertise prefix
#
#       establish BGP neighbor
#
#       modify LOCAL_PREF
#
#       alter MED
#
#       change communities
#
#       modify route maps
#
#
# Those are network-control actions.
#
#
# ============================================================================
#
#
#       OBSERVE != REMEDIATE
#
#       DETECT != ACT
#
#
# ============================================================================


# ============================================================================
# REASONING AUTHORITY != NETWORK AUTHORITY
# ============================================================================
#
# Even if an AI system correctly reasons:
#
#
#       "Changing LOCAL_PREF would restore the desired route."
#
#
# that does not mean it possesses authority to make the change.
#
#
# ============================================================================
#
#
#       REASONING AUTHORIZATION
#           !=
#       EXECUTION AUTHORIZATION
#
#
# ============================================================================


# ============================================================================
# FUTURE SAFE NETWORK-AUTOMATION CHAIN
# ============================================================================
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
#       AUDIT
#
#
# path.py does not implement that workflow.
#
#
# ============================================================================


# ============================================================================
# ROUTE EVIDENCE AND CANDIDATE EVALUATION
# ============================================================================
#
# Route evidence should eventually contribute to:
#
#
#       NetworkPathAssessment
#
#
# not directly to:
#
#
#       AIRouter
#
#
# Intended future flow:
#
#
#       BGP
#        |
#        v
#   RouteEvidence
#        |
#        |
#        +--------------------+
#                             |
#   Data-plane evidence ------+
#                             |
#                             v
#                   NetworkPathAssessment
#                             |
#                             v
#                    CandidateEvaluator
#                             |
#                             v
#                    RoutingCandidate
#                             |
#                             v
#                        AIRouter
#
#
# ============================================================================


# ============================================================================
# AIRouter MUST REMAIN BORING
# ============================================================================
#
# AIRouter should never need:
#
#
#       AS_PATH
#
#       LOCAL_PREF
#
#       MED
#
#       BGP communities
#
#       BGP session state
#
#       RPKI
#
#
# If AIRouter needs those things, the network/candidate-evaluation boundary
# has probably collapsed.
#
#
# ============================================================================


# ============================================================================
# TEST: ROUTE PRESENT
# ============================================================================
#
#
#     reader = StaticBgpRouteReader(
#         known_routes={
#             "10.50.0.0/16",
#         }
#     )
#
#
#     provider = BgpRouteEvidenceProvider(
#         source_id="agent11-tokyo",
#         bgp_reader=reader,
#     )
#
#
#     evaluator = RouteEvidenceEvaluator(provider)
#
#
#     evidence = evaluator.get_route_evidence(
#         source_id="agent11-tokyo",
#         destination="10.50.0.0/16",
#     )
#
#
#     assert evidence.state is RouteObservationState.PRESENT
#
#
# ============================================================================


# ============================================================================
# TEST: ROUTE ABSENT
# ============================================================================
#
#
#     reader = StaticBgpRouteReader(
#         known_routes=set()
#     )
#
#
#     provider = BgpRouteEvidenceProvider(
#         source_id="agent11-tokyo",
#         bgp_reader=reader,
#     )
#
#
#     evaluator = RouteEvidenceEvaluator(provider)
#
#
#     evidence = evaluator.get_route_evidence(
#         source_id="agent11-tokyo",
#         destination="10.50.0.0/16",
#     )
#
#
#     assert evidence.state is RouteObservationState.ABSENT
#
#
# ============================================================================
# IMPORTANT
# ============================================================================
#
# This ABSENT result means:
#
#
#       the BGP reader successfully established
#       that the qualifying route was absent.
#
#
# It does NOT mean:
#
#
#       the AI service is down.
#
#
# ============================================================================


# ============================================================================
# TEST: OBSERVATION FAILURE
# ============================================================================
#
#
#     class FailingBgpReader:
#
#         def route_exists(
#             self,
#             destination: str,
#         ) -> bool:
#             raise RouteObservationError(
#                 "BGP observer unavailable."
#             )
#
#
#     provider = BgpRouteEvidenceProvider(
#         source_id="agent11-tokyo",
#         bgp_reader=FailingBgpReader(),
#     )
#
#
#     evaluator = RouteEvidenceEvaluator(provider)
#
#
#     evidence = evaluator.get_route_evidence(
#         source_id="agent11-tokyo",
#         destination="10.50.0.0/16",
#     )
#
#
#     assert evidence.state is RouteObservationState.UNKNOWN
#
#
# ============================================================================
# IMPORTANT
# ============================================================================
#
#
#       OBSERVATION FAILURE
#           ->
#       UNKNOWN
#
#
# not:
#
#
#       OBSERVATION FAILURE
#           ->
#       ABSENT
#
#
# ============================================================================


# ============================================================================
# TEST: SOURCE MISMATCH
# ============================================================================
#
# A Tokyo provider must not pretend to provide Virginia evidence.
#
#
#     provider = BgpRouteEvidenceProvider(
#         source_id="agent11-tokyo",
#         bgp_reader=reader,
#     )
#
#
#     provider.collect_route_evidence(
#         source_id="agent11-virginia",
#         destination="10.50.0.0/16",
#     )
#
#
# should raise:
#
#
#       ValueError
#
#
# ============================================================================
#
#
#       EVIDENCE PROVENANCE MISMATCH
#           !=
#       NETWORK UNCERTAINTY
#
#
# ============================================================================


# ============================================================================
# QUERY VS ASSERTION
# ============================================================================
#
# Notice the difference:
#
#
# StaticRouteEvidenceProvider searches a collection:
#
#
#       missing key
#           ->
#       UNKNOWN
#
#
# BgpRouteEvidenceProvider is explicitly configured for one source:
#
#
#       mismatched source
#           ->
#       ValueError
#
#
# This follows:
#
#
#       QUERY COLLECTION != ASSERT OBJECT PAIR
#
#
# ============================================================================


# ============================================================================
# BGP LAB — THE SUFFERING BEGINS
# ============================================================================
#
# SCENARIO:
#
#
#       company inference service
#           HEALTHY
#
#
#       private VPN
#           AVAILABLE
#
#
#       BGP route
#           PRESENT
#
#
# Student conclusion:
#
#
#       "The route is viable."
#
#
# Not yet.
#
#
# Missing:
#
#
#       policy
#
#       capability
#
#       end-to-end path evidence
#
#
# ============================================================================


# ============================================================================
# BGP LAB — CONTROL PLANE / DATA PLANE
# ============================================================================
#
# SCENARIO:
#
#
#       BGP route
#           PRESENT
#
#
#       TCP probe
#           FAILS
#
#
# Question:
#
#
#       Is BGP wrong?
#
#
# Answer:
#
#
#       NOT NECESSARILY.
#
#
# BGP established control-plane route evidence.
#
# The TCP probe established data-plane failure evidence.
#
#
# Investigate:
#
#
#       ACL
#
#       firewall
#
#       tunnel
#
#       next-hop reachability
#
#       asymmetric routing
#
#       downstream routing
#
#
# ============================================================================


# ============================================================================
# BGP LAB — DESTINATION STILL HEALTHY
# ============================================================================
#
# SCENARIO:
#
#
#       AI service
#           AVAILABLE
#
#
#       BGP route
#           ABSENT
#
#
# Question:
#
#
#       Is the AI service unavailable?
#
#
# Answer:
#
#
#       NO.
#
#
# The service may be healthy from its own operational perspective.
#
# This caller lacks qualifying route evidence.
#
#
# ============================================================================
#
#
#       SERVICE HEALTH != CALLER REACHABILITY
#
#
# ============================================================================


# ============================================================================
# BGP LAB — CONVERGENCE TRAP
# ============================================================================
#
# SCENARIO:
#
#
#       E9 request
#
#       private path permitted
#
#       Internet path prohibited
#
#
# Private route disappears.
#
#
# BGP converges.
#
#
# Internet route becomes preferred.
#
#
# Network:
#
#
#       CONNECTIVITY RESTORED
#
#
# Agent 11:
#
#
#       REQUEST MAY STILL HAVE NO
#       POLICY-COMPLIANT PATH
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
# BGP LAB — TWO ROUTES
# ============================================================================
#
# SCENARIO:
#
#
#       route A
#           preferred by BGP
#
#       route B
#           less preferred by BGP
#
#
# Student:
#
#
#       "Agent 11 should use route A."
#
#
# Chewbacca:
#
#
#       "You have confused packet routing
#        with AI routing."
#
#
# BGP preference does not establish:
#
#
#       data authorization
#
#       AI model capability
#
#       AI service health
#
#       AI service preference
#
#
# ============================================================================


# ============================================================================
# BGP LAB — ROUTE LEAK
# ============================================================================
#
# SCENARIO:
#
#
# An unexpected route appears.
#
#
# Student:
#
#
#       "Excellent. More availability."
#
#
# Security engineer:
#
#
#       "Why is that route visible?"
#
#
# ============================================================================
#
#
#       DISCOVERED != TRUSTED
#
#       MORE REACHABILITY != MORE AUTHORIZATION
#
#
# ============================================================================


# ============================================================================
# BGP LAB — READ VS WRITE
# ============================================================================
#
# Agent 11 discovers:
#
#
#       route absent
#
#
# and correctly reasons:
#
#
#       "A route advertisement could restore reachability."
#
#
# Does Agent 11 advertise it?
#
#
# No authority has been established.
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
# PART III-A DOES NOT YET IMPLEMENT
# ============================================================================
#
# Part III-A deliberately does NOT implement:
#
#
#       real FRRouting integration
#
#       real GoBGP integration
#
#       Cisco integration
#
#       Juniper integration
#
#       BGP neighbor configuration
#
#       BGP session management
#
#       route advertisement
#
#       route withdrawal
#
#       route-map modification
#
#       LOCAL_PREF modification
#
#       MED modification
#
#       community modification
#
#       AS_PATH analysis
#
#       RIB/FIB reconciliation
#
#       RPKI validation
#
#       route-leak detection
#
#       hijack detection
#
#       route scoring
#
#       path scoring
#
#       path authorization
#
#       path selection
#
#       network remediation
#
#
# These become future components only when their responsibilities are
# explicitly defined.
#
#
# ============================================================================


# ============================================================================
# PART III-B HANDOFF
# ============================================================================
#
# Part III-A produces:
#
#
#       ROUTE EVIDENCE
#
#
# Part III-B will ask:
#
#
#       "HOW DOES ROUTE EVIDENCE COMBINE WITH
#        DATA-PLANE EVIDENCE TO DESCRIBE
#        ACTUAL NETWORK PATHS?"
#
#
# That is where we can introduce:
#
#
#       NetworkPathEvidence
#
#       NetworkPathAssessment
#
#       source -> destination identity
#
#       multiple path instances
#
#       parallel paths
#
#       contradictory observations
#
#       degraded paths
#
#       path freshness
#
#
# ============================================================================
# DO NOT SKIP THE LAYER
# ============================================================================
#
#
#       RouteEvidence
#
#           DOES NOT GO DIRECTLY TO
#
#       RoutingCandidate
#
#
# Instead:
#
#
#       RouteEvidence --------+
#                             |
#       DataPlaneEvidence ----+
#                             |
#                             v
#                  NetworkPathAssessment
#                             |
#                             v
#                    CandidateEvaluator
#                             |
#                             v
#                    RoutingCandidate
#
#
# ============================================================================


# ============================================================================
# PART III-A FINAL INVARIANTS
# ============================================================================
#
#
#       PATH TYPE != ROUTING PROTOCOL
#
#       ROUTE EVIDENCE != PATH EVIDENCE
#
#       ROUTE EVIDENCE != PATH ASSESSMENT
#
#       ROUTE EVIDENCE != AUTHORIZATION
#
#       ROUTE EVIDENCE != AI ROUTING DECISION
#
#       ROUTE PRESENT != PATH AVAILABLE
#
#       ROUTE ABSENT != SERVICE FAILURE
#
#       ABSENT != UNKNOWN
#
#       UNKNOWN != STALE
#
#       FAILED OBSERVATION != NEGATIVE OBSERVATION
#
#       OBSERVATION FAILURE != ROUTE ABSENCE
#
#       ROUTE OBSERVED THEN != ROUTE CONFIRMED NOW
#
#       STALE EVIDENCE != FALSE EVIDENCE
#
#       BGP ROUTE EXISTS != END-TO-END CONNECTIVITY
#
#       BGP LEARNED ROUTE != FORWARDING ENTRY
#
#       BGP BEST PATH != AGENT 11 BEST AI ROUTE
#
#       BGP LOCAL_PREF != AI ROUTING PREFERENCE
#
#       SHORTER AS_PATH != BETTER AI DESTINATION
#
#       NETWORK METRIC != AI POLICY
#
#       BGP COMMUNITY != AGENT 11 AUTHORIZATION
#
#       NEXT HOP KNOWN != NEXT HOP REACHABLE
#
#       NEXT HOP REACHABLE != DESTINATION REACHABLE
#
#       BGP SESSION ESTABLISHED != REQUIRED ROUTE PRESENT
#
#       BGP SESSION DOWN != DESTINATION UNREACHABLE
#
#       ROUTE WITHDRAWAL != SERVICE FAILURE
#
#       ROUTE PRESENT != ROUTE INTENDED
#
#       ROUTE REACHABILITY != DESTINATION IDENTITY
#
#       ROUTE ORIGIN VALIDITY != ROUTE AVAILABILITY
#
#       CONTROL PLANE != DATA PLANE
#
#       DATA PLANE != APPLICATION PLANE
#
#       ROUTE STATE IS SOURCE-RELATIVE
#
#       SOURCE KNOWN != SOURCE AUTHORITATIVE
#
#       VALID PYDANTIC MODEL != TRUSTED EVIDENCE
#
#       DISCOVERED != TRUSTED
#
#       MORE REACHABILITY != MORE AUTHORIZATION
#
#       NETWORK CONVERGENCE != POLICY-COMPLIANT RECOVERY
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#       OBSERVE != REMEDIATE
#
#       DETECT != ACT
#
#       CORRECT REASONING != EXECUTION AUTHORITY
#
#       REASONING AUTHORIZATION != EXECUTION AUTHORIZATION
#
#       FAIL CLOSED != FALSIFY STATE
#
#       INFRASTRUCTURE HAS FIELD != DOMAIN REQUIRES FIELD
#
#       INFRASTRUCTURE COMPLEXITY SHOULD BE TRANSLATED,
#       NOT REPLICATED
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================
# FINAL PART III-A RULE
# ============================================================================
#
#
#       BGP TELLS AGENT 11
#       WHAT THE NETWORK CONTROL PLANE
#       BELIEVES ABOUT ROUTING.
#
#
#       BGP DOES NOT TELL AGENT 11
#       WHAT DATA POLICY PERMITS.
#
#
#       BGP DOES NOT TELL AGENT 11
#       WHETHER INFERENCE WORKS.
#
#
#       BGP DOES NOT SELECT
#       THE AI SERVICE.
#
#
# ============================================================================
# END OF PART III-A
# ============================================================================

# ============================================================================
# network/path.py
#
# PART III-B
#
# PATH EVIDENCE + PATH ASSESSMENT
# ============================================================================
#
# PURPOSE
# -------
#
# Part III-A introduced:
#
#
#       ROUTE EVIDENCE
#
#
# Route evidence describes what the network CONTROL PLANE reports about
# routing toward a destination.
#
#
# Part III-B introduces:
#
#
#       PATH EVIDENCE
#
# and:
#
#       PATH ASSESSMENT
#
#
# Path evidence describes observations about actual connectivity between:
#
#
#       SOURCE
#           ->
#       DESTINATION
#
#
# Path assessment describes what Agent 11 currently concludes from the
# available path evidence.
#
#
# ============================================================================
# CENTRAL FLOW
# ============================================================================
#
#
#       RouteEvidence ------------------+
#                                       |
#       Data-plane observations --------+
#                                       |
#                                       v
#                             NetworkPathEvidence
#                                       |
#                                       v
#                           NetworkPathAssessment
#
#
# ============================================================================
# IMPORTANT
# ============================================================================
#
# Even NetworkPathAssessment does NOT answer:
#
#
#       "May this request use the path?"
#
#
# That remains policy.
#
#
# Therefore:
#
#
#       PATH EVIDENCE != PATH ASSESSMENT
#
#       PATH ASSESSMENT != PATH AUTHORIZATION
#
#       PATH AUTHORIZATION != AI SERVICE SELECTION
#
#
# ============================================================================
# PART III-B QUESTION
# ============================================================================
#
#
#       "WHAT OPERATIONAL CONNECTIVITY EVIDENCE
#        DO WE HAVE BETWEEN THIS SOURCE
#        AND THIS DESTINATION,
#        AND WHAT CAN WE CURRENTLY CONCLUDE
#        FROM THAT EVIDENCE?"
#
#
# ============================================================================


from datetime import datetime, timezone
from typing import Protocol

from pydantic import Field, model_validator

from ..models.base_model import Agent11BaseModel
from ..models.enums.network_enums import (
    NetworkPathState,
    NetworkPathType,
)


# ============================================================================
# ASSUMPTION
# ============================================================================
#
# Part III-A introduced RouteEvidence.
#
# In the production project, that noun will eventually belong in an
# appropriate models/network/ package once that package is formally created.
#
#
# This section assumes RouteEvidence already exists.
#
#
# ============================================================================


# ============================================================================
# PATH EVIDENCE
# ============================================================================
#
# One NetworkPathEvidence object represents ONE observation about ONE
# connectivity relationship.
#
#
# Conceptually:
#
#
#       source
#           |
#           | path
#           v
#       destination
#
#
# ============================================================================
# WHY SOURCE IDENTITY NOW MATTERS
# ============================================================================
#
# Part I could ask:
#
#
#       service_id + path_type
#
#
# Part III-B can no longer pretend that path state belongs only to the
# destination.
#
#
# Example:
#
#
#       Tokyo
#           ->
#       inference endpoint
#
#           AVAILABLE
#
#
# while:
#
#
#       Virginia
#           ->
#       same inference endpoint
#
#           UNAVAILABLE
#
#
# Both observations may be correct.
#
#
#       PATH STATE IS SOURCE-RELATIVE
#
#
# ============================================================================


class NetworkPathEvidence(Agent11BaseModel):
    """
    One normalized observation about a network path.

    This model records operational evidence.

    It does not authorize the path.

    It does not select the path.

    It does not select an AI service.
    """

    source_id: str = Field(
        min_length=1,
        description=(
            "Logical identity of the source from which connectivity "
            "was observed."
        ),
    )

    destination_id: str = Field(
        min_length=1,
        description=(
            "Logical identity of the destination toward which "
            "connectivity was observed."
        ),
    )

    path_type: NetworkPathType = Field(
        description=(
            "Broad connectivity mechanism represented by this evidence."
        ),
    )

    state: NetworkPathState = Field(
        description=(
            "Operational state established by this observation."
        ),
    )

    observed_at: datetime = Field(
        description=(
            "Time at which this path condition was observed."
        ),
    )


# ============================================================================
# WHAT IS NOT IN NetworkPathEvidence
# ============================================================================
#
# Notice what is deliberately absent:
#
#
#       authorized
#
#       policy_decision
#
#       routing_candidate
#
#       selected
#
#       model_id
#
#       prompt
#
#       response
#
#       cost
#
#       preference score
#
#
# Why?
#
#
# Because:
#
#
#       PATH EVIDENCE DESCRIBES CONNECTIVITY.
#
#
# It does not describe authorization or AI selection.
#
#
# ============================================================================


# ============================================================================
# PATH EVIDENCE != ROUTE EVIDENCE
# ============================================================================
#
# Part III-A:
#
#
#       RouteEvidence
#
#
# may say:
#
#
#       BGP route PRESENT
#
#
# Part III-B:
#
#
#       NetworkPathEvidence
#
#
# may say:
#
#
#       VPN path UNAVAILABLE
#
#
# These are not necessarily contradictory.
#
#
# ============================================================================
# EXAMPLE
# ============================================================================
#
#
#       BGP:
#
#           route PRESENT
#
#
#       TCP probe:
#
#           connection FAILED
#
#
# Therefore:
#
#
#       CONTROL PLANE
#           knows route
#
#
#       DATA PLANE
#           currently fails
#
#
# Both may be true.
#
#
# ============================================================================


# ============================================================================
# PATH OBSERVATION ERROR
# ============================================================================
#
# Part II introduced the principle:
#
#
#       OBSERVATION FAILURE != PATH FAILURE
#
#
# We preserve it.
#
#
# ============================================================================


class PathEvidenceObservationError(RuntimeError):
    """
    Expected failure while obtaining path evidence.

    This means current connectivity state could not be established.

    It does not mean the path is unavailable.
    """


# ============================================================================
# PATH EVIDENCE PROVIDER
# ============================================================================
#
# Infrastructure-specific observers should normalize their observations
# behind this contract.
#
#
# ============================================================================


class NetworkPathEvidenceProvider(Protocol):
    """
    Behavioral contract for collecting normalized path evidence.

    Implementations may use:

        synthetic probes

        VPN telemetry

        SD-WAN telemetry

        cloud networking APIs

        internal monitoring

        Kubernetes-side probes

    without exposing those implementation details to generic Agent 11
    path-assessment behavior.
    """

    def collect_path_evidence(
        self,
        source_id: str,
        destination_id: str,
        path_type: NetworkPathType,
    ) -> NetworkPathEvidence:
        ...


# ============================================================================
# PATH EVIDENCE EVALUATOR
# ============================================================================
#
# The evaluator creates a consistent Agent 11 boundary around path
# observation.
#
#
# Expected observation failure:
#
#
#       UNKNOWN
#
#
# Programming defect:
#
#
#       exception remains visible
#
#
# ============================================================================


class NetworkPathEvidenceEvaluator:
    """
    Obtain normalized network-path evidence from an injected provider.
    """

    def __init__(
        self,
        evidence_provider: NetworkPathEvidenceProvider,
    ) -> None:
        self._evidence_provider = evidence_provider

    def get_path_evidence(
        self,
        source_id: str,
        destination_id: str,
        path_type: NetworkPathType,
    ) -> NetworkPathEvidence:
        """
        Return normalized path evidence.

        Expected infrastructure observation failure becomes UNKNOWN.

        Unexpected programming failures remain visible.
        """

        try:
            return self._evidence_provider.collect_path_evidence(
                source_id=source_id,
                destination_id=destination_id,
                path_type=path_type,
            )

        except PathEvidenceObservationError:
            return NetworkPathEvidence(
                source_id=source_id,
                destination_id=destination_id,
                path_type=path_type,
                state=NetworkPathState.UNKNOWN,
                observed_at=datetime.now(timezone.utc),
            )


# ============================================================================
# WHY NOT except Exception?
# ============================================================================
#
#
#       except Exception:
#           return UNKNOWN
#
#
# would hide defects.
#
#
# Examples:
#
#
#       TypeError
#
#       AttributeError
#
#       broken translation logic
#
#       malformed configuration
#
#
# Those are not network uncertainty.
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
# STATIC PATH EVIDENCE PROVIDER
# ============================================================================
#
# This gives deterministic Part III-B tests without requiring:
#
#
#       router
#
#       cloud
#
#       VPN
#
#       SD-WAN
#
#       Kubernetes
#
#
# ============================================================================


class StaticNetworkPathEvidenceProvider:
    """
    Deterministic in-memory provider for path evidence.

    Evidence is keyed by:

        (
            source_id,
            destination_id,
            path_type,
        )

    Missing evidence becomes UNKNOWN.

    Missing evidence does NOT become UNAVAILABLE.
    """

    def __init__(
        self,
        evidence: dict[
            tuple[str, str, NetworkPathType],
            NetworkPathEvidence,
        ],
    ) -> None:
        self._evidence = dict(evidence)

    def collect_path_evidence(
        self,
        source_id: str,
        destination_id: str,
        path_type: NetworkPathType,
    ) -> NetworkPathEvidence:

        key = (
            source_id,
            destination_id,
            path_type,
        )

        evidence = self._evidence.get(key)

        if evidence is None:
            return NetworkPathEvidence(
                source_id=source_id,
                destination_id=destination_id,
                path_type=path_type,
                state=NetworkPathState.UNKNOWN,
                observed_at=datetime.now(timezone.utc),
            )

        if evidence.source_id != source_id:
            raise ValueError(
                "Stored path evidence does not match "
                "the requested source."
            )

        if evidence.destination_id != destination_id:
            raise ValueError(
                "Stored path evidence does not match "
                "the requested destination."
            )

        if evidence.path_type is not path_type:
            raise ValueError(
                "Stored path evidence does not match "
                "the requested path type."
            )

        return evidence


# ============================================================================
# SAMPLE PATH EVIDENCE
# ============================================================================
#
#
#     evidence = NetworkPathEvidence(
#         source_id="agent11-tokyo",
#         destination_id="company-cloud-primary",
#         path_type=NetworkPathType.PRIVATE_LINK,
#         state=NetworkPathState.AVAILABLE,
#         observed_at=datetime.now(timezone.utc),
#     )
#
#
#     provider = StaticNetworkPathEvidenceProvider(
#         evidence={
#             (
#                 "agent11-tokyo",
#                 "company-cloud-primary",
#                 NetworkPathType.PRIVATE_LINK,
#             ): evidence,
#         }
#     )
#
#
# ============================================================================


# ============================================================================
# DATA-PLANE PROBE
# ============================================================================
#
# Part III-A gave us control-plane route evidence.
#
#
# Part III-B should also have a truthful data-plane seam.
#
#
# A probe may attempt:
#
#
#       TCP connection
#
#       HTTPS request
#
#       application-independent health probe
#
#
# The probe implementation belongs below Agent 11's normalized evidence
# model.
#
#
# ============================================================================


class DataPlaneProbe(Protocol):
    """
    Low-level contract for observing data-plane connectivity.

    True:
        successful observation established connectivity.

    False:
        successful observation established connectivity failure.

    PathEvidenceObservationError:
        trustworthy current evidence could not be established.
    """

    def probe(
        self,
        destination_id: str,
    ) -> bool:
        ...


class DataPlanePathEvidenceProvider:
    """
    Translate a low-level data-plane probe into NetworkPathEvidence.

    The provider is configured for one logical source and one path type.

    That makes evidence provenance explicit.
    """

    def __init__(
        self,
        source_id: str,
        path_type: NetworkPathType,
        probe: DataPlaneProbe,
    ) -> None:
        self._source_id = source_id
        self._path_type = path_type
        self._probe = probe

    def collect_path_evidence(
        self,
        source_id: str,
        destination_id: str,
        path_type: NetworkPathType,
    ) -> NetworkPathEvidence:

        if source_id != self._source_id:
            raise ValueError(
                "Requested source does not match the configured "
                "data-plane observation source."
            )

        if path_type is not self._path_type:
            raise ValueError(
                "Requested path type does not match the configured "
                "data-plane observation path."
            )

        reachable = self._probe.probe(
            destination_id=destination_id,
        )

        state = (
            NetworkPathState.AVAILABLE
            if reachable
            else NetworkPathState.UNAVAILABLE
        )

        return NetworkPathEvidence(
            source_id=source_id,
            destination_id=destination_id,
            path_type=path_type,
            state=state,
            observed_at=datetime.now(timezone.utc),
        )


# ============================================================================
# SIMPLE PROBE LIMITATION
# ============================================================================
#
# A bool probe can truthfully establish:
#
#
#       success
#
#       failure
#
#
# It cannot truthfully establish:
#
#
#       DEGRADED
#
#
# unless richer measurements exist.
#
#
# ============================================================================
#
#
#       VOCABULARY EXISTS != EVIDENCE EXISTS
#
#
# ============================================================================


# ============================================================================
# DEGRADED REQUIRES EVIDENCE
# ============================================================================
#
# DEGRADED may eventually be established using:
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
#       partial tunnel availability
#
#       reduced redundancy
#
#
# But Part III-B does not invent thresholds.
#
#
# ============================================================================
#
#
#       MEASUREMENT != THRESHOLD
#
#       THRESHOLD != POLICY
#
#
# ============================================================================


# ============================================================================
# PATH ASSESSMENT
# ============================================================================
#
# We now have evidence.
#
#
# We need a separate noun representing:
#
#
#       WHAT AGENT 11 CURRENTLY CONCLUDES
#
#
# about connectivity between:
#
#
#       source
#           ->
#       destination
#
#
# ============================================================================
#
#
#       EVIDENCE != ASSESSMENT
#
#
# ============================================================================


class NetworkPathAssessment(Agent11BaseModel):
    """
    Current Agent 11 assessment of network connectivity between one source
    and one destination.

    This is an operational assessment.

    It is not authorization.
    """

    source_id: str = Field(
        min_length=1,
    )

    destination_id: str = Field(
        min_length=1,
    )

    state: NetworkPathState

    evidence: list[NetworkPathEvidence] = Field(
        default_factory=list,
    )

    assessed_at: datetime

    @model_validator(mode="after")
    def validate_evidence_relationships(
        self,
    ) -> "NetworkPathAssessment":
        """
        Ensure every evidence record belongs to the same source/destination
        relationship represented by this assessment.

        The aggregate validates relationships among its members.

        It does not determine authorization or routing preference.
        """

        for item in self.evidence:

            if item.source_id != self.source_id:
                raise ValueError(
                    "All path evidence must belong to the "
                    "assessment source."
                )

            if item.destination_id != self.destination_id:
                raise ValueError(
                    "All path evidence must belong to the "
                    "assessment destination."
                )

        return self


# ============================================================================
# AGGREGATE RULE
# ============================================================================
#
#
#       A MODEL VALIDATES ITSELF.
#
#       AN AGGREGATE VALIDATES RELATIONSHIPS
#       BETWEEN ITS MEMBERS.
#
#       AN ORCHESTRATOR CONTROLS HOW
#       THE AGGREGATE EVOLVES.
#
#       A SERVICE PERFORMS WORK.
#
#
# ============================================================================


# ============================================================================
# MULTIPLE PATHS
# ============================================================================
#
# Now consider:
#
#
#                         +--> PRIVATE_LINK -> AVAILABLE
#                         |
#       Agent 11 Tokyo ---+--> VPN ---------> DEGRADED
#                         |
#                         +--> INTERNET ----> AVAILABLE
#
#
# These are not three contradictory observations.
#
#
# They describe three different path dimensions.
#
#
# ============================================================================
#
#
#       DIFFERENT PATHS
#           !=
#       CONFLICTING EVIDENCE
#
#
# ============================================================================


# ============================================================================
# SAME PATH + DIFFERENT OBSERVERS
# ============================================================================
#
# Now consider:
#
#
#       PRIVATE_LINK
#
#           observer A -> AVAILABLE
#
#           observer B -> UNAVAILABLE
#
#
# That MAY be contradictory evidence about the same path.
#
#
# Therefore:
#
#
#       EVIDENCE IDENTITY MATTERS
#
#
# Part III-B still does not have:
#
#
#       observer_id
#
#       path_id
#
#
# so we should not pretend we can perfectly resolve every multi-observer
# situation yet.
#
#
# ============================================================================


# ============================================================================
# PATH ASSESSMENT EVALUATOR
# ============================================================================
#
# This evaluator performs OPERATIONAL aggregation only.
#
#
# It does NOT ask:
#
#
#       Is this path authorized?
#
#       Is Internet permitted?
#
#       Is E9 permitted?
#
#       Which AI service should win?
#
#
# ============================================================================
#
#
#       OPERATIONAL ASSESSMENT != POLICY EVALUATION
#
#
# ============================================================================


class NetworkPathAssessmentEvaluator:
    """
    Build an operational path assessment from normalized path evidence.

    Current SEIR-II semantics:

        no evidence
            -> UNKNOWN

        any AVAILABLE path
            -> AVAILABLE

        otherwise any DEGRADED path
            -> DEGRADED

        all relevant paths UNAVAILABLE
            -> UNAVAILABLE

        otherwise
            -> UNKNOWN

    IMPORTANT:

    AVAILABLE here means:

        "At least one observed operational path is available."

    It does NOT mean:

        "At least one AUTHORIZED path is available."
    """

    def assess(
        self,
        source_id: str,
        destination_id: str,
        evidence: list[NetworkPathEvidence],
        assessed_at: datetime,
    ) -> NetworkPathAssessment:

        relevant_evidence = [
            item
            for item in evidence
            if (
                item.source_id == source_id
                and item.destination_id == destination_id
            )
        ]

        if not relevant_evidence:
            return NetworkPathAssessment(
                source_id=source_id,
                destination_id=destination_id,
                state=NetworkPathState.UNKNOWN,
                evidence=[],
                assessed_at=assessed_at,
            )

        states = {
            item.state
            for item in relevant_evidence
        }

        if NetworkPathState.AVAILABLE in states:
            state = NetworkPathState.AVAILABLE

        elif NetworkPathState.DEGRADED in states:
            state = NetworkPathState.DEGRADED

        elif states == {NetworkPathState.UNAVAILABLE}:
            state = NetworkPathState.UNAVAILABLE

        else:
            state = NetworkPathState.UNKNOWN

        return NetworkPathAssessment(
            source_id=source_id,
            destination_id=destination_id,
            state=state,
            evidence=relevant_evidence,
            assessed_at=assessed_at,
        )


# ============================================================================
# WHY "ANY AVAILABLE -> AVAILABLE"?
# ============================================================================
#
# Suppose:
#
#
#       PRIVATE_LINK
#           UNAVAILABLE
#
#
#       VPN
#           AVAILABLE
#
#
# Those observations do not disagree.
#
#
# They establish:
#
#
#       one path failed
#
#       another path works
#
#
# Therefore an operational source-to-destination assessment may reasonably
# conclude:
#
#
#       AVAILABLE
#
#
# ============================================================================
# BUT...
# ============================================================================
#
# This does NOT establish that the current request may use VPN.
#
#
# Policy has not been evaluated.
#
#
# ============================================================================


# ============================================================================
# CRITICAL SEMANTIC DEFINITION
# ============================================================================
#
# In NetworkPathAssessment:
#
#
#       AVAILABLE
#
#
# means:
#
#
#       AT LEAST ONE OPERATIONALLY AVAILABLE PATH EXISTS
#
#
# It does NOT mean:
#
#
#       AT LEAST ONE POLICY-COMPLIANT PATH EXISTS
#
#
# ============================================================================
#
#
#       OPERATIONALLY AVAILABLE
#           !=
#       AUTHORIZED
#
#
# ============================================================================


# ============================================================================
# WHY UNKNOWN DOES NOT OVERRIDE AVAILABLE
# ============================================================================
#
# Suppose:
#
#
#       PRIVATE_LINK
#           AVAILABLE
#
#
#       VPN
#           UNKNOWN
#
#
# We still possess positive evidence that some connectivity exists.
#
#
# Therefore:
#
#
#       overall operational connectivity
#           AVAILABLE
#
#
# can be reasonable.
#
#
# This does NOT mean the VPN became available.
#
#
# ============================================================================
#
#
#       ONE UNKNOWN PATH
#           !=
#       ALL CONNECTIVITY UNKNOWN
#
#
# ============================================================================


# ============================================================================
# WHY UNAVAILABLE + UNKNOWN -> UNKNOWN
# ============================================================================
#
# Suppose:
#
#
#       PRIVATE_LINK
#           UNAVAILABLE
#
#
#       VPN
#           UNKNOWN
#
#
# Can we conclude:
#
#
#       destination unreachable?
#
#
# No.
#
#
# The VPN may still work.
#
#
# Therefore:
#
#
#       UNAVAILABLE + UNKNOWN
#           ->
#       UNKNOWN
#
#
# ============================================================================
#
#
#       KNOWN FAILURE + UNKNOWN ALTERNATIVE
#           !=
#       TOTAL FAILURE
#
#
# ============================================================================


# ============================================================================
# WHY DEGRADED + UNKNOWN -> DEGRADED
# ============================================================================
#
# Suppose:
#
#
#       VPN
#           DEGRADED
#
#
#       PRIVATE_LINK
#           UNKNOWN
#
#
# We possess evidence that some connectivity currently exists, but it is
# degraded.
#
#
# Therefore:
#
#
#       DEGRADED
#
#
# is a reasonable operational assessment.
#
#
# Again:
#
#
#       DEGRADED != AUTHORIZED
#
#
# ============================================================================


# ============================================================================
# ALL UNAVAILABLE
# ============================================================================
#
# Suppose:
#
#
#       PRIVATE_LINK
#           UNAVAILABLE
#
#
#       VPN
#           UNAVAILABLE
#
#
#       INTERNET
#           UNAVAILABLE
#
#
# Then:
#
#
#       NetworkPathAssessment
#           UNAVAILABLE
#
#
# is supported by the evidence.
#
#
# ============================================================================
# PROVIDED...
# ============================================================================
#
# those are all the relevant paths Agent 11 is currently assessing.
#
#
# This becomes harder when path discovery becomes dynamic.
#
#
# Part III-C can revisit that.
#
#
# ============================================================================


# ============================================================================
# KNOWN PATH SET MATTERS
# ============================================================================
#
# Imagine:
#
#
#       VPN
#           UNAVAILABLE
#
#
# but Agent 11 does not know whether:
#
#
#       PRIVATE_LINK
#
#
# exists.
#
#
# Is the destination:
#
#
#       UNAVAILABLE
#
#
# or:
#
#
#       UNKNOWN?
#
#
# That depends upon whether the assessment knows the complete expected path
# set.
#
#
# ============================================================================
# IMPORTANT FUTURE PROBLEM
# ============================================================================
#
#
#       OBSERVED PATH SET
#           !=
#       COMPLETE POSSIBLE PATH SET
#
#
# Part III-B does not yet solve dynamic path inventory.
#
#
# ============================================================================


# ============================================================================
# PATH DISCOVERY != PATH HEALTH
# ============================================================================
#
# Future Agent 11 may need:
#
#
#       expected paths
#
#       discovered paths
#
#       observed paths
#
#
# These are different concepts.
#
#
# ============================================================================
#
#
#       DISCOVERED != EXPECTED
#
#       EXPECTED != AVAILABLE
#
#       AVAILABLE != AUTHORIZED
#
#
# ============================================================================


# ============================================================================
# ROUTE EVIDENCE ENTERS HERE
# ============================================================================
#
# Part III-A route evidence can contribute to understanding a path.
#
#
# Example:
#
#
#       BGP route
#           PRESENT
#
#
#       TCP probe
#           SUCCESS
#
#
# Together they provide stronger operational understanding than either alone.
#
#
# But they still describe different layers.
#
#
# ============================================================================


# ============================================================================
# DO NOT FLATTEN BGP INTO PATH STATE TOO EARLY
# ============================================================================
#
# Incorrect:
#
#
#       BGP PRESENT
#           ->
#       NetworkPathState.AVAILABLE
#
#
# Why?
#
#
# Because:
#
#
#       route present
#
#
# does not establish:
#
#
#       data-plane connectivity.
#
#
# ============================================================================
#
#
#       CONTROL-PLANE SUCCESS
#           !=
#       DATA-PLANE SUCCESS
#
#
# ============================================================================


# ============================================================================
# SAMPLE CONTROL + DATA-PLANE MATRIX
# ============================================================================
#
#
#       ROUTE       DATA PLANE       INTERPRETATION
#
#       PRESENT     AVAILABLE        strong positive evidence
#
#       PRESENT     UNAVAILABLE      route exists, data plane fails
#
#       ABSENT      UNAVAILABLE      both layers indicate failure
#
#       UNKNOWN     AVAILABLE        packets work despite route uncertainty
#
#       PRESENT     UNKNOWN          route known, data plane uncertain
#
#
# ============================================================================
# IMPORTANT
# ============================================================================
#
# None of these rows contains:
#
#
#       AUTHORIZED
#
#
# because authorization is not a network observation.
#
#
# ============================================================================


# ============================================================================
# ROUTE PRESENT + DATA PLANE UNAVAILABLE
# ============================================================================
#
# This is the classic III-B troubleshooting case.
#
#
#       BGP
#           PRESENT
#
#
#       path probe
#           UNAVAILABLE
#
#
# Possible investigation:
#
#
#       firewall
#
#       ACL
#
#       next-hop reachability
#
#       tunnel
#
#       downstream route
#
#       asymmetric return path
#
#       NAT
#
#       endpoint
#
#
# ============================================================================
#
#
#       CONTROL PLANE HEALTH
#           DOES NOT PROVE
#       DATA PLANE HEALTH
#
#
# ============================================================================


# ============================================================================
# ROUTE UNKNOWN + DATA PLANE AVAILABLE
# ============================================================================
#
# This one is fun.
#
#
# Suppose:
#
#
#       BGP observer
#           UNKNOWN
#
#
# because:
#
#
#       router telemetry API failed
#
#
# while:
#
#
#       TCP probe
#           AVAILABLE
#
#
# Agent 11 has direct operational evidence that traffic currently flows.
#
#
# The BGP observer's failure does not erase that evidence.
#
#
# ============================================================================
#
#
#       OBSERVER FAILURE
#           !=
#       NETWORK FAILURE
#
#
# ============================================================================


# ============================================================================
# ROUTE ABSENT + DATA PLANE AVAILABLE
# ============================================================================
#
# This is not impossible either.
#
#
# Possible reasons:
#
#
#       static route
#
#       connected route
#
#       another routing protocol
#
#       BGP observer scoped incorrectly
#
#       different routing table
#
#       different VRF
#
#
# Therefore:
#
#
#       BGP ROUTE ABSENT
#           !=
#       NO ROUTE OF ANY KIND EXISTS
#
#
# ============================================================================


# ============================================================================
# ROUTE PROTOCOL != PATH TYPE
# ============================================================================
#
# Example:
#
#
#       path_type:
#           VPN
#
#
# while:
#
#
#       route protocol:
#           BGP
#
#
# Another VPN might use:
#
#
#       STATIC
#
#
# Therefore:
#
#
#       VPN != BGP
#
#
# and:
#
#
#       VPN != STATIC
#
#
# ============================================================================


# ============================================================================
# PATH INSTANCE PRESSURE
# ============================================================================
#
# Part III-B exposes another limitation.
#
#
# Suppose:
#
#
#       VPN-TOKYO-A
#
#       VPN-TOKYO-B
#
#
# Both are:
#
#
#       NetworkPathType.VPN
#
#
# One:
#
#
#       AVAILABLE
#
#
# the other:
#
#
#       UNAVAILABLE
#
#
# Our current NetworkPathEvidence identifies only:
#
#
#       source_id
#       destination_id
#       path_type
#
#
# That cannot uniquely distinguish two VPN instances.
#
#
# ============================================================================
# THIS IS INTENTIONAL TECHNICAL PRESSURE
# ============================================================================
#
# We now know:
#
#
#       PATH TYPE != PATH INSTANCE
#
#
# Part III-C can decide whether:
#
#
#       path_id
#
#
# has finally earned existence.
#
#
# ============================================================================


# ============================================================================
# DO NOT USE LIST POSITION AS IDENTITY
# ============================================================================
#
# Never decide:
#
#
#       evidence[0] = VPN-A
#
#       evidence[1] = VPN-B
#
#
# List order is not domain identity.
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
# SOURCE ID PRESSURE
# ============================================================================
#
# source_id currently gives us:
#
#
#       agent11-tokyo
#
#
# Future source identity may need:
#
#
#       deployment
#
#       cluster
#
#       node
#
#       network zone
#
#       region
#
#
# Do not explode source_id into those fields yet.
#
#
# ============================================================================
#
#
#       DOMAIN PRESSURE SHOULD CREATE MODELS.
#
#       IMAGINATION ALONE SHOULD NOT.
#
#
# ============================================================================


# ============================================================================
# DESTINATION ID PRESSURE
# ============================================================================
#
# destination_id currently gives us a logical destination.
#
#
# Future:
#
#
#       AIService
#           |
#           +---- deployment A
#           |       |
#           |       +---- endpoint 1
#           |
#           +---- deployment B
#                   |
#                   +---- endpoint 2
#
#
# Eventually:
#
#
#       SERVICE != DEPLOYMENT != ENDPOINT
#
#
# Part III-B records the pressure.
#
# It does not solve the entire deployment model.
#
#
# ============================================================================


# ============================================================================
# EVIDENCE FRESHNESS
# ============================================================================
#
# Path evidence is temporal.
#
#
# Suppose:
#
#
#       10:00
#           VPN AVAILABLE
#
#
# Current time:
#
#
#       11:00
#
#
# Is that evidence still current enough?
#
#
# Maybe not.
#
#
# ============================================================================
#
#
#       OBSERVED THEN != CONFIRMED NOW
#
#
# ============================================================================


# ============================================================================
# observed_at != FRESHNESS POLICY
# ============================================================================
#
# NetworkPathEvidence stores:
#
#
#       observed_at
#
#
# It does not decide:
#
#
#       evidence older than 30 seconds is stale
#
#
# because that is assessment behavior/configuration.
#
#
# Different evidence sources may require different freshness windows.
#
#
# ============================================================================
#
#
#       TIMESTAMP != FRESHNESS DECISION
#
#
# ============================================================================


# ============================================================================
# STALE EVIDENCE
# ============================================================================
#
# If evidence becomes stale:
#
#
#       do not rewrite history.
#
#
# The evidence still truthfully says:
#
#
#       "At time T, the path was AVAILABLE."
#
#
# Assessment may say:
#
#
#       "That evidence is too old to establish current state."
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
# FUTURE FRESHNESS FILTER
# ============================================================================
#
# A future assessment evaluator may receive:
#
#
#       current_time
#
#       freshness_window
#
#
# and exclude evidence that is too old.
#
#
# Do not hide:
#
#
#       datetime.now()
#
#
# deep inside that future evaluator if deterministic testing matters.
#
#
# Prefer injected/current assessment time.
#
#
# ============================================================================


# ============================================================================
# WHY assessed_at IS PROVIDED TO assess()
# ============================================================================
#
# Notice:
#
#
#       assessed_at
#
#
# is an argument.
#
#
# This makes assessment deterministic.
#
#
# Tests can say:
#
#
#       assess as of exactly T
#
#
# rather than depending upon wall-clock timing.
#
#
# ============================================================================
#
#
#       TIME IS A DEPENDENCY TOO.
#
#
# ============================================================================


# ============================================================================
# EVIDENCE PROVENANCE
# ============================================================================
#
# Part III-B still has minimal provenance.
#
#
# Eventually evidence may need:
#
#
#       observer_id
#
#       evidence_type
#
#       observation method
#
#       infrastructure source
#
#       trust level
#
#
# But:
#
#
#       MORE METADATA != MORE TRUTH
#
#
# Add provenance when Agent 11 needs to reason about trust or conflicting
# evidence.
#
#
# ============================================================================


# ============================================================================
# MULTIPLE OBSERVERS
# ============================================================================
#
# Imagine:
#
#
#       synthetic probe
#           AVAILABLE
#
#
#       VPN controller
#           DEGRADED
#
#
# Are they contradictory?
#
#
# Not necessarily.
#
#
# The synthetic probe says:
#
#
#       traffic works
#
#
# The VPN controller says:
#
#
#       underlying VPN redundancy is impaired
#
#
# Both can be true.
#
#
# ============================================================================
#
#
#       DIFFERENT EVIDENCE TYPES
#           !=
#       CONTRADICTORY EVIDENCE
#
#
# ============================================================================


# ============================================================================
# THIS IS WHY FUTURE EVIDENCE TYPE MATTERS
# ============================================================================
#
# Eventually:
#
#
#       DATA_PLANE_PROBE
#
#       VPN_CONTROL_PLANE
#
#       BGP_ROUTE
#
#       SD_WAN_TELEMETRY
#
#
# may deserve explicit evidence-type vocabulary.
#
#
# Part III-B does not introduce it yet because we have separate RouteEvidence
# and NetworkPathEvidence boundaries.
#
#
# ============================================================================


# ============================================================================
# DEGRADED IS NOT A SCORE
# ============================================================================
#
# DEGRADED is a categorical operational state.
#
#
# It does not mean:
#
#
#       60%
#
#       score 0.6
#
#       acceptable with probability 0.6
#
#
# ============================================================================
#
#
#       STATE != SCORE
#
#
# ============================================================================


# ============================================================================
# NO GENERIC CONFIDENCE FLOAT
# ============================================================================
#
# Avoid:
#
#
#       confidence: float = 0.82
#
#
# unless the domain can explain:
#
#
#       0.82 of WHAT?
#
#       calculated HOW?
#
#       calibrated AGAINST WHAT?
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
# PATH ASSESSMENT != PATH SELECTION
# ============================================================================
#
# NetworkPathAssessment may say:
#
#
#       AVAILABLE
#
#
# It still does not say:
#
#
#       use VPN
#
#
#       use PrivateLink
#
#
#       use Internet
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
# PATH SELECTION != AI SERVICE SELECTION
# ============================================================================
#
# Future network infrastructure may select:
#
#
#       which tunnel
#
#       which circuit
#
#       which next hop
#
#
# Agent 11 separately selects:
#
#
#       which reasoning service
#
#
# ============================================================================
#
#
#       NETWORK PATH SELECTION
#           !=
#       AI SERVICE SELECTION
#
#
# ============================================================================


# ============================================================================
# POLICY REMAINS OUTSIDE
# ============================================================================
#
# Suppose:
#
#
#       PRIVATE_LINK
#           UNAVAILABLE
#
#
#       INTERNET
#           AVAILABLE
#
#
# NetworkPathAssessment may legitimately say:
#
#
#       AVAILABLE
#
#
# because some operational path exists.
#
#
# Policy may simultaneously say:
#
#
#       INTERNET
#           DENIED FOR THIS DATA
#
#
# ============================================================================
# BOTH ARE TRUE
# ============================================================================
#
#
#       NETWORK:
#           destination operationally reachable
#
#
#       POLICY:
#           request has no authorized usable path
#
#
# ============================================================================


# ============================================================================
# WHY CANDIDATE EVALUATION MUST EXIST
# ============================================================================
#
# This is exactly the responsibility gap that candidate evaluation fills.
#
#
# Network cannot answer:
#
#
#       "Is this AI destination viable?"
#
#
# because network does not own:
#
#
#       data policy
#
#       model capability
#
#       service health
#
#
# ============================================================================
# EVENTUAL JOIN
# ============================================================================
#
#
#       PolicyDecision ------------------+
#                                       |
#       Model capability ----------------+
#                                       |
#       Service health ------------------+--> CandidateEvaluator
#                                       |
#       Path assessment -----------------+
#                                       |
#                                       v
#                              RoutingCandidate
#
#
# ============================================================================


# ============================================================================
# IMPORTANT FUTURE REFINEMENT
# ============================================================================
#
# A destination-level NetworkPathAssessment may eventually be TOO COARSE for
# candidate evaluation.
#
#
# Why?
#
#
# Suppose:
#
#
#       PrivateLink AVAILABLE
#
#       Internet AVAILABLE
#
#
# overall:
#
#
#       NetworkPathAssessment.AVAILABLE
#
#
# But policy permits only:
#
#
#       PrivateLink
#
#
# Candidate evaluation must know WHICH available path satisfies policy.
#
#
# ============================================================================
#
#
#       AGGREGATE REACHABILITY
#           MAY BE TOO LOSSY
#       FOR PATH-SPECIFIC AUTHORIZATION
#
#
# ============================================================================


# ============================================================================
# FUTURE PATH-SPECIFIC VIABILITY
# ============================================================================
#
# Eventually the flow may need:
#
#
#       individual path evidence
#               |
#               v
#       individual path assessment
#               |
#               +
#       path authorization
#               |
#               v
#       viable path set
#               |
#               v
#       service candidate viability
#
#
# Do not build that yet.
#
#
# Current policy does not yet require path-specific authorization.
#
#
# ============================================================================


# ============================================================================
# POLICY NEVER BECOMES A SCORE
# ============================================================================
#
# Future path selection may optimize:
#
#
#       latency
#
#       cost
#
#       reliability
#
#
# But:
#
#
#       policy
#
#
# remains a hard constraint.
#
#
# ============================================================================
#
#
#       FILTER BY HARD CONSTRAINTS FIRST.
#
#       OPTIMIZE SECOND.
#
#
# ============================================================================


# ============================================================================
# NETWORK FAILOVER
# ============================================================================
#
# Suppose:
#
#
#       VPN-A
#           UNAVAILABLE
#
#
#       VPN-B
#           AVAILABLE
#
#
# Network infrastructure may perform failover.
#
#
# That is an operational networking concern.
#
#
# Agent 11 must still preserve:
#
#
#       authorization
#
#
# ============================================================================
#
#
#       NETWORK FAILOVER
#           !=
#       POLICY FAILOVER
#
#
# ============================================================================


# ============================================================================
# NETWORK CONVERGENCE
# ============================================================================
#
# Part III-A:
#
#
#       BGP converges
#
#
# Part III-B:
#
#
#       resulting data path becomes available
#
#
# Later:
#
#
#       policy determines whether the realized path is acceptable.
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
# ASYMMETRIC ROUTING
# ============================================================================
#
# Part III-B also exposes another advanced issue.
#
#
# Connectivity is not necessarily symmetric.
#
#
#       A -> B
#
#
# may differ from:
#
#
#       B -> A
#
#
# This matters with:
#
#
#       BGP
#
#       firewalls
#
#       stateful inspection
#
#       multi-cloud networks
#
#       NAT
#
#       multiple tunnels
#
#
# ============================================================================
#
#
#       FORWARD PATH != RETURN PATH
#
#
# ============================================================================


# ============================================================================
# DOES NetworkPathEvidence REPRESENT BOTH DIRECTIONS?
# ============================================================================
#
# Currently:
#
#
#       source_id
#           ->
#       destination_id
#
#
# represents the observed relationship from the source's perspective.
#
#
# It does not claim symmetry.
#
#
# Future systems requiring explicit return-path reasoning may need additional
# evidence.
#
#
# ============================================================================


# ============================================================================
# DNS
# ============================================================================
#
# A data-plane path may depend upon DNS.
#
#
# But:
#
#
#       DNS RESOLVES
#           !=
#       PATH AVAILABLE
#
#
# Likewise:
#
#
#       DNS FAILURE
#
#
# may prevent application connectivity even while raw IP routing works.
#
#
# ============================================================================
#
#
#       NAME RESOLUTION != NETWORK REACHABILITY
#
#
# ============================================================================


# ============================================================================
# TLS
# ============================================================================
#
# Similarly:
#
#
#       TCP AVAILABLE
#
#
# does not establish:
#
#
#       TLS VALID
#
#
# and:
#
#
#       TLS VALID
#
#
# does not establish:
#
#
#       AI SERVICE HEALTHY
#
#
# ============================================================================
#
#
#       TCP != TLS != APPLICATION
#
#
# ============================================================================


# ============================================================================
# LAYERED TROUBLESHOOTING
# ============================================================================
#
# Students should be able to reason:
#
#
#       1. Route known?
#
#       2. Data plane works?
#
#       3. Transport works?
#
#       4. TLS works?
#
#       5. Application responds?
#
#       6. AI service healthy?
#
#       7. Request authorized?
#
#       8. Service viable?
#
#
# Do not replace this with:
#
#
#       "It doesn't work."
#
#
# ============================================================================


# ============================================================================
# PATH AVAILABLE != APPLICATION AVAILABLE
# ============================================================================
#
# Example:
#
#
#       TCP 443
#           reachable
#
#
# but:
#
#
#       inference API
#           HTTP 503
#
#
# Network path:
#
#
#       AVAILABLE
#
#
# AI service:
#
#
#       potentially UNAVAILABLE
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
# APPLICATION AVAILABLE != REQUEST SUCCESS
# ============================================================================
#
# Even:
#
#
#       service healthy
#
#
# does not establish:
#
#
#       this particular inference request succeeds.
#
#
# ============================================================================
#
#
#       SERVICE AVAILABLE != INFERENCE SUCCESS
#
#
# ============================================================================


# ============================================================================
# PATH AVAILABLE != DESTINATION IDENTITY
# ============================================================================
#
# A connection reaching SOMETHING does not automatically prove that it
# reached the intended trusted destination.
#
#
# Future endpoint/TLS identity work may become important.
#
#
# ============================================================================
#
#
#       REACHABILITY != IDENTITY
#
#
# ============================================================================


# ============================================================================
# ROUTE LEAK / HIJACK CONSEQUENCE
# ============================================================================
#
# Part III-A showed that unexpected BGP route evidence may exist.
#
#
# Part III-B adds:
#
#
#       packets may actually flow over that unexpected path.
#
#
# That still does not make the path trusted.
#
#
# ============================================================================
#
#
#       WORKING PATH != TRUSTED PATH
#
#
# ============================================================================


# ============================================================================
# OBSERVABILITY != TRUTH
# ============================================================================
#
# Every observation system has limits.
#
#
# A probe may:
#
#
#       fail
#
#       time out
#
#       be blocked
#
#       observe only one region
#
#       observe only one protocol
#
#
# Therefore:
#
#
#       OBSERVATION != OMNISCIENCE
#
#
# ============================================================================


# ============================================================================
# UNKNOWN REMAINS NECESSARY
# ============================================================================
#
# UNKNOWN is not an embarrassment.
#
#
# It is an accurate statement:
#
#
#       "Agent 11 currently lacks sufficient evidence
#        to establish this state."
#
#
# ============================================================================
#
#
#       UNKNOWN IS INFORMATION.
#
#
# ============================================================================


# ============================================================================
# FAIL CLOSED
# ============================================================================
#
# Later candidate evaluation may say:
#
#
#       path assessment UNKNOWN
#           ->
#       candidate not viable
#
#
# That is legitimate.
#
#
# NetworkPathAssessment still remains:
#
#
#       UNKNOWN
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
# NO REMEDIATION
# ============================================================================
#
# Part III-B does not:
#
#
#       restart tunnel
#
#       modify route
#
#       alter firewall
#
#       change NetworkPolicy
#
#       create PrivateLink
#
#       change SD-WAN policy
#
#
# ============================================================================
#
#
#       OBSERVE != REMEDIATE
#
#
# ============================================================================


# ============================================================================
# READ AUTHORITY
# ============================================================================
#
# Path observers should normally receive only enough authority to collect
# evidence.
#
#
# They should not automatically receive network mutation authority.
#
#
# ============================================================================
#
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#
# ============================================================================


# ============================================================================
# TEST: SINGLE AVAILABLE PATH
# ============================================================================
#
#
#     evidence = [
#         NetworkPathEvidence(
#             source_id="agent11-tokyo",
#             destination_id="company-cloud-primary",
#             path_type=NetworkPathType.PRIVATE_LINK,
#             state=NetworkPathState.AVAILABLE,
#             observed_at=datetime.now(timezone.utc),
#         )
#     ]
#
#
#     evaluator = NetworkPathAssessmentEvaluator()
#
#
#     assessment = evaluator.assess(
#         source_id="agent11-tokyo",
#         destination_id="company-cloud-primary",
#         evidence=evidence,
#         assessed_at=datetime.now(timezone.utc),
#     )
#
#
#     assert assessment.state is NetworkPathState.AVAILABLE
#
#
# ============================================================================


# ============================================================================
# TEST: PARALLEL AVAILABLE + UNAVAILABLE
# ============================================================================
#
#
#     evidence = [
#
#         NetworkPathEvidence(
#             source_id="agent11-tokyo",
#             destination_id="company-cloud-primary",
#             path_type=NetworkPathType.PRIVATE_LINK,
#             state=NetworkPathState.UNAVAILABLE,
#             observed_at=datetime.now(timezone.utc),
#         ),
#
#         NetworkPathEvidence(
#             source_id="agent11-tokyo",
#             destination_id="company-cloud-primary",
#             path_type=NetworkPathType.VPN,
#             state=NetworkPathState.AVAILABLE,
#             observed_at=datetime.now(timezone.utc),
#         ),
#     ]
#
#
# Expected:
#
#
#       AVAILABLE
#
#
# because one operational path exists.
#
#
# ============================================================================


# ============================================================================
# TEST: UNAVAILABLE + UNKNOWN
# ============================================================================
#
#
#       PRIVATE_LINK
#           UNAVAILABLE
#
#
#       VPN
#           UNKNOWN
#
#
# Expected:
#
#
#       UNKNOWN
#
#
# because total failure has not been established.
#
#
# ============================================================================


# ============================================================================
# TEST: ALL UNAVAILABLE
# ============================================================================
#
#
#       PRIVATE_LINK
#           UNAVAILABLE
#
#
#       VPN
#           UNAVAILABLE
#
#
# Expected:
#
#
#       UNAVAILABLE
#
#
# assuming those are the complete relevant observed paths.
#
#
# ============================================================================


# ============================================================================
# TEST: DEGRADED + UNAVAILABLE
# ============================================================================
#
#
#       VPN
#           DEGRADED
#
#
#       PRIVATE_LINK
#           UNAVAILABLE
#
#
# Expected:
#
#
#       DEGRADED
#
#
# Some operational connectivity remains, but positive AVAILABLE evidence does
# not exist.
#
#
# ============================================================================


# ============================================================================
# TEST: AVAILABLE + UNKNOWN
# ============================================================================
#
#
#       PRIVATE_LINK
#           AVAILABLE
#
#
#       VPN
#           UNKNOWN
#
#
# Expected:
#
#
#       AVAILABLE
#
#
# because positive operational connectivity has been established.
#
#
# ============================================================================


# ============================================================================
# TEST: IRRELEVANT EVIDENCE
# ============================================================================
#
# Suppose evidence contains:
#
#
#       Tokyo -> service A
#
#       Tokyo -> service B
#
#       Virginia -> service A
#
#
# Assessing:
#
#
#       Tokyo -> service A
#
#
# should filter the collection to that relationship.
#
#
# Unrelated evidence is not a programming error.
#
#
# ============================================================================
#
#
#       QUERY COLLECTION != ASSERT OBJECT PAIR
#
#
# ============================================================================


# ============================================================================
# TEST: INVALID ASSESSMENT AGGREGATE
# ============================================================================
#
# Directly constructing:
#
#
#       NetworkPathAssessment(
#           source_id="agent11-tokyo",
#           destination_id="service-a",
#           evidence=[
#               evidence_from_virginia
#           ],
#           ...
#       )
#
#
# should fail validation.
#
#
# Why?
#
#
# The aggregate claims all evidence belongs to:
#
#
#       Tokyo -> service-a
#
#
# but one member does not.
#
#
# ============================================================================
#
#
#       AGGREGATE VALIDATES MEMBER RELATIONSHIPS
#
#
# ============================================================================


# ============================================================================
# IMPORTANT: ASSESSMENT CORRECTNESS
# ============================================================================
#
# Pydantic can prove:
#
#
#       evidence belongs to the same source/destination
#
#
# It cannot prove:
#
#
#       the assessment algorithm chose the correct operational conclusion.
#
#
# ============================================================================
#
#
#       INTERNAL CONSISTENCY != DOMAIN CORRECTNESS
#
#
# ============================================================================


# ============================================================================
# MODELS VS BEHAVIOR
# ============================================================================
#
# Part III-B now gives us durable nouns:
#
#
#       NetworkPathEvidence
#
#       NetworkPathAssessment
#
#
# These are increasingly strong candidates for:
#
#
#       models/network/path.py
#
#
# while:
#
#
#       NetworkPathEvidenceEvaluator
#
#       NetworkPathAssessmentEvaluator
#
#
# belong in:
#
#
#       network/path.py
#
#
# ============================================================================
#
#
#       NOUNS / CONTRACTS -> models/
#
#       BEHAVIOR          -> network/
#
#
# ============================================================================


# ============================================================================
# models/network/ HAS NOW EARNED A STRONGER CASE
# ============================================================================
#
# Earlier we deliberately refused to create:
#
#
#       models/network/
#
#
# merely because the original directory tree had network files.
#
#
# Now we have reusable domain nouns that may be consumed by:
#
#
#       network behavior
#
#       candidate evaluation
#
#       telemetry
#
#       audit
#
#       orchestration
#
#
# That is actual architectural pressure.
#
#
# ============================================================================
#
#
#       PACKAGE EXISTS BECAUSE DOMAIN EXISTS.
#
#       DOMAIN DOES NOT EXIST BECAUSE PACKAGE EXISTS.
#
#
# ============================================================================


# ============================================================================
# ROUTING/NETWORK_CONTEXT.PY
# ============================================================================
#
# Part III-B makes the original:
#
#
#       routing/network_context.py
#
#
# even harder to justify.
#
#
# Network now has the responsibility to produce network facts.
#
#
# Routing should consume those facts.
#
#
# ============================================================================
#
#
#       NETWORK
#           |
#           | produces evidence / assessment
#           v
#       CANDIDATE EVALUATION
#           |
#           v
#       ROUTING
#
#
# ============================================================================


# ============================================================================
# DO NOT DUPLICATE NETWORK TRUTH
# ============================================================================
#
# Avoid:
#
#
#       network/path.py
#           has path state
#
#
# while:
#
#
#       routing/network_context.py
#           has another path state
#
#
# Which one is authoritative?
#
#
# ============================================================================
#
#
#       DUPLICATED TRUTH
#           ->
#       EVENTUAL CONTRADICTION
#
#
# ============================================================================


# ============================================================================
# PART III-C HANDOFF
# ============================================================================
#
# Part III-B established:
#
#
#       source -> destination
#
#       path evidence
#
#       path assessment
#
#       multiple broad path types
#
#       route evidence vs path evidence
#
#       operational aggregation
#
#
# Part III-C can now pressure this model with:
#
#
#       path instances
#
#       multiple clouds
#
#       multiple regions
#
#       multiple deployments
#
#       failure domains
#
#       correlated failures
#
#       SD-WAN
#
#       BGP convergence
#
#       freshness
#
#       evidence provenance
#
#       latency / jitter / packet loss
#
#       path-specific authorization
#
#       dynamic failover
#
#
# ============================================================================


# ============================================================================
# PART III-B FINAL ARCHITECTURE
# ============================================================================
#
#
#                         CONTROL PLANE
#
#                              BGP
#                               |
#                               v
#                         RouteEvidence
#                               |
#                               |
#                               +------------------+
#                                                  |
#                                                  |
#                         DATA PLANE               |
#                                                  |
#                      Synthetic Probe             |
#                            |                     |
#                            v                     |
#                 NetworkPathEvidence <------------+
#                            |
#                            v
#                NetworkPathAssessment
#                            |
#                            |
#                            v
#                 Candidate Evaluation
#                            |
#                            v
#                   RoutingCandidate
#                            |
#                            v
#                       AIRouter
#
#
# Policy joins at candidate evaluation.
#
# It does NOT live inside path assessment.
#
#
# ============================================================================


# ============================================================================
# PART III-B FINAL INVARIANTS
# ============================================================================
#
#
#       PATH IS SOURCE-RELATIVE
#
#       PATH EVIDENCE != ROUTE EVIDENCE
#
#       PATH EVIDENCE != PATH ASSESSMENT
#
#       PATH ASSESSMENT != PATH AUTHORIZATION
#
#       PATH AUTHORIZATION != AI SERVICE SELECTION
#
#       OPERATIONAL ASSESSMENT != POLICY EVALUATION
#
#       DIFFERENT PATHS != CONFLICTING EVIDENCE
#
#       DIFFERENT EVIDENCE TYPES != CONTRADICTORY EVIDENCE
#
#       PATH TYPE != PATH INSTANCE
#
#       COLLECTION POSITION != RESOURCE IDENTITY
#
#       ROUTING PROTOCOL != PATH TYPE
#
#       BGP ROUTE PRESENT != PATH AVAILABLE
#
#       BGP ROUTE ABSENT != NO ROUTE OF ANY KIND EXISTS
#
#       CONTROL PLANE != DATA PLANE
#
#       DATA PLANE != TRANSPORT
#
#       TCP != TLS != APPLICATION
#
#       NETWORK SUCCESS != APPLICATION SUCCESS
#
#       SERVICE AVAILABLE != INFERENCE SUCCESS
#
#       REACHABILITY != IDENTITY
#
#       WORKING PATH != TRUSTED PATH
#
#       OPERATIONALLY AVAILABLE != AUTHORIZED
#
#       AVAILABLE ALTERNATE PATH != AUTHORIZED ALTERNATE PATH
#
#       NETWORK FAILOVER != POLICY FAILOVER
#
#       NETWORK CONVERGENCE != POLICY-COMPLIANT RECOVERY
#
#       FORWARD PATH != RETURN PATH
#
#       OBSERVATION != OMNISCIENCE
#
#       OBSERVATION FAILURE != PATH FAILURE
#
#       UNKNOWN != UNAVAILABLE
#
#       ONE UNKNOWN PATH != ALL CONNECTIVITY UNKNOWN
#
#       KNOWN FAILURE + UNKNOWN ALTERNATIVE != TOTAL FAILURE
#
#       OBSERVED PATH SET != COMPLETE POSSIBLE PATH SET
#
#       DISCOVERED != EXPECTED
#
#       EXPECTED != AVAILABLE
#
#       AVAILABLE != AUTHORIZED
#
#       OBSERVED THEN != CONFIRMED NOW
#
#       TIMESTAMP != FRESHNESS DECISION
#
#       STALE EVIDENCE != FALSE EVIDENCE
#
#       TIME IS A DEPENDENCY TOO
#
#       STATE != SCORE
#
#       DECIMAL PRECISION != EPISTEMIC PRECISION
#
#       ASSESSMENT != SELECTION
#
#       NETWORK PATH SELECTION != AI SERVICE SELECTION
#
#       AGGREGATE REACHABILITY MAY BE TOO LOSSY
#       FOR PATH-SPECIFIC AUTHORIZATION
#
#       FILTER BY HARD CONSTRAINTS FIRST
#
#       OPTIMIZE SECOND
#
#       POLICY NEVER BECOMES A SCORE
#
#       OBSERVE != REMEDIATE
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#       QUERY COLLECTION != ASSERT OBJECT PAIR
#
#       INTERNAL CONSISTENCY != DOMAIN CORRECTNESS
#
#       FAIL CLOSED != FALSIFY STATE
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================
# FINAL PART III-B RULE
# ============================================================================
#
#
#       ROUTE EVIDENCE TELLS US
#       WHAT THE CONTROL PLANE KNOWS.
#
#
#       PATH EVIDENCE TELLS US
#       WHAT CONNECTIVITY OBSERVERS SAW.
#
#
#       PATH ASSESSMENT TELLS US
#       WHAT AGENT 11 CURRENTLY CONCLUDES
#       ABOUT OPERATIONAL CONNECTIVITY.
#
#
#       POLICY TELLS US
#       WHETHER THE REQUEST MAY USE IT.
#
#
#       CANDIDATE EVALUATION TELLS US
#       WHETHER THE AI DESTINATION IS VIABLE.
#
#
#       AIRouter SELECTS AMONG
#       ALREADY-EVALUATED CANDIDATES.
#
#
# ============================================================================
# END OF PART III-B
# ============================================================================

# ============================================================================
# network/path.py
#
# PART III-C
#
# SEIR-II:
# MULTI-CLOUD, SD-WAN, PATH IDENTITY, FAILURE DOMAINS,
# FRESHNESS, PROVENANCE, MEASUREMENTS, AND PATH-SPECIFIC POLICY
# ============================================================================
#
# PURPOSE
# -------
#
# Part III-A established:
#
#       ROUTE EVIDENCE
#
#
# Part III-B established:
#
#       PATH EVIDENCE
#
#       PATH ASSESSMENT
#
#
# Part III-C asks what happens when real enterprise infrastructure introduces:
#
#
#       multiple path instances
#
#       multiple clouds
#
#       multiple regions
#
#       multiple deployments
#
#       SD-WAN
#
#       BGP convergence
#
#       shared failure domains
#
#       path measurements
#
#       stale telemetry
#
#       evidence provenance
#
#       path-specific security requirements
#
#
# This section is intentionally future-facing.
#
#
# ============================================================================
# CENTRAL SEIR-II PROBLEM
# ============================================================================
#
# The SEIR-I abstraction:
#
#
#       service_id
#           +
#       path_type
#           ->
#       NetworkPathState
#
#
# was intentionally small.
#
#
# SEIR-II infrastructure eventually requires:
#
#
#       SOURCE
#           |
#           v
#       PATH INSTANCE
#           |
#           v
#       DESTINATION ENDPOINT
#
#
# with operational evidence attached to THAT relationship.
#
#
# ============================================================================
# PATH TYPE != PATH INSTANCE
# ============================================================================
#
# This is now unavoidable.
#
#
# Example:
#
#
#       NetworkPathType.VPN
#
#
# may describe:
#
#
#       vpn-tokyo-a
#
#       vpn-tokyo-b
#
#       vpn-virginia-a
#
#
# Those paths can have:
#
#
#       different states
#
#       different latency
#
#       different providers
#
#       different failure domains
#
#       different policy status
#
#
# Therefore:
#
#
#       PATH TYPE != PATH INSTANCE
#
#
# ============================================================================
# POSSIBLE FUTURE PATH IDENTITY
# ============================================================================
#
# A future model may therefore earn:
#
#
#       NetworkPathIdentity
#
#
# Conceptually:
#
#
#     class NetworkPathIdentity(Agent11BaseModel):
#
#         path_id: str
#
#         source_id: str
#
#         destination_id: str
#
#         path_type: NetworkPathType
#
#
# Do not add more fields until behavior requires them.
#
#
# ============================================================================
# IDENTITY != DESCRIPTION
# ============================================================================
#
# path_id should identify the path.
#
#
# Do not build identity from mutable properties such as:
#
#
#       latency
#
#       state
#
#       provider display name
#
#
# ============================================================================
# RESOURCE IDENTITY SHOULD SURVIVE STATE CHANGE
# ============================================================================
#
#
#       AVAILABLE
#           ->
#       DEGRADED
#           ->
#       UNAVAILABLE
#
#
# should not create three different path identities.
#
#
# ============================================================================
# ENDPOINT IDENTITY
# ============================================================================
#
# Part III-B used:
#
#
#       destination_id
#
#
# Eventually the destination may need to be an actual endpoint identity.
#
#
# Example:
#
#
#       AIService
#           |
#           +---- Deployment Tokyo
#           |         |
#           |         +---- private endpoint A
#           |
#           +---- Deployment Virginia
#                     |
#                     +---- private endpoint B
#
#
# Therefore:
#
#
#       SERVICE != DEPLOYMENT
#
#       DEPLOYMENT != ENDPOINT
#
#       ENDPOINT != PATH
#
#
# ============================================================================
# POSSIBLE FUTURE ENDPOINT CONTRACT
# ============================================================================
#
# network/endpoint.py may eventually earn:
#
#
#       NetworkEndpoint
#
#
# because endpoint identity is now consumed by:
#
#
#       path evidence
#
#       health evidence
#
#       candidate evaluation
#
#       telemetry
#
#
# That is real domain pressure.
#
#
# ============================================================================
# models/network/ HAS NOW EARNED EXISTENCE
# ============================================================================
#
# By SEIR-II we now have durable shared nouns:
#
#
#       NetworkEndpoint
#
#       NetworkPathIdentity
#
#       NetworkPathEvidence
#
#       NetworkPathAssessment
#
#       RouteEvidence
#
#       HealthEvidence
#
#       HealthAssessment
#
#
# These are no longer merely implementation helpers.
#
#
# They are domain contracts used across:
#
#
#       network/
#
#       routing/
#
#       telemetry/
#
#       audit/
#
#
# Therefore a future structure such as:
#
#
#       models/
#       └── network/
#           ├── __init__.py
#           ├── endpoint.py
#           ├── path.py
#           ├── route.py
#           └── health.py
#
#
# becomes legitimate.
#
#
# ============================================================================
# PACKAGE RULE
# ============================================================================
#
#
#       DOMAIN CREATES PACKAGE.
#
#       PACKAGE DOES NOT CREATE DOMAIN.
#
#
# ============================================================================
# MULTI-CLOUD
# ============================================================================
#
# Agent 11 may eventually observe paths across:
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
#       on-prem
#
#
# Example:
#
#
#                        +---- AWS
#                        |
#       Agent 11 --------+---- Azure
#                        |
#                        +---- GCP
#                        |
#                        +---- OCI
#                        |
#                        +---- on-prem
#
#
# ============================================================================
# CLOUD PROVIDER != ROUTING DOMAIN
# ============================================================================
#
# Preserve:
#
#
#       AIRoute.COMPANY_CLOUD_LLM
#
#
# independently from:
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
# A company-owned logical routing domain may span several providers.
#
#
# ============================================================================
#
#
#       ROUTING DOMAIN != CLOUD PROVIDER
#
#
# ============================================================================
# CLOUD PROVIDER != PATH TYPE
# ============================================================================
#
# AWS is not a path type.
#
# Azure is not a path type.
#
#
# A path might instead be:
#
#
#       PRIVATE_LINK
#
#       VPN
#
#       SD_WAN
#
#       INTERNET
#
#
# while connecting to infrastructure hosted in a particular provider.
#
#
# ============================================================================
#
#
#       CLOUD PROVIDER != NETWORK PATH TYPE
#
#
# ============================================================================
# CLOUD PROVIDER != FAILURE DOMAIN
# ============================================================================
#
# Two services in AWS may live in independent failure domains.
#
#
# Two services in different clouds may still share:
#
#
#       DNS
#
#       identity provider
#
#       carrier
#
#       gateway
#
#       on-prem transit
#
#
# Therefore:
#
#
#       DIFFERENT CLOUDS != INDEPENDENT FAILURE
#
#
# ============================================================================
# MULTI-CLOUD != RESILIENCE
# ============================================================================
#
# Merely placing workloads in:
#
#
#       AWS + Azure
#
#
# does not automatically create resilient independence.
#
#
# ============================================================================
# FAILURE DOMAIN
# ============================================================================
#
# SEIR-II may eventually need:
#
#
#       FailureDomain
#
#
# A failure domain describes infrastructure expected to fail together.
#
#
# Examples:
#
#
#       physical router
#
#       cloud region
#
#       availability zone
#
#       transit gateway
#
#       VPN concentrator
#
#       carrier circuit
#
#       DNS provider
#
#       identity provider
#
#       gateway
#
#
# ============================================================================
# PATH COUNT != FAILURE-DOMAIN COUNT
# ============================================================================
#
# Example:
#
#
#       vpn-a
#
#       vpn-b
#
#
# both terminate on:
#
#
#       firewall-01
#
#
# Then:
#
#
#       TWO PATHS
#
#
# does not mean:
#
#
#       TWO INDEPENDENT FAILURE DOMAINS
#
#
# ============================================================================
#
#
#       MULTI-PATH != RESILIENCE
#
#
# ============================================================================
# CORRELATED FAILURE
# ============================================================================
#
# Suppose:
#
#
#       private-link-a
#
#       vpn-a
#
#       sdwan-a
#
#
# all depend upon:
#
#
#       same cloud transit gateway
#
#
# One transit-gateway failure can remove all three.
#
#
# ============================================================================
# SHARED DEPENDENCY != INDEPENDENT PATH
# ============================================================================
#
# Future resilience analysis may therefore require dependency relationships.
#
#
# Do not hide that complexity inside:
#
#
#       path_count
#
#
# ============================================================================
# FAILURE-DOMAIN MODELING WARNING
# ============================================================================
#
# Do not immediately build a giant topology graph.
#
#
# Model only the failure relationships required by:
#
#
#       routing
#
#       resilience
#
#       audit
#
#
# ============================================================================
# SD-WAN
# ============================================================================
#
# SD-WAN is where Part III-C becomes especially interesting.
#
#
# An SD-WAN system may own:
#
#
#       overlay paths
#
#       SLA measurement
#
#       dynamic steering
#
#       circuit selection
#
#       failover
#
#
# It may choose among:
#
#
#       broadband Internet
#
#       MPLS
#
#       LTE / 5G
#
#       private circuits
#
#       cloud interconnect
#
#
# ============================================================================
# AGENT 11 SHOULD NOT REIMPLEMENT SD-WAN
# ============================================================================
#
# Agent 11 should consume the evidence necessary for its own domain.
#
#
# It should NOT become:
#
#
#       Cisco SD-WAN controller clone
#
#       Fortinet SD-WAN controller clone
#
#       VMware/VeloCloud clone
#
#
# ============================================================================
#
#
#       INFRASTRUCTURE COMPLEXITY
#           SHOULD BE TRANSLATED,
#           NOT REPLICATED.
#
#
# ============================================================================
# SD-WAN PATH EVIDENCE
# ============================================================================
#
# A future adapter might translate:
#
#
#       controller SLA state
#
#       loss
#
#       latency
#
#       jitter
#
#       circuit condition
#
#
# into:
#
#
#       NetworkPathEvidence
#
#
# ============================================================================
# SD-WAN BEST PATH != AGENT 11 BEST SERVICE
# ============================================================================
#
# Same lesson as BGP.
#
#
# SD-WAN may select:
#
#
#       best transport path
#
#
# Agent 11 selects:
#
#
#       best AI service candidate
#
#
# ============================================================================
#
#
#       SD-WAN SELECTION != AI SERVICE SELECTION
#
#
# ============================================================================
# SD-WAN FAILOVER != POLICY-COMPLIANT FAILOVER
# ============================================================================
#
# Example:
#
#
#       private circuit
#           fails
#
#
# SD-WAN chooses:
#
#
#       public Internet
#
#
# Network:
#
#
#       recovered
#
#
# Agent 11:
#
#
#       maybe prohibited
#
#
# ============================================================================
#
#
#       SD-WAN CONVERGENCE
#           !=
#       SECURITY APPROVAL
#
#
# ============================================================================
# CRITICAL ENTERPRISE RULE
# ============================================================================
#
#
#       THE NETWORK MAY LEGITIMATELY
#       RESTORE CONNECTIVITY
#
#
#       WHILE AGENT 11 LEGITIMATELY
#       REFUSES TO USE THAT CONNECTIVITY.
#
#
# ============================================================================
# THIS IS NOT A NETWORK FAILURE
# ============================================================================
#
# If:
#
#
#       Internet path AVAILABLE
#
#
# but:
#
#
#       policy DENIES Internet
#
#
# Agent 11 refusing the path is not a network failure.
#
#
# It is a policy decision.
#
#
# ============================================================================
# PATH-SPECIFIC POLICY
# ============================================================================
#
# SEIR-II may eventually need policy dimensions beyond:
#
#
#       DataClassification
#           x
#       AIRoute
#
#
# For example:
#
#
#       DataClassification
#           x
#       AIRoute
#           x
#       NetworkPathType
#
#
# or eventually:
#
#
#       path identity
#
#
# ============================================================================
# EXAMPLE
# ============================================================================
#
#
#       E9
#           +
#       COMPANY_CLOUD_LLM
#           +
#       PRIVATE_LINK
#
#           -> ALLOW
#
#
#       E9
#           +
#       COMPANY_CLOUD_LLM
#           +
#       INTERNET
#
#           -> DENY
#
#
# ============================================================================
# DESTINATION AUTHORIZED != EVERY PATH AUTHORIZED
# ============================================================================
#
# This is one of the most important SEIR-II policy pressures.
#
#
# ============================================================================
# PATH AUTHORIZATION BELONGS IN POLICY
# ============================================================================
#
# Do not add:
#
#
#       authorized: bool
#
#
# to:
#
#
#       NetworkPathEvidence
#
#
# Evidence describes observation.
#
# Policy describes permission.
#
#
# ============================================================================
# INDIVIDUAL PATH VIABILITY
# ============================================================================
#
# Once path-specific policy exists, destination-level:
#
#
#       NetworkPathAssessment.AVAILABLE
#
#
# becomes too coarse.
#
#
# Example:
#
#
#       PrivateLink
#           UNAVAILABLE
#
#
#       Internet
#           AVAILABLE
#
#
# aggregate:
#
#
#       AVAILABLE
#
#
# but policy:
#
#
#       Internet DENIED
#
#
# Thus:
#
#
#       aggregate reachability AVAILABLE
#
#
# while:
#
#
#       policy-compliant path set EMPTY
#
#
# ============================================================================
# FUTURE CANDIDATE PIPELINE
# ============================================================================
#
#
#       PATH EVIDENCE
#           |
#           v
#       INDIVIDUAL PATH ASSESSMENT
#           |
#           +
#       PATH POLICY
#           |
#           v
#       POLICY-COMPLIANT PATH SET
#           |
#           +
#       SERVICE HEALTH
#           |
#           +
#       MODEL CAPABILITY
#           |
#           +
#       DESTINATION POLICY
#           |
#           v
#       RoutingCandidate
#
#
# ============================================================================
# CANDIDATE VIABILITY != AGGREGATE NETWORK REACHABILITY
# ============================================================================
#
# Once path-specific authorization exists:
#
#
#       "some path works"
#
#
# is insufficient.
#
#
# We need:
#
#
#       "some permitted path works."
#
#
# ============================================================================
# HARD CONSTRAINTS FIRST
# ============================================================================
#
# Future path optimization may consider:
#
#
#       latency
#
#       jitter
#
#       loss
#
#       bandwidth
#
#       cost
#
#
# But:
#
#
#       authorization
#
#
# remains a hard constraint.
#
#
# ============================================================================
#
#
#       FILTER BY HARD CONSTRAINTS FIRST.
#
#       OPTIMIZE SECOND.
#
#
# ============================================================================
# POLICY NEVER BECOMES A SCORE
# ============================================================================
#
# Example:
#
#
#       Internet
#           latency = 10 ms
#
#
#       PrivateLink
#           latency = 30 ms
#
#
# If Internet is prohibited:
#
#
#       10 ms
#
#
# does not overpower:
#
#
#       DENY
#
#
# ============================================================================
#
#
#       FASTER != AUTHORIZED
#
#
# ============================================================================
# PATH MEASUREMENTS
# ============================================================================
#
# SEIR-II may collect:
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
#       availability
#
#
# These are measurements.
#
#
# They are not path state by themselves.
#
#
# ============================================================================
#
#
#       MEASUREMENT != INTERPRETATION
#
#
# ============================================================================
# LATENCY
# ============================================================================
#
# Example:
#
#
#       40 ms
#
#
# Is that:
#
#
#       AVAILABLE?
#
#       DEGRADED?
#
#
# It depends.
#
#
# ============================================================================
# LATENCY THRESHOLD != UNIVERSAL TRUTH
# ============================================================================
#
# 40 ms may be excellent for:
#
#
#       long-form reasoning
#
#
# but unacceptable for:
#
#
#       real-time voice interaction
#
#
# Therefore:
#
#
#       PATH STATE != WORKLOAD SUITABILITY
#
#
# ============================================================================
# JITTER
# ============================================================================
#
# Jitter may matter strongly for:
#
#
#       streaming
#
#       voice
#
#       interactive media
#
#
# and matter far less for:
#
#
#       batch inference
#
#
# ============================================================================
# PACKET LOSS
# ============================================================================
#
# Small packet loss may be:
#
#
#       tolerable
#
#       degraded
#
#       catastrophic
#
#
# depending upon transport and workload.
#
#
# ============================================================================
# BANDWIDTH
# ============================================================================
#
# Large model payloads or tool transfers may care about bandwidth.
#
#
# But:
#
#
#       BANDWIDTH != POLICY
#
#
# ============================================================================
# CAPACITY != CONNECTIVITY
# ============================================================================
#
# A path can be:
#
#
#       reachable
#
#
# while:
#
#
#       saturated
#
#
# Therefore:
#
#
#       CONNECTIVITY != CAPACITY
#
#
# ============================================================================
# POSSIBLE FUTURE MEASUREMENT MODEL
# ============================================================================
#
# Agent 11 may eventually earn something like:
#
#
#       NetworkPathMetrics
#
#
# containing:
#
#
#       latency_ms
#
#       jitter_ms
#
#       packet_loss_ratio
#
#       available_bandwidth_mbps
#
#
# But only if actual behavior consumes those values.
#
#
# ============================================================================
# NO METRIC DUMPING
# ============================================================================
#
# Do not copy every SD-WAN or router metric into Agent 11.
#
#
# ============================================================================
#
#
#       INFRASTRUCTURE HAS METRIC
#           !=
#       DOMAIN NEEDS METRIC
#
#
# ============================================================================
# DEGRADED
# ============================================================================
#
# SEIR-II may eventually define DEGRADED using explicit rules.
#
#
# Example:
#
#
#       path exists
#
#       loss above threshold
#
#       latency above threshold
#
#
# But those thresholds should be:
#
#
#       explicit
#
#       testable
#
#       configurable
#
#
# ============================================================================
# DO NOT HIDE THRESHOLDS
# ============================================================================
#
# Avoid:
#
#
#       if latency > 75:
#           degraded
#
#
# buried in infrastructure adapters.
#
#
# ============================================================================
# INFRASTRUCTURE ADAPTER REPORTS FACT
#
# ASSESSMENT POLICY INTERPRETS FACT
# ============================================================================
#
# Example:
#
#
#       SD-WAN adapter:
#
#           latency = 93 ms
#
#
#       path evaluator:
#
#           based on configured semantics
#           -> DEGRADED
#
#
# ============================================================================
# WORKLOAD-SPECIFIC SUITABILITY
# ============================================================================
#
# Candidate evaluation may later say:
#
#
#       path DEGRADED
#
#       +
#       LIGHT workload
#
#           -> acceptable
#
#
# while:
#
#
#       path DEGRADED
#
#       +
#       real-time workload
#
#           -> unacceptable
#
#
# ============================================================================
#
#
#       OPERATIONAL STATE != REQUEST SUITABILITY
#
#
# ============================================================================
# FRESHNESS
# ============================================================================
#
# Real network evidence ages quickly.
#
#
# Examples:
#
#
#       BGP evidence
#
#       SD-WAN SLA state
#
#       VPN tunnel status
#
#       synthetic probe
#
#
# all have temporal meaning.
#
#
# ============================================================================
# OBSERVED THEN != CONFIRMED NOW
# ============================================================================
#
# Every future evidence record should preserve:
#
#
#       observed_at
#
#
# ============================================================================
# FRESHNESS POLICY
# ============================================================================
#
# Different evidence may have different maximum useful ages.
#
#
# Example:
#
#
#       synthetic probe
#           perhaps seconds
#
#
#       BGP route observation
#           perhaps seconds
#
#
#       topology metadata
#           perhaps minutes/hours
#
#
# Exact values are configuration decisions.
#
#
# ============================================================================
# ONE GLOBAL TTL MAY BE WRONG
# ============================================================================
#
#
#       FRESHNESS REQUIREMENT
#           MAY DEPEND ON
#       EVIDENCE TYPE
#
#
# ============================================================================
# STALE != FALSE
# ============================================================================
#
# Historical evidence remains:
#
#
#       evidence of what was observed at time T.
#
#
# It may simply no longer be current enough for assessment.
#
#
# ============================================================================
# FRESHNESS SHOULD NOT MUTATE HISTORY
# ============================================================================
#
# Avoid changing:
#
#
#       AVAILABLE
#
#
# to:
#
#
#       UNKNOWN
#
#
# inside the old evidence object because time passed.
#
#
# Instead:
#
#
#       evidence = AVAILABLE at T
#
#       freshness = STALE now
#
#
# ============================================================================
# TIME IS A DEPENDENCY
# ============================================================================
#
# For deterministic tests, future evaluators should accept:
#
#
#       assessed_at
#
#
# rather than calling:
#
#
#       datetime.now()
#
#
# throughout internal logic.
#
#
# ============================================================================
# CLOCK SKEW
# ============================================================================
#
# Distributed network observers introduce:
#
#
#       clock skew
#
#       delayed events
#
#       telemetry buffering
#
#       reordered observations
#
#
# observed_at must therefore be interpreted carefully.
#
#
# ============================================================================
# OBSERVATION TIME != INGEST TIME
# ============================================================================
#
# Future architecture may eventually need:
#
#
#       observed_at
#
#       received_at
#
#
# if transport delay matters.
#
#
# Do not add both until behavior requires them.
#
#
# ============================================================================
# PROVENANCE
# ============================================================================
#
# Multi-observer systems eventually need to know:
#
#
#       who observed?
#
#       how?
#
#       from where?
#
#       through which system?
#
#
# ============================================================================
# POSSIBLE PROVENANCE
# ============================================================================
#
# Examples:
#
#
#       synthetic probe
#
#       SD-WAN controller
#
#       router telemetry
#
#       BGP monitor
#
#       cloud networking API
#
#       VPN controller
#
#
# ============================================================================
# SOURCE KNOWN != SOURCE TRUSTED
# ============================================================================
#
# Merely knowing:
#
#
#       observer = sdwan-controller-01
#
#
# does not prove the evidence is correct.
#
#
# ============================================================================
# TRUSTED != INFALLIBLE
# ============================================================================
#
# Trusted infrastructure can still be:
#
#
#       stale
#
#       misconfigured
#
#       buggy
#
#       compromised
#
#
# ============================================================================
# VALID MODEL != TRUSTED EVIDENCE
# ============================================================================
#
# Pydantic can prove:
#
#
#       field structure
#
#
# It cannot prove:
#
#
#       router telemetry is truthful
#
#
# ============================================================================
# EVIDENCE INDEPENDENCE
# ============================================================================
#
# Suppose:
#
#
#       SD-WAN says DEGRADED
#
#       Prometheus says DEGRADED
#
#       synthetic probe says DEGRADED
#
#
# Are those:
#
#
#       three independent confirmations?
#
#
# Not necessarily.
#
#
# ============================================================================
# CORRELATED EVIDENCE
# ============================================================================
#
# All three may derive from:
#
#
#       same broken circuit
#
#       same monitoring source
#
#       same controller
#
#
# ============================================================================
#
#
#       NUMBER OF OBSERVERS
#           !=
#       NUMBER OF INDEPENDENT EVIDENCE CHANNELS
#
#
# ============================================================================
# EVIDENCE CONFLICT
# ============================================================================
#
# Example:
#
#
#       SD-WAN controller:
#           AVAILABLE
#
#
#       probe:
#           UNAVAILABLE
#
#
# This may mean:
#
#
#       control plane healthy
#
#       data plane broken
#
#
# rather than:
#
#
#       one observer is wrong.
#
#
# ============================================================================
# DIFFERENT DIMENSIONS MAY APPEAR TO CONFLICT
# ============================================================================
#
# This repeats the lesson from health.py:
#
#
#       apparent disagreement
#
#
# may reveal:
#
#
#       insufficient domain dimensions.
#
#
# ============================================================================
# DO NOT SOLVE EVERYTHING WITH PRECEDENCE
# ============================================================================
#
# Avoid immediately writing:
#
#
#       probe always wins
#
#
# or:
#
#
#       SD-WAN always wins
#
#
# Ask first:
#
#
#       what exactly did each observer measure?
#
#
# ============================================================================
# MULTI-REGION
# ============================================================================
#
# One service may expose:
#
#
#       Tokyo endpoint
#
#       Virginia endpoint
#
#       Frankfurt endpoint
#
#
# with different:
#
#
#       path states
#
#       latency
#
#       policy
#
#       health
#
#
# ============================================================================
#
#
#       SERVICE HEALTH != DEPLOYMENT HEALTH
#
#       SERVICE PATH != ENDPOINT PATH
#
#
# ============================================================================
# DATA RESIDENCY
# ============================================================================
#
# Future path viability may interact with:
#
#
#       region
#
#       country
#
#       regulatory boundary
#
#
# But residency is not a network-health fact.
#
#
# ============================================================================
# LOCATION != AUTHORIZATION
# ============================================================================
#
# A Tokyo path may be:
#
#
#       AVAILABLE
#
#
# while policy still prohibits it.
#
#
# ============================================================================
# NETWORK LOCATION != DATA POLICY
# ============================================================================
#
# Keep those dimensions separate.
#
#
# ============================================================================
# MULTIPLE DEPLOYMENTS
# ============================================================================
#
# Example:
#
#
#       proprietary-model
#           |
#           +---- Azure deployment
#           |
#           +---- GCP deployment
#
#
# One logical AI service might expose both.
#
#
# ============================================================================
# MODEL != SERVICE != DEPLOYMENT != ENDPOINT
# ============================================================================
#
# Preserve this permanently.
#
#
# ============================================================================
# PATH TO SERVICE != PATH TO DEPLOYMENT
# ============================================================================
#
# SEIR-I could reason broadly about:
#
#
#       service_id
#
#
# SEIR-II may need:
#
#
#       endpoint-specific path evidence.
#
#
# ============================================================================
# DYNAMIC FAILOVER
# ============================================================================
#
# Future infrastructure may fail over automatically:
#
#
#       VPN
#
#       SD-WAN
#
#       BGP
#
#       cloud gateways
#
#
# Agent 11 must understand:
#
#
#       observed path may change
#
#
# even when:
#
#
#       destination identity remains constant.
#
#
# ============================================================================
# REALIZED PATH
# ============================================================================
#
# A mature system may eventually need to know:
#
#
#       intended path
#
#       observed path
#
#       realized path
#
#
# especially when infrastructure performs dynamic steering.
#
#
# ============================================================================
# EXPECTED PATH != REALIZED PATH
# ============================================================================
#
# Example:
#
#
#       expected:
#           PrivateLink
#
#
#       actual:
#           Internet
#
#
# This may be a major security event.
#
#
# ============================================================================
# NETWORK WORKING != NETWORK WORKING AS INTENDED
# ============================================================================
#
# Very important distinction.
#
#
# ============================================================================
# PATH DRIFT
# ============================================================================
#
# Future telemetry may detect:
#
#
#       intended private path
#
#       observed public path
#
#
# ============================================================================
# PATH DRIFT != PATH FAILURE
# ============================================================================
#
# Connectivity may still work perfectly.
#
#
# But policy/security posture may have changed.
#
#
# ============================================================================
# SECURITY INCIDENT WITHOUT AVAILABILITY INCIDENT
# ============================================================================
#
# Example:
#
#
#       Internet path working
#
#       private path bypassed
#
#
# operational availability:
#
#       GOOD
#
#
# security:
#
#       BAD
#
#
# ============================================================================
# SECURITY STATE != PATH STATE
# ============================================================================
#
# Do not encode:
#
#
#       security problem
#
#
# as:
#
#
#       UNAVAILABLE
#
#
# unless the path is actually unavailable.
#
#
# ============================================================================
# MANUAL QUARANTINE
# ============================================================================
#
# Security may intentionally prohibit:
#
#
#       an otherwise healthy path
#
#
# That should remain a separate control.
#
#
# ============================================================================
#
#
#       QUARANTINED != UNAVAILABLE
#
#
# ============================================================================
# OBSERVE != CONTROL
# ============================================================================
#
# Part III-C still does NOT grant network mutation.
#
#
# ============================================================================
# SD-WAN OBSERVER SHOULD NOT RECONFIGURE SD-WAN
# ============================================================================
#
# BGP observer should not advertise routes.
#
#
# VPN observer should not rebuild tunnels.
#
#
# ============================================================================
#
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#
# ============================================================================
# NETWORK REMEDIATION
# ============================================================================
#
# Future remediation may include:
#
#
#       change SD-WAN policy
#
#       establish backup tunnel
#
#       modify route
#
#       drain path
#
#       alter firewall
#
#
# Those require:
#
#
#       separate policy
#
#       explicit authority
#
#       audit
#
#       rollback
#
#
# ============================================================================
# OBSERVE -> REASON -> PROPOSE -> APPROVE -> EXECUTE
# ============================================================================
#
# A safer future architecture:
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
# VERIFY AFTER REMEDIATION
# ============================================================================
#
# If future systems modify infrastructure:
#
#
#       command succeeded
#
#
# does not establish:
#
#
#       desired network state achieved.
#
#
# ============================================================================
#
#
#       EXECUTION SUCCESS != OUTCOME SUCCESS
#
#
# ============================================================================
# ROLLBACK
# ============================================================================
#
# Any future automatic network mutation should define:
#
#
#       rollback conditions
#
#       rollback authority
#
#       rollback verification
#
#
# ============================================================================
# HEALTH / PATH / POLICY AFTER CHANGE
# ============================================================================
#
# After infrastructure changes:
#
#
#       re-observe
#
#       re-assess
#
#       re-evaluate policy
#
#
# Do not assume old evidence remains valid.
#
#
# ============================================================================
# TELEMETRY
# ============================================================================
#
# SEIR-II telemetry should eventually be able to answer:
#
#
#       Which path was observed?
#
#       Which path was selected by infrastructure?
#
#       Was it expected?
#
#       Was it permitted?
#
#       What was its state?
#
#       How fresh was the evidence?
#
#       Which observer reported it?
#
#       Did BGP converge?
#
#       Did SD-WAN steer traffic?
#
#
# ============================================================================
# TELEMETRY != DOMAIN MODEL
# ============================================================================
#
# Logging does not define path semantics.
#
#
# ============================================================================
# EXPLAINABILITY
# ============================================================================
#
# Future Agent 11 should produce explanations such as:
#
#
#       "The destination remained reachable after the private path failed,
#        but the remaining Internet path was prohibited for E9 data."
#
#
# That is much more useful than:
#
#
#       "Routing failed."
#
#
# ============================================================================
# STRUCTURED FACTS FIRST
# ============================================================================
#
# Human-readable explanations should derive from:
#
#
#       structured path evidence
#
#       structured policy decisions
#
#
# not free-form strings as authoritative truth.
#
#
# ============================================================================
# TESTING STRATEGY
# ============================================================================
#
# SEIR-II tests should separate:
#
#
#       DOMAIN TESTS
#
#       ADAPTER TESTS
#
#       INFRASTRUCTURE TESTS
#
#       INTEGRATION TESTS
#
#
# ============================================================================
# DOMAIN TESTS
# ============================================================================
#
# Test:
#
#
#       path assessment semantics
#
#       identity relationships
#
#       freshness rules
#
#       failure-domain rules
#
#
# without:
#
#
#       real Cisco equipment
#
#       real cloud infrastructure
#
#
# ============================================================================
# ADAPTER TESTS
# ============================================================================
#
# Test:
#
#
#       Cisco SD-WAN response
#           ->
#       Agent 11 evidence
#
#
#       BGP response
#           ->
#       RouteEvidence
#
#
# ============================================================================
# INFRASTRUCTURE TESTS
# ============================================================================
#
# Then students may use:
#
#
#       Cisco lab
#
#       FRRouting
#
#       cloud VPNs
#
#       cloud routers
#
#
# ============================================================================
# INTEGRATION TESTS
# ============================================================================
#
# Finally test:
#
#
#       route changes
#
#       SD-WAN failover
#
#       path evidence changes
#
#       policy-compliant candidate outcome
#
#
# ============================================================================
# EXCELLENT SD-WAN LAB SCENARIO
# ============================================================================
#
# Initial condition:
#
#
#       Private path
#           AVAILABLE
#
#
#       Internet path
#           AVAILABLE
#
#
#       E9 policy:
#           private only
#
#
# SD-WAN uses:
#
#
#       private path
#
#
# ============================================================================
# FAILURE EVENT
# ============================================================================
#
# Private path fails.
#
#
# SD-WAN automatically moves traffic to:
#
#
#       Internet
#
#
# ============================================================================
# NETWORK RESULT
# ============================================================================
#
#
#       connectivity AVAILABLE
#
#
# ============================================================================
# AGENT 11 RESULT
# ============================================================================
#
#
#       no policy-compliant path
#
#
# ============================================================================
# CORRECT OUTCOME
# ============================================================================
#
# Agent 11 refuses E9 inference.
#
#
# ============================================================================
# STUDENT LESSON
# ============================================================================
#
#
#       NETWORK AVAILABILITY
#           !=
#       SECURITY-COMPLIANT AVAILABILITY
#
#
# ============================================================================
# SECOND SD-WAN LAB
# ============================================================================
#
# Paths:
#
#
#       circuit-a
#           latency 15 ms
#
#
#       circuit-b
#           latency 40 ms
#
#
# Both authorized.
#
#
# Agent 11 may later optimize after policy filtering.
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
# THIRD SD-WAN LAB
# ============================================================================
#
# Paths:
#
#
#       circuit-a
#           AVAILABLE
#
#
#       circuit-b
#           AVAILABLE
#
#
# Both share:
#
#
#       same carrier
#
#
# Student:
#
#
#       "We have redundancy."
#
#
# Instructor:
#
#
#       "Do you?"
#
#
# ============================================================================
#
#
#       MULTIPLE PATHS != MULTIPLE FAILURE DOMAINS
#
#
# ============================================================================
# FOURTH SD-WAN LAB
# ============================================================================
#
# Controller says:
#
#
#       path AVAILABLE
#
#
# synthetic probe says:
#
#
#       path UNAVAILABLE
#
#
# Student must reason about:
#
#
#       control plane
#
#       data plane
#
#       evidence provenance
#
#
# ============================================================================
# FIFTH SD-WAN LAB
# ============================================================================
#
# SD-WAN changes path:
#
#
#       Private -> Internet
#
#
# but:
#
#
#       no outage occurs.
#
#
# Student must detect:
#
#
#       PATH DRIFT
#
#
# rather than:
#
#
#       availability failure.
#
#
# ============================================================================
# CISCO LAB PRESSURE
# ============================================================================
#
# Future Cisco/SD-WAN exercises can expose:
#
#
#       tunnel state
#
#       SLA classes
#
#       path preference
#
#       control connections
#
#       policy
#
#       BGP
#
#
# But students should translate Cisco-specific facts into Agent 11
# vocabulary.
#
#
# ============================================================================
#
#
#       CISCO VOCABULARY
#           !=
#       AGENT 11 DOMAIN VOCABULARY
#
#
# ============================================================================
# DO NOT LET VENDOR TERMS LEAK EVERYWHERE
# ============================================================================
#
# Vendor-specific vocabulary belongs primarily in:
#
#
#       adapters
#
#
# ============================================================================
# POSSIBLE FUTURE ADAPTER STRUCTURE
# ============================================================================
#
#
#       network/
#       └── adapters/
#           ├── bgp.py
#           ├── cisco_sdwan.py
#           ├── vpn.py
#           ├── aws.py
#           ├── azure.py
#           ├── gcp.py
#           └── oci.py
#
#
# Create adapters only as implementations actually exist.
#
#
# ============================================================================
# ADAPTER != DOMAIN MODEL
# ============================================================================
#
# Cisco-specific response objects should not become:
#
#
#       NetworkPathEvidence
#
#
# directly.
#
#
# They should be translated.
#
#
# ============================================================================
# ROUTING/NETWORK_CONTEXT.PY
# ============================================================================
#
# By III-C, routing/network_context.py likely deserves a serious deletion
# review.
#
#
# Network facts now belong in:
#
#
#       network/
#
#       models/network/
#
#
# Routing should consume those facts.
#
#
# ============================================================================
# DUPLICATED NETWORK STATE IS DANGEROUS
# ============================================================================
#
# Avoid:
#
#
#       network/path.py
#           says AVAILABLE
#
#
#       routing/network_context.py
#           says UNAVAILABLE
#
#
# ============================================================================
#
#
#       ONE DOMAIN FACT
#           SHOULD HAVE
#       ONE AUTHORITATIVE REPRESENTATION
#
#
# ============================================================================
# CANDIDATE EVALUATION
# ============================================================================
#
# The SEIR-II join point increasingly looks like:
#
#
#       Data policy -------------------------+
#                                            |
#       Path policy -------------------------+
#                                            |
#       Model capability --------------------+
#                                            |
#       Service health ----------------------+--> CandidateEvaluator
#                                            |
#       Endpoint evidence -------------------+
#                                            |
#       Path assessment ---------------------+
#                                            |
#       Failure-domain constraints ----------+
#                                            |
#                                            v
#                                   RoutingCandidate
#
#
# ============================================================================
# AIRouter REMAINS BORING
# ============================================================================
#
# AIRouter still should not know:
#
#
#       Cisco
#
#       BGP
#
#       SD-WAN
#
#       packet loss
#
#       ExpressRoute
#
#       Direct Connect
#
#       Cloud Interconnect
#
#
# It receives:
#
#
#       evaluated candidates.
#
#
# ============================================================================
# NEVER PUT EVERYTHING INTO AIRouter
# ============================================================================
#
# If AIRouter becomes:
#
#
#       network monitor
#
#       security policy engine
#
#       model registry
#
#       cloud adapter
#
#       SD-WAN controller
#
#
# the architecture has collapsed.
#
#
# ============================================================================
# SEIR-II FUTURE FLOW
# ============================================================================
#
#
#       BGP ------------------+
#                             |
#       SD-WAN ---------------+
#                             |
#       VPN telemetry --------+
#                             |
#       Cloud network APIs ---+
#                             |
#       Synthetic probes -----+
#                             |
#                             v
#                       PATH EVIDENCE
#                             |
#                             v
#                    Path Assessment
#                             |
#            +----------------+----------------+
#            |                                 |
#            v                                 v
#       telemetry                        path policy
#                                              |
#                                              v
#                                policy-compliant paths
#                                              |
#                         +--------------------+------------------+
#                         |                    |                  |
#                         v                    v                  v
#                   capability             health          destination policy
#                         |                    |                  |
#                         +--------------------+------------------+
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
# FUTURE-SELF CHECKLIST:
# BEFORE ADDING path_id
# ============================================================================
#
# Ask:
#
#
#       Do multiple same-type paths exist?
#
#       Does behavior need to distinguish them?
#
#       Does telemetry need stable identity?
#
#
# If yes:
#
#
#       path_id may be earned.
#
#
# ============================================================================
# FUTURE-SELF CHECKLIST:
# BEFORE ADDING CLOUD PROVIDER
# ============================================================================
#
# Ask:
#
#
#       Is this really provider identity?
#
#       Or is it deployment identity?
#
#       Or path identity?
#
#       Or routing domain?
#
#
# ============================================================================
# FUTURE-SELF CHECKLIST:
# BEFORE ADDING FAILURE DOMAIN
# ============================================================================
#
# Ask:
#
#
#       What decision consumes it?
#
#       Is the dependency actually shared?
#
#       Is failure correlation observable?
#
#
# ============================================================================
# FUTURE-SELF CHECKLIST:
# BEFORE ADDING A METRIC
# ============================================================================
#
# Ask:
#
#
#       What decision consumes the metric?
#
#       What units?
#
#       What freshness?
#
#       What threshold?
#
#       Is threshold workload-specific?
#
#
# ============================================================================
# FUTURE-SELF CHECKLIST:
# BEFORE ADDING A SCORE
# ============================================================================
#
# Ask:
#
#
#       What does this score mean?
#
#       Are its dimensions comparable?
#
#       Can it override policy?
#
#
# If yes to the last question:
#
#
#       DELETE IT.
#
#
# ============================================================================
# FUTURE-SELF CHECKLIST:
# BEFORE ADDING SD-WAN CONTROL
# ============================================================================
#
# Ask:
#
#
#       Are we observing or mutating?
#
#       What authority is required?
#
#       What is rollback?
#
#       What is verification?
#
#       What is audit?
#
#
# ============================================================================
# CHEWBACCA SD-WAN REVIEW #1
# ============================================================================
#
# Student:
#
#
#       "SD-WAN restored Internet connectivity."
#
#
# Chewbacca:
#
#
#       "Was Internet authorized?"
#
#
# ============================================================================
# CHEWBACCA SD-WAN REVIEW #2
# ============================================================================
#
# Student:
#
#
#       "We have two VPNs, so we have redundancy."
#
#
# Chewbacca:
#
#
#       "Show me the failure domains."
#
#
# ============================================================================
# CHEWBACCA SD-WAN REVIEW #3
# ============================================================================
#
# Student:
#
#
#       "The Cisco controller says healthy."
#
#
# Chewbacca:
#
#
#       "What does the data-plane probe say?"
#
#
# ============================================================================
# CHEWBACCA SD-WAN REVIEW #4
# ============================================================================
#
# Student:
#
#
#       "The Internet path is 20 ms faster."
#
#
# Chewbacca:
#
#
#       "Policy says no."
#
#
# ============================================================================
# CHEWBACCA SD-WAN REVIEW #5
# ============================================================================
#
# Student:
#
#
#       "I added an API call to change the SD-WAN policy
#        inside NetworkPathEvaluator."
#
#
# Chewbacca:
#
#
#       "No."
#
#
# ============================================================================
# PART III-C FINAL INVARIANTS
# ============================================================================
#
#
#       PATH TYPE != PATH INSTANCE
#
#       PATH IDENTITY != PATH STATE
#
#       SERVICE != DEPLOYMENT
#
#       DEPLOYMENT != ENDPOINT
#
#       ENDPOINT != PATH
#
#       ROUTING DOMAIN != CLOUD PROVIDER
#
#       CLOUD PROVIDER != PATH TYPE
#
#       CLOUD PROVIDER != FAILURE DOMAIN
#
#       DIFFERENT CLOUDS != INDEPENDENT FAILURE
#
#       MULTI-CLOUD != RESILIENCE
#
#       PATH COUNT != FAILURE-DOMAIN COUNT
#
#       MULTI-PATH != RESILIENCE
#
#       SHARED DEPENDENCY != INDEPENDENT PATH
#
#       SD-WAN SELECTION != AI SERVICE SELECTION
#
#       SD-WAN CONVERGENCE != SECURITY APPROVAL
#
#       NETWORK AVAILABILITY != SECURITY-COMPLIANT AVAILABILITY
#
#       DESTINATION AUTHORIZED != EVERY PATH AUTHORIZED
#
#       AGGREGATE REACHABILITY != POLICY-COMPLIANT REACHABILITY
#
#       FASTER != AUTHORIZED
#
#       MEASUREMENT != INTERPRETATION
#
#       PATH STATE != WORKLOAD SUITABILITY
#
#       CONNECTIVITY != CAPACITY
#
#       INFRASTRUCTURE HAS METRIC != DOMAIN NEEDS METRIC
#
#       OBSERVED THEN != CONFIRMED NOW
#
#       TIMESTAMP != FRESHNESS DECISION
#
#       STALE != FALSE
#
#       OBSERVATION TIME != INGEST TIME
#
#       SOURCE KNOWN != SOURCE TRUSTED
#
#       TRUSTED != INFALLIBLE
#
#       VALID MODEL != TRUSTED EVIDENCE
#
#       NUMBER OF OBSERVERS != NUMBER OF INDEPENDENT EVIDENCE CHANNELS
#
#       EXPECTED PATH != REALIZED PATH
#
#       NETWORK WORKING != NETWORK WORKING AS INTENDED
#
#       PATH DRIFT != PATH FAILURE
#
#       SECURITY STATE != PATH STATE
#
#       QUARANTINED != UNAVAILABLE
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#       OBSERVE != REMEDIATE
#
#       EXECUTION SUCCESS != OUTCOME SUCCESS
#
#       FILTER BY HARD CONSTRAINTS FIRST
#
#       OPTIMIZE SECOND
#
#       POLICY NEVER BECOMES A SCORE
#
#       ONE DOMAIN FACT SHOULD HAVE ONE AUTHORITATIVE REPRESENTATION
#
#       INFRASTRUCTURE COMPLEXITY SHOULD BE TRANSLATED,
#       NOT REPLICATED
#
#       FUTURE-AWARE != FUTURE-BLOATED
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
#       AGENT 11 MUST STILL DETERMINE
#       WHETHER THAT PATH IS PERMITTED.
#
#
#       MULTIPLE WORKING PATHS
#       DO NOT GUARANTEE
#       MULTIPLE INDEPENDENT FAILURE DOMAINS.
#
#
#       THE FASTEST PATH
#       IS NOT AUTOMATICALLY
#       THE RIGHT PATH.
#
#
#       THE PATH SELECTED
#       BY NETWORK INFRASTRUCTURE
#       IS NOT AUTOMATICALLY
#       THE PATH AUTHORIZED
#       FOR AI DATA.
#
#
# ============================================================================
# END OF PART III-C
# ============================================================================
