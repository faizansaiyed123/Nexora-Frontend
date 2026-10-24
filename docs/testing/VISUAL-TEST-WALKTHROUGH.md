# Nexora visual end-to-end walkthrough

This document is generated only after the browser journey passes. The workflow drives the real frontend against FastAPI and disposable PostgreSQL/Redis services, sends account-verification, password-reset and competitive-alert email through a loopback STARTTLS inbox, and publishes browser screenshots with SHA-256 hashes.

Workflow: https://github.com/faizansaiyed123/Nexora-Frontend/actions/workflows/e2e-walkthrough.yml

The collection/discovery engine fetches versioned Schema.org HTML fixtures over HTTPS so extraction and price movement can be verified reproducibly without mocking application API responses. CI evidence is for its tested revisions and disposable services, not the deployed production environment.
