# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository nature

TBAS is a **schema repository**. It defines the **Time-Based Agnostic
Structure**: a JSON Schema 2020-12 specification for time-base components —
frequency-control products (quartz crystals, ceramic resonators, XO / TCXO /
VCXO / OCXO, MEMS, silicon-RC, programmable oscillators), 555-class timers,
and SR latches — each family carrying both datasheet fields for orderable
parts and a simulator-agnostic ideal `behavioral` block (the control atoms
of PEAS-RFC 0001: periodic source / one-shot / latch). Work here is editing
JSON Schema files and Markdown docs.

Boundary tests: a PWM/LLC/PFC controller is CTAS; an op amp / comparator /
sample-and-hold is AAS; RTC modules, clock generators/buffers, RF VCOs and
SAW devices are deliberately OUT (calendar/distribution/RF — not time bases).

The only executable is `scripts/validate.py` (the validation gate). Run it
after every schema change:

```bash
pip install jsonschema referencing
python3 scripts/validate.py
```

## Layout (the AAS pattern)

- `schemas/tbas.json` — top wrapper `{ inputs, <family>, outputs }` with the
  bare-component/full-document `anyOf` + a `oneOf` over the 3 family
  discriminators (`oscillator` | `timer` | `latch`). Every valid TBAS
  document is also a valid PEAS document (the `timeBase` branch).
- `schemas/<family>.json` — one file per family: `{ manufacturerInfo,
  distributorsInfo, behavioral }`, any one alone valid;
  `manufacturerInfo.datasheetInfo = { part, electrical, thermal, mechanical,
  provenance }`.
- `schemas/utils.json` — TBAS-owned shared defs (`part`/`thermal`/`mechanical`
  over the PEAS `datasheetInfo*` bases, TBAS `supply`, family enums).
- `schemas/inputs.json` + `schemas/inputs/designRequirements.json` — seed on
  the PEAS `designRequirementsBase` mixin with `deviceType` discriminator.
- `schemas/outputs.json` — selection-only output surface on PEAS `outputBase`.
- `docs/schema.md`, `examples/*.json` — keep in sync with schema edits and
  re-run `validate.py`.

There is **no** `data/` directory: orderable parts live in
**`TAS/data/time_bases.ndjson`** (PEAS-wrapped `{"timeBase": ...}`),
validated by `TAS/tests/test_data.py` and physics-checked by the TAS
validator ("Blade Runner", `TAS/validator/src/time_bases.cpp`).

## Conventions that carry weight here

- Fractional-frequency quantities (tolerance, stability, aging, pull range,
  duty cycle, spread bandwidth) are **dimensionless fractions** (1 ppm =
  1e-6, 1% = 0.01) — the same field serves ppm-class quartz and %-class
  ceramic/RC parts. Everything else SI.
- The operating-temperature range that `frequencyStability` is specified
  over lives in `datasheetInfo.thermal` (PEAS mixin) — do NOT add a second
  temperature range to `electrical`.
- Behavioral blocks follow the no-fallbacks rule: everything an emitter
  needs is required (`offset`, `dominance`, `retriggerable` have no
  defaults); "absent = waveform origin" style conventions are documented
  physical conventions, not silent numeric defaults.
- `technology` enum growth: compound classes are combinations, not values
  (VCTCXO = tcxo + pullRange; DCXO = programmable). Don't add SAW/RTC/clock-gen
  values — they are out of scope by design.
