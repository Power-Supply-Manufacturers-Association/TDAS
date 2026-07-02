# TBAS — Time-Based Agnostic Structure

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A vendor-neutral JSON Schema (draft 2020-12) data model for **time-base
components**: frequency-control products (quartz crystals, ceramic
resonators, XO / TCXO / VCXO / OCXO, MEMS and silicon-RC oscillators,
programmable oscillators), **555-class timers** and **set/reset latches** —
plus the simulator-agnostic ideal `behavioral` blocks (periodic source /
one-shot / latch) that make PWM, peak-current-mode, constant-on-time and
resonant frequency-modulation control loops netlistable from atoms
(PEAS-RFC 0001).

TBAS is part of the OpenConverters *Agnostic Structure* family rooted at
[PEAS](../PEAS): every valid TBAS document is also a valid PEAS document
(the `timeBase` branch). Boundaries: PWM/LLC/PFC **controller ICs** live in
CTAS; **analog signal-path ICs** (op amps, comparators, sample-and-holds)
live in AAS; **RTC modules, clock generators/buffers/jitter attenuators, RF
VCOs and SAW devices** are deliberately out of scope (calendar/distribution/RF,
not time bases for a converter BOM).

## Document shape

```json
{
  "inputs":     { "designRequirements": { "deviceType": "oscillator", ... } },
  "oscillator": { "manufacturerInfo": { ... },  "behavioral": { ... } },
  "outputs":    [ { "selection": { ... } } ]
}
```

Exactly one of `oscillator` | `timer` | `latch` (the field name is the
discriminator, the SAS/AAS pattern). A bare component (`{"oscillator": {}}`),
a part-less ideal block (`{"oscillator": {"behavioral": ...}}`) and a fully
bound part are all valid — datasheet requireds apply only once
`manufacturerInfo` is present.

## The families

| Family | Orderable parts | Ideal behavioral atom |
|---|---|---|
| `oscillator` | quartz crystals, ceramic resonators, XO/TCXO/VCXO/OCXO, MEMS, silicon-RC, programmable | periodic source: sawtooth/triangle/square/sine, optional VCO (`frequencyControl`) |
| `timer` | 555 class (bipolar/CMOS/precision/programmable) | monostable one-shot (constant-on-time) / astable |
| `latch` | discrete SR latches (74HC279 class) | set/reset memory with independent thresholds and required `dominance` |

Fractional-frequency specs (tolerance, stability, aging, pull range) are
stored as **dimensionless fractions** (1 ppm = 1e-6; 1 % = 0.01) — one field
serves ppm-class quartz and %-class ceramic/RC parts. All other values SI.

## Validation

```bash
pip install jsonschema referencing
python3 scripts/validate.py
```

Three gates (a gate that cannot run FAILS): schema meta-validation + full
`$ref` resolution against the sibling-repo registry, examples against
`tbas.json`, and PEAS citizenship of every example. Requires the sibling
repos checked out alongside TBAS (see [the workspace layout](../PEAS)).

Finished orderable parts live in **`TAS/data/time_bases.ndjson`** (PEAS-wrapped
`{"timeBase": ...}`), validated by `TAS/tests/test_data.py` and physics-checked
by the TAS validator.

## Examples

- [`examples/mems-oscillator-25mhz.json`](examples/mems-oscillator-25mhz.json) — bound MEMS XO with full datasheet block
- [`examples/watch-crystal-32768.json`](examples/watch-crystal-32768.json) — bare 32.768 kHz quartz crystal
- [`examples/ideal-pwm-ramp-behavioral.json`](examples/ideal-pwm-ramp-behavioral.json) — part-less PWM sawtooth atom
- [`examples/ne555-monostable.json`](examples/ne555-monostable.json) — NE555 with both datasheet and behavioral blocks
- [`examples/ideal-pcm-latch-behavioral.json`](examples/ideal-pcm-latch-behavioral.json) — part-less PCM gate latch

## License

MIT — see [LICENSE](LICENSE).
