import type { Preview } from "@storybook/react";
import "../styles/globals.css";

const preview: Preview = {
  globals: {
    theme: "dark"
  },
  parameters: {
    backgrounds: {
      default: "dark",
      values: [
        { name: "dark", value: "#000000" }
      ]
    },
    layout: "centered",
    controls: { expanded: true },
    options: { showPanel: true },
    a11y: { element: "#root", manual: false }
  }
};

export default preview;
