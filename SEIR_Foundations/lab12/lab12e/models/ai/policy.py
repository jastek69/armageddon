# ==========================================================================
# PART I — DATA ROUTE POLICY
# ==========================================================================
#
# DataRoutePolicy describes configured data-routing policy.
#
# It answers:
#
#
#     "FOR THIS DATA CLASSIFICATION,
#      WHAT DOES POLICY SAY ABOUT THIS ROUTING DOMAIN?"
#
#
# Example:
#
#
#     E8
#      |
#      +--> EXTERNAL_FM
#      |        DENY
#      |
#      +--> COMPANY_CLOUD_LLM
#      |        DENY
#      |
#      +--> COMPANY_ONPREM_LLM
#               ALLOW
#
#
# DataRoutePolicy is POLICY CONFIGURATION.
#
# It is NOT the result of evaluating a particular AIRequest.
#
#
#     POLICY CONFIGURATION != POLICY EVALUATION
#
#
# Part II introduces PolicyDecision, which represents the result of
# evaluating policy for a request.
#
# ==========================================================================


# ==========================================================================
# IMPORTS
# ==========================================================================
#
# Keep policy.py dependent on Agent 11 domain contracts.
#
# Do not import:
#
#     cloud SDKs
#     model-provider SDKs
#     policy-engine SDKs
#     routing implementations
#     network implementations
#
#
# models/ai/policy.py describes policy domain objects.
#
# It does not implement the policy engine.
# ==========================================================================

from pydantic import Field

from ..base_model import Agent11BaseModel
from ..enums.policy_enums import (
    DataClassificationLevel,
    DataRoutePolicyEffect,
)
from ..enums.routing_enums import AIRoute


# ==========================================================================
# NOTE ABOUT DataRoutePolicyEffect
# ==========================================================================
#
# DataRoutePolicyEffect belongs in:
#
#
#     models/enums/policy_enums.py
#
#
# Its intended SEIR-I definition is:
#
#
#     class DataRoutePolicyEffect(Agent11Enum):
#         ALLOW = "allow"
#         DENY = "deny"
#
#
# DataRoutePolicyEffect describes CONFIGURED POLICY.
#
# It intentionally does not contain:
#
#
#     RESTRICT
#     INDETERMINATE
#
#
# Those concepts belong to policy EVALUATION and are represented by
# PolicyDecisionStatus in Part II.
#
#
# Why make this distinction?
#
#
#     CONFIGURED POLICY
#
#         E8 + EXTERNAL_FM = DENY
#
#
# is different from:
#
#
#     POLICY EVALUATION
#
#         request abc
#         +
#         EXTERNAL_FM
#         =
#         INDETERMINATE
#
#
# An organization may deliberately configure:
#
#
#     ALLOW
#
# or:
#
#     DENY
#
#
# But INDETERMINATE means Agent 11 could not establish a definitive
# authorization result during evaluation.
#
#
# That is an observed evaluation outcome.
#
# It is not deliberate policy configuration.
#
#
#     POLICY EFFECT != POLICY DECISION STATUS
#
#
#     CONFIGURATION SHOULD NOT INTENTIONALLY
#     CONFIGURE UNCERTAINTY
#
# ==========================================================================


# ==========================================================================
# DataRoutePolicy
# ==========================================================================
#
# DataRoutePolicy represents ONE configured relationship between:
#
#
#     DATA CLASSIFICATION
#
# and:
#
#     ROUTING DOMAIN
#
#
# producing:
#
#     POLICY EFFECT
#
#
# Conceptually:
#
#
#     DATA CLASSIFICATION
#             +
#     ROUTING DOMAIN
#             |
#             v
#       POLICY EFFECT
#
#
# Example:
#
#
#     E8
#      +
#     COMPANY_CLOUD_LLM
#      =
#     DENY
#
#
# This is intentionally a small model.
#
# DataRoutePolicy does not need to know how policy is stored,
# evaluated, distributed, versioned, or enforced.
#
#
#     MODEL DESCRIBES
#
#     POLICY ENGINE EVALUATES
#
#     ROUTING CONSUMES THE RESULT
#
# ==========================================================================


class DataRoutePolicy(Agent11BaseModel):
    """
    Describes configured routing policy for one data classification
    and one Agent 11 routing domain.

    DataRoutePolicy is policy configuration.

    It does not evaluate AI requests, inspect AI services, determine
    capability, determine service availability, determine network
    reachability, select routes, or invoke AI models.
    """

    classification: DataClassificationLevel = Field(
        description=(
            "Data classification governed by this routing policy rule."
        ),
    )

    routing_domain: AIRoute = Field(
        description=(
            "Agent 11 routing domain governed by this policy rule."
        ),
    )

    effect: DataRoutePolicyEffect = Field(
        description=(
            "Configured policy effect for this classification and "
            "routing domain."
        ),
    )


# ==========================================================================
# FIELD SEMANTICS — classification
# ==========================================================================
#
# classification identifies the data classification to which this
# policy rule applies.
#
#
# Example classifications may include:
#
#
#     NORMAL
#
#     E7
#
#     E8
#
#     E9
#
#
# The exact classification vocabulary belongs to the classification
# domain.
#
#
# DataRoutePolicy CONSUMES that vocabulary.
#
# It does not define what E7, E8, or E9 mean.
#
#
# Most importantly, a classification does not itself select a route.
#
#
# This would be conceptually wrong:
#
#
#     E8 == COMPANY_ONPREM_LLM
#
#
# Instead:
#
#
#     DATA
#       |
#       v
#     CLASSIFICATION
#       |
#       v
#     POLICY
#       |
#       v
#     AUTHORIZATION RESULT
#       |
#       v
#     ROUTING
#
#
# Therefore:
#
#
#     DATA CLASSIFICATION != ROUTING DOMAIN
#
#
#     CLASSIFICATION INFORMS POLICY
#
#
#     POLICY CONSTRAINS ROUTING
#
# ==========================================================================


# ==========================================================================
# FIELD SEMANTICS — routing_domain
# ==========================================================================
#
# routing_domain identifies the Agent 11 routing domain governed by
# this rule.
#
#
# Current SEIR-I routing domains:
#
#
#     EXTERNAL_FM
#
#     COMPANY_CLOUD_LLM
#
#     COMPANY_ONPREM_LLM
#
#
# These are routing / trust domains.
#
# They are NOT cloud-provider identifiers.
#
#
# COMPANY_CLOUD_LLM may eventually contain services deployed in:
#
#
#     AWS
#
#     Azure
#
#     GCP
#
#     OCI
#
#     another cloud
#
#
# without requiring additional AIRoute values.
#
#
# Therefore:
#
#
#     ROUTING DOMAIN != CLOUD PROVIDER
#
#
#     ROUTING DOMAIN != DEPLOYMENT LOCATION
#
#
#     ROUTING DOMAIN != REGION
#
#
#     ROUTING DOMAIN != AVAILABILITY ZONE
#
#
#     ROUTING DOMAIN != KUBERNETES CLUSTER
#
#
#     ROUTING DOMAIN != INFERENCE ENDPOINT
#
#
# Those are deployment/runtime facts.
#
# Future policy may CONSUME those facts without making them part of
# AIRoute.
#
# ==========================================================================


# ==========================================================================
# FIELD SEMANTICS — effect
# ==========================================================================
#
# effect describes what this configured policy rule says.
#
#
# SEIR-I:
#
#
#     ALLOW
#
#         This policy rule permits the routing domain for the
#         specified data classification.
#
#
#     DENY
#
#         This policy rule prohibits the routing domain for the
#         specified data classification.
#
#
# effect does NOT describe:
#
#
#     model capability
#
#     service health
#
#     network reachability
#
#     latency
#
#     cost
#
#     route preference
#
#     route selection
#
#
# It answers one policy question:
#
#
#     "DOES THIS CONFIGURED POLICY RULE PERMIT
#      THIS ROUTING DOMAIN FOR THIS DATA CLASSIFICATION?"
#
#
# It does not answer:
#
#
#     "SHOULD ROUTING SELECT IT?"
#
# ==========================================================================


# ==========================================================================
# SEIR-I POLICY EXAMPLE
# ==========================================================================
#
# The following table is an EXAMPLE organizational policy.
#
# It demonstrates how DataRoutePolicy can be used.
#
# It is NOT universal Agent 11 behavior.
#
#
#     +----------------+-------------+---------------+----------------+
#     | Classification | External FM | Company Cloud | Company OnPrem |
#     +----------------+-------------+---------------+----------------+
#     | NORMAL         | ALLOW       | ALLOW         | ALLOW          |
#     | E7             | DENY        | ALLOW         | ALLOW          |
#     | E8             | DENY        | DENY          | ALLOW          |
#     | E9             | DENY        | DENY          | ALLOW          |
#     +----------------+-------------+---------------+----------------+
#
#
# Each cell can conceptually be represented by one DataRoutePolicy.
#
#
# Example:
#
#
#     DataRoutePolicy(
#         classification=DataClassificationLevel.E8,
#         routing_domain=AIRoute.EXTERNAL_FM,
#         effect=DataRoutePolicyEffect.DENY,
#     )
#
#
#     DataRoutePolicy(
#         classification=DataClassificationLevel.E8,
#         routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#         effect=DataRoutePolicyEffect.DENY,
#     )
#
#
#     DataRoutePolicy(
#         classification=DataClassificationLevel.E8,
#         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#         effect=DataRoutePolicyEffect.ALLOW,
#     )
#
#
# IMPORTANT:
#
#
#     THIS TABLE IS POLICY DATA.
#
#     THIS TABLE IS NOT ROUTER LOGIC.
#
#
# If the organization later changes:
#
#
#     E8 + COMPANY_CLOUD_LLM
#
# from:
#
#     DENY
#
# to:
#
#     ALLOW
#
#
# that should be a policy-configuration change.
#
# It should NOT require rewriting router.py.
#
#
#     POLICY DATA != ROUTER LOGIC
#
# ==========================================================================


# ==========================================================================
# MODEL DEFINITION != POLICY DATABASE
# ==========================================================================
#
# The example policy objects above are documentation examples.
#
# Do not instantiate the organization's complete policy table as
# module-level objects merely because DataRoutePolicy is defined here.
#
#
# This module defines:
#
#
#     WHAT A DATA ROUTE POLICY RULE LOOKS LIKE
#
#
# It does not define:
#
#
#     ALL POLICY RULES CURRENTLY IN FORCE
#
#
# Future policy configuration might come from:
#
#
#     configuration files
#
#     databases
#
#     policy services
#
#     governance platforms
#
#     external policy engines
#
#     other enterprise systems
#
#
# Therefore:
#
#
#     MODEL DEFINITION != POLICY DATABASE
#
#
#     DOMAIN CONTRACT != CURRENT CONFIGURATION
#
# ==========================================================================


# ==========================================================================
# WHY DataRoutePolicy HAS NO CUSTOM VALIDATOR
# ==========================================================================
#
# Pydantic already establishes:
#
#
#     classification
#
#         is a valid DataClassificationLevel
#
#
#     routing_domain
#
#         is a valid AIRoute
#
#
#     effect
#
#         is a valid DataRoutePolicyEffect
#
#
# There is currently no additional cross-field invariant that belongs
# to DataRoutePolicy itself.
#
#
# For example, DO NOT write:
#
#
#     @model_validator(mode="after")
#     def prevent_e8_external(self):
#         if (
#             self.classification is DataClassificationLevel.E8
#             and self.routing_domain is AIRoute.EXTERNAL_FM
#         ):
#             raise ValueError(...)
#
#
# Why would that be wrong?
#
#
# Because:
#
#
#     "E8 data may not use external AI"
#
#
# is an ORGANIZATIONAL POLICY CHOICE.
#
#
# It is not a structural invariant of DataRoutePolicy.
#
#
# The object:
#
#
#     E8 + EXTERNAL_FM + ALLOW
#
#
# is structurally capable of representing policy.
#
# Whether that policy is acceptable to a particular organization is a
# policy-governance question.
#
#
# If we encode today's organizational policy into Pydantic validators,
# then:
#
#
#     PYDANTIC MODEL
#
# quietly becomes:
#
#     POLICY ENGINE
#
#
# That destroys the boundary.
#
#
# Therefore:
#
#
#     VALIDATION DEFINES DOMAIN LEGALITY
#
#
#     POLICY DATA DEFINES ORGANIZATIONAL CHOICE
#
#
#     VALIDATION != POLICY CONFIGURATION
#
#
#     ORGANIZATIONAL POLICY != PYDANTIC INVARIANT
#
#
# A validator should exist because the object itself would otherwise
# become semantically contradictory.
#
# It should not exist merely because we know how to write validators.
#
#
#     VALIDATION SHOULD REPRESENT A RULE
#
#
#     VALIDATION SHOULD NOT BE DECORATION
#
# ==========================================================================


# ==========================================================================
# DataRoutePolicy DOES NOT KNOW
# ==========================================================================
#
# DataRoutePolicy does not need:
#
#
#     request_id
#
#     response_id
#
#     user_id
#
#     service_id
#
#     model_id
#
#     deployment_id
#
#     cloud_provider
#
#     region
#
#     endpoint
#
#     service health
#
#     network path
#
#     BGP state
#
#     SD-WAN state
#
#     latency
#
#     token cost
#
#     GPU utilization
#
#     queue depth
#
#     routing score
#
#     selected destination
#
#     AI response
#
#
# Why?
#
#
# Because DataRoutePolicy represents one configured relationship:
#
#
#     DATA CLASSIFICATION
#
#              +
#
#     ROUTING DOMAIN
#
#              =
#
#     POLICY EFFECT
#
#
# Those other facts belong to neighboring domains.
#
#
# Before adding another field, ask:
#
#
#     WHICH THING OWNS WHICH FACT?
#
#
# Do not turn DataRoutePolicy into:
#
#
#     EnterprisePolicyRoutingCloudNetworkModelThing.py
#
#
# Chewbacca submitted that pull request.
#
# Agent 11 requested changes.
#
# ==========================================================================


