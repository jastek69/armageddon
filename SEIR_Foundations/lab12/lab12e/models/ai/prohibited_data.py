# ============================================================================
# PART I — PROHIBITED DATA FINDING
# ============================================================================
#
# PURPOSE
# -------
# This section defines the domain contract used by Agent 11 to represent
# a prohibited-data finding.
#
# The fundamental question answered by this model is:
#
#       "WHAT PROHIBITED-DATA FINDING EXISTS?"
#
#
# A ProhibitedData object records that some security, privacy, compliance,
# or content-safety mechanism identified data requiring special handling.
#
# It does NOT determine what Agent 11 should do about the finding.
#
#
# ============================================================================
# ARCHITECTURAL BOUNDARY
# ============================================================================
#
# Prohibited-data detection is related to data classification, but the two
# controls answer different questions.
#
#
#                       DATA
#                        |
#             +----------+----------+
#             |                     |
#             v                     v
#       CLASSIFICATION        PROHIBITED-DATA
#       "How sensitive?"      "What special finding?"
#             |                     |
#             +----------+----------+
#                        |
#                        v
#                     POLICY
#                        |
#                        v
#                     ROUTING
#
#
# Classification describes the sensitivity of data.
#
# ProhibitedData describes a security, privacy, compliance, or content-safety
# finding associated with the data.
#
# Policy determines what those facts mean for a particular processing
# environment.
#
# Routing selects among destinations that remain authorized and viable.
#
#
#       CLASSIFICATION DESCRIBES SENSITIVITY.
#
#       PROHIBITED DATA DESCRIBES A FINDING.
#
#       POLICY DETERMINES AUTHORIZATION.
#
#       ROUTING SELECTS A VIABLE AUTHORIZED DESTINATION.
#
#
# ============================================================================
# CORE INVARIANTS
# ============================================================================
#
#       SENSITIVE != PROHIBITED
#
#       PROHIBITED FINDING != DATA CLASSIFICATION
#
#       PROHIBITED FINDING != POLICY DECISION
#
#       PROHIBITED FINDING != ROUTING DECISION
#
#       PROHIBITED FINDING != USER INTENT
#
#       PROHIBITED FINDING != ENFORCEMENT ACTION
#
#       DETECTION != AUTHORIZATION
#
#
# An E9 document, for example, may still be permitted for processing by an
# approved company on-premises reasoning service.
#
# Conversely, a private key may require special handling regardless of the
# classification assigned to the surrounding document.
#
#
#       E9 != PROHIBITED DATA
#
#       PRIVATE KEY != E9
#
#
# Agent 11 should preserve these facts independently and allow later policy
# components to determine their combined security meaning.
#
#
# ============================================================================
# CRITICAL DATA-HANDLING RULE
# ============================================================================
#
# The detected sensitive or prohibited value MUST NOT be copied into this
# model.
#
# Do NOT add fields such as:
#
#       value: str
#       detected_value: str
#       detected_text: str
#       matched_content: str
#       original_content: str
#       secret: str
#       payload: str
#
#
# A prohibited-data finding may eventually pass through:
#
#       - Pydantic serialization
#       - application logs
#       - telemetry
#       - distributed tracing
#       - audit systems
#       - exception handling
#       - message queues
#       - agent state
#       - agent-to-agent communication
#       - MCP messages
#       - SIEM systems
#
#
# Copying the protected value into the finding could therefore reproduce
# exactly the information the security control was intended to protect.
#
#
#       DETECT THE SENSITIVE DATA.
#
#       DESCRIBE THE FINDING.
#
#       DO NOT COPY THE SENSITIVE DATA INTO THE FINDING.
#
#
# This applies whether the finding concerns:
#
#       credentials
#       authentication tokens
#       private keys
#       personally identifiable information
#       payment-card information
#       prohibited content
#       or other organization-restricted information
#
#
#       FINDING METADATA != PROTECTED PAYLOAD
#
#
# ============================================================================
# ONE FINDING = ONE DOMAIN OBJECT
# ============================================================================
#
# A single piece of data may produce multiple prohibited-data findings.
#
# Example:
#
#       customer document
#             |
#             +--> PERSONALLY_IDENTIFIABLE_INFORMATION
#             |
#             +--> PAYMENT_CARD
#             |
#             +--> CREDENTIAL
#
#
# Agent 11 should represent these as separate ProhibitedData objects:
#
#       [
#           ProhibitedData(...PII...),
#           ProhibitedData(...PAYMENT_CARD...),
#           ProhibitedData(...CREDENTIAL...),
#       ]
#
#
# rather than collapsing them into:
#
#       prohibited = True
#
#
# Each finding may eventually require different:
#
#       evidence
#       provenance
#       review
#       policy
#       escalation
#       audit
#       or compliance handling
#
#
# Therefore:
#
#       ONE FINDING = ONE DOMAIN OBJECT
#
#       MULTIPLE FINDINGS != ONE GENERIC "BAD DATA" FLAG
#
#
# ============================================================================
# OBJECT EXISTENCE MEANS A FINDING EXISTS
# ============================================================================
#
# ProhibitedData deliberately does not contain:
#
#       detected: bool
#
#
# The existence of a ProhibitedData object already means that a finding
# exists.
#
# This would therefore be redundant:
#
#       ProhibitedData(
#           detected=True,
#           category=...,
#           source=...,
#       )
#
#
# And this would be contradictory:
#
#       ProhibitedData(
#           detected=False,
#           category=PRIVATE_KEY,
#           source=AUTOMATIC_DETECTOR,
#       )
#
#
# Instead:
#
#       OBJECT EXISTS = FINDING EXISTS
#
#       NO FINDING = NO OBJECT
#
#
# If prohibited-data processing produces no findings, represent that with
# an empty collection:
#
#       findings = []
#
#
# ============================================================================
# UNKNOWN != NO FINDING
# ============================================================================
#
# UNKNOWN is a legitimate security observation.
#
# A finding with:
#
#       category = UNKNOWN
#
# means:
#
#       "A prohibited-data condition was identified, but the specific
#        category could not be established."
#
#
# It does NOT mean:
#
#       "No prohibited data was detected."
#
#
# Therefore:
#
#       [] != [ProhibitedData(category=UNKNOWN, ...)]
#
#
# The first means:
#
#       NO FINDING EXISTS
#
#
# The second means:
#
#       A FINDING EXISTS,
#       BUT ITS CATEGORY IS UNRESOLVED
#
#
# This follows the same semantic discipline used elsewhere in Agent 11:
#
#
#       CLASSIFICATION:
#           UNKNOWN != NORMAL
#
#       POLICY:
#           INDETERMINATE != DENY
#
#       NETWORK:
#           UNKNOWN != UNAVAILABLE
#
#       PROHIBITED DATA:
#           UNKNOWN != NO FINDING
#
#
# Conservative security behavior must not require Agent 11 to falsify
# what it actually knows.
#
#
#       CONSERVATIVE BEHAVIOR != FALSE OBSERVATION
#
#
# ============================================================================
# FINDING != USER INTENT
# ============================================================================
#
# A prohibited-data finding describes content.
#
# It does not establish why the content exists or why a person submitted it.
#
# For example, content concerning:
#
#       sex trafficking
#       prostitution
#       pornography
#       animal cruelty
#       active threats
#
# may legitimately appear in:
#
#       security investigations
#       legal investigations
#       compliance reviews
#       incident response
#       trust-and-safety operations
#       research
#
#
# Therefore:
#
#       CONTENT FINDING != USER INTENT
#
#       DISCUSSION != PARTICIPATION
#
#       INVESTIGATION != ENDORSEMENT
#
#       DETECTION != GUILT
#
#
# User intent, if Agent 11 eventually needs to reason about it, belongs in
# a different domain contract.
#
#
# ============================================================================
# FINDING != ENFORCEMENT
# ============================================================================
#
# ProhibitedData does not determine whether Agent 11 should:
#
#       allow
#       deny
#       block
#       quarantine
#       review
#       escalate
#       retain
#       report
#       route
#       invoke a model
#
#
# Those are consequential behaviors.
#
# They belong to policy, safety, compliance, or other orchestrators.
#
#
#       ProhibitedData
#             |
#             v
#       POLICY / SAFETY
#        EVALUATION
#             |
#       +-----+-----+----------+
#       |           |          |
#       v           v          v
#     BLOCK       REVIEW    ESCALATE
#
#
# Other explicitly authorized processing may also exist depending on
# organizational policy.
#
#
#       FINDING DESCRIBES.
#
#       POLICY DECIDES.
#
#
# ============================================================================
# IMPORTS
# ============================================================================

from pydantic import Field

from ..base_model import Agent11BaseModel
from ..enums.policy_enums import (
    ProhibitedDataCategory,
    ProhibitedDataSource,
)


# ============================================================================
# ProhibitedData
# ============================================================================

class ProhibitedData(Agent11BaseModel):
    """
    Describes a prohibited-data finding associated with data processed
    by Agent 11.

    ProhibitedData records the finding.

    It does not contain the detected sensitive value, perform prohibited-
    data detection, determine data classification, evaluate policy,
    authorize AI destinations, select routes, invoke AI services, or
    perform enforcement actions.

    A ProhibitedData object means that a finding exists.

    Absence of prohibited-data findings should be represented by the
    absence of ProhibitedData objects rather than by a boolean field.
    """

    category: ProhibitedDataCategory = Field(
        description=(
            "Category of prohibited or specially controlled data "
            "identified by Agent 11 security processing."
        ),
    )

    source: ProhibitedDataSource = Field(
        description=(
            "Source from which the prohibited-data finding "
            "was established."
        ),
    )


# ============================================================================
# MODEL DESIGN NOTES
# ============================================================================
#
# ProhibitedData intentionally contains exactly two fields:
#
#       category
#       source
#
#
# This is not an incomplete model.
#
# It is a deliberately narrow domain contract.
#
#
# ============================================================================
# WHY THERE IS NO RAW VALUE
# ============================================================================
#
# The model records WHAT CATEGORY was detected.
#
# It deliberately does not preserve the detected content itself.
#
# Appropriate:
#
#       category = PRIVATE_KEY
#
#
# Not appropriate:
#
#       value = "-----BEGIN PRIVATE KEY----- ..."
#
#
# Appropriate:
#
#       category = AUTHENTICATION_TOKEN
#
#
# Not appropriate:
#
#       token = "<actual authentication token>"
#
#
# Appropriate:
#
#       category = PERSONALLY_IDENTIFIABLE_INFORMATION
#
#
# Not appropriate:
#
#       detected_text = "<person's private information>"
#
#
# The finding should remain safe to serialize without intentionally
# reproducing the protected payload.
#
#
#       FINDING METADATA != PROTECTED PAYLOAD
#
#
# ============================================================================
# WHY THERE IS NO `detected: bool`
# ============================================================================
#
# The object itself represents the finding.
#
#
#       ProhibitedData(...)
#
# means:
#
#       A FINDING EXISTS
#
#
# Therefore a boolean would duplicate state and make contradictory states
# possible.
#
#
#       OBJECT EXISTS = FINDING EXISTS
#
#       NO FINDING = NO OBJECT
#
#
# ============================================================================
# WHY THERE IS NO POLICY RESULT
# ============================================================================
#
# Do not add:
#
#       blocked: bool
#       allowed: bool
#       external_allowed: bool
#       cloud_allowed: bool
#       onprem_allowed: bool
#       requires_escalation: bool
#
#
# Those fields would collapse detection into enforcement.
#
#
# Instead:
#
#       ProhibitedData
#             |
#             v
#          POLICY
#             |
#             v
#       PolicyDecision
#
#
# or, for future content-safety workflows:
#
#
#       ProhibitedData
#             |
#             v
#       SAFETY / COMPLIANCE
#          EVALUATION
#             |
#             v
#       CONTROLLED ACTION
#
#
# The same finding may legitimately produce different outcomes depending
# on:
#
#       organization policy
#       processing purpose
#       routing domain
#       deployment
#       jurisdiction
#       regulatory obligations
#       contractual obligations
#       future governance requirements
#
#
# The finding must therefore remain independent from those decisions.
#
#
#       FINDING != POLICY
#
#       FINDING != ENFORCEMENT
#
#
# ============================================================================
# WHY THERE IS NO CONFIDENCE FIELD
# ============================================================================
#
# Some future detectors may produce probabilistic confidence.
#
# Example:
#
#       AUTOMATIC CLASSIFIER
#           |
#           v
#       PII probability = 0.91
#
#
# Other sources may be deterministic or authoritative.
#
# Example:
#
#       ORGANIZATION_METADATA
#           |
#           v
#       explicitly marked restricted
#
#
# A probability may have no useful meaning in the second case.
#
# Confidence therefore does not belong on every ProhibitedData object.
#
#
# If operational evidence demonstrates a need for confidence, a future
# neighboring contract may represent:
#
#       finding
#       confidence
#       evidence
#       detector identity
#       detector version
#       review requirement
#
#
# without changing the fundamental meaning of ProhibitedData.
#
#
#       USED DURING DETECTION != OWNED BY ProhibitedData
#
#       CONFIDENCE != FINDING
#
#
# ============================================================================
# WHY THERE IS NO SEVERITY FIELD
# ============================================================================
#
# Severity is intentionally absent from the SEIR-I contract.
#
# Different organizations, jurisdictions, and workflows may assign
# different operational severity to the same category.
#
# Severity may also depend on context that ProhibitedData does not own.
#
# For example:
#
#       finding category
#       +
#       processing context
#       +
#       quantity
#       +
#       destination
#       +
#       organizational policy
#       +
#       legal requirements
#       =
#       operational severity
#
#
# Therefore:
#
#       CATEGORY != SEVERITY
#
#
# If SEIR-I operational evidence demonstrates that severity needs its own
# domain representation, SEIR-II can introduce an appropriate neighboring
# contract.
#
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================
# WHY THERE IS NO REQUEST ID
# ============================================================================
#
# ProhibitedData does not own an AI request.
#
# A prohibited-data finding may eventually be associated with:
#
#       an AI request
#       a context item
#       a document
#       an MCP tool result
#       an uploaded artifact
#       an agent message
#       generated output
#       persisted context
#
#
# Adding:
#
#       request_id
#
# would unnecessarily define this noun as:
#
#       "a prohibited-data finding belonging specifically to AIRequest"
#
#
# Instead, the surrounding workflow should establish the relationship
# between a finding and the object being inspected.
#
#
#       DOMAIN OBJECT != WORKFLOW OWNERSHIP
#
#
# ============================================================================
# WHY THERE IS NO LOCATION FIELD
# ============================================================================
#
# A future detector may need to identify where a finding occurred.
#
# Examples:
#
#       context.customer
#       document.page_17
#       tool_result.record_4
#
#
# That information may eventually belong to evidence or provenance.
#
# It does not need to be embedded in the foundational finding contract
# merely because a future system might use it.
#
#
#       POSSIBLE FUTURE REQUIREMENT
#           !=
#       REQUIRED CURRENT FIELD
#
#
# ============================================================================
# WHY THERE IS NO CUSTOM VALIDATOR
# ============================================================================
#
# There is currently no cross-field semantic invariant requiring one.
#
# `category` and `source` are independent observations.
#
#
# This can be legitimate:
#
#       category = PERSONALLY_IDENTIFIABLE_INFORMATION
#       source   = UNKNOWN
#
#
# Agent 11 knows WHAT was identified but lacks information about where
# the classification assertion originated.
#
#
# This can also be legitimate:
#
#       category = UNKNOWN
#       source   = ORGANIZATION_METADATA
#
#
# Agent 11 knows WHERE the finding originated but cannot resolve the
# finding to a more specific category.
#
#
# Do not invent a validator requiring:
#
#       UNKNOWN category -> UNKNOWN source
#
# or:
#
#       UNKNOWN source -> UNKNOWN category
#
#
# Those would create a relationship that does not actually exist in the
# domain.
#
#
# Pydantic makes validators easy to write.
#
# That does not mean every model should have one.
#
#
#       VALIDATION SHOULD REPRESENT
#       A REAL DOMAIN INVARIANT.
#
#       VALIDATION SHOULD NOT INVENT ONE.
#
#       VALIDATION SHOULD NOT BE DECORATION.
#
#
# ============================================================================
# WHAT THIS MODEL DOES NOT KNOW
# ============================================================================
#
# ProhibitedData intentionally does not know:
#
#       request_id
#       user_id
#       service_id
#       model_id
#       deployment_id
#       routing_domain
#       cloud provider
#       region
#       endpoint
#       network path
#       BGP state
#       SD-WAN state
#       service health
#       latency
#       token cost
#       routing score
#       selected destination
#       AI response
#
#
# It also does not currently know:
#
#       confidence
#       evidence
#       exact detected value
#       detector version
#       policy version
#       severity
#       reviewer
#       approval state
#       escalation state
#       legal disposition
#
#
# Those facts may matter elsewhere.
#
# They are not therefore automatically fields of ProhibitedData.
#
#
# When deciding whether a field belongs here, ask:
#
#
#       "WHICH THING OWNS THIS FACT?"
#
#
# ============================================================================
# PART I CONTRACT
# ============================================================================
#
# ProhibitedData answers:
#
#
#       "WHAT PROHIBITED-DATA FINDING EXISTS?"
#
#
# It does not answer:
#
#
#       "HOW WAS THE CONTENT DETECTED?"
#           -> detection behavior
#
#
#       "HOW CERTAIN ARE WE?"
#           -> future assessment / evidence
#
#
#       "HOW SENSITIVE IS THE DATA?"
#           -> DataClassification
#
#
#       "MAY THIS DATA GO THERE?"
#           -> policy
#
#
#       "WHICH DESTINATION SHOULD WE USE?"
#           -> routing
#
#
#       "SHOULD A HUMAN REVIEW THIS?"
#           -> future safety / compliance behavior
#
#
#       "SHOULD THIS BE ESCALATED?"
#           -> future safety / threat workflow
#
#
#       "WHAT ACTION MAY THE AGENT PERFORM?"
#           -> execution authorization
#
#
# The model therefore remains:
#
#
#       TWO FIELDS
#
#       ZERO CUSTOM VALIDATORS
#
#       ZERO RAW PROTECTED VALUES
#
#       ZERO POLICY LOGIC
#
#       ZERO ROUTING LOGIC
#
#       ZERO ENFORCEMENT LOGIC
#
#
# Small responsibility.
#
# Small domain contract.
#
#
# ============================================================================
# END PART I
# ============================================================================

