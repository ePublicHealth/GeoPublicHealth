#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight runner for GeoPublicHealth Processing tests.

Requires a QGIS Python environment with processing available.
"""

import os
import sys
import tempfile
import types


def _fail(message):
    sys.stderr.write(message + "\n")
    return 1


def _load_yaml(path):
    try:
        import yaml
    except ImportError:
        return None, "PyYAML is required to run processing tests."

    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle), None


def _resolve_path(base_dir, entry):
    return os.path.normpath(os.path.join(base_dir, entry))


def _load_layer(path):
    from qgis.core import QgsVectorLayer

    layer = QgsVectorLayer(path, os.path.basename(path), "ogr")
    return layer if layer.isValid() else None


def _compare_vector_layers(expected_path, actual_path):
    expected = _load_layer(expected_path)
    actual = _load_layer(actual_path)

    if not expected:
        return False, f"Expected layer invalid: {expected_path}"
    if not actual:
        return False, f"Actual layer invalid: {actual_path}"

    if expected.featureCount() != actual.featureCount():
        return False, "Feature count mismatch"

    if expected.geometryType() != actual.geometryType():
        return False, "Geometry type mismatch"

    exp_extent = expected.extent()
    act_extent = actual.extent()
    if exp_extent != act_extent:
        return False, "Extent mismatch"

    return True, "ok"


def _register_provider():
    plugin_path = os.environ.get("GPH_PLUGIN_PATH")
    if plugin_path:
        sys.path.insert(0, plugin_path)
        if os.path.basename(plugin_path) == "geopublichealth":
            parent = os.path.dirname(plugin_path)
            sys.path.insert(0, parent)

        if "geopublichealth" not in sys.modules:
            stub = types.ModuleType("geopublichealth")
            stub.__path__ = [plugin_path]
            stub.__file__ = os.path.join(plugin_path, "__init__.py")
            sys.modules["geopublichealth"] = stub

    provider_class = None
    try:
        from geopublichealth.src.processing_geopublichealth.provider import Provider

        provider_class = Provider
    except ImportError:
        try:
            from src.processing_geopublichealth.provider import Provider

            provider_class = Provider
        except ImportError as exc:
            sys.stderr.write(
                f"Provider import failed. Plugin path: {plugin_path} ({exc})\n"
            )
            return

    try:
        from qgis.core import QgsApplication
    except ImportError:
        return

    registry = QgsApplication.processingRegistry()
    existing = registry.providerById("GeoPublicHealth")
    if existing:
        return

    provider = provider_class()
    try:
        provider.loadAlgorithms()
    except Exception:
        pass

    added = registry.addProvider(provider)
    if not added:
        raise RuntimeError("Failed to register GeoPublicHealth provider")


def main():
    try:
        from qgis.testing import start_app
    except ImportError:
        return _fail("QGIS Python environment not available.")

    start_app()

    try:
        _register_provider()
    except Exception as exc:
        sys.stderr.write(f"Provider registration warning: {exc}\n")

    try:
        import processing
    except ImportError:
        return _fail("Processing framework not available in QGIS environment.")

    try:
        from qgis.core import QgsApplication

        registry = QgsApplication.processingRegistry()
        provider = registry.providerById("GeoPublicHealth")
        if provider:
            alg_ids = []
            for alg in provider.algorithms():
                try:
                    alg_ids.append(
                        f"{alg.id()} (name={alg.name()}, provider={getattr(alg.provider(), 'id', lambda: None)() if alg.provider() else None})"
                    )
                except Exception:
                    alg_ids.append("<error>")
            sys.stdout.write(
                "Registered GeoPublicHealth algorithms (%d): %s\n"
                % (len(alg_ids), ", ".join(alg_ids))
            )
        else:
            sys.stderr.write("GeoPublicHealth provider not registered.\n")
    except Exception:
        pass

    try:
        from src.processing_geopublichealth.blurring import BlurringGeoAlgorithm

        alg = BlurringGeoAlgorithm()
        sys.stdout.write(
            f"BlurringGeoAlgorithm name: {alg.name()} displayName: {alg.displayName()}\n"
        )
    except Exception as exc:
        sys.stderr.write(f"Direct algorithm import failed: {exc}\n")

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    testdata_dir = os.path.join(
        repo_root,
        "src",
        "processing_geopublichealth",
        "testdata",
    )
    yaml_path = os.path.join(testdata_dir, "algorithm_tests.yaml")

    data, error = _load_yaml(yaml_path)
    if error:
        return _fail(error)

    tests = data.get("tests", []) if isinstance(data, dict) else []
    if not tests:
        return _fail("No tests found in algorithm_tests.yaml")

    failures = 0
    for test in tests:
        name = test.get("name", "<unnamed>")
        algorithm = test.get("algorithm")
        params = test.get("params", {})
        results = test.get("results", {})

        if not algorithm:
            sys.stderr.write(f"[{name}] Missing algorithm id\n")
            failures += 1
            continue

        resolved_params = {}
        for key, value in params.items():
            if isinstance(value, dict) and value.get("type") in ("vector", "file"):
                resolved_params[key] = _resolve_path(testdata_dir, value["name"])
            else:
                resolved_params[key] = value

        output_dir = tempfile.mkdtemp(prefix="gph_processing_")
        for output_key, output_spec in results.items():
            if not isinstance(output_spec, dict):
                continue
            name_value = output_spec.get("name")
            if name_value:
                resolved_params[output_key] = os.path.join(
                    output_dir,
                    os.path.basename(name_value),
                )

        try:
            algo_to_run = algorithm
            try:
                from qgis.core import QgsApplication

                registry = QgsApplication.processingRegistry()
                if registry.algorithmById(algorithm) is None:
                    if algorithm.endswith(":geopublichealth_blurring"):
                        from src.processing_geopublichealth.blurring import (
                            BlurringGeoAlgorithm,
                        )

                        algo_to_run = BlurringGeoAlgorithm()
            except Exception:
                pass

            processing.run(algo_to_run, resolved_params)
        except Exception as exc:
            sys.stderr.write(f"[{name}] Failed to run: {exc}\n")
            failures += 1
            continue

        for output_key, output_spec in results.items():
            if not isinstance(output_spec, dict):
                continue
            output_type = output_spec.get("type")
            expected_name = output_spec.get("name")
            if not expected_name:
                continue
            expected_path = _resolve_path(testdata_dir, expected_name)
            actual_path = resolved_params.get(output_key)

            if output_type == "vector":
                ok, reason = _compare_vector_layers(expected_path, actual_path)
            else:
                ok, reason = False, f"Unsupported output type: {output_type}"

            if not ok:
                sys.stderr.write(f"[{name}] {output_key} failed: {reason}\n")
                failures += 1

    if failures:
        return _fail(f"Processing tests failed: {failures}")

    sys.stdout.write("Processing tests passed\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
