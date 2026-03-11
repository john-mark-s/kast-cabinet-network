"""
Build the network graph from config.py + processed data.

For Phase 1: builds Quiroz network manually (~21 nodes, ~22 edges).
All seed ministers get a single "person" node each with status="seed".

Outputs:
  data/graph/graph.json          — full network
  data/graph/ministers/{id}.json — per-minister detail
  data/graph/meta.json           — last-updated timestamps
"""

import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from config import CABINET, SOURCES

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

GRAPH_DIR = Path(__file__).parent.parent / "data" / "graph"
MINISTERS_DIR = GRAPH_DIR / "ministers"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

TODAY = datetime.now(timezone.utc).date().isoformat()
NOW = datetime.now(timezone.utc).isoformat()


def make_id(*parts) -> str:
    """Create a deterministic ID from parts."""
    return "-".join(str(p).lower().replace(" ", "-").replace(".", "").replace(",", "") for p in parts if p)


def load_processed(subdir: str, filename: str) -> dict:
    """Load a processed data file, returning empty dict if not found."""
    path = PROCESSED_DIR / subdir / filename
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception as e:
            logger.warning(f"Could not load {path}: {e}")
    return {}


# ---------------------------------------------------------------------------
# Flag detection
# ---------------------------------------------------------------------------

RED_FLAG_DEFS = {
    "SELF_DEALING": {"severity": "critical", "label": "Autocontratación", "icon": "🔴"},
    "REVOLVING_DOOR": {"severity": "high", "label": "Puerta giratoria", "icon": "🔄"},
    "DIRECT_AWARD_CLUSTER": {"severity": "high", "label": "Trato directo repetido", "icon": "🎯"},
    "LOBBY_TO_CONTRACT": {"severity": "high", "label": "Lobby → Contrato", "icon": "🤝"},
    "CONCENTRATION": {"severity": "medium", "label": "Concentración de contratos", "icon": "⚠️"},
    "CORPORATE_RESTRUCTURING": {"severity": "medium", "label": "Reestructuración corporativa", "icon": "🔀"},
    "GOV_CONTRACTOR": {"severity": "info", "label": "Contratista del Estado", "icon": "📋"},
    "COLLUSION_LINK": {"severity": "high", "label": "Vinculado a caso colusión", "icon": "⚖️"},
    "ACTIVE_CONTRACT": {"severity": "info", "label": "Contrato activo", "icon": "📄"},
}


def detect_flags_for_minister(minister: dict) -> list[str]:
    """Detect applicable red flags for a minister based on seed data."""
    flags = []

    if minister.get("collusion_links"):
        flags.append("COLLUSION_LINK")

    if minister.get("known_gov_contracts"):
        flags.append("GOV_CONTRACTOR")
        # Check for active contracts (no end date or future end date)
        for contract in minister.get("known_gov_contracts", []):
            if contract.get("year", 0) >= 2022:
                flags.append("ACTIVE_CONTRACT")
                break

    if minister.get("corporate_events"):
        for event in minister.get("corporate_events", []):
            if any(word in event.get("event", "").lower() for word in ["renombr", "restructur", "salió", "renam"]):
                flags.append("CORPORATE_RESTRUCTURING")
                break

    # Revolving door: check associates
    for assoc in minister.get("known_associates", []):
        if "REVOLVING_DOOR" in assoc.get("flags", []):
            flags.append("REVOLVING_DOOR")
            break

    return list(set(flags))


def detect_flags_for_company(company: dict, minister: dict) -> list[str]:
    """Detect flags for a company node."""
    flags = []

    # GOV_CONTRACTOR: has known contracts
    if minister.get("known_gov_contracts"):
        flags.append("GOV_CONTRACTOR")

    # COLLUSION_LINK: in collusion cases
    company_name_lower = company.get("name", "").lower()
    for case in minister.get("collusion_links", []):
        case_companies = case.get("company", "").lower()
        if any(part in case_companies for part in company_name_lower.split()[:2] if len(part) > 3):
            flags.append("COLLUSION_LINK")
            break

    # CORPORATE_RESTRUCTURING: renamed
    if company.get("relationship", "") and "exited" in company.get("relationship", "").lower():
        pass  # exited is not restructuring
    for event in minister.get("corporate_events", []):
        if "renombr" in event.get("event", "").lower() or "renam" in event.get("event", "").lower():
            flags.append("CORPORATE_RESTRUCTURING")
            break

    return list(set(flags))


# ---------------------------------------------------------------------------
# Node builders
# ---------------------------------------------------------------------------

