# ==========================================================================
# PART I — DATA CLASSIFICATION
# ==========================================================================
#
# DataClassification describes the classification currently assigned
# to data involved in Agent 11 reasoning.
#
#
# It answers:
#
#
#     "WHAT CLASSIFICATION HAS BEEN ASSIGNED TO THIS DATA?"
#
#
# It does NOT answer:
#
#
#     "Where may this data go?"
#
#     "Which AI service may process this data?"
#
#     "Which route should Agent 11 select?"
#
#     "How was the classification calculated?"
#
#     "Should this classification be trusted?"
#
#     "Does this classification require human review?"
#
#
# Those questions belong to neighboring domains and classification
# behavior.
#
#
# The fundamental boundary is:
#
#
#     CLASSIFICATION DESCRIBES DATA
#
#     POLICY AUTHORIZES USE OF DATA
#
#     ROUTING SELECTS A VIABLE DESTINATION
#
#
# Conceptually:
#
#
#                   DATA
#                    |
#                    v
#            DataClassification
#                    |
#                    v
#            Policy Evaluation
#                    |
#                    v
#             PolicyDecision
#                    |
#                    v
#                Routing
#
#
# Therefore:
#
#
#     DATA CLASSIFICATION != POLICY
#
#     DATA CLASSIFICATION != ROUTING
#
#     CLASSIFIED != AUTHORIZED
#
#     CLASSIFICATION INFORMS POLICY
#
#     POLICY CONSTRAINS ROUTING
# ==========================================================================


# ==========================================================================
# IMPORTS
# ==========================================================================
#
# Keep this model dependent only on:
#
#
#     Pydantic
#
#     Agent 11 base models
#
#     Agent 11 enum vocabulary
#
#
# Do not import:
#
#
#     cloud SDKs
#
#     DLP SDKs
#
#     AI provider SDKs
#
#     policy engines
#
#     routing implementations
#
#     network implementations
#
#
# This file describes classification state.
#
# It does not perform classification.
#
#
#     DOMAIN MODEL != CLASSIFICATION ENGINE
# ==========================================================================

from pydantic import Field

from ..base_model import Agent11BaseModel
from ..enums.policy_enums import (
    DataClassificationLevel,
    DataClassificationSource,
)


# ==========================================================================
# CLASSIFICATION VOCABULARY
# ==========================================================================
#
# The classification vocabulary is defined outside this model in:
#
#
#     models/enums/policy_enums.py
#
#
# SEIR-I uses:
#
#
#     DataClassificationLevel
#
#         NORMAL
#         E7
#         E8
#         E9
#         UNKNOWN
#
#
# and:
#
#
#     DataClassificationSource
#
#         USER_DECLARED
#         APPLICATION_DECLARED
#         ORGANIZATION_METADATA
#         AUTOMATIC_CLASSIFIER
#         INHERITED
#         UNKNOWN
#
#
# The enums define vocabulary.
#
# They do not perform classification.
#
#
#     ENUM = VOCABULARY
#
#     ENUM != CLASSIFICATION ENGINE
# ==========================================================================


# ==========================================================================
# CLASSIFICATION LEVEL
# ==========================================================================
#
# DataClassificationLevel answers:
#
#
#     "WHAT CLASSIFICATION HAS BEEN ASSIGNED?"
#
#
# Examples:
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
#     UNKNOWN
#
#
# The classification level describes data.
#
# It does NOT describe:
#
#
#     an AI route
#
#     an AI service
#
#     a cloud provider
#
#     a deployment
#
#     a policy decision
#
#     network reachability
#
#     service availability
#
#
# In particular:
#
#
#     level = E8
#
#
# does NOT inherently mean:
#
#
#     EXTERNAL_FM = DENY
#
#     COMPANY_CLOUD_LLM = DENY
#
#     COMPANY_ONPREM_LLM = ALLOW
#
#
# Those are possible organizational policy rules.
#
# They are not the definition of E8.
#
#
# Therefore:
#
#
#     CLASSIFICATION LEVEL != ROUTING POLICY
#
#
#     CLASSIFICATION LEVEL != AUTHORIZATION
#
#
#     CLASSIFICATION LEVEL != ROUTING DOMAIN
# ==========================================================================


# ==========================================================================
# UNKNOWN IS A REAL CLASSIFICATION STATE
# ==========================================================================
#
# UNKNOWN is intentionally different from NORMAL.
#
#
#     NORMAL
#
# means:
#
#     THE DATA HAS BEEN CLASSIFIED AS NORMAL
#
#
#     UNKNOWN
#
# means:
#
#     AGENT 11 DOES NOT CURRENTLY HAVE AN ESTABLISHED
#     CLASSIFICATION FOR THE DATA
#
#
# Never silently convert:
#
#
#     UNKNOWN
#
# into:
#
#     NORMAL
#
#
# merely because NORMAL is easier to process.
#
#
# This follows the same Agent 11 semantic principle used by neighboring
# domains:
#
#
#     NETWORK:
#
#         UNKNOWN != UNAVAILABLE
#
#
#     POLICY:
#
#         INDETERMINATE != DENY
#
#
#     CLASSIFICATION:
#
#         UNKNOWN != NORMAL
#
#
# Security behavior may still be conservative when classification is
# UNKNOWN.
#
#
# But conservative behavior must not falsify the classification state.
#
#
#     UNKNOWN != NORMAL
#
#     UNKNOWN != LOW SENSITIVITY
#
#     UNKNOWN != SAFE
#
#     UNKNOWN != PERMISSION
#
#
#     CONSERVATIVE BEHAVIOR != FALSE OBSERVATION
# ==========================================================================


# ==========================================================================
# CLASSIFICATION SOURCE
# ==========================================================================
#
# DataClassificationSource answers:
#
#
#     "WHERE DID THIS CLASSIFICATION ASSERTION COME FROM?"
#
#
# Examples:
#
#
#     USER_DECLARED
#
#     APPLICATION_DECLARED
#
#     ORGANIZATION_METADATA
#
#     AUTOMATIC_CLASSIFIER
#
#     INHERITED
#
#     UNKNOWN
#
#
# Source records the origin of the classification assertion.
#
#
# It does NOT answer:
#
#
#     "Is the classification correct?"
#
#     "How confident are we?"
#
#     "What evidence supports it?"
#
#     "Who approved it?"
#
#     "Who has authority to change it?"
#
#
# Those are different facts.
#
#
# Therefore:
#
#
#     SOURCE != CORRECTNESS
#
#     SOURCE != CONFIDENCE
#
#     SOURCE != EVIDENCE
#
#     SOURCE != AUTHORITY
#
#     SOURCE != APPROVAL
#
#
# Keep source small.
#
# Do not turn DataClassificationSource into an audit or provenance
# system.
# ==========================================================================


# ==========================================================================
# SOURCE != PROVENANCE
# ==========================================================================
#
# Consider:
#
#
#     source = AUTOMATIC_CLASSIFIER
#
#
# This tells Agent 11:
#
#
#     an automatic classifier produced the classification
#
#
# It does NOT tell Agent 11:
#
#
#     which classifier
#
#     which classifier version
#
#     which DLP product
#
#     which rule matched
#
#     which evidence was observed
#
#     what confidence was produced
#
#     whether a human reviewed the result
#
#
# Those may become future classification-provenance concepts.
#
#
# Likewise:
#
#
#     source = ORGANIZATION_METADATA
#
#
# does not need to contain the entire metadata record that supplied
# the classification.
#
#
# Therefore:
#
#
#     CLASSIFICATION SOURCE != CLASSIFICATION PROVENANCE
#
#
#     CLASSIFICATION SOURCE != CLASSIFICATION EVIDENCE
#
#
#     SOURCE IDENTIFIES ORIGIN
#
#     SOURCE DOES NOT EXPLAIN THE ENTIRE HISTORY
# ==========================================================================