# ==========================================================================
# DataRoutePolicy VS PolicyDecision
# ==========================================================================
#
# DataRoutePolicy describes:
#
#
#     WHAT POLICY IS CONFIGURED TO SAY
#
#
# PolicyDecision describes:
#
#
#     WHAT POLICY EVALUATION CONCLUDED
#
#
# Example:
#
#
#     CONFIGURATION
#
#
#         E8
#          +
#         COMPANY_CLOUD_LLM
#          =
#         DENY
#
#
#                  |
#                  v
#
#          POLICY EVALUATION
#
#                  |
#                  v
#
#
#         PolicyDecision
#
#             request_id = ...
#
#             routing_domain =
#                 COMPANY_CLOUD_LLM
#
#             status =
#                 DENY
#
#
# Therefore:
#
#
#     POLICY RULE != POLICY DECISION
#
#
#     CONFIGURATION != EVALUATION RESULT
#
#
#     DataRoutePolicy != PolicyDecision
#
#
# Part II defines PolicyDecision.
# ==========================================================================


# ==========================================================================
# POLICY DOES NOT ROUTE
# ==========================================================================
#
# Suppose DataRoutePolicy says:
#
#
#     E8
#      +
#     COMPANY_ONPREM_LLM
#      =
#     ALLOW
#
#
# That does NOT mean Agent 11 must select an on-premises service.
#
#
# The service might:
#
#
#     lack the required capability
#
#     be unavailable
#
#     be unreachable
#
#
# Or another policy-permitted destination may eventually be preferable.
#
#
# Policy establishes one required routing fact:
#
#
#     AUTHORIZATION
#
#
# It does not establish complete viability.
#
#
# Recall the Agent 11 routing contract:
#
#
#     VIABLE ROUTE
#
#         =
#
#     POLICY PERMITTED
#
#         +
#
#     SERVICE CAPABLE
#
#         +
#
#     SERVICE AVAILABLE
#
#         +
#
#     PATH AVAILABLE
#
#
# Therefore:
#
#
#     POLICY ALLOW != ROUTE SELECTED
#
#
#     AUTHORIZED != CAPABLE
#
#
#     AUTHORIZED != AVAILABLE
#
#
#     AUTHORIZED != REACHABLE
#
#
#     AUTHORIZED != VIABLE
#
#
#     AUTHORIZED != SELECTED
#
#
# Policy answers:
#
#
#     MAY WE?
#
#
# Routing answers:
#
#
#     WHICH VIABLE DESTINATION?
#
# ==========================================================================


# ==========================================================================
# POLICY IS A CONSTRAINT
# ==========================================================================
#
# Policy authorization is not a routing preference.
#
#
# Do not treat:
#
#
#     ALLOW
#
# and:
#
#     DENY
#
#
# as different weights in an optimization function.
#
#
# Do not create:
#
#
#     policy_score = 0.8
#
#
# and allow:
#
#
#     lower cost
#
#     lower latency
#
#     higher quality
#
#
# to compensate for missing authorization.
#
#
# A policy-denied destination is not:
#
#
#     "slightly less desirable."
#
#
# It is:
#
#
#     NOT AUTHORIZED
#
#
# Therefore:
#
#
#     POLICY IS A CONSTRAINT
#
#
#     POLICY IS NOT A PREFERENCE
#
#
#     POLICY IS NOT AN OPTIMIZATION WEIGHT
#
#
#     POLICY NEVER BECOMES A SCORE
#
#
# SEIR-II may perform sophisticated optimization among candidates that
# have already satisfied required policy constraints.
#
# Optimization must never create authorization.
# ==========================================================================


# ==========================================================================
# USER RESTRICTIONS
# ==========================================================================
#
# Part I describes organization-configured data-routing policy.
#
# Future policy evaluation may combine this configuration with user
# restrictions.
#
#
# The foundational rule is:
#
#
#     EFFECTIVE POLICY
#
#         =
#
#     ORGANIZATION POLICY
#
#         INTERSECTION
#
#     USER POLICY
#
#
# Therefore:
#
#
#     USER MAY NARROW
#
#
#     USER MAY NOT EXPAND
#
#
# Example:
#
#
# Organization permits:
#
#
#     EXTERNAL_FM
#
#     COMPANY_CLOUD_LLM
#
#     COMPANY_ONPREM_LLM
#
#
# User chooses:
#
#
#     ONPREM_ONLY
#
#
# Effective authorization may narrow to:
#
#
#     COMPANY_ONPREM_LLM
#
#
# But if organization policy prohibits:
#
#
#     EXTERNAL_FM
#
#
# the user cannot create authorization by requesting:
#
#
#     EXTERNAL_FM
#
#
#     PREFERENCE != AUTHORITY
#
#
# Part II and Part III preserve the richer evaluation semantics.
# ==========================================================================


# ==========================================================================
# SEIR-II EXPANSION MARKER — DO NOT DELETE
# ==========================================================================
#
# SEIR-I DataRoutePolicy intentionally governs:
#
#
#     DATA CLASSIFICATION
#
#              +
#
#     ROUTING DOMAIN
#
#
# This is intentionally simple.
#
#
# Future policy evaluation may additionally consume:
#
#
#     model identity
#
#     service identity
#
#     deployment identity
#
#     cloud provider
#
#     region
#
#     jurisdiction
#
#     data residency
#
#     sovereignty requirements
#
#     model governance
#
#     service governance
#
#     customer restrictions
#
#     regulatory requirements
#
#     identity context
#
#     workload context
#
#
# Example:
#
#
#                  COMPANY_CLOUD_LLM
#
#                         |
#            +------------+------------+
#            |            |            |
#            v            v            v
#           AWS         AZURE         GCP
#            |            |            |
#            v            v            v
#       Deployment A Deployment B Deployment C
#
#
# Policy may generally permit:
#
#
#     COMPANY_CLOUD_LLM
#
#
# while future deployment-aware policy determines:
#
#
#     Deployment A
#         AWS / US
#         ALLOW
#
#
#     Deployment B
#         Azure / US
#         ALLOW
#
#
#     Deployment C
#         GCP / EU
#         DENY for this dataset
#
#
# This does NOT require:
#
#
#     AIRoute.COMPANY_AWS_LLM
#
#     AIRoute.COMPANY_AZURE_LLM
#
#     AIRoute.COMPANY_GCP_LLM
#
#
# Those would collapse deployment topology into routing-domain
# vocabulary.
#
#
# Instead:
#
#
#     FUTURE POLICY CONSUMES RICHER DEPLOYMENT FACTS
#
#
# while:
#
#
#     AIRoute REMAINS A ROUTING-DOMAIN ABSTRACTION
#
#
# Therefore:
#
#
#     POLICY MAY BECOME MORE PRECISE
#
#     WITHOUT MAKING AIRoute MORE SPECIFIC
#
#
#     POLICY PRECISION != ROUTING DOMAIN EXPANSION
#
#
#     ROUTING DOMAIN != CLOUD PROVIDER
#
#
#     ROUTING DOMAIN != DEPLOYMENT LOCATION
#
#
# Part III expands these SEIR-II policy semantics substantially.
#
# DO NOT DELETE THIS EXPANSION MARKER MERELY BECAUSE THE CURRENT
# SEIR-I IMPLEMENTATION DOES NOT YET REQUIRE THOSE FEATURES.
#
#
# This is the letter from SEIR-I to SEIR-II:
#
#
#     EXTEND THE POLICY MODEL WHEN THE DOMAIN REQUIRES IT.
#
#     DO NOT DESTROY THE EXISTING DOMAIN BOUNDARIES TO GET THERE.
#
# ==========================================================================


# ==========================================================================
# PART I — FINAL INVARIANTS
# ==========================================================================
#
#     DataRoutePolicy = POLICY CONFIGURATION
#
#
#     DATA CLASSIFICATION
#         +
#     ROUTING DOMAIN
#         =
#     POLICY EFFECT
#
#
#     POLICY CONFIGURATION != POLICY EVALUATION
#
#
#     POLICY RULE != POLICY DECISION
#
#
#     POLICY EFFECT != POLICY DECISION STATUS
#
#
#     CONFIGURATION SHOULD NOT INTENTIONALLY CONFIGURE UNCERTAINTY
#
#
#     DATA CLASSIFICATION != ROUTING DOMAIN
#
#
#     CLASSIFICATION INFORMS POLICY
#
#
#     POLICY CONSTRAINS ROUTING
#
#
#     POLICY ALLOW != ROUTE SELECTED
#
#
#     AUTHORIZED != CAPABLE
#
#
#     AUTHORIZED != AVAILABLE
#
#
#     AUTHORIZED != REACHABLE
#
#
#     AUTHORIZED != VIABLE
#
#
#     AUTHORIZED != SELECTED
#
#
#     ROUTING DOMAIN != CLOUD PROVIDER
#
#
#     ROUTING DOMAIN != DEPLOYMENT LOCATION
#
#
#     MODEL DEFINITION != POLICY DATABASE
#
#
#     DOMAIN CONTRACT != CURRENT CONFIGURATION
#
#
#     VALIDATION != POLICY CONFIGURATION
#
#
#     ORGANIZATIONAL POLICY != PYDANTIC INVARIANT
#
#
#     VALIDATION SHOULD REPRESENT A RULE
#
#
#     VALIDATION SHOULD NOT BE DECORATION
#
#
#     POLICY DATA != ROUTER LOGIC
#
#
#     POLICY IS A CONSTRAINT
#
#
#     POLICY IS NOT A PREFERENCE
#
#
#     POLICY IS NOT AN OPTIMIZATION WEIGHT
#
#
#     POLICY NEVER BECOMES A SCORE
#
#
#     USER MAY NARROW
#
#
#     USER MAY NOT EXPAND
#
#
#     PREFERENCE != AUTHORITY
#
#
#     POLICY MAY BECOME MORE PRECISE
#     WITHOUT MAKING AIRoute MORE SPECIFIC
#
#
#     POLICY PRECISION != ROUTING DOMAIN EXPANSION
#
#
#     WHICH THING OWNS WHICH FACT?
#
#
#     PYDANTIC DEFINES THE DOMAIN CONTRACT
#
#     POLICY BEHAVIOR PRODUCES THE DOMAIN OBJECT
# ==========================================================================
# END PART I
# ==========================================================================

# ==========================================================================
# PART II — POLICY DECISION
# ==========================================================================
#
# Part I defined:
#
#
#     DataRoutePolicy
#
#         WHAT IS POLICY CONFIGURED TO SAY?
#
#
# Part II defines:
#
#
#     PolicyDecision
#
#         WHAT DID POLICY EVALUATION CONCLUDE
#         FOR THIS REQUEST AND ROUTING DOMAIN?
#
#
# Conceptually:
#
#
#     AIRequest
#         |
#         v
#     Data Classification
#         |
#         v
#     Configured Policy
#         |
#         +
#         |
#     User Restrictions
#         |
#         v
#     Policy Evaluation
#         |
#         v
#     PolicyDecision
#
#
# PolicyDecision is an EVALUATION RESULT.
#
#
# It is NOT:
#
#
#     policy configuration,
#
#     a routing candidate,
#
#     a routing decision,
#
#     a service-health observation,
#
#     a network observation,
#
#     or an AI response.
#
#
#     POLICY CONFIGURATION != POLICY EVALUATION
#
#
#     POLICY DECISION != ROUTING DECISION
#
#
# Policy answers:
#
#
#     MAY WE?
#
#
# Routing answers:
#
#
#     WHICH VIABLE DESTINATION?
#
# ==========================================================================


# ==========================================================================
# ADDITIONAL PART II IMPORTS
# ==========================================================================
#
# Part II additionally requires:
#
#
#     UUID
#
#     PolicyDecisionStatus
#
#
# Add these to the import section at the TOP of policy.py:
#
#
#     from uuid import UUID
#
#
# and ensure:
#
#
#     PolicyDecisionStatus
#
# is included in:
#
#
#     from ..enums.policy_enums import (...)
#
#
# Do not place executable imports here in the middle of the final file.
# ==========================================================================


# ==========================================================================
# PolicyDecisionStatus
# ==========================================================================
#
# PolicyDecisionStatus describes the result of policy EVALUATION.
#
#
# Current SEIR-I vocabulary:
#
#
#     ALLOW
#
#         Authorization was established.
#
#
#     DENY
#
#         Policy explicitly prohibits the routing domain for this
#         request context.
#
#
#     RESTRICT
#
#         Policy did not produce an unconditional ALLOW.
#         Additional policy constraints apply.
#
#
#     INDETERMINATE
#
#         Policy evaluation could not establish a definitive
#         authorization result.
#
#
# This is intentionally richer than:
#
#
#     DataRoutePolicyEffect
#
#
# which contains:
#
#
#     ALLOW
#
#     DENY
#
#
# Why?
#
#
# Because:
#
#
#     DataRoutePolicyEffect
#
# describes:
#
#     CONFIGURATION
#
#
# while:
#
#
#     PolicyDecisionStatus
#
# describes:
#
#     EVALUATION RESULT
#
#
# Policy evaluation may combine several sources, encounter incomplete
# information, or impose restrictions that do not exist on one simple
# DataRoutePolicy rule.
#
#
#     POLICY EFFECT != POLICY DECISION STATUS
# ==========================================================================


