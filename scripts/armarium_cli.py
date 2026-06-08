#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config import DECISION_LABELS, PHASE_LABELS, get_settings
from backend.app.database import init_db
from backend.app.services import git_service, project_service, review_service
from backend.app.services.filesystem_service import ValidationError


def cmd_list(args: argparse.Namespace) -> int:
    settings = get_settings()
    for work in project_service.list_works(settings):
        print(f"{work.work_id}\t{work.name}\t{PHASE_LABELS.get(work.phase, work.phase)}")
    return 0


def cmd_create_work(args: argparse.Namespace) -> int:
    settings = get_settings()
    work = project_service.create_work(
        settings,
        name=args.name,
        work_id=args.work_id,
        idea=args.idea,
        hard_requirements=args.hard_requirements or "",
        template_id=args.template,
        personas=args.personas,
    )
    print(f"created {work.work_id}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    settings = get_settings()
    work = project_service.require_work(settings, args.work_id)
    print(f"Name: {work.name}")
    print(f"Work ID: {work.work_id}")
    print(f"Phase: {PHASE_LABELS.get(work.phase, work.phase)}")
    print(f"Repo: {work.repo_path}")
    print(f"Skriptorium: {work.scriptorium_path}")
    print(f"Personen: {', '.join(work.personas)}")
    return 0


def cmd_set_phase(args: argparse.Namespace) -> int:
    settings = get_settings()
    work = project_service.set_phase(settings, args.work_id, args.phase)
    print(f"{work.work_id}: {work.phase}")
    return 0


def cmd_add_review(args: argparse.Namespace) -> int:
    settings = get_settings()
    review = review_service.add_review(settings, args.work_id, args.decision, args.comment)
    print(f"review {review.id}: {DECISION_LABELS.get(review.decision, review.decision)}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    settings = get_settings()
    work = project_service.require_work(settings, args.work_id)
    last = review_service.last_review(settings, work.work_id)
    print(f"Work: {work.name} ({work.work_id})")
    print(f"Phase: {PHASE_LABELS.get(work.phase, work.phase)}")
    print(f"Git: {git_service.status(Path(work.repo_path))}")
    print(f"Last review: {DECISION_LABELS.get(last.decision, last.decision) if last else 'none'}")
    print(f"Next action: {project_service.next_action_for_phase(work.phase, last.decision if last else None)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ArmariumLabs local CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list")
    list_parser.set_defaults(func=cmd_list)

    create = sub.add_parser("create-work")
    create.add_argument("--name", required=True)
    create.add_argument("--work-id")
    create.add_argument("--idea", required=True)
    create.add_argument("--hard-requirements")
    create.add_argument("--template", default="einfaches-werk")
    create.add_argument("--personas", nargs="+", default=["schatzmeister"])
    create.set_defaults(func=cmd_create_work)

    show = sub.add_parser("show")
    show.add_argument("work_id")
    show.set_defaults(func=cmd_show)

    phase = sub.add_parser("set-phase")
    phase.add_argument("work_id")
    phase.add_argument("phase")
    phase.set_defaults(func=cmd_set_phase)

    review = sub.add_parser("add-review")
    review.add_argument("work_id")
    review.add_argument("--decision", required=True)
    review.add_argument("--comment", required=True)
    review.set_defaults(func=cmd_add_review)

    status = sub.add_parser("status")
    status.add_argument("work_id")
    status.set_defaults(func=cmd_status)
    return parser


def main() -> int:
    init_db(get_settings().db_path)
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
