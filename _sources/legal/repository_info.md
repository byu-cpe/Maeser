# About the licenses used in the Maeser project

This is a guide for what licenses are used where and should continue to be used for new code contributions.
If a directory or file type is not explicitly listed, find the most similar item listed.

## The `maeser` package (`maeser/` directory)

File or directory | Type of file(s) | Current license | Acceptable licenses for new files in the same family
---:|:---:|:---:|:---
`maeser/*.py` | Python source | [LGPL v3](LGPL.md)+ | [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)
`maeser/graphs/*.py` | Python source | [LGPL v3](LGPL.md)+ | [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)
`maeser/controllers/*.py` | Python source | [LGPL v3](LGPL.md)+ | [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)
`maeser/controllers/common/*.py` | Python source | [LGPL v3](LGPL.md)+ | [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)
`maeser/chat/*.py` | Python source | [LGPL v3](LGPL.md)+ | [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)
`maeser/data/static/bootstrap-icons/*` | Bootstrap icon package | [MIT](MIT.md) | [MIT](MIT.md), [CC0](CC0.md)
`maeser/data/static/*.js` | JavaScript source | [LGPL v3](LGPL.md)+ | [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)
`maeser/data/static/styles.css` | Cascading Style Sheets source | [LGPL v3](LGPL.md)+ | [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)
`maeser/data/static/normalize.css` | Cascading Style Sheets source | [CC0](CC0.md) | [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)
`maeser/data/static/*.png` | Image | [CC-BY-SA 4.0](CCBYSA4.md) | [CC-BY-SA 4.0](CCBYSA4.md), [CC0](CC0.md)
`maeser/data/templates/*.html` | Jinja2 HTML source | [LGPL v3](LGPL.md)+ | [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)

New sources in this directory should be compatible with the LGPL.


## The example usage for the `maeser` package (`example/` directory)

File or directory | Type of file(s) | Current license | Acceptable licenses for new files in the same family
---:|:---:|:---:|:---
`example/*.py` | Python source | [LGPL v3](LGPL.md)+ | [AGPL v3](AGPL.md)+*, [GPL v3](GPL.md)+*, [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)
`example/vectorstores/*` | Vector Store | [CC-BY-SA 4.0](CCBYSA4.md) | [CC-BY-SA 4.0](CCBYSA4.md), [CC0](CC0.md)
`example/static/*.png` | Image | Public Domain + [CC-BY-SA 4.0](CCBYSA4.md) | [CC-BY-SA 4.0](CCBYSA4.md), [CC0](CC0.md)


## The unit tests for the `maeser` package (`tests/` directory)

File or directory | Type of file(s) | Current license | Acceptable licenses for new files in the same family
---:|:---:|:---:|:---
`tests/*.py` | Python source | [LGPL v3](LGPL.md)+ | [AGPL v3](AGPL.md)+*, [GPL v3](GPL.md)+*, [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)
`tests/chat/*.py` | Python source | [LGPL v3](LGPL.md)+ | [AGPL v3](AGPL.md)+*, [GPL v3](GPL.md)+*, [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)


## GitHub config (`.github/` directory)

File or directory | Type of file(s) | Current license | Acceptable licenses for new files in the same family
---:|:---:|:---:|:---
`.github/*.py` | Python source | [LGPL v3](LGPL.md)+ | [AGPL v3](AGPL.md)+*, [GPL v3](GPL.md)+*, [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)
`.github/Makefile` | Makefile source | [LGPL v3](LGPL.md)+ | [AGPL v3](AGPL.md)+*, [GPL v3](GPL.md)+*, [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)


## Sphinx Documentation (`sphinx-docs/` directory)

File or directory | Type of file(s) | Current license | Acceptable licenses for new files in the same family
---:|:---:|:---:|:---
`sphinx-docs/*.py` | Python source | [LGPL v3](LGPL.md)+ | [AGPL v3](AGPL.md)+*, [GPL v3](GPL.md)+*, [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)
`sphinx-docs/Makefile` | Makefile source | [LGPL v3](LGPL.md)+ | [AGPL v3](AGPL.md)+*, [GPL v3](GPL.md)+*, [LGPL v3](LGPL.md)+, [MIT](MIT.md), [CC0](CC0.md)
`sphinx-docs/*/*.md` | Markdown source | [CC-BY-SA 4.0](CCBYSA4.md) | [CC-BY-SA 4.0](CCBYSA4.md), [CC0](CC0.md)

*AGPL and GPL can be used outside of the package while keeping the package LPGL, so long as no GPL code is backported to the LGPL codebase. Otherwise, the package will need to be licensed under the GPL.
