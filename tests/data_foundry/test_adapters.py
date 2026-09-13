from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from echo.data_foundry.adapters import (
    parse_esc50_metadata,
    parse_fsd50k_ground_truth,
    parse_singapura,
    parse_sonyc_annotations,
    parse_urbansound8k_metadata,
)


class AdapterTests(unittest.TestCase):
    def test_esc50_preserves_source_group(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "esc50.csv"
            path.write_text("filename,fold,target,category,esc10,src_file,take\n1.wav,1,1,siren,False,123,A\n", encoding="utf-8")
            rows = parse_esc50_metadata(path)
            self.assertEqual(rows[0].original_labels, ("siren",))
            self.assertEqual(rows[0].recording_group_id, "esc50:123")

    def test_urbansound_groups_occurrence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "urban.csv"
            path.write_text(
                "slice_file_name,fsID,start,end,salience,fold,classID,class,occurrenceID\n"
                "x.wav,99,0,1,1,3,1,car_horn,2\n",
                encoding="utf-8",
            )
            rows = parse_urbansound8k_metadata(path)
            self.assertEqual(rows[0].recording_group_id, "urbansound8k:99:2")
            self.assertEqual(rows[0].original_labels, ("car_horn",))

    def test_fsd50k_uses_mids_plus_vocabulary_to_preserve_comma_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ground_truth = root / "fsd.csv"
            vocabulary = root / "vocabulary.csv"
            ground_truth.write_text('fname,mids,split\n123,"/m/siren,/m/horn",train\n', encoding="utf-8")
            vocabulary.write_text(
                'index,mid,display_name\n0,/m/siren,Siren\n1,/m/horn,"Vehicle horn, car horn, honking"\n',
                encoding="utf-8",
            )
            rows = parse_fsd50k_ground_truth(
                ground_truth,
                partition="dev",
                vocabulary_csv=vocabulary,
            )
            self.assertEqual(
                rows[0].original_labels,
                ("Siren", "Vehicle horn, car horn, honking"),
            )
            self.assertEqual(rows[0].original_split, "train")

    def test_sonyc_consolidates_presence_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ann.csv"
            path.write_text(
                "audio_filename,sensor_id,split,5-1_car-horn_presence,5-3_siren_presence\n"
                "a.wav,S1,train,1,0\n"
                "a.wav,S1,train,0,1\n",
                encoding="utf-8",
            )
            rows = parse_sonyc_annotations(path)
            self.assertEqual(rows[0].original_labels, ("car-horn", "siren"))

    def test_singapura_reads_strong_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            meta = root / "metadata.csv"
            labels = root / "labels"
            labels.mkdir()
            meta.write_text("filename,sensor_id\na.wav,S1\n", encoding="utf-8")
            (labels / "a.csv").write_text("event_label,onset,offset\n3-1,0.1,0.8\n", encoding="utf-8")
            rows = parse_singapura(meta, labels)
            self.assertEqual(rows[0].original_labels, ("3-1",))
            self.assertEqual(rows[0].recording_group_id, "singapura:S1:a.wav")


if __name__ == "__main__":
    unittest.main()
