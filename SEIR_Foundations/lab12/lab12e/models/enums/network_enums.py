"""
Agent 11 Network Enums
======================

Defines the controlled vocabulary used by Agent 11 to describe
network paths and their operational condition.

The Agent 11 network layer exists to answer questions such as:

    - What kind of network path connects Agent 11 to a reasoning service?
    - Is that path currently usable?
    - Is the path degraded?
    - Is the current path state unknown?
    - What network information should routing consume?

The network layer does NOT answer:

    - Is the data authorized to leave the organization?
    - Is the user authorized to perform the operation?
    - Is the reasoning service healthy?
    - Is the reasoning service capable of performing the work?
    - Which AI model should be selected?
    - Which AI route should ultimately be selected?

Those responsibilities belong to other Agent 11 layers.

Architecture rules:

    NETWORK REPORTS REACHABILITY.

    POLICY REPORTS PERMISSION.

    SERVICE REPORTS CONDITION.

    ROUTING COMPOSES THOSE FACTS.

    REACHABLE != AUTHORIZED

    AUTHORIZED != REACHABLE

    PRIVATE != AUTHORIZED

    INTERNET != PROHIBITED

    NETWORK PATH != AI ROUTE

    BGP != NETWORK PATH TYPE

    SECURE TRANSPORT != DATA AUTHORIZATION

The network model is intentionally simple in SEIR-I.

This is not because enterprise networking is simple.

It is because SEIR-I establishes the interface between AI reasoning
infrastructure and enterprise network state.

Students will return to this architecture in SEIR-II, where the
network information contributing to Agent 11 routing decisions can
become significantly richer.
"""

from .base_enum import Agent11Enum


# ===========================================================================
# Network Path Type
# ===========================================================================


class NetworkPathType(Agent11Enum):
    """
    Describes the general type of network path used to reach an
    AI reasoning destination.

    LOCAL
        A path through local infrastructure.

    INTERNET
        A path using public Internet connectivity.

    VPN
        A path using VPN-mediated connectivity.

    PRIVATE_LINK
        A private service-connectivity path.

    SD_WAN
        A path whose enterprise connectivity is mediated by an
        SD-WAN architecture.

    NetworkPathType describes connectivity.

    It does NOT establish:

        - authorization
        - data classification
        - policy permission
        - reasoning capability
        - service health
        - routing viability

    A path may be technically available while policy prohibits the
    data from being sent to the destination.

    Likewise, policy may permit a destination while no usable network
    path currently exists.

    Therefore:

        REACHABLE != AUTHORIZED

        AUTHORIZED != REACHABLE
    """

    LOCAL = "local"
    INTERNET = "internet"
    VPN = "vpn"
    PRIVATE_LINK = "private_link"
    SD_WAN = "sd_wan"


# ===========================================================================
# LOCAL
# ===========================================================================

# NetworkPathType.LOCAL describes connectivity through infrastructure
# considered local to the applicable Agent 11 deployment context.
#
# A common SEIR-I example is an on-premises reasoning service:
#
#
#     Agent 11
#         |
#         v
#     Local Network
#         |
#         v
#     Company On-Prem LLM
#
#
# LOCAL describes the path category.
#
# It does not establish trust.
#
#
#     LOCAL != TRUSTED
#
#
# A local reasoning destination could still be:
#
#
#     - prohibited by policy
#     - improperly configured
#     - unhealthy
#     - incapable of the requested work
#     - unavailable
#
#
# The fact that packets remain within local infrastructure does not
# automatically establish permission to process the data.
#
#
# Therefore:
#
#
#     LOCAL != AUTHORIZED
#
#     LOCAL != HEALTHY
#
#     LOCAL != CAPABLE


# ===========================================================================
# INTERNET
# ===========================================================================

# NetworkPathType.INTERNET describes connectivity using the public
# Internet.
#
# A common example is:
#
#
#     Agent 11
#         |
#         v
#     Internet
#         |
#         v
#     External Foundational Model
#
#
# However:
#
#
#     INTERNET != EXTERNAL_FM
#
#
# The network path and AI routing domain are different concepts.
#
# A company-controlled cloud reasoning service may also be reachable
# through Internet connectivity.
#
# Likewise, an external AI provider may eventually be reachable through
# private enterprise connectivity.
#
#
# Therefore:
#
#
#     AI DESTINATION != NETWORK TRANSPORT
#
#
# INTERNET also does not automatically mean prohibited.
#
# For example:
#
#
#     Data Classification:
#         NORMAL
#
#     AI Route:
#         EXTERNAL_FM
#
#     Policy:
#         ALLOW
#
#     Service:
#         HEALTHY
#
#     Network Path:
#         INTERNET
#
#     Path Status:
#         AVAILABLE
#
#
# may be a completely valid routing candidate.
#
#
# Therefore:
#
#
#     INTERNET != DENY
#
#     PUBLIC CONNECTIVITY != AUTOMATICALLY PROHIBITED
#
#
# Policy determines whether the data may be sent.
#
# The network layer describes how the destination can be reached.


# ===========================================================================
# VPN
# ===========================================================================

