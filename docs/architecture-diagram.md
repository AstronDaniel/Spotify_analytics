# System Architecture and Data Flow

## High-Level Architecture

The following diagram illustrates the overall system architecture, showing how different components interact:

```mermaid
graph TD
    subgraph Client Layer
        V[Visitors] --> |HTTP| FE[Frontend Application]
        U[Authenticated Users] --> |HTTP| FE
        FE --> |API Requests| BE[Backend Server]
    end

    subgraph Backend Layer
        BE --> |OAuth| Spotify[Spotify API]
        BE --> |Query| DB[(PostgreSQL)]
        BE --> |Cache| Redis[Redis Cache]
        
        subgraph Services
            AA[Analytics Engine]
            VM[Visualization Module]
            DP[Data Processor]
        end
        
        BE --> Services
    end

    subgraph Data Storage
        DB --> UT[User Tables]
        DB --> AT[Analytics Tables]
        DB --> PT[Public Tables]
        Redis --> PC[Public Cache]
        Redis --> UC[User Cache]
    end
```

**Diagram Explanation:**
- **Client Layer**: Represents how both visitors and authenticated users access our application through the frontend interface
- **Backend Layer**: Shows the core server components and their connections to external services
- **Data Storage**: Illustrates our data persistence strategy using both PostgreSQL and Redis
- **Services**: Displays the main processing modules that handle different aspects of data analysis

## Data Flow for Visitors

This diagram shows how visitors interact with our system and how we handle public data requests:

```mermaid
sequenceDiagram
    participant V as Visitor
    participant FE as Frontend
    participant BE as Backend
    participant C as Cache
    participant DB as Database
    participant S as Spotify API

    V->>FE: Access Public Dashboard
    FE->>BE: Request Public Analytics
    BE->>C: Check Cache
    alt Cache Hit
        C->>BE: Return Cached Data
    else Cache Miss
        BE->>DB: Query Public Trends
        alt Needs Fresh Data
            BE->>S: Fetch New Trends
            S->>BE: Return API Data
            BE->>DB: Update Public Trends
        end
        DB->>BE: Return Trends Data
        BE->>C: Update Cache
    end
    BE->>FE: Send Analytics Data
    FE->>V: Display Visualizations
```

**Diagram Explanation:**
- **Initial Request**: Visitor accesses the public dashboard
- **Cache Check**: System first checks if requested data is in cache
- **Data Retrieval**: If cache misses, system fetches from database or Spotify API
- **Data Flow**: Shows how data moves from source to visitor's screen
- **Optimization**: Demonstrates caching strategy for better performance

## Data Flow for Authenticated Users

This diagram illustrates the authentication process and data access for registered users:

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant BE as Backend
    participant S as Spotify API
    participant DB as Database

    U->>FE: Login with Spotify
    FE->>BE: Auth Request
    BE->>S: OAuth Flow
    S->>BE: Access Token
    BE->>DB: Create/Update User
    BE->>FE: Session Token
    
    U->>FE: Request Analytics
    FE->>BE: API Request + Token
    BE->>S: Fetch User Data
    S->>BE: User Music Data
    BE->>BE: Process Analytics
    BE->>DB: Store Results
    BE->>FE: Send Analysis
    FE->>U: Display Dashboard
```

**Diagram Explanation:**
- **Authentication**: Shows the OAuth flow with Spotify
- **Session Management**: Illustrates how user sessions are handled
- **Data Access**: Demonstrates the process of fetching and analyzing user data
- **Security**: Highlights token-based authentication and secure data flow
- **Analytics Process**: Shows how user data is processed and stored

## Component Interaction

Detailed breakdown of how different system components work together:

```mermaid
graph TD
    %% User Interface Layer
    subgraph UI[User Interface Layer]
        PD[Public Dashboard]
        UD[User Dashboard]
        VP[Visualization Panel]
        EP[Export Panel]
        AP[Analytics Panel]
        TP[Trends Panel]
    end

    %% Core Services Layer
    subgraph CS[Core Services Layer]
        AE[Analytics Engine]
        VM[Visualization Module]
        CM[Cache Manager]
        AM[Authentication Module]
        DP[Data Processor]
    end

    %% Data Analysis Components
    subgraph DA[Data Analysis]
        TA[Trend Analyzer]
        PA[Playlist Analyzer]
        GA[Genre Analyzer]
        AA[Artist Analyzer]
    end

    %% External Services Layer
    subgraph ES[External Services Layer]
        SA[Spotify API]
        SS[Storage Service]
        RC[Redis Cache]
    end

    %% Security Layer
    subgraph SL[Security Layer]
        RL[Rate Limiter]
        Auth[Authentication]
        Enc[Encryption]
    end

    %% UI Connections
    PD --> VP
    UD --> VP
    VP --> EP
    UD --> AP
    PD --> TP

    %% Core Service Connections
    AE --> VM
    VM --> CM
    AM --> AE
    DP --> AE

    %% Data Analysis Connections
    AE --> TA
    AE --> PA
    AE --> GA
    AE --> AA

    %% External Service Connections
    AM --> SA
    CM --> RC
    DP --> SS

    %% Security Connections
    RL --> SA
    Auth --> AM
    Enc --> SS
```

**Component Details:**

1. **User Interface Layer**
   - **Public Dashboard**: Entry point for visitors, showing general trends and public analytics
   - **User Dashboard**: Personalized interface for authenticated users
   - **Visualization Panel**: Renders charts, graphs, and interactive visualizations
   - **Export Panel**: Handles data export and sharing functionality
   - **Analytics Panel**: Shows detailed music analysis
   - **Trends Panel**: Displays current music trends and patterns

2. **Core Services Layer**
   - **Analytics Engine**: Core processing unit for music data analysis
   - **Visualization Module**: Transforms data into visual representations
   - **Cache Manager**: Handles data caching for improved performance
   - **Authentication Module**: Manages user authentication and sessions
   - **Data Processor**: Processes raw data from various sources

3. **Data Analysis Components**
   - **Trend Analyzer**: Processes and identifies music trends
   - **Playlist Analyzer**: Analyzes playlist composition and patterns
   - **Genre Analyzer**: Processes genre-related data and statistics
   - **Artist Analyzer**: Analyzes artist popularity and metrics

4. **External Services Layer**
   - **Spotify API**: External music data source
   - **Storage Service**: Handles persistent data storage
   - **Redis Cache**: In-memory data caching

5. **Security Layer**
   - **Rate Limiter**: Controls API request frequency
   - **Authentication**: Handles user authentication
   - **Encryption**: Manages data encryption/decryption

**Inter-Component Communication:**
- UI components communicate with core services through RESTful APIs
- Core services interact with external services using appropriate protocols
- Data flows through the security layer for all external communications
- Cache manager optimizes data access across all components
- Analytics engine coordinates with all analysis components for comprehensive insights

This architecture ensures:
- Scalability through modular design
- Security through layered approach
- Performance through effective caching
- Reliability through service isolation
- Maintainability through clear separation of concerns