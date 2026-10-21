import type { CSSProperties } from "react";
import { Easing, interpolate } from "remotion";

export const C = {
  bg: "#050506",
  ink: "#F2EFE7",
  soft: "#B9B4A8",
  muted: "#9A948A",
  dim: "#5E5A53",
  line: "rgba(242,239,231,0.14)",
  gold: "#E8B54A",
  panel: "#0D0D0F",
} as const;

export const FONT = {
  serif: '"Songti TC","Noto Serif TC","Songti SC",serif',
  sans: '"PingFang TC","Noto Sans TC","Heiti TC",sans-serif',
  mono: '"SF Mono","Menlo","DejaVu Sans Mono",monospace',
  display: '"Avenir Next","Helvetica Neue","Arial",sans-serif',
} as const;

export const inOut = Easing.inOut(Easing.cubic);

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

export const enterStyle = (
  frame: number,
  start: number,
  duration = 9,
  distance = 22,
  direction = 1,
): CSSProperties => {
  const t = ramp(frame, start, start + duration, 0, 1);
  return {
    opacity: t,
    transform: `translate(${(1 - t) * distance * direction}px, ${
      (1 - t) * distance
    }px)`,
  };
};

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
