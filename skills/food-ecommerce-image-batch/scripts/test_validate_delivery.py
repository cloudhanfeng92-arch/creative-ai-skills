#!/usr/bin/env python3
"""Regression tests for the strict no-placeholder delivery validator."""

from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

from validate_delivery import ASSETS, _canonical_role


def _chunk(kind: bytes, payload: bytes) -> bytes:
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def _write_png(path: Path, width: int, height: int, color_seed: int) -> None:
    color = bytes(((128 + color_seed) % 256, (64 + color_seed * 3) % 256, (32 + color_seed * 7) % 256))
    scanline = b"\x00" + color * width
    pixels = scanline * height
    payload = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _chunk(b"IDAT", zlib.compress(pixels))
        + _chunk(b"IEND", b"")
    )
    path.write_bytes(payload)


def _valid_manifest() -> dict[str, object]:
    substitution_slots = {5, 7, 9, 10, 11}
    assets: list[dict[str, object]] = []
    for slot, asset in enumerate(ASSETS):
        substituted = slot in substitution_slots
        role = _canonical_role(asset.filename)
        package_presence = "required" if slot in {0, 2, 9} else "optional" if slot == 11 else "omit"
        package_visible = package_presence != "omit"
        input_ref = "image_1" if slot in {0, 2, 9, 11} else "image_2"
        input_role = "PACK_FRONT" if input_ref == "image_1" else "FOOD_REAL"
        source_ref: dict[str, object] = {"ref": input_ref, "role": input_role}
        if input_role == "FOOD_REAL":
            source_ref["evidence_coverage"] = [
                "whole",
                "surface",
                "scale",
                "prepared_state",
            ]
        source_refs: list[dict[str, object]] = [source_ref]
        if slot == 2:
            source_refs.append(
                {
                    "ref": "image_2",
                    "role": "FOOD_REAL",
                    "evidence_coverage": ["whole", "surface", "scale", "prepared_state"],
                }
            )
        record: dict[str, object] = {
            "id": f"SET_01-{slot:02d}",
            "set_id": "SET_01",
            "role": role,
            "aspect_ratio": "1:1" if asset.ratio == 1.0 else "3:4",
            "source_refs": source_refs,
            "status": "qa_pass",
            "publishable": True,
            "content_mode": "evidence_safe_substitution" if substituted else "standard",
            "evidence_mode": (
                ["visible_evidence", "category_context", "auto_role_substitution"]
                if substituted
                else ["direct_input"]
            ),
            "original_role": role,
            "delivered_role": f"safe_{role}" if substituted else role,
            "substitution_reason": "缺少精确商品事实，改用可见证据完成同一消费者问题" if substituted else None,
            "evidence_keys": [f"evidence_{slot:02d}"],
            "evidence_axis": f"slot {slot:02d} 独立证据轴",
            "shot_delta": f"slot {slot:02d} 独立镜头变化",
            "visual_lead": "package" if slot in {0, 2, 9} else "layout" if slot == 11 else "food",
            "package_presence": package_presence,
            "package_visible": package_visible,
            "package_presence_reason": "本槽位需要商品识别" if package_visible else "本槽位由其他视觉主角完成",
            "package_variant": "outer" if package_visible else "none",
            "package_scale_role": "hero" if slot == 0 else "anchor" if package_visible else "none",
            "integration_plan": "匹配透视、光向、接触阴影、色温和景深" if package_visible else "not_applicable",
            "headline": None if slot == 0 else f"示例标题{slot:02d}",
            "subline": None if slot == 0 else f"与当前视觉证据对应的解释文字{slot:02d}",
            "typography_direction": None if slot == 0 else "modern-bold",
            "detail_layout": f"detail_module_{slot:02d}" if slot >= 6 else None,
            "output_path": f"SET_01/{asset.filename}",
        }
        if substituted and slot != 11:
            record["research_sources"] = ["WEB_CAT_01"]
        assets.append(record)
    assets[11]["evidence_mode"] = [
        "exact_sku_web",
        "visible_evidence",
        "auto_role_substitution",
    ]
    assets[11]["research_sources"] = ["WEB_01"]
    return {
        "execution_mode": "render",
        "research_status": "completed",
        "exact_sku_status": "verified",
        "platform_scope": "generic_ecommerce",
        "research_queries": ["示例品牌 示例食品 100克"],
        "input_refs": [
            {"id": "image_1", "roles": ["PACK_FRONT"]},
            {
                "id": "image_2",
                "roles": ["FOOD_REAL"],
                "evidence_coverage": ["whole", "surface", "scale", "prepared_state"],
            },
        ],
        "research_sources": [
            {
                "id": "WEB_01",
                "url": "https://example.com/official-product",
                "title": "示例品牌官方商品页",
                "retrieved_at": "2026-09-06",
                "source_tier": "official_brand",
                "source_authority": "example_brand",
                "exact_sku_match": True,
                "identity_anchors": ["brand", "product_name", "net_weight"],
                "evidence_excerpt": "品牌、品名与规格字段位于商品页信息区",
                "allowed_uses": ["specs", "visual_evidence", "copy"],
            },
            {
                "id": "WEB_CAT_01",
                "url": "https://example.com/category-research",
                "title": "食品电商视觉研究",
                "retrieved_at": "2026-09-06",
                "source_tier": "category_page",
                "exact_sku_match": False,
                "identity_anchors": [],
                "allowed_uses": ["visual_strategy", "scene_context"],
            },
            {
                "id": "WEB_RULE_01",
                "url": "https://example.gov/ecommerce-advertising-rule",
                "title": "通用电商广告规则",
                "retrieved_at": "2026-09-06",
                "source_tier": "regulator",
                "exact_sku_match": False,
                "identity_anchors": [],
                "allowed_uses": ["platform_compliance"],
            },
        ],
        "facts": [
            {
                "key": f"evidence_{slot:02d}",
                "fact_domain": "product_identity" if slot == 11 else "visible_form",
                "value": f"与槽位 {slot:02d} 对应的真实可见证据",
                "status": "verified_web" if slot == 11 else "confirmed",
                "source_refs": (
                    ["WEB_01"]
                    if slot == 11
                    else ["image_1", "image_2"]
                    if slot == 2
                    else ["image_1" if slot in {0, 9} else "image_2"]
                ),
                "allowed_uses": ["visual_evidence", "copy"],
            }
            for slot in range(len(ASSETS))
        ],
        "assets": assets,
    }


