# Ontology Design

## Object
A governed business entity such as Equipment, P&ID, HAZOP Node or Safeguard.

## Property
Typed business information such as equipment tag, design pressure, revision or PFD.

## Link
Semantic relationships, for example:
- Equipment LOCATED_IN Unit
- Equipment REPRESENTED_ON PIDDocument
- Equipment INCLUDED_IN HAZOPNode
- Deviation HAS_CAUSE Cause
- Consequence MITIGATED_BY Safeguard

## Action
Typed operations executed through policy controls, for example:
- approve recommendation
- close action item
- import DEXPI revision
- create HAZOP draft
- validate safeguard

## AI interaction
AI reads through ontology services and acts through governed action definitions. This creates a stable security and audit boundary.

## Versioning
Future releases should version object types, property schemas, link constraints, action contracts, agent definitions, workflows and policies.
