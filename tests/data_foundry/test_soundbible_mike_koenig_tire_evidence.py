from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'configs/data_foundry/soundbible_mike_koenig_tire.v1.json'
WORKFLOW = ROOT / '.github/workflows/mk1-soundbible-mike-koenig-tire-materialization.yml'
CANONICAL_WORKFLOW = ROOT / '.github/workflows/mk1-canonical-ledger.yml'
SCRIPT = ROOT / 'scripts/data_foundry/materialize_soundbible_mike_koenig_tire.py'
AUGMENTOR = ROOT / 'scripts/data_foundry/augment_canonical_ledger_with_soundbible_tire.py'
SOURCE_POLICY = ROOT / 'configs/data_foundry/dataset_certification.v1.json'
FAMILY_POLICY = ROOT / 'configs/data_foundry/underlying_source_families.v1.json'


class SoundBibleMikeKoenigTireEvidenceContractTests(unittest.TestCase):
    def test_manifest_is_evidence_only_origin_bound_and_one_family(self) -> None:
        payload = json.loads(MANIFEST.read_text(encoding='utf-8'))
        self.assertEqual(payload['phase'], 'EVIDENCE_MATERIALIZATION_ONLY')
        self.assertEqual(payload['target'], 'TIRE_SQUEAL')
        self.assertEqual(payload['source_id_candidate'], 'echo-soundbible-mike-koenig-tire-v1')
        self.assertEqual(payload['underlying_source_family_candidate'], 'SOUNDBIBLE_MIKE_KOENIG')
        self.assertEqual(payload['origin']['declared_license'], 'CC-BY-3.0')
        self.assertEqual(payload['transport']['declared_license'], 'CC-BY-3.0')
        self.assertEqual(payload['asset']['semantic_candidate'], 'tire_squeal')
        self.assertEqual(payload['asset']['expected_audio_file_count'], 3)
        self.assertEqual(payload['asset']['recording_family_candidate'], 'soundbible:mike-koenig:tires-squealing-1178')
        self.assertIn('zero corpus', payload['policy'].casefold())
        self.assertTrue(any('one candidate recording family' in value.casefold() for value in payload['stop_lines']))

    def test_script_materializes_all_members_instead_of_selecting_first(self) -> None:
        text = SCRIPT.read_text(encoding='utf-8')
        self.assertIn('assets = [materialize_member(', text)
        self.assertIn('exact_pcm_identity_groups', text)
        self.assertNotIn('audio_path = audio_files[0]', text)
        self.assertNotIn('"asset": {', text)

    def test_materialization_is_sha_bound_and_never_rebases(self) -> None:
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('ref: ${{ github.sha }}', text)
        self.assertIn('git reset --hard "${GITHUB_SHA}"', text)
        self.assertIn('git fetch origin main', text)
        self.assertIn('refusing to persist stale evidence', text)
        self.assertNotIn('git pull --rebase', text)
        self.assertIn("assert len(assets) == 3", text)

    def test_certified_lane_reaches_canonical_ledger_without_inflating_origin(self) -> None:
        workflow = CANONICAL_WORKFLOW.read_text(encoding='utf-8')
        augmentor = AUGMENTOR.read_text(encoding='utf-8')
        source_policy = json.loads(SOURCE_POLICY.read_text(encoding='utf-8'))
        family_policy = json.loads(FAMILY_POLICY.read_text(encoding='utf-8'))
        source_id = 'echo-soundbible-mike-koenig-tire-v1'

        self.assertIn('soundbible_mike_koenig_tire.v1.json', workflow)
        self.assertIn('soundbible-mike-koenig-tire-materialization.json', workflow)
        self.assertIn('augment_canonical_ledger_with_soundbible_tire.py', workflow)
        self.assertEqual(source_policy['sources'][source_id]['profiles']['release_safe'], 'ALLOW')
        self.assertEqual(family_policy['sources'][source_id]['family'], 'SOUNDBIBLE_MIKE_KOENIG')
        self.assertTrue(family_policy['sources'][source_id]['diversity_credit'])
        self.assertIn('len(assets) != 3', augmentor)
        self.assertIn('RECORDING_GROUP = "soundbible:mike-koenig:tires-squealing-1178"', augmentor)
        self.assertIn('LICENSE_ID = "CC-BY-3.0"', augmentor)


if __name__ == '__main__':
    unittest.main()
