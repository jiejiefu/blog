import React from "react";
import { useVideoConfig } from "remotion";
import { C, FONT, pop, ramp } from "./theme";

const COMMAND = "pytest -q";
const QUESTION = "為什麼這樣會對？";

const typedCount = (frame: number, start: number, end: number, total: number) =>
  Math.round(ramp(frame, start, end, 0, total));

export const TerminalScene: React.FC<{ local: number }> = ({ local }) => {
  const { fps } = useVideoConfig();
  const panelIn = pop(local, fps, -10, 18);
  const panelOpacity = ramp(local, -6, 4, 0, 1);
  const push = ramp(local, 72, 100, 0, 0.06);
  const sweep = ramp(local, 52, 74, -30, 470);
  const sweepOpacity = ramp(local, 52, 60, 0, 1) * (1 - ramp(local, 66, 74, 0, 1));

  const cmd = COMMAND.slice(0, typedCount(local, 18, 38, COMMAND.length));
  const question = QUESTION.slice(0, typedCount(local, 58, 78, QUESTION.length));
  const questionStarted = local >= 58;
  const caretOn = questionStarted && local < 78 ? true : Math.floor(local / 15) % 2 === 0;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        transform: `scale(${1 + push})`,
      }}
    >
      <div
        style={{
          position: "absolute",
          right: 96,
          bottom: 40,
          fontFamily: FONT.serif,
          fontSize: 780,
          fontWeight: 700,
          lineHeight: 1,
          color: C.accent,
          opacity: 0.06 * ramp(local, 78, 100, 0, 1),
          transform: `scale(${0.92 + ramp(local, 78, 100, 0, 0.08)})`,
          userSelect: "none",
        }}
      >
        ?
      </div>

      <div
        style={{
          width: 1180,
          borderRadius: 16,
          border: `1px solid ${C.line}`,
          background: `linear-gradient(180deg, ${C.panel} 0%, ${C.panelAlt} 100%)`,
          boxShadow: "0 40px 120px rgba(0,0,0,0.55)",
          opacity: panelOpacity,
          transform: `translateY(${(1 - panelIn) * 54}px) scale(${
            0.965 + panelIn * 0.035
          })`,
          overflow: "hidden",
          position: "relative",
        }}
      >
        <div
          style={{
            height: 60,
            display: "flex",
            alignItems: "center",
            padding: "0 28px",
            background: "linear-gradient(90deg, #16213A 0%, #101A2B 100%)",
            borderBottom: `1px solid ${C.line}`,
          }}
        >
          {[C.red, C.amber, C.teal].map((color) => (
            <span
              key={color}
              style={{
                width: 13,
                height: 13,
                borderRadius: 999,
                background: color,
                marginRight: 13,
                opacity: 0.9,
              }}
            />
          ))}
          <span
            style={{
              marginLeft: "auto",
              fontFamily: FONT.mono,
              fontSize: 14,
              letterSpacing: "0.12em",
              color: C.dim,
            }}
          >
            zsh · 80×24
          </span>
        </div>

        <div style={{ padding: "34px 48px 40px 48px" }}>
          <div
            style={{
              fontFamily: FONT.mono,
              fontSize: 38,
              color: C.ink,
              letterSpacing: "0.01em",
              height: 46,
              display: "flex",
              alignItems: "center",
            }}
          >
            <span style={{ color: C.dim, marginRight: 16 }}>$</span>
            {cmd}
            {local < 40 && (
              <span
                style={{
                  display: "inline-block",
                  width: 17,
                  height: 4,
                  marginLeft: 4,
                  background: C.teal,
                  opacity: caretOn ? 1 : 0,
                }}
              />
            )}
          </div>

          <div
            style={{
              display: "flex",
              gap: 13,
              alignItems: "center",
              height: 44,
              marginTop: 14,
            }}
          >
            {Array.from({ length: 10 }).map((_, index) => {
              const start = 38 + index * 1.2;
              const t = ramp(local, start, start + 7, 0, 1);
              return (
                <span
                  key={index}
                  style={{
                    width: 17,
                    height: 17,
                    borderRadius: 999,
                    background: C.teal,
                    opacity: t,
                    transform: `scale(${0.35 + t * 0.65})`,
                    boxShadow: `0 0 ${18 * t}px rgba(94,234,212,${0.55 * t})`,
                  }}
                />
              );
            })}
          </div>

          <div
            style={{
              marginTop: 8,
              fontFamily: FONT.mono,
              fontSize: 33,
              color: C.teal,
              opacity: ramp(local, 48, 58, 0, 1),
              transform: `translateY(${(1 - ramp(local, 48, 58, 0, 1)) * 10}px)`,
            }}
          >
            10 passed in 0.42s
          </div>

          <div
            style={{
              marginTop: 30,
              paddingTop: 26,
              borderTop: `1px solid ${C.line}`,
              fontFamily: FONT.sans,
              fontSize: 40,
              color: C.ink,
              height: 54,
              display: "flex",
              alignItems: "center",
              letterSpacing: "0.02em",
            }}
          >
            <span style={{ color: C.accent, marginRight: 18, fontWeight: 600 }}>
              &gt;
            </span>
            {question}
            <span
              style={{
                display: "inline-block",
                width: 3,
                height: 42,
                marginLeft: 6,
                background: ramp(local, 76, 90, 0, 1) > 0.5 ? C.amber : C.teal,
                opacity: caretOn ? 1 : 0,
              }}
            />
          </div>
        </div>

        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: sweep,
            height: 120,
            opacity: sweepOpacity,
            background:
              "linear-gradient(180deg, rgba(94,234,212,0) 0%, rgba(94,234,212,0.13) 55%, rgba(94,234,212,0) 100%)",
            borderTop: "1px solid rgba(94,234,212,0.55)",
          }}
        />
      </div>
    </div>
  );
};
