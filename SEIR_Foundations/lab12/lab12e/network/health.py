"""
Agent 11 Network Health
=======================

PART I
------

Infrastructure-neutral service-health semantics.

This module establishes the Agent 11 behavioral boundary for reasoning about
the current operational condition of an AI service.

The central question answered by this module is:

    WHAT IS THE CURRENT OPERATIONAL CONDITION
    OF THIS AI SERVICE?

This module does NOT answer:

    Does an endpoint exist?
        -> network/endpoint.py

    Can Agent 11 reach the endpoint?
        -> network/path.py

    Is this request authorized to use the service?
        -> policy/

    Does the model support the requested capability?
        -> model/capability evaluation

    Should routing select this service?
        -> routing/

The distinction is intentional.

Agent 11 eventually combines several independent facts when determining
whether an AI destination is viable:

    POLICY PERMITTED
        +
    SERVICE CAPABLE
        +
    SERVICE AVAILABLE
        +
    PATH AVAILABLE

No single subsystem should silently answer all four questions.


===========================================================================
PRIMARY ARCHITECTURAL RULE
===========================================================================

    HEALTH.PY DOES NOT ANSWER:

        "SHOULD I ROUTE HERE?"


    HEALTH.PY ANSWERS:

        "WHAT IS THE CURRENT OPERATIONAL
         CONDITION OF THIS SERVICE?"


Health information is evidence consumed by later decision-making behavior.

Health is not routing.


===========================================================================
IMPORTANT DISTINCTIONS
===========================================================================

    ENDPOINT EXISTS
        !=
    SERVICE HEALTHY


    SERVICE HEALTHY
        !=
    PATH AVAILABLE


    PATH AVAILABLE
        !=
    AUTHORIZED


    AUTHORIZED
        !=
    SELECTED


A service may have a known endpoint while being operationally unavailable.

A service may be operationally available while Agent 11 has no usable
network path to it.

A service may be healthy and reachable while organizational policy prohibits
the current request from using it.

A service may be healthy, reachable, and authorized while another viable
service is preferred by routing.

These conditions must remain independently observable.


===========================================================================
HEALTH IS NOT A BOOLEAN
===========================================================================

A Boolean representation such as:

    healthy = True

or:

    healthy = False

is insufficient for Agent 11.

Consider an infrastructure observation failure:

    Kubernetes API timeout

That observation does not establish:

    SERVICE UNAVAILABLE

It establishes:

    CURRENT SERVICE CONDITION CANNOT BE DETERMINED
    FROM THIS EVIDENCE SOURCE

Agent 11 therefore preserves a four-state service-health vocabulary:

    AVAILABLE

    DEGRADED

    UNAVAILABLE

    UNKNOWN


The exact enum is defined in:

    models/enums/network_enums.py


===========================================================================
AVAILABLE
===========================================================================

AVAILABLE means that the available operational evidence supports the
conclusion that the service is currently operating normally according to the
semantics of the evidence source.

It does NOT mean:

    the service is authorized for this request

    the network path is available

    the model supports the requested capability

    inference will necessarily succeed

    routing must select the service


Therefore:

    AVAILABLE != AUTHORIZED

    AVAILABLE != REACHABLE

    AVAILABLE != CAPABLE

    AVAILABLE != SELECTED


===========================================================================
DEGRADED
===========================================================================

DEGRADED means that the service retains some operational capability while
evidence indicates an impaired condition.

Examples in future implementations might include:

    reduced replica availability

    elevated latency

    partial backend failure

    reduced inference capacity

    queue saturation

    impaired accelerator capacity

The specific evidence belongs to the infrastructure-specific evidence
provider.

DEGRADED does NOT automatically mean that routing must reject the service.

For example, a future routing system might determine:

    LIGHT workload + DEGRADED service
        -> potentially usable

while:

    HEAVY workload + DEGRADED service
        -> potentially unsuitable

The health state itself has not changed.

The workload requirement has changed.

Therefore:

    HEALTH STATE
        !=
    WORKLOAD SUITABILITY


===========================================================================
UNAVAILABLE
===========================================================================

UNAVAILABLE means that operational evidence establishes that the service
cannot currently perform its intended work according to the semantics of the
evidence source.

This is a positive operational conclusion.

It should not be used merely because information is missing.

Therefore:

    KNOWN FAILURE
        -> potentially UNAVAILABLE

but:

    UNKNOWN CONDITION
        -> UNKNOWN


===========================================================================
UNKNOWN
===========================================================================

UNKNOWN means that Agent 11 cannot currently establish the service's
operational condition from the available evidence.

Possible causes include:

    no evidence exists

    evidence is stale

    an evidence source cannot be queried

    authorization prevents observation

    an infrastructure control plane is unavailable

    a service has no configured mapping

    evidence is contradictory

UNKNOWN is a first-class state.

It is not an alias for UNAVAILABLE.


===========================================================================
CRITICAL INVARIANT
===========================================================================

    UNKNOWN != UNAVAILABLE


UNKNOWN says:

    "I cannot currently establish the operational condition."


UNAVAILABLE says:

    "I have operational evidence that the service is unavailable."


These statements are materially different.

Routing may eventually fail closed when health is UNKNOWN.

That does not give the health subsystem permission to rewrite UNKNOWN as
UNAVAILABLE.


===========================================================================
FAIL CLOSED != FALSIFY STATE
===========================================================================

Agent 11 should preserve evidence honestly.

If the system cannot establish whether a service is available, the health
state should remain UNKNOWN.

A later security or routing layer may conservatively determine that UNKNOWN
is insufficient for routing.

That produces:

    UNKNOWN
        |
        v
    ROUTING REFUSES TO USE SERVICE

not:

    UNKNOWN
        |
        v
    HEALTH LIES AND REPORTS UNAVAILABLE


The former preserves provenance and supports accurate telemetry.

The latter destroys information.


===========================================================================
MODEL HEALTH != SERVICE HEALTH
===========================================================================

Agent 11 distinguishes:

    AIModel
        =
    logical model identity


    AIService
        =
    a service exposing a model for use


Therefore:

    MODEL != SERVICE


A logical model does not necessarily become "down."

A particular service exposing that model may become unavailable.

For example:

    proprietary-model-v4

could eventually be exposed through:

    company-cloud-primary

    company-cloud-secondary

    company-onprem-primary


Their health states could simultaneously be:

    company-cloud-primary
        -> AVAILABLE

    company-cloud-secondary
        -> DEGRADED

    company-onprem-primary
        -> UNAVAILABLE


while all three services reference the same logical AI model.

Health therefore correlates with the service identifier in SEIR-I.

Future deployment-level health may introduce a more granular identity when
the architecture earns it.


===========================================================================
CURRENT CORRELATION != PERMANENT DOMAIN IDENTITY
===========================================================================

SEIR-I uses:

    service_id

as the correlation identifier for health evidence.

This is intentionally simple.

Future infrastructure may require:

    service
        |
        +-- deployment A
        |
        +-- deployment B
        |
        +-- deployment C


with independent health states.

For example:

    Tokyo deployment
        -> AVAILABLE

    Virginia deployment
        -> UNAVAILABLE


At that point:

    SERVICE HEALTH
        !=
    DEPLOYMENT HEALTH


Agent 11 should introduce deployment identity only when actual infrastructure
requires it.

Do not prematurely model hypothetical complexity.

    FUTURE-AWARE != FUTURE-BLOATED


===========================================================================
HEALTH != CAPABILITY
===========================================================================

A service may be completely operational while its model cannot perform the
requested task.

For example:

    service state
        -> AVAILABLE

    requested capability
        -> SECURITY_ANALYSIS

    model capability
        -> unsupported


The correct interpretation is:

    SERVICE AVAILABLE

    CAPABILITY MISMATCH


not:

    SERVICE UNAVAILABLE


Therefore:

    CAPABILITY MISMATCH != SERVICE UNAVAILABLE


This distinction is essential for accurate routing diagnostics and telemetry.


===========================================================================
HEALTH != ENDPOINT PRESENCE
===========================================================================

Endpoint discovery and service health answer different questions.

An endpoint may exist while the service behind it is unhealthy.

Conversely, an application may be locally healthy while Agent 11 lacks
current endpoint evidence for reaching it.

Therefore:

    ENDPOINT KNOWN
        !=
    SERVICE AVAILABLE


Endpoint behavior belongs in:

    network/endpoint.py


===========================================================================
HEALTH != NETWORK PATH
===========================================================================

A service may be healthy while Agent 11 cannot reach it.

For example:

    service state
        -> AVAILABLE

    VPN
        -> DOWN

    network path
        -> UNAVAILABLE


Both facts may simultaneously be true.

The health subsystem must not rewrite:

    AVAILABLE

as:

    UNAVAILABLE

merely because the network path is unavailable.

That would confuse service condition with network condition.

Network-path behavior belongs in:

    network/path.py


===========================================================================
HEALTH != POLICY
===========================================================================

A service may be:

    AVAILABLE

    reachable

    capable

while organizational policy still prohibits the current request from using
that destination.

For example:

    EXTERNAL_FM
        -> AVAILABLE

while:

    E8 data
        -> external routing denied


The service remains AVAILABLE.

The request remains prohibited from using it.

Therefore:

    HEALTHY != PERMITTED


Policy belongs in:

    policy/


===========================================================================
HEALTH != ROUTING
===========================================================================

The health subsystem reports operational condition.

Routing consumes operational condition.

The health subsystem does not determine whether a service becomes a viable
routing candidate.

Conceptually:

    HEALTH
        |
        | ServiceState
        v
    CANDIDATE EVALUATION
        |
        +-- policy
        +-- capability
        +-- service health
        +-- network path
        |
        v
    RoutingCandidate


This boundary becomes particularly important for DEGRADED services.

Health should report:

    DEGRADED

Candidate evaluation may later decide whether DEGRADED is sufficient for the
specific workload.

Therefore:

    HEALTH REPORTS CONDITION.

    ROUTING INTERPRETS CONDITION
    IN THE CONTEXT OF VIABILITY.


===========================================================================
DEPENDENCY INVERSION
===========================================================================

Agent 11's generic health behavior must not depend directly upon a particular
infrastructure technology.

Today, health evidence may be static.

Soon, it may come from Kubernetes.

Later, it may come from:

    Prometheus

    OpenTelemetry

    service mesh telemetry

    cloud-provider APIs

    inference gateways

    internal health platforms


The dependency direction should remain:

    NetworkHealthEvaluator
            |
            v
    HealthEvidenceSource
            ^
            |
      +-----+------------------+
      |                        |
    Static                 Kubernetes
    Evidence               Evidence
    Source                 Source


The high-level component depends upon an abstraction.

Infrastructure-specific implementations satisfy that abstraction.


===========================================================================
DEPENDENCY INJECTION
===========================================================================

The health evaluator receives its evidence source from outside.

It does not construct the source itself.

Therefore:

    COMPONENT USES DEPENDENCY
        !=
    COMPONENT CHOOSES DEPENDENCY


This is ordinary constructor injection.

Agent 11 does not require a dependency-injection framework merely to practice
dependency inversion.

The application's composition layer decides which implementation to supply.


===========================================================================
PART I SCOPE
===========================================================================

Part I implements:

    HealthEvidenceSource

    StaticHealthEvidenceSource

    NetworkHealthEvaluator


Part I intentionally does NOT implement:

    Kubernetes SDK integration

    Kubernetes authentication

    Kubernetes Deployment inspection

    Pod readiness inspection

    Prometheus queries

    inference health probes

    GPU telemetry

    network probing

    routing decisions

    policy decisions

    capability matching

    remediation

    service restart

    deployment scaling


Those responsibilities either belong to later parts of this module or to
other Agent 11 subsystems.


===========================================================================
PART I FINAL INVARIANTS
===========================================================================

    HEALTH != ROUTING

    HEALTH != POLICY

    HEALTH != CAPABILITY

    HEALTH != NETWORK PATH

    HEALTH != ENDPOINT PRESENCE

    MODEL != SERVICE

    AVAILABLE != AUTHORIZED

    AVAILABLE != REACHABLE

    AVAILABLE != SELECTED

    DEGRADED != UNAVAILABLE

    UNKNOWN != UNAVAILABLE

    ABSENCE OF EVIDENCE != EVIDENCE OF ABSENCE

    FAIL CLOSED != FALSIFY STATE

    HEALTH STATE != WORKLOAD SUITABILITY

    COMPONENT USES DEPENDENCY
        !=
    COMPONENT CHOOSES DEPENDENCY

    FUTURE-AWARE != FUTURE-BLOATED
"""


from typing import Protocol

from ..models.enums.network_enums import ServiceState


# ============================================================================
# HEALTH EVIDENCE SOURCE
# ============================================================================


class HealthEvidenceSource(Protocol):
    """
    Behavioral contract for service-health evidence providers.

    Implementations translate their infrastructure-specific observations
    into Agent 11's service-state vocabulary.

    Examples of possible implementations include:

        StaticHealthEvidenceSource

        KubernetesHealthEvidenceSource

        PrometheusHealthEvidenceSource

        ServiceMeshHealthEvidenceSource

    The evidence source answers:

        "What operational state does the available evidence currently
         support for this service?"

    It does NOT answer:

        whether the service is authorized

        whether a network path is available

        whether the model supports a requested capability

        whether routing should select the service

    Those questions belong to other Agent 11 subsystems.
    """

    def get_state(
        self,
        service_id: str,
    ) -> ServiceState:
        """
        Return the currently supported operational state for a service.

        UNKNOWN must be preserved when the evidence source cannot establish
        the service's operational condition.

        Implementations must not silently translate uncertainty into
        UNAVAILABLE.
        """
        ...


# ============================================================================
# STATIC HEALTH EVIDENCE SOURCE
# ============================================================================


class StaticHealthEvidenceSource:
    """
    Simple in-memory service-health evidence source for SEIR-I.

    This implementation provides deterministic health evidence without
    requiring external infrastructure.

    It is useful for:

        teaching

        unit testing

        local development

        early Agent 11 integration

    Each configured service identifier maps directly to an Agent 11
    ServiceState.

    Example:

        {
            "external-primary": ServiceState.AVAILABLE,
            "company-cloud-primary": ServiceState.DEGRADED,
            "company-onprem-primary": ServiceState.UNAVAILABLE,
        }


    ------------------------------------------------------------------------
    UNKNOWN SERVICES
    ------------------------------------------------------------------------

    A service identifier missing from this source returns:

        ServiceState.UNKNOWN

    It does NOT return:

        ServiceState.UNAVAILABLE


    Why?

    Because this source has no evidence about the missing service.

    Missing evidence means:

        "I don't know."

    It does not mean:

        "I know the service is down."


    Therefore:

        ABSENCE OF EVIDENCE
            !=
        EVIDENCE OF ABSENCE
    """

    def __init__(
        self,
        service_states: dict[str, ServiceState],
    ) -> None:
        """
        Initialize the static evidence source.

        Parameters
        ----------
        service_states:
            Mapping from Agent 11 service identifiers to their currently
            configured operational states.

        The mapping contains operational evidence only.

        It does not grant authorization and does not establish network
        reachability.
        """
        self._service_states = service_states

    def get_state(
        self,
        service_id: str,
    ) -> ServiceState:
        """
        Return the configured operational state for a service.

        Unknown service identifiers return ServiceState.UNKNOWN.

        This behavior intentionally preserves uncertainty.
        """
        return self._service_states.get(
            service_id,
            ServiceState.UNKNOWN,
        )


# ============================================================================
# NETWORK HEALTH EVALUATOR
# ============================================================================


