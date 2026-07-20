# TDAS schema reference

Generated against the schemas in `schemas/` — keep in sync when editing them.

## Top level (`tdas.json`)

`{ inputs, <family>, outputs }` — exactly one of `oscillator` | `timer` |
`latch` (top-level field presence is the discriminator). A single-key bare
component is valid; a document with `inputs` must also carry `outputs`.
Every valid TDAS document is a valid PEAS document under `{timeBase: ...}`.

## `inputs` (`inputs.json`)

- `designRequirements`* — the selection seed (below)
- `operatingPoints[]` — `{name, ambientTemperature [degC], supplyVoltage [V]}`

### `designRequirements` (`inputs/designRequirements.json`)

PEAS `designRequirementsBase` mixin + `deviceType`* (`oscillator`/`timer`/`latch`),
`frequency` (dimensionWithTolerance, Hz), `maximumFrequencyStability`
(dimensionless), `maximumRmsPhaseJitter` (s), `supplyVoltage`
(dimensionWithTolerance, V), `maximumCurrentConsumption` (A). Sealed with
`unevaluatedProperties: false`.

## `oscillator` (`oscillator.json`)

`{ manufacturerInfo, distributorsInfo, behavioral }` — any one alone is valid
(`manufacturerInfo` | `behavioral` | empty seed).

### `electrical`

All optional (partial datasheet data validates); the set mirrors the live
distributor filter columns plus headline datasheet specs, nothing derived:

| Field | Unit | Notes |
|---|---|---|
| `technology` | enum | `quartzCrystal`, `ceramicResonator` (bare resonators), `crystalOscillator`, `tcxo`, `vcxo`, `ocxo`, `mems`, `siliconRC`, `programmable` (covers pin-selectable + DCXO). VCTCXO = `tcxo` + `pullRange`. |
| `frequency` | Hz | nominal output / resonant frequency |
| `mode` | enum | `fundamental`, `overtone3/5/7` (quartz only) |
| `outputType` | enum | `cmos`, `lvds`, `lvpecl`, `hcsl`, `clippedSine`, `sine`, `none` (bare resonator) |
| `frequencyTolerance` | — | initial tolerance at 25 degC, fraction (1 ppm = 1e-6) |
| `frequencyStability` | — | over the operating temperature range (which lives in `thermal.operatingTemperature`) |
| `agingPerYear` | /yr | fractional aging, first-year value |
| `rmsPhaseJitter` | s | + `jitterBandLow`/`jitterBandHigh` (Hz) — the integration band it was specified over |
| `startupTime` | s | OCXO: warm-up to initial tolerance |
| `pullRange` | — | absolute pull range (APR), pulled classes only |
| `dutyCycle` | — | output symmetry window (dimensionWithTolerance; 45–55% = `{minimum: 0.45, maximum: 0.55}`) |
| `spreadSpectrum` | — | SSXO only: `{bandwidth (fraction), mode (downSpread/centerSpread)}` |
| `enableFunction` | enum | `none`, `outputEnable`, `standby`, `triState` |
| `loadCapacitance` | F | bare resonators (CL) |
| `equivalentSeriesResistance` | Ohm | bare quartz (ESR max) |
| `resonantImpedance` | Ohm | ceramic resonators |
| `builtInCapacitance` | F | three-terminal ceramic resonators |
| `shuntCapacitance` | F | bare resonators: C0, static shunt capacitance (typ. 1–7 pF quartz) |
| `motionalCapacitance` | F | bare resonators: C1/Cm, motional-arm capacitance (typ. 1–30 fF quartz); with C0 gives exact pull ΔF/F = C1 / (2·(C0 + CL)) |
| `supply` | — | `{minimumSupplyVoltage, maximumSupplyVoltage, currentConsumption, warmupPower (OCXO)}` |

### `behavioral` (the TDAS periodic-source atom)

Required: `shape` (`sawtooth`/`triangle`/`square`/`sine`), `frequency` (Hz),
`amplitude` (V), `offset` (V). Optional: `phase` (rad; absent = waveform
origin), `dutyCycle` (required iff `shape=square`), `frequencyControl`
(`{gain [Hz/V]}` — present = VCO, f = frequency + gain·v(control)).
Emission: fixed saw/tri/square → PULSE, fixed sine → SINE; any VCO →
canonical phase-accumulator subcircuit.

## `timer` (`timer.json`)

### `electrical`
`technology` (`bipolar555`/`cmos555`/`precision`/`programmable`),
`maximumFrequency` (Hz), `timingAccuracy` (fraction), `numberOfChannels`
(556 = 2), `supply`.

### `behavioral` (the TDAS one-shot atom)
Required: `mode` (`monostable`/`astable`), `outputHigh`, `outputLow` (V).
Monostable additionally requires `threshold` (V), `polarity`
(`risingEdge`/`fallingEdge`), `onTime` (s), `retriggerable` (bool — required,
the behaviors differ exactly at COT minimum-off-time); astable requires
`period` (s) + `dutyCycle`. Cross-mode fields are rejected (complete oneOf).

## `latch` (`latch.json`)

### `electrical`
`technology` (`CMOS`/`TTL`), `propagationDelay` (s), `numberOfChannels`, `supply`.

### `behavioral` (the TDAS memory atom)
All required: `setThreshold`, `resetThreshold`, `outputHigh`, `outputLow` (V),
`dominance` (`set`/`reset` — never defaulted; PCM gate latches are
reset-dominant so over-current wins the race with the clock).

## `outputs` (`outputs.json`)

Per operating point, a single optional `selection` block on the PEAS
`outputBase` shell: `frequencyErrorWorstCase` (fraction),
`supplyVoltageMargin` (fraction), `passes`* (bool).

## Shared (`utils.json`)

`part` / `thermal` / `mechanical` extend the PEAS `datasheetInfo*` bases
(AAS pattern, sealed extension branches). `supply` is TDAS-specific
(single-channel current; `warmupPower` because the OCXO oven makes warm-up
power a first-class spec; steady-state power is derivable and NOT stored).
Enums: `oscillatorTechnology`, `oscillatorMode`, `outputType`,
`enableFunction`, `timerTechnology`, `logicFamily`.