class PolicyDecision(Agent11BaseModel):
    """
    Describes the result of policy evaluation for an AI request
    against an Agent 11 routing domain.

    PolicyDecision records the authorization outcome produced by
    policy evaluation.

    It does not perform policy evaluation, service evaluation,
    capability matching, network evaluation, routing, AI invocation,
    or execution authorization.
    """

    # ----------------------------------------------------------------------
    # request_id
    # ----------------------------------------------------------------------
    #
    # DataRoutePolicy does not reference an AI request because it
    # represents reusable policy configuration.
    #
    #
    # PolicyDecision DOES reference a request because it represents the
    # result of evaluating policy in a particular request context.
    #
    #
    # Compare:
    #
    #
    #     DataRoutePolicy
    #
    #         E8 + EXTERNAL_FM = DENY
    #
    #
    # versus:
    #
    #
    #     PolicyDecision
    #
    #         request_id = ...
    #
    #         routing_domain = EXTERNAL_FM
    #
    #         status = DENY
    #
    #
    # Therefore:
    #
    #
    #     POLICY RULE = REUSABLE CONFIGURATION
    #
    #
    #     POLICY DECISION = REQUEST-SPECIFIC EVALUATION RESULT
    #
    #
    # PolicyDecision references the request.
    #
    # It does not embed AIRequest.
    #
    #
    #     POLICY DECISION REFERENCES REQUEST
    #
    #     POLICY DECISION DOES NOT OWN REQUEST
    #
    # ----------------------------------------------------------------------

    request_id: UUID = Field(
        description=(
            "Identifier of the AI request for which policy was evaluated."
        ),
    )

    # ----------------------------------------------------------------------
    # routing_domain
    # ----------------------------------------------------------------------
    #
    # SEIR-I policy evaluates Agent 11 routing domains.
    #
    #
    # Current routing domains:
    #
    #
    #     EXTERNAL_FM
    #
    #     COMPANY_CLOUD_LLM
    #
    #     COMPANY_ONPREM_LLM
    #
    #
    # Example:
    #
    #
    #     Request:
    #
    #         classification = E8
    #
    #
    #     Policy Evaluation:
    #
    #         EXTERNAL_FM
    #             DENY
    #
    #         COMPANY_CLOUD_LLM
    #             DENY
    #
    #         COMPANY_ONPREM_LLM
    #             ALLOW
    #
    #
    # One request may therefore produce several PolicyDecision objects,
    # one for each routing domain actually evaluated.
    #
    #
    # SEIR-I deliberately does NOT require PolicyDecision to contain:
    #
    #
    #     service_id
    #
    #     model_id
    #
    #     deployment_id
    #
    #     cloud_provider
    #
    #     region
    #
    #
    # Future SEIR-II policy evaluation may consume those attributes.
    #
    # That future precision does not require them to become part of the
    # current routing-domain decision contract.
    #
    #
    #     SEIR-I POLICY TARGET = ROUTING DOMAIN
    #
    #
    #     ROUTING DOMAIN != SERVICE
    #
    #     ROUTING DOMAIN != MODEL
    #
    #     ROUTING DOMAIN != DEPLOYMENT
    #
    #     ROUTING DOMAIN != CLOUD PROVIDER
    #
    # ----------------------------------------------------------------------

    routing_domain: AIRoute = Field(
        description=(
            "Agent 11 routing domain evaluated by policy."
        ),
    )

    # ----------------------------------------------------------------------
    # status
    # ----------------------------------------------------------------------
    #
    # status records what policy evaluation concluded.
    #
    #
    #     ALLOW
    #
    #     DENY
    #
    #     RESTRICT
    #
    #     INDETERMINATE
    #
    #
    # This field is the machine-readable policy semantic.
    #
    #
    # It must not be replaced by:
    #
    #
    #     allowed: bool
    #
    #
    # because a Boolean cannot faithfully represent:
    #
    #
    #     RESTRICT
    #
    # or:
    #
    #     INDETERMINATE
    #
    #
    # Preserve the richer policy vocabulary.
    #
    #
    #     POLICY DECISION STATUS
    #         !=
    #     BOOLEAN AUTHORIZATION FLAG
    #
    # ----------------------------------------------------------------------

    status: PolicyDecisionStatus = Field(
        description=(
            "Result of policy evaluation for the request and routing domain."
        ),
    )

    # ----------------------------------------------------------------------
    # reason
    # ----------------------------------------------------------------------
    #
    # reason provides an optional human-readable explanation.
    #
    #
    # Example:
    #
    #
    #     "External AI is prohibited for E8-classified data."
    #
    #
    # Useful for:
    #
    #
    #     logs
    #
    #     operators
    #
    #     troubleshooting
    #
    #     audit interpretation
    #
    #     teaching
    #
    #
    # But downstream behavior must NOT parse this text to determine
    # authorization.
    #
    #
    # BAD:
    #
    #
    #     if "prohibited" in decision.reason:
    #         ...
    #
    #
    # Machine semantics belong to:
    #
    #
    #     PolicyDecisionStatus
    #
    #
    # Future richer evidence should receive typed domain contracts
    # rather than increasingly elaborate prose.
    #
    #
    #     HUMAN EXPLANATION != MACHINE CONTRACT
    #
    #
    #     REASON TEXT != POLICY SEMANTICS
    #
    # ----------------------------------------------------------------------

    reason: str | None = Field(
        default=None,
        description=(
            "Optional human-readable explanation of the policy decision."
        ),
    )


# ==========================================================================
# ALLOW
# ==========================================================================
#
# ALLOW means:
#
#
#     POLICY AUTHORIZATION WAS ESTABLISHED
#
#
# The evaluated routing domain survived the policy gate.
#
#
# Example:
#
#
#     PolicyDecision(
#         request_id=request.request_id,
#         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#         status=PolicyDecisionStatus.ALLOW,
#     )
#
#
# This means:
#
#
#     Agent 11 policy permits the request to use the
#     COMPANY_ONPREM_LLM routing domain.
#
#
# It does NOT mean:
#
#
#     a suitable model exists
#
#     a suitable service exists
#
#     the service is healthy
#
#     the network can reach the service
#
#     the route is optimal
#
#     routing selected the destination
#
#
# Therefore:
#
#
#     ALLOW != CAPABLE
#
#
#     ALLOW != AVAILABLE
#
#
#     ALLOW != REACHABLE
#
#
#     ALLOW != VIABLE
#
#
#     ALLOW != SELECTED
#
#
# Policy ALLOW contributes one required fact to viability.
#
#
#     POLICY PERMITTED
#
#         +
#
#     SERVICE CAPABLE
#
#         +
#
#     SERVICE AVAILABLE
#
#         +
#
#     PATH AVAILABLE
#
#         =
#
#     VIABLE ROUTE
# ==========================================================================


# ==========================================================================
# DENY
# ==========================================================================
#
# DENY means:
#
#
#     POLICY EXPLICITLY PROHIBITS THIS ROUTING DOMAIN
#     FOR THE EVALUATED REQUEST CONTEXT
#
#
# Example:
#
#
#     PolicyDecision(
#         request_id=request.request_id,
#         routing_domain=AIRoute.EXTERNAL_FM,
#         status=PolicyDecisionStatus.DENY,
#         reason=(
#             "External AI is prohibited for E8-classified data."
#         ),
#     )
#
#
# The external service might still be:
#
#
#     capable
#
#     healthy
#
#     reachable
#
#     fast
#
#     inexpensive
#
#
# None of those facts override policy.
#
#
# Therefore:
#
#
#     DENY != SERVICE FAILURE
#
#
#     DENY != NETWORK FAILURE
#
#
#     DENY != CAPABILITY FAILURE
#
#
#     HEALTHY != PERMITTED
#
#
#     REACHABLE != AUTHORIZED
#
#
#     CHEAPER != PERMITTED
#
#
#     FASTER != PERMITTED
#
#
# A DENY is a policy outcome.
#
# It is not an infrastructure diagnosis.
# ==========================================================================


# ==========================================================================
# RESTRICT
# ==========================================================================
#
# RESTRICT means:
#
#
#     POLICY DID NOT PRODUCE AN UNCONDITIONAL ALLOW
#
#
# Additional constraints apply before the destination can be treated as
# usable.
#
#
# Future examples may include:
#
#
#     approved deployment locations only
#
#     approved model families only
#
#     approved services only
#
#     human approval required
#
#     enhanced logging required
#
#     reduced data scope
#
#     customer-specific controls
#
#     residency requirements
#
#
# SEIR-I deliberately does NOT attempt to encode every possible
# restriction here.
#
#
# Therefore:
#
#
#     RESTRICT != ALLOW
#
#
#     RESTRICT != DENY
#
#
#     RESTRICT != INDETERMINATE
#
#
# Most importantly:
#
#
#     RESTRICT
#
# does NOT mean:
#
#     "Go ahead and figure out the restrictions later."
#
#
# Required restrictions must be satisfied before the route can become
# usable.
#
#
# Future SEIR-II may introduce typed restriction details.
#
#
#     RESTRICTION STATUS
#         !=
#     RESTRICTION DETAILS
#
#
# Do not prematurely create:
#
#
#     restrictions: dict[str, Any]
#
#
# merely to hold arbitrary policy information.
#
#
#     UNTYPED DICTIONARY != DOMAIN MODEL
# ==========================================================================


# ==========================================================================
# INDETERMINATE
# ==========================================================================
#
# INDETERMINATE means:
#
#
#     POLICY EVALUATION COULD NOT ESTABLISH
#     A DEFINITIVE AUTHORIZATION RESULT
#
#
# Possible future causes:
#
#
#     missing policy
#
#     unavailable policy source
#
#     conflicting policy information
#
#     missing request attributes
#
#     unresolved user restrictions
#
#     incomplete deployment metadata
#
#     unavailable identity information
#
#     policy-engine evaluation failure
#
#
# INDETERMINATE is NOT:
#
#
#     ALLOW
#
#
# and it is NOT semantically identical to:
#
#
#     DENY
#
#
# Agent 11 should fail closed when authorization cannot be established.
#
#
# Therefore:
#
#
#     INDETERMINATE
#         |
#         v
#     DO NOT TREAT DESTINATION AS AUTHORIZED
#
#
# But the recorded policy fact remains:
#
#
#     INDETERMINATE
#
#
# not:
#
#     DENY
#
#
# Why preserve the distinction?
#
#
# DENY may mean:
#
#
#     SECURITY POLICY WORKED CORRECTLY
#
#
# INDETERMINATE may mean:
#
#
#     POLICY INFRASTRUCTURE / EVIDENCE PROBLEM
#
#
# Those operational meanings are different.
#
#
# Therefore:
#
#
#     INDETERMINATE != DENY
#
#
#     INDETERMINATE != ALLOW
#
#
#     INDETERMINATE => FAIL CLOSED
#
#
#     FAIL CLOSED != FALSIFY OBSERVED STATE
#
#
#     DECISION BEHAVIOR != OBSERVED TRUTH
# ==========================================================================


# ==========================================================================
# WHY PolicyDecision DOES NOT USE allowed: bool
# ==========================================================================
#
# Consider:
#
#
#     ALLOW
#         -> True
#
#
#     DENY
#         -> False
#
#
#     RESTRICT
#         -> ???
#
#
#     INDETERMINATE
#         -> ???
#
#
# A Boolean destroys policy semantics.
#
#
# This is the same architectural lesson used in routing:
#
#
#     RoutingStatus
#
#         SELECTED
#         BLOCKED
#         NO_VIABLE_ROUTE
#         NULL
#
#
# should not collapse into:
#
#
#     success: bool
#
#
# Likewise:
#
#
#     PolicyDecisionStatus
#
# should not collapse into:
#
#
#     allowed: bool
#
#
#     PRESERVE THE DOMAIN STATE
#
# ==========================================================================


# ==========================================================================
# WHY PolicyDecision HAS NO CUSTOM VALIDATOR YET
# ==========================================================================
#
# Pydantic already validates:
#
#
#     request_id
#         is a UUID
#
#
#     routing_domain
#         is a valid AIRoute
#
#
#     status
#         is a valid PolicyDecisionStatus
#
#
#     reason
#         is text or None
#
#
# There is currently no required cross-field semantic invariant.
#
#
# For example:
#
#
#     DENY => reason required
#
#
# is NOT currently an invariant.
#
#
# A machine-readable DENY remains valid without human-readable prose.
#
#
# Likewise:
#
#
#     INDETERMINATE => reason required
#
#
# is not necessarily an invariant.
#
#
# Future provenance may hold detailed evidence elsewhere.
#
#
# And:
#
#
#     ALLOW => reason forbidden
#
#
# would also be incorrect.
#
#
# An ALLOW decision may legitimately explain why authorization was
# established.
#
#
# Therefore:
#
#
#     NO CUSTOM VALIDATOR IS REQUIRED YET
#
#
# This is deliberate restraint.
#
#
#     VALIDATION SHOULD REPRESENT A RULE
#
#
#     VALIDATION SHOULD NOT BE DECORATION
#
#
#     KNOWING HOW TO WRITE A VALIDATOR
#         !=
#     NEEDING A VALIDATOR
# ==========================================================================


# ==========================================================================
# EFFECTIVE POLICY
# ==========================================================================
#
# Policy evaluation may combine several policy sources.
#
#
# At minimum:
#
#
#     ORGANIZATION POLICY
#
# and:
#
#     USER RESTRICTION
#
#
# The foundational security principle is:
#
#
#     EFFECTIVE POLICY
#
#         =
#
#     ORGANIZATION POLICY
#
#         INTERSECTION
#
#     USER POLICY
#
#
# Example:
#
#
# Organization allows:
#
#
#     EXTERNAL_FM
#
#     COMPANY_CLOUD_LLM
#
#     COMPANY_ONPREM_LLM
#
#
# User chooses:
#
#
#     ONPREM_ONLY
#
#
# Effective authorization:
#
#
#     COMPANY_ONPREM_LLM
#
#
# This is legitimate because the user narrowed organizational
# authorization.
#
#
# But:
#
#
# Organization allows:
#
#
#     COMPANY_ONPREM_LLM only
#
#
# User requests:
#
#
#     EXTERNAL_FM
#
#
# Effective authorization remains:
#
#
#     COMPANY_ONPREM_LLM only
#
#
# Therefore:
#
#
#     USER MAY NARROW
#
#
#     USER MAY NOT EXPAND
#
#
#     LOWER AUTHORITY CANNOT GRANT
#     WHAT HIGHER AUTHORITY PROHIBITED
# ==========================================================================


# ==========================================================================
# FUTURE POLICY AUTHORITY HIERARCHY — SEIR-II MARKER
# ==========================================================================
#
# Future enterprise policy may involve:
#
#
#     ORGANIZATION POLICY
#             |
#             v
#     BUSINESS UNIT POLICY
#             |
#             v
#     APPLICATION POLICY
#             |
#             v
#     WORKLOAD POLICY
#             |
#             v
#     AGENT POLICY
#             |
#             v
#     USER RESTRICTION
#             |
#             v
#       EFFECTIVE POLICY
#
#
# The exact hierarchy is intentionally NOT modeled in SEIR-I.
#
#
# Future policy composition must eventually define:
#
#
#     authority
#
#     precedence
#
#     inheritance
#
#     conflict behavior
#
#     narrowing
#
#     exceptions
#
#
# Do NOT assume:
#
#
#     policy composition = majority vote
#
#
# Example:
#
#
#     one authoritative DENY
#
# should not automatically be overridden by:
#
#
#     three lower-authority ALLOW rules
#
#
# Therefore:
#
#
#     LOWER AUTHORITY MAY NARROW
#
#     LOWER AUTHORITY MAY NOT EXPAND
#
#
#     POLICY COMPOSITION != MAJORITY VOTE
#
#
#     POLICY SOURCE COUNT != POLICY AUTHORITY
#
#
# Part III expands this substantially.
# ==========================================================================


