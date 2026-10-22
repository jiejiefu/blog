import React from "react";
import {
  Easing,
  interpolateColors,
  spring,
  useVideoConfig,
} from "remotion";
import { C, FONT, ramp } from "./theme";

const SEGMENTS = [
  { label: "重現", width: 109, color: "#6B5A2F" },
  { label: "關鍵字", width: 137, color: "#8A6E2E" },
  { label: "搜尋", width: 221, color: "#B07A2C" },
  { label: "版本", width: 193, color: "#D08A38" },
  { label: "文件", width: 277, color: "#E39A44" },
  { label: "試錯", width: 444, color: "#F5B84C" },
];

const TOKENS = ["重現", "關鍵字", "搜尋", "版本", "文件", "試錯"];
const BAR_X = 300;
const BAR_Y = 352;
const BAR_H = 76;

const QuestionMark: React.FC<{
  draw: number;
  opacity: number;
  scale: number;
}> = ({ draw, opacity, scale }) => (
  <div
    style={{
      position: "absolute",
      left: 1250,
      top: 362,
      width: 420,
      height: 420,
      opacity,
      transform: `scale(${scale})`,
      transformOrigin: "center center",
    }}
  >
    <svg viewBox="0 0 100 110" width="420" height="462">
      <path
        d="M 30 36 C 30 20 42 11 55 11 C 70 11 79 21 79 35 C 79 48 68 53 59 59 C 52 64 50 69 50 80"
        fill="none"
        stroke={C.accent}
        strokeWidth={3.4}
        strokeLinecap="round"
        pathLength={1}
        strokeDasharray={1}
        strokeDashoffset={1 - draw}
        opacity={draw > 0.004 ? 1 : 0}
      />
      <circle
        cx="50"
        cy="96"
        r="4"
        fill={C.accent}
        opacity={ramp(draw, 0.72, 0.95, 0, 1)}
      />
    </svg>
  </div>
);