# ==========================================================================
# DataClassification
# ==========================================================================


class DataClassification(Agent11BaseModel):
    """
    Describes the classification assigned to data involved in
    Agent 11 reasoning.

    DataClassification records classification state.

    It does not classify data, evaluate classification confidence,
    determine routing policy, authorize AI destinations, select routes,
    or invoke AI services.
    """

    # ----------------------------------------------------------------------
    # level
    # ----------------------------------------------------------------------
    #
    # level records WHAT classification has been assigned to the data.
    #
    #
    # Example:
    #
    #
    #     DataClassificationLevel.E8
    #
    #
    # means:
    #
    #
    #     THIS DATA IS CURRENTLY CLASSIFIED E8
    #
    #
    # It does NOT mean:
    #
    #
    #     route to on-premises AI
    #
    #     prohibit external AI
    #
    #     prohibit company-cloud AI
    #
    #
    # Those conclusions belong to policy.
    #
    #
    # The same classification vocabulary may be used by organizations
    # with different routing policies.
    #
    #
    #     CLASSIFICATION DESCRIBES
    #
    #     POLICY AUTHORIZES
    #
    # ----------------------------------------------------------------------

    level: DataClassificationLevel = Field(
        description=(
            "Classification level currently assigned to the data."
        ),
    )

    # ----------------------------------------------------------------------
    # source
    # ----------------------------------------------------------------------
    #
    # source records WHERE the classification assertion originated.
    #
    #
    # Example:
    #
    #
    #     DataClassificationSource.ORGANIZATION_METADATA
    #
    #
    # means:
    #
    #
    #     organization-controlled metadata supplied the classification
    #
    #
    # while:
    #
    #
    #     DataClassificationSource.AUTOMATIC_CLASSIFIER
    #
    #
    # means:
    #
    #
    #     an automated classification mechanism supplied the
    #     classification
    #
    #
    # These classifications may have different future:
    #
    #
    #     trust requirements
    #
    #     review requirements
    #
    #     evidence requirements
    #
    #     provenance requirements
    #
    #
    # But source itself does not encode those behaviors.
    #
    #
    #     SOURCE IDENTIFIES ORIGIN
    #
    #     SOURCE DOES NOT DEFINE SECURITY BEHAVIOR
    #
    # ----------------------------------------------------------------------

    source: DataClassificationSource = Field(
        description=(
            "Source from which the current data classification "
            "was established."
        ),
    )


# ==========================================================================
# EXAMPLE — ORGANIZATION METADATA
# ==========================================================================
#
# Conceptually:
#
#
#     classification = DataClassification(
#         level=DataClassificationLevel.E8,
#         source=DataClassificationSource.ORGANIZATION_METADATA,
#     )
#
#
# This tells Agent 11:
#
#
#     CLASSIFICATION:
#
#         E8
#
#
#     SOURCE:
#
#         ORGANIZATION_METADATA
#
#
# It does NOT tell Agent 11:
#
#
#     EXTERNAL_FM = DENY
#
#     COMPANY_CLOUD_LLM = DENY
#
#     COMPANY_ONPREM_LLM = ALLOW
#
#
# Those conclusions require policy evaluation.
#
#
# Conceptually:
#
#
#     DataClassification
#         level = E8
#
#              |
#              v
#
#     Policy Evaluation
#
#              |
#              +--> EXTERNAL_FM
#              |
#              +--> COMPANY_CLOUD_LLM
#              |
#              +--> COMPANY_ONPREM_LLM
#
#              |
#              v
#
#     PolicyDecision
#
#
# Therefore:
#
#
#     CLASSIFICATION DESCRIBES
#
#     POLICY AUTHORIZES
# ==========================================================================


# ==========================================================================
# EXAMPLE — AUTOMATIC CLASSIFIER
# ==========================================================================
#
# Conceptually:
#
#
#     classification = DataClassification(
#         level=DataClassificationLevel.E8,
#         source=DataClassificationSource.AUTOMATIC_CLASSIFIER,
#     )
#
#
# This records:
#
#
#     WHAT:
#
#         E8
#
#
#     WHERE FROM:
#
#         AUTOMATIC_CLASSIFIER
#
#
# It deliberately does NOT record:
#
#
#     confidence
#
#     classifier version
#
#     evidence
#
#     review status
#
#     reviewer
#
#     approval
#
#
# Those facts do not belong to this simple SEIR-I classification-state
# contract.
#
#
# Future operational experience may justify a neighboring contract for
# classification assessment, evidence, review, or provenance.
#
#
# Do not add those fields merely because they are imaginable.
#
#
#     FUTURE-AWARE != FUTURE-BLOATED
# ==========================================================================


# ==========================================================================
# AUTOMATIC CLASSIFICATION != AUTOMATIC TRUST
# ==========================================================================
#
# Suppose a future classifier reports:
#
#
#     classification:
#
#         E8
#
#
#     confidence:
#
#         90%
#
#
# The classification system must NOT interpret this as:
#
#
#     "There is a 10% chance this may safely be treated as NORMAL."
#
#
# Uncertainty about classification does not grant authority to lower
# classification.
#
#
# Depending on organizational requirements, the correct behavior may
# instead be:
#
#
#     MANUAL CONFIRMATION
#
#
# before the data proceeds.
#
#
# That review decision belongs to classification behavior and security
# governance.
#
#
# It does not belong inside DataClassification itself.
#
#
# Therefore:
#
#
#     AUTOMATIC CLASSIFICATION != AUTOMATIC TRUST
#
#
#     CLASSIFIER CONFIDENCE != AUTHORIZATION
#
#
#     UNCERTAINTY != PERMISSION TO DOWNGRADE
#
#
#     90% CERTAIN E8 != NORMAL
#
#
#     REVIEW REQUIREMENT != CLASSIFICATION LEVEL
# ==========================================================================


# ==========================================================================
# LEVEL AND SOURCE ARE INDEPENDENT FACTS
# ==========================================================================
#
# These two dimensions answer different questions:
#
#
#     level:
#
#         WHAT IS THE CLASSIFICATION?
#
#
#     source:
#
#         WHERE DID THE CLASSIFICATION COME FROM?
#
#
# Therefore:
#
#
#     level = E8
#     source = UNKNOWN
#
#
# is structurally meaningful.
#
#
# It means:
#
#
#     Agent 11 has an E8 classification,
#
# but:
#
#     the source of that classification is not currently established.
#
#
# Likewise:
#
#
#     level = UNKNOWN
#     source = ORGANIZATION_METADATA
#
#
# may be meaningful.
#
#
# It could mean that organization-controlled metadata explicitly
# indicates that classification has not yet been established.
#
#
# Whether either state should trigger:
#
#
#     manual review
#
#     policy restriction
#
#     fail-closed behavior
#
#
# belongs to behavior outside this model.
#
#
# Therefore:
#
#
#     CLASSIFICATION LEVEL != CLASSIFICATION SOURCE
#
#
#     UNKNOWN LEVEL != UNKNOWN SOURCE
# ==========================================================================