# ==========================================================================
# PolicyDecision VS RoutingCandidate
# ==========================================================================
#
# Consider:
#
#
#     PolicyDecision
#
#         routing_domain =
#             COMPANY_CLOUD_LLM
#
#         status =
#             ALLOW
#
#
# Routing still needs to establish:
#
#
#     capability
#
#     service availability
#
#     network availability
#
#
# Only after those facts are evaluated can a particular AIService become:
#
#
#     RoutingCandidateStatus.VIABLE
#
#
# Therefore:
#
#
#     POLICY ALLOW != VIABLE CANDIDATE
#
#
# PolicyDecision answers:
#
#
#     MAY WE?
#
#
# RoutingCandidate answers:
#
#
#     DID THIS PARTICULAR SERVICE SURVIVE
#     THE COMPLETE VIABILITY EVALUATION?
# ==========================================================================


# ==========================================================================
# PolicyDecision VS RoutingDecision
# ==========================================================================
#
# Policy may allow:
#
#
#     COMPANY_CLOUD_LLM
#
# and:
#
#     COMPANY_ONPREM_LLM
#
#
# Both may eventually contain viable services.
#
#
# Routing might then select:
#
#
#     COMPANY_ONPREM_LLM
#
#
# Therefore:
#
#
#     POLICY DECISION != ROUTING DECISION
#
#
# Policy does not choose the final destination.
#
#
#     POLICY:
#
#         MAY WE?
#
#
#     ROUTING:
#
#         WHICH VIABLE DESTINATION?
#
#
#     INFERENCE:
#
#         WHAT DID THE MODEL PRODUCE?
#
#
#     EXECUTION AUTHORIZATION:
#
#         MAY THAT OUTPUT CAUSE AN ACTION?
#
#
# Keep those questions separate.
# ==========================================================================


# ==========================================================================
# ONE REQUEST MAY PRODUCE MULTIPLE PolicyDecision OBJECTS
# ==========================================================================
#
# Example:
#
#
#     AIRequest abc
#
#         |
#         +--> EXTERNAL_FM
#         |       DENY
#         |
#         +--> COMPANY_CLOUD_LLM
#         |       ALLOW
#         |
#         +--> COMPANY_ONPREM_LLM
#                 ALLOW
#
#
# Conceptually:
#
#
#     PolicyDecision(
#         request_id=abc,
#         routing_domain=AIRoute.EXTERNAL_FM,
#         status=PolicyDecisionStatus.DENY,
#     )
#
#
#     PolicyDecision(
#         request_id=abc,
#         routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#         status=PolicyDecisionStatus.ALLOW,
#     )
#
#
#     PolicyDecision(
#         request_id=abc,
#         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#         status=PolicyDecisionStatus.ALLOW,
#     )
#
#
# Each decision remains small and explicit.
#
#
# Avoid:
#
#
#     external_allowed: bool
#
#     cloud_allowed: bool
#
#     onprem_allowed: bool
#
#
# because that structure hard-codes today's AIRoute vocabulary into
# the PolicyDecision schema.
#
#
# A future aggregate may collect PolicyDecision objects.
#
# That aggregate does not need to exist here today.
# ==========================================================================


# ==========================================================================
# PolicyDecision DOES NOT KNOW THAT "E8 MEANS X"
# ==========================================================================
#
# PolicyDecision records the result.
#
#
# It does NOT contain organizational rules such as:
#
#
#     if classification == E8:
#         deny_external()
#
#
# Those rules belong to configured policy and policy evaluation.
#
#
# Otherwise:
#
#
#     POLICY MODEL
#
# becomes:
#
#     ORGANIZATION-SPECIFIC POLICY ENGINE
#
#
# and changing organizational policy requires editing Pydantic models.
#
#
# That would destroy the separation established in Part I.
#
#
# Therefore:
#
#
#     POLICY MODEL != POLICY ENGINE
#
#
#     POLICY CONFIGURATION != POLICY MODEL VALIDATION
#
#
#     ORGANIZATIONAL POLICY != PYDANTIC INVARIANT
# ==========================================================================


# ==========================================================================
# POLICY DECISION != POLICY EVIDENCE
# ==========================================================================
#
# PolicyDecision records:
#
#
#     THE RESULT
#
#
# Future policy evidence may include:
#
#
#     policy identifier
#
#     policy version
#
#     classification evidence
#
#     user restriction
#
#     identity context
#
#     deployment metadata
#
#     residency rule
#
#     regulatory rule
#
#     policy-engine trace
#
#
# Those facts should not automatically become fields on PolicyDecision.
#
#
# Future provenance can reference them.
#
#
# Therefore:
#
#
#     POLICY DECISION != POLICY EVIDENCE
#
#
#     DECISION != PROVENANCE
#
#
#     REFERENCE EVIDENCE
#
#     DO NOT DUPLICATE EVIDENCE
# ==========================================================================


# ==========================================================================
# SEIR-II EXPANSION MARKER — POLICY TARGET PRECISION — DO NOT DELETE
# ==========================================================================
#
# SEIR-I PolicyDecision primarily evaluates:
#
#
#     REQUEST
#
#         +
#
#     ROUTING DOMAIN
#
#
# Future policy may require more precise evaluation.
#
#
# Example:
#
#
#     routing domain:
#
#         COMPANY_CLOUD_LLM
#
#
# contains:
#
#
#     Service A
#
#         company proprietary model
#
#         deployment:
#             AWS / US
#
#
#     Service B
#
#         company proprietary model
#
#         deployment:
#             Azure / US
#
#
#     Service C
#
#         company proprietary model
#
#         deployment:
#             GCP / EU
#
#
# Company-cloud routing may generally be permitted.
#
# But Service C might be prohibited for a particular dataset because
# of residency or jurisdiction requirements.
#
#
# Future policy evaluation may therefore consume:
#
#
#     service identity
#
#     model identity
#
#     deployment identity
#
#     cloud provider
#
#     region
#
#     jurisdiction
#
#     data residency
#
#     governance state
#
#     customer restrictions
#
#     regulatory requirements
#
#
# This does NOT imply:
#
#
#     AIRoute.COMPANY_AWS_LLM
#
#     AIRoute.COMPANY_AZURE_LLM
#
#     AIRoute.COMPANY_GCP_LLM
#
#
# Instead:
#
#
#     POLICY EVALUATION BECOMES MORE PRECISE
#
# while:
#
#     ROUTING DOMAIN REMAINS STABLE
#
#
# Therefore:
#
#
#     POLICY PRECISION != AIRoute EXPANSION
#
#
#     POLICY MAY BECOME MORE PRECISE
#     WITHOUT MAKING AIRoute MORE SPECIFIC
#
#
# Part III expands this multi-cloud policy model in depth.
# ==========================================================================


# ==========================================================================
# POLICY IS NOT ROUTING OPTIMIZATION
# ==========================================================================
#
# Never create:
#
#
#     policy_score = 0.8
#
#
# and combine it with:
#
#
#     quality_score
#
#     cost_score
#
#     latency_score
#
#
# into:
#
#
#     routing_score
#
#
# Authorization is not a preference.
#
#
# A route is not:
#
#
#     80% authorized
#
#
# If required authorization is not established:
#
#
#     the destination does not enter the viable optimization set.
#
#
# Therefore:
#
#
#     POLICY IS A CONSTRAINT
#
#
#     POLICY IS NOT A PREFERENCE
#
#
#     POLICY IS NOT AN OPTIMIZATION WEIGHT
#
#
#     POLICY NEVER BECOMES A SCORE
#
#
#     OPTIMIZATION NEVER CREATES AUTHORIZATION
# ==========================================================================


# ==========================================================================
# EXAMPLE — ALLOW
# ==========================================================================
#
#     decision = PolicyDecision(
#         request_id=request.request_id,
#         routing_domain=AIRoute.COMPANY_ONPREM_LLM,
#         status=PolicyDecisionStatus.ALLOW,
#         reason=(
#             "The company on-premises routing domain is authorized "
#             "for this request."
#         ),
#     )
#
#
# This authorizes the domain.
#
# It does not select it.
#
#
#     ALLOW != SELECTED
# ==========================================================================


# ==========================================================================
# EXAMPLE — DENY
# ==========================================================================
#
#     decision = PolicyDecision(
#         request_id=request.request_id,
#         routing_domain=AIRoute.EXTERNAL_FM,
#         status=PolicyDecisionStatus.DENY,
#         reason=(
#             "External foundation models are prohibited for "
#             "this request classification."
#         ),
#     )
#
#
# The candidate may later be summarized by routing as:
#
#
#     RoutingCandidateStatus.REJECTED
#
#     RoutingRejectionReason.POLICY_DENIED
#
#
# Notice:
#
#
#     PolicyDecision
#
# and:
#
#     RoutingCandidate
#
#
# remain separate domain objects.
# ==========================================================================


# ==========================================================================
# EXAMPLE — RESTRICT
# ==========================================================================
#
#     decision = PolicyDecision(
#         request_id=request.request_id,
#         routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#         status=PolicyDecisionStatus.RESTRICT,
#         reason=(
#             "Company-cloud AI is permitted only under additional "
#             "deployment restrictions."
#         ),
#     )
#
#
# SEIR-I preserves the policy result.
#
#
# It does NOT pretend to have a universal schema for every possible
# restriction.
#
#
# Future SEIR-II may introduce typed restriction contracts.
# ==========================================================================


# ==========================================================================
# EXAMPLE — INDETERMINATE
# ==========================================================================
#
#     decision = PolicyDecision(
#         request_id=request.request_id,
#         routing_domain=AIRoute.COMPANY_CLOUD_LLM,
#         status=PolicyDecisionStatus.INDETERMINATE,
#         reason=(
#             "Required policy information could not be resolved."
#         ),
#     )
#
#
# Safe routing behavior:
#
#
#     DO NOT TREAT THIS DOMAIN AS AUTHORIZED
#
#
# But preserve:
#
#
#     status = INDETERMINATE
#
#
# Do not mutate it into:
#
#
#     status = DENY
#
#
# simply because the operational action is conservative.
#
#
#     FAIL CLOSED != FALSIFY OBSERVED STATE
# ==========================================================================


# ==========================================================================
# CHEWBACCA REVIEWS PolicyDecision
# ==========================================================================
#
# Chewbacca:
#
#     "External FM is healthy."
#
#
# Policy Engine:
#
#     IRRELEVANT TO MY QUESTION.
#
#
# Chewbacca:
#
#     "It is reachable."
#
#
# Policy Engine:
#
#     STILL NOT MY QUESTION.
#
#
# Chewbacca:
#
#     "It is cheaper."
#
#
# Policy Engine:
#
#     DEFINITELY NOT MY QUESTION.
#
#
# Chewbacca:
#
#     "Fine. May this request use EXTERNAL_FM?"
#
#
# Policy Engine:
#
#     DENY.
#
#
# Chewbacca:
#
#     "May it use COMPANY_ONPREM_LLM?"
#
#
# Policy Engine:
#
#     ALLOW.
#
#
# Chewbacca:
#
#     "So select on-prem?"
#
#
# Policy Engine:
#
#     THAT IS ROUTING'S JOB.
#
#
# Chewbacca:
#
#     "What if I cannot determine the policy?"
#
#
# Policy Engine:
#
#     INDETERMINATE.
#
#
# Chewbacca:
#
#     "So I assume ALLOW?"
#
#
# Agent 11:
#
#     ABSOLUTELY NOT.
#
#
#     FAIL CLOSED.
#
#
# Chewbacca:
#
#     "Then I'll record DENY."
#
#
# Agent 11:
#
#     ALSO NO.
#
#
#     THE POLICY RESULT IS STILL INDETERMINATE.
#
#
# Chewbacca:
#
#     "Same action, different fact?"
#
#
# Agent 11:
#
#     EXACTLY.
#
#
# Chewbacca:
#
#     "Pydantic validator?"
#
#
# Agent 11:
#
#     THERE IS NO CROSS-FIELD INVARIANT TO VALIDATE HERE.
#
#
# Chewbacca:
#
#     "So zero validators?"
#
#
# Agent 11:
#
#     RESTRAINT IS ALSO ARCHITECTURE.
# ==========================================================================


# ==========================================================================
# PART II — FINAL INVARIANTS
# ==========================================================================
#
#     PolicyDecision = POLICY EVALUATION RESULT
#
#
#     POLICY CONFIGURATION != POLICY EVALUATION
#
#
#     POLICY RULE != POLICY DECISION
#
#
#     POLICY EFFECT != POLICY DECISION STATUS
#
#
#     POLICY DECISION REFERENCES REQUEST
#
#
#     POLICY DECISION DOES NOT OWN REQUEST
#
#
#     SEIR-I POLICY TARGET = ROUTING DOMAIN
#
#
#     ROUTING DOMAIN != SERVICE
#
#
#     ROUTING DOMAIN != MODEL
#
#
#     ROUTING DOMAIN != DEPLOYMENT
#
#
#     ROUTING DOMAIN != CLOUD PROVIDER
#
#
#     POLICY DECISION STATUS
#         !=
#     BOOLEAN AUTHORIZATION FLAG
#
#
#     ALLOW != CAPABLE
#
#
#     ALLOW != AVAILABLE
#
#
#     ALLOW != REACHABLE
#
#
#     ALLOW != VIABLE
#
#
#     ALLOW != SELECTED
#
#
#     DENY != SERVICE FAILURE
#
#
#     DENY != NETWORK FAILURE
#
#
#     DENY != CAPABILITY FAILURE
#
#
#     RESTRICT != ALLOW
#
#
#     RESTRICT != DENY
#
#
#     RESTRICT != INDETERMINATE
#
#
#     RESTRICTION STATUS != RESTRICTION DETAILS
#
#
#     INDETERMINATE != ALLOW
#
#
#     INDETERMINATE != DENY
#
#
#     INDETERMINATE => FAIL CLOSED
#
#
#     FAIL CLOSED != FALSIFY OBSERVED STATE
#
#
#     DECISION BEHAVIOR != OBSERVED TRUTH
#
#
#     HUMAN EXPLANATION != MACHINE CONTRACT
#
#
#     REASON TEXT != POLICY SEMANTICS
#
#
#     EFFECTIVE POLICY
#         =
#     ORGANIZATION POLICY
#         INTERSECTION
#     USER POLICY
#
#
#     USER MAY NARROW
#
#
#     USER MAY NOT EXPAND
#
#
#     LOWER AUTHORITY MAY NARROW
#
#
#     LOWER AUTHORITY MAY NOT EXPAND
#
#
#     POLICY COMPOSITION != MAJORITY VOTE
#
#
#     POLICY SOURCE COUNT != POLICY AUTHORITY
#
#
#     POLICY ALLOW != VIABLE CANDIDATE
#
#
#     POLICY DECISION != ROUTING DECISION
#
#
#     POLICY MODEL != POLICY ENGINE
#
#
#     ORGANIZATIONAL POLICY != PYDANTIC INVARIANT
#
#
#     POLICY DECISION != POLICY EVIDENCE
#
#
#     DECISION != PROVENANCE
#
#
#     REFERENCE EVIDENCE
#
#     DO NOT DUPLICATE EVIDENCE
#
#
#     POLICY PRECISION != AIRoute EXPANSION
#
#
#     POLICY MAY BECOME MORE PRECISE
#     WITHOUT MAKING AIRoute MORE SPECIFIC
#
#
#     POLICY IS A CONSTRAINT
#
#
#     POLICY IS NOT A PREFERENCE
#
#
#     POLICY IS NOT AN OPTIMIZATION WEIGHT
#
#
#     POLICY NEVER BECOMES A SCORE
#
#
#     OPTIMIZATION NEVER CREATES AUTHORIZATION
#
#
#     VALIDATION SHOULD REPRESENT A RULE
#
#
#     VALIDATION SHOULD NOT BE DECORATION
#
#
#     KNOWING HOW TO WRITE A VALIDATOR
#         !=
#     NEEDING A VALIDATOR
#
#
#     PYDANTIC DEFINES THE DOMAIN CONTRACT
#
#     POLICY BEHAVIOR PRODUCES THE DOMAIN OBJECT
# ==========================================================================
# END PART II
# ==========================================================================

