"""
===============================================================================

Agent 11 - AI Reasoning Infrastructure

Module:
    orchestrator.py

Part I:
    Foundation and Dependency Contracts

===============================================================================

Business Objective
-------------------------------------------------------------------------------

Agent11Orchestrator is the top-level coordinator for Agent 11.

It coordinates specialized subsystems responsible for:

    • Policy
    • AI runtime availability
    • Network path availability
    • AI routing
    • AI execution
    • MCP tool access
    • Telemetry

The top-level orchestrator does NOT implement the detailed logic owned by
those subsystems.

Its responsibility is coordination.

The Agent 11 decision sequence is:

    Request
        │
        ▼
    Policy
        │
        ▼
    Runtime Availability
        │
        ▼
    Network Availability
        │
        ▼
    Routing
        │
        ▼
    Execution
        │
        ▼
    Telemetry

Architectural Rules
-------------------------------------------------------------------------------

    REACHABLE
        does not mean
    AUTHORIZED.

    AUTHORIZED
        does not mean
    REACHABLE.

    HEALTHY
        does not mean
    PERMITTED.

    FALLBACK
        does not mean
    IGNORE POLICY.

If no policy-compliant viable route exists, Agent 11 must fail closed.

===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


# =============================================================================
# Policy Orchestrator Contract
# =============================================================================


@runtime_checkable
class PolicyOrchestratorProtocol(Protocol):
    """
    Contract for the Agent 11 policy subsystem.

    Policy answers:

        "MAY this request use this destination?"

    The policy subsystem is responsible for concepts such as:

        • Organizational policy
        • User restrictions
        • Data classifications
        • Prohibited data
        • Permitted routes
        • Prohibited routes

    Policy does NOT determine:

        • Service health
        • Network reachability
        • Final route selection
    """

    async def evaluate(
        self,
        request: Any,
    ) -> Any:
        """
        Evaluate the request against organizational and user policy.

        Expected future return model:

            PolicyDecision
        """

        ...


# =============================================================================
# Runtime Orchestrator Contract
# =============================================================================


@runtime_checkable
class RuntimeOrchestratorProtocol(Protocol):
    """
    Contract for the Agent 11 reasoning-runtime subsystem.

    Runtime answers:

        "Which reasoning services exist?"

        "Which services support the requested capability?"

        "Which services are currently available?"

    Runtime maintains AI service availability.

    It does not decide whether a service is permitted by policy.
    """

    async def get_candidates(
        self,
        request: Any,
        policy_decision: Any,
    ) -> Any:
        """
        Return reasoning services capable of handling the request.

        Candidate services should already respect the policy decision
        supplied by the PolicyOrchestrator.

        Expected future return model:

            RuntimeCandidates
        """

        ...

    async def health(self) -> Any:
        """
        Return the current health of known AI reasoning services.

        Expected future return model:

            RuntimeHealth
        """

        ...


# =============================================================================
# Network Orchestrator Contract
# =============================================================================


@runtime_checkable
class NetworkOrchestratorProtocol(Protocol):
    """
    Contract for the Agent 11 network subsystem.

    Network answers:

        "CAN we reach this reasoning destination?"

    Network maintains path availability for reasoning destinations.

    It may eventually consume information from:

        • Local networking
        • Internet connectivity
        • VPN
        • Private connectivity
        • SD-WAN
        • BGP
        • Cloud networking

    Network does NOT determine whether an AI destination is authorized.
    """

    async def evaluate_paths(
        self,
        candidates: Any,
    ) -> Any:
        """
        Evaluate network paths to candidate reasoning services.

        Expected future return model:

            NetworkContext
        """

        ...

    async def health(self) -> Any:
        """
        Return current network and reasoning-path health.

        Expected future return model:

            NetworkHealth
        """

        ...


# =============================================================================
# Routing Orchestrator Contract
# =============================================================================


@runtime_checkable
class RoutingOrchestratorProtocol(Protocol):
    """
    Contract for the Agent 11 routing subsystem.

    Routing answers:

        "WHICH viable reasoning destination should we use?"

    Routing selects among destinations that have survived:

        • Policy evaluation
        • Capability evaluation
        • Runtime health evaluation
        • Network path evaluation

    Routing does not create authorization.

    It selects within the authorized set.
    """

    async def select(
        self,
        request: Any,
        policy_decision: Any,
        candidates: Any,
        network_context: Any,
    ) -> Any:
        """
        Select the preferred viable reasoning route.

        Expected future return model:

            RoutingDecision
        """

        ...


# =============================================================================
# AI Orchestrator Contract
# =============================================================================


@runtime_checkable
class AIOrchestratorProtocol(Protocol):
    """
    Contract for AI reasoning execution.

    The AI orchestrator performs the actual reasoning invocation after
    Agent 11 has selected a valid route.

    AI execution may eventually support:

        • External foundational models
        • Company cloud LLMs
        • Company on-premises LLMs
        • Multiple model providers
        • Model redundancy
        • Provider adapters

    AIOrchestrator does NOT decide which route is authorized.

    It executes the RoutingDecision it receives.
    """

    async def execute(
        self,
        request: Any,
        routing_decision: Any,
    ) -> Any:
        """
        Execute the reasoning request using the selected route.

        Expected future return model:

            AIResponse
        """

        ...

    async def health(self) -> Any:
        """
        Return health information for the AI execution subsystem.
        """

        ...


# =============================================================================
# MCP Orchestrator Contract
# =============================================================================


@runtime_checkable
class MCPOrchestratorProtocol(Protocol):
    """
    Contract for MCP tool orchestration.

    MCP represents the tool-capability path within Agent 11.

    Reasoning requests and tool requests remain separate architectural
    concerns.

        Reasoning
            → AI routing

        Tools
            → MCP

    Discovery of an MCP tool does NOT automatically establish authority
    to invoke that tool.
    """

    async def execute(
        self,
        request: Any,
    ) -> Any:
        """
        Execute an authorized MCP tool request.

        Expected future return model:

            MCPResponse
        """

        ...

    async def health(self) -> Any:
        """
        Return MCP service and tool availability information.
        """

        ...


# =============================================================================
# Telemetry Orchestrator Contract
# =============================================================================


@runtime_checkable
class TelemetryOrchestratorProtocol(Protocol):
    """
    Contract for Agent 11 telemetry.

    Telemetry should eventually allow administrators and engineers to
    reconstruct the reasoning path taken by Agent 11.

    Important events may include:

        • Request received
        • Data classification
        • Policy decision
        • Prohibited routes
        • Runtime candidates
        • Service health
        • Network path state
        • Routing decision
        • Fallback
        • AI invocation
        • MCP invocation
        • Request blocked
        • Request failed
        • Request completed

    Telemetry does not make routing decisions.

    It records them.
    """

    async def record(
        self,
        event: Any,
    ) -> None:
        """
        Record one Agent 11 telemetry event.

        Expected future event model:

            TelemetryEvent
        """

        ...


# =============================================================================
# Agent 11 Dependency Container
# =============================================================================


@dataclass(
    frozen=True,
    slots=True,
)
class Agent11Dependencies:
    """
    Contains the major subsystems required by Agent11Orchestrator.

    Dependencies are injected rather than constructed internally.

    This provides:

        • Loose coupling
        • Easier testing
        • Replaceable implementations
        • Smaller blast radius
        • Cleaner dependency ownership

    Example
    ---------------------------------------------------------------------------

    A unit test could provide:

        FakePolicyOrchestrator

        FakeRuntimeOrchestrator

        FakeNetworkOrchestrator

        FakeRoutingOrchestrator

    and simulate:

        COMPANY_CLOUD_LLM
            service = HEALTHY
            path    = UNAVAILABLE

        COMPANY_ONPREM_LLM
            service = HEALTHY
            path    = AVAILABLE

    without requiring:

        • A real cloud LLM
        • An on-premises inference server
        • SD-WAN
        • BGP
        • A real MCP service

    SEIR-II may replace the fake implementations with real enterprise
    infrastructure without changing the Agent11Orchestrator contract.
    """

    policy: PolicyOrchestratorProtocol

    runtime: RuntimeOrchestratorProtocol

    network: NetworkOrchestratorProtocol

    routing: RoutingOrchestratorProtocol

    ai: AIOrchestratorProtocol

    mcp: MCPOrchestratorProtocol

    telemetry: TelemetryOrchestratorProtocol


# =============================================================================
# Agent 11 Orchestrator
# =============================================================================


class Agent11Orchestrator:
    """
    Top-level coordinator for Agent 11.

    Agent11Orchestrator coordinates specialized Agent 11 subsystems.

    It does not replace them.

    The complete SEIR-I implementation will support two primary request
    paths.

    ---------------------------------------------------------------------------
    Reasoning Path
    ---------------------------------------------------------------------------

        AI Request
            │
            ▼
        Policy
            │
            ▼
        Runtime
            │
            ▼
        Network
            │
            ▼
        Routing
            │
            ▼
        Route Validation
            │
            ▼
        AI Execution
            │
            ▼
        AI Response

    ---------------------------------------------------------------------------
    Tool Path
    ---------------------------------------------------------------------------

        Tool Request
            │
            ▼
        Policy / Authorization
            │
            ▼
        MCP
            │
            ▼
        Tool Response

    Telemetry surrounds both workflows.

    The top-level orchestrator should remain relatively small.

    Detailed implementation logic belongs in specialized subpackages.
    """

    def __init__(
        self,
        dependencies: Agent11Dependencies,
    ) -> None:
        """
        Initialize Agent 11 using explicitly supplied dependencies.

        Agent11Orchestrator deliberately does not construct subordinate
        orchestrators itself.

        Dependency creation belongs to:

            • Application startup
            • Configuration
            • Bootstrap logic
            • A future Agent 11 factory

        This makes Agent11Orchestrator significantly easier to test.
        """

        self._policy = dependencies.policy

        self._runtime = dependencies.runtime

        self._network = dependencies.network

        self._routing = dependencies.routing

        self._ai = dependencies.ai

        self._mcp = dependencies.mcp

        self._telemetry = dependencies.telemetry

    # =========================================================================
    # Dependency Properties
    # =========================================================================

    @property
    def policy(
        self,
    ) -> PolicyOrchestratorProtocol:
        """
        Return the configured policy orchestrator.
        """

        return self._policy

    @property
    def runtime(
        self,
    ) -> RuntimeOrchestratorProtocol:
        """
        Return the configured runtime orchestrator.
        """

        return self._runtime

    @property
    def network(
        self,
    ) -> NetworkOrchestratorProtocol:
        """
        Return the configured network orchestrator.
        """

        return self._network

    @property
    def routing(
        self,
    ) -> RoutingOrchestratorProtocol:
        """
        Return the configured routing orchestrator.
        """

        return self._routing

    @property
    def ai(
        self,
    ) -> AIOrchestratorProtocol:
        """
        Return the configured AI execution orchestrator.
        """

        return self._ai

    @property
    def mcp(
        self,
    ) -> MCPOrchestratorProtocol:
        """
        Return the configured MCP orchestrator.
        """

        return self._mcp

    @property
    def telemetry(
        self,
    ) -> TelemetryOrchestratorProtocol:
        """
        Return the configured telemetry orchestrator.
        """

        return self._telemetry


# =============================================================================
# Part II
# =============================================================================
#
# Part II will implement the AI reasoning workflow:
#
#     handle_reasoning()
#
#     _handle_reasoning()
#
#     _evaluate_policy()
#
#     _discover_candidates()
#
#     _evaluate_network()
#
#     _select_route()
#
#     _validate_route()
#
#     _execute_reasoning()
#
#     _fail_reasoning()
#
#
# Decision sequence:
#
#     POLICY
#        ↓
#     RUNTIME
#        ↓
#     NETWORK
#        ↓
#     ROUTING
#        ↓
#     FINAL VALIDATION
#        ↓
#     AI EXECUTION
#
#
# =============================================================================
# Part III
# =============================================================================
#
# Part III will implement:
#
#     handle()
#
#     handle_tool()
#
#     _handle_tool()
#
#     _record_event()
#
#     health()
#
#     _aggregate_health()
#
#     normalized operational failure handling
#
#
# =============================================================================
#
# Chewbacca's Commentary 🐾
#
# The orchestrator
#
# is the bridge.
#
# The bridge
#
# coordinates.
#
# The bridge
#
# does not
#
# manufacture
#
# the engines.
#
# It does not
#
# calculate
#
# every route.
#
# It does not
#
# inspect
#
# every packet.
#
# It does not
#
# decide
#
# whether E8
#
# may leave
#
# the company.
#
# That belongs
#
# to Policy.
#
# It does not
#
# decide
#
# whether
#
# the Dallas LLM
#
# is healthy.
#
# That belongs
#
# to Runtime.
#
# It does not
#
# decide
#
# whether
#
# BGP has
#
# a route
#
# to Dallas.
#
# That belongs
#
# to Network.
#
# It does not
#
# decide
#
# which viable
#
# destination
#
# is preferred.
#
# That belongs
#
# to Routing.
#
# Agent11Orchestrator
#
# coordinates
#
# the conversation.
#
# If this file
#
# eventually contains:
#
#     if classification == "E8":
#
# someone
#
# is in
#
# the wrong room.
#
# If this file
#
# contains:
#
#     boto3.client(...)
#
# someone
#
# is still
#
# in the
#
# wrong room.
#
# If this file
#
# starts parsing
#
# BGP attributes...
#
# evacuate
#
# the building.
#
# And if
#
# someone writes:
#
#     except Exception:
#         return None
#
# Chewbacca
#
# takes away
#
# their keyboard.
#
# Small bridge.
#
# Specialized systems.
#
# Explicit contracts.
#
# Replaceable dependencies.
#
# Testable failures.
#
# Small blast radius.
#
# No
#
# VS Code
#
# Christmas.
#
#                              — Chewbacca
#                                Chief Wookiee AI Routing Architect
#                                Agent 11 Bridge Operations
#                                Dependency Injection Enthusiast
#                                VS Code Christmas Prevention Office
#
# =============================================================================

    # =========================================================================
    # Part II - Reasoning Workflow
    # =========================================================================
    #
    # The reasoning workflow implements the core Agent 11 decision sequence:
    #
    #     POLICY
    #        ↓
    #     RUNTIME
    #        ↓
    #     NETWORK
    #        ↓
    #     ROUTING
    #        ↓
    #     FINAL VALIDATION
    #        ↓
    #     AI EXECUTION
    #
    # Each stage has a distinct responsibility.
    #
    # The top-level orchestrator coordinates those stages.
    #
    # It does not absorb their implementation logic.
    # =========================================================================


    async def handle_reasoning(
        self,
        request: Any,
    ) -> Any:
        """
        Public entry point for an Agent 11 reasoning request.

        This method intentionally delegates to the internal reasoning
        workflow.

        Part III will later introduce the more general:

            handle()

        method capable of dispatching both:

            • reasoning requests
            • MCP tool requests

        For Part II, reasoning requests may be tested directly through:

            await orchestrator.handle_reasoning(request)

        Parameters
        ----------
        request:
            The AI reasoning request.

            Expected future model:

                AIRequest

        Returns
        -------
        Any
            Expected future model:

                AIResponse

            or a normalized Agent 11 blocked / failure response.
        """

        return await self._handle_reasoning(request)


    async def _handle_reasoning(
        self,
        request: Any,
    ) -> Any:
        """
        Coordinate the complete Agent 11 reasoning workflow.

        The workflow deliberately follows the Agent 11 Architecture
        Contract in security order.

        Decision sequence:

            1. Evaluate policy.

            2. Discover capable and available reasoning services.

            3. Evaluate network paths to those services.

            4. Select a viable reasoning route.

            5. Validate the selected route against the original policy
               and operational context.

            6. Execute the reasoning request.

        Optimization occurs only after policy has constrained the
        permitted route set.

        A healthy service does not create authorization.

        A reachable service does not create authorization.

        A routing decision does not override authorization.
        """

        # ---------------------------------------------------------------------
        # Stage 1 - Policy
        # ---------------------------------------------------------------------

        policy_decision = await self._evaluate_policy(
            request=request,
        )

        if self._policy_denied(policy_decision):
            return await self._fail_reasoning(
                request=request,
                reason="POLICY_DENIED",
                context=policy_decision,
            )

        # ---------------------------------------------------------------------
        # Stage 2 - Runtime
        # ---------------------------------------------------------------------

        candidates = await self._discover_candidates(
            request=request,
            policy_decision=policy_decision,
        )

        if self._no_candidates(candidates):
            return await self._fail_reasoning(
                request=request,
                reason="NO_CAPABLE_SERVICE",
                context={
                    "policy_decision": policy_decision,
                    "candidates": candidates,
                },
            )

        # ---------------------------------------------------------------------
        # Stage 3 - Network
        # ---------------------------------------------------------------------

        network_context = await self._evaluate_network(
            candidates=candidates,
        )

        if self._no_available_path(network_context):
            return await self._fail_reasoning(
                request=request,
                reason="PATH_UNAVAILABLE",
                context={
                    "policy_decision": policy_decision,
                    "candidates": candidates,
                    "network_context": network_context,
                },
            )

        # ---------------------------------------------------------------------
        # Stage 4 - Routing
        # ---------------------------------------------------------------------

        routing_decision = await self._select_route(
            request=request,
            policy_decision=policy_decision,
            candidates=candidates,
            network_context=network_context,
        )

        if self._no_route_selected(routing_decision):
            return await self._fail_reasoning(
                request=request,
                reason="NO_VIABLE_ROUTE",
                context={
                    "policy_decision": policy_decision,
                    "candidates": candidates,
                    "network_context": network_context,
                    "routing_decision": routing_decision,
                },
            )

        # ---------------------------------------------------------------------
        # Stage 5 - Final Route Validation
        # ---------------------------------------------------------------------

        self._validate_route(
            policy_decision=policy_decision,
            candidates=candidates,
            network_context=network_context,
            routing_decision=routing_decision,
        )

        # ---------------------------------------------------------------------
        # Stage 6 - AI Execution
        # ---------------------------------------------------------------------

        return await self._execute_reasoning(
            request=request,
            routing_decision=routing_decision,
        )


    # =========================================================================
    # Policy Stage
    # =========================================================================


    async def _evaluate_policy(
        self,
        request: Any,
    ) -> Any:
        """
        Evaluate organizational and user policy for the request.

        Policy is always evaluated before:

            • runtime discovery
            • network evaluation
            • routing
            • AI execution

        Expected future return model:

            PolicyDecision
        """

        return await self._policy.evaluate(request)


    @staticmethod
    def _policy_denied(
        policy_decision: Any,
    ) -> bool:
        """
        Determine whether policy denied the request.

        This helper is intentionally conservative.

        During Part II, Agent 11 supports lightweight development
        contracts while the final Pydantic PolicyDecision model is still
        being developed.

        Once PolicyDecision is finalized, this helper should become
        strongly typed and explicit.
        """

        if policy_decision is None:
            return True

        allowed = getattr(
            policy_decision,
            "allowed",
            None,
        )

        if allowed is None and isinstance(policy_decision, dict):
            allowed = policy_decision.get("allowed")

        # Unknown policy state is not treated as permission.
        return allowed is not True


    # =========================================================================
    # Runtime Stage
    # =========================================================================


    async def _discover_candidates(
        self,
        request: Any,
        policy_decision: Any,
    ) -> Any:
        """
        Discover reasoning services capable of handling the request.

        Runtime candidate discovery occurs only after policy evaluation.

        The runtime subsystem may eventually consider:

            • reasoning capability
            • model availability
            • service health
            • supported context size
            • supported workload type
            • provider availability

        Expected future return model:

            RuntimeCandidates
        """

        return await self._runtime.get_candidates(
            request=request,
            policy_decision=policy_decision,
        )


    @staticmethod
    def _no_candidates(
        candidates: Any,
    ) -> bool:
        """
        Determine whether runtime discovery produced no usable candidates.

        This compatibility helper exists while RuntimeCandidates is still
        being designed.

        The final Pydantic model should expose this state explicitly.
        """

        if candidates is None:
            return True

        if isinstance(
            candidates,
            (list, tuple, set, frozenset),
        ):
            return len(candidates) == 0

        if isinstance(candidates, dict):
            if "candidates" in candidates:
                return len(candidates["candidates"]) == 0

            if "available" in candidates:
                return not bool(candidates["available"])

        candidate_items = getattr(
            candidates,
            "candidates",
            None,
        )

        if candidate_items is not None:
            try:
                return len(candidate_items) == 0
            except TypeError:
                pass

        available = getattr(
            candidates,
            "available",
            None,
        )

        if available is not None:
            return not bool(available)

        # Unknown candidate structure is not automatically treated as empty.
        return False


    # =========================================================================
    # Network Stage
    # =========================================================================


    async def _evaluate_network(
        self,
        candidates: Any,
    ) -> Any:
        """
        Evaluate network-path availability for candidate services.

        Network evaluation answers:

            "Can we reach these destinations?"

        It does NOT answer:

            "Are we authorized to use these destinations?"

        Expected future return model:

            NetworkContext
        """

        return await self._network.evaluate_paths(
            candidates,
        )


    @staticmethod
    def _no_available_path(
        network_context: Any,
    ) -> bool:
        """
        Determine whether no confirmed usable network path exists.

        Agent 11 treats unknown network state conservatively.

        UNKNOWN is not equivalent to AVAILABLE.

        Once NetworkContext is implemented as a Pydantic contract, this
        helper should use explicit path-state enums rather than compatibility
        inspection.
        """

        if network_context is None:
            return True

        # ---------------------------------------------------------------------
        # Dictionary compatibility
        # ---------------------------------------------------------------------

        if isinstance(network_context, dict):

            if "has_available_path" in network_context:
                return network_context["has_available_path"] is not True

            if "available" in network_context:
                return network_context["available"] is not True

            if "paths" in network_context:
                paths = network_context["paths"]

                if not paths:
                    return True

                return not any(
                    Agent11Orchestrator._path_is_available(path)
                    for path in paths
                )

        # ---------------------------------------------------------------------
        # Object compatibility
        # ---------------------------------------------------------------------

        has_available_path = getattr(
            network_context,
            "has_available_path",
            None,
        )

        if has_available_path is not None:
            return has_available_path is not True

        available = getattr(
            network_context,
            "available",
            None,
        )

        if available is not None:
            return available is not True

        paths = getattr(
            network_context,
            "paths",
            None,
        )

        if paths is not None:

            try:
                if len(paths) == 0:
                    return True
            except TypeError:
                pass

            return not any(
                Agent11Orchestrator._path_is_available(path)
                for path in paths
            )

        # ---------------------------------------------------------------------
        # Conservative Default
        # ---------------------------------------------------------------------
        #
        # If Agent 11 cannot establish that a path exists, it does not invent
        # one.
        # ---------------------------------------------------------------------

        return True


    @staticmethod
    def _path_is_available(
        path: Any,
    ) -> bool:
        """
        Determine whether one network path is explicitly available.

        Temporary compatibility logic supports both dictionaries and
        lightweight objects.

        Future implementation:

            path.status == NetworkPathStatus.AVAILABLE
        """

        if path is None:
            return False

        if isinstance(path, dict):

            available = path.get("available")

            if available is not None:
                return available is True

            status = path.get("status")

        else:

            available = getattr(
                path,
                "available",
                None,
            )

            if available is not None:
                return available is True

            status = getattr(
                path,
                "status",
                None,
            )

        if status is None:
            return False

        status_value = getattr(
            status,
            "value",
            status,
        )

        return str(status_value).upper() == "AVAILABLE"


    # =========================================================================
    # Routing Stage
    # =========================================================================


    async def _select_route(
        self,
        request: Any,
        policy_decision: Any,
        candidates: Any,
        network_context: Any,
    ) -> Any:
        """
        Select a viable reasoning destination.

        Routing occurs only after Agent 11 has:

            • evaluated policy
            • discovered runtime candidates
            • evaluated network paths

        Expected future return model:

            RoutingDecision
        """

        return await self._routing.select(
            request=request,
            policy_decision=policy_decision,
            candidates=candidates,
            network_context=network_context,
        )


    @staticmethod
    def _no_route_selected(
        routing_decision: Any,
    ) -> bool:
        """
        Determine whether the routing subsystem failed to select a route.

        Once RoutingDecision is finalized, route selection should be
        represented explicitly by the model.
        """

        if routing_decision is None:
            return True

        if isinstance(routing_decision, dict):

            selected_route = routing_decision.get(
                "selected_route"
            )

        else:

            selected_route = getattr(
                routing_decision,
                "selected_route",
                None,
            )

        return selected_route is None


    # =========================================================================
    # Final Route Validation
    # =========================================================================


    def _validate_route(
        self,
        *,
        policy_decision: Any,
        candidates: Any,
        network_context: Any,
        routing_decision: Any,
    ) -> None:
        """
        Perform defense-in-depth validation before AI execution.

        The router is not permitted to override policy.

        The selected route must satisfy the same architectural constraints
        that produced the viable-route set.

        This method intentionally performs a final validation even though
        the RoutingOrchestrator should already have selected a valid route.

        Why?

        Because:

            POLICY
                and
            ROUTING

        are separate trust boundaries.

        If policy says:

            EXTERNAL_FM = DENIED

        and routing somehow returns:

            EXTERNAL_FM

        Agent 11 must NOT invoke the model.

        That condition represents an architectural invariant violation.
        """

        selected_route = self._extract_selected_route(
            routing_decision
        )

        if selected_route is None:
            raise RuntimeError(
                "Agent 11 routing invariant violation: "
                "routing decision contains no selected route."
            )

        if not self._route_permitted(
            selected_route=selected_route,
            policy_decision=policy_decision,
        ):
            raise RuntimeError(
                "Agent 11 routing policy violation: "
                f"selected route {selected_route!r} "
                "is not permitted by policy."
            )

        if not self._route_in_candidates(
            selected_route=selected_route,
            candidates=candidates,
        ):
            raise RuntimeError(
                "Agent 11 routing invariant violation: "
                f"selected route {selected_route!r} "
                "was not present in runtime candidates."
            )

        if not self._route_has_available_path(
            selected_route=selected_route,
            network_context=network_context,
        ):
            raise RuntimeError(
                "Agent 11 routing invariant violation: "
                f"selected route {selected_route!r} "
                "does not have a confirmed available network path."
            )


    @staticmethod
    def _extract_selected_route(
        routing_decision: Any,
    ) -> Any:
        """
        Extract the selected logical route from a routing decision.
        """

        if routing_decision is None:
            return None

        if isinstance(routing_decision, dict):
            return routing_decision.get("selected_route")

        return getattr(
            routing_decision,
            "selected_route",
            None,
        )


    @staticmethod
    def _normalize_route_value(
        route: Any,
    ) -> Any:
        """
        Normalize lightweight route values for temporary comparisons.

        Future enum-driven models will remove most of this compatibility
        behavior.
        """

        if route is None:
            return None

        value = getattr(
            route,
            "value",
            route,
        )

        if isinstance(value, str):
            return value.upper()

        return value


    @classmethod
    def _route_permitted(
        cls,
        *,
        selected_route: Any,
        policy_decision: Any,
    ) -> bool:
        """
        Verify that the selected route is permitted by policy.

        Unknown policy structure fails closed.
        """

        normalized_selected = cls._normalize_route_value(
            selected_route
        )

        if policy_decision is None:
            return False

        if isinstance(policy_decision, dict):

            permitted_routes = policy_decision.get(
                "permitted_routes"
            )

            prohibited_routes = policy_decision.get(
                "prohibited_routes",
                [],
            )

        else:

            permitted_routes = getattr(
                policy_decision,
                "permitted_routes",
                None,
            )

            prohibited_routes = getattr(
                policy_decision,
                "prohibited_routes",
                [],
            )

        normalized_prohibited = {
            cls._normalize_route_value(route)
            for route in prohibited_routes or []
        }

        if normalized_selected in normalized_prohibited:
            return False

        if permitted_routes is None:
            return False

        normalized_permitted = {
            cls._normalize_route_value(route)
            for route in permitted_routes
        }

        return normalized_selected in normalized_permitted


    @classmethod
    def _route_in_candidates(
        cls,
        *,
        selected_route: Any,
        candidates: Any,
    ) -> bool:
        """
        Verify that the selected route was represented by runtime candidates.

        Runtime candidates may temporarily be represented as:

            • lists
            • tuples
            • sets
            • dictionaries
            • lightweight objects

        The final RuntimeCandidates Pydantic model will make this much
        simpler.
        """

        normalized_selected = cls._normalize_route_value(
            selected_route
        )

        if candidates is None:
            return False

        candidate_items = candidates

        if isinstance(candidates, dict):
            candidate_items = candidates.get(
                "candidates",
                candidates.get(
                    "services",
                    [],
                ),
            )

        else:
            nested_candidates = getattr(
                candidates,
                "candidates",
                None,
            )

            if nested_candidates is not None:
                candidate_items = nested_candidates

        try:
            iterator = iter(candidate_items)

        except TypeError:
            return False

        for candidate in iterator:

            if isinstance(candidate, dict):

                route = candidate.get(
                    "route",
                    candidate.get("destination"),
                )

            else:

                route = getattr(
                    candidate,
                    "route",
                    getattr(
                        candidate,
                        "destination",
                        candidate,
                    ),
                )

            if (
                cls._normalize_route_value(route)
                == normalized_selected
            ):
                return True

        return False


    @classmethod
    def _route_has_available_path(
        cls,
        *,
        selected_route: Any,
        network_context: Any,
    ) -> bool:
        """
        Verify that the selected route has a confirmed available path.

        UNKNOWN does not equal AVAILABLE.

        Missing path information does not equal AVAILABLE.
        """

        normalized_selected = cls._normalize_route_value(
            selected_route
        )

        if network_context is None:
            return False

        if isinstance(network_context, dict):
            paths = network_context.get("paths", [])

        else:
            paths = getattr(
                network_context,
                "paths",
                [],
            )

        for path in paths or []:

            if isinstance(path, dict):

                route = path.get(
                    "route",
                    path.get("destination"),
                )

            else:

                route = getattr(
                    path,
                    "route",
                    getattr(
                        path,
                        "destination",
                        None,
                    ),
                )

            if (
                cls._normalize_route_value(route)
                != normalized_selected
            ):
                continue

            if cls._path_is_available(path):
                return True

        return False


    # =========================================================================
    # AI Execution Stage
    # =========================================================================


    async def _execute_reasoning(
        self,
        *,
        request: Any,
        routing_decision: Any,
    ) -> Any:
        """
        Execute the AI reasoning request.

        This method is reached only after:

            • policy approval
            • runtime candidate discovery
            • network-path evaluation
            • route selection
            • final route validation

        AIOrchestrator receives the selected RoutingDecision.

        It does not independently select another provider.

        If the selected service fails during invocation, future fallback
        behavior must return to Agent 11 routing rather than silently
        choosing an unauthorized destination.
        """

        try:

            return await self._ai.execute(
                request=request,
                routing_decision=routing_decision,
            )

        except Exception as exc:

            return await self._fail_reasoning(
                request=request,
                reason="INVOCATION_FAILED",
                context={
                    "routing_decision": routing_decision,
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                },
            )


    # =========================================================================
    # Reasoning Failure Handling
    # =========================================================================


    async def _fail_reasoning(
        self,
        *,
        request: Any,
        reason: str,
        context: Any = None,
    ) -> Any:
        """
        Produce a temporary structured reasoning failure result.

        This is intentionally lightweight.

        Part III and the final Pydantic response contracts will replace this
        dictionary with an explicit normalized Agent 11 response model.

        Important:

            BLOCKED
                is not necessarily the same as
            FAILED.

        For example:

            POLICY_DENIED
            NO_VIABLE_ROUTE

        may indicate successful security enforcement.

        Whereas:

            INVOCATION_FAILED

        represents an operational execution failure.
        """

        blocked_reasons = {
            "POLICY_DENIED",
            "NO_CAPABLE_SERVICE",
            "PATH_UNAVAILABLE",
            "NO_VIABLE_ROUTE",
        }

        status = (
            "BLOCKED"
            if reason in blocked_reasons
            else "FAILED"
        )

        request_id = getattr(
            request,
            "request_id",
            None,
        )

        if request_id is None and isinstance(request, dict):
            request_id = request.get("request_id")

        return {
            "request_id": request_id,
            "status": status,
            "reason": reason,
            "context": context,
        }


# =============================================================================
# Chewbacca's Part II Commentary 🐾
# =============================================================================
#
# We now have
#
# traffic
#
# on the bridge.
#
#
# A request
#
# arrives.
#
#
# First:
#
#     POLICY.
#
#
# Not:
#
#     "Which model
#      is fastest?"
#
#
# Not:
#
#     "Which model
#      is cheapest?"
#
#
# Not:
#
#     "Claude seems
#      healthy."
#
#
# POLICY.
#
#
# Then:
#
#     RUNTIME.
#
#
# Which permitted
#
# reasoning services
#
# can actually
#
# perform
#
# the work?
#
#
# Then:
#
#     NETWORK.
#
#
# Can we
#
# reach them?
#
#
# A service
#
# can be
#
# perfectly healthy
#
# while the route
#
# to it
#
# is completely dead.
#
#
# Ask BGP.
#
#
# BGP knows.
#
#
# BGP always knows.
#
#
# Sometimes
#
# BGP refuses
#
# to explain itself.
#
#
# Then:
#
#     ROUTING.
#
#
# Choose among
#
# what survived.
#
#
# But then
#
# something important
#
# happens.
#
#
# Agent 11
#
# checks
#
# the router's
#
# homework.
#
#
# Policy:
#
#     E8
#
#     EXTERNAL_FM
#
#     DENIED
#
#
# Router:
#
#     EXTERNAL_FM
#
#
# Agent 11:
#
#     absolutely
#
#     not.
#
#
# The router
#
# does not
#
# outrank
#
# policy.
#
#
# Ever.
#
#
# Finally:
#
#     EXECUTION.
#
#
# Only now
#
# does anyone
#
# talk
#
# to an LLM.
#
#
# Six gates
#
# before
#
# inference.
#
#
# Some engineer
#
# will eventually
#
# complain:
#
#     "This seems
#      unnecessarily
#      complicated."
#
#
# That engineer
#
# is why
#
# we have
#
# six gates.
#
#
# And remember:
#
#
#     UNKNOWN
#
#         !=
#
#     AVAILABLE
#
#
#     HEALTHY
#
#         !=
#
#     AUTHORIZED
#
#
#     REACHABLE
#
#         !=
#
#     PERMITTED
#
#
#     ROUTER SAID SO
#
#         !=
#
#     POLICY SAID SO
#
#
# If there
#
# is no
#
# confirmed,
#
# authorized,
#
# capable,
#
# reachable
#
# reasoning path...
#
#
# do not
#
# invent one.
#
#
# BLOCK.
#
#
# Part III
#
# will remember
#
# everything
#
# everyone did.
#
#
# Telemetry
#
# is coming.
#
#
# The humans
#
# should probably
#
# start behaving.
#
#
#                              — Chewbacca
#                                Chief Wookiee AI Routing Architect
#                                Agent 11 Reasoning Control Plane
#                                Final Route Validation Officer
#                                BGP Emotional Support Department
#
# =============================================================================

    # =========================================================================
    # Part III - Unified Dispatch, MCP, Telemetry, and Health
    # =========================================================================


    async def handle(
        self,
        request: Any,
    ) -> Any:
        """
        Unified public entry point for Agent 11 requests.

        Agent 11 supports two primary request paths:

            • REASONING
            • TOOL / MCP

        The request-type contract will eventually be replaced by a
        strongly typed Pydantic model and enum.

        Until then, this method supports lightweight dictionary/object
        compatibility for testing.
        """

        await self._record_event(
            {
                "event": "REQUEST_RECEIVED",
                "request_id": self._extract_request_id(request),
                "request_type": self._extract_request_type(request),
            }
        )

        request_type = self._extract_request_type(
            request
        )

        try:

            if request_type == "REASONING":

                response = await self.handle_reasoning(
                    request
                )

            elif request_type in {
                "TOOL",
                "MCP",
            }:

                response = await self.handle_tool(
                    request
                )

            else:

                response = await self._fail_request(
                    request=request,
                    reason="UNKNOWN_REQUEST_TYPE",
                    context={
                        "request_type": request_type,
                    },
                )

        except Exception as exc:

            response = await self._fail_request(
                request=request,
                reason="ORCHESTRATION_FAILED",
                context={
                    "exception_type":
                        type(exc).__name__,

                    "exception_message":
                        str(exc),
                },
            )

        await self._record_event(
            {
                "event": "REQUEST_COMPLETED",
                "request_id": self._extract_request_id(request),
                "result": response,
            }
        )

        return response


    # =========================================================================
    # Request Type Helpers
    # =========================================================================


    @staticmethod
    def _extract_request_type(
        request: Any,
    ) -> str | None:
        """
        Extract and normalize the request type.

        Expected future enum:

            Agent11RequestType
        """

        if request is None:
            return None

        if isinstance(request, dict):

            request_type = (
                request.get("request_type")
                or
                request.get("type")
            )

        else:

            request_type = getattr(
                request,
                "request_type",
                getattr(
                    request,
                    "type",
                    None,
                ),
            )

        if request_type is None:
            return None

        value = getattr(
            request_type,
            "value",
            request_type,
        )

        return str(value).upper()


    @staticmethod
    def _extract_request_id(
        request: Any,
    ) -> Any:
        """
        Extract the request identifier for correlation and telemetry.
        """

        if request is None:
            return None

        if isinstance(request, dict):
            return request.get("request_id")

        return getattr(
            request,
            "request_id",
            None,
        )


    # =========================================================================
    # MCP / Tool Workflow
    # =========================================================================


    async def handle_tool(
        self,
        request: Any,
    ) -> Any:
        """
        Public entry point for MCP/tool requests.
        """

        return await self._handle_tool(
            request
        )


    async def _handle_tool(
        self,
        request: Any,
    ) -> Any:
        """
        Coordinate the Agent 11 MCP/tool workflow.

        Tool requests remain separate from AI reasoning requests.

        Discovery does not establish authorization.

        The basic workflow is:

            TOOL REQUEST
                │
                ▼
            POLICY
                │
                ▼
            AUTHORIZED?
             /        \\
           NO          YES
           │            │
           ▼            ▼
         BLOCK         MCP
                        │
                        ▼
                     EXECUTE
        """

        await self._record_event(
            {
                "event": "MCP_REQUEST_STARTED",
                "request_id": self._extract_request_id(request),
            }
        )

        # ---------------------------------------------------------------------
        # Policy Evaluation
        # ---------------------------------------------------------------------

        policy_decision = await self._evaluate_policy(
            request=request,
        )

        if self._policy_denied(
            policy_decision
        ):

            return await self._fail_tool(
                request=request,
                reason="MCP_TOOL_DENIED",
                context=policy_decision,
            )

        # ---------------------------------------------------------------------
        # MCP Execution
        # ---------------------------------------------------------------------

        try:

            response = await self._mcp.execute(
                request
            )

        except Exception as exc:

            return await self._fail_tool(
                request=request,
                reason="MCP_TOOL_FAILED",
                context={
                    "exception_type":
                        type(exc).__name__,

                    "exception_message":
                        str(exc),
                },
            )

        await self._record_event(
            {
                "event": "MCP_REQUEST_COMPLETED",
                "request_id": self._extract_request_id(request),
            }
        )

        return response


    # =========================================================================
    # Telemetry
    # =========================================================================


    async def _record_event(
        self,
        event: Any,
    ) -> None:
        """
        Record an Agent 11 telemetry event.

        Telemetry is deliberately abstract.

        Future implementations may send events to:

            • CloudWatch
            • OpenTelemetry
            • Splunk
            • Elastic
            • Datadog
            • Security Lake
            • SIEM
            • Kafka
            • Database storage

        The top-level orchestrator does not need to know which backend
        ultimately receives the event.
        """

        try:

            await self._telemetry.record(
                event
            )

        except Exception:
            # -----------------------------------------------------------------
            # SEIR-I behavior:
            #
            # Telemetry failure should not automatically crash the request.
            #
            # Later versions may introduce:
            #
            #     audit_required = True
            #
            # for classifications where absence of audit telemetry must cause
            # fail-closed behavior.
            # -----------------------------------------------------------------

            return None


    # =========================================================================
    # General Failure Handling
    # =========================================================================


    async def _fail_request(
        self,
        *,
        request: Any,
        reason: str,
        context: Any = None,
    ) -> Any:
        """
        Produce a normalized temporary Agent 11 request failure.

        Future implementation will replace this dictionary with a
        Pydantic Agent11Response / Agent11Failure model.
        """

        blocked_reasons = {
            "POLICY_DENIED",
            "MCP_TOOL_DENIED",
            "NO_CAPABLE_SERVICE",
            "PATH_UNAVAILABLE",
            "NO_VIABLE_ROUTE",
        }

        status = (
            "BLOCKED"
            if reason in blocked_reasons
            else "FAILED"
        )

        result = {
            "request_id":
                self._extract_request_id(
                    request
                ),

            "status":
                status,

            "reason":
                reason,

            "context":
                context,
        }

        await self._record_event(
            {
                "event": "REQUEST_FAILED",
                "request_id": result["request_id"],
                "status": status,
                "reason": reason,
            }
        )

        return result


    async def _fail_tool(
        self,
        *,
        request: Any,
        reason: str,
        context: Any = None,
    ) -> Any:
        """
        Produce a normalized temporary MCP/tool failure result.
        """

        result = await self._fail_request(
            request=request,
            reason=reason,
            context=context,
        )

        await self._record_event(
            {
                "event": "MCP_REQUEST_FAILED",
                "request_id":
                    self._extract_request_id(
                        request
                    ),

                "reason":
                    reason,
            }
        )

        return result


    # =========================================================================
    # Health Aggregation
    # =========================================================================


    async def health(
        self,
    ) -> Any:
        """
        Return an aggregated operational view of Agent 11.

        Agent11Orchestrator does not independently probe every service.

        Instead, it aggregates health information maintained by the
        specialized subsystems.

        Expected future return model:

            Agent11Health
        """

        runtime_health = await self._safe_health_call(
            subsystem="runtime",
            health_callable=self._runtime.health,
        )

        network_health = await self._safe_health_call(
            subsystem="network",
            health_callable=self._network.health,
        )

        ai_health = await self._safe_health_call(
            subsystem="ai",
            health_callable=self._ai.health,
        )

        mcp_health = await self._safe_health_call(
            subsystem="mcp",
            health_callable=self._mcp.health,
        )

        return self._aggregate_health(
            runtime_health=runtime_health,
            network_health=network_health,
            ai_health=ai_health,
            mcp_health=mcp_health,
        )


    async def _safe_health_call(
        self,
        *,
        subsystem: str,
        health_callable: Any,
    ) -> Any:
        """
        Safely request health information from one subsystem.

        A failed health query becomes UNKNOWN rather than crashing the
        entire Agent 11 health endpoint.
        """

        try:

            return await health_callable()

        except Exception as exc:

            return {
                "subsystem":
                    subsystem,

                "status":
                    "UNKNOWN",

                "error_type":
                    type(exc).__name__,

                "error":
                    str(exc),
            }


    @staticmethod
    def _extract_health_status(
        health: Any,
    ) -> str:
        """
        Extract a normalized subsystem health status.

        Supported states:

            HEALTHY
            DEGRADED
            UNAVAILABLE
            UNKNOWN
        """

        if health is None:
            return "UNKNOWN"

        if isinstance(
            health,
            str,
        ):
            return health.upper()

        if isinstance(
            health,
            dict,
        ):

            status = health.get(
                "status",
                "UNKNOWN",
            )

        else:

            status = getattr(
                health,
                "status",
                "UNKNOWN",
            )

        value = getattr(
            status,
            "value",
            status,
        )

        return str(value).upper()


    @classmethod
    def _aggregate_health(
        cls,
        *,
        runtime_health: Any,
        network_health: Any,
        ai_health: Any,
        mcp_health: Any,
    ) -> dict[str, Any]:
        """
        Aggregate subordinate subsystem health into an Agent 11 view.

        SEIR-I keeps this intentionally simple.

        Future versions may provide capability-specific health such as:

            NORMAL_REASONING
                AVAILABLE

            E7_REASONING
                AVAILABLE

            E8_REASONING
                UNAVAILABLE

            E9_REASONING
                UNAVAILABLE

        That will become important when different classifications have
        different authorized reasoning paths.
        """

        subsystems = {
            "runtime":
                runtime_health,

            "network":
                network_health,

            "ai":
                ai_health,

            "mcp":
                mcp_health,
        }

        statuses = {
            name:
                cls._extract_health_status(
                    health
                )

            for name, health
            in subsystems.items()
        }

        # ---------------------------------------------------------------------
        # Overall Health
        # ---------------------------------------------------------------------

        if all(
            status == "HEALTHY"
            for status
            in statuses.values()
        ):

            overall = "HEALTHY"

        elif all(
            status == "UNAVAILABLE"
            for status
            in statuses.values()
        ):

            overall = "UNAVAILABLE"

        elif all(
            status == "UNKNOWN"
            for status
            in statuses.values()
        ):

            overall = "UNKNOWN"

        else:

            overall = "DEGRADED"

        return {
            "status":
                overall,

            "subsystem_status":
                statuses,

            "subsystems":
                subsystems,
        }


# =============================================================================
# Chewbacca's Part III Commentary 🐾
# =============================================================================
#
# Part I
#
# built
#
# the bridge.
#
#
# Part II
#
# routed
#
# the reasoning.
#
#
# Part III
#
# asks:
#
#
#     "What happens
#      when humans
#      actually operate
#      this thing?"
#
#
# Requests
#
# now arrive
#
# through
#
# one door.
#
#
# Reasoning
#
# goes
#
# one way.
#
#
# Tools
#
# go
#
# another.
#
#
# MCP
#
# does not
#
# receive
#
# magical permission
#
# merely because
#
# a tool
#
# appeared
#
# in discovery.
#
#
# Discovery
#
# says:
#
#     "I exist."
#
#
# Policy
#
# says:
#
#     "You may
#      use it."
#
#
# Those are
#
# different
#
# sentences.
#
#
# Then
#
# telemetry
#
# begins
#
# remembering
#
# everything.
#
#
# Humans
#
# become
#
# noticeably
#
# less adventurous
#
# when they know
#
# the system
#
# remembers
#
# what they did.
#
#
# This is called:
#
#     ACCOUNTABILITY.
#
#
# Health
#
# also becomes
#
# interesting.
#
#
# One model
#
# is healthy.
#
#
# Another
#
# is unavailable.
#
#
# One path
#
# is degraded.
#
#
# MCP
#
# is healthy.
#
#
# Is Agent 11
#
# down?
#
#
# Maybe not.
#
#
# Is every
#
# reasoning capability
#
# available?
#
#
# Also
#
# maybe not.
#
#
# This is why
#
# binary health
#
# eventually
#
# becomes
#
# insufficient.
#
#
# HEALTHY
#
# DEGRADED
#
# UNAVAILABLE
#
# UNKNOWN
#
#
# Four words
#
# that will
#
# save
#
# many meetings.
#
#
# Also remember:
#
#
#     BLOCKED
#
#         !=
#
#     FAILED
#
#
# If E8
#
# cannot leave
#
# the data center
#
# and Agent 11
#
# refuses
#
# to send it
#
# to an
#
# external FM...
#
#
# the AI request
#
# did not
#
# succeed.
#
#
# The security
#
# architecture
#
# absolutely
#
# did.
#
#
# Sometimes
#
# success
#
# looks like:
#
#
#     NO ROUTE
#
#
#     REQUEST BLOCKED
#
#
#     HUMAN ALERTED
#
#
# That is
#
# not failure.
#
#
# That is
#
# discipline.
#
#
# Finally...
#
#
# if the
#
# telemetry backend
#
# goes down
#
# during SEIR-I,
#
# we do not
#
# immediately
#
# destroy
#
# the reasoning request.
#
#
# Later,
#
# someone
#
# will inevitably
#
# create:
#
#
#     audit_required = True
#
#
# Then
#
# the students
#
# will discover
#
# another wonderful
#
# enterprise truth:
#
#
# Sometimes
#
# you are not
#
# allowed
#
# to perform
#
# an operation
#
# unless
#
# you can prove
#
# that you
#
# performed it.
#
#
# Welcome
#
# to production.
#
#
#                              — Chewbacca
#                                Chief Wookiee AI Routing Architect
#                                Agent 11 Operations Center
#                                MCP Permission Enforcement Division
#                                Telemetry Remembers Everything Department
# =============================================================================

