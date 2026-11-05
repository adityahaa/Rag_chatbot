# Preparing a later deployment

Current delivery is a single-user Windows application bound to 127.0.0.1. There is no
public deployment, cloud database or credential integration. Python API routes, a separate
static frontend, pinned dependencies, source provenance and local model manifests provide
clear boundaries for later work.

A shared host needs authenticated workspace ownership, durable encrypted document/evidence
storage with explicit retention, server-side session authorization, upload/job quotas, worker
isolation for model/parser workloads, and an origin/host policy for the intended domain.
Add these before exposing the process publicly. Current host restriction, nonpersistent
sessions and loopback-only launch are intentional and must not be described as shared-host
security. If moving inference to an external provider, first add explicit disclosure and
consent about exactly which document chunks and questions are transmitted, with a free-only
configuration and no paid fallback.

Before any release, recheck dataset and original-contributor permissions, remove test-only
research fixtures if inappropriate, run the full input–review–decision–export workflow on
that host, and record model/runtime limits. The optional FLAN-T5 model has a negative local
quality result; public release must retain its experimental label or replace it under a
new, independently evaluated development/evaluation plan.
