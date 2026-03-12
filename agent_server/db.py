from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import psycopg


def _dsn() -> str:
    return os.environ["POSTGRES_URL"]


def init_db() -> None:
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    payload JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                    status TEXT NOT NULL,
                    payload JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )


def save_task(task_id: str, payload: Dict[str, Any]) -> None:
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks (id, payload, created_at, updated_at)
                VALUES (%s, %s::jsonb, NOW(), NOW())
                ON CONFLICT (id)
                DO UPDATE SET payload = EXCLUDED.payload, updated_at = NOW();
                """,
                (task_id, json.dumps(payload)),
            )


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT payload FROM tasks WHERE id = %s;", (task_id,))
            row = cur.fetchone()
    return row[0] if row else None


def list_tasks() -> List[Dict[str, Any]]:
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT payload FROM tasks ORDER BY created_at DESC;")
            rows = cur.fetchall()
    return [row[0] for row in rows]


def save_run(run_id: str, task_id: str, status: str, payload: Dict[str, Any]) -> None:
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO runs (id, task_id, status, payload, created_at, updated_at)
                VALUES (%s, %s, %s, %s::jsonb, NOW(), NOW())
                ON CONFLICT (id)
                DO UPDATE SET
                    status = EXCLUDED.status,
                    payload = EXCLUDED.payload,
                    updated_at = NOW();
                """,
                (run_id, task_id, status, json.dumps(payload)),
            )


def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT payload FROM runs WHERE id = %s;", (run_id,))
            row = cur.fetchone()
    return row[0] if row else None


def list_runs(task_id: str) -> List[Dict[str, Any]]:
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT payload FROM runs WHERE task_id = %s ORDER BY created_at DESC;", (task_id,))
            rows = cur.fetchall()
    return [row[0] for row in rows]
