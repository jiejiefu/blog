import React from "react";
import {
  AbsoluteFill,
  interpolateColors,
  useCurrentFrame,
} from "remotion";
import { Backdrop, ChartLabels, Chrome, StructureStack } from "./Chrome";
import { FilmStage } from "./FilmStage";
import { GoldLine, PairLabels, TenBars } from "./TenBars";
import { TitleCard } from "./TitleCard";
import { C, ramp } from "./theme";
import { FILMS, START, activeIndex } from "./films";

const stageAccent = (frame: number) => {
  const index = activeIndex(frame);
  if (index === 0) return FILMS[0].accent;
  const since = frame - START[index];
  if (since < 8) {
    return interpolateColors(
      frame,
      [START[index], START[index] + 8],
      [FILMS[index - 1].accent, FILMS[index].accent],
    );
  }
  return FILMS[index].accent;
};

export const TenLifelongClassics: React.FC = () => {
  const frame = useCurrentFrame();
  const stage = frame >= 44 && frame < 192;
  const accent = stage ? stageAccent(frame) : C.gold;
  const pair = stage ? FILMS[activeIndex(frame)].pair : 0;

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg }}>
      <Backdrop accent={accent} frame={frame} />
      <Chrome frame={frame} pair={pair} />
      <ChartLabels frame={frame} />
      <StructureStack frame={frame} />
      <FilmStage frame={frame} />
      <TenBars frame={frame} />
      <PairLabels frame={frame} />
      <GoldLine frame={frame} />
      <TitleCard frame={frame} />
      <AbsoluteFill
        style={{
          backgroundColor: C.bg,
          opacity:
            ramp(frame, 0, 8, 1, 0) + ramp(frame, 292, 300, 0, 1),
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
