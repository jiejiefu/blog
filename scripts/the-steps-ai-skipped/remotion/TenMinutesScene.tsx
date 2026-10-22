import React from "react";
import { Easing, useVideoConfig } from "remotion";
import { C, FONT, pop, ramp } from "./theme";

const RING_R = 200;
const BOX = 480;
const TICKS = 10;

export const TenMinutesScene: React.FC<{ local: number }> = ({ local }) => {
  const { fps } = useVideoConfig();

  const dock = ramp(local, 36, 56, 0, 1, Easing.inOut(Easing.cubic));
  const dy = -210 * dock;
  const scale = 1 - 0.62 * dock;

  const draw = ramp(local, 2, 22, 0, 0.92, Easing.inOut(Easing.cubic));
  const clockIn = pop(local, fps, 4, 14);
  const clockOpacity = ramp(local, 4, 12, 0, 1);

  const headlineOut = 1 - ramp(local, 36, 44, 0, 1);
  const headlineIn = ramp(local, 10, 22, 0, 1);
  const subIn = ramp(local, 18, 28, 0, 1);

  const line1 = ramp(local, 46, 60, 0, 1);
  const line2 = ramp(local, 50, 64, 0, 1);
  const footer = ramp(local, 60, 74, 0, 1);

  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            width: BOX,
            height: BOX,
            position: "relative",
            transform: `translateY(${dy}px) scale(${scale})`,
          }}
        >
          <svg width={BOX} height={BOX} viewBox={`0 0 ${BOX} ${BOX}`}>
            <circle
              cx={BOX / 2}
              cy={BOX / 2}
              r={RING_R}
              fill="none"
              stroke={C.line}
              strokeWidth={2}
            />
            <circle
              cx={BOX / 2}
              cy={BOX / 2}
              r={RING_R}
              fill="none"
              stroke={C.teal}
              strokeWidth={3}
              strokeLinecap="round"
              pathLength={1}
              strokeDasharray={1}
              strokeDashoffset={1 - draw}
              transform={`rotate(-90 ${BOX / 2} ${BOX / 2})`}
              style={{ filter: "drop-shadow(0 0 14px rgba(94,234,212,0.35))" }}
            />
            {Array.from({ length: TICKS }).map((_, index) => {
              const angle = (index / TICKS) * Math.PI * 2 - Math.PI / 2;
              const start = 4 + index * 1.5;
              const lit = ramp(local, start, start + 8, 0, 1);
              return (
                <circle
                  key={index}
                  cx={BOX / 2 + Math.cos(angle) * RING_R}
                  cy={BOX / 2 + Math.sin(angle) * RING_R}
                  r={5.5}
                  fill={C.teal}
                  opacity={0.14 + lit * 0.86}
                />
              );
            })}
          </svg>

          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              opacity: clockOpacity,
              transform: `scale(${0.82 + clockIn * 0.18})`,
            }}
          >
            <div
              style={{
                fontFamily: FONT.mono,
                fontSize: 104,
                fontWeight: 700,
                letterSpacing: "-0.02em",
                fontVariantNumeric: "tabular-nums",
                color: C.ink,
                lineHeight: 1,
              }}
            >
              10:00
            </div>
            <div
              style={{
                marginTop: 16,
                fontFamily: FONT.mono,
                fontSize: 14,
                letterSpacing: "0.34em",
                color: C.dim,
              }}
            >
              MINUTES
            </div>
          </div>
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 786,
          textAlign: "center",
          fontFamily: FONT.serif,
          fontSize: 88,
          fontWeight: 700,
          letterSpacing: "0.03em",
          color: C.ink,
          opacity: headlineIn * headlineOut,
          transform: `translateY(${(1 - headlineIn) * 26}px)`,
        }}
      >
        先留十分鐘
      </div>

      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 912,
          textAlign: "center",
          fontFamily: FONT.sans,
          fontSize: 31,
          letterSpacing: "0.16em",
          color: C.muted,
          opacity: subIn * headlineOut,
        }}
      >
        在打開 AI 之前
      </div>

      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 442,
          textAlign: "center",
          fontFamily: FONT.serif,
          fontSize: 58,
          fontWeight: 700,
          letterSpacing: "0.02em",
          color: C.ink,
          opacity: line1,
          transform: `translateY(${(1 - line1) * 18}px)`,
        }}
      >
        AI 把 Bug 修好了，
      </div>

      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 518,
          display: "flex",
          justifyContent: "center",
          alignItems: "baseline",
          opacity: line2,
          transform: `translateY(${(1 - line2) * 18}px)`,
          fontFamily: FONT.serif,
          fontWeight: 700,
          letterSpacing: "0.02em",
          color: C.ink,
        }}
      >
        <span style={{ fontSize: 58 }}>我這工程師只剩</span>
        <span
          style={{
            fontSize: 86,
            color: C.accent,
            marginLeft: 14,
            letterSpacing: "0.04em",
          }}
        >
          BI
        </span>
      </div>

      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 666,
          textAlign: "center",
          fontFamily: FONT.mono,
          fontSize: 17,
          letterSpacing: "0.3em",
          color: C.dim,
          opacity: footer,
        }}
      >
        THE STEPS AI SKIPPED · JAY FU · 2026
      </div>
    </div>
  );
};