# NetworkPathType.VPN describes a path using VPN-mediated connectivity.
#
# Example:
#
#
#     Agent 11
#         |
#         v
#        VPN
#         |
#         v
#     Corporate Environment
#         |
#         v
#     Reasoning Service
#
#
# VPN connectivity may provide important transport-security properties,
# but those properties do not establish AI data authorization.
#
#
#     VPN != AUTHORIZED
#
#
# Consider:
#
#
#     VPN:
#         CONNECTED
#
#     Destination:
#         REACHABLE
#
#     Data Policy:
#         DENY
#
#
# The request remains prohibited.
#
#
# This establishes an important enterprise security principle:
#
#
#     SECURE TRANSPORT != AUTHORIZED DATA MOVEMENT
#
#
# The existence of an encrypted or private tunnel answers a networking
# question.
#
# It does not answer a policy question.


# ===========================================================================
# PRIVATE_LINK
# ===========================================================================

# NetworkPathType.PRIVATE_LINK represents private service connectivity.
#
# PRIVATE_LINK is intentionally a generic Agent 11 architectural term.
#
# It should not be interpreted as requiring one specific cloud vendor's
# implementation.
#
# The category may eventually represent private service-connectivity
# mechanisms across:
#
#
#     - AWS
#     - Azure
#     - Google Cloud
#     - private data centers
#     - other enterprise environments
#
#
# Agent 11 therefore avoids foundational Enum values such as:
#
#
#     AWS_PRIVATELINK
#     AZURE_PRIVATE_ENDPOINT
#     GCP_PRIVATE_SERVICE_CONNECT
#
#
# Vendor-specific implementation details belong in configuration,
# adapters, runtime state, or future network models.
#
# The architectural vocabulary should remain stable when vendors or
# products change.
#
#
# PRIVATE_LINK also does not imply authorization.
#
#
# Example:
#
#
#     External FM
#
#     Network Path:
#         PRIVATE_LINK
#
#     Path:
#         AVAILABLE
#
#     Service:
#         HEALTHY
#
#     Policy:
#         DENY
#
#             |
#             v
#
#         NOT VIABLE
#
#
# Private connectivity does not enlarge the policy boundary.
#
#
# Therefore:
#
#
#     PRIVATE != AUTHORIZED
#
#     PRIVATE != POLICY EXCEPTION
#
#     REACHABLE != PERMITTED


# ===========================================================================
# SD_WAN
# ===========================================================================

# NetworkPathType.SD_WAN represents an enterprise path whose
# connectivity is mediated by an SD-WAN architecture.
#
# In SEIR-I, Agent 11 only needs to understand the high-level fact:
#
#
#     "This reasoning destination is reachable through an
#      SD-WAN-mediated enterprise path."
#
#
# Agent 11 does NOT currently:
#
#
#     - control the SD-WAN fabric
#     - select WAN transports
#     - modify centralized SD-WAN policy
#     - calculate SLA compliance
#     - perform application-aware routing
#     - manipulate tunnels
#     - change enterprise route advertisements
#
#
# SEIR-I consumes simplified network state.
#
# It does not attempt to replace the enterprise network controller.
#
#
#     NETWORK SYSTEM
#          |
#          | path state
#          v
#       Agent 11
#
#
# Agent 11 can then combine that state with:
#
#
#     policy
#       +
#     reasoning capability
#       +
#     service health
#       +
#     network-path state
#       =
#     routing viability


# ===========================================================================
# SD-WAN -- SEIR-II Expansion Point
# ===========================================================================

# Cisco Engineers:
#
#     We are coming back here.
#
#
# NetworkPathType.SD_WAN is intentionally simple in SEIR-I.
#
# Do not mistake the small Enum value for the eventual size of the
# networking problem.
#
# In SEIR-II, this abstraction may expand to consume substantially
# richer SD-WAN information.
#
#
#     SD-WAN Path State
#     |
#     +-- site
#     +-- region
#     +-- edge/router identity
#     |
#     +-- transport
#     |   |
#     |   +-- MPLS
#     |   +-- broadband Internet
#     |   +-- DIA
#     |   +-- LTE / 5G
#     |   +-- other enterprise WAN transports
#     |
#     +-- tunnel state
#     |
#     +-- path metrics
#     |   |
#     |   +-- latency
#     |   +-- jitter
#     |   +-- packet loss
#     |   +-- bandwidth / capacity
#     |
#     +-- SLA state
#     |
#     +-- application-aware path information
#     |
#     +-- preferred path
#     +-- alternate path
#     |
#     +-- failover state
#     |
#     +-- telemetry
#
#
# The important architectural transition will be:
#
#
#     SEIR-I
#
#         Agent 11 consumes:
#
#             PathStatus.AVAILABLE
#
#
#     SEIR-II
#
#         Students investigate:
#
#             WHY is the path AVAILABLE?
#
#
# That answer may eventually involve:
#
#
#     underlay transport
#            +
#     overlay state
#            +
#     routing state
#            +
#     SLA measurements
#            +
#     enterprise network policy
#            =
#     usable AI inference path
#
#
# For example, a future SD-WAN environment might expose:
#
#
#     Data Center 1
#     |
#     +-- MPLS
#     |   |
#     |   +-- latency:      31 ms
#     |   +-- jitter:        4 ms
#     |   +-- packet loss: 0.1%
#     |   +-- SLA:         PASS
#     |
#     +-- DIA
#     |   |
#     |   +-- latency:      64 ms
#     |   +-- jitter:       11 ms
#     |   +-- packet loss: 0.4%
#     |   +-- SLA:         PASS
#     |
#     +-- 5G
#         |
#         +-- latency:     143 ms
#         +-- jitter:       37 ms
#         +-- packet loss: 2.1%
#         +-- SLA:         FAIL
#
#
# The enterprise SD-WAN system may already know which path satisfies
# the required network policy and SLA.
#
# Agent 11 does not need to recreate the entire SD-WAN control plane.
#
# Instead, future Agent 11 network components may consume that
# intelligence when evaluating AI inference reachability.
#
#
# This creates an important bridge:
#
#
#     NETWORK ENGINEERING
#           |
#           | path intelligence
#           v
#        Agent 11
#           |
#           | viable AI reasoning path
#           v
#     AI INFRASTRUCTURE
#
#
# Existing network-engineering knowledge therefore remains directly
# relevant to AI infrastructure.
#
# The application has changed.
#
# The need to understand transport, routing, reachability, path quality,
# resiliency, and failure has not.
#
#
# IMPORTANT SECURITY BOUNDARY:
#
#
#     SD-WAN MAY OPTIMIZE HOW WE REACH A DESTINATION.
#
#     SD-WAN MAY NOT DECIDE WHETHER THE DATA IS AUTHORIZED
#     TO REACH THAT DESTINATION.
#
#
# A beautifully optimized path to a prohibited AI service is still a
# prohibited AI route.


