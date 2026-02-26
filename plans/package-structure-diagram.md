# gcsbuffer Package Structure Diagram

## Current Structure (Before Refactoring)

```mermaid
graph TD
    A[gcsbuffer/] --> B[classes/]
    B --> B1[vertex.py - DUPLICATE]
    B --> B2[edge.py - DUPLICATE]
    B --> B3[polygon.py - DUPLICATE]
    B --> B4[polyline.py - DUPLICATE]
    B --> B5[circle.py - DUPLICATE]
    B --> B6[timer.py - DUPLICATE]
    B --> B7[gcstiff.py - KEEP]
    B --> B8[pycase.py - KEEP]

    A --> C[algorithms/]
    C --> C1[find_minimal_enclosing_polygon.py]
    C --> C2[split_by_length.py]

    A --> D[formats/]
    D --> D1[save_vertex_as_polygon.py]

    style B1 fill:#ffcccc
    style B2 fill:#ffcccc
    style B3 fill:#ffcccc
    style B4 fill:#ffcccc
    style B5 fill:#ffcccc
    style B6 fill:#ffcccc
    style B7 fill:#ccffcc
    style B8 fill:#ccffcc
```

## Proposed Structure (After Refactoring)

```mermaid
graph TD
    A[gcsbuffer/] --> A1[__init__.py - Main Entry Point]

    A --> B[buffer/]
    B --> B1[__init__.py]
    B --> B2[raster.py - gcstiff renamed]

    A --> C[utils/]
    C --> C1[__init__.py]
    C --> C2[case.py - pycase renamed]

    A --> D[algorithms/]
    D --> D1[__init__.py]
    D --> D2[find_minimal_enclosing_polygon.py]
    D --> D3[split_by_length.py]

    A --> E[formats/]
    E --> E1[__init__.py]
    E --> E2[save_vertex_as_polygon.py]

    style B2 fill:#ccffcc
    style C2 fill:#ccffcc
    style D2 fill:#cce5ff
    style D3 fill:#cce5ff
    style E2 fill:#cce5ff
```

## Import Flow Diagram

```mermaid
graph LR
    subgraph User Code
        U[from gcsbuffer import point, line, polygon, polyline, circle, timer]
    end

    subgraph gcsbuffer Main __init__.py
        G[gcsbuffer/__init__.py]
    end

    subgraph pyearth Geometry
        P1[pyearth.toolbox.mesh.point.pypoint]
        P2[pyearth.toolbox.mesh.line.pyline]
        P3[pyearth.toolbox.mesh.polygon.pypolygon]
        P4[pyearth.toolbox.mesh.polyline.pypolyline]
        P5[pyearth.toolbox.mesh.circle.pycircle]
        P6[pyearth.toolbox.date.timer.pytimer]
    end

    subgraph gcsbuffer Buffer Classes
        B1[gcsbuffer.buffer.raster.RasterBuffer]
        B2[gcsbuffer.utils.case.BufferCase]
    end

    U --> G
    G --> P1
    G --> P2
    G --> P3
    G --> P4
    G --> P5
    G --> P6
    G --> B1
    G --> B2

    style U fill:#e1f5ff
    style G fill:#fff9c4
    style P1 fill:#c8e6c9
    style P2 fill:#c8e6c9
    style P3 fill:#c8e6c9
    style P4 fill:#c8e6c9
    style P5 fill:#c8e6c9
    style P6 fill:#c8e6c9
    style B1 fill:#ffccbc
    style B2 fill:#ffccbc
```

## Class Mapping Flow

```mermaid
graph TD
    subgraph Old gcsbuffer Classes - DELETE
        O1[pyvertex]
        O2[pyedge]
        O3[pypolygon]
        O4[pyflowline]
        O5[pycircle]
        O6[pytimer]
    end

    subgraph New Imports from pyearth
        N1[pypoint as point]
        N2[pyline as line]
        N3[pypolygon as polygon]
        N4[pypolyline as polyline]
        N5[pycircle as circle]
        N6[pytimer as timer]
    end

    subgraph gcsbuffer-Specific - KEEP
        K1[gcstiff as RasterBuffer]
        K2[pycase as BufferCase]
    end

    O1 -.->|replace with| N1
    O2 -.->|replace with| N2
    O3 -.->|replace with| N3
    O4 -.->|replace with| N4
    O5 -.->|replace with| N5
    O6 -.->|replace with| N6

    style O1 fill:#ffcccc
    style O2 fill:#ffcccc
    style O3 fill:#ffcccc
    style O4 fill:#ffcccc
    style O5 fill:#ffcccc
    style O6 fill:#ffcccc
    style N1 fill:#c8e6c9
    style N2 fill:#c8e6c9
    style N3 fill:#c8e6c9
    style N4 fill:#c8e6c9
    style N5 fill:#c8e6c9
    style N6 fill:#c8e6c9
    style K1 fill:#fff9c4
    style K2 fill:#fff9c4
```

## File Operations Summary

```mermaid
graph LR
    subgraph DELETE
        D1[classes/vertex.py]
        D2[classes/edge.py]
        D3[classes/polygon.py]
        D4[classes/polyline.py]
        D5[classes/circle.py]
        D6[classes/timer.py]
    end

    subgraph MOVE & RENAME
        M1[classes/gcstiff.py → buffer/raster.py]
        M2[classes/pycase.py → utils/case.py]
    end

    subgraph KEEP IN PLACE
        K1[algorithms/]
        K2[formats/]
    end

    style D1 fill:#ffcccc
    style D2 fill:#ffcccc
    style D3 fill:#ffcccc
    style D4 fill:#ffcccc
    style D5 fill:#ffcccc
    style D6 fill:#ffcccc
    style M1 fill:#fff9c4
    style M2 fill:#fff9c4
    style K1 fill:#c8e6c9
    style K2 fill:#c8e6c9
```

## Legend

- 🔴 Red: Files to DELETE (duplicates of pyearth)
- 🟢 Green: Files to KEEP (gcsbuffer-specific or from pyearth)
- 🟡 Yellow: Files to MOVE/RENAME
- 🔵 Blue: Supporting modules (algorithms, formats)
