import React from "react";
import { AbsoluteFill } from "remotion";
import { C, FONT, inOut, lerp, ramp } from "./theme";
import {
  DUR,
  FILMS,
  PAIR_COLOR,
  START,
  activeIndex,
  type Rect,
} from "./films";

const SLOT_W = 1728 / 10;
const slotCenter = (index: number) => 96 + index * SLOT_W + SLOT_W / 2;
const pairCenter = (group: number) => 268.8 + 345.6 * group;

const barLength = (index: number) => 70 + (11 - FILMS[index].rank) * 60;

const chartRect = (index: number): Rect => ({
  x: 230,
  y: 200 + index * 68,
  w: barLength(index),
  h: 36,
});

const stripRect = (index: number): Rect => ({
  x: slotCenter(index) - 48,
  y: 976,
  w: 96,
  h: 4,
});

const riseRect = (index: number): Rect => ({
  x: slotCenter(index) - 11,
  y: 520,
  w: 22,
  h: 120,
});

const pairRect = (group: number): Rect => ({
  x: pairCenter(group) - 11,
  y: 520,
  w: 22,
  h: 120,
});

const goldRect = (): Rect => ({ x: 957, y: 520, w: 6, h: 120 });

const lerpRect = (a: Rect, b: Rect, t: number): Rect => ({
  x: lerp(a.x, b.x, t),
  y: lerp(a.y, b.y, t),
  w: lerp(a.w, b.w, t),
  h: lerp(a.h, b.h, t),
});

type BarState = { rect: Rect; opacity: number; glow: boolean };

const barState = (frame: number, index: number): BarState | null => {
  if (frame < 30) {
    return {
      rect: chartRect(index),
      opacity: ramp(frame, 1 + index * 1.4, 9 + index * 1.4, 0, 0.9),
      glow: false,
    };
  }

  if (frame < 44) {
    const t = ramp(frame, 30, 44, 0, 1, inOut);
    return {
      rect: lerpRect(chartRect(index), stripRect(index), t),
      opacity: lerp(0.9, 0.55, t),
      glow: false,
    };
  }

  if (frame < 190) {
    const active = activeIndex(frame);
    const local = frame - START[active];
    const pulse =
      ramp(local, 0, 4, 0, 1) *
      (1 - ramp(local, DUR[active] - 4, DUR[active], 0, 1));
    const isActive = index === active;
    return {
      rect: isActive
        ? { ...stripRect(index), h: 4 + 7 * pulse }
        : stripRect(index),
      opacity: isActive ? 1 : 0.42,
      glow: isActive,
    };
  }

  if (frame < 206) {
    const t = ramp(frame, 190, 206, 0, 1, inOut);
    return {
      rect: lerpRect(stripRect(index), riseRect(index), t),
      opacity: 1,
      glow: true,
    };
  }

  if (frame < 224) {
    const t = ramp(frame, 206, 224, 0, 1, inOut);
    const group = Math.floor(index / 2);
    const isLead = index % 2 === 0;
    return {
      rect: lerpRect(riseRect(index), pairRect(group), t),
      opacity: isLead ? 1 : 1 - t,
      glow: isLead,
    };
  }

  if (frame < 236 && index % 2 === 0) {
    const t = ramp(frame, 224, 236, 0, 1, inOut);
    const group = Math.floor(index / 2);
    return {
      rect: lerpRect(pairRect(group), goldRect(), t),
      opacity: 1 - ramp(frame, 228, 236, 0, 1),
      glow: true,
    };
  }

  return null;
};

export const TenBars: React.FC<{ frame: number }> = ({ frame }) => {
  if (frame >= 236) return null;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {FILMS.map((film, index) => {
        const state = barState(frame, index);
        if (!state || state.opacity <= 0.002) return null;
        return (
          <div
            key={film.file}
            style={{
              position: "absolute",
              left: state.rect.x,
              top: state.rect.y,
              width: state.rect.w,
              height: state.rect.h,
              backgroundColor: film.accent,
              opacity: state.opacity,
              boxShadow: state.glow
                ? `0 0 26px ${film.accent}66`
                : undefined,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

export const PairLabels: React.FC<{ frame: number }> = ({ frame }) => {
  if (frame < 204 || frame > 238) return null;

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {[0, 1, 2, 3, 4].map((group) => {
        const pair = 5 - group;
        const color = PAIR_COLOR[pair];
        const label = FILMS.find((film) => film.pair === pair)?.pairLabel ?? "";
        const inT = ramp(frame, 206 + group * 1.5, 214 + group * 1.5, 0, 1);
        const outT =
          1 - ramp(frame, 218 + group * 1.5, 226 + group * 1.5, 0, 1);
        const opacity = inT * outT;
        if (opacity <= 0.002) return null;

        return (
          <React.Fragment key={pair}>
            <div
              style={{
                position: "absolute",
                left: slotCenter(group * 2) + 13,
                top: 500,
                width: SLOT_W - 26,
                height: 1,
                backgroundColor: color,
                opacity: opacity * 0.45,
              }}
            />
            <div
              style={{
                position: "absolute",
                left: pairCenter(group) - 130,
                top: 456,
                width: 260,
                textAlign: "center",
                fontFamily: FONT.serif,
                fontSize: 24,
                letterSpacing: "0.22em",
                color,
                opacity,
                transform: `translateY(${(1 - inT) * 12}px)`,
                whiteSpace: "nowrap",
              }}
            >
              {label}
            </div>
            <div
              style={{
                position: "absolute",
                left: pairCenter(group) - 130,
                top: 424,
                width: 260,
                textAlign: "center",
                fontFamily: FONT.mono,
                fontSize: 10,
                letterSpacing: "0.24em",
                color: C.muted,
                opacity: opacity * 0.8,
              }}
            >
              PAIR {pair.toString().padStart(2, "0")}
            </div>
          </React.Fragment>
        );
      })}

      {frame >= 222 ? (
        <div
          style={{
            position: "absolute",
            left: 760,
            top: 456,
            width: 400,
            textAlign: "center",
            fontFamily: FONT.serif,
            fontSize: 26,
            letterSpacing: "0.3em",
            color: C.gold,
            opacity:
              ramp(frame, 222, 229, 0, 1) *
              (1 - ramp(frame, 234, 238, 0, 1)),
          }}
        >
          一個問題
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

export const GoldLine: React.FC<{ frame: number }> = ({ frame }) => {
  if (frame < 224) return null;
  const t = ramp(frame, 236, 250, 0, 1, inOut);
  const opacity = ramp(frame, 224, 234, 0, 1);
  const rect: Rect = {
    x: lerp(957, 750, t),
    y: lerp(520, 500, t),
    w: lerp(6, 420, t),
    h: lerp(120, 3, t),
  };

  return (
    <div
      style={{
        position: "absolute",
        left: rect.x,
        top: rect.y,
        width: rect.w,
        height: rect.h,
        backgroundColor: C.gold,
        opacity,
        boxShadow: `0 0 30px ${C.gold}55`,
      }}
    />
  );
};