# ===========================================================================
# BGP -- Deliberately Not a NetworkPathType
# ===========================================================================

# BGP is deliberately NOT represented as:
#
#
#     NetworkPathType.BGP
#
#
# BGP is a routing protocol.
#
# It may contribute to determining whether a usable path exists, but
# it is not itself the transport path.
#
#
# For example:
#
#
#     Agent 11
#         |
#         v
#     Private Connectivity
#         |
#         | routing information provided through BGP
#         v
#     Corporate Network
#         |
#         v
#     On-Prem Reasoning Service
#
#
# The path might therefore be represented at a high level as:
#
#
#     NetworkPathType.PRIVATE_LINK
#
#
# while BGP contributes control-plane information about how the
# destination is reached.
#
#
# Cisco Engineers:
#
#     Yes.
#
#     BGP is coming.
#
#
# In SEIR-II, routing information may contribute to NetworkPath state:
#
#
#     Prefix Advertisement
#             |
#             v
#       Route Accepted
#             |
#             v
#       Usable Next Hop
#             |
#             v
#     PathStatus.AVAILABLE
#
#
# A failure may look like:
#
#
#       Prefix Withdrawal
#             |
#             v
#       Route Disappears
#             |
#             v
#     Destination Unreachable
#             |
#             v
#     PathStatus.UNAVAILABLE
#
#
# Future routing information may include:
#
#
#     - prefixes
#     - advertisements
#     - withdrawals
#     - next-hop information
#     - route attributes
#     - path preference
#     - multiple data-center reachability
#
#
# Later labs may allow students to observe how changes in enterprise
# routing state affect the set of AI reasoning destinations Agent 11
# can actually reach.
#
#
# SEIR-I does not implement this control-plane intelligence.
#
# It creates the architectural location where that intelligence can
# later enter Agent 11.


# ===========================================================================
# SEIR-II NetworkPath Expansion
# ===========================================================================

# PLACEHOLDER FOR SEIR-II
#
# Students will return to this architecture later.
#
# SEIR-I intentionally keeps NetworkPath state relatively small.
#
# SEIR-II is expected to expand the model toward:
#
#
#     NetworkPath
#     |
#     +-- transport/path characteristics
#     |
#     +-- SD-WAN state
#     |
#     +-- routing information
#     |   |
#     |   +-- BGP
#     |   +-- prefixes
#     |   +-- advertisements
#     |   +-- withdrawals
#     |   +-- route attributes
#     |
#     +-- latency
#     +-- jitter
#     +-- loss
#     +-- SLA
#
#
# The SEIR-I question is:
#
#
#     "Is there a usable path?"
#
#
# The SEIR-II questions become:
#
#
#     "Why is the path usable?"
#
#     "Why did it become degraded?"
#
#     "Why did it disappear?"
#
#     "What routing event changed reachability?"
#
#     "Which WAN transport is currently preferred?"
#
#     "Is the selected path satisfying its SLA?"
#
#     "What happens to AI inference routing when the network
#      control plane changes?"
#
#
# Do NOT implement these SEIR-II fields here yet.
#
# This section is an architectural and curricular placeholder.
#
# The intentionally simple SEIR-I interface gives the later network
# architecture somewhere clean to expand.


# ===========================================================================
# End of Part I
# ===========================================================================

# Part II continues this SAME file.
#
# Part II will add:
#
#     PathStatus
#         AVAILABLE
#         DEGRADED
#         UNAVAILABLE
#         UNKNOWN
#
# and will demonstrate how network state interacts with:
#
#     - ServiceStatus
#     - policy decisions
#     - routing viability
#     - future Pydantic NetworkPath models
#
# Do not add another module docstring or another Agent11Enum import
# when Part II is appended.

