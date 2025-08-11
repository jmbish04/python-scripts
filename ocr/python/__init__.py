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

def process_document(payload):
    worker_url = "https://ask-my-doc.hacolby.workers.dev/"
    try:
        res = requests.post(worker_url, json=payload, timeout=60)
        res.raise_for_status()  # Raise an exception for bad status codes
        return res.json()
    except requests.exceptions.RequestException as exc:
        return {"error": str(exc)}

def run(stdscr):
    # Input source selection
    src_idx = menu(stdscr, "Select input source", ["R2 Bucket", "Local File", "Website URL", "Website URL (Browser Render)"])
    if src_idx == 0:
        bucket = prompt(stdscr, "R2 bucket name:")
        key = prompt(stdscr, "Object key:")
        input_data = {"type": "r2", "bucket": bucket, "key": key}
    elif src_idx == 1:
        path = prompt(stdscr, "Local file path:")
        with open(path, "rb") as f:
            content = base64.b64encode(f.read()).decode()
        input_data = {"type": "local", "filename": os.path.basename(path), "content": content}
    elif src_idx == 2:
        url = prompt(stdscr, "Website URL:")
        input_data = {"type": "url", "url": url}
    else:
        url = prompt(stdscr, "Website URL:")
        input_data = {"type": "url", "url": url, "browser": True}

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

    payload = {
        "input": input_data,
        "process": process_data,
        "output": {"bucket": bucket_out, "key": key_out, "local": local_idx == 1},
    }

    stdscr.clear()
    stdscr.addstr(0, 0, "Processing...")
    stdscr.refresh()

    result = process_document(payload)

    stdscr.clear()
    if "error" in result:
        stdscr.addstr(0, 0, f"Error: {result['error']}")
    else:
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
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(run)