def make_person_node(minister: dict) -> dict:
    """Create a person node for a minister."""
    flags = detect_flags_for_minister(minister)
    return {
        "id": minister["id"],
        "type": "person",
        "label": minister["name"],
        "role": minister["role"],
        "party": minister.get("party", ""),
        "ministry": minister.get("ministry", ""),
        "flags": flags,
        "sources": [SOURCES[s]["name"] for s in minister.get("sources", []) if s in SOURCES],
        "sourceKeys": minister.get("sources", []),
        "verifyUrls": minister.get("verify_urls", []),
        "addedDate": TODAY,
        "lastModified": TODAY,
        "status": minister.get("status", "seed"),
        "notes": minister.get("notes", ""),
    }


def make_company_node(company: dict, minister: dict) -> dict:
    """Create a company node."""
    node_id = company.get("rut", "") or make_id("company", company["name"])
    if company.get("rut"):
        node_id = f"rut-{company['rut'].replace('.', '').replace('-', '')}"

    flags = detect_flags_for_company(company, minister)
    source_names = [SOURCES[s]["name"] for s in company.get("sources", []) if s in SOURCES]

    return {
        "id": node_id,
        "type": "company",
        "label": company["name"],
        "rut": company.get("rut", ""),
        "flags": flags,
        "sources": source_names,
        "sourceKeys": company.get("sources", []),
        "verifyUrls": company.get("verify_urls", []),
        "addedDate": TODAY,
        "lastModified": TODAY,
        "status": "mapped",
    }


def make_associate_node(associate: dict) -> dict:
    """Create a person node for an associate."""
    node_id = make_id("person", associate["name"])
    flags = associate.get("flags", [])
    source_names = [SOURCES[s]["name"] for s in associate.get("sources", []) if s in SOURCES]

    return {
        "id": node_id,
        "type": "person",
        "label": associate["name"],
        "role": associate.get("relationship", ""),
        "flags": flags,
        "sources": source_names,
        "sourceKeys": associate.get("sources", []),
        "verifyUrls": [],
        "addedDate": TODAY,
        "lastModified": TODAY,
        "status": "seed",
    }


def make_collusion_client_node(case: dict) -> dict:
    """Create a corporate_client node for a collusion case company."""
    node_id = make_id("client", case["company"])
    source_names = [SOURCES[s]["name"] for s in case.get("sources", []) if s in SOURCES]

    return {
        "id": node_id,
        "type": "corporate_client",
        "label": case["company"],
        "case": case.get("case", ""),
        "flags": ["COLLUSION_LINK"],
        "sources": source_names,
        "sourceKeys": case.get("sources", []),
        "verifyUrls": [{"label": "Ver en TDLC", "url": "https://www.tdlc.cl/"}],
        "addedDate": TODAY,
        "lastModified": TODAY,
        "status": "seed",
    }


def make_institution_node(minister: dict) -> dict:
    """Create an institution node for a ministry."""
    node_id = make_id("inst", minister["ministry"])
    return {
        "id": node_id,
        "type": "institution",
        "label": minister["ministry"],
        "flags": [],
        "sources": [],
        "sourceKeys": [],
        "verifyUrls": [
            {"label": "Portal Transparencia", "url": minister.get("ministry_transparency_url", "https://www.portaltransparencia.cl/")}
        ],
        "addedDate": TODAY,
        "lastModified": TODAY,
        "status": "seed",
    }


# ---------------------------------------------------------------------------
# Edge builders
# ---------------------------------------------------------------------------

def make_edge(source: str, target: str, edge_type: str, label: str,
              flags: list = None, sources: list = None, source_keys: list = None,
              verify_urls: list = None) -> dict:
    edge_id = f"e-{make_id(source, target, edge_type)}"
    return {
        "id": edge_id,
        "source": source,
        "target": target,
        "type": edge_type,
        "label": label,
        "flags": flags or [],
        "sources": sources or [],
        "sourceKeys": source_keys or [],
        "verifyUrls": verify_urls or [],
        "addedDate": TODAY,
        "lastModified": TODAY,
    }


# ---------------------------------------------------------------------------
# Main graph builder
# ---------------------------------------------------------------------------

