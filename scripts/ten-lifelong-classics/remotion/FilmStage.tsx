import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, FONT, ramp } from "./theme";
import {
  DUR,
  FILMS,
  LAYOUTS,
  PAIR_ORDER,
  START,
  layoutAt,
  type Film,
  type Layout,
} from "./films";

const accentRule = (accent: string) => (
  <div style={{ width: 64, height: 3, backgroundColor: accent }} />
);

const TextBlock: React.FC<{
  film: Film;
  layout: Layout;
  inT: number;
  outT: number;
}> = ({ film, layout, inT, outT }) => {
  const direction = layout.text.x > 900 ? 1 : -1;
  const opacity = inT * outT;
  const shift = (1 - inT) * 20 * direction - (1 - outT) * 20 * direction;

  return (
    <div
      style={{
        position: "absolute",
        left: layout.text.x,
        top: layout.text.y,
        width: layout.text.w,
        opacity,
        transform: `translateX(${shift}px)`,
      }}
    >
      <div
        style={{
          position: "absolute",
          right: 0,
          top: -84,
          fontFamily: FONT.display,
          fontSize: 360,
          lineHeight: 0.8,
          fontWeight: 700,
          color: film.accent,
          opacity: 0.055,
          letterSpacing: "-0.04em",
          fontVariantNumeric: "tabular-nums",
          pointerEvents: "none",
        }}
      >
        {film.rank.toString().padStart(2, "0")}
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          fontFamily: FONT.mono,
          fontSize: 14,
          letterSpacing: "0.26em",
          color: C.muted,
        }}
      >
        <span style={{ color: film.accent }}>
          NO. {film.rank.toString().padStart(2, "0")}
        </span>
        <span style={{ opacity: 0.5 }}>·</span>
        <span>{film.medium}</span>
        <span style={{ opacity: 0.5 }}>·</span>
        <span>{film.year}</span>
      </div>

      <div
        style={{
          marginTop: 46,
          fontFamily: FONT.serif,
          fontSize: 74,
          lineHeight: 1.1,
          letterSpacing: "0.02em",
          color: C.ink,
          fontWeight: 700,
        }}
      >
        {film.zh}
      </div>

      <div style={{ marginTop: 24 }}>{accentRule(film.accent)}</div>

      <div
        style={{
          marginTop: 26,
          fontFamily: FONT.mono,
          fontSize: 12,
          letterSpacing: "0.28em",
          color: C.muted,
        }}
      >
        {film.en}
      </div>

      <div
        style={{
          marginTop: 26,
          borderLeft: `2px solid ${film.accent}`,
          paddingLeft: 16,
          maxWidth: 560,
          fontFamily: FONT.sans,
          fontSize: 24,
          lineHeight: 1.62,
          color: C.soft,
        }}
      >
        {film.thesis}
      </div>
    </div>
  );
};

const StageMount: React.FC<{ frame: number; layout: Layout }> = ({
  frame,
  layout,
}) => {
  const open = ramp(frame, 44, 50, 0, 1);
  const opacity = open * (1 - ramp(frame, 186, 192, 0, 1));
  if (opacity <= 0.002) return null;

  const { panel } = layout;
  const inset = (1 - open) * 20;
  const corner = 22;
  const cornerStyle = { position: "absolute", width: corner, height: corner };
  const gold = "rgba(232,181,74,0.62)";

  return (
    <div
      style={{
        position: "absolute",
        left: panel.x - inset,
        top: panel.y - inset,
        width: panel.w + inset * 2,
        height: panel.h + inset * 2,
        border: "1px solid rgba(242,239,231,0.12)",
        backgroundColor: "rgba(10,10,12,0.72)",
        opacity,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          ...cornerStyle,
          left: 0,
          top: 0,
          borderTop: `2px solid ${gold}`,
          borderLeft: `2px solid ${gold}`,
        }}
      />
      <div
        style={{
          ...cornerStyle,
          right: 0,
          top: 0,
          borderTop: `2px solid ${gold}`,
          borderRight: `2px solid ${gold}`,
        }}
      />
      <div
        style={{
          ...cornerStyle,
          left: 0,
          bottom: 0,
          borderBottom: `2px solid ${gold}`,
          borderLeft: `2px solid ${gold}`,
        }}
      />
      <div
        style={{
          ...cornerStyle,
          right: 0,
          bottom: 0,
          borderBottom: `2px solid ${gold}`,
          borderRight: `2px solid ${gold}`,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 22,
          bottom: 18,
          fontFamily: FONT.mono,
          fontSize: 10,
          letterSpacing: "0.26em",
          color: C.muted,
          opacity: 1 - open,
        }}
      >
        SEQUENCE 10 → 1
      </div>
    </div>
  );
};

