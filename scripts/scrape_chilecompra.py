"""
ChileCompra scraper — queries the Mercado Público REST API for each company RUT.

API documentation: https://www.mercadopublico.cl/Procurement/Modules/RFB/AceptarAnularOrden.aspx
Test API key: F8537A18-6766-4DEF-9E59-426B4FEE2844

Results saved to: data/processed/chilecompra/{rut_normalized}.json
"""

import json
import logging
import os
import sys
from pathlib import Path

# Allow imports from parent directory
sys.path.insert(0, str(Path(__file__).parent))

from config import CABINET
from utils import normalize_rut, format_rut_for_api, api_get, utc_now_iso

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# --- Config ---
API_KEY = os.getenv("CHILECOMPRA_API_KEY", "F8537A18-6766-4DEF-9E59-426B4FEE2844")
BASE_URL = "https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed" / "chilecompra"
DISCOVERED_RUTS_FILE = Path(__file__).parent.parent / "data" / "processed" / "infoprobidad" / "discovered_ruts.json"


def load_all_ruts() -> list[str]:
    """Collect all company RUTs from config + discovered_ruts.json."""
    ruts = set()

    for minister in CABINET:
        for company in minister.get("known_companies", []):
            rut = company.get("rut", "")
            if rut:
                ruts.add(normalize_rut(rut))

    if DISCOVERED_RUTS_FILE.exists():
        try:
            discovered = json.loads(DISCOVERED_RUTS_FILE.read_text())
            for rut in discovered.get("ruts", []):
                if rut:
                    ruts.add(normalize_rut(rut))
        except Exception as e:
            logger.warning(f"Could not load discovered_ruts.json: {e}")

    return list(ruts)


def fetch_orders_for_rut(rut_normalized: str) -> dict:
    """
    Query ChileCompra API for all purchase orders where this RUT is the supplier.
    Handles pagination (100 per page).
    """
    rut_api = format_rut_for_api(rut_normalized)
    logger.info(f"Querying ChileCompra for RUT {rut_api}")

    all_orders = []
    page = 1

    while True:
        params = {
            "ticket": API_KEY,
            "rutProveedor": rut_api,
            "pagina": page,
        }
        try:
            data = api_get(BASE_URL, params=params)
        except Exception as e:
            logger.error(f"Failed to fetch page {page} for RUT {rut_api}: {e}")
            break

        orders = data.get("Listado", []) or []
        if not orders:
            break

        all_orders.extend(orders)
        logger.info(f"  Page {page}: got {len(orders)} orders (total so far: {len(all_orders)})")

        # ChileCompra returns up to 100 per page; if fewer returned, we're done
        if len(orders) < 100:
            break
        page += 1

    return {
        "rut": rut_normalized,
        "rut_api_format": rut_api,
        "fetchedAt": utc_now_iso(),
        "totalOrders": len(all_orders),
        "orders": all_orders,
    }


def save_result(rut_normalized: str, data: dict) -> None:
    """Save result to data/processed/chilecompra/{rut_normalized}.json."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Use rut without dash for filename to avoid filesystem issues
    filename = rut_normalized.replace("-", "_").replace(".", "")
    out_path = OUTPUT_DIR / f"{filename}.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    logger.info(f"  Saved to {out_path}")


def main():
    ruts = load_all_ruts()
    logger.info(f"Found {len(ruts)} RUTs to query")

    if not ruts:
        logger.warning("No RUTs found. Check config.py known_companies and discovered_ruts.json.")
        return

    for rut in ruts:
        try:
            result = fetch_orders_for_rut(rut)
            save_result(rut, result)
        except Exception as e:
            logger.error(f"Error processing RUT {rut}: {e}")

    logger.info("ChileCompra scraping complete.")


if __name__ == "__main__":
    main()
