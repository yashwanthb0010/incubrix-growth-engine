"""
IncuBrix Persistence Module
SQLite-backed storage for inputs, generation runs, assets, validations, and telemetry.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


DB_DEFAULT_PATH = "data/incubrix.db"


class PersistenceManager:
    def __init__(self, db_path: str = DB_DEFAULT_PATH):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Inputs table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS inputs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                word_count INTEGER NOT NULL,
                source_url TEXT,
                raw_text TEXT NOT NULL,
                metadata_json TEXT,
                created_at TEXT NOT NULL
            );
            """)

            # Generation runs table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS generation_runs (
                run_id TEXT PRIMARY KEY,
                input_id TEXT,
                mode TEXT NOT NULL,
                requested_count INTEGER NOT NULL,
                successful_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                runtime_seconds REAL DEFAULT 0.0,
                model_name TEXT NOT NULL,
                is_demo_mode INTEGER DEFAULT 0,
                retry_count INTEGER DEFAULT 0,
                token_usage INTEGER DEFAULT 0,
                estimated_ai_cost REAL DEFAULT 0.0,
                estimated_render_cost REAL DEFAULT 0.0,
                status TEXT NOT NULL,
                FOREIGN KEY (input_id) REFERENCES inputs(id)
            );
            """)

            # Assets table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                asset_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                format_type TEXT NOT NULL,
                content_pillar TEXT NOT NULL,
                target_audience TEXT NOT NULL,
                campaign_objective TEXT NOT NULL,
                hook TEXT NOT NULL,
                caption TEXT NOT NULL,
                hashtags TEXT NOT NULL,
                cta TEXT NOT NULL,
                destination_url TEXT NOT NULL,
                utm_url TEXT NOT NULL,
                target_metric TEXT NOT NULL,
                metric_measurement_method TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                timezone TEXT NOT NULL,
                creative_file_path TEXT NOT NULL,
                editable_source_path TEXT NOT NULL,
                product_claim_status TEXT NOT NULL,
                rights_review_status TEXT NOT NULL,
                quality_status TEXT NOT NULL,
                publication_status TEXT NOT NULL,
                source_reference TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES generation_runs(run_id)
            );
            """)

            # Validation checks table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id TEXT NOT NULL,
                check_name TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
            );
            """)

            # Audit logs table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                sample_size INTEGER NOT NULL,
                pass_count INTEGER NOT NULL,
                fail_count INTEGER NOT NULL,
                pass_rate REAL NOT NULL,
                report_path TEXT,
                created_at TEXT NOT NULL
            );
            """)

            conn.commit()

    def save_input(self, input_id: str, title: str, word_count: int, raw_text: str, source_url: Optional[str] = None, metadata: Optional[dict] = None) -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO inputs (id, title, word_count, source_url, raw_text, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                input_id,
                title,
                word_count,
                source_url,
                raw_text,
                json.dumps(metadata or {}),
                datetime.now().isoformat()
            ))
            conn.commit()
        return input_id

    def create_generation_run(
        self,
        run_id: str,
        input_id: str,
        mode: str,
        requested_count: int,
        model_name: str,
        is_demo_mode: bool = False
    ):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO generation_runs (
                run_id, input_id, mode, requested_count, successful_count, failed_count,
                start_time, model_name, is_demo_mode, status
            ) VALUES (?, ?, ?, ?, 0, 0, ?, ?, ?, 'IN_PROGRESS');
            """, (
                run_id,
                input_id,
                mode,
                requested_count,
                datetime.now().isoformat(),
                model_name,
                1 if is_demo_mode else 0
            ))
            conn.commit()

    def update_generation_run(
        self,
        run_id: str,
        successful_count: int,
        failed_count: int,
        runtime_seconds: float,
        status: str,
        retry_count: int = 0,
        token_usage: int = 0,
        estimated_ai_cost: float = 0.0,
        estimated_render_cost: float = 0.0
    ):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE generation_runs
            SET successful_count = ?,
                failed_count = ?,
                end_time = ?,
                runtime_seconds = ?,
                retry_count = ?,
                token_usage = ?,
                estimated_ai_cost = ?,
                estimated_render_cost = ?,
                status = ?
            WHERE run_id = ?;
            """, (
                successful_count,
                failed_count,
                datetime.now().isoformat(),
                runtime_seconds,
                retry_count,
                token_usage,
                estimated_ai_cost,
                estimated_render_cost,
                status,
                run_id
            ))
            conn.commit()

    def save_asset(self, asset_dict: Dict[str, Any]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO assets (
                asset_id, run_id, platform, format_type, content_pillar, target_audience,
                campaign_objective, hook, caption, hashtags, cta, destination_url, utm_url,
                target_metric, metric_measurement_method, scheduled_time, timezone,
                creative_file_path, editable_source_path, product_claim_status,
                rights_review_status, quality_status, publication_status, source_reference,
                content_hash, version, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                asset_dict["asset_id"],
                asset_dict["run_id"],
                asset_dict["platform"],
                asset_dict["format_type"],
                asset_dict["content_pillar"],
                asset_dict["target_audience"],
                asset_dict["campaign_objective"],
                asset_dict["hook"],
                asset_dict["caption"],
                asset_dict["hashtags"] if isinstance(asset_dict["hashtags"], str) else " ".join(asset_dict["hashtags"]),
                asset_dict["cta"],
                asset_dict["destination_url"],
                asset_dict["utm_url"],
                asset_dict["target_metric"],
                asset_dict["metric_measurement_method"],
                asset_dict["scheduled_time"],
                asset_dict["timezone"],
                asset_dict["creative_file_path"],
                asset_dict["editable_source_path"],
                asset_dict["product_claim_status"],
                asset_dict["rights_review_status"],
                asset_dict["quality_status"],
                asset_dict.get("publication_status", "DRAFT"),
                asset_dict["source_reference"],
                asset_dict["content_hash"],
                asset_dict.get("version", 1),
                datetime.now().isoformat()
            ))
            conn.commit()

    def save_validation_results(self, asset_id: str, results: List[Dict[str, Any]]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM validation_results WHERE asset_id = ?", (asset_id,))
            for r in results:
                cursor.execute("""
                INSERT INTO validation_results (asset_id, check_name, status, details, created_at)
                VALUES (?, ?, ?, ?, ?);
                """, (
                    asset_id,
                    r["check_name"],
                    r["status"],
                    r.get("details", ""),
                    datetime.now().isoformat()
                ))
            conn.commit()

    def update_asset_status(self, asset_id: str, publication_status: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE assets SET publication_status = ? WHERE asset_id = ?;
            """, (publication_status, asset_id))
            conn.commit()

    def get_all_existing_texts(self) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hook, caption FROM assets;")
            rows = cursor.fetchall()
            return [f"{r['hook']} {r['caption']}" for r in rows]

    def list_assets(self, run_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if run_id:
                cursor.execute("SELECT * FROM assets WHERE run_id = ? ORDER BY asset_id ASC;", (run_id,))
            else:
                cursor.execute("SELECT * FROM assets ORDER BY created_at DESC;")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM assets WHERE asset_id = ?;", (asset_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_asset_validations(self, asset_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM validation_results WHERE asset_id = ?;", (asset_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM assets;")
            total_assets = cursor.fetchone()["total"]

            cursor.execute("SELECT platform, COUNT(*) as count FROM assets GROUP BY platform;")
            by_platform = {r["platform"]: r["count"] for r in cursor.fetchall()}

            cursor.execute("SELECT format_type, COUNT(*) as count FROM assets GROUP BY format_type;")
            by_format = {r["format_type"]: r["count"] for r in cursor.fetchall()}

            cursor.execute("SELECT publication_status, COUNT(*) as count FROM assets GROUP BY publication_status;")
            by_status = {r["publication_status"]: r["count"] for r in cursor.fetchall()}

            cursor.execute("SELECT quality_status, COUNT(*) as count FROM assets GROUP BY quality_status;")
            by_quality = {r["quality_status"]: r["count"] for r in cursor.fetchall()}

            cursor.execute("SELECT * FROM generation_runs ORDER BY start_time DESC LIMIT 5;")
            recent_runs = [dict(r) for r in cursor.fetchall()]

            return {
                "total_assets": total_assets,
                "by_platform": by_platform,
                "by_format": by_format,
                "by_status": by_status,
                "by_quality": by_quality,
                "recent_runs": recent_runs
            }

    def save_audit_log(self, run_id: str, sample_size: int, pass_count: int, fail_count: int, pass_rate: float, report_path: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO audit_logs (run_id, sample_size, pass_count, fail_count, pass_rate, report_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                run_id, sample_size, pass_count, fail_count, pass_rate, report_path, datetime.now().isoformat()
            ))
            conn.commit()