class NetworkHealthEvaluator:
    """
    Infrastructure-neutral evaluator for Agent 11 service health.

    NetworkHealthEvaluator receives a HealthEvidenceSource through constructor
    injection.

    The evaluator therefore does not know whether health evidence originated
    from:

        static configuration

        Kubernetes

        Prometheus

        a service mesh

        a cloud API

        an inference gateway

        another future infrastructure system


    ------------------------------------------------------------------------
    RESPONSIBILITY
    ------------------------------------------------------------------------

    This class owns:

        requesting normalized service-health evidence


    This class does NOT own:

        infrastructure authentication

        Kubernetes client construction

        Kubernetes discovery

        Prometheus queries

        HTTP health probes

        model invocation

        model capability matching

        endpoint discovery

        network-path evaluation

        policy evaluation

        routing selection

        remediation


    ------------------------------------------------------------------------
    WHY THERE IS NO is_service_available()
    ------------------------------------------------------------------------

    This class intentionally does not expose:

        is_service_available(service_id) -> bool


    Such a method would immediately require interpretation such as:

        AVAILABLE
            -> True

        DEGRADED
            -> ???

        UNAVAILABLE
            -> False

        UNKNOWN
            -> False


    The question represented by "???" reveals the problem.

    That method would no longer be asking:

        "What is the service state?"

    It would be asking:

        "Is this service state sufficient for some particular purpose?"


    That second question belongs to the consumer of health evidence.

    Candidate evaluation may eventually determine that DEGRADED is sufficient
    for one workload and insufficient for another.

    Therefore this evaluator preserves the richer ServiceState rather than
    prematurely collapsing it into a Boolean.


    ------------------------------------------------------------------------
    CRITICAL BOUNDARY
    ------------------------------------------------------------------------

        HEALTH REPORTS CONDITION.

        ROUTING INTERPRETS CONDITION
        IN THE CONTEXT OF VIABILITY.
    """

    def __init__(
        self,
        health_source: HealthEvidenceSource,
    ) -> None:
        """
        Initialize the health evaluator with an injected evidence source.

        The evaluator does not construct its dependency.

        Therefore:

            COMPONENT USES DEPENDENCY
                !=
            COMPONENT CHOOSES DEPENDENCY
        """
        self._health_source = health_source

    def get_service_state(
        self,
        service_id: str,
    ) -> ServiceState:
        """
        Return the current operational state reported by the configured
        health-evidence source.

        The returned value remains an operational fact.

        No policy, capability, reachability, or routing interpretation is
        performed here.
        """
        return self._health_source.get_state(service_id)


# ============================================================================
# END OF PART I
# ============================================================================
#
# At this point Agent 11 has an infrastructure-neutral health boundary:
#
#
#                     NetworkHealthEvaluator
#                              |
#                              v
#                     HealthEvidenceSource
#                              ^
#                              |
#                  StaticHealthEvidenceSource
#
#
# Part II extends the architecture:
#
#
#                     NetworkHealthEvaluator
#                              |
#                              v
#                     HealthEvidenceSource
#                              ^
#                              |
#                 +------------+------------+
#                 |                         |
#                 v                         v
#          StaticHealthEvidence      KubernetesHealthEvidence
#          Source                    Source
#                                            |
#                                            v
#                                  Kubernetes infrastructure
#
#
# The important point is that NetworkHealthEvaluator does not change.
#
# Kubernetes becomes another source of evidence.
#
# It does not become Agent 11's health architecture.
#
#
# FINAL REMINDER:
#
#     KUBERNETES CAN TELL US SOMETHING
#     ABOUT THE CONDITION OF A WORKLOAD.
#
#     IT CANNOT TELL AGENT 11 WHETHER
#     E8 DATA IS AUTHORIZED TO GO THERE.
#
#
#     HEALTHY != PERMITTED
#
# ============================================================================

# ============================================================================
# PART II
#
# KUBERNETES HEALTH EVIDENCE AND INFRASTRUCTURE ADAPTATION
# ============================================================================
#
# PURPOSE
# -------
#
# Part I established an infrastructure-neutral health contract:
#
#
#       NetworkHealthEvaluator
#               |
#               v
#       HealthEvidenceSource
#
#
# Part II provides one infrastructure-specific implementation:
#
#
#       KubernetesHealthEvidenceSource
#
#
# Kubernetes is therefore a SOURCE OF HEALTH EVIDENCE.
#
# Kubernetes does not become Agent 11's health domain.
#
#
# ============================================================================
# ARCHITECTURE
# ============================================================================
#
#
#                     NetworkHealthEvaluator
#                              |
#                              v
#                     HealthEvidenceSource
#                              ^
#                              |
#                 +------------+------------+
#                 |                         |
#                 v                         v
#       StaticHealthEvidenceSource   KubernetesHealthEvidenceSource
#                                             |
#                                             v
#                                  KubernetesDeploymentReader
#                                             ^
#                                             |
#                                  KubernetesSDKDeploymentReader
#                                             |
#                                             v
#                                      Kubernetes API
#
#
# There are deliberately TWO translation boundaries here.
#
#
# Boundary 1:
#
#       Kubernetes SDK objects
#               |
#               v
#       KubernetesDeploymentReader
#               |
#               v
#       simple replica observations
#
#
# Boundary 2:
#
#       replica observations
#               |
#               v
#       KubernetesHealthEvidenceSource
#               |
#               v
#       Agent 11 ServiceState
#
#
# The first boundary isolates the infrastructure SDK.
#
# The second boundary owns the interpretation of infrastructure evidence.
#
#
# ============================================================================
# PRIMARY RULE
# ============================================================================
#
#       KUBERNETES PROVIDES EVIDENCE.
#
#       AGENT 11 OWNS THE MEANING
#       OF THAT EVIDENCE.
#
#
# ============================================================================
# CRITICAL INVARIANTS
# ============================================================================
#
#       KUBERNETES != AGENT 11
#
#       KUBERNETES SERVICE != AI SERVICE
#
#       KUBERNETES DEPLOYMENT != AI SERVICE
#
#       POD != AI MODEL
#
#       POD != AI SERVICE
#
#       POD READY != INFERENCE HEALTHY
#
#       AVAILABLE REPLICA != AUTHORIZED DESTINATION
#
#       KUBERNETES HEALTH != NETWORK REACHABILITY
#
#       KUBERNETES HEALTH != ROUTING VIABILITY
#
#       KUBERNETES HEALTH != MODEL CAPABILITY
#
#       OBSERVATION FAILURE != SERVICE FAILURE
#
#       CONTROL-PLANE FAILURE != DATA-PLANE FAILURE
#
#       UNKNOWN != UNAVAILABLE
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ============================================================================
# KUBERNETES IS AN INFRASTRUCTURE ADAPTER
# ============================================================================
#
# The generic NetworkHealthEvaluator must never need to know about:
#
#       kubernetes.client
#
#       AppsV1Api
#
#       V1Deployment
#
#       Pod
#
#       ReplicaSet
#
#       kubeconfig
#
#       ServiceAccount
#
#       workload identity
#
#       Kubernetes RBAC
#
#
# Those are infrastructure concerns.
#
# Part II keeps them behind an adapter boundary.
#
#
# ============================================================================
# IDENTITY WARNING
# ============================================================================
#
# Agent 11 identifies an AI service using:
#
#       service_id
#
#
# Kubernetes identifies workloads using concepts such as:
#
#       cluster
#
#       namespace
#
#       workload kind
#
#       workload name
#
#       Kubernetes resource UID
#
#
# These are NOT automatically the same identity.
#
#
#       AIService.service_id
#           !=
#       Kubernetes Deployment.metadata.name
#
#
# Part II therefore uses an EXPLICIT mapping:
#
#
#       service_id
#           ->
#       (namespace, deployment_name)
#
#
# Example:
#
#       company-cloud-primary
#           ->
#       ("agent11-inference", "llama-primary")
#
#
# Agent 11 must not guess this mapping from naming conventions.
#
#
# ============================================================================
# WHY WE ARE NOT CREATING KubernetesWorkloadReference YET
# ============================================================================
#
# A future object might contain:
#
#       cluster_id
#
#       namespace
#
#       workload_kind
#
#       workload_name
#
#       region
#
#       environment
#
#       deployment_id
#
#
# That would be a meaningful noun.
#
# If multiple Agent 11 components begin sharing that information, then the
# architecture may have earned:
#
#
#       models/network/
#
#
# For SEIR-I, however:
#
#
#       dict[str, tuple[str, str]]
#
#
# is sufficient for the narrow service-to-Deployment mapping used here.
#
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================
# KUBERNETES DEPLOYMENT READER
# ============================================================================
#
# KubernetesHealthEvidenceSource should not know how to call the Kubernetes
# Python SDK.
#
# It needs only a narrow observation:
#
#
#       desired replica count
#
#       available replica count
#
#
# Therefore we introduce a small behavioral Protocol.
#
#
# This Protocol is NOT a Pydantic domain noun.
#
# It is an infrastructure behavior boundary.
#
# ============================================================================


class KubernetesDeploymentReader(Protocol):
    """
    Behavioral contract for reading Kubernetes Deployment replica evidence.

    Implementations retrieve infrastructure observations.

    They do not decide Agent 11 service health.

    The returned tuple contains:

        desired_replicas

        available_replicas

    in that order.

    Implementations should raise an exception when trustworthy evidence
    cannot be established.

    They must not silently fabricate replica counts merely to satisfy this
    interface.
    """

    def get_deployment_replica_counts(
        self,
        namespace: str,
        deployment_name: str,
    ) -> tuple[int, int]:
        """
        Return Kubernetes Deployment replica evidence.

        Returns
        -------
        tuple[int, int]
            A tuple containing:

                desired_replicas

                available_replicas

        Raises
        ------
        Exception
            When trustworthy Kubernetes evidence cannot be obtained.

        Important:

            OBSERVATION FAILURE
                !=
            ZERO AVAILABLE REPLICAS
        """
        ...


# ============================================================================
# KUBERNETES HEALTH EVIDENCE SOURCE
# ============================================================================
#
# This class performs the important translation:
#
#
#       Kubernetes infrastructure evidence
#                   |
#                   v
#       Agent 11 ServiceState
#
#
# It implements the HealthEvidenceSource behavioral contract established in
# Part I.
#
#
# It does NOT:
#
#       create Kubernetes clients
#
#       authenticate to Kubernetes
#
#       select a Kubernetes cluster
#
#       load kubeconfig
#
#       load in-cluster configuration
#
#       perform routing
#
#       evaluate policy
#
#       evaluate model capability
#
#       evaluate network reachability
#
#       invoke an AI model
#
#       restart Pods
#
#       scale Deployments
#
#       remediate failures
#
#
# ============================================================================


class KubernetesHealthEvidenceSource:
    """
    Agent 11 health-evidence source backed by Kubernetes Deployment state.

    This adapter translates Kubernetes replica availability into Agent 11's
    ServiceState vocabulary.

    The translation is deliberately conservative.

    Kubernetes-derived health evidence is useful operational evidence.

    It is NOT absolute proof that AI inference is functioning correctly.
    """

    def __init__(
        self,
        deployment_reader: KubernetesDeploymentReader,
        service_workloads: dict[str, tuple[str, str]],
    ) -> None:
        """
        Initialize the Kubernetes health-evidence source.

        Parameters
        ----------
        deployment_reader:
            Injected infrastructure reader capable of obtaining Kubernetes
            Deployment replica information.

        service_workloads:
            Explicit mapping from Agent 11 service identifiers to Kubernetes
            namespace and Deployment name.

            Format:

                {
                    "service-id": (
                        "namespace",
                        "deployment-name",
                    )
                }

        The adapter does not infer Kubernetes identity from service_id.
        """
        self._deployment_reader = deployment_reader
        self._service_workloads = service_workloads

    def get_state(
        self,
        service_id: str,
    ) -> ServiceState:
        """
        Return Kubernetes-derived operational state for an Agent 11 service.

        UNKNOWN is returned when Kubernetes-derived health cannot be
        established.

        UNAVAILABLE is returned only when successfully obtained evidence
        establishes that the configured workload has no available replicas.

        This distinction is fundamental:

            UNKNOWN
                =
            "I cannot establish current health."

            UNAVAILABLE
                =
            "I established that the workload has no available capacity."
        """

        # --------------------------------------------------------------------
        # STEP 1
        #
        # RESOLVE AGENT 11 SERVICE IDENTITY TO KUBERNETES IDENTITY
        # --------------------------------------------------------------------
        #
        # No mapping means this evidence source does not know which Kubernetes
        # workload corresponds to the Agent 11 service.
        #
        # Possible explanations include:
        #
        #       configuration has not been provided
        #
        #       the service belongs to another cluster
        #
        #       the service is not hosted on Kubernetes
        #
        #       the service was newly deployed
        #
        #       the mapping is incomplete
        #
        #
        # None of those establish that the service is unavailable.
        #
        #
        #       NO MAPPING
        #           ->
        #       UNKNOWN
        #
        #
        # not:
        #
        #
        #       NO MAPPING
        #           ->
        #       UNAVAILABLE
        #
        # --------------------------------------------------------------------

        workload = self._service_workloads.get(service_id)

        if workload is None:
            return ServiceState.UNKNOWN

        namespace, deployment_name = workload

        # --------------------------------------------------------------------
        # STEP 2
        #
        # OBTAIN KUBERNETES EVIDENCE
        # --------------------------------------------------------------------
        #
        # The infrastructure reader may fail because:
        #
        #       Kubernetes API server is unavailable
        #
        #       authentication failed
        #
        #       RBAC denied the observation
        #
        #       network connectivity to the control plane failed
        #
        #       the client timed out
        #
        #       the Deployment disappeared during observation
        #
        #       infrastructure returned malformed or incomplete evidence
        #
        #
        # These are failures to OBSERVE.
        #
        # They are not automatically failures of the AI service.
        #
        #
        #       CONTROL-PLANE OBSERVATION FAILURE
        #           !=
        #       DATA-PLANE SERVICE FAILURE
        #
        # --------------------------------------------------------------------

        try:
            desired_replicas, available_replicas = (
                self._deployment_reader.get_deployment_replica_counts(
                    namespace=namespace,
                    deployment_name=deployment_name,
                )
            )

        except Exception:
            # ----------------------------------------------------------------
            # IMPORTANT:
            #
            # We intentionally preserve UNKNOWN.
            #
            # Routing may later fail closed because UNKNOWN health is
            # insufficient evidence.
            #
            # But this component does not falsify the operational state by
            # claiming UNAVAILABLE.
            #
            #
            #       FAIL CLOSED != FALSIFY STATE
            #
            # ----------------------------------------------------------------

            return ServiceState.UNKNOWN

        # --------------------------------------------------------------------
        # STEP 3
        #
        # TRANSLATE KUBERNETES EVIDENCE INTO AGENT 11 VOCABULARY
        # --------------------------------------------------------------------

        return self._translate_replica_state(
            desired_replicas=desired_replicas,
            available_replicas=available_replicas,
        )

    @staticmethod
    def _translate_replica_state(
        desired_replicas: int,
        available_replicas: int,
    ) -> ServiceState:
        """
        Translate Kubernetes Deployment replica evidence into ServiceState.

        SEIR-I translation:

            desired > 0
            available == desired
                -> AVAILABLE

            desired > 0
            0 < available < desired
                -> DEGRADED

            desired > 0
            available == 0
                -> UNAVAILABLE

            desired == 0
                -> UNKNOWN

            contradictory or impossible evidence
                -> UNKNOWN


        --------------------------------------------------------------------
        WHY desired == 0 IS UNKNOWN
        --------------------------------------------------------------------

        A zero-replica Deployment may represent:

            intentional scale-to-zero

            administrative shutdown

            maintenance

            dormant inference capacity

            autoscaling behavior

            misconfiguration

        Replica counts alone do not establish which interpretation is
        correct.

        Therefore SEIR-I does not pretend to know.

            0 desired / 0 available
                -> UNKNOWN


        Future infrastructure may introduce explicit scale-to-zero semantics.

        That should be modeled when the architecture actually requires it.


        --------------------------------------------------------------------
        IMPORTANT LIMITATION
        --------------------------------------------------------------------

        This method translates Kubernetes replica availability.

        It does NOT prove:

            successful inference

            model weights are loaded

            GPU capacity is healthy

            inference latency is acceptable

            request queues are healthy

            the correct model is mounted

            an inference API will return HTTP 200

            generated output will be correct

        Therefore:

            KUBERNETES WORKLOAD HEALTH
                !=
            AI INFERENCE HEALTH
        """

        # --------------------------------------------------------------------
        # INVALID / CONTRADICTORY EVIDENCE
        # --------------------------------------------------------------------
        #
        # Impossible observations should not produce confident conclusions.
        #
        # Examples:
        #
        #       desired = -1
        #
        #       available = -1
        #
        #       desired = 2
        #       available = 4
        #
        #
        # These observations indicate that the evidence itself cannot be
        # trusted as a complete SEIR-I health signal.
        #
        # --------------------------------------------------------------------

        if desired_replicas < 0:
            return ServiceState.UNKNOWN

        if available_replicas < 0:
            return ServiceState.UNKNOWN

        if available_replicas > desired_replicas:
            return ServiceState.UNKNOWN

        # --------------------------------------------------------------------
        # ZERO DESIRED REPLICAS
        # --------------------------------------------------------------------
        #
        # Do not assume:
        #
        #       zero desired replicas == broken
        #
        #
        # Scale-to-zero makes that assumption unsafe.
        #
        # --------------------------------------------------------------------

        if desired_replicas == 0:
            return ServiceState.UNKNOWN

        # --------------------------------------------------------------------
        # FULL AVAILABILITY
        # --------------------------------------------------------------------
        #
        # Kubernetes reports that every desired replica is available.
        #
        # This supports:
        #
        #       AVAILABLE
        #
        # under this evidence source's SEIR-I semantics.
        #
        # --------------------------------------------------------------------

        if available_replicas == desired_replicas:
            return ServiceState.AVAILABLE

        # --------------------------------------------------------------------
        # ZERO AVAILABLE REPLICAS
        # --------------------------------------------------------------------
        #
        # We successfully obtained Kubernetes evidence.
        #
        # Kubernetes reports:
        #
        #       desired > 0
        #
        #       available == 0
        #
        #
        # This is materially different from failing to query Kubernetes.
        #
        # --------------------------------------------------------------------

        if available_replicas == 0:
            return ServiceState.UNAVAILABLE

        # --------------------------------------------------------------------
        # PARTIAL AVAILABILITY
        # --------------------------------------------------------------------
        #
        # At this point:
        #
        #       desired > 0
        #
        #       available > 0
        #
        #       available < desired
        #
        #
        # Some operational capacity remains, but Kubernetes indicates an
        # impaired workload condition.
        #
        # --------------------------------------------------------------------

        return ServiceState.DEGRADED


