// ============================================================================
// Abstract Task Domain: Write a Research Paper
// ============================================================================
// Demonstrates abstract planning with Sophia's capabilities.
// Each Process uses exactly one Capability (atomic execution).
// ============================================================================

// UUID Reference Table:
// Entity:
//   MyResearchPaper:        b0000001-0000-0000-0000-000000000001
//
// States:
//   TopicSelected:          c0000001-0000-0000-0000-000000000000
//   PapersFound:            c0000001-0000-0000-0000-000000000001
//   LiteratureSummarized:   c0000001-0000-0000-0000-000000000002
//   OutlineComplete:        c0000001-0000-0000-0000-000000000003
//   DraftWritten:           c0000001-0000-0000-0000-000000000004
//   DraftRevised:           c0000001-0000-0000-0000-000000000005
//   PaperFinalized:         c0000001-0000-0000-0000-000000000006
//
// Processes:
//   SearchForPapers:        d0000001-0000-0000-0000-000000000001
//   SummarizeLiterature:    d0000001-0000-0000-0000-000000000002
//   CreateOutline:          d0000001-0000-0000-0000-000000000003
//   WriteDraft:             d0000001-0000-0000-0000-000000000004
//   ReviseDraft:            d0000001-0000-0000-0000-000000000005
//   HumanReview:            d0000001-0000-0000-0000-000000000006
//
// Capabilities (Sophia's tools):
//   WebSearchCapability:    e0000001-0000-0000-0000-000000000001
//   LLMCapability:          e0000001-0000-0000-0000-000000000002
//   HumanCapability:        e0000001-0000-0000-0000-000000000003

// --- Concepts (Abstract Types) ---
CREATE (c1:Concept {uuid: "a0000001-0000-0000-0000-000000000001", name: "ResearchPaper", description: "A written academic paper"})
CREATE (c2:Concept {uuid: "a0000001-0000-0000-0000-000000000002", name: "Literature", description: "Body of existing research"})
CREATE (c3:Concept {uuid: "a0000001-0000-0000-0000-000000000003", name: "SearchTask", description: "Information retrieval task"})
CREATE (c4:Concept {uuid: "a0000001-0000-0000-0000-000000000004", name: "WritingTask", description: "Text generation task"})
CREATE (c5:Concept {uuid: "a0000001-0000-0000-0000-000000000005", name: "ReviewTask", description: "Human review/approval task"});

// --- Entity: The Paper We're Writing ---
CREATE (paper:Entity {
  uuid: "b0000001-0000-0000-0000-000000000001",
  name: "MyResearchPaper",
  description: "HCG Planning for Cognitive Tasks"
});

// --- States (Document/Knowledge States) ---

// Initial state
CREATE (s0:State {
  uuid: "c0000001-0000-0000-0000-000000000000",
  name: "TopicSelected",
  description: "Research topic has been chosen"
});

// After web search
CREATE (s1:State {
  uuid: "c0000001-0000-0000-0000-000000000001",
  name: "PapersFound",
  description: "Relevant papers have been found via search"
});

// After LLM summarization
CREATE (s2:State {
  uuid: "c0000001-0000-0000-0000-000000000002",
  name: "LiteratureSummarized",
  description: "Papers have been read and summarized"
});

// After outline creation
CREATE (s3:State {
  uuid: "c0000001-0000-0000-0000-000000000003",
  name: "OutlineComplete",
  description: "Paper structure is defined"
});

// After draft writing
CREATE (s4:State {
  uuid: "c0000001-0000-0000-0000-000000000004",
  name: "DraftWritten",
  description: "First draft is complete"
});

// After LLM revision
CREATE (s5:State {
  uuid: "c0000001-0000-0000-0000-000000000005",
  name: "DraftRevised",
  description: "Draft has been revised by LLM"
});

// Goal state - after human review
CREATE (s6:State {
  uuid: "c0000001-0000-0000-0000-000000000006",
  name: "PaperFinalized",
  description: "Paper is reviewed and ready for submission"
});

// --- Link States to Entity ---
MATCH (paper:Entity {uuid: "b0000001-0000-0000-0000-000000000001"})
MATCH (s0:State {uuid: "c0000001-0000-0000-0000-000000000000"})
MATCH (s1:State {uuid: "c0000001-0000-0000-0000-000000000001"})
MATCH (s2:State {uuid: "c0000001-0000-0000-0000-000000000002"})
MATCH (s3:State {uuid: "c0000001-0000-0000-0000-000000000003"})
MATCH (s4:State {uuid: "c0000001-0000-0000-0000-000000000004"})
MATCH (s5:State {uuid: "c0000001-0000-0000-0000-000000000005"})
MATCH (s6:State {uuid: "c0000001-0000-0000-0000-000000000006"})
CREATE (s0)-[:OF_ENTITY]->(paper)
CREATE (s1)-[:OF_ENTITY]->(paper)
CREATE (s2)-[:OF_ENTITY]->(paper)
CREATE (s3)-[:OF_ENTITY]->(paper)
CREATE (s4)-[:OF_ENTITY]->(paper)
CREATE (s5)-[:OF_ENTITY]->(paper)
CREATE (s6)-[:OF_ENTITY]->(paper);

