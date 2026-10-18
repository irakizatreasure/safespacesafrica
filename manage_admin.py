"""Offline administrator provisioning. Run from the application directory."""
import argparse
import getpass
import os
from app import DEFAULT_DB, db_connect, hash_password, utcnow

ROLES = ["CEO", "President", "content_editor", "subject_matter_reviewer", "support_worker", "safeguarding_officer", "technical_administrator", "analytics_user"]


def main():
    parser = argparse.ArgumentParser(description="Provision an administrator without exposing passwords in shell history.")
    parser.add_argument("email")
    parser.add_argument("--role", choices=ROLES, default="content_editor")
    parser.add_argument("--db", default=os.environ.get("SISP_DB_PATH", str(DEFAULT_DB)))
    args = parser.parse_args()
    email = args.email.strip().lower()
    password = getpass.getpass("New password (minimum 14 characters): ")
    confirm = getpass.getpass("Confirm password: ")
    if len(password) < 14 or password != confirm:
        raise SystemExit("Password must be at least 14 characters and both entries must match.")
    with db_connect(args.db) as conn:
        conn.execute("INSERT INTO admins(email,password_hash,role,created_at) VALUES(?,?,?,?)", (email, hash_password(password), args.role, utcnow()))
    print(f"Created {args.role} account for {email}.")


if __name__ == "__main__":
    main()
