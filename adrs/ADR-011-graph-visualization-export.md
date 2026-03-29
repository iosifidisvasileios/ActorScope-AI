# ADR-011: Provide LangGraph visualization export capabilities

## Status
**Implemented**

## Context
The system needs to support:
- Visual understanding of the simulation flow
- Documentation of the graph structure
- Debugging and communication tools
- Architecture visualization for stakeholders

LangGraph graphs are complex and textual descriptions are insufficient for understanding node relationships and flow patterns.

## Decision
Implement graph visualization export with:

### Multiple output formats
- **PNG**: Direct visual representation when rendering is available
- **Mermaid (.mmd)**: Source format for documentation and custom rendering
- **Status file**: Fallback information when rendering fails

### Export utility
- `export_langgraph_figure.py` standalone script
- Automatic artifact directory creation
- Graceful handling of unavailable rendering features
- Clear status reporting

### Integration points
- Export to `artifacts/` directory alongside other outputs
- Consistent naming conventions
- Error handling for missing dependencies

## Implementation details
```python
# Core functionality
app = build_graph()
graph = app.get_graph()
graph.draw_mermaid()        # Mermaid source
graph.draw_mermaid_png()    # PNG bytes (when available)
```

## Alternatives considered
### Manual diagram creation
Rejected because it would become outdated as the graph evolves and creates maintenance overhead.

### Text-only graph descriptions
Rejected because visual relationships are much easier to understand than node lists.

### External documentation only
Rejected because having the export as part of the codebase ensures it stays current with the actual implementation.

## Rationale
Visual documentation is essential for complex graph systems. Providing automated exports ensures documentation stays synchronized with implementation and supports both technical and non-technical stakeholders.

## Consequences
- Graph structure is always documented and current
- Easy inclusion in README and documentation
- Supports debugging and architecture discussions
- Graceful degradation when rendering is unavailable
- Additional artifact in the standard output location

## Usage
```bash
poetry run python export_langgraph_figure.py
```

Outputs:
- `artifacts/langgraph_graph.png` (when rendering available)
- `artifacts/langgraph_graph.mmd` (Mermaid source)
- `artifacts/langgraph_graph.txt` (status and fallback)

## Future considerations
- Integration with documentation pipelines
- Custom styling options
- Interactive graph viewers
- Graph comparison tools for different versions
