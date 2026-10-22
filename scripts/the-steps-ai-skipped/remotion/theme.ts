import type { CSSProperties } from "react";
import { Easing, interpolate, spring } from "remotion";

export const C = {
  bg: "#0B1220",
  panel: "#101A2B",
  panelAlt: "#0D1524",
  line: "#26354F",
  ink: "#E8EEF9",
  muted: "#93A4BE",
  dim: "#5D6E88",
  accent: "#8B93FF",
  teal: "#5EEAD4",
  amber: "#F5B84C",
  red: "#FF6B72",
} as const;

export const FONT = {
  serif: '"Noto Serif TC", "Songti TC", "Noto Serif CJK TC", serif',
  sans: '"PingFang TC", "Noto Sans TC", "Heiti TC", sans-serif',
  mono: '"SF Mono", "Menlo", "DejaVu Sans Mono", monospace',
} as const;

export const ramp = (
  frame: number,
  from: number,
  to: number,
  outFrom: number,
  outTo: number,
  easing: (input: number) => number = Easing.out(Easing.cubic),
) =>
  interpolate(frame, [from, to], [outFrom, outTo], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing,
  });

export const enter = (
  frame: number,
  start: number,
  duration = 16,
  distance = 26,
): CSSProperties => {
  const t = ramp(frame, start, start + duration, 0, 1);
  return {
    opacity: t,
    transform: `translateY(${(1 - t) * distance}px)`,
  };
};

export const pop = (frame: number, fps: number, start: number, damping = 15) =>
  spring({
    frame: frame - start,
    fps,
    config: { damping, stiffness: 180, mass: 0.7 },
  });
