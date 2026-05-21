#!/usr/bin/env python3
"""
Spike de Instagram question sticker via instagrapi/private API.

Nao use em conta principal ate validar em conta secundaria.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.types import StorySticker


ROOT = Path(__file__).resolve().parent
SESSION_FILE = ROOT / "session.json"


def client() -> Client:
    load_dotenv(ROOT / ".env")
    cl = Client()
    if SESSION_FILE.exists():
        cl.load_settings(SESSION_FILE)
    return cl


def login() -> None:
    username = os.environ.get("IG_USERNAME")
    password = os.environ.get("IG_PASSWORD")
    if not username or not password:
        raise SystemExit("Defina IG_USERNAME e IG_PASSWORD em .env")

    cl = client()
    cl.login(username, password)
    cl.dump_settings(SESSION_FILE)
    print(f"login_ok user_id={cl.user_id}")


def tray() -> None:
    cl = client()
    username = os.environ.get("IG_USERNAME")
    password = os.environ.get("IG_PASSWORD")
    if username and password:
        cl.login(username, password)
    data = cl.sticker_tray()
    out = ROOT / "sticker_tray.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(out)


def question_sticker(question: str, variant: str) -> StorySticker:
    base = {
        "tap_state": 0,
        "question": question,
        "text": question,
        "question_type": "text",
        "viewer_can_interact": True,
        "background_color": "#FFFFFF",
        "text_color": "#000000",
    }

    variants = {
        # Nome observado em respostas de stories: story_questions[].question_sticker
        "question_sticker": {
            "id": "question_sticker",
            "type": "question",
            "tap_state_str_id": "question_sticker",
            **base,
        },
        # Algumas surfaces antigas usam plural.
        "questions_sticker": {
            "id": "questions_sticker",
            "type": "question",
            "tap_state_str_id": "questions_sticker",
            **base,
        },
        # Variante com type mais explicito.
        "story_question": {
            "id": "question_sticker",
            "type": "story_question",
            "tap_state_str_id": "question_sticker",
            **base,
        },
        # Testa se a API aceita objeto aninhado como nas respostas.
        "raw_story_questions": {
            "id": "question_sticker",
            "type": "question",
            "tap_state_str_id": "question_sticker",
            "question_sticker": base,
        },
    }
    if variant not in variants:
        raise SystemExit(f"Variante invalida: {variant}. Use: {', '.join(variants)}")

    return StorySticker(
        x=0.5,
        y=0.62,
        z=1000005,
        width=0.82,
        height=0.22,
        rotation=0.0,
        type=variants[variant]["type"],
        id=variants[variant]["id"],
        extra={k: v for k, v in variants[variant].items() if k not in {"id", "type"}},
    )


def post(image: str, question: str, variant: str) -> None:
    username = os.environ.get("IG_USERNAME")
    password = os.environ.get("IG_PASSWORD")
    if not username or not password:
        raise SystemExit("Defina IG_USERNAME e IG_PASSWORD em .env")

    cl = client()
    cl.login(username, password)

    sticker = question_sticker(question, variant)
    media = cl.photo_upload_to_story(Path(image), stickers=[sticker])
    print(json.dumps({
        "ok": True,
        "variant": variant,
        "media_pk": getattr(media, "pk", None),
        "media_id": getattr(media, "id", None),
    }, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login")
    sub.add_parser("tray")
    p_post = sub.add_parser("post")
    p_post.add_argument("--image", required=True)
    p_post.add_argument("--question", required=True)
    p_post.add_argument(
        "--variant",
        default="question_sticker",
        choices=["question_sticker", "questions_sticker", "story_question", "raw_story_questions"],
    )
    args = parser.parse_args()

    if args.cmd == "login":
        login()
    elif args.cmd == "tray":
        tray()
    elif args.cmd == "post":
        post(args.image, args.question, args.variant)


if __name__ == "__main__":
    main()