# ============================================================================
# KUBERNETES SDK DEPLOYMENT READER
# ============================================================================
#
# The following adapter is the infrastructure-specific edge.
#
#
#       KubernetesHealthEvidenceSource
#                   |
#                   v
#       KubernetesDeploymentReader
#                   ^
#                   |
#       KubernetesSDKDeploymentReader
#                   |
#                   v
#       Kubernetes Python SDK
#
#
# The generic health subsystem never needs to import Kubernetes SDK objects.
#
#
# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================
#
# KubernetesSDKDeploymentReader receives an already configured Kubernetes
# API client.
#
# It does NOT perform:
#
#
#       config.load_kube_config()
#
#       config.load_incluster_config()
#
#
# It does not:
#
#       choose a cluster
#
#       select credentials
#
#       choose a Kubernetes context
#
#       assume a cloud identity
#
#       obtain a ServiceAccount token
#
#
# Those responsibilities belong to the application's composition/bootstrap
# layer.
#
#
#       COMPONENT USES DEPENDENCY
#           !=
#       COMPONENT CHOOSES DEPENDENCY
#
#
# ============================================================================


class KubernetesSDKDeploymentReader:
    """
    KubernetesDeploymentReader implementation backed by an injected
    AppsV1Api-compatible Kubernetes client.

    This class is intentionally infrastructure-specific.

    It converts Kubernetes SDK objects into the narrow replica-count evidence
    consumed by KubernetesHealthEvidenceSource.

    It does not interpret those counts as Agent 11 health states.
    """

    def __init__(
        self,
        apps_api,
    ) -> None:
        """
        Initialize the reader with an already configured Kubernetes API
        client.

        The caller owns client creation, authentication, cluster selection,
        and credential lifecycle.
        """
        self._apps_api = apps_api

    def get_deployment_replica_counts(
        self,
        namespace: str,
        deployment_name: str,
    ) -> tuple[int, int]:
        """
        Read replica evidence for a Kubernetes Deployment.

        Returns
        -------
        tuple[int, int]
            desired replicas and available replicas.

        Raises
        ------
        RuntimeError
            When Kubernetes returns insufficient replica evidence.

        Other Kubernetes/client exceptions intentionally propagate upward.

        KubernetesHealthEvidenceSource will translate observation failure into
        ServiceState.UNKNOWN.


        --------------------------------------------------------------------
        WHY WE DO NOT CONVERT MISSING VALUES TO ZERO
        --------------------------------------------------------------------

        This implementation intentionally avoids:

            None -> 0

        for replica fields when doing so would manufacture a stronger claim
        than the evidence supports.

        Zero means:

            "Kubernetes established zero."

        None means:

            "This observation did not establish a value."

        Those are not equivalent.

        Therefore:

            UNKNOWN VALUE != ZERO VALUE

        and:

            OBSERVATION FAILURE != SERVICE FAILURE
        """

        deployment = self._apps_api.read_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
        )

        # --------------------------------------------------------------------
        # DESIRED REPLICAS
        # --------------------------------------------------------------------
        #
        # The Deployment specification represents desired state.
        #
        # If we cannot establish that value, this reader does not fabricate
        # one.
        #
        # --------------------------------------------------------------------

        desired_replicas = deployment.spec.replicas

        if desired_replicas is None:
            raise RuntimeError(
                "Kubernetes Deployment did not provide a desired "
                "replica count."
            )

        # --------------------------------------------------------------------
        # AVAILABLE REPLICAS
        # --------------------------------------------------------------------
        #
        # Deployment status represents observed workload state.
        #
        # A missing value is treated as insufficient evidence rather than
        # automatically converted to zero.
        #
        # This preserves:
        #
        #       UNKNOWN != UNAVAILABLE
        #
        # --------------------------------------------------------------------

        available_replicas = deployment.status.available_replicas

        if available_replicas is None:
            raise RuntimeError(
                "Kubernetes Deployment did not provide an available "
                "replica count."
            )

        return (
            desired_replicas,
            available_replicas,
        )


# ============================================================================
# APPLICATION COMPOSITION
# ============================================================================
#
# IMPORTANT:
#
# The examples below are documentation only.
#
# They are NOT executed by health.py.
#
#
# health.py does not choose how Kubernetes authentication occurs.
#
#
# ---------------------------------------------------------------------------
# LOCAL DEVELOPMENT EXAMPLE
# ---------------------------------------------------------------------------
#
# A local developer might compose the dependencies like this:
#
#
#     from kubernetes import client, config
#
#
#     config.load_kube_config()
#
#
#     apps_api = client.AppsV1Api()
#
#
#     deployment_reader = KubernetesSDKDeploymentReader(
#         apps_api=apps_api,
#     )
#
#
#     health_source = KubernetesHealthEvidenceSource(
#         deployment_reader=deployment_reader,
#         service_workloads={
#             "company-cloud-primary": (
#                 "agent11-inference",
#                 "llama-primary",
#             ),
#         },
#     )
#
#
#     health_evaluator = NetworkHealthEvaluator(
#         health_source=health_source,
#     )
#
#
# ---------------------------------------------------------------------------
# IN-CLUSTER EXAMPLE
# ---------------------------------------------------------------------------
#
# Agent 11 running inside Kubernetes might instead use:
#
#
#     from kubernetes import client, config
#
#
#     config.load_incluster_config()
#
#
#     apps_api = client.AppsV1Api()
#
#
#     deployment_reader = KubernetesSDKDeploymentReader(
#         apps_api=apps_api,
#     )
#
#
#     health_source = KubernetesHealthEvidenceSource(
#         deployment_reader=deployment_reader,
#         service_workloads=service_workloads,
#     )
#
#
#     health_evaluator = NetworkHealthEvaluator(
#         health_source=health_source,
#     )
#
#
# Everything below Kubernetes client construction remains the same.
#
#
# This demonstrates inversion of control:
#
#
#       LOCAL
#
#       kubeconfig
#           |
#           v
#       Kubernetes client
#           |
#           v
#       KubernetesSDKDeploymentReader
#           |
#           v
#       KubernetesHealthEvidenceSource
#           |
#           v
#       NetworkHealthEvaluator
#
#
# versus:
#
#
#       IN CLUSTER
#
#       ServiceAccount / workload identity
#           |
#           v
#       Kubernetes client
#           |
#           v
#       KubernetesSDKDeploymentReader
#           |
#           v
#       KubernetesHealthEvidenceSource
#           |
#           v
#       NetworkHealthEvaluator
#
#
# The health domain does not change merely because authentication changes.
#
#
# ============================================================================
# KUBERNETES RBAC != AGENT 11 POLICY
# ============================================================================
#
# Kubernetes may ask:
#
#
#       MAY THIS SERVICEACCOUNT READ DEPLOYMENTS?
#
#
# Agent 11 policy may ask:
#
#
#       MAY THIS E8 REQUEST USE THIS AI ROUTING DOMAIN?
#
#
# These are completely different authorization questions.
#
#
# Kubernetes RBAC controls Agent 11's authority to observe Kubernetes
# resources.
#
# Agent 11 policy controls whether protected data may use an AI destination.
#
#
# Therefore:
#
#
#       KUBERNETES RBAC
#           !=
#       AGENT 11 DATA POLICY
#
#
# and:
#
#
#       MAY OBSERVE DESTINATION
#           !=
#       MAY USE DESTINATION
#
#
# ============================================================================
# LEAST PRIVILEGE
# ============================================================================
#
# The health adapter should receive only the infrastructure authority needed
# to observe health evidence.
#
# It should not require cluster-admin.
#
# It should not require Deployment mutation authority.
#
# It should not require Pod deletion authority.
#
# It should not require scaling authority.
#
#
# Conceptually:
#
#
#       READ AUTHORITY
#           !=
#       WRITE AUTHORITY
#
#
# A component responsible for observing infrastructure should not
# automatically receive permission to modify that infrastructure.
#
#
# ============================================================================
# OBSERVATION != REMEDIATION
# ============================================================================
#
# Suppose Agent 11 observes:
#
#
#       company-cloud-primary
#           ->
#       UNAVAILABLE
#
#
# This component may report that evidence.
#
# It may NOT conclude:
#
#
#       restart the Deployment
#
#       scale the Deployment
#
#       delete the Pods
#
#       move the workload
#
#       create replacement infrastructure
#
#
# Those are actions.
#
# Actions require a different authority boundary.
#
#
# A future architecture might support:
#
#
#       OBSERVE
#           |
#           v
#       REASON
#           |
#           v
#       RECOMMEND
#           |
#           v
#       POLICY / APPROVAL
#           |
#           v
#       AUTHORIZED EXECUTION
#
#
# It should not become:
#
#
#       OBSERVE
#           |
#           v
#       AUTONOMOUSLY PATCH PRODUCTION
#
#
# Therefore:
#
#
#       OBSERVE != REMEDIATE
#
#       DETECT != ACT
#
#       REASONING AUTHORITY != EXECUTION AUTHORITY
#
#
# ============================================================================
# KUBERNETES WORKLOAD HEALTH != AI INFERENCE HEALTH
# ============================================================================
#
# This is the largest limitation of the SEIR-I Kubernetes implementation.
#
#
# Suppose Kubernetes reports:
#
#
#       desired replicas   = 4
#
#       available replicas = 4
#
#
# KubernetesHealthEvidenceSource returns:
#
#
#       AVAILABLE
#
#
# But the inference application could still have:
#
#
#       model weights failed to load
#
#       GPU allocation failure
#
#       inference queue saturation
#
#       upstream dependency failure
#
#       inference endpoint returning HTTP 500
#
#       wrong model loaded
#
#       token quota exhausted
#
#       model server deadlocked
#
#
# Kubernetes replica availability does not establish those facts.
#
#
# Therefore:
#
#
#       KUBERNETES WORKLOAD HEALTH
#           !=
#       AI INFERENCE HEALTH
#
#
# The current state means:
#
#
#       "Kubernetes-derived infrastructure evidence supports AVAILABLE."
#
#
# It does NOT mean:
#
#
#       "Every AI inference request will succeed."
#
#
# ============================================================================
# READINESS IS ALSO EVIDENCE
# ============================================================================
#
# Kubernetes readiness can improve the quality of infrastructure evidence.
#
# But readiness remains infrastructure evidence.
#
#
#       POD READY
#           !=
#       AI SERVICE DEFINITELY HEALTHY
#
#
# A badly designed readiness probe might check only:
#
#
#       process exists
#
#
# while failing to check:
#
#
#       model loaded
#
#       accelerator ready
#
#       dependencies available
#
#       inference path functional
#
#
# Agent 11 should therefore avoid treating Kubernetes readiness as universal
# truth about inference health.
#
#
# ============================================================================
# CONTROL PLANE != DATA PLANE
# ============================================================================
#
# Another important Kubernetes distinction:
#
#
#       Kubernetes API server
#           =
#       control-plane observation path
#
#
# while:
#
#
#       inference service
#           =
#       application data plane
#
#
# The Kubernetes API may be temporarily unavailable while already-running
# inference workloads continue serving traffic normally.
#
#
# Therefore:
#
#
#       KUBERNETES API UNAVAILABLE
#           !=
#       INFERENCE SERVICE UNAVAILABLE
#
#
# This is why Kubernetes observation failure maps to:
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
# TESTING STRATEGY
# ============================================================================
#
# The architecture should allow health semantics to be tested without:
#
#
#       a real Kubernetes cluster
#
#       kubeconfig
#
#       EKS
#
#       AKS
#
#       GKE
#
#       OKE
#
#       cloud credentials
#
#       DNS
#
#       VPN connectivity
#
#
# Example test double:
#
#
#     class FakeDeploymentReader:
#
#         def __init__(
#             self,
#             desired: int,
#             available: int,
#         ) -> None:
#             self._desired = desired
#             self._available = available
#
#         def get_deployment_replica_counts(
#             self,
#             namespace: str,
#             deployment_name: str,
#         ) -> tuple[int, int]:
#             return (
#                 self._desired,
#                 self._available,
#             )
#
#
# Then:
#
#
#     reader = FakeDeploymentReader(
#         desired=4,
#         available=2,
#     )
#
#
#     source = KubernetesHealthEvidenceSource(
#         deployment_reader=reader,
#         service_workloads={
#             "company-cloud-primary": (
#                 "agent11-inference",
#                 "llama-primary",
#             ),
#         },
#     )
#
#
#     state = source.get_state(
#         "company-cloud-primary"
#     )
#
#
#     assert state is ServiceState.DEGRADED
#
#
# ============================================================================
# TESTING OBSERVATION FAILURE
# ============================================================================
#
# Observation failure should be equally easy to test.
#
#
#     class FailingDeploymentReader:
#
#         def get_deployment_replica_counts(
#             self,
#             namespace: str,
#             deployment_name: str,
#         ) -> tuple[int, int]:
#             raise RuntimeError(
#                 "Kubernetes API unavailable."
#             )
#
#
#     reader = FailingDeploymentReader()
#
#
#     source = KubernetesHealthEvidenceSource(
#         deployment_reader=reader,
#         service_workloads={
#             "company-cloud-primary": (
#                 "agent11-inference",
#                 "llama-primary",
#             ),
#         },
#     )
#
#
#     state = source.get_state(
#         "company-cloud-primary"
#     )
#
#
#     assert state is ServiceState.UNKNOWN
#
#
# That test captures:
#
#
#       I COULD NOT OBSERVE THE SERVICE
#           !=
#       THE SERVICE IS DOWN
#
#
# ============================================================================
# TESTING TRANSLATION SEMANTICS
# ============================================================================
#
# The following cases should eventually become explicit unit tests:
#
#
#       desired = 4
#       available = 4
#           -> AVAILABLE
#
#
#       desired = 4
#       available = 2
#           -> DEGRADED
#
#
#       desired = 4
#       available = 0
#           -> UNAVAILABLE
#
#
#       desired = 0
#       available = 0
#           -> UNKNOWN
#
#
#       desired = -1
#       available = 0
#           -> UNKNOWN
#
#
#       desired = 4
#       available = -1
#           -> UNKNOWN
#
#
#       desired = 2
#       available = 4
#           -> UNKNOWN
#
#
#       no service mapping
#           -> UNKNOWN
#
#
#       Kubernetes observation failure
#           -> UNKNOWN
#
#
# ============================================================================
# DO NOT TEST EVERYTHING THROUGH KUBERNETES
# ============================================================================
#
# Generic NetworkHealthEvaluator tests should not require mocking:
#
#
#       Kubernetes
#
#       AWS
#
#       Azure
#
#       GCP
#
#       OCI
#
#       DNS
#
#       BGP
#
#       Agent 11 policy
#
#       model registries
#
#
# If a generic health test requires all of those systems, the architecture
# boundary has collapsed.
#
#
# Test each responsibility independently.
#
#
# ============================================================================
# MULTI-CLOUD WARNING
# ============================================================================
#
# Kubernetes does not imply one cloud provider.
#
#
# Agent 11 may eventually observe inference workloads running on:
#
#
#       EKS
#
#       AKS
#
#       GKE
#
#       OKE
#
#       on-prem Kubernetes
#
#       bare-metal Kubernetes
#
#
# Therefore:
#
#
#       KUBERNETES != CLOUD PROVIDER
#
#       CLOUD PROVIDER != ROUTING DOMAIN
#
#       KUBERNETES CLUSTER != ROUTING DOMAIN
#
#
# For example:
#
#
#       COMPANY_CLOUD_LLM
#
#
# may eventually contain services deployed across several providers.
#
# The routing domain remains an Agent 11 policy/routing abstraction.
#
#
# ============================================================================
# SERVICE != DEPLOYMENT
# ============================================================================
#
# SEIR-I currently correlates Kubernetes evidence using:
#
#
#       service_id
#
#
# But future infrastructure may expose:
#
#
#                       AIService
#                           |
#               +-----------+-----------+
#               |                       |
#               v                       v
#       Tokyo Deployment         Virginia Deployment
#            AVAILABLE                UNAVAILABLE
#
#
# At that point:
#
#
#       SERVICE HEALTH
#           !=
#       DEPLOYMENT HEALTH
#
#
# Part II deliberately does not solve this yet.
#
# Deployment identity should be introduced when real infrastructure requires
# Agent 11 to reason at deployment granularity.
#
#
# ============================================================================
# WHERE THE KUBERNETES ADAPTER MAY EVENTUALLY LIVE
# ============================================================================
#
# For teaching and early implementation, the classes can remain together in:
#
#
#       network/health.py
#
#
# This makes the architecture visible in one place.
#
#
# If Kubernetes-specific behavior grows substantially, a later refactor may
# earn:
#
#
#       network/kubernetes.py
#
#
# or eventually:
#
#
#       network/adapters/
#           kubernetes.py
#
#
# Do not create package structure merely because it looks architecturally
# sophisticated.
#
#
#       STRUCTURE SHOULD FOLLOW RESPONSIBILITY.
#
#       RESPONSIBILITY SHOULD NOT BE INVENTED
#       TO JUSTIFY STRUCTURE.
#
#
# ============================================================================
# PART II FINAL ARCHITECTURE
# ============================================================================
#
#
#                         AGENT 11
#                            |
#                            v
#                 NetworkHealthEvaluator
#                            |
#                            v
#                  HealthEvidenceSource
#                     /             \
#                    /               \
#                   v                 v
#          StaticHealth         KubernetesHealth
#          EvidenceSource       EvidenceSource
#                                      |
#                                      v
#                         KubernetesDeploymentReader
#                                      ^
#                                      |
#                                      v
#                       KubernetesSDKDeploymentReader
#                                      |
#                                      v
#                             Kubernetes API
#
#
# The output of this subsystem remains:
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
# Candidate evaluation will later combine that evidence with:
#
#
#       POLICY
#
#       CAPABILITY
#
#       SERVICE HEALTH
#
#       NETWORK PATH
#
#
# to determine:
#
#
#       RoutingCandidate
#
#
# ============================================================================
# PART II FINAL INVARIANTS
# ============================================================================
#
#       KUBERNETES != AGENT 11
#
#       KUBERNETES != CLOUD PROVIDER
#
#       CLOUD PROVIDER != ROUTING DOMAIN
#
#       KUBERNETES CLUSTER != ROUTING DOMAIN
#
#       KUBERNETES SERVICE != AI SERVICE
#
#       KUBERNETES DEPLOYMENT != AI SERVICE
#
#       POD != AI MODEL
#
#       POD != AI SERVICE
#
#       POD READY != AI INFERENCE HEALTHY
#
#       AVAILABLE REPLICA != AUTHORIZED DESTINATION
#
#       SERVICE HEALTH != NETWORK REACHABILITY
#
#       SERVICE HEALTH != CAPABILITY
#
#       SERVICE HEALTH != ROUTING VIABILITY
#
#       CONTROL-PLANE FAILURE != DATA-PLANE FAILURE
#
#       OBSERVATION FAILURE != SERVICE FAILURE
#
#       NO MAPPING != SERVICE UNAVAILABLE
#
#       UNKNOWN VALUE != ZERO VALUE
#
#       UNKNOWN != UNAVAILABLE
#
#       DEGRADED != UNAVAILABLE
#
#       HEALTH EVIDENCE != ABSOLUTE HEALTH TRUTH
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#       OBSERVATION AUTHORITY != MUTATION AUTHORITY
#
#       MAY OBSERVE DESTINATION != MAY USE DESTINATION
#
#       KUBERNETES RBAC != AGENT 11 DATA POLICY
#
#       OBSERVE != REMEDIATE
#
#       DETECT != ACT
#
#       REASONING AUTHORITY != EXECUTION AUTHORITY
#
#       COMPONENT USES DEPENDENCY
#           !=
#       COMPONENT CHOOSES DEPENDENCY
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ============================================================================
# SEIR-I BOUNDARY
# ============================================================================
#
# Part II intentionally stops here.
#
#
# We currently translate ONE type of operational evidence:
#
#
#       Kubernetes Deployment replica availability
#
#
# into:
#
#
#       Agent 11 ServiceState
#
#
# That is enough to teach and implement:
#
#
#       dependency inversion
#
#       infrastructure adapters
#
#       observation authority
#
#       health-state preservation
#
#       UNKNOWN semantics
#
#       Kubernetes integration
#
#       control-plane/data-plane separation
#
#
# WITHOUT prematurely building:
#
#
#       health scoring
#
#       telemetry fusion
#
#       GPU diagnostics
#
#       multi-cluster consensus
#
#       inference probes
#
#       Prometheus aggregation
#
#       service-mesh analysis
#
#       deployment-level routing
#
#       autonomous remediation
#
#
# Those belong to the future architecture explored in Part III.
#
#
# ============================================================================
# END OF PART II
# ============================================================================