# ==========================================================================
# WHY DataClassification HAS NO CUSTOM VALIDATOR
# ==========================================================================
#
# Pydantic already establishes:
#
#
#     level
#
#         is a valid DataClassificationLevel
#
#
#     source
#
#         is a valid DataClassificationSource
#
#
# There is currently no additional cross-field invariant.
#
#
# It may be tempting to write:
#
#
#     if level == UNKNOWN:
#         source must be UNKNOWN
#
#
# But that is not necessarily true.
#
#
# It may also be tempting to write:
#
#
#     if source == AUTOMATIC_CLASSIFIER:
#         level cannot be E9
#
#
# or:
#
#
#     if source == USER_DECLARED:
#         level cannot be NORMAL
#
#
# Those would invent relationships that the domain has not established.
#
#
# They could also accidentally encode:
#
#
#     organizational policy
#
#     classification-engine behavior
#
#     trust policy
#
#
# inside a simple classification-state model.
#
#
# Do not do that.
#
#
# Therefore:
#
#
#     TWO FIELDS
#
#     ZERO CUSTOM VALIDATORS
#
#
# This is deliberate architectural restraint.
#
#
#     VALIDATION SHOULD REPRESENT A REAL DOMAIN INVARIANT
#
#
#     VALIDATION SHOULD NOT INVENT ONE
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
# CLASSIFICATION DOES NOT CONTAIN POLICY
# ==========================================================================
#
# DO NOT create:
#
#
#     class DataClassification(...):
#
#         level: DataClassificationLevel
#
#         source: DataClassificationSource
#
#         external_allowed: bool
#
#         company_cloud_allowed: bool
#
#         company_onprem_allowed: bool
#
#
# That would collapse:
#
#
#     CLASSIFICATION
#
# and:
#
#     POLICY
#
#
# into one object.
#
#
# Correct separation:
#
#
#     DataClassification
#
#         level = E8
#
#              |
#              v
#
#     DataRoutePolicy
#
#         E8 + EXTERNAL_FM = DENY
#
#              |
#              v
#
#     PolicyDecision
#
#         request X + EXTERNAL_FM = DENY
#
#
# Therefore:
#
#
#     CLASSIFICATION != POLICY
#
#
#     CLASSIFICATION != ROUTING DOMAIN
#
#
#     CLASSIFICATION != POLICY DECISION
#
#
#     CLASSIFICATION INFORMS POLICY
#
#
#     POLICY CONSTRAINS ROUTING
# ==========================================================================


# ==========================================================================
# CLASSIFICATION LEVEL IS VOCABULARY — NOT AN ENGINE
# ==========================================================================
#
# SEIR-I classification levels appear naturally ordered:
#
#
#     NORMAL
#
#         <
#
#     E7
#
#         <
#
#     E8
#
#         <
#
#     E9
#
#
# Do not put behavior such as:
#
#
#     __lt__()
#
#     highest()
#
#     dominates()
#
#     aggregate()
#
#     downgrade()
#
#
# into DataClassificationLevel merely because this ordering currently
# appears obvious.
#
#
# The enum defines vocabulary.
#
#
# Future classification behavior may need to answer:
#
#
#     Which classification dominates?
#
#     How are several classifications aggregated?
#
#     Can a classification be changed?
#
#     Who has authority to change it?
#
#
# Those are classification-behavior and governance questions.
#
#
# Furthermore, future classification may become multidimensional.
#
#
# Therefore:
#
#
#     ENUM = VOCABULARY
#
#
#     ENUM != CLASSIFICATION ENGINE
#
#
#     LEVEL ORDERING != AUTOMATIC SECURITY BEHAVIOR
# ==========================================================================


# ==========================================================================
# DataClassification DOES NOT KNOW
# ==========================================================================
#
# DataClassification intentionally does not own:
#
#
#     request_id
#
#     user_id
#
#     routing_domain
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
#     policy status
#
#     network state
#
#     service health
#
#     selected route
#
#     token cost
#
#     latency
#
#     AI response
#
#
# It also does not currently own:
#
#
#     confidence
#
#     evidence
#
#     classifier version
#
#     DLP rule
#
#     reviewer
#
#     approval state
#
#     reclassification history
#
#     declassification authority
#
#
# Some of these may become neighboring classification-domain concepts
# in SEIR-II.
#
#
# But:
#
#
#     USED DURING CLASSIFICATION
#
# does not automatically mean:
#
#     OWNED BY DataClassification
#
#
# Before adding another field, ask:
#
#
#     WHICH THING OWNS WHICH FACT?
# ==========================================================================


# ==========================================================================
# THE COMPLETE SEIR-I CONTRACT
# ==========================================================================
#
# After all of the architectural explanation above, the executable
# DataClassification contract remains:
#
#
#     DataClassification
#
#         level
#
#         source
#
#
# That's it.
#
#
#     TWO FIELDS
#
#     ZERO CUSTOM VALIDATORS
#
#
# This is not underengineering.
#
#
# The model is small because its responsibility is small.
#
#
#     SMALL RESPONSIBILITY
#
#         ->
#
#     SMALL DOMAIN CONTRACT
#
#
# Complexity belongs in the behavior that actually requires it.
# ==========================================================================


# ==========================================================================
# PART I — FINAL INVARIANTS
# ==========================================================================
#
#     DataClassification = CLASSIFICATION STATE
#
#
#     DataClassification ANSWERS:
#
#         WHAT CLASSIFICATION HAS BEEN ASSIGNED?
#
#
#     CLASSIFICATION DESCRIBES DATA
#
#
#     POLICY AUTHORIZES USE OF DATA
#
#
#     ROUTING SELECTS A VIABLE DESTINATION
#
#
#     DATA CLASSIFICATION != POLICY
#
#
#     DATA CLASSIFICATION != ROUTING
#
#
#     CLASSIFIED != AUTHORIZED
#
#
#     CLASSIFICATION != DESTINATION
#
#
#     CLASSIFICATION != ROUTING DOMAIN
#
#
#     CLASSIFICATION != POLICY DECISION
#
#
#     CLASSIFICATION INFORMS POLICY
#
#
#     POLICY CONSTRAINS ROUTING
#
#
#     CLASSIFICATION LEVEL != ROUTING POLICY
#
#
#     CLASSIFICATION LEVEL != AUTHORIZATION
#
#
#     UNKNOWN != NORMAL
#
#
#     UNKNOWN != LOW SENSITIVITY
#
#
#     UNKNOWN != SAFE
#
#
#     UNKNOWN != PERMISSION
#
#
#     CONSERVATIVE BEHAVIOR != FALSE OBSERVATION
#
#
#     CLASSIFICATION LEVEL != CLASSIFICATION SOURCE
#
#
#     UNKNOWN LEVEL != UNKNOWN SOURCE
#
#
#     SOURCE != CORRECTNESS
#
#
#     SOURCE != CONFIDENCE
#
#
#     SOURCE != EVIDENCE
#
#
#     SOURCE != AUTHORITY
#
#
#     SOURCE != APPROVAL
#
#
#     CLASSIFICATION SOURCE != CLASSIFICATION PROVENANCE
#
#
#     CLASSIFICATION SOURCE != CLASSIFICATION EVIDENCE
#
#
#     SOURCE IDENTIFIES ORIGIN
#
#
#     SOURCE DOES NOT EXPLAIN THE ENTIRE HISTORY
#
#
#     AUTOMATIC CLASSIFICATION != AUTOMATIC TRUST
#
#
#     CLASSIFIER CONFIDENCE != AUTHORIZATION
#
#
#     UNCERTAINTY != PERMISSION TO DOWNGRADE
#
#
#     90% CERTAIN E8 != NORMAL
#
#
#     REVIEW REQUIREMENT != CLASSIFICATION LEVEL
#
#
#     ENUM = VOCABULARY
#
#
#     ENUM != CLASSIFICATION ENGINE
#
#
#     LEVEL ORDERING != AUTOMATIC SECURITY BEHAVIOR
#
#
#     USED DURING CLASSIFICATION
#         !=
#     OWNED BY DataClassification
#
#
#     TWO FIELDS
#
#
#     ZERO CUSTOM VALIDATORS
#
#
#     VALIDATION SHOULD REPRESENT A REAL DOMAIN INVARIANT
#
#
#     VALIDATION SHOULD NOT INVENT ONE
#
#
#     VALIDATION SHOULD NOT BE DECORATION
#
#
#     SMALL RESPONSIBILITY
#         ->
#     SMALL DOMAIN CONTRACT
#
#
#     WHICH THING OWNS WHICH FACT?
#
#
#     PYDANTIC DEFINES THE DOMAIN CONTRACT
#
#     CLASSIFICATION BEHAVIOR PRODUCES THE DOMAIN OBJECT
# ==========================================================================
# END PART I
# ==========================================================================

