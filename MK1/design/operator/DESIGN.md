# ECHO Operator design specification

Status: SPECIFIED / IMPLEMENTATION_AUTHORIZED / VISUAL_QA_NOT_EXECUTED.
All visual values below are GENERATED, confidence: design choice, not measured
ECHO identity. Scientific authority remains PROJECT-CHARTER.md.

Tokens: background #080d16; panel #101927; elevated #172337; border #26354b;
primary text #eef4ff; secondary #a5b4cb; accent #62ddbd; warning #f3c878;
danger #fb8f9b; blue #86b8ff. System sans typography, tabular numeric values,
8px spacing unit, 16px panels, 44px minimum controls, visible focus outlines.

Desktop: narrow navigation rail, header, evidence banner, four KPI cards,
camera grid plus selected source monitor, timeline. Mobile <760px: bottom
navigation, single-column cards, alert-first page, selected monitor in flow.
Tablet <1100px: collapse rail labels, two-column cards. No horizontal content
overflow; scroll inside the camera grid only when needed.

Views: Operations / Sources / Events / Alerts / Settings. Sources support search,
grid/list, activity-only and priority/source order. Events filter source, type,
lifecycle, origin and UTC date range with paginated results. Detail links preserve
event identity. Alerts offer acknowledge/resolve with audit history.

Every state uses text and a symbol as well as color. Evidence labels: LAB
DIAGNOSTIC, CONTROLLED / UNASSESSED, ACCEPTED OPERATIONAL, UNKNOWN / ABSTAIN.
CONFIRMED means temporal acoustic evidence, never an emergency. Unavailable data
renders an em dash; stale data loses LIVE and the camera tile loses activity
emphasis. Loading, empty, failure, expired session, push denial, unsupported push,
offline, reconnecting and command pending broker receipt are explicit.

Motion: only a quiet live marker; no invented waveform, score or event. Respect
prefers-reduced-motion. SVG waveforms use measured envelope; score bars use real
scores. No auto-playing audio. Controls have names and label associations, keyboard
focus, status updates through polite aria-live, and a skip-to-main link.

Live workflow: sign in → choose camera → request playback → change lab scenario
→ observe MQTT source generation separately from worker session → inspect real
score/window evidence → inspect LAB candidate → optionally send explicitly labeled
lab push. Alerts may legitimately remain empty while the robustness gate is open.
