#!/usr/bin/env bash
# Aseguramos que las tablas existan y lanzamos la app
uvicorn backend.main:app --host 0.0.0.0 --port 10000