export const TimeGapScene: React.FC<{ local: number }> = ({ local }) => {
  const { fps } = useVideoConfig();

  const headerIn = ramp(local, 0, 12, 0, 1);
  const headlineIn = ramp(local, 2, 16, 0, 1);
  const collapse = ramp(local, 36, 52, 0, 1, Easing.inOut(Easing.cubic));
  const barFade = 1 - ramp(local, 44, 52, 0, 1);
  const tealIn = ramp(local, 44, 52, 0, 1);
  const numberShift = ramp(local, 36, 52, 0, 1);
  const minutes =
    local < 36
      ? Math.round(ramp(local, 8, 28, 0, 250, Easing.out(Easing.cubic)))
      : Math.round(ramp(local, 36, 52, 250, 10, Easing.inOut(Easing.cubic)));
  const numberColor = interpolateColors(
    numberShift,
    [0, 1],
    [C.amber, C.teal],
  );
  const ghostWidth = ramp(local, 56, 74, 0, 1326, Easing.out(Easing.cubic));
  const draw = ramp(local, 72, 92, 0, 1, Easing.inOut(Easing.cubic));
  const qScale = 1 + ramp(local, 92, 114, 0, 13, Easing.in(Easing.cubic));
  const qOpacity = 1 - ramp(local, 98, 112, 0, 1);

  const widths = SEGMENTS.map((segment, index) => {
    const grow = spring({
      frame: local - (8 + index * 2.4),
      fps,
      config: { damping: 16, stiffness: 190, mass: 0.6 },
    });
    return (
      segment.width *
      Math.min(1, Math.max(0, grow)) *
      (1 - collapse * 0.96)
    );
  });
  const totalWidth = widths.reduce((sum, w) => sum + w, 0);

  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div
        style={{
          position: "absolute",
          left: 96,
          top: 140,
          fontFamily: FONT.mono,
          fontSize: 15,
          letterSpacing: "0.3em",
          color: C.accent,
          opacity: headerIn,
        }}
      >
        TIME · BEFORE / AFTER
      </div>

      <div
        style={{
          position: "absolute",
          left: 96,
          top: 196,
          fontFamily: FONT.serif,
          fontSize: 58,
          fontWeight: 700,
          lineHeight: 1.15,
          color: C.ink,
          letterSpacing: "0.01em",
          opacity: headlineIn,
          transform: `translateY(${(1 - headlineIn) * 20}px)`,
        }}
      >
        十分鐘，與被省下的兩百四十分鐘
      </div>

      <div
        style={{
          position: "absolute",
          left: 96,
          top: 340,
          fontFamily: FONT.sans,
          fontSize: 26,
          fontWeight: 700,
          color: C.amber,
          opacity: 1 - ramp(local, 34, 44, 0, 1),
        }}
      >
        以前
      </div>

      <div
        style={{
          position: "absolute",
          left: 96,
          top: 340,
          fontFamily: FONT.sans,
          fontSize: 26,
          fontWeight: 700,
          color: C.teal,
          opacity: ramp(local, 46, 54, 0, 1),
        }}
      >
        現在
      </div>

      <div
        style={{
          position: "absolute",
          left: BAR_X + totalWidth + 14,
          top: 366,
          fontFamily: FONT.mono,
          fontSize: 34,
          fontWeight: 700,
          fontVariantNumeric: "tabular-nums",
          color: numberColor,
          letterSpacing: "0.01em",
          opacity: ramp(local, 10, 22, 0, 1),
        }}
      >
        {minutes} min
      </div>

      <div
        style={{
          position: "absolute",
          left: BAR_X,
          top: BAR_Y,
          display: "flex",
          height: BAR_H,
          opacity: barFade,
        }}
      >
        {SEGMENTS.map((segment, index) => (
          <div
            key={segment.label}
            style={{
              width: widths[index],
              height: BAR_H,
              background: segment.color,
              borderRadius: 4,
              overflow: "hidden",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span
              style={{
                fontFamily: FONT.sans,
                fontSize: 20,
                fontWeight: 700,
                color: "#1A1408",
                whiteSpace: "nowrap",
                opacity: 1 - ramp(local, 30, 36, 0, 1),
              }}
            >
              {segment.label}
            </span>
          </div>
        ))}
      </div>

      <div
        style={{
          position: "absolute",
          left: BAR_X,
          top: BAR_Y,
          width: 55,
          height: BAR_H,
          borderRadius: 4,
          background: C.teal,
          opacity: tealIn,
          boxShadow: "0 0 42px rgba(94,234,212,0.28)",
        }}
      />

      <div
        style={{
          position: "absolute",
          left: 355,
          top: 512,
          width: ghostWidth,
          borderTop: "2px dashed rgba(147,164,190,0.5)",
        }}
      />

      <div
        style={{
          position: "absolute",
          left: 355,
          top: 530,
          fontFamily: FONT.sans,
          fontSize: 23,
          letterSpacing: "0.04em",
          color: C.muted,
          opacity: ramp(local, 64, 76, 0, 1),
        }}
      >
        被省下的 240 分鐘
      </div>

      {TOKENS.map((token, index) => {
        const start = 52 + index * 3.2;
        const appear = ramp(local, start, start + 8, 0, 1);
        const out = ramp(local, 80, 92, 0, 1);
        return (
          <div
            key={token}
            style={{
              position: "absolute",
              left: 380 + index * 150 + out * 40,
              top: 466,
              fontFamily: FONT.mono,
              fontSize: 22,
              letterSpacing: "0.06em",
              color: C.muted,
              opacity: appear * (1 - out),
              transform: `translateY(${(1 - appear) * 10}px)`,
              whiteSpace: "nowrap",
            }}
          >
            ▸ {token}
          </div>
        );
      })}

      <QuestionMark draw={draw} opacity={qOpacity} scale={qScale} />

      <div
        style={{
          position: "absolute",
          left: 96,
          right: 96,
          top: 836,
          textAlign: "center",
          fontFamily: FONT.sans,
          fontSize: 31,
          letterSpacing: "0.03em",
          color: C.muted,
          opacity: ramp(local, 74, 86, 0, 1),
        }}
      >
        快的不是解法，是被跳過的步驟。
      </div>
    </div>
  );
};