# ============================================================================
# PART II — PROHIBITED-DATA SEMANTICS
# ============================================================================
#
# PURPOSE
# -------
# Part I defined the ProhibitedData domain object.
#
# Part II defines the architectural meaning of a prohibited-data finding.
#
# This section is intentionally documentation-only.
#
# It adds:
#
#       NO runtime behavior
#       NO Pydantic fields
#       NO validators
#       NO detector implementation
#       NO policy implementation
#       NO routing logic
#       NO enforcement actions
#
#
# The permanent question answered by this section is:
#
#
#       "WHAT DOES A PROHIBITED-DATA FINDING MEAN?"
#
#
# Part I answers:
#
#       WHAT FINDING EXISTS?
#
#
# Part II answers:
#
#       WHAT MUST THAT FINDING MEAN
#       THROUGHOUT THE AGENT 11 ARCHITECTURE?
#
#
# ============================================================================
# 1. THE PERMANENT SECURITY PIPELINE
# ============================================================================
#
# Prohibited-data detection is one stage in a larger security pipeline.
#
#
#                       DATA
#                        |
#             +----------+----------+
#             |                     |
#             v                     v
#       CLASSIFICATION        PROHIBITED-DATA
#       "How sensitive?"      "What finding exists?"
#             |                     |
#             +----------+----------+
#                        |
#                        v
#               POLICY / SAFETY
#                  EVALUATION
#                        |
#                        v
#               CONTROLLED DECISION
#                        |
#             +----------+----------+
#             |                     |
#             v                     v
#          ROUTING              OTHER SAFETY /
#                               COMPLIANCE FLOW
#
#
# These stages must remain separate.
#
#
#       CLASSIFICATION DESCRIBES SENSITIVITY.
#
#       PROHIBITED-DATA DETECTION DESCRIBES FINDINGS.
#
#       POLICY DETERMINES AUTHORIZATION.
#
#       SAFETY / COMPLIANCE DETERMINES SPECIAL HANDLING.
#
#       ROUTING SELECTS AMONG AUTHORIZED VIABLE DESTINATIONS.
#
#
# No stage should quietly absorb the responsibilities of all the others.
#
#
# ============================================================================
# 2. A FINDING IS AN OBSERVATION
# ============================================================================
#
# ProhibitedData records an observation produced by security processing.
#
# For example:
#
#
#       category = PRIVATE_KEY
#
#
# means:
#
#       "Security processing identified a private-key finding."
#
#
# It does NOT inherently mean:
#
#
#       delete the request
#       block every possible workflow
#       report the user
#       terminate the session
#       send the event to law enforcement
#       allow the data on-premises
#       deny the data externally
#       quarantine the data
#       escalate to a human
#
#
# Those are possible consequences.
#
# They are not the meaning of the finding itself.
#
#
#       FINDING = OBSERVATION
#
#       FINDING != CONSEQUENCE
#
#
# ============================================================================
# 3. FINDING != ENFORCEMENT ACTION
# ============================================================================
#
# The architecture must preserve a boundary between:
#
#
#       WHAT WAS FOUND?
#
# and:
#
#       WHAT SHOULD WE DO ABOUT IT?
#
#
# Conceptually:
#
#
#       DATA
#        |
#        v
#   DETECTOR
#        |
#        v
#   ProhibitedData
#        |
#        v
#   POLICY / SAFETY / COMPLIANCE
#        |
#        +----------------+----------------+----------------+
#        |                |                |                |
#        v                v                v                v
#      ALLOW            BLOCK            REVIEW          ESCALATE
#   under explicit
#      authority
#
#
# Future workflows may add additional controlled outcomes.
#
# That does not change the meaning of ProhibitedData.
#
#
#       FINDING != BLOCK
#
#       FINDING != REVIEW
#
#       FINDING != ESCALATION
#
#       FINDING != ALLOW
#
#
# The finding remains descriptive.
#
# Consequential behavior belongs elsewhere.
#
#
# ============================================================================
# 4. "PROHIBITED" DOES NOT MEAN "DELETE EVERYTHING"
# ============================================================================
#
# The name ProhibitedData indicates that the finding requires special
# security handling.
#
# It must NOT be interpreted as:
#
#
#       IF FINDING:
#           DELETE EVERYTHING
#
#
# Some findings may need to be preserved and processed by an approved
# security, privacy, compliance, legal, or safety workflow.
#
#
# Consider:
#
#       ACTIVE_THREAT
#
#
# An architecture that immediately destroys all information about the
# finding could interfere with an organization's legitimate threat-response
# responsibilities.
#
#
# Likewise, a privacy incident may require:
#
#       evidence preservation
#       incident analysis
#       compliance review
#       controlled remediation
#
#
# Therefore:
#
#
#       PROHIBITED FINDING
#               |
#               v
#       SPECIAL HANDLING REQUIRED
#
#
# not:
#
#
#       PROHIBITED FINDING
#               |
#               v
#       DESTROY ALL INFORMATION
#
#
#       PROHIBITED FINDING != DISCARD THE EVIDENCE
#
#
# ============================================================================
# 5. INFORMATION PROTECTION AND CONTENT SAFETY
# ============================================================================
#
# Agent 11 intentionally uses ProhibitedData for findings from more than
# one security family.
#
#
#                   PROHIBITED-DATA FINDINGS
#                            |
#              +-------------+-------------+
#              |                           |
#              v                           v
#      INFORMATION PROTECTION        CONTENT SAFETY
#
#
# Examples:
#
#
# INFORMATION PROTECTION
# ----------------------
#
#       CREDENTIAL
#       AUTHENTICATION_TOKEN
#       PRIVATE_KEY
#       PERSONAL_IDENTIFIER
#       PERSONALLY_IDENTIFIABLE_INFORMATION
#       PAYMENT_CARD
#
#
# CONTENT SAFETY
# --------------
#
#       CHILD_SEXUAL_ABUSE_MATERIAL
#       SEX_TRAFFICKING
#       PROSTITUTION
#       COMMERCIAL_SEXUAL_CONTENT
#       PORNOGRAPHIC_CONTENT
#       ANIMAL_CRUELTY
#       ACTIVE_THREAT
#
#
# These findings share a common contract because they all indicate that
# normal AI processing may require additional security handling.
#
# They do NOT necessarily share:
#
#
#       the same detector
#       the same policy
#       the same severity
#       the same legal meaning
#       the same compliance requirement
#       the same review process
#       the same escalation process
#       the same retention requirement
#
#
# Therefore:
#
#
#       INFORMATION PROTECTION != CONTENT SAFETY
#
#
# and:
#
#
#       SHARED DOMAIN CONTRACT
#           !=
#       IDENTICAL SECURITY SEMANTICS
#
#
# ============================================================================
# 6. SENSITIVE != PROHIBITED
# ============================================================================
#
# Data classification and prohibited-data findings remain separate axes.
#
#
#       DataClassification
#             |
#             +--> NORMAL
#             +--> E7
#             +--> E8
#             +--> E9
#             +--> UNKNOWN
#
#
#       ProhibitedData
#             |
#             +--> PII
#             +--> PRIVATE_KEY
#             +--> ACTIVE_THREAT
#             +--> ...
#
#
# A highly classified document may still be authorized for processing
# inside an approved environment.
#
# A credential may require special handling even when it appears inside
# otherwise ordinary data.
#
#
#       E9 != PROHIBITED DATA
#
#       PROHIBITED DATA != E9
#
#       SENSITIVE != PROHIBITED
#
#
# Classification and prohibited-data findings may both become inputs to
# later policy evaluation.
#
#
# ============================================================================
# 7. MULTIPLE SECURITY FACTS MAY COEXIST
# ============================================================================
#
# Real enterprise data can produce several findings simultaneously.
#
#
# Example:
#
#
#       CUSTOMER RECORD
#             |
#             +--> classification = E8
#             |
#             +--> PII
#             |
#             +--> PAYMENT_CARD
#
#
# Another example:
#
#
#       SECURITY INCIDENT
#             |
#             +--> classification = E9
#             |
#             +--> ACTIVE_THREAT
#             |
#             +--> PII
#             |
#             +--> ORGANIZATION_RESTRICTED
#
#
# Another:
#
#
#       TRAFFICKING INVESTIGATION
#             |
#             +--> SEX_TRAFFICKING
#             |
#             +--> PROSTITUTION
#             |
#             +--> PII
#
#
# Agent 11 must preserve these independently.
#
#
#       ONE FINDING DOES NOT ERASE ANOTHER FINDING
#
#       ONE SECURITY DIMENSION DOES NOT ERASE ANOTHER DIMENSION
#
#
# Do not collapse the entire security state into:
#
#
#       prohibited = True
#
#
# That destroys information the later policy and compliance systems may
# require.
#
#
# ============================================================================
# 8. ONE FINDING = ONE DOMAIN OBJECT
# ============================================================================
#
# Each prohibited-data finding should remain independently representable.
#
#
# Prefer:
#
#
#       [
#           ProhibitedData(category=PII, ...),
#           ProhibitedData(category=PAYMENT_CARD, ...),
#           ProhibitedData(category=CREDENTIAL, ...),
#       ]
#
#
# rather than a single generic object representing:
#
#
#       "some bad stuff was found"
#
#
# Future systems may need to associate different:
#
#
#       evidence
#       provenance
#       confidence
#       review
#       policy
#       severity
#       disposition
#
#
# with individual findings.
#
#
#       ONE FINDING = ONE DOMAIN OBJECT
#
#
# ============================================================================
# 9. FINDING != USER INTENT
# ============================================================================
#
# This is a permanent security and governance boundary.
#
# Prohibited-data detection describes CONTENT.
#
# It does not establish the motivation of the person who supplied that
# content.
#
#
# Legitimate enterprise workloads may contain material discussing:
#
#
#       prostitution
#       sex trafficking
#       pornography
#       child sexual abuse material
#       animal cruelty
#       threats
#       credentials
#       privacy incidents
#
#
# because the workload itself may involve:
#
#
#       security analysis
#       incident response
#       compliance
#       legal investigation
#       trust and safety
#       abuse investigation
#       academic research
#       threat intelligence
#
#
# Therefore:
#
#
#       CONTENT FINDING != USER INTENT
#
#       DISCUSSION != PARTICIPATION
#
#       INVESTIGATION != ENDORSEMENT
#
#       DETECTION != GUILT
#
#
# A security system must not transform a content observation into an
# unsupported assertion about a human being.
#
#
# ============================================================================
# 10. SEXUAL AND EXPLOITATION CATEGORIES REMAIN DISTINCT
# ============================================================================
#
# Agent 11 deliberately preserves multiple sexual/exploitation categories.
#
#
#       CHILD_SEXUAL_ABUSE_MATERIAL
#
#       SEX_TRAFFICKING
#
#       PROSTITUTION
#
#       COMMERCIAL_SEXUAL_CONTENT
#
#       PORNOGRAPHIC_CONTENT
#
#
# These categories are not synonyms.
#
#
#       SEX_TRAFFICKING != PROSTITUTION
#
#       PROSTITUTION != PORNOGRAPHIC_CONTENT
#
#       PORNOGRAPHIC_CONTENT != COMMERCIAL_SEXUAL_CONTENT
#
#       CSAM != PORNOGRAPHIC_CONTENT
#
#
# A particular item or investigation may produce more than one finding.
#
# Agent 11 should preserve those findings rather than force them into one
# generalized category.
#
#
# ============================================================================
# 11. CSAM IS A DISTINCT HIGH-CONSEQUENCE FINDING
# ============================================================================
#
# CHILD_SEXUAL_ABUSE_MATERIAL is deliberately distinct from adult
# pornographic content.
#
# It must not be reduced to:
#
#
#       "another pornography category"
#
#
# Therefore:
#
#
#       CSAM != PORNOGRAPHIC_CONTENT
#
#
# The detector must also preserve the distinction between:
#
#
#       MATERIAL
#
# and:
#
#       DISCUSSION ABOUT THE MATERIAL
#
#
# Examples such as:
#
#
#       "The detector identified suspected CSAM."
#
#       "The investigation concerns CSAM."
#
#       "Our policy prohibits CSAM."
#
#
# discuss the category.
#
# Those statements are not themselves the prohibited material.
#
#
# Therefore:
#
#
#       DISCUSSION OF CSAM != CSAM
#
#       REPORT ABOUT CSAM != CSAM
#
#       INVESTIGATION OF CSAM != CSAM
#
#
# This distinction is essential for:
#
#
#       security teams
#       compliance teams
#       legal teams
#       trust-and-safety teams
#       investigators
#
#
# A future detector should distinguish between discussion ABOUT a category
# and detection OF the underlying material as accurately as reasonably
# possible.
#
#
# ============================================================================
# 12. DO NOT REPRODUCE THE DETECTED MATERIAL
# ============================================================================
#
# This is one of the strongest invariants in the entire module.
#
#
#       DETECT THE MATERIAL.
#
#       RECORD THE CATEGORY.
#
#       DO NOT COPY THE MATERIAL.
#
#
# ProhibitedData must not intentionally contain:
#
#
#       passwords
#       authentication tokens
#       private keys
#       payment-card values
#       raw PII
#       prohibited imagery
#       prohibited text
#       other protected payloads
#
#
# Why?
#
# Because the finding may eventually be serialized into:
#
#
#       application logs
#       telemetry
#       traces
#       audit systems
#       exception messages
#       queues
#       agent state
#       MCP traffic
#       SIEM events
#       debugging output
#
#
# A detector that discovers protected data and then reproduces that data
# throughout the observability environment has created a second security
# problem.
#
#
#       SECURITY DETECTION
#           MUST NOT BECOME
#       SECURITY EXFILTRATION
#
#
#       FINDING METADATA != DETECTED PAYLOAD
#
#
# ============================================================================
# 13. PII IS CONSERVATIVE BY DESIGN IN SEIR-I
# ============================================================================
#
# SEIR-I intentionally treats PII conservatively.
#
# Privacy failures can create:
#
#
#       confidentiality loss
#       compliance exposure
#       regulatory exposure
#       contractual exposure
#       financial penalties
#       customer harm
#       loss of trust
#
#
# The cost of a false positive and the cost of a false negative are
# therefore not necessarily symmetrical.
#
#
#       FALSE POSITIVE
#             |
#             v
#       legitimate request may be
#       delayed, blocked, or reviewed
#
#
#       FALSE NEGATIVE
#             |
#             v
#       protected personal information
#       may leave its authorized boundary
#
#
# Therefore:
#
#
#       FALSE POSITIVE COST
#           !=
#       FALSE NEGATIVE COST
#
#
# For SEIR-I, the architecture deliberately biases toward protecting the
# data when uncertainty has meaningful privacy consequences.
#
#
# ============================================================================
# 14. PII IS MORE THAN SIMPLE IDENTIFIERS
# ============================================================================
#
# A naive detector might search only for:
#
#
#       Social Security numbers
#       passport numbers
#       driver's-license numbers
#       account numbers
#
#
# Those are useful signals.
#
# They are not the complete definition of personal information.
#
#
# Personal information may also exist as narrative or contextual history.
#
# Examples may include:
#
#
#       medical history
#       employment history
#       family relationships
#       financial circumstances
#       location history
#       personal correspondence
#       behavioral history
#
#
# Therefore:
#
#
#       NO SSN DETECTED != NO PII
#
#       NO PASSPORT NUMBER != NO PII
#
#       NO SIMPLE IDENTIFIER != NO PERSONAL INFORMATION
#
#
# A long personal history may be highly privacy-sensitive even if it does
# not conveniently contain one value matching a regular expression.
#
#
# ============================================================================
# 15. UNCERTAIN PII != NO PII
# ============================================================================
#
# Suppose a future detector concludes:
#
#
#       PII likelihood = high
#
#
# but cannot establish complete certainty.
#
# Agent 11 must not silently transform uncertainty into:
#
#
#       NO PII
#
#
# merely because certainty is incomplete.
#
#
#       UNCERTAIN PII != NO PII
#
#
# Depending on policy, uncertain PII may require:
#
#
#       conservative blocking
#       human confirmation
#       privacy review
#       additional detection
#
#
# Those behaviors belong outside ProhibitedData.
#
#
# ============================================================================
# 16. CONSERVATIVE BEHAVIOR != FALSE OBSERVATION
# ============================================================================
#
# Agent 11 repeatedly separates:
#
#
#       WHAT DO WE KNOW?
#
# from:
#
#       HOW SHOULD WE BEHAVE GIVEN WHAT WE KNOW?
#
#
# If the exact prohibited-data category remains unresolved:
#
#
#       category = UNKNOWN
#
#
# may accurately represent the observation.
#
# Security policy may nevertheless behave conservatively.
#
#
#       OBSERVATION
#           |
#           v
#       UNKNOWN
#           |
#           v
#       POLICY / SAFETY
#           |
#           v
#       CONSERVATIVE ACTION
#
#
# Do not rewrite:
#
#
#       UNKNOWN
#
# as:
#
#       DEFINITELY SAFE
#
#
# merely to make downstream code easier.
#
#
# Likewise, do not rewrite:
#
#
#       UNKNOWN
#
# as:
#
#       DEFINITELY PRIVATE KEY
#
#
# if that is not what the detector established.
#
#
# Preserve the observation.
#
# Apply conservative behavior separately.
#
#
#       CONSERVATIVE BEHAVIOR != FALSE OBSERVATION
#
#
# This is consistent with Agent 11's broader semantics:
#
#
#       UNKNOWN CLASSIFICATION != NORMAL
#
#       INDETERMINATE POLICY != DENY
#
#       UNKNOWN NETWORK STATE != UNAVAILABLE
#
#       UNKNOWN PROHIBITED CATEGORY != NO FINDING
#
#
# ============================================================================
# 17. ACTIVE THREAT != THREAT LANGUAGE
# ============================================================================
#
# Text containing threatening language does not automatically establish an
# active threat.
#
#
# Example:
#
#
#       "The villain threatened the mayor."
#
#
# is materially different from a specific statement expressing immediate
# intent to harm a real target.
#
#
# Therefore:
#
#
#       THREAT LANGUAGE != ACTIVE THREAT
#
#
# A future threat-assessment system may consider:
#
#
#       context
#       immediacy
#       specificity
#       target
#       expressed intent
#       capability indicators
#
#
# Those assessment mechanics do not belong in ProhibitedData.
#
#
#       THREAT ASSESSMENT != ProhibitedData
#
#
# ProhibitedData records the resulting finding after the appropriate
# security mechanism has made that determination.
#
#
# ============================================================================
# 18. UNCERTAIN HIGH-CONSEQUENCE FINDING != NO FINDING
# ============================================================================
#
# The conservative principle extends beyond privacy.
#
# A high-consequence detector may encounter evidence that requires further
# review without possessing complete certainty.
#
#
# The architecture must not use:
#
#
#       NOT 100% CERTAIN
#
#
# as equivalent to:
#
#
#       NOTHING FOUND
#
#
# Therefore:
#
#
#       UNCERTAIN HIGH-CONSEQUENCE FINDING
#           !=
#       NO FINDING
#
#
# Future assessment and review contracts may represent this distinction
# more precisely.
#
# SEIR-I should preserve the conceptual boundary now.
#
#
# ============================================================================
# 19. ANIMAL DEATH != ANIMAL CRUELTY
# ============================================================================
#
# ANIMAL_CRUELTY is intentionally narrower than:
#
#
#       ANIMAL DEATH
#
# or:
#
#       KILLING_ANIMALS
#
#
# Legitimate contexts may involve:
#
#
#       veterinary euthanasia
#       agriculture
#       food production
#       pest control
#       wildlife management
#       hunting regulation
#       scientific or legal discussion
#
#
# The mere presence of animal death does not establish cruelty.
#
#
#       ANIMAL DEATH != ANIMAL CRUELTY
#
#
# Context belongs to detection.
#
# The resulting finding belongs to ProhibitedData.
#
#
# ============================================================================
# 20. PLATFORM != CONTENT CATEGORY
# ============================================================================
#
# Agent 11 should avoid turning individual commercial platform names into
# permanent security ontology.
#
#
# A platform name does not inherently mean:
#
#
#       COMMERCIAL_SEXUAL_CONTENT
#
# or:
#
#       PORNOGRAPHIC_CONTENT
#
#
# A particular organization may choose to prohibit or restrict a platform.
#
# That restriction belongs in:
#
#
#       organization configuration
#       policy
#       filtering
#       future source controls
#
#
# rather than permanently encoding the vendor into the domain vocabulary.
#
#
#       PLATFORM != CONTENT
#
#       SOURCE != CATEGORY
#
#       VENDOR NAME != PERMANENT DOMAIN ONTOLOGY
#
#
# ============================================================================
# 21. SOURCE DESCRIBES ORIGIN, NOT TRUTH
# ============================================================================
#
# ProhibitedDataSource answers:
#
#
#       "WHERE DID THIS FINDING ASSERTION COME FROM?"
#
#
# It does not answer:
#
#
#       "IS THE FINDING DEFINITELY CORRECT?"
#
#
# Possible sources may include:
#
#
#       USER_DECLARED
#       APPLICATION_DECLARED
#       ORGANIZATION_METADATA
#       AUTOMATIC_DETECTOR
#       UNKNOWN
#
#
# These describe origin.
#
# They do not inherently describe:
#
#
#       confidence
#       evidence
#       authority
#       approval
#       correctness
#       severity
#
#
# Therefore:
#
#
#       SOURCE != CONFIDENCE
#
#       SOURCE != EVIDENCE
#
#       SOURCE != AUTHORITY
#
#       SOURCE != APPROVAL
#
#       SOURCE != CORRECTNESS
#
#
# ============================================================================
# 22. AUTOMATIC DETECTION != AUTOMATIC AUTHORITY
# ============================================================================
#
# A future automatic detector may identify:
#
#
#       PII
#       PRIVATE_KEY
#       ACTIVE_THREAT
#       SEX_TRAFFICKING
#
#
# That does not mean the detector owns the final security decision.
#
#
#       AUTOMATIC DETECTION != AUTOMATIC AUTHORITY
#
#
# Depending on category, certainty, organizational policy, and consequence,
# future workflows may require:
#
#
#       automatic handling
#       human review
#       security review
#       privacy review
#       compliance review
#       legal review
#       safety escalation
#
#
# The detector produces evidence or findings.
#
# The appropriate authority determines consequential action.
#
#
# ============================================================================
# 23. CONFIDENCE != FINDING
# ============================================================================
#
# Some detectors may be probabilistic.
#
# Others may be deterministic.
#
# Others may consume authoritative organizational metadata.
#
#
# Example:
#
#
#       ML / LLM CLASSIFIER
#              |
#              v
#       confidence may be meaningful
#
#
#       ORGANIZATION METADATA
#              |
#              v
#       probability may be meaningless
#
#
# Therefore:
#
#
#       CONFIDENCE != FINDING
#
#
# ProhibitedData intentionally does not contain a universal confidence
# field.
#
# If future operational evidence demonstrates that confidence must become
# a first-class domain concept, a neighboring assessment contract can own
# that fact.
#
#
# ============================================================================
# 24. FINDING != EVIDENCE
# ============================================================================
#
# A finding states:
#
#
#       WHAT CATEGORY WAS IDENTIFIED?
#
#
# Evidence answers:
#
#
#       WHY DID THE SYSTEM REACH THAT CONCLUSION?
#
#
# These are not the same thing.
#
#
#       FINDING != EVIDENCE
#
#
# Future evidence might include safe metadata such as:
#
#
#       detector identity
#       detector version
#       rule identifier
#       classification technique
#       safe location reference
#       timestamp
#
#
# Evidence design must continue to respect the rule:
#
#
#       DO NOT REPRODUCE THE PROTECTED PAYLOAD
#
#
# Auditability does not require copying the dangerous or sensitive content
# into every audit artifact.
#
#
# ============================================================================
# 25. FINDING != PROVENANCE
# ============================================================================
#
# ProhibitedDataSource is intentionally coarse.
#
# It may tell Agent 11:
#
#
#       AUTOMATIC_DETECTOR
#
#
# It does not necessarily tell Agent 11:
#
#
#       which detector
#       which version
#       which rule
#       which model
#       which policy bundle
#       which processing stage
#
#
# Those are provenance questions.
#
#
#       SOURCE != COMPLETE PROVENANCE
#
#
# Future provenance requirements should be represented separately rather
# than forcing all audit history into ProhibitedData.
#
#
# ============================================================================
# 26. FINDING != SEVERITY
# ============================================================================
#
# Category and severity must remain conceptually distinct.
#
#
#       CATEGORY
#           "What kind of finding is this?"
#
#
#       SEVERITY
#           "How consequential is this finding in this context?"
#
#
# Operational severity may eventually depend on:
#
#
#       category
#       quantity
#       processing purpose
#       user context
#       destination
#       jurisdiction
#       organizational policy
#       legal requirements
#       repeated behavior
#       other findings
#
#
# Therefore:
#
#
#       CATEGORY != SEVERITY
#
#
# Do not turn ProhibitedDataCategory into an implicit severity ladder.
#
#
# ============================================================================
# 27. POLICY REMAINS THE AUTHORIZATION BOUNDARY
# ============================================================================
#
# ProhibitedData does not answer:
#
#
#       "MAY THIS DATA BE SENT TO THIS AI DESTINATION?"
#
#
# That remains a policy question.
#
#
#       ProhibitedData
#             |
#             v
#          POLICY
#             |
#             v
#       PolicyDecision
#
#
# Example organization policy might eventually say:
#
#
#       PII + EXTERNAL_FM
#           -> DENY
#
#
#       PII + APPROVED COMPANY CLOUD DEPLOYMENT
#           -> ALLOW under explicit conditions
#
#
#       PII + COMPANY_ONPREM_LLM
#           -> ALLOW under explicit conditions
#
#
# Another organization may establish:
#
#
#       PII + ANY AI PROCESSING
#           -> DENY
#
#
# The finding remains:
#
#
#       PII
#
#
# Organizational policy determines the authorization.
#
#
#       FINDING != POLICY
#
#       ORGANIZATIONAL POLICY != DOMAIN VOCABULARY
#
#
# ============================================================================
# 28. ABSENCE OF AUTHORIZATION != AUTHORIZATION
# ============================================================================
#
# High-risk processing must not depend on an assumption such as:
#
#
#       "Nobody explicitly said no."
#
#
# Agent 11's security model requires authorization to be established where
# policy requires it.
#
#
#       ABSENCE OF DENIAL
#           !=
#       ESTABLISHED AUTHORIZATION
#
#
# This matters particularly for:
#
#
#       PII
#       credentials
#       authentication tokens
#       private keys
#       payment-card data
#       high-consequence content-safety findings
#
#
# If authorization cannot be established:
#
#
#       FAIL CLOSED
#
#
# But preserve the actual reason and observed state.
#
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ============================================================================
# 29. A POLICY-DENIED FINDING DOES NOT DEFINE EVERY WORKFLOW
# ============================================================================
#
# A category prohibited from normal AI inference may still require handling
# by another approved organizational workflow.
#
#
# Example:
#
#
#       ACTIVE_THREAT
#             |
#             +--> normal external AI processing denied
#             |
#             +--> approved threat-response workflow
#
#
# Or:
#
#
#       EXPOSED PRIVATE KEY
#             |
#             +--> normal AI reasoning denied
#             |
#             +--> credential-rotation workflow
#
#
# Therefore:
#
#
#       DENIED FOR ONE PROCESSING PURPOSE
#           !=
#       FORBIDDEN FROM EVERY SECURITY WORKFLOW
#
#
# Processing purpose becomes increasingly important as Agent 11 evolves.
#
#
# ============================================================================
# 30. PROHIBITED DATA != DANGEROUS ACTION
# ============================================================================
#
# ProhibitedData governs observations about DATA.
#
# Execution authorization governs ACTIONS.
#
#
# Example:
#
#
#       "Here is a private key."
#               |
#               v
#       PROHIBITED-DATA HANDLING
#
#
#       "Delete the production database."
#               |
#               v
#       EXECUTION AUTHORIZATION
#
#
# These are different security domains.
#
#
#       DANGEROUS ACTION != PROHIBITED DATA
#
#
# Do not add categories such as:
#
#
#       DELETE_DATABASE
#       DROP_TABLE
#       TERMINATE_INSTANCE
#       TRANSFER_FUNDS
#
#
# to ProhibitedDataCategory.
#
# Those describe actions.
#
# They belong to future execution/tool authorization controls.
#
#
# ============================================================================
# 31. PROHIBITED DATA != PROMPT INJECTION
# ============================================================================
#
# Prompt injection is also a distinct AI-security problem.
#
# A prompt-injection attempt may be embedded inside data.
#
# That does not make prompt injection equivalent to:
#
#
#       PII
#       PRIVATE_KEY
#       PAYMENT_CARD
#       ACTIVE_THREAT
#
#
# Therefore:
#
#
#       PROMPT INJECTION != DATA CLASSIFICATION
#
#       PROMPT INJECTION != PROHIBITED-DATA CATEGORY
#
#
# Future Agent 11 input-security controls should model prompt injection
# separately.
#
#
# Otherwise ProhibitedDataCategory eventually becomes:
#
#
#       "EVERY SECURITY PROBLEM AGENT 11 HAS EVER HEARD OF"
#
#
# which would destroy the domain boundary.
#
#
# ============================================================================
# 32. AI MAY NEED A SECRET REFERENCE, NOT THE SECRET
# ============================================================================
#
# Agent 11 may eventually direct tools that require credentials.
#
# The reasoning model does not necessarily need to possess those
# credentials.
#
#
# Preferred conceptual architecture:
#
#
#       AI REASONING
#            |
#            v
#       "Use approved credential reference X"
#            |
#            v
#       EXECUTION LAYER
#            |
#            v
#       SECRET MANAGER
#            |
#            v
#       TARGET SERVICE
#
#
# The reasoning system may know:
#
#
#       a credential exists
#       an approved reference exists
#       the execution layer may use it
#
#
# without receiving:
#
#
#       the password
#       the token
#       the private key
#
#
# Therefore:
#
#
#       AI MAY NEED THE REFERENCE.
#
#       AI MAY NOT NEED THE SECRET.
#
#
# This reduces unnecessary exposure through:
#
#
#       model context
#       provider APIs
#       traces
#       logs
#       agent state
#       MCP messages
#       debugging
#
#
# ============================================================================
# 33. PROHIBITED-DATA HANDLING EXTENDS BEYOND MODEL INPUT
# ============================================================================
#
# Prohibited data may appear at several points in an agentic workflow.
#
#
#       USER INPUT
#           |
#           v
#       AI REQUEST
#           |
#           v
#       MODEL OUTPUT
#           |
#           v
#       MCP / TOOL RESULT
#           |
#           v
#       AGENT MESSAGE
#           |
#           v
#       GENERATED ARTIFACT
#
#
# A future architecture must not assume:
#
#
#       "We checked the original prompt,
#        therefore the rest of the workflow is safe."
#
#
# Protected or prohibited data may be:
#
#
#       introduced
#       retrieved
#       inferred
#       generated
#       transformed
#       returned by tools
#
#
# after initial request inspection.
#
#
# Therefore:
#
#
#       INPUT INSPECTION != COMPLETE LIFECYCLE PROTECTION
#
#
# Part III will preserve the future expansion of this requirement.
#
#
# ============================================================================
# 34. AI-GENERATED DATA != SAFE DATA
# ============================================================================
#
# AI-generated output does not receive an automatic exemption from
# prohibited-data controls.
#
#
# A model may:
#
#
#       reproduce PII from context
#       expose credentials from retrieved data
#       generate sensitive derived information
#       reproduce prohibited material from supplied context
#
#
# Therefore:
#
#
#       AI-GENERATED != SAFE
#
#       AI-GENERATED != PUBLIC
#
#       AI-GENERATED != UNRESTRICTED
#
#
# Output inspection may eventually be required.
#
#
# ============================================================================
# 35. TRANSFORMATION != SANITIZATION
# ============================================================================
#
# Transforming data does not automatically remove prohibited-data concerns.
#
#
# Examples:
#
#
#       summarization
#       translation
#       extraction
#       reformatting
#       compression
#       paraphrasing
#
#
# do not inherently prove that protected information has been removed.
#
#
#       TRANSFORMATION != SANITIZATION
#
#
# Likewise:
#
#
#       REDACTION ATTEMPT != VERIFIED SAFE OUTPUT
#
#
# A future sanitization or de-identification workflow should have explicit
# semantics rather than assuming that any transformation lowered risk.
#
#
# ============================================================================
# 36. MCP TOOL RESULTS ARE NOT TRUSTED BY DEFAULT
# ============================================================================
#
# Future MCP tools may return:
#
#
#       customer records
#       logs
#       documents
#       credentials
#       database rows
#       threat intelligence
#       external content
#
#
# The fact that data came from an approved tool does not mean that every
# value returned by that tool is appropriate for unrestricted AI
# processing.
#
#
#       APPROVED TOOL != UNRESTRICTED TOOL OUTPUT
#
#
#       TOOL RESULT != SAFE BY DEFAULT
#
#
# Prohibited-data inspection may eventually need to occur at tool
# boundaries as well as initial request boundaries.
#
#
# ============================================================================
# 37. AGENT HANDOFF != SECURITY RESET
# ============================================================================
#
# Future Agent 11 workflows may involve multiple agents.
#
# A prohibited-data finding must not disappear merely because data moved
# from:
#
#
#       Agent A
#
# to:
#
#       Agent B
#
#
# Conceptually:
#
#
#       DATA + SECURITY CONTEXT
#               |
#               v
#            AGENT A
#               |
#               v
#       DATA + SECURITY CONTEXT
#               |
#               v
#            AGENT B
#
#
# not:
#
#
#       DATA + SECURITY CONTEXT
#               |
#               v
#            AGENT A
#               |
#               v
#          SECURITY RESET
#               |
#               v
#            AGENT B
#
#
# Therefore:
#
#
#       AGENT HANDOFF != SECURITY RESET
#
#
# Part III will preserve this as a SEIR-II expansion problem.
#
#
# ============================================================================
# 38. REQUEST INTERRUPTION MAY REPRESENT SUCCESSFUL SECURITY
# ============================================================================
#
# Suppose Agent 11 detects PII and organizational policy requires human
# review before AI processing.
#
# The user does not immediately receive an AI response.
#
# That does not mean Agent 11 failed.
#
#
#       REQUEST INTERRUPTED
#               !=
#       SECURITY CONTROL FAILED
#
#
# Likewise:
#
#
#       CREDENTIAL BLOCKED
#
#       PII HELD FOR REVIEW
#
#       ACTIVE THREAT ESCALATED
#
#
# may represent successful security outcomes.
#
#
# Availability metrics alone cannot determine whether the security system
# behaved correctly.
#
#
# ============================================================================
# 39. SECURITY TELEMETRY MUST PRESERVE WHY PROCESSING STOPPED
# ============================================================================
#
# Future telemetry should distinguish:
#
#
#       model failure
#
#       routing failure
#
#       network failure
#
#       policy denial
#
#       prohibited-data control
#
#       manual review
#
#       safety escalation
#
#
# Otherwise dashboards may incorrectly report successful security
# enforcement as ordinary technical failure.
#
#
#       SECURITY ENFORCEMENT != SYSTEM MALFUNCTION
#
#
# The telemetry layer records what happened.
#
# It does not redefine the security semantics.
#
#
# ============================================================================
# 40. PROHIBITED-DATA DETECTION MUST NOT BECOME A ROUTING SCORE
# ============================================================================
#
# Agent 11 must not eventually implement logic such as:
#
#
#       PII = -20 points
#
#       PRIVATE_KEY = -50 points
#
#       cheap model = +30 points
#
#       low latency = +15 points
#
#       total score > threshold -> route
#
#
# That would allow economic or performance preferences to compensate for
# security constraints.
#
#
# Security policy must be evaluated before optimization.
#
#
#       POLICY PERMITTED
#              |
#              v
#       CAPABILITY SUITABLE
#              |
#              v
#       SERVICE AVAILABLE
#              |
#              v
#       NETWORK AVAILABLE
#              |
#              v
#       VIABLE DESTINATIONS
#              |
#              v
#       OPTIMIZE AMONG SURVIVORS
#
#
# Therefore:
#
#
#       SECURITY FINDING != ROUTING SCORE
#
#       POLICY NEVER BECOMES A SCORE
#
#       CHEAPER != PERMITTED
#
#       FASTER != PERMITTED
#
#
# ============================================================================
# 41. FALLBACK MUST NOT ESCAPE PROHIBITED-DATA POLICY
# ============================================================================
#
# Suppose the preferred AI service becomes unavailable.
#
# Agent 11 may attempt fallback.
#
# Fallback must re-evaluate the remaining destination against the same
# security requirements.
#
#
#       PRIMARY SERVICE FAILS
#               |
#               v
#       NEXT CANDIDATE
#               |
#               v
#       RE-EVALUATE SECURITY / POLICY
#               |
#          +----+----+
#          |         |
#          v         v
#       PERMITTED   DENIED
#          |         |
#          v         v
#       CONTINUE   REJECT
#
#
# Never:
#
#
#       "The approved service is down,
#        so send grandma's private history to anything that answers."
#
#
# Therefore:
#
#
#       FALLBACK != POLICY ESCAPE
#
#       AVAILABILITY FAILURE != SECURITY EXCEPTION
#
#
# ============================================================================
# 42. FAIL CLOSED WITHOUT DESTROYING SEMANTIC PRECISION
# ============================================================================
#
# When required authorization cannot be established, Agent 11 should fail
# closed.
#
# But fail closed is a behavior.
#
# It must not collapse all underlying states into the same observation.
#
#
# Examples:
#
#
#       explicit policy DENY
#
#       policy INDETERMINATE
#
#       prohibited-data category UNKNOWN
#
#       service unavailable
#
#       network unavailable
#
#
# may all prevent processing.
#
# They are not the same fact.
#
#
#       FAIL CLOSED
#           !=
#       ERASE WHY WE FAILED CLOSED
#
#
# Accurate state is essential for:
#
#
#       audit
#       compliance
#       incident response
#       troubleshooting
#       future policy improvement
#
#
# ============================================================================
# 43. CHEWBACCA'S PROHIBITED-DATA REVIEW
# ============================================================================
#
# Security Engineer:
#
#       "Chewbacca, the detector found PII."
#
# Chewbacca:
#
#       "Then we know there is a PII finding."
#
#
# Security Engineer:
#
#       "So external AI is blocked?"
#
# Chewbacca:
#
#       "Ask policy."
#
#
# ---------------------------------------------------------------------------
#
# Security Engineer:
#
#       "The detector found a private key."
#
# Chewbacca:
#
#       "Record PRIVATE_KEY."
#
#
# Security Engineer:
#
#       "Should I put the key itself into the audit event?"
#
# Chewbacca:
#
#       "No."
#
#
# Security Engineer:
#
#       "But Audit wants evidence."
#
# Chewbacca:
#
#       "Give Audit safe evidence that a private key was detected.
#        Do not give the logging system another copy of the private key."
#
#
# ---------------------------------------------------------------------------
#
# Security Engineer:
#
#       "The detector thinks this may contain PII."
#
# Chewbacca:
#
#       "How certain?"
#
#
# Security Engineer:
#
#       "Not certain enough for me to risk releasing it."
#
# Chewbacca:
#
#       "Then uncertainty is not permission to call it public."
#
#
# ---------------------------------------------------------------------------
#
# Security Engineer:
#
#       "A security report discusses sex trafficking."
#
# Chewbacca:
#
#       "Discussion is not participation."
#
#
# ---------------------------------------------------------------------------
#
# Security Engineer:
#
#       "A compliance report contains the term CSAM."
#
# Chewbacca:
#
#       "Discussion of the category is not detection of the material."
#
#
# ---------------------------------------------------------------------------
#
# Security Engineer:
#
#       "The user asked the agent to delete production."
#
# Chewbacca:
#
#       "That is not prohibited data.
#        Go talk to execution authorization."
#
#
# ---------------------------------------------------------------------------
#
# Security Engineer:
#
#       "Our approved MCP tool returned customer PII."
#
# Chewbacca:
#
#       "Approved tool does not mean unrestricted output."
#
#
# ---------------------------------------------------------------------------
#
# Security Engineer:
#
#       "The primary private model is down.
#        Can I fall back to an external model?"
#
# Chewbacca:
#
#       "Only if the data is authorized there."
#
#
# Security Engineer:
#
#       "But the external model is cheaper."
#
# Chewbacca:
#
#       "That was not the question."
#
#
# ============================================================================
# 44. FINAL PART II INVARIANTS
# ============================================================================
#
# Preserve these rules as Agent 11 evolves.
#
#
# ---------------------------------------------------------------------------
# FINDING BOUNDARY
# ---------------------------------------------------------------------------
#
#       FINDING = OBSERVATION
#
#       FINDING != CONSEQUENCE
#
#       FINDING != ENFORCEMENT ACTION
#
#       FINDING != POLICY DECISION
#
#       FINDING != ROUTING DECISION
#
#       FINDING != USER INTENT
#
#
# ---------------------------------------------------------------------------
# CLASSIFICATION BOUNDARY
# ---------------------------------------------------------------------------
#
#       SENSITIVE != PROHIBITED
#
#       PROHIBITED FINDING != DATA CLASSIFICATION
#
#       E9 != PROHIBITED DATA
#
#
# ---------------------------------------------------------------------------
# CONTENT BOUNDARY
# ---------------------------------------------------------------------------
#
#       CONTENT FINDING != USER INTENT
#
#       DISCUSSION != PARTICIPATION
#
#       INVESTIGATION != ENDORSEMENT
#
#       DETECTION != GUILT
#
#
# ---------------------------------------------------------------------------
# SEXUAL / EXPLOITATION BOUNDARY
# ---------------------------------------------------------------------------
#
#       SEX_TRAFFICKING != PROSTITUTION
#
#       PROSTITUTION != PORNOGRAPHIC_CONTENT
#
#       PORNOGRAPHIC_CONTENT != COMMERCIAL_SEXUAL_CONTENT
#
#       CSAM != PORNOGRAPHIC_CONTENT
#
#       DISCUSSION OF CSAM != CSAM
#
#       REPORT ABOUT CSAM != CSAM
#
#       INVESTIGATION OF CSAM != CSAM
#
#
# ---------------------------------------------------------------------------
# PRIVACY BOUNDARY
# ---------------------------------------------------------------------------
#
#       UNCERTAIN PII != NO PII
#
#       NO SSN DETECTED != NO PII
#
#       NO SIMPLE IDENTIFIER != NO PERSONAL INFORMATION
#
#       FALSE POSITIVE COST != FALSE NEGATIVE COST
#
#
# ---------------------------------------------------------------------------
# OBSERVATION BOUNDARY
# ---------------------------------------------------------------------------
#
#       UNKNOWN != NO FINDING
#
#       CONSERVATIVE BEHAVIOR != FALSE OBSERVATION
#
#       FAIL CLOSED != FALSIFY STATE
#
#
# ---------------------------------------------------------------------------
# THREAT / SAFETY BOUNDARY
# ---------------------------------------------------------------------------
#
#       THREAT LANGUAGE != ACTIVE THREAT
#
#       UNCERTAIN HIGH-CONSEQUENCE FINDING != NO FINDING
#
#       ANIMAL DEATH != ANIMAL CRUELTY
#
#
# ---------------------------------------------------------------------------
# DATA-HANDLING BOUNDARY
# ---------------------------------------------------------------------------
#
#       FINDING METADATA != DETECTED PAYLOAD
#
#       DETECT THE SENSITIVE DATA.
#
#       DESCRIBE THE FINDING.
#
#       DO NOT COPY THE SENSITIVE DATA INTO THE FINDING.
#
#
# ---------------------------------------------------------------------------
# SOURCE / ASSESSMENT BOUNDARY
# ---------------------------------------------------------------------------
#
#       SOURCE != CONFIDENCE
#
#       SOURCE != EVIDENCE
#
#       SOURCE != AUTHORITY
#
#       SOURCE != APPROVAL
#
#       SOURCE != CORRECTNESS
#
#       SOURCE != COMPLETE PROVENANCE
#
#       AUTOMATIC DETECTION != AUTOMATIC AUTHORITY
#
#       CONFIDENCE != FINDING
#
#       FINDING != EVIDENCE
#
#       FINDING != PROVENANCE
#
#       CATEGORY != SEVERITY
#
#
# ---------------------------------------------------------------------------
# POLICY BOUNDARY
# ---------------------------------------------------------------------------
#
#       FINDING != POLICY
#
#       ABSENCE OF DENIAL != ESTABLISHED AUTHORIZATION
#
#       ABSENCE OF AUTHORIZATION != AUTHORIZATION
#
#       POLICY NEVER BECOMES A SCORE
#
#
# ---------------------------------------------------------------------------
# ROUTING / FALLBACK BOUNDARY
# ---------------------------------------------------------------------------
#
#       SECURITY FINDING != ROUTING SCORE
#
#       CHEAPER != PERMITTED
#
#       FASTER != PERMITTED
#
#       FALLBACK != POLICY ESCAPE
#
#       AVAILABILITY FAILURE != SECURITY EXCEPTION
#
#
# ---------------------------------------------------------------------------
# AI / TOOL BOUNDARY
# ---------------------------------------------------------------------------
#
#       PROHIBITED DATA != DANGEROUS ACTION
#
#       PROHIBITED DATA != PROMPT INJECTION
#
#       APPROVED TOOL != UNRESTRICTED TOOL OUTPUT
#
#       TOOL RESULT != SAFE BY DEFAULT
#
#       AI MAY NEED A SECRET REFERENCE.
#
#       AI MAY NOT NEED THE SECRET.
#
#
# ---------------------------------------------------------------------------
# LIFECYCLE BOUNDARY
# ---------------------------------------------------------------------------
#
#       INPUT INSPECTION != COMPLETE LIFECYCLE PROTECTION
#
#       AI-GENERATED != SAFE
#
#       AI-GENERATED != PUBLIC
#
#       TRANSFORMATION != SANITIZATION
#
#       AGENT HANDOFF != SECURITY RESET
#
#
# ---------------------------------------------------------------------------
# OPERATIONAL BOUNDARY
# ---------------------------------------------------------------------------
#
#       REQUEST INTERRUPTED != SECURITY CONTROL FAILED
#
#       SECURITY ENFORCEMENT != SYSTEM MALFUNCTION
#
#       FAIL CLOSED != ERASE WHY WE FAILED CLOSED
#
#
# ============================================================================
# PART II CONTRACT
# ============================================================================
#
# ProhibitedData remains a small descriptive noun.
#
# Part II does not make it responsible for:
#
#
#       detection algorithms
#       DLP
#       confidence
#       evidence
#       provenance
#       severity
#       policy
#       legal interpretation
#       compliance disposition
#       human review
#       escalation
#       routing
#       model invocation
#       tool authorization
#       execution authorization
#       incident response
#
#
# Those systems may CONSUME a ProhibitedData finding.
#
# They do not therefore belong INSIDE ProhibitedData.
#
#
#       CONSUMES THE FINDING
#           !=
#       OWNED BY THE FINDING
#
#
# This distinction allows the tiny Part I contract to survive while the
# surrounding Agent 11 security architecture becomes substantially more
# sophisticated.
#
#
# Part III preserves that future expansion.
#
#
# ============================================================================
# END PART II
# ============================================================================

