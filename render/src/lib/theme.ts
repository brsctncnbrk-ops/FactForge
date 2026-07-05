// Shared visual language for all 16 templates. Components read from here so a
// future restyle is one file, not sixteen.
//
// Style target: bright flat-vector infographic (The Infographics Show) — solid
// flat colors, no gradients/grain/vignette, thick rounded shapes, bold
// geometric sans. loadFont() is called once at module scope (Remotion caches
// this internally) so every template gets the family without importing fonts
// itself.
import { loadFont } from "@remotion/google-fonts/Poppins";

const { fontFamily: poppins } = loadFont("normal", {
  weights: ["500", "700", "800"],
});

export const theme = {
  bg: "#123B6B",
  bgAlt: "#0D2C52",
  panel: "rgba(255,255,255,0.10)",
  text: "#FFFFFF",
  textDim: "#B9CBE4",
  accent: "#FF9736",
  accentAlt: "#FF5C5C",
  good: "#3DD68C",
  stroke: "rgba(255,255,255,0.85)",
  fontTitle: `'${poppins}', 'Segoe UI', Arial, sans-serif`,
  fontBody: `'${poppins}', 'Segoe UI', Arial, sans-serif`,
  fontWeightTitle: 800,
  fontWeightBody: 500,
} as const;

export const absoluteFill: React.CSSProperties = {
  position: "absolute",
  inset: 0,
};

export const centerColumn: React.CSSProperties = {
  position: "absolute",
  inset: 0,
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
};

// Flat solid field (no gradient) — SceneFrame's default background.
export const bgGradient = theme.bg;
