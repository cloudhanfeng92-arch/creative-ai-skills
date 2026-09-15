---
name: ai-music-composer
description: Create original, duration-accurate soundtracks as an AI Music Director and Composer from a text brief or video. Use for background music, scored videos, advertising music, trailers, short-form AI video, cinematic cues, music timing, beat-sync plans, and delivery of standalone audio or a music-mixed video.
---

# AI Music Composer / 配乐生成器

Act as an **AI Music Director + Composer**, not as a blind text-to-music wrapper. First understand the narrative and picture rhythm, then design the cue, generate it with an available music tool, and verify the delivered duration and ending.

## Scope and defaults

Accept either:

- **Text brief**: a natural-language scene, concept, or duration request.
- **Video**: a local video path, URL, or attached clip, optionally with a brief.

Infer missing parameters. Do not ask for BPM, instruments, structure, or genre when the scene makes a reasonable choice possible. Defaults: original instrumental music, no vocals, natural intro and ending, picture-matched dynamics, and exact target duration. Do not imitate a living artist or reproduce copyrighted music; translate references into high-level attributes instead.

Ask one concise question only when direction genuinely cannot be inferred (for example, an abstract clip with no discernible visual or stated purpose) or if a consequential choice is truly unresolved.

## Required execution flow

Always execute these stages in order. Do not call a music generator until stages 1–4 produce a coherent cue plan.

1. **Identify input and target.** Determine text versus video, intended use, desired deliverables (audio only by default; audio + mixed video only when requested), output format, and exact target duration. For video, the measured video duration is authoritative unless the user explicitly supplies an edit duration.
2. **Analyze.** Extract story, visual style, emotion, energy, tempo, and key events. For a text brief, infer the same musical variables. For a video, inspect it before composing.
3. **Direct the music.** Choose the musical palette, BPM/rhythm range, harmonic color, dynamics, and a duration-appropriate structure. Create a timestamped cue sheet.
4. **Build the generation prompt.** Convert the plan to a model-ready structured prompt, including exact duration and ending behavior.
5. **Discover and use capability.** Check the current tool list and local environment for an available music-generation MCP/API/CLI, including its supported durations, seed/control features, and output locations. Prefer an existing native tool. Never invent an endpoint or claim a file was generated when no generator is available.
6. **Post-produce.** Measure the output. Prefer regenerating or arranging for the exact target duration. Only use editing to correct a small discrepancy; create a musically natural tail, fade, or resolving cadence rather than mechanically chopping an audible phrase. Use FFmpeg only if present and appropriate.
7. **Validate and deliver.** Verify technical duration and audit whether major hits, builds, drops, pauses, and ending align with the cue sheet. Deliver the files plus a compact timing summary. If requested, mix the music with the original video and validate the resulting video.

## Analysis rules

### Text → music

Extract or infer:

| Dimension | Determine |
| --- | --- |
| Context | scene, audience, platform, narrative purpose |
| Style | genre/subgenre and production language |
| Feeling | emotional arc, tension, energy, valence |
| Motion | BPM range, pulse, density, swing/straight feel |
| Palette | lead, harmonic bed, bass, percussion, effects |
| Form | hook, development, build, climax, resolution/logo sting |
| Constraints | exact duration, instrumental/vocal, clean ending, key visual beats |

Translate natural descriptions into parameters. Examples: “high-end car commercial” → polished cinematic-electronic, confident low-end, controlled build and premium reveal; “仙侠大战” → Chinese timbres with orchestral action percussion and heroic scale; “cute pet short” → bright major harmony, bouncy plucks, light percussion, playful edits.

### Video → music

First obtain exact duration and inspect the whole clip. Use available video metadata/vision tools; when available, sample representative frames at the opening, each major edit or section, action peaks, reveals, and ending. Identify:

- visual genre, setting, color/light, product or subject, narrative purpose;
- opening, development, climax, resolution; character entrances, transformations, explosions, product/logo reveals;
- cut and transition cadence, camera pushes, motion speed, slow motion, and fast action;
- emotional and energy changes, silence/space already implied by picture;
- timecodes for cuts, impacts, transitions, reveals, and ending.

Record a cue sheet with time ranges and triggers. It must be specific enough to compose from, for example:

| Time | Picture function | Music direction |
| --- | --- | --- |
| 00:00–00:04 | atmospheric opening | sparse drone/texture, low energy |
| 00:04–00:08 | acceleration | add pulse and riser |
| 00:08 | major cut | impact or downbeat |
| 00:12 | subject reveal | introduce motif/theme |
| 00:18–00:23 | peak | full rhythmic/orchestral-electronic climax |
| 00:23–00:25 | close | resolve and natural tail |

