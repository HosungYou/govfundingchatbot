# UI Layout Specification

## Document Purpose
This specification defines pixel-perfect layouts, component hierarchy, and interaction patterns for the GovFunding Chatbot web application. Designed to guide frontend implementation and Figma mockup creation.

---

## Design System Foundation

### Grid System
- **Container Width:** 1440px max-width (desktop)
- **Breakpoints:**
  - Mobile: 320px - 639px
  - Tablet: 640px - 1023px
  - Desktop: 1024px - 1439px
  - Wide: 1440px+
- **Column Grid:** 12-column layout (Tailwind `grid-cols-12`)
- **Gutter:** 24px between columns (Tailwind `gap-6`)

### Spacing Scale (Tailwind)
```css
4px   → space-1
8px   → space-2
12px  → space-3
16px  → space-4
24px  → space-6
32px  → space-8
48px  → space-12
64px  → space-16
```

### Color Palette
```typescript
// colors.ts
export const colors = {
  // Primary - Blue (Trust, Professional)
  primary: {
    50: '#eff6ff',
    100: '#dbeafe',
    500: '#3b82f6',  // Main brand color
    600: '#2563eb',  // Hover states
    700: '#1d4ed8',  // Active states
  },

  // Neutral - Gray (Content, Backgrounds)
  neutral: {
    50: '#f9fafb',   // Page background
    100: '#f3f4f6',  // Card background
    200: '#e5e7eb',  // Borders
    500: '#6b7280',  // Secondary text
    700: '#374151',  // Body text
    900: '#111827',  // Headings
  },

  // Semantic Colors
  success: '#10b981',  // Green - Eligibility met
  warning: '#f59e0b',  // Orange - Closing soon
  danger: '#ef4444',   // Red - Closed/Ineligible
  info: '#06b6d4',     // Cyan - New opportunities
}
```

### Typography
```css
/* Font Stack */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

/* Hierarchy */
H1: 48px / 56px line-height, font-weight: 700 (Homepage hero)
H2: 36px / 44px, font-weight: 700 (Section headers)
H3: 24px / 32px, font-weight: 600 (Card titles)
H4: 20px / 28px, font-weight: 600 (Subsections)
Body: 16px / 24px, font-weight: 400
Small: 14px / 20px, font-weight: 400
Caption: 12px / 16px, font-weight: 500
```

---

## Page Layouts

### 1. Landing Page (Unauthenticated)

**Layout Structure:**
```
┌─────────────────────────────────────────┐
│  Header (sticky)                        │ 64px height
├─────────────────────────────────────────┤
│                                         │
│         Hero Section                    │ 600px min-height
│                                         │
├─────────────────────────────────────────┤
│                                         │
│      Live Metrics Strip                 │ 120px height
│                                         │
├─────────────────────────────────────────┤
│                                         │
│        Features Grid                    │ Auto height
│                                         │
├─────────────────────────────────────────┤
│                                         │
│      Testimonials Carousel              │ 400px height
│                                         │
├─────────────────────────────────────────┤
│           Footer                        │ 240px height
└─────────────────────────────────────────┘
```

#### **Header Component**
```html
<header class="sticky top-0 z-50 bg-white border-b border-neutral-200 h-16">
  <div class="max-w-7xl mx-auto px-6 flex items-center justify-between h-full">
    <!-- Logo (Left) -->
    <div class="flex items-center gap-3">
      <img src="/logo.svg" alt="GovFunding" class="h-8 w-8" />
      <span class="text-xl font-bold text-neutral-900">GovFunding</span>
    </div>

    <!-- Navigation (Center) -->
    <nav class="hidden md:flex gap-8">
      <a href="#features" class="text-neutral-700 hover:text-primary-600">Features</a>
      <a href="#how-it-works" class="text-neutral-700 hover:text-primary-600">How It Works</a>
      <a href="#pricing" class="text-neutral-700 hover:text-primary-600">Pricing</a>
    </nav>

    <!-- CTAs (Right) -->
    <div class="flex items-center gap-4">
      <button class="text-neutral-700 hover:text-primary-600">Sign In</button>
      <button class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600">
        Get Started
      </button>
    </div>
  </div>
</header>
```

