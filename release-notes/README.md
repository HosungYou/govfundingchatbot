# GovFunding Chatbot Release Notes

This directory tracks published releases of the GovFunding Chatbot project. Each file captures technical context, deployment guidance, and migration notes for a specific version.

## 📁 Structure

```
release-notes/
├── README.md           # Overview & navigation
├── v1.0.0.md           # Initial architecture scaffolding release
└── v1.1.0.md           # Repository restructure & documentation expansion
```

## 🚀 Current Version

### [v1.1.0](v1.1.0.md) – Repository Restructure & Docs Expansion
**Release Date**: October 10, 2025  
**Type**: Minor Release / Developer Experience

**Highlights**
- ETL code moved to `apps/etl/` with updated scripts and packaging
- New architecture diagram, backlog tracker, and agent responsibilities
- Updated README and project map reflecting upcoming services

**Breaking Changes**: Yes – module import path changed to `apps.etl`  
**Migration Required**: Yes – update scripts and automations to new paths

#### Previous Releases
- [v1.0.0](v1.0.0.md) – Repository bootstrap & architecture blueprint (October 10, 2025)

---

Future releases should append additional files (e.g., `v1.1.0.md`, `v1.0.1.md`) in this directory following the template described in each release document.

**Last Updated**: October 10, 2025  
**Maintainers**: GovFunding Chatbot Core Team
