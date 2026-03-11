"""
Diff graph.json against the previous git commit version.

Detects:
  NEW_NODE, REMOVED_NODE, NEW_EDGE, CHANGED_EDGE,
  NEW_FLAG, RESOLVED_FLAG, CORPORATE_EVENT, DECLARATION_FILED, MINISTER_APPEARED

Output: data/graph/changelog.json grouped by ISO week.

For Phase 1: generates a seed changelog entry for the inaugural build.
"""

import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import iso_week, utc_now_iso, today_iso

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

GRAPH_DIR = Path(__file__).parent.parent / "data" / "graph"
GRAPH_PATH = GRAPH_DIR / "graph.json"
CHANGELOG_PATH = GRAPH_DIR / "changelog.json"

EVENT_ICONS = {
    "NEW_NODE": "➕",
    "REMOVED_NODE": "➖",
    "NEW_EDGE": "🔗",
    "CHANGED_EDGE": "✏️",
    "NEW_FLAG": "🚩",
    "RESOLVED_FLAG": "✅",
    "CORPORATE_EVENT": "🏢",
    "DECLARATION_FILED": "📋",
    "MINISTER_APPEARED": "👤",
    "INAUGURAL_BUILD": "🚀",
}

SEVERITY_MAP = {
    "SELF_DEALING": "high",
    "REVOLVING_DOOR": "high",
    "DIRECT_AWARD_CLUSTER": "high",
    "LOBBY_TO_CONTRACT": "high",
    "COLLUSION_LINK": "high",
    "CONCENTRATION": "medium",
    "CORPORATE_RESTRUCTURING": "medium",
    "GOV_CONTRACTOR": "info",
    "ACTIVE_CONTRACT": "info",
}


