import { Easing, interpolate } from "remotion";

export const FPS = 30;
export const DURATION = 300;

export type Film = {
  rank: number;
  file: string;
  zh: string;
  en: string;
  medium: string;
  year: string;
  accent: string;
  thesis: string;
  pair: number;
  pairLabel: string;
  focus: [number, number];
  zoom: number;
  shade?: number;
};

export const FILMS: Film[] = [
  {
    rank: 10,
    file: "01_black_mirror",
    zh: "黑鏡",
    en: "BLACK MIRROR",
    medium: "TELEVISION",
    year: "2011–",
    accent: "#7DD3FC",
    thesis: "我們自願走進的動物園，卻忘了欄杆是自己焊的。",
    pair: 5,
    pairLabel: "螢幕與石碑",
    focus: [0.9, 0.5],
    zoom: 1.34,
  },
  {
    rank: 9,
    file: "02_2001",
    zh: "2001：太空漫遊",
    en: "2001: A SPACE ODYSSEY",
    medium: "FILM",
    year: "1968",
    accent: "#D7263D",
    thesis: "石碑從不回答，只改變你。",
    pair: 5,
    pairLabel: "螢幕與石碑",
    focus: [0.82, 0.5],
    zoom: 1.48,
    shade: 0.32,
  },
  {
    rank: 8,
    file: "03_akira",
    zh: "阿基拉",
    en: "AKIRA",
    medium: "ANIMATION",
    year: "1988",
    accent: "#E11D2E",
    thesis: "力量沒有長大，只有失控。",
    pair: 4,
    pairLabel: "廢墟與雨夜",
    focus: [0.84, 0.5],
    zoom: 1.5,
  },
  {
    rank: 7,
    file: "04_blade_runner",
    zh: "銀翼殺手",
    en: "BLADE RUNNER",
    medium: "FILM",
    year: "1982／2017",
    accent: "#F0A21B",
    thesis: "比人更懂懷念的複製品。",
    pair: 4,
    pairLabel: "廢墟與雨夜",
    focus: [0.82, 0.5],
    zoom: 1.48,
  },
  {
    rank: 6,
    file: "05_interstellar",
    zh: "星際效應",
    en: "INTERSTELLAR",
    medium: "FILM",
    year: "2014",
    accent: "#F2A65A",
    thesis: "愛是唯一能穿過維度的資料。",
    pair: 3,
    pairLabel: "星海與沙海",
    focus: [0.93, 0.5],
    zoom: 1.5,
  },
  {
    rank: 5,
    file: "06_dune",
    zh: "沙丘",
    en: "DUNE",
    medium: "FILM",
    year: "2021／2024",
    accent: "#C2410C",
    thesis: "預知讓自由變成最重的負擔。",
    pair: 3,
    pairLabel: "星海與沙海",
    focus: [0.9, 0.62],
    zoom: 1.42,
    shade: 0.16,
  },
  {
    rank: 4,
    file: "07_matrix",
    zh: "駭客任務",
    en: "THE MATRIX",
    medium: "FILM",
    year: "1999",
    accent: "#00FF66",
    thesis: "選擇本身，也是被設計好的。",
    pair: 2,
    pairLabel: "母體與夢境",
    focus: [0.8, 0.5],
    zoom: 1.12,
  },
  {
    rank: 3,
    file: "08_paprika",
    zh: "紅辣椒",
    en: "PAPRIKA",
    medium: "ANIMATION",
    year: "2006",
    accent: "#FF2E88",
    thesis: "夢是還沒被命名的心靈。",
    pair: 2,
    pairLabel: "母體與夢境",
    focus: [0.84, 0.5],
    zoom: 1.28,
    shade: 0.3,
  },
  {
    rank: 2,
    file: "09_ghost_in_the_shell",
    zh: "攻殼機動隊",
    en: "GHOST IN THE SHELL",
    medium: "ANIMATION",
    year: "1995",
    accent: "#59E1D6",
    thesis: "當記憶可以備份，靈魂住在哪裡？",
    pair: 1,
    pairLabel: "義體與巨人",
    focus: [0.94, 0.5],
    zoom: 1.5,
  },
  {
    rank: 1,
    file: "10_attack_on_titan",
    zh: "進擊的巨人",
    en: "ATTACK ON TITAN",
    medium: "ANIMATION",
    year: "2013–2023",
    accent: "#B3121A",
    thesis: "自由，是踩過別人的自由。",
    pair: 1,
    pairLabel: "義體與巨人",
    focus: [0.88, 0.56],
    zoom: 1.5,
    shade: 0.28,
  },
];