**Dimensions:**
- Height: 64px
- Logo: 32px × 32px
- Button height: 40px
- Horizontal padding: 24px (container)

---

#### **Hero Section**
```html
<section class="bg-gradient-to-br from-primary-50 to-neutral-50 py-24">
  <div class="max-w-7xl mx-auto px-6 grid grid-cols-12 gap-12 items-center">
    <!-- Left Column (7 cols) -->
    <div class="col-span-12 lg:col-span-7">
      <h1 class="text-5xl lg:text-6xl font-bold text-neutral-900 leading-tight">
        Find Federal Funding
        <span class="text-primary-500">10× Faster</span>
      </h1>

      <p class="mt-6 text-xl text-neutral-600 leading-relaxed">
        AI-powered search across NSF awards and federal grants.
        Get alerts for opportunities matching your research.
      </p>

      <!-- CTA Buttons -->
      <div class="mt-8 flex gap-4">
        <button class="px-8 py-4 bg-primary-500 text-white rounded-lg hover:bg-primary-600 text-lg font-semibold">
          Try Dashboard →
        </button>
        <button class="px-8 py-4 border-2 border-primary-500 text-primary-600 rounded-lg hover:bg-primary-50 text-lg font-semibold">
          Watch Demo
        </button>
      </div>

      <!-- Social Proof -->
      <div class="mt-8 flex items-center gap-2 text-sm text-neutral-500">
        <div class="flex -space-x-2">
          <img src="/avatar1.jpg" class="w-8 h-8 rounded-full border-2 border-white" />
          <img src="/avatar2.jpg" class="w-8 h-8 rounded-full border-2 border-white" />
          <img src="/avatar3.jpg" class="w-8 h-8 rounded-full border-2 border-white" />
        </div>
        <span>Trusted by 500+ researchers</span>
      </div>
    </div>

    <!-- Right Column (5 cols) - Hero Image/Illustration -->
    <div class="col-span-12 lg:col-span-5">
      <img src="/hero-dashboard-preview.png" alt="Dashboard Preview"
           class="rounded-xl shadow-2xl border border-neutral-200" />
    </div>
  </div>
</section>
```

**Dimensions:**
- Section padding-y: 96px (desktop), 64px (mobile)
- Heading: 60px font size (desktop), 48px (mobile)
- CTA buttons: 56px height, 32px horizontal padding
- Hero image: 600px width (auto height, maintain aspect ratio)

---

#### **Live Metrics Strip**
```html
<section class="bg-white py-12 border-y border-neutral-200">
  <div class="max-w-7xl mx-auto px-6">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Metric 1 -->
      <div class="text-center">
        <div class="text-4xl font-bold text-primary-500">
          1,247
        </div>
        <div class="mt-2 text-neutral-600">
          Active Opportunities
        </div>
        <div class="mt-1 text-sm text-success">
          ↑ 34 new this week
        </div>
      </div>

      <!-- Metric 2 -->
      <div class="text-center">
        <div class="text-4xl font-bold text-primary-500">
          $12.4B
        </div>
        <div class="mt-2 text-neutral-600">
          Available Funding
        </div>
      </div>

      <!-- Metric 3 -->
      <div class="text-center">
        <div class="text-4xl font-bold text-primary-500">
          <2s
        </div>
        <div class="mt-2 text-neutral-600">
          Average Search Time
        </div>
      </div>
    </div>
  </div>
</section>
```

**Dimensions:**
- Section height: 120px
- Metric number: 48px font size
- Grid gap: 32px

---

### 2. Dashboard Page (Authenticated)

