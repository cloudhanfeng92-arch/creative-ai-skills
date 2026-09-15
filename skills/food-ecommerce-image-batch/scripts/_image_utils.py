"""Small dependency-free image checks shared by the skill helpers."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_FILE_BYTES = 512 * 1024 * 1024
MAX_DIMENSION = 32768
MAX_DECODED_BYTES = 512 * 1024 * 1024
COLOR_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
VALID_DEPTHS = {
    0: {1, 2, 4, 8, 16},
    2: {8, 16},
    3: {1, 2, 4, 8},
    4: {8, 16},
    6: {8, 16},
}


class PngValidationError(ValueError):
    """Raised when a PNG is structurally invalid or has no decodable pixels."""


def validate_png(path: Path) -> tuple[int, int]:
    """Validate PNG chunks, CRCs, zlib data, scanline size, and dimensions."""

    try:
        file_size = path.stat().st_size
        if file_size > MAX_FILE_BYTES:
            raise PngValidationError(
                f"PNG file is too large for validation ({file_size} bytes; max {MAX_FILE_BYTES})"
            )
        blob = path.read_bytes()
    except OSError as exc:
        raise PngValidationError(str(exc)) from exc
    if not blob.startswith(PNG_SIGNATURE):
        raise PngValidationError("invalid PNG signature")

    offset = len(PNG_SIGNATURE)
    width = height = bit_depth = color_type = interlace = None
    seen_ihdr = seen_plte = seen_idat = seen_iend = False
    idat_parts: list[bytes] = []

    while offset < len(blob):
        if offset + 12 > len(blob):
            raise PngValidationError("truncated PNG chunk")
        length = struct.unpack(">I", blob[offset : offset + 4])[0]
        chunk_end = offset + 12 + length
        if chunk_end > len(blob):
            raise PngValidationError("PNG chunk length exceeds file size")
        chunk_type = blob[offset + 4 : offset + 8]
        payload = blob[offset + 8 : offset + 8 + length]
        expected_crc = struct.unpack(">I", blob[offset + 8 + length : chunk_end])[0]
        actual_crc = zlib.crc32(chunk_type + payload) & 0xFFFFFFFF
        if expected_crc != actual_crc:
            label = chunk_type.decode("ascii", errors="replace")
            raise PngValidationError(f"CRC mismatch in {label} chunk")

        if not seen_ihdr and chunk_type != b"IHDR":
            raise PngValidationError("IHDR must be the first PNG chunk")
        if chunk_type == b"IHDR":
            if seen_ihdr or length != 13:
                raise PngValidationError("invalid or duplicate IHDR")
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
            if width <= 0 or height <= 0:
                raise PngValidationError("invalid PNG dimensions")
            if width > MAX_DIMENSION or height > MAX_DIMENSION:
                raise PngValidationError(
                    f"PNG dimensions exceed the supported maximum of {MAX_DIMENSION}px"
                )
            if color_type not in VALID_DEPTHS or bit_depth not in VALID_DEPTHS[color_type]:
                raise PngValidationError("unsupported PNG color type or bit depth")
            if compression != 0 or filter_method != 0:
                raise PngValidationError("unsupported PNG compression, filter, or interlace method")
            if interlace != 0:
                raise PngValidationError(
                    "interlaced PNG is not supported by this validator; normalize it first"
                )
            seen_ihdr = True
        elif chunk_type == b"PLTE":
            if seen_plte or seen_idat or color_type in {0, 4} or length < 3 or length > 768 or length % 3:
                raise PngValidationError("invalid PLTE chunk")
            if color_type == 3 and length // 3 > 2**bit_depth:
                raise PngValidationError("PLTE has more entries than the indexed bit depth allows")
            seen_plte = True
        elif chunk_type == b"IDAT":
            if not seen_ihdr or seen_iend:
                raise PngValidationError("IDAT appears in an invalid position")
            if color_type == 3 and not seen_plte:
                raise PngValidationError("indexed-color PNG is missing PLTE before IDAT")
            seen_idat = True
            idat_parts.append(payload)
        elif chunk_type == b"IEND":
            if length != 0 or not seen_idat:
                raise PngValidationError("invalid IEND or missing IDAT")
            seen_iend = True
            offset = chunk_end
            break
        offset = chunk_end

    if not (seen_ihdr and seen_idat and seen_iend):
        raise PngValidationError("PNG is missing IHDR, IDAT, or IEND")
    if blob[offset:].strip(b"\x00\r\n\t "):
        raise PngValidationError("unexpected non-padding data after IEND")

    assert width is not None
    assert height is not None
    assert bit_depth is not None
    assert color_type is not None
    assert interlace is not None
    channels = COLOR_CHANNELS[color_type]
    row_bytes = (width * channels * bit_depth + 7) // 8
    expected_length = height * (row_bytes + 1)
    if expected_length > MAX_DECODED_BYTES:
        raise PngValidationError(
            f"decoded pixel stream would exceed {MAX_DECODED_BYTES} bytes"
        )
    try:
        decompressor = zlib.decompressobj()
        pixels = decompressor.decompress(b"".join(idat_parts), expected_length + 1)
        if len(pixels) > expected_length or decompressor.unconsumed_tail:
            raise PngValidationError("decoded pixel stream exceeds the dimensions declared in IHDR")
        pixels += decompressor.flush(expected_length + 1 - len(pixels))
    except zlib.error as exc:
        raise PngValidationError(f"invalid compressed pixel data: {exc}") from exc
    if not decompressor.eof or decompressor.unused_data or decompressor.unconsumed_tail:
        raise PngValidationError("compressed pixel stream is truncated or has trailing data")
    if not pixels:
        raise PngValidationError("PNG contains no decoded scanlines")
    if len(pixels) != expected_length:
        raise PngValidationError(
            f"decoded scanline length {len(pixels)} does not match expected {expected_length}"
        )
    stride = row_bytes + 1
    if any(pixels[row * stride] > 4 for row in range(height)):
        raise PngValidationError("invalid PNG scanline filter byte")
    return width, height
