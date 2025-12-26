# My3 Frontend

Next.js 15 frontend for My3 - AI-powered personal relationship and gifting concierge.

## Project Structure

```
my3-frontend/
├── app/                    # Next.js App Router
│   ├── dashboard/         # Dashboard page
│   ├── login/             # Login page
│   ├── register/          # Register page
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Landing page
│   └── globals.css        # Global styles
├── components/
│   ├── dashboard/         # Dashboard components
│   │   ├── DashboardLayout.tsx
│   │   ├── NetworkGraph.tsx
│   │   ├── ChatWindow.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── ChatInput.tsx
│   │   ├── GiftInlineCard.tsx
│   │   └── ConfirmationPrompt.tsx
│   └── landing/           # Landing page components
│       ├── Hero.tsx
│       ├── Features.tsx
│       └── Demo.tsx
├── hooks/                  # Custom React hooks
│   ├── useAuth.ts
│   ├── useChat.ts
│   └── useRecipients.ts
├── lib/                    # Utilities
│   ├── api/               # API client
│   └── types.ts           # TypeScript types
└── store/                  # Zustand stores
    └── chatStore.ts
```

## Setup Instructions

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your settings
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

4. **Open browser:**
   - http://localhost:3000

## Features

- **Landing Page**: Hero, features, and demo sections
- **Authentication**: Login and registration pages
- **Dashboard**: Conversation-first interface with network graph background
- **Network Graph**: D3.js visualization of relationships (max 10)
- **Chat Interface**: Real-time chat with My3 AI agent
- **Responsive Design**: Mobile-friendly layout

## Design System

- **Primary**: Warm gradient (#FF6B6B to #FFA07A)
- **Background**: Soft cream (#FFF9F5)
- **Text**: Charcoal (#2D3748)
- **Accent**: Teal (#14B8A6)
- **Font**: Inter

## Tech Stack

- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- TanStack Query
- Zustand
- D3.js
- Framer Motion
- Axios

## Development

- Build: `npm run build`
- Start production: `npm start`
- Lint: `npm run lint`

