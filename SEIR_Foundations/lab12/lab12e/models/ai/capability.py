# ==========================================================================
# AGENT 11 — AI CAPABILITY MODEL
# ==========================================================================
#
# File:
#
#     agent11/models/ai/capability.py
#
#
# Purpose
# -------
#
# This module defines the domain contract used to describe an AI
# capability.
#
# An AI capability answers two primary questions:
#
#     1. WHAT kind of reasoning work can an AI resource perform?
#
#     2. AT WHAT reasoning levels can it perform that work?
#
#
# Example:
#
#     SECURITY_ANALYSIS
#     |
#     +-- STANDARD
#     |
#     +-- HEAVY
#
#
# This module deliberately does NOT answer:
#
#     - Which model should be selected?
#
#     - Which provider should be selected?
#
#     - Is the resource authorized to receive the data?
#
#     - Is the resource currently available?
#
#     - Can the resource be reached over the network?
#
#     - How much will the resource cost?
#
#     - Should Agent 11 route the request to the resource?
#
#
# Those questions belong to other Agent 11 domains.
#
#
# ==========================================================================
# ARCHITECTURAL BOUNDARY
# ==========================================================================
#
# Capability describes:
#
#     WHAT A RESOURCE CAN DO
#
#
# Capability does not describe:
#
#     WHETHER AGENT 11 MAY USE IT
#
#
# This distinction is foundational.
#
#
#     CAPABLE
#         !=
#     AUTHORIZED
#
#
#     CAPABLE
#         !=
#     AVAILABLE
#
#
#     CAPABLE
#         !=
#     REACHABLE
#
#
#     CAPABLE
#         !=
#     SELECTED
#
#
# A resource may be technically capable of performing a task while being:
#
#     - prohibited by policy,
#     - unavailable,
#     - unreachable,
#     - too expensive,
#     - or simply not selected by the router.
#
#
# Capability is therefore ONE INPUT into future routing decisions.
#
# It is not the routing decision itself.
#
#
# ==========================================================================
# MODELS ARE NOUNS
# ==========================================================================
#
# This file lives under:
#
#     models/ai/
#
#
# Therefore its responsibility is to represent a domain concept.
#
#
#     models/ai/capability.py
#             |
#             v
#     WHAT CAPABILITY MEANS
#
#
# Future components under:
#
#     routing/
#
#     models_runtime/
#
#     policy/
#
#     network/
#
#     orchestrators/
#
# will determine what Agent 11 DOES with capability information.
#
#
# Teaching principle:
#
#     MODELS ARE NOUNS.
#
#     BEHAVIOR LIVES ELSEWHERE.
#
#
# ==========================================================================


from pydantic import Field

from ..base_model import Agent11BaseModel
from ..enums.ai_enums import AICapabilityType, ReasoningLevel


# ==========================================================================
# AICapability
# ==========================================================================
#
# AICapability describes one reasoning capability supported by an AI
# resource.
#
#
# The model deliberately contains only three fields:
#
#
#     AICapability
#     |
#     +-- capability_type
#     |
#     +-- supported_reasoning_levels
#     |
#     +-- description
#
#
# Each field has one clear responsibility.
#
#
#     capability_type
#         |
#         +-- WHAT can the resource do?
#
#
#     supported_reasoning_levels
#         |
#         +-- At WHAT reasoning levels can it do that work?
#
#
#     description
#         |
#         +-- How can the capability be explained to a human?
#
#
# ==========================================================================


class AICapability(Agent11BaseModel):
    """
    Describes a reasoning capability supported by an AI resource.

    Capability describes what work a resource can perform and the
    reasoning levels at which that capability is supported.

    Capability does not establish authorization, availability,
    reachability, cost preference, or route selection.
    """

    # ----------------------------------------------------------------------
    # CAPABILITY TYPE
    # ----------------------------------------------------------------------
    #
    # capability_type identifies the kind of reasoning work represented
    # by this capability.
    #
    #
    # Examples may include:
    #
    #     SECURITY_ANALYSIS
    #
    #     CLASSIFICATION
    #
    #     SUMMARIZATION
    #
    #     CODE_REASONING
    #
    #     STRUCTURED_OUTPUT
    #
    #     TOOL_USE
    #
    #
    # The exact vocabulary is controlled by:
    #
    #     AICapabilityType
    #
    #
    # This is important because Agent 11 should reason about controlled
    # domain vocabulary rather than arbitrary strings.
    #
    #
    # Good:
    #
    #     AICapabilityType.SECURITY_ANALYSIS
    #
    #
    # Bad:
    #
    #     "security-ish stuff"
    #
    #
    # The capability type identifies WHAT the capability is.
    #
    # It does NOT identify:
    #
    #     - a model,
    #     - a provider,
    #     - a service,
    #     - a route,
    #     - or an endpoint.
    #
    #
    # Therefore:
    #
    #     CAPABILITY TYPE != MODEL
    #
    #     CAPABILITY TYPE != PROVIDER
    #
    #     CAPABILITY TYPE != SERVICE
    #
    #     CAPABILITY TYPE != ROUTE
    #
    # ----------------------------------------------------------------------

    capability_type: AICapabilityType = Field(
        description=(
            "The type of reasoning capability supported by the AI resource."
        ),
    )

    # ----------------------------------------------------------------------
    # SUPPORTED REASONING LEVELS
    # ----------------------------------------------------------------------
    #
    # supported_reasoning_levels identifies the reasoning levels at which
    # this particular capability can operate.
    #
    #
    # Example:
    #
    #     SECURITY_ANALYSIS
    #     |
    #     +-- LIGHT       X
    #     |
    #     +-- STANDARD    YES
    #     |
    #     +-- HEAVY       YES
    #
    #
    # represented as:
    #
    #     {
    #         ReasoningLevel.STANDARD,
    #         ReasoningLevel.HEAVY,
    #     }
    #
    #
    # A set is intentional.
    #
    # For supported reasoning levels:
    #
    #     membership matters,
    #
    #     ordering does not matter,
    #
    #     duplication does not matter.
    #
    #
    # These:
    #
    #     STANDARD, HEAVY
    #
    # and:
    #
    #     HEAVY, STANDARD
    #
    # describe the same supported set.
    #
    #
    # Likewise, claiming:
    #
    #     STANDARD
    #     STANDARD
    #     STANDARD
    #
    # does not create:
    #
    #     SUPER STANDARD
    #
    #
    # A set naturally represents the domain semantics.
    #
    #
    # min_length=1 is also deliberate.
    #
    # Agent 11 should not accept:
    #
    #     "I support SECURITY_ANALYSIS."
    #
    # followed by:
    #
    #     "At which reasoning levels?"
    #
    #     "None."
    #
    #
    # That would be a contradictory capability advertisement.
    #
    #
    # Therefore:
    #
    #     CAPABILITY ADVERTISED
    #             +
    #     AT LEAST ONE REASONING LEVEL
    #             =
    #     VALID CAPABILITY CONTRACT
    #
    #
    # while:
    #
    #     CAPABILITY ADVERTISED
    #             +
    #     ZERO REASONING LEVELS
    #             =
    #     INVALID CAPABILITY CONTRACT
    #
    #
    # IMPORTANT:
    #
    # Reasoning level remains a workload characteristic.
    #
    # It does not identify an implementation destination.
    #
    #
    #     HEAVY != COMPANY_ONPREM_LLM
    #
    #     STANDARD != COMPANY_CLOUD_LLM
    #
    #
    # Therefore:
    #
    #     REASONING LEVEL != MODEL
    #
    #     REASONING LEVEL != SERVICE
    #
    #     REASONING LEVEL != ROUTE
    #
    # ----------------------------------------------------------------------

    supported_reasoning_levels: set[ReasoningLevel] = Field(
        min_length=1,
        description=(
            "One or more reasoning levels supported for this capability."
        ),
    )

    # ----------------------------------------------------------------------
    # DESCRIPTION
    # ----------------------------------------------------------------------
    #
    # description provides optional human-readable documentation.
    #
    #
    # Example:
    #
    #     "Analyzes security evidence and produces reasoned findings."
    #
    #
    # The description is intentionally optional because capability_type
    # already provides the machine-readable identity of the capability.
    #
    #
    # Therefore:
    #
    #     capability_type
    #         |
    #         +-- MACHINE-READABLE SEMANTICS
    #
    #
    #     description
    #         |
    #         +-- HUMAN-READABLE EXPLANATION
    #
    #
    # Application logic should reason about:
    #
    #     capability.capability_type
    #
    #
    # It should NOT attempt to discover capability identity by parsing:
    #
    #     capability.description
    #
    #
    # Do NOT build:
    #
    #     if "security" in capability.description:
    #         ...
    #
    #
    # The description documents the capability.
    #
    # It does not define the capability.
    #
    #
    #     DESCRIPTION != CAPABILITY IDENTITY
    #
    # ----------------------------------------------------------------------

    description: str | None = Field(
        default=None,
        description=(
            "Optional human-readable description of the capability."
        ),
    )


