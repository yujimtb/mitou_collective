# Security Policy

## Reporting

If you discover a security issue, please avoid opening a public issue with exploit details.

Instead, contact the maintainer directly through a private channel if one is available. If no private channel is available yet, open a minimal public issue that only states that you found a security concern and request a private contact path.

## Scope

This repository is a research prototype. Security hardening is not complete, and interfaces may change quickly.

Areas that deserve particular care include:

- authentication and token handling
- proposal and review authorization rules
- API input validation
- seed and demo-data execution paths

## Expectations

- do not publish credentials or sensitive data in issues
- do not publish proof-of-concept exploit code until a fix is available
- include reproduction steps, impact, and affected paths when reporting