# ===========================================================================
# Path Status
# ===========================================================================


class PathStatus(Agent11Enum):
    """
    Describes the current operational condition of a network path.

    AVAILABLE
        Agent 11 has information indicating that the network path is
        currently available for consideration.

    DEGRADED
        The network path remains usable, but one or more operating
        conditions are outside the expected normal range.

    UNAVAILABLE
        Agent 11 has information establishing that the network path
        cannot currently provide the required connectivity.

    UNKNOWN
        Agent 11 cannot currently establish the operational condition
        of the network path.

    PathStatus reports network condition.

    It does NOT determine:

        - policy permission
        - data authorization
        - service health
        - reasoning capability
        - final routing viability
        - final routing selection

    Therefore:

        AVAILABLE != AUTHORIZED

        DEGRADED != UNAVAILABLE

        UNKNOWN != AVAILABLE

        UNKNOWN != UNAVAILABLE

        NETWORK REPORTS CONDITION.

        ROUTING DECIDES CONSEQUENCE.
    """

    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


# ===========================================================================
# AVAILABLE
# ===========================================================================

# PathStatus.AVAILABLE means Agent 11 has information indicating that
# the network path is currently available for consideration.
#
# Example:
#
#
#     Agent 11
#         |
#         | PRIVATE_LINK
#         | AVAILABLE
#         v
#     Company Cloud LLM
#
#
# AVAILABLE answers a network question:
#
#
#     "Can the destination currently be reached through this path?"
#
#
# It does not answer:
#
#
#     "May this data be sent to the destination?"
#
#
# Consider:
#
#
#     External FM
#
#     Path Type:
#         INTERNET
#
#     Path Status:
#         AVAILABLE
#
#     Service Status:
#         HEALTHY
#
#     Policy:
#         DENY
#
#             |
#             v
#
#         NOT VIABLE
#
#
# The network layer has done its job correctly.
#
# It reported that the destination is reachable.
#
# Policy independently reported that the data may not be sent there.
#
#
# Therefore:
#
#
#     AVAILABLE != AUTHORIZED
#
#     AVAILABLE != PERMITTED
#
#     AVAILABLE != SELECTED
#
#
# Reachability is necessary for a viable route.
#
# Reachability alone is not sufficient.


# ===========================================================================
# DEGRADED
# ===========================================================================

# PathStatus.DEGRADED means the network path remains operational, but
# one or more conditions are outside the expected normal operating
# range.
#
# In SEIR-I, Agent 11 consumes the simplified state:
#
#
#     PathStatus.DEGRADED
#
#
# It does not yet need to understand every measurement that produced
# that state.
#
# In SEIR-II, DEGRADED may eventually result from information such as:
#
#
#     - increased latency
#     - increased jitter
#     - packet loss
#     - reduced bandwidth
#     - tunnel degradation
#     - SD-WAN SLA failure
#     - unstable routing
#     - partial transport failure
#
#
# Example:
#
#
#     Company Cloud LLM
#
#     Service:
#         HEALTHY
#
#     Network:
#         SD_WAN
#
#     Path:
#         DEGRADED
#
#
# This does not automatically mean:
#
#
#     DO NOT USE
#
#
# Another candidate might exist:
#
#
#     Company On-Prem LLM
#
#     Service:
#         HEALTHY
#
#     Path:
#         AVAILABLE
#
#
# Routing may prefer the fully available path.
#
#
# But consider:
#
#
#     Company Cloud LLM
#
#         Path:
#             DEGRADED
#
#
#     Company On-Prem LLM
#
#         Path:
#             UNAVAILABLE
#
#
#     External FM
#
#         Policy:
#             DENY
#
#
# Depending upon the later routing rules and the nature of the
# degradation, the degraded company-cloud path may remain the only
# viable candidate.
#
#
# Therefore:
#
#
#     DEGRADED != UNAVAILABLE
#
#
# The network layer reports the condition.
#
# The routing layer determines the consequence.


# ===========================================================================
# UNAVAILABLE
# ===========================================================================

# PathStatus.UNAVAILABLE means Agent 11 has information establishing
# that the path cannot currently provide the required connectivity.
#
# Possible causes may eventually include:
#
#
#     - interface failure
#     - VPN failure
#     - tunnel failure
#     - private connectivity failure
#     - SD-WAN path failure
#     - missing route
#     - route withdrawal
#     - unreachable next hop
#     - transport outage
#
#
# SEIR-I does not need to diagnose all of these conditions.
#
# It consumes:
#
#
#     PathStatus.UNAVAILABLE
#
#
# Example:
#
#
#     Company On-Prem LLM
#
#     Policy:
#         ALLOW
#
#     Service:
#         HEALTHY
#
#     Capability:
#         SUFFICIENT
#
#     Network:
#         VPN
#
#     Path:
#         UNAVAILABLE
#
#             |
#             v
#
#         NOT VIABLE
#
#
# Notice that policy has not changed.
#
# The reasoning service has not necessarily failed.
#
# The network path has failed.
#
#
# Therefore:
#
#
#     PATH FAILURE != POLICY FAILURE
#
#     PATH FAILURE != SERVICE FAILURE
#
#
# Routing consumes the network condition and reevaluates the remaining
# candidates.


