// This small javascript code fixes Mermaid diagrams not rendering properly in dark or light mode
document.addEventListener("DOMContentLoaded", () => {
  const theme = document.documentElement.getAttribute("data-theme") === "dark"
    ? "dark"
    : "default";
  mermaid.initialize({ startOnLoad: true, theme });
});