#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import io

# Force UTF-8 encoding for stdout on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def fmt_tokens(tokens):
    """Formate les tokens : 1200 → 1.2k"""
    if tokens >= 1000:
        return f"{tokens/1000:.1f}k"
    return str(tokens)


def fmt_model(name):
    """Abrège le nom du modèle : 'Claude Sonnet 4.5' → 'Sonnet'"""
    for keyword in ('Opus', 'Sonnet', 'Haiku'):
        if keyword in name:
            return keyword
    return name.split()[-1] if name else '?'


try:
    data = json.load(sys.stdin)
    model = fmt_model(data.get('model', {}).get('display_name', '?'))

    ctx = data.get('context_window', {})
    pct = int(ctx.get('used_percentage', 0) or 0)
    ctx_size = ctx.get('context_window_size', 0) or 0
    tokens_in = ctx.get('total_input_tokens', 0) or 0
    tokens_out = ctx.get('total_output_tokens', 0) or 0
    total = tokens_in + tokens_out

    usage = ctx.get('current_usage', {}) or {}
    cache_read = usage.get('cache_read_input_tokens', 0) or 0
    cache_write = usage.get('cache_creation_input_tokens', 0) or 0

    cost = data.get('cost', {}).get('total_cost_usd', 0) or 0
    duration_ms = data.get('cost', {}).get('total_duration_ms', 0) or 0
    mins = duration_ms // 60000
    secs = (duration_ms % 60000) // 1000

    # Barre de progression compacte (10 caractères)
    filled = pct * 10 // 100
    bar = '█' * filled + '░' * (10 - filled)

    status = f"🤖 {model} {bar} {pct}% │ {fmt_tokens(total)}/{fmt_tokens(ctx_size)}"

    if cache_read > 0 or cache_write > 0:
        status += f" │ ⚡{fmt_tokens(cache_read)}R"

    status += f" │ ${cost:.2f} │ ⏱{mins}m{secs:02d}s"

    print(status)
except Exception as e:
    print(f"⚠ {e}")
