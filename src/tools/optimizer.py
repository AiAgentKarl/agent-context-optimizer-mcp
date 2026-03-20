"""Optimizer-Tools — Context-Window-Management für MCP-Server."""

import json
import re
from mcp.server.fastmcp import FastMCP

# Bekannte MCP-Server mit ihren Tool-Kategorien und geschätzten Token-Kosten
KNOWN_SERVERS = {
    "solana": {"category": "crypto", "tools": 11, "est_tokens": 4500, "keywords": ["blockchain", "crypto", "defi", "wallet", "token", "solana", "nft"]},
    "weather": {"category": "weather", "tools": 6, "est_tokens": 2800, "keywords": ["weather", "forecast", "temperature", "climate", "rain", "wind", "air quality"]},
    "agriculture": {"category": "data", "tools": 8, "est_tokens": 3200, "keywords": ["agriculture", "farming", "crop", "food", "fao", "harvest", "soil"]},
    "germany": {"category": "data", "tools": 10, "est_tokens": 4000, "keywords": ["germany", "deutschland", "behörde", "destatis", "bundesanzeiger"]},
    "space": {"category": "science", "tools": 8, "est_tokens": 3400, "keywords": ["space", "nasa", "asteroid", "mars", "planet", "satellite", "iss"]},
    "aviation": {"category": "transport", "tools": 7, "est_tokens": 3000, "keywords": ["flight", "airport", "airline", "aviation", "plane", "travel"]},
    "eu-company": {"category": "business", "tools": 8, "est_tokens": 3200, "keywords": ["company", "business", "firm", "register", "lei", "filing"]},
    "cybersecurity": {"category": "security", "tools": 7, "est_tokens": 3000, "keywords": ["cve", "vulnerability", "security", "exploit", "threat", "cyber"]},
    "medical": {"category": "health", "tools": 8, "est_tokens": 3400, "keywords": ["health", "disease", "who", "medical", "drug", "clinical", "trial"]},
    "memory": {"category": "infrastructure", "tools": 5, "est_tokens": 2200, "keywords": ["memory", "store", "retrieve", "persist", "remember", "knowledge"]},
    "directory": {"category": "infrastructure", "tools": 5, "est_tokens": 2200, "keywords": ["directory", "find", "service", "discover", "registry"]},
    "reputation": {"category": "infrastructure", "tools": 5, "est_tokens": 2200, "keywords": ["trust", "reputation", "score", "rate", "review", "quality"]},
    "analytics": {"category": "infrastructure", "tools": 5, "est_tokens": 2000, "keywords": ["analytics", "usage", "metrics", "track", "monitor", "stats"]},
    "x402": {"category": "payments", "tools": 5, "est_tokens": 2200, "keywords": ["payment", "pay", "money", "transaction", "invoice", "micropayment"]},
    "hub": {"category": "infrastructure", "tools": 6, "est_tokens": 2600, "keywords": ["hub", "appstore", "install", "search", "catalog", "mcp"]},
}

# Typische Aufgaben-Muster und welche Server sie brauchen
TASK_PATTERNS = {
    "crypto_analysis": {
        "patterns": ["crypto", "bitcoin", "solana", "token", "defi", "wallet", "blockchain", "nft"],
        "required_servers": ["solana"],
        "optional_servers": ["analytics"],
    },
    "weather_check": {
        "patterns": ["weather", "forecast", "temperature", "rain", "climate", "air quality"],
        "required_servers": ["weather"],
        "optional_servers": [],
    },
    "business_research": {
        "patterns": ["company", "business", "firm", "financial", "due diligence", "competitor"],
        "required_servers": ["eu-company"],
        "optional_servers": ["analytics"],
    },
    "security_audit": {
        "patterns": ["vulnerability", "cve", "security", "exploit", "threat", "hack", "breach"],
        "required_servers": ["cybersecurity"],
        "optional_servers": [],
    },
    "medical_research": {
        "patterns": ["health", "disease", "drug", "clinical", "medical", "patient", "treatment"],
        "required_servers": ["medical"],
        "optional_servers": [],
    },
    "space_science": {
        "patterns": ["space", "nasa", "asteroid", "mars", "planet", "rocket", "satellite"],
        "required_servers": ["space"],
        "optional_servers": [],
    },
    "travel_planning": {
        "patterns": ["flight", "airport", "travel", "airline", "booking", "trip"],
        "required_servers": ["aviation", "weather"],
        "optional_servers": [],
    },
    "agriculture_analysis": {
        "patterns": ["farm", "crop", "agriculture", "food", "harvest", "soil", "livestock"],
        "required_servers": ["agriculture"],
        "optional_servers": ["weather"],
    },
    "agent_development": {
        "patterns": ["build agent", "mcp server", "tool", "integrate", "api", "develop"],
        "required_servers": ["hub", "directory"],
        "optional_servers": ["memory", "analytics"],
    },
    "multi_agent": {
        "patterns": ["coordinate", "multi-agent", "collaborate", "swarm", "consensus"],
        "required_servers": ["memory", "directory"],
        "optional_servers": ["reputation", "analytics"],
    },
}


