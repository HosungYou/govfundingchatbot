# Next.js MVP UI Blueprint

## Product Principles
- Highlight timely, actionable funding intel within 10 seconds of landing.
- Keep interaction cost low for grant officers (keyboard-first search, quick filters).
- Make saving and sharing opportunities frictionless to foster collaboration.

## Information Architecture
- **/ (Marketing Landing)**
  - Hero value prop, call-to-action buttons (`Get Updates`, `Try Dashboard`).
  - Live metrics (`new opportunities this week`, `total funding posted`).
  - Testimonials/Use cases panel.
- **/dashboard** (authenticated)
  - Personalized feed: `Saved segments`, `Closing soon`, `New matches`.
  - Insight strip: bar chart of awards by directorate, total available funding.
  - Activity log: alerts sent, team activity (future).
- **/search**
  - Filters: keyword, agency, CFDA, category, award amount slider, close date range.
  - Results list with `OpportunityCard`, infinite scroll.
  - Split view toggle (list ↔ split with detail preview).
- **/opportunities/[id]**
  - Header with key metadata, `Follow opportunity` CTA.
  - Summary, eligibility, timeline milestones, attachments, related opportunities.
  - RAG assistant panel (`Ask about this opportunity`).
- **/settings/alerts**
  - Channels (Email, Slack), frequency, quiet hours.
  - Saved search segments with edit/delete.
  - Notification preview.

## Component Library
- `PrimaryButton`, `SecondaryButton`, `IconButton` (Tailwind variants, Radix Icon usage).
- `OpportunityCard`
  - Props: `title`, `agency`, `closeDate`, `awardRange`, `tags`, `isBookmarked`.
  - Supports `compact` and `default` layout.
- `FilterPanel`
  - Controlled form with React Hook Form + Zod schema.
  - Overlays for advanced filters, quick reset action.
- `InsightKPI`
  - Displays metric, delta arrow, tooltip with definition.
- `AlertPreferenceForm`
  - Stepper UI guiding user through channel selection and alert cadence.
- `CommandPalette`
  - Powered by `cmdk`, surfaces navigation, saved searches, quick actions.

## Visual Language
- Typeface: `Inter` for UI, `DM Serif Display` optional for landing hero headline.
- Color tokens (Tailwind config):
  - `brand-500 #2563eb`, `brand-600 #1d4ed8`, `brand-100 #dbeafe`.
  - Supporting neutrals `neutral-900/700/500/200`.
  - Status: success `#059669`, warning `#f59e0b`, danger `#dc2626`.
- Spacing scale: 4px base → Tailwind default scale.
- Elevation: card uses `shadow-md` base, overlay uses `shadow-xl` + blur background.

## State Management
- Server components for all data-fetching pages.
- Client components only for interactive controls (`FilterPanel`, `AlertPreferenceForm`).
- Data fetching via Server Actions hitting Supabase RPC.
- Use `SWR` for client revalidation after mutate operations (e.g., bookmark toggle).

## Data Contracts
- `/api/opportunities` (GET): accepts filters, returns paginated DTO with summary fields.
- `/api/opportunities/[id]` (GET): returns full detail + `related` array.
- `/api/opportunities/[id]/summary` (POST): returns RAG-based answer (Edge function).
- `/api/alerts` (POST/PUT/DELETE): manage alert preferences.

## Layout & Responsive Notes
- Breakpoints: mobile `<640px`, tablet `640-1024`, desktop `>1024`.
- Mobile dashboard collapses feed into stacked sections; filter drawer becomes bottom sheet.
- Use CSS Grid for dashboard insights area (`grid-cols-12`).

## Accessibility Checklist
- Color contrast AA compliance for text/buttons.
- Keyboard nav: trap focus inside modals, provide skip links.
- Live region for alert success/failure to accommodate screen readers.

## Design Deliverables
1. Figma page `01 - Design System`: color styles, text styles, auto-layout button components.
2. Page `02 - Wireframes`: low-fi wireframes for each route at desktop + mobile.
3. Page `03 - High Fidelity`: polished marketing hero, dashboard, opportunity detail.
4. Prototype connections for main onboarding flow (landing → signup → dashboard → alert).

## Implementation Checklist
- Configure Tailwind + custom theme tokens (`tailwind.config.ts`).
- Scaffold `app` routes with loading/skeleton states.
- Integrate NextAuth with Supabase provider.
- Build `OpportunityCard` and shared layout first, then hook up data fetchers.
- Add analytics instrumentation (PostHog) inside `_app` event tracker wrapper.
