# Neo4j Knowledge Graph Schema — Sen'Analytics Mission Control

## Graph Model

The knowledge graph stores governance relationships that are naturally graph-shaped:
lineage, ownership, regulation mapping, control dependencies, and risk propagation.

---

## Node Types

### :DataDomain
```
CREATE (:DataDomain {
    id: "uuid",
    name: "Customer Data",
    description: "All customer-related data assets",
    owner: "Data Governance Team",
    sensitivity: "HIGH",
    created_at: datetime()
})
```

### :DataProduct
```
CREATE (:DataProduct {
    id: "uuid",
    name: "Customer 360",
    description: "Unified customer profile",
    domain_id: "uuid",
    owner: "Product Team",
    created_at: datetime()
})
```

### :Table
```
CREATE (:Table {
    id: "uuid",
    name: "customers",
    schema: "public",
    database: "prod-db",
    row_count: 1500000,
    storage_bytes: 524288000,
    created_at: datetime()
})
```

### :Column
```
CREATE (:Column {
    id: "uuid",
    name: "email",
    data_type: "VARCHAR(255)",
    nullable: false,
    is_pii: true,
    classification: "PII-EMAIL",
    sensitivity: "HIGH",
    encryption_status: "encrypted_at_rest"
})
```

### :Report
```
CREATE (:Report {
    id: "uuid",
    name: "Quarterly Compliance Report",
    type: "COMPLIANCE",
    format: "PDF",
    generated_by: "Reporting Agent",
    created_at: datetime()
})
```

### :Control
```
CREATE (:Control {
    id: "uuid",
    name: "Control-17",
    description: "Encryption at rest for PII data",
    framework: "SOC2-CC6.1",
    status: "IMPLEMENTED",
    last_assessed: datetime()
})
```

### :Policy
```
CREATE (:Policy {
    id: "uuid",
    name: "CDP-ART-34",
    title: "PII Encryption Requirement",
    description: "PII must be encrypted at rest and in transit",
    framework: "Senegal-CDP",
    category: "DATA_PROTECTION",
    severity: "CRITICAL"
})
```

### :Owner
```
CREATE (:Owner {
    id: "uuid",
    name: "Aminata Diop",
    role: "Data Steward",
    department: "Governance",
    email: "aminata@example.com"
})
```

### :Risk
```
CREATE (:Risk {
    id: "uuid",
    name: "Unencrypted PII in transit",
    likelihood: 0.7,
    impact: 0.9,
    score: 0.63,
    severity: "CRITICAL",
    status: "OPEN",
    detected_at: datetime()
})
```

### :Incident
```
CREATE (:Incident {
    id: "uuid",
    name: "Cross-border PII transfer to US",
    severity: "CRITICAL",
    status: "INVESTIGATING",
    detected_by: "PolicyEvaluator",
    detected_at: datetime()
})
```

---

## Relationships

```
// Lineage
(:DataDomain)-[:CONTAINS]->(:DataProduct)
(:DataProduct)-[:CONTAINS]->(:Table)
(:Table)-[:HAS_COLUMN]->(:Column)

// Classification
(:Column)-[:CLASSIFIED_AS {confidence: 0.95, detected_by: "ClassificationAgent"}]->(:Classification)

// Ownership
(:DataDomain)-[:OWNED_BY]->(:Owner)
(:Table)-[:STEWARDED_BY]->(:Owner)

// Regulation mapping
(:Column)-[:REGULATED_BY]->(:Policy)
(:Policy)-[:MAPPED_TO]->(:Control)
(:Policy)-[:DERIVED_FROM]->(:Framework)

// Risk mapping
(:Column)-[:HAS_RISK]->(:Risk)
(:Risk)-[:MITIGATED_BY]->(:Control)
(:Risk)-[:CAUSED]->(:Incident)

// Reporting
(:Incident)-[:DOCUMENTED_IN]->(:Report)
(:Risk)-[:REPORTED_IN]->(:Report)
(:Policy)-[:EVIDENCED_BY]->(:Report)
```

---

## Key Queries

### 1. Full Lineage: Trace a column's entire governance context
```cypher
MATCH (d:DataDomain)-[:CONTAINS*]->(t:Table)-[:HAS_COLUMN]->(c:Column {name: "email"})
MATCH (c)-[:REGULATED_BY]->(p:Policy)-[:MAPPED_TO]->(ctrl:Control)
MATCH (c)-[:HAS_RISK]->(r:Risk)
RETURN d, t, c, p, ctrl, r
```

### 2. Impact Analysis: What breaks if a policy changes?
```cypher
MATCH (p:Policy {name: "CDP-ART-34"})<-[:REGULATED_BY]-(c:Column)<-[:HAS_COLUMN]-(t:Table)
MATCH (c)-[:HAS_RISK]->(r:Risk)
RETURN p.name, c.name, t.name, r.severity
```

### 3. Compliance Gap Report: Columns with no mapped control
```cypher
MATCH (c:Column {is_pii: true})
WHERE NOT (c)-[:REGULATED_BY]->(:Policy)-[:MAPPED_TO]->(:Control)
RETURN c.name, c.table, c.classification
```

### 4. Risk Heatmap: Top risks by score
```cypher
MATCH (r:Risk {status: "OPEN"})
MATCH (r)<-[:HAS_RISK]-(c:Column)
RETURN r.name, r.score, r.likelihood, r.impact, count(c) as affected_columns
ORDER BY r.score DESC LIMIT 20
```

### 5. Audit Trail: Full trace of an incident
```cypher
MATCH (i:Incident {name: "Cross-border PII transfer to US"})
OPTIONAL MATCH (i)-[*..3]-(related)
RETURN i, related
```

---

## Integration Pattern

```python
# backend/app/knowledge/graph.py
from neo4j import GraphDatabase

class KnowledgeGraph:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def register_data_domain(self, domain: dict):
        with self.driver.session() as session:
            session.run(
                "CREATE (d:DataDomain $props)", props=domain
            )
    
    def trace_lineage(self, column_name: str):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (d:DataDomain)-[:CONTAINS*]->(t:Table)-[:HAS_COLUMN]->(c:Column {name: $name})
                MATCH (c)-[:REGULATED_BY]->(p:Policy)-[:MAPPED_TO]->(ctrl:Control)
                MATCH (c)-[:HAS_RISK]->(r:Risk)
                RETURN d, t, c, p, ctrl, r
                """, name=column_name
            )
            return result.data()
```

---

## Sync with PostgreSQL

Knowledge graph nodes are mirrored in PostgreSQL `knowledge_nodes` and `knowledge_edges` tables
for SQL-based querying and backup. The Neo4j graph is the **primary** store for graph traversals
(lineage, impact analysis). PostgreSQL is the **source of truth** for relational data (workflows,
executions, audit logs).

Synchronization pattern:
1. Write to PostgreSQL first (transactional)
2. Upsert into Neo4j (eventually consistent)
3. Use Redis Streams for async sync
