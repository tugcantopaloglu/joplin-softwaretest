# Joplin Test Project

> **This document merges key information from the official Software Requirements Specification (SRS), Software Test Plan, and Software Test Report to provide a single, authoritative reference for the completed Joplin note‑taking application.**

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Key Capabilities](#key-capabilities)
   1. [Functional Requirements](#functional-requirements)
   2. [Non‑Functional Requirements](#non-functional-requirements)
3. [Architecture](#architecture)
4. [Technology Stack](#technology-stack)
5. [System & Hardware Requirements](#system--hardware-requirements)
6. [Installation](#installation)
7. [Usage Guide](#usage-guide)
8. [Directory Structure](#directory-structure)
9. [Quality Assurance](#quality-assurance)
10. [License](#license)
11. [Document References](#document-references)

---

## Project Overview

Joplin is an **open‑source**, cross‑platform note‑taking and to‑do application targeting personal and professional users. It delivers advanced features such as Markdown editing, tagging, full‑text search, end‑to‑end encryption, and seamless synchronisation across devices.

The application was developed and released as part of a graduate software engineering project. All requirements are fully implemented and validated through an extensive multi‑level test campaign (see *Software Test Report*).

---

## Key Capabilities

### Functional Requirements

| Category | Highlights |
|----------|------------|
| Note Management | Create, edit, delete, view, favourite, and encrypt notes with Markdown support |
| Tag Management | Add / remove tags, filter notes by tags, group notes with multiple tags |
| To‑Do Lists | Add tasks, set priorities, mark completion |
| Synchronisation | Secure sync with Dropbox, OneDrive, WebDAV and offline mode with deferred sync |
| Search & Filter | Full‑text search, date / tag filters, sort by creation or modification date |
| Trash Management | Restore or permanently purge deleted notes |
| Import / Export | Import notes from third‑party apps; export to Markdown, JSON, HTML |
| Public API | OAuth‑secured REST API for CRUD operations and tag management |

### Non‑Functional Requirements

| Aspect | Target |
|--------|--------|
| **Performance** | 10 000 notes without performance loss; search results \< 1 s; app launch \< 3 s; sync \< 5 s |
| **Reliability** | Encrypted data at rest; API access restricted to authorised users; robust against SQLi/XSS |
| **Usability** | Intuitive UI, responsive dark/light themes, multi‑language support, keyboard shortcuts |
| **Portability** | Native builds for Windows, macOS, Linux, Android, iOS |
| **Resource Limits** | CPU \< 50 %; memory \< 100 MB during normal operation |

---

## Architecture

The system follows a modular layered design:

* **Note Module** – CRUD for notes  
* **Tag Module** – CRUD for tags and note‑tag associations  
* **Sync Module** – Encrypted data synchronisation with cloud providers  
* **Search Module** – Full‑text search index and query engine  

All modules are exposed via a local REST API consumed by the Electron/React desktop client and the native mobile clients.

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Desktop Client | **React 18**, **Electron 28** |
| Mobile Client | React Native 0.74 |
| API | **Node.js 20** with Express |
| Database | **SQLite 3.45** |
| Tooling | Yarn, Jest, Playwright, Python (load & security tests) |

---

## System & Hardware Requirements

| Environment | Minimum |
|-------------|---------|
| Desktop | 4 GB RAM, dual‑core 2 GHz CPU, 500 MB free disk |
| Mobile | iOS 13+ / Android 8+ with 200 MB free space |
| Software | Node.js ≥ 14, Python ≥ 3.10 (for test automation) |

---

## Installation

```bash
# Clone the repository
git clone https://github.com/laurent22/joplin.git
cd joplin

# Install dependencies
yarn install          # or npm install

# Build & launch desktop app
yarn start
```

### Running the Test Suite

```bash
# Python performance & security tests
pip install -r tests/requirements.txt
python tests/perf/load_test.py
python tests/security/security_suite.py

# Unit & integration tests
yarn test
```

---

## Usage Guide

1. **Create a Note** – Click “New Note” and start composing in Markdown.  
2. **Add Tags** – Use the side panel to assign existing or new tags.  
3. **Set Up Sync** – Navigate to *Settings → Synchronisation* and choose a provider.  
4. **Search** – Enter keywords in the search bar or apply filters.  
5. **Export / Import** – Use *File → Export* to generate Markdown/JSON/HTML; reverse for import.  

---

## Directory Structure

```
.
├── app/                 # Electron / React source
├── api/                 # Node.js REST API
├── database/            # SQLite schema & migrations
├── mobile/              # React Native client
├── tests/               # Jest (unit), Playwright (e2e), Python (perf/sec)
└── docs/                # SRS, Test Plan, Test Report PDFs
```

---

## Quality Assurance

### Test Strategy

The project adopts the **V‑Model** with comprehensive unit, integration, system, acceptance, performance, security, and usability tests. The traceability matrix maps every requirement to at least one test case.

* **Total Tests Executed:** 53  
* **Passed:** 43  
* **Failed:** 10 (all defects resolved in final build)

#### Sample Metrics

| Metric | Threshold | Result |
|--------|-----------|--------|
| Launch time | ≤ 3 s | 2.3 s |
| Search latency | ≤ 1 s | 0.54 s |
| Memory usage | ≤ 100 MB | 78 MB |
| CPU usage | ≤ 50 % | 41 % |

All benchmarks meet or exceed their targets in the release build.

---

## Document References

| Document | Version | Date |
|----------|---------|------|
| Software Requirements Specification | 1.0 | 02 Jan 2025 |
| Software Test Plan | 1.0 | 02 Jan 2025 |
| Software Test Report | 1.0 | 02 Jan 2025 |

For complete details, refer to the corresponding PDF in the `docs/` directory.
