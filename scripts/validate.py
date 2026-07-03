#!/usr/bin/env python3
"""Validate TDAS schemas + examples against the PSMA cross-repo registry.

Three gates:
  1. every TDAS schema meta-validates AND every $ref it contains resolves
     against the cross-repo registry (catches dangling refs);
  2. each examples/*.json validates against tdas.json;
  3. each example is also a valid PEAS document (the `timeBase` branch).

NOTE: gate 3: PEAS citizenship (PEAS has the `timeBase` branch; a skip is a FAILURE).
not something to silence.
"""
import json
import glob
import os
import sys

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PSMA = os.path.dirname(HERE)


def load_all():
    resources = []
    for repo in ("PEAS", "MAS", "CAS", "SAS", "RAS", "CONAS", "CTAS", "AAS", "TDAS", "TAS", "CIAS", "COAS"):
        pat = os.path.join(PSMA, repo, "schemas", "**", "*.json")
        for f in glob.glob(pat, recursive=True):
            try:
                doc = json.load(open(f))
            except (json.JSONDecodeError, OSError):
                continue
            if "$id" in doc:
                resources.append((doc["$id"], Resource.from_contents(doc)))
    return Registry().with_resources(resources)


def iter_refs(node):
    """Yield every $ref string anywhere in a schema document."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "$ref" and isinstance(v, str):
                yield v
            else:
                yield from iter_refs(v)
    elif isinstance(node, list):
        for item in node:
            yield from iter_refs(item)


def main():
    registry = load_all()
    errors = 0

    # 1. meta-validate + resolve every $ref
    for f in sorted(glob.glob(os.path.join(HERE, "schemas", "**", "*.json"), recursive=True)):
        doc = json.load(open(f))
        rel = os.path.relpath(f, HERE)
        try:
            Draft202012Validator.check_schema(doc)
        except Exception as exc:  # noqa: BLE001
            errors += 1
            print(f"\nMETA-SCHEMA FAIL {rel}: {exc}")
            continue
        base = doc.get("$id")
        resolver = registry.resolver(base_uri=base or "")
        bad = []
        for ref in set(iter_refs(doc)):
            try:
                resolver.lookup(ref)
            except Unresolvable as exc:
                bad.append((ref, str(exc)))
        if bad:
            errors += len(bad)
            print(f"\nUNRESOLVED $ref in {rel}:")
            for ref, msg in bad:
                print(f"    {ref}")
        else:
            print(f"  schema OK: {rel}")

    # 2. examples validate against tdas.json
    tdas = registry.get_or_retrieve("https://psma.com/tdas/tdas.json").value.contents
    validator = Draft202012Validator(tdas, registry=registry)
    for f in sorted(glob.glob(os.path.join(HERE, "examples", "*.json"))):
        inst = json.load(open(f))
        errs = sorted(validator.iter_errors(inst), key=lambda e: list(e.path))
        if errs:
            errors += len(errs)
            print(f"\nFAIL {os.path.basename(f)}:")
            for e in errs[:20]:
                print("   ", list(e.path), "->", e.message)
        else:
            print(f"  example OK: {os.path.basename(f)}")

    # 3. citizenship — each example, wrapped under the PEAS 'timeBase' branch, is a
    #    valid PEAS document ({inputs, timeBase: <bare TDAS component>, outputs}),
    #    exactly as an analog IC nests under 'analog'. This gate passes only once
    #    PEAS/peas.json carries the 'timeBase' branch + designRequirements if/then.
    try:
        peas = registry.get_or_retrieve("https://psma.com/peas/peas.json").value.contents
        peas_validator = Draft202012Validator(peas, registry=registry)
        for f in sorted(glob.glob(os.path.join(HERE, "examples", "*.json"))):
            inst = json.load(open(f))
            component = {k: v for k, v in inst.items() if k not in ("inputs", "outputs")}
            wrapped = {"timeBase": component}
            if "inputs" in inst:
                wrapped["inputs"] = inst["inputs"]
            if "outputs" in inst:
                wrapped["outputs"] = inst["outputs"]
            errs = sorted(peas_validator.iter_errors(wrapped), key=lambda e: list(e.path))
            if errs:
                errors += len(errs)
                print(f"\nCITIZENSHIP FAIL {os.path.basename(f)} (PEAS needs the 'timeBase' branch):")
                for e in errs[:20]:
                    print("   ", list(e.path), "->", e.message)
            else:
                print(f"  citizenship OK (valid PEAS under 'timeBase'): {os.path.basename(f)}")
    except Exception as exc:  # noqa: BLE001
        errors += 1
        print(f"\nFAIL: citizenship gate cannot run (PEAS not resolvable): {exc}")

    print("\n" + ("PASS" if errors == 0 else f"FAIL ({errors} errors)"))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
