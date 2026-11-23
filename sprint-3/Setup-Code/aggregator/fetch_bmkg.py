#!/usr/bin/env python3
"""
HyperEvac System - Prototipe Siklus 1 (MVP Core: API Engine)

Menarik data gempa terbaru dan prakiraan cuaca dari API terbuka BMKG,
menormalisasinya, lalu menampilkan penilaian tingkat bahaya sederhana.

Fitur mitigasi risiko R1 (API publik down/timeout):
  - retry dengan exponential backoff
  - cache lokal sebagai fallback, dengan penanda usia data

CATATAN:
  - Ini prototipe untuk keperluan analisis/tugas, BUKAN sistem peringatan resmi.
  - Aturan tingkat bahaya di bawah adalah heuristik sederhana untuk demonstrasi,
    bukan standar BMKG. Untuk peringatan resmi, rujuk BMKG.
  - Sumber data: BMKG (Badan Meteorologi, Klimatologi, dan Geofisika).
    Sesuai ketentuan BMKG, sumber data wajib dicantumkan pada aplikasi/sistem.
  - Batas akses API cuaca BMKG: 60 permintaan per menit per IP.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

BMKG_GEMPA_URL = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"
BMKG_CUACA_URL = "https://api.bmkg.go.id/publik/prakiraan-cuaca"
ATTRIBUTION = "Sumber data: BMKG (Badan Meteorologi, Klimatologi, dan Geofisika)"

# Tingkat bahaya (heuristik prototipe)
LEVEL_AMAN = "AMAN"
LEVEL_WASPADA = "WASPADA"
LEVEL_SIAGA = "SIAGA"
_LEVEL_ORDER = {LEVEL_AMAN: 0, LEVEL_WASPADA: 1, LEVEL_SIAGA: 2}

# Ambang heuristik (dapat disesuaikan pada evaluasi siklus)
GEMPA_WASPADA_MAG = 5.0
GEMPA_SIAGA_MAG = 6.5
CUACA_SIAGA_DESC = ("hujan lebat", "hujan petir")
CUACA_WASPADA_DESC = ("hujan sedang",)
CUACA_SIAGA_TP_MM = 20.0
CUACA_WASPADA_TP_MM = 5.0

log = logging.getLogger("hyperevac.aggregator")


# --------------------------------------------------------------------------- #
# Model data
# --------------------------------------------------------------------------- #
@dataclass
class Gempa:
    tanggal: str = ""
    jam: str = ""
    datetime_utc: str = ""
    magnitude: float = 0.0
    kedalaman: str = ""
    lintang: str = ""
    bujur: str = ""
    koordinat: str = ""
    wilayah: str = ""
    potensi: str = ""
    dirasakan: str = ""
    level: str = LEVEL_AMAN
    alasan: str = ""


@dataclass
class Prakiraan:
    waktu_lokal: str = ""
    suhu_c: Optional[float] = None
    kelembapan_pct: Optional[float] = None
    curah_hujan_mm: Optional[float] = None
    kecepatan_angin: Optional[float] = None
    arah_angin: str = ""
    cuaca: str = ""
    level: str = LEVEL_AMAN
    alasan: str = ""


@dataclass
class HasilCuaca:
    lokasi: dict = field(default_factory=dict)
    prakiraan: list = field(default_factory=list)
    level_tertinggi: str = LEVEL_AMAN


@dataclass
class Sumber:
    """Metadata pengambilan data, termasuk penanda usia data (fallback cache)."""
    dari_cache: bool = False
    diambil_pada: str = ""
    usia_detik: float = 0.0


# --------------------------------------------------------------------------- #
# Utilitas
# --------------------------------------------------------------------------- #
def _to_float(value: Any) -> Optional[float]:
    """Konversi longgar ke float ('5.3', 5.3, '5,3'); None bila tidak bisa."""
    if value is None:
        return None
    try:
        return float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None


def _max_level(a: str, b: str) -> str:
    return a if _LEVEL_ORDER[a] >= _LEVEL_ORDER[b] else b


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------- #
# Pengambilan data: retry + cache fallback (mitigasi R1)
# --------------------------------------------------------------------------- #
def _default_http_get(url: str, params: Optional[dict], timeout: float) -> Any:
    import requests  # import lazy agar parser dapat diuji tanpa library ini

    resp = requests.get(
        url,
        params=params,
        timeout=timeout,
        headers={"User-Agent": "HyperEvac-Prototype/0.1 (tugas kuliah RPL)"},
    )
    resp.raise_for_status()
    return resp.json()


def _cache_file(cache_dir: Path, name: str) -> Path:
    return cache_dir / f"{name}.json"


def _save_cache(cache_dir: Path, name: str, payload: Any) -> None:
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        record = {"diambil_pada": _now_iso(), "payload": payload}
        _cache_file(cache_dir, name).write_text(
            json.dumps(record, ensure_ascii=False), encoding="utf-8"
        )
    except OSError as exc:
        log.warning("Gagal menulis cache %s: %s", name, exc)


def _load_cache(cache_dir: Path, name: str) -> Optional[tuple[Any, Sumber]]:
    path = _cache_file(cache_dir, name)
    if not path.exists():
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        diambil = datetime.fromisoformat(record["diambil_pada"])
        usia = (datetime.now(timezone.utc) - diambil).total_seconds()
        return record["payload"], Sumber(True, record["diambil_pada"], max(usia, 0.0))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        log.warning("Cache %s rusak/tidak terbaca: %s", name, exc)
        return None


def fetch_with_fallback(
    name: str,
    url: str,
    params: Optional[dict] = None,
    *,
    cache_dir: Path,
    retries: int = 3,
    backoff: float = 1.5,
    timeout: float = 10.0,
    http_get: Callable[[str, Optional[dict], float], Any] = _default_http_get,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[Any, Sumber]:
    """
    Ambil JSON dari `url`. Gagal -> retry dengan exponential backoff.
    Tetap gagal -> pakai cache terakhir (ditandai dari_cache=True).
    Tanpa cache -> lempar RuntimeError.
    """
    last_error: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            payload = http_get(url, params, timeout)
            _save_cache(cache_dir, name, payload)
            return payload, Sumber(False, _now_iso(), 0.0)
        except Exception as exc:  # noqa: BLE001 - semua kegagalan jaringan ditangani sama
            last_error = exc
            log.warning("Percobaan %d/%d untuk %s gagal: %s", attempt, retries, name, exc)
            if attempt < retries:
                sleep(backoff ** attempt)

    cached = _load_cache(cache_dir, name)
    if cached is not None:
        log.warning("Memakai cache untuk %s (usia %.0f detik)", name, cached[1].usia_detik)
        return cached
    raise RuntimeError(f"Gagal mengambil {name} dan tidak ada cache: {last_error}")


# --------------------------------------------------------------------------- #
# Parser + penilaian bahaya (fungsi murni, mudah diuji)
# --------------------------------------------------------------------------- #
def nilai_gempa(magnitude: float, potensi: str) -> tuple[str, str]:
    potensi_l = (potensi or "").lower()
    ada_tsunami = "tsunami" in potensi_l and "tidak berpotensi" not in potensi_l
    if ada_tsunami:
        return LEVEL_SIAGA, "Berpotensi tsunami"
    if magnitude >= GEMPA_SIAGA_MAG:
        return LEVEL_SIAGA, f"Magnitudo {magnitude} >= {GEMPA_SIAGA_MAG}"
    if magnitude >= GEMPA_WASPADA_MAG:
        return LEVEL_WASPADA, f"Magnitudo {magnitude} >= {GEMPA_WASPADA_MAG}"
    return LEVEL_AMAN, "Di bawah ambang"


def parse_gempa(payload: dict) -> Gempa:
    """Format autogempa.json: {"Infogempa": {"gempa": {...}}}."""
    try:
        g = payload["Infogempa"]["gempa"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Struktur autogempa.json tidak dikenali") from exc

    mag = _to_float(g.get("Magnitude")) or 0.0
    potensi = str(g.get("Potensi", ""))
    level, alasan = nilai_gempa(mag, potensi)
    return Gempa(
        tanggal=str(g.get("Tanggal", "")),
        jam=str(g.get("Jam", "")),
        datetime_utc=str(g.get("DateTime", "")),
        magnitude=mag,
        kedalaman=str(g.get("Kedalaman", "")),
        lintang=str(g.get("Lintang", "")),
        bujur=str(g.get("Bujur", "")),
        koordinat=str(g.get("Coordinates", "")),
        wilayah=str(g.get("Wilayah", "")),
        potensi=potensi,
        dirasakan=str(g.get("Dirasakan", "")),
        level=level,
        alasan=alasan,
    )


def nilai_cuaca(deskripsi: str, curah_hujan: Optional[float]) -> tuple[str, str]:
    d = (deskripsi or "").lower()
    tp = curah_hujan or 0.0
    if any(k in d for k in CUACA_SIAGA_DESC) or tp >= CUACA_SIAGA_TP_MM:
        return LEVEL_SIAGA, f"Cuaca '{deskripsi}', curah hujan {tp} mm"
    if any(k in d for k in CUACA_WASPADA_DESC) or tp >= CUACA_WASPADA_TP_MM:
        return LEVEL_WASPADA, f"Cuaca '{deskripsi}', curah hujan {tp} mm"
    return LEVEL_AMAN, "Di bawah ambang"


def parse_cuaca(payload: dict) -> HasilCuaca:
    """
    Format prakiraan-cuaca: data[0].cuaca berupa list hari, tiap hari
    berisi list prakiraan per 3 jam. Field diakses defensif karena
    struktur respons dapat berubah.
    """
    if not isinstance(payload, dict):
        raise ValueError("Payload cuaca bukan objek JSON")
    data = payload.get("data")
    if not isinstance(data, list) or not data:
        raise ValueError("Struktur prakiraan-cuaca tidak dikenali (data kosong)")

    entry = data[0] or {}
    lokasi = payload.get("lokasi") or entry.get("lokasi") or {}
    hasil = HasilCuaca(lokasi=lokasi)

    for hari in entry.get("cuaca") or []:
        for p in hari or []:
            desc = str(p.get("weather_desc", ""))
            tp = _to_float(p.get("tp"))
            level, alasan = nilai_cuaca(desc, tp)
            hasil.prakiraan.append(
                Prakiraan(
                    waktu_lokal=str(p.get("local_datetime", "")),
                    suhu_c=_to_float(p.get("t")),
                    kelembapan_pct=_to_float(p.get("hu")),
                    curah_hujan_mm=tp,
                    kecepatan_angin=_to_float(p.get("ws")),
                    arah_angin=str(p.get("wd", "")),
                    cuaca=desc,
                    level=level,
                    alasan=alasan,
                )
            )
            hasil.level_tertinggi = _max_level(hasil.level_tertinggi, level)
    return hasil


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv()
    except ImportError:
        pass


def _fmt_sumber(s: Sumber) -> str:
    if s.dari_cache:
        return f"CACHE (usia {s.usia_detik / 60:.0f} menit, diambil {s.diambil_pada})"
    return "LIVE"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="HyperEvac - prototipe agregator data BMKG (Siklus 1)")
    p.add_argument("--adm4", default=os.getenv("BMKG_ADM4", ""),
                   help="Kode wilayah administrasi tingkat IV (mis. 31.71.03.1001). Default: env BMKG_ADM4")
    p.add_argument("--cache-dir", default=os.getenv("CACHE_DIR", ".cache"), help="Folder cache lokal")
    p.add_argument("--timeout", type=float, default=float(os.getenv("HTTP_TIMEOUT", "10")))
    p.add_argument("--retries", type=int, default=int(os.getenv("HTTP_RETRIES", "3")))
    p.add_argument("--json", action="store_true", help="Keluaran JSON, bukan tabel teks")
    p.add_argument("--skip-gempa", action="store_true")
    p.add_argument("--skip-cuaca", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    _load_dotenv_if_available()
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    cache_dir = Path(args.cache_dir)
    keluaran: dict[str, Any] = {"atribusi": ATTRIBUTION}
    exit_code = 0

    if not args.skip_gempa:
        try:
            payload, sumber = fetch_with_fallback(
                "autogempa", BMKG_GEMPA_URL, None,
                cache_dir=cache_dir, retries=args.retries, timeout=args.timeout,
            )
            keluaran["gempa"] = {"data": asdict(parse_gempa(payload)), "sumber": asdict(sumber)}
        except (RuntimeError, ValueError) as exc:
            keluaran["gempa"] = {"error": str(exc)}
            exit_code = 1

    if not args.skip_cuaca:
        if not args.adm4:
            keluaran["cuaca"] = {"error": "Kode wilayah kosong. Isi --adm4 atau BMKG_ADM4 di .env"}
            exit_code = 1
        else:
            try:
                payload, sumber = fetch_with_fallback(
                    f"cuaca_{args.adm4}", BMKG_CUACA_URL, {"adm4": args.adm4},
                    cache_dir=cache_dir, retries=args.retries, timeout=args.timeout,
                )
                keluaran["cuaca"] = {"data": asdict(parse_cuaca(payload)), "sumber": asdict(sumber)}
            except (RuntimeError, ValueError) as exc:
                keluaran["cuaca"] = {"error": str(exc)}
                exit_code = 1

    if args.json:
        print(json.dumps(keluaran, ensure_ascii=False, indent=2))
        return exit_code

    print("=" * 64)
    print("HYPEREVAC - Prototipe Siklus 1 (bukan peringatan resmi)")
    print("=" * 64)

    g = keluaran.get("gempa")
    if g:
        print("\n[GEMPA TERBARU]")
        if "error" in g:
            print(f"  ERROR: {g['error']}")
        else:
            d, s = g["data"], g["sumber"]
            print(f"  Sumber data : {_fmt_sumber(Sumber(**s))}")
            print(f"  Waktu       : {d['tanggal']} {d['jam']}")
            print(f"  Magnitudo   : {d['magnitude']}   Kedalaman: {d['kedalaman']}")
            print(f"  Lokasi      : {d['wilayah']}")
            print(f"  Potensi     : {d['potensi']}")
            print(f"  Tingkat     : {d['level']}  ({d['alasan']})")

    c = keluaran.get("cuaca")
    if c:
        print("\n[PRAKIRAAN CUACA]")
        if "error" in c:
            print(f"  ERROR: {c['error']}")
        else:
            d, s = c["data"], c["sumber"]
            lok = d["lokasi"] or {}
            nama = ", ".join(str(lok[k]) for k in ("desa", "kecamatan", "kotkab", "provinsi") if lok.get(k))
            print(f"  Sumber data : {_fmt_sumber(Sumber(**s))}")
            print(f"  Lokasi      : {nama or '(tidak tersedia)'}")
            print(f"  Tingkat maks: {d['level_tertinggi']}")
            print("  Waktu lokal          Cuaca                 Hujan(mm)  Tingkat")
            for p in d["prakiraan"][:8]:
                hujan = "-" if p["curah_hujan_mm"] is None else f"{p['curah_hujan_mm']:g}"
                print(f"  {p['waktu_lokal']:<20} {p['cuaca']:<21} {hujan:<10} {p['level']}")

    print(f"\n{ATTRIBUTION}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