**Layout Structure:**
```
┌──────────┬──────────────────────────────────────┐
│          │  Top Navigation Bar                  │ 64px
│          ├──────────────────────────────────────┤
│  Sidebar │                                      │
│          │         Main Content Area            │
│  240px   │                                      │
│          │                                      │
│          │                                      │
└──────────┴──────────────────────────────────────┘
```

#### **Sidebar Navigation**
```html
<aside class="fixed left-0 top-16 w-60 h-[calc(100vh-64px)] bg-white border-r border-neutral-200">
  <nav class="p-6 space-y-2">
    <!-- Navigation Items -->
    <a href="/dashboard" class="flex items-center gap-3 px-4 py-3 bg-primary-50 text-primary-600 rounded-lg">
      <HomeIcon class="w-5 h-5" />
      <span class="font-medium">Dashboard</span>
    </a>

    <a href="/search" class="flex items-center gap-3 px-4 py-3 text-neutral-700 hover:bg-neutral-50 rounded-lg">
      <SearchIcon class="w-5 h-5" />
      <span>Search</span>
    </a>

    <a href="/saved" class="flex items-center gap-3 px-4 py-3 text-neutral-700 hover:bg-neutral-50 rounded-lg">
      <BookmarkIcon class="w-5 h-5" />
      <span>Saved (12)</span>
      <span class="ml-auto text-xs bg-primary-100 text-primary-600 px-2 py-1 rounded-full">12</span>
    </a>

    <a href="/alerts" class="flex items-center gap-3 px-4 py-3 text-neutral-700 hover:bg-neutral-50 rounded-lg">
      <BellIcon class="w-5 h-5" />
      <span>Alerts</span>
    </a>

    <hr class="my-4 border-neutral-200" />

    <a href="/settings" class="flex items-center gap-3 px-4 py-3 text-neutral-700 hover:bg-neutral-50 rounded-lg">
      <SettingsIcon class="w-5 h-5" />
      <span>Settings</span>
    </a>
  </nav>
</aside>
```

**Dimensions:**
- Width: 240px (fixed)
- Item height: 48px
- Icon size: 20px × 20px
- Padding: 24px (container)

---

#### **Dashboard Main Content**
```html
<main class="ml-60 pt-16 min-h-screen bg-neutral-50">
  <div class="max-w-7xl mx-auto p-8">
    <!-- Page Header -->
    <header class="mb-8">
      <h1 class="text-3xl font-bold text-neutral-900">Dashboard</h1>
      <p class="mt-2 text-neutral-600">Welcome back, Dr. Smith</p>
    </header>

    <!-- Insight Cards Row -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <!-- Card 1: Saved Opportunities -->
      <div class="bg-white p-6 rounded-xl border border-neutral-200 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-neutral-900">Saved</h3>
          <BookmarkIcon class="w-6 h-6 text-primary-500" />
        </div>
        <div class="text-3xl font-bold text-neutral-900">12</div>
        <p class="mt-2 text-sm text-neutral-600">opportunities</p>
      </div>

      <!-- Card 2: Closing Soon -->
      <div class="bg-white p-6 rounded-xl border border-neutral-200 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-neutral-900">Closing Soon</h3>
          <ClockIcon class="w-6 h-6 text-warning" />
        </div>
        <div class="text-3xl font-bold text-neutral-900">3</div>
        <p class="mt-2 text-sm text-warning">within 7 days</p>
      </div>

      <!-- Card 3: New Matches -->
      <div class="bg-white p-6 rounded-xl border border-neutral-200 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-neutral-900">New Matches</h3>
          <SparklesIcon class="w-6 h-6 text-success" />
        </div>
        <div class="text-3xl font-bold text-neutral-900">8</div>
        <p class="mt-2 text-sm text-success">since last login</p>
      </div>
    </div>

    <!-- Opportunities Feed -->
    <section class="bg-white rounded-xl border border-neutral-200 p-6">
      <h2 class="text-xl font-bold text-neutral-900 mb-6">Recent Opportunities</h2>

      <!-- Opportunity Cards (See component spec below) -->
      <div class="space-y-4">
        <!-- Cards rendered here -->
      </div>
    </section>
  </div>
</main>
```

