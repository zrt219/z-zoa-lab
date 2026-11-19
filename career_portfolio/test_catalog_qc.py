import tempfile
import unittest
from pathlib import Path

from career_portfolio.catalog_qc import describe_catalog


class TestCatalogQC(unittest.TestCase):
    def test_mask_is_descriptive(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "train.csv"
            path.write_text("object_id,l_deg,b_deg,cz_km_s\nA,20,2,3000\nB,40,-15,5000\n", encoding="utf-8")
            report = describe_catalog(path)
            self.assertEqual(report["objects_inside_mask"], 1)
            self.assertEqual(report["objects"], 2)
            self.assertEqual(len(report["catalog_sha256"]), 64)

    def test_holdout_directory_denied(self):
        with self.assertRaisesRegex(ValueError, "HOLDOUT"):
            describe_catalog("datasets/HOLDOUT/vela.csv")

    def test_duplicate_id_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text("object_id,l_deg,b_deg,cz_km_s\nA,20,2,3000\nA,30,3,4000\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                describe_catalog(path)


if __name__ == "__main__":
    unittest.main()
