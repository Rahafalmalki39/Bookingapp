# BookIt System Architecture Diagram

## Overall System Architecture
```mermaid
graph TB
    subgraph "Client Layer"
        User[👤 User Browser]
        Mobile[📱 Mobile/Desktop App]
    end
    
    subgraph "Frontend - App Engine"
        Flask[Flask Web Application<br/>Python 3.12]
        Templates[Jinja2 Templates<br/>HTML/CSS/JS]
        StaticFiles[Static Assets<br/>Images, CSS]
    end
    
    subgraph "Backend Services"
        Auth[Authentication Service<br/>bcrypt + Sessions]
        API[REST API Endpoints<br/>/api/*]
        Chat[AI Chatbot<br/>Rule-based]
    end
    
    subgraph "Data Layer - NoSQL"
        Firestore[(Google Cloud Firestore<br/>NoSQL Database)]
        FirestoreCollections[Collections:<br/>- users<br/>- events]
    end
    
    subgraph "Data Layer - SQL"
        CloudSQL[(Cloud SQL PostgreSQL<br/>Relational Database)]
        SQLTables[Tables:<br/>- bookings<br/>- transactions]
    end
    
    subgraph "Serverless Functions"
        CF1[Cloud Function:<br/>Booking Confirmation<br/>SendGrid Email]
        CF2[Cloud Function:<br/>Event Analytics<br/>Metrics Calculation]
    end
    
    subgraph "External APIs"
        SendGrid[SendGrid API<br/>Email Service]
        CloudAPIs[Google Cloud APIs<br/>Firestore, Cloud SQL]
    end
    
    User --> Flask
    Mobile --> API
    Flask --> Templates
    Flask --> Auth
    Flask --> API
    Flask --> Chat
    
    Auth --> Firestore
    API --> Firestore
    API --> CloudSQL
    Flask --> CloudSQL
    
    Firestore --> FirestoreCollections
    CloudSQL --> SQLTables
    
    Flask -.Async Call.-> CF1
    API -.On Demand.-> CF2
    
    CF1 --> SendGrid
    CF2 --> CloudSQL
    
    Flask --> CloudAPIs
    API --> CloudAPIs
    
    style Flask fill:#667eea,color:#fff
    style Firestore fill:#f90,color:#fff
    style CloudSQL fill:#4285f4,color:#fff
    style CF1 fill:#0f9d58,color:#fff
    style CF2 fill:#0f9d58,color:#fff
    style SendGrid fill:#1a82e2,color:#fff
```

## Data Flow Diagram
```mermaid
sequenceDiagram
    participant U as User
    participant F as Flask App
    participant FS as Firestore
    participant SQL as Cloud SQL
    participant CF as Cloud Function
    participant SG as SendGrid
    
    U->>F: 1. Browse Events
    F->>FS: Query events collection
    FS-->>F: Return events list
    F-->>U: Display events with images
    
    U->>F: 2. Book Event (POST)
    F->>SQL: Begin Transaction
    F->>SQL: Insert booking record
    F->>SQL: Insert transaction record
    SQL-->>F: Return booking_id
    F->>FS: Update available_seats
    FS-->>F: Confirm update
    
    F->>CF: 3. Trigger confirmation (async)
    CF->>SG: Send email via SendGrid
    SG-->>CF: Email sent
    CF-->>F: Confirmation success
    
    F-->>U: Redirect to My Bookings
    U->>F: 4. View Bookings
    F->>SQL: SELECT bookings WHERE user_id
    SQL-->>F: Return booking records
    F-->>U: Display booking history
```

## Security Architecture
```mermaid
graph LR
    subgraph "Security Layers"
        Input[Input Validation<br/>Sanitization]
        Auth[Authentication<br/>bcrypt Hashing]
        Session[Session Management<br/>Secure Cookies]
        RateLimit[Rate Limiting<br/>20 req/min]
        Headers[Security Headers<br/>XSS, CSRF Protection]
        HTTPS[HTTPS Enforcement<br/>App Engine SSL]
    end
    
    User[User Request] --> Input
    Input --> RateLimit
    RateLimit --> Auth
    Auth --> Session
    Session --> Headers
    Headers --> HTTPS
    HTTPS --> Application[Protected Application]
    
    style Input fill:#f44336,color:#fff
    style Auth fill:#e91e63,color:#fff
    style Session fill:#9c27b0,color:#fff
    style RateLimit fill:#673ab7,color:#fff
    style Headers fill:#3f51b5,color:#fff
    style HTTPS fill:#2196f3,color:#fff
```

## Technology Stack Overview
```mermaid
mindmap
  root((BookIt<br/>Platform))
    Frontend
      Flask 3.0.0
      Jinja2 Templates
      Tailwind-like CSS
      Vanilla JavaScript
    Backend
      Python 3.12
      Flask Framework
      RESTful APIs
      Cloud Functions
    Databases
      Firestore NoSQL
        Users
        Events
      Cloud SQL PostgreSQL
        Bookings
        Transactions
    Security
      bcrypt Hashing
      Session Auth
      Input Validation
      Rate Limiting
      Security Headers
    Cloud Services
      App Engine
      Cloud Functions
      Cloud SQL Connector
      SendGrid API
    DevOps
      Git Version Control
      GitHub Repository
      pytest Unit Tests
      Cloud Deployment
```

## Testing Results Summary
```mermaid
pie title Unit Test Results
    "Passed Tests" : 10
    "Failed Tests" : 0
```

## Deployment Architecture
```mermaid
graph TB
    subgraph "Development"
        Dev[Local Development<br/>Cloud Shell]
        Git[Git Repository<br/>GitHub]
    end
    
    subgraph "CI/CD"
        Build[gcloud Build]
        Test[Unit Tests<br/>10/10 Passed]
    end
    
    subgraph "Production - Google Cloud"
        AppEngine[App Engine<br/>Python 3.12 Runtime]
        
        subgraph "Databases"
            FS[Firestore<br/>europe-west2]
            SQL[Cloud SQL<br/>PostgreSQL 14]
        end
        
        subgraph "Serverless"
            CF[Cloud Functions<br/>Gen2]
        end
    end
    
    subgraph "Monitoring"
        Logs[Cloud Logging]
        Metrics[Performance Metrics]
    end
    
    Dev --> Git
    Git --> Build
    Build --> Test
    Test --> AppEngine
    
    AppEngine --> FS
    AppEngine --> SQL
    AppEngine --> CF
    
    AppEngine --> Logs
    AppEngine --> Metrics
    
    style AppEngine fill:#4285f4,color:#fff
    style FS fill:#f90,color:#fff
    style SQL fill:#4285f4,color:#fff
    style CF fill:#0f9d58,color:#fff
```