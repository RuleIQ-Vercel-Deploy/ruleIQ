# ruleIQ Frontend

A modern Next.js 15 application for compliance management with AI-powered automation.

## 🚀 Features

- **Next.js 15** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Authentication** with JWT tokens and Zustand state management
- **shadcn/ui** components for consistent UI
- **React Query** for server state management
- **Responsive Design** with mobile-first approach

## 📋 Prerequisites

- **Node.js** (version 18.0 or higher)
- **npm** (version 9.0 or higher)
- **Backend API** running on port 8000

## 🚀 Getting Started

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Environment Configuration**
   
   The `.env.local` file is already configured for local development:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_APP_NAME=NexCompli
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   
   Navigate to [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
app/
├── api/                    # API integration files
│   └── auth.ts            # Authentication API calls
├── dashboard/             # Dashboard page
│   └── page.tsx
├── lib/                   # Utilities and configurations
│   ├── api-client.ts      # Axios client configuration
│   ├── utils.ts           # Utility functions
│   └── validators.ts      # Zod schemas
├── login/                 # Login page
│   └── page.tsx
├── store/                 # State management
│   └── auth-store.ts      # Zustand auth store
├── types/                 # TypeScript type definitions
│   └── api.ts             # API response types
├── globals.css            # Global styles
├── layout.tsx             # Root layout
├── page.tsx               # Home page
└── providers.tsx          # React Query and Theme providers

components/                # Reusable UI components
├── ui/                    # shadcn/ui components
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   └── ...
└── ...

hooks/                     # Custom React hooks
└── use-toast.ts          # Toast notification hook

public/                    # Static assets
├── placeholder-logo.png
└── ...
```

## 📜 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run type-check` | Run TypeScript type checking |

## 🔧 Configuration

### API Integration

The frontend connects to the backend API running on `http://localhost:8000`. Key endpoints:

- **Authentication**: `/api/auth/login`, `/api/auth/register`
- **User Profile**: `/api/users/profile`
- **Business Profiles**: `/api/business-profiles`
- **Assessments**: `/api/assessments`
- **Evidence**: `/api/evidence`

### Authentication Flow

1. User logs in via `/login` page
2. Credentials sent to `/api/auth/login`
3. JWT tokens stored in localStorage
4. Zustand store manages auth state
5. API client automatically adds Bearer token to requests
6. Protected routes redirect to login if not authenticated

### State Management

- **Zustand** for client state (authentication, user preferences)
- **React Query** for server state (API data, caching, mutations)
- **LocalStorage** for persistent auth tokens

## 🎨 UI Components

The application uses shadcn/ui components with Tailwind CSS:

```tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Dashboard</CardTitle>
  </CardHeader>
  <CardContent>
    <Button>Get Started</Button>
  </CardContent>
</Card>
```

## 🚀 Deployment

### Build

```bash
npm run build
```

### Production Server

```bash
npm run start
```

### Environment Variables for Production

```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_APP_NAME=NexCompli
NODE_ENV=production
```

## 🔍 Key Pages

- **Home (`/`)**: Landing page with feature overview
- **Login (`/login`)**: Authentication page
- **Dashboard (`/dashboard`)**: Main compliance dashboard
- **Protected Routes**: Automatically redirect to login if not authenticated

## 🛠️ Development

### Adding New Pages

1. Create page component in `app/[route]/page.tsx`
2. Add authentication if needed
3. Update navigation/routing as required

### Adding API Endpoints

1. Add types to `app/types/api.ts`
2. Create API functions in `app/api/[feature].ts`
3. Use React Query hooks for data fetching

### Adding UI Components

1. Install shadcn/ui component: `npx shadcn-ui@latest add [component]`
2. Use existing components from `components/ui/`
3. Follow Tailwind CSS conventions

## 🔒 Security

- JWT tokens stored in localStorage (consider httpOnly cookies for production)
- API requests include CSRF protection headers
- Environment variables for sensitive configuration
- Automatic token cleanup on logout

## 🐛 Troubleshooting

### Common Issues

**Build errors**
- Run `npm run type-check` to identify TypeScript issues
- Ensure all imports use correct paths with `@/` alias

**API connection issues**
- Verify backend is running on port 8000
- Check CORS configuration in backend
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

**Authentication issues**
- Clear localStorage and try again
- Check network tab for 401 responses
- Verify JWT token format in API client

## 📝 License

This project is part of the NexCompli compliance management platform.

---

**Ready to manage compliance with AI! 🎉**