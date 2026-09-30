"""Uji offline (tanpa jaringan) untuk parser, penilaian bahaya, dan fallback cache."""
import json
import tempfile
import unittest
from pathlib import Path

from aggregator.fetch_bmkg import (
    LEVEL_AMAN, LEVEL_SIAGA, LEVEL_WASPADA,
    fetch_with_fallback, nilai_cuaca, nilai_gempa, parse_cuaca, parse_gempa,
)

SAMPLE_GEMPA = {
    "Infogempa": {
        "gempa": {
            "Tanggal": "01 Jan 2026", "Jam": "10:00:00 WIB",
            "DateTime": "2026-01-01T03:00:00+00:00", "Coordinates": "-6.50,106.50",
            "Lintang": "6.50 LS", "Bujur": "106.50 BT", "Magnitude": "5.3",
            "Kedalaman": "10 km", "Wilayah": "Data contoh",
            "Potensi": "Tidak berpotensi tsunami", "Dirasakan": "III Data contoh",
        }
    }
}

SAMPLE_CUACA = {
    "lokasi": {"desa": "Desa Contoh", "kecamatan": "Kec. Contoh", "kotkab": "Kota Contoh", "provinsi": "Provinsi Contoh"},
    "data": [{
        "cuaca": [[
            {"local_datetime": "2026-01-01 07:00:00", "t": 27, "hu": 83, "tp": 0,
             "ws": 7.3, "wd": "SW", "weather_desc": "Berawan"},
            {"local_datetime": "2026-01-01 10:00:00", "t": 25, "hu": 90, "tp": 6.5,
             "ws": 9.0, "wd": "S", "weather_desc": "Hujan Sedang"},
            {"local_datetime": "2026-01-01 13:00:00", "t": 24, "hu": 95, "tp": 25,
             "ws": 12.0, "wd": "S", "weather_desc": "Hujan Lebat"},
        ]]
    }],
}


class TestGempa(unittest.TestCase):
    def test_parse_field_dan_level(self):
        g = parse_gempa(SAMPLE_GEMPA)
        self.assertEqual(g.magnitude, 5.3)
        self.assertEqual(g.level, LEVEL_WASPADA)

    def test_struktur_salah(self):
        with self.assertRaises(ValueError):
            parse_gempa({"foo": "bar"})

    def test_ambang(self):
        self.assertEqual(nilai_gempa(4.0, "Tidak berpotensi tsunami")[0], LEVEL_AMAN)
        self.assertEqual(nilai_gempa(6.8, "Tidak berpotensi tsunami")[0], LEVEL_SIAGA)

    def test_potensi_tsunami(self):
        self.assertEqual(nilai_gempa(5.0, "Berpotensi tsunami")[0], LEVEL_SIAGA)
        self.assertEqual(nilai_gempa(5.0, "Tidak berpotensi tsunami")[0], LEVEL_WASPADA)


class TestCuaca(unittest.TestCase):
    def test_parse_dan_level_tertinggi(self):
        h = parse_cuaca(SAMPLE_CUACA)
        self.assertEqual(len(h.prakiraan), 3)
        self.assertEqual(h.level_tertinggi, LEVEL_SIAGA)
        self.assertEqual(h.prakiraan[0].level, LEVEL_AMAN)
        self.assertEqual(h.prakiraan[1].level, LEVEL_WASPADA)

    def test_data_kosong(self):
        with self.assertRaises(ValueError):
            parse_cuaca({"data": []})

    def test_nilai_tp_none(self):
        self.assertEqual(nilai_cuaca("Cerah", None)[0], LEVEL_AMAN)


class TestFallback(unittest.TestCase):
    def test_retry_lalu_sukses(self):
        panggilan = {"n": 0}

        def flaky(url, params, timeout):
            panggilan["n"] += 1
            if panggilan["n"] < 3:
                raise TimeoutError("timeout")
            return SAMPLE_GEMPA

        with tempfile.TemporaryDirectory() as d:
            payload, sumber = fetch_with_fallback(
                "x", "http://contoh", cache_dir=Path(d), retries=3,
                http_get=flaky, sleep=lambda s: None,
            )
        self.assertEqual(panggilan["n"], 3)
        self.assertFalse(sumber.dari_cache)
        self.assertEqual(payload, SAMPLE_GEMPA)

    def test_gagal_pakai_cache(self):
        def selalu_gagal(url, params, timeout):
            raise TimeoutError("down")

        with tempfile.TemporaryDirectory() as d:
            cache = Path(d)
            (cache / "x.json").write_text(json.dumps({
                "diambil_pada": "2026-01-01T00:00:00+00:00", "payload": SAMPLE_GEMPA,
            }), encoding="utf-8")
            payload, sumber = fetch_with_fallback(
                "x", "http://contoh", cache_dir=cache, retries=2,
                http_get=selalu_gagal, sleep=lambda s: None,
            )
        self.assertTrue(sumber.dari_cache)
        self.assertGreater(sumber.usia_detik, 0)
        self.assertEqual(payload, SAMPLE_GEMPA)

    def test_gagal_tanpa_cache(self):
        def selalu_gagal(url, params, timeout):
            raise TimeoutError("down")

        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):
                fetch_with_fallback(
                    "x", "http://contoh", cache_dir=Path(d), retries=2,
                    http_get=selalu_gagal, sleep=lambda s: None,
                )


if __name__ == "__main__":
    unittest.main()
