"""
Idempotently ensure a default user exists.

This script is safe to run repeatedly. It will:
 - look up by email first; update flags/username when --force-update
 - if not found by email, check for an existing row with the same ID
   and skip insert to avoid PK conflicts
 - otherwise insert; conflicts on (id) are ignored
"""

from __future__ import annotations

import os
import sys
import uuid
import asyncio
import argparse
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


def getenv_bool(key: str, default: bool) -> bool:
    v = os.getenv(key)
    if v is None:
        return default
    return v.lower() in {"1", "true", "yes", "on"}


def make_password_hash() -> str:
    env_hash = os.getenv("DEFAULT_USER_PASSWORD_HASH")
    if env_hash:
        return env_hash

    password = os.getenv("DEFAULT_USER_PASSWORD", "changeme")
    try:
        import bcrypt  # type: ignore

        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    except Exception:
        # fallback, never used for real auth
        return "$2b$12$abcdefghijklmnopqrstuv/1234567890abcdefghiJK"


async def ensure_default_user(
    database_url: str,
    user_id: Optional[str],
    username: str,
    email: str,
    is_active: bool,
    is_verified: bool,
    force_update: bool,
    verbose: bool,
) -> None:
    engine = create_async_engine(database_url, echo=False, future=True)
    password_hash = make_password_hash()

    if not user_id:
        user_id = str(uuid.uuid4())

    if verbose:
        print("[ensure_default_user] start", file=sys.stderr)
        print(f"  email={email} username={username} id={user_id}", file=sys.stderr)

    async with engine.begin() as conn:
        # Check by email
        row_by_email = (
            await conn.execute(
                text(
                    "SELECT id, username, is_active, is_verified FROM users WHERE email = :email"
                ),
                {"email": email},
            )
        ).mappings().first()

        # Check by id (to avoid PK conflicts when a seed migration already inserted a row)
        row_by_id = (
            await conn.execute(
                text("SELECT id, email FROM users WHERE id = :id"),
                {"id": user_id},
            )
        ).mappings().first()

        if row_by_email:
            if verbose:
                print(
                    f"[ensure_default_user] found existing user by email id={row_by_email['id']}",
                    file=sys.stderr,
                )
            if force_update:
                await conn.execute(
                    text(
                        """
                        UPDATE users
                           SET username = :username,
                               is_active = :is_active,
                               is_verified = :is_verified
                         WHERE email = :email
                        """
                    ),
                    {
                        "username": username,
                        "is_active": is_active,
                        "is_verified": is_verified,
                        "email": email,
                    },
                )
                if verbose:
                    print("[ensure_default_user] user updated (force_update=true)", file=sys.stderr)
            else:
                if verbose:
                    print("[ensure_default_user] no changes (force_update=false)", file=sys.stderr)
            await engine.dispose()
            return

        if row_by_id:
            if verbose:
                print(
                    f"[ensure_default_user] found existing user by id={row_by_id['id']}; skip insert",
                    file=sys.stderr,
                )
            await engine.dispose()
            return

        # Insert; ignore id conflict if any
        await conn.execute(
            text(
                """
                INSERT INTO users (id, username, email, password_hash, is_active, is_verified)
                VALUES (:id, :username, :email, :password_hash, :is_active, :is_verified)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": user_id,
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "is_active": is_active,
                "is_verified": is_verified,
            },
        )
        if verbose:
            print(f"[ensure_default_user] user inserted id={user_id}", file=sys.stderr)

    await engine.dispose()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Ensure default user exists (idempotent).")
    parser.add_argument("--force-update", action="store_true", help="Update fields when user exists")
    parser.add_argument("--verbose", action="store_true", help="Verbose logs")
    args = parser.parse_args(argv)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set", file=sys.stderr)
        return 2

    user_id = os.getenv("DEFAULT_USER_ID")
    username = os.getenv("DEFAULT_USER_USERNAME", "default_user")
    email = os.getenv("DEFAULT_USER_EMAIL", "default@example.com")
    is_active = getenv_bool("DEFAULT_USER_IS_ACTIVE", True)
    is_verified = getenv_bool("DEFAULT_USER_IS_VERIFIED", True)

    try:
        asyncio.run(
            ensure_default_user(
                database_url=database_url,
                user_id=user_id,
                username=username,
                email=email,
                is_active=is_active,
                is_verified=is_verified,
                force_update=args.force_update,
                verbose=args.verbose,
            )
        )
        return 0
    except Exception as e:
        print(f"[ensure_default_user] ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

