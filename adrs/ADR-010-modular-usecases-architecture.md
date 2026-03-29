# ADR-010: Use modular usecases architecture for scenario management

## Status
**Implemented**

## Context
The system needs to support:
- Multiple built-in scenarios of varying complexity
- Custom scenario input from external sources
- Flexible execution patterns for different use cases
- Clear separation between scenario definitions and execution logic

Hard-coding scenarios in main.py creates maintenance issues and limits extensibility.

## Decision
Create a modular `usecases/` package with:

### Scenario definitions
- Individual Python modules for each built-in scenario
- Standardized factory functions returning scenario dictionaries
- Clear separation between simple and complex scenarios

### Execution utilities
- `run_usecase.py` - Universal execution script
- Support for built-in scenario selection via name
- Support for custom JSON scenario input
- Flexible artifact directory configuration

### Registry pattern
- `USECASE_REGISTRY` mapping names to factory functions
- Easy discovery and selection of available scenarios
- Extensible design for future scenario additions

## Implementation structure
```
usecases/
├── __init__.py
├── run_usecase.py          # Universal execution script
├── demo_organization.py    # Simple workplace scenario
├── us_iran_regional_crisis.py  # Complex geopolitical scenario
└── [future scenarios...]
```

## Alternatives considered
### Keep scenarios in main.py
Rejected because it creates monolithic code and limits scenario diversity.

### JSON-only scenario definitions
Rejected because Python provides better validation, documentation, and complex object construction.

### Database-backed scenarios
Rejected for v1 as it adds unnecessary complexity; file-based is sufficient.

## Rationale
This architecture supports both simple demos and complex real-world scenarios while keeping the core simulation engine clean and scenario-agnostic.

## Consequences
- Scenarios are easily discoverable and selectable
- Custom scenarios can be provided without code changes
- Built-in scenarios can range from simple to complex
- Main.py becomes a thin wrapper rather than scenario host
- Future scenarios can be added without modifying core logic
- Scenario complexity is not limited by execution framework

## Example usage
```bash
# Run default complex scenario
poetry run python main.py

# Run simple demo
poetry run python usecases/run_usecase.py --usecase demo_organization

# Run custom scenario
poetry run python usecases/run_usecase.py --input-json my_scenario.json
```
