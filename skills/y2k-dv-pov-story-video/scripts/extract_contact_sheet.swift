#!/usr/bin/env swift
import Foundation
import AVFoundation
import AppKit

guard CommandLine.arguments.count == 3 || CommandLine.arguments.count == 4 else {
    fputs("usage: extract_contact_sheet.swift input.mp4 output.jpg [frame_count]\n", stderr)
    exit(2)
}

let input = URL(fileURLWithPath: CommandLine.arguments[1])
let output = URL(fileURLWithPath: CommandLine.arguments[2])
let count = max(1, CommandLine.arguments.count == 4 ? (Int(CommandLine.arguments[3]) ?? 12) : 12)
let asset = AVURLAsset(url: input)
let duration = CMTimeGetSeconds(asset.duration)
guard duration.isFinite && duration > 0 else {
    fputs("could not read a positive video duration\n", stderr)
    exit(1)
}

let generator = AVAssetImageGenerator(asset: asset)
generator.appliesPreferredTrackTransform = true
generator.requestedTimeToleranceBefore = .zero
generator.requestedTimeToleranceAfter = .zero
generator.maximumSize = CGSize(width: 480, height: 480)

var frames: [(NSImage, Double)] = []
for index in 0..<count {
    let second = duration * (Double(index) + 0.5) / Double(count)
    do {
        let cg = try generator.copyCGImage(
            at: CMTime(seconds: second, preferredTimescale: 600),
            actualTime: nil
        )
        frames.append((NSImage(cgImage: cg, size: .zero), second))
    } catch {
        fputs("frame \(index + 1) failed: \(error)\n", stderr)
    }
}

guard let first = frames.first else {
    fputs("no frames could be extracted\n", stderr)
    exit(1)
}

let portrait = first.0.size.height > first.0.size.width
let columns = portrait ? 4 : 3
let rows = Int(ceil(Double(frames.count) / Double(columns)))
let cellWidth: CGFloat = portrait ? 300 : 420
let cellHeight: CGFloat = portrait ? 540 : 260
let size = CGSize(width: cellWidth * CGFloat(columns), height: cellHeight * CGFloat(rows))
let canvas = NSImage(size: size)

canvas.lockFocus()
NSColor.black.setFill()
NSRect(origin: .zero, size: size).fill()
let labelAttributes: [NSAttributedString.Key: Any] = [
    .font: NSFont.monospacedSystemFont(ofSize: 20, weight: .semibold),
    .foregroundColor: NSColor.white,
    .backgroundColor: NSColor.black.withAlphaComponent(0.65)
]

for (index, frame) in frames.enumerated() {
    let column = index % columns
    let row = rows - 1 - index / columns
    let rect = NSRect(
        x: CGFloat(column) * cellWidth,
        y: CGFloat(row) * cellHeight,
        width: cellWidth,
        height: cellHeight
    )
    frame.0.draw(
        in: rect,
        from: .zero,
        operation: .copy,
        fraction: 1.0,
        respectFlipped: true,
        hints: [.interpolation: NSImageInterpolation.high]
    )
    String(format: " %02d  %.1fs ", index + 1, frame.1)
        .draw(at: NSPoint(x: rect.minX + 8, y: rect.minY + 8), withAttributes: labelAttributes)
}
canvas.unlockFocus()

guard let tiff = canvas.tiffRepresentation,
      let bitmap = NSBitmapImageRep(data: tiff),
      let jpeg = bitmap.representation(using: .jpeg, properties: [.compressionFactor: 0.88]) else {
    fputs("could not encode contact sheet\n", stderr)
    exit(1)
}

do {
    try jpeg.write(to: output)
    print("duration=\(String(format: "%.3f", duration)) frames=\(frames.count) output=\(output.path)")
} catch {
    fputs("could not write output: \(error)\n", stderr)
    exit(1)
}