export const FilmStage: React.FC<{ frame: number }> = ({ frame }) => {
  const layout = layoutAt(frame);
  const { panel } = layout;

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <StageMount frame={frame} layout={layout} />
      {FILMS.map((film, index) => {
        const local = frame - START[index];
        const duration = DUR[index];
        if (local < -1 || local > duration + 1) return null;

        const inT = ramp(local, 0, 5, 0, 1);
        const outT = 1 - ramp(local, duration - 4, duration, 0, 1);
        const opacity = inT * outT;
        if (opacity <= 0.002) return null;

        const slide = (1 - inT) * 74 - (1 - outT) * 74;
        const drift = 1 + 0.018 * (Math.max(0, local) / duration);
        const pairFirst =
          index === 0 || PAIR_ORDER[index] !== PAIR_ORDER[index - 1];
        const textDelay = index === 0 ? 1 : pairFirst ? 4 : 1;
        const settled = LAYOUTS[PAIR_ORDER[index]];

        return (
          <React.Fragment key={film.file}>
            <div
              style={{
                position: "absolute",
                left: panel.x,
                top: panel.y,
                width: panel.w,
                height: panel.h,
                overflow: "hidden",
                border: `1px solid rgba(242,239,231,0.16)`,
                backgroundColor: C.panel,
                boxShadow: "0 46px 130px rgba(0,0,0,0.55)",
                opacity,
              }}
            >
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  transform: `translateY(${slide}px)`,
                }}
              >
                <Img
                  src={staticFile(`ten-classics/${film.file}.png`)}
                  style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                    objectPosition: `${film.focus[0] * 100}% ${
                      film.focus[1] * 100
                    }%`,
                    transform: `scale(${film.zoom * drift})`,
                    transformOrigin: `${film.focus[0] * 100}% ${
                      film.focus[1] * 100
                    }%`,
                    filter: "brightness(0.97) saturate(1.02)",
                  }}
                />
              </div>

              {film.shade ? (
                <div
                  style={{
                    position: "absolute",
                    inset: 0,
                    backgroundColor: `rgba(5,5,6,${film.shade})`,
                  }}
                />
              ) : null}

              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  background:
                    "linear-gradient(180deg, rgba(5,5,6,0.18) 0%, transparent 22%, transparent 68%, rgba(5,5,6,0.42) 100%)",
                }}
              />

              <div
                style={{
                  position: "absolute",
                  left: 0,
                  top: 0,
                  width: "100%",
                  height: 3,
                  backgroundColor: film.accent,
                  opacity: 0.92,
                }}
              />

              <div
                style={{
                  position: "absolute",
                  right: 16,
                  bottom: 14,
                  padding: "5px 9px",
                  backgroundColor: "rgba(5,5,6,0.62)",
                  fontFamily: FONT.mono,
                  fontSize: 10,
                  letterSpacing: "0.18em",
                  color: "rgba(242,239,231,0.78)",
                }}
              >
                PAIR {film.pair.toString().padStart(2, "0")} ·{" "}
                {film.rank.toString().padStart(2, "0")}/10
              </div>

              {inT < 1 ? (
                <div
                  style={{
                    position: "absolute",
                    left: 0,
                    bottom: 0,
                    width: "100%",
                    height: 3,
                    backgroundColor: film.accent,
                    opacity: 1 - inT,
                  }}
                />
              ) : null}
            </div>

            <TextBlock
              film={film}
              layout={settled}
              inT={ramp(local, textDelay, textDelay + 3, 0, 1)}
              outT={1 - ramp(local, duration - 2, duration, 0, 1)}
            />
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};