**Dimensions:**
- Main area: Calc(100% - 240px sidebar)
- Content padding: 32px
- Card height: 144px
- Grid gap: 24px

---

### 3. Search Page

**Layout Structure:**
```
┌──────────┬─────────────┬────────────────────────┐
│          │             │                        │
│  Sidebar │  Filter     │   Results Grid         │
│          │  Panel      │                        │
│  240px   │  280px      │   Flexible             │
│          │             │                        │
└──────────┴─────────────┴────────────────────────┘
```

#### **Filter Panel**
```html
<aside class="w-70 bg-white border-r border-neutral-200 p-6 overflow-y-auto">
  <h3 class="text-lg font-bold text-neutral-900 mb-6">Filters</h3>

  <!-- Search Bar -->
  <div class="mb-6">
    <label class="text-sm font-medium text-neutral-700 mb-2 block">Keyword</label>
    <input
      type="text"
      placeholder="Search opportunities..."
      class="w-full px-4 py-2 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-500"
    />
  </div>

  <!-- Agency Filter -->
  <div class="mb-6">
    <label class="text-sm font-medium text-neutral-700 mb-2 block">Agency</label>
    <select class="w-full px-4 py-2 border border-neutral-200 rounded-lg">
      <option>All Agencies</option>
      <option>NSF</option>
      <option>NIH</option>
      <option>DOE</option>
    </select>
  </div>

  <!-- Award Amount Slider -->
  <div class="mb-6">
    <label class="text-sm font-medium text-neutral-700 mb-2 block">
      Award Amount: $50K - $500K
    </label>
    <input type="range" min="0" max="1000000" class="w-full" />
  </div>

  <!-- Close Date Range -->
  <div class="mb-6">
    <label class="text-sm font-medium text-neutral-700 mb-2 block">Close Date</label>
    <div class="grid grid-cols-2 gap-2">
      <input type="date" class="px-3 py-2 border border-neutral-200 rounded-lg text-sm" />
      <input type="date" class="px-3 py-2 border border-neutral-200 rounded-lg text-sm" />
    </div>
  </div>

  <!-- Apply/Reset Buttons -->
  <div class="flex gap-2">
    <button class="flex-1 px-4 py-2 bg-primary-500 text-white rounded-lg">Apply</button>
    <button class="px-4 py-2 border border-neutral-200 text-neutral-700 rounded-lg">Reset</button>
  </div>
</aside>
```

**Dimensions:**
- Width: 280px (fixed)
- Input height: 40px
- Button height: 40px
- Spacing between sections: 24px

---

#### **Results Grid**
```html
<main class="flex-1 p-8">
  <!-- Results Header -->
  <div class="flex items-center justify-between mb-6">
    <div>
      <h2 class="text-2xl font-bold text-neutral-900">Search Results</h2>
      <p class="mt-1 text-neutral-600">1,247 opportunities found</p>
    </div>

    <!-- View Toggle + Sort -->
    <div class="flex items-center gap-4">
      <div class="flex border border-neutral-200 rounded-lg">
        <button class="px-3 py-2 bg-primary-50 text-primary-600 rounded-l-lg">
          <GridIcon class="w-5 h-5" />
        </button>
        <button class="px-3 py-2 text-neutral-700 rounded-r-lg">
          <ListIcon class="w-5 h-5" />
        </button>
      </div>

      <select class="px-4 py-2 border border-neutral-200 rounded-lg">
        <option>Most Relevant</option>
        <option>Closing Soon</option>
        <option>Highest Funding</option>
        <option>Most Recent</option>
      </select>
    </div>
  </div>

  <!-- Opportunity Cards Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- OpportunityCard components rendered here -->
  </div>

  <!-- Pagination -->
  <div class="mt-8 flex justify-center">
    <nav class="flex gap-2">
      <button class="px-4 py-2 border border-neutral-200 rounded-lg">Previous</button>
      <button class="px-4 py-2 bg-primary-500 text-white rounded-lg">1</button>
      <button class="px-4 py-2 border border-neutral-200 rounded-lg">2</button>
      <button class="px-4 py-2 border border-neutral-200 rounded-lg">3</button>
      <button class="px-4 py-2 border border-neutral-200 rounded-lg">Next</button>
    </nav>
  </div>
</main>
```