def build_graph() -> dict:
    nodes: dict[str, dict] = {}
    edges: list[dict] = {}
    edge_set = {}  # deduplicate by id

    def add_node(node: dict):
        if node["id"] not in nodes:
            nodes[node["id"]] = node
        else:
            # Merge flags
            existing_flags = set(nodes[node["id"]].get("flags", []))
            new_flags = set(node.get("flags", []))
            nodes[node["id"]]["flags"] = list(existing_flags | new_flags)

    def add_edge(edge: dict):
        if edge["id"] not in edge_set:
            edge_set[edge["id"]] = edge

    for minister in CABINET:
        minister_node = make_person_node(minister)
        add_node(minister_node)

        # Ministry institution node
        inst_node = make_institution_node(minister)
        add_node(inst_node)

        # Minister → heads → Ministry
        add_edge(make_edge(
            minister["id"], inst_node["id"],
            "heads", f"Ministro/a de {minister['ministry']}",
            sources=[SOURCES[s]["name"] for s in minister.get("sources", []) if s in SOURCES],
            source_keys=minister.get("sources", []),
        ))

        if minister.get("status") != "mapped":
            continue  # Only build full network for mapped ministers

        # --- Companies ---
        for company in minister.get("known_companies", []):
            company_node = make_company_node(company, minister)
            add_node(company_node)

            edge_flags = []
            if "COLLUSION_LINK" in company_node.get("flags", []):
                edge_flags.append("COLLUSION_LINK")

            add_edge(make_edge(
                minister["id"], company_node["id"],
                "owned", company.get("relationship", "Socio/dueño"),
                flags=edge_flags,
                sources=[SOURCES[s]["name"] for s in company.get("sources", []) if s in SOURCES],
                source_keys=company.get("sources", []),
                verify_urls=company.get("verify_urls", []),
            ))

        # --- Associates ---
        for associate in minister.get("known_associates", []):
            assoc_node = make_associate_node(associate)
            add_node(assoc_node)

            edge_type = "family" if "cónyuge" in associate.get("relationship", "").lower() else "works_at"
            edge_flags = associate.get("flags", [])

            add_edge(make_edge(
                minister["id"], assoc_node["id"],
                edge_type, associate.get("relationship", "Asociado/a"),
                flags=edge_flags,
                sources=[SOURCES[s]["name"] for s in associate.get("sources", []) if s in SOURCES],
                source_keys=associate.get("sources", []),
            ))

            # If associate has worked at the minister's companies, link them too
            if minister.get("known_companies"):
                main_company = minister["known_companies"][0]
                company_node = make_company_node(main_company, minister)
                if "socio" in associate.get("relationship", "").lower() or "asociado" in associate.get("relationship", "").lower():
                    add_edge(make_edge(
                        assoc_node["id"], company_node["id"],
                        "works_at", "Socio/a",
                        sources=[SOURCES[s]["name"] for s in associate.get("sources", []) if s in SOURCES],
                        source_keys=associate.get("sources", []),
                    ))

        # --- Government Contracts ---
        for i, contract in enumerate(minister.get("known_gov_contracts", [])):
            buyer = contract["buyer"]
            buyer_id = make_id("inst", buyer)

            if buyer_id not in nodes:
                buyer_node = {
                    "id": buyer_id,
                    "type": "institution",
                    "label": buyer,
                    "flags": [],
                    "sources": [SOURCES[s]["name"] for s in contract.get("sources", []) if s in SOURCES],
                    "sourceKeys": contract.get("sources", []),
                    "verifyUrls": [{"label": "Ver en Mercado Público", "url": contract.get("verify_url", "https://www.mercadopublico.cl/")}],
                    "addedDate": TODAY,
                    "lastModified": TODAY,
                    "status": "seed",
                }
                add_node(buyer_node)

            # Find the company (use first known company)
            if minister.get("known_companies"):
                company_node = make_company_node(minister["known_companies"][0], minister)
                contract_flags = ["GOV_CONTRACTOR"]
                if contract.get("year", 0) >= 2022:
                    contract_flags.append("ACTIVE_CONTRACT")

                edge_id = f"e-contract-{minister['id']}-{i}"
                add_edge({
                    "id": edge_id,
                    "source": company_node["id"],
                    "target": buyer_id,
                    "type": "contract",
                    "label": f"{contract['desc']} ({contract.get('year', '?')})",
                    "amount_clp": contract.get("amount_clp"),
                    "year": contract.get("year"),
                    "flags": contract_flags,
                    "sources": [SOURCES[s]["name"] for s in contract.get("sources", []) if s in SOURCES],
                    "sourceKeys": contract.get("sources", []),
                    "verifyUrls": [{"label": "Ver en Mercado Público", "url": contract.get("verify_url", "")}],
                    "addedDate": TODAY,
                    "lastModified": TODAY,
                })

        # --- Collusion Links ---
        for case in minister.get("collusion_links", []):
            client_node = make_collusion_client_node(case)
            add_node(client_node)

            add_edge(make_edge(
                minister["id"], client_node["id"],
                "advisory", f"Consultor/perito: {case.get('role', '')}",
                flags=["COLLUSION_LINK"],
                sources=[SOURCES[s]["name"] for s in case.get("sources", []) if s in SOURCES],
                source_keys=case.get("sources", []),
                verify_urls=[{"label": "Ver en TDLC", "url": "https://www.tdlc.cl/"}],
            ))

        # --- Board memberships ---
        for board in minister.get("board_memberships", []):
            board_id = make_id("inst", board["entity"])
            if board_id not in nodes:
                board_source_names = [SOURCES[s]["name"] for s in board.get("sources", []) if s in SOURCES]
                board_node = {
                    "id": board_id,
                    "type": "institution",
                    "label": board["entity"],
                    "flags": [],
                    "sources": board_source_names,
                    "sourceKeys": board.get("sources", []),
                    "verifyUrls": [],
                    "addedDate": TODAY,
                    "lastModified": TODAY,
                    "status": "seed",
                }
                add_node(board_node)

            add_edge(make_edge(
                minister["id"], board_id,
                "board", f"Director/a: {board.get('status', '')}",
                sources=[SOURCES[s]["name"] for s in board.get("sources", []) if s in SOURCES],
                source_keys=board.get("sources", []),
            ))

    # Build final lists
    nodes_list = list(nodes.values())
    edges_list = list(edge_set.values())

    graph = {
        "nodes": nodes_list,
        "edges": edges_list,
        "meta": {
            "generatedAt": NOW,
            "nodeCount": len(nodes_list),
            "edgeCount": len(edges_list),
            "sources": {k: {"name": v["name"], "url": v["url"]} for k, v in SOURCES.items()},
            "phase": 1,
            "description": "Phase 1 seed graph — Quiroz fully mapped, all other ministers as seed nodes",
        },
    }

    return graph


