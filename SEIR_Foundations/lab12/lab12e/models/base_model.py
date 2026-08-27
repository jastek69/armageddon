"""
Agent 11 Base Model
===================

Provides the common Pydantic foundation used by Agent 11 domain models.

Agent11BaseModel establishes shared validation behavior while keeping
Pydantic visible to developers and students.

Agent 11 models should use normal Pydantic methods directly, including:

    model_validate()
    model_validate_json()
    model_dump()
    model_dump_json()
    model_copy()
    model_json_schema()

The base model does NOT contain:

    - AI routing logic
    - policy enforcement
    - network logic
    - model invocation
    - MCP logic
    - service health checks
    - timestamps or identifiers that do not apply to every model

Architecture rule:

    MODELS describe.
    PYDANTIC validates.
    POLICY permits.
    NETWORK reports reachability.
    ROUTING selects.
    SERVICES execute.
    ORCHESTRATORS coordinate.
"""

from pydantic import BaseModel, ConfigDict


class Agent11BaseModel(BaseModel):
    """
    Common Pydantic base class for Agent 11 domain models.

    This class establishes shared validation behavior for the Agent 11
    model layer without hiding or replacing Pydantic's native API.

    Models inheriting from Agent11BaseModel receive:

        - validation when the model is created
        - validation when fields are reassigned
        - rejection of undeclared fields
        - normal Pydantic Enum behavior
        - standard Pydantic serialization
        - standard Pydantic JSON Schema generation

    Example:

        class ReasoningProfile(Agent11BaseModel):
            estimated_tokens: int

        profile = ReasoningProfile(
            estimated_tokens=50_000,
        )

        # Standard Pydantic serialization
        data = profile.model_dump()

        # Standard Pydantic JSON serialization
        json_data = profile.model_dump_json(indent=2)

        # Standard Pydantic validation
        profile = ReasoningProfile.model_validate(
            {
                "estimated_tokens": 50_000,
            }
        )

        # Standard Pydantic JSON Schema
        schema = ReasoningProfile.model_json_schema()
    """

    model_config = ConfigDict(
        # Validate values when fields are changed after model creation.
        #
        # Without this:
        #
        #     profile.estimated_tokens = "いっぱいね"
        #
        # could bypass normal creation-time validation.
        validate_assignment=True,

        # Reject fields that are not explicitly defined by the model.
        #
        # This is particularly useful for catching spelling mistakes
        # and unexpected data entering Agent 11.
        #
        # Example:
        #
        #     RoutingDecision(
        #         selected_route=...,
        #         seleced_model=...,   # Typo
        #     )
        #
        # Pydantic should reject the unexpected field rather than
        # silently ignoring it.
        extra="forbid",

        # Preserve Enum instances inside Python models.
        #
        # Agent 11 is intentionally Enum-driven. Internal code should
        # therefore be able to work with:
        #
        #     route == AIRoute.COMPANY_ONPREM_LLM
        #
        # rather than reducing controlled vocabulary to arbitrary
        # strings throughout the application.
        use_enum_values=False,
    )
