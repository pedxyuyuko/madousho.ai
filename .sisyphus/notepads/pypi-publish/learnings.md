# PyPI Publishing Learnings

## February 28, 2026
- Successfully configured pyproject.toml for PyPI publishing with comprehensive metadata
- Key fields added: name="madousho-ai", authors, maintainers, license, readme, classifiers, URLs
- Expanded description based on architecture.md to properly describe the systematic AI agent framework
- Proper TOML structure required: dependencies and other fields must be under [project] table, not as separate tables
- URLs section needed to use [project.urls] table correctly to avoid conflicts with dependencies
- Both sdist and wheel builds succeeded with python -m build
- Twine check confirmed package validity for PyPI upload
- Setuptools deprecation warnings noted regarding license format (can be updated to SPDX expression in future)

## PyPI README Updates - February 28, 2026

### Key Changes Made
- Updated README.md from minimal "Systematic Agent I guess" to comprehensive description based on architecture.md
- Added installation instructions using pip install madousho-ai
- Included CLI commands documentation with examples
- Added basic usage examples showing flow decorators
- Documented core features of the framework
- Maintained existing development setup instructions for contributors

### Technical Notes
- README validates correctly with readme-renderer after installing cmarkgfm dependency
- Markdown syntax is compatible with PyPI rendering requirements
- Structure maintains compatibility with both GitHub and PyPI rendering

### Content Sources
- Primary content sourced from madousho-architecture.md
- Focus on key selling points: systematic agent control vs randomness in traditional agents
- Emphasis on the "fixed flow control + AI execution" concept

## GitHub Actions PyPI Publishing - February 28, 2026

- Created GitHub Actions workflow for trusted publisher (OIDC) authentication
- Used `pypa/gh-action-pypi-publish@release/v1` for secure PyPI publishing without API tokens
- Implemented proper release trigger with `release.types: [published]`
- Configured environment `pypi` with URL to the package page
- Set required `id-token: write` permission for OIDC authentication
- Included build and publish jobs with proper dependencies
- Addressed yamllint warnings by using array format for event types
- OIDC authentication is more secure than using PYPI_API_TOKEN secrets
- Workflow builds sdist and wheel distributions before publishing

# TestPyPI Workflow Creation (Feb 28, 2026)

- Created GitHub Actions workflow `.github/workflows/pypi-test-publish.yml` for publishing to TestPyPI
- Workflow triggers on push to main branch for testing before production releases
- Used Trusted Publisher (OIDC) authentication instead of API tokens for security
- Included `permissions: id-token: write` which is mandatory for OIDC-based publishing
- Used `pypa/gh-action-pypi-publish@release/v1` action with `repository-url: https://test.pypi.org/legacy/`
- Applied proper YAML formatting validated with yamllint using custom configuration for GitHub Actions workflows
- Set up GitHub Environment `testpypi` for secure deployment configuration
- Built distribution packages using `python -m build` before publishing
- Configuration allows testing package integrity before pushing to production PyPI

# YAML Indentation Fix - February 28, 2026

- Fixed indentation issue in `.github/workflows/pypi-test-publish.yml` that was causing yamllint validation failure
- Original error: "wrong indentation: expected 6 but found 4 (indentation)" at line 17 position 5
- Steps section required consistent 6-space indentation for list items under the 4-space "steps:" key
- Added document start marker "---" to comply with project's yamllint configuration
- Final validation passes without errors, ensuring workflow will execute properly in GitHub Actions
- Proper indentation in GitHub Actions workflows is critical: parent keys like "steps:" use 4 spaces, list items use 6 spaces