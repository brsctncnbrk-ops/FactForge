// Shared visual language for all 12 templates. Components read from here so a
// future restyle is one file, not twelve.
export const theme = {
  bg: "#101420",
  bgAlt: "#181f30",
  panel: "rgba(255,255,255,0.06)",
  text: "#f2ede3",
  textDim: "#a8a294",
  accent: "#d4a24e",
  accentAlt: "#b3452f",
  good: "#7fae6a",
  stroke: "rgba(242,237,227,0.25)",
  fontTitle:
    "'Georgia', 'Times New Roman', serif",
  fontBody:
    "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
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

export const bgGradient = `radial-gradient(120% 120% at 50% 20%, ${theme.bgAlt} 0%, ${theme.bg} 70%)`;
