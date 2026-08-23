        agent11/
        │
        ├── __init__.py
        ├── orchestrator.py
        │
        ├── models/
        │   │
        │   ├── __init__.py
        │   ├── base_model.py
        │   │
        │   ├── enums/
        │   │   ├── __init__.py
        │   │   ├── base_enum.py
        │   │   │
        │   │   ├── ai_enums.py
        │   │   ├── routing_enums.py
        │   │   ├── policy_enums.py
        │   │   ├── model_enums.py
        │   │   └── network_enums.py
        │   │
        │   └── ai/
        │       ├── __init__.py
        │       ├── request.py
        │       ├── response.py
        │       ├── capability.py
        │       ├── model.py
        │       ├── service.py
        │       ├── routing.py
        │       ├── policy.py
        │       ├── data_classification.py
        │       ├── prohibited_data.py
        │       └── orchestrator.py
        │
        ├── routing/
        │   ├── __init__.py
        │   ├── orchestrator.py
        │   ├── router.py
        │   ├── model_router.py
        │   ├── fallback.py
        │   └── network_context.py
        │
        ├── policy/
        │   ├── __init__.py
        │   ├── orchestrator.py
        │   ├── data_policy.py
        │   ├── policy_gate.py
        │   └── user_policy.py
        │
        ├── models_runtime/
        │   ├── __init__.py
        │   ├── orchestrator.py
        │   ├── registry.py
        │   ├── company_cloud.py
        │   ├── company_onprem.py
        │   └── external_fm.py
        │
        ├── mcp/
        │   ├── __init__.py
        │   ├── orchestrator.py
        │   ├── client.py
        │   ├── service.py
        │   └── tool_registry.py
        │
        ├── network/
        │   ├── __init__.py
        │   ├── orchestrator.py
        │   ├── endpoint.py
        │   ├── health.py
        │   └── path.py
        │
        ├── telemetry/
        │   ├── __init__.py
        │   ├── orchestrator.py
        │   ├── routing_event.py
        │   ├── policy_event.py
        │   └── usage.py
        │
        └── general/
            ├── README.md
            ├── AGENT_11.md
            ├── AGENT_11_PLAYBOOK.md
            ├── INSTALL.md
            ├── AI_ROUTING.md
            ├── DATA_POLICY.md
            └── MCP.md
