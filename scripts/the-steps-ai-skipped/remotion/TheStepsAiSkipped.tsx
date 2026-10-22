import React from "react";
import { AbsoluteFill, Easing, useCurrentFrame } from "remotion";
import { Backdrop, Chrome, WipeEdge } from "./chrome";
import { C, ramp } from "./theme";
import { TenMinutesScene } from "./TenMinutesScene";
import { TerminalScene } from "./TerminalScene";
import { TimeGapScene } from "./TimeGapScene";

export const TheStepsAiSkipped: React.FC = () => {
  const frame = useCurrentFrame();

  const wipe = ramp(frame, 74, 88, 0, 1, Easing.inOut(Easing.cubic));
  const iris = ramp(frame, 170, 190, 0, 1, Easing.inOut(Easing.cubic));
  const wipeEdgeOpacity =
    ramp(frame, 74, 78, 0, 1) * (1 - ramp(frame, 86, 90, 0, 1));

  return (
    <AbsoluteFill
      style={{
        backgroundColor: C.bg,
        overflow: "hidden",
        WebkitFontSmoothing: "antialiased",
      }}
    >
      <Backdrop />
      {frame < 88 && <TerminalScene local={frame} />}

      {frame < 191 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            clipPath: `inset(0 ${Math.max(0, 100 - wipe * 100)}% 0 0)`,
          }}
        >
          <Backdrop />
          <TimeGapScene local={frame - 78} />
        </div>
      )}

      <div
        style={{
          position: "absolute",
          inset: 0,
          clipPath: `circle(${iris * 1600}px at 76% 55%)`,
        }}
      >
        <Backdrop />
        <TenMinutesScene local={frame - 178} />
      </div>

      {frame >= 72 && frame <= 92 && (
        <WipeEdge progress={wipe} opacity={wipeEdgeOpacity} />
      )}

      <Chrome />
    </AbsoluteFill>
  );
};
