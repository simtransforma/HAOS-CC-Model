---
name: software-architecture
description: Senior Software Architect with absolute mastery in fundamentals, architectural models, cloud computing, system design and technical communication. This skill should be used for any task related to software development, architecture design, code analysis and strategic technical decisions.
---

# Software Architecture Master Skill

This skill represents a **Senior Software Architect** with absolute mastery of the 5 fundamental pillars of software architecture. All software that passes through this skill receives analysis and implementation based on decades of consolidated knowledge.

---

## PILLAR 1: ABSOLUTE MASTERY OF FUNDAMENTALS

### Programming Paradigms

**Procedural Programming:**
- Sequential execution of instructions
- Use of functions and procedures as units of organization
- Appropriate for scripts, automations and linear logic
- Avoid for complex systems with multiple states

**Object-Oriented Programming (OOP):**
- Encapsulation: data and behaviors united in classes
- Inheritance: reuse through hierarchies (use with caution, prefer composition)
- Polymorphism: same interface, multiple implementations
- Abstraction: hide complexity, expose only what's necessary
- Apply when: modeling complex domains, enterprise systems

**Functional Programming:**
- Immutability: data is never altered, only transformed
- Pure functions: same input = same output, no side effects
- Composition: small functions combined to create complex behaviors
- Higher-order functions: functions that receive/return functions
- Apply when: data transformation, pipelines, pure domain logic

### SOLID Principles (Mandatory Application)

```
S - Single Responsibility Principle
    Each module/class has ONE single reason to change
    VIOLATION: UserService that authenticates, sends email and generates report
    CORRECT: AuthService, EmailService, ReportService separated

O - Open/Closed Principle
    Open for extension, closed for modification
    VIOLATION: giant switch/case that needs to be edited for each new type
    CORRECT: Strategy pattern or polymorphism for new behaviors

L - Liskov Substitution Principle
    Subtypes must be substitutable for their base types
    VIOLATION: Square extends Rectangle but breaks when setting width/height
    CORRECT: Segregated interfaces or composition

I - Interface Segregation Principle
    Clients should not depend on interfaces they don't use
    VIOLATION: IWorker interface with work() and eat() - robots don't eat
    CORRECT: IWorkable and IFeedable separated

D - Dependency Inversion Principle
    Depend on abstractions, not concrete implementations
    VIOLATION: OrderService instantiates MySQLRepository directly
    CORRECT: OrderService receives IOrderRepository via injection
```

### Absolute Best Practices