export const START = [50, 62, 73, 85, 98, 112, 126, 141, 157, 174];
export const DUR = [12, 11, 12, 13, 14, 14, 15, 16, 17, 18];

export const PAIR_ORDER = [5, 5, 4, 4, 3, 3, 2, 2, 1, 1];

export const PAIR_COLOR: Record<number, string> = {
  5: "#7DD3FC",
  4: "#E11D2E",
  3: "#F2A65A",
  2: "#00FF66",
  1: "#59E1D6",
};

export const FOOTER_NOTE = "ORIGINAL ARTWORK · NO FILM STILLS USED";

export const activeIndex = (frame: number) => {
  let index = 0;
  for (let i = 0; i < START.length; i += 1) {
    if (frame >= START[i]) index = i;
  }
  return index;
};

export type Rect = { x: number; y: number; w: number; h: number };
export type TextBox = { x: number; y: number; w: number };
export type Layout = { panel: Rect; text: TextBox };

export const LAYOUTS: Record<number, Layout> = {
  5: {
    panel: { x: 96, y: 150, w: 820, h: 780 },
    text: { x: 1010, y: 330, w: 760 },
  },
  4: {
    panel: { x: 1004, y: 150, w: 820, h: 780 },
    text: { x: 110, y: 330, w: 760 },
  },
  3: {
    panel: { x: 96, y: 150, w: 1000, h: 720 },
    text: { x: 1136, y: 330, w: 640 },
  },
  2: {
    panel: { x: 1004, y: 150, w: 820, h: 780 },
    text: { x: 110, y: 330, w: 760 },
  },
  1: {
    panel: { x: 96, y: 110, w: 1000, h: 860 },
    text: { x: 1136, y: 330, w: 640 },
  },
};

const MORPHS: Array<{ from: number; to: number; a: number; b: number }> = [
  { from: 5, to: 4, a: 73, b: 77 },
  { from: 4, to: 3, a: 98, b: 102 },
  { from: 3, to: 2, a: 126, b: 130 },
  { from: 2, to: 1, a: 157, b: 161 },
];

const rectLerp = (a: Rect, b: Rect, t: number): Rect => ({
  x: a.x + (b.x - a.x) * t,
  y: a.y + (b.y - a.y) * t,
  w: a.w + (b.w - a.w) * t,
  h: a.h + (b.h - a.h) * t,
});

const textLerp = (a: TextBox, b: TextBox, t: number): TextBox => ({
  x: a.x + (b.x - a.x) * t,
  y: a.y + (b.y - a.y) * t,
  w: a.w + (b.w - a.w) * t,
});

export const layoutAt = (frame: number): Layout => {
  for (const morph of MORPHS) {
    if (frame >= morph.a && frame <= morph.b) {
      const t = interpolate(frame, [morph.a, morph.b], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: Easing.inOut(Easing.cubic),
      });
      const from = LAYOUTS[morph.from];
      const to = LAYOUTS[morph.to];
      return {
        panel: rectLerp(from.panel, to.panel, t),
        text: textLerp(from.text, to.text, t),
      };
    }
  }
  return LAYOUTS[PAIR_ORDER[activeIndex(frame)]];
};
