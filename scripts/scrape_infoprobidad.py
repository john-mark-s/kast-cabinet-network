"""
InfoProbidad scraper — queries the InfoProbidad open data API by minister name.

Extracts company participations (name + RUT).
Appends new RUTs to data/processed/infoprobidad/discovered_ruts.json.
Saves full declaration data to data/processed/infoprobidad/{minister_id}.json.

API: https://www.infoprobidad.cl/DatosAbiertos/DatosAbiertos
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import CABINET
from utils import normalize_rut, validate_rut, api_get, utc_now_iso

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed" / "infoprobidad"
DISCOVERED_RUTS_FILE = OUTPUT_DIR / "discovered_ruts.json"

# InfoProbidad open data API endpoints
BASE_URL = "https://www.infoprobidad.cl/DatosAbiertos"


def load_discovered_ruts() -> set:
    """Load existing discovered RUTs."""
    if DISCOVERED_RUTS_FILE.exists():
        try:
            data = json.loads(DISCOVERED_RUTS_FILE.read_text())
            return set(data.get("ruts", []))
        except Exception as e:
            logger.warning(f"Could not load discovered_ruts.json: {e}")
    return set()


def save_discovered_ruts(ruts: set) -> None:
    """Persist discovered RUTs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "updatedAt": utc_now_iso(),
        "count": len(ruts),
        "ruts": sorted(list(ruts)),
    }
    DISCOVERED_RUTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    logger.info(f"Saved {len(ruts)} discovered RUTs to {DISCOVERED_RUTS_FILE}")


def search_declarations_by_name(name: str) -> list[dict]:
    """
    Search InfoProbidad for declarations by person name.
    Returns list of declaration records.
    """
    # InfoProbidad open data search endpoint
    url = f"{BASE_URL}/BuscarDeclaraciones"
    params = {"nombre": name}

    try:
        data = api_get(url, params=params)
        if isinstance(data, list):
            return data
        return data.get("declaraciones", data.get("Declaraciones", []))
    except Exception as e:
        logger.warning(f"InfoProbidad search failed for '{name}': {e}")
        return []


def extract_company_ruts(declarations: list[dict]) -> list[dict]:
    """
    Extract company participations with RUTs from declaration data.
    Returns list of {name, rut, relationship} dicts.
    """
    companies = []
    seen_ruts = set()

    for decl in declarations:
        # Participaciones en empresas
        participaciones = (
            decl.get("participaciones", [])
            or decl.get("Participaciones", [])
            or decl.get("empresas", [])
            or []
        )
        for p in participaciones:
            rut = (
                p.get("rut", "")
                or p.get("Rut", "")
                or p.get("rutEmpresa", "")
                or ""
            )
            company_name = (
                p.get("nombre", "")
                or p.get("Nombre", "")
                or p.get("razonSocial", "")
                or ""
            )
            if rut:
                rut_norm = normalize_rut(rut)
                if rut_norm and rut_norm not in seen_ruts:
                    seen_ruts.add(rut_norm)
                    companies.append({
                        "name": company_name,
                        "rut": rut_norm,
                        "rut_valid": validate_rut(rut_norm),
                        "relationship": p.get("tipo", p.get("participacion", "")),
                    })

    return companies


def fetch_for_minister(minister: dict) -> dict:
    """Fetch InfoProbidad data for a single minister."""
    minister_id = minister["id"]
    name = minister["name"]
    logger.info(f"Fetching InfoProbidad data for {name} ({minister_id})")

    declarations = search_declarations_by_name(name)
    companies = extract_company_ruts(declarations)

    logger.info(f"  Found {len(declarations)} declarations, {len(companies)} companies")

    return {
        "minister_id": minister_id,
        "minister_name": name,
        "fetchedAt": utc_now_iso(),
        "declarations": declarations,
        "companies": companies,
        "summary": {
            "total_declarations": len(declarations),
            "total_companies": len(companies),
        },
    }


def save_result(minister_id: str, data: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{minister_id}.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    logger.info(f"  Saved to {out_path}")


def main():
    discovered_ruts = load_discovered_ruts()
    initial_count = len(discovered_ruts)

    for minister in CABINET:
        try:
            result = fetch_for_minister(minister)
            save_result(minister["id"], result)

            # Collect new RUTs
            for company in result.get("companies", []):
                rut = company.get("rut", "")
                if rut and company.get("rut_valid", False):
                    discovered_ruts.add(rut)

        except Exception as e:
            logger.error(f"Error processing {minister['id']}: {e}")
            empty = {
                "minister_id": minister["id"],
                "minister_name": minister["name"],
                "fetchedAt": utc_now_iso(),
                "declarations": [],
                "companies": [],
                "summary": {"total_declarations": 0, "total_companies": 0},
                "error": str(e),
            }
            save_result(minister["id"], empty)

    new_ruts = len(discovered_ruts) - initial_count
    logger.info(f"Discovered {new_ruts} new RUTs (total: {len(discovered_ruts)})")
    save_discovered_ruts(discovered_ruts)

    logger.info("InfoProbidad scraping complete.")


if __name__ == "__main__":
    main()
