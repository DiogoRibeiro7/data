"""Offline integrity and interpretation checks for the INE rent snapshot."""

from __future__ import annotations

import hashlib
import json
import unittest
from collections import Counter
from decimal import Decimal
from pathlib import Path

import yaml

from data_registry import RegistryClient

ROOT = Path(__file__).resolve().parents[1]
DATASET_ID = "ine-portugal-new-lease-rents"
DATASET = ROOT / "datasets" / DATASET_ID
OBSERVATIONS = "raw/ine_0014698_S7A2025_2026-10-30.json"
INDICATOR_METADATA = "raw/ine_0014698_metadata_2026-11-16.json"
METHODOLOGY = "raw/ine_0014698_methodology_2026-11-16.html"
IDENTITIES = {
    OBSERVATIONS: (91363, "e19aa7476bc3c21f0525b753b774c8a71f87e6e02bfb049adffcb43607377285"),
    INDICATOR_METADATA: (
        150884, "a3f73b35775d909322f44aecd21f667d6a54180e1e3fb1e012dae1d2829e609b"
    ),
    METHODOLOGY: (8819, "636de2e18744e021e783a0378679ab2f250c60ebbd4193a478d98d26b724ec1a"),
}


class IneNewLeaseRentsTests(unittest.TestCase):
    """Keep the historical response and later interpretation metadata distinct."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.registry_metadata = yaml.safe_load(
            (DATASET / "metadata.yaml").read_text(encoding="utf-8")
        )
        (cls.observation,) = json.loads((DATASET / OBSERVATIONS).read_bytes())
        (cls.indicator,) = json.loads((DATASET / INDICATOR_METADATA).read_bytes())
        cls.rows = cls.observation["Dados"]["2025"]
        cls.categories = [
            category
            for group in cls.indicator["Dimensoes"]["Categoria_Dim"]
            for categories in group.values()
            for category in categories
            if category["dim_num"] == "2"
        ]

    def test_exact_artifacts_and_redistribution(self) -> None:
        """Both the promoted response and companion bytes remain unchanged."""
        declared = {item["path"]: item for item in self.registry_metadata["files"]}
        self.assertEqual(set(declared), set(IDENTITIES))
        self.assertEqual(self.registry_metadata["license"]["redistribution"], "allowed")
        self.assertEqual(self.registry_metadata["lineage"], [])
        for path, (size, digest) in IDENTITIES.items():
            with self.subTest(path=path):
                raw = (DATASET / path).read_bytes()
                self.assertEqual(len(raw), size)
                self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
                self.assertEqual(declared[path]["sha256"], digest)
                self.assertEqual(declared[path]["role"], "raw")

    def test_period_methodology_and_separate_acquisitions(self) -> None:
        """The metadata covers more years but cannot expand the observation scope."""
        self.assertEqual(self.observation["IndicadorCod"], "0014698")
        self.assertEqual(self.indicator["IndicadorCod"], "0014698")
        self.assertEqual(set(self.observation["Dados"]), {"2025"})
        self.assertEqual(self.observation["DataExtracao"], "2026-10-30T15:16:42.184Z")
        self.assertEqual(self.indicator["DataExtracao"], "2026-11-16T08:56:09.906Z")
        self.assertEqual(self.observation["DataUltimoAtualizacao"], "2026-09-29")
        self.assertEqual(self.indicator["DataUltimaAtualizacao"], "2026-09-29")
        self.assertEqual(self.indicator["Periodic"], "Anual")
        self.assertEqual(self.indicator["UnidadeMedida"], "Euro/ Metro quadrado (€/ m²)")
        self.assertEqual(self.indicator["Potencia10"], "0")
        self.assertEqual(self.indicator["PrecisaoDecimal"], "2")
        self.assertIn("Metodologia 2026", self.indicator["IndicadorNome"])
        dimensions = {
            item["dim_num"]: item for item in self.indicator["Dimensoes"]["Descricao_Dim"]
        }
        self.assertEqual(set(dimensions), {"1", "2"})
        self.assertEqual(dimensions["2"]["versao"], "05433")
        self.assertIn("NUTS - 2024", dimensions["2"]["abrv"])
        self.assertIn("revista", dimensions["1"]["nota_dsg"])

    def test_codebook_coverage_labels_and_unique_cells(self) -> None:
        """All source cells resolve to the pinned codebook without guessing levels."""
        codes = {item["categ_cod"]: item for item in self.categories}
        self.assertEqual(len(codes), len(self.categories))
        self.assertEqual(len(self.rows), 638)
        self.assertEqual(len({row["geocod"] for row in self.rows}), 638)
        self.assertEqual(set(codes), {row["geocod"] for row in self.rows})
        self.assertEqual(
            Counter(item["categ_nivel"] for item in self.categories),
            {"1": 1, "2": 3, "3": 9, "4": 26, "5": 308, "6": 291},
        )
        for row in self.rows:
            with self.subTest(geography=row["geocod"]):
                self.assertIsInstance(row["geocod"], str)
                self.assertEqual(row["geodsg"], codes[row["geocod"]]["categ_dsg"])

    def test_decimal_values_and_null_flags(self) -> None:
        """Null/non-applicable cells remain distinct from zero and numeric values."""
        codes = {item["categ_cod"]: item for item in self.categories}
        missing = Counter()
        numeric = 0
        for row in self.rows:
            with self.subTest(geography=row["geocod"]):
                if "valor" not in row:
                    self.assertEqual(row["sinal_conv"], "-")
                    self.assertEqual(row["sinal_conv_desc"], "Dado nulo ou não aplicável")
                    self.assertEqual(row["ind_string"], "-")
                    missing[codes[row["geocod"]]["categ_nivel"]] += 1
                else:
                    self.assertIsInstance(row["valor"], str)
                    value = Decimal(row["valor"])
                    self.assertTrue(value.is_finite())
                    self.assertGreaterEqual(value, 0)
                    self.assertEqual(value, value.quantize(Decimal("0.01")))
                    self.assertNotIn("sinal_conv", row)
                    numeric += 1
        self.assertEqual(numeric, 487)
        self.assertEqual(missing, {"5": 61, "6": 90})

    def test_information_page_keeps_source_inconsistency(self) -> None:
        """Do not silently repair the sales wording under the rent indicator."""
        page = (DATASET / METHODOLOGY).read_text(encoding="utf-8")
        self.assertIn("0014698", page)
        self.assertIn("rendas de novos contratos", page)
        self.assertIn("Mediana do valor das vendas", page)

    def test_handoff_includes_all_interpretation_artifacts(self) -> None:
        """A metadata plan carries every companion hash, not just observation bytes."""
        # This synthetic pin tests plan construction only; it asserts no Git identity.
        plan = RegistryClient(ROOT).handoff(
            DATASET_ID, commit="0123456789abcdef0123456789abcdef01234567", verify_local=True
        ).to_mapping()
        self.assertTrue(plan["local_bytes_verified"])
        self.assertFalse(plan["checkout_identity_verified"])
        self.assertEqual(len(plan["objects"]), 3)
        self.assertEqual(
            {item["sha256"] for item in plan["objects"]},
            {digest for _, digest in IDENTITIES.values()},
        )


if __name__ == "__main__":
    unittest.main()