def _run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("validate_delivery.py")),
            str(root),
            "--sets",
            "1",
            "--strict-manifest",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="food-ecommerce-validator-") as temp_dir:
        root = Path(temp_dir)
        set_dir = root / "SET_01"
        set_dir.mkdir()
        for slot, asset in enumerate(ASSETS):
            width, height = (4, 4) if asset.ratio == 1.0 else (3, 4)
            _write_png(set_dir / asset.filename, width, height, slot)

        manifest = _valid_manifest()
        manifest_path = root / "manifest.json"

        def assert_rejected(
            payload: dict[str, object], marker: str, failure_message: str
        ) -> None:
            manifest_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            result = _run_validator(root)
            if result.returncode == 0 or marker not in result.stdout:
                print(result.stdout, file=sys.stderr)
                print(result.stderr, file=sys.stderr)
                raise AssertionError(failure_message)

        def assert_accepted(payload: dict[str, object], failure_message: str) -> None:
            manifest_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            result = _run_validator(root)
            if result.returncode != 0:
                print(result.stdout, file=sys.stderr)
                print(result.stderr, file=sys.stderr)
                raise AssertionError(failure_message)

        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        passing = _run_validator(root)
        if passing.returncode != 0:
            print(passing.stdout, file=sys.stderr)
            print(passing.stderr, file=sys.stderr)
            raise AssertionError("valid no-placeholder delivery should pass")

        manifest_assets = manifest["assets"]
        assert isinstance(manifest_assets, list)
        first_asset = manifest_assets[0]
        assert isinstance(first_asset, dict)
        first_asset["status"] = "data_pending"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        blocked = _run_validator(root)
        if blocked.returncode == 0 or "removed pending status data_pending" not in blocked.stdout:
            print(blocked.stdout, file=sys.stderr)
            print(blocked.stderr, file=sys.stderr)
            raise AssertionError("legacy pending status should fail strict validation")

        first_asset["status"] = "qa_pass"
        second_asset = manifest_assets[1]
        assert isinstance(second_asset, dict)
        second_asset["shot_delta"] = first_asset["shot_delta"]
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        duplicate = _run_validator(root)
        if duplicate.returncode == 0 or "duplicates shot_delta" not in duplicate.stdout:
            print(duplicate.stdout, file=sys.stderr)
            print(duplicate.stderr, file=sys.stderr)
            raise AssertionError("duplicate shot_delta should fail strict validation")

        second_asset["shot_delta"] = "slot 01 独立镜头变化"
        manifest_facts = manifest["facts"]
        assert isinstance(manifest_facts, list)
        web_fact = manifest_facts[11]
        assert isinstance(web_fact, dict)
        web_fact["fact_domain"] = "ingredient"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        unsafe_fact = _run_validator(root)
        if unsafe_fact.returncode == 0 or "high-risk web fact requires two" not in unsafe_fact.stdout:
            print(unsafe_fact.stdout, file=sys.stderr)
            print(unsafe_fact.stderr, file=sys.stderr)
            raise AssertionError("single-source high-risk web fact should fail strict validation")

        wrong_source = _valid_manifest()
        wrong_assets = wrong_source["assets"]
        assert isinstance(wrong_assets, list)
        wrong_asset = wrong_assets[11]
        assert isinstance(wrong_asset, dict)
        wrong_asset["research_sources"] = ["WEB_CAT_01"]
        assert_rejected(
            wrong_source,
            "exact_sku_web requires at least one exact-SKU research source",
            "category source must not satisfy exact_sku_web",
        )

        mixed_sources = _valid_manifest()
        mixed_assets = mixed_sources["assets"]
        assert isinstance(mixed_assets, list)
        mixed_asset = mixed_assets[11]
        assert isinstance(mixed_asset, dict)
        mixed_asset["research_sources"] = ["WEB_01", "WEB_CAT_01"]
        assert_accepted(
            mixed_sources,
            "asset should allow an exact-SKU fact source together with a category design source",
        )

        duplicate_url = _valid_manifest()
        duplicate_sources = duplicate_url["research_sources"]
        assert isinstance(duplicate_sources, list)
        second_exact = dict(duplicate_sources[0])
        second_exact["id"] = "WEB_02"
        second_exact["url"] = "https://example.com/official-product#different-section"
        duplicate_sources.append(second_exact)
        duplicate_facts = duplicate_url["facts"]
        assert isinstance(duplicate_facts, list)
        duplicate_fact = duplicate_facts[11]
        assert isinstance(duplicate_fact, dict)
        duplicate_fact["fact_domain"] = "ingredient"
        duplicate_fact["source_refs"] = ["WEB_01", "WEB_02"]
        assert_rejected(
            duplicate_url,
            "duplicates URL",
            "duplicate URLs must not satisfy two-source confirmation",
        )

        tracking_variants = _valid_manifest()
        tracking_sources = tracking_variants["research_sources"]
        tracking_facts = tracking_variants["facts"]
        assert isinstance(tracking_sources, list)
        assert isinstance(tracking_facts, list)
        first_tracking_source = tracking_sources[0]
        assert isinstance(first_tracking_source, dict)
        first_tracking_source["url"] = (
            "https://example.com/official-product?utm_source=a&srsltid=one"
        )
        second_tracking_source = dict(first_tracking_source)
        second_tracking_source["id"] = "WEB_02"
        second_tracking_source["url"] = (
            "https://example.com:443/official-product?utm_source=b&srsltid=two#different-section"
        )
        second_tracking_source["source_tier"] = "regulator"
        second_tracking_source["source_authority"] = "example_regulator"
        tracking_sources.append(second_tracking_source)
        tracking_fact = tracking_facts[11]
        assert isinstance(tracking_fact, dict)
        tracking_fact["fact_domain"] = "ingredient"
        tracking_fact["source_refs"] = ["WEB_01", "WEB_02"]
        assert_rejected(
            tracking_variants,
            "duplicates URL",
            "tracking parameters and default ports must not create a second source",
        )

        case_sensitive_paths = _valid_manifest()
        case_sources = case_sensitive_paths["research_sources"]
        case_facts = case_sensitive_paths["facts"]
        case_assets = case_sensitive_paths["assets"]
        assert isinstance(case_sources, list)
        assert isinstance(case_facts, list)
        assert isinstance(case_assets, list)
        case_second_exact = dict(case_sources[0])
        case_second_exact["id"] = "WEB_02"
        case_second_exact["url"] = "https://example.com/Official-Product"
        case_second_exact["source_tier"] = "regulator"
        case_second_exact["source_authority"] = "example_regulator"
        case_sources.append(case_second_exact)
        case_fact = case_facts[11]
        case_asset = case_assets[11]
        assert isinstance(case_fact, dict)
        assert isinstance(case_asset, dict)
        case_fact["fact_domain"] = "ingredient"
        case_fact["source_refs"] = ["WEB_01", "WEB_02"]
        case_asset["research_sources"] = ["WEB_01", "WEB_02", "WEB_CAT_01"]
        assert_accepted(
            case_sensitive_paths,
            "URL paths with different case must remain distinct",
        )

        observable_claim = _valid_manifest()
        observable_assets = observable_claim["assets"]
        observable_facts = observable_claim["facts"]
        assert isinstance(observable_assets, list)
        assert isinstance(observable_facts, list)
        observable_asset = observable_assets[11]
        observable_fact = observable_facts[11]
        assert isinstance(observable_asset, dict)
        assert isinstance(observable_fact, dict)
        observable_asset["evidence_mode"] = ["visible_evidence", "auto_role_substitution"]
        observable_asset["research_sources"] = []
        observable_fact["fact_domain"] = "health_claim"
        observable_fact["status"] = "observable"
        observable_fact["source_refs"] = ["image_1"]
        assert_rejected(
            observable_claim,
            "high-risk domain cannot use observable status",
            "observable status must not support a health claim",
        )

        missing_publishable = _valid_manifest()
        missing_publishable_assets = missing_publishable["assets"]
        assert isinstance(missing_publishable_assets, list)
        missing_publishable_asset = missing_publishable_assets[0]
        assert isinstance(missing_publishable_asset, dict)
        del missing_publishable_asset["publishable"]
        assert_rejected(
            missing_publishable,
            "missing boolean publishable",
            "publishable must be a required boolean",
        )

        malformed_research = _valid_manifest()
        malformed_research["research_status"] = []
        assert_rejected(
            malformed_research,
            "invalid or missing research_status",
            "malformed research status should be reported without crashing",
        )
        malformed_fact = _valid_manifest()
        malformed_facts = malformed_fact["facts"]
        assert isinstance(malformed_facts, list)
        malformed_fact_record = malformed_facts[0]
        assert isinstance(malformed_fact_record, dict)
        malformed_fact_record["status"] = []
        assert_rejected(
            malformed_fact,
            "has invalid status []",
            "malformed fact status should be reported without crashing",
        )
        malformed_asset = _valid_manifest()
        malformed_assets = malformed_asset["assets"]
        assert isinstance(malformed_assets, list)
        malformed_asset_record = malformed_assets[0]
        assert isinstance(malformed_asset_record, dict)
        malformed_asset_record["status"] = []
        assert_rejected(
            malformed_asset,
            "has invalid status []",
            "malformed asset status should be reported without crashing",
        )

        invalid_domain = _valid_manifest()
        invalid_domain_facts = invalid_domain["facts"]
        assert isinstance(invalid_domain_facts, list)
        invalid_domain_fact = invalid_domain_facts[11]
        assert isinstance(invalid_domain_fact, dict)
        invalid_domain_fact["fact_domain"] = "ingredients"
        assert_rejected(
            invalid_domain,
            "invalid or missing fact_domain",
            "fact-domain aliases must not bypass high-risk rules",
        )

        invalid_url = _valid_manifest()
        invalid_url_sources = invalid_url["research_sources"]
        assert isinstance(invalid_url_sources, list)
        invalid_url_source = invalid_url_sources[0]
        assert isinstance(invalid_url_source, dict)
        invalid_url_source["url"] = "not a url"
        assert_rejected(
            invalid_url,
            "needs a valid HTTP(S) url",
            "research sources must use valid direct URLs",
        )

        empty_detail = _valid_manifest()
        empty_detail_assets = empty_detail["assets"]
        assert isinstance(empty_detail_assets, list)
        empty_detail_asset = empty_detail_assets[6]
        assert isinstance(empty_detail_asset, dict)
        empty_detail_asset["subline"] = None
        empty_detail_asset["detail_layers"] = [None]
        assert_rejected(
            empty_detail,
            "detail module needs at least 8 meaningful explanation characters",
            "null-only detail layers must not count as complete content",
        )

        untrusted_platform_rule = _valid_manifest()
        untrusted_sources = untrusted_platform_rule["research_sources"]
        assert isinstance(untrusted_sources, list)
        untrusted_source = untrusted_sources[2]
        assert isinstance(untrusted_source, dict)
        untrusted_source["source_tier"] = "ugc"
        assert_rejected(
            untrusted_platform_rule,
            "requires an official platform/regulatory compliance source",
            "UGC must not satisfy platform compliance research",
        )

        missing_sources_field = _valid_manifest()
        del missing_sources_field["research_sources"]
        assert_rejected(
            missing_sources_field,
            "research_sources must be a list",
            "research_sources must remain explicit even when empty",
        )

        wrong_asset_metadata = _valid_manifest()
        wrong_metadata_assets = wrong_asset_metadata["assets"]
        assert isinstance(wrong_metadata_assets, list)
        wrong_metadata_asset = wrong_metadata_assets[0]
        assert isinstance(wrong_metadata_asset, dict)
        wrong_metadata_asset["set_id"] = "SET_99"
        wrong_metadata_asset["role"] = "anything"
        wrong_metadata_asset["aspect_ratio"] = "9:16"
        assert_rejected(
            wrong_asset_metadata,
            "set_id must be 'SET_01'",
            "asset identity metadata must match its fixed slot",
        )

        duplicate_axis = _valid_manifest()
        duplicate_axis_assets = duplicate_axis["assets"]
        assert isinstance(duplicate_axis_assets, list)
        first_axis_asset = duplicate_axis_assets[0]
        second_axis_asset = duplicate_axis_assets[1]
        assert isinstance(first_axis_asset, dict)
        assert isinstance(second_axis_asset, dict)
        second_axis_asset["evidence_axis"] = first_axis_asset["evidence_axis"]
        assert_rejected(
            duplicate_axis,
            "duplicates evidence_axis",
            "each asset needs a distinct evidence axis",
        )

        ungrounded_inner = _valid_manifest()
        inner_assets = ungrounded_inner["assets"]
        assert isinstance(inner_assets, list)
        inner_asset = inner_assets[1]
        assert isinstance(inner_asset, dict)
        inner_asset["package_presence"] = "optional"
        inner_asset["package_visible"] = True
        inner_asset["package_variant"] = "inner"
        inner_asset["package_scale_role"] = "secondary"
        inner_asset["integration_plan"] = "匹配场景光线与阴影"
        assert_rejected(
            ungrounded_inner,
            "inner package requires a PACK_INNER source_ref",
            "inner packaging must be grounded in a real reference",
        )

        polluted_confirmed = _valid_manifest()
        polluted_facts = polluted_confirmed["facts"]
        assert isinstance(polluted_facts, list)
        polluted_fact = polluted_facts[0]
        assert isinstance(polluted_fact, dict)
        polluted_fact["source_refs"] = ["WEB_CAT_01", "image_does_not_exist"]
        assert_rejected(
            polluted_confirmed,
            "must cite a declared input_ref",
            "category web research must not become a confirmed product fact",
        )

        disallowed_fact_use = _valid_manifest()
        disallowed_sources = disallowed_fact_use["research_sources"]
        assert isinstance(disallowed_sources, list)
        disallowed_source = disallowed_sources[0]
        assert isinstance(disallowed_source, dict)
        disallowed_source["allowed_uses"] = ["specs"]
        assert_rejected(
            disallowed_fact_use,
            "uses must be allowed by every cited web source",
            "web facts must stay within source-level allowed uses",
        )

        malformed_evidence_keys = _valid_manifest()
        malformed_key_assets = malformed_evidence_keys["assets"]
        assert isinstance(malformed_key_assets, list)
        malformed_key_asset = malformed_key_assets[0]
        assert isinstance(malformed_key_asset, dict)
        malformed_key_asset["evidence_keys"] = ["evidence_00", {"fake": "key"}]
        assert_rejected(
            malformed_evidence_keys,
            "needs string evidence_keys",
            "non-string evidence keys must not be ignored",
        )

        wrong_role_mode = _valid_manifest()
        wrong_role_assets = wrong_role_mode["assets"]
        assert isinstance(wrong_role_assets, list)
        wrong_role_asset = wrong_role_assets[1]
        assert isinstance(wrong_role_asset, dict)
        wrong_role_asset["delivered_role"] = "silent_role_change"
        assert_rejected(
            wrong_role_mode,
            "standard content must keep the canonical delivered_role",
            "standard content must not silently change roles",
        )

        placeholder_copy = _valid_manifest()
        placeholder_assets = placeholder_copy["assets"]
        assert isinstance(placeholder_assets, list)
        placeholder_asset = placeholder_assets[1]
        assert isinstance(placeholder_asset, dict)
        placeholder_asset["headline"] = "资料待补"
        placeholder_asset["subline"] = "不可发布"
        assert_rejected(
            placeholder_copy,
            "user-visible copy contains forbidden placeholder term",
            "placeholder copy must never pass strict delivery validation",
        )

        style_only_fact = _valid_manifest()
        style_inputs = style_only_fact["input_refs"]
        style_facts = style_only_fact["facts"]
        assert isinstance(style_inputs, list)
        assert isinstance(style_facts, list)
        style_inputs.append({"id": "style_1", "roles": ["STYLE_ONLY"]})
        style_fact = style_facts[0]
        assert isinstance(style_fact, dict)
        style_fact["source_refs"] = ["style_1"]
        assert_rejected(
            style_only_fact,
            "cannot cite STYLE_ONLY inputs",
            "STYLE_ONLY material must not prove a product fact",
        )

        ungrounded_outer = _valid_manifest()
        outer_assets = ungrounded_outer["assets"]
        assert isinstance(outer_assets, list)
        outer_asset = outer_assets[0]
        assert isinstance(outer_asset, dict)
        outer_asset["source_refs"] = [{"ref": "image_2", "role": "FOOD_REAL"}]
        assert_rejected(
            ungrounded_outer,
            "white-background packshot requires a PACK_FRONT source_ref",
            "visible outer packaging must use a real package anchor",
        )

        missing_category_research = _valid_manifest()
        category_sources = missing_category_research["research_sources"]
        category_assets = missing_category_research["assets"]
        assert isinstance(category_sources, list)
        assert isinstance(category_assets, list)
        category_sources[:] = [source for source in category_sources if source.get("id") != "WEB_CAT_01"]
        for category_asset in category_assets:
            assert isinstance(category_asset, dict)
            modes = category_asset.get("evidence_mode")
            if isinstance(modes, list) and "category_context" in modes:
                category_asset["evidence_mode"] = [mode for mode in modes if mode != "category_context"]
                category_asset["research_sources"] = []
        assert_rejected(
            missing_category_research,
            "completed research requires a non-SKU design/context source",
            "compliance research alone must not replace category design research",
        )

        mismatched_exact_fact = _valid_manifest()
        mismatch_sources = mismatched_exact_fact["research_sources"]
        mismatch_facts = mismatched_exact_fact["facts"]
        assert isinstance(mismatch_sources, list)
        assert isinstance(mismatch_facts, list)
        mismatch_second_source = dict(mismatch_sources[0])
        mismatch_second_source["id"] = "WEB_02"
        mismatch_second_source["url"] = "https://regulator.example/verified-product"
        mismatch_second_source["source_tier"] = "regulator"
        mismatch_second_source["source_authority"] = "example_regulator"
        mismatch_sources.append(mismatch_second_source)
        mismatch_fact = mismatch_facts[11]
        assert isinstance(mismatch_fact, dict)
        mismatch_fact["source_refs"] = ["WEB_02"]
        assert_rejected(
            mismatched_exact_fact,
            "omits verified fact sources",
            "an asset must list the exact sources used by its verified fact keys",
        )

        split_permissions = _valid_manifest()
        split_sources = split_permissions["research_sources"]
        split_facts = split_permissions["facts"]
        split_assets = split_permissions["assets"]
        assert isinstance(split_sources, list)
        assert isinstance(split_facts, list)
        assert isinstance(split_assets, list)
        first_split_source = split_sources[0]
        assert isinstance(first_split_source, dict)
        first_split_source["allowed_uses"] = ["visual_evidence"]
        second_split_source = dict(first_split_source)
        second_split_source["id"] = "WEB_02"
        second_split_source["url"] = "https://regulator.example/verified-product"
        second_split_source["source_tier"] = "regulator"
        second_split_source["source_authority"] = "example_regulator"
        second_split_source["allowed_uses"] = ["copy"]
        split_sources.append(second_split_source)
        split_fact = split_facts[11]
        split_asset = split_assets[11]
        assert isinstance(split_fact, dict)
        assert isinstance(split_asset, dict)
        split_fact["fact_domain"] = "ingredient"
        split_fact["source_refs"] = ["WEB_01", "WEB_02"]
        split_fact["allowed_uses"] = ["visual_evidence", "copy"]
        split_asset["research_sources"] = ["WEB_01", "WEB_02"]
        assert_rejected(
            split_permissions,
            "uses must be allowed by every cited web source",
            "source permissions must not be combined as a permissive union",
        )

        malformed_source_tiers = _valid_manifest()
        malformed_tier_sources = malformed_source_tiers["research_sources"]
        assert isinstance(malformed_tier_sources, list)
        malformed_tier_sources[0]["source_tier"] = []
        malformed_tier_sources[2]["source_tier"] = {}
        assert_rejected(
            malformed_source_tiers,
            "has invalid source_tier",
            "container-valued source tiers must be rejected without crashing",
        )

        invalid_port = _valid_manifest()
        invalid_port_sources = invalid_port["research_sources"]
        assert isinstance(invalid_port_sources, list)
        invalid_port_sources[0]["url"] = "https://example.com:notaport/official-product"
        assert_rejected(
            invalid_port,
            "needs a valid HTTP(S) url",
            "non-numeric URL ports must be rejected",
        )

        invalid_hostname = _valid_manifest()
        invalid_hostname_sources = invalid_hostname["research_sources"]
        assert isinstance(invalid_hostname_sources, list)
        invalid_hostname_sources[0]["url"] = "https://exa mple.com/official-product"
        assert_rejected(
            invalid_hostname,
            "needs a valid HTTP(S) url",
            "whitespace in a URL hostname must be rejected",
        )

        msclkid_variants = _valid_manifest()
        msclkid_sources = msclkid_variants["research_sources"]
        msclkid_facts = msclkid_variants["facts"]
        msclkid_assets = msclkid_variants["assets"]
        assert isinstance(msclkid_sources, list)
        assert isinstance(msclkid_facts, list)
        assert isinstance(msclkid_assets, list)
        msclkid_sources[0]["url"] = "https://example.com/product?msclkid=alpha"
        second_msclkid_source = dict(msclkid_sources[0])
        second_msclkid_source["id"] = "WEB_02"
        second_msclkid_source["url"] = "https://example.com/product?msclkid=beta"
        second_msclkid_source["source_tier"] = "regulator"
        second_msclkid_source["source_authority"] = "example_regulator"
        msclkid_sources.append(second_msclkid_source)
        msclkid_fact = msclkid_facts[11]
        msclkid_asset = msclkid_assets[11]
        assert isinstance(msclkid_fact, dict)
        assert isinstance(msclkid_asset, dict)
        msclkid_fact["fact_domain"] = "ingredient"
        msclkid_fact["source_refs"] = ["WEB_01", "WEB_02"]
        msclkid_asset["research_sources"] = ["WEB_01", "WEB_02"]
        assert_rejected(
            msclkid_variants,
            "duplicates URL",
            "msclkid variants of one page must not count as independent sources",
        )

        same_authority_alias = _valid_manifest()
        authority_sources = same_authority_alias["research_sources"]
        authority_facts = same_authority_alias["facts"]
        authority_assets = same_authority_alias["assets"]
        assert isinstance(authority_sources, list)
        assert isinstance(authority_facts, list)
        assert isinstance(authority_assets, list)
        authority_sources[0]["source_authority"] = "Example Brand"
        second_authority_source = dict(authority_sources[0])
        second_authority_source["id"] = "WEB_02"
        second_authority_source["url"] = "https://store.example.net/product"
        second_authority_source["source_tier"] = "official_store"
        second_authority_source["source_authority"] = "Example Brand Official Store"
        authority_sources.append(second_authority_source)
        authority_fact = authority_facts[11]
        authority_asset = authority_assets[11]
        assert isinstance(authority_fact, dict)
        assert isinstance(authority_asset, dict)
        authority_fact["fact_domain"] = "ingredient"
        authority_fact["source_refs"] = ["WEB_01", "WEB_02"]
        authority_asset["research_sources"] = ["WEB_01", "WEB_02"]
        assert_rejected(
            same_authority_alias,
            "requires two independent source_authorities",
            "official-site and official-store labels for one brand must remain one authority",
        )

        disguised_verified_fact = _valid_manifest()
        disguised_assets = disguised_verified_fact["assets"]
        assert isinstance(disguised_assets, list)
        disguised_asset = disguised_assets[11]
        assert isinstance(disguised_asset, dict)
        disguised_asset["evidence_mode"] = ["visible_evidence", "auto_role_substitution"]
        disguised_asset["research_sources"] = []
        assert_rejected(
            disguised_verified_fact,
            "verified_web evidence requires exact_sku_web evidence_mode",
            "an asset must not disguise a web fact as visible evidence",
        )

        mismatched_input_fact = _valid_manifest()
        mismatched_input_assets = mismatched_input_fact["assets"]
        assert isinstance(mismatched_input_assets, list)
        mismatched_input_asset = mismatched_input_assets[1]
        assert isinstance(mismatched_input_asset, dict)
        mismatched_input_asset["source_refs"] = [{"ref": "image_1", "role": "PACK_FRONT"}]
        assert_rejected(
            mismatched_input_fact,
            "omits input sources for evidence",
            "an asset must cite the exact input that supports its evidence key",
        )

        confirmed_price = _valid_manifest()
        confirmed_price_facts = confirmed_price["facts"]
        assert isinstance(confirmed_price_facts, list)
        confirmed_price_facts.append(
            {
                "key": "user_price_01",
                "fact_domain": "price",
                "value": "用户确认价格",
                "status": "confirmed",
                "source_refs": ["image_1"],
                "allowed_uses": ["specs"],
            }
        )
        assert_accepted(
            confirmed_price,
            "a user-confirmed price fact must be representable in the fact ledger",
        )

        official_serving_method = _valid_manifest()
        serving_method_facts = official_serving_method["facts"]
        assert isinstance(serving_method_facts, list)
        serving_method_fact = serving_method_facts[11]
        assert isinstance(serving_method_fact, dict)
        serving_method_fact["fact_domain"] = "serving_method"
        assert_accepted(
            official_serving_method,
            "one exact official source may support ordinary serving instructions",
        )

        short_headline = _valid_manifest()
        short_headline_assets = short_headline["assets"]
        assert isinstance(short_headline_assets, list)
        short_headline_assets[1]["headline"] = "香"
        assert_rejected(
            short_headline,
            "main headline must contain 4-12 visible characters",
            "one-character main headlines must be rejected",
        )

        short_subline = _valid_manifest()
        short_subline_assets = short_subline["assets"]
        assert isinstance(short_subline_assets, list)
        short_subline_assets[1]["subline"] = "好"
        assert_rejected(
            short_subline,
            "main subline must contain 8-24 visible characters",
            "one-character explanatory copy must be rejected",
        )

        question_mark_spec = _valid_manifest()
        question_mark_assets = question_mark_spec["assets"]
        assert isinstance(question_mark_assets, list)
        question_mark_assets[11]["spec_fields"] = {"净含量": "?"}
        assert_rejected(
            question_mark_spec,
            "spec_fields contain a question-mark placeholder",
            "question marks must not stand in for missing specification values",
        )

        missing_input_coverage = _valid_manifest()
        coverage_inputs = missing_input_coverage["input_refs"]
        assert isinstance(coverage_inputs, list)
        del coverage_inputs[1]["evidence_coverage"]
        assert_rejected(
            missing_input_coverage,
            "FOOD_REAL needs valid non-empty evidence_coverage",
            "each FOOD_REAL input must declare what it actually proves",
        )

        missing_asset_coverage = _valid_manifest()
        coverage_assets = missing_asset_coverage["assets"]
        assert isinstance(coverage_assets, list)
        coverage_source_refs = coverage_assets[1]["source_refs"]
        assert isinstance(coverage_source_refs, list)
        del coverage_source_refs[0]["evidence_coverage"]
        assert_rejected(
            missing_asset_coverage,
            "FOOD_REAL needs valid non-empty evidence_coverage",
            "each asset must declare the FOOD_REAL coverage it actually uses",
        )

        typography_only_research = _valid_manifest()
        typography_sources = typography_only_research["research_sources"]
        assert isinstance(typography_sources, list)
        typography_sources[1]["allowed_uses"] = ["typography"]
        assert_rejected(
            typography_only_research,
            "requires category visual_strategy coverage",
            "typography-only research must not count as complete category and scene research",
        )

        dot_hostname = _valid_manifest()
        dot_hostname_sources = dot_hostname["research_sources"]
        assert isinstance(dot_hostname_sources, list)
        dot_hostname_sources[0]["url"] = "https://."
        assert_rejected(
            dot_hostname,
            "needs a valid HTTP(S) url",
            "a punctuation-only hostname must not count as a valid research URL",
        )

        parenthesized_authority_alias = _valid_manifest()
        parenthesized_sources = parenthesized_authority_alias["research_sources"]
        parenthesized_facts = parenthesized_authority_alias["facts"]
        parenthesized_assets = parenthesized_authority_alias["assets"]
        assert isinstance(parenthesized_sources, list)
        assert isinstance(parenthesized_facts, list)
        assert isinstance(parenthesized_assets, list)
        parenthesized_sources[0]["source_authority"] = "Example Brand"
        parenthesized_second = dict(parenthesized_sources[0])
        parenthesized_second["id"] = "WEB_02"
        parenthesized_second["url"] = "https://store.example.net/second-product-page"
        parenthesized_second["source_tier"] = "official_store"
        parenthesized_second["source_authority"] = "Example Brand（品牌方）"
        parenthesized_sources.append(parenthesized_second)
        parenthesized_fact = parenthesized_facts[11]
        parenthesized_asset = parenthesized_assets[11]
        assert isinstance(parenthesized_fact, dict)
        assert isinstance(parenthesized_asset, dict)
        parenthesized_fact["fact_domain"] = "ingredient"
        parenthesized_fact["source_refs"] = ["WEB_01", "WEB_02"]
        parenthesized_asset["research_sources"] = ["WEB_01", "WEB_02"]
        assert_rejected(
            parenthesized_authority_alias,
            "requires two independent source_authorities",
            "a parenthesized brand-party label must not create a second authority",
        )

        insufficient_food_coverage = _valid_manifest()
        insufficient_coverage_facts = insufficient_food_coverage["facts"]
        insufficient_coverage_assets = insufficient_food_coverage["assets"]
        assert isinstance(insufficient_coverage_facts, list)
        assert isinstance(insufficient_coverage_assets, list)
        insufficient_coverage_fact = insufficient_coverage_facts[1]
        insufficient_coverage_asset = insufficient_coverage_assets[1]
        assert isinstance(insufficient_coverage_fact, dict)
        assert isinstance(insufficient_coverage_asset, dict)
        insufficient_coverage_fact["fact_domain"] = "visible_surface"
        insufficient_coverage_asset["source_refs"][0]["evidence_coverage"] = ["whole"]
        assert_rejected(
            insufficient_food_coverage,
            "needs FOOD_REAL coverage",
            "a whole-food view must not prove unsupported surface detail",
        )

        question_mark_spec_key = _valid_manifest()
        question_mark_key_assets = question_mark_spec_key["assets"]
        assert isinstance(question_mark_key_assets, list)
        question_mark_key_assets[11]["spec_fields"] = {"净含量？": "100克"}
        assert_rejected(
            question_mark_spec_key,
            "spec_fields contain a question-mark placeholder",
            "a question mark in a specification key must also be rejected",
        )

        regulator_only_design = _valid_manifest()
        regulator_design_sources = regulator_only_design["research_sources"]
        assert isinstance(regulator_design_sources, list)
        regulator_design_sources[1]["source_tier"] = "regulator"
        regulator_design_sources[1]["allowed_uses"] = [
            "visual_strategy",
            "scene_context",
            "platform_compliance",
        ]
        assert_rejected(
            regulator_only_design,
            "uses design research fields with a non-design source_tier",
            "a regulatory page alone must not masquerade as category visual research",
        )

        symbol_only_copy = _valid_manifest()
        symbol_only_assets = symbol_only_copy["assets"]
        assert isinstance(symbol_only_assets, list)
        symbol_only_assets[1]["headline"] = "🔥🔥🔥🔥"
        symbol_only_assets[1]["subline"] = "!!!!!!!!"
        assert_rejected(
            symbol_only_copy,
            "main headline must contain 4-12 visible characters",
            "pure symbols must not satisfy main-image copy requirements",
        )

        missing_fact_value = _valid_manifest()
        missing_value_facts = missing_fact_value["facts"]
        assert isinstance(missing_value_facts, list)
        del missing_value_facts[0]["value"]
        assert_rejected(
            missing_fact_value,
            "evidentiary fact needs a meaningful value",
            "an evidence key without an actual fact value must be rejected",
        )

        stray_substitution_mode = _valid_manifest()
        stray_mode_assets = stray_substitution_mode["assets"]
        assert isinstance(stray_mode_assets, list)
        stray_mode_assets[1]["evidence_mode"] = ["direct_input", "auto_role_substitution"]
        assert_rejected(
            stray_substitution_mode,
            "auto_role_substitution is only valid for evidence_safe_substitution",
            "standard content must not carry a hidden substitution mode",
        )

        symbol_only_detail = _valid_manifest()
        symbol_detail_assets = symbol_only_detail["assets"]
        assert isinstance(symbol_detail_assets, list)
        symbol_detail_assets[6]["headline"] = "★★★★"
        assert_rejected(
            symbol_only_detail,
            "detail headline must contain 4-18 meaningful characters",
            "pure symbols must not satisfy detail headline requirements",
        )

        empty_spec_value = _valid_manifest()
        empty_spec_assets = empty_spec_value["assets"]
        assert isinstance(empty_spec_assets, list)
        empty_spec_assets[11]["spec_fields"] = {"净含量": ""}
        assert_rejected(
            empty_spec_value,
            "spec_fields contain an empty label or value",
            "empty specification values must not survive strict validation",
        )

        unsupported_steps = _valid_manifest()
        unsupported_step_assets = unsupported_steps["assets"]
        assert isinstance(unsupported_step_assets, list)
        unsupported_step_assets[10]["steps"] = ["第一步", "第二步"]
        assert_rejected(
            unsupported_steps,
            "numbered steps require serving_method or process evidence",
            "numbered instructions must be backed by a serving or process fact",
        )

        package_only_product_role = _valid_manifest()
        package_only_assets = package_only_product_role["assets"]
        package_only_facts = package_only_product_role["facts"]
        assert isinstance(package_only_assets, list)
        assert isinstance(package_only_facts, list)
        package_only_assets[2]["source_refs"] = [
            {"ref": "image_1", "role": "PACK_FRONT"}
        ]
        package_only_facts[2]["source_refs"] = ["image_1"]
        assert_rejected(
            package_only_product_role,
            "standard role for slot 02 requires a FOOD_REAL source_ref",
            "a package-only image must trigger an honest replacement of product-real role",
        )

        unsupported_standard_ingredient = _valid_manifest()
        standard_ingredient_assets = unsupported_standard_ingredient["assets"]
        assert isinstance(standard_ingredient_assets, list)
        standard_ingredient = standard_ingredient_assets[5]
        standard_ingredient["content_mode"] = "standard"
        standard_ingredient["evidence_mode"] = ["visible_evidence"]
        standard_ingredient["delivered_role"] = standard_ingredient["original_role"]
        standard_ingredient["substitution_reason"] = None
        assert_rejected(
            unsupported_standard_ingredient,
            "standard ingredient role requires confirmed ingredient evidence",
            "slot 05 must be relabeled when ingredient evidence is absent",
        )

        unsupported_standard_difference = _valid_manifest()
        standard_difference_assets = unsupported_standard_difference["assets"]
        assert isinstance(standard_difference_assets, list)
        standard_difference = standard_difference_assets[7]
        standard_difference["content_mode"] = "standard"
        standard_difference["evidence_mode"] = ["visible_evidence"]
        standard_difference["delivered_role"] = standard_difference["original_role"]
        standard_difference["substitution_reason"] = None
        assert_rejected(
            unsupported_standard_difference,
            "standard difference role requires a differentiator evidence use",
            "slot 07 must be relabeled when no confirmed differentiator exists",
        )

        unsupported_standard_angles = _valid_manifest()
        standard_angle_assets = unsupported_standard_angles["assets"]
        assert isinstance(standard_angle_assets, list)
        standard_angles = standard_angle_assets[9]
        standard_angles["content_mode"] = "standard"
        standard_angles["evidence_mode"] = ["direct_input"]
        standard_angles["delivered_role"] = standard_angles["original_role"]
        standard_angles["substitution_reason"] = None
        assert_rejected(
            unsupported_standard_angles,
            "standard multi-angle role requires a PACK_OTHER source_ref",
            "slot 09 must become package details when only a front view exists",
        )

        unsupported_standard_process = _valid_manifest()
        standard_process_assets = unsupported_standard_process["assets"]
        assert isinstance(standard_process_assets, list)
        standard_process = standard_process_assets[10]
        standard_process["content_mode"] = "standard"
        standard_process["evidence_mode"] = ["visible_evidence"]
        standard_process["delivered_role"] = standard_process["original_role"]
        standard_process["substitution_reason"] = None
        assert_rejected(
            unsupported_standard_process,
            "standard process role requires process evidence",
            "slot 10 must be relabeled when process evidence is absent",
        )

        unsupported_standard_specs = _valid_manifest()
        standard_spec_assets = unsupported_standard_specs["assets"]
        assert isinstance(standard_spec_assets, list)
        standard_specs = standard_spec_assets[11]
        standard_specs["content_mode"] = "standard"
        standard_specs["evidence_mode"] = ["exact_sku_web"]
        standard_specs["delivered_role"] = standard_specs["original_role"]
        standard_specs["substitution_reason"] = None
        assert_rejected(
            unsupported_standard_specs,
            "standard specs role requires non-empty spec_fields",
            "slot 11 must become an information overview when specification fields are absent",
        )

        package_claiming_food_surface = _valid_manifest()
        package_surface_assets = package_claiming_food_surface["assets"]
        package_surface_facts = package_claiming_food_surface["facts"]
        assert isinstance(package_surface_assets, list)
        assert isinstance(package_surface_facts, list)
        package_surface_assets[4]["source_refs"] = [
            {"ref": "image_1", "role": "PACK_FRONT"}
        ]
        package_surface_facts[4]["fact_domain"] = "visible_surface"
        package_surface_facts[4]["source_refs"] = ["image_1"]
        assert_rejected(
            package_claiming_food_surface,
            "visible_surface requires a FOOD_REAL input source",
            "packaging alone must not prove the food surface",
        )

        bad_date = _valid_manifest()
        bad_date_sources = bad_date["research_sources"]
        assert isinstance(bad_date_sources, list)
        bad_date_source = bad_date_sources[0]
        assert isinstance(bad_date_source, dict)
        bad_date_source["retrieved_at"] = "not-a-date"
        assert_rejected(
            bad_date,
            "needs retrieved_at YYYY-MM-DD",
            "research access dates must be machine-verifiable",
        )

        named_platform_without_rule = _valid_manifest()
        named_platform_without_rule["platform_scope"] = "Example Marketplace"
        assert_rejected(
            named_platform_without_rule,
            "named platform scope requires an official platform_rule source",
            "a named platform must use its official rule source",
        )

        duplicate_image_manifest = _valid_manifest()
        first_image = set_dir / ASSETS[0].filename
        second_image = set_dir / ASSETS[1].filename
        second_image.write_bytes(first_image.read_bytes())
        assert_rejected(
            duplicate_image_manifest,
            "exact duplicate image",
            "identical image files must not be reused across slots",
        )

    print(
        "PASS: strict manifest accepts complete assets and rejects pending states, repeated shots, "
        "unsafe or ungrounded evidence, incomplete research/modules, placeholder copy, repeated "
        "visuals, invalid URLs, and malformed manifests"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
