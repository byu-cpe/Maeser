// This small javascript code replaces the content of the author and copyright sections, allowing hyperlinks to be inserted

GITHUB_URL = "https://github.com/byu-cpe/Maeser";

const AUTHOR_CONTENT = 
    `By the Maeser Team. See the <a href='${GITHUB_URL}/graphs/contributors'>full list of contributors</a> in the GitHub repository.`;

const COPYRIGHT_CONTENT = 
    `© Copyright 2025. Licensed under the GNU Lesser General Public License v3.0 or later. For more details, see <a href='${GITHUB_URL}/blob/master/COPYING.LESSER.md'>COPYING.LESSER.md</a> and <a href='${GITHUB_URL}/blob/master/COPYING.md'>COPYING.md</a> in the GitHub repository.`;

document.addEventListener("DOMContentLoaded", () => {
  const author = document.getElementsByClassName("component-author")[0];
  const copyright = document.getElementsByClassName("copyright")[0];

  author.innerHTML = AUTHOR_CONTENT;
  copyright.innerHTML = COPYRIGHT_CONTENT;
});