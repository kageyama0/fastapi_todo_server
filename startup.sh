#!/usr/bin/env bash
python app/db.py
uvicorn app.main:app --host 0.0.0.0 --port 80