# ==========================================================================
# PART II — CLASSIFICATION SEMANTICS AND SEIR-II EXPANSION
# ==========================================================================
#
# THIS SECTION IS ARCHITECTURAL DOCUMENTATION ONLY.
#
#
# Part I defined:
#
#
#     DataClassification
#
#         WHAT CLASSIFICATION HAS BEEN ASSIGNED TO THIS DATA?
#
#
# Part II preserves:
#
#
#     HOW MUST CLASSIFICATION SEMANTICS BE TREATED
#     AS AGENT 11 BECOMES MORE SOPHISTICATED?
#
#
# This section intentionally introduces:
#
#
#     NO additional Pydantic fields
#
#     NO additional validators
#
#     NO classification engine
#
#     NO DLP integration
#
#     NO confidence threshold
#
#     NO manual-review workflow
#
#     NO aggregation engine
#
#     NO declassification engine
#
#     NO policy behavior
#
#
# Those capabilities may eventually exist.
#
# They do not belong inside the DataClassification domain object merely
# because DataClassification participates in those workflows.
#
#
# The purpose of Part II is:
#
#
#     PRESERVE THE FUTURE PROBLEM
#
#     WITHOUT PRETENDING TO HAVE THE FUTURE SOLUTION
#
#
# Therefore:
#
#
#     FUTURE-AWARE != FUTURE-BLOATED
# ==========================================================================


# ==========================================================================
# THE PERMANENT CLASSIFICATION BOUNDARY
# ==========================================================================
#
# Classification answers:
#
#
#     "WHAT KIND OF DATA IS THIS?"
#
#
# Policy answers:
#
#
#     "MAY THIS DATA BE USED WITH THIS DESTINATION?"
#
#
# Routing answers:
#
#
#     "WHICH AUTHORIZED, CAPABLE, AVAILABLE, REACHABLE
#      DESTINATION SHOULD BE USED?"
#
#
# Conceptually:
#
#
#                  DATA
#                   |
#                   v
#          DataClassification
#                   |
#                   v
#           Policy Evaluation
#                   |
#                   v
#           PolicyDecision
#                   |
#                   v
#        Candidate Evaluation
#                   |
#                   v
#          RoutingDecision
#
#
# Classification is an input to policy.
#
# Classification is not policy.
#
#
# Therefore:
#
#
#     CLASSIFICATION != POLICY
#
#     CLASSIFICATION != AUTHORIZATION
#
#     CLASSIFICATION != ROUTING
#
#     CLASSIFICATION != DESTINATION
#
#     CLASSIFICATION INFORMS POLICY
#
#     POLICY CONSTRAINS ROUTING
# ==========================================================================


# ==========================================================================
# UNKNOWN MUST REMAIN UNKNOWN
# ==========================================================================
#
# Agent 11 must preserve the difference between:
#
#
#     NORMAL
#
# and:
#
#     UNKNOWN
#
#
# NORMAL means:
#
#
#     THE DATA HAS BEEN CLASSIFIED AS NORMAL
#
#
# UNKNOWN means:
#
#
#     THE DATA'S CLASSIFICATION HAS NOT BEEN ESTABLISHED
#
#
# These are fundamentally different observations.
#
#
# Never implement:
#
#
#     if classification.level == DataClassificationLevel.UNKNOWN:
#         classification.level = DataClassificationLevel.NORMAL
#
#
# merely because NORMAL makes downstream processing easier.
#
#
# This follows the broader Agent 11 semantic pattern:
#
#
#     NETWORK:
#
#         UNKNOWN != UNAVAILABLE
#
#
#     POLICY:
#
#         INDETERMINATE != DENY
#
#
#     CLASSIFICATION:
#
#         UNKNOWN != NORMAL
#
#
# Security behavior may be conservative when classification is unknown.
#
# But conservative behavior must not falsify the observed state.
#
#
# Therefore:
#
#
#     UNKNOWN != NORMAL
#
#     UNKNOWN != LOW SENSITIVITY
#
#     UNKNOWN != SAFE
#
#     UNKNOWN != PERMISSION
#
#
#     CONSERVATIVE BEHAVIOR != FALSE OBSERVATION
# ==========================================================================


# ==========================================================================
# AUTOMATED CLASSIFICATION AND UNCERTAINTY
# ==========================================================================
#
# Future classification mechanisms may include:
#
#
#     deterministic rules
#
#     metadata
#
#     pattern matching
#
#     DLP systems
#
#     machine-learning classifiers
#
#     language models
#
#     combinations of these systems
#
#
# Some mechanisms may produce probabilistic results.
#
#
# Example:
#
#
#     predicted classification:
#
#         E8
#
#
#     confidence:
#
#         90%
#
#
# This must NOT be interpreted as:
#
#
#     "There is a 10% chance that treating the data as NORMAL
#      is acceptable."
#
#
# Classification uncertainty is uncertainty about what the data is.
#
# It is not permission to lower security requirements.
#
#
# Therefore:
#
#
#     UNCERTAINTY != PERMISSION TO DOWNGRADE
#
#
#     CLASSIFIER CONFIDENCE != AUTHORIZATION
#
#
#     PROBABILISTIC CLASSIFICATION
#         !=
#     PROBABILISTIC SECURITY POLICY
#
#
#     90% CERTAIN E8 != NORMAL
#
#
# The classifier may be probabilistic.
#
# The organization's requirement to establish an acceptable
# classification before sensitive processing does not therefore become
# probabilistic.
# ==========================================================================


# ==========================================================================
# MANUAL REVIEW IS A SEPARATE SECURITY DECISION
# ==========================================================================
#
# Future classification behavior may require human confirmation when an
# automated system cannot establish sufficient certainty.
#
#
# Conceptually:
#
#
#                  DATA
#                   |
#                   v
#          Automatic Classifier
#                   |
#                   v
#       Classification Assessment
#                   |
#          +--------+--------+
#          |                 |
#          v                 v
#      sufficient        insufficient
#       certainty         certainty
#          |                 |
#          v                 v
#       continue        MANUAL REVIEW
#
#
# Example:
#
#
#     predicted classification:
#
#         E8
#
#
#     confidence:
#
#         90%
#
#
# Organization security requirements may determine that 90% certainty
# is insufficient for autonomous processing.
#
#
# The correct behavior may therefore be:
#
#
#     STOP
#
#     REQUIRE HUMAN CONFIRMATION
#
#     CONTINUE ONLY AFTER CLASSIFICATION IS ACCEPTABLY ESTABLISHED
#
#
# The threshold belongs to classification behavior and organizational
# security governance.
#
#
# It does NOT belong in:
#
#
#     DataClassificationLevel
#
#
# and does not automatically belong on:
#
#
#     DataClassification
#
#
# Therefore:
#
#
#     CLASSIFICATION RESULT != REVIEW DECISION
#
#
#     REVIEW REQUIREMENT != CLASSIFICATION LEVEL
#
#
#     AUTOMATED CLASSIFICATION != AUTOMATIC TRUST
#
#
#     HUMAN CONFIRMATION MAY BE A SECURITY CONTROL
#
#
# Future operational experience may justify a neighboring contract such
# as:
#
#
#     ClassificationAssessment
#
# or:
#
#     ClassificationReview
#
#
# Do not implement either merely because the name can be imagined.
# ==========================================================================


