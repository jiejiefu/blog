import React from "react";
import { AbsoluteFill } from "remotion";
import { C, FONT, ramp } from "./theme";

export const TitleCard: React.FC<{ frame: number }> = ({ frame }) => {
  if (frame < 236) return null;

  const kicker = ramp(frame, 238, 248, 0, 1);
  const title = ramp(frame, 240, 256, 0, 1);
  const sub = ramp(frame, 248, 260, 0, 1);
  const meta = ramp(frame, 254, 266, 0, 1);
  const question = ramp(frame, 262, 278, 0, 1);

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 300,
          width: "100%",
          textAlign: "center",
          fontFamily: FONT.mono,
          fontSize: 14,
          letterSpacing: "0.42em",
          color: C.gold,
          opacity: kicker,
          transform: `translateY(${(1 - kicker) * 14}px)`,
        }}
      >
        A PERSONAL CANON
      </div>

      <div
        style={{
          position: "absolute",
          left: 0,
          top: 352,
          width: "100%",
          textAlign: "center",
          fontFamily: FONT.serif,
          fontSize: 116,
          lineHeight: 1.16,
          letterSpacing: "0.08em",
          fontWeight: 700,
          color: C.ink,
          opacity: title,
          clipPath: `inset(0 ${(1 - title) * 100}% 0 0)`,
        }}
      >
        從黑鏡到巨人
      </div>

      <div
        style={{
          position: "absolute",
          left: 0,
          top: 542,
          width: "100%",
          textAlign: "center",
          fontFamily: FONT.sans,
          fontSize: 30,
          letterSpacing: "0.14em",
          color: C.soft,
          opacity: sub,
        }}
      >
        十部科幻與人性史詩 · 五組對讀
      </div>

      <div
        style={{
          position: "absolute",
          left: 0,
          top: 606,
          width: "100%",
          textAlign: "center",
          fontFamily: FONT.mono,
          fontSize: 13,
          letterSpacing: "0.3em",
          color: C.muted,
          opacity: meta * 0.9,
        }}
      >
        10 FILMS / 5 PAIRS / ONE QUESTION
      </div>

      <div
        style={{
          position: "absolute",
          left: 0,
          top: 676,
          width: "100%",
          textAlign: "center",
          fontFamily: FONT.sans,
          fontSize: 23,
          lineHeight: 1.95,
          letterSpacing: "0.05em",
          color: C.muted,
          opacity: question,
          transform: `translateY(${(1 - question) * 12}px)`,
        }}
      >
        當科技和權力不斷改變我們對人的定義，
        <br />
        我們究竟該如何看待自己，又該如何看待別人？
      </div>
    </AbsoluteFill>
  );
};