# ===========================================================================
# UNKNOWN
# ===========================================================================

# PathStatus.UNKNOWN means Agent 11 cannot currently establish the
# operational condition of the network path.
#
# This is intentionally different from UNAVAILABLE.
#
#
#     UNAVAILABLE
#
#         "We have established that the path cannot currently
#          provide the required connectivity."
#
#
#     UNKNOWN
#
#         "We cannot currently establish whether the path can
#          provide the required connectivity."
#
#
# These states should remain distinguishable for:
#
#
#     - telemetry
#     - troubleshooting
#     - auditing
#     - incident response
#     - routing analysis
#
#
# Therefore:
#
#
#     UNKNOWN != UNAVAILABLE
#
#     UNKNOWN != AVAILABLE
#
#
# UNKNOWN must not accidentally inherit the privileges of AVAILABLE.
#
#
# Dangerous:
#
#
#     if path.status is not PathStatus.UNAVAILABLE:
#         send_request()
#
#
# Why?
#
# Because:
#
#
#     PathStatus.UNKNOWN
#
#
# is also:
#
#
#     not PathStatus.UNAVAILABLE
#
#
# The implementation would accidentally define:
#
#
#     UNKNOWN = GOOD ENOUGH
#
#
# Prefer explicit state handling:
#
#
#     if path.status is PathStatus.AVAILABLE:
#         ...
#
#     elif path.status is PathStatus.DEGRADED:
#         ...
#
#     elif path.status is PathStatus.UNAVAILABLE:
#         ...
#
#     elif path.status is PathStatus.UNKNOWN:
#         ...
#
#
# This supports a broader Agent 11 engineering principle:
#
#
#     UNKNOWN STATE MUST NEVER ACCIDENTALLY INHERIT
#     THE PRIVILEGES OF KNOWN-GOOD STATE.


# ===========================================================================
# Network Status and Service Status Are Independent
# ===========================================================================

# ServiceStatus and PathStatus describe independent operational
# dimensions.
#
#
#     ServiceStatus
#
#         "Is the AI reasoning service operational?"
#
#
#     PathStatus
#
#         "Is the network path to that service operational?"
#
#
# These facts must not be collapsed.
#
#
# Example 1:
#
#
#     ServiceStatus.HEALTHY
#
#     PathStatus.AVAILABLE
#
#
# The service is operational and the network path is available.
#
# This is a good candidate so far.
#
# Policy and capability must still be evaluated.
#
#
# ---------------------------------------------------------------------------
#
# Example 2:
#
#
#     ServiceStatus.HEALTHY
#
#     PathStatus.UNAVAILABLE
#
#
# The reasoning service works.
#
# Agent 11 cannot currently reach it.
#
#
#     SERVICE HEALTHY
#           +
#     PATH UNAVAILABLE
#           =
#     NOT VIABLE
#
#
# ---------------------------------------------------------------------------
#
# Example 3:
#
#
#     ServiceStatus.UNAVAILABLE
#
#     PathStatus.AVAILABLE
#
#
# The network can successfully deliver packets to the destination.
#
# Unfortunately, the reasoning service cannot currently do useful
# work.
#
#
#     NETWORK:
#
#         "I delivered your packets."
#
#
#     REASONING SERVICE:
#
#         "Congratulations. I am unavailable."
#
#
#     RESULT:
#
#         NOT VIABLE
#
#
# ---------------------------------------------------------------------------
#
# Example 4:
#
#
#     ServiceStatus.HEALTHY
#
#     PathStatus.DEGRADED
#
#
# The reasoning service is healthy.
#
# The path is impaired.
#
# Routing may consider another candidate depending upon the routing
# rules and available alternatives.
#
#
# ---------------------------------------------------------------------------
#
# Example 5:
#
#
#     ServiceStatus.UNKNOWN
#
#     PathStatus.AVAILABLE
#
#
# Network reachability has been established.
#
# Service health has not.
#
#
# ---------------------------------------------------------------------------
#
# Example 6:
#
#
#     ServiceStatus.HEALTHY
#
#     PathStatus.UNKNOWN
#
#
# The reasoning service may be healthy from the perspective of its
# service-health system.
#
# Agent 11 cannot establish a usable path to it.
#
#
# Therefore:
#
#
#     SERVICE HEALTH != NETWORK REACHABILITY
#
#     NETWORK REACHABILITY != SERVICE HEALTH


# ===========================================================================
# Network Status and Policy Are Independent
# ===========================================================================

# Network state and policy state are also independent.
#
# The network layer may establish:
#
#
#     "I can reach the destination."
#
#
# Policy may simultaneously establish:
#
#
#     "You may not send this data there."
#
#
# Example:
#
#
#     External FM
#
#     Network Path:
#         INTERNET
#
#     Path Status:
#         AVAILABLE
#
#     Service Status:
#         HEALTHY
#
#     Policy Decision:
#         DENY
#
#
# Result:
#
#
#     NOT VIABLE
#
#
# The fact that a destination is easy to reach does not create
# permission to use it.
#
#
# Likewise:
#
#
#     Company On-Prem LLM
#
#     Policy Decision:
#         ALLOW
#
#     Service Status:
#         HEALTHY
#
#     Path Status:
#         UNAVAILABLE
#
#
# Result:
#
#
#     NOT VIABLE
#
#
# Permission does not create connectivity.
#
#
# Therefore:
#
#
#     REACHABLE != AUTHORIZED
#
#     AUTHORIZED != REACHABLE