// === CAPABILITIES (Sophia's Tools) ===

CREATE (cap_search:Capability {
  uuid: "e0000001-0000-0000-0000-000000000001",
  name: "WebSearchCapability",
  description: "Search the web for academic papers and resources",
  executor_type: "service",
  service_endpoint: "https://api.semanticscholar.org/",
  estimated_duration_ms: 5000,
  success_rate: 0.95
});

CREATE (cap_llm:Capability {
  uuid: "e0000001-0000-0000-0000-000000000002",
  name: "LLMCapability",
  description: "Use language model for reading, writing, and analysis",
  executor_type: "llm",
  prompt_template: "You are a research assistant helping write an academic paper.",
  estimated_duration_ms: 30000,
  success_rate: 0.90
});

CREATE (cap_human:Capability {
  uuid: "e0000001-0000-0000-0000-000000000003",
  name: "HumanCapability",
  description: "Request human review and approval",
  executor_type: "human",
  instruction_template: "Please review the document and provide feedback.",
  estimated_duration_ms: 3600000,
  success_rate: 1.0
});

// --- Link Capabilities to Concepts via IMPLEMENTS ---
MATCH (cap_search:Capability {uuid: "e0000001-0000-0000-0000-000000000001"})
MATCH (search_concept:Concept {uuid: "a0000001-0000-0000-0000-000000000003"})
CREATE (cap_search)-[:IMPLEMENTS]->(search_concept);

MATCH (cap_llm:Capability {uuid: "e0000001-0000-0000-0000-000000000002"})
MATCH (writing_concept:Concept {uuid: "a0000001-0000-0000-0000-000000000004"})
CREATE (cap_llm)-[:IMPLEMENTS]->(writing_concept);

MATCH (cap_human:Capability {uuid: "e0000001-0000-0000-0000-000000000003"})
MATCH (review_concept:Concept {uuid: "a0000001-0000-0000-0000-000000000005"})
CREATE (cap_human)-[:IMPLEMENTS]->(review_concept);

// === PROCESSES (Atomic Tasks) ===

// Process 1: SearchForPapers (WebSearch)
CREATE (p1:Process {
  uuid: "d0000001-0000-0000-0000-000000000001",
  name: "SearchForPapers",
  description: "Search academic databases for relevant papers",
  duration_ms: 5000
});

// Process 2: SummarizeLiterature (LLM)
CREATE (p2:Process {
  uuid: "d0000001-0000-0000-0000-000000000002",
  name: "SummarizeLiterature",
  description: "Read and summarize the found papers",
  duration_ms: 60000
});

// Process 3: CreateOutline (LLM)
CREATE (p3:Process {
  uuid: "d0000001-0000-0000-0000-000000000003",
  name: "CreateOutline",
  description: "Create paper outline based on literature review",
  duration_ms: 30000
});

// Process 4: WriteDraft (LLM)
CREATE (p4:Process {
  uuid: "d0000001-0000-0000-0000-000000000004",
  name: "WriteDraft",
  description: "Write the first complete draft",
  duration_ms: 120000
});

// Process 5: ReviseDraft (LLM)
CREATE (p5:Process {
  uuid: "d0000001-0000-0000-0000-000000000005",
  name: "ReviseDraft",
  description: "Revise and improve the draft",
  duration_ms: 60000
});

// Process 6: HumanReview (Human)
CREATE (p6:Process {
  uuid: "d0000001-0000-0000-0000-000000000006",
  name: "HumanReview",
  description: "Human reviews and finalizes the paper",
  duration_ms: 3600000
});

// === REQUIRES/CAUSES Edges (The Planning Graph) ===

// SearchForPapers: requires TopicSelected, causes PapersFound
MATCH (p:Process {uuid: "d0000001-0000-0000-0000-000000000001"})
MATCH (pre:State {uuid: "c0000001-0000-0000-0000-000000000000"})
MATCH (post:State {uuid: "c0000001-0000-0000-0000-000000000001"})
CREATE (p)-[:REQUIRES]->(pre)
CREATE (p)-[:CAUSES]->(post);

// SummarizeLiterature: requires PapersFound, causes LiteratureSummarized
MATCH (p:Process {uuid: "d0000001-0000-0000-0000-000000000002"})
MATCH (pre:State {uuid: "c0000001-0000-0000-0000-000000000001"})
MATCH (post:State {uuid: "c0000001-0000-0000-0000-000000000002"})
CREATE (p)-[:REQUIRES]->(pre)
CREATE (p)-[:CAUSES]->(post);