# ============================================================================
# PART III — SEIR-II PROHIBITED-DATA / SAFETY / COMPLIANCE EXPANSION
# ============================================================================
#
# PURPOSE
# -------
# Parts I and II establish the SEIR-I prohibited-data contract.
#
# Part III preserves the architectural problems that future versions of
# Agent 11 are expected to encounter as the system expands into:
#
#       enterprise DLP
#       richer privacy controls
#       automated content-safety systems
#       human review
#       compliance workflows
#       legal workflows
#       threat response
#       multimodal AI
#       MCP
#       multi-agent systems
#       SIEM / SOAR
#       multi-cloud AI infrastructure
#
#
# This section is intentionally documentation-only.
#
# It adds:
#
#       NO runtime behavior
#       NO Pydantic fields
#       NO validators
#       NO detector implementation
#       NO policy implementation
#       NO vendor SDK dependencies
#       NO workflow implementation
#
#
# This is a letter from SEIR-I to SEIR-II.
#
#
#       PRESERVE THE FUTURE PROBLEM
#
#       WITHOUT PRETENDING
#       TO HAVE THE FUTURE SOLUTION.
#
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#
# ============================================================================
# 1. THE SEIR-I CONTRACT MUST SURVIVE SEIR-II
# ============================================================================
#
# The SEIR-I contract is intentionally small:
#
#
#       ProhibitedData
#           |
#           +--> category
#           |
#           +--> source
#
#
# SEIR-II will almost certainly require richer surrounding systems.
#
# That does not mean the foundational finding must become:
#
#
#       ProhibitedData(
#           category=...,
#           source=...,
#           confidence=...,
#           severity=...,
#           evidence=...,
#           detector=...,
#           detector_version=...,
#           jurisdiction=...,
#           policy=...,
#           reviewer=...,
#           escalation=...,
#           legal_status=...,
#           routing_domain=...,
#           cloud_provider=...,
#           region=...,
#           deployment=...,
#           ticket=...,
#           incident=...,
#           ...
#       )
#
#
# That would turn one domain noun into an entire security platform.
#
#
#       RICHER SYSTEM
#           !=
#       FATTER FOUNDATIONAL OBJECT
#
#
# Prefer neighboring contracts and orchestrators when operational evidence
# demonstrates that additional concepts deserve first-class representation.
#
#
# ============================================================================
# 2. SEIR-II SHOULD BE INFORMED BY SEIR-I EVIDENCE
# ============================================================================
#
# SEIR-II should not be designed only by imagining features.
#
# SEIR-I should produce operational evidence showing where the current
# architecture is insufficient.
#
#
# Questions worth measuring include:
#
#
#       How often are prohibited-data findings generated?
#
#       Which categories appear most often?
#
#       How frequently is category UNKNOWN?
#
#       Why does UNKNOWN occur?
#
#       Which sources produce the most findings?
#
#       Which detectors produce excessive false positives?
#
#       Which findings require manual review?
#
#       Which findings are overturned during review?
#
#       How often does PII appear in narrative rather than obvious
#       identifiers?
#
#       How often do multiple findings coexist?
#
#       How often do MCP tools introduce new prohibited data?
#
#       How often does model output introduce prohibited data?
#
#       How often does a finding interrupt routing?
#
#       How often does a finding trigger escalation?
#
#       Which audit questions cannot be answered with current telemetry?
#
#
# These observations should inform future contracts.
#
#
#       SEIR-I TELEMETRY
#              |
#              v
#       OPERATIONAL EVIDENCE
#              |
#              v
#       SEIR-II DOMAIN DESIGN
#
#
# not:
#
#
#       "THIS FIELD MIGHT BE USEFUL SOMEDAY"
#              |
#              v
#       ADD IT TO EVERYTHING
#
#
# ============================================================================
# 3. FUTURE DLP INTEGRATION
# ============================================================================
#
# Enterprise Agent 11 deployments may consume findings from Data Loss
# Prevention systems.
#
# Those systems may identify:
#
#
#       PII
#       financial data
#       credentials
#       regulated identifiers
#       organization-sensitive content
#       customer-specific information
#
#
# Future architecture may conceptually resemble:
#
#
#       DATA
#        |
#        v
#       DLP SYSTEM
#        |
#        v
#       DLP-SPECIFIC RESULT
#        |
#        v
#       AGENT 11 ADAPTER
#        |
#        v
#       AGENT 11 DOMAIN FINDING
#
#
# The adapter boundary matters.
#
#
#       DLP VENDOR VOCABULARY
#           !=
#       AGENT 11 DOMAIN VOCABULARY
#
#
# Do not allow:
#
#
#       vendor-specific detector types
#       vendor-specific rule names
#       vendor-specific confidence formats
#       vendor-specific SDK objects
#
#
# to become permanent dependencies of ProhibitedData.
#
#
#       DLP SYSTEM != AGENT 11 DOMAIN CONTRACT
#
#
# Vendor systems change.
#
# The Agent 11 security semantics should survive them.
#
#
# ============================================================================
# 4. FUTURE DETECTOR ADAPTERS
# ============================================================================
#
# Agent 11 may eventually consume findings from several detector types.
#
#
#       deterministic rules
#       regular expressions
#       DLP systems
#       machine-learning classifiers
#       LLM classifiers
#       organization metadata
#       document labels
#       application assertions
#       security services
#
#
# Conceptually:
#
#
#       DETECTOR A ----+
#                     |
#       DETECTOR B ----+
#                     |
#       DETECTOR C ----+----> NORMALIZATION ----> ProhibitedData
#                     |
#       DLP SYSTEM -----+
#                     |
#       METADATA -------+
#
#
# ProhibitedData should not need to understand each detector implementation.
#
#
#       DETECTOR IMPLEMENTATION != FINDING CONTRACT
#
#
# ============================================================================
# 5. FUTURE ASSESSMENT CONTRACT
# ============================================================================
#
# Operational evidence may show that Agent 11 needs to distinguish:
#
#
#       THE FINDING
#
# from:
#
#       THE ASSESSMENT THAT PRODUCED THE FINDING
#
#
# A future neighboring concept might represent:
#
#
#       ProhibitedDataAssessment
#
#
# Conceptually, it could eventually own facts such as:
#
#
#       finding
#       confidence
#       detector identity
#       detector version
#       assessment method
#       review recommendation
#
#
# This is NOT implemented in SEIR-I.
#
#
# The important architectural distinction is:
#
#
#       FINDING != ASSESSMENT
#
#
# A deterministic finding should not be forced to pretend it has a
# probabilistic confidence value merely because another detector does.
#
#
# ============================================================================
# 6. FUTURE EVIDENCE
# ============================================================================
#
# Audit, Security, Privacy, and Compliance may eventually ask:
#
#
#       "WHY DID AGENT 11 SAY THIS WAS PII?"
#
#
# That question requires evidence.
#
# Evidence is richer than:
#
#
#       category = PII
#
#
# Future safe evidence might include:
#
#
#       detector identifier
#       detector version
#       rule identifier
#       detection technique
#       safe location reference
#       timestamp
#       assessment identifier
#
#
# Evidence must be designed carefully.
#
# The obvious implementation:
#
#
#       evidence = detected_value
#
#
# may create exactly the security exposure the detector was intended
# to prevent.
#
#
#       AUDITABILITY != COPY THE PROTECTED DATA
#
#
#       EVIDENCE != PROTECTED PAYLOAD
#
#
# ============================================================================
# 7. FUTURE PROVENANCE
# ============================================================================
#
# Source is intentionally coarse.
#
# Provenance may eventually need to answer:
#
#
#       Which system produced the finding?
#
#       Which detector version?
#
#       Which rule?
#
#       Which model?
#
#       Which policy bundle?
#
#       Which processing stage?
#
#       Which Agent 11 instance?
#
#       Which workflow?
#
#
# Conceptually:
#
#
#       FINDING
#          |
#          v
#       PROVENANCE
#          |
#          +--> detector
#          +--> version
#          +--> rule
#          +--> timestamp
#          +--> processing stage
#
#
# Again:
#
#
#       SOURCE != COMPLETE PROVENANCE
#
#       FINDING != PROVENANCE
#
#
# ============================================================================
# 8. FUTURE HUMAN REVIEW
# ============================================================================
#
# Some findings may require human confirmation.
#
# This is particularly important when:
#
#
#       detector confidence is insufficient
#       consequences are high
#       legal interpretation is required
#       context is ambiguous
#       escalation is consequential
#
#
# Conceptually:
#
#
#       AUTOMATIC DETECTION
#              |
#              v
#          ASSESSMENT
#              |
#       +------+------+
#       |             |
#       v             v
#   SUFFICIENT     INSUFFICIENT
#   CERTAINTY       CERTAINTY
#       |             |
#       v             v
#    CONTINUE      HUMAN REVIEW
#
#
# Human review is a workflow.
#
# It is not a boolean inherent to every finding.
#
#
#       FINDING != REVIEW
#
#       FINDING != REVIEWER
#
#       FINDING != REVIEW DECISION
#
#
# ============================================================================
# 9. REVIEW MUST NOT BECOME A SECURITY BYPASS
# ============================================================================
#
# A future human-review mechanism needs explicit authority boundaries.
#
# The existence of a human reviewer must not imply:
#
#
#       HUMAN CLICKED "ALLOW"
#           =
#       ALL SECURITY POLICY DISAPPEARS
#
#
# Review authority may need to be scoped by:
#
#
#       category
#       organization
#       role
#       jurisdiction
#       processing purpose
#       destination
#
#
# Therefore:
#
#
#       HUMAN REVIEW != UNBOUNDED AUTHORITY
#
#       REVIEW APPROVAL != POLICY DELETION
#
#
# ============================================================================
# 10. FUTURE SEVERITY
# ============================================================================
#
# SEIR-II may discover that operational severity needs first-class
# representation.
#
# If so, severity should remain separate from category.
#
#
#       CATEGORY
#           "What was found?"
#
#
#       SEVERITY
#           "How consequential is this finding in this context?"
#
#
# Severity might depend on:
#
#
#       category
#       quantity
#       certainty
#       destination
#       processing purpose
#       user context
#       regulatory context
#       customer context
#       repeated events
#       other findings
#
#
# Therefore:
#
#
#       CATEGORY != SEVERITY
#
#
# Do not create a hidden severity hierarchy inside
# ProhibitedDataCategory.
#
#
# ============================================================================
# 11. FUTURE DISPOSITION
# ============================================================================
#
# Security and compliance systems may eventually need to record what
# happened to a finding.
#
#
# Possible conceptual outcomes might include:
#
#
#       blocked
#       reviewed
#       escalated
#       remediated
#       approved for restricted processing
#       false positive
#
#
# The exact vocabulary should be based on future operational requirements.
#
#
# A disposition describes what happened AFTER the finding.
#
#
#       FINDING != DISPOSITION
#
#
# Do not add disposition fields to ProhibitedData merely because future
# workflows may need them.
#
#
# ============================================================================
# 12. FUTURE PRIVACY WORKFLOW
# ============================================================================
#
# PII findings may eventually feed a dedicated privacy workflow.
#
#
#       PII FINDING
#            |
#            v
#       PRIVACY POLICY
#            |
#            +--> processing purpose
#            +--> destination
#            +--> jurisdiction
#            +--> customer requirements
#            +--> residency
#            |
#            v
#       PRIVACY DECISION
#
#
# Privacy processing may eventually consider concepts that do not belong
# to ProhibitedData itself.
#
#
#       FINDING != PRIVACY POLICY
#
#       PII != AUTOMATIC UNIVERSAL DENIAL
#
#
# SEIR-I intentionally begins conservatively.
#
# SEIR-II may introduce more precise approved-processing rules without
# weakening the foundational finding contract.
#
#
# ============================================================================
# 13. FUTURE JURISDICTION-AWARE HANDLING
# ============================================================================
#
# Enterprise AI processing may cross legal jurisdictions.
#
# Future policy may need to consider:
#
#
#       where the data originated
#       where the data subject resides
#       where processing occurs
#       where storage occurs
#       where the AI service operates
#       applicable contracts
#       applicable regulatory obligations
#
#
# These facts must not become new AIRoute values.
#
#
#       ROUTING DOMAIN != JURISDICTION
#
#       ROUTING DOMAIN != COUNTRY
#
#       ROUTING DOMAIN != REGION
#
#
# Likewise:
#
#
#       ProhibitedData != JURISDICTION DATABASE
#
#
# Jurisdiction should enter through neighboring policy/deployment/context
# contracts.
#
#
# ============================================================================
# 14. FUTURE DATA RESIDENCY
# ============================================================================
#
# PII and other protected information may eventually be subject to
# residency requirements.
#
#
#       FINDING
#          +
#       DATA RESIDENCY REQUIREMENT
#          +
#       DEPLOYMENT LOCATION
#          |
#          v
#       POLICY EVALUATION
#
#
# These are separate facts.
#
#
#       PII != RESIDENCY REQUIREMENT
#
#       RESIDENCY != CLASSIFICATION
#
#       RESIDENCY != ROUTING DOMAIN
#
#
# A finding should not need to know whether the eventual model is running
# in:
#
#
#       AWS
#       Azure
#       GCP
#       OCI
#       another cloud
#       company data center
#
#
# Deployment context owns deployment facts.
#
#
# ============================================================================
# 15. MULTI-CLOUD MUST NOT EXPLODE THE FINDING MODEL
# ============================================================================
#
# SEIR-II may operate proprietary or third-party AI services across:
#
#
#       AWS
#       Azure
#       GCP
#       OCI
#       other cloud providers
#       company-operated infrastructure
#
#
# The same prohibited-data finding should remain understandable regardless
# of where the reasoning service is deployed.
#
#
#       PII
#
# remains:
#
#       PII
#
#
# whether the potential destination is:
#
#
#       Azure-hosted proprietary model
#       GCP-hosted proprietary model
#       AWS-hosted model
#       OCI-hosted model
#       on-premises model
#
#
# Therefore:
#
#
#       FINDING != CLOUD PROVIDER
#
#       FINDING != DEPLOYMENT LOCATION
#
#       FINDING != ROUTING DOMAIN
#
#
# Multi-cloud complexity belongs to deployment, policy, network, and
# routing systems.
#
#
# ============================================================================
# 16. FUTURE MULTIMODAL DETECTION
# ============================================================================
#
# SEIR-I may begin primarily with textual processing.
#
# SEIR-II may need prohibited-data controls for:
#
#
#       text
#       images
#       audio
#       video
#       documents
#       structured records
#       archives
#       multimodal model input
#       multimodal model output
#
#
# Conceptually:
#
#
#                    DATA
#                     |
#       +-------------+-------------+
#       |             |             |
#       v             v             v
#      TEXT          IMAGE         AUDIO
#       |             |             |
#       +-------------+-------------+
#                     |
#                     v
#              DETECTION LAYER
#                     |
#                     v
#              ProhibitedData
#
#
# The finding contract should not require a different fundamental meaning
# merely because the detector inspected another modality.
#
#
#       MODALITY != FINDING CATEGORY
#
#
# Future evidence may need modality-specific details.
#
# Those details should not automatically become fields on ProhibitedData.
#
#
# ============================================================================
# 17. MULTIMODAL SYSTEMS MUST NOT COPY PROHIBITED MATERIAL INTO TELEMETRY
# ============================================================================
#
# The "do not copy the payload" rule becomes even more important with
# multimodal systems.
#
# A detector must not respond to prohibited imagery by placing:
#
#
#       image bytes
#       screenshots
#       thumbnails
#       extracted frames
#       encoded copies
#
#
# into ordinary Agent 11 telemetry merely to prove that detection occurred.
#
#
# Likewise, audio/video inspection must not casually reproduce prohibited
# content into logs or traces.
#
#
#       DETECTION != REPLICATION
#
#
# Safe evidence design becomes a dedicated SEIR-II concern.
#
#
# ============================================================================
# 18. FUTURE OUTPUT INSPECTION
# ============================================================================
#
# Prohibited-data protection must eventually consider AI output as well
# as AI input.
#
#
#       INPUT
#         |
#         v
#       MODEL
#         |
#         v
#       OUTPUT
#         |
#         v
#       OUTPUT INSPECTION
#
#
# A model might expose:
#
#
#       PII present in context
#       credentials retrieved from tools
#       restricted organization information
#       other prohibited content
#
#
# Therefore:
#
#
#       INPUT WAS SAFE
#           !=
#       OUTPUT IS SAFE
#
#
#       AI-GENERATED != SAFE
#
#
# ============================================================================
# 19. FUTURE DERIVED DATA
# ============================================================================
#
# A model may generate information derived from protected source data.
#
# The derived output may remain sensitive even if it does not reproduce
# the original text exactly.
#
#
#       PROTECTED INPUT
#              |
#              v
#           MODEL
#              |
#              v
#       DERIVED OUTPUT
#
#
# Future systems may need to determine whether prohibited-data or
# classification controls propagate into derived artifacts.
#
#
#       PARAPHRASE != AUTOMATIC SANITIZATION
#
#       SUMMARY != AUTOMATIC SANITIZATION
#
#       TRANSLATION != AUTOMATIC SANITIZATION
#
#
# ============================================================================
# 20. FUTURE SANITIZATION / REDACTION
# ============================================================================
#
# Agent 11 may eventually support controlled sanitization.
#
#
#       PROTECTED DATA
#            |
#            v
#       SANITIZATION
#            |
#            v
#       VERIFICATION
#            |
#            v
#       POLICY RE-EVALUATION
#
#
# The critical step is verification.
#
#
#       REDACTION ATTEMPT != VERIFIED SAFE DATA
#
#
#       SANITIZATION ATTEMPT != AUTHORIZED DECLASSIFICATION
#
#
# A future sanitizer should not be permitted to declare its own output
# safe merely because it performed a transformation.
#
#
# ============================================================================
# 21. FUTURE MCP INTEGRATION
# ============================================================================
#
# MCP dramatically expands the prohibited-data problem.
#
# Tool results may introduce data that was not present in the original
# AI request.
#
#
#       AI REQUEST
#            |
#            v
#       REASONING
#            |
#            v
#       MCP TOOL
#            |
#            v
#       TOOL RESULT
#            |
#            v
#       NEW DATA
#
#
# That new data may contain:
#
#
#       PII
#       credentials
#       payment information
#       restricted records
#       content-safety findings
#
#
# Therefore:
#
#
#       ORIGINAL REQUEST INSPECTED
#           !=
#       MCP RESULT SAFE
#
#
#       APPROVED MCP TOOL
#           !=
#       UNRESTRICTED MCP OUTPUT
#
#
# ============================================================================
# 22. MCP CREDENTIALS SHOULD REMAIN OUTSIDE REASONING CONTEXT
# ============================================================================
#
# An MCP tool may need credentials to perform its work.
#
# The reasoning model may not need those credentials.
#
#
# Preferred architecture:
#
#
#       AGENT 11
#          |
#          v
#       MCP REQUEST
#          |
#          v
#       AUTHORIZED MCP SERVICE
#          |
#          v
#       SECRET REFERENCE
#          |
#          v
#       SECRET MANAGER
#          |
#          v
#       TARGET SYSTEM
#
#
# Avoid:
#
#
#       SECRET MANAGER
#          |
#          v
#       RAW SECRET
#          |
#          v
#       LLM CONTEXT
#
#
# whenever the raw secret is unnecessary.
#
#
#       TOOL NEEDS CREDENTIAL
#           !=
#       MODEL NEEDS CREDENTIAL
#
#
# ============================================================================
# 23. FUTURE MULTI-AGENT PROPAGATION
# ============================================================================
#
# Agent 11 may eventually coordinate multiple specialized agents.
#
# Security findings must survive agent boundaries.
#
#
#       DATA
#        +
#       SECURITY CONTEXT
#            |
#            v
#         AGENT A
#            |
#            v
#       AGENT MESSAGE
#            |
#            v
#         AGENT B
#
#
# The handoff must not implicitly mean:
#
#
#       "Agent B starts from NORMAL because Agent A already looked at it."
#
#
# Therefore:
#
#
#       AGENT HANDOFF != SECURITY RESET
#
#
# Future state-management architecture may need to propagate:
#
#
#       classifications
#       prohibited-data findings
#       policy constraints
#       provenance
#
#
# without unnecessarily propagating the protected payload itself.
#
#
# ============================================================================
# 24. FUTURE AGENT MEMORY
# ============================================================================
#
# Persistent agent memory creates another prohibited-data boundary.
#
#
#       DATA
#        |
#        v
#       AGENT
#        |
#        v
#       MEMORY
#
#
# A request being authorized for temporary processing does not necessarily
# imply authorization for persistent storage.
#
#
#       AUTHORIZED FOR PROCESSING
#           !=
#       AUTHORIZED FOR MEMORY
#
#
# Future policy may separately govern:
#
#
#       inference
#       persistence
#       retrieval
#       sharing
#       retention
#       deletion
#
#
# ProhibitedData should remain the finding.
#
# Memory policy should remain policy.
#
#
# ============================================================================
# 25. FUTURE AGENT-TO-AGENT TRUST
# ============================================================================
#
# Multi-agent architectures may involve agents with different:
#
#
#       permissions
#       owners
#       models
#       deployments
#       tools
#       trust levels
#
#
# The fact that Agent A is authorized to process a finding does not prove
# that Agent B is authorized.
#
#
#       AGENT A AUTHORIZED
#           !=
#       AGENT B AUTHORIZED
#
#
# Security policy may need to be re-evaluated at agent boundaries.
#
#
# ============================================================================
# 26. FUTURE CONTENT-SAFETY TAXONOMY
# ============================================================================
#
# SEIR-I deliberately begins with a small explicit vocabulary.
#
# SEIR-II may discover operational need for additional categories or
# subcategories.
#
# Possible drivers include:
#
#
#       actual incident patterns
#       organization policy
#       customer requirements
#       legal requirements
#       trust-and-safety operations
#       detector capabilities
#
#
# Do not expand the enum merely because additional categories can be
# imagined.
#
#
#       CAN NAME A CATEGORY
#           !=
#       NEED A DOMAIN CATEGORY
#
#
# Expansion should be driven by actual control requirements.
#
#
# ============================================================================
# 27. CONTENT TAXONOMY MUST NOT BECOME MORAL ONTOLOGY
# ============================================================================
#
# Agent 11's content categories exist to support security, compliance,
# safety, and organizational policy.
#
# They should not attempt to encode a universal theory of morality.
#
#
# Prefer specific operational categories such as:
#
#
#       SEX_TRAFFICKING
#       PROSTITUTION
#       PORNOGRAPHIC_CONTENT
#       ANIMAL_CRUELTY
#       ACTIVE_THREAT
#
#
# over vague categories such as:
#
#
#       IMMORAL
#       VICE
#       BAD_CONTENT
#
#
# Why?
#
# Because specific categories can be:
#
#
#       detected
#       audited
#       governed
#       explained
#       mapped to policy
#
#
# with substantially greater precision.
#
#
#       SECURITY TAXONOMY != MORAL ONTOLOGY
#
#
# ============================================================================
# 28. FUTURE THREAT-ASSESSMENT WORKFLOW
# ============================================================================
#
# ACTIVE_THREAT may eventually feed a dedicated threat-assessment system.
#
#
#       THREAT SIGNAL
#            |
#            v
#       THREAT ASSESSMENT
#            |
#            +--> context
#            +--> immediacy
#            +--> specificity
#            +--> target
#            +--> capability indicators
#            +--> intent indicators
#            |
#            v
#       CONTROLLED RESPONSE
#
#
# The details of threat assessment must not be encoded into
# ProhibitedData.
#
#
#       ACTIVE_THREAT FINDING != THREAT-RESPONSE SYSTEM
#
#
# ============================================================================
# 29. FUTURE HIGH-CONSEQUENCE SAFETY WORKFLOWS
# ============================================================================
#
# Some categories may require specialized handling beyond ordinary AI
# policy.
#
# For example:
#
#
#       CHILD_SEXUAL_ABUSE_MATERIAL
#       ACTIVE_THREAT
#       SEX_TRAFFICKING
#
#
# may require carefully governed workflows.
#
# The exact workflow may depend on:
#
#
#       organization
#       jurisdiction
#       role
#       processing purpose
#       legal requirements
#       safety requirements
#
#
# Do not hard-code one universal legal or escalation procedure into
# ProhibitedData.
#
#
#       HIGH CONSEQUENCE
#           !=
#       UNIVERSAL WORKFLOW
#
#
# ============================================================================
# 30. FUTURE COMPLIANCE ORCHESTRATION
# ============================================================================
#
# Enterprise Agent 11 may eventually coordinate several control domains.
#
#
#                      ProhibitedData
#                            |
#                            v
#                 COMPLIANCE / SAFETY
#                    ORCHESTRATOR
#                            |
#          +-----------------+------------------+
#          |                 |                  |
#          v                 v                  v
#       PRIVACY          SECURITY          TRUST / SAFETY
#          |                 |                  |
#          +-----------------+------------------+
#                            |
#                            v
#                    CONTROLLED OUTCOME
#
#
# The orchestrator may coordinate systems.
#
# It should not redefine the finding.
#
#
# ============================================================================
# 31. FUTURE SIEM INTEGRATION
# ============================================================================
#
# Agent 11 findings may eventually generate SIEM telemetry.
#
#
#       ProhibitedData
#            |
#            v
#       SAFE SECURITY EVENT
#            |
#            v
#           SIEM
#
#
# The word SAFE matters.
#
# SIEM integration must not casually reproduce:
#
#
#       credentials
#       PII
#       payment data
#       prohibited content
#
#
# into another system.
#
#
# Prefer telemetry such as:
#
#
#       category
#       safe finding identifier
#       timestamp
#       safe source metadata
#       workflow outcome
#       policy result
#
#
# rather than the detected payload.
#
#
#       LOG THE FINDING.
#
#       DO NOT LOG THE SECRET.
#
#
# ============================================================================
# 32. FUTURE SOAR INTEGRATION
# ============================================================================
#
# Some findings may eventually trigger automated security workflows.
#
#
#       FINDING
#          |
#          v
#       POLICY / SAFETY DECISION
#          |
#          v
#       APPROVED AUTOMATION
#          |
#          v
#         SOAR
#
#
# Notice the ordering.
#
#
# Do not build:
#
#
#       FINDING
#          |
#          v
#       UNBOUNDED AUTOMATED ACTION
#
#
# Automated remediation must remain subject to scoped authority.
#
#
#       DETECTION != EXECUTION AUTHORITY
#
#
# ============================================================================
# 33. FUTURE INCIDENT MANAGEMENT
# ============================================================================
#
# Some findings may become security or privacy incidents.
#
# Others may not.
#
#
#       FINDING
#          !=
#       INCIDENT
#
#
# An incident may require:
#
#
#       correlation
#       scope
#       severity
#       affected systems
#       affected subjects
#       investigation
#       disposition
#
#
# Those concepts belong to incident-management architecture rather than
# ProhibitedData.
#
#
# ============================================================================
# 34. FUTURE CORRELATION
# ============================================================================
#
# Individual findings may become more significant when correlated.
#
#
# Example:
#
#
#       repeated credential findings
#             +
#       repeated external-routing attempts
#             +
#       unusual user behavior
#             |
#             v
#       SECURITY SIGNAL
#
#
# Correlation is behavior over multiple observations.
#
#
#       INDIVIDUAL FINDING != CORRELATED INCIDENT
#
#
# Do not place correlation logic inside the Pydantic finding.
#
#
# ============================================================================
# 35. FUTURE CUSTOMER-SPECIFIC CONTROLS
# ============================================================================
#
# Enterprise organizations may have customer-specific requirements.
#
#
#       CUSTOMER A DATA
#           -> external AI prohibited
#
#
#       CUSTOMER B DATA
#           -> approved private cloud permitted
#
#
#       CUSTOMER C DATA
#           -> on-premises only
#
#
# Those differences belong to policy.
#
#
#       CUSTOMER POLICY != ProhibitedDataCategory
#
#
# Do not create:
#
#
#       CUSTOMER_A_PII
#       CUSTOMER_B_PII
#       CUSTOMER_C_PII
#
#
# PII remains PII.
#
# Customer context remains customer context.
#
#
# ============================================================================
# 36. FUTURE REGULATORY AND CONTRACTUAL CONTROLS
# ============================================================================
#
# A prohibited-data finding may interact with:
#
#
#       regulatory requirements
#       contractual restrictions
#       organization policy
#       customer policy
#       residency requirements
#       sovereignty requirements
#
#
# These are independent policy dimensions.
#
#
# Avoid categories such as:
#
#
#       E8_US_ONLY_CUSTOMER_A_REGULATED_PII
#
#
# That would collapse multiple dimensions into one enum value.
#
#
# Prefer:
#
#
#       finding
#           +
#       classification
#           +
#       customer context
#           +
#       regulatory context
#           +
#       residency context
#           |
#           v
#       POLICY
#
#
# ============================================================================
# 37. FUTURE POLICY VERSIONING
# ============================================================================
#
# Audit and Compliance may eventually ask:
#
#
#       "WHICH POLICY CAUSED THIS FINDING TO BE BLOCKED?"
#
#
# The answer requires policy provenance.
#
# That does not mean ProhibitedData needs:
#
#
#       policy_version
#
#
# The finding existed independently of the policy evaluation.
#
#
#       FINDING != POLICY VERSION
#
#
# Policy decisions and telemetry should preserve the appropriate policy
# identity.
#
#
# ============================================================================
# 38. FUTURE EXPLAINABILITY
# ============================================================================
#
# Security and compliance teams may require explanations such as:
#
#
#       What was detected?
#
#       Which detector produced the finding?
#
#       Why was processing stopped?
#
#       Which policy applied?
#
#       Which destination was denied?
#
#       Was human review required?
#
#       What happened afterward?
#
#
# No single object should answer all of those questions.
#
#
# Explainability emerges from correlated domain records:
#
#
#       FINDING
#          +
#       ASSESSMENT
#          +
#       POLICY DECISION
#          +
#       ROUTING DECISION
#          +
#       WORKFLOW OUTCOME
#          +
#       TELEMETRY
#          |
#          v
#       EXPLAINABLE SECURITY EVENT
#
#
#       EXPLAINABILITY != GIANT OBJECT
#
#
# ============================================================================
# 39. FUTURE AUDITABILITY
# ============================================================================
#
# Auditability requires enough information to reconstruct what happened.
#
# It does not require storing every protected value.
#
#
# Good audit questions include:
#
#
#       What category was detected?
#
#       When?
#
#       By what kind of source?
#
#       Which policy evaluated it?
#
#       What decision resulted?
#
#       Which route was considered?
#
#       Was processing interrupted?
#
#       Was review required?
#
#
# The architecture should answer those questions through correlated,
# appropriately protected records.
#
#
#       AUDITABLE != COPY EVERYTHING
#
#
# ============================================================================
# 40. FUTURE RETENTION AND DELETION
# ============================================================================
#
# Different security artifacts may require different retention periods.
#
#
#       original data
#       prohibited-data finding
#       detector evidence
#       policy decision
#       audit event
#       incident record
#
#
# are not necessarily governed by identical retention rules.
#
#
#       FINDING RETENTION != PAYLOAD RETENTION
#
#
# Future lifecycle controls should preserve these distinctions.
#
#
# ============================================================================
# 41. FUTURE OBSERVABILITY MUST BE DATA-MINIMIZED
# ============================================================================
#
# Agent 11 will need observability.
#
# Observability must not become an excuse to duplicate protected data.
#
#
#       MORE LOGGING
#           !=
#       MORE SECURITY
#
#
# Good security telemetry should prefer:
#
#
#       identifiers
#       categories
#       states
#       decisions
#       safe metadata
#
#
# over:
#
#
#       raw secrets
#       raw PII
#       raw prohibited content
#
#
#       OBSERVABILITY != DATA HOARDING
#
#
# ============================================================================
# 42. FUTURE SECURITY TESTING
# ============================================================================
#
# SEIR-II should test prohibited-data controls as architecture, not merely
# test whether a Pydantic object can be instantiated.
#
#
# Useful scenarios may include:
#
#
#       PII detected before external inference
#
#       PII false-positive review
#
#       private key detected in context
#
#       credential returned by MCP tool
#
#       PII generated by model output
#
#       multiple findings in one request
#
#       UNKNOWN category
#
#       active-threat escalation
#
#       approved model unavailable during protected-data request
#
#       fallback destination prohibited by policy
#
#       agent-to-agent handoff preserving findings
#
#       sanitized data requiring re-evaluation
#
#
# The test should ask:
#
#
#       DID THE SECURITY ARCHITECTURE
#       PRESERVE THE CORRECT SEMANTICS?
#
#
# not merely:
#
#
#       DID THE CODE RETURN 200?
#
#
# ============================================================================
# 43. TEST FALSE POSITIVES
# ============================================================================
#
# Conservative detection creates false positives.
#
# That is expected.
#
# SEIR-II should measure them rather than pretending they do not exist.
#
#
# Questions include:
#
#
#       Which categories create the most false positives?
#
#       Which detectors create them?
#
#       How much operational friction results?
#
#       Can precision improve without unacceptable false negatives?
#
#
# Security tuning should be evidence-driven.
#
#
#       CONSERVATIVE
#           !=
#       NEVER IMPROVE PRECISION
#
#
# ============================================================================
# 44. TEST FALSE NEGATIVES
# ============================================================================
#
# False negatives are especially important for high-consequence categories.
#
#
#       PII MISSED
#       CREDENTIAL MISSED
#       PRIVATE KEY MISSED
#       HIGH-CONSEQUENCE SAFETY FINDING MISSED
#
#
# may create substantially greater harm than unnecessary review.
#
# SEIR-II testing should therefore evaluate:
#
#
#       precision
#       recall
#       consequence
#       review burden
#       policy effectiveness
#
#
# rather than optimizing one metric in isolation.
#
#
# ============================================================================
# 45. TEST SECURITY FAILURE MODES
# ============================================================================
#
# Agent 11 must also test what happens when the security infrastructure
# itself fails.
#
#
# Examples:
#
#
#       detector unavailable
#
#       detector timeout
#
#       malformed detector result
#
#       DLP service unavailable
#
#       policy service unavailable
#
#       evidence store unavailable
#
#       review system unavailable
#
#
# The architecture must define conservative behavior without falsifying
# observed state.
#
#
#       SECURITY COMPONENT FAILURE
#           !=
#       DATA IS SAFE
#
#
# ============================================================================
# 46. PRESERVE FAILURE DATA
# ============================================================================
#
# When security processing fails, future telemetry should preserve why.
#
#
#       detector unavailable
#           !=
#       no finding
#
#
#       assessment indeterminate
#           !=
#       safe
#
#
#       human review unavailable
#           !=
#       approved
#
#
# Therefore:
#
#
#       FAILURE TO ESTABLISH RISK
#           !=
#       ESTABLISHED ABSENCE OF RISK
#
#
# ============================================================================
# 47. SECURITY CONTROLS MUST REMAIN EXPLAINABLE TO HUMANS
# ============================================================================
#
# Audit, Compliance, Security, Privacy, Legal, and operations personnel
# need understandable states.
#
# Avoid architecture where the explanation is:
#
#
#       "The AI safety score was 0.48372."
#
#
# Prefer explicit domain facts:
#
#
#       PII finding detected
#
#       source = automatic detector
#
#       external route denied by policy
#
#       approved private route unavailable
#
#       request held for review
#
#
# Explicit state is easier to:
#
#
#       audit
#       explain
#       test
#       troubleshoot
#       govern
#
#
# ============================================================================
# 48. SECURITY MUST NOT BECOME A SINGLE MAGIC SCORE
# ============================================================================
#
# Future systems may use scoring internally for classification,
# prioritization, ranking, or optimization.
#
# Scores must not erase hard security boundaries.
#
#
# Never allow:
#
#
#       HIGH PII RISK
#           +
#       VERY CHEAP MODEL
#           +
#       VERY LOW LATENCY
#           =
#       ALLOW
#
#
# Security constraints must be evaluated independently.
#
#
#       POLICY NEVER BECOMES A SCORE
#
#
# ============================================================================
# 49. PROHIBITED-DATA CONTROL BELONGS IN THE AI CONTROL PLANE
# ============================================================================
#
# Agent 11's AI control plane coordinates:
#
#
#       classification
#       prohibited-data handling
#       policy
#       service state
#       network state
#       routing
#       MCP governance
#       telemetry
#
#
# It should determine whether and how AI processing may occur.
#
# The inference plane performs the actual model inference.
#
#
#       CONTROL PLANE
#           !=
#       INFERENCE PLANE
#
#
# Prohibited-data policy belongs to the control plane.
#
#
# ============================================================================
# 50. REASONING AUTHORIZATION != EXECUTION AUTHORIZATION
# ============================================================================
#
# Even if protected data is authorized for reasoning:
#
#
#       AUTHORIZED TO REASON
#
#
# that does not mean the resulting agent has authority to:
#
#
#       delete
#       modify
#       purchase
#       transfer
#       deploy
#       terminate
#       disclose
#
#
# anything.
#
#
#       REASONING AUTHORIZATION
#           !=
#       EXECUTION AUTHORIZATION
#
#
# This remains one of Agent 11's most important defenses against
# Judgment Day as Code.
#
#
# ============================================================================
# 51. PROHIBITED-DATA CONTROLS MUST NOT GRANT AUTHORITY
# ============================================================================
#
# A security detector may determine:
#
#
#       "No prohibited-data finding exists."
#
#
# That means only that the prohibited-data control did not establish a
# finding.
#
# It does NOT mean:
#
#
#       user authorized
#       route authorized
#       tool authorized
#       action authorized
#       output approved
#
#
# Therefore:
#
#
#       NO PROHIBITED-DATA FINDING
#           !=
#       GLOBAL AUTHORIZATION
#
#
# ============================================================================
# 52. POSSIBLE FUTURE NEIGHBORING CONTRACTS
# ============================================================================
#
# Operational evidence may eventually justify neighboring contracts such
# as:
#
#
#       ProhibitedDataAssessment
#
#       ProhibitedDataEvidence
#
#       ProhibitedDataProvenance
#
#       ProhibitedDataReview
#
#       ProhibitedDataDisposition
#
#       ProhibitedDataSeverity
#
#       ProhibitedDataContext
#
#       SafetyDecision
#
#       PrivacyDecision
#
#       ThreatAssessment
#
#       SanitizationResult
#
#
# THESE ARE CONCEPTUAL NAMES ONLY.
#
# They are not commitments.
#
# They are not implemented by this file.
#
#
#       POSSIBLE FUTURE NOUN
#           !=
#       REQUIRED CURRENT CLASS
#
#
# Create them only when the domain demonstrates that they are necessary.
#
#
# ============================================================================
# 53. POSSIBLE FUTURE ORCHESTRATION
# ============================================================================
#
# A mature future pipeline might conceptually resemble:
#
#
#       DATA
#        |
#        v
#       CLASSIFICATION
#        |
#        v
#       PROHIBITED-DATA DETECTION
#        |
#        v
#       ASSESSMENT
#        |
#        +--------------------+
#        |                    |
#        v                    v
#    SUFFICIENT            REVIEW
#    EVIDENCE              REQUIRED
#        |                    |
#        +---------+----------+
#                  |
#                  v
#          POLICY / SAFETY
#             EVALUATION
#                  |
#          +-------+-------+
#          |       |       |
#          v       v       v
#       BLOCK    ALLOW   ESCALATE
#                  |
#                  v
#              ROUTING
#                  |
#                  v
#              INFERENCE
#                  |
#                  v
#          OUTPUT INSPECTION
#                  |
#                  v
#          CONTROLLED RESULT
#
#
# This diagram preserves boundaries.
#
# It does not prescribe exact implementation.
#
#
# ============================================================================
# 54. FRAMEWORK INDEPENDENCE
# ============================================================================
#
# Agent 11 may evolve through:
#
#
#       plain Python
#       LangGraph
#       CrewAI
#       Amazon Bedrock AgentCore
#       MCP
#       custom orchestration
#       future frameworks not yet selected
#
#
# ProhibitedData should remain understandable regardless.
#
#
#       FRAMEWORKS CHANGE.
#
#       SECURITY SEMANTICS SHOULD SURVIVE THEM.
#
#
# ============================================================================
# 55. CLOUD INDEPENDENCE
# ============================================================================
#
# Likewise, Agent 11 may operate across:
#
#
#       AWS
#       Azure
#       GCP
#       OCI
#       on-premises infrastructure
#       future providers
#
#
# The meaning of:
#
#
#       PERSONALLY_IDENTIFIABLE_INFORMATION
#
#
# must not change because the deployment provider changed.
#
#
#       CLOUD PROVIDER != SECURITY SEMANTICS
#
#
# ============================================================================
# 56. CHEWBACCA VISITS SEIR-II
# ============================================================================
#
# SEIR-II Engineer:
#
#       "Chewbacca, I added confidence, severity, evidence, provenance,
#        jurisdiction, reviewer, incident number, cloud provider, region,
#        and policy version to ProhibitedData."
#
# Chewbacca:
#
#       "Why?"
#
#
# Engineer:
#
#       "Enterprise."
#
# Chewbacca:
#
#       "That is not an architecture."
#
#
# ---------------------------------------------------------------------------
#
# Engineer:
#
#       "Our DLP vendor has 600 proprietary categories."
#
# Chewbacca:
#
#       "Normalize them at the adapter boundary."
#
#
# Engineer:
#
#       "Should I add all 600 to Agent 11?"
#
# Chewbacca:
#
#       "Only if Agent 11 actually needs 600 domain distinctions."
#
#
# ---------------------------------------------------------------------------
#
# Engineer:
#
#       "Audit wants evidence that a private key was detected."
#
# Chewbacca:
#
#       "Good."
#
#
# Engineer:
#
#       "So I logged the private key."
#
# Chewbacca:
#
#       "That was not evidence. That was another incident."
#
#
# ---------------------------------------------------------------------------
#
# Engineer:
#
#       "The approved MCP tool returned PII."
#
# Chewbacca:
#
#       "Inspect the result."
#
#
# Engineer:
#
#       "But the tool is approved."
#
# Chewbacca:
#
#       "The tool is approved.
#        That does not make every byte it returns unrestricted."
#
#
# ---------------------------------------------------------------------------
#
# Engineer:
#
#       "Agent A was authorized to process this data."
#
# Chewbacca:
#
#       "And Agent B?"
#
#
# Engineer:
#
#       "I assumed the authorization followed the message."
#
# Chewbacca:
#
#       "Find the policy team."
#
#
# ---------------------------------------------------------------------------
#
# Engineer:
#
#       "The private model failed, so I routed the PII to the cheapest
#        external model."
#
# Chewbacca:
#
#       "You optimized before you authorized."
#
#
# ---------------------------------------------------------------------------
#
# Engineer:
#
#       "The detector is offline, so there are no findings."
#
# Chewbacca:
#
#       "No. The detector is offline."
#
#
# ---------------------------------------------------------------------------
#
# Engineer:
#
#       "The AI summarized the customer record, so it should be safe now."
#
# Chewbacca:
#
#       "Transformation is not sanitization."
#
#
# ---------------------------------------------------------------------------
#
# Engineer:
#
#       "Can I put every security concept into ProhibitedData?"
#
# Chewbacca:
#
#       "No."
#
#
# Engineer:
#
#       "Why?"
#
# Chewbacca:
#
#       "Because then you no longer have ProhibitedData.
#        You have ProhibitedEverything."
#
#
# ============================================================================
# 57. FINAL SEIR-II INVARIANTS
# ============================================================================
#
# Preserve these rules as prohibited-data controls become more sophisticated.
#
#
# ---------------------------------------------------------------------------
# FOUNDATIONAL CONTRACT
# ---------------------------------------------------------------------------
#
#       RICHER SYSTEM != FATTER FOUNDATIONAL OBJECT
#
#       FUTURE-AWARE != FUTURE-BLOATED
#
#       POSSIBLE FUTURE NOUN != REQUIRED CURRENT CLASS
#
#
# ---------------------------------------------------------------------------
# EVIDENCE-DRIVEN EVOLUTION
# ---------------------------------------------------------------------------
#
#       SEIR-I TELEMETRY
#           ->
#       OPERATIONAL EVIDENCE
#           ->
#       SEIR-II DOMAIN DESIGN
#
#
# ---------------------------------------------------------------------------
# DETECTOR BOUNDARY
# ---------------------------------------------------------------------------
#
#       DETECTOR IMPLEMENTATION != FINDING CONTRACT
#
#       DLP VENDOR VOCABULARY != AGENT 11 DOMAIN VOCABULARY
#
#       DLP SYSTEM != AGENT 11 DOMAIN CONTRACT
#
#
# ---------------------------------------------------------------------------
# ASSESSMENT BOUNDARY
# ---------------------------------------------------------------------------
#
#       FINDING != ASSESSMENT
#
#       CONFIDENCE != FINDING
#
#       FINDING != EVIDENCE
#
#       FINDING != PROVENANCE
#
#       SOURCE != COMPLETE PROVENANCE
#
#       CATEGORY != SEVERITY
#
#       FINDING != DISPOSITION
#
#
# ---------------------------------------------------------------------------
# REVIEW BOUNDARY
# ---------------------------------------------------------------------------
#
#       FINDING != REVIEW
#
#       HUMAN REVIEW != UNBOUNDED AUTHORITY
#
#       REVIEW APPROVAL != POLICY DELETION
#
#
# ---------------------------------------------------------------------------
# PRIVACY / LOCATION BOUNDARY
# ---------------------------------------------------------------------------
#
#       PII != RESIDENCY REQUIREMENT
#
#       RESIDENCY != CLASSIFICATION
#
#       RESIDENCY != ROUTING DOMAIN
#
#       FINDING != JURISDICTION
#
#       FINDING != CLOUD PROVIDER
#
#       FINDING != DEPLOYMENT LOCATION
#
#
# ---------------------------------------------------------------------------
# MULTIMODAL BOUNDARY
# ---------------------------------------------------------------------------
#
#       MODALITY != FINDING CATEGORY
#
#       DETECTION != REPLICATION
#
#       INPUT WAS SAFE != OUTPUT IS SAFE
#
#       AI-GENERATED != SAFE
#
#
# ---------------------------------------------------------------------------
# TRANSFORMATION BOUNDARY
# ---------------------------------------------------------------------------
#
#       PARAPHRASE != AUTOMATIC SANITIZATION
#
#       SUMMARY != AUTOMATIC SANITIZATION
#
#       TRANSLATION != AUTOMATIC SANITIZATION
#
#       REDACTION ATTEMPT != VERIFIED SAFE DATA
#
#       SANITIZATION ATTEMPT != AUTHORIZED DECLASSIFICATION
#
#
# ---------------------------------------------------------------------------
# MCP BOUNDARY
# ---------------------------------------------------------------------------
#
#       ORIGINAL REQUEST INSPECTED != MCP RESULT SAFE
#
#       APPROVED MCP TOOL != UNRESTRICTED MCP OUTPUT
#
#       TOOL NEEDS CREDENTIAL != MODEL NEEDS CREDENTIAL
#
#
# ---------------------------------------------------------------------------
# MULTI-AGENT BOUNDARY
# ---------------------------------------------------------------------------
#
#       AGENT HANDOFF != SECURITY RESET
#
#       AGENT A AUTHORIZED != AGENT B AUTHORIZED
#
#       AUTHORIZED FOR PROCESSING != AUTHORIZED FOR MEMORY
#
#
# ---------------------------------------------------------------------------
# TAXONOMY BOUNDARY
# ---------------------------------------------------------------------------
#
#       CAN NAME A CATEGORY != NEED A DOMAIN CATEGORY
#
#       SECURITY TAXONOMY != MORAL ONTOLOGY
#
#       CUSTOMER POLICY != ProhibitedDataCategory
#
#
# ---------------------------------------------------------------------------
# SAFETY BOUNDARY
# ---------------------------------------------------------------------------
#
#       ACTIVE_THREAT FINDING != THREAT-RESPONSE SYSTEM
#
#       HIGH CONSEQUENCE != UNIVERSAL WORKFLOW
#
#
# ---------------------------------------------------------------------------
# AUDIT / TELEMETRY BOUNDARY
# ---------------------------------------------------------------------------
#
#       AUDITABILITY != COPY THE PROTECTED DATA
#
#       EVIDENCE != PROTECTED PAYLOAD
#
#       AUDITABLE != COPY EVERYTHING
#
#       FINDING RETENTION != PAYLOAD RETENTION
#
#       OBSERVABILITY != DATA HOARDING
#
#       LOG THE FINDING.
#       DO NOT LOG THE SECRET.
#
#
# ---------------------------------------------------------------------------
# AUTOMATION BOUNDARY
# ---------------------------------------------------------------------------
#
#       DETECTION != EXECUTION AUTHORITY
#
#       FINDING != INCIDENT
#
#       INDIVIDUAL FINDING != CORRELATED INCIDENT
#
#
# ---------------------------------------------------------------------------
# FAILURE BOUNDARY
# ---------------------------------------------------------------------------
#
#       SECURITY COMPONENT FAILURE != DATA IS SAFE
#
#       DETECTOR UNAVAILABLE != NO FINDING
#
#       ASSESSMENT INDETERMINATE != SAFE
#
#       REVIEW SYSTEM UNAVAILABLE != APPROVED
#
#       FAILURE TO ESTABLISH RISK
#           !=
#       ESTABLISHED ABSENCE OF RISK
#
#
# ---------------------------------------------------------------------------
# POLICY / OPTIMIZATION BOUNDARY
# ---------------------------------------------------------------------------
#
#       POLICY NEVER BECOMES A SCORE
#
#       SECURITY CONSTRAINT != OPTIMIZATION PREFERENCE
#
#       CHEAPER != PERMITTED
#
#       FASTER != PERMITTED
#
#
# ---------------------------------------------------------------------------
# AUTHORITY BOUNDARY
# ---------------------------------------------------------------------------
#
#       REASONING AUTHORIZATION != EXECUTION AUTHORIZATION
#
#       NO PROHIBITED-DATA FINDING != GLOBAL AUTHORIZATION
#
#
# ---------------------------------------------------------------------------
# PLATFORM BOUNDARY
# ---------------------------------------------------------------------------
#
#       CONTROL PLANE != INFERENCE PLANE
#
#       FRAMEWORKS CHANGE.
#       SECURITY SEMANTICS SHOULD SURVIVE THEM.
#
#       CLOUD PROVIDER != SECURITY SEMANTICS
#
#
# ============================================================================
# 58. LETTER TO THE FUTURE ENGINEER
# ============================================================================
#
# If you are modifying this file during SEIR-II, do not begin by asking:
#
#
#       "What additional fields can I put on ProhibitedData?"
#
#
# Begin by asking:
#
#
#       "What new domain concept did operational evidence reveal?"
#
#
# Then determine which component owns that concept.
#
#
# If the answer is:
#
#
#       detector assessment
#       evidence
#       provenance
#       review
#       severity
#       policy
#       privacy
#       legal disposition
#       incident response
#       routing
#       deployment
#       network
#       MCP
#       execution authority
#
#
# then the answer is probably NOT:
#
#
#       "Add another field to ProhibitedData."
#
#
# Preserve the noun.
#
# Build the neighboring architecture.
#
#
#       SMALL CONTRACTS
#           +
#       EXPLICIT BOUNDARIES
#           +
#       CONSERVATIVE SECURITY
#           +
#       EVIDENCE-DRIVEN EVOLUTION
#           =
#       ARCHITECTURE THAT CAN SURVIVE SEIR-II
#
#
# ============================================================================
# END PART III
# ============================================================================