# ===========================================================================
# Private Connectivity Does Not Create Authorization
# ===========================================================================

# Engineers may understandably associate private connectivity with
# stronger security characteristics.
#
# That does not make private connectivity an authorization mechanism.
#
#
# Example:
#
#
#     Destination:
#         External AI Service
#
#     Path:
#         PRIVATE_LINK
#
#     Path Status:
#         AVAILABLE
#
#     Encryption:
#         ENABLED
#
#     Policy:
#         DENY
#
#
# Result:
#
#
#     DENY
#
#
# The network architecture may provide:
#
#
#     - confidentiality in transit
#     - controlled connectivity
#     - reduced public exposure
#     - predictable network paths
#
#
# Those characteristics are valuable.
#
# They do not rewrite data policy.
#
#
# Therefore:
#
#
#     ENCRYPTED != AUTHORIZED
#
#     PRIVATE != AUTHORIZED
#
#     REACHABLE != AUTHORIZED


# ===========================================================================
# Public Connectivity Does Not Automatically Mean Prohibited
# ===========================================================================

# The reverse assumption is also incorrect.
#
# NetworkPathType.INTERNET does not automatically produce a policy
# denial.
#
#
# Example:
#
#
#     Data:
#         NORMAL
#
#     Destination:
#         Approved External FM
#
#     Policy:
#         ALLOW
#
#     Service:
#         HEALTHY
#
#     Path:
#         INTERNET
#
#     Path Status:
#         AVAILABLE
#
#
# may be a viable candidate.
#
#
# Therefore:
#
#
#     PRIVATE != AUTOMATICALLY ALLOWED
#
#     PUBLIC != AUTOMATICALLY DENIED
#
#
# Network architecture describes connectivity.
#
# Policy determines permission.


# ===========================================================================
# BGP and Future Path-State Changes
# ===========================================================================

# Part I established that BGP is deliberately NOT a NetworkPathType.
#
# This section shows why that distinction becomes useful.
#
#
# Consider a future SEIR-II environment:
#
#
#     Company On-Prem LLM
#
#     Prefix:
#         10.40.0.0/16
#
#     BGP Advertisement:
#         PRESENT
#
#     Route:
#         ACCEPTED
#
#     Next Hop:
#         REACHABLE
#
#             |
#             v
#
#     PathStatus.AVAILABLE
#
#
# Now change the network control plane:
#
#
#     BGP UPDATE
#         |
#         v
#     10.40.0.0/16 WITHDRAWN
#         |
#         v
#     ROUTE REMOVED
#         |
#         v
#     DESTINATION NO LONGER REACHABLE
#         |
#         v
#     PathStatus.UNAVAILABLE
#
#
# Agent 11 does not need to become a BGP implementation.
#
# It needs a clean way to consume the operational consequence of
# enterprise routing state.
#
#
# This creates the future relationship:
#
#
#     NETWORK CONTROL PLANE
#              |
#              | routing intelligence
#              v
#        NetworkPath State
#              |
#              | reachability intelligence
#              v
#          Agent 11 Router
#
#
# Cisco Engineers:
#
#     Your routing knowledge did not disappear.
#
#     The application sitting above the network changed.


# ===========================================================================
# SD-WAN and Future Path-State Changes
# ===========================================================================

# Part I also established the SEIR-II SD-WAN expansion point.
#
# Consider a future environment with several transports:
#
#
#     SD-WAN Edge
#     |
#     +-- MPLS
#     |     SLA: PASS
#     |
#     +-- DIA
#     |     SLA: PASS
#     |
#     +-- 5G
#           SLA: FAIL
#
#
# The SD-WAN system may determine that MPLS is currently preferred.
#
#
#     MPLS
#       |
#       v
#     Preferred Path
#       |
#       v
#     PathStatus.AVAILABLE
#
#
# Now suppose MPLS fails:
#
#
#     MPLS
#       |
#       v
#     FAILURE
#       |
#       v
#     SD-WAN REEVALUATION
#       |
#       v
#     DIA SELECTED
#       |
#       v
#     PathStatus.AVAILABLE
#
#
# From Agent 11's SEIR-I perspective, the high-level path may have
# remained AVAILABLE throughout the transport failover.
#
# That is important.
#
# The network can absorb some failures beneath the AI application.
#
#
# In SEIR-II, students can investigate the machinery underneath that
# deceptively simple:
#
#
#     PathStatus.AVAILABLE
#
#
# They may eventually ask:
#
#
#     - Which transport is active?
#     - Did a failover occur?
#     - Which SLA triggered the failover?
#     - What was the previous path?
#     - What is the current latency?
#     - What is the current jitter?
#     - What is the current loss?
#     - Is the alternate path acceptable for AI inference?
#
#
# This is the trapdoor.
#
#
#     SEIR-I:
#
#         AVAILABLE
#
#
#     SEIR-II:
#
#         "AVAILABLE because of what?"


# ===========================================================================
# Network Path vs AI Route
# ===========================================================================