---

### 4. Opportunity Detail Page

**Layout Structure:**
```
┌─────────────────────────────────────────────────┐
│  Breadcrumb Navigation                          │ 48px
├─────────────────────────┬───────────────────────┤
│                         │                       │
│   Main Content          │   Sidebar Actions     │
│   (8 cols)              │   (4 cols)            │
│                         │                       │
│   - Header              │   - Quick Actions     │
│   - Summary             │   - Key Metadata      │
│   - Eligibility         │   - Timeline          │
│   - Timeline            │                       │
│   - Documents           │                       │
│   - Related Opps        │                       │
│                         │                       │
└─────────────────────────┴───────────────────────┘
```

#### **Opportunity Header**
```html
<header class="bg-white border-b border-neutral-200 p-8">
  <!-- Breadcrumb -->
  <nav class="text-sm text-neutral-600 mb-4">
    <a href="/dashboard" class="hover:text-primary-600">Dashboard</a>
    <span class="mx-2">/</span>
    <a href="/search" class="hover:text-primary-600">Search</a>
    <span class="mx-2">/</span>
    <span class="text-neutral-900">Opportunity Detail</span>
  </nav>

  <div class="grid grid-cols-12 gap-8">
    <!-- Left: Title & Meta (8 cols) -->
    <div class="col-span-12 lg:col-span-8">
      <!-- Tags -->
      <div class="flex gap-2 mb-4">
        <span class="px-3 py-1 bg-primary-50 text-primary-600 rounded-full text-sm font-medium">
          NSF
        </span>
        <span class="px-3 py-1 bg-success/10 text-success rounded-full text-sm font-medium">
          Open
        </span>
        <span class="px-3 py-1 bg-warning/10 text-warning rounded-full text-sm font-medium">
          Closes in 12 days
        </span>
      </div>

      <h1 class="text-4xl font-bold text-neutral-900 leading-tight">
        Advancing Informal STEM Learning (AISL)
      </h1>

      <p class="mt-4 text-lg text-neutral-600">
        NSF-23-612 | Posted March 15, 2025
      </p>
    </div>

    <!-- Right: Quick Stats (4 cols) -->
    <div class="col-span-12 lg:col-span-4 space-y-4">
      <div class="bg-neutral-50 p-4 rounded-lg">
        <div class="text-sm text-neutral-600">Award Range</div>
        <div class="text-2xl font-bold text-neutral-900">$50K - $500K</div>
      </div>

      <div class="bg-neutral-50 p-4 rounded-lg">
        <div class="text-sm text-neutral-600">Close Date</div>
        <div class="text-2xl font-bold text-warning">April 15, 2025</div>
      </div>
    </div>
  </div>
</header>
```

---

