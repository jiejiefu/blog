import React from "react";
import { AbsoluteFill } from "remotion";
import { C, FONT, ramp } from "./theme";
import { FILMS, FOOTER_NOTE, PAIR_COLOR, type Film } from "./films";

const DOT_GRID = {
  backgroundImage:
    "radial-gradient(circle at 1px 1px, rgba(242,239,231,0.07) 1px, transparent 0)",
  backgroundSize: "28px 28px",
} as const;

const SCANLINES = {
  backgroundImage:
    "repeating-linear-gradient(0deg, rgba(0,0,0,0.22) 0px, rgba(0,0,0,0.22) 1px, transparent 1px, transparent 4px)",
  opacity: 0.28,
} as const;

const rgba = (hex: string, alpha: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
};

export const Backdrop: React.FC<{ accent: string; frame: number }> = ({
  accent,
  frame,
}) => {
  const breathe = 0.07 + Math.sin(frame / 26) * 0.02;
  return (
    <AbsoluteFill style={{ backgroundColor: C.bg }}>
      <AbsoluteFill style={DOT_GRID} />
      <AbsoluteFill style={SCANLINES} />
      <AbsoluteFill
        style={{
          background: `radial-gradient(1180px 820px at 74% 16%, ${rgba(
            accent,
            breathe,
          )}, transparent 70%), radial-gradient(900px 700px at 12% 92%, ${rgba(
            C.gold,
            0.045,
          )}, transparent 72%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(1250px 960px at 50% 46%, transparent 40%, rgba(0,0,0,0.66) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

export const Chrome: React.FC<{ frame: number; pair: number }> = ({
  frame,
  pair,
}) => {
  const chromeIn = ramp(frame, 0, 14, 0, 1);
  const stageMode = frame >= 44 && frame < 192;
  const topRight = stageMode
    ? `PAIR 0${pair} · ${FILMS.find((f) => f.pair === pair)?.pairLabel ?? ""}`
    : "ESSAY · 2026";

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          inset: 34,
          border: `1px solid ${C.line}`,
          opacity: chromeIn,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 66,
          left: 96,
          fontFamily: FONT.mono,
          fontSize: 14,
          letterSpacing: "0.32em",
          color: C.gold,
          opacity: ramp(frame, 4, 18, 0, 1),
          whiteSpace: "nowrap",
        }}
      >
        TEN LIFELONG CLASSICS
      </div>
      <div
        style={{
          position: "absolute",
          top: 66,
          right: 96,
          display: "flex",
          alignItems: "center",
          gap: 10,
          fontFamily: FONT.mono,
          fontSize: 13,
          letterSpacing: "0.24em",
          color: C.muted,
          opacity: ramp(frame, 8, 22, 0, 1),
          whiteSpace: "nowrap",
        }}
      >
        {stageMode ? (
          <span
            style={{
              width: 7,
              height: 7,
              backgroundColor: PAIR_COLOR[pair],
              display: "inline-block",
            }}
          />
        ) : null}
        {topRight}
      </div>
      <div
        style={{
          position: "absolute",
          left: 96,
          bottom: 58,
          fontFamily: FONT.mono,
          fontSize: 10,
          letterSpacing: "0.2em",
          color: C.dim,
          opacity: ramp(frame, 12, 24, 0, 1),
        }}
      >
        {FOOTER_NOTE}
      </div>
      <div
        style={{
          position: "absolute",
          right: 96,
          bottom: 58,
          fontFamily: FONT.mono,
          fontSize: 10,
          letterSpacing: "0.2em",
          color: C.dim,
          opacity: ramp(frame, 12, 24, 0, 1),
        }}
      >
        JAY FU / 2026
      </div>
    </AbsoluteFill>
  );
};

const barLength = (film: Film) => 70 + (11 - film.rank) * 60;

export const ChartLabels: React.FC<{ frame: number }> = ({ frame }) => {
  const out = 1 - ramp(frame, 31, 40, 0, 1);
  if (out <= 0) return null;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity: out }}>
      {FILMS.map((film, index) => {
        const t = ramp(frame, 2 + index * 1.4, 11 + index * 1.4, 0, 1);
        const y = 200 + index * 68;
        return (
          <React.Fragment key={film.file}>
            <div
              style={{
                position: "absolute",
                left: 150,
                top: y - 2,
                width: 58,
                textAlign: "right",
                fontFamily: FONT.mono,
                fontSize: 21,
                letterSpacing: "0.06em",
                color: film.accent,
                opacity: t,
                fontVariantNumeric: "tabular-nums",
              }}
            >
              {film.rank.toString().padStart(2, "0")}
            </div>
            <div
              style={{
                position: "absolute",
                left: 230 + barLength(film) + 18,
                top: y + 3,
                fontFamily: FONT.sans,
                fontSize: 19,
                letterSpacing: "0.08em",
                color: C.ink,
                opacity: t * 0.88,
                whiteSpace: "nowrap",
              }}
            >
              {film.zh}
            </div>
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};

const STATS = [
  { n: "10", label: "FILMS", y: 244 },
  { n: "5", label: "PAIRS", y: 470 },
  { n: "1", label: "QUESTION", y: 696 },
];

export const StructureStack: React.FC<{ frame: number }> = ({ frame }) => {
  const out = 1 - ramp(frame, 32, 42, 0, 1);
  if (out <= 0) return null;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity: out }}>
      <div
        style={{
          position: "absolute",
          left: 1122,
          top: 236,
          width: 1,
          height: 690,
          backgroundColor: C.gold,
          opacity: 0.22,
          transform: `scaleY(${ramp(frame, 4, 24, 0, 1)})`,
          transformOrigin: "top",
        }}
      />
      {STATS.map((stat, index) => {
        const t = ramp(frame, 8 + index * 6, 20 + index * 6, 0, 1);
        return (
          <React.Fragment key={stat.label}>
            <div
              style={{
                position: "absolute",
                left: 1160,
                top: stat.y,
                fontFamily: FONT.display,
                fontSize: 196,
                lineHeight: 0.86,
                fontWeight: 700,
                color: C.gold,
                opacity: t * 0.9,
                transform: `translateY(${(1 - t) * 26}px)`,
                fontVariantNumeric: "tabular-nums",
              }}
            >
              {stat.n}
            </div>
            <div
              style={{
                position: "absolute",
                left: 1164,
                top: stat.y + 176,
                fontFamily: FONT.mono,
                fontSize: 14,
                letterSpacing: "0.3em",
                color: C.muted,
                opacity: t,
              }}
            >
              {stat.label}
            </div>
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};