# NetworkPathType and AIRoute must remain separate.
#
#
# AIRoute answers:
#
#
#     "Which logical AI reasoning domain is being considered?"
#
#
# NetworkPathType answers:
#
#
#     "What kind of network connectivity is used to reach it?"
#
#
# Example:
#
#
#     AIRoute.COMPANY_ONPREM_LLM
#
# may be reachable through:
#
#
#     NetworkPathType.LOCAL
#
# or:
#
#
#     NetworkPathType.VPN
#
# or:
#
#
#     NetworkPathType.SD_WAN
#
#
# depending upon where Agent 11 is running.
#
#
# Likewise:
#
#
#     AIRoute.EXTERNAL_FM
#
# might be reachable through:
#
#
#     NetworkPathType.INTERNET
#
#
# or eventually:
#
#
#     NetworkPathType.PRIVATE_LINK
#
#
# Therefore:
#
#
#     NETWORK PATH != AI ROUTE
#
#
# Keeping them independent allows the same AI destination to have
# multiple possible network paths.


# ===========================================================================
# Multiple Paths to the Same AI Destination
# ===========================================================================

# A future NetworkPath model may allow multiple paths to one reasoning
# destination.
#
#
# Example:
#
#
#     Company On-Prem LLM
#             |
#             +-- SD-WAN Path A
#             |       AVAILABLE
#             |
#             +-- VPN Path B
#                     AVAILABLE
#
#
# Or:
#
#
#     Company Cloud LLM
#             |
#             +-- PRIVATE_LINK
#             |       UNAVAILABLE
#             |
#             +-- INTERNET
#                     AVAILABLE
#
#
# Whether Agent 11 may use an alternate network path may depend upon
# future network and security rules.
#
# The existence of an alternate path does not automatically mean the
# alternate path is acceptable.
#
#
# This mirrors the AI fallback rule:
#
#
#     ALTERNATE != AUTOMATICALLY VIABLE
#
#
# Every meaningful alternative must independently satisfy its
# applicable requirements.


# ===========================================================================
# Routing Viability
# ===========================================================================

# Network state contributes one part of Agent 11 routing viability.
#
#
#                         POLICY
#                            |
#                            v
#                    Policy Permitted?
#                            |
#                            v
#
#                       CAPABILITY
#                            |
#                            v
#                   Service Capable?
#                            |
#                            v
#
#                         SERVICE
#                            |
#                            v
#                  Service Available?
#                            |
#                            v
#
#                         NETWORK
#                            |
#                            v
#                     Path Available?
#                            |
#                            v
#
#                      VIABLE ROUTE
#
#
# Conceptually:
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
# NetworkPathType and PathStatus contribute connectivity information.
#
# They do not replace the other requirements.


# ===========================================================================
# Example Candidate Evaluation
# ===========================================================================

# Consider three reasoning candidates.
#
#
# Candidate A:
#
#     External FM
#
#     Policy:
#         DENY
#
#     Service:
#         HEALTHY
#
#     Path:
#         INTERNET
#
#     Path Status:
#         AVAILABLE
#
#             |
#             v
#
#     REJECTED BY POLICY
#
#
# ---------------------------------------------------------------------------
#
# Candidate B:
#
#     Company Cloud LLM
#
#     Policy:
#         ALLOW
#
#     Service:
#         HEALTHY
#
#     Path:
#         PRIVATE_LINK
#
#     Path Status:
#         UNAVAILABLE
#
#             |
#             v
#
#     REJECTED BY NETWORK STATE
#
#
# ---------------------------------------------------------------------------
#
# Candidate C:
#
#     Company On-Prem LLM
#
#     Policy:
#         ALLOW
#
#     Service:
#         HEALTHY
#
#     Path:
#         SD_WAN
#
#     Path Status:
#         AVAILABLE
#
#             |
#             v
#
#          VIABLE
#
#
# Routing can then select Candidate C.
#
#
# Notice what did NOT happen:
#
#
#     - policy did not inspect BGP
#     - network did not authorize the data
#     - service health did not select the route
#     - SD-WAN did not override policy
#
#
# Each layer reported its own facts.
#
# Routing composed them.


# ===========================================================================
# Future Pydantic NetworkPath Model
# ===========================================================================

# These Enums will eventually be composed by a Pydantic NetworkPath
# model.
#
# A deliberately simple SEIR-I version may resemble:
#
#
#     class NetworkPath(Agent11BaseModel):
#         path_id: str
#         source: str
#         destination: str
#         path_type: NetworkPathType
#         status: PathStatus
#
#
# Example:
#
#
#     path = NetworkPath(
#         path_id="cloud-to-dc1",
#         source="agent11-cloud",
#         destination="company-onprem-llm",
#         path_type=NetworkPathType.SD_WAN,
#         status=PathStatus.AVAILABLE,
#     )
#
#
# This model answers:
#
#
#     WHICH PATH?
#
#         cloud-to-dc1
#
#
#     FROM WHERE?
#
#         agent11-cloud
#
#
#     TO WHERE?
#
#         company-onprem-llm
#
#
#     WHAT KIND?
#
#         SD_WAN
#
#
#     WHAT CONDITION?
#
#         AVAILABLE
#
#
# Later SEIR-II models may expand this state without changing the
# fundamental meaning of NetworkPathType or PathStatus.


# ===========================================================================
# SEIR-II Reminder
# ===========================================================================

# DO NOT REMOVE THIS PLACEHOLDER DURING SEIR-I REFACTORING.
#
# Students will return to NetworkPath in SEIR-II.
#
#
#     NetworkPath
#     |
#     +-- transport/path characteristics
#     |
#     +-- SD-WAN state
#     |
#     +-- routing information
#     |   |
#     |   +-- BGP
#     |   +-- prefixes
#     |   +-- advertisements
#     |   +-- withdrawals
#     |   +-- route attributes
#     |
#     +-- latency
#     +-- jitter
#     +-- loss
#     +-- SLA
#
#
# SEIR-I intentionally consumes simplified path state.
#
# SEIR-II will investigate the network intelligence underneath that
# simplified state.
#
#
# The small Enum:
#
#
#     PathStatus.AVAILABLE
#
#
# is therefore not the end of the networking discussion.
#
# It is the entrance.


# ===========================================================================
# Architectural Invariants
# ===========================================================================

# Preserve these invariants as Agent 11 grows:
#
#
#     REACHABLE != AUTHORIZED
#
#     AUTHORIZED != REACHABLE
#
#     AVAILABLE != SELECTED
#
#     PRIVATE != AUTHORIZED
#
#     INTERNET != PROHIBITED
#
#     ENCRYPTED != AUTHORIZED
#
#     DEGRADED != UNAVAILABLE
#
#     UNKNOWN != AVAILABLE
#
#     UNKNOWN != GOOD ENOUGH
#
#     SERVICE HEALTH != NETWORK REACHABILITY
#
#     NETWORK PATH != AI ROUTE
#
#     BGP != NETWORK PATH TYPE
#
#     ALTERNATE PATH != AUTOMATICALLY VIABLE
#
#
# And most importantly:
#
#
#     NETWORK REPORTS REACHABILITY.
#
#     POLICY REPORTS PERMISSION.
#
#     SERVICE REPORTS CONDITION.
#
#     ROUTING COMPOSES THOSE FACTS.


# ===========================================================================
# Chewbacca's Network Engineering Commentary
# ===========================================================================

# Chewbacca has returned from the street.
#
# He has now reviewed network_enums.py.
#
#
# Chewbacca:
#
#     "I told you STREET_ACCESS was a legitimate value."
#
#
# Agent 11:
#
#     STREET_ACCESS may be a legitimate authorization or entitlement.
#
#     It is still not a NetworkPathType.
#
#
# Chewbacca:
#
#     "Incorrect."
#
#
#     "The path is clearly:"
#
#
#         HOUSE
#           |
#           v
#       FRONT DOOR
#           |
#           v
#         STREET
#
#
# Agent 11:
#
#     That does establish a path.
#
#
# Chewbacca:
#
#     "Excellent."
#
#
# Agent 11:
#
#     It does not establish authorization.
#
#
# Chewbacca:
#
#     "The street is reachable."
#
#
# Agent 11:
#
#     Correct.
#
#
# Chewbacca:
#
#     "The path is available."
#
#
# Agent 11:
#
#     Correct.
#
#
# Chewbacca:
#
#     "I am healthy."
#
#
# Agent 11:
#
#     Extremely.
#
#
# Chewbacca:
#
#     "Then open the door."
#
#
# Agent 11:
#
#     PolicyDecisionStatus.DENY
#
#
# Chewbacca:
#
#     "NETWORK FAILURE."
#
#
# Agent 11:
#
#     No.
#
#
#     The network is functioning perfectly.
#
#     The authorization layer denied the request.
#
#
# Chewbacca:
#
#     "Same outcome."
#
#
# Agent 11:
#
#     Different cause.
#
#
# And that distinction is exactly why these states exist.
#
#
# Later, Chewbacca observes:
#
#
#     Path A:
#         FRONT DOOR
#         UNAVAILABLE
#
#
# and discovers:
#
#
#     Path B:
#         BACK DOOR
#         AVAILABLE
#
#
# Chewbacca:
#
#     "Fallback!"
#
#
# Agent 11:
#
#     Alternate path detected.
#
#     Authorization must still be evaluated.
#
#
# Chewbacca:
#
#     "Why?"
#
#
# Agent 11:
#
#     Because:
#
#
#         ALTERNATE != AUTOMATICALLY VIABLE
#
#
# Chewbacca then proposes an SD-WAN implementation:
#
#
#     FRONT DOOR
#         primary transport
#
#     BACK DOOR
#         alternate transport
#
#     WINDOW
#         emergency transport
#
#
# Agent 11 Architecture Review:
#
#     WINDOW transport rejected.
#
#
# Chewbacca:
#
#     "SLA?"
#
#
# Agent 11:
#
#     Security policy.
#
#
# Final architectural ruling:
#
#
#     THE NETWORK TELLS AGENT 11
#     WHAT IT CAN REACH.
#
#
#     POLICY TELLS AGENT 11
#     WHAT IT MAY REACH.
#
#
#     ROUTING MAY SELECT ONLY FROM
#     WHAT REMAINS.
#
#
# Cisco Engineers:
#
#     In SEIR-II, we open the trapdoor.
