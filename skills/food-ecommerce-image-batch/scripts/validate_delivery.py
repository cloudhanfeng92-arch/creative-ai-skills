#!/usr/bin/env python3
"""Validate the fixed file matrix and aspect ratios of a finished batch."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from _image_utils import PngValidationError, validate_png


@dataclass(frozen=True)
class Asset:
    filename: str
    ratio: float


ASSETS = (
    Asset("00_packshot_white_1x1.png", 1.0),
    Asset("01_main_click_hook_1x1.png", 1.0),
    Asset("02_main_product_real_1x1.png", 1.0),
    Asset("03_main_usage_pairing_1x1.png", 1.0),
    Asset("04_main_texture_proof_1x1.png", 1.0),
    Asset("05_main_ingredient_advantage_1x1.png", 1.0),
    Asset("06_detail_core_value_3x4.png", 3 / 4),
    Asset("07_detail_key_difference_3x4.png", 3 / 4),
    Asset("08_detail_usage_scene_3x4.png", 3 / 4),
    Asset("09_detail_multi_angle_3x4.png", 3 / 4),
    Asset("10_detail_process_3x4.png", 3 / 4),
    Asset("11_detail_specs_3x4.png", 3 / 4),
)

ALLOWED_STATUSES = {"planned", "researching", "generating", "qa_pass", "failed"}
ALLOWED_CONTENT_MODES = {"standard", "evidence_safe_substitution", "concept_render"}
ALLOWED_EVIDENCE_MODES = {
    "direct_input",
    "exact_sku_web",
    "visible_evidence",
    "category_context",
    "auto_role_substitution",
}
ALLOWED_RESEARCH_STATUSES = {"completed", "web_unavailable", "user_forbade_web"}
ALLOWED_EXACT_SKU_STATUSES = {
    "verified",
    "no_exact_sku_source",
    "conflict_rejected",
    "not_needed",
}
EXACT_SKU_SOURCE_TIERS = {"official_brand", "official_store", "regulator"}
CATEGORY_DESIGN_USES = {
    "visual_strategy",
    "scene_context",
    "typography",
    "consumer_motivation",
}
CATEGORY_DESIGN_SOURCE_TIERS = {
    "official_brand",
    "official_store",
    "peer_reviewed",
    "category_page",
    "editorial",
    "ugc",
}
DESIGN_RESEARCH_USES = CATEGORY_DESIGN_USES | {"platform_compliance"}
ALLOWED_FACT_STATUSES = {
    "confirmed",
    "verified_web",
    "observable",
    "category_research",
    "hypothesis",
    "unknown",
}
ALLOWED_SOURCE_TIERS = {
    "official_brand",
    "official_store",
    "regulator",
    "platform_rule",
    "peer_reviewed",
    "category_page",
    "editorial",
    "ugc",
}
ALLOWED_FACT_DOMAINS = {
    "allergen",
    "award",
    "brand",
    "certification",
    "consumer_motivation",
    "expiry_date",
    "flavor",
    "food_form",
    "health_claim",
    "ingredient",
    "ingredient_ratio",
    "net_weight",
    "nutrition",
    "origin",
    "pack_count",
    "package_structure",
    "patent",
    "platform_rule",
    "portion_yield",
    "price",
    "prepared_state",
    "process",
    "process_parameter",
    "producer",
    "product_identity",
    "product_name",
    "promotion",
    "sales_claim",
    "sensory_description",
    "serving_method",
    "shelf_life",
    "sku",
    "specification",
    "storage",
    "target_audience",
    "test_report",
    "typography",
    "usage_scene",
    "visible_form",
    "visible_scale",
    "visible_surface",
    "visual_strategy",
}
HIGH_RISK_FACT_DOMAINS = {
    "allergen",
    "award",
    "certification",
    "expiry_date",
    "health_claim",
    "ingredient",
    "ingredient_ratio",
    "nutrition",
    "origin",
    "patent",
    "process",
    "process_parameter",
    "promotion",
    "sales_claim",
    "shelf_life",
    "storage",
    "target_audience",
    "test_report",
}
ALLOWED_REFERENCE_ROLES = {
    "PACK_FRONT",
    "PACK_OTHER",
    "PACK_INNER",
    "FOOD_REAL",
    "INGREDIENT",
    "USAGE_SCENE",
    "STYLE_ONLY",
}
ALLOWED_FOOD_EVIDENCE_COVERAGE = {
    "whole",
    "surface",
    "cross_section",
    "scale",
    "prepared_state",
    "portion_yield_confirmed",
}
FOOD_COVERAGE_REQUIREMENTS = {
    "food_form": {"whole"},
    "visible_form": {"whole"},
    "visible_surface": {"surface", "cross_section"},
    "visible_scale": {"scale"},
    "prepared_state": {"prepared_state"},
    "portion_yield": {"portion_yield_confirmed"},
}
FOOD_INPUT_REQUIRED_DOMAINS = {
    "food_form",
    "visible_surface",
    "prepared_state",
    "portion_yield",
}
INGREDIENT_FACT_DOMAINS = {"ingredient", "ingredient_ratio"}
PROCESS_FACT_DOMAINS = {"process", "process_parameter"}
SPEC_FACT_DOMAINS = {
    "product_name",
    "sku",
    "flavor",
    "net_weight",
    "pack_count",
    "specification",
    "price",
    "ingredient",
    "ingredient_ratio",
    "serving_method",
    "origin",
    "shelf_life",
    "storage",
}
ALLOWED_VISUAL_LEADS = {"food", "package", "scene", "evidence", "layout"}
ALLOWED_PACKAGE_PRESENCE = {"required", "optional", "omit"}
ALLOWED_PACKAGE_VARIANTS = {"outer", "inner", "none"}
ALLOWED_PACKAGE_SCALE_ROLES = {"hero", "anchor", "secondary", "none"}
MAX_VISIBLE_PACKAGES_PER_SET = 6
TRACKING_QUERY_KEYS = {
    "_ga",
    "fbclid",
    "from",
    "gclid",
    "mc_cid",
    "mc_eid",
    "msclkid",
    "ref",
    "referrer",
    "scm",
    "source",
    "spm",
    "srsltid",
    "wbraid",
    "yclid",
    "_gl",
    "dclid",
    "gbraid",
    "igshid",
    "mkt_tok",
}
FORBIDDEN_VISIBLE_TERMS = {
    "data_pending",
    "不可发布",
    "待补",
    "待补资料",
    "待补信息",
    "资料待补",
}
LEGACY_PENDING_STATUSES = {
    "concept_only",
    "data_pending",
    "draft_role_substitution",
    "approved_substitution",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check food-commerce delivery filenames, count, PNG readability, and ratios."
    )
    parser.add_argument("root", type=Path, help="Directory containing SET_01 ... SET_N")
    parser.add_argument("--sets", type=int, required=True, help="Expected number of sets")
    parser.add_argument(
        "--ratio-tolerance",
        type=float,
        default=0.012,
        help="Allowed absolute ratio difference (default: 0.012)",
    )
    parser.add_argument(
        "--allow-extra-images",
        action="store_true",
        help="Warn rather than fail when extra PNG files exist in a set directory",
    )
    parser.add_argument(
        "--strict-manifest",
        action="store_true",
        help=(
            "Also require manifest.json with one qa_pass record per slot, current content/evidence "
            "modes, and no legacy pending states"
        ),
    )
    return parser.parse_args()


def _as_mode_set(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return set(value)
    return set()


def _normalize_url(value: object) -> str:
    if not isinstance(value, str):
        return ""
    raw = value.strip()
    if not raw:
        return ""
    try:
        parts = urlsplit(raw)
    except ValueError:
        return raw.split("#", 1)[0].rstrip("/")
    try:
        hostname = parts.hostname.casefold() if parts.hostname else ""
        port = parts.port
    except ValueError:
        return raw.split("#", 1)[0].rstrip("/")
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    default_port = (parts.scheme.casefold() == "https" and port == 443) or (
        parts.scheme.casefold() == "http" and port == 80
    )
    netloc = hostname if port is None or default_port else f"{hostname}:{port}"
    path = parts.path.rstrip("/")
    query_pairs = []
    for key, item_value in parse_qsl(parts.query, keep_blank_values=True):
        normalized_key = key.casefold()
        if (
            normalized_key.startswith("utm_")
            or normalized_key.endswith("clid")
            or normalized_key in TRACKING_QUERY_KEYS
        ):
            continue
        query_pairs.append((key, item_value))
    normalized_query = urlencode(sorted(query_pairs))
    return urlunsplit(
        (
            parts.scheme.casefold(),
            netloc,
            path,
            normalized_query,
            "",
        )
    )


def _is_valid_http_url(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    raw = value.strip()
    if any(character.isspace() or ord(character) < 32 for character in raw):
        return False
    try:
        parts = urlsplit(raw)
        hostname = parts.hostname
        port = parts.port  # Access validates malformed/non-numeric/out-of-range ports.
        return (
            parts.scheme.casefold() in {"http", "https"}
            and bool(hostname)
            and bool(parts.netloc)
            and parts.username is None
            and parts.password is None
            and (port is None or port > 0)
            and not any(character.isspace() for character in (hostname or ""))
            and _is_valid_hostname(hostname or "")
        )
    except ValueError:
        return False


def _is_valid_hostname(value: str) -> bool:
    candidate = value.strip("[]")
    try:
        ipaddress.ip_address(candidate)
        return True
    except ValueError:
        pass
    try:
        ascii_hostname = candidate.rstrip(".").encode("idna").decode("ascii")
    except (UnicodeError, ValueError):
        return False
    if not ascii_hostname or len(ascii_hostname) > 253:
        return False
    labels = ascii_hostname.split(".")
    return all(
        1 <= len(label) <= 63
        and re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label, re.I)
        is not None
        for label in labels
    )


def _normalize_authority(value: object) -> str:
    """Collapse common official-store wrappers to the underlying publishing entity."""

    if not isinstance(value, str):
        return ""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    for phrase in (
        "官方旗舰店",
        "品牌旗舰店",
        "官方商城",
        "官方店铺",
        "官方店",
        "旗舰店",
        "品牌官网",
        "官方网站",
        "官网",
        "品牌所有者",
        "品牌持有人",
        "品牌运营方",
        "品牌运营商",
        "品牌官方",
        "品牌方",
        "品牌商",
        "官方渠道",
        "官方账号",
    ):
        normalized = normalized.replace(phrase, "")
    tokens = re.findall(r"[a-z0-9]+|[\u3400-\u9fff]+", normalized)
    generic_tokens = {
        "official",
        "authorized",
        "brand",
        "owner",
        "publisher",
        "channel",
        "account",
        "flagship",
        "store",
        "shop",
        "website",
        "webshop",
    }
    return "".join(token for token in tokens if token not in generic_tokens)


def _is_iso_date(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 10:
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _has_meaningful_content(value: object) -> bool:
    if isinstance(value, str):
        return _meaningful_character_count(value) > 0
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return True
    if isinstance(value, list):
        return any(_has_meaningful_content(item) for item in value)
    if isinstance(value, dict):
        return any(_has_meaningful_content(item) for item in value.values())
    return False


def _meaningful_content_count(value: object) -> int:
    if isinstance(value, str):
        return _meaningful_character_count(value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return len(str(value))
    if isinstance(value, (list, tuple)):
        return sum(_meaningful_content_count(item) for item in value)
    if isinstance(value, dict):
        return sum(_meaningful_content_count(item) for item in value.values())
    return 0


def _visible_character_count(value: str) -> int:
    return sum(1 for character in value.strip() if not character.isspace())


def _meaningful_character_count(value: str) -> int:
    return sum(
        1
        for character in value.strip()
        if unicodedata.category(character)[:1] in {"L", "N"}
    )


def _iter_strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _iter_strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _iter_strings(key)
            yield from _iter_strings(item)


def _canonical_role(filename: str) -> str:
    stem = Path(filename).stem
    role = stem.split("_", 1)[1]
    for suffix in ("_1x1", "_3x4"):
        if role.endswith(suffix):
            return role[: -len(suffix)]
    return role


def validate_manifest(root: Path, set_count: int) -> list[str]:
    """Validate completion and evidence metadata for the no-placeholder workflow."""

    errors: list[str] = []
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        return ["manifest.json: missing (required by --strict-manifest)"]
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"manifest.json: cannot parse: {exc}"]
    if not isinstance(payload, dict):
        return ["manifest.json: root must be an object"]

    execution_mode = payload.get("execution_mode")
    if execution_mode != "render":
        errors.append(
            f"manifest.json: strict image validation requires execution_mode 'render', got {execution_mode!r}"
        )

    research_status = payload.get("research_status")
    if not isinstance(research_status, str) or research_status not in ALLOWED_RESEARCH_STATUSES:
        errors.append(f"manifest.json: invalid or missing research_status {research_status!r}")
    exact_sku_status = payload.get("exact_sku_status")
    if not isinstance(exact_sku_status, str) or exact_sku_status not in ALLOWED_EXACT_SKU_STATUSES:
        errors.append(f"manifest.json: invalid or missing exact_sku_status {exact_sku_status!r}")
    platform_scope = payload.get("platform_scope")
    if not isinstance(platform_scope, str) or not platform_scope.strip():
        errors.append("manifest.json: missing platform_scope")
    research_queries = payload.get("research_queries")
    if not isinstance(research_queries, list):
        errors.append("manifest.json: research_queries must be a list")
    elif research_status != "user_forbade_web":
        if not any(
            isinstance(query, str) and query.strip() for query in research_queries
        ):
            errors.append("manifest.json: research_queries must record at least one attempted query")

    input_refs = payload.get("input_refs")
    input_ref_roles: dict[str, set[str]] = {}
    input_ref_food_coverage: dict[str, set[str]] = {}
    if not isinstance(input_refs, list) or not input_refs:
        errors.append("manifest.json: input_refs must be a non-empty list")
    else:
        for position, input_ref in enumerate(input_refs):
            label = f"manifest.json: input_refs[{position}]"
            if not isinstance(input_ref, dict):
                errors.append(f"{label} must be an object")
                continue
            ref_id = input_ref.get("id")
            if not isinstance(ref_id, str) or not ref_id.strip():
                errors.append(f"{label} missing id")
                continue
            if ref_id in input_ref_roles:
                errors.append(f"{label} duplicates id {ref_id}")
            raw_roles = input_ref.get("roles", input_ref.get("role"))
            if isinstance(raw_roles, str):
                roles = {raw_roles}
            elif isinstance(raw_roles, list) and all(
                isinstance(role, str) and role for role in raw_roles
            ):
                roles = set(raw_roles)
            else:
                roles = set()
            if not roles or not roles.issubset(ALLOWED_REFERENCE_ROLES):
                errors.append(f"{label} has invalid or missing roles")
            input_ref_roles[ref_id] = roles
            raw_coverage = input_ref.get("evidence_coverage")
            if "FOOD_REAL" in roles:
                if (
                    not isinstance(raw_coverage, list)
                    or not raw_coverage
                    or not all(
                        isinstance(item, str) and item in ALLOWED_FOOD_EVIDENCE_COVERAGE
                        for item in raw_coverage
                    )
                ):
                    errors.append(
                        f"{label} FOOD_REAL needs valid non-empty evidence_coverage"
                    )
                    input_ref_food_coverage[ref_id] = set()
                else:
                    input_ref_food_coverage[ref_id] = set(raw_coverage)
            elif raw_coverage not in (None, []):
                errors.append(f"{label} evidence_coverage is only valid for FOOD_REAL")

    research_sources = payload.get("research_sources")
    source_ids: set[str] = set()
    exact_source_ids: set[str] = set()
    source_urls: dict[str, str] = {}
    source_authorities: dict[str, str] = {}
    source_allowed_uses: dict[str, set[str]] = {}
    design_source_ids: set[str] = set()
    seen_source_urls: dict[str, str] = {}
    exact_source_count = 0
    design_source_count = 0
    generic_compliance_source_count = 0
    named_platform_rule_source_count = 0
    completed_design_uses: set[str] = set()
    if not isinstance(research_sources, list):
        errors.append("manifest.json: research_sources must be a list")
    else:
        for position, source in enumerate(research_sources):
            if not isinstance(source, dict):
                errors.append(f"manifest.json: research_sources[{position}] must be an object")
                continue
            source_id = source.get("id")
            if isinstance(source_id, str) and source_id:
                if source_id in source_ids or source_id in input_ref_roles:
                    errors.append(f"manifest.json: duplicate research source id {source_id}")
                source_ids.add(source_id)
            else:
                errors.append(f"manifest.json: research_sources[{position}] missing id")
            source_url = source.get("url")
            if not _is_valid_http_url(source_url):
                errors.append(
                    f"manifest.json: research source {source_id or position} needs a valid HTTP(S) url"
                )
            normalized_url = _normalize_url(source_url)
            if normalized_url and _is_valid_http_url(source_url):
                prior_source_id = seen_source_urls.get(normalized_url)
                if prior_source_id:
                    errors.append(
                        f"manifest.json: research source {source_id or position} duplicates URL from {prior_source_id}"
                    )
                elif isinstance(source_id, str) and source_id:
                    seen_source_urls[normalized_url] = source_id
                if isinstance(source_id, str) and source_id:
                    source_urls[source_id] = normalized_url
            title = source.get("title")
            if not isinstance(title, str) or not title.strip():
                errors.append(
                    f"manifest.json: research source {source_id or position} missing title"
                )
            if not _is_iso_date(source.get("retrieved_at")):
                errors.append(
                    f"manifest.json: research source {source_id or position} needs retrieved_at YYYY-MM-DD"
                )
            raw_source_tier = source.get("source_tier")
            source_tier = raw_source_tier if isinstance(raw_source_tier, str) else ""
            if source_tier not in ALLOWED_SOURCE_TIERS:
                errors.append(
                    f"manifest.json: research source {source_id or position} has invalid source_tier"
                )
            allowed_uses = source.get("allowed_uses")
            if (
                not isinstance(allowed_uses, list)
                or not allowed_uses
                or not all(isinstance(item, str) and item.strip() for item in allowed_uses)
            ):
                errors.append(
                    f"manifest.json: research source {source_id or position} needs string allowed_uses"
                )
                allowed_use_set: set[str] = set()
            else:
                allowed_use_set = set(allowed_uses)
            if isinstance(source_id, str) and source_id:
                source_allowed_uses[source_id] = allowed_use_set
            exact_sku_match = source.get("exact_sku_match")
            if not isinstance(exact_sku_match, bool):
                errors.append(
                    f"manifest.json: research source {source_id or position} missing boolean exact_sku_match"
                )
            if exact_sku_match is False and not allowed_use_set.issubset(DESIGN_RESEARCH_USES):
                errors.append(
                    f"manifest.json: non-SKU source {source_id or position} has disallowed uses"
                )
            design_uses = allowed_use_set.intersection(CATEGORY_DESIGN_USES)
            if exact_sku_match is False and design_uses:
                if source_tier not in CATEGORY_DESIGN_SOURCE_TIERS:
                    errors.append(
                        f"manifest.json: research source {source_id or position} uses design research fields with a non-design source_tier"
                    )
                else:
                    design_source_count += 1
                    completed_design_uses.update(design_uses)
                    if isinstance(source_id, str) and source_id:
                        design_source_ids.add(source_id)
            if exact_sku_match is False and "platform_compliance" in allowed_use_set:
                if source_tier in {"platform_rule", "regulator"}:
                    generic_compliance_source_count += 1
                if source_tier == "platform_rule":
                    named_platform_rule_source_count += 1
            if exact_sku_match is True:
                exact_source_count += 1
                if isinstance(source_id, str) and source_id:
                    exact_source_ids.add(source_id)
                if source_tier not in EXACT_SKU_SOURCE_TIERS:
                    errors.append(
                        f"manifest.json: exact-SKU source {source_id or position} has untrusted source_tier"
                    )
                source_authority = source.get("source_authority")
                if not isinstance(source_authority, str) or not source_authority.strip():
                    errors.append(
                        f"manifest.json: exact-SKU source {source_id or position} missing source_authority"
                    )
                elif isinstance(source_id, str) and source_id:
                    normalized_authority = _normalize_authority(source_authority)
                    if not normalized_authority:
                        errors.append(
                            f"manifest.json: exact-SKU source {source_id} has unusable source_authority"
                        )
                    else:
                        source_authorities[source_id] = normalized_authority
                anchors = source.get("identity_anchors")
                anchor_set = (
                    {item for item in anchors if isinstance(item, str) and item}
                    if isinstance(anchors, list)
                    else set()
                )
                if not {"brand", "producer"}.intersection(anchor_set) or "product_name" not in anchor_set:
                    errors.append(
                        f"manifest.json: exact-SKU source {source_id or position} needs product_name plus brand or producer identity anchors"
                    )
                excerpt = source.get("evidence_excerpt")
                if not isinstance(excerpt, str) or not excerpt.strip():
                    errors.append(
                        f"manifest.json: exact-SKU source {source_id or position} missing evidence_excerpt"
                    )

    if research_status == "completed" and not source_ids:
        errors.append("manifest.json: completed research requires at least one research source")
    if research_status == "completed" and design_source_count == 0:
        errors.append("manifest.json: completed research requires a non-SKU design/context source")
    if research_status == "completed" and "visual_strategy" not in completed_design_uses:
        errors.append(
            "manifest.json: completed research requires category visual_strategy coverage"
        )
    if research_status == "completed" and not completed_design_uses.intersection(
        {"scene_context", "consumer_motivation"}
    ):
        errors.append(
            "manifest.json: completed research requires scene_context or consumer_motivation coverage"
        )
    if research_status == "completed" and generic_compliance_source_count == 0:
        errors.append(
            "manifest.json: completed research requires an official platform/regulatory compliance source"
        )
    if (
        research_status == "completed"
        and isinstance(platform_scope, str)
        and platform_scope.strip()
        and platform_scope != "generic_ecommerce"
        and named_platform_rule_source_count == 0
    ):
        errors.append(
            "manifest.json: named platform scope requires an official platform_rule source"
        )
    if exact_sku_status == "verified" and exact_source_count == 0:
        errors.append("manifest.json: exact_sku_status verified requires an exact-SKU source")
    if exact_sku_status != "verified" and exact_source_count:
        errors.append("manifest.json: exact-SKU sources require exact_sku_status verified")

    facts = payload.get("facts")
    fact_keys: set[str] = set()
    fact_status_by_key: dict[str, str] = {}
    fact_domain_by_key: dict[str, str] = {}
    fact_allowed_uses_by_key: dict[str, set[str]] = {}
    fact_source_refs_by_key: dict[str, set[str]] = {}
    if not isinstance(facts, list):
        errors.append("manifest.json: facts must be a list")
    else:
        for position, fact in enumerate(facts):
            label = f"manifest.json: facts[{position}]"
            if not isinstance(fact, dict):
                errors.append(f"{label} must be an object")
                continue
            fact_key = fact.get("key")
            if not isinstance(fact_key, str) or not fact_key.strip():
                errors.append(f"{label} missing key")
                continue
            label = f"manifest.json: fact {fact_key}"
            if fact_key in fact_keys:
                errors.append(f"{label} is duplicated")
            fact_keys.add(fact_key)
            fact_domain = fact.get("fact_domain")
            if not isinstance(fact_domain, str) or fact_domain not in ALLOWED_FACT_DOMAINS:
                errors.append(f"{label} has invalid or missing fact_domain {fact_domain!r}")
            else:
                fact_domain_by_key[fact_key] = fact_domain
            fact_status = fact.get("status")
            if not isinstance(fact_status, str) or fact_status not in ALLOWED_FACT_STATUSES:
                errors.append(f"{label} has invalid status {fact_status!r}")
            else:
                fact_status_by_key[fact_key] = fact_status
            if (
                isinstance(fact_status, str)
                and fact_status in {"confirmed", "verified_web", "observable"}
                and not _has_meaningful_content(fact.get("value"))
            ):
                errors.append(f"{label} evidentiary fact needs a meaningful value")
            source_refs = fact.get("source_refs")
            if (
                not isinstance(source_refs, list)
                or not source_refs
                or not all(isinstance(ref, str) and ref.strip() for ref in source_refs)
            ):
                errors.append(f"{label} needs string source_refs")
                source_ref_set: set[str] = set()
            else:
                source_ref_set = set(source_refs)
                fact_source_refs_by_key[fact_key] = source_ref_set
            allowed_uses = fact.get("allowed_uses")
            if (
                not isinstance(allowed_uses, list)
                or not allowed_uses
                or not all(isinstance(item, str) and item.strip() for item in allowed_uses)
            ):
                errors.append(f"{label} needs string allowed_uses")
                fact_allowed_use_set: set[str] = set()
            else:
                fact_allowed_use_set = set(allowed_uses)
                fact_allowed_uses_by_key[fact_key] = fact_allowed_use_set
            if isinstance(fact_domain, str) and fact_domain in HIGH_RISK_FACT_DOMAINS:
                if fact_status == "observable":
                    errors.append(f"{label} high-risk domain cannot use observable status")
            if fact_status == "verified_web":
                if not source_ref_set or not source_ref_set.issubset(exact_source_ids):
                    errors.append(f"{label} verified_web must reference exact-SKU sources")
                if fact_allowed_use_set and any(
                    not fact_allowed_use_set.issubset(source_allowed_uses.get(ref, set()))
                    for ref in source_ref_set
                ):
                    errors.append(
                        f"{label} uses must be allowed by every cited web source"
                    )
                if isinstance(fact_domain, str) and fact_domain in HIGH_RISK_FACT_DOMAINS:
                    distinct_urls = {
                        source_urls[ref]
                        for ref in source_ref_set
                        if ref in exact_source_ids and source_urls.get(ref)
                    }
                    if len(distinct_urls) < 2:
                        errors.append(
                            f"{label} high-risk web fact requires two distinct exact-SKU sources"
                        )
                    distinct_authorities = {
                        source_authorities[ref]
                        for ref in source_ref_set
                        if ref in exact_source_ids and source_authorities.get(ref)
                    }
                    if len(distinct_authorities) < 2:
                        errors.append(
                            f"{label} high-risk web fact requires two independent source_authorities"
                        )
            if (
                isinstance(fact_status, str)
                and fact_status in {"confirmed", "observable"}
                and source_ref_set
            ):
                if not source_ref_set.intersection(input_ref_roles):
                    errors.append(
                        f"{label} {fact_status} must cite a declared input_ref"
                    )
                non_input_refs = source_ref_set - set(input_ref_roles)
                if non_input_refs:
                    errors.append(
                        f"{label} {fact_status} may only cite declared input_refs: {sorted(non_input_refs)}"
                    )
                style_only_refs = {
                    ref
                    for ref in source_ref_set
                    if input_ref_roles.get(ref) == {"STYLE_ONLY"}
                }
                if style_only_refs:
                    errors.append(
                        f"{label} {fact_status} cannot cite STYLE_ONLY inputs: {sorted(style_only_refs)}"
                    )
                if (
                    isinstance(fact_domain, str)
                    and fact_domain in FOOD_INPUT_REQUIRED_DOMAINS
                    and not any(
                        "FOOD_REAL" in input_ref_roles.get(ref, set())
                        for ref in source_ref_set
                    )
                ):
                    errors.append(
                        f"{label} {fact_domain} requires a FOOD_REAL input source"
                    )

    assets = payload.get("assets")
    if not isinstance(assets, list):
        errors.append("manifest.json: assets must be a list")
        return errors

    expected: dict[str, str] = {}
    expected_roles: dict[str, str] = {}
    expected_ratios: dict[str, str] = {}
    for set_index in range(1, set_count + 1):
        set_name = f"SET_{set_index:02d}"
        for slot, asset in enumerate(ASSETS):
            asset_id = f"{set_name}-{slot:02d}"
            expected[asset_id] = f"{set_name}/{asset.filename}"
            expected_roles[asset_id] = _canonical_role(asset.filename)
            expected_ratios[asset_id] = "1:1" if asset.ratio == 1.0 else "3:4"

    seen_ids: set[str] = set()
    seen_shot_deltas: dict[str, dict[str, str]] = {}
    seen_evidence_axes: dict[str, dict[str, str]] = {}
    visible_package_counts: dict[str, int] = {}
    seen_detail_layouts: dict[str, set[str]] = {}
    seen_typography_directions: dict[str, set[str]] = {}
    seen_headlines: dict[str, dict[str, str]] = {}
    for position, record in enumerate(assets):
        label = f"manifest.json: assets[{position}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        asset_id = record.get("id") or record.get("asset_id")
        if not isinstance(asset_id, str) or not asset_id:
            errors.append(f"{label} missing id")
            continue
        label = f"manifest.json: {asset_id}"
        if asset_id in seen_ids:
            errors.append(f"{label} is duplicated")
        seen_ids.add(asset_id)
        if asset_id not in expected:
            errors.append(f"{label} is not an expected slot")
            continue
        set_id, slot_text = asset_id.rsplit("-", 1)
        slot = int(slot_text)
        if record.get("set_id") != set_id:
            errors.append(f"{label} set_id must be {set_id!r}")
        canonical_role = expected_roles[asset_id]
        if record.get("role") != canonical_role:
            errors.append(f"{label} role must be {canonical_role!r}")
        if record.get("aspect_ratio") != expected_ratios[asset_id]:
            errors.append(f"{label} aspect_ratio must be {expected_ratios[asset_id]!r}")

        status = record.get("status")
        if isinstance(status, str) and status in LEGACY_PENDING_STATUSES:
            errors.append(f"{label} uses removed pending status {status}")
        elif not isinstance(status, str) or status not in ALLOWED_STATUSES:
            errors.append(f"{label} has invalid status {status!r}")
        elif status != "qa_pass":
            errors.append(f"{label} is not complete; strict final status must be qa_pass")

        content_mode = record.get("content_mode")
        if not isinstance(content_mode, str) or content_mode not in ALLOWED_CONTENT_MODES:
            errors.append(f"{label} has invalid or missing content_mode {content_mode!r}")
        publishable = record.get("publishable")
        if not isinstance(publishable, bool):
            errors.append(f"{label} missing boolean publishable")
        elif content_mode == "concept_render" and publishable:
            errors.append(f"{label} concept_render cannot be marked publishable")
        elif (
            isinstance(content_mode, str)
            and content_mode in {"standard", "evidence_safe_substitution"}
            and not publishable
        ):
            errors.append(f"{label} completed publishable content must be marked publishable")

        modes = _as_mode_set(record.get("evidence_mode"))
        if not modes:
            errors.append(f"{label} missing evidence_mode")
        invalid_modes = modes - ALLOWED_EVIDENCE_MODES
        if invalid_modes:
            errors.append(f"{label} has invalid evidence_mode values: {sorted(invalid_modes)}")
        if "auto_role_substitution" in modes and content_mode != "evidence_safe_substitution":
            errors.append(
                f"{label} auto_role_substitution is only valid for evidence_safe_substitution"
            )
        raw_asset_research_refs = record.get("research_sources", [])
        if not isinstance(raw_asset_research_refs, list) or not all(
            isinstance(ref, str) and ref.strip() for ref in raw_asset_research_refs
        ):
            errors.append(f"{label} research_sources must be a list of source IDs")
            asset_research_ref_set: set[str] = set()
        else:
            asset_research_ref_set = set(raw_asset_research_refs)
            unknown_asset_research_refs = asset_research_ref_set - source_ids
            if unknown_asset_research_refs:
                errors.append(
                    f"{label} references unknown research sources: {sorted(unknown_asset_research_refs)}"
                )
        if "exact_sku_web" in modes:
            if not asset_research_ref_set:
                errors.append(f"{label} uses exact_sku_web without research_sources")
            elif not asset_research_ref_set.intersection(exact_source_ids):
                errors.append(f"{label} exact_sku_web requires at least one exact-SKU research source")
        if "category_context" in modes:
            if not asset_research_ref_set:
                errors.append(f"{label} uses category_context without research_sources")
            elif not asset_research_ref_set.intersection(design_source_ids):
                errors.append(f"{label} category_context requires a non-SKU design source")

        original_role = record.get("original_role")
        delivered_role = record.get("delivered_role")
        if original_role != canonical_role:
            errors.append(f"{label} original_role must be {canonical_role!r}")
        if not isinstance(delivered_role, str) or not delivered_role.strip():
            errors.append(f"{label} missing delivered_role")
        if content_mode == "standard" and delivered_role != canonical_role:
            errors.append(f"{label} standard content must keep the canonical delivered_role")
        if content_mode == "evidence_safe_substitution":
            reason = record.get("substitution_reason")
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"{label} substitution requires substitution_reason")
            if "auto_role_substitution" not in modes:
                errors.append(f"{label} substitution requires auto_role_substitution evidence_mode")
            if delivered_role == canonical_role:
                errors.append(f"{label} substitution must declare a different delivered_role")

        asset_source_refs = record.get("source_refs")
        asset_input_ref_ids: set[str] = set()
        asset_food_coverage_by_ref: dict[str, set[str]] = {}
        has_pack_inner_ref = False
        has_pack_outer_ref = False
        has_pack_front_ref = False
        has_pack_other_ref = False
        has_food_real_ref = False
        if not isinstance(asset_source_refs, list) or not asset_source_refs:
            errors.append(f"{label} source_refs must be a non-empty list")
        else:
            for ref_position, source_ref in enumerate(asset_source_refs):
                ref_label = f"{label} source_refs[{ref_position}]"
                if not isinstance(source_ref, dict):
                    errors.append(f"{ref_label} must be an object")
                    continue
                ref_id = source_ref.get("ref")
                if not isinstance(ref_id, str) or not ref_id.strip():
                    errors.append(f"{ref_label} missing ref")
                    continue
                raw_roles = source_ref.get("roles", source_ref.get("role"))
                if isinstance(raw_roles, str):
                    ref_roles = {raw_roles}
                elif isinstance(raw_roles, list) and raw_roles and all(
                    isinstance(role, str) and role for role in raw_roles
                ):
                    ref_roles = set(raw_roles)
                else:
                    ref_roles = set()
                if not ref_roles or not ref_roles.issubset(ALLOWED_REFERENCE_ROLES):
                    errors.append(f"{ref_label} has invalid or missing roles")
                if ref_id in input_ref_roles:
                    asset_input_ref_ids.add(ref_id)
                    if not ref_roles.issubset(input_ref_roles[ref_id]):
                        errors.append(f"{ref_label} roles exceed declared input_ref roles")
                elif ref_id in exact_source_ids:
                    pass
                elif ref_id in source_ids:
                    if ref_roles != {"STYLE_ONLY"}:
                        errors.append(f"{ref_label} non-SKU web source must be STYLE_ONLY")
                else:
                    errors.append(f"{ref_label} references an unknown input or web source")
                if "PACK_INNER" in ref_roles:
                    has_pack_inner_ref = True
                if ref_roles.intersection({"PACK_FRONT", "PACK_OTHER"}):
                    has_pack_outer_ref = True
                if "PACK_FRONT" in ref_roles:
                    has_pack_front_ref = True
                if "PACK_OTHER" in ref_roles:
                    has_pack_other_ref = True
                if "FOOD_REAL" in ref_roles:
                    has_food_real_ref = True
                raw_coverage = source_ref.get("evidence_coverage")
                if "FOOD_REAL" in ref_roles:
                    if (
                        not isinstance(raw_coverage, list)
                        or not raw_coverage
                        or not all(
                            isinstance(item, str) and item in ALLOWED_FOOD_EVIDENCE_COVERAGE
                            for item in raw_coverage
                        )
                    ):
                        errors.append(
                            f"{ref_label} FOOD_REAL needs valid non-empty evidence_coverage"
                        )
                    elif ref_id in input_ref_food_coverage and not set(raw_coverage).issubset(
                        input_ref_food_coverage[ref_id]
                    ):
                        errors.append(
                            f"{ref_label} evidence_coverage exceeds the declared input coverage"
                        )
                    else:
                        asset_food_coverage_by_ref[ref_id] = set(raw_coverage)
                elif raw_coverage not in (None, []):
                    errors.append(
                        f"{ref_label} evidence_coverage is only valid for FOOD_REAL"
                    )

        evidence_keys = record.get("evidence_keys")
        if (
            not isinstance(evidence_keys, list)
            or not evidence_keys
            or not all(isinstance(key, str) and key.strip() for key in evidence_keys)
        ):
            errors.append(f"{label} needs string evidence_keys")
        elif any(key not in fact_keys for key in evidence_keys):
            errors.append(f"{label} references an unknown evidence key")
        elif any(
            fact_status_by_key.get(key) not in {"confirmed", "verified_web", "observable"}
            for key in evidence_keys
        ):
            errors.append(f"{label} uses a non-evidentiary fact as evidence")
        elif any(
            not fact_allowed_uses_by_key.get(key, set()).intersection(
                {"copy", "headline", "proof", "specs", "subline", "visual_evidence", "visual_lock"}
            )
            for key in evidence_keys
        ):
            errors.append(f"{label} evidence key is not allowed for image/copy use")
        else:
            verified_evidence_keys = [
                key for key in evidence_keys if fact_status_by_key.get(key) == "verified_web"
            ]
            input_evidence_keys = [
                key
                for key in evidence_keys
                if fact_status_by_key.get(key) in {"confirmed", "observable"}
            ]
            if "exact_sku_web" in modes and not verified_evidence_keys:
                errors.append(f"{label} exact_sku_web mode needs a verified_web evidence key")
            if verified_evidence_keys and "exact_sku_web" not in modes:
                errors.append(
                    f"{label} verified_web evidence requires exact_sku_web evidence_mode"
                )
            if input_evidence_keys and not modes.intersection(
                {"direct_input", "visible_evidence"}
            ):
                errors.append(
                    f"{label} input evidence requires direct_input or visible_evidence mode"
                )
            for key in input_evidence_keys:
                missing_input_sources = (
                    fact_source_refs_by_key.get(key, set()) - asset_input_ref_ids
                )
                if missing_input_sources:
                    errors.append(
                        f"{label} omits input sources for evidence {key}: {sorted(missing_input_sources)}"
                    )
                required_coverage = FOOD_COVERAGE_REQUIREMENTS.get(
                    fact_domain_by_key.get(key, ""), set()
                )
                if required_coverage:
                    for ref_id in fact_source_refs_by_key.get(key, set()):
                        if "FOOD_REAL" not in input_ref_roles.get(ref_id, set()):
                            continue
                        used_coverage = asset_food_coverage_by_ref.get(ref_id, set())
                        if not used_coverage.intersection(required_coverage):
                            errors.append(
                                f"{label} evidence {key} needs FOOD_REAL coverage from {sorted(required_coverage)}"
                            )
            for key in verified_evidence_keys:
                missing_fact_sources = (
                    fact_source_refs_by_key.get(key, set()) - asset_research_ref_set
                )
                if missing_fact_sources:
                    errors.append(
                        f"{label} omits verified fact sources: {sorted(missing_fact_sources)}"
                    )
        valid_asset_evidence_keys = (
            [key for key in evidence_keys if isinstance(key, str)]
            if isinstance(evidence_keys, list)
            else []
        )
        asset_fact_domains = {
            fact_domain_by_key[key]
            for key in valid_asset_evidence_keys
            if key in fact_domain_by_key
        }
        asset_fact_uses = {
            allowed_use
            for key in valid_asset_evidence_keys
            for allowed_use in fact_allowed_uses_by_key.get(key, set())
        }
        if content_mode == "standard":
            if slot in {1, 2, 4} and not has_food_real_ref:
                errors.append(
                    f"{label} standard role for slot {slot:02d} requires a FOOD_REAL source_ref"
                )
            if slot == 5 and not asset_fact_domains.intersection(INGREDIENT_FACT_DOMAINS):
                errors.append(
                    f"{label} standard ingredient role requires confirmed ingredient evidence"
                )
            if slot == 7 and "differentiator" not in asset_fact_uses:
                errors.append(
                    f"{label} standard difference role requires a differentiator evidence use"
                )
            if slot == 9 and not has_pack_other_ref:
                errors.append(
                    f"{label} standard multi-angle role requires a PACK_OTHER source_ref"
                )
            if slot == 10 and not asset_fact_domains.intersection(PROCESS_FACT_DOMAINS):
                errors.append(
                    f"{label} standard process role requires process evidence"
                )
            if slot == 11:
                declared_specs = record.get("spec_fields")
                if not isinstance(declared_specs, dict) or not declared_specs:
                    errors.append(
                        f"{label} standard specs role requires non-empty spec_fields"
                    )
                if not asset_fact_domains.intersection(SPEC_FACT_DOMAINS):
                    errors.append(
                        f"{label} standard specs role requires specification evidence"
                    )
        evidence_axis = record.get("evidence_axis")
        if (
            not isinstance(evidence_axis, str)
            or _meaningful_character_count(evidence_axis) < 4
        ):
            errors.append(f"{label} missing evidence_axis")
        else:
            normalized_axis = " ".join(evidence_axis.casefold().split())
            prior_asset = seen_evidence_axes.setdefault(set_id, {}).get(normalized_axis)
            if prior_asset:
                errors.append(f"{label} duplicates evidence_axis from {prior_asset}")
            else:
                seen_evidence_axes[set_id][normalized_axis] = asset_id
        shot_delta = record.get("shot_delta")
        if not isinstance(shot_delta, str) or _meaningful_character_count(shot_delta) < 4:
            errors.append(f"{label} missing shot_delta")
        else:
            normalized_delta = " ".join(shot_delta.casefold().split())
            prior_asset = seen_shot_deltas.setdefault(set_id, {}).get(normalized_delta)
            if prior_asset:
                errors.append(f"{label} duplicates shot_delta from {prior_asset}")
            else:
                seen_shot_deltas[set_id][normalized_delta] = asset_id

        visual_lead = record.get("visual_lead")
        if not isinstance(visual_lead, str) or visual_lead not in ALLOWED_VISUAL_LEADS:
            errors.append(f"{label} has invalid or missing visual_lead {visual_lead!r}")
        package_presence = record.get("package_presence")
        if not isinstance(package_presence, str) or package_presence not in ALLOWED_PACKAGE_PRESENCE:
            errors.append(f"{label} has invalid or missing package_presence {package_presence!r}")
        package_reason = record.get("package_presence_reason")
        if not isinstance(package_reason, str) or not package_reason.strip():
            errors.append(f"{label} missing package_presence_reason")
        package_variant = record.get("package_variant")
        if not isinstance(package_variant, str) or package_variant not in ALLOWED_PACKAGE_VARIANTS:
            errors.append(f"{label} has invalid or missing package_variant {package_variant!r}")
        package_scale_role = record.get("package_scale_role")
        if (
            not isinstance(package_scale_role, str)
            or package_scale_role not in ALLOWED_PACKAGE_SCALE_ROLES
        ):
            errors.append(
                f"{label} has invalid or missing package_scale_role {package_scale_role!r}"
            )
        package_visible = record.get("package_visible")
        if not isinstance(package_visible, bool):
            errors.append(f"{label} missing boolean package_visible")
        elif package_visible:
            visible_package_counts[set_id] = visible_package_counts.get(set_id, 0) + 1
        if package_presence == "required" and package_visible is not True:
            errors.append(f"{label} required package must be visible")
        if package_presence == "omit" and package_visible is not False:
            errors.append(f"{label} omitted package must not be visible")
        if package_visible is False:
            if package_variant != "none" or package_scale_role != "none":
                errors.append(f"{label} hidden package must use variant/scale role 'none'")
        elif package_visible is True:
            if package_variant == "none" or package_scale_role == "none":
                errors.append(f"{label} visible package needs a real variant and scale role")
            integration_plan = record.get("integration_plan")
            if not isinstance(integration_plan, str) or not integration_plan.strip():
                errors.append(f"{label} visible package requires integration_plan")
        if package_variant == "inner" and not has_pack_inner_ref:
            errors.append(f"{label} inner package requires a PACK_INNER source_ref")
        if package_visible is True and package_variant == "outer" and not has_pack_outer_ref:
            errors.append(f"{label} visible outer package requires a PACK_FRONT/PACK_OTHER source_ref")
        if slot == 0 and not has_pack_front_ref:
            errors.append(f"{label} white-background packshot requires a PACK_FRONT source_ref")
        if slot in {0, 2, 9} and package_presence != "required":
            errors.append(f"{label} fixed identity slot requires package_presence 'required'")

        headline = record.get("headline")
        subline = record.get("subline")
        if slot == 0:
            if headline not in (None, "") or subline not in (None, ""):
                errors.append(f"{label} white-background packshot must not add marketing copy")
        elif 1 <= slot <= 5:
            if not isinstance(headline, str) or not headline.strip():
                errors.append(f"{label} main image missing headline")
            elif not (
                4 <= _visible_character_count(headline) <= 12
                and 4 <= _meaningful_character_count(headline) <= 12
            ):
                errors.append(f"{label} main headline must contain 4-12 visible characters")
            if not isinstance(subline, str) or not subline.strip():
                errors.append(f"{label} main image missing explanatory subline")
            elif not (
                8 <= _visible_character_count(subline) <= 24
                and 8 <= _meaningful_character_count(subline) <= 24
            ):
                errors.append(f"{label} main subline must contain 8-24 visible characters")
        else:
            if not isinstance(headline, str) or not headline.strip():
                errors.append(f"{label} detail module missing headline")
            elif not (
                4 <= _visible_character_count(headline) <= 18
                and 4 <= _meaningful_character_count(headline) <= 18
            ):
                errors.append(f"{label} detail headline must contain 4-18 meaningful characters")
            explanation_fields = (
                record.get("subline"),
                record.get("proof"),
                record.get("body"),
                record.get("description"),
                record.get("detail_layers"),
            )
            if sum(_meaningful_content_count(value) for value in explanation_fields) < 8:
                errors.append(
                    f"{label} detail module needs at least 8 meaningful explanation characters"
                )
            detail_layout = record.get("detail_layout")
            if not isinstance(detail_layout, str) or not detail_layout.strip():
                errors.append(f"{label} detail module missing detail_layout")
            else:
                seen_detail_layouts.setdefault(set_id, set()).add(
                    " ".join(detail_layout.casefold().split())
                )
        if slot > 0:
            typography_direction = record.get("typography_direction")
            if not isinstance(typography_direction, str) or not typography_direction.strip():
                errors.append(f"{label} missing typography_direction")
            else:
                seen_typography_directions.setdefault(set_id, set()).add(
                    " ".join(typography_direction.casefold().split())
                )
            if isinstance(headline, str) and headline.strip():
                normalized_headline = " ".join(headline.casefold().split())
                prior_asset = seen_headlines.setdefault(set_id, {}).get(normalized_headline)
                if prior_asset:
                    errors.append(f"{label} duplicates headline from {prior_asset}")
                else:
                    seen_headlines[set_id][normalized_headline] = asset_id

        visible_copy_fields = (
            record.get("headline"),
            record.get("subline"),
            record.get("kicker"),
            record.get("proof"),
            record.get("body"),
            record.get("description"),
            record.get("detail_layers"),
            record.get("spec_fields"),
            record.get("steps"),
            record.get("inspiration_panels"),
        )
        for visible_text in _iter_strings(visible_copy_fields):
            lowered_text = visible_text.casefold()
            matched_term = next(
                (term for term in FORBIDDEN_VISIBLE_TERMS if term in lowered_text),
                None,
            )
            if matched_term:
                errors.append(
                    f"{label} user-visible copy contains forbidden placeholder term {matched_term!r}"
                )
                break
        spec_fields = record.get("spec_fields")
        if any("?" in text or "？" in text for text in _iter_strings(spec_fields)):
            errors.append(f"{label} spec_fields contain a question-mark placeholder")
        if spec_fields is not None:
            if not isinstance(spec_fields, dict) or not spec_fields:
                errors.append(f"{label} spec_fields must be a non-empty object when present")
            elif any(
                not isinstance(key, str)
                or _meaningful_character_count(key) < 1
                or not _has_meaningful_content(value)
                for key, value in spec_fields.items()
            ):
                errors.append(f"{label} spec_fields contain an empty label or value")
        steps = record.get("steps")
        if _has_meaningful_content(steps):
            valid_evidence_key_list = evidence_keys if isinstance(evidence_keys, list) else []
            step_fact_domains = {
                fact_domain_by_key.get(key)
                for key in valid_evidence_key_list
                if isinstance(key, str)
            }
            if not step_fact_domains.intersection(
                {"serving_method", "process", "process_parameter"}
            ):
                errors.append(
                    f"{label} numbered steps require serving_method or process evidence"
                )

        output_path = record.get("output_path")
        if output_path != expected[asset_id]:
            errors.append(
                f"{label} output_path {output_path!r} does not match {expected[asset_id]!r}"
            )

    missing_ids = sorted(set(expected) - seen_ids)
    if missing_ids:
        errors.append(f"manifest.json: missing asset records: {', '.join(missing_ids)}")
    if len(assets) != len(expected):
        errors.append(
            f"manifest.json: has {len(assets)} asset records; expected {len(expected)}"
        )
    for set_id, count in visible_package_counts.items():
        if count > MAX_VISIBLE_PACKAGES_PER_SET:
            errors.append(
                f"manifest.json: {set_id} has {count} visible packages; maximum is {MAX_VISIBLE_PACKAGES_PER_SET}"
            )
    for set_id in (f"SET_{index:02d}" for index in range(1, set_count + 1)):
        if len(seen_detail_layouts.get(set_id, set())) < 3:
            errors.append(f"manifest.json: {set_id} needs at least three distinct detail_layout values")
        if len(seen_typography_directions.get(set_id, set())) > 1:
            errors.append(f"manifest.json: {set_id} must use one typography_direction")
    return errors


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    if args.sets < 1:
        print("error: --sets must be at least 1", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"error: output root is not a directory: {root}", file=sys.stderr)
        return 2
    if not 0 <= args.ratio_tolerance <= 0.1:
        print("error: --ratio-tolerance must be between 0 and 0.1", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    checked = 0
    expected_names = {asset.filename for asset in ASSETS}

    expected_set_names = {f"SET_{index:02d}" for index in range(1, args.sets + 1)}
    actual_set_names = {
        path.name
        for path in root.iterdir()
        if path.is_dir() and path.name.startswith("SET_")
    }
    unexpected_sets = sorted(actual_set_names - expected_set_names)
    if unexpected_sets:
        errors.append(f"unexpected set directories: {', '.join(unexpected_sets)}")

    for index in range(1, args.sets + 1):
        set_name = f"SET_{index:02d}"
        set_dir = root / set_name
        if not set_dir.is_dir():
            errors.append(f"{set_name}: missing directory")
            continue

        actual_names = {path.name for path in set_dir.glob("*.png") if path.is_file()}
        extra = sorted(actual_names - expected_names)
        if extra:
            message = f"{set_name}: extra PNG files: {', '.join(extra)}"
            if args.allow_extra_images:
                warnings.append(message)
            else:
                errors.append(message)

        seen_image_hashes: dict[str, str] = {}
        for asset in ASSETS:
            path = set_dir / asset.filename
            if not path.is_file():
                errors.append(f"{set_name}/{asset.filename}: missing")
                continue
            try:
                width, height = validate_png(path)
            except (OSError, PngValidationError) as exc:
                errors.append(f"{set_name}/{asset.filename}: {exc}")
                continue
            checked += 1
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            prior_filename = seen_image_hashes.get(digest)
            if prior_filename:
                errors.append(
                    f"{set_name}/{asset.filename}: exact duplicate image of {prior_filename}"
                )
            else:
                seen_image_hashes[digest] = asset.filename
            actual_ratio = width / height
            if abs(actual_ratio - asset.ratio) > args.ratio_tolerance:
                errors.append(
                    f"{set_name}/{asset.filename}: ratio {width}:{height} "
                    f"({actual_ratio:.4f}) expected {asset.ratio:.4f}"
                )

    expected_total = args.sets * len(ASSETS)
    if args.strict_manifest:
        errors.extend(validate_manifest(root, args.sets))
    print(f"checked {checked}/{expected_total} expected images under {root}")
    for warning in warnings:
        print(f"warning: {warning}")
    if errors:
        for error in errors:
            print(f"error: {error}")
        print(f"FAIL: {len(errors)} issue(s)")
        return 1
    success = "filenames, count, PNG readability, and aspect ratios are valid"
    if args.strict_manifest:
        success += "; manifest records are complete and contain no pending states"
    print(f"PASS: {success}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
