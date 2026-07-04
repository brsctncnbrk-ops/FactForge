// Inlines an SVG asset into the DOM (instead of <Img>) so `currentColor`
// fills inherit the CSS `color` we set — our CC0 icon/figure assets are
// single-fill currentColor vectors. Uses delayRender so the render waits for
// the fetch.
import { useEffect, useState } from "react";
import { cancelRender, continueRender, delayRender } from "remotion";

const cache = new Map<string, string>();

// Strip the root <svg> width/height attributes and set 100%/100% so the
// wrapping div controls the rendered size (our assets carry small intrinsic
// px sizes that would otherwise win).
const normalizeSize = (svg: string): string =>
  svg.replace(/<svg\b[^>]*>/, (tag) => {
    const cleaned = tag
      .replace(/\s(width|height)="[^"]*"/g, "")
      .replace(/\s(width|height)='[^']*'/g, "");
    return cleaned.replace(/<svg\b/, '<svg width="100%" height="100%"');
  });

export const InlineSvg: React.FC<{
  src: string;
  color?: string;
  style?: React.CSSProperties;
}> = ({ src, color, style }) => {
  const [svg, setSvg] = useState<string | null>(cache.get(src) ?? null);
  const [handle] = useState(() =>
    cache.has(src) ? null : delayRender(`InlineSvg ${src}`)
  );

  useEffect(() => {
    if (cache.has(src)) {
      return;
    }
    let cancelled = false;
    fetch(src)
      .then((r) => {
        if (!r.ok) throw new Error(`SVG fetch failed: ${src} (${r.status})`);
        return r.text();
      })
      .then((raw) => {
        const text = normalizeSize(raw);
        cache.set(src, text);
        if (!cancelled) {
          setSvg(text);
          if (handle !== null) continueRender(handle);
        }
      })
      .catch((err) => cancelRender(err));
    return () => {
      cancelled = true;
    };
  }, [src, handle]);

  if (svg === null) {
    return null;
  }
  return (
    <div
      style={{ color, lineHeight: 0, display: "flex", ...style }}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
};