// CreateOutline: requires LiteratureSummarized, causes OutlineComplete
MATCH (p:Process {uuid: "d0000001-0000-0000-0000-000000000003"})
MATCH (pre:State {uuid: "c0000001-0000-0000-0000-000000000002"})
MATCH (post:State {uuid: "c0000001-0000-0000-0000-000000000003"})
CREATE (p)-[:REQUIRES]->(pre)
CREATE (p)-[:CAUSES]->(post);

// WriteDraft: requires OutlineComplete, causes DraftWritten
MATCH (p:Process {uuid: "d0000001-0000-0000-0000-000000000004"})
MATCH (pre:State {uuid: "c0000001-0000-0000-0000-000000000003"})
MATCH (post:State {uuid: "c0000001-0000-0000-0000-000000000004"})
CREATE (p)-[:REQUIRES]->(pre)
CREATE (p)-[:CAUSES]->(post);

// ReviseDraft: requires DraftWritten, causes DraftRevised
MATCH (p:Process {uuid: "d0000001-0000-0000-0000-000000000005"})
MATCH (pre:State {uuid: "c0000001-0000-0000-0000-000000000004"})
MATCH (post:State {uuid: "c0000001-0000-0000-0000-000000000005"})
CREATE (p)-[:REQUIRES]->(pre)
CREATE (p)-[:CAUSES]->(post);

// HumanReview: requires DraftRevised, causes PaperFinalized
MATCH (p:Process {uuid: "d0000001-0000-0000-0000-000000000006"})
MATCH (pre:State {uuid: "c0000001-0000-0000-0000-000000000005"})
MATCH (post:State {uuid: "c0000001-0000-0000-0000-000000000006"})
CREATE (p)-[:REQUIRES]->(pre)
CREATE (p)-[:CAUSES]->(post);

// === USES_CAPABILITY Edges (Process -> Capability) ===

// SearchForPapers uses WebSearchCapability
MATCH (p:Process {uuid: "d0000001-0000-0000-0000-000000000001"})
MATCH (cap:Capability {uuid: "e0000001-0000-0000-0000-000000000001"})
CREATE (p)-[:USES_CAPABILITY]->(cap);

// SummarizeLiterature uses LLMCapability
MATCH (p:Process {uuid: "d0000001-0000-0000-0000-000000000002"})
MATCH (cap:Capability {uuid: "e0000001-0000-0000-0000-000000000002"})
CREATE (p)-[:USES_CAPABILITY]->(cap);

// CreateOutline uses LLMCapability
MATCH (p:Process {uuid: "d0000001-0000-0000-0000-000000000003"})
MATCH (cap:Capability {uuid: "e0000001-0000-0000-0000-000000000002"})
CREATE (p)-[:USES_CAPABILITY]->(cap);

// WriteDraft uses LLMCapability
MATCH (p:Process {uuid: "d0000001-0000-0000-0000-000000000004"})
MATCH (cap:Capability {uuid: "e0000001-0000-0000-0000-000000000002"})
CREATE (p)-[:USES_CAPABILITY]->(cap);

// ReviseDraft uses LLMCapability
MATCH (p:Process {uuid: "d0000001-0000-0000-0000-000000000005"})
MATCH (cap:Capability {uuid: "e0000001-0000-0000-0000-000000000002"})
CREATE (p)-[:USES_CAPABILITY]->(cap);

// HumanReview uses HumanCapability
MATCH (p:Process {uuid: "d0000001-0000-0000-0000-000000000006"})
MATCH (cap:Capability {uuid: "e0000001-0000-0000-0000-000000000003"})
CREATE (p)-[:USES_CAPABILITY]->(cap);

// === Process IS_A Concept (for capability lookup via type) ===

MATCH (p1:Process {uuid: "d0000001-0000-0000-0000-000000000001"})
MATCH (search_concept:Concept {uuid: "a0000001-0000-0000-0000-000000000003"})
CREATE (p1)-[:IS_A]->(search_concept);

MATCH (p2:Process {uuid: "d0000001-0000-0000-0000-000000000002"})
MATCH (p3:Process {uuid: "d0000001-0000-0000-0000-000000000003"})
MATCH (p4:Process {uuid: "d0000001-0000-0000-0000-000000000004"})
MATCH (p5:Process {uuid: "d0000001-0000-0000-0000-000000000005"})
MATCH (writing_concept:Concept {uuid: "a0000001-0000-0000-0000-000000000004"})
CREATE (p2)-[:IS_A]->(writing_concept)
CREATE (p3)-[:IS_A]->(writing_concept)
CREATE (p4)-[:IS_A]->(writing_concept)
CREATE (p5)-[:IS_A]->(writing_concept);

MATCH (p6:Process {uuid: "d0000001-0000-0000-0000-000000000006"})
MATCH (review_concept:Concept {uuid: "a0000001-0000-0000-0000-000000000005"})
CREATE (p6)-[:IS_A]->(review_concept);
