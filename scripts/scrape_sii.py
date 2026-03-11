"""
SII (Servicio de Impuestos Internos) bulk file scraper.

Downloads the SII nómina de personas jurídicas (bulk CSV/Excel).
For every RUT in config.py + discovered_ruts.json, looks up:
- Activity code (rubro)
- Size category
- Address
Flags entities at the same address.

Results saved to: data/processed/sii/companies.json
"""

import csv
import io
import json
import logging
import sys
import zipfile
from pathlib import Path
from typing import Optional

import requests

sys.path.insert(0, str(Path(__file__).parent))

from config import CABINET
from utils import normalize_rut, api_get, utc_now_iso

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed" / "sii"
DISCOVERED_RUTS_FILE = Path(__file__).parent.parent / "data" / "processed" / "infoprobidad" / "discovered_ruts.json"
RAW_DIR = Path(__file__).parent.parent / "data" / "raw"

# SII bulk file URL (nómina personas jurídicas)
SII_BULK_URL = "https://www.sii.cl/sobre_el_sii/nominapersonasjuridicas.html"
SII_CSV_URL = "https://www.sii.cl/estadisticas/nominas/contribuyentes_renta.csv"


def load_all_ruts() -> set:
    """Load all RUTs from config + discovered_ruts."""
    ruts = set()

    for minister in CABINET:
        for company in minister.get("known_companies", []):
            rut = company.get("rut", "")
            if rut:
                ruts.add(normalize_rut(rut))

    if DISCOVERED_RUTS_FILE.exists():
        try:
            data = json.loads(DISCOVERED_RUTS_FILE.read_text())
            for rut in data.get("ruts", []):
                if rut:
                    ruts.add(normalize_rut(rut))
        except Exception as e:
            logger.warning(f"Could not load discovered_ruts.json: {e}")

    return ruts


def download_sii_bulk() -> Optional[Path]:
    """
    Download SII bulk CSV file.
    Returns path to downloaded file, or None if download fails.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / "sii_nominapj.csv"

    logger.info(f"Downloading SII bulk file from {SII_CSV_URL}")
    try:
        response = requests.get(SII_CSV_URL, timeout=120, stream=True)
        response.raise_for_status()

        with open(out_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Downloaded SII bulk file to {out_path}")
        return out_path
    except Exception as e:
        logger.error(f"Failed to download SII bulk file: {e}")
        return None


def parse_sii_csv(csv_path: Path, target_ruts: set) -> dict:
    """
    Parse SII CSV file and extract records for target RUTs.
    Returns dict: rut_normalized -> record dict.
    """
    results = {}
    logger.info(f"Parsing SII CSV for {len(target_ruts)} target RUTs...")

    try:
        with open(csv_path, encoding="latin-1", errors="replace") as f:
            # Try to detect delimiter
            sample = f.read(2048)
            f.seek(0)
            delimiter = ";" if sample.count(";") > sample.count(",") else ","

            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                # RUT column may be named differently
                rut_raw = (
                    row.get("RUT", "")
                    or row.get("Rut", "")
                    or row.get("rut", "")
                    or row.get("RUT_EMPRESA", "")
                    or ""
                )
                rut_norm = normalize_rut(str(rut_raw).strip())

                if rut_norm in target_ruts:
                    results[rut_norm] = {
                        "rut": rut_norm,
                        "razon_social": (
                            row.get("RAZON_SOCIAL", "")
                            or row.get("razonSocial", "")
                            or row.get("NOMBRE", "")
                            or ""
                        ).strip(),
                        "actividad": (
                            row.get("ACTIVIDAD_ECONOMICA", "")
                            or row.get("actividad", "")
                            or row.get("GIRO", "")
                            or ""
                        ).strip(),
                        "codigo_actividad": (
                            row.get("COD_ACTIVIDAD", "")
                            or row.get("codigo_actividad", "")
                            or ""
                        ).strip(),
                        "tamano": (
                            row.get("TAMANO_EMPRESA", "")
                            or row.get("tamano", "")
                            or row.get("TAMANHO", "")
                            or ""
                        ).strip(),
                        "region": (
                            row.get("REGION", "")
                            or row.get("region", "")
                            or ""
                        ).strip(),
                        "comuna": (
                            row.get("COMUNA", "")
                            or row.get("comuna", "")
                            or ""
                        ).strip(),
                        "direccion": (
                            row.get("CALLE", "")
                            or row.get("calle", "")
                            or row.get("DIRECCION", "")
                            or ""
                        ).strip(),
                        "_raw": dict(row),
                    }
    except Exception as e:
        logger.error(f"Error parsing SII CSV: {e}")

    return results


def flag_same_address(companies: dict) -> dict:
    """
    Flag companies sharing the same address.
    Adds 'same_address_ruts' list to each flagged company.
    """
    # Build address → ruts mapping
    address_map: dict[str, list] = {}
    for rut, info in companies.items():
        addr = f"{info.get('direccion', '')} {info.get('comuna', '')} {info.get('region', '')}".strip().lower()
        if addr and addr != "  ":
            address_map.setdefault(addr, []).append(rut)

    # Flag companies sharing address
    for rut, info in companies.items():
        addr = f"{info.get('direccion', '')} {info.get('comuna', '')} {info.get('region', '')}".strip().lower()
        sharing = [r for r in address_map.get(addr, []) if r != rut]
        if sharing:
            info["same_address_ruts"] = sharing
            info["flags"] = info.get("flags", []) + ["SAME_ADDRESS"]

    return companies


def main():
    target_ruts = load_all_ruts()
    logger.info(f"Looking up {len(target_ruts)} RUTs in SII bulk file")

    csv_path = download_sii_bulk()
    companies = {}

    if csv_path and csv_path.exists():
        companies = parse_sii_csv(csv_path, target_ruts)
        logger.info(f"Found {len(companies)} matching companies in SII data")
    else:
        logger.warning("SII bulk file not available; creating empty results")

    # Add placeholder entries for RUTs not found in SII
    for rut in target_ruts:
        if rut not in companies:
            companies[rut] = {
                "rut": rut,
                "razon_social": "",
                "actividad": "",
                "codigo_actividad": "",
                "tamano": "",
                "region": "",
                "comuna": "",
                "direccion": "",
                "not_found": True,
            }

    companies = flag_same_address(companies)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "fetchedAt": utc_now_iso(),
        "totalRuts": len(target_ruts),
        "foundCount": sum(1 for c in companies.values() if not c.get("not_found")),
        "companies": companies,
    }

    out_path = OUTPUT_DIR / "companies.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    logger.info(f"Saved SII data to {out_path}")
    logger.info("SII scraping complete.")


if __name__ == "__main__":
    main()
