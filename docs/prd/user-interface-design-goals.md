# User Interface Design Goals

## Overall UX Vision

The user experience centers on **conversational, natural language interaction** that feels like consulting with an intelligent assistant rather than operating a traditional search interface. Recruiters should be able to express complex, multi-criteria requirements in plain English without learning query syntax or navigating complex filter menus. The system prioritizes **transparency and explainability**—every recommendation should come with clear reasoning that helps recruiters understand and trust the results. The interface should support iterative refinement, allowing users to naturally narrow or expand searches through follow-up questions, mimicking how they would work with a human research assistant.

## Key Interaction Paradigms

- **Conversational Query**: Users type natural language questions in a chat interface (e.g., "Show me senior DevOps engineers with AWS and Terraform experience")
- **Iterative Refinement**: Follow-up queries that modify previous searches (e.g., "Now show only candidates with leadership experience")
- **Explainable Results**: Each candidate recommendation displays as a rich card or message showing match reasoning, graph relationships, and skill alignments
- **Contextual Clarification**: System can ask clarifying questions when queries are ambiguous (e.g., "By 'cloud experience' do you mean AWS, Azure, GCP, or any cloud platform?")
- **Progressive Disclosure**: Initial results show summary information with expandable details for deeper exploration of candidate-profile alignments

## Core Screens and Views

Since this is an OpenWebUI-based solution, the interface is primarily chat-driven:

- **Chat Interface**: Primary view where all queries are entered and results are displayed
- **Candidate Detail View**: Expanded view showing full CV content, all matched CIGREF missions/activities, graph relationship visualizations, and confidence scores
- **Match Explanation Panel**: Structured breakdown of why a candidate was recommended, including skill overlaps, experience alignment, and graph-based insights
- **Query History**: Sidebar or panel showing previous searches for easy recall and refinement

## Accessibility

**WCAG AA compliance** through OpenWebUI's existing accessibility features. No custom accessibility work required for POC—leverage OpenWebUI's built-in support for screen readers, keyboard navigation, and contrast standards.

**Assumption**: OpenWebUI already meets basic accessibility requirements. If specific recruitment workflows require enhanced accessibility (e.g., high-volume screen reader use), this would be addressed in Phase 2.

## Branding

**Minimal branding requirements for POC**. Use OpenWebUI's default theme with potential minor customization:
- Clean, professional aesthetic appropriate for HR/recruitment workflows
- Clear visual hierarchy distinguishing system messages from candidate results
- Readable typography for dense information (CV content, competency descriptions)

**Assumption**: No corporate branding requirements exist for POC. If production deployment requires specific brand alignment, this would be configured in OpenWebUI's theming system during Phase 2.

## Target Device and Platforms

**Web Responsive (Desktop-Primary)**

Primary use case is desktop/laptop usage by recruiters at their workstations during candidate screening workflows. The OpenWebUI interface should be:
- Optimized for desktop browsers (Chrome, Edge, Firefox)
- Functional on tablets (iPad) for managers reviewing shortlists on the go
- Mobile-accessible but not optimized (basic chat functionality works, but dense candidate information may be cramped)

**Assumption**: Recruiters primarily work at desks with large screens when conducting detailed candidate evaluation. Mobile access is secondary for Phase 2 consideration.

---