#### **Main Content Sections**
```html
<div class="max-w-7xl mx-auto p-8">
  <div class="grid grid-cols-12 gap-8">
    <!-- Main Content (8 cols) -->
    <main class="col-span-12 lg:col-span-8 space-y-8">
      <!-- Summary Section -->
      <section class="bg-white p-6 rounded-xl border border-neutral-200">
        <h2 class="text-2xl font-bold text-neutral-900 mb-4">Summary</h2>
        <p class="text-neutral-700 leading-relaxed">
          The Advancing Informal STEM Learning program seeks to advance new approaches to...
        </p>
      </section>

      <!-- Eligibility Section -->
      <section class="bg-white p-6 rounded-xl border border-neutral-200">
        <h2 class="text-2xl font-bold text-neutral-900 mb-4">Eligibility</h2>
        <ul class="space-y-2">
          <li class="flex items-start gap-2">
            <CheckCircleIcon class="w-5 h-5 text-success mt-1" />
            <span>Institutions of Higher Education</span>
          </li>
          <li class="flex items-start gap-2">
            <CheckCircleIcon class="w-5 h-5 text-success mt-1" />
            <span>Non-profit organizations</span>
          </li>
        </ul>
      </section>

      <!-- RAG Assistant Panel -->
      <section class="bg-gradient-to-br from-primary-50 to-neutral-50 p-6 rounded-xl border border-primary-200">
        <h3 class="text-lg font-bold text-neutral-900 mb-4 flex items-center gap-2">
          <SparklesIcon class="w-5 h-5 text-primary-500" />
          AI Assistant
        </h3>

        <div class="bg-white p-4 rounded-lg mb-4 max-h-64 overflow-y-auto">
          <!-- Chat messages rendered here -->
          <div class="text-sm text-neutral-600">
            Ask me anything about this opportunity...
          </div>
        </div>

        <div class="flex gap-2">
          <input
            type="text"
            placeholder="e.g., What are the review criteria?"
            class="flex-1 px-4 py-2 border border-neutral-200 rounded-lg"
          />
          <button class="px-6 py-2 bg-primary-500 text-white rounded-lg">
            Ask
          </button>
        </div>
      </section>
    </main>

    <!-- Sidebar (4 cols) -->
    <aside class="col-span-12 lg:col-span-4 space-y-6">
      <!-- Action Buttons -->
      <div class="bg-white p-6 rounded-xl border border-neutral-200 space-y-3">
        <button class="w-full px-4 py-3 bg-primary-500 text-white rounded-lg font-semibold">
          Save Opportunity
        </button>
        <button class="w-full px-4 py-3 border-2 border-primary-500 text-primary-600 rounded-lg font-semibold">
          Set Alert
        </button>
        <button class="w-full px-4 py-3 border border-neutral-200 text-neutral-700 rounded-lg">
          Export PDF
        </button>
      </div>

      <!-- Timeline -->
      <div class="bg-white p-6 rounded-xl border border-neutral-200">
        <h3 class="text-lg font-bold text-neutral-900 mb-4">Timeline</h3>
        <div class="space-y-4">
          <div class="flex gap-3">
            <div class="w-2 h-2 bg-success rounded-full mt-2"></div>
            <div>
              <div class="text-sm font-medium text-neutral-900">Posted</div>
              <div class="text-xs text-neutral-600">March 15, 2025</div>
            </div>
          </div>
          <div class="flex gap-3">
            <div class="w-2 h-2 bg-warning rounded-full mt-2"></div>
            <div>
              <div class="text-sm font-medium text-neutral-900">Closes</div>
              <div class="text-xs text-neutral-600">April 15, 2025</div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  </div>
</div>
```

---

## Component Library

### OpportunityCard (Reusable)

**Variants:** Default | Compact | Featured

```html
<!-- Default Variant -->
<article class="bg-white p-6 rounded-xl border border-neutral-200 hover:border-primary-300 hover:shadow-lg transition-all cursor-pointer">
  <!-- Header: Title + Bookmark -->
  <div class="flex items-start justify-between mb-3">
    <h3 class="text-lg font-semibold text-neutral-900 line-clamp-2 flex-1">
      Advancing Informal STEM Learning (AISL)
    </h3>
    <button class="text-neutral-400 hover:text-primary-500">
      <BookmarkIcon class="w-6 h-6" />
    </button>
  </div>

  <!-- Agency + ID -->
  <div class="flex items-center gap-2 text-sm text-neutral-600 mb-4">
    <span class="font-medium">NSF</span>
    <span>•</span>
    <span>NSF-23-612</span>
  </div>

  <!-- Summary -->
  <p class="text-sm text-neutral-700 line-clamp-3 mb-4">
    The Advancing Informal STEM Learning program seeks to advance new approaches...
  </p>

  <!-- Tags -->
  <div class="flex flex-wrap gap-2 mb-4">
    <span class="px-2 py-1 bg-neutral-100 text-neutral-700 rounded text-xs">
      Education
    </span>
    <span class="px-2 py-1 bg-neutral-100 text-neutral-700 rounded text-xs">
      STEM
    </span>
  </div>

  <!-- Footer: Amount + Close Date -->
  <div class="flex items-center justify-between pt-4 border-t border-neutral-200">
    <div class="text-sm">
      <span class="text-neutral-600">Award:</span>
      <span class="font-semibold text-neutral-900">$50K - $500K</span>
    </div>
    <div class="text-sm">
      <span class="text-warning font-medium">Closes in 12 days</span>
    </div>
  </div>
</article>
```

