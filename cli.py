#!/usr/bin/env python3
import curses
import base64
import json
import os
import requests

def menu(stdscr, title, options):
    curses.curs_set(0)
    idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, title)
        for i, opt in enumerate(options):
            mode = curses.A_REVERSE if i == idx else curses.A_NORMAL
            stdscr.addstr(i + 2, 0, opt, mode)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')) and idx > 0:
            idx -= 1
        elif key in (curses.KEY_DOWN, ord('j')) and idx < len(options) - 1:
            idx += 1
        elif key in (curses.KEY_ENTER, 10, 13):
            return idx

def prompt(stdscr, text):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, text)
    stdscr.refresh()
    val = stdscr.getstr(1, 0).decode()
    curses.noecho()
    return val

def run(stdscr):
    # Input source selection
    src_idx = menu(stdscr, "Select input source", ["R2 Bucket", "Local File", "Website URL"])
    if src_idx == 0:
        bucket = prompt(stdscr, "R2 bucket name:")
        key = prompt(stdscr, "Object key:")
        input_data = {"type": "r2", "bucket": bucket, "key": key}
    elif src_idx == 1:
        path = prompt(stdscr, "Local file path:")
        with open(path, "rb") as f:
            content = base64.b64encode(f.read()).decode()
        input_data = {"type": "local", "filename": os.path.basename(path), "content": content}
    else:
        url = prompt(stdscr, "Website URL:")
        input_data = {"type": "url", "url": url}

    # Processing options
    emb_idx = menu(stdscr, "Generate embeddings?", ["No", "Yes"])
    rag_idx = menu(stdscr, "RAG format", ["none", "json", "markdown"])
    sum_idx = menu(stdscr, "Add AI summary + RAG?", ["No", "Yes"])
    process_data = {
        "embeddings": emb_idx == 1,
        "rag_format": None if rag_idx == 0 else ["json", "markdown"][rag_idx - 1],
        "summary": sum_idx == 1,
    }

    # Output options
    bucket_out = prompt(stdscr, "Destination R2 bucket:")
    key_out = prompt(stdscr, "Output key prefix:")
    local_idx = menu(stdscr, "Also export to current path?", ["No", "Yes"])
    worker_url = prompt(stdscr, "Worker URL (e.g., http://localhost:8787/process):")

    payload = {
        "input": input_data,
        "process": process_data,
        "output": {"bucket": bucket_out, "key": key_out, "local": local_idx == 1},
    }

    stdscr.clear()
    stdscr.addstr(0, 0, "Processing...")
    stdscr.refresh()
    try:
        res = requests.post(worker_url, json=payload, timeout=60)
    except Exception as exc:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Request failed: {exc}")
        stdscr.getch()
        return

    stdscr.clear()
    if res.ok:
        result = res.json()
        if payload["output"]["local"]:
            with open("extracted.txt", "w") as f:
                f.write(result.get("extracted_text", ""))
            if result.get("embedding") is not None:
                with open("embedding.json", "w") as f:
                    json.dump(result["embedding"], f)
            if result.get("rag"):
                ext = "json" if process_data["rag_format"] == "json" else "md"
                with open(f"rag.{ext}", "w") as f:
                    f.write(result["rag"])
            if result.get("summary"):
                with open("summary.txt", "w") as f:
                    f.write(result["summary"])
        stdscr.addstr(0, 0, "Done. Press any key to exit.")
    else:
        stdscr.addstr(0, 0, f"Error: {res.status_code}")
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(run)