# ==========================================================================
# PART III — POLICY SEMANTICS AND SEIR-II EXPANSION — DO NOT DELETE
# ==========================================================================
#
# THIS SECTION IS ARCHITECTURAL DOCUMENTATION ONLY.
#
#
# Part I defined:
#
#
#     DataRoutePolicy
#
#         WHAT IS POLICY CONFIGURED TO SAY?
#
#
# Part II defined:
#
#
#     PolicyDecision
#
#         WHAT DID POLICY EVALUATION CONCLUDE?
#
#
# Part III preserves:
#
#
#     WHAT MUST REMAIN TRUE AS AGENT 11 POLICY
#     BECOMES MORE SOPHISTICATED?
#
#
# This section intentionally introduces:
#
#
#     NO executable policy behavior
#
#     NO additional Pydantic fields
#
#     NO additional validators
#
#     NO cloud-provider dependencies
#
#     NO policy-engine dependencies
#
#     NO routing behavior
#
#     NO network behavior
#
#     NO premature SEIR-II abstractions
#
#
# The purpose is:
#
#
#     PRESERVE THE FUTURE PROBLEM.
#
#     DO NOT PRETEND TO HAVE THE FUTURE SOLUTION.
#
#
# Agent 11 is intentionally simple enough for SEIR-I.
#
# That simplicity must not accidentally create architectural assumptions
# that make SEIR-II impossible.
#
#
# Therefore:
#
#
#     SIMPLE TODAY SHOULD NOT MEAN IMPOSSIBLE TOMORROW
#
#
#     FUTURE-AWARE != FUTURE-BLOATED
#
#
# The comments below are a letter from the SEIR-I implementation to the
# future SEIR-II implementation.
#
#
#     DO NOT DELETE THE LETTER
#
# ==========================================================================


# ==========================================================================
# THE PERMANENT POLICY BOUNDARY
# ==========================================================================
#
# Policy answers:
#
#
#     "MAY THIS REQUEST USE THIS DESTINATION?"
#
#
# Policy does NOT answer:
#
#
#     "Can this model perform the requested work?"
#
#     "Is this service operationally healthy?"
#
#     "Can the network reach this service?"
#
#     "Is this destination inexpensive?"
#
#     "Is this destination fast?"
#
#     "Is this the preferred destination?"
#
#     "Should routing select this destination?"
#
#
# Those questions belong to neighboring domains.
#
#
#     POLICY
#
#         MAY WE?
#
#
#     CAPABILITY
#
#         CAN IT DO THE WORK?
#
#
#     SERVICE STATE
#
#         IS IT OPERATIONALLY AVAILABLE?
#
#
#     NETWORK
#
#         CAN WE REACH IT?
#
#
#     ROUTING
#
#         WHICH VIABLE DESTINATION SHOULD WE USE?
#
#
# These questions may eventually be evaluated by one orchestration
# workflow.
#
# That does not make them the same domain.
#
#
#     POLICY != CAPABILITY
#
#     POLICY != SERVICE HEALTH
#
#     POLICY != NETWORK
#
#     POLICY != ROUTING
#
#
# Orchestration may coordinate domains.
#
# Coordination does not erase domain ownership.
#
#
#     COORDINATION != OWNERSHIP
#
# ==========================================================================


# ==========================================================================
# THE VIABLE ROUTE CONTRACT
# ==========================================================================
#
# Policy participates in a larger Agent 11 viability decision.
#
#
#     VIABLE ROUTE
#
#         =
#
#     POLICY PERMITTED
#
#         +
#
#     SERVICE CAPABLE
#
#         +
#
#     SERVICE AVAILABLE
#
#         +
#
#     PATH AVAILABLE
#
#
# Every term answers a different question.
#
#
# A destination can be:
#
#
#     reachable
#
# but:
#
#     unauthorized
#
#
# A destination can be:
#
#
#     authorized
#
# but:
#
#     unreachable
#
#
# A destination can be:
#
#
#     healthy
#
# but:
#
#     prohibited
#
#
# A destination can be:
#
#
#     inexpensive
#
# but:
#
#     prohibited
#
#
# Therefore:
#
#
#     REACHABLE != AUTHORIZED
#
#     AUTHORIZED != REACHABLE
#
#     HEALTHY != PERMITTED
#
#     CAPABLE != AUTHORIZED
#
#     CHEAPER != PERMITTED
#
#     FASTER != PERMITTED
#
#
# Policy contributes authorization.
#
# Policy does not create the other viability facts.
# ==========================================================================


# ==========================================================================
# EFFECTIVE POLICY
# ==========================================================================
#
# SEIR-I begins with a deliberately simple authority model:
#
#
#     EFFECTIVE POLICY
#
#         =
#
#     ORGANIZATION POLICY
#
#         INTERSECTION
#
#     USER POLICY
#
#
# This establishes a foundational authority rule:
#
#
#     USER MAY NARROW
#
#     USER MAY NOT EXPAND
#
#
# Example:
#
#
# Organization permits:
#
#
#     EXTERNAL_FM
#
#     COMPANY_CLOUD_LLM
#
#     COMPANY_ONPREM_LLM
#
#
# User chooses:
#
#
#     ONPREM_ONLY
#
#
# Effective authorization becomes:
#
#
#     COMPANY_ONPREM_LLM
#
#
# The user removed destinations.
#
# Good.
#
#
# But suppose organization policy permits only:
#
#
#     COMPANY_ONPREM_LLM
#
#
# The user cannot request:
#
#
#     EXTERNAL_FM
#
#
# and thereby create authorization.
#
#
# Therefore:
#
#
#     PREFERENCE != AUTHORITY
#
#
#     LOWER AUTHORITY MAY NARROW
#
#     LOWER AUTHORITY MAY NOT EXPAND
#
# ==========================================================================


# ==========================================================================
# SEIR-II — POLICY AUTHORITY HIERARCHY
# ==========================================================================
#
# Real enterprise policy will eventually be more complicated than:
#
#
#     ORGANIZATION + USER
#
#
# Future authority layers may include:
#
#
#     ORGANIZATION POLICY
#             |
#             v
#     BUSINESS UNIT POLICY
#             |
#             v
#     APPLICATION POLICY
#             |
#             v
#     WORKLOAD POLICY
#             |
#             v
#     AGENT POLICY
#             |
#             v
#     USER RESTRICTION
#             |
#             v
#       EFFECTIVE POLICY
#
#
# The exact hierarchy is intentionally NOT implemented in SEIR-I.
#
#
# SEIR-II will need to define concepts such as:
#
#
#     authority
#
#     precedence
#
#     inheritance
#
#     narrowing
#
#     conflicts
#
#     exceptions
#
#
# IMPORTANT:
#
#
#     POLICY COMPOSITION != MAJORITY VOTE
#
#
# Example:
#
#
#     Business Unit:
#         ALLOW
#
#     Application:
#         ALLOW
#
#     User:
#         ALLOW
#
#     Organization:
#         DENY
#
#
# This is NOT:
#
#
#     3 ALLOW
#     1 DENY
#
#     therefore ALLOW wins.
#
#
# Policy sources have authority.
#
# They are not votes.
#
#
# Therefore:
#
#
#     POLICY SOURCE COUNT != POLICY AUTHORITY
#
#
#     POLICY SOURCE != POLICY PRECEDENCE
#
#
#     LOWER AUTHORITY MAY NARROW
#
#     LOWER AUTHORITY MAY NOT EXPAND
#
# ==========================================================================


# ==========================================================================
# INDETERMINATE MUST SURVIVE SEIR-II
# ==========================================================================
#
# Future policy evaluation may depend on:
#
#
#     external policy engines
#
#     identity systems
#
#     classification systems
#
#     governance catalogs
#
#     deployment metadata
#
#     regulatory data
#
#     customer restrictions
#
#     residency information
#
#
# Sometimes Agent 11 will not be able to establish authorization.
#
#
# PolicyDecision must preserve:
#
#
#     INDETERMINATE
#
#
# Agent 11 should then fail closed.
#
#
# But:
#
#
#     INDETERMINATE != DENY
#
#
# DENY means:
#
#
#     POLICY EXPLICITLY PROHIBITED THE OPERATION
#
#
# INDETERMINATE means:
#
#
#     AUTHORIZATION COULD NOT BE ESTABLISHED
#
#
# Operational behavior may be similar:
#
#
#     DO NOT USE THE DESTINATION
#
#
# But operational meaning is different.
#
#
# DENY may indicate:
#
#
#     successful policy enforcement
#
#
# while INDETERMINATE may indicate:
#
#
#     missing evidence
#
#     policy-service failure
#
#     unresolved identity
#
#     incomplete deployment metadata
#
#     policy conflict
#
#
# Telemetry must be able to distinguish these situations.
#
#
# Therefore:
#
#
#     INDETERMINATE != DENY
#
#
#     FAIL CLOSED != ERASE SEMANTICS
#
#
#     FAIL CLOSED != FALSIFY OBSERVED STATE
#
#
#     CONSERVATIVE ACTION != FALSE OBSERVATION
#
# ==========================================================================


# ==========================================================================
# SEIR-II — RESTRICT MUST EVENTUALLY HAVE MEANING
# ==========================================================================
#
# SEIR-I preserves:
#
#
#     PolicyDecisionStatus.RESTRICT
#
#
# without pretending to know every future restriction type.
#
#
# Future restrictions may include:
#
#
#     approved regions only
#
#     approved countries only
#
#     approved deployments only
#
#     approved model families only
#
#     approved service operators only
#
#     human approval required
#
#     enhanced logging required
#
#     reduced data scope
#
#     customer-specific restrictions
#
#     residency requirements
#
#     retention requirements
#
#
# When those requirements become real, prefer typed domain contracts.
#
#
# Avoid turning restrictions into:
#
#
#     restrictions: dict[str, Any]
#
#
# containing:
#
#
#     {
#         "whatever": "special",
#         "probably_ok": True,
#         "bob_said": "US only"
#     }
#
#
# That does not model policy.
#
# It hides policy inside an untyped dictionary.
#
#
# Therefore:
#
#
#     RESTRICT != UNTYPED POLICY BAG
#
#
#     RESTRICTION STATUS != RESTRICTION DETAILS
#
#
#     UNKNOWN FUTURE REQUIREMENT
#         !=
#     EXCUSE FOR UNBOUNDED dict[str, Any]
#
#
# When the domain becomes known:
#
#
#     MODEL THE DOMAIN
# ==========================================================================


# ==========================================================================
# SEIR-II — POLICY PRECISION WITHOUT AIRoute EXPANSION
# ==========================================================================
#
# SEIR-I policy primarily evaluates:
#
#
#     DATA CLASSIFICATION
#
#              +
#
#     ROUTING DOMAIN
#
#
# Future policy may additionally consume:
#
#
#     model identity
#
#     service identity
#
#     deployment identity
#
#     cloud provider
#
#     region
#
#     country
#
#     jurisdiction
#
#     data residency
#
#     sovereignty requirements
#
#     governance state
#
#     customer
#
#     tenant
#
#     regulatory context
#
#
# This means:
#
#
#     POLICY BECOMES MORE PRECISE
#
#
# It does NOT mean:
#
#
#     AIRoute BECOMES MORE PRECISE
#
#
# These are independent dimensions.
#
#
# Therefore:
#
#
#     POLICY PRECISION != ROUTING DOMAIN EXPANSION
#
#
#     POLICY MAY BECOME MORE PRECISE
#     WITHOUT MAKING AIRoute MORE SPECIFIC
# ==========================================================================


# ==========================================================================
# SEIR-II — MULTI-CLOUD POLICY — DO NOT DELETE
# ==========================================================================
#
# COMPANY_CLOUD_LLM is intentionally provider-neutral.
#
#
# Future company reasoning infrastructure may look like:
#
#
#                       COMPANY_CLOUD_LLM
#
#                               |
#
#              +----------------+----------------+
#              |                |                |
#              v                v                v
#             AWS             AZURE             GCP
#              |                |                |
#              v                v                v
#        Deployment A     Deployment B     Deployment C
#                                               |
#                                               |
#                                               v
#                                              OCI
#                                               |
#                                               v
#                                         Deployment D
#
#
# More accurately, these deployments are siblings under the same
# company-cloud routing domain:
#
#
#                       COMPANY_CLOUD_LLM
#
#              +----------+----------+----------+
#              |          |          |          |
#              v          v          v          v
#             AWS       AZURE       GCP        OCI
#
#
# Policy may generally permit:
#
#
#     COMPANY_CLOUD_LLM
#
#
# while applying additional restrictions to individual deployments.
#
#
# Example:
#
#
#     AWS / US
#         ALLOW
#
#
#     Azure / US
#         ALLOW
#
#
#     GCP / EU
#         DENY for this dataset
#
#
#     OCI / US
#         ALLOW
#
#
# This does NOT require:
#
#
#     AIRoute.COMPANY_AWS_LLM
#
#     AIRoute.COMPANY_AZURE_LLM
#
#     AIRoute.COMPANY_GCP_LLM
#
#     AIRoute.COMPANY_OCI_LLM
#
#
# Those values would confuse:
#
#
#     ROUTING DOMAIN
#
# with:
#
#     DEPLOYMENT PROVIDER
#
#
# Future deployment/provider/location attributes become INPUTS to
# policy evaluation.
#
#
# Therefore:
#
#
#     ROUTING DOMAIN != CLOUD PROVIDER
#
#
#     ROUTING DOMAIN != DEPLOYMENT LOCATION
#
#
#     DEPLOYMENT LOCATION MAY INFORM POLICY
#
#
#     DEPLOYMENT LOCATION DOES NOT DEFINE AIRoute
#
#
#     MULTI-CLOUD != MULTIPLY AIRoute VALUES
# ==========================================================================


