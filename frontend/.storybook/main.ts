import type { StorybookConfig } from "@storybook/nextjs";

const config: StorybookConfig = {
  framework: {
    name: "@storybook/nextjs",
    options: {}
  },
  stories: [
    "../components/**/*.stories.@(ts|tsx|mdx)",
    "../components/ui/**/*.tsx",
    "../_req_pages/stories/**/*.stories.@(ts|tsx|mdx)"
  ],
  addons: [
    "@storybook/addon-essentials",
    "@storybook/addon-a11y",
    "@storybook/addon-interactions",
    "@storybook/addon-viewport",
    "@storybook/addon-links"
  ],
  docs: {
    autodocs: true
  },
  staticDirs: [
    { from: "../public", to: "/" }
  ]
};

export default config;