# ==========================================================================
# CLASSIFICATION SOURCE != CLASSIFICATION AUTHORITY
# ==========================================================================
#
# Part I records:
#
#
#     DataClassificationSource
#
#
# Source answers:
#
#
#     "WHERE DID THIS CLASSIFICATION ASSERTION COME FROM?"
#
#
# It does NOT answer:
#
#
#     "WHO HAS AUTHORITY TO CLASSIFY THIS DATA?"
#
#
# or:
#
#     "WHO HAS AUTHORITY TO CHANGE THIS CLASSIFICATION?"
#
#
# Example:
#
#
#     source = USER_DECLARED
#
#
# tells Agent 11 that the user supplied the classification.
#
#
# It does NOT automatically mean the user has authority to:
#
#
#     lower classification
#
#     override organization metadata
#
#     override DLP findings
#
#     declassify data
#
#
# Likewise:
#
#
#     source = AUTOMATIC_CLASSIFIER
#
#
# identifies the source of the assertion.
#
# It does not automatically establish that the result is sufficiently
# authoritative for every security workflow.
#
#
# Future classification governance may need to distinguish:
#
#
#     source
#
#     authority
#
#     confidence
#
#     evidence
#
#     review
#
#     approval
#
#
# Therefore:
#
#
#     SOURCE != AUTHORITY
#
#     SOURCE != CONFIDENCE
#
#     SOURCE != EVIDENCE
#
#     SOURCE != APPROVAL
#
#
#     WHO ASSERTED A CLASSIFICATION
#         !=
#     WHO MAY CHANGE A CLASSIFICATION
# ==========================================================================


# ==========================================================================
# MULTIPLE DATA ITEMS AND EFFECTIVE CLASSIFICATION
# ==========================================================================
#
# An AI request may contain several pieces of data.
#
#
# Example:
#
#
#     task:
#
#         NORMAL
#
#
#     context A:
#
#         E7
#
#
#     context B:
#
#         E8
#
#
#     context C:
#
#         NORMAL
#
#
# Agent 11 may need an effective classification for the complete
# reasoning request.
#
#
# A simple SEIR-I behavior might conceptually determine:
#
#
#     NORMAL
#       +
#     E7
#       +
#     E8
#       +
#     NORMAL
#
#       =
#
#     E8
#
#
# But:
#
#
#     DataClassification
#
# should NOT calculate this.
#
#
# Aggregation is behavior.
#
#
# DataClassification answers:
#
#
#     WHAT CLASSIFICATION EXISTS?
#
#
# Classification aggregation answers:
#
#
#     HOW SHOULD SEVERAL CLASSIFICATIONS BE COMBINED?
#
#
# Therefore:
#
#
#     CLASSIFICATION STATE != CLASSIFICATION AGGREGATION
#
#
#     DOMAIN OBJECT != AGGREGATION ENGINE
# ==========================================================================


# ==========================================================================
# "HIGHEST LEVEL WINS" IS NOT A PERMANENT DOMAIN ASSUMPTION
# ==========================================================================
#
# SEIR-I may treat:
#
#
#     NORMAL < E7 < E8 < E9
#
#
# as an operational sensitivity hierarchy.
#
#
# That may be perfectly sufficient for the initial implementation.
#
#
# But future enterprise classification may become multidimensional.
#
#
# Data may eventually carry concepts such as:
#
#
#     sensitivity
#
#     customer boundary
#
#     compartment
#
#     regulatory domain
#
#     residency requirement
#
#     handling requirement
#
#
# Example:
#
#
#     sensitivity:
#
#         E8
#
#
#     customer:
#
#         ACME
#
#
#     regulatory_domain:
#
#         FINANCIAL
#
#
#     residency:
#
#         US_ONLY
#
#
#     compartment:
#
#         TRADING_MODEL
#
#
# There may no longer be one universal:
#
#
#     highest()
#
#
# operation.
#
#
# Therefore:
#
#
#     LEVEL ORDERING != COMPLETE CLASSIFICATION SEMANTICS
#
#
#     "HIGHEST LEVEL WINS"
#         MAY BE SEIR-I BEHAVIOR
#
#     "HIGHEST LEVEL WINS"
#         MUST NOT BECOME A PERMANENT DOMAIN ASSUMPTION
#
#
# Keep ordering and aggregation behavior outside the enum.
# ==========================================================================


# ==========================================================================
# CLASSIFICATION INHERITANCE
# ==========================================================================
#
# Future Agent 11 workflows will create derived data.
#
#
# Example:
#
#
#     E8 SOURCE
#         |
#         v
#     AI ANALYSIS
#         |
#         v
#     DERIVED OUTPUT
#
#
# Another example:
#
#
#     E9 DOCUMENT
#         |
#         v
#     AI SUMMARY
#         |
#         v
#     SUMMARY DOCUMENT
#
#
# Derived information may need to inherit classification from its
# source data.
#
#
# The exact inheritance rules belong to classification behavior and
# governance.
#
#
# Do not put:
#
#
#     output.level = input.level
#
#
# inside DataClassification itself.
#
#
# DataClassification records state.
#
# It does not govern information-flow inheritance.
#
#
# Therefore:
#
#
#     CLASSIFICATION STATE != CLASSIFICATION INHERITANCE
#
#
#     DERIVED DATA REQUIRES CLASSIFICATION
#
#
#     DERIVATION != DECLASSIFICATION
# ==========================================================================


# ==========================================================================
# TRANSFORMATION != DECLASSIFICATION
# ==========================================================================
#
# This is a permanent security invariant.
#
#
# Suppose:
#
#
#     E9 SOURCE DOCUMENT
#             |
#             v
#        SUMMARIZATION
#             |
#             v
#       SHORT SUMMARY
#
#
# The output contains fewer words.
#
#
# That does NOT establish:
#
#
#     LOWER CLASSIFICATION
#
#
# Likewise:
#
#
#     translation
#
#     formatting
#
#     summarization
#
#     extraction
#
#     paraphrasing
#
#     tokenization
#
#     embedding
#
#     conversion to structured data
#
#
# do not inherently declassify information.
#
#
# Therefore:
#
#
#     TRANSFORMATION != DECLASSIFICATION
#
#
#     SUMMARIZATION != DECLASSIFICATION
#
#
#     TRANSLATION != DECLASSIFICATION
#
#
#     EXTRACTION != DECLASSIFICATION
#
#
#     SHORTER != LESS SENSITIVE
#
#
#     DERIVED != DECLASSIFIED
# ==========================================================================


# ==========================================================================
# REDACTION != AUTOMATIC DECLASSIFICATION
# ==========================================================================
#
# Redaction deserves explicit treatment.
#
#
# Example:
#
#
#     E9 DOCUMENT
#         |
#         v
#     REDACTION PROCESS
#         |
#         v
#     MODIFIED DOCUMENT
#
#
# Even if sensitive information appears to have been removed:
#
#
#     REDACTED
#
# does not automatically mean:
#
#     DECLASSIFIED
#
#
# Declassification may require:
#
#
#     verification
#
#     evidence
#
#     authority
#
#     approval
#
#     governance
#
#     audit
#
#
# Therefore:
#
#
#     REDACTION != AUTOMATIC DECLASSIFICATION
#
#
#     CONTENT MODIFICATION != AUTHORITY TO LOWER CLASSIFICATION
#
#
# A successful redaction may eventually become evidence supporting a
# declassification decision.
#
#
# It is not itself the declassification decision.
# ==========================================================================


# ==========================================================================
# DECLASSIFICATION IS A GOVERNED STATE TRANSITION
# ==========================================================================
#
# Future Agent 11 implementations may need to lower classification.
#
#
# Example:
#
#
#     E9
#
#       |
#       v
#
#     E8
#
#
# or:
#
#
#     E8
#
#       |
#       v
#
#     NORMAL
#
#
# These are not ordinary data mutations.
#
#
# They are security-relevant state transitions.
#
#
# Future declassification may require:
#
#
#     authority
#
#     evidence
#
#     reason
#
#     approval
#
#     provenance
#
#     audit
#
#
# Agent11BaseModel currently uses:
#
#
#     validate_assignment=True
#
#
# Therefore Pydantic can validate that:
#
#
#     classification.level = DataClassificationLevel.NORMAL
#
#
# contains a valid enum value.
#
#
# Pydantic cannot establish:
#
#
#     THE ACTOR WAS AUTHORIZED TO DECLASSIFY THE DATA
#
#
# This distinction is critical.
#
#
# Therefore:
#
#
#     VALID TYPE != AUTHORIZED STATE TRANSITION
#
#
#     PYDANTIC VALIDATION != DECLASSIFICATION AUTHORITY
#
#
#     DECLASSIFICATION != ORDINARY FIELD ASSIGNMENT
#
#
# If Agent 11 eventually supports declassification, it deserves an
# explicit governance boundary.
# ==========================================================================


