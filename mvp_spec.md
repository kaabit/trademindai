# TradeMindAI MVP Specification

## Product vision
TradeMindAI helps importers, exporters, freight forwarders, and customs brokers review customs documents, detect missing information, suggest clarification questions, and reduce clearance delays.

## First MVP
The first version is an AI-assisted document checker for commercial invoices and packing lists.

## Core features
1. Upload or paste shipment document text.
2. Detect missing mandatory customs fields.
3. Detect HS code presence and possible format issues.
4. Detect vague product descriptions.
5. Detect sensitive words that require manual review.
6. Generate a risk score: Low / Medium / High.
7. Generate questions to send to the importer/exporter.
8. Export a review report.

## What the MVP will not do initially
- It will not submit customs declarations.
- It will not guarantee HS classification.
- It will not calculate final official duties.
- It will not replace a customs broker.
- It will not make legal decisions.

## Future roadmap
### Phase 2
- OCR for PDFs and scanned documents
- AI-generated HS code candidates
- Incoterms validation
- Country-specific document checklists

### Phase 3
- Duty and tax estimator
- Sanctions/restricted goods screening
- Broker dashboard
- Customer portal
- Audit trail

### Phase 4
- API for freight forwarders and logistics companies
- Integrations with ERP, TMS, customs broker systems
- Enterprise deployment
