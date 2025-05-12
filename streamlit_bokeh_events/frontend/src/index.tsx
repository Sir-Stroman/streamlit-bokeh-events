import React from "react";
import { createRoot } from "react-dom/client";
import StreamlitBokehEventsComponent from "./StreamlitBokehEventsComponent";

const root = createRoot(document.getElementById("root") as HTMLElement);

root.render(
  <React.StrictMode>
    <StreamlitBokehEventsComponent />
  </React.StrictMode>
);
