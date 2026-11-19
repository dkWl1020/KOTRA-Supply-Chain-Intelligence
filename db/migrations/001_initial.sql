-- SQLite 3.35+; run inside a transaction with PRAGMA foreign_keys=ON.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS "regions" (
  "region_id" TEXT NOT NULL,
  "name_ko" TEXT NOT NULL,
  "name_en" TEXT NOT NULL,
  "area_type" TEXT NOT NULL,
  "parent_id" TEXT,
  "fips" TEXT,
  "scope_note" TEXT,
  PRIMARY KEY ("region_id"),
  FOREIGN KEY ("parent_id") REFERENCES "regions"("region_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_regions_parent_id" ON "regions"("parent_id");

CREATE TABLE IF NOT EXISTS "region_memberships" (
  "membership_id" TEXT NOT NULL,
  "research_region_id" TEXT NOT NULL,
  "member_region_id" TEXT NOT NULL,
  "valid_from" TEXT,
  "valid_to" TEXT,
  PRIMARY KEY ("membership_id"),
  FOREIGN KEY ("research_region_id") REFERENCES "regions"("region_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("member_region_id") REFERENCES "regions"("region_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_region_memberships_research_region_id" ON "region_memberships"("research_region_id");

CREATE INDEX IF NOT EXISTS "idx_region_memberships_member_region_id" ON "region_memberships"("member_region_id");

CREATE TABLE IF NOT EXISTS "industries" (
  "industry_id" TEXT NOT NULL,
  "industry_name" TEXT NOT NULL,
  "cluster" TEXT NOT NULL,
  "parent_industry_id" TEXT,
  "definition" TEXT,
  PRIMARY KEY ("industry_id"),
  FOREIGN KEY ("parent_industry_id") REFERENCES "industries"("industry_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_industries_parent_industry_id" ON "industries"("parent_industry_id");

CREATE TABLE IF NOT EXISTS "companies" (
  "company_id" TEXT NOT NULL,
  "name_ko" TEXT,
  "name_en" TEXT NOT NULL,
  "country" TEXT NOT NULL,
  "entity_type" TEXT NOT NULL,
  "parent_company_id" TEXT,
  "website" TEXT,
  "aliases" TEXT,
  "is_demo" INTEGER CHECK ("is_demo" IN (0,1)),
  "visibility" TEXT,
  PRIMARY KEY ("company_id"),
  FOREIGN KEY ("parent_company_id") REFERENCES "companies"("company_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_companies_parent_company_id" ON "companies"("parent_company_id");

CREATE TABLE IF NOT EXISTS "facilities" (
  "facility_id" TEXT NOT NULL,
  "facility_name" TEXT,
  "operator_company_id" TEXT NOT NULL,
  "owner_company_id" TEXT,
  "region_id" TEXT NOT NULL,
  "facility_type" TEXT NOT NULL,
  "address" TEXT,
  "latitude" REAL CHECK ("latitude" BETWEEN -90 AND 90),
  "longitude" REAL CHECK ("longitude" BETWEEN -180 AND 180),
  "operating_status" TEXT,
  "coordinate_source" TEXT,
  "geocoding_precision" TEXT,
  "valid_from" TEXT,
  "valid_to" TEXT,
  PRIMARY KEY ("facility_id"),
  FOREIGN KEY ("operator_company_id") REFERENCES "companies"("company_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("owner_company_id") REFERENCES "companies"("company_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("region_id") REFERENCES "regions"("region_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_facilities_operator_company_id" ON "facilities"("operator_company_id");

CREATE INDEX IF NOT EXISTS "idx_facilities_owner_company_id" ON "facilities"("owner_company_id");

CREATE INDEX IF NOT EXISTS "idx_facilities_region_id" ON "facilities"("region_id");

CREATE TABLE IF NOT EXISTS "products" (
  "product_id" TEXT NOT NULL,
  "product_name" TEXT NOT NULL,
  "product_group" TEXT,
  "description" TEXT,
  PRIMARY KEY ("product_id")
);

CREATE TABLE IF NOT EXISTS "activities" (
  "activity_id" TEXT NOT NULL,
  "company_id" TEXT NOT NULL,
  "facility_id" TEXT,
  "industry_id" TEXT NOT NULL,
  "product_id" TEXT,
  "activity_role" TEXT NOT NULL,
  "record_basis" TEXT NOT NULL,
  PRIMARY KEY ("activity_id"),
  FOREIGN KEY ("company_id") REFERENCES "companies"("company_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("facility_id") REFERENCES "facilities"("facility_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("industry_id") REFERENCES "industries"("industry_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("product_id") REFERENCES "products"("product_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_activities_company_id" ON "activities"("company_id");

CREATE INDEX IF NOT EXISTS "idx_activities_facility_id" ON "activities"("facility_id");

CREATE INDEX IF NOT EXISTS "idx_activities_industry_id" ON "activities"("industry_id");

CREATE INDEX IF NOT EXISTS "idx_activities_product_id" ON "activities"("product_id");

CREATE TABLE IF NOT EXISTS "statistics" (
  "observation_id" TEXT NOT NULL,
  "metric_id" TEXT NOT NULL,
  "region_id" TEXT,
  "industry_id" TEXT,
  "company_id" TEXT,
  "facility_id" TEXT,
  "product_id" TEXT,
  "period" TEXT NOT NULL,
  "value" REAL,
  "unit" TEXT NOT NULL,
  "value_type" TEXT NOT NULL,
  "scope_note" TEXT,
  "source_id" TEXT NOT NULL,
  "period_start" TEXT,
  "period_end" TEXT,
  "frequency" TEXT,
  "currency" TEXT,
  "price_basis" TEXT,
  "base_year" INTEGER,
  "adjustment" TEXT,
  "ownership_scope" TEXT,
  "partner_region_id" TEXT,
  "trade_direction" TEXT,
  "value_status" TEXT NOT NULL,
  "lower_bound" REAL,
  "upper_bound" REAL,
  "record_version_id" TEXT,
  PRIMARY KEY ("observation_id"),
  FOREIGN KEY ("metric_id") REFERENCES "metric_definitions"("metric_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("region_id") REFERENCES "regions"("region_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("industry_id") REFERENCES "industries"("industry_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("company_id") REFERENCES "companies"("company_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("facility_id") REFERENCES "facilities"("facility_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("product_id") REFERENCES "products"("product_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("source_id") REFERENCES "sources"("source_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("partner_region_id") REFERENCES "regions"("region_id") DEFERRABLE INITIALLY DEFERRED,
  CHECK (lower_bound IS NULL OR upper_bound IS NULL OR lower_bound <= upper_bound)
);

CREATE INDEX IF NOT EXISTS "idx_statistics_metric_id" ON "statistics"("metric_id");

CREATE INDEX IF NOT EXISTS "idx_statistics_region_id" ON "statistics"("region_id");

CREATE INDEX IF NOT EXISTS "idx_statistics_industry_id" ON "statistics"("industry_id");

CREATE INDEX IF NOT EXISTS "idx_statistics_company_id" ON "statistics"("company_id");

CREATE INDEX IF NOT EXISTS "idx_statistics_facility_id" ON "statistics"("facility_id");

CREATE INDEX IF NOT EXISTS "idx_statistics_product_id" ON "statistics"("product_id");

CREATE INDEX IF NOT EXISTS "idx_statistics_source_id" ON "statistics"("source_id");

CREATE INDEX IF NOT EXISTS "idx_statistics_partner_region_id" ON "statistics"("partner_region_id");

CREATE TABLE IF NOT EXISTS "projects" (
  "project_id" TEXT NOT NULL,
  "company_id" TEXT NOT NULL,
  "facility_id" TEXT,
  "project_type" TEXT NOT NULL,
  "investment_value" REAL,
  "currency" TEXT,
  "announced_at" TEXT,
  "construction_at" TEXT,
  "target_operation_at" TEXT,
  "project_stage" TEXT NOT NULL,
  PRIMARY KEY ("project_id"),
  FOREIGN KEY ("company_id") REFERENCES "companies"("company_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("facility_id") REFERENCES "facilities"("facility_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_projects_company_id" ON "projects"("company_id");

CREATE INDEX IF NOT EXISTS "idx_projects_facility_id" ON "projects"("facility_id");

CREATE TABLE IF NOT EXISTS "relationships" (
  "relationship_id" TEXT NOT NULL,
  "from_company_id" TEXT NOT NULL,
  "to_company_id" TEXT NOT NULL,
  "relationship_type" TEXT NOT NULL,
  "product_id" TEXT,
  "from_facility_id" TEXT,
  "to_facility_id" TEXT,
  "valid_from" TEXT,
  "valid_to" TEXT,
  "record_basis" TEXT NOT NULL,
  PRIMARY KEY ("relationship_id"),
  FOREIGN KEY ("from_company_id") REFERENCES "companies"("company_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("to_company_id") REFERENCES "companies"("company_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("product_id") REFERENCES "products"("product_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("from_facility_id") REFERENCES "facilities"("facility_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("to_facility_id") REFERENCES "facilities"("facility_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_relationships_from_company_id" ON "relationships"("from_company_id");

CREATE INDEX IF NOT EXISTS "idx_relationships_to_company_id" ON "relationships"("to_company_id");

CREATE INDEX IF NOT EXISTS "idx_relationships_product_id" ON "relationships"("product_id");

CREATE INDEX IF NOT EXISTS "idx_relationships_from_facility_id" ON "relationships"("from_facility_id");

CREATE INDEX IF NOT EXISTS "idx_relationships_to_facility_id" ON "relationships"("to_facility_id");

CREATE TABLE IF NOT EXISTS "routes" (
  "route_id" TEXT NOT NULL,
  "route_name" TEXT NOT NULL,
  "origin_region_id" TEXT,
  "destination_region_id" TEXT,
  "origin_facility_id" TEXT,
  "destination_facility_id" TEXT,
  "route_basis" TEXT NOT NULL,
  "valid_from" TEXT,
  "valid_to" TEXT,
  PRIMARY KEY ("route_id"),
  FOREIGN KEY ("origin_region_id") REFERENCES "regions"("region_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("destination_region_id") REFERENCES "regions"("region_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("origin_facility_id") REFERENCES "facilities"("facility_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("destination_facility_id") REFERENCES "facilities"("facility_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_routes_origin_region_id" ON "routes"("origin_region_id");

CREATE INDEX IF NOT EXISTS "idx_routes_destination_region_id" ON "routes"("destination_region_id");

CREATE INDEX IF NOT EXISTS "idx_routes_origin_facility_id" ON "routes"("origin_facility_id");

CREATE INDEX IF NOT EXISTS "idx_routes_destination_facility_id" ON "routes"("destination_facility_id");

CREATE TABLE IF NOT EXISTS "route_segments" (
  "segment_id" TEXT NOT NULL,
  "route_id" TEXT NOT NULL,
  "sequence" INTEGER NOT NULL CHECK ("sequence" >= 0),
  "origin_facility_id" TEXT,
  "destination_facility_id" TEXT,
  "transport_mode" TEXT NOT NULL,
  "corridor_name" TEXT,
  "geometry_ref" TEXT,
  PRIMARY KEY ("segment_id"),
  FOREIGN KEY ("route_id") REFERENCES "routes"("route_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("origin_facility_id") REFERENCES "facilities"("facility_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("destination_facility_id") REFERENCES "facilities"("facility_id") DEFERRABLE INITIALLY DEFERRED,
  UNIQUE(route_id, sequence)
);

CREATE INDEX IF NOT EXISTS "idx_route_segments_route_id" ON "route_segments"("route_id");

CREATE INDEX IF NOT EXISTS "idx_route_segments_origin_facility_id" ON "route_segments"("origin_facility_id");

CREATE INDEX IF NOT EXISTS "idx_route_segments_destination_facility_id" ON "route_segments"("destination_facility_id");

CREATE TABLE IF NOT EXISTS "risk_profiles" (
  "risk_profile_id" TEXT NOT NULL,
  "target_type" TEXT NOT NULL,
  "target_id" TEXT NOT NULL,
  "risk_type" TEXT NOT NULL,
  "description" TEXT,
  "metric_id" TEXT,
  "assessment_basis" TEXT NOT NULL,
  "reference_period" TEXT,
  PRIMARY KEY ("risk_profile_id"),
  FOREIGN KEY ("metric_id") REFERENCES "metric_definitions"("metric_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_risk_profiles_metric_id" ON "risk_profiles"("metric_id");

CREATE TABLE IF NOT EXISTS "events" (
  "event_id" TEXT NOT NULL,
  "event_type" TEXT NOT NULL,
  "title" TEXT NOT NULL,
  "description" TEXT,
  "occurred_at" TEXT,
  "announced_at" TEXT,
  "ended_at" TEXT,
  "event_status" TEXT NOT NULL,
  "location_ref" TEXT,
  "external_event_key" TEXT,
  "last_seen_at" TEXT,
  "expires_at" TEXT,
  "geometry_ref" TEXT,
  "severity_basis" TEXT,
  "is_replay" INTEGER CHECK ("is_replay" IN (0,1)),
  PRIMARY KEY ("event_id")
);

CREATE TABLE IF NOT EXISTS "event_impacts" (
  "impact_id" TEXT NOT NULL,
  "event_id" TEXT NOT NULL,
  "target_type" TEXT NOT NULL,
  "target_id" TEXT NOT NULL,
  "impact_type" TEXT NOT NULL,
  "impact_description" TEXT,
  "assessment_basis" TEXT NOT NULL,
  "relationship_id" TEXT,
  "analysis_id" TEXT,
  "regulation_id" TEXT,
  "assessment_status" TEXT,
  "input_version_refs" TEXT,
  "review_id" TEXT,
  PRIMARY KEY ("impact_id"),
  FOREIGN KEY ("event_id") REFERENCES "events"("event_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("relationship_id") REFERENCES "relationships"("relationship_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("analysis_id") REFERENCES "analysis_runs"("analysis_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("regulation_id") REFERENCES "regulations"("regulation_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("review_id") REFERENCES "review_history"("review_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_event_impacts_event_id" ON "event_impacts"("event_id");

CREATE INDEX IF NOT EXISTS "idx_event_impacts_relationship_id" ON "event_impacts"("relationship_id");

CREATE INDEX IF NOT EXISTS "idx_event_impacts_analysis_id" ON "event_impacts"("analysis_id");

CREATE INDEX IF NOT EXISTS "idx_event_impacts_regulation_id" ON "event_impacts"("regulation_id");

CREATE INDEX IF NOT EXISTS "idx_event_impacts_review_id" ON "event_impacts"("review_id");

CREATE TABLE IF NOT EXISTS "regulations" (
  "regulation_id" TEXT NOT NULL,
  "authority" TEXT NOT NULL,
  "jurisdiction" TEXT NOT NULL,
  "title" TEXT NOT NULL,
  "document_number" TEXT,
  "published_at" TEXT,
  "effective_at" TEXT,
  "expires_at" TEXT,
  "status" TEXT NOT NULL,
  "supersedes_id" TEXT,
  PRIMARY KEY ("regulation_id"),
  FOREIGN KEY ("supersedes_id") REFERENCES "regulations"("regulation_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_regulations_supersedes_id" ON "regulations"("supersedes_id");

CREATE TABLE IF NOT EXISTS "response_options" (
  "response_id" TEXT NOT NULL,
  "risk_type" TEXT NOT NULL,
  "industry_id" TEXT,
  "product_id" TEXT,
  "action" TEXT NOT NULL,
  "prerequisites" TEXT,
  "constraints" TEXT,
  "case_event_id" TEXT,
  "response_basis" TEXT NOT NULL,
  PRIMARY KEY ("response_id"),
  FOREIGN KEY ("industry_id") REFERENCES "industries"("industry_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("product_id") REFERENCES "products"("product_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("case_event_id") REFERENCES "events"("event_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_response_options_industry_id" ON "response_options"("industry_id");

CREATE INDEX IF NOT EXISTS "idx_response_options_product_id" ON "response_options"("product_id");

CREATE INDEX IF NOT EXISTS "idx_response_options_case_event_id" ON "response_options"("case_event_id");

CREATE TABLE IF NOT EXISTS "sources" (
  "source_id" TEXT NOT NULL,
  "publisher" TEXT NOT NULL,
  "title" TEXT NOT NULL,
  "source_type" TEXT NOT NULL,
  "url" TEXT NOT NULL,
  "local_document_ref" TEXT,
  "published_at" TEXT,
  "retrieved_at" TEXT,
  "version" TEXT,
  "access_note" TEXT,
  "original_publisher" TEXT,
  "collection_source_id" TEXT,
  "license_note" TEXT,
  "content_hash" TEXT,
  "access_status" TEXT,
  "local_snapshot_ref" TEXT,
  PRIMARY KEY ("source_id"),
  FOREIGN KEY ("collection_source_id") REFERENCES "collection_sources"("collection_source_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_sources_collection_source_id" ON "sources"("collection_source_id");

CREATE TABLE IF NOT EXISTS "evidence" (
  "evidence_id" TEXT NOT NULL,
  "record_type" TEXT NOT NULL,
  "record_id" TEXT NOT NULL,
  "field_name" TEXT,
  "source_id" TEXT NOT NULL,
  "locator" TEXT NOT NULL,
  "excerpt" TEXT,
  "support_type" TEXT NOT NULL,
  "extraction_method" TEXT,
  "source_version_id" TEXT,
  "record_version_id" TEXT,
  "review_status" TEXT,
  "reviewed_at" TEXT,
  PRIMARY KEY ("evidence_id"),
  FOREIGN KEY ("source_id") REFERENCES "sources"("source_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_evidence_source_id" ON "evidence"("source_id");

CREATE TABLE IF NOT EXISTS "metric_definitions" (
  "metric_id" TEXT NOT NULL,
  "metric_name" TEXT NOT NULL,
  "definition" TEXT NOT NULL,
  "default_unit" TEXT NOT NULL,
  "aggregation_rule" TEXT,
  "comparison_conditions" TEXT,
  "required_dimensions" TEXT,
  "source_definition" TEXT,
  "denominator" TEXT,
  "aggregation_level" TEXT,
  PRIMARY KEY ("metric_id")
);

CREATE TABLE IF NOT EXISTS "classification_mappings" (
  "mapping_id" TEXT NOT NULL,
  "target_type" TEXT NOT NULL,
  "target_id" TEXT NOT NULL,
  "code_system" TEXT NOT NULL,
  "code_version" TEXT NOT NULL,
  "code" TEXT NOT NULL,
  "mapping_scope" TEXT,
  "source_id" TEXT NOT NULL,
  PRIMARY KEY ("mapping_id"),
  FOREIGN KEY ("source_id") REFERENCES "sources"("source_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_classification_mappings_source_id" ON "classification_mappings"("source_id");

CREATE TABLE IF NOT EXISTS "relationship_routes" (
  "link_id" TEXT NOT NULL,
  "relationship_id" TEXT NOT NULL,
  "route_id" TEXT NOT NULL,
  "product_id" TEXT,
  "route_basis" TEXT NOT NULL,
  "valid_from" TEXT,
  "valid_to" TEXT,
  PRIMARY KEY ("link_id"),
  FOREIGN KEY ("relationship_id") REFERENCES "relationships"("relationship_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("route_id") REFERENCES "routes"("route_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("product_id") REFERENCES "products"("product_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_relationship_routes_relationship_id" ON "relationship_routes"("relationship_id");

CREATE INDEX IF NOT EXISTS "idx_relationship_routes_route_id" ON "relationship_routes"("route_id");

CREATE INDEX IF NOT EXISTS "idx_relationship_routes_product_id" ON "relationship_routes"("product_id");

CREATE TABLE IF NOT EXISTS "regulation_scopes" (
  "scope_id" TEXT NOT NULL,
  "regulation_id" TEXT NOT NULL,
  "code_system" TEXT NOT NULL,
  "code_version" TEXT NOT NULL,
  "product_code" TEXT NOT NULL,
  "origin_country" TEXT,
  "destination_country" TEXT,
  "rate_value" REAL,
  "rate_unit" TEXT,
  "conditions" TEXT NOT NULL,
  "effective_from" TEXT,
  "effective_to" TEXT,
  PRIMARY KEY ("scope_id"),
  FOREIGN KEY ("regulation_id") REFERENCES "regulations"("regulation_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_regulation_scopes_regulation_id" ON "regulation_scopes"("regulation_id");

CREATE TABLE IF NOT EXISTS "evaluation_cases" (
  "case_id" TEXT NOT NULL,
  "question" TEXT NOT NULL,
  "input_ids" TEXT,
  "expected_entity_ids" TEXT,
  "required_evidence_ids" TEXT,
  "expected_findings" TEXT NOT NULL,
  "forbidden_claims" TEXT NOT NULL,
  PRIMARY KEY ("case_id")
);

CREATE TABLE IF NOT EXISTS "region_industries" (
  "region_id" TEXT NOT NULL,
  "industry_id" TEXT NOT NULL,
  "coverage_status" TEXT NOT NULL,
  "role_summary" TEXT NOT NULL,
  "is_priority" INTEGER CHECK ("is_priority" IN (0,1)),
  "evidence_refs" TEXT,
  PRIMARY KEY ("region_id", "industry_id")
);

CREATE TABLE IF NOT EXISTS "collection_sources" (
  "collection_source_id" TEXT NOT NULL,
  "publisher" TEXT NOT NULL,
  "access_method" TEXT NOT NULL,
  "endpoint_or_url" TEXT NOT NULL,
  "adapter_key" TEXT NOT NULL,
  "query_config_ref" TEXT,
  "refresh_policy" TEXT,
  "enabled" INTEGER CHECK ("enabled" IN (0,1)),
  "credentials_env_name" TEXT,
  "availability_note" TEXT,
  PRIMARY KEY ("collection_source_id")
);

CREATE TABLE IF NOT EXISTS "company_contexts" (
  "context_id" TEXT NOT NULL,
  "company_id" TEXT NOT NULL,
  "product_ids" TEXT,
  "trade_role" TEXT,
  "target_markets" TEXT,
  "known_relationship_ids" TEXT,
  "known_route_ids" TEXT,
  "constraints" TEXT,
  "input_basis" TEXT NOT NULL,
  "visibility" TEXT,
  "version" INTEGER,
  PRIMARY KEY ("context_id"),
  FOREIGN KEY ("company_id") REFERENCES "companies"("company_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_company_contexts_company_id" ON "company_contexts"("company_id");

CREATE TABLE IF NOT EXISTS "watchlists" (
  "watchlist_id" TEXT NOT NULL,
  "owner_id" TEXT,
  "target_type" TEXT NOT NULL,
  "target_id" TEXT NOT NULL,
  "filters" TEXT,
  "created_at" TEXT,
  PRIMARY KEY ("watchlist_id"),
  FOREIGN KEY ("owner_id") REFERENCES "users_roles"("user_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_watchlists_owner_id" ON "watchlists"("owner_id");

CREATE TABLE IF NOT EXISTS "alerts" (
  "alert_id" TEXT NOT NULL,
  "event_id" TEXT,
  "regulation_id" TEXT,
  "watchlist_id" TEXT NOT NULL,
  "priority_reason" TEXT,
  "read_at" TEXT,
  "dismissed_at" TEXT,
  "snoozed_until" TEXT,
  "dedupe_key" TEXT NOT NULL,
  "expires_at" TEXT,
  PRIMARY KEY ("alert_id"),
  FOREIGN KEY ("event_id") REFERENCES "events"("event_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("regulation_id") REFERENCES "regulations"("regulation_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("watchlist_id") REFERENCES "watchlists"("watchlist_id") DEFERRABLE INITIALLY DEFERRED,
  UNIQUE(dedupe_key)
);

CREATE INDEX IF NOT EXISTS "idx_alerts_event_id" ON "alerts"("event_id");

CREATE INDEX IF NOT EXISTS "idx_alerts_regulation_id" ON "alerts"("regulation_id");

CREATE INDEX IF NOT EXISTS "idx_alerts_watchlist_id" ON "alerts"("watchlist_id");

CREATE TABLE IF NOT EXISTS "analysis_runs" (
  "analysis_id" TEXT NOT NULL,
  "case_ref" TEXT,
  "context_version" INTEGER,
  "input_record_versions" TEXT,
  "source_versions" TEXT,
  "model_ref" TEXT,
  "prompt_version" TEXT,
  "schema_version" TEXT,
  "status" TEXT NOT NULL,
  "result" TEXT,
  "created_at" TEXT NOT NULL,
  "error" TEXT,
  PRIMARY KEY ("analysis_id")
);

CREATE TABLE IF NOT EXISTS "review_history" (
  "review_id" TEXT NOT NULL,
  "analysis_id" TEXT NOT NULL,
  "report_version" INTEGER,
  "reviewer_id" TEXT,
  "decision" TEXT NOT NULL,
  "edited_content" TEXT,
  "reason" TEXT,
  "reviewed_at" TEXT NOT NULL,
  PRIMARY KEY ("review_id"),
  FOREIGN KEY ("analysis_id") REFERENCES "analysis_runs"("analysis_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("reviewer_id") REFERENCES "users_roles"("user_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_review_history_analysis_id" ON "review_history"("analysis_id");

CREATE INDEX IF NOT EXISTS "idx_review_history_reviewer_id" ON "review_history"("reviewer_id");

CREATE TABLE IF NOT EXISTS "reports" (
  "report_id" TEXT NOT NULL,
  "company_id" TEXT NOT NULL,
  "analysis_id" TEXT NOT NULL,
  "version" INTEGER NOT NULL,
  "content" TEXT NOT NULL,
  "evidence_refs" TEXT,
  "review_id" TEXT,
  "status" TEXT NOT NULL,
  "export_file_ref" TEXT,
  "created_at" TEXT NOT NULL,
  PRIMARY KEY ("report_id"),
  FOREIGN KEY ("company_id") REFERENCES "companies"("company_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("analysis_id") REFERENCES "analysis_runs"("analysis_id") DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY ("review_id") REFERENCES "review_history"("review_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_reports_company_id" ON "reports"("company_id");

CREATE INDEX IF NOT EXISTS "idx_reports_analysis_id" ON "reports"("analysis_id");

CREATE INDEX IF NOT EXISTS "idx_reports_review_id" ON "reports"("review_id");

CREATE TABLE IF NOT EXISTS "ingestion_runs" (
  "run_id" TEXT NOT NULL,
  "collection_source_id" TEXT,
  "started_at" TEXT NOT NULL,
  "finished_at" TEXT,
  "cursor" TEXT,
  "status" TEXT NOT NULL,
  "new_count" INTEGER CHECK ("new_count" >= 0),
  "updated_count" INTEGER CHECK ("updated_count" >= 0),
  "rejected_count" INTEGER CHECK ("rejected_count" >= 0),
  "error_ref" TEXT,
  PRIMARY KEY ("run_id"),
  FOREIGN KEY ("collection_source_id") REFERENCES "collection_sources"("collection_source_id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "idx_ingestion_runs_collection_source_id" ON "ingestion_runs"("collection_source_id");

CREATE TABLE IF NOT EXISTS "record_versions" (
  "record_type" TEXT NOT NULL,
  "record_id" TEXT NOT NULL,
  "version" INTEGER NOT NULL,
  "valid_from" TEXT,
  "valid_to" TEXT,
  "recorded_at" TEXT NOT NULL,
  "source_version" TEXT,
  "change_type" TEXT NOT NULL,
  "changed_by" TEXT,
  PRIMARY KEY ("record_type", "record_id", "version")
);

CREATE TABLE IF NOT EXISTS "users_roles" (
  "user_id" TEXT NOT NULL,
  "role" TEXT NOT NULL,
  "organization_scope" TEXT,
  "active" INTEGER NOT NULL CHECK ("active" IN (0,1)),
  PRIMARY KEY ("user_id")
);

CREATE VIEW IF NOT EXISTS object_registry AS
SELECT 'regions' AS object_type, CAST("region_id" AS TEXT) AS object_id FROM "regions"
UNION ALL
SELECT 'region_memberships' AS object_type, CAST("membership_id" AS TEXT) AS object_id FROM "region_memberships"
UNION ALL
SELECT 'industries' AS object_type, CAST("industry_id" AS TEXT) AS object_id FROM "industries"
UNION ALL
SELECT 'companies' AS object_type, CAST("company_id" AS TEXT) AS object_id FROM "companies"
UNION ALL
SELECT 'facilities' AS object_type, CAST("facility_id" AS TEXT) AS object_id FROM "facilities"
UNION ALL
SELECT 'products' AS object_type, CAST("product_id" AS TEXT) AS object_id FROM "products"
UNION ALL
SELECT 'activities' AS object_type, CAST("activity_id" AS TEXT) AS object_id FROM "activities"
UNION ALL
SELECT 'statistics' AS object_type, CAST("observation_id" AS TEXT) AS object_id FROM "statistics"
UNION ALL
SELECT 'projects' AS object_type, CAST("project_id" AS TEXT) AS object_id FROM "projects"
UNION ALL
SELECT 'relationships' AS object_type, CAST("relationship_id" AS TEXT) AS object_id FROM "relationships"
UNION ALL
SELECT 'routes' AS object_type, CAST("route_id" AS TEXT) AS object_id FROM "routes"
UNION ALL
SELECT 'route_segments' AS object_type, CAST("segment_id" AS TEXT) AS object_id FROM "route_segments"
UNION ALL
SELECT 'risk_profiles' AS object_type, CAST("risk_profile_id" AS TEXT) AS object_id FROM "risk_profiles"
UNION ALL
SELECT 'events' AS object_type, CAST("event_id" AS TEXT) AS object_id FROM "events"
UNION ALL
SELECT 'event_impacts' AS object_type, CAST("impact_id" AS TEXT) AS object_id FROM "event_impacts"
UNION ALL
SELECT 'regulations' AS object_type, CAST("regulation_id" AS TEXT) AS object_id FROM "regulations"
UNION ALL
SELECT 'response_options' AS object_type, CAST("response_id" AS TEXT) AS object_id FROM "response_options"
UNION ALL
SELECT 'sources' AS object_type, CAST("source_id" AS TEXT) AS object_id FROM "sources"
UNION ALL
SELECT 'evidence' AS object_type, CAST("evidence_id" AS TEXT) AS object_id FROM "evidence"
UNION ALL
SELECT 'metric_definitions' AS object_type, CAST("metric_id" AS TEXT) AS object_id FROM "metric_definitions"
UNION ALL
SELECT 'classification_mappings' AS object_type, CAST("mapping_id" AS TEXT) AS object_id FROM "classification_mappings"
UNION ALL
SELECT 'relationship_routes' AS object_type, CAST("link_id" AS TEXT) AS object_id FROM "relationship_routes"
UNION ALL
SELECT 'regulation_scopes' AS object_type, CAST("scope_id" AS TEXT) AS object_id FROM "regulation_scopes"
UNION ALL
SELECT 'evaluation_cases' AS object_type, CAST("case_id" AS TEXT) AS object_id FROM "evaluation_cases"
UNION ALL
SELECT 'collection_sources' AS object_type, CAST("collection_source_id" AS TEXT) AS object_id FROM "collection_sources"
UNION ALL
SELECT 'company_contexts' AS object_type, CAST("context_id" AS TEXT) AS object_id FROM "company_contexts"
UNION ALL
SELECT 'watchlists' AS object_type, CAST("watchlist_id" AS TEXT) AS object_id FROM "watchlists"
UNION ALL
SELECT 'alerts' AS object_type, CAST("alert_id" AS TEXT) AS object_id FROM "alerts"
UNION ALL
SELECT 'analysis_runs' AS object_type, CAST("analysis_id" AS TEXT) AS object_id FROM "analysis_runs"
UNION ALL
SELECT 'review_history' AS object_type, CAST("review_id" AS TEXT) AS object_id FROM "review_history"
UNION ALL
SELECT 'reports' AS object_type, CAST("report_id" AS TEXT) AS object_id FROM "reports"
UNION ALL
SELECT 'ingestion_runs' AS object_type, CAST("run_id" AS TEXT) AS object_id FROM "ingestion_runs"
UNION ALL
SELECT 'users_roles' AS object_type, CAST("user_id" AS TEXT) AS object_id FROM "users_roles";
