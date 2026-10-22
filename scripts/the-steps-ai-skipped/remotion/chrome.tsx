import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C, FONT, ramp } from "./theme";

const DOT_GRID = {
  backgroundImage:
    "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.06) 1px, transparent 0)",
  backgroundSize: "28px 28px",
} as const;

export const Backdrop: React.FC = () => {
  const raw = useCurrentFrame();
  const frame = Math.min(raw, 288);
  const breathe = 0.62 + Math.sin(frame / 24) * 0.08;

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg }}>
      <AbsoluteFill style={DOT_GRID} />
      <AbsoluteFill
        style={{
          background: `radial-gradient(1120px 780px at 22% 6%, rgba(139,147,255,${
            0.1 + breathe * 0.12
          }), transparent 68%), radial-gradient(900px 720px at 84% 92%, rgba(94,234,212,${
            0.04 + breathe * 0.06
          }), transparent 70%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(1250px 940px at 50% 44%, transparent 42%, rgba(4,7,13,0.62) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

const chapterStyle: React.CSSProperties = {
  position: "absolute",
  right: 0,
  top: 0,
  fontFamily: FONT.mono,
  fontSize: 15,
  letterSpacing: "0.24em",
  color: C.dim,
  whiteSpace: "nowrap",
};

export const Chrome: React.FC = () => {
  const frame = useCurrentFrame();
  const frameIn = ramp(frame, 0, 16, 0, 1);
  const a = 1 - ramp(frame, 70, 80, 0, 1);
  const b =
    ramp(frame, 70, 80, 0, 1) * (1 - ramp(frame, 170, 182, 0, 1));
  const d = ramp(frame, 170, 182, 0, 1);

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          inset: 28,
          border: `1px solid ${C.line}`,
          opacity: frameIn * 0.8,
        }}
      />

      <div
        style={{
          position: "absolute",
          top: 58,
          left: 96,
          right: 96,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          opacity: frameIn,
        }}
      >
        <span
          style={{
            fontFamily: FONT.mono,
            fontSize: 15,
            letterSpacing: "0.3em",
            color: C.muted,
          }}
        >
          JAY FU / ENGINEERING NOTES
        </span>
        <span style={{ position: "relative", width: 340, height: 20 }}>
          <span style={{ ...chapterStyle, opacity: a }}>FIELD NOTE 00</span>
          <span style={{ ...chapterStyle, opacity: b }}>FIG. 01 · TIME GAP</span>
          <span style={{ ...chapterStyle, opacity: d }}>FIG. 07 · 10:00</span>
        </span>
      </div>

      <div
        style={{
          position: "absolute",
          bottom: 56,
          left: 96,
          right: 96,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontFamily: FONT.mono,
          fontSize: 13,
          letterSpacing: "0.26em",
          color: C.dim,
          opacity: frameIn * 0.9,
        }}
      >
        <span>THE STEPS AI SKIPPED</span>
        <span>2026</span>
      </div>
    </AbsoluteFill>
  );
};

export const WipeEdge: React.FC<{ progress: number; opacity: number }> = ({
  progress,
  opacity,
}) => {
  const x = progress * 1920;

  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity }}>
      <div
        style={{
          position: "absolute",
          top: 0,
          bottom: 0,
          left: x - 300,
          width: 300,
          background:
            "linear-gradient(90deg, rgba(94,234,212,0) 0%, rgba(94,234,212,0.16) 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 0,
          bottom: 0,
          left: x - 1.5,
          width: 3,
          background: C.teal,
          boxShadow: "0 0 48px 10px rgba(94,234,212,0.45)",
        }}
      />
    </AbsoluteFill>
  );
};