# ==========================================================================
# SEIR-II — MODEL OWNERSHIP != DEPLOYMENT LOCATION
# ==========================================================================
#
# A company-owned proprietary model may run:
#
#
#     on-premises
#
#     AWS
#
#     Azure
#
#     GCP
#
#     OCI
#
#     another future infrastructure provider
#
#
# Therefore:
#
#
#     PROPRIETARY MODEL != ON-PREMISES MODEL
#
#
# Consider these as independent facts:
#
#
#     MODEL IDENTITY
#
#     MODEL OWNER
#
#     MODEL PROVIDER / ORIGIN
#
#     SERVICE OPERATOR
#
#     DEPLOYMENT PROVIDER
#
#     DEPLOYMENT LOCATION
#
#     ROUTING DOMAIN
#
#     POLICY AUTHORIZATION
#
#
# Example:
#
#
#     model owner:
#
#         COMPANY
#
#
#     deployment provider:
#
#         GCP
#
#
#     routing domain:
#
#         COMPANY_CLOUD_LLM
#
#
# There is no contradiction.
#
#
# Likewise:
#
#
#     provider:
#
#         ANTHROPIC
#
#
#     service operator:
#
#         COMPANY
#
#
#     deployment/access environment:
#
#         AWS
#
#
#     routing domain:
#
#         COMPANY_CLOUD_LLM
#
#
# may describe a completely different enterprise arrangement.
#
#
# Do not infer one fact from another unless the domain explicitly
# guarantees that relationship.
#
#
# Therefore:
#
#
#     MODEL IDENTITY != DEPLOYMENT IDENTITY
#
#
#     MODEL PROVIDER != DEPLOYMENT PROVIDER
#
#
#     MODEL OWNERSHIP != ROUTING DOMAIN
#
#
#     CLOUD PROVIDER != MODEL OWNER
#
#
#     ROUTING DOMAIN != MODEL PROVIDER
# ==========================================================================


# ==========================================================================
# SEIR-II — DEPLOYMENT CONTEXT
# ==========================================================================
#
# Future policy may need a richer deployment concept.
#
#
# A future deployment contract might eventually describe:
#
#
#     deployment_id
#
#     service_id
#
#     cloud_provider
#
#     region
#
#     account
#
#     subscription
#
#     project
#
#     tenancy
#
#     cluster
#
#     endpoint
#
#     residency boundary
#
#     sovereignty boundary
#
#     failure domain
#
#     private connectivity
#
#
# DO NOT add these fields to AIRoute.
#
#
# DO NOT automatically add these fields to PolicyDecision.
#
#
# They belong to the deployment/runtime domain.
#
#
# Policy may consume them.
#
#
# Therefore:
#
#
#     POLICY CONSUMES DEPLOYMENT FACTS
#
#
#     POLICY DOES NOT OWN DEPLOYMENT FACTS
#
#
#     INPUT TO POLICY != FIELD ON PolicyDecision
# ==========================================================================


# ==========================================================================
# SEIR-II — DATA RESIDENCY
# ==========================================================================
#
# Future policy may need to evaluate:
#
#
#     WHERE MAY THIS DATA BE PROCESSED?
#
#
# That may depend on:
#
#
#     country
#
#     region
#
#     customer
#
#     contract
#
#     classification
#
#     regulation
#
#     deployment
#
#
# Example:
#
#
#     COMPANY_CLOUD_LLM
#
# may be authorized in principle.
#
#
# But:
#
#
#     GCP / europe-west...
#
#
# may be prohibited for a particular dataset.
#
#
# This does not mean:
#
#
#     COMPANY_CLOUD_LLM
#
# itself is globally prohibited.
#
#
# It means future policy evaluation has become more precise.
#
#
# Therefore:
#
#
#     ROUTING-DOMAIN AUTHORIZATION
#
# may eventually become one component of:
#
#
#     COMPLETE DEPLOYMENT AUTHORIZATION
#
#
# Again:
#
#
#     POLICY PRECISION != AIRoute EXPANSION
# ==========================================================================


# ==========================================================================
# SEIR-II — SOVEREIGNTY
# ==========================================================================
#
# Data residency and sovereignty are related but should not be assumed
# to be identical.
#
#
# Future requirements may care about:
#
#
#     physical processing location
#
#     legal jurisdiction
#
#     operator control
#
#     administrative access
#
#     encryption-key control
#
#     sovereign-cloud boundary
#
#     organizational ownership
#
#
# A deployment being physically located in an approved country may not
# automatically satisfy every sovereignty requirement.
#
#
# Therefore:
#
#
#     LOCATION != SOVEREIGNTY
#
#
#     RESIDENCY != COMPLETE GOVERNANCE
#
#
# Do not collapse future governance concepts merely because they happen
# to produce the same decision in an early implementation.
# ==========================================================================


# ==========================================================================
# SEIR-II — SUBJECT / IDENTITY-AWARE POLICY
# ==========================================================================
#
# Future authorization may depend on WHO or WHAT initiated the request.
#
#
# Possible subjects include:
#
#
#     human user
#
#     workload identity
#
#     application
#
#     autonomous agent
#
#     service account
#
#     delegated agent
#
#
# Future policy may consume:
#
#
#     identity
#
#     role
#
#     organization
#
#     tenant
#
#     entitlement
#
#     delegation
#
#     authentication strength
#
#     session context
#
#
# Identity systems establish identity facts.
#
#
# Policy evaluates those facts.
#
#
# Therefore:
#
#
#     IDENTITY != POLICY
#
#
#     AUTHENTICATED != AUTHORIZED
#
#
#     KNOWN IDENTITY != PERMITTED ACTION
#
#
#     IDENTITY FACT != POLICY DECISION
# ==========================================================================


# ==========================================================================
# SEIR-II — USER RESTRICTION IS NOT USER AUTHORIZATION
# ==========================================================================
#
# A user may say:
#
#
#     "Do not send my data to external AI."
#
#
# That may narrow organizational authorization.
#
#
# A user may NOT say:
#
#
#     "Send E9 data to an external AI service even though
#      organizational policy prohibits it."
#
#
# and thereby create authorization.
#
#
# Therefore:
#
#
#     USER PREFERENCE MAY REMOVE ROUTES
#
#
#     USER PREFERENCE MAY NOT CREATE PROHIBITED ROUTES
#
#
# This remains true even if a future interface calls the setting:
#
#
#     preference
#
#     privacy choice
#
#     routing preference
#
#     personal policy
#
#
# Names do not create authority.
#
#
#     PREFERENCE != AUTHORIZATION GRANT
# ==========================================================================


# ==========================================================================
# SEIR-II — CUSTOMER-SPECIFIC POLICY
# ==========================================================================
#
# Enterprise AI systems may eventually serve many customers with
# different contractual or governance requirements.
#
#
# Example:
#
#
#     Customer A
#
#         permits company-cloud inference in the United States
#
#
#     Customer B
#
#         requires company on-premises inference
#
#
#     Customer C
#
#         permits only specifically approved cloud deployments
#
#
# The same AI service may therefore be:
#
#
#     authorized for Customer A
#
# and:
#
#     prohibited for Customer B
#
#
# without the service itself changing.
#
#
# Therefore:
#
#
#     SERVICE IDENTITY != UNIVERSAL AUTHORIZATION
#
#
#     AUTHORIZATION MAY DEPEND ON REQUEST CONTEXT
#
#
# This is another reason PolicyDecision represents an evaluated result
# rather than a permanent property of AIService.
# ==========================================================================


# ==========================================================================
# SEIR-II — REGULATORY AND CONTRACTUAL POLICY
# ==========================================================================
#
# Future effective policy may consume requirements originating from:
#
#
#     law
#
#     regulation
#
#     customer contracts
#
#     industry requirements
#
#     organizational governance
#
#     internal security policy
#
#
# Agent 11 should not assume every policy source has:
#
#
#     equal authority
#
#     equal scope
#
#     equal precedence
#
#     equal duration
#
#
# Future policy composition may require explicit source metadata and
# authority relationships.
#
#
# Therefore:
#
#
#     POLICY SOURCE != POLICY AUTHORITY
#
#
#     POLICY SOURCE != POLICY PRECEDENCE
#
#
#     POLICY SOURCE != POLICY SCOPE
#
#
# The source of a policy requirement may matter.
# ==========================================================================


# ==========================================================================
# SEIR-II — POLICY VERSIONING
# ==========================================================================
#
# Future operators will eventually ask:
#
#
#     "Why was this request allowed yesterday
#      but denied today?"
#
#
# One possible answer:
#
#
#     POLICY CHANGED
#
#
# Future audit/provenance may therefore need:
#
#
#     policy identifier
#
#     policy version
#
#     policy source
#
#     effective period
#
#     evaluated_at
#
#
# Do not automatically add all of these fields to PolicyDecision.
#
#
# A future provenance contract may reference the policy evidence used
# to produce the decision.
#
#
# Therefore:
#
#
#     CURRENT POLICY != HISTORICAL POLICY
#
#
#     DECISION != POLICY VERSION DATABASE
#
#
#     POLICY DECISION != POLICY DOCUMENT
# ==========================================================================


# ==========================================================================
# SEIR-II — POLICY PROVENANCE
# ==========================================================================
#
# Future audit requirements may need to reconstruct:
#
#
#     WHICH POLICY SOURCES CONTRIBUTED TO THIS DECISION?
#
#
# Supporting evidence may eventually include:
#
#
#     organization policy
#
#     business-unit policy
#
#     application policy
#
#     user restriction
#
#     classification evidence
#
#     identity evidence
#
#     deployment metadata
#
#     residency requirement
#
#     regulatory requirement
#
#     policy-engine evaluation
#
#
# PolicyDecision should remain a compact result.
#
#
# Future provenance should reference evidence rather than copying
# entire source documents into the decision object.
#
#
# Therefore:
#
#
#     REFERENCE EVIDENCE
#
#
#     DO NOT DUPLICATE EVIDENCE
#
#
#     DECISION != PROVENANCE
#
#
#     AUDITABLE != EVERYTHING IN ONE OBJECT
# ==========================================================================


# ==========================================================================
# POLICY DECISION != POLICY EVIDENCE
# ==========================================================================
#
# PolicyDecision may say:
#
#
#     DENY
#
#
# Supporting evidence may say:
#
#
#     classification:
#         E8
#
#
#     organization policy:
#         version 17
#
#
#     external AI rule:
#         prohibited
#
#
#     user restriction:
#         company only
#
#
# These are different concepts.
#
#
#     DECISION
#
#         =
#
#     RESULT
#
#
#     EVIDENCE
#
#         =
#
#     FACTS SUPPORTING THE RESULT
#
#
# Keeping them separate supports:
#
#
#     audit
#
#     replay
#
#     policy evolution
#
#     alternative policy engines
#
#     compact routing records
#
#
# without turning PolicyDecision into a document store.
#
#
#     POLICY DECISION != POLICY EVIDENCE
# ==========================================================================


# ==========================================================================
# SEIR-II — POLICY EXPLAINABILITY
# ==========================================================================
#
# Future operators may need answers to questions such as:
#
#
#     "Why was this denied?"
#
#
#     "Which rule caused the restriction?"
#
#
#     "Which authority supplied that rule?"
#
#
#     "Which deployment attribute caused the failure?"
#
#
#     "Would another deployment have been permitted?"
#
#
# The current:
#
#
#     reason: str | None
#
#
# is useful human-readable context.
#
#
# It is NOT sufficient as future machine-readable explainability.
#
#
# Future explainability should use typed evidence/provenance structures.
#
#
# Do not turn:
#
#
#     reason
#
# into:
#
#     a hidden policy language.
#
#
# Therefore:
#
#
#     HUMAN EXPLANATION != MACHINE EVIDENCE
#
#
#     REASON TEXT != POLICY PROVENANCE
# ==========================================================================


# ==========================================================================
# SEIR-II — EXTERNAL POLICY ENGINES
# ==========================================================================
#
# Future Agent 11 implementations may evaluate policy using:
#
#
#     custom Python
#
#     OPA / Rego
#
#     Cedar
#
#     cloud-native authorization services
#
#     enterprise authorization platforms
#
#     governance platforms
#
#     future policy technologies
#
#
# The architecture should permit:
#
#
#     External Policy Engine
#             |
#             v
#         Adapter Layer
#             |
#             v
#       PolicyDecision
#
#
# The external engine may have:
#
#
#     different vocabulary
#
#     different APIs
#
#     different rule languages
#
#     different deployment models
#
#
# Agent 11 adapters translate those technologies into Agent 11 domain
# semantics.
#
#
# Therefore:
#
#
#     POLICY ENGINE != POLICY DOMAIN CONTRACT
#
#
#     POLICY ENGINE TECHNOLOGY MAY CHANGE
#
#
#     POLICY SEMANTICS SHOULD SURVIVE
#
#
# Do not make PolicyDecision an OPA object.
#
# Do not make PolicyDecision a Cedar object.
#
# Do not make PolicyDecision a cloud-provider authorization object.
#
#
# It is an:
#
#
#     AGENT 11 DOMAIN OBJECT
# ==========================================================================