# ==========================================================================
# EXAMPLE — SECURITY ANALYSIS CAPABILITY
# ==========================================================================
#
# A resource that supports STANDARD and HEAVY security analysis could
# advertise:
#
#
# security_analysis = AICapability(
#     capability_type=AICapabilityType.SECURITY_ANALYSIS,
#     supported_reasoning_levels={
#         ReasoningLevel.STANDARD,
#         ReasoningLevel.HEAVY,
#     },
#     description=(
#         "Analyzes security evidence and produces reasoned findings."
#     ),
# )
#
#
# Conceptually:
#
#
#     SECURITY_ANALYSIS
#     |
#     +-- LIGHT       X
#     |
#     +-- STANDARD    YES
#     |
#     +-- HEAVY       YES
#
#
# Notice what this object does NOT say.
#
# It does not say:
#
#     "Use the company on-premises LLM."
#
# It does not say:
#
#     "Use an external foundation model."
#
# It does not say:
#
#     "This capability is authorized for E8."
#
# It does not say:
#
#     "The service is currently healthy."
#
# It simply describes the capability.
#
#
# ==========================================================================
# EXAMPLE — DESCRIPTION IS OPTIONAL
# ==========================================================================
#
# This is also valid:
#
#
# classification = AICapability(
#     capability_type=AICapabilityType.CLASSIFICATION,
#     supported_reasoning_levels={
#         ReasoningLevel.LIGHT,
#         ReasoningLevel.STANDARD,
#     },
# )
#
#
# The controlled vocabulary already establishes:
#
#     CLASSIFICATION
#
#
# Therefore:
#
#
#     REQUIRED
#     |
#     +-- capability_type
#     |
#     +-- supported_reasoning_levels
#
#
#     OPTIONAL
#     |
#     +-- description
#
#
# ==========================================================================
# EXAMPLE — EMPTY REASONING LEVEL SET
# ==========================================================================
#
# This should fail validation:
#
#
# invalid_capability = AICapability(
#     capability_type=AICapabilityType.SECURITY_ANALYSIS,
#     supported_reasoning_levels=set(),
# )
#
#
# Because:
#
#
#     SECURITY_ANALYSIS
#             +
#     NO SUPPORTED REASONING LEVEL
#             =
#     INVALID CONTRACT
#
#
# Pydantic enforces this through:
#
#     min_length=1
#
#
# ==========================================================================
# PYDANTIC VALIDATION
# ==========================================================================
#
# Capability information may eventually arrive from:
#
#     - configuration,
#     - model registries,
#     - service registries,
#     - APIs,
#     - discovery systems,
#     - deployment metadata,
#     - or other platform components.
#
#
# External Python data can be validated using native Pydantic:
#
#
# payload = {
#     "capability_type": "security_analysis",
#     "supported_reasoning_levels": [
#         "standard",
#         "heavy",
#     ],
#     "description": (
#         "Analyzes security evidence and produces reasoned findings."
#     ),
# }
#
#
# capability = AICapability.model_validate(payload)
#
#
# Conceptually:
#
#
#     RAW DATA
#        |
#        v
#     AICapability.model_validate()
#        |
#        +-- capability enum validation
#        |
#        +-- reasoning-level enum validation
#        |
#        +-- set construction
#        |
#        +-- non-empty constraint
#        |
#        +-- extra-field validation
#        |
#        v
#     AICapability
#
#
# Again, Agent 11 deliberately uses native Pydantic APIs.
#
# We do not need to hide:
#
#     model_validate()
#
# behind unnecessary framework wrappers.
#
#
# ==========================================================================
# INVALID CAPABILITY TYPE
# ==========================================================================
#
# Consider:
#
#
# payload = {
#     "capability_type": "make_coffee",
#     "supported_reasoning_levels": [
#         "standard",
#     ],
# }
#
#
# capability = AICapability.model_validate(payload)
#
#
# Pydantic should reject the capability because:
#
#     make_coffee
#
# is not part of the controlled AICapabilityType vocabulary.
#
#
# Unless, of course, Agent 11 eventually adds:
#
#     AICapabilityType.MAKE_COFFEE
#
#
# At which point we probably need to have a larger architecture meeting.
#
#
# ==========================================================================
# INVALID REASONING LEVEL
# ==========================================================================
#
# Consider:
#
#
# payload = {
#     "capability_type": "security_analysis",
#     "supported_reasoning_levels": [
#         "standard",
#         "super_duper_heavy",
#     ],
# }
#
#
# capability = AICapability.model_validate(payload)
#
#
# Pydantic should reject:
#
#     super_duper_heavy
#
#
# Agent 11 currently recognizes:
#
#     LIGHT
#
#     STANDARD
#
#     HEAVY
#
#
# Controlled vocabulary prevents developers from gradually creating:
#
#     HEAVY
#
#     VERY_HEAVY
#
#     EXTRA_HEAVY
#
#     REALLY_HEAVY
#
#     SUPER_HEAVY
#
#     HEAVY_PLUS
#
#     HEAVY_PRO_MAX
#
#
# until nobody knows what the words mean anymore.
#
#
# ==========================================================================
# ARCHITECTURAL BOUNDARY ENFORCEMENT
# ==========================================================================
#
# Agent11BaseModel configures:
#
#     extra="forbid"
#
#
# This is useful for more than catching spelling mistakes.
#
# It can also expose architectural boundary violations.
#
#
# For example, someone may attempt:
#
#
# capability = AICapability(
#     capability_type=AICapabilityType.SECURITY_ANALYSIS,
#     supported_reasoning_levels={
#         ReasoningLevel.HEAVY,
#     },
#     authorized_for_e8=True,
# )
#
#
# Agent 11 should reject this.
#
#
# Why?
#
# Because:
#
#     authorized_for_e8
#
# is not capability information.
#
# Someone is trying to smuggle policy into the capability model.
#
#
# Likewise:
#
#
# capability = AICapability(
#     capability_type=AICapabilityType.SECURITY_ANALYSIS,
#     supported_reasoning_levels={
#         ReasoningLevel.HEAVY,
#     },
#     network_available=True,
# )
#
#
# should fail.
#
#
# Network availability belongs to the network domain.
#
#
# Likewise:
#
#
# capability = AICapability(
#     capability_type=AICapabilityType.SECURITY_ANALYSIS,
#     supported_reasoning_levels={
#         ReasoningLevel.HEAVY,
#     },
#     cost_per_million_tokens=0.42,
# )
#
#
# should fail.
#
#
# Cost belongs to economics / usage / routing concerns.
#
#
# These are not merely invalid fields.
#
# They represent invalid architectural responsibilities.
#
#
# ==========================================================================
# CAPABILITY IS NOT AVAILABILITY
# ==========================================================================
#
# This distinction deserves special attention.
#
#
# Imagine yesterday:
#
#
#     COMPANY ON-PREM AI SERVICE
#     |
#     +-- SECURITY_ANALYSIS
#     |       |
#     |       +-- STANDARD    YES
#     |       |
#     |       +-- HEAVY       YES
#     |
#     +-- SERVICE STATUS
#             |
#             +-- HEALTHY
#
#
# Today the GPU cluster catches fire.
#
#
#     COMPANY ON-PREM AI SERVICE
#     |
#     +-- SECURITY_ANALYSIS
#     |       |
#     |       +-- STANDARD    YES
#     |       |
#     |       +-- HEAVY       YES
#     |
#     +-- SERVICE STATUS
#             |
#             +-- UNAVAILABLE
#
#
# The resource did not suddenly forget how to perform security analysis.
#
# Its operational availability changed.
#
# Its capability did not.
#
#
# Therefore:
#
#
#     CAPABILITY
#         |
#         +-- relatively durable
#
#
#     AVAILABILITY
#         |
#         +-- operational state
#
#
# INVARIANT:
#
#     CAPABILITY != AVAILABILITY
#
#
# This distinction becomes especially important when Agent 11 later
# introduces:
#
#     service.py
#
# and runtime service-health information.
#
#
# ==========================================================================
# CAPABILITY IS NOT AUTHORIZATION
# ==========================================================================
#
# Imagine three reasoning resources:
#
#
#                         SECURITY_ANALYSIS / HEAVY
#
#     External FM                    YES
#
#     Company Cloud LLM              YES
#
#     Company On-Prem LLM            YES
#
#
# Capability has now answered:
#
#     "Which resources can technically perform the requested work?"
#
#
# It has NOT answered:
#
#     "Which resources are permitted to receive this request's data?"
#
#
# A future policy decision might produce:
#
#
#                         CAPABILITY       POLICY
#
#     External FM             YES            NO
#
#     Company Cloud LLM       YES            NO
#
#     Company On-Prem LLM     YES            YES
#
#
# Nothing about the capability objects needs to change.
#
#
# The resources remain technically capable.
#
# Policy independently determines which resources may be used.
#
#
# Therefore:
#
#     CAPABILITY != AUTHORIZATION
#
#
# ==========================================================================
# CAPABILITY DOES NOT CONTAIN BEHAVIOR
# ==========================================================================
#
# AICapability should not grow methods such as:
#
#
#     capability.matches(request)
#
#
#     capability.find_best_model()
#
#
#     capability.check_policy()
#
#
#     capability.route()
#
#
# Those operations represent behavior.
#
#
# Future behavior belongs in components such as:
#
#     routing/
#
#     models_runtime/
#
#     policy/
#
#     orchestrators/
#
#
# The model remains a noun.
#
#
#     models/ai/capability.py
#             |
#             v
#     WHAT CAPABILITY MEANS
#
#
#     routing/
#     models_runtime/
#     orchestrators/
#             |
#             v
#     WHAT AGENT 11 DOES WITH CAPABILITY
#
#
# Teaching principle:
#
#     MODELS ARE NOUNS.
#
#     BEHAVIOR LIVES ELSEWHERE.
#
#
# ==========================================================================
# PART I — RESPONSIBILITY MAP
# ==========================================================================
#
# AICapability OWNS:
#
#
#     AICapability
#     |
#     +-- capability identity
#     |
#     +-- supported reasoning levels
#     |
#     +-- optional human-readable explanation
#
#
# AICapability DOES NOT OWN:
#
#
#     - provider identity,
#
#     - model identity,
#
#     - service identity,
#
#     - endpoint information,
#
#     - data classification,
#
#     - authorization,
#
#     - policy decisions,
#
#     - service health,
#
#     - network availability,
#
#     - route selection,
#
#     - fallback,
#
#     - cost,
#
#     - latency,
#
#     - telemetry,
#
#     - execution,
#
#     - or orchestration.
#
#
# ==========================================================================
# PART I — FINAL INVARIANTS
# ==========================================================================
#
#     CAPABILITY TYPE
#         !=
#     MODEL
#
#
#     CAPABILITY TYPE
#         !=
#     PROVIDER
#
#
#     CAPABILITY TYPE
#         !=
#     SERVICE
#
#
#     REASONING LEVEL
#         !=
#     MODEL
#
#
#     REASONING LEVEL
#         !=
#     ROUTE
#
#
#     DESCRIPTION
#         !=
#     CAPABILITY IDENTITY
#
#
#     CAPABILITY
#         !=
#     AUTHORIZATION
#
#
#     CAPABILITY
#         !=
#     AVAILABILITY
#
#
#     CAPABILITY
#         !=
#     REACHABILITY
#
#
#     CAPABILITY
#         !=
#     COST
#
#
#     CAPABILITY
#         !=
#     ROUTE SELECTION
#
#
#     CAPABLE
#         !=
#     VIABLE
#
#
#     CAPABLE
#         !=
#     SELECTED
#
#
# ==========================================================================
# FINAL DEFINITION
# ==========================================================================
#
# AICapability answers:
#
#
#     WHAT CAN THIS RESOURCE DO?
#
#                 AND
#
#     AT WHAT REASONING LEVELS?
#
#
# It deliberately does NOT answer:
#
#
#     MAY WE USE IT?
#
#     IS IT WORKING?
#
#     CAN WE REACH IT?
#
#     HOW MUCH DOES IT COST?
#
#     SHOULD WE SELECT IT?
#
#
# Those questions belong to the larger Agent 11 architecture.
#
#
# ==========================================================================
# END PART I
# ==========================================================================


