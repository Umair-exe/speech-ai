# AI Detector - Frontend

Modern Next.js application for AI-generated media detection.

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Zustand** - State management
- **Axios** - HTTP client
- **React Dropzone** - File upload

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── layout.tsx      # Root layout
│   │   ├── page.tsx        # Home page
│   │   ├── history/        # History page
│   │   └── pricing/        # Pricing page
│   ├── components/          # React components
│   │   ├── FileUpload.tsx  # File upload component
│   │   ├── ResultCard.tsx  # Result display
│   │   ├── Header.tsx      # Navigation header
│   │   └── LoadingSpinner.tsx
│   ├── lib/                 # Utilities
│   │   ├── api.ts          # API client
│   │   ├── utils.ts        # Helper functions
│   │   └── store.ts        # Zustand store
│   └── types/               # TypeScript types
│       └── index.ts
├── public/                  # Static assets
├── package.json
└── tsconfig.json
```

## Setup

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Start development server
npm run dev
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Check TypeScript types

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAX_FILE_SIZE=104857600
```

## Key Components

### FileUpload
Drag-and-drop file upload with validation

### ResultCard
Displays detection results with confidence scores and artifacts

### Header
Navigation and branding

## Styling

Uses Tailwind CSS with custom configuration:
- Primary color palette
- Custom animations
- Responsive breakpoints

## State Management

Zustand store manages:
- User state
- Detection results
- Loading states
- Errors

## API Integration

The `api.ts` file provides:
- `uploadMedia()` - Upload single file
- `batchUpload()` - Upload multiple files
- `getAnalysisHistory()` - Fetch history
- `getAnalysisById()` - Get single analysis

## Building for Production

```bash
npm run build
npm start
```

## Docker

```bash
docker build -t ai-detector-frontend .
docker run -p 3000:3000 ai-detector-frontend
```
