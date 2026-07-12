---
name: example-ablate-before-adding
type: skill
status: candidate
created: 2026-06-11
nights_used: 0
source: seeded as a format example at lab setup
---

Before adding complexity to train.py, spend one run removing something. A
deletion that holds val_bpb constant is a win (simplicity criterion), and the
freed VRAM/compute budget often makes the *next* additive experiment viable.

Procedure: pick the component you trust least (a norm layer, a residual scale,
an activation choice). Run one experiment with it removed. If val_bpb is equal
or better, keep the deletion and log it as `keep`. Only then try the additive
idea you originally had.
