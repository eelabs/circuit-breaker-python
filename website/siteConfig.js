const projectName = "circuit-breaker-python"
const owner = "eelabs"

const siteConfig = {
  title: 'Circuit Breaker for Requests',
  tagline: "If it's broke, don't call it",
  url: `https://${owner}.github.io`,
  baseUrl: `/${projectName}/`,
  projectName: projectName,
  organizationName: owner,
  headerLinks: [
    { search: false },
    { doc: 'getting-started', label: 'Docs' }
  ],
  colors: {
    primaryColor: '#58251e',
    secondaryColor: '#3d1915'
  },
  copyright: `Copyright © ${new Date().getFullYear()} ${owner}.`,
  highlight: {
    theme: 'github'
  },
  onPageNav: 'separate',
  cleanUrl: true,
  docsSideNaveCollapsible: true,
  repoUrl: `https://github.com/${owner}/${projectName}`,
  scripts: [
    'https://cdnjs.cloudflare.com/ajax/libs/mermaid/8.4.4/mermaid.min.js',
    '/init.js',
  ],
  markdownPlugins: [
    (md) => {
      md.renderer.rules.fence_custom.mermaid = (tokens, idx, options, env, instance) => {
        return `<div class="mermaid">${tokens[idx].content}</div>`;
      };
    }
  ]
};

module.exports = siteConfig;
