"""
Agent 11 Policy Enums
=====================

Defines the controlled vocabulary used by the Agent 11 policy layer.

This module answers two fundamental policy questions:

    PolicyDecisionStatus
        "What did policy evaluation conclude?"

    UserDataPreference
        "Has the user chosen to further restrict how their data
         may be processed?"

These concepts are intentionally separate.

Policy Enums do NOT:

    - authenticate users
    - validate credentials
    - perform MFA
    - establish identity
    - classify data
    - select AI routes
    - determine service health
    - determine network reachability
    - invoke AI models
    - invoke MCP tools
    - perform orchestration

Architecture rules:

    AUTHENTICATION != AUTHORIZATION

    CLASSIFICATION != POLICY

    POLICY ALLOW != ROUTE SELECTED

    DENY != INDETERMINATE

    RESTRICT != DENY

    USER POLICY MAY RESTRICT ORGANIZATION POLICY

    USER POLICY MAY NEVER EXPAND ORGANIZATION POLICY

    CANNOT ESTABLISH ALLOW = DO NOT PROCEED
"""

from .base_enum import Agent11Enum


# ===========================================================================
# Policy Decision Status
# ===========================================================================


class PolicyDecisionStatus(Agent11Enum):
    """
    Describes the outcome of an Agent 11 policy evaluation.

    ALLOW
        Policy evaluation determined that the operation is permitted
        under the evaluated conditions.

    DENY
        Policy evaluation explicitly determined that the operation
        is prohibited.

    RESTRICT
        The operation may proceed, but only within additional policy
        constraints.

    INDETERMINATE
        Agent 11 could not establish whether the operation is
        permitted.

    These outcomes are intentionally distinct.

    Conceptually:

                           POLICY
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
           ALLOW           RESTRICT           DENY
                              |
                              |
                              +---------- INDETERMINATE

    ALLOW and RESTRICT may permit further processing.

    DENY and INDETERMINATE must not permit a prohibited or
    unverified operation to proceed.
    """

    ALLOW = "allow"
    DENY = "deny"
    RESTRICT = "restrict"
    INDETERMINATE = "indeterminate"

# ==========================================================================
# DATA ROUTE POLICY EFFECT
# ==========================================================================
#
# DataRoutePolicyEffect describes CONFIGURED policy behavior.
#
# It answers:
#
#
#     "WHAT DOES THIS POLICY RULE SAY?"
#
#
# This is intentionally different from PolicyDecisionStatus.
#
#
#     DataRoutePolicyEffect
#         =
#     CONFIGURATION
#
#
#     PolicyDecisionStatus
#         =
#     EVALUATION RESULT
#
#
# SEIR-I configuration supports:
#
#
#     ALLOW
#
#     DENY
#
#
# Do not add INDETERMINATE here.
#
# INDETERMINATE means policy evaluation could not establish a
# definitive authorization result. It is not something an
# administrator intentionally configures.
#
#
# Do not add RESTRICT merely because PolicyDecisionStatus contains it.
#
# A configured restriction eventually requires a typed contract
# describing WHAT is restricted.
#
#
# Future SEIR-II examples may include:
#
#     allowed regions
#     prohibited regions
#     approved model families
#     approved deployments
#     human approval requirements
#     residency requirements
#     customer-specific restrictions
#
#
# When those requirements become real, introduce the domain object
# that actually describes them.
#
#
#     RESTRICT WITHOUT RESTRICTION DETAILS
#         =
#     INCOMPLETE DOMAIN MODEL
#
#
#     CONFIGURATION != EVALUATION
#
#     POLICY EFFECT != POLICY DECISION STATUS
#
#     FUTURE-AWARE != FUTURE-BLOATED
# ==========================================================================


class DataRoutePolicyEffect(Agent11Enum):
    """
    Configured effect of a data-routing policy rule.

    This enum represents policy configuration, not the result of
    evaluating policy for a particular AI request.
    """

    ALLOW = "allow"
    DENY = "deny"
    
# ===========================================================================
# User Data Preference
# ===========================================================================


class UserDataPreference(Agent11Enum):
    """
    Describes additional user-selected restrictions on AI processing.

    ORGANIZATION_DEFAULT
        The user imposes no additional restriction beyond the
        organization's established policy.

    COMPANY_ONLY
        The user permits company-controlled AI services but does not
        permit external foundational-model services.

    ONPREM_ONLY
        The user permits processing only by company-controlled
        on-premises AI infrastructure.

    UserDataPreference may only make organizational policy more
    restrictive.

    It may never enlarge the organization's permission boundary.

    Conceptually:

        EFFECTIVE POLICY
                =
        ORGANIZATION POLICY
                INTERSECT
        USER POLICY

    Never:

        ORGANIZATION POLICY
                UNION
        USER POLICY

    Therefore:

        USER POLICY MAY REMOVE PERMISSIONS.

        USER POLICY MAY NOT CREATE PERMISSIONS.
    """

    ORGANIZATION_DEFAULT = "organization_default"
    COMPANY_ONLY = "company_only"
    ONPREM_ONLY = "onprem_only"


