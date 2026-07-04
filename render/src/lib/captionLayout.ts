// Shared layout contract for the burned-in caption band. The subtitle overlay
// (CaptionOverlay) owns the bottom strip of the frame; any scene chrome that
// would otherwise sit there (OverlayText labels, source credits) must lift
// clear of it when captions are on. One source of truth so the reserved band
// and the drawing position never drift apart.
import { createContext } from "react";

// Where CaptionOverlay anchors its box (% from the frame bottom).
export const CAPTION_BOTTOM_PCT = 6.5;

// Height of the zone (% from the bottom) a two-line cue can reach. A two-line
// cue at 40px/1.3 line height + padding is ~18% tall counting the anchor
// offset; 20 leaves a small margin. Scene chrome must stay above this.
export const CAPTION_BAND_PCT = 20;

// Bottom offset for lower-third scene labels when captions are burned in —
// just above the reserved band so label and subtitle never overlap.
export const OVERLAY_SAFE_BOTTOM_PCT = CAPTION_BAND_PCT + 1; // 21%

// True only inside the "video-captioned" composition (VideoComposition passes
// a non-null captions prop). Scene templates read this to relocate their own
// bottom text; the plain "video" and "draft" comps leave it false.
export const CaptionsActiveContext = createContext(false);
