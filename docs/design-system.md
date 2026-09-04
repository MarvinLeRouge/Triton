[🇫🇷 Version française](design-system.fr.md) | 🇬🇧 English version

---

# Design System

**Status**: preparatory. The frontend currently renders a functional but
unstyled Canvas view (grid, entities, sonar cones, probability heatmap) with
no deliberate visual design pass yet. This document describes the sections
this file is expected to contain once the Phase 7 `impeccable` design pass
runs, so the intended scope is visible before the work starts. Content below
will be replaced with the actual, evaluated design decisions at that point —
treat it as a placeholder, not a settled specification.

## Expected sections (to be filled in during Phase 7)

- **Color palette**: a coherent scale for the probability heatmap (low → high
  confidence), distinct colors for Blue/Red entities and sonar cones, legible
  in both light and dark contexts if a theme toggle is added.
- **Entity iconography**: how `BlueMothership`, `BlueDrone`, and `RedVessel`
  are visually distinguished on the canvas, including detection-state
  indicators (searching / signaling / confirming / tracking).
- **Visual hierarchy**: what draws the eye first during a running simulation
  (active detections, the mothership, the current turn/result banner).
- **Accessibility**: contrast ratios for the heatmap and entity markers,
  any non-color-dependent cues for detection state (shape, not just hue).
- **Responsive behavior**: how the canvas and side panel adapt to different
  viewport sizes.

## Why this is deferred

Per the project's own roadmap decision, the `impeccable` design pass is
deliberately scheduled for Phase 7, once the API, WebSocket protocol, and UI
surfaces have stabilized — running it earlier would mean redoing work as the
canvas layout kept changing across Phases 1–6 (cones, heatmap, state
machine, etc.).