# ============================================================================
# PART III
#
# NOTES TO FUTURE SELF
#
# MULTI-SOURCE HEALTH EVIDENCE, PROVENANCE, FRESHNESS,
# ASSESSMENT, AND SEIR-II EVOLUTION
# ============================================================================
#
# PURPOSE
# -------
#
# Part I established the infrastructure-neutral health boundary:
#
#
#       NetworkHealthEvaluator
#               |
#               v
#       HealthEvidenceSource
#               |
#               v
#       ServiceState
#
#
# Part II demonstrated how Kubernetes can provide operational evidence
# without becoming Agent 11's health domain:
#
#
#       Kubernetes
#           |
#           v
#       KubernetesDeploymentReader
#           |
#           v
#       KubernetesHealthEvidenceSource
#           |
#           v
#       ServiceState
#
#
# That architecture is intentionally sufficient for SEIR-I.
#
#
# Part III records the architectural problems that will appear when Agent 11
# begins consuming MULTIPLE independent health observations.
#
#
# Example:
#
#
#       Kubernetes
#           -> AVAILABLE
#
#       Prometheus
#           -> DEGRADED
#
#       inference probe
#           -> UNAVAILABLE
#
#       GPU telemetry
#           -> AVAILABLE
#
#       service mesh
#           -> DEGRADED
#
#
# At that point, the question is no longer simply:
#
#
#       "What state did one source report?"
#
#
# Agent 11 must distinguish:
#
#
#       OBSERVATION
#
#       EVIDENCE
#
#       FRESHNESS
#
#       PROVENANCE
#
#       ASSESSMENT
#
#       ROUTING INTERPRETATION
#
#
# These are different concepts.
#
#
# ============================================================================
# PART III IS PRIMARILY AN ARCHITECTURE CONTRACT
# ============================================================================
#
# Part III does NOT require SEIR-I to immediately implement:
#
#
#       Prometheus
#
#       OpenTelemetry
#
#       GPU telemetry
#
#       inference probes
#
#       service-mesh telemetry
#
#       multi-cluster aggregation
#
#       evidence reconciliation
#
#       health scoring
#
#       deployment-level routing
#
#       automated remediation
#
#
# The purpose of these notes is to prevent future infrastructure complexity
# from destroying the boundaries established in Parts I and II.
#
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================
# THE FIRST MAJOR SEIR-II PROBLEM
# ============================================================================
#
# The current interface:
#
#
#       HealthEvidenceSource.get_state(
#           service_id
#       ) -> ServiceState
#
#
# intentionally collapses one source's observations into:
#
#
#       AVAILABLE
#       DEGRADED
#       UNAVAILABLE
#       UNKNOWN
#
#
# That is sufficient while one source is authoritative enough for the
# current SEIR-I exercise.
#
#
# It becomes lossy when several independent observers exist.
#
#
# Consider:
#
#
#       Kubernetes:
#
#           AVAILABLE
#           observed 10:00:00
#
#
#       inference probe:
#
#           UNAVAILABLE
#           observed 10:00:02
#
#
# If Agent 11 stores only:
#
#
#       ServiceState
#
#
# important information disappears:
#
#
#       who made the observation?
#
#       what kind of evidence was observed?
#
#       when was it observed?
#
#       how old is it?
#
#       what operational dimension was measured?
#
#       do the observations actually contradict one another?
#
#
# ============================================================================
# EVIDENCE != ASSESSMENT
# ============================================================================
#
# SEIR-II should preserve this distinction:
#
#
#       HEALTH EVIDENCE
#           =
#       WHAT AN OBSERVER REPORTED
#
#
#       HEALTH ASSESSMENT
#           =
#       WHAT AGENT 11 CURRENTLY CONCLUDES
#       FROM THE AVAILABLE EVIDENCE
#
#
# Therefore:
#
#
#       EVIDENCE != ASSESSMENT
#
#
# This follows the same architecture used elsewhere in Agent 11:
#
#
#       PROHIBITED-DATA FINDING
#           !=
#       ENFORCEMENT
#
#
#       POLICY CONFIGURATION
#           !=
#       POLICY DECISION
#
#
#       NETWORK EVIDENCE
#           !=
#       ROUTING DECISION
#
#
#       HEALTH EVIDENCE
#           !=
#       HEALTH ASSESSMENT
#
#
# ============================================================================
# ONE OBSERVATION = ONE EVIDENCE RECORD
# ============================================================================
#
# Future health evidence should preserve individual observations.
#
#
# Example:
#
#
#       Kubernetes observed AVAILABLE.
#
#
# That is one observation.
#
#
#       inference probe observed UNAVAILABLE.
#
#
# That is another observation.
#
#
# Do not prematurely merge them into:
#
#
#       DEGRADED
#
#
# merely because DEGRADED appears numerically or intuitively "between" the
# two states.
#
#
# ServiceState is not an arithmetic scale.
#
#
#       AVAILABLE + UNAVAILABLE
#           !=
#       DEGRADED
#
#
# ============================================================================
# DISAGREEMENT != DEGRADED
# ============================================================================
#
# This deserves its own invariant.
#
#
# DEGRADED means:
#
#
#       operational evidence supports an impaired condition
#
#
# DISAGREEMENT means:
#
#
#       different observations currently support different conclusions
#
#
# Those are not the same thing.
#
#
# Example:
#
#
#       Kubernetes:
#           AVAILABLE
#
#       inference probe:
#           UNAVAILABLE
#
#
# That does not automatically mean:
#
#
#       DEGRADED
#
#
# It may mean:
#
#
#       UNKNOWN
#
#
# until Agent 11 has explicit evidence-resolution semantics.
#
#
# ============================================================================
# DO NOT INVENT HEALTH SCORES
# ============================================================================
#
# Multiple evidence sources create a temptation:
#
#
#       Kubernetes AVAILABLE
#           +10
#
#       Prometheus DEGRADED
#           +5
#
#       probe UNAVAILABLE
#           -10
#
#       GPU AVAILABLE
#           +10
#
#       -----------------
#       score = 15
#
#       therefore HEALTHY
#
#
# No.
#
#
# Such arithmetic destroys meaning unless a formally defined operational
# model gives those numbers legitimate semantics.
#
#
# Agent 11 already protects:
#
#
#       POLICY NEVER BECOMES A SCORE
#
#
# Health should preserve a related rule:
#
#
#       MULTIPLE OBSERVATIONS
#           !=
#       PERMISSION TO INVENT A SCORE
#
#
# ============================================================================
# POSSIBLE FUTURE DOMAIN MODEL
# ============================================================================
#
# When multi-source evidence becomes real, Agent 11 may earn first-class
# health nouns.
#
#
# Likely ownership:
#
#
#       models/
#       └── network/
#           ├── __init__.py
#           ├── health_evidence.py
#           └── health_assessment.py
#
#
# while:
#
#
#       network/
#           ├── endpoint.py
#           ├── health.py
#           ├── path.py
#           └── orchestrator.py
#
#
# continues to contain behavior.
#
#
# This preserves:
#
#
#       models/ = NOUNS / CONTRACTS
#
#       network/ = NETWORK BEHAVIOR
#
#
# Do not create models/network merely because these comments mention it.
#
# Create it when actual executable architecture requires shared network
# domain contracts.
#
#
# ============================================================================
# POSSIBLE HealthEvidence CONTRACT
# ============================================================================
#
# A future HealthEvidence model may need to preserve:
#
#
#       service_id
#
#       state
#
#       evidence_type
#
#       source_type
#
#       observed_at
#
#
# Example conceptual shape:
#
#
#     class HealthEvidence(Agent11BaseModel):
#
#         service_id: str
#
#         state: ServiceState
#
#         evidence_type: HealthEvidenceType
#
#         source_type: HealthEvidenceSourceType
#
#         observed_at: datetime
#
#
# This model belongs in models/network/ if and when implemented.
#
#
# It should NOT contain:
#
#
#       routing selection
#
#       policy decisions
#
#       network authorization
#
#       remediation commands
#
#       Kubernetes clients
#
#       Prometheus clients
#
#
# ============================================================================
# SOURCE != EVIDENCE TYPE
# ============================================================================
#
# Future architecture should distinguish:
#
#
#       WHERE DID THIS OBSERVATION COME FROM?
#
#
# from:
#
#
#       WHAT KIND OF CONDITION WAS OBSERVED?
#
#
# Example:
#
#
#       source:
#           PROMETHEUS
#
#       evidence type:
#           APPLICATION_METRIC
#
#
# Another:
#
#
#       source:
#           KUBERNETES
#
#       evidence type:
#           WORKLOAD_AVAILABILITY
#
#
# Therefore:
#
#
#       SOURCE != EVIDENCE TYPE
#
#
# This distinction allows technologies to change without changing the
# operational meaning of evidence.
#
#
# ============================================================================
# POSSIBLE EVIDENCE TYPES
# ============================================================================
#
# Future evidence categories might include:
#
#
#       WORKLOAD_AVAILABILITY
#
#       INFERENCE_PROBE
#
#       APPLICATION_METRIC
#
#       ACCELERATOR_HEALTH
#
#       CAPACITY
#
#       NETWORK_TELEMETRY
#
#
# These names are architectural examples.
#
# They are not yet approved domain vocabulary.
#
#
# ============================================================================
# POSSIBLE SOURCE TYPES
# ============================================================================
#
# Future sources might include:
#
#
#       STATIC
#
#       KUBERNETES
#
#       PROMETHEUS
#
#       OPENTELEMETRY
#
#       SERVICE_MESH
#
#       INFERENCE_PROBE
#
#       CLOUD_PLATFORM
#
#
# Again:
#
#
#       THESE COMMENTS DO NOT CREATE ENUM MEMBERS.
#
#
# Vocabulary should be introduced only when executable behavior requires it.
#
#
# ============================================================================
# HEALTH ASSESSMENT
# ============================================================================
#
# Once multiple observations exist, Agent 11 may require:
#
#
#       HealthAssessment
#
#
# Conceptually:
#
#
#       HealthEvidence[]
#               |
#               v
#       HealthAssessmentEvaluator
#               |
#               v
#       HealthAssessment
#
#
# A possible future assessment could preserve:
#
#
#       service_id
#
#       resulting ServiceState
#
#       evidence used
#
#       assessed_at
#
#
# The assessment remains an OPERATIONAL conclusion.
#
#
# It is NOT:
#
#
#       policy authorization
#
#       routing selection
#
#       network reachability
#
#       capability evaluation
#
#
# ============================================================================
# AGGREGATE VALIDATION
# ============================================================================
#
# If HealthAssessment contains HealthEvidence[], the aggregate should enforce
# relational consistency.
#
#
# For example:
#
#
#       assessment.service_id
#
# must match:
#
#
#       evidence.service_id
#
#
# for every evidence record.
#
#
# This follows the Agent 11 rule:
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
# The validator should NOT decide:
#
#
#       which evidence source wins
#
#       whether stale evidence should be ignored
#
#       whether routing may use the service
#
#
# Those are behavioral decisions.
#
#
# ============================================================================
# FIRST CONSERVATIVE ASSESSMENT RULE
# ============================================================================
#
# Before Agent 11 has explicit evidence-resolution policy, the simplest
# defensible assessment behavior is:
#
#
#       no evidence
#           -> UNKNOWN
#
#
#       all fresh evidence agrees
#           -> agreed state
#
#
#       evidence disagrees
#           -> UNKNOWN
#
#
# Example:
#
#
#       AVAILABLE
#       AVAILABLE
#           ->
#       AVAILABLE
#
#
#       DEGRADED
#       DEGRADED
#           ->
#       DEGRADED
#
#
#       UNAVAILABLE
#       UNAVAILABLE
#           ->
#       UNAVAILABLE
#
#
#       AVAILABLE
#       UNAVAILABLE
#           ->
#       UNKNOWN
#
#
# This is intentionally conservative.
#
#
# It avoids inventing authority relationships between evidence sources before
# those relationships have been explicitly modeled.
#
#
# ============================================================================
# WORST STATE DOES NOT AUTOMATICALLY WIN
# ============================================================================
#
# Another tempting shortcut is:
#
#
#       choose the worst observed state
#
#
# That may eventually be appropriate for some evidence dimensions.
#
# It should not become a universal rule without analysis.
#
#
# Example:
#
#
#       inference probe:
#           UNAVAILABLE
#           observed 45 minutes ago
#
#
#       Kubernetes:
#           AVAILABLE
#           observed 2 seconds ago
#
#
# Blindly selecting the worst state would ignore freshness.
#
#
# Conversely:
#
#
#       Kubernetes:
#           AVAILABLE
#
#       inference probe:
#           UNAVAILABLE
#
#
# both observed now
#
#
# may indicate that infrastructure is running while application function is
# broken.
#
#
# In that case the inference observation may legitimately matter more to
# service usability.
#
#
# The rule must be explicit.
#
#
# ============================================================================
# BEST STATE DOES NOT AUTOMATICALLY WIN
# ============================================================================
#
# Selecting the most optimistic observation is even more dangerous.
#
#
#       Kubernetes AVAILABLE
#
# does not erase:
#
#
#       inference probe UNAVAILABLE
#
#
# simply because Kubernetes reports healthy replicas.
#
#
# ============================================================================
# EVIDENCE DIMENSIONS
# ============================================================================
#
# A deeper future possibility is that apparently conflicting evidence does
# not actually conflict.
#
#
# Example:
#
#
#       Kubernetes:
#           workload AVAILABLE
#
#
#       GPU telemetry:
#           accelerator AVAILABLE
#
#
#       inference probe:
#           inference UNAVAILABLE
#
#
# All three observations can simultaneously be true.
#
#
# The problem may be that one ServiceState is being asked to represent too
# many operational dimensions.
#
#
# Future architecture may therefore need separate dimensions such as:
#
#
#       WORKLOAD CONDITION
#
#       APPLICATION CONDITION
#
#       INFERENCE CONDITION
#
#       ACCELERATOR CONDITION
#
#       CAPACITY CONDITION
#
#
# before producing an overall service assessment.
#
#
# ============================================================================
# CONFLICTING EVIDENCE MAY REVEAL A BAD MODEL
# ============================================================================
#
# Do not automatically solve every disagreement by writing more precedence
# rules.
#
#
# Sometimes disagreement means:
#
#
#       THE DOMAIN MODEL IS COLLAPSING
#       DISTINCT FACTS INTO ONE FIELD.
#
#
# That is an architecture signal.
#
#
# ============================================================================
# FRESHNESS
# ============================================================================
#
# Health evidence is temporal.
#
#
#       OBSERVED THEN
#           !=
#       TRUE NOW
#
#
# Example:
#
#
#       Kubernetes:
#           AVAILABLE
#           observed 2 seconds ago
#
#
#       inference probe:
#           UNAVAILABLE
#           observed 47 minutes ago
#
#
# Those observations should not necessarily carry equal operational weight.
#
#
# ============================================================================
# STALE != FALSE
# ============================================================================
#
# If evidence becomes stale, the historical observation remains true:
#
#
#       "At time T, this source observed UNAVAILABLE."
#
#
# Staleness means:
#
#
#       the evidence may no longer be sufficiently current
#       for the present assessment.
#
#
# Therefore:
#
#
#       STALE EVIDENCE != FALSE EVIDENCE
#
#
# Do not rewrite:
#
#
#       UNAVAILABLE
#
# into:
#
#       UNKNOWN
#
#
# inside the historical evidence object merely because time passed.
#
#
# Instead:
#
#
#       HealthEvidence
#           remains historical observation
#
#
#       freshness behavior
#           determines whether it participates
#           in current assessment
#
#
# ============================================================================
# FRESHNESS IS BEHAVIOR
# ============================================================================
#
# A future:
#
#
#       HealthEvidenceFreshnessEvaluator
#
#
# might determine whether evidence remains usable for a current assessment.
#
#
# Conceptually:
#
#
#       HealthEvidence
#               |
#               v
#       FreshnessEvaluator
#               |
#               v
#       fresh / stale
#
#
# The HealthEvidence model itself should not dynamically mutate as wall-clock
# time advances.
#
#
# ============================================================================
# ONE GLOBAL FRESHNESS WINDOW MAY BE WRONG
# ============================================================================
#
# Different evidence types may age differently.
#
#
# Example:
#
#
#       Kubernetes workload evidence
#           maximum useful age: perhaps tens of seconds
#
#
#       inference probe
#           maximum useful age: perhaps seconds
#
#
#       accelerator telemetry
#           maximum useful age: perhaps seconds
#
#
#       slow-moving configuration evidence
#           potentially much longer
#
#
# Exact values are future policy/configuration decisions.
#
#
# The important architectural point is:
#
#
#       FRESHNESS REQUIREMENT
#           MAY DEPEND ON
#       EVIDENCE TYPE
#
#
# ============================================================================
# CLOCKS MATTER
# ============================================================================
#
# Once evidence becomes distributed, timestamps introduce real engineering
# problems:
#
#
#       clock skew
#
#       delayed telemetry
#
#       buffered telemetry
#
#       reordered events
#
#       collector lag
#
#       asynchronous observation
#
#
# observed_at should mean:
#
#
#       WHEN THE CONDITION WAS OBSERVED
#
#
# not merely:
#
#
#       WHEN AGENT 11 RECEIVED THE RECORD
#
#
# A future model may need both concepts if transport delay becomes important.
#
#
# Do not add both timestamps until behavior needs them.
#
#
# ============================================================================
# PROVENANCE
# ============================================================================
#
# Agent 11 eventually needs to know where health evidence came from.
#
#
# Provenance matters because:
#
#
#       evidence sources have different semantics
#
#       evidence sources may have different trust boundaries
#
#       evidence may be stale
#
#       evidence may be compromised
#
#       evidence may be misconfigured
#
#       evidence may observe different layers
#
#
# But provenance does NOT automatically create authority.
#
#
#       SOURCE KNOWN
#           !=
#       SOURCE AUTHORITATIVE
#
#
# ============================================================================
# TRUSTED SOURCE != TRUE OBSERVATION
# ============================================================================
#
# Even a trusted telemetry system can report incorrect information because:
#
#
#       probes are misconfigured
#
#       instrumentation is broken
#
#       clocks are wrong
#
#       labels are incorrect
#
#       metrics are stale
#
#       caches are stale
#
#       software contains bugs
#
#
# Therefore:
#
#
#       TRUSTED SOURCE
#           !=
#       INFALLIBLE SOURCE
#
#
# ============================================================================
# VALID DATA != TRUSTED EVIDENCE
# ============================================================================
#
# Pydantic can establish:
#
#
#       field types are valid
#
#       required fields exist
#
#       enum values are legal
#
#
# Pydantic cannot establish:
#
#
#       Prometheus is telling the truth
#
#       Kubernetes observed the correct cluster
#
#       the probe targeted the intended service
#
#       telemetry was not tampered with
#
#
# Therefore:
#
#
#       VALID PYDANTIC MODEL
#           !=
#       TRUSTED OPERATIONAL EVIDENCE
#
#
# ============================================================================
# KUBERNETES + PROMETHEUS
# ============================================================================
#
# Prometheus may eventually provide evidence such as:
#
#
#       request error rate
#
#       latency
#
#       saturation
#
#       queue depth
#
#       active inference count
#
#       process health
#
#
# These observations should not cause PromQL to leak throughout Agent 11.
#
#
# A Prometheus adapter should translate:
#
#
#       Prometheus query results
#
# into:
#
#
#       normalized Agent 11 health evidence
#
#
# The generic health evaluator should not know PromQL.
#
#
# ============================================================================
# OPENTELEMETRY
# ============================================================================
#
# OpenTelemetry may eventually provide:
#
#
#       traces
#
#       metrics
#
#       logs
#
#       request latency
#
#       error signals
#
#       dependency observations
#
#
# Again:
#
#
#       TELEMETRY TECHNOLOGY
#           !=
#       AGENT 11 DOMAIN CONTRACT
#
#
# OpenTelemetry may change.
#
# Agent 11's distinction between evidence and assessment should survive.
#
#
# ============================================================================
# INFERENCE PROBES
# ============================================================================
#
# An inference probe may be substantially closer to the actual function Agent
# 11 cares about than Kubernetes replica availability.
#
#
# Example:
#
#
#       POST inference request
#
#       model successfully responds
#
#
# provides different evidence from:
#
#
#       Deployment has four available replicas
#
#
# Therefore:
#
#
#       WORKLOAD HEALTH
#           !=
#       INFERENCE HEALTH
#
#
# A future inference probe should still remain scoped.
#
# It should not automatically become:
#
#
#       model-quality evaluator
#
#       policy evaluator
#
#       security evaluator
#
#       routing engine
#
#
# ============================================================================
# HEALTH PROBE != REAL USER REQUEST
# ============================================================================
#
# Even successful inference probes have limits.
#
#
# A tiny synthetic request may succeed while:
#
#
#       large context requests fail
#
#       structured output fails
#
#       tool use fails
#
#       heavy reasoning fails
#
#       long-running generation fails
#
#       particular models fail
#
#
# Therefore:
#
#
#       PROBE SUCCESS
#           !=
#       UNIVERSAL SERVICE SUCCESS
#
#
# ============================================================================
# GPU / ACCELERATOR HEALTH
# ============================================================================
#
# Proprietary inference infrastructure may eventually expose:
#
#
#       GPU availability
#
#       memory pressure
#
#       thermal conditions
#
#       accelerator errors
#
#       device resets
#
#       failed nodes
#
#       accelerator fragmentation
#
#
# These are operational observations.
#
#
# They should not cause health.py to become a GPU-management system.
#
#
#       GPU EVIDENCE
#           !=
#       GPU REMEDIATION
#
#
# ============================================================================
# CAPACITY != HEALTH
# ============================================================================
#
# Another future distinction:
#
#
#       SERVICE HEALTH
#           !=
#       SERVICE CAPACITY
#
#
# A service can be healthy while fully saturated.
#
#
# Example:
#
#
#       all replicas healthy
#
#       queue full
#
#       no remaining inference capacity
#
#
# Whether that becomes DEGRADED, UNAVAILABLE, or a separate capacity
# dimension should be determined by the future domain model.
#
#
# Do not hide capacity inside a vague health score.
#
#
# ============================================================================
# QUOTA != HEALTH
# ============================================================================
#
# External and cloud-hosted AI services may have:
#
#
#       token quotas
#
#       request quotas
#
#       concurrency limits
#
#       regional capacity limits
#
#
# A provider may be operationally healthy while Agent 11 cannot submit
# another request because the organization's quota is exhausted.
#
#
# Therefore:
#
#
#       PROVIDER HEALTHY
#           !=
#       CAPACITY AVAILABLE TO US
#
#
# Future candidate evaluation may need this as another viability dimension.
#
#
# ============================================================================
# SERVICE MESH
# ============================================================================
#
# A service mesh may report:
#
#
#       endpoint health
#
#       retries
#
#       circuit-breaker state
#
#       connection failures
#
#       latency
#
#       mTLS state
#
#
# This is useful evidence.
#
#
# But:
#
#
#       MESH HEALTH != AI SERVICE HEALTH
#
#       MESH REACHABILITY != AGENT 11 AUTHORIZATION
#
#       mTLS != DATA POLICY APPROVAL
#
#
# ============================================================================
# CIRCUIT BREAKERS
# ============================================================================
#
# Future Agent 11 may encounter circuit breakers at several layers:
#
#
#       model SDK
#
#       Agent 11
#
#       HTTP client
#
#       service mesh
#
#       gateway
#
#       cloud load balancer
#
#
# Circuit-breaker state may itself become operational evidence.
#
#
# But circuit breakers also affect behavior.
#
#
# Health observation must not silently become circuit-breaker ownership.
#
#
# ============================================================================
# RETRY MULTIPLICATION
# ============================================================================
#
# Suppose:
#
#
#       Agent 11 retries 3 times
#
#       SDK retries 3 times
#
#       mesh retries 3 times
#
#       gateway retries 3 times
#
#
# A single logical request can explode into many physical attempts.
#
#
# This affects:
#
#
#       cost
#
#       latency
#
#       load
#
#       telemetry
#
#       rate limits
#
#       disclosure surface
#
#
# Retry ownership therefore matters.
#
#
# Health evidence should not silently trigger retries.
#
#
# ============================================================================
# HEALTH != RETRY POLICY
# ============================================================================
#
# Health may report:
#
#
#       DEGRADED
#
#
# A retry subsystem may decide:
#
#
#       retry same service
#
#
# A fallback subsystem may decide:
#
#
#       consider another service
#
#
# Routing may decide:
#
#
#       no viable route
#
#
# These remain separate responsibilities.
#
#
# ============================================================================
# MULTI-CLUSTER HEALTH
# ============================================================================
#
# Future Agent 11 may observe:
#
#
#       EKS cluster A
#
#       AKS cluster B
#
#       GKE cluster C
#
#       OKE cluster D
#
#       on-prem cluster E
#
#
# A logical AI service may span more than one cluster.
#
#
# Therefore:
#
#
#       ONE SERVICE
#           !=
#       ONE CLUSTER
#
#
# and:
#
#
#       CLUSTER HEALTH
#           !=
#       SERVICE HEALTH
#
#
# ============================================================================
# MULTI-CLOUD HEALTH
# ============================================================================
#
# Agent 11 must continue preserving:
#
#
#       ROUTING DOMAIN
#           !=
#       CLOUD PROVIDER
#
#
# For example:
#
#
#       COMPANY_CLOUD_LLM
#
#
# may contain deployments on:
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
# A cloud provider's identity does not determine Agent 11 authorization.
#
#
# ============================================================================
# MODEL != SERVICE != DEPLOYMENT
# ============================================================================
#
# SEIR-II will likely need:
#
#
#       AIModel
#           |
#           v
#       AIService
#           |
#           +-------------------+
#           |                   |
#           v                   v
#       Deployment A        Deployment B
#           |                   |
#           v                   v
#       Endpoint(s)         Endpoint(s)
#
#
# Health evidence may eventually attach to different levels:
#
#
#       service
#
#       deployment
#
#       endpoint
#
#       accelerator
#
#       gateway
#
#
# Do not pretend these identities are interchangeable.
#
#
#       MODEL != SERVICE
#
#       SERVICE != DEPLOYMENT
#
#       DEPLOYMENT != ENDPOINT
#
#
# ============================================================================
# SERVICE-LEVEL HEALTH MAY BECOME AN AGGREGATE
# ============================================================================
#
# Suppose:
#
#
#       Tokyo deployment
#           -> AVAILABLE
#
#
#       Virginia deployment
#           -> UNAVAILABLE
#
#
# What is:
#
#
#       AIService health?
#
#
# There may be no universally correct answer.
#
#
# It depends upon what "service" means operationally.
#
#
# If either deployment can serve requests:
#
#
#       service may remain available
#
#
# If a request is residency-bound to Virginia:
#
#
#       that request may have no usable deployment
#
#
# Notice what happened:
#
#
#       GLOBAL SERVICE HEALTH
#
# became insufficient for:
#
#
#       REQUEST-SPECIFIC VIABILITY
#
#
# This is why health should remain evidence feeding candidate evaluation
# rather than trying to become the routing engine.
#
#
# ============================================================================
# HEALTH STATE != WORKLOAD SUITABILITY
# ============================================================================
#
# This remains critical.
#
#
# A DEGRADED deployment may be perfectly suitable for:
#
#
#       LIGHT
#
#
# reasoning while unsuitable for:
#
#
#       HEAVY
#
#
# reasoning.
#
#
# Therefore:
#
#
#       HEALTH STATE
#           !=
#       WORKLOAD SUITABILITY
#
#
# ============================================================================
# HEALTH != CAPABILITY
# ============================================================================
#
# A healthy service can lack a required capability.
#
#
# An unhealthy service can expose a perfectly capable model.
#
#
# Therefore:
#
#
#       HEALTH
#           !=
#       CAPABILITY
#
#
# ============================================================================
# HEALTH != PATH
# ============================================================================
#
# A service can be healthy in Tokyo while Agent 11 in Virginia cannot reach
# it because:
#
#
#       VPN failure
#
#       BGP withdrawal
#
#       SD-WAN failure
#
#       private-link failure
#
#       firewall change
#
#       DNS failure
#
#
# Health should remain:
#
#
#       AVAILABLE
#
#
# if the service itself is operational.
#
#
# Path may simultaneously be:
#
#
#       UNAVAILABLE
#
#
# ============================================================================
# BGP DOES NOT BELONG HERE
# ============================================================================
#
# BGP may eventually provide important network-path evidence.
#
#
# BGP answers questions such as:
#
#
#       "How can packets reach this destination?"
#
#
# It does not answer:
#
#
#       "Is the AI inference application healthy?"
#
#
# and certainly not:
#
#
#       "May E9 data be sent there?"
#
#
# Therefore:
#
#
#       BGP REACHABLE != SERVICE HEALTHY
#
#       BGP REACHABLE != AI AUTHORIZED
#
#
# ============================================================================
# SD-WAN DOES NOT BELONG HERE
# ============================================================================
#
# SD-WAN may influence path selection and path health.
#
#
# It should not become service-health semantics.
#
#
# ============================================================================
# DNS DOES NOT BELONG HERE
# ============================================================================
#
# DNS resolution may affect reachability.
#
#
# DNS success does not establish service health.
#
#
# DNS failure does not necessarily establish service failure.
#
#
# ============================================================================
# CONTROL PLANE != DATA PLANE
# ============================================================================
#
# Part II already established this for Kubernetes.
#
# SEIR-II must preserve it across all infrastructure.
#
#
# Examples:
#
#
#       Kubernetes API unavailable
#           while inference Pods continue serving
#
#
#       Prometheus unavailable
#           while application continues serving
#
#
#       cloud management API unavailable
#           while deployed workload continues serving
#
#
# Therefore:
#
#
#       OBSERVER FAILURE
#           !=
#       OBSERVED SYSTEM FAILURE
#
#
# ============================================================================
# OBSERVATION FAILURE SHOULD REMAIN OBSERVABLE
# ============================================================================
#
# The current SEIR-I interface maps observation failure to:
#
#
#       UNKNOWN
#
#
# That is sufficient today.
#
#
# Future evidence architecture may need to preserve WHY evidence became
# unavailable:
#
#
#       timeout
#
#       authorization failure
#
#       stale cache
#
#       collector failure
#
#       source unavailable
#
#       malformed response
#
#
# This may eventually justify richer evidence status.
#
#
# Do not add it until telemetry and behavior need it.
#
#
# ============================================================================
# UNKNOWN != ABSENT
# ============================================================================
#
# This remains one of the most important rules in the network architecture.
#
#
#       UNKNOWN
#           !=
#       ABSENT
#
#
#       UNKNOWN
#           !=
#       UNAVAILABLE
#
#
#       OBSERVATION ERROR
#           !=
#       ZERO CAPACITY
#
#
# ============================================================================
# CACHING
# ============================================================================
#
# Production health collection will likely require caching.
#
#
# Querying:
#
#
#       Kubernetes
#
#       Prometheus
#
#       service mesh
#
#       inference endpoints
#
#
# synchronously for every routing decision may be:
#
#
#       slow
#
#       expensive
#
#       fragile
#
#       rate-limited
#
#
# A future architecture may therefore use:
#
#
#       asynchronous observation
#           |
#           v
#       health evidence cache
#           |
#           v
#       synchronous assessment
#
#
# This is an implementation strategy.
#
# It does not change the domain distinction between evidence and assessment.
#
#
# ============================================================================
# CACHE HIT != FRESH EVIDENCE
# ============================================================================
#
# Cached evidence must retain observation time.
#
#
# The fact that a value exists in a cache does not establish that the value
# remains operationally useful.
#
#
#       CACHED != CURRENT
#
#
# ============================================================================
# CACHE MISS != SERVICE FAILURE
# ============================================================================
#
# Similarly:
#
#
#       CACHE MISS
#           !=
#       SERVICE UNAVAILABLE
#
#
# A cache miss is an evidence-availability problem.
#
#
# ============================================================================
# WATCHES
# ============================================================================
#
# Kubernetes watches may eventually replace repeated API polling.
#
#
# Watches introduce:
#
#
#       resource versions
#
#       reconnect behavior
#
#       missed events
#
#       stale local state
#
#       watch termination
#
#       control-plane outages
#
#
# Therefore:
#
#
#       WATCH ACTIVE
#           !=
#       EVIDENCE FRESH
#
#
# and:
#
#
#       WATCH FAILED
#           !=
#       SERVICE FAILED
#
#
# ============================================================================
# ASYNC != DOMAIN SEMANTICS
# ============================================================================
#
# Future collection may be asynchronous.
#
#
# That does not mean:
#
#
#       HealthEvidence
#
# must become an async concept.
#
#
# Async describes execution mechanics.
#
# Evidence describes domain information.
#
#
# ============================================================================
# FAILURE DOMAINS
# ============================================================================
#
# Multiple healthy endpoints do not necessarily provide independent
# resilience.
#
#
# Example:
#
#
#       endpoint A
#       endpoint B
#       endpoint C
#
#
# all run:
#
#
#       same cluster
#       same region
#       same cloud account
#       same GPU pool
#       same gateway
#
#
# Then:
#
#
#       THREE ENDPOINTS
#           !=
#       THREE FAILURE DOMAINS
#
#
# Future resilience logic may need explicit failure-domain identity.
#
#
# ============================================================================
# MODEL DIVERSITY != FAILURE-DOMAIN DIVERSITY
# ============================================================================
#
# Two different models can still fail together because they depend upon:
#
#
#       same cloud
#
#       same region
#
#       same gateway
#
#       same identity provider
#
#       same network
#
#       same quota
#
#
# Likewise:
#
#
#       SAME MODEL
#
# deployed across independent environments may provide meaningful resilience.
#
#
# ============================================================================
# HEALTH EVIDENCE != FAILURE-DOMAIN EVIDENCE
# ============================================================================
#
# Do not overload health observations to describe topology.
#
#
# ============================================================================
# SCALE TO ZERO
# ============================================================================
#
# Part II deliberately maps:
#
#
#       desired replicas = 0
#
# into:
#
#
#       UNKNOWN
#
#
# because replica evidence alone cannot distinguish:
#
#
#       intentionally dormant
#
#       scale-to-zero
#
#       maintenance
#
#       administratively disabled
#
#       misconfigured
#
#
# Future serverless and scale-to-zero infrastructure may require explicit
# lifecycle semantics.
#
#
# ============================================================================
# ZERO READY ENDPOINTS != SERVICE DOES NOT EXIST
# ============================================================================
#
# This becomes especially important with:
#
#
#       serverless inference
#
#       cold starts
#
#       event-driven scaling
#
#       scale-to-zero
#
#
# The current endpoint and health contracts may need to evolve when this
# becomes real.
#
#
# Do not silently reinterpret existing methods.
#
#
# ============================================================================
# HEALTH COLLECTION CAN ITSELF FAIL
# ============================================================================
#
# Future Agent 11 should distinguish:
#
#
#       SERVICE FAILURE
#
# from:
#
#
#       HEALTH-COLLECTION FAILURE
#
#
# If every health observer disappears, Agent 11 has an observability problem.
#
# It does not automatically have proof that every inference service failed.
#
#
# ============================================================================
# OBSERVABILITY FAILURE MAY STILL BLOCK ROUTING
# ============================================================================
#
# Security or operational policy may eventually say:
#
#
#       current health evidence is required before routing
#
#
# If health evidence cannot be established:
#
#
#       routing may reject the candidate
#
#
# while telemetry still records:
#
#
#       SERVICE STATE UNKNOWN
#
#
# Again:
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ============================================================================
# HEALTH ASSESSMENT != ROUTING CANDIDATE
# ============================================================================
#
# Even a future HealthAssessment should not contain:
#
#
#       RoutingCandidateStatus
#
#       RoutingRejectionReason
#
#       selected_service_id
#
#       fallback strategy
#
#
# Those belong to routing.
#
#
# ============================================================================
# CANDIDATE EVALUATION REMAINS THE JOIN POINT
# ============================================================================
#
# The eventual architecture remains:
#
#
#       POLICY EVIDENCE -----------+
#                                  |
#       CAPABILITY EVIDENCE -------+
#                                  |
#       HEALTH ASSESSMENT ---------+----> CANDIDATE EVALUATION
#                                  |               |
#       NETWORK PATH EVIDENCE -----+               v
#                                           RoutingCandidate
#                                                   |
#                                                   v
#                                               AIRouter
#
#
# Candidate evaluation is where independent domain facts become a routing
# viability conclusion.
#
#
# ============================================================================
# DO NOT MOVE CANDIDATE EVALUATION INTO HEALTH.PY
# ============================================================================
#
# If health.py begins asking:
#
#
#       Is E8 permitted here?
#
#       Does this model support SECURITY_ANALYSIS?
#
#       Is the VPN available?
#
#       Is this the cheapest provider?
#
#
# health.py has crossed its boundary.
#
#
# ============================================================================
# POLICY NEVER BECOMES HEALTH
# ============================================================================
#
# A service prohibited by policy does not become unhealthy.
#
#
# Example:
#
#
#       external service
#           -> AVAILABLE
#
#
#       E9 policy
#           -> DENY
#
#
# Correct:
#
#
#       HEALTH = AVAILABLE
#
#       POLICY = DENY
#
#
# Incorrect:
#
#
#       HEALTH = UNAVAILABLE
#
#
# ============================================================================
# HEALTH NEVER OVERRIDES POLICY
# ============================================================================
#
# A beautifully healthy service remains unusable if policy prohibits it.
#
#
#       HEALTHY != PERMITTED
#
#
# ============================================================================
# PRIVATE != HEALTHY
# ============================================================================
#
# Private connectivity does not prove health.
#
#
# ============================================================================
# PRIVATE != AUTHORIZED
# ============================================================================
#
# Private connectivity also does not prove authorization.
#
#
# ============================================================================
# mTLS != AUTHORIZED
# ============================================================================
#
# Encryption and authenticated transport are valuable controls.
#
# They do not decide whether organizational data policy permits the
# destination.
#
#
# ============================================================================
# EXTERNAL FM HEALTH
# ============================================================================
#
# External foundation-model providers may not expose Kubernetes-style health
# evidence.
#
#
# Evidence may instead come from:
#
#
#       provider status APIs
#
#       synthetic probes
#
#       request telemetry
#
#       SDK errors
#
#       quota APIs
#
#
# Therefore the health architecture must remain infrastructure-neutral.
#
#
# ============================================================================
# COMPANY CLOUD HEALTH
# ============================================================================
#
# COMPANY_CLOUD_LLM may eventually include:
#
#
#       Azure-hosted proprietary model
#
#       GCP-hosted proprietary model
#
#       AWS-hosted proprietary model
#
#       OCI-hosted proprietary model
#
#
# Health evidence should describe actual deployments and services.
#
# It should not force cloud identity into AIRoute.
#
#
# ============================================================================
# ON-PREM HEALTH
# ============================================================================
#
# On-prem inference may provide evidence through:
#
#
#       Kubernetes
#
#       Prometheus
#
#       bare-metal telemetry
#
#       GPU management systems
#
#       internal service discovery
#
#       synthetic probes
#
#
# The same Agent 11 health contracts should survive.
#
#
# ============================================================================
# FRAMEWORK INDEPENDENCE
# ============================================================================
#
# None of these health contracts should depend upon:
#
#
#       LangGraph
#
#       CrewAI
#
#       Bedrock AgentCore
#
#       a particular agent framework
#
#
# Those systems may consume Agent 11 behavior.
#
# They should not define Agent 11's health vocabulary.
#
#
#       FRAMEWORKS CHANGE.
#
#       DOMAIN CONTRACTS SHOULD SURVIVE THEM.
#
#
# ============================================================================
# HEALTH TELEMETRY
# ============================================================================
#
# Future telemetry may need to record:
#
#
#       evidence received
#
#       evidence source
#
#       observation time
#
#       assessment result
#
#       assessment time
#
#       stale evidence
#
#       contradictory evidence
#
#       observation failures
#
#
# This enables questions such as:
#
#
#       Why did Agent 11 consider this service UNKNOWN?
#
#       Which observer reported UNAVAILABLE?
#
#       Was the evidence stale?
#
#       Did sources disagree?
#
#       Was routing blocked because health could not be established?
#
#
# ============================================================================
# TELEMETRY != DOMAIN STATE
# ============================================================================
#
# Logging an observation is not the same as owning the observation.
#
#
# telemetry/ records what happened.
#
# models/network/ may eventually define what the evidence IS.
#
# network/ evaluates it.
#
#
# ============================================================================
# PROVENANCE SHOULD SURVIVE ASSESSMENT
# ============================================================================
#
# Suppose Agent 11 concludes:
#
#
#       UNAVAILABLE
#
#
# Future operators should still be able to discover:
#
#
#       Kubernetes -> AVAILABLE
#
#       inference probe -> UNAVAILABLE
#
#
# The assessment should not destroy the evidence that produced it.
#
#
# ============================================================================
# EXPLAINABILITY
# ============================================================================
#
# Operational decisions should eventually be explainable in human terms:
#
#
#       "Service was assessed UNKNOWN because two current evidence sources
#        disagreed."
#
#
# or:
#
#
#       "Service was assessed UNAVAILABLE because the current inference probe
#        failed and infrastructure evidence alone was insufficient to
#        establish functional availability."
#
#
# Human-readable explanation should be derived from structured evidence.
#
# Do not make free-form text the authoritative state.
#
#
# ============================================================================
# REASON != STRUCTURED EVIDENCE
# ============================================================================
#
# A field such as:
#
#
#       reason: str
#
#
# may help operators.
#
# It should not replace typed provenance and evidence.
#
#
# ============================================================================
# SECURITY OF HEALTH EVIDENCE
# ============================================================================
#
# Health telemetry can itself expose sensitive infrastructure information:
#
#
#       cluster names
#
#       internal service names
#
#       regions
#
#       IP addresses
#
#       topology
#
#       failure conditions
#
#       capacity
#
#
# Therefore future telemetry should apply data minimization.
#
#
# ============================================================================
# CREDENTIALS NEVER BELONG IN HEALTH EVIDENCE
# ============================================================================
#
# Never place:
#
#
#       kubeconfig
#
#       ServiceAccount token
#
#       API key
#
#       bearer token
#
#       cloud credential
#
#       private key
#
#
# inside:
#
#
#       HealthEvidence
#
#       HealthAssessment
#
#       telemetry events
#
#
# ============================================================================
# EVIDENCE COLLECTION AUTHORITY
# ============================================================================
#
# Each observer should receive only the authority required to observe its
# assigned evidence.
#
#
# Kubernetes observer:
#
#       read required workload state
#
#
# Prometheus observer:
#
#       query required metrics
#
#
# inference probe:
#
#       invoke narrowly scoped health operation
#
#
# None automatically requires infrastructure mutation authority.
#
#
# ============================================================================
# OBSERVE != REMEDIATE
# ============================================================================
#
# This invariant remains permanent.
#
#
# Health architecture should not gradually evolve into:
#
#
#       observe problem
#           |
#           v
#       restart production
#
#
# without a separately designed execution authority.
#
#
# ============================================================================
# AI RECOMMENDATION != EXECUTION AUTHORITY
# ============================================================================
#
# Agent 11 may eventually reason:
#
#
#       "Restarting deployment X may restore capacity."
#
#
# That reasoning does not itself grant:
#
#
#       PATCH deployment
#
#
# authority.
#
#
# ============================================================================
# REASONING AUTHORIZATION != EXECUTION AUTHORIZATION
# ============================================================================
#
# These remain separate security gates.
#
#
# ============================================================================
# MULTIPLE HEALTH SOURCES DO NOT AUTOMATICALLY FORM CONSENSUS
# ============================================================================
#
# Five observers agreeing does not automatically make them independent.
#
#
# Example:
#
#
#       Prometheus
#       service mesh
#       Kubernetes
#
#
# may all ultimately derive their state from the same failing node or the same
# control plane.
#
#
# Therefore:
#
#
#       NUMBER OF SOURCES
#           !=
#       NUMBER OF INDEPENDENT EVIDENCE CHANNELS
#
#
# ============================================================================
# CORRELATED EVIDENCE
# ============================================================================
#
# Future assessment may need to understand correlated evidence.
#
#
# Do not count:
#
#
#       five metrics from one exporter
#
#
# as:
#
#
#       five independent confirmations.
#
#
# ============================================================================
# CORRELATED FAILURE
# ============================================================================
#
# Similarly, multi-cloud or multi-deployment architecture should reason about
# shared dependencies:
#
#
#       identity provider
#
#       DNS
#
#       gateway
#
#       network carrier
#
#       cloud region
#
#       model artifact store
#
#       control plane
#
#
# Health evidence alone may not encode all of these relationships.
#
#
# ============================================================================
# HEALTH HISTORY
# ============================================================================
#
# Future systems may preserve historical evidence to answer:
#
#
#       Is this service flapping?
#
#       Has availability deteriorated?
#
#       Did failures begin after deployment?
#
#       Is this region unstable?
#
#
# Historical analysis belongs outside the immediate ServiceState contract.
#
#
# ============================================================================
# CURRENT HEALTH != HISTORICAL RELIABILITY
# ============================================================================
#
# A service may currently be:
#
#
#       AVAILABLE
#
#
# while having terrible reliability over the previous hour.
#
#
# These are different facts.
#
#
# ============================================================================
# HISTORICAL RELIABILITY != CURRENT VIABILITY
# ============================================================================
#
# Routing optimization may eventually consider reliability.
#
# But current hard constraints still come first.
#
#
# ============================================================================
# HARD CONSTRAINTS BEFORE OPTIMIZATION
# ============================================================================
#
# Agent 11 must preserve:
#
#
#       FILTER BY CONSTRAINTS FIRST.
#
#       OPTIMIZE SECOND.
#
#
# Health metrics must not become a score capable of overpowering:
#
#
#       policy denial
#
#       capability mismatch
#
#       unavailable path
#
#
# ============================================================================
# MACHINE LEARNING FOR HEALTH
# ============================================================================
#
# Future systems may predict:
#
#
#       impending failures
#
#       saturation
#
#       capacity shortages
#
#       anomalous latency
#
#
# Predictions are evidence.
#
# Predictions are not truth.
#
#
# ============================================================================
# PREDICTED FAILURE != OBSERVED FAILURE
# ============================================================================
#
# If predictive evidence is introduced, preserve its provenance and semantic
# distinction from directly observed failure.
#
#
# ============================================================================
# CONFIDENCE SCORES
# ============================================================================
#
# Do not add:
#
#
#       confidence: float
#
#
# merely because machine learning systems commonly expose confidence.
#
#
# Ask first:
#
#
#       Confidence in what?
#
#       Calibrated how?
#
#       Comparable across which sources?
#
#       Used by which behavior?
#
#
# A generic confidence float can create false mathematical precision.
#
#
# ============================================================================
# SOURCE PRECEDENCE
# ============================================================================
#
# SEIR-II may eventually establish rules such as:
#
#
#       functional inference evidence
#           has different relevance from
#       infrastructure replica evidence
#
#
# That is reasonable.
#
#
# But precedence must be:
#
#
#       explicit
#
#       testable
#
#       documented
#
#       observable
#
#
# not hidden inside arbitrary if-statements.
#
#
# ============================================================================
# PRECEDENCE != TRUST
# ============================================================================
#
# A source can be more relevant to a particular operational question without
# being universally more trustworthy.
#
#
# ============================================================================
# HEALTH ASSESSMENT POLICY
# ============================================================================
#
# If evidence-resolution rules become substantial, Agent 11 may eventually
# need an explicit health-assessment policy/configuration concept.
#
#
# Do not bury dozens of organization-specific thresholds inside health.py.
#
#
# ============================================================================
# ORGANIZATION POLICY != HEALTH-ASSESSMENT POLICY
# ============================================================================
#
# Be careful with terminology.
#
#
# Data-routing policy answers:
#
#
#       MAY THIS REQUEST USE THIS DESTINATION?
#
#
# Health-assessment configuration answers:
#
#
#       HOW SHOULD OPERATIONAL EVIDENCE
#       BE INTERPRETED?
#
#
# They are separate policy domains.
#
#
# ============================================================================
# THRESHOLDS
# ============================================================================
#
# Future evidence may require thresholds:
#
#
#       error rate
#
#       latency
#
#       queue depth
#
#       GPU utilization
#
#       available capacity
#
#
# Thresholds should be configuration.
#
# Do not hard-code production assumptions into domain models.
#
#
# ============================================================================
# THRESHOLD != DOMAIN TRUTH
# ============================================================================
#
# Example:
#
#
#       latency > 2 seconds
#
#
# might be DEGRADED for one workload and perfectly acceptable for another.
#
#
# ============================================================================
# REQUEST-SPECIFIC HEALTH SUITABILITY
# ============================================================================
#
# Eventually Agent 11 may need to distinguish:
#
#
#       SERVICE CONDITION
#
# from:
#
#
#       SERVICE SUITABILITY FOR THIS REQUEST
#
#
# The latter belongs closer to candidate evaluation.
#
#
# Do not mutate the health state merely because request requirements differ.
#
#
# ============================================================================
# HEALTH ASSESSMENT SHOULD REMAIN REQUEST-INDEPENDENT WHEN POSSIBLE
# ============================================================================
#
# A useful architectural preference is:
#
#
#       HealthAssessment
#           describes service condition
#
#
# while:
#
#
#       candidate evaluation
#           decides request-specific suitability
#
#
# This keeps operational observation reusable across many requests.
#
#
# ============================================================================
# HEALTH AND FALLBACK
# ============================================================================
#
# A selected service may fail after routing.
#
#
# That failure can become new operational evidence.
#
#
# But:
#
#
#       INVOCATION FAILURE
#           !=
#       SERVICE FAILURE
#
#
# One failed request does not necessarily establish that the entire service
# is unavailable.
#
#
# ============================================================================
# INVOCATION FAILURE AS EVIDENCE
# ============================================================================
#
# SEIR-II may eventually convert repeated invocation failures into health
# evidence.
#
#
# That requires careful semantics:
#
#
#       timeout
#
#       provider 500
#
#       malformed response
#
#       context-window error
#
#       user input error
#
#       quota failure
#
#       policy rejection
#
#
# do not all mean the same thing.
#
#
# ============================================================================
# USER ERROR != SERVICE HEALTH FAILURE
# ============================================================================
#
# A request rejected because it exceeds a model context window should not
# automatically make the service UNAVAILABLE.
#
#
# ============================================================================
# POLICY DENIAL != SERVICE FAILURE
# ============================================================================
#
# A policy-blocked request produces no evidence that the service itself is
# unhealthy.
#
#
# ============================================================================
# CAPABILITY MISMATCH != SERVICE FAILURE
# ============================================================================
#
# This invariant remains permanent.
#
#
# ============================================================================
# FALLBACK MUST USE FRESH HEALTH EVIDENCE
# ============================================================================
#
# After a selected route fails:
#
#
#       HISTORICAL VIABILITY
#           !=
#       CURRENT VIABILITY
#
#
# Fresh routing evaluation should use current health evidence.
#
#
# ============================================================================
# HEALTH EVIDENCE MAY CHANGE DURING A REQUEST
# ============================================================================
#
# Long-running workflows may observe:
#
#
#       service AVAILABLE at start
#
#       service DEGRADED during execution
#
#       service UNAVAILABLE before next step
#
#
# Therefore health should be treated as temporal evidence, not permanent
# service metadata.
#
#
# ============================================================================
# DURABLE WORKFLOWS
# ============================================================================
#
# Future multi-agent or long-running workflows may span minutes or hours.
#
#
# A health assessment made at workflow start should not automatically remain
# authoritative for the entire workflow.
#
#
# ============================================================================
# MCP
# ============================================================================
#
# MCP tool health is related but distinct from reasoning-service health.
#
#
# Agent 11 currently separates:
#
#
#       REASONING REQUEST
#           -> model routing
#
#
#       TOOL REQUEST
#           -> MCP service
#
#
# Do not make AI service health silently become MCP tool health.
#
#
# ============================================================================
# TOOL HEALTH != MODEL HEALTH
# ============================================================================
#
# A model can be healthy while an MCP tool is unavailable.
#
#
# An MCP tool can be healthy while the selected model is unavailable.
#
#
# ============================================================================
# MULTI-AGENT WORKFLOWS
# ============================================================================
#
# Future workflows may involve several agents using different services.
#
#
# Health must remain associated with the actual service/deployment evidence,
# not with vague concepts such as:
#
#
#       "the workflow is healthy"
#
#
# unless workflow health becomes a separately modeled domain.
#
#
# ============================================================================
# OUTPUT HEALTH?
# ============================================================================
#
# Be careful with terminology.
#
#
# A successful AI response can still be:
#
#
#       incorrect
#
#       hallucinated
#
#       unsafe
#
#       poorly grounded
#
#
# That is not necessarily service-health failure.
#
#
#       SUCCESS != CORRECT
#
#       SUCCESS != GROUNDED
#
#       SUCCESS != SAFE
#
#       SUCCESS != APPROVED
#
#
# Output evaluation belongs elsewhere.
#
#
# ============================================================================
# SERVICE HEALTH != MODEL QUALITY
# ============================================================================
#
# A service can be operationally perfect while producing a poor model answer.
#
#
# ============================================================================
# DATA CLASSIFICATION DOES NOT CHANGE HEALTH
# ============================================================================
#
# E9 data does not make an external provider unhealthy.
#
#
# It makes the destination prohibited for that request.
#
#
# ============================================================================
# HEALTH EVIDENCE SHOULD BE DATA-MINIMIZED
# ============================================================================
#
# Operational evidence should contain only what is necessary to describe the
# condition.
#
#
# Do not copy:
#
#
#       user prompts
#
#       model responses
#
#       credentials
#
#       protected payloads
#
#
# into health records merely because a probe failed.
#
#
# ============================================================================
# PROBE PAYLOADS
# ============================================================================
#
# Synthetic inference probes should use deliberately safe test data.
#
#
# Health checking should not require production customer data.
#
#
# ============================================================================
# PROBE AUTHORITY
# ============================================================================
#
# A health probe may require permission to invoke an inference service.
#
#
# That permission should be narrowly scoped.
#
#
# ============================================================================
# PROBE != CUSTOMER
# ============================================================================
#
# Probe success does not guarantee identical behavior for every customer
# workload.
#
#
# ============================================================================
# SECURITY INCIDENTS
# ============================================================================
#
# A service may be operationally AVAILABLE while security operations decide
# it must not be used.
#
#
# Example:
#
#
#       credential compromise
#
#       suspected model tampering
#
#       provider incident
#
#
# Those may produce security restrictions rather than health changes.
#
#
# ============================================================================
# SECURITY STATE != HEALTH STATE
# ============================================================================
#
# Do not overload UNAVAILABLE to mean:
#
#
#       "we intentionally disabled this for security."
#
#
# Operational and security facts should remain distinguishable.
#
#
# ============================================================================
# MANUAL QUARANTINE
# ============================================================================
#
# If SEIR-II introduces administrative quarantine, that should likely be a
# separate control from operational health.
#
#
# ============================================================================
# INCIDENT RESPONSE
# ============================================================================
#
# Incident response may consume health evidence.
#
# Health collection should not become the incident-response orchestrator.
#
#
# ============================================================================
# REMEDIATION
# ============================================================================
#
# Future remediation may include:
#
#
#       restart workload
#
#       scale workload
#
#       drain endpoint
#
#       fail over region
#
#       rotate credentials
#
#       replace node
#
#
# None belongs implicitly to health observation.
#
#
# ============================================================================
# HEALTH.PY SHOULD REMAIN BORING
# ============================================================================
#
# This principle matters.
#
#
# A mature health subsystem may become sophisticated.
#
# But health.py should still have a comprehensible responsibility:
#
#
#       collect / interpret operational health evidence
#
#
# It should not become:
#
#
#       infrastructure controller
#
#       policy engine
#
#       router
#
#       model selector
#
#       BGP controller
#
#       cloud failover engine
#
#       Kubernetes operator
#
#
# ============================================================================
# FUTURE PACKAGE EVOLUTION
# ============================================================================
#
# If health evidence becomes first-class:
#
#
#       models/
#       └── network/
#           ├── __init__.py
#           ├── health_evidence.py
#           └── health_assessment.py
#
#
# may become appropriate.
#
#
# If infrastructure adapters multiply:
#
#
#       network/
#       └── adapters/
#           ├── kubernetes.py
#           ├── prometheus.py
#           ├── inference_probe.py
#           └── ...
#
#
# may become appropriate.
#
#
# Neither structure should be created merely for architectural aesthetics.
#
#
# ============================================================================
# REVISIT network/endpoint.py
# ============================================================================
#
# Once HealthEvidence becomes richer, endpoint evidence may eventually need a
# similar treatment:
#
#
#       endpoint observation
#
#       endpoint evidence
#
#       freshness
#
#       provenance
#
#
# Do not mechanically refactor endpoint.py simply because health.py evolved.
#
# Let real requirements earn the abstraction.
#
#
# ============================================================================
# REVISIT network/path.py
# ============================================================================
#
# Path evidence will almost certainly require richer state eventually:
#
#
#       Internet
#
#       VPN
#
#       private link
#
#       SD-WAN
#
#       BGP
#
#       regional paths
#
#       cloud-private connectivity
#
#
# The same evidence/assessment distinction may prove useful there.
#
#
# ============================================================================
# REVISIT routing/network_context.py
# ============================================================================
#
# After:
#
#
#       endpoint.py
#
#       health.py
#
#       path.py
#
#
# are understood, return to:
#
#
#       routing/network_context.py
#
#
# Ask:
#
#
#       "Does this file still own a distinct responsibility?"
#
#
# If network/ already produces the facts candidate evaluation needs, then:
#
#
#       routing/network_context.py
#
#
# may have no reason to exist.
#
#
# Delete redundant abstractions rather than preserving them because they
# appeared in the original directory tree.
#
#
# ============================================================================
# ROUTING ORCHESTRATOR REMAINS LAST
# ============================================================================
#
# Do not make routing/orchestrator.py absorb these unresolved responsibilities
# prematurely.
#
#
# Let:
#
#
#       policy
#
#       capability
#
#       service health
#
#       endpoint
#
#       path
#
#       fallback
#
#
# reveal their stable boundaries first.
#
#
# Then the orchestrator can coordinate them without inventing their
# semantics.
#
#
# ============================================================================
# POSSIBLE FUTURE FLOW
# ============================================================================
#
#
#       Kubernetes ----------------+
#                                  |
#       Prometheus ----------------+
#                                  |
#       OpenTelemetry -------------+
#                                  |
#       inference probe -----------+
#                                  |
#       GPU telemetry -------------+
#                                  |
#                                  v
#                         HealthEvidence[]
#                                  |
#                                  v
#                       Freshness Evaluation
#                                  |
#                                  v
#                     HealthAssessmentEvaluator
#                                  |
#                                  v
#                        HealthAssessment
#                                  |
#                                  |
#             +--------------------+--------------------+
#             |                                         |
#             v                                         v
#       telemetry                                  candidate
#       / audit                                    evaluation
#                                                      |
#                         +----------------------------+-------------------+
#                         |                            |                   |
#                         v                            v                   v
#                       policy                    capability             path
#                         |                            |                   |
#                         +----------------------------+-------------------+
#                                                      |
#                                                      v
#                                              RoutingCandidate
#                                                      |
#                                                      v
#                                                  AIRouter
#
#
# ============================================================================
# IMPORTANT: HEALTH DOES NOT CALL AIRouter
# ============================================================================
#
# The arrow is:
#
#
#       health evidence
#           ->
#       candidate evaluation
#           ->
#       AIRouter
#
#
# not:
#
#
#       health.py
#           ->
#       AIRouter.select_route()
#
#
# ============================================================================
# IMPORTANT: AIRouter DOES NOT COLLECT HEALTH
# ============================================================================
#
# AIRouter receives already evaluated RoutingCandidate objects.
#
# It should not query:
#
#
#       Kubernetes
#
#       Prometheus
#
#       inference probes
#
#
# ============================================================================
# FUTURE CANDIDATE EVALUATOR
# ============================================================================
#
# The architecture still has an intentionally visible gap:
#
#
#       WHO COMBINES:
#
#           policy
#
#           capability
#
#           service availability
#
#           path availability
#
#       INTO:
#
#           RoutingCandidate
#
#
# That responsibility should be designed explicitly.
#
# Do not solve it accidentally inside health.py.
#
#
# ============================================================================
# FUTURE-SELF CHECKLIST:
# BEFORE ADDING A HEALTH FIELD
# ============================================================================
#
# Ask:
#
#       What behavior requires this field?
#
#       Is it a health fact or infrastructure detail?
#
#       Is it evidence or assessment?
#
#       Is it service-level or deployment-level?
#
#       Is it current or historical?
#
#       Does another subsystem already own it?
#
#       Does it expose sensitive infrastructure information?
#
#
# ============================================================================
# FUTURE-SELF CHECKLIST:
# BEFORE ADDING AN EVIDENCE SOURCE
# ============================================================================
#
# Ask:
#
#       What unique operational fact does this source provide?
#
#       Is that fact already available elsewhere?
#
#       Is the source independent?
#
#       How fresh must its evidence be?
#
#       What happens when observation fails?
#
#       What authority does collection require?
#
#       Does collection accidentally require write permissions?
#
#
# ============================================================================
# FUTURE-SELF CHECKLIST:
# BEFORE ADDING SOURCE PRECEDENCE
# ============================================================================
#
# Ask:
#
#       Are these observations actually contradictory?
#
#       Or do they measure different dimensions?
#
#       Why is one source more relevant?
#
#       Is the rule explicit?
#
#       Is the rule testable?
#
#       Is freshness considered?
#
#       Is provenance preserved?
#
#
# ============================================================================
# FUTURE-SELF CHECKLIST:
# BEFORE ADDING A SCORE
# ============================================================================
#
# Ask:
#
#       What exactly does the number mean?
#
#       Is it calibrated?
#
#       Are different sources mathematically comparable?
#
#       What decision consumes the score?
#
#       Could a score accidentally override a hard constraint?
#
#
# If the answers are vague:
#
#
#       DO NOT ADD THE SCORE.
#
#
# ============================================================================
# FUTURE-SELF CHECKLIST:
# BEFORE ADDING REMEDIATION
# ============================================================================
#
# Ask:
#
#       Is this still observation?
#
#       What execution authority is required?
#
#       What policy authorizes the action?
#
#       Is human approval required?
#
#       Is the action idempotent?
#
#       What is the rollback behavior?
#
#       What is audited?
#
#
# If health.py itself is answering these questions, the boundary is probably
# wrong.
#
#
# ============================================================================
# FUTURE-SELF CHECKLIST:
# BEFORE ADDING MULTI-CLOUD LOGIC
# ============================================================================
#
# Ask:
#
#       Is this fact really about cloud provider?
#
#       Is it actually about deployment?
#
#       Is it about routing domain?
#
#       Is it about network path?
#
#       Is it about failure domain?
#
#
# Preserve:
#
#
#       ROUTING DOMAIN
#           !=
#       CLOUD PROVIDER
#           !=
#       DEPLOYMENT
#           !=
#       NETWORK PATH
#
#
# ============================================================================
# CHEWBACCA REVIEW #1
# ============================================================================
#
# Future engineer:
#
#
#       "Kubernetes says four replicas are available,
#        so E9 data can go there."
#
#
# Chewbacca:
#
#
#       NO.
#
#
# Kubernetes reported infrastructure condition.
#
# Policy decides whether E9 data may use the destination.
#
#
# ============================================================================
# CHEWBACCA REVIEW #2
# ============================================================================
#
# Future engineer:
#
#
#       "Prometheus timed out, so the AI service is down."
#
#
# Chewbacca:
#
#
#       NO.
#
#
# The observer failed.
#
# The observed system may still be operating.
#
#
# ============================================================================
# CHEWBACCA REVIEW #3
# ============================================================================
#
# Future engineer:
#
#
#       "Three health sources agree, so confidence is 0.97."
#
#
# Chewbacca:
#
#
#       SHOW YOUR MATH.
#
#
# Three correlated observers do not magically create calibrated probability.
#
#
# ============================================================================
# CHEWBACCA REVIEW #4
# ============================================================================
#
# Future engineer:
#
#
#       "The service is DEGRADED because Kubernetes says AVAILABLE
#        and the inference probe says UNAVAILABLE."
#
#
# Chewbacca:
#
#
#       THAT IS NOT WHAT DEGRADED MEANS.
#
#
# Disagreement is not arithmetic.
#
#
# ============================================================================
# CHEWBACCA REVIEW #5
# ============================================================================
#
# Future engineer:
#
#
#       "I added kubectl rollout restart to HealthEvaluator."
#
#
# Chewbacca:
#
#
#       YOUR PULL REQUEST HAS BEEN RETURNED
#       TO THE FOREST MOON OF ENDOR.
#
#
# Observation authority is not remediation authority.
#
#
# ============================================================================
# POSSIBLE SEIR-II DOMAIN EVOLUTION
# ============================================================================
#
# The following concepts may eventually earn implementation:
#
#
#       HealthEvidence
#
#       HealthAssessment
#
#       HealthEvidenceType
#
#       HealthEvidenceSourceType
#
#       HealthEvidenceFreshnessEvaluator
#
#       HealthAssessmentEvaluator
#
#       Deployment
#
#       DeploymentIdentity
#
#       FailureDomain
#
#
# These names are architectural possibilities.
#
#
#       COMMENTED NAME
#           !=
#       APPROVED DOMAIN TYPE
#
#
# ============================================================================
# POSSIBLE SEIR-II PROVIDER EVOLUTION
# ============================================================================
#
# The current:
#
#
#       HealthEvidenceSource
#           ->
#       ServiceState
#
#
# may eventually evolve toward:
#
#
#       HealthEvidenceProvider
#           ->
#       HealthEvidence
#
#
# or:
#
#
#       HealthEvidenceProvider
#           ->
#       list[HealthEvidence]
#
#
# depending upon actual collection semantics.
#
#
# Do not change the interface until multiple evidence records are genuinely
# required.
#
#
# ============================================================================
# POSSIBLE SEIR-II ASSESSMENT EVOLUTION
# ============================================================================
#
# A future architecture might become:
#
#
#       Evidence Providers
#               |
#               v
#       HealthEvidence[]
#               |
#               v
#       freshness filtering
#               |
#               v
#       dimensional interpretation
#               |
#               v
#       HealthAssessmentEvaluator
#               |
#               v
#       HealthAssessment
#
#
# But each arrow represents a responsibility.
#
#
# Do not compress all arrows into one giant:
#
#
#       HealthManager
#
#
# ============================================================================
# HEALTH MANAGER WARNING
# ============================================================================
#
# If someone proposes:
#
#
#       class HealthManager:
#
#
# ask immediately:
#
#
#       What exactly does it manage?
#
#
# If the answer is:
#
#
#       Kubernetes
#       Prometheus
#       probes
#       GPUs
#       BGP
#       routing
#       failover
#       remediation
#
#
# the class name is hiding collapsed architecture.
#
#
# ============================================================================
# PART III FINAL INVARIANTS
# ============================================================================
#
#       EVIDENCE != ASSESSMENT
#
#       ASSESSMENT != ROUTING DECISION
#
#       OBSERVATION != ABSOLUTE TRUTH
#
#       SOURCE != EVIDENCE TYPE
#
#       SOURCE KNOWN != SOURCE AUTHORITATIVE
#
#       TRUSTED SOURCE != INFALLIBLE SOURCE
#
#       VALID PYDANTIC MODEL != TRUSTED EVIDENCE
#
#       STALE EVIDENCE != FALSE EVIDENCE
#
#       OBSERVED THEN != TRUE NOW
#
#       CACHE HIT != FRESH EVIDENCE
#
#       CACHE MISS != SERVICE FAILURE
#
#       WATCH FAILED != SERVICE FAILED
#
#       UNKNOWN != UNAVAILABLE
#
#       UNKNOWN != ABSENT
#
#       OBSERVATION FAILURE != SERVICE FAILURE
#
#       CONTROL-PLANE FAILURE != DATA-PLANE FAILURE
#
#       DISAGREEMENT != DEGRADED
#
#       AVAILABLE + UNAVAILABLE != DEGRADED
#
#       MULTIPLE OBSERVATIONS != PERMISSION TO INVENT A SCORE
#
#       NUMBER OF SOURCES != NUMBER OF INDEPENDENT EVIDENCE CHANNELS
#
#       HEALTH STATE != WORKLOAD SUITABILITY
#
#       HEALTH != CAPABILITY
#
#       HEALTH != POLICY
#
#       HEALTH != PATH
#
#       HEALTH != ROUTING
#
#       HEALTH != RETRY POLICY
#
#       HEALTH != REMEDIATION
#
#       SERVICE HEALTH != SERVICE CAPACITY
#
#       QUOTA != HEALTH
#
#       KUBERNETES WORKLOAD HEALTH != AI INFERENCE HEALTH
#
#       PROBE SUCCESS != UNIVERSAL SERVICE SUCCESS
#
#       GPU HEALTH != SERVICE AUTHORIZATION
#
#       MESH HEALTH != AGENT 11 AUTHORIZATION
#
#       mTLS != DATA POLICY APPROVAL
#
#       BGP REACHABLE != SERVICE HEALTHY
#
#       BGP REACHABLE != AI AUTHORIZED
#
#       MODEL != SERVICE
#
#       SERVICE != DEPLOYMENT
#
#       DEPLOYMENT != ENDPOINT
#
#       ENDPOINT != HEALTH EVIDENCE
#
#       MULTIPLE ENDPOINTS != MULTIPLE FAILURE DOMAINS
#
#       MODEL DIVERSITY != FAILURE-DOMAIN DIVERSITY
#
#       CURRENT HEALTH != HISTORICAL RELIABILITY
#
#       HISTORICAL RELIABILITY != CURRENT VIABILITY
#
#       INVOCATION FAILURE != SERVICE FAILURE
#
#       POLICY DENIAL != SERVICE FAILURE
#
#       CAPABILITY MISMATCH != SERVICE FAILURE
#
#       OBSERVE != REMEDIATE
#
#       DETECT != ACT
#
#       REASONING AUTHORIZATION != EXECUTION AUTHORIZATION
#
#       READ AUTHORITY != WRITE AUTHORITY
#
#       FAIL CLOSED != FALSIFY STATE
#
#       FILTER BY CONSTRAINTS FIRST
#
#       OPTIMIZE SECOND
#
#       POLICY NEVER BECOMES A SCORE
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================
# FINAL WARNING TO FUTURE SELF
# ============================================================================
#
# If health.py eventually knows:
#
#
#       how to authenticate to every Kubernetes cluster
#
#       how to execute PromQL
#
#       how to restart Deployments
#
#       how to inspect NVIDIA drivers
#
#       how to read BGP routes
#
#       how to choose between AWS, Azure, GCP, and OCI
#
#       how to classify E9 data
#
#       how to select Claude versus Gemini
#
#       how to calculate token cost
#
#       how to perform fallback
#
#       how to patch production
#
#
# then:
#
#
#       HEALTH.PY DOES NOT NEED
#       ANOTHER 2,000 LINES.
#
#
#       THE ARCHITECTURAL BOUNDARIES
#       HAVE COLLAPSED.
#
#
# ============================================================================
# DECISION RECORD
# ============================================================================
#
# CURRENT SEIR-I:
#
#
#       HealthEvidenceSource
#           ->
#       ServiceState
#
#
#       StaticHealthEvidenceSource
#
#       KubernetesHealthEvidenceSource
#
#       NetworkHealthEvaluator
#
#
# CURRENT CORRELATION:
#
#
#       service_id
#
#
# CURRENT HEALTH STATES:
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
# CURRENT KUBERNETES EVIDENCE:
#
#
#       Deployment desired replicas
#
#       Deployment available replicas
#
#
# CURRENT NON-GOALS:
#
#
#       multi-source evidence fusion
#
#       first-class HealthEvidence
#
#       first-class HealthAssessment
#
#       deployment identity
#
#       failure-domain identity
#
#       Prometheus integration
#
#       OpenTelemetry integration
#
#       inference probes
#
#       GPU telemetry
#
#       health scoring
#
#       autonomous remediation
#
#
# EXPECTED SEIR-II PRESSURE:
#
#
#       multiple evidence sources
#
#       evidence provenance
#
#       evidence freshness
#
#       conflicting observations
#
#       deployment-level health
#
#       multi-cluster health
#
#       multi-cloud health
#
#       inference-specific evidence
#
#       capacity and saturation
#
#       correlated failures
#
#
# LIKELY FUTURE ARCHITECTURAL RESPONSE:
#
#
#       models/network/
#           ->
#       health evidence / assessment contracts
#
#
#       network/
#           ->
#       collection / interpretation behavior
#
#
#       infrastructure adapters
#           ->
#       Kubernetes / Prometheus / probes / etc.
#
#
#       candidate evaluation
#           ->
#       combines health with policy,
#       capability, and path evidence
#
#
#       AIRouter
#           ->
#       selects among already evaluated candidates
#
#
# ============================================================================
# FINAL NOTE
# ============================================================================
#
# Part I taught Agent 11:
#
#
#       PRESERVE SERVICE STATE.
#
#
# Part II taught Agent 11:
#
#
#       TRANSLATE INFRASTRUCTURE EVIDENCE
#       WITHOUT LETTING INFRASTRUCTURE
#       OWN THE DOMAIN.
#
#
# Part III teaches future Agent 11:
#
#
#       PRESERVE WHAT WAS OBSERVED
#       SEPARATELY FROM
#       WHAT YOU CONCLUDE.
#
#
# That distinction becomes increasingly important as Agent 11 grows from a
# simple routing system into a distributed reasoning control plane.
#
#
#       EVIDENCE != ASSESSMENT
#
#
#       ASSESSMENT != AUTHORIZATION
#
#
#       AUTHORIZATION != REACHABILITY
#
#
#       REACHABILITY != SELECTION
#
#
#       SELECTION != SUCCESS
#
#
#       SUCCESS != CORRECTNESS
#
#
# Preserve the distinctions.
#
#
# ============================================================================
# END OF PART III
# ============================================================================