# ===========================================================================
# ALLOW
# ===========================================================================

# PolicyDecisionStatus.ALLOW means policy has determined that the
# evaluated operation is permitted.
#
# Example:
#
#
#     Data Classification
#           NORMAL
#              |
#              v
#       Policy Evaluation
#              |
#              v
#           ALLOW
#
#
# ALLOW does not select an AI destination.
#
# Routing must still consider:
#
#
#     - required capability
#     - service capability
#     - service availability
#     - network-path availability
#     - routing preference
#
#
# Therefore:
#
#
#     POLICY ALLOW != ROUTE SELECTED
#
#
# Policy answers:
#
#     "May this operation occur?"
#
#
# Routing answers:
#
#     "Which viable destination should perform it?"


# ===========================================================================
# DENY
# ===========================================================================

# PolicyDecisionStatus.DENY means policy explicitly prohibits the
# evaluated operation.
#
# Example:
#
#
#     Data Classification
#             E8
#              |
#              v
#       Requested Domain
#         EXTERNAL_FM
#              |
#              v
#       Policy Evaluation
#              |
#              v
#            DENY
#
#
# Other operational facts cannot override DENY.
#
# For example:
#
#
#     EXTERNAL_FM
#
#     Service capable        YES
#     Service available      YES
#     Network reachable      YES
#     Low latency            YES
#     Low cost               YES
#     Policy permitted       NO
#
#
# The operation remains prohibited.
#
#
# Therefore:
#
#
#     DENY IS NOT A ROUTING PREFERENCE.
#
#
# Routing does not get to reconsider an explicit policy denial.


# ===========================================================================
# RESTRICT
# ===========================================================================

# PolicyDecisionStatus.RESTRICT means processing may proceed, but only
# within additional constraints.
#
# Example:
#
#
#     Data Classification
#             E7
#              |
#              v
#       Policy Evaluation
#              |
#              v
#          RESTRICT
#
#
# Possible resulting constraints:
#
#
#     EXTERNAL_FM             DENIED
#     COMPANY_CLOUD_LLM       ALLOWED
#     COMPANY_ONPREM_LLM      ALLOWED
#
#
# The request itself has not been completely denied.
#
# Its permitted processing universe has been reduced.
#
#
# Therefore:
#
#
#     RESTRICT != DENY
#
#
# The Enum communicates that restrictions exist.
#
# A future Pydantic PolicyDecision model will describe the actual
# restrictions.
#
# Conceptually:
#
#
#     PolicyDecisionStatus.RESTRICT
#
#                 +
#
#     allowed_routes = {
#         COMPANY_CLOUD_LLM,
#         COMPANY_ONPREM_LLM,
#     }
#
#
# The Enum describes the policy outcome.
#
# The model describes the resulting policy state.


# ===========================================================================
# INDETERMINATE
# ===========================================================================

# PolicyDecisionStatus.INDETERMINATE means Agent 11 could not establish
# whether the operation is permitted.
#
# Example:
#
#
#     Request
#        |
#        v
#     Policy Evaluation
#        |
#        v
#     Required policy source
#     cannot be evaluated
#        |
#        v
#     INDETERMINATE
#
#
# INDETERMINATE is intentionally different from DENY.
#
#
#     DENY
#
#         "Policy was successfully evaluated and explicitly
#          prohibited this operation."
#
#
#     INDETERMINATE
#
#         "Agent 11 cannot establish whether policy permits
#          this operation."
#
#
# These states are operationally different and should therefore remain
# distinguishable in telemetry and audit records.
#
# Their security consequence, however, is the same:
#
#
#     DENY
#       |
#       v
#     DO NOT PROCEED
#
#
#     INDETERMINATE
#       |
#       v
#     DO NOT PROCEED
#
#
# Agent 11 therefore follows the fail-closed principle:
#
#
#     CANNOT ESTABLISH ALLOW
#              =
#        DO NOT PROCEED
#
#
# Fail-closed behavior is an architectural invariant.
#
# It is intentionally not represented as a configurable:
#
#
#     PolicyEnforcement.FAIL_CLOSED
#
#
# because Agent 11 should not imply that weakening this behavior is a
# supported alternative for protected AI routing.


