SEIR-II
AI REASONING NETWORK
│
├── Multiple Company LLMs
├── Multiple FMs
├── SaaS AI
├── MCP federation
├── AgentCore
│
├── BGP
│   ├── route advertisements
│   ├── preferred paths
│   ├── failover
│   └── multiple DCs
│
├── SD-WAN
│   ├── application-aware routing
│   ├── path health
│   ├── latency
│   └── transport selection
│
├── AI Policy
│   ├── classification
│   ├── residency
│   ├── user restriction
│   ├── provider authorization
│   └── reasoning tier
│
└── Economics
    ├── tokens
    ├── GPU capacity
    ├── cloud inference cost
    └── latency




Now SEIR 1 

Agent 11 Foundation
│
├── AIOrchestrator
├── DataPolicyGate
├── ProhibitedData
├── RoutingPolicy
├── RoutingDecision
├── ModelRegistry
│
├── Routes
│   ├── EXTERNAL_FM
│   ├── COMPANY_CLOUD_LLM
│   └── COMPANY_ONPREM_LLM
│
├── MCP Service
│
└── Network Context
    ├── endpoint
    ├── region/site
    ├── reachable
    ├── health
    └── network_path


  Scenario 

  Dallas LLM capacity = 96%

Chicago latency = 41 ms

AWS FM = healthy

E7 request = 3,000 tokens

E8 request = 70,000 tokens

Tokyo SD-WAN path = degraded

Company Cloud LLM = healthy

Dallas BGP route withdrawn

What you knew                    What AI infrastructure needs

BGP                  ─────────▶  AI endpoint reachability
SD-WAN               ─────────▶  reasoning-path optimization
Segmentation         ─────────▶  AI trust zones
DLP                  ─────────▶  inference data controls
AAA                  ─────────▶  agent/tool authority
QoS                  ─────────▶  inference service objectives
HA                   ─────────▶  model redundancy
DR                   ─────────▶  reasoning continuity
Observability        ─────────▶  inference-path telemetry

Cisco map

SEIR-I
Cisco / AI Infrastructure Foundation
        │
        ├── VLANs / segmentation
        ├── ACLs
        ├── BGP fundamentals
        ├── redundant paths
        └── Company DC ↔ Cloud
                    │
                    ▼
              Agent 11
           AI Routing Plane


SEIR-1 Problems

Student:
"Why did you make us learn BGP?"

Several modules later...

E8 Request
    │
    ▼
AI Policy Gate
    │
    ▼
ON-PREM ONLY
    │
    ▼
Which DC?
    │
    ▼
BGP + SD-WAN
    │
    ▼
Local LLM

Student:
"........oh."


SEIR 1 massive problems


PRIMARY DC LLM DOWN

E7
Company Cloud allowed
On-Prem allowed
External FM prohibited

E8
On-Prem only

BGP withdraws DC-A route.

SD-WAN prefers DC-B.

DC-B GPU utilization = 94%.

Company Cloud LLM healthy.

External FM healthy.

AgentCore healthy.

MCP healthy.


QUESTION:

Where does E7 go?

Where does E8 go?

What happens if DC-B reaches capacity?

What traffic MUST NOT fail over?

What gets queued?

What gets rejected?

What gets logged?

Who gets alerted?





  
