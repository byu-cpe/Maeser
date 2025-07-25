// This script replaces the content of the author and copyright sections, allowing hyperlinks to be inserted

// Get relative link of TOC page
function get_toc_link(page_name) {
  toc_links = document.getElementsByClassName("reference internal");
  target_page = Array.from(toc_links).find(el => el.textContent == page_name);
  target_href = target_page.getAttribute('href');
  return `<a href='${target_href}'>${page_name}</a>`
}


document.addEventListener("DOMContentLoaded", () => {
  GITHUB_URL = "https://github.com/byu-cpe/Maeser";
  const AUTHOR_CONTENT = 
    `By the Maeser Team. See the <a href='${GITHUB_URL}/graphs/contributors'>full list of contributors</a> in the GitHub repository.`;
  const COPYRIGHT_CONTENT = 
    `© Copyright 2025. Licensed under the GNU Lesser General Public License v3.0 or later. For more details, see ${get_toc_link("About the licenses used in the Maeser project")}.`;

  const author = document.getElementsByClassName("component-author")[0];
  const copyright = document.getElementsByClassName("copyright")[0];

  author.innerHTML = AUTHOR_CONTENT;
  copyright.innerHTML = COPYRIGHT_CONTENT;
});