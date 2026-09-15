#!/usr/bin/env python3
"""Read-only structural and numeric checks for a story-video Master Timeline.

This tool does not inspect media, call a network service, or modify the input.
Only an explicitly requested --output report may be written.
"""

import argparse
import json
import math
from pathlib import Path
import sys


STAGES = ("pre_video", "post_video", "pre_compose")
NOTICE = (
    "仅校验 Master Timeline 的结构与数值；通过不代表故事语义、画面内容、"
    "媒体文件、口型、实际音频时长、听审或最终 QC 已通过。"
    "measured 状态和时长由输入提供，本工具不探测或认证媒体。"
)


def finite_number(value):
    """JSON numbers only; bool is deliberately excluded."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, TypeError):
        return False


def nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


class Validator:
    def __init__(self, stage):
        self.stage = stage
        self.errors = []
        self.epsilon = None
        self.duration = None
        self.shots = []
        self.audio = []

    def error(self, code, path, message):
        self.errors.append({"code": code, "path": path, "message": message})

    def required(self, item, key, path):
        if key not in item:
            self.error("missing_field", path + "." + key, "缺少必填字段。")
            return False
        return True

    def string(self, item, key, path, nonempty=False):
        if not self.required(item, key, path):
            return False
        value = item[key]
        if not isinstance(value, str) or (nonempty and not value.strip()):
            label = "非空字符串" if nonempty else "字符串"
            self.error("invalid_string", path + "." + key, "必须是" + label + "。")
            return False
        return True

    def number(self, item, key, path, minimum=None, positive=False, nullable=False):
        if not self.required(item, key, path):
            return False
        value = item[key]
        if nullable and value is None:
            return True
        if not finite_number(value):
            self.error("invalid_number", path + "." + key,
                       "必须是有限数值，不能用布尔值、NaN 或 Infinity。")
            return False
        if positive and value <= 0:
            self.error("nonpositive_number", path + "." + key, "必须大于 0。")
            return False
        if minimum is not None and value < minimum:
            self.error("number_below_minimum", path + "." + key,
                       "必须大于或等于 {}。".format(minimum))
            return False
        return True

    def array(self, item, key, path, nonempty=False):
        if not self.required(item, key, path):
            return False
        value = item[key]
        if not isinstance(value, list) or (nonempty and not value):
            self.error("invalid_array", path + "." + key,
                       "必须是{}数组。".format("非空" if nonempty else ""))
            return False
        return True

    def string_array(self, item, key, path, nonempty=False):
        if not self.array(item, key, path, nonempty):
            return False
        valid = True
        seen = set()
        for index, value in enumerate(item[key]):
            value_path = "{}.{}[{}]".format(path, key, index)
            if not nonempty_string(value):
                self.error("invalid_identifier", value_path, "必须是非空字符串 ID。")
                valid = False
            elif value in seen:
                self.error("duplicate_reference", value_path, "同一数组中的 ID 不可重复。")
                valid = False
            else:
                seen.add(value)
        return valid

    def interval(self, item, path, duration_required=False):
        start_ok = self.number(item, "Start_Time", path)
        end_ok = self.number(item, "End_Time", path)
        duration_ok = True
        if duration_required:
            duration_ok = self.number(item, "Duration", path, positive=True)
        if not (start_ok and end_ok):
            return False
        start, end = item["Start_Time"], item["End_Time"]
        if end <= start:
            self.error("empty_or_reversed_interval", path, "End_Time 必须大于 Start_Time。")
            return False
        if self.epsilon is not None:
            if start < -self.epsilon:
                self.error("negative_start", path + ".Start_Time", "事件或镜头不能早于全片起点 0。")
            if self.duration is not None and end > self.duration + self.epsilon:
                self.error("timeline_overflow", path + ".End_Time", "结束时间超出全片 Duration。")
            if duration_required and duration_ok:
                if abs(item["Duration"] - (end - start)) > self.epsilon:
                    self.error("duration_mismatch", path + ".Duration",
                               "Duration 必须等于 End_Time - Start_Time（容差一帧）。")
        return True

    def source_timing(self, item, path, interval_ok):
        keys = ("Source_In", "Source_Out", "Playback_Rate")
        if not any(key in item for key in keys):
            return  # Source timing metadata is optional for this helper.
        checks = [
            self.number(item, "Source_In", path, minimum=0),
            self.number(item, "Source_Out", path),
            self.number(item, "Playback_Rate", path, positive=True),
        ]
        if not all(checks):
            return
        if item["Source_Out"] <= item["Source_In"]:
            self.error("invalid_source_interval", path + ".Source_Out",
                       "Source_Out 必须大于 Source_In。")
            return
        try:
            source_duration = (item["Source_Out"] - item["Source_In"]) / item["Playback_Rate"]
            if not finite_number(source_duration):
                raise OverflowError("变速后的源片时长超出有限数值范围。")
            if interval_ok:
                used_duration = item["End_Time"] - item["Start_Time"]
                if not finite_number(used_duration):
                    raise OverflowError("使用区间时长超出有限数值范围。")
                if self.epsilon is not None and abs(source_duration - used_duration) > self.epsilon:
                    self.error("source_duration_mismatch", path,
                               "(Source_Out - Source_In) / Playback_Rate 必须等于 End_Time - Start_Time（容差一帧）。")
        except (OverflowError, ZeroDivisionError) as exc:
            self.error("source_timing_overflow", path, str(exc))

    def validate(self, data):
        if not isinstance(data, dict):
            self.error("invalid_root", "$", "顶层必须是 JSON 对象。")
            return
        self.string(data, "Timeline_ID", "$", nonempty=True)
        for key in ("Revision", "FPS"):
            if self.required(data, key, "$"):
                value = data[key]
                if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                    self.error("invalid_positive_integer", "$." + key, "必须是正整数，不能是布尔值。")
                elif key == "FPS":
                    try:
                        self.epsilon = 1.0 / value
                    except OverflowError:
                        self.error("fps_out_of_range", "$.FPS", "FPS 超出本校验器可计算的数值范围。")
        if self.number(data, "Duration", "$", positive=True):
            self.duration = data["Duration"]
        shots_ok = self.array(data, "Shots", "$", nonempty=True)
        audio_ok = self.array(data, "Audio_Events", "$")
        if shots_ok:
            self.validate_shots(data["Shots"])
            self.validate_generation_clips()
        if audio_ok:
            self.validate_audio(data["Audio_Events"])
        if shots_ok and self.epsilon is not None:
            self.validate_coverage()
        if shots_ok and audio_ok and self.epsilon is not None:
            self.validate_bindings()
            self.validate_speech_overlap()
            if self.stage == "pre_compose":
                self.validate_measured_totals()

    def validate_shots(self, shots):
        seen = set()
        for index, shot in enumerate(shots):
            path = "$.Shots[{}]".format(index)
            if not isinstance(shot, dict):
                self.error("invalid_shot", path, "镜头必须是对象。")
                continue
            id_ok = self.string(shot, "Shot_ID", path, nonempty=True)
            if id_ok:
                if shot["Shot_ID"] in seen:
                    self.error("duplicate_shot_id", path + ".Shot_ID", "Shot_ID 必须全片唯一。")
                seen.add(shot["Shot_ID"])
            interval_ok = self.interval(shot, path, duration_required=True)
            if shot.get("Video") is not None:
                self.source_timing(shot, path, interval_ok)
            for key in ("Narration_Text", "Camera_Movement", "Character_Action",
                        "Performance_Beat", "Visual_Evidence"):
                self.string(shot, key, path)
            for key in ("Beat_ID", "Generation_Clip_ID"):
                self.string(shot, key, path, nonempty=True)
            for key in ("Narration_Audio_Duration", "Dialogue_Audio_Duration"):
                self.number(shot, key, path, minimum=0, nullable=True)
            for key in ("Character_Dialogue", "Music", "SFX"):
                self.array(shot, key, path)
            characters_ok = self.string_array(shot, "Character_IDs", path)
            for key in ("Image", "Video"):
                if self.required(shot, key, path):
                    value = shot[key]
                    if not (value is None or nonempty_string(value)
                            or (isinstance(value, dict) and bool(value))):
                        self.error("invalid_resource_reference", path + "." + key,
                                   "必须为 null、非空资源引用字符串或非空资源引用对象。")
            if self.required(shot, "Transition", path) and not isinstance(shot["Transition"], dict):
                self.error("invalid_transition", path + ".Transition", "Transition 必须是对象。")
            self.shots.append({"value": shot, "path": path, "index": index,
                               "id_ok": id_ok, "interval_ok": interval_ok,
                               "characters_ok": characters_ok})

    def validate_generation_clips(self):
        """A Generation_Clip_ID must describe one consecutive run of shots."""
        closed = set()
        current = None
        for record in self.shots:
            shot, path = record["value"], record["path"]
            clip_id = shot.get("Generation_Clip_ID")
            if not nonempty_string(clip_id):
                continue
            if clip_id == current:
                continue
            if current is not None:
                closed.add(current)
            if clip_id in closed:
                self.error("noncontiguous_generation_clip", path + ".Generation_Clip_ID",
                           "同一 Generation_Clip_ID 必须对应数组中连续的一组 Shot，不能结束后再次出现。")
            current = clip_id

    def validate_audio(self, audio):
        seen = set()
        for index, event in enumerate(audio):
            path = "$.Audio_Events[{}]".format(index)
            if not isinstance(event, dict):
                self.error("invalid_audio_event", path, "音频事件必须是对象。")
                continue
            if self.string(event, "Audio_ID", path, nonempty=True):
                if event["Audio_ID"] in seen:
                    self.error("duplicate_audio_id", path + ".Audio_ID", "Audio_ID 必须全片唯一。")
                seen.add(event["Audio_ID"])
            kind_ok = self.string(event, "Kind", path, nonempty=True)
            if kind_ok and event["Kind"] not in ("narration", "dialogue", "music", "sfx"):
                self.error("invalid_audio_kind", path + ".Kind", "必须是 narration/dialogue/music/sfx。")
                kind_ok = False
            interval_ok = self.interval(event, path)
            self.source_timing(event, path, interval_ok)
            bindings_ok = self.string_array(event, "Shot_IDs", path, nonempty=True)
            voice = kind_ok and event["Kind"] in ("narration", "dialogue")
            self.string(event, "Text", path, nonempty=voice)
            status_ok = self.string(event, "Timing_Status", path, nonempty=True)
            if status_ok and event["Timing_Status"] not in ("estimated", "measured"):
                self.error("invalid_timing_status", path + ".Timing_Status", "必须是 estimated 或 measured。")
            if voice:
                self.string(event, "Voice_ID", path, nonempty=True)
                if self.stage == "pre_compose" and event.get("Timing_Status") != "measured":
                    self.error("unmeasured_speech", path + ".Timing_Status",
                               "pre_compose 阶段的全部旁白和对白必须为 measured。")
            if kind_ok and event["Kind"] == "dialogue":
                self.string(event, "Character_ID", path, nonempty=True)
            self.audio.append({"value": event, "path": path, "interval_ok": interval_ok,
                               "bindings_ok": bindings_ok, "kind_ok": kind_ok})

    def validate_coverage(self):
        valid = [record for record in self.shots if record["interval_ok"]]
        if len(valid) != len(self.shots) or not valid:
            return
        first, last = valid[0], valid[-1]
        if abs(first["value"]["Start_Time"]) > self.epsilon:
            self.error("timeline_start_gap", first["path"] + ".Start_Time", "第一个镜头必须从 0 开始。")
        for previous, current in zip(valid, valid[1:]):
            delta = current["value"]["Start_Time"] - previous["value"]["End_Time"]
            if abs(delta) > self.epsilon:
                self.error("shot_gap" if delta > 0 else "shot_overlap", current["path"] + ".Start_Time",
                           "镜头须按数组顺序连续覆盖时间轴；此处存在{}。".format("缺口" if delta > 0 else "重叠或乱序"))
        if self.duration is not None and abs(last["value"]["End_Time"] - self.duration) > self.epsilon:
            self.error("timeline_end_mismatch", last["path"] + ".End_Time", "最后一个镜头必须结束于全片 Duration。")

    @staticmethod
    def intersection(a, b):
        return max(0, min(a["End_Time"], b["End_Time"]) - max(a["Start_Time"], b["Start_Time"]))

    def validate_bindings(self):
        # Keep the first occurrence; duplicates are separately reported as errors.
        by_id = {}
        for record in self.shots:
            if record["id_ok"]:
                by_id.setdefault(record["value"]["Shot_ID"], record)
        for record in self.audio:
            event, path = record["value"], record["path"]
            if not record["bindings_ok"]:
                continue
            bound_intervals = []
            for index, shot_id in enumerate(event["Shot_IDs"]):
                ref_path = path + ".Shot_IDs[{}]".format(index)
                shot_record = by_id.get(shot_id)
                if shot_record is None:
                    self.error("unknown_shot_reference", ref_path, "引用的 Shot_ID 不存在。")
                    continue
                shot = shot_record["value"]
                if event.get("Kind") == "dialogue" and shot_record["characters_ok"]:
                    character = event.get("Character_ID")
                    if character not in shot["Character_IDs"]:
                        self.error("character_not_in_shot", ref_path,
                                   "对白 Character_ID 必须出现在每个绑定镜头的 Character_IDs 中。")
                if record["interval_ok"] and shot_record["interval_ok"]:
                    # Half-open intervals sharing only an endpoint do not intersect.
                    if self.intersection(event, shot) <= 0:
                        self.error("nonintersecting_shot_reference", ref_path,
                                   "绑定镜头必须与音频事件区间有正长度交集；仅端点接触不算交集。")
                    else:
                        bound_intervals.append((max(event["Start_Time"], shot["Start_Time"]),
                                                min(event["End_Time"], shot["End_Time"])))
            if event.get("Kind") in ("narration", "dialogue") and record["interval_ok"]:
                cursor = event["Start_Time"]
                for start, end in sorted(bound_intervals):
                    if start > cursor + self.epsilon:
                        self.error("speech_binding_gap", path + ".Shot_IDs",
                                   "人声事件区间必须被绑定镜头完整覆盖，不能跨越未绑定镜头。")
                        break
                    cursor = max(cursor, end)
                else:
                    if cursor < event["End_Time"] - self.epsilon:
                        self.error("speech_binding_gap", path + ".Shot_IDs",
                                   "人声事件区间必须被绑定镜头完整覆盖，不能跨越未绑定镜头。")

    def validate_speech_overlap(self):
        voice_events = sorted(
            (record for record in self.audio if record["interval_ok"]
             and record["value"].get("Kind") in ("narration", "dialogue")),
            key=lambda record: record["value"]["Start_Time"],
        )
        if not voice_events:
            return
        furthest = voice_events[0]
        for current in voice_events[1:]:
            if self.intersection(furthest["value"], current["value"]) > self.epsilon:
                self.error("speech_overlap", current["path"],
                           "旁白与对白共用不可重叠的人声时间线；与 {} 存在超过一帧的重叠。".format(furthest["path"]))
            if current["value"]["End_Time"] > furthest["value"]["End_Time"]:
                furthest = current

    def validate_measured_totals(self):
        for shot_record in self.shots:
            shot, path = shot_record["value"], shot_record["path"]
            if not (shot_record["interval_ok"] and shot_record["id_ok"]):
                continue
            for kind, key in (("narration", "Narration_Audio_Duration"),
                              ("dialogue", "Dialogue_Audio_Duration")):
                value = shot.get(key)
                if value is None:
                    self.error("missing_measured_duration", path + "." + key,
                               "pre_compose 阶段须填写实际时长；没有该类人声时填 0。")
                    continue
                if not finite_number(value):
                    continue  # Structural check already reports this value.
                total = sum(self.intersection(shot, record["value"])
                            for record in self.audio
                            if record["interval_ok"] and record["bindings_ok"]
                            and record["value"].get("Kind") == kind
                            and shot["Shot_ID"] in record["value"]["Shot_IDs"])
                if not finite_number(total) or abs(value - total) > self.epsilon:
                    self.error("measured_duration_mismatch", path + "." + key,
                               "应等于该镜头与绑定 {} 事件的交集时长之和（{} 秒，容差一帧）。".format(kind, total))


def reject_constant(value):
    raise ValueError("JSON 禁止使用非有限数值：" + value)


def parse_finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("JSON 数值超出有限浮点数范围：" + value)
    return result


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON 对象存在重复字段：" + key)
        result[key] = value
    return result


def same_file(source, target):
    if source.resolve() == target.resolve():
        return True
    return source.exists() and target.exists() and source.samefile(target)


class ReportingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        report = {
            "timeline_file": None, "stage": None, "result": "failed",
            "scope": "structural_and_numeric_only", "notice": NOTICE,
            "tolerance_seconds": None,
            "summary": {"shot_count": 0, "audio_event_count": 0, "error_count": 1},
            "errors": [{"code": "argument_error", "path": "arguments", "message": message}],
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        self.exit(1)


def main(argv=None):
    parser = ReportingArgumentParser(
        description="只读检查 Master Timeline JSON 的结构与数值；不探测媒体，不代表语义、听审或最终 QC 通过。",
        epilog=("所有时间单位为秒，区间为 [Start_Time, End_Time)，时间误差容限为 1/FPS。"
                "pre_video/post_video 允许 estimated 人声与 null 实际时长；"
                "pre_compose 要求 measured 人声及每镜实际时长交集总和。"
                "音频事件或含 Video 的镜头若提供 Source_In/Source_Out/Playback_Rate，"
                "须三项齐全且变速后的源片时长与使用区间一致。"
                "除 --help 外，报告以 JSON 输出；通过退出 0，参数、校验、读取、解析或报告写入失败退出 1。"),
    )
    parser.add_argument("timeline", type=Path, help="输入 Master Timeline JSON 文件路径（不会修改）。")
    parser.add_argument("--stage", required=True, choices=STAGES, help="当前执行阶段（必填）。")
    parser.add_argument("--output", type=Path, help="可选 JSON 报告路径；不能与输入指向同一文件。")
    args = parser.parse_args(argv)
    validator = Validator(args.stage)
    try:
        with args.timeline.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle, parse_constant=reject_constant,
                             parse_float=parse_finite_float, object_pairs_hook=unique_object)
        validator.validate(data)
    except (OSError, UnicodeError, ValueError, RecursionError, OverflowError) as exc:
        validator.error("input_read_or_parse_error", "$", str(exc))
    report = {
        "timeline_file": str(args.timeline),
        "stage": args.stage,
        "result": "failed" if validator.errors else "passed",
        "scope": "structural_and_numeric_only",
        "notice": NOTICE,
        "tolerance_seconds": validator.epsilon,
        "summary": {"shot_count": len(validator.shots), "audio_event_count": len(validator.audio),
                    "error_count": len(validator.errors)},
        "errors": validator.errors,
    }
    if args.output:
        try:
            if same_file(args.timeline, args.output):
                raise ValueError("报告输出不能覆盖输入 Master Timeline（包括符号链接或硬链接指向同一文件）。")
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                                   encoding="utf-8")
        except (OSError, ValueError, RuntimeError) as exc:
            validator.error("report_write_error", "--output", str(exc))
            report["result"] = "failed"
            report["summary"]["error_count"] = len(validator.errors)
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 1 if validator.errors else 0


if __name__ == "__main__":
    sys.exit(main())
