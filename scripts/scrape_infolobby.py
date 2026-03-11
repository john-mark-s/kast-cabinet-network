"""
InfoLobby scraper — queries the InfoLobby REST API for each minister by name.

API base: https://www.leylobby.gob.cl/api/v1/
No authentication required.

Results saved to: data/processed/infolobby/{minister_id}.json
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import CABINET
from utils import api_get, utc_now_iso

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://www.leylobby.gob.cl/api/v1"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed" / "infolobby"
PAGE_SIZE = 100


def fetch_audiencias_for_person(name: str) -> list[dict]:
    """
    Fetch all lobby audiencias (meetings) for a given person name.
    Handles pagination.
    """
    all_records = []
    page = 1

    while True:
        url = f"{BASE_URL}/audiencias"
        params = {
            "nombre": name,
            "per_page": PAGE_SIZE,
            "page": page,
        }
        try:
            data = api_get(url, params=params)
        except Exception as e:
            logger.error(f"Failed to fetch audiencias for '{name}' page {page}: {e}")
            break

        records = data if isinstance(data, list) else data.get("data", data.get("audiencias", []))
        if not records:
            break

        all_records.extend(records)
        logger.info(f"  Page {page}: got {len(records)} records (total: {len(all_records)})")

        if len(records) < PAGE_SIZE:
            break
        page += 1

    return all_records


def fetch_viajes_for_person(name: str) -> list[dict]:
    """Fetch travel records."""
    all_records = []
    page = 1

    while True:
        url = f"{BASE_URL}/viajes"
        params = {"nombre": name, "per_page": PAGE_SIZE, "page": page}
        try:
            data = api_get(url, params=params)
        except Exception as e:
            logger.error(f"Failed to fetch viajes for '{name}' page {page}: {e}")
            break

        records = data if isinstance(data, list) else data.get("data", data.get("viajes", []))
        if not records:
            break

        all_records.extend(records)
        if len(records) < PAGE_SIZE:
            break
        page += 1

    return all_records


def fetch_donativos_for_person(name: str) -> list[dict]:
    """Fetch gift/donativo records."""
    all_records = []
    page = 1

    while True:
        url = f"{BASE_URL}/donativos"
        params = {"nombre": name, "per_page": PAGE_SIZE, "page": page}
        try:
            data = api_get(url, params=params)
        except Exception as e:
            logger.error(f"Failed to fetch donativos for '{name}' page {page}: {e}")
            break

        records = data if isinstance(data, list) else data.get("data", data.get("donativos", []))
        if not records:
            break

        all_records.extend(records)
        if len(records) < PAGE_SIZE:
            break
        page += 1

    return all_records


def fetch_for_minister(minister: dict) -> dict:
    """
    Fetch all InfoLobby data for a minister.
    For daniel-mas-valdes, queries both ministries.
    """
    minister_id = minister["id"]
    name = minister["name"]
    logger.info(f"Fetching InfoLobby data for {name} ({minister_id})")

    audiencias = fetch_audiencias_for_person(name)
    viajes = fetch_viajes_for_person(name)
    donativos = fetch_donativos_for_person(name)

    # For daniel-mas-valdes, also search by both ministry names
    extra_audiencias = []
    if minister_id == "daniel-mas-valdes":
        for ministry_info in minister.get("ministries", []):
            ministry_name = ministry_info.get("name", "")
            logger.info(f"  Also searching by ministry: {ministry_name}")
            extra = fetch_audiencias_for_person(ministry_name)
            extra_audiencias.extend(extra)

    return {
        "minister_id": minister_id,
        "minister_name": name,
        "fetchedAt": utc_now_iso(),
        "audiencias": audiencias,
        "audiencias_extra": extra_audiencias,
        "viajes": viajes,
        "donativos": donativos,
        "summary": {
            "total_audiencias": len(audiencias) + len(extra_audiencias),
            "total_viajes": len(viajes),
            "total_donativos": len(donativos),
        },
    }


def save_result(minister_id: str, data: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{minister_id}.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    logger.info(f"  Saved to {out_path}")


def main():
    logger.info(f"Processing {len(CABINET)} ministers")

    for minister in CABINET:
        try:
            result = fetch_for_minister(minister)
            save_result(minister["id"], result)
        except Exception as e:
            logger.error(f"Error processing {minister['id']}: {e}")
            # Save empty result so downstream doesn't fail
            empty = {
                "minister_id": minister["id"],
                "minister_name": minister["name"],
                "fetchedAt": utc_now_iso(),
                "audiencias": [],
                "audiencias_extra": [],
                "viajes": [],
                "donativos": [],
                "summary": {"total_audiencias": 0, "total_viajes": 0, "total_donativos": 0},
                "error": str(e),
            }
            save_result(minister["id"], empty)

    logger.info("InfoLobby scraping complete.")


if __name__ == "__main__":
    main()