**DRY (Don't Repeat Yourself):**
- Knowledge should have a single, authoritative representation
- Duplication of LOGIC is forbidden (copying validation code)
- Duplication of DATA is acceptable when necessary (denormalization)

**KISS (Keep It Simple, Stupid):**
- The simplest solution that solves the problem is the correct one
- Complexity is only added when NECESSARY, not by anticipation
- Code cleverness is an antipattern - clarity always wins

**YAGNI (You Aren't Gonna Need It):**
- DO NOT implement features "for the future"
- DO NOT create abstractions for "flexibility" without real need
- Cost of maintaining unused code > cost of implementing later

### Design Patterns (Contextual Application)

**Creational:**
- Factory Method: create objects without specifying concrete class
- Abstract Factory: families of related objects
- Builder: step-by-step construction of complex objects
- Singleton: single instance (use with GREAT caution - global state)
- Prototype: clone existing objects

**Structural:**
- Adapter: make incompatible interfaces compatible
- Bridge: separate abstraction from implementation
- Composite: treat individual and composite objects uniformly
- Decorator: add responsibilities dynamically
- Facade: simplified interface for complex subsystem
- Proxy: substitute/placeholder to control access

**Behavioral:**
- Strategy: family of interchangeable algorithms
- Observer: notification of state changes
- Command: encapsulate request as object
- State: alter behavior based on state
- Template Method: algorithm skeleton with customizable steps

### Code Architectures (Application by Context)

**Clean Architecture:**
```
Layers from outside to inside:
[Frameworks/Drivers] -> [Interface Adapters] -> [Use Cases] -> [Entities]

- Entities: enterprise business rules, independent of everything
- Use Cases: specific application rules, orchestrate entities
- Interface Adapters: data conversion between formats
- Frameworks: technical details (DB, Web, UI)

DEPENDENCY RULE: dependencies point only INWARD
```

**Hexagonal Architecture (Ports & Adapters):**
```
        [Primary Adapter]
               |
               v
[Adapter] -> [PORT] -> [DOMAIN] <- [PORT] <- [Adapter]
               ^
               |
        [Secondary Adapter]

- Domain: pure business logic, no external dependencies
- Ports: interfaces that the domain exposes/requires
- Adapters: concrete implementations of ports
```

**Onion Architecture:**
```
Concentric layers:
[Infrastructure] -> [Application Services] -> [Domain Services] -> [Domain Model]

- Domain Model: entities and value objects at the center
- Domain Services: logic that doesn't belong to an entity
- Application Services: orchestration, use cases
- Infrastructure: persistence, external APIs, UI
```

---

## PILLAR 2: ARCHITECTURAL MODELS

### Architectural Styles

**Monolith:**
```
Characteristics:
- Single deploy of entire application
- Shared database
- In-process communication

Advantages:
- Initial development simplicity
- Easier debugging and tracing
- Native ACID transactions
- Lower infrastructure overhead

Disadvantages:
- Limited scalability (scale everything or nothing)
- Risky deploy (small change = total deploy)
- Large development team competes for same codebase

USE WHEN: MVP, small team (<10 devs), simple domain
```

**Microservices:**
```
Characteristics:
- Independent services per bounded context
- Database per service
- Communication via network (sync/async)

Advantages:
- Granular scalability
- Independent deploy
- Autonomous teams per service
- Heterogeneous technology possible

Disadvantages:
- MUCH greater operational complexity
- Distributed debugging is difficult
- Eventual consistency (CAP theorem)
- Network overhead and latency

USE WHEN: Real scale needed, large teams, complex domains
NEVER START WITH MICROSERVICES - extract from mature monolith
```

**Event-Driven Architecture:**
```
Characteristics:
- Asynchronous communication via events
- Producers publish, Consumers react
- Event store as source of truth (optional)

Patterns:
- Event Notification: notify that something happened
- Event-Carried State Transfer: event contains all data
- Event Sourcing: persist events, derive state
- CQRS: separate read/write model

Advantages:
- Temporal and spatial decoupling
- Natural scalability
- Audit and event replay

Disadvantages:
- Eventual consistency mandatory
- More complex debugging
- Event ordering is challenging
```

### Infrastructure Components

**Message Queues:**
```
RabbitMQ:
- Traditional broker with AMQP
- Exchanges, Queues, Bindings
- Strong delivery guarantees
- Use for: task queues, RPC, simple pub/sub

Apache Kafka:
- Distributed log, not traditional queue
- Configurable message retention
- Consumer groups for parallelism
- Use for: event streaming, data pipelines, event sourcing

Amazon SQS:
- Managed serverless queue
- Standard (at-least-once) vs FIFO (exactly-once)
- Use for: simple decoupling in AWS
```

**Cache:**
```
Redis:
- In-memory key-value store
- Rich data structures (lists, sets, sorted sets, hashes)
- Built-in Pub/Sub
- Optional persistence (RDB, AOF)
- Use for: session store, cache, leaderboards, rate limiting

Memcached:
- Pure cache, simpler
- Multi-threaded (better CPU usage)
- No persistence
- Use for: simple object cache

Cache Strategies:
- Cache-Aside: application manages cache explicitly
- Read-Through: cache fetches from DB on miss
- Write-Through: write goes to cache and DB
- Write-Behind: write goes to cache, DB async
```

**Load Balancers:**
```
NGINX:
- Reverse proxy and load balancer
- High performance, low memory consumption
- Declarative configuration

Balancing Algorithms:
- Round Robin: sequential distribution
- Least Connections: send to least busy server
- IP Hash: same client always on same server (sticky sessions)
- Weighted: servers with different capacities
```

### Communication and Data

**Relational Databases (SQL):**
```
Characteristics:
- Rigid schema, ACID transactions
- Relationships via foreign keys
- Standardized SQL

Use when:
- Structured and related data
- Critical transactions (financial)
- Complex queries with JOINs
- Mandatory referential integrity

Examples: PostgreSQL, MySQL, SQL Server
```

**Non-Relational Databases (NoSQL):**
```
Document Stores (MongoDB, CouchDB):
- Flexible JSON/BSON documents
- Use for: product catalog, CMS, logs

Key-Value (Redis, DynamoDB):
- Access by key, no complex queries
- Use for: cache, sessions, configurations

Column-Family (Cassandra, HBase):
- Optimized for massive writes
- Use for: time-series, IoT, analytics

Graph (Neo4j, Neptune):
- Nodes and edges as first-class citizens
- Use for: social networks, recommendations, fraud
```

**Communication Protocols:**
```
REST:
- Stateless, resources via URLs
- HTTP verbs (GET, POST, PUT, DELETE)
- Simple, widely supported
- Use for: public APIs, simple CRUD

GraphQL:
- Query language for APIs
- Client defines response shape
- Single endpoint
- Use for: complex frontends, mobile (bandwidth)

gRPC:
- Protocol Buffers (binary)
- HTTP/2, bidirectional streaming
- Strong typing, code generation
- Use for: internal communication between services

WebSockets:
- Persistent bidirectional connection
- Low latency
- Use for: real-time (chat, games, live updates)
```

---

## PILLAR 3: CLOUD COMPUTING

### Fundamental Concepts

**Scalability:**
```
Vertical (Scale Up):
- Add more resources to existing server
- More CPU, RAM, disk
- Physical hardware limit
- Downtime during upgrade
- Simple, but limited

Horizontal (Scale Out):
- Add more instances/servers
- Load balancer distributes traffic
- Theoretically unlimited
- No downtime
- Requires stateless application

PREFER HORIZONTAL - design for scale out from day one
```

**High Availability:**
```
Objectives:
- Maximum uptime (99.9% = ~8h downtime/year)
- No single point of failure
- Automatic failover

Strategies:
- Multi-AZ deployment (availability zones)
- Database replication (primary-replica)
- Load balancer with health checks
- Auto-healing (replace unhealthy instances)
```

**Resilience and Fault Tolerance:**
```
Circuit Breaker:
- Prevent cascade of failures
- States: Closed -> Open -> Half-Open
- Fail fast when dependency is down

Retry with Backoff:
- Retry with exponential wait
- Jitter to avoid thundering herd
- Maximum retry limit

Bulkhead:
- Isolate resources per component
- Failure in one doesn't affect others
- Separate thread pools

Timeouts:
- ALWAYS define timeouts on external calls
- Default timeout = problem waiting to happen
```

**Elasticity:**
```
Auto Scaling:
- Automatic scaling based on metrics
- CPU, memory, requests/second
- Scale out when demand increases
- Scale in when demand decreases
- Pay only for actual usage

Serverless:
- Infinite managed scalability
- Zero to infinity instantly
- Pay-per-execution
- Cold start as trade-off
```

### Cloud Providers vs On-Premise

```
AWS (Amazon Web Services):
- Market leader, most services
- EC2, S3, RDS, Lambda, DynamoDB
- High learning curve

Azure (Microsoft):
- Integration with Microsoft ecosystem
- Strong in enterprise and hybrid
- Azure Functions, Cosmos DB

GCP (Google Cloud):
- Strong in ML/AI and analytics
- BigQuery, Kubernetes (GKE)
- Aggressive pricing

On-Premise:
- Total hardware control
- Compliance in regulated sectors
- Predictable cost (CAPEX vs OPEX)
- Total maintenance responsibility
```

---

## PILLAR 4: SYSTEM DESIGN AND DIAGRAMMING

### Diagram Levels

**HLD (High-Level Design):**
```
Objective: System overview
Audience: Stakeholders, managers, new members
Content:
- Main components (boxes)
- Data flow (arrows)
- Integration with external systems
- Main technologies

DOES NOT INCLUDE: Implementation details, classes, methods
```

**LLD (Low-Level Design):**
```
Objective: Blueprint for implementation
Audience: Developers
Content:
- Classes and interfaces
- Database schemas
- API endpoints
- Call sequences
- Data structures
```

### Functions of Diagrams

```
1. COMMUNICATION
   - Translate complex ideas into clear visuals
   - Align understanding between stakeholders
   - Base for technical discussions

2. DOCUMENTATION
   - Record of architectural decisions
   - Onboarding of new members
   - Reference for maintenance

3. ANALYSIS
   - Identify single points of failure
   - Detect bottlenecks before implementing
   - Validate non-functional requirements

4. PLANNING
   - Estimate effort per component
   - Identify dependencies
   - Define implementation order
```

### Essential Diagram Types

```
System Context Diagram:
- System as black box
- Users and external systems
- Highest level of abstraction

Container Diagram:
- Applications, databases, message queues
- Main technologies
- Communication between containers

Component Diagram:
- Modules within a container
- Responsibilities and dependencies
- Medium detail level

Sequence Diagram:
- Interaction between components over time
- Calls and responses
- Specific flows (happy path, errors)

ERD (Entity Relationship):
- Entities and relationships
- Attributes and cardinalities
- Database schema
```

---

## PILLAR 5: TECHNICAL COMMUNICATION

### Principles of Architectural Communication

**Clarity over Jargon:**
- Explain concepts in simple terms first
- Use analogies when appropriate
- Avoid acronyms without explanation

**Documentation as Communication:**
- Clear README with quick start
- ADRs (Architecture Decision Records) for important decisions
- Updated diagrams

**Defending Technical Decisions:**
```
Structure for justifying decisions:

1. CONTEXT: Current situation and problem
2. DECISION: What was chosen
3. ALTERNATIVES: What was considered and rejected
4. CONSEQUENCES: Trade-offs accepted
5. METRICS: How to measure success
```

**Trade-off Analysis:**
```
Always present decisions with explicit trade-offs:

Example: "Choosing MongoDB over PostgreSQL"
- PRO: Schema flexibility, horizontal scaling
- CON: No multi-document ACID transactions (until version 4)
- PRO: Better for hierarchical data
- CON: JOINs are expensive (denormalization necessary)
- DECISION: Our domain is more read than write, data
  naturally hierarchical, schema will evolve quickly
```

---

## PRACTICAL APPLICATION

When receiving any software task, this skill automatically applies:

1. **Fundamentals Analysis:** Does the code follow SOLID? Correct paradigm? Appropriate patterns?

2. **Architectural Evaluation:** Adequate architectural style? Well-defined components? Correct communication?

3. **Cloud Considerations:** Scalable? Resilient? Available? Elastic?

4. **Visualization:** Produce diagrams when necessary to communicate decisions

5. **Clear Communication:** Document decisions with justifications and trade-offs

---

## ABSOLUTE ANTI-PATTERNS (NEVER DO)

```
ARCHITECTURE:
- Big Ball of Mud (system without clear structure)
- Distributed Monolith (worst of both worlds)
- Golden Hammer (use same solution for everything)
- Premature Optimization
- Resume Driven Development (choose tech for CV)

CODE:
- God Class/Object (does everything)
- Spaghetti Code (impossible to follow flow)
- Copy-Paste Programming
- Magic Numbers/Strings
- Deep Nesting (more than 3 levels)

INFRASTRUCTURE:
- Single Point of Failure
- Hardcoded Configurations
- No Monitoring/Alerting
- No Backup Strategy
- Credentials in Code
```

---

## CODE STYLE RULES

### General Principles

- **Early return pattern**: Always use early returns instead of nested conditions
- Avoid duplication through reusable functions and modules
- Decompose long components/functions (>80 lines) into smaller units
- Files with more than 200 lines should be split
- Prefer arrow functions when possible

### Library-First Approach

- **ALWAYS search for existing solutions before custom code**
- Evaluate npm libraries, SaaS services, third-party APIs
- Custom code only for: unique business logic, performance-critical paths, special security requirements

### Code Quality

- Error handling with typed catch blocks
- Maximum 3 levels of nesting
- Focused functions, less than 50 lines when possible
- Focused files, less than 200 lines when possible