# ==========================================================================
# RECLASSIFICATION IS ALSO A GOVERNED TRANSITION
# ==========================================================================
#
# Classification changes are not always downgrades.
#
#
# Example:
#
#
#     E7
#
#       |
#       v
#
#     E8
#
#
# after additional sensitive information is discovered.
#
#
# Future classification lifecycle behavior may need:
#
#
#     previous classification
#
#     new classification
#
#     reason
#
#     authority
#
#     evidence
#
#     timestamp
#
#     audit record
#
#
# Again:
#
#
#     VALID ENUM ASSIGNMENT
#
# does not establish:
#
#     AUTHORIZED CLASSIFICATION CHANGE
#
#
# Therefore:
#
#
#     RECLASSIFICATION != ORDINARY MUTATION
#
#
#     RECLASSIFICATION != AUTOMATIC DECLASSIFICATION
#
#
#     VALID STATE != AUTHORIZED TRANSITION
# ==========================================================================


# ==========================================================================
# AI-GENERATED OUTPUT REQUIRES CLASSIFICATION
# ==========================================================================
#
# AI output must not automatically be assumed NORMAL.
#
#
# Example:
#
#
#     E8 INPUT
#         |
#         v
#      AI MODEL
#         |
#         v
#     GENERATED OUTPUT
#
#
# The generated output may:
#
#
#     reproduce sensitive information
#
#     summarize sensitive information
#
#     infer sensitive information
#
#     combine sensitive facts
#
#     reveal information not directly copied from the input
#
#
# Therefore:
#
#
#     AI OUTPUT != NORMAL BY DEFAULT
#
#
#     AI-GENERATED != PUBLIC
#
#
#     AI-GENERATED != DECLASSIFIED
#
#
# Future Agent 11 workflows may need to classify output before:
#
#
#     storage
#
#     logging
#
#     transmission
#
#     user delivery
#
#     MCP delivery
#
#     tool execution
#
#     creation of downstream artifacts
#
#
# Classification therefore may need to exist throughout the information
# lifecycle rather than only at request ingestion.
# ==========================================================================


# ==========================================================================
# SEIR-II — MULTI-AGENT INFORMATION FLOW
# ==========================================================================
#
# Future Agent 11 workflows may resemble:
#
#
#     USER DATA
#         |
#         v
#      Agent A
#         |
#         v
#      Agent B
#         |
#         v
#      MCP Tool
#         |
#         v
#      Agent C
#         |
#         v
#     FINAL OUTPUT
#
#
# Data may cross several:
#
#
#     reasoning boundaries
#
#     service boundaries
#
#     agent boundaries
#
#     tool boundaries
#
#     storage boundaries
#
#
# Classification cannot simply disappear after the first inference
# request.
#
#
# Future architecture may need to preserve classification through:
#
#
#     agent messages
#
#     reasoning handoffs
#
#     MCP requests
#
#     MCP responses
#
#     tool results
#
#     generated artifacts
#
#     persisted context
#
#
# Therefore:
#
#
#     CLASSIFICATION IS NOT ONLY AN INGEST CONCERN
#
#
#     CLASSIFICATION MAY NEED TO SURVIVE THE DATA LIFECYCLE
#
#
#     AGENT HANDOFF != CLASSIFICATION RESET
#
#
#     TOOL RESULT != NORMAL BY DEFAULT
#
#
# Do not implement this lifecycle machinery inside DataClassification.
#
# Preserve the requirement for the future behavior that owns it.
# ==========================================================================


# ==========================================================================
# SEIR-II — DLP INTEGRATION
# ==========================================================================
#
# Future classification may consume information from enterprise DLP
# systems.
#
#
# Conceptually:
#
#
#         DLP SYSTEM
#             |
#             v
#           ADAPTER
#             |
#             v
#     Classification Behavior
#             |
#             v
#      DataClassification
#
#
# External DLP technologies may expose:
#
#
#     vendor-specific labels
#
#     confidence scores
#
#     rule identifiers
#
#     findings
#
#     evidence
#
#     severity
#
#
# Do not make DataClassification a vendor-specific DLP object.
#
#
# Adapters should translate external technology into Agent 11 domain
# semantics.
#
#
# Therefore:
#
#
#     DLP SYSTEM != AGENT 11 DOMAIN CONTRACT
#
#
#     DLP VENDOR VOCABULARY
#         !=
#     AGENT 11 CLASSIFICATION VOCABULARY
#
#
#     CLASSIFICATION TECHNOLOGY MAY CHANGE
#
#
#     DOMAIN SEMANTICS SHOULD SURVIVE
# ==========================================================================


# ==========================================================================
# SEIR-II — CLASSIFICATION PROVENANCE
# ==========================================================================
#
# Future operators may ask:
#
#
#     "Why does Agent 11 believe this data is E8?"
#
#
# Part I records:
#
#
#     level
#
#     source
#
#
# That is intentionally not a complete provenance record.
#
#
# Future provenance may include:
#
#
#     classifier identifier
#
#     classifier version
#
#     DLP rule
#
#     evidence
#
#     evaluated_at
#
#     inherited classifications
#
#     original classification
#
#     reviewer
#
#     approval
#
#     reclassification history
#
#
# Do not automatically add these fields to DataClassification.
#
#
# A future neighboring provenance contract may own them.
#
#
# Therefore:
#
#
#     CLASSIFICATION != CLASSIFICATION PROVENANCE
#
#
#     SOURCE != COMPLETE PROVENANCE
#
#
#     CLASSIFICATION != CLASSIFICATION EVIDENCE
#
#
#     REFERENCE EVIDENCE
#
#
#     DO NOT DUPLICATE EVIDENCE
#
#
#     AUDITABLE != EVERYTHING IN ONE OBJECT
# ==========================================================================


# ==========================================================================
# SEIR-II — MULTIDIMENSIONAL CLASSIFICATION
# ==========================================================================
#
# SEIR-I deliberately begins with one sensitivity dimension:
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
# Future enterprise requirements may require several independent
# dimensions.
#
#
# Conceptually:
#
#
#     sensitivity:
#
#         E8
#
#
#     customer:
#
#         CUSTOMER_A
#
#
#     regulatory_domain:
#
#         FINANCIAL
#
#
#     residency:
#
#         US_ONLY
#
#
#     compartment:
#
#         TRADING_MODEL
#
#
#     handling:
#
#         NO_EXTERNAL_AI
#
#
# These facts should not automatically become additional members of:
#
#
#     DataClassificationLevel
#
#
# For example, do NOT create:
#
#
#     E8_US_ONLY
#
#     E8_FINANCIAL
#
#     E8_CUSTOMER_A
#
#     E8_CUSTOMER_A_US_ONLY_FINANCIAL
#
#
# That would collapse several independent domains into one exploding
# enum vocabulary.
#
#
# Therefore:
#
#
#     SENSITIVITY != CUSTOMER BOUNDARY
#
#
#     SENSITIVITY != REGULATORY DOMAIN
#
#
#     SENSITIVITY != RESIDENCY
#
#
#     SENSITIVITY != COMPARTMENT
#
#
#     SENSITIVITY != HANDLING REQUIREMENT
#
#
#     CLASSIFICATION DIMENSIONS SHOULD REMAIN SEMANTICALLY DISTINCT
#
#
# Let operational evidence determine whether SEIR-II actually needs
# these additional dimensions.
# ==========================================================================


# ==========================================================================
# SEIR-II — CLASSIFICATION AND RESIDENCY
# ==========================================================================
#
# Classification and residency may interact through policy.
#
#
# Example:
#
#
#     classification:
#
#         E8
#
#
#     residency:
#
#         US_ONLY
#
#
# These are different facts.
#
#
# Do not redefine:
#
#
#     E8
#
# to mean:
#
#     E8_AND_US_ONLY
#
#
# Instead:
#
#
#     DataClassification
#              |
#              |
#              +------------+
#                           |
#     ResidencyRequirement  |
#              |            |
#              +------------+
#                           |
#                           v
#                    Policy Evaluation
#
#
# Classification describes sensitivity.
#
# Residency describes a location/handling requirement.
#
# Policy may consume both.
#
#
# Therefore:
#
#
#     CLASSIFICATION != RESIDENCY
#
#
#     RESIDENCY != SENSITIVITY
#
#
#     POLICY MAY CONSUME BOTH
# ==========================================================================


# ==========================================================================
# SEIR-II — CLASSIFICATION AND POLICY MUST REMAIN SEPARATE
# ==========================================================================
#
# As classification becomes richer, there will be pressure to put
# handling rules directly into the classification model.
#
#
# Example temptation:
#
#
#     DataClassification(
#         level=E8,
#         allow_external=False,
#         allow_cloud=False,
#         require_onprem=True,
#     )
#
#
# Do not do this.
#
#
# A classification should remain usable across different policy
# environments.
#
#
# Example:
#
#
# Organization A:
#
#     E8 + COMPANY_CLOUD_LLM = DENY
#
#
# Organization B:
#
#     E8 + COMPANY_CLOUD_LLM = ALLOW
#
#     but only for approved sovereign deployments
#
#
# The meaning of:
#
#
#     E8
#
# should not need to change between those organizations.
#
#
# Therefore:
#
#
#     CLASSIFICATION DESCRIBES THE DATA
#
#
#     POLICY DESCRIBES PERMITTED HANDLING
#
#
#     ORGANIZATIONAL POLICY != CLASSIFICATION DEFINITION
# ==========================================================================


# ==========================================================================
# SEIR-II — POSSIBLE FUTURE NEIGHBORING CONTRACTS
# ==========================================================================
#
# DO NOT IMPLEMENT THESE MERELY BECAUSE THEY ARE LISTED HERE.
#
#
# Operational experience may eventually justify concepts such as:
#
#
#     ClassificationAssessment
#
#     ClassificationEvidence
#
#     ClassificationProvenance
#
#     ClassificationReview
#
#     ClassificationAuthority
#
#     ClassificationChange
#
#     ClassificationAggregation
#
#     ClassificationContext
#
#     DeclassificationDecision
#
#     Compartment
#
#     HandlingRequirement
#
#
# These are conceptual expansion points.
#
#
# They are NOT a SEIR-I TODO list.
#
#
# When a new requirement becomes real:
#
#
#     IDENTIFY THE NEW FACT
#             |
#             v
#     IDENTIFY THE DOMAIN THAT OWNS THE FACT
#             |
#             v
#     CREATE THE APPROPRIATE CONTRACT
#             |
#             v
#     LET CLASSIFICATION / POLICY CONSUME IT
#
#
# Do not respond to every requirement by adding another optional field
# to DataClassification.
#
#
# Therefore:
#
#
#     CONCEPTUAL TRAPDOOR != REQUIRED IMPLEMENTATION
#
#
#     FUTURE NOTE != TODO LIST
#
#
#     ADD THE DOMAIN THAT OWNS THE NEW FACT
# ==========================================================================


# ==========================================================================
# SEIR-II — TEST WHAT SEIR-I ACTUALLY TEACHES US
# ==========================================================================
#
# Before expanding this model, use operational evidence.
#
#
# Future engineers should ask:
#
#
#     How often was classification UNKNOWN?
#
#
#     Why was classification UNKNOWN?
#
#
#     Which classification sources were most reliable?
#
#
#     How often did automatic classification require manual review?
#
#
#     Which confidence levels were operationally meaningful?
#
#
#     Did classification source affect review requirements?
#
#
#     Did requests routinely contain multiple classification levels?
#
#
#     Was "highest level wins" actually sufficient?
#
#
#     Did AI-generated output require independent classification?
#
#
#     Did derived data preserve classification correctly?
#
#
#     Did redaction create real declassification requirements?
#
#
#     Were unauthorized downgrade attempts observed?
#
#
#     Did customer requirements require additional dimensions?
#
#
#     Did regulatory requirements require additional dimensions?
#
#
#     Did residency become part of classification or remain a separate
#     policy input?
#
#
#     Did DLP integration require richer evidence/provenance?
#
#
#     Did multi-agent workflows lose classification context?
#
#
# These observations should drive SEIR-II.
#
#
# Architecture should expand because:
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
# Not because:
#
#
#     "WE CAN IMAGINE ANOTHER FIELD."
# ==========================================================================


# ==========================================================================
# SEIR-II — PRESERVE CLASSIFICATION FAILURE DATA
# ==========================================================================
#
# Some of the most useful SEIR-II requirements may be discovered when
# classification fails.
#
#
# Preserve future telemetry around:
#
#
#     UNKNOWN classifications
#
#     classifier disagreement
#
#     insufficient confidence
#
#     manual-review requests
#
#     manual-review outcomes
#
#     attempted classification changes
#
#     attempted downgrades
#
#     DLP findings
#
#     inherited classifications
#
#     output classifications
#
#     classification lost during agent handoff
#
#
# A workflow stopping for manual classification review may be:
#
#
#     SUCCESSFUL SECURITY ENFORCEMENT
#
#
# even though:
#
#
#     THE AI REQUEST DID NOT CONTINUE
#
#
# Therefore:
#
#
#     REQUEST INTERRUPTION != SECURITY FAILURE
#
#
#     MANUAL REVIEW != SYSTEM FAILURE
#
#
#     CONSERVATIVE CLASSIFICATION BEHAVIOR != BROKEN SYSTEM
#
#
# Telemetry should eventually preserve enough detail to tell us which
# condition actually occurred.
# ==========================================================================


# ==========================================================================
# FRAMEWORK INDEPENDENCE
# ==========================================================================
#
# Future classification behavior may participate in:
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
# Framework adapters may transport Agent 11 classification contracts.
#
#
# Framework terminology should not redefine Agent 11 classification
# semantics.
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
#     CLASSIFICATION TECHNOLOGY MAY CHANGE
#
#
#     CLASSIFICATION SEMANTICS SHOULD SURVIVE
# ==========================================================================


# ==========================================================================
# CHEWBACCA CLASSIFICATION REVIEW
# ==========================================================================
#
# Automatic Classifier:
#
#     "E8. Confidence: 90%."
#
#
# Chewbacca:
#
#     "90% is an A."
#
#
# Security:
#
#     "This is not English Literature."
#
#
# Chewbacca:
#
#     "So what happens to the other 10%?"
#
#
# Agent 11:
#
#     THAT IS WHY WE HAVE REVIEW REQUIREMENTS.
#
#
# Chewbacca:
#
#     "Can I call it NORMAL until someone checks?"
#
#
# Agent 11:
#
#     UNKNOWN != NORMAL.
#
#     UNCERTAINTY != PERMISSION TO DOWNGRADE.
#
#
# Chewbacca:
#
#     "Fine. I summarized an E9 document.
#      It's only three paragraphs now."
#
#
# Agent 11:
#
#     SHORTER != LESS SENSITIVE.
#
#
# Chewbacca:
#
#     "I translated it."
#
#
# Agent 11:
#
#     TRANSLATION != DECLASSIFICATION.
#
#
# Chewbacca:
#
#     "I redacted it."
#
#
# Agent 11:
#
#     REDACTION != AUTOMATIC DECLASSIFICATION.
#
#
# Chewbacca:
#
#     "The AI generated something completely new."
#
#
# Agent 11:
#
#     AI-GENERATED != PUBLIC.
#
#
# Chewbacca:
#
#     "Can I just assign level=NORMAL?"
#
#
# Pydantic:
#
#     "NORMAL is a valid DataClassificationLevel."
#
#
# Security:
#
#     "Nobody asked whether NORMAL was a valid enum."
#
#
# Agent 11:
#
#     VALID TYPE != AUTHORIZED STATE TRANSITION.
#
#
# Chewbacca:
#
#     "So Pydantic can't decide whether I'm allowed to declassify?"
#
#
# Agent 11:
#
#     CORRECT.
#
#
# Chewbacca:
#
#     "Then I'll put declassification logic in DataClassification."
#
#
# Agent 11:
#
#     ALSO NO.
#
#
# Chewbacca:
#
#     "Which thing owns which fact?"
#
#
# Agent 11:
#
#     THERE IT IS.
# ==========================================================================


