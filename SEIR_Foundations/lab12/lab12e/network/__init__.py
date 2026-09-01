"""
Agent 11 network package.

This package contains network-related behavior used by Agent 11.

The network subsystem is responsible for determining and coordinating
network state that may later be consumed by routing.

It does NOT determine AI authorization.

The core architectural separation is:

    NETWORK
        ->
    REACHABILITY

    POLICY
        ->
    AUTHORIZATION

    ROUTING
        ->
    SELECTION


Important invariants:

    REACHABLE != AUTHORIZED

    AUTHORIZED != REACHABLE

    HEALTHY != PERMITTED

    PATH AVAILABLE != ROUTE AUTHORIZED

    ROUTE AUTHORIZED != PATH AVAILABLE


A network path may be completely operational while policy prohibits Agent 11
from sending a request through it.

Likewise, policy may authorize an AI destination while no usable network path
currently exists.

Both conditions must eventually be satisfied before a route can become
viable.


SEIR-I
------

The initial network subsystem will focus on relatively simple network facts
such as:

    endpoint state

    health state

    path state

    reachability


SEIR-II
-------

Future versions may incorporate richer network infrastructure and telemetry,
including:

    Internet connectivity

    VPN

    private connectivity

    SD-WAN

    BGP

    multi-region connectivity

    multi-cloud connectivity

    deployment-specific paths

    latency

    packet loss

    correlated network failures


Those additions must preserve the same architectural boundary:

    NETWORK STATE != SECURITY POLICY


For example:

    BGP

answers:

    "How can packets reach the destination?"

It does not answer:

    "May Agent 11 send this request to the destination?"


Likewise:

    SD-WAN PATH AVAILABLE
        !=
    AI ROUTE AUTHORIZED


Package activation
------------------

Agent 11 treats __init__.py as the package front door.

Imports should be enabled only after the corresponding implementation has
been designed, implemented, and tested.

The existence of a module does not automatically make that module part of
the package's public interface.
"""


# ============================================================================
# PACKAGE EXPORTS
# ============================================================================
#
# Planned network behavior imports are intentionally disabled until their
# corresponding implementations are complete and tested.
#
#
# from .orchestrator import NetworkOrchestrator
#
# from .endpoint import NetworkEndpointEvaluator
#
# from .health import NetworkHealthEvaluator
#
# from .path import NetworkPathEvaluator
#
#
# IMPORTANT:
#
# These class names remain provisional until endpoint.py, health.py, and
# path.py are implemented.
#
# Do not enable an import simply because the corresponding file exists.
#
#
#       FILE EXISTS
#           !=
#       PUBLIC PACKAGE CONTRACT
#
#
# ============================================================================


__all__: list[str] = []
