# NovaCRM Frontend

A modern, high-fidelity CRM frontend built with React, Vite, and Tailwind CSS.

## 🌟 Vision

NovaCRM is a next-generation CRM designed for speed, clarity, and ease of use. It features a sleek, premium design system powered by Radix UI and Shadcn UI, with a focus on high-fidelity user interactions and real-time data flow.

---

## 🚀 Tech Stack

- **Framework**: React 18 (Vite)
- **Language**: TypeScript
- **Styling**: Tailwind CSS, Radix UI, Shadcn UI
- **Data Fetching**: TanStack Query (v5)
- **State Management**: React Context API
- **Routing**: React Router DOM (v6)
- **Forms**: React Hook Form, Zod (validation)
- **Icons**: Lucide React
- **Testing**: Vitest, Playwright, Testing Library

---

## 🏗️ Folder Structure

```text
src/
├── api/                # API client and service functions
├── components/         # Reusable UI components
│   ├── ui/             # Shadcn/Radix primitive components
│   ├── auth/           # Authentication-specific components (Protected Routes)
│   └── dashboard/      # Dashboard and analytics components
├── contexts/           # Global application state (AuthContext)
├── hooks/              # Custom React hooks (useAuth, useLocalStorage)
├── lib/                # Utility libraries (utils.ts for tailwind-merge)
├── pages/              # Main application pages and route handlers
│   ├── DashboardPage.tsx
│   ├── ContactsPage.tsx
│   ├── LeadsPage.tsx
│   ├── DealsPage.tsx
│   ├── TasksPage.tsx
│   ├── LoginPage.tsx
│   └── RegisterPage.tsx
├── App.tsx             # Application entry point and routing config
└── main.tsx            # DOM initialization
```

---

## 🛠️ Getting Started

### Prerequisites

- Node.js 18+
- [Bun](https://bun.sh/) (Recommended) or NPM/Yarn

### Setup Instructions

1. **Install Dependencies**:
   ```bash
   bun install  # or npm install
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```bash
   # Required variables
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

3. **Start the Development Server**:
   ```bash
   bun run dev  # or npm run dev
   ```

The application will be available at `http://localhost:5173`.

---

## 📡 API Integration

NovaCRM uses **TanStack Query** for efficient data fetching, caching, and state synchronization.
- **Service Layer**: Found in `src/api/`, these are typed functions that interact with the backend.
- **Hooks**: Custom hooks in `src/hooks/` wrap these API calls for easy use in components.

---

## 🔐 Authentication

Authentication is handled via **JWT** and managed through `AuthContext`.
- **Protected Routes**: Secure pages are wrapped with the `<ProtectedRoute />` component.
- **Token Persistence**: Tokens are securely stored in `localStorage` for session continuity.

---

## 🧪 Testing

Run unit and integration tests with Vitest:
```bash
bun run test
```

Run end-to-end tests with Playwright:
```bash
npx playwright test
```

---

## 🎨 Design System

NovaCRM utilizes a sophisticated design system:
- **Shadcn UI**: For foundational components like Buttons, Inputs, Dialogs, etc.
- **Tailwind CSS**: For consistent, utility-first styling.
- **Vibrant Color Palette**: Modern gradients and dark-mode compatibility.
- **Micro-animations**: Enhanced UX with smooth transitions and hover effects.