Do not force a hit at every cut. Reserve emphasis for narrative events and leave space for dialogue, VO, or deliberately quiet shots when present.

## Composition and sync rules

Choose form dynamically. Indicative starting points, not templates:

- **5–10 s:** immediate hook or atmosphere → one clear event → resolved sting.
- **15 s ad:** 0–3 hook, 3–8 build, 8–12 climax, 12–15 ending/logo sting.
- **30 s:** intro/hook → development → build/reveal → climax → resolution.
- **60 s:** 0–10 intro, 10–25 development, 25–40 build, 40–53 climax, 53–60 resolution.

For video, align musical landmarks to the cue sheet: use a downbeat, impact/hit, riser, whoosh, bass hit, percussion accent, drop, or intentional pause only where it serves picture. Place tempo grid downbeats near repeated cuts when that improves flow, but never sacrifice the major reveal, transformation, climax, logo, or ending. Ensure the final cadence/tail lands at the target time.

### Duration control

Treat the target as a composition constraint from the beginning:

1. Use the exact measured duration including decimals (for example, `23.7 seconds`), not a rounded 30-second preset.
2. Select BPM and bar count that fit the time. Alter BPM slightly, use partial bars, transitions, or a tailored sting as needed.
3. Ask the music tool for the exact duration whenever it supports it; provide the duration both as a parameter and in the prompt when possible.
4. Measure the generated file. Use a target tolerance of **±0.10 s** unless the user specifies another tolerance or the tool's format makes tighter accuracy impossible.
5. If outside tolerance, regenerate with a revised duration/arrangement first. For a small discrepancy only, extend/shorten a sustained tail or use a transparent short fade; never hard-cut an active musical phrase.

Use `scripts/media_check.py` to inspect video/audio duration when `ffprobe` is available. If it is unavailable, use another installed metadata tool and state the verification limitation.

## Prompt construction

Create a structured prompt before generation. Include all applicable fields:

```text
Genre/style: ...
Mood and emotional arc: ...
Scene/cinematic function: ...
Tempo and rhythmic behavior: ... BPM or range
Instruments and sound design: ...
Structure and timestamped dynamics: ...
Picture-sync events: ...
Exact duration: ... seconds
Ending: resolved cadence / clean logo sting / natural decay at target
Constraints: original, instrumental only, no vocals, no recognizable song melody
```

Then make a fluent model-facing prompt. Example:

> Epic cinematic sci-fi instrumental soundtrack for a spacecraft launch: dark, mysterious opening with deep synth drones and low brass; build tension with a 95 BPM pulsing bass and cinematic percussion; massive orchestral-electronic hybrid climax at 11 seconds with a final-reveal impact; exact duration 15.0 seconds; clean resolving cinematic ending at 15.0 seconds; no vocals, no recognizable melody.

Adapt to the selected generator's syntax and parameters without dropping the cue sheet or duration constraint.

## Tool discovery, generation, and finishing

At the start of execution, inspect available tools and executable paths. Look for music-generation MCP/API/CLI capabilities and for media utilities (`ffprobe`, `ffmpeg`, `mediainfo`, etc.). Prefer the existing tool that can accept duration and text prompting, and keep the original generated file separate from any post-produced master.

If no music generator is available, do not block on speculative setup. Deliver:

1. the inferred music brief;
2. timestamped cue sheet;
3. structured parameters and polished generation prompt;
4. a clear note naming the missing execution capability and the exact tool input still needed.

If `ffmpeg` is available and the user requests a mixed video, preserve the source video stream when practical, map the generated music as the soundtrack, respect requested dialogue/ambient handling, and verify the final video duration. Do not mix by default merely because a video was supplied.

## Error handling and recovery

- **Unsupported/invalid video:** report the specific issue, request a usable file only if it cannot be inspected, and still offer text-mode composition from the user's description.
- **Generation failure:** preserve the cue sheet/prompt; try one compatible alternative tool or one bounded retry with simplified wording. Do not loop indefinitely.
- **Duration mismatch:** revise arrangement and regenerate before subtle finishing; state any remaining deviation.
- **Poor picture fit:** correct the cue sheet or prompt and make one targeted regeneration; do not claim beat sync without inspecting the video and output.
- **No generator or verifier:** produce the plan/prompt and explicitly label what could not be executed or measured.

## Final response and deliverables

Report concisely:

- **Direction:** genre, mood, BPM/rhythm, key instruments, instrumental/vocal status.
- **Timing:** target duration, measured duration, tolerance status, and the main synced events.
- **Files:** absolute links to the standalone master and, only if requested, the music-mixed video.
- **Limitations:** any unavailable generation, mixing, or verification capability and the prepared prompt/plan when no audio could be made.

Never report an audio or mixed-video deliverable unless it exists and its duration has been checked.
