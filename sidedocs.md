graph TB
    subgraph "Design System Foundation"
        DS[Design System Core]
        DS --> Tokens[Design Tokens]
        DS --> Components[Component Library]
        DS --> Patterns[Design Patterns]
        
        Tokens --> Colors[Color Palette<br/>Primary: #1e40af<br/>Secondary: #3730a3<br/>Accent: #6366f1<br/>Trust: #10b981]
        Tokens --> Typography[Typography Scale<br/>Display/Headers/Body<br/>Inter Font Family]
        Tokens --> Spacing[Spacing System<br/>4px base unit<br/>Consistent rhythm]
        Tokens --> Animation[Animation Tokens<br/>Timing/Easing<br/>Micro-interactions]
    end
    
    subgraph "Component Libraries Integration"
        CL[Component Stack]
        CL --> Shadcn[shadcn/ui<br/>Base Components]
        CL --> Aceternity[Aceternity UI<br/>Animation Layer]
        CL --> Custom[Custom Components<br/>Compliance-specific]
        
        Shadcn --> BaseUI[Button/Card/Dialog<br/>Form/Table/Tabs<br/>Alert/Badge/Toast]
        Aceternity --> AnimUI[Shimmer Effects<br/>Float Animations<br/>Glass Morphism<br/>Progress Indicators]
        Custom --> CompUI[Compliance Score<br/>Policy Cards<br/>Audit Tracker<br/>Risk Matrix]
    end
    
    subgraph "Page Architecture"
        Pages[Page Structure]
        Pages --> Landing[Landing Page<br/>Hero + Features<br/>Trust Signals]
        Pages --> Dashboard[Dashboard<br/>Analytics View<br/>Task Management]
        Pages --> Compliance[Compliance Hub<br/>Policy Manager<br/>Gap Analysis]
        Pages --> Reports[Reporting<br/>Executive View<br/>Audit Trails]
    end
    
    subgraph "Design Principles"
        Principles[Core Principles]
        Principles --> Analytical[For Analytical Users<br/>Data-rich interfaces<br/>Customizable views<br/>Export capabilities]
        Principles --> Cautious[For Cautious Users<br/>Step-by-step guidance<br/>Trust indicators<br/>Security badges]
        Principles --> Principled[For Principled Users<br/>Transparent workflows<br/>Audit trails<br/>Compliance focus]
    end
    
    subgraph "Technical Implementation"
        Tech[Tech Stack]
        Tech --> NextJS[Next.js 14<br/>App Router<br/>Server Components]
        Tech --> React[React 18<br/>TypeScript<br/>Hooks/Context]
        Tech --> Styling[Tailwind CSS<br/>CSS Variables<br/>Dark Mode]
        Tech --> Performance[Performance<br/>Code Splitting<br/>Lazy Loading<br/>Core Web Vitals]
    end
    
    DS --> CL
    CL --> Pages
    Principles --> Pages
    Pages --> Tech
    
    classDef designSystem fill:#e0e7ff,stroke:#6366f1,stroke-width:2px
    classDef component fill:#dcfce7,stroke:#10b981,stroke-width:2px
    classDef page fill:#fef3c7,stroke:#f59e0b,stroke-width:2px
    classDef principle fill:#fee2e2,stroke:#ef4444,stroke-width:2px
    classDef tech fill:#f3f4f6,stroke:#6b7280,stroke-width:2px
    
    class DS,Tokens,Components,Patterns designSystem
    class CL,Shadcn,Aceternity,Custom component
    class Pages,Landing,Dashboard,Compliance,Reports page
    class Principles,Analytical,Cautious,Principled principle
    class Tech,NextJS,React,Styling,Performance tech


    