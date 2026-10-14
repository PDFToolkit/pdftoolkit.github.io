# Documentation changelog

## [Unreleased]

## [0.1.2] - 2026-10-14

- Keep the component search input at its normal control height on desktop and
  mobile. Remove a flex basis that incorrectly applied 230 pixels to its height
  inside a column label; retain the responsive width and minimum 44-pixel height.
- Fingerprint stylesheet URLs from their content so browsers load updated styles
  after a documentation deployment instead of retaining a cached previous version.

## [0.1.1] - 2026-10-14

- Document Composer installation of all four PHP libraries from Packagist,
  including optional modules and the core's independent installation.
- Link the published Packagist packages from package cards, module entry points
  and API package indexes.
- Distinguish application installation from the locked development checkout
  used to execute tutorials and build their actual PDF results.
- Select core 0.5.4 and module 0.1.5 source releases for the documented package
  versions and installation commands.

## [0.1.0] - 2026-10-14

- Centralize PDFToolkit documentation at https://pdftoolkit.github.io/ in a
  dedicated repository, with shared guides, tutorials, API pages and real PDFs.
- Add dedicated entry points and centrally rendered guides for the core, reader,
  image converters and font converters.
- Separate documentation provenance from each package's published version and
  exact source commit. Validate stable source pins and generated source links.
- Select core 0.5.3 and optional module 0.1.4 releases for this first documentation
  version, with their published tags and exact package commits.
- Preserve existing `/pdf/` navigation, queries, fragments and binary downloads
  through a compatibility deployment.
