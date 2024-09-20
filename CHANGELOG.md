# Changelog

All notable changes are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2024-09-20

### Added

- Excalidraw process diagrams for blog.
- Favicon.

### Changed

- Bumped Shiny version to 1.1.0

### Removed

- Unused reactive import in app.py.

## [iter-*]  - 2024-09-17

### Added

- In development iterations of app for use in upcoming blog post.

## [1.1.0] - 2024-09-13

### Added

- UI link to source code on GitHub.
- CHANGELOG.md.


## [1.0.2] - 2024-09-12

### Changed

- Refactored Dockerfile to COPY all python files to base image.
- Refactored app server to include handle_credentials.py &
moderations.py.

## [1.0.1] - 2024-09-11

### Added

- Updated docstrings to numpy format.

### Fixed

- Async used to await api key authentication.

### Changed

- Minor UI change in the wording of api key not being cached between
sessions.
- Removed duplicated chat stream initialisation.
- Single client initialisation.
- Actions reference commit SHA instead of version.

## [1.0.0] - 2024-09-11

### Added

- Docstrings.
- Deployment action.
- Shell file to run container & launch browser.
- Dockerfile.
- Check key validity prior to instantiating openai client.
- Action button to API key submission field.
- Check user prompt against openai moderations endpoint prior to querying
gpt-3.5-turbo.
- Initial app design.

### Changed

- Code formatting.
- More explicit game-over statement.
