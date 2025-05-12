import React, { ReactNode } from "react";
import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib";
import { embed_item } from "@bokeh/bokehjs/lib/embed";

declare global {
  interface Window {
    Bokeh?: any;
  }
}

interface State {
  eventDetailMap: Map<string, unknown>;
}

class StreamlitBokehEventsComponent extends StreamlitComponentBase<State> {
  public state: State = { eventDetailMap: new Map() };

  private debounced(delay: number, fn: (...args: any[]) => void) {
    let timer: ReturnType<typeof setTimeout> | undefined;
    return (...args: any[]) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), delay);
    };
  }

  private handleEvent = (event: CustomEvent) => {
    this.setState(
      prev => {
        const map = new Map(prev.eventDetailMap);
        map.set(event.type, event.detail);
        return { eventDetailMap: map };
      },
      () => Streamlit.setComponentValue(
        Object.fromEntries(this.state.eventDetailMap)
      )
    );
  };

  private plotChart() {
    const containerId = this.props.args["_id"];
    const container = document.getElementById(containerId);
    if (!container) return;

    while (container.firstChild) container.removeChild(container.firstChild);

    const events = (this.props.args["events"] as string)
      .split(",")
      .map(e => e.trim())
      .filter(Boolean);
    const debounceTime = this.props.args["debounce_time"] ?? 50;
    const debouncedHandler = this.debounced(debounceTime, this.handleEvent);
    events.forEach(evt =>
      document.addEventListener(evt, debouncedHandler as EventListener)
    );

    const jsonItem = JSON.parse(this.props.args["bokeh_plot"]);
    try {
      embed_item(jsonItem, containerId);
    } catch {
      window.Bokeh?.embed?.embed_item?.(jsonItem, containerId);
    }

    const plotRef =
      jsonItem?.doc?.roots?.references?.find?.(
        (r: any) => r.type === "Plot"
      ) ?? null;
    let height =
      plotRef?.attributes?.height ??
      plotRef?.attributes?.plot_height ??
      600;
    if (this.props.args["override_height"])
      height = this.props.args["override_height"] as number;

    Streamlit.setFrameHeight(height);
  }

  componentDidMount() {
    this.plotChart();
  }

  componentDidUpdate() {
    if (this.props.args["refresh_on_update"]) this.plotChart();
  }

  componentWillUnmount() {
    const events = (this.props.args["events"] as string)
      .split(",")
      .map(e => e.trim())
      .filter(Boolean);
    const debounceTime = this.props.args["debounce_time"] ?? 50;
    const debouncedHandler = this.debounced(debounceTime, this.handleEvent);
    events.forEach(evt =>
      document.removeEventListener(evt, debouncedHandler as EventListener)
    );
  }

  render(): ReactNode {
    return (
      <div
        id={this.props.args["_id"]}
        className="stBokehChart"
        style={{ width: "100%", height: "100%" }}
      />
    );
  }
}

export default withStreamlitConnection(StreamlitBokehEventsComponent);
