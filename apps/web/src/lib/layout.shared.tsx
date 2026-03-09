import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

const baseUrl = "https://typemap.nesalia.com";

export function baseOptions(): BaseLayoutProps {
  return {
    nav: {
      title: "typemap",
    },
    githubUrl: "https://github.com/nesalia-inc/python-typemap",
  };
}

export { baseUrl };