# ==========================================================================
# PART II — CAPABILITY INSIDE AGENT 11
# ==========================================================================
#
# Part I answered:
#
#     WHAT CAN THIS RESOURCE DO?
#
#                 AND
#
#     AT WHAT REASONING LEVELS?
#
#
# Part II asks:
#
#     HOW DOES AGENT 11 USE THAT INFORMATION?
#
#
# The basic relationship is:
#
#
#             AIRequest
#                 |
#                 | requires
#                 v
#            CAPABILITY
#                 ^
#                 | provides
#                 |
#           AI RESOURCE
#
#
# A request expresses requirements.
#
# A resource advertises capabilities.
#
# Agent 11 later compares the two.
#
#
# IMPORTANT:
#
# AICapability describes capability.
#
# It does NOT perform capability matching.
#
#
#     MODEL
#         |
#         +-- describes the fact
#
#
#     ROUTING / MATCHING
#         |
#         +-- acts upon the fact
#
#
# Teaching principle:
#
#     MODELS ARE NOUNS.
#
#     BEHAVIOR LIVES ELSEWHERE.
#
#
# ==========================================================================
# REQUIREMENT != OFFERING
# ==========================================================================
#
# There are two sides of capability matching.
#
#
#     REQUEST SIDE
#     ------------
#
#     "What capability do I NEED?"
#
#
#     RESOURCE SIDE
#     -------------
#
#     "What capabilities can I PROVIDE?"
#
#
# These are related concepts.
#
# They are not necessarily identical domain objects.
#
#
# A future AIRequest may contain something like:
#
#
#     required_capabilities: set[AICapabilityType]
#
#
# together with:
#
#
#     reasoning_level: ReasoningLevel
#
#
# Example:
#
#
#     REQUEST
#     |
#     +-- required capability
#     |       |
#     |       +-- SECURITY_ANALYSIS
#     |
#     +-- reasoning level
#             |
#             +-- HEAVY
#
#
# A resource may advertise the richer:
#
#
#     AICapability(
#         capability_type=AICapabilityType.SECURITY_ANALYSIS,
#         supported_reasoning_levels={
#             ReasoningLevel.STANDARD,
#             ReasoningLevel.HEAVY,
#         },
#     )
#
#
# Therefore:
#
#
#     REQUEST REQUIREMENT
#             !=
#     RESOURCE CAPABILITY ADVERTISEMENT
#
#
# SEIR-I may keep the request side deliberately simple.
#
# If requirements later become richer, Agent 11 can introduce a dedicated:
#
#
#     CapabilityRequirement
#
#
# model without changing what AICapability means.
#
#
# ==========================================================================
# CONCEPTUAL CAPABILITY MATCH
# ==========================================================================
#
# Suppose a request eventually declares:
#
#
#     required_capability =
#         AICapabilityType.SECURITY_ANALYSIS
#
#
#     required_reasoning_level =
#         ReasoningLevel.HEAVY
#
#
# And a resource advertises:
#
#
#     security_analysis = AICapability(
#         capability_type=AICapabilityType.SECURITY_ANALYSIS,
#         supported_reasoning_levels={
#             ReasoningLevel.STANDARD,
#             ReasoningLevel.HEAVY,
#         },
#     )
#
#
# Conceptually, matching asks:
#
#
#     Does capability_type match?
#
#
#         SECURITY_ANALYSIS == SECURITY_ANALYSIS
#
#                     YES
#
#
#     Is the required reasoning level supported?
#
#
#         HEAVY in {STANDARD, HEAVY}
#
#                     YES
#
#
# Therefore:
#
#
#                     CAPABLE
#
#
# IMPORTANT:
#
# This file does NOT implement that matching behavior.
#
# The example exists to explain how the domain contract will eventually
# be consumed.
#
#
# ==========================================================================
# CAPABILITY MISMATCH
# ==========================================================================
#
# Suppose the request requires:
#
#
#     SECURITY_ANALYSIS
#
#     HEAVY
#
#
# But a resource advertises:
#
#
#     security_analysis = AICapability(
#         capability_type=AICapabilityType.SECURITY_ANALYSIS,
#         supported_reasoning_levels={
#             ReasoningLevel.LIGHT,
#             ReasoningLevel.STANDARD,
#         },
#     )
#
#
# The capability type matches:
#
#
#     SECURITY_ANALYSIS == SECURITY_ANALYSIS
#
#                     YES
#
#
# But:
#
#
#     HEAVY in {LIGHT, STANDARD}
#
#                     NO
#
#
# Therefore:
#
#
#                 NOT CAPABLE
#
#
# Notice:
#
#     NOT CAPABLE
#
# does NOT mean:
#
#     POLICY DENIED
#
# or:
#
#     SERVICE FAILED
#
# or:
#
#     NETWORK UNAVAILABLE
#
#
# It means only:
#
#
#     THE RESOURCE DOES NOT SATISFY
#     THE REQUESTED CAPABILITY REQUIREMENT.
#
#
# ==========================================================================
# MULTIPLE RESOURCES MAY PROVIDE THE SAME CAPABILITY
# ==========================================================================
#
# Agent 11 may eventually have multiple reasoning destinations.
#
#
# Example:
#
#
#     EXTERNAL FM
#     |
#     +-- SECURITY_ANALYSIS
#             |
#             +-- LIGHT
#             +-- STANDARD
#             +-- HEAVY
#
#
#     COMPANY CLOUD LLM
#     |
#     +-- SECURITY_ANALYSIS
#             |
#             +-- LIGHT
#             +-- STANDARD
#
#
#     COMPANY ON-PREM LLM
#     |
#     +-- SECURITY_ANALYSIS
#             |
#             +-- STANDARD
#             +-- HEAVY
#
#
# Now consider:
#
#
#     REQUEST
#     |
#     +-- SECURITY_ANALYSIS
#     |
#     +-- HEAVY
#
#
# Capability evaluation produces:
#
#
#                         CAPABILITY MATCH
#
#     External FM               YES
#
#     Company Cloud LLM         NO
#
#     Company On-Prem LLM       YES
#
#
# At this point Agent 11 knows:
#
#
#     WHO CAN DO THE WORK?
#
#
# It still does NOT know:
#
#
#     WHO MAY RECEIVE THE DATA?
#
#     WHO IS HEALTHY?
#
#     WHO IS REACHABLE?
#
#     WHO SHOULD BE SELECTED?
#
#
# ==========================================================================
# CAPABILITY != POLICY
# ==========================================================================
#
# Continue the previous example.
#
#
# Request:
#
#
#     SECURITY_ANALYSIS
#
#     HEAVY
#
#
# Suppose the request contains highly restricted data.
#
#
# Capability evaluation:
#
#
#                         CAPABILITY
#
#     External FM             YES
#
#     Company Cloud LLM       NO
#
#     Company On-Prem LLM     YES
#
#
# Policy evaluation might independently produce:
#
#
#                         CAPABILITY       POLICY
#
#     External FM             YES            NO
#
#     Company Cloud LLM       NO             NO
#
#     Company On-Prem LLM     YES            YES
#
#
# Only the company on-premises resource survives both gates.
#
#
# This is why AICapability does not contain fields such as:
#
#
#     authorized_for_e8
#
#     allowed_for_confidential
#
#     company_data_only
#
#
# Classification and policy taxonomies differ between organizations.
#
# Capability should not need to understand them.
#
#
# INVARIANT:
#
#
#     CAPABLE != AUTHORIZED
#
#
# A resource can be completely capable of performing work that it is
# completely prohibited from receiving.
#
#
# ==========================================================================
# CAPABILITY != AVAILABILITY
# ==========================================================================
#
# Suppose:
#
#
#     COMPANY ON-PREM LLM
#     |
#     +-- SECURITY_ANALYSIS / HEAVY
#     |
#     +-- SERVICE STATUS = UNAVAILABLE
#
#
# Capability:
#
#
#     YES
#
#
# Availability:
#
#
#     NO
#
#
# Therefore the resource remains capable but cannot currently service
# the request.
#
#
# This distinction matters because:
#
#
#     CAPABILITY
#         |
#         +-- relatively durable resource characteristic
#
#
#     AVAILABILITY
#         |
#         +-- changing operational state
#
#
# A GPU failure should not rewrite the resource's capability catalog.
#
#
#     CAPABLE != AVAILABLE
#
#
# ==========================================================================
# CAPABILITY != REACHABILITY
# ==========================================================================
#
# Suppose:
#
#
#     COMPANY ON-PREM LLM
#
#     SECURITY_ANALYSIS / HEAVY
#         |
#         +-- CAPABLE
#
#
#     POLICY
#         |
#         +-- ALLOWED
#
#
#     SERVICE
#         |
#         +-- HEALTHY
#
#
#     NETWORK
#         |
#         +-- UNAVAILABLE
#
#
# Perhaps:
#
#     - the private link is unavailable,
#
#     - an SD-WAN path is down,
#
#     - a BGP route has been withdrawn,
#
#     - the destination prefix is unreachable,
#
#     - or a data-center path has failed.
#
#
# The resource remains capable.
#
# Agent 11 simply cannot establish a viable route to it.
#
#
#     CAPABLE != REACHABLE
#
#
# Network reachability does not alter capability semantics.
#
#
# ==========================================================================
# CAPABILITY IS ONE VIABILITY GATE
# ==========================================================================
#
# Agent 11's broader route-viability model is:
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
# Capability owns exactly one part of that equation.
#
#
# Conceptually:
#
#
#                         VIABLE ROUTE
#                              |
#              +---------------+---------------+
#              |               |               |
#              v               v               v
#           POLICY         CAPABILITY       SERVICE
#          PERMITTED         MATCH         AVAILABLE
#                                              |
#                                              v
#                                        PATH AVAILABLE
#
#
# Another way to visualize the decision is:
#
#
#     CANDIDATE
#         |
#         v
#     POLICY PERMITTED?
#         |
#        YES
#         |
#         v
#     CAPABILITY MATCH?
#         |
#        YES
#         |
#         v
#     SERVICE AVAILABLE?
#         |
#        YES
#         |
#         v
#     PATH AVAILABLE?
#         |
#        YES
#         |
#         v
#     VIABLE CANDIDATE
#
#
# IMPORTANT:
#
# The actual implementation does not necessarily need to evaluate these
# conditions in this exact order.
#
# An orchestrator or router may order checks differently for:
#
#     - efficiency,
#
#     - cost,
#
#     - caching,
#
#     - security,
#
#     - or operational reasons.
#
#
# The architecture requires only that ALL required conditions ultimately
# be satisfied before the route is considered viable.
#
#
# Therefore:
#
#
#     CAPABLE != VIABLE
#
#
# ==========================================================================
# CAPABLE != VIABLE != SELECTED
# ==========================================================================
#
# Suppose two resources survive every viability gate:
#
#
#                         POLICY  CAPABLE  HEALTHY  PATH
#
#     External FM           YES      YES      YES    YES
#
#     Company On-Prem       YES      YES      YES    YES
#
#
# Both resources are viable.
#
#
# Agent 11 still needs routing logic to choose between them.
#
#
# Future routing considerations might include:
#
#
#     - organizational preference,
#
#     - user restrictions,
#
#     - reasoning requirements,
#
#     - latency,
#
#     - cost,
#
#     - capacity,
#
#     - locality,
#
#     - model quality,
#
#     - data residency,
#
#     - or other policy-safe objectives.
#
#
# Therefore:
#
#
#     CAPABLE
#         !=
#     VIABLE
#
#
#     VIABLE
#         !=
#     SELECTED
#
#
# Capability does not select routes.
#
#
# ==========================================================================
# CAPABILITY IS NOT A ROUTING SCORE
# ==========================================================================
#
# Avoid turning AICapability into something like:
#
#
#     capability_score = 0.97
#
#
# followed by:
#
#
#     highest capability score wins
#
#
# That would collapse several different architectural questions into one
# unexplained number.
#
#
# What does:
#
#
#     0.97
#
#
# actually mean?
#
#
#     - task support?
#
#     - model quality?
#
#     - benchmark performance?
#
#     - confidence?
#
#     - latency?
#
#     - availability?
#
#     - policy preference?
#
#
# Those concepts are not interchangeable.
#
#
# Capability should first answer a clean semantic question:
#
#
#     CAN THIS RESOURCE SATISFY
#     THE REQUIRED CAPABILITY?
#
#
# Quality and preference may later be modeled independently.
#
#
# Teaching principle:
#
#
#     DO NOT COMPRESS
#     DIFFERENT ARCHITECTURAL DIMENSIONS
#     INTO A MYSTERY NUMBER.
#
#
# ==========================================================================
# MULTIPLE CAPABILITY REQUIREMENTS
# ==========================================================================
#
# A future request may require more than one capability.
#
#
# Example:
#
#
#     REQUEST
#     |
#     +-- SECURITY_ANALYSIS
#     |
#     +-- STRUCTURED_OUTPUT
#     |
#     +-- TOOL_USE
#     |
#     +-- HEAVY reasoning
#
#
# A candidate may therefore need to satisfy a capability set rather than
# a single capability.
#
#
# Conceptually:
#
#
#     REQUIRED
#
#         {A, B, C}
#
#
#     PROVIDED
#
#         {A, B, C, D, E}
#
#
#     REQUIRED subset-of PROVIDED
#
#                     YES
#
#
# But capability requirements may eventually become richer than simple
# set membership.
#
#
# For that reason, matching behavior does not belong in AICapability.
#
#
# ==========================================================================
# REASONING SUPPORT MAY DIFFER BY CAPABILITY
# ==========================================================================
#
# A single AI resource does not necessarily support every capability at
# the same reasoning level.
#
#
# Example:
#
#
#     AI RESOURCE
#     |
#     +-- SUMMARIZATION
#     |       |
#     |       +-- LIGHT
#     |       +-- STANDARD
#     |       +-- HEAVY
#     |
#     +-- SECURITY_ANALYSIS
#     |       |
#     |       +-- LIGHT
#     |       +-- STANDARD
#     |
#     +-- CODE_REASONING
#             |
#             +-- STANDARD
#             +-- HEAVY
#
#
# Therefore it would be less precise to place one global:
#
#
#     supported_reasoning_levels
#
#
# on the entire AI resource.
#
#
# Reasoning support belongs with the particular capability being
# advertised.
#
#
# ==========================================================================
# FUTURE MODEL / SERVICE REGISTRY RELATIONSHIP
# ==========================================================================
#
# A future AI resource may advertise multiple AICapability objects.
#
#
#     AIModel / AIService
#     |
#     +-- identity
#     |
#     +-- characteristics
#     |
#     +-- capabilities
#             |
#             +-- AICapability
#             |
#             +-- AICapability
#             |
#             +-- AICapability
#
#
# Example:
#
#
#     Company Reasoning Model
#     |
#     +-- SECURITY_ANALYSIS
#     |       |
#     |       +-- STANDARD
#     |       +-- HEAVY
#     |
#     +-- CLASSIFICATION
#     |       |
#     |       +-- LIGHT
#     |       +-- STANDARD
#     |
#     +-- CODE_REASONING
#             |
#             +-- STANDARD
#             +-- HEAVY
#
#
# Later:
#
#
#     models_runtime/registry.py
#
#
# can maintain information about which deployed resources expose these
# capabilities.
#
#
# IMPORTANT:
#
# AICapability itself does not discover resources.
#
#
# ==========================================================================
# SEIR-II EXPANSION MARKER — DO NOT DELETE
# ==========================================================================
#
# The following comments are intentionally retained in the SEIR-I source.
#
# They are architectural bookmarks for SEIR-II.
#
#
# SEIR-I deliberately keeps AICapability small:
#
#
#     AICapability
#     |
#     +-- capability_type
#     |
#     +-- supported_reasoning_levels
#     |
#     +-- description
#
#
# This is intentional.
#
#
# DO NOT expand the SEIR-I model merely because the following concepts
# will eventually matter.
#
#
# SEIR-II should revisit capability modeling as the AI platform expands.
#
#
# Possible future capability dimensions:
#
#
#     CAPABILITY ECOSYSTEM
#     |
#     +-- TASK / REASONING CAPABILITIES
#     |       |
#     |       +-- summarization
#     |       +-- classification
#     |       +-- security analysis
#     |       +-- code reasoning
#     |       +-- planning
#     |       +-- extraction
#     |       +-- evaluation
#     |       +-- translation
#     |
#     +-- MODALITIES
#     |       |
#     |       +-- text
#     |       +-- image / vision
#     |       +-- audio
#     |       +-- video
#     |       +-- multimodal
#     |
#     +-- MODEL / SERVICE FEATURES
#     |       |
#     |       +-- structured output
#     |       +-- tool use
#     |       +-- streaming
#     |       +-- embeddings
#     |       +-- reranking
#     |       +-- function calling
#     |       +-- long-context processing
#     |
#     +-- EXECUTION CONSTRAINTS
#     |       |
#     |       +-- context-window limits
#     |       +-- input limits
#     |       +-- output limits
#     |       +-- concurrency
#     |       +-- batching support
#     |       +-- accelerator requirements
#     |
#     +-- SPECIALIZATION
#             |
#             +-- security
#             +-- code
#             +-- legal
#             +-- finance
#             +-- organizational knowledge
#
#
# IMPORTANT DESIGN WARNING:
#
# These are NOT necessarily one giant future enum.
#
#
# SEIR-II should evaluate whether they belong in separate typed domains:
#
#
#     CapabilityType
#
#     Modality
#
#     ModelFeature
#
#     ExecutionConstraint
#
#     Specialization
#
#
# Do NOT create:
#
#
#     GiantEverythingTheModelCanPossiblyDoEnum
#
#
# simply because all of these concepts relate to AI resources.
#
#
# The dimensions are different.
#
#
#     TASK CAPABILITY != MODALITY
#
#     MODALITY != FEATURE
#
#     FEATURE != EXECUTION CONSTRAINT
#
#     SPECIALIZATION != AUTHORIZATION
#
#
# SEIR-II should preserve those distinctions.
#
#
# ==========================================================================
# SEIR-II EXPANSION — CAPABILITY REQUIREMENTS
# ==========================================================================
#
# SEIR-I may begin with:
#
#
#     required_capabilities: set[AICapabilityType]
#
#
# But future requests may need richer requirements.
#
#
# Possible SEIR-II concept:
#
#
#     CapabilityRequirement
#     |
#     +-- capability_type
#     |
#     +-- minimum_reasoning_level
#     |
#     +-- required_features
#     |
#     +-- required_modalities
#     |
#     +-- constraints
#
#
# Example:
#
#
#     "I need security analysis,
#      at HEAVY reasoning,
#      with structured output,
#      over text and image evidence."
#
#
# That requirement is richer than:
#
#
#     SECURITY_ANALYSIS
#
#
# IMPORTANT:
#
# Do not implement CapabilityRequirement in SEIR-I merely because this
# future requirement is visible.
#
# This comment is an architectural bookmark.
#
#
# ==========================================================================
# SEIR-II EXPANSION — CAPABILITY DISCOVERY
# ==========================================================================
#
# SEIR-I may configure capabilities explicitly.
#
#
# SEIR-II may discover capability information from:
#
#
#     - model registries,
#
#     - inference servers,
#
#     - MCP-connected systems,
#
#     - cloud provider APIs,
#
#     - deployment manifests,
#
#     - Kubernetes resources,
#
#     - model metadata,
#
#     - benchmark systems,
#
#     - internal service catalogs,
#
#     - or AI platform control-plane APIs.
#
#
# Possible future flow:
#
#
#     AI RESOURCE
#         |
#         v
#     CAPABILITY DISCOVERY
#         |
#         v
#     NORMALIZATION
#         |
#         v
#     AICapability / FUTURE CAPABILITY CONTRACTS
#         |
#         v
#     MODEL REGISTRY
#
#
# Discovery is behavior.
#
#
# Therefore:
#
#
#     capability.py
#
#
# should NOT become a discovery client.
#
#
# ==========================================================================
# SEIR-II EXPANSION — ADVERTISED VS VERIFIED CAPABILITY
# ==========================================================================
#
# A future AI platform may need to distinguish:
#
#
#     ADVERTISED CAPABILITY
#
# from:
#
#     VERIFIED CAPABILITY
#
#
# A provider or model registry may claim:
#
#
#     SECURITY_ANALYSIS / HEAVY
#
#
# But organizational evaluation may determine:
#
#
#     SECURITY_ANALYSIS / STANDARD
#
#
# is the highest level approved by internal testing.
#
#
# Future architecture may therefore consider:
#
#
#     RESOURCE CLAIM
#         |
#         v
#     CAPABILITY EVALUATION
#         |
#         v
#     VERIFIED CAPABILITY
#         |
#         v
#     ORGANIZATIONAL REGISTRY
#
#
# This becomes especially important when:
#
#
#     - hosting open models,
#
#     - comparing model versions,
#
#     - quantizing models,
#
#     - fine-tuning models,
#
#     - changing inference runtimes,
#
#     - or deploying models onto different hardware.
#
#
# IMPORTANT:
#
#
#     ADVERTISED != VERIFIED
#
#
# and:
#
#
#     CAPABLE != APPROVED
#
#
# SEIR-II should revisit provenance and verification of capability claims.
#
#
# ==========================================================================
# SEIR-II EXPANSION — MODEL CAPABILITY VS DEPLOYED CAPABILITY
# ==========================================================================
#
# Future Agent 11 architecture may need to distinguish:
#
#
#     MODEL CAPABILITY
#
# from:
#
#     DEPLOYED SERVICE CAPABILITY
#
#
# A model may theoretically support:
#
#
#     128K context
#
#
# while a particular inference deployment is configured for:
#
#
#     32K context
#
#
# A model may support:
#
#
#     TOOL_USE
#
#
# while a particular service deployment intentionally disables tools.
#
#
# A model may support:
#
#
#     HEAVY reasoning
#
#
# while a resource-constrained deployment is approved only for:
#
#
#     STANDARD
#
#
# Therefore future architecture may distinguish:
#
#
#     MODEL
#       |
#       +-- inherent / evaluated capability
#
#
#     DEPLOYED SERVICE
#       |
#       +-- capability actually exposed by this deployment
#
#
# This distinction should be revisited when:
#
#
#     model.py
#
#     service.py
#
# and:
#
#     models_runtime/
#
#
# become richer.
#
#
# ==========================================================================
# SEIR-II EXPANSION — CAPABILITY VERSIONING
# ==========================================================================
#
# Capabilities may eventually need provenance and version context.
#
#
# Example:
#
#
#     Model Version 1
#         |
#         +-- SECURITY_ANALYSIS
#                 |
#                 +-- STANDARD
#
#
#     Model Version 2
#         |
#         +-- SECURITY_ANALYSIS
#                 |
#                 +-- STANDARD
#                 +-- HEAVY
#
#
# Or:
#
#
#     Model Version 3
#         |
#         +-- SECURITY_ANALYSIS
#                 |
#                 +-- STANDARD
#
#
# because evaluation found a regression.
#
#
# Therefore future capability records may need association with:
#
#
#     - model version,
#
#     - deployment version,
#
#     - evaluation version,
#
#     - benchmark version,
#
#     - validation date,
#
#     - or approval provenance.
#
#
# Do NOT add those fields to the SEIR-I AICapability merely because they
# may eventually matter.
#
#
# SEIR-II should determine which neighboring model owns that provenance.
#
#
# ==========================================================================
# SEIR-II EXPANSION — CAPABILITY EVALUATION
# ==========================================================================
#
# SEIR-II should eventually consider how capability claims are tested.
#
#
# A capability should not necessarily become trusted merely because:
#
#
#     - a vendor says it exists,
#
#     - a model card says it exists,
#
#     - an API advertises it,
#
#     - or a deployment manifest declares it.
#
#
# A future enterprise AI platform may evaluate capabilities against
# organizational test suites.
#
#
# Conceptually:
#
#
#     MODEL / SERVICE
#          |
#          v
#     CLAIMED CAPABILITY
#          |
#          v
#     ORGANIZATIONAL EVALUATION
#          |
#          +-- task tests
#          |
#          +-- quality tests
#          |
#          +-- security tests
#          |
#          +-- reliability tests
#          |
#          +-- structured-output tests
#          |
#          +-- domain-specific benchmarks
#          |
#          v
#     VERIFIED CAPABILITY
#
#
# This creates an important future distinction:
#
#
#     "The model claims it can do this."
#
#                     !=
#
#     "Our organization has verified that this deployment
#      can do this to an acceptable standard."
#
#
# ==========================================================================
# SEIR-II EXPANSION — CAPABILITY AND AI PLATFORM ENGINEERING
# ==========================================================================
#
# Capability becomes increasingly important as the organization moves
# from consuming managed AI toward operating its own AI platform.
#
#
# A simplified progression:
#
#
#     CONSUME INTELLIGENCE
#             |
#             v
#     Managed models / managed AI
#
#
#             |
#             v
#
#
#     HOST INTELLIGENCE
#             |
#             v
#     Model and inference platform
#
#
#             |
#             v
#
#
#     BUILD INTELLIGENCE
#             |
#             v
#     ML platform / proprietary models
#
#
#             |
#             v
#
#
#     OWN THE COMPUTE
#             |
#             v
#     AI infrastructure / GPU platform
#
#
# At each stage the meaning of:
#
#
#     "What can this AI resource actually do?"
#
#
# becomes more important.
#
#
# When the organization hosts models itself, capability may depend on:
#
#
#     - model architecture,
#
#     - model version,
#
#     - quantization,
#
#     - fine-tuning,
#
#     - inference runtime,
#
#     - context configuration,
#
#     - accelerator resources,
#
#     - deployment configuration,
#
#     - and organizational evaluation.
#
#
# SEIR-II should revisit capability modeling in that larger platform
# engineering context.
#
#
# ==========================================================================
# WHY WE ARE NOT IMPLEMENTING ALL OF THAT NOW
# ==========================================================================
#
# After reading the SEIR-II expansion notes, it may be tempting to turn:
#
#
#     AICapability
#
#
# into:
#
#
#     AICapability
#     |
#     +-- capability
#     +-- reasoning
#     +-- modality
#     +-- context window
#     +-- tool support
#     +-- streaming
#     +-- embeddings
#     +-- hardware
#     +-- benchmarks
#     +-- provider
#     +-- deployment
#     +-- cost
#     +-- authorization
#     +-- networking
#     +-- health
#     +-- weather
#     +-- current moon phase
#     +-- Chewbacca's street-access status
#
#
# Do not.
#
#
# SEIR-I needs one clean answer:
#
#
#     WHAT CAN THIS RESOURCE DO?
#
#                 AND
#
#     AT WHAT REASONING LEVELS?
#
#
# Everything else should be introduced when the architecture actually
# needs it and when ownership can be assigned correctly.
#
#
# Teaching principle:
#
#
#     FUTURE-AWARE
#         !=
#     FUTURE-BLOATED
#
#
# ==========================================================================
# CHEWBACCA'S CAPABILITY REVIEW
# ==========================================================================
#
# Chewbacca registers:
#
#
#     capability_type:
#         SECURITY_ANALYSIS
#
#
#     supported_reasoning_levels:
#         HEAVY
#
#
# Agent 11:
#
#     CAPABILITY ACCEPTED.
#
#
# Chewbacca:
#
#     "Excellent. I can access E8."
#
#
# Agent 11:
#
#     NO.
#
#
# Chewbacca:
#
#     "But you just said I'm capable."
#
#
# Agent 11:
#
#     CORRECT.
#
#
# Chewbacca:
#
#     "Therefore I'm authorized."
#
#
# Agent 11:
#
#     INCORRECT.
#
#
# Chewbacca:
#
#     "What if I'm healthy?"
#
#
# Agent 11:
#
#     STILL INCORRECT.
#
#
# Chewbacca:
#
#     "What if BGP can reach me?"
#
#
# Agent 11:
#
#     IMPRESSIVELY STILL INCORRECT.
#
#
# Chewbacca:
#
#     "What if I'm cheaper?"
#
#
# Agent 11:
#
#     ALSO IRRELEVANT TO AUTHORIZATION.
#
#
# Chewbacca:
#
#     "What if I have STREET_ACCESS?"
#
#
# Agent 11:
#
#     LEGITIMATE VOCABULARY.
#
#     WRONG MODEL.
#
#
# Chewbacca:
#
#     "I would like to speak to the orchestrator."
#
#
# Agent 11:
#
#     THE ORCHESTRATOR CANNOT OVERRIDE POLICY EITHER.
#
#
# ==========================================================================
# PART II — RESPONSIBILITY MAP
# ==========================================================================
#
# CAPABILITY answers:
#
#
#     CAN THIS RESOURCE PERFORM
#     THE REQUIRED KIND OF WORK?
#
#
# POLICY answers:
#
#
#     MAY THIS REQUEST'S DATA
#     BE SENT TO THIS RESOURCE?
#
#
# SERVICE STATE answers:
#
#
#     CAN THIS RESOURCE PERFORM
#     THE WORK RIGHT NOW?
#
#
# NETWORK answers:
#
#
#     CAN AGENT 11 REACH
#     THIS RESOURCE RIGHT NOW?
#
#
# ROUTING answers:
#
#
#     WHICH VIABLE RESOURCE
#     SHOULD BE SELECTED?
#
#
# These questions cooperate.
#
# They must not be collapsed into one another.
#
#
# ==========================================================================
# PART II — FINAL INVARIANTS
# ==========================================================================
#
#     REQUIREMENT
#         !=
#     OFFERING
#
#
#     CAPABILITY
#         !=
#     POLICY
#
#
#     CAPABILITY
#         !=
#     AVAILABILITY
#
#
#     CAPABILITY
#         !=
#     REACHABILITY
#
#
#     CAPABILITY
#         !=
#     COST
#
#
#     CAPABILITY
#         !=
#     QUALITY SCORE
#
#
#     CAPABILITY
#         !=
#     ROUTING DECISION
#
#
#     CAPABLE
#         !=
#     AUTHORIZED
#
#
#     CAPABLE
#         !=
#     AVAILABLE
#
#
#     CAPABLE
#         !=
#     REACHABLE
#
#
#     CAPABLE
#         !=
#     VIABLE
#
#
#     VIABLE
#         !=
#     SELECTED
#
#
#     ADVERTISED
#         !=
#     VERIFIED
#
#
#     MODEL CAPABILITY
#         !=
#     DEPLOYED SERVICE CAPABILITY
#
#
#     FUTURE-AWARE
#         !=
#     FUTURE-BLOATED
#
#
# ==========================================================================
# FINAL CAPABILITY PIPELINE
# ==========================================================================
#
# The capability domain occupies one precise location inside Agent 11:
#
#
#                         AIRequest
#                             |
#                             v
#                    REQUEST REQUIREMENTS
#                             |
#                             v
#                    CAPABILITY MATCHING
#                             |
#                  +----------+----------+
#                  |                     |
#                  v                     v
#             NOT CAPABLE             CAPABLE
#                                        |
#                                        v
#                                     POLICY
#                                        |
#                                        v
#                                  SERVICE STATE
#                                        |
#                                        v
#                                  NETWORK STATE
#                                        |
#                                        v
#                                     ROUTING
#                                        |
#                                        v
#                                    SELECTED
#
#
# Capability does not own this entire pipeline.
#
# Capability provides one of the facts the pipeline needs.
#
#
# In SEIR-I:
#
#
#     "Can it do the work?"
#
#
# In SEIR-II, this may expand toward:
#
#
#     "What exactly can it do,
#
#      through which deployment,
#
#      under which execution constraints,
#
#      according to whose claim,
#
#      verified by which evaluation,
#
#      for which model and deployment version?"
#
#
# But even then:
#
#
#     CAPABILITY
#         !=
#     AUTHORIZATION
#
#
# and:
#
#
#     CAPABILITY
#         !=
#     ROUTING
#
#
# remain true.
#
#
# ==========================================================================
# END PART II
# ==========================================================================