**Dimensions:**
- Height: 280px (auto-expand if needed)
- Padding: 24px
- Border radius: 12px
- Title: 2-line clamp
- Summary: 3-line clamp

---

### FilterPanel Component

**Collapsible Sections (Mobile):**
```html
<div class="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-neutral-200 p-4 z-40">
  <button class="w-full px-4 py-3 bg-primary-500 text-white rounded-lg flex items-center justify-center gap-2">
    <FilterIcon class="w-5 h-5" />
    Show Filters (12)
  </button>
</div>

<!-- Full Panel (slides up on mobile) -->
<div class="fixed inset-0 bg-black/50 z-50 lg:hidden">
  <div class="absolute bottom-0 left-0 right-0 bg-white rounded-t-2xl max-h-[80vh] overflow-y-auto">
    <!-- Filter content here -->
  </div>
</div>
```

---

### CommandPalette (Keyboard Shortcut)

**Trigger:** Cmd+K / Ctrl+K

```html
<div class="fixed inset-0 bg-black/50 flex items-start justify-center pt-32 z-50">
  <div class="bg-white w-full max-w-2xl rounded-xl shadow-2xl">
    <!-- Search Input -->
    <div class="p-4 border-b border-neutral-200">
      <input
        type="text"
        placeholder="Type a command or search..."
        class="w-full text-lg outline-none"
        autofocus
      />
    </div>

    <!-- Results -->
    <div class="max-h-96 overflow-y-auto">
      <!-- Recent Searches -->
      <div class="p-2">
        <div class="px-3 py-2 text-xs font-semibold text-neutral-500 uppercase">
          Recent
        </div>
        <button class="w-full px-3 py-2 flex items-center gap-3 hover:bg-neutral-50 rounded-lg text-left">
          <ClockIcon class="w-5 h-5 text-neutral-400" />
          <span>NSF CAREER awards</span>
        </button>
      </div>

      <!-- Quick Actions -->
      <div class="p-2">
        <div class="px-3 py-2 text-xs font-semibold text-neutral-500 uppercase">
          Actions
        </div>
        <button class="w-full px-3 py-2 flex items-center gap-3 hover:bg-neutral-50 rounded-lg text-left">
          <PlusIcon class="w-5 h-5 text-neutral-400" />
          <span>Create new alert</span>
          <kbd class="ml-auto px-2 py-1 bg-neutral-100 text-xs rounded">⌘N</kbd>
        </button>
      </div>
    </div>
  </div>
</div>
```

---

## Responsive Behavior

### Breakpoint Adjustments

**Mobile (< 640px):**
- Sidebar: Hidden, hamburger menu
- Grid: 1 column
- Font sizes: -10% scale
- Padding: 16px (from 32px)

**Tablet (640px - 1023px):**
- Sidebar: Collapsible drawer
- Grid: 2 columns
- Filter panel: Bottom sheet

**Desktop (>1024px):**
- Full layout as specified
- Sidebar: Fixed visible

---

## Interaction Patterns

### Hover States
```css
.opportunity-card:hover {
  border-color: theme('colors.primary.300');
  box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
  transition: all 200ms ease-in-out;
}
```