# ==========================================================================
# SEIR-II — POLICY NEVER BECOMES A SCORE
# ==========================================================================
#
# Future routing may optimize among viable candidates using:
#
#
#     quality
#
#     latency
#
#     cost
#
#     capacity
#
#     locality
#
#     failure domain
#
#     model preference
#
#
# Policy does NOT become:
#
#
#     policy_score = 0.73
#
#
# and join:
#
#
#     quality_score
#
#     latency_score
#
#     cost_score
#
#
# in a weighted average.
#
#
# Authorization is a required constraint.
#
#
# There is no meaningful:
#
#
#     "73% authorized."
#
#
# If required policy authorization is not established:
#
#
#     THE CANDIDATE DOES NOT ENTER OPTIMIZATION
#
#
# Therefore:
#
#
#     POLICY IS A CONSTRAINT
#
#
#     POLICY IS NOT A PREFERENCE
#
#
#     POLICY IS NOT AN OPTIMIZATION WEIGHT
#
#
#     POLICY NEVER BECOMES A SCORE
#
#
#     OPTIMIZATION NEVER CREATES AUTHORIZATION
# ==========================================================================


# ==========================================================================
# SEIR-II — CHEAPER != PERMITTED
# ==========================================================================
#
# Example:
#
#
#     External Model
#
#         policy:
#             DENY
#
#         cost:
#             $0.001
#
#
#     Company Model
#
#         policy:
#             ALLOW
#
#         cost:
#             $0.010
#
#
# Routing does NOT calculate:
#
#
#     "The external model is ten times cheaper,
#      so perhaps DENY is negotiable."
#
#
# No.
#
#
# The policy-denied destination never enters the viable optimization
# set.
#
#
# Therefore:
#
#
#     CHEAPER != PERMITTED
#
#
#     FASTER != PERMITTED
#
#
#     BETTER MODEL != PERMITTED
#
#
#     HIGHER QUALITY != PERMITTED
#
#
#     MORE AVAILABLE != PERMITTED
#
#
# Optimization occurs among policy-eligible candidates.
# ==========================================================================


# ==========================================================================
# SEIR-II — EMERGENCY POLICY != POLICY BYPASS
# ==========================================================================
#
# Production incidents may eventually create pressure:
#
#
#     "The company model is down."
#
#
#     "The external model is available."
#
#
#     "We need an answer immediately."
#
#
# If organizational requirements permit emergency behavior, then
# define:
#
#
#     EMERGENCY POLICY
#
#
# with explicit:
#
#
#     authority
#
#     scope
#
#     duration
#
#     eligible data
#
#     eligible destinations
#
#     approval requirements
#
#     audit requirements
#
#
# Do NOT implement:
#
#
#     if outage:
#         ignore_policy()
#
#
# Do NOT implement:
#
#
#     if important_customer:
#         ignore_policy()
#
#
# Do NOT implement:
#
#
#     if latency_is_bad:
#         ignore_policy()
#
#
# Therefore:
#
#
#     AVAILABILITY PRESSURE != POLICY EXCEPTION
#
#
#     BUSINESS PRESSURE != POLICY EXCEPTION
#
#
#     EMERGENCY POLICY != ROUTER BYPASS
#
#
#     URGENCY != AUTHORIZATION
# ==========================================================================


# ==========================================================================
# FAIL CLOSED
# ==========================================================================
#
# Agent 11 must establish required authorization before using a
# destination.
#
#
# If required authorization cannot be established:
#
#
#     DO NOT USE THE DESTINATION
#
#
# But preserve WHY:
#
#
#     DENY
#
# or:
#
#     INDETERMINATE
#
#
# Those may produce similar conservative behavior while representing
# different operational conditions.
#
#
# Therefore:
#
#
#     FAIL CLOSED
#
# does NOT mean:
#
#     SEMANTICALLY LABEL EVERYTHING DENY
#
#
# It means:
#
#
#     REQUIRE AUTHORIZATION BEFORE USE
#
#
# Therefore:
#
#
#     FAIL CLOSED != DENY EVERYTHING SEMANTICALLY
#
#
#     FAIL CLOSED = REQUIRE AUTHORIZATION BEFORE USE
# ==========================================================================


# ==========================================================================
# POLICY AND ROUTING
# ==========================================================================
#
# Conceptually:
#
#
#       PolicyDecision
#            |
#            v
#     Candidate Evaluation
#            |
#            +------ Capability
#            |
#            +------ Service State
#            |
#            +------ Network State
#            |
#            v
#      RoutingCandidate
#            |
#            v
#      RoutingDecision
#
#
# Policy contributes:
#
#
#     AUTHORIZATION FACT
#
#
# Routing combines that fact with neighboring domain facts.
#
#
# Therefore:
#
#
#     ROUTING CONSUMES POLICY
#
#
#     ROUTING DOES NOT BECOME POLICY
#
#
#     POLICY DOES NOT BECOME ROUTING
#
#
# This separation becomes MORE important as both systems become more
# sophisticated.
# ==========================================================================


# ==========================================================================
# POLICY AND FALLBACK
# ==========================================================================
#
# Fallback never means:
#
#
#     TRY A LESS AUTHORIZED DESTINATION
#
#
# Fallback means:
#
#
#     RE-EVALUATE ANOTHER DESTINATION
#
#
# under the same required policy constraints.
#
#
# Example:
#
#
#     COMPANY_CLOUD_LLM
#
#         authorized
#         unavailable
#
#
#     COMPANY_ONPREM_LLM
#
#         authorized
#         available
#
#
# Fallback may choose the on-premises destination.
#
#
# But:
#
#
#     COMPANY_CLOUD_LLM
#
#         authorized
#         unavailable
#
#
#     EXTERNAL_FM
#
#         prohibited
#         available
#
#
# does NOT make EXTERNAL_FM a valid fallback.
#
#
# Therefore:
#
#
#     FALLBACK != IGNORE POLICY
#
#
#     FALLBACK != REDUCE SECURITY REQUIREMENTS
#
#
#     FALLBACK = ANOTHER INDEPENDENT VIABILITY EVALUATION
#
#
# Availability may decrease.
#
# Security policy does not.
# ==========================================================================


# ==========================================================================
# SEIR-II — REASONING POLICY VS TOOL POLICY
# ==========================================================================
#
# Agent 11 will eventually coordinate:
#
#
#     AI REASONING
#
# and:
#
#     MCP / TOOL EXECUTION
#
#
# These are related governance problems.
#
# They are not identical authorization decisions.
#
#
# Conceptually:
#
#
#     Reasoning Request
#          |
#          v
#     AI Routing Policy
#
#
#     Tool Request
#          |
#          v
#     MCP / Tool Authorization
#
#
# Permission to send information to an AI reasoning service does NOT
# automatically grant permission to execute a tool.
#
#
# Example:
#
#
# An AI model may be permitted to reason about:
#
#
#     "What would happen if the production database were deleted?"
#
#
# That does NOT mean the model is authorized to:
#
#
#     DELETE THE PRODUCTION DATABASE
#
#
# Therefore:
#
#
#     REASONING AUTHORIZATION != TOOL AUTHORIZATION
#
#
#     AI ROUTING POLICY != MCP EXECUTION POLICY
#
#
#     ABILITY TO RECOMMEND ACTION
#         !=
#     AUTHORITY TO EXECUTE ACTION
# ==========================================================================


# ==========================================================================
# SEIR-II — POLICY AS A JUDGMENT DAY AS CODE BOUNDARY
# ==========================================================================
#
# Dangerous architecture:
#
#
#     AI CAPABILITY
#
#         +
#
#     UNBOUNDED AUTHORITY
#
#         +
#
#     AUTOMATED EXECUTION
#
#         +
#
#     POOR GOVERNANCE
#
#         =
#
#     JUDGMENT DAY AS CODE
#
#
# Safer architecture:
#
#
#     REASONING
#         |
#         v
#     POLICY GATES
#         |
#         v
#     SCOPED AUTHORITY
#         |
#         v
#     APPROVED EXECUTION
#         |
#         v
#     AUDIT / PROVENANCE
#
#
# Human approval may also exist where risk requires it.
#
#
# The important architectural separation is:
#
#
#     REASONING CAPABILITY != EXECUTION AUTHORITY
#
#
#     INTELLIGENCE != AUTHORIZATION
#
#
#     MODEL OUTPUT != ACTION AUTHORITY
#
#
# Increasing model intelligence must not silently increase authority.
# ==========================================================================


# ==========================================================================
# SEIR-II — POLICY IN THE AI CONTROL PLANE
# ==========================================================================
#
# Future Agent 11 increasingly resembles an AI control plane.
#
#
#                         AGENT 11
#
#              +-------------+-------------+
#              |             |             |
#              v             v             v
#           POLICY        ROUTING      GOVERNANCE
#              |             |             |
#              +-------------+-------------+
#                            |
#                            v
#                       AI SERVICES
#
#
# Policy is one control-plane responsibility.
#
#
# Agent 11 may coordinate policy facts obtained from:
#
#
#     identity systems
#
#     governance systems
#
#     deployment registries
#
#     regulatory systems
#
#     policy engines
#
#
# Agent 11 does not therefore need to become:
#
#
#     the identity provider
#
#     the regulatory database
#
#     the policy language
#
#     the cloud control plane
#
#     the network controller
#
#
# Therefore:
#
#
#     COORDINATION != OWNERSHIP OF EVERYTHING
#
#
#     CONTROL PLANE != GIANT GOD OBJECT
# ==========================================================================


# ==========================================================================
# DO NOT TURN PolicyDecision INTO THE ENTIRE POLICY SYSTEM
# ==========================================================================
#
# Future engineers may be tempted to add:
#
#
#     user_id
#
#     role
#
#     organization
#
#     business_unit
#
#     customer
#
#     policy_document
#
#     policy_version
#
#     regulation
#
#     customer_contract
#
#     cloud_provider
#
#     region
#
#     residency
#
#     sovereignty
#
#     model_governance
#
#     service_governance
#
#     identity_evidence
#
#     approval_chain
#
#     audit_payload
#
#
# directly to PolicyDecision.
#
#
# Before adding a field, ask:
#
#
#     WHICH DOMAIN OWNS THIS FACT?
#
#
# If another domain owns it:
#
#
#     CONSUME IT
#
# or:
#
#     REFERENCE IT
#
#
# Do not automatically duplicate it.
#
#
# Therefore:
#
#
#     USED BY POLICY != OWNED BY PolicyDecision
#
#
#     INPUT TO POLICY != FIELD ON PolicyDecision
#
#
#     POLICY DECISION != ENTERPRISE DATABASE
# ==========================================================================


# ==========================================================================
# SEIR-II — POSSIBLE FUTURE NEIGHBORING CONTRACTS
# ==========================================================================
#
# DO NOT IMPLEMENT THESE MERELY BECAUSE THEY ARE LISTED HERE.
#
#
# Future operational experience may justify concepts such as:
#
#
#     PolicyEvaluation
#
#     PolicyEvidence
#
#     PolicyProvenance
#
#     PolicyRestriction
#
#     PolicySource
#
#     PolicyAuthority
#
#     PolicyVersion
#
#     EffectivePolicy
#
#     GovernanceDecision
#
#     ResidencyRequirement
#
#     SovereigntyRequirement
#
#     JurisdictionConstraint
#
#     SubjectContext
#
#     DeploymentContext
#
#
# These names are possible architectural destinations.
#
# They are NOT current implementation requirements.
#
#
# Their purpose here is to preserve conceptual expansion points.
#
#
# When operational experience proves a new concept is needed:
#
#
#     IDENTIFY THE FACT
#
#         |
#         v
#     IDENTIFY THE DOMAIN THAT OWNS THE FACT
#
#         |
#         v
#     CREATE THE APPROPRIATE CONTRACT
#
#         |
#         v
#     LET POLICY CONSUME THAT CONTRACT
#
#
# Do not respond to every new requirement by adding another optional
# field to PolicyDecision.
#
#
# Therefore:
#
#
#     ADD THE DOMAIN THAT OWNS THE NEW FACT
#
#
#     CONCEPTUAL TRAPDOOR != REQUIRED IMPLEMENTATION
#
#
#     FUTURE NOTE != TODO LIST
# ==========================================================================


# ==========================================================================
# SEIR-II — CONCEPTUAL FUTURE POLICY PIPELINE
# ==========================================================================
#
# A mature future policy evaluation may resemble:
#
#
#                         AIRequest
#                            |
#                            v
#                   Data Classification
#                            |
#              +-------------+-------------+
#              |             |             |
#              v             v             v
#        Organization     Identity       User
#           Policy         Context    Restriction
#              |             |             |
#              +-------------+-------------+
#                            |
#                            v
#                    Deployment Context
#                            |
#                            v
#                     Governance State
#                            |
#                            v
#                  Regulatory / Residency
#                            |
#                            v
#                    POLICY EVALUATION
#                            |
#                            v
#                      PolicyDecision
#                            |
#                            v
#                   Candidate Evaluation
#                            |
#                            v
#                         Routing
#
#
# IMPORTANT:
#
#
# These inputs remain owned by their respective domains.
#
#
#     POLICY CONSUMES DOMAIN FACTS
#
#
#     POLICY DOES NOT BECOME EVERY DOMAIN
# ==========================================================================


# ==========================================================================
# SEIR-II — FRAMEWORK INDEPENDENCE
# ==========================================================================
#
# Future Agent 11 policy may be consumed by:
#
#
#     Python orchestration
#
#     LangGraph
#
#     CrewAI
#
#     Amazon Bedrock AgentCore
#
#     MCP-aware agents
#
#     custom orchestration
#
#     future frameworks
#
#
# Framework adapters may translate Agent 11 policy contracts.
#
#
# Framework terminology should not redefine Agent 11 domain semantics.
#
#
# Therefore:
#
#
#     FRAMEWORKS CHANGE
#
#
#     DOMAIN CONTRACTS SHOULD SURVIVE THEM
#
#
#     POLICY ENGINE TECHNOLOGY MAY CHANGE
#
#
#     POLICY SEMANTICS SHOULD SURVIVE
#
#
# Agent 11 domain contracts belong to Agent 11.
#
# They do not belong to whichever framework happens to be fashionable
# when the current implementation is written.
# ==========================================================================


