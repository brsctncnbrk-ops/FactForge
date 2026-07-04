// Template name (schema enum) -> Remotion component. The names must match
// scenes-file.schema.json's template enum exactly; validate.py has already
// checked every scene's props against /templates/schemas before render.
import type { Scene } from "../types/generated";
import { ChartScene } from "./ChartScene";
import { ComparisonSplit } from "./ComparisonSplit";
import { IconGrid } from "./IconGrid";
import { ImageSpotlight } from "./ImageSpotlight";
import { ListReveal } from "./ListReveal";
import { MapScene } from "./MapScene";
import { QuoteCard } from "./QuoteCard";
import { SilhouetteScene } from "./SilhouetteScene";
import { StatCard } from "./StatCard";
import { TextEmphasis } from "./TextEmphasis";
import { TimelineScene } from "./TimelineScene";
import { TransitionBreak } from "./TransitionBreak";

export const renderScene = (scene: Scene): React.ReactElement => {
  // props were schema-validated upstream; the cast crosses from the generic
  // Scene.props object to the template-specific generated type.
  const p = scene.props as never;
  const fromLibrary = scene.assets.fromLibrary ?? [];
  switch (scene.template) {
    case "map-scene":
      return <MapScene p={p} fromLibrary={fromLibrary} />;
    case "timeline-scene":
      return <TimelineScene p={p} />;
    case "stat-card":
      return <StatCard p={p} />;
    case "comparison-split":
      return <ComparisonSplit p={p} />;
    case "list-reveal":
      return <ListReveal p={p} />;
    case "quote-card":
      return <QuoteCard p={p} />;
    case "silhouette-scene":
      return <SilhouetteScene p={p} />;
    case "chart-scene":
      return <ChartScene p={p} />;
    case "icon-grid":
      return <IconGrid p={p} />;
    case "text-emphasis":
      return <TextEmphasis p={p} />;
    case "image-spotlight":
      return <ImageSpotlight p={p} />;
    case "transition-break":
      return <TransitionBreak p={p} />;
    default:
      throw new Error(`Unknown template "${scene.template}"`);
  }
};