def write_minister_detail(minister: dict, graph: dict):
    """Write per-minister detail JSON."""
    minister_id = minister["id"]

    # Find all nodes and edges related to this minister
    related_nodes = {minister_id}
    minister_edges = []

    for edge in graph["edges"]:
        if edge["source"] == minister_id or edge["target"] == minister_id:
            minister_edges.append(edge)
            related_nodes.add(edge["source"])
            related_nodes.add(edge["target"])

    related_node_objects = [n for n in graph["nodes"] if n["id"] in related_nodes]

    detail = {
        "minister": next((n for n in graph["nodes"] if n["id"] == minister_id), None),
        "nodes": related_node_objects,
        "edges": minister_edges,
        "rawData": {
            "known_companies": minister.get("known_companies", []),
            "known_associates": minister.get("known_associates", []),
            "known_gov_contracts": minister.get("known_gov_contracts", []),
            "collusion_links": minister.get("collusion_links", []),
            "board_memberships": minister.get("board_memberships", []),
            "corporate_events": minister.get("corporate_events", []),
        },
        "generatedAt": NOW,
    }

    MINISTERS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = MINISTERS_DIR / f"{minister_id}.json"
    out_path.write_text(json.dumps(detail, ensure_ascii=False, indent=2))


def write_meta(graph: dict):
    """Write meta.json with timestamps."""
    meta = {
        "lastUpdated": NOW,
        "phase": 1,
        "nodeCount": graph["meta"]["nodeCount"],
        "edgeCount": graph["meta"]["edgeCount"],
        "ministerCount": len(CABINET),
        "mappedCount": sum(1 for m in CABINET if m.get("status") == "mapped"),
        "seedCount": sum(1 for m in CABINET if m.get("status") == "seed"),
        "sources": {
            "chilecompra": {"lastRun": None, "status": "pending"},
            "infolobby": {"lastRun": None, "status": "pending"},
            "infoprobidad": {"lastRun": None, "status": "pending"},
            "sii": {"lastRun": None, "status": "pending"},
        },
        "flagCounts": {},
    }

    # Count flags
    for node in graph["nodes"]:
        for flag in node.get("flags", []):
            meta["flagCounts"][flag] = meta["flagCounts"].get(flag, 0) + 1

    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    out_path = GRAPH_DIR / "meta.json"
    out_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    logger.info(f"Saved meta.json")


def main():
    logger.info("Building graph from config.py + processed data...")

    graph = build_graph()

    logger.info(f"Graph: {graph['meta']['nodeCount']} nodes, {graph['meta']['edgeCount']} edges")

    # Save graph.json
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    graph_path = GRAPH_DIR / "graph.json"
    graph_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2))
    logger.info(f"Saved graph.json")

    # Save per-minister detail files
    for minister in CABINET:
        try:
            write_minister_detail(minister, graph)
        except Exception as e:
            logger.error(f"Error writing detail for {minister['id']}: {e}")

    logger.info(f"Saved {len(CABINET)} minister detail files")

    # Save meta.json
    write_meta(graph)

    # Log flag summary
    flag_counts: dict[str, int] = {}
    for node in graph["nodes"]:
        for flag in node.get("flags", []):
            flag_counts[flag] = flag_counts.get(flag, 0) + 1
    if flag_counts:
        logger.info("Red flag summary:")
        for flag, count in sorted(flag_counts.items(), key=lambda x: -x[1]):
            logger.info(f"  {flag}: {count} nodes")

    logger.info("Graph build complete.")


if __name__ == "__main__":
    main()