def get_previous_graph() -> dict | None:
    """
    Try to load graph.json from the previous git commit.
    Returns None if this is the first commit or git is unavailable.
    """
    try:
        result = subprocess.run(
            ["git", "show", "HEAD~1:data/graph/graph.json"],
            capture_output=True,
            text=True,
            cwd=str(GRAPH_DIR.parent.parent),
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        logger.info(f"No previous git commit found (expected on first run): {e}")
    return None


def load_current_graph() -> dict:
    if GRAPH_PATH.exists():
        return json.loads(GRAPH_PATH.read_text())
    return {"nodes": [], "edges": [], "meta": {}}


def load_existing_changelog() -> dict:
    if CHANGELOG_PATH.exists():
        try:
            return json.loads(CHANGELOG_PATH.read_text())
        except Exception:
            pass
    return {"weeks": []}


def make_event(event_type: str, title: str, desc: str, severity: str,
               node_refs: list = None, source: str = "", date: str = None) -> dict:
    return {
        "type": event_type,
        "date": date or today_iso(),
        "severity": severity,
        "icon": EVENT_ICONS.get(event_type, "📌"),
        "title": title,
        "desc": desc,
        "source": source,
        "nodeRefs": node_refs or [],
    }


def diff_graphs(prev: dict, curr: dict) -> list[dict]:
    """Compare two graphs and return list of change events."""
    events = []
    today = today_iso()

    prev_nodes = {n["id"]: n for n in prev.get("nodes", [])}
    curr_nodes = {n["id"]: n for n in curr.get("nodes", [])}
    prev_edges = {e["id"]: e for e in prev.get("edges", [])}
    curr_edges = {e["id"]: e for e in curr.get("edges", [])}

    # New nodes
    for node_id, node in curr_nodes.items():
        if node_id not in prev_nodes:
            node_type = node.get("type", "unknown")
            if node_type == "person":
                event_type = "MINISTER_APPEARED"
                title = f"Nuevo ministro/a: {node['label']}"
                desc = f"Se agregó {node['label']} ({node.get('role', '')}) a la red."
                severity = "medium"
            else:
                event_type = "NEW_NODE"
                title = f"Nueva entidad: {node['label']}"
                desc = f"Se detectó nueva entidad tipo {node_type}: {node['label']}"
                severity = "info"
            events.append(make_event(event_type, title, desc, severity, [node_id], date=today))

    # Removed nodes
    for node_id, node in prev_nodes.items():
        if node_id not in curr_nodes:
            events.append(make_event(
                "REMOVED_NODE",
                f"Entidad removida: {node['label']}",
                f"La entidad {node['label']} fue removida del grafo.",
                "info", [node_id], date=today,
            ))

    # New flags on existing nodes
    for node_id in set(prev_nodes) & set(curr_nodes):
        prev_flags = set(prev_nodes[node_id].get("flags", []))
        curr_flags = set(curr_nodes[node_id].get("flags", []))
        new_flags = curr_flags - prev_flags
        resolved_flags = prev_flags - curr_flags

        node_label = curr_nodes[node_id]["label"]

        for flag in new_flags:
            severity = SEVERITY_MAP.get(flag, "medium")
            events.append(make_event(
                "NEW_FLAG",
                f"Nueva alerta en {node_label}: {flag}",
                f"Se detectó indicador {flag} en {node_label}.",
                severity, [node_id], date=today,
            ))

        for flag in resolved_flags:
            events.append(make_event(
                "RESOLVED_FLAG",
                f"Alerta resuelta en {node_label}: {flag}",
                f"El indicador {flag} fue marcado como resuelto en {node_label}.",
                "info", [node_id], date=today,
            ))

    # New edges
    for edge_id, edge in curr_edges.items():
        if edge_id not in prev_edges:
            events.append(make_event(
                "NEW_EDGE",
                f"Nueva conexión: {edge.get('label', edge_id)}",
                f"Nueva relación tipo {edge['type']} entre {edge['source']} y {edge['target']}.",
                "info", [edge["source"], edge["target"]], date=today,
            ))

    return events


def merge_into_changelog(existing: dict, new_events: list[dict]) -> dict:
    """Merge new events into the changelog, grouped by ISO week."""
    if not new_events:
        return existing

    # Group events by week
    week_map: dict[str, list] = {}
    for week_entry in existing.get("weeks", []):
        week_map[week_entry["week"]] = week_entry["events"]

    for event in new_events:
        try:
            dt = datetime.fromisoformat(event["date"])
        except Exception:
            dt = datetime.now(timezone.utc)
        week = iso_week(dt)
        if week not in week_map:
            week_map[week] = []
        week_map[week].append(event)

    # Sort weeks descending
    sorted_weeks = sorted(week_map.keys(), reverse=True)
    return {
        "updatedAt": utc_now_iso(),
        "totalEvents": sum(len(v) for v in week_map.values()),
        "weeks": [
            {"week": w, "events": week_map[w]}
            for w in sorted_weeks
        ],
    }


def generate_inaugural_changelog(curr_graph: dict) -> list[dict]:
    """Generate the seed changelog for the first build."""
    events = []
    today = today_iso()

    nodes = curr_graph.get("nodes", [])
    edges = curr_graph.get("edges", [])
    person_nodes = [n for n in nodes if n.get("type") == "person"]
    flagged_nodes = [n for n in nodes if n.get("flags")]

    # Main inaugural event
    events.append(make_event(
        "INAUGURAL_BUILD",
        "Red de conexiones publicada — Gabinete Kast",
        (
            f"Se publicó el grafo inaugural del Gabinete Kast (11 marzo 2026). "
            f"{len(nodes)} nodos, {len(edges)} conexiones. "
            f"Jorge Quiroz (Hacienda) completamente mapeado con {len(flagged_nodes)} alertas detectadas. "
            f"Los {len(person_nodes) - 1} ministros restantes están listados como nodos semilla."
        ),
        "info",
        [n["id"] for n in person_nodes[:5]],
        source="config.py seed data",
        date=today,
    ))

    # Flag events for Quiroz
    for node in nodes:
        if node["id"] == "jorge-quiroz":
            for flag in node.get("flags", []):
                severity = SEVERITY_MAP.get(flag, "medium")
                events.append(make_event(
                    "NEW_FLAG",
                    f"Alerta detectada en Jorge Quiroz: {flag}",
                    f"Se identificó indicador {flag} en el Ministro de Hacienda.",
                    severity,
                    ["jorge-quiroz"],
                    source="Investigación periodística (CIPER, La Tercera, Contrapoder)",
                    date=today,
                ))

    # Corporate restructuring event
    events.append(make_event(
        "CORPORATE_EVENT",
        "Reestructuración corporativa detectada — QA Consultores",
        (
            "En agosto 2025, las empresas de Quiroz fueron renombradas durante la campaña electoral: "
            "Quiroz y Asociados SA → QA Consultores; Quiroz y Asociados Consultores → QYA Consultores. "
            "En enero 2026, Quiroz y Paula Hurtado salen de QYA. Socios Givovich (58.81%) y Bravo (41.19%) quedan."
        ),
        "medium",
        ["jorge-quiroz", "rut-969531208"],
        source="La Tercera, Contrapoder Chile",
        date="2026-01-01",
    ))

    return events


def main():
    curr_graph = load_current_graph()
    prev_graph = get_previous_graph()
    existing_changelog = load_existing_changelog()

    if prev_graph is None:
        logger.info("First run — generating inaugural changelog")
        new_events = generate_inaugural_changelog(curr_graph)
    else:
        logger.info("Diffing against previous commit")
        new_events = diff_graphs(prev_graph, curr_graph)

    if not new_events:
        logger.info("No changes detected")
        new_events = []

    updated_changelog = merge_into_changelog(existing_changelog, new_events)

    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    CHANGELOG_PATH.write_text(json.dumps(updated_changelog, ensure_ascii=False, indent=2))
    logger.info(f"Saved changelog.json with {updated_changelog['totalEvents']} total events")

    # Summary
    if new_events:
        logger.info(f"New events this run: {len(new_events)}")
        high_sev = [e for e in new_events if e.get("severity") == "high"]
        if high_sev:
            logger.warning(f"  {len(high_sev)} HIGH severity events!")
    else:
        logger.info("No new events generated")

    logger.info("Diff complete.")


if __name__ == "__main__":
    main()