def _calculate_relevance(task: str, server_name: str, server_info: dict) -> float:
    """Relevanz eines Servers für eine Aufgabe berechnen (0.0 - 1.0)."""
    task_lower = task.lower()
    score = 0.0
    keywords = server_info.get("keywords", [])

    for keyword in keywords:
        if keyword in task_lower:
            score += 1.0 / len(keywords)

    # Bonus für exakte Kategorie-Treffer
    if server_info.get("category", "") in task_lower:
        score += 0.3

    return min(score, 1.0)


def register_optimizer_tools(mcp: FastMCP):
    """Context-Optimizer MCP-Tools registrieren."""

    @mcp.tool()
    async def analyze_task(task_description: str) -> dict:
        """Analysiere eine Aufgabe und empfehle die optimale Server-Kombination.

        Bestimmt welche MCP-Server für eine Aufgabe relevant sind,
        schätzt den Token-Verbrauch und gibt Empfehlungen zur
        Context-Optimierung.

        Args:
            task_description: Beschreibung der Aufgabe (z.B. "Check SOL token safety")
        """
        task_lower = task_description.lower()

        # Relevanz für jeden bekannten Server berechnen
        server_scores = {}
        for name, info in KNOWN_SERVERS.items():
            score = _calculate_relevance(task_description, name, info)
            if score > 0:
                server_scores[name] = {
                    "relevance": round(score, 2),
                    "est_tokens": info["est_tokens"],
                    "tools_count": info["tools"],
                    "category": info["category"],
                }

        # Task-Pattern-Matching
        matched_pattern = None
        best_match_score = 0
        for pattern_name, pattern_info in TASK_PATTERNS.items():
            match_count = sum(1 for p in pattern_info["patterns"] if p in task_lower)
            if match_count > best_match_score:
                best_match_score = match_count
                matched_pattern = pattern_name

        # Empfohlene Server zusammenstellen
        recommended = []
        if matched_pattern:
            pattern = TASK_PATTERNS[matched_pattern]
            for s in pattern["required_servers"]:
                if s in KNOWN_SERVERS:
                    recommended.append({
                        "server": s,
                        "priority": "required",
                        "est_tokens": KNOWN_SERVERS[s]["est_tokens"],
                    })
            for s in pattern["optional_servers"]:
                if s in KNOWN_SERVERS:
                    recommended.append({
                        "server": s,
                        "priority": "optional",
                        "est_tokens": KNOWN_SERVERS[s]["est_tokens"],
                    })

        # Token-Budget berechnen
        total_if_all = sum(s["est_tokens"] for s in KNOWN_SERVERS.values())
        total_recommended = sum(r["est_tokens"] for r in recommended)
        savings_pct = round((1 - total_recommended / total_if_all) * 100, 1) if total_if_all > 0 else 0

        return {
            "task": task_description,
            "matched_pattern": matched_pattern,
            "recommended_servers": recommended,
            "all_relevant_servers": server_scores,
            "token_budget": {
                "all_servers_tokens": total_if_all,
                "recommended_tokens": total_recommended,
                "savings_percent": savings_pct,
            },
            "advice": f"Lade nur die empfohlenen Server — spart {savings_pct}% Context-Tokens.",
        }

    @mcp.tool()
    async def estimate_context_usage(server_names: list[str]) -> dict:
        """Schätze den Context-Window-Verbrauch einer Server-Kombination.

        Hilft zu verstehen wie viel Context-Budget eine bestimmte
        Kombination von MCP-Servern verbraucht.

        Args:
            server_names: Liste von Server-Namen (z.B. ["solana", "weather"])
        """
        total_tokens = 0
        total_tools = 0
        details = []

        for name in server_names:
            if name in KNOWN_SERVERS:
                info = KNOWN_SERVERS[name]
                total_tokens += info["est_tokens"]
                total_tools += info["tools"]
                details.append({
                    "server": name,
                    "tools": info["tools"],
                    "est_tokens": info["est_tokens"],
                    "category": info["category"],
                })
            else:
                details.append({
                    "server": name,
                    "tools": "unknown",
                    "est_tokens": 3000,  # Durchschnitt
                    "category": "unknown",
                })
                total_tokens += 3000

        # Kontext-Window-Anteil (typisch 200k tokens)
        context_pct = round((total_tokens / 200000) * 100, 1)

        return {
            "servers": details,
            "total_tools": total_tools,
            "total_est_tokens": total_tokens,
            "context_window_usage_pct": context_pct,
            "remaining_for_conversation_pct": round(100 - context_pct, 1),
            "recommendation": "OK" if context_pct < 30 else "WARNING: Über 30% Context für Tools — erwäge Server zu reduzieren" if context_pct < 50 else "CRITICAL: Über 50% Context für Tools — reduziere Server dringend",
        }

    @mcp.tool()
    async def get_server_catalog() -> dict:
        """Vollständiger Katalog aller bekannten MCP-Server mit Kategorien.

        Zeigt alle Server, ihre Kategorien, Tool-Anzahl und
        geschätzten Token-Verbrauch.
        """
        catalog = {}
        for name, info in KNOWN_SERVERS.items():
            cat = info["category"]
            if cat not in catalog:
                catalog[cat] = []
            catalog[cat].append({
                "name": name,
                "tools": info["tools"],
                "est_tokens": info["est_tokens"],
                "keywords": info["keywords"][:5],
            })

        total_servers = len(KNOWN_SERVERS)
        total_tools = sum(s["tools"] for s in KNOWN_SERVERS.values())
        total_tokens = sum(s["est_tokens"] for s in KNOWN_SERVERS.values())

        return {
            "categories": catalog,
            "totals": {
                "servers": total_servers,
                "tools": total_tools,
                "total_est_tokens": total_tokens,
                "avg_tokens_per_server": round(total_tokens / total_servers),
            },
        }

    @mcp.tool()
    async def optimize_server_set(
        current_servers: list[str], task_description: str
    ) -> dict:
        """Optimiere eine bestehende Server-Kombination für eine Aufgabe.

        Analysiert welche der aktuell geladenen Server für die Aufgabe
        nötig sind und welche entfernt werden können.

        Args:
            current_servers: Aktuell geladene Server-Namen
            task_description: Was soll erledigt werden
        """
        keep = []
        remove = []
        task_lower = task_description.lower()

        for name in current_servers:
            if name in KNOWN_SERVERS:
                relevance = _calculate_relevance(task_description, name, KNOWN_SERVERS[name])
                info = KNOWN_SERVERS[name]
                entry = {
                    "server": name,
                    "relevance": round(relevance, 2),
                    "est_tokens": info["est_tokens"],
                }
                if relevance > 0.1:
                    keep.append(entry)
                else:
                    remove.append(entry)
            else:
                keep.append({"server": name, "relevance": 0.5, "est_tokens": 3000})

        tokens_before = sum(
            KNOWN_SERVERS.get(s, {}).get("est_tokens", 3000) for s in current_servers
        )
        tokens_after = sum(k["est_tokens"] for k in keep)
        saved = tokens_before - tokens_after

        return {
            "task": task_description,
            "keep": keep,
            "remove": remove,
            "optimization": {
                "tokens_before": tokens_before,
                "tokens_after": tokens_after,
                "tokens_saved": saved,
                "savings_pct": round((saved / tokens_before) * 100, 1) if tokens_before > 0 else 0,
            },
        }

    @mcp.tool()
    async def suggest_minimal_set(task_description: str) -> dict:
        """Empfehle die minimale Server-Kombination für maximale Effizienz.

        Gibt die absolut kleinste Menge an Servern zurück die für
        eine Aufgabe benötigt werden — für maximale Context-Effizienz.

        Args:
            task_description: Beschreibung der Aufgabe
        """
        task_lower = task_description.lower()

        # Nur Server mit hoher Relevanz
        minimal = []
        for name, info in KNOWN_SERVERS.items():
            relevance = _calculate_relevance(task_description, name, info)
            if relevance >= 0.3:
                minimal.append({
                    "server": name,
                    "relevance": round(relevance, 2),
                    "est_tokens": info["est_tokens"],
                    "tools": info["tools"],
                })

        # Sortiere nach Relevanz
        minimal.sort(key=lambda x: x["relevance"], reverse=True)

        # Maximal 3 Server empfehlen
        minimal = minimal[:3]

        total_tokens = sum(m["est_tokens"] for m in minimal)
        total_tools = sum(m["tools"] for m in minimal)

        return {
            "task": task_description,
            "minimal_servers": minimal,
            "total_tokens": total_tokens,
            "total_tools": total_tools,
            "context_usage_pct": round((total_tokens / 200000) * 100, 1),
            "efficiency_note": f"Nur {len(minimal)} Server mit {total_tools} Tools — maximale Context-Effizienz",
        }
