-- Full record snapshots supplement the public record_versions metadata.
CREATE TABLE IF NOT EXISTS _record_snapshots (
    record_type TEXT NOT NULL,
    record_id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK(version >= 1),
    snapshot TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    PRIMARY KEY (record_type, record_id, version)
);
CREATE INDEX IF NOT EXISTS idx_record_snapshots_time ON _record_snapshots(recorded_at);