# ==========================================================================
# SEIR-II — TEST WHAT THE ARCHITECTURE CLAIMS
# ==========================================================================
#
# The SEIR-I implementation should generate operational evidence before
# SEIR-II expands these contracts.
#
#
# Future testing should ask questions such as:
#
#
#     Did DENY remain distinct from infrastructure failure?
#
#
#     Did INDETERMINATE occur in real operations?
#
#
#     Which situations produced INDETERMINATE?
#
#
#     Did users need restrictions beyond COMPANY_ONLY / ONPREM_ONLY?
#
#
#     Did policy require service-level precision?
#
#
#     Did policy require deployment-level precision?
#
#
#     Did residency requirements appear?
#
#
#     Did customer-specific policy appear?
#
#
#     Did multiple policy authorities conflict?
#
#
#     Did operators need policy provenance?
#
#
#     Did operators need historical policy reconstruction?
#
#
#     Did RESTRICT require typed restriction details?
#
#
#     Did emergency operations create pressure to bypass policy?
#
#
#     Did multi-cloud deployments create provider-specific policy?
#
#
#     Did MCP introduce separate execution-authorization requirements?
#
#
# These observations should inform SEIR-II.
#
#
# Do not expand architecture merely because expansion is imaginable.
#
#
# Expand architecture because:
#
#
#     OPERATIONAL EVIDENCE
#
#         +
#
#     CLEAR DOMAIN REQUIREMENT
#
#         =
#
#     JUSTIFIED ARCHITECTURAL EXPANSION
#
#
# This is why these notes are preserved.
# ==========================================================================


# ==========================================================================
# SEIR-II — PRESERVE FAILURE DATA
# ==========================================================================
#
# Some of the most valuable SEIR-II requirements will be discovered
# when SEIR-I fails.
#
#
# Preserve evidence about:
#
#
#     policy denials
#
#     indeterminate decisions
#
#     unavailable policy sources
#
#     conflicting policy inputs
#
#     routing candidates rejected by policy
#
#     fallback attempts
#
#     no-viable-route outcomes
#
#     emergency requests
#
#     user-policy narrowing
#
#     deployment-specific exceptions
#
#
# Do not treat every failure as something to hide.
#
#
# A correctly blocked request may be:
#
#
#     SUCCESSFUL SECURITY ENFORCEMENT
#
#
# A correctly failed-closed INDETERMINATE may also be:
#
#
#     SUCCESSFUL SECURITY BEHAVIOR
#
#
# while simultaneously indicating:
#
#
#     OPERATIONAL POLICY INFRASTRUCTURE NEEDS ATTENTION
#
#
# Therefore:
#
#
#     REQUEST FAILURE != SECURITY FAILURE
#
#
#     BLOCKED != BROKEN
#
#
#     FAIL CLOSED != SYSTEM MALFUNCTION
#
#
# Telemetry should eventually preserve enough distinction to teach us
# which condition actually occurred.
# ==========================================================================


# ==========================================================================
# SEIR-II — DO NOT LET TELEMETRY REDEFINE POLICY
# ==========================================================================
#
# Future telemetry may observe:
#
#
#     policy decision
#
#     rejection reason
#
#     policy source
#
#     policy version
#
#     selected route
#
#     fallback behavior
#
#     latency
#
#     cost
#
#
# Telemetry observes and records.
#
#
# Telemetry does not become the policy authority merely because it has
# a large amount of information.
#
#
# Therefore:
#
#
#     OBSERVABILITY != AUTHORITY
#
#
#     TELEMETRY != POLICY
#
#
#     AUDIT RECORD != AUTHORIZATION GRANT
# ==========================================================================


# ==========================================================================
# SEIR-II — CHEWBACCA MEETS ENTERPRISE POLICY
# ==========================================================================
#
# Chewbacca:
#
#     "The company model moved from Azure to GCP."
#
#
# Agent 11:
#
#     OKAY.
#
#
# Chewbacca:
#
#     "Should I create COMPANY_GCP_LLM?"
#
#
# Agent 11:
#
#     NO.
#
#
#     ROUTING DOMAIN != CLOUD PROVIDER.
#
#
# Chewbacca:
#
#     "But E8 cannot use the EU deployment."
#
#
# Agent 11:
#
#     THEN POLICY EVALUATES DEPLOYMENT ATTRIBUTES.
#
#
# Chewbacca:
#
#     "So I'll put region on AIRoute."
#
#
# Agent 11:
#
#     ALSO NO.
#
#
#     DEPLOYMENT LOCATION DOES NOT DEFINE AIRoute.
#
#
# Chewbacca:
#
#     "What if the external model is much cheaper?"
#
#
# Agent 11:
#
#     WHAT DOES POLICY SAY?
#
#
# Chewbacca:
#
#     "DENY."
#
#
# Agent 11:
#
#     THEN COST IS IRRELEVANT TO ELIGIBILITY.
#
#
# Chewbacca:
#
#     "What if the company-cloud model is down?"
#
#
# Agent 11:
#
#     EVALUATE ANOTHER AUTHORIZED DESTINATION.
#
#
# Chewbacca:
#
#     "External is available."
#
#
# Agent 11:
#
#     POLICY?
#
#
# Chewbacca:
#
#     "Still DENY."
#
#
# Agent 11:
#
#     THEN IT IS NOT A FALLBACK.
#
#
# Chewbacca:
#
#     "What if policy evaluation fails?"
#
#
# Agent 11:
#
#     INDETERMINATE.
#
#
# Chewbacca:
#
#     "So DENY?"
#
#
# Agent 11:
#
#     FAIL CLOSED.
#
#     RECORD INDETERMINATE.
#
#
# Chewbacca:
#
#     "Same action, different fact."
#
#
# Agent 11:
#
#     EXACTLY.
#
#
# Chewbacca:
#
#     "Can the model still call the production deletion tool?"
#
#
# Agent 11:
#
#     YOU HAVE CHANGED THE QUESTION.
#
#
#     REASONING AUTHORIZATION
#
#         !=
#
#     EXECUTION AUTHORIZATION
#
#
# Chewbacca:
#
#     "Can I just add all of this to PolicyDecision?"
#
#
# Agent 11:
#
#     WHICH THING OWNS WHICH FACT?
#
#
# Chewbacca:
#
#     "Fine."
#
#
# Agent 11:
#
#     ARCHITECTURE ACHIEVED.
# ==========================================================================


# ==========================================================================
# PART III — FINAL POLICY INVARIANTS — DO NOT DELETE
# ==========================================================================
#
#     THIS SECTION IS DOCUMENTATION ONLY
#
#
#     PRESERVE THE FUTURE PROBLEM
#
#
#     DO NOT PRETEND TO HAVE THE FUTURE SOLUTION
#
#
#     SIMPLE TODAY SHOULD NOT MEAN IMPOSSIBLE TOMORROW
#
#
#     FUTURE-AWARE != FUTURE-BLOATED
#
#
#     POLICY ANSWERS: MAY WE?
#
#
#     POLICY != CAPABILITY
#
#
#     POLICY != SERVICE HEALTH
#
#
#     POLICY != NETWORK
#
#
#     POLICY != ROUTING
#
#
#     COORDINATION != OWNERSHIP
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
#     REACHABLE != AUTHORIZED
#
#
#     AUTHORIZED != REACHABLE
#
#
#     HEALTHY != PERMITTED
#
#
#     CAPABLE != AUTHORIZED
#
#
#     CHEAPER != PERMITTED
#
#
#     FASTER != PERMITTED
#
#
#     EFFECTIVE POLICY
#         =
#     ORGANIZATION POLICY
#         INTERSECTION
#     USER POLICY
#
#
#     USER MAY NARROW
#
#
#     USER MAY NOT EXPAND
#
#
#     LOWER AUTHORITY MAY NARROW
#
#
#     LOWER AUTHORITY MAY NOT EXPAND
#
#
#     PREFERENCE != AUTHORITY
#
#
#     POLICY COMPOSITION != MAJORITY VOTE
#
#
#     POLICY SOURCE COUNT != POLICY AUTHORITY
#
#
#     POLICY SOURCE != POLICY PRECEDENCE
#
#
#     INDETERMINATE != DENY
#
#
#     INDETERMINATE != ALLOW
#
#
#     FAIL CLOSED != ERASE SEMANTICS
#
#
#     FAIL CLOSED != FALSIFY OBSERVED STATE
#
#
#     CONSERVATIVE ACTION != FALSE OBSERVATION
#
#
#     RESTRICT != UNTYPED POLICY BAG
#
#
#     RESTRICTION STATUS != RESTRICTION DETAILS
#
#
#     POLICY PRECISION != ROUTING DOMAIN EXPANSION
#
#
#     POLICY MAY BECOME MORE PRECISE
#     WITHOUT MAKING AIRoute MORE SPECIFIC
#
#
#     ROUTING DOMAIN != CLOUD PROVIDER
#
#
#     ROUTING DOMAIN != DEPLOYMENT LOCATION
#
#
#     DEPLOYMENT LOCATION MAY INFORM POLICY
#
#
#     DEPLOYMENT LOCATION DOES NOT DEFINE AIRoute
#
#
#     MULTI-CLOUD != MULTIPLY AIRoute VALUES
#
#
#     PROPRIETARY MODEL != ON-PREMISES MODEL
#
#
#     MODEL IDENTITY != DEPLOYMENT IDENTITY
#
#
#     MODEL PROVIDER != DEPLOYMENT PROVIDER
#
#
#     MODEL OWNERSHIP != ROUTING DOMAIN
#
#
#     CLOUD PROVIDER != MODEL OWNER
#
#
#     ROUTING DOMAIN != MODEL PROVIDER
#
#
#     POLICY CONSUMES DEPLOYMENT FACTS
#
#
#     POLICY DOES NOT OWN DEPLOYMENT FACTS
#
#
#     INPUT TO POLICY != FIELD ON PolicyDecision
#
#
#     LOCATION != SOVEREIGNTY
#
#
#     RESIDENCY != COMPLETE GOVERNANCE
#
#
#     IDENTITY != POLICY
#
#
#     AUTHENTICATED != AUTHORIZED
#
#
#     KNOWN IDENTITY != PERMITTED ACTION
#
#
#     IDENTITY FACT != POLICY DECISION
#
#
#     USER PREFERENCE MAY REMOVE ROUTES
#
#
#     USER PREFERENCE MAY NOT CREATE PROHIBITED ROUTES
#
#
#     PREFERENCE != AUTHORIZATION GRANT
#
#
#     SERVICE IDENTITY != UNIVERSAL AUTHORIZATION
#
#
#     AUTHORIZATION MAY DEPEND ON REQUEST CONTEXT
#
#
#     CURRENT POLICY != HISTORICAL POLICY
#
#
#     DECISION != POLICY VERSION DATABASE
#
#
#     POLICY DECISION != POLICY DOCUMENT
#
#
#     POLICY DECISION != POLICY EVIDENCE
#
#
#     DECISION != PROVENANCE
#
#
#     REFERENCE EVIDENCE
#
#
#     DO NOT DUPLICATE EVIDENCE
#
#
#     AUDITABLE != EVERYTHING IN ONE OBJECT
#
#
#     HUMAN EXPLANATION != MACHINE EVIDENCE
#
#
#     REASON TEXT != POLICY PROVENANCE
#
#
#     POLICY ENGINE != POLICY DOMAIN CONTRACT
#
#
#     POLICY ENGINE TECHNOLOGY MAY CHANGE
#
#
#     POLICY SEMANTICS SHOULD SURVIVE
#
#
#     POLICY IS A CONSTRAINT
#
#
#     POLICY IS NOT A PREFERENCE
#
#
#     POLICY IS NOT AN OPTIMIZATION WEIGHT
#
#
#     POLICY NEVER BECOMES A SCORE
#
#
#     OPTIMIZATION NEVER CREATES AUTHORIZATION
#
#
#     BETTER MODEL != PERMITTED
#
#
#     HIGHER QUALITY != PERMITTED
#
#
#     MORE AVAILABLE != PERMITTED
#
#
#     AVAILABILITY PRESSURE != POLICY EXCEPTION
#
#
#     BUSINESS PRESSURE != POLICY EXCEPTION
#
#
#     EMERGENCY POLICY != ROUTER BYPASS
#
#
#     URGENCY != AUTHORIZATION
#
#
#     FAIL CLOSED = REQUIRE AUTHORIZATION BEFORE USE
#
#
#     ROUTING CONSUMES POLICY
#
#
#     ROUTING DOES NOT BECOME POLICY
#
#
#     POLICY DOES NOT BECOME ROUTING
#
#
#     FALLBACK != IGNORE POLICY
#
#
#     FALLBACK != REDUCE SECURITY REQUIREMENTS
#
#
#     FALLBACK = ANOTHER INDEPENDENT VIABILITY EVALUATION
#
#
#     REASONING AUTHORIZATION != TOOL AUTHORIZATION
#
#
#     AI ROUTING POLICY != MCP EXECUTION POLICY
#
#
#     ABILITY TO RECOMMEND ACTION != AUTHORITY TO EXECUTE ACTION
#
#
#     REASONING CAPABILITY != EXECUTION AUTHORITY
#
#
#     INTELLIGENCE != AUTHORIZATION
#
#
#     MODEL OUTPUT != ACTION AUTHORITY
#
#
#     COORDINATION != OWNERSHIP OF EVERYTHING
#
#
#     CONTROL PLANE != GIANT GOD OBJECT
#
#
#     USED BY POLICY != OWNED BY PolicyDecision
#
#
#     POLICY DECISION != ENTERPRISE DATABASE
#
#
#     ADD THE DOMAIN THAT OWNS THE NEW FACT
#
#
#     CONCEPTUAL TRAPDOOR != REQUIRED IMPLEMENTATION
#
#
#     FUTURE NOTE != TODO LIST
#
#
#     POLICY CONSUMES DOMAIN FACTS
#
#
#     POLICY DOES NOT BECOME EVERY DOMAIN
#
#
#     FRAMEWORKS CHANGE
#
#
#     DOMAIN CONTRACTS SHOULD SURVIVE THEM
#
#
#     OPERATIONAL EVIDENCE
#         +
#     CLEAR DOMAIN REQUIREMENT
#         =
#     JUSTIFIED ARCHITECTURAL EXPANSION
#
#
#     REQUEST FAILURE != SECURITY FAILURE
#
#
#     BLOCKED != BROKEN
#
#
#     FAIL CLOSED != SYSTEM MALFUNCTION
#
#
#     OBSERVABILITY != AUTHORITY
#
#
#     TELEMETRY != POLICY
#
#
#     AUDIT RECORD != AUTHORIZATION GRANT
#
#
#     WHICH THING OWNS WHICH FACT?
# ==========================================================================
# END PART III
# ==========================================================================