### Loading States
```html
<!-- Skeleton Loader for OpportunityCard -->
<div class="bg-white p-6 rounded-xl border border-neutral-200 animate-pulse">
  <div class="h-6 bg-neutral-200 rounded w-3/4 mb-3"></div>
  <div class="h-4 bg-neutral-200 rounded w-1/4 mb-4"></div>
  <div class="h-4 bg-neutral-200 rounded w-full mb-2"></div>
  <div class="h-4 bg-neutral-200 rounded w-full mb-2"></div>
  <div class="h-4 bg-neutral-200 rounded w-2/3"></div>
</div>
```

### Empty States
```html
<div class="flex flex-col items-center justify-center py-16">
  <img src="/empty-state.svg" alt="No results" class="w-64 h-64 mb-6" />
  <h3 class="text-xl font-semibold text-neutral-900 mb-2">No opportunities found</h3>
  <p class="text-neutral-600 mb-6">Try adjusting your filters or search terms</p>
  <button class="px-6 py-3 bg-primary-500 text-white rounded-lg">
    Clear Filters
  </button>
</div>
```

---

## Accessibility Requirements

### WCAG 2.1 AA Compliance

**Color Contrast:**
- Text: 4.5:1 minimum (body text on backgrounds)
- Large text (>18px): 3:1 minimum
- UI elements: 3:1 minimum

**Keyboard Navigation:**
- All interactive elements: `tabindex` and focus states
- Skip links: "Skip to main content"
- Focus indicators: 2px solid ring at `theme('colors.primary.500')`

**Screen Reader Support:**
- Semantic HTML (`<nav>`, `<main>`, `<article>`, `<aside>`)
- ARIA labels for icon-only buttons
- Live regions for dynamic content updates

**Example:**
```html
<button
  aria-label="Save opportunity"
  class="focus:ring-2 focus:ring-primary-500 focus:outline-none"
>
  <BookmarkIcon class="w-5 h-5" />
</button>
```

---

## Animation Guidelines

### Micro-interactions
- **Hover transitions:** 200ms ease-in-out
- **Button clicks:** Scale(0.98) for 100ms
- **Page transitions:** 300ms fade-in
- **Skeleton loaders:** Pulse animation 1.5s infinite

### Page Transitions (Next.js App Router)
```typescript
// app/layout.tsx
import { AnimatePresence, motion } from 'framer-motion'

export default function RootLayout({ children }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

---

## Implementation Checklist

### Phase 1: Core Pages (Week 1-2)
- [ ] Design system tokens configured in `tailwind.config.ts`
- [ ] Reusable components built in `components/ui/`
- [ ] Landing page implemented
- [ ] Dashboard layout + navigation

### Phase 2: Search & Detail (Week 2-3)
- [ ] Search page with filters
- [ ] Opportunity detail page
- [ ] OpportunityCard variations
- [ ] RAG assistant integration

### Phase 3: Polish & Responsive (Week 3-4)
- [ ] Mobile responsive layouts
- [ ] Loading/empty states
- [ ] Accessibility audit
- [ ] Animation polish

---

## Figma Deliverables Checklist

### Required Frames
1. **Design System Page**
   - [ ] Color palette with hex codes
   - [ ] Typography scale
   - [ ] Component variants (buttons, inputs, cards)
   - [ ] Icon library

2. **Landing Page**
   - [ ] Desktop (1440px)
   - [ ] Mobile (375px)

3. **Dashboard**
   - [ ] Desktop layout
   - [ ] Tablet layout
   - [ ] Mobile layout

4. **Search + Filters**
   - [ ] Desktop split view
   - [ ] Mobile with bottom sheet filters

5. **Opportunity Detail**
   - [ ] Desktop
   - [ ] Mobile

### Prototype Connections
- [ ] Landing → Sign Up → Dashboard
- [ ] Dashboard → Search → Detail
- [ ] Detail → RAG Assistant interaction

---

**Document Status:** Draft v1.0
**Last Updated:** 2025-10-10
**Next Review:** After Figma mockups complete
**Owner:** Design + Frontend Team