# ==========================================================================
# PART II — FINAL CLASSIFICATION INVARIANTS — DO NOT DELETE
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
#     FUTURE-AWARE != FUTURE-BLOATED
#
#
#     CLASSIFICATION ANSWERS:
#
#         WHAT KIND OF DATA IS THIS?
#
#
#     POLICY ANSWERS:
#
#         MAY THIS DATA BE USED THERE?
#
#
#     ROUTING ANSWERS:
#
#         WHICH AUTHORIZED VIABLE DESTINATION?
#
#
#     CLASSIFICATION != POLICY
#
#
#     CLASSIFICATION != AUTHORIZATION
#
#
#     CLASSIFICATION != ROUTING
#
#
#     CLASSIFICATION != DESTINATION
#
#
#     CLASSIFICATION INFORMS POLICY
#
#
#     POLICY CONSTRAINS ROUTING
#
#
#     UNKNOWN != NORMAL
#
#
#     UNKNOWN != LOW SENSITIVITY
#
#
#     UNKNOWN != SAFE
#
#
#     UNKNOWN != PERMISSION
#
#
#     CONSERVATIVE BEHAVIOR != FALSE OBSERVATION
#
#
#     UNCERTAINTY != PERMISSION TO DOWNGRADE
#
#
#     CLASSIFIER CONFIDENCE != AUTHORIZATION
#
#
#     PROBABILISTIC CLASSIFICATION
#         !=
#     PROBABILISTIC SECURITY POLICY
#
#
#     90% CERTAIN E8 != NORMAL
#
#
#     CLASSIFICATION RESULT != REVIEW DECISION
#
#
#     REVIEW REQUIREMENT != CLASSIFICATION LEVEL
#
#
#     AUTOMATED CLASSIFICATION != AUTOMATIC TRUST
#
#
#     HUMAN CONFIRMATION MAY BE A SECURITY CONTROL
#
#
#     SOURCE != AUTHORITY
#
#
#     SOURCE != CONFIDENCE
#
#
#     SOURCE != EVIDENCE
#
#
#     SOURCE != APPROVAL
#
#
#     WHO ASSERTED A CLASSIFICATION
#         !=
#     WHO MAY CHANGE A CLASSIFICATION
#
#
#     CLASSIFICATION STATE != CLASSIFICATION AGGREGATION
#
#
#     DOMAIN OBJECT != AGGREGATION ENGINE
#
#
#     LEVEL ORDERING != COMPLETE CLASSIFICATION SEMANTICS
#
#
#     "HIGHEST LEVEL WINS"
#         !=
#     PERMANENT DOMAIN ASSUMPTION
#
#
#     CLASSIFICATION STATE != CLASSIFICATION INHERITANCE
#
#
#     DERIVED DATA REQUIRES CLASSIFICATION
#
#
#     DERIVATION != DECLASSIFICATION
#
#
#     TRANSFORMATION != DECLASSIFICATION
#
#
#     SUMMARIZATION != DECLASSIFICATION
#
#
#     TRANSLATION != DECLASSIFICATION
#
#
#     EXTRACTION != DECLASSIFICATION
#
#
#     SHORTER != LESS SENSITIVE
#
#
#     REDACTION != AUTOMATIC DECLASSIFICATION
#
#
#     CONTENT MODIFICATION != AUTHORITY TO LOWER CLASSIFICATION
#
#
#     VALID TYPE != AUTHORIZED STATE TRANSITION
#
#
#     VALID STATE != AUTHORIZED TRANSITION
#
#
#     PYDANTIC VALIDATION != DECLASSIFICATION AUTHORITY
#
#
#     DECLASSIFICATION != ORDINARY FIELD ASSIGNMENT
#
#
#     RECLASSIFICATION != ORDINARY MUTATION
#
#
#     AI OUTPUT != NORMAL BY DEFAULT
#
#
#     AI-GENERATED != PUBLIC
#
#
#     AI-GENERATED != DECLASSIFIED
#
#
#     CLASSIFICATION IS NOT ONLY AN INGEST CONCERN
#
#
#     CLASSIFICATION MAY NEED TO SURVIVE THE DATA LIFECYCLE
#
#
#     AGENT HANDOFF != CLASSIFICATION RESET
#
#
#     TOOL RESULT != NORMAL BY DEFAULT
#
#
#     DLP SYSTEM != AGENT 11 DOMAIN CONTRACT
#
#
#     DLP VENDOR VOCABULARY
#         !=
#     AGENT 11 CLASSIFICATION VOCABULARY
#
#
#     CLASSIFICATION TECHNOLOGY MAY CHANGE
#
#
#     CLASSIFICATION SEMANTICS SHOULD SURVIVE
#
#
#     CLASSIFICATION != CLASSIFICATION PROVENANCE
#
#
#     CLASSIFICATION != CLASSIFICATION EVIDENCE
#
#
#     SOURCE != COMPLETE PROVENANCE
#
#
#     AUDITABLE != EVERYTHING IN ONE OBJECT
#
#
#     REFERENCE EVIDENCE
#
#
#     DO NOT DUPLICATE EVIDENCE
#
#
#     SENSITIVITY != CUSTOMER BOUNDARY
#
#
#     SENSITIVITY != REGULATORY DOMAIN
#
#
#     SENSITIVITY != RESIDENCY
#
#
#     SENSITIVITY != COMPARTMENT
#
#
#     SENSITIVITY != HANDLING REQUIREMENT
#
#
#     CLASSIFICATION DIMENSIONS SHOULD REMAIN SEMANTICALLY DISTINCT
#
#
#     CLASSIFICATION != RESIDENCY
#
#
#     RESIDENCY != SENSITIVITY
#
#
#     POLICY MAY CONSUME BOTH
#
#
#     ORGANIZATIONAL POLICY != CLASSIFICATION DEFINITION
#
#
#     CONCEPTUAL TRAPDOOR != REQUIRED IMPLEMENTATION
#
#
#     FUTURE NOTE != TODO LIST
#
#
#     ADD THE DOMAIN THAT OWNS THE NEW FACT
#
#
#     OPERATIONAL EVIDENCE
#         +
#     CLEAR DOMAIN REQUIREMENT
#         =
#     JUSTIFIED ARCHITECTURAL EXPANSION
#
#
#     REQUEST INTERRUPTION != SECURITY FAILURE
#
#
#     MANUAL REVIEW != SYSTEM FAILURE
#
#
#     CONSERVATIVE CLASSIFICATION BEHAVIOR != BROKEN SYSTEM
#
#
#     FRAMEWORKS CHANGE
#
#
#     DOMAIN CONTRACTS SHOULD SURVIVE THEM
#
#
#     WHICH THING OWNS WHICH FACT?
# ==========================================================================
# END PART II
# ==========================================================================
