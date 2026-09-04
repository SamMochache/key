# KEY — Partner Institution Assessment Dashboard

> **Assessment, evidence, and curriculum-impact dashboard for STEMForge partner institutions.**

KEY is the dashboard layer that sits downstream of STEMForge's curriculum-design and programme-delivery work. Its purpose is to help a partner institution move from **"we delivered the curriculum"** to **"we can demonstrate what learners experienced, what they can do, where they are growing, and where intervention is needed."**

This repository is currently a **frontend prototype / product foundation**. It contains the dashboard experience, reusable UI components, charts, role concepts, and representative data needed to validate the partner-institution workflow before the persistence/API layer is introduced.

---

## Table of Contents

1. [What KEY Is](#what-key-is)
2. [Where KEY Fits in the STEMForge Ecosystem](#where-key-fits-in-the-stemforge-ecosystem)
3. [The Core Problem](#the-core-problem)
4. [Product Philosophy](#product-philosophy)
5. [Current Repository Status](#current-repository-status)
6. [Current Assessment Workflow](#current-assessment-workflow)
7. [End-to-End KEY Flow](#end-to-end-key-flow)
8. [Repository Architecture](#repository-architecture)
9. [Assessment Rubric Model](#assessment-rubric-model)
10. [Data Flow Today](#data-flow-today)
11. [Future Production Data Flow](#future-production-data-flow)
12. [Roles and Permissions](#roles-and-permissions)
13. [What Is Working](#what-is-working)
14. [What Is Still Prototype-Only](#what-is-still-prototype-only)
15. [Recommended Production Roadmap](#recommended-production-roadmap)
16. [Development Principles](#development-principles)
17. [Getting Started](#getting-started)
18. [Testing Checklist](#testing-checklist)
19. [Relationship to STEMForge](#relationship-to-stemforge)
20. [License](#license)

---

## What KEY Is

**KEY** is intended to become the operational assessment and learning-evidence dashboard used by institutions that partner with STEMForge.

The central idea is simple:

```text
STEMForge designs and delivers the learning experience
                    ↓
Partner institution implements the curriculum
                    ↓
Teachers / facilitators collect evidence
                    ↓
KEY records and organises assessment evidence
                    ↓
KEY turns evidence into learner + class insights
                    ↓
Institution identifies strengths, gaps, and interventions
                    ↓
STEMForge + institution improve the programme
```

KEY therefore should not be treated as a generic school-management system. Its strongest product identity is **learning evidence + competency assessment + programme impact**.

---

## Where KEY Fits in the STEMForge Ecosystem

STEMForge is being positioned as a B2B EdTech/STEM partner rather than simply a course catalogue. The curriculum is the intervention; KEY is the measurement and feedback layer around that intervention.

A useful conceptual split is:

| Layer | Responsibility |
|---|---|
| **STEMForge** | Programme design, curriculum design, STEM learning experiences, implementation support |
| **Partner Institution** | Learner enrolment, delivery environment, teachers/facilitators, local academic context |
| **KEY** | Assessment capture, evidence, competency profiles, progress monitoring, reporting |
| **Institution leadership** | Decisions based on the evidence |

This separation keeps KEY focused. The dashboard should answer questions such as:

- What was taught?
- Who participated?
- What evidence was collected?
- Which competencies are developing?
- Which learners need additional support?
- Which classes or cohorts are progressing?
- Is the programme producing the intended learning outcomes?
- What should the institution or STEMForge change next?

---

## The Core Problem

A curriculum can be beautifully designed and still be difficult for a partner institution to evaluate consistently.

Traditional reporting often reduces learning to:

- attendance,
- assignment completion,
- marks,
- exam results.

Those metrics are useful, but they do not fully represent project-based, practical, competency-oriented STEM learning.

KEY is being built around a broader evidence model:

```text
Participation
    +
Observation
    +
Practical work
    +
Projects
    +
Competency rubric
    +
Teacher evidence
    +
Progress over time
    =
Learning picture
```

The dashboard should make that picture understandable to teachers and decision-makers without forcing them to become data analysts.

---

## Product Philosophy

### 1. Measure growth, not only marks

The current dashboard already expresses this idea in the Assessments page: growth is represented through observations, practical work, competencies, and progress rather than marks alone.

### 2. Evidence should explain a score

A competency level without evidence is weak. A future production assessment should therefore associate a selected level with observable evidence, comments, artefacts, or project submissions.

### 3. Curriculum outcomes should drive the rubric

The rubric should ultimately be configurable against the curriculum a partner is implementing. The UI should not hard-code one school's entire academic model.

### 4. Keep the dashboard decision-oriented

The purpose of a chart is not to display data simply because it exists. It should help someone decide what to do next.

### 5. Preserve the existing UI architecture

The current repository already has reusable components for cards, badges, page headers, statistics, charts, and data/types. The assessment work extends that architecture rather than replacing it.

---

## Current Repository Status

The repository currently behaves as a **frontend prototype with local/mock data**.

The existing application already contains a dashboard shell and reusable UI architecture. The assessment area has now been extended on the feature branch to demonstrate the intended partner assessment workflow without restructuring the application.

### Assessment work completed in this branch

- Added a partner assessment workspace.
- Added learner selection.
- Added assessment-period selection.
- Added learning-area selection.
- Added a four-level competency rubric.
- Added selectable competency scores.
- Added observable-evidence guidance for each competency.
- Added evidence/observation notes.
- Added draft/completed assessment state in the UI.
- Added an assessment summary with percentage and competency band.
- Added per-competency progress indicators.
- Retained the existing assignments/projects area.
- Retained the learning-outcome distribution.
- Retained the competency radar visualisation.
- Added explanatory code comments so the prototype's intended production seams are easier to follow.

> **Important:** the current save actions are intentionally local UI state. They do not yet persist assessments to a backend database.

---

## Current Assessment Workflow

The current Assessments page follows this sequence:

### Step 1 — Choose the learner

The assessor selects an enrolled learner from the existing student data.

### Step 2 — Choose the assessment context

The assessor selects:

- assessment period,
- curriculum / learning area.

This is important because the same learner may be assessed against different curriculum outcomes over time.

### Step 3 — Score competencies

The assessor evaluates each competency using four levels:

| Level | Meaning |
|---|---|
| **1 — Emerging** | Beginning to demonstrate the competency with guidance. |
| **2 — Developing** | Demonstrates the competency inconsistently and benefits from support. |
| **3 — Secure** | Demonstrates the competency independently and consistently. |
| **4 — Mastered** | Applies the competency confidently and transfers it to new situations. |

The current competencies are:

- Communication
- Creativity
- Critical Thinking
- Collaboration
- Independence
- Application & Transfer

These are currently representative dashboard data, not yet a backend-configurable institutional rubric.

### Step 4 — Add evidence

The assessor records an observation describing what the learner actually did.

For example:

```text
During the bridge challenge, the learner tested three designs,
explained why the second failed, and independently revised the structure.
```

This is the bridge between a numeric level and defensible assessment evidence.

### Step 5 — Review the learner summary

The dashboard calculates:

- average rubric score,
- percentage equivalent,
- overall performance band,
- per-competency progress,
- evidence status.

### Step 6 — Save as draft or complete

The current prototype supports the conceptual distinction between a draft assessment and a completed assessment.

In production, this should become a persisted assessment lifecycle with audit history rather than a simple local state change.

---

## End-to-End KEY Flow

The larger product flow should eventually look like this:

```text
┌───────────────────────────────┐
│ STEMForge Curriculum Design   │
│ Outcomes / competencies       │
│ Projects / learning activities│
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Partner Programme Setup       │
│ Institution / classes /       │
│ learners / facilitators       │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Curriculum Delivery           │
│ Lessons / projects / practical │
│ activities / observations     │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Evidence Collection            │
│ Rubric levels + notes +        │
│ submissions + observations     │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ KEY Assessment Engine          │
│ Scores / outcomes / trends /   │
│ learner competency profiles    │
└───────────────┬───────────────┘
                │
        ┌───────┴────────┐
        ▼                ▼
┌──────────────┐  ┌────────────────┐
│ Learner View │  │ Class / Cohort │
│              │  │ View           │
└──────┬───────┘  └───────┬────────┘
       │                  │
       └────────┬─────────┘
                ▼
┌───────────────────────────────┐
│ Institution Insights          │
│ Strengths / gaps / trends /   │
│ intervention opportunities    │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Programme Improvement         │
│ Curriculum refinement +       │
│ facilitator support + impact  │
└───────────────────────────────┘
```

### The important distinction

KEY is not simply storing scores.

It should eventually create a **feedback loop**:

```text
Curriculum → Delivery → Evidence → Assessment → Insight → Improvement
     ↑                                                   │
     └───────────────────────────────────────────────────┘
```

That feedback loop is what makes the project strategically useful to STEMForge.

---

## Repository Architecture

The existing structure should be preserved.

A simplified view of the frontend is:

```text
key/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── charts/
│   │   │   └── ui/
│   │   ├── lib/
│   │   │   ├── data.ts
│   │   │   └── types.ts
│   │   ├── pages/
│   │   │   └── Assessments.tsx
│   │   └── ...
│   └── ...
└── README.md
```

### `components/ui/`

Reusable interface primitives such as cards, badges, buttons, page headers, and statistic cards.

The assessment page uses these rather than introducing a parallel design system.

### `components/charts/`

Reusable visualisations. `CompetencyRadarChart` is already present and is used by the assessment dashboard to show a high-level competency profile. fileciteturn40file0L2-L2

### `lib/data.ts`

The current source of representative dashboard data. It includes users/roles, students, classes, assignments, trends, competencies, and comparison data. fileciteturn41file0L2-L2

In a production implementation, this is the layer that should gradually be replaced or supplemented by API-backed data without forcing a rewrite of the UI components.

### `lib/types.ts`

The type definitions provide the domain vocabulary used by the frontend. This should remain the contract between the UI and the future API/data layer.

### `pages/Assessments.tsx`

This is the partner assessment workspace. The feature branch extends the existing page instead of creating a separate assessment application.

---

## Assessment Rubric Model

The current rubric deliberately uses **descriptive performance bands** rather than pretending that every competency can be reduced to an exam mark.

### Rubric entity concept

The eventual backend model should conceptually resemble:

```text
Assessment
├── learner
├── institution
├── class / cohort
├── curriculum
├── learning_area
├── assessment_period
├── assessor
├── status
├── evidence / general notes
└── assessment_items[]
      ├── competency
      ├── level
      ├── evidence
      └── timestamp
```

This is a conceptual model only. It does **not** require changing the current frontend structure yet.

### Why evidence belongs beside the level

Consider:

```text
Critical Thinking = Secure
```

That statement becomes much more useful when the institution can also see:

```text
Evidence:
Learner compared three possible bridge designs,
identified the structural weakness in one design,
and revised the design after testing.
```

This gives leadership a basis for understanding the result and gives the next facilitator a basis for planning intervention.

---

## Data Flow Today

At the moment, the flow is intentionally lightweight:

```text
React component
      ↓
Local component state
      ↓
Derived assessment summary
      ↓
Rendered dashboard
```

The assessment page calculates its summary from the selected rubric values rather than storing a duplicated summary object. This keeps the prototype internally consistent while the user changes scores.

The existing repository also contains representative students, classes, assignments, competency data, and trends in `lib/data.ts`. fileciteturn41file0L2-L2

### What does NOT happen yet

There is currently no demonstrated persistent workflow for:

```text
React
  ↓
HTTP API
  ↓
Authentication / authorisation
  ↓
Database
  ↓
Assessment record
  ↓
Audit trail
```

The README therefore intentionally describes the assessment page as a prototype rather than claiming backend persistence that is not present.

---

## Future Production Data Flow

When the backend is introduced, the intended flow should become:

```text
Teacher / Facilitator
        │
        ▼
KEY Frontend
        │
        │ HTTPS / authenticated API request
        ▼
API / Backend
        │
        ├── Validate user permission
        ├── Validate learner + curriculum
        ├── Validate rubric level
        ├── Store evidence
        └── Create audit event
        │
        ▼
PostgreSQL / persistence layer
        │
        ▼
Analytics / aggregation layer
        │
        ▼
KEY Dashboard
```

The important architectural principle is that the frontend should not become responsible for deciding whether a user is authorised to assess a learner. That belongs to the backend.

---

## Roles and Permissions

The current data model already recognises multiple roles including administrator, principal, teacher, parent, and student. fileciteturn41file0L2-L2

For the production assessment workflow, those roles should have different capabilities.

| Role | Likely assessment responsibility |
|---|---|
| **Administrator** | Institution configuration, users, programmes, reporting |
| **Principal / Leadership** | Institution-wide insight, approval, reporting |
| **Teacher / Facilitator** | Create observations and assessments for assigned learners |
| **Parent** | View permitted learner progress and evidence |
| **Student** | View appropriate personal progress and feedback |
| **STEMForge Programme Team** | Programme-level monitoring and curriculum impact, subject to partner permissions |

These are product recommendations for the eventual backend, not claims that the current prototype enforces all of these permissions.

---

## What Is Working

Based on the repository structure and current implementation, the following pieces are already strong foundations:

### UI architecture

The page is built from reusable `Card`, `CardHeader`, `StatCard`, `Badge`, `Button`, and chart components. This is preferable to embedding an entirely separate UI architecture into the assessment page.

### Existing visual language

The assessment workspace uses the existing dashboard styling, spacing, typography, cards, badges, and chart conventions rather than introducing a new visual system.

### Existing data vocabulary

The repository already models students, classes, roles, assignments, learning trends, and competencies. fileciteturn41file0L2-L2

### Assessment interaction

The feature branch demonstrates the important interaction loop:

```text
Select learner
   ↓
Select context
   ↓
Select competency levels
   ↓
Record evidence
   ↓
Review summary
   ↓
Save draft / complete
```

### Separation of concerns

The existing chart implementation remains reusable. The assessment page consumes the competency radar instead of duplicating chart implementation details. fileciteturn40file0L2-L2

---

## What Is Still Prototype-Only

This is the most important section to keep in mind while developing KEY.

### 1. Data persistence

Assessment changes currently live in React state. Refreshing the page should not be treated as a persistent save.

### 2. Authentication

The repository contains role concepts, but the assessment workflow should eventually be protected by real authentication and backend authorisation.

### 3. Multi-tenancy

A B2B partner product needs strong institution boundaries:

```text
Institution A
  ├── users
  ├── learners
  ├── classes
  └── assessments

Institution B
  ├── users
  ├── learners
  ├── classes
  └── assessments
```

One institution must never be able to access another institution's learner or assessment records.

### 4. Configurable rubrics

The current competency list is representative. Production KEY should allow a curriculum/programme to define its own assessment criteria while retaining reusable competency frameworks where appropriate.

### 5. Evidence attachments

The prototype accepts written evidence. A mature system may eventually support links or attachments for project artefacts, photographs, documents, or other evidence where appropriate and consented.

### 6. Audit history

Assessment changes should be traceable. A completed assessment should not silently change without an audit event or revision history.

### 7. Reporting

The current charts are representative dashboard visuals. Production reporting should calculate results from actual assessment records rather than static arrays.

---

## Recommended Production Roadmap

Do not rewrite the current frontend structure to accomplish this. Build outward from it.

### Phase 1 — Stabilise the assessment UX

- Validate learner selection.
- Validate assessment context.
- Validate rubric interaction.
- Make evidence required before completion where appropriate.
- Add clear validation/error states.
- Add loading/saving states when API integration begins.
- Test desktop and mobile layouts.

### Phase 2 — Define the domain model

Establish backend entities for:

- Institution
- Programme
- Curriculum
- Learning Area
- Outcome
- Competency
- Rubric
- Rubric Level
- Learner
- Class/Cohort
- Assessment
- Assessment Item
- Evidence
- Assessor

The exact schema should be decided alongside the final product requirements rather than prematurely duplicating the frontend state shape.

### Phase 3 — API integration

Introduce authenticated endpoints for:

```text
GET    learners
GET    programmes
GET    rubrics
POST   assessments
GET    assessments/:id
PATCH  assessments/:id
POST   assessments/:id/complete
GET    learners/:id/progress
GET    classes/:id/analytics
```

These endpoint names are a planning model, not an existing API contract.

### Phase 4 — Assessment lifecycle

Move from:

```text
Draft → Complete
```

toward a controlled lifecycle such as:

```text
Draft
  ↓
Submitted
  ↓
Reviewed
  ↓
Finalised
  ↓
Archived
```

Whether all stages are necessary should be determined by the partner institution's operating model.

### Phase 5 — Institution analytics

Build analytics around real evidence:

- learner growth,
- competency distribution,
- class comparison,
- programme outcomes,
- assessment completion,
- intervention candidates,
- longitudinal progress.

### Phase 6 — Reporting

Provide institution-friendly reports such as:

- learner progress report,
- class competency report,
- programme impact report,
- curriculum outcome report,
- assessment completion report.

### Phase 7 — STEMForge feedback loop

The most strategic stage is connecting assessment insight back to programme improvement:

```text
KEY identifies a recurring weakness
             ↓
STEMForge reviews evidence
             ↓
Curriculum / facilitator support is adjusted
             ↓
Partner implements change
             ↓
KEY measures the next cycle
```

---

## Development Principles

### Do not change the existing structure without a reason

The current repository already has a useful component architecture. New functionality should fit into it.

### Prefer reusable components

If a control or presentation pattern appears in multiple pages, promote it into the existing UI component layer instead of creating one-off implementations.

### Keep domain logic understandable

Comments should explain **why** a piece of assessment logic exists, especially where a future API/database boundary is being represented by local prototype state.

### Avoid fake persistence

A button saying "Save" should eventually save to a backend. Until then, the code should make it obvious that the current implementation is a prototype.

### Evidence over unsupported claims

The dashboard should distinguish between:

- observed evidence,
- calculated metrics,
- inferred insights,
- recommendations.

### Privacy by design

Learner assessment information is sensitive institutional data. Production implementation should use least-privilege access, institution isolation, secure authentication, auditability, and appropriate retention policies.

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/SamMochache/key.git
cd key
```

### 2. Enter the frontend

```bash
cd frontend
```

### 3. Install dependencies

```bash
npm install
```

### 4. Start the development server

```bash
npm run dev
```

The exact available scripts should be confirmed against `frontend/package.json` in the working checkout.

---

## Testing Checklist

Before considering the assessment workflow production-ready, test at least the following:

### Functional

- [ ] Learner can be selected.
- [ ] Assessment period can be selected.
- [ ] Learning area can be selected.
- [ ] Every rubric item can be scored.
- [ ] Changing a score recalculates the summary.
- [ ] Evidence can be entered.
- [ ] Draft state is distinguishable from completed state.
- [ ] Completion validation is enforced.
- [ ] Assignments still render correctly.
- [ ] Existing competency chart still renders.

### Responsive

- [ ] Desktop assessment table works.
- [ ] Tablet layout works.
- [ ] Mobile rubric remains usable.
- [ ] Horizontal overflow is intentional and usable where required.
- [ ] Buttons remain accessible on small screens.

### Data integrity

- [ ] Invalid learner IDs cannot be submitted.
- [ ] Invalid rubric levels are rejected by the backend.
- [ ] Users cannot assess learners outside their institution.
- [ ] Completed assessments cannot be silently overwritten.
- [ ] Assessment history is auditable.

### Security

- [ ] Authentication is enforced.
- [ ] Role permissions are enforced server-side.
- [ ] Institution-level data isolation is enforced.
- [ ] Sensitive learner information is not unnecessarily exposed to the client.
- [ ] API validation is enforced independently of frontend validation.

---

## Relationship to STEMForge

The repositories have complementary responsibilities.

### STEMForge

STEMForge is the programme and partnership side:

```text
Partner discovery
      ↓
Programme design
      ↓
Curriculum design
      ↓
Implementation
      ↓
Learning experience
```

### KEY

KEY is the evidence and assessment side:

```text
Learner participation
      ↓
Evidence collection
      ↓
Competency assessment
      ↓
Progress analysis
      ↓
Institution insight
      ↓
Programme improvement
```

Together:

```text
              STEMForge
                  │
       Curriculum + Programme
                  │
                  ▼
        Partner Institution
                  │
                  ▼
                 KEY
                  │
      Assessment + Evidence
                  │
                  ▼
          Programme Insight
                  │
                  ▼
              STEMForge
```

That is the product loop I would preserve as KEY develops.

---

## Current Branch / Assessment Work

This assessment implementation is being developed on a separate feature branch so the existing `main` branch remains unchanged until the work is reviewed.

The intended workflow is:

```text
main
 │
 └── feature/assessment-rubric
          │
          ├── assessment UX
          ├── rubric interaction
          ├── evidence notes
          ├── assessment summary
          └── documentation
                    │
                    ▼
                 Pull Request
                    │
                    ▼
              Review / test
                    │
                    ▼
                  Merge
```

This gives us a clean place to review the assessment work before it becomes part of the main product.

---

## License

License information should be added when the project's distribution terms are finalised.

---

**KEY is intended to make the learning produced by a STEM programme visible, understandable, and actionable.**