# ===========================================================================
# Organization Policy
# ===========================================================================

# Organizational policy establishes the maximum permission boundary.
#
# Example:
#
#
#     Organization permits:
#
#         EXTERNAL_FM
#         COMPANY_CLOUD_LLM
#         COMPANY_ONPREM_LLM
#
#
# A user may choose to narrow this boundary.
#
# A user may not enlarge it.
#
#
# The conceptual rule is:
#
#
#     EFFECTIVE ROUTES
#           =
#     ORGANIZATION ROUTES
#           INTERSECT
#     USER ROUTES
#
#
# This means organizational policy always remains the upper bound.


# ===========================================================================
# ORGANIZATION_DEFAULT
# ===========================================================================

# UserDataPreference.ORGANIZATION_DEFAULT means the user imposes no
# additional restriction beyond organizational policy.
#
# It does NOT mean:
#
#
#     unrestricted
#
#
# Example:
#
#
#     Organization Policy:
#
#         E8 -> COMPANY_ONPREM_LLM only
#
#
#     User Preference:
#
#         ORGANIZATION_DEFAULT
#
#
#     Effective Permission:
#
#         COMPANY_ONPREM_LLM only
#
#
# Organization policy remains fully effective.


# ===========================================================================
# COMPANY_ONLY
# ===========================================================================

# UserDataPreference.COMPANY_ONLY removes external foundational-model
# infrastructure from the user's permitted processing set.
#
# Example:
#
#
#     Organization permits:
#
#         EXTERNAL_FM
#         COMPANY_CLOUD_LLM
#         COMPANY_ONPREM_LLM
#
#
#     User preference:
#
#         COMPANY_ONLY
#
#
#     Effective permission:
#
#         COMPANY_CLOUD_LLM
#         COMPANY_ONPREM_LLM
#
#
# The user has narrowed the organization's permission set.


# ===========================================================================
# ONPREM_ONLY
# ===========================================================================

# UserDataPreference.ONPREM_ONLY restricts processing to company
# on-premises AI infrastructure.
#
# Example:
#
#
#     Organization permits:
#
#         EXTERNAL_FM
#         COMPANY_CLOUD_LLM
#         COMPANY_ONPREM_LLM
#
#
#     User preference:
#
#         ONPREM_ONLY
#
#
#     Effective permission:
#
#         COMPANY_ONPREM_LLM
#
#
# Again, the user has removed permissions.
#
# The user has not created any new permissions.


# ===========================================================================
# Empty Policy Intersection
# ===========================================================================

# Organization policy and user policy may legitimately produce an
# empty effective permission set.
#
# Example:
#
#
#     Organization permits:
#
#         COMPANY_CLOUD_LLM
#
#
#     User permits:
#
#         COMPANY_ONPREM_LLM
#
#
#     Intersection:
#
#         { }
#
#
# Nothing remains permitted.
#
# Agent 11 must not respond by weakening either policy.
#
# It must preserve both constraints.
#
# A later routing evaluation may consequently produce:
#
#
#     RoutingStatus.NO_VIABLE_ROUTE
#
#
# This demonstrates an important security principle:
#
#
#     AVAILABILITY DOES NOT OVERRIDE POLICY.
#
#
# A valid combination of policies may intentionally result in zero
# available permissions.


# ===========================================================================
# Policy and Data Classification
# ===========================================================================

# Data classification and policy are intentionally separate concepts.
#
#
#     DATA CLASSIFICATION
#
#         "What kind of data is this?"
#
#
#     POLICY
#
#         "Given what kind of data this is, what may happen to it?"
#
#
# Agent 11 may eventually evaluate:
#
#
#     DataClassification.E8
#             |
#             v
#       Policy Evaluation
#             |
#             v
#     PolicyDecisionStatus.RESTRICT
#             |
#             v
#     COMPANY_ONPREM_LLM only
#
#
# This separation allows organizations to replace the training
# classification vocabulary:
#
#
#     E7
#     E8
#     E9
#
#
# with their own vocabulary:
#
#
#     PUBLIC
#     INTERNAL
#     CONFIDENTIAL
#     RESTRICTED
#
#
# without changing the fundamental policy architecture.
#
#
# Therefore:
#
#
#     CLASSIFICATION != POLICY


# ===========================================================================
# Policy and Authentication
# ===========================================================================

# Policy does not authenticate users.
#
# Authentication may establish an identity that later becomes part of
# policy evaluation.
#
# Conceptually:
#
#
#     AUTHENTICATION
#          |
#          v
#     ESTABLISHED IDENTITY
#          |
#          v
#     POLICY / AUTHORIZATION
#          |
#          v
#        ROUTING
#
#
# Authentication answers:
#
#
#     "Who are you, and can you prove it?"
#
#
# Policy answers:
#
#
#     "Given the established identity, data, operation, and
#      organizational rules, what is permitted?"
#
#
# Therefore:
#
#
#     AUTHENTICATION != AUTHORIZATION


# ===========================================================================
# Future PolicyDecision Model
# ===========================================================================

# These Enums will eventually be composed by Pydantic models.
#
# A simplified future example may resemble:
#
#
#     class PolicyDecision(Agent11BaseModel):
#         status: PolicyDecisionStatus
#         allowed_routes: set[AIRoute]
#         reason: str | None = None
#
#
# Example:
#
#
#     decision = PolicyDecision(
#         status=PolicyDecisionStatus.RESTRICT,
#         allowed_routes={
#             AIRoute.COMPANY_CLOUD_LLM,
#             AIRoute.COMPANY_ONPREM_LLM,
#         },
#         reason=(
#             "External foundational models prohibited "
#             "for E7 data."
#         ),
#     )
#
#
# This demonstrates:
#
#
#     ENUM
#         describes an individual controlled fact
#
#
#     PYDANTIC MODEL
#         composes controlled facts into meaningful state


# ===========================================================================
# Chewbacca's Architecture Commentary
# ===========================================================================

# Chewbacca has discovered:
#
#
#     PolicyDecisionStatus.INDETERMINATE
#
#
# and immediately submitted the following request:
#
#
#     "Route all stupid traffic there."
#
#
# Agent 11 Architecture Review:
#
#     INDETERMINATE is not a physical routing destination.
#
#
# Chewbacca:
#
#     "It should be."
#
#
# Agent 11:
#
#     Wrong Enum.
#
#
# AIRoute describes destinations.
#
# PolicyDecisionStatus describes policy outcomes.
#
#
# Chewbacca:
#
#     "Fine."
#
#
# Chewbacca then discovers a request whose policy source cannot be
# evaluated.
#
#
#     PolicyDecisionStatus.INDETERMINATE
#
#
# Chewbacca:
#
#     "Excellent."
#
#
#     "Nobody said no."
#
#
# Agent 11:
#
#     Correct.
#
#
# Chewbacca:
#
#     "So we proceed."
#
#
# Agent 11:
#
#     Incorrect.
#
#
# Chewbacca:
#
#     "But INDETERMINATE isn't DENY."
#
#
# Agent 11:
#
#     Correct.
#
#
#     DENY means:
#
#         "Policy explicitly prohibited the operation."
#
#
#     INDETERMINATE means:
#
#         "Permission could not be established."
#
#
# Chewbacca:
#
#     "Those sound different."
#
#
# Agent 11:
#
#     They are.
#
#
#     Telemetry should preserve that difference.
#
#
#     Security enforcement should not.
#
#
# Both result in:
#
#
#     DO NOT PROCEED
#
#
# Chewbacca then submits:
#
#
#     Organization Policy:
#         E8 -> COMPANY_ONPREM_LLM only
#
#
#     User Preference:
#         EXTERNAL_FM
#
#
# Agent 11:
#
#     That preference does not exist.
#
#
# Chewbacca:
#
#     "Then add it."
#
#
# Agent 11:
#
#     No.
#
#
# UserDataPreference intentionally contains only choices that can
# preserve or further restrict organizational policy.
#
#
# The organization establishes the maximum permission boundary.
#
# The user may make that boundary smaller.
#
# The user may never make it larger.
#
#
# Chewbacca proposes:
#
#
#     ORGANIZATION POLICY
#             UNION
#     USER POLICY
#
#
# Agent 11 replaces the operator:
#
#
#     ORGANIZATION POLICY
#             INTERSECT
#     USER POLICY
#
#
# Chewbacca:
#
#     "I think you used the wrong mathematical operator."
#
#
# Agent 11:
#
#     No.
#
#
# Final architectural ruling:
#
#
#     USER POLICY MAY CLOSE ADDITIONAL DOORS.
#
#     USER POLICY MAY NOT OPEN A DOOR
#     THE ORGANIZATION HAS ALREADY LOCKED.
#
#
# Chewbacca has classified this ruling as:
#
#
#     PolicyDecisionStatus.INDETERMINATE
#
#
# Agent 11 has classified Chewbacca's classification as:
#
#
#     PolicyDecisionStatus.DENY
