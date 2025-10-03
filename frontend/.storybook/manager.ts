import { addons } from "@storybook/manager-api";
import { create } from "@storybook/theming/create";

const theme = create({
  base: "dark",
  brandTitle: "ruleIQ UI – Storybook",
  brandUrl: "https://example.com",
  colorSecondary: "#8b5cf6"
});

addons.setConfig({ theme });
