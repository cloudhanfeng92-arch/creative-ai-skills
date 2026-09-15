# LibTV execution contract

Use the installed `libtv` CLI only. Never invent HTTP requests or switch to the web UI.

## Preconditions

1. Confirm `libtv` is installed and logged in.
2. Work inside the intended canvas directory.
3. Confirm a canvas is bound with `libtv project use <canvas-uuid>` or pass `-p <canvas-uuid>` explicitly.
4. Use unique node names for each run.

## Resolve live model names and schemas

```bash
libtv model search --type image "Lib Image"
libtv model search --type image "GPT Image 2"
libtv model search --type image "General image Pro"
libtv model search --type video "Seedance 2.0"

libtv model "<exact image model name>"
libtv model "<exact video model name>"
```

Use the exact display name returned by search in `-s "model=..."`. Derive parameter names and accepted values from the live schema. Do not assume a historical model key is still valid.

## Upload character reference

```bash
libtv upload "角色参考-<run-id>" -t image --resource "/absolute/path/to/character.png"
```

## Generate the design reference

For `Lib Image`, the usual schema supports `ratio`, `quality`, and `resolution`:

```bash
libtv node create "机甲设定-<run-id>" -t image \
  --left "角色参考-<run-id>" \
  --prompt "<approved image prompt>" \
  -s "model=<resolved primary image model name>" \
  -s ratio=16:9 -s quality=high -s resolution=2K \
  --run
```

For `General image Pro`, use only fields accepted by its live schema; its resolution field may be named `quality`:

```bash
libtv node create "机甲设定-<run-id>" -t image \
  --left "角色参考-<run-id>" \
  --prompt "<approved image prompt>" \
  -s "model=<resolved fallback image model name>" \
  -s ratio=16:9 -s quality=2K -s searchable=0 \
  --run
```

Do not run either command until the user approves the image cost and exact prompt.

## Generate the 15-second video

Connect both references. The prompt must identify the character upload as `@image_1` and the generated design as `@image_2`.

```bash
libtv node create "机甲变身视频-<run-id>" -t video \
  --left "角色参考-<run-id>" \
  --left "机甲设定-<run-id>" \
  --prompt "<approved locked video prompt>" \
  -s "model=<resolved Seedance 2.0 display name>" \
  -s modeType=mixed2video \
  -s count=1 \
  -s ratio=16:9 \
  -s resolution=720p \
  -s duration=15 \
  -s enableSound=on \
  -s search_enabled=1 \
  --run
```

Do not run until the user separately approves the video cost and exact prompt.

`--run` is synchronous. Wait for the process to exit and read its terminal JSON. Do not add an external poller, background execution, or timeout.

If Seedance compliance validation rejects a human reference, report the exact failure. Do not bypass or replace the identity reference without user direction.

