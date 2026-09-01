"""
Comprehensive Local LLM Classifier Unit Tests.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from pydantic import ValidationError

from main.cli import main
from main.utils.kb_engine.classifier import (
    DEFAULT_LOCAL_MODEL,
    DocumentTaggingResult,
    FakeModelAdapter,
    LocalLLMClassifier,
    MLXAdapter,
    OllamaAdapter,
    _consolidate_window_results,
    _split_into_windows,
    apply_tags_to_file,
    classify_content,
    classify_document,
)
from main.utils.kb_engine.engine import KBEngine
from main.utils.kb_engine.errors import (
    MissingDependencyError,
    ModelConnectionError,
    ModelInferenceError,
)
from main.utils.kb_engine.taxonomy import TaxonomyRegistry


class TestClassifierSuite(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.kb_dir = Path(self.temp_dir.name) / "Knowledge_base"
        self.kb_dir.mkdir()
        TaxonomyRegistry.generate_taxonomy_markdown(self.kb_dir)
        self.taxonomy = TaxonomyRegistry(self.kb_dir)

    def test_pydantic_schema_validation_and_rejection(self) -> None:
        """1. Exact Pydantic rejection of invented categories, topics, and aliases."""
        valid_res = DocumentTaggingResult(
            category="training",
            topics=["VO2max_and_aerobic_hiit", "Zone2_and_endurance_base"],
            summary="A high quality aerobic training guide.",
            confidence_score=0.95,
        )
        self.assertEqual(valid_res.category, "training")
        self.assertEqual(len(valid_res.topics), 2)

        # Non-canonical category rejected
        with self.assertRaises(ValidationError):
            DocumentTaggingResult(
                category="invented_domain",
                topics=["Zone2_and_endurance_base"],
                summary="Invalid category test.",
            )

        # Non-canonical topic rejected (no silent alias acceptance)
        with self.assertRaises(ValidationError):
            DocumentTaggingResult(
                category="training",
                topics=["completely_fake_topic"],
                summary="Invalid topic test.",
            )

        with self.assertRaises(ValidationError):
            DocumentTaggingResult(
                category="training",
                topics=[],
                summary="Empty topic test.",
            )

        schema = DocumentTaggingResult.json_schema_for_taxonomy(self.taxonomy)
        self.assertEqual(
            set(schema["properties"]["category"]["enum"]),
            set(self.taxonomy.categories()),
        )
        self.assertEqual(
            set(schema["properties"]["topics"]["items"]["enum"]),
            set(self.taxonomy.topics()),
        )

    def test_prompt_coverage_from_registry(self) -> None:
        """2. Prompt coverage derived from all 36 registry topics and 4 categories."""
        classifier = LocalLLMClassifier(
            adapter=FakeModelAdapter(), taxonomy=self.taxonomy, kb_dir=self.kb_dir
        )
        prompt = classifier.build_prompt(
            title="Sample Article",
            content="Sample Content",
            existing_summary="Existing abstract.",
        )

        for cat in self.taxonomy.categories():
            self.assertIn(f"### Category: `{cat}`", prompt)

        for topic in self.taxonomy.topics():
            self.assertIn(f"`{topic}`", prompt)

    def test_cross_domain_bottom_up_categorization(self) -> None:
        """3. Cross-domain topics with bottom-up primary-category selection."""
        adapter = FakeModelAdapter(
            default_response={
                "category": "training",
                "topics": [
                    "VO2max_and_aerobic_hiit",
                    "Threshold_intervals",
                    "VO2max_and_aerobic_kinetics",
                    "Cardiovascular_and_hemodynamics",
                ],
                "summary": "4x8min interval protocols expand cardiac stroke volume.",
                "confidence_score": 0.98,
                "topic_evidence": {
                    "VO2max_and_aerobic_hiit": "4x8min prescription.",
                    "Cardiovascular_and_hemodynamics": "Cardiac stroke volume.",
                },
            }
        )
        classifier = LocalLLMClassifier(
            adapter=adapter, taxonomy=self.taxonomy, kb_dir=self.kb_dir
        )
        res = classifier.classify_content(
            content="4x8min intervals at 108% FTP expand stroke volume.",
            title="4x8min HIIT Guide",
        )
        self.assertEqual(res.category, "training")
        self.assertEqual(len(res.topics), 4)
        self.assertIn("Cardiovascular_and_hemodynamics", res.topics)

    def test_evidence_after_4000_chars_and_windowing(self) -> None:
        """4. Evidence occurring after character 4,000 and in the final window."""
        filler = "Standard endurance background information.\n\n" * 150
        content = (
            "# Large Endurance Guide\n\n"
            + filler
            + "## Late Section: Hydration and Electrolytes\n\n"
            + "Sodium bicarbonate and electrolyte loading improves plasma volume."
        )
        self.assertGreater(len(content), 5000)

        windows = _split_into_windows(content, max_window_chars=3000)
        self.assertGreater(len(windows), 1)
        combined_text = "".join(windows)
        self.assertIn("Sodium bicarbonate and electrolyte", combined_text)

        responses = {
            "Standard endurance background": {
                "category": "training",
                "topics": ["Zone2_and_endurance_base"],
                "summary": "Endurance base riding.",
                "confidence_score": 0.9,
                "topic_evidence": {"Zone2_and_endurance_base": "base info"},
            },
            "Sodium bicarbonate": {
                "category": "nutrition",
                "topics": [
                    "Hydration_and_electrolyte_balance",
                    "Ergogenic_supplements_and_buffers",
                ],
                "summary": "Electrolytes and sodium bicarbonate buffers.",
                "confidence_score": 0.96,
                "topic_evidence": {
                    "Hydration_and_electrolyte_balance": "Sodium loading."
                },
            },
        }
        classifier = LocalLLMClassifier(
            adapter=FakeModelAdapter(responses_by_keyword=responses),
            taxonomy=self.taxonomy,
            kb_dir=self.kb_dir,
            max_window_chars=3000,
        )
        res = classifier.classify_content(content, title="Large Guide")
        self.assertIn("Hydration_and_electrolyte_balance", res.topics)
        self.assertIn("Zone2_and_endurance_base", res.topics)

    def test_long_document_multi_window_consolidation_with_more_than_eight_topics(
        self,
    ) -> None:
        """Test consolidation when candidate topics exceed 8 and synthesize summary."""
        w1 = DocumentTaggingResult(
            category="physiology",
            topics=[
                "Mitochondrial_and_cellular_adaptation",
                "Lactate_kinetics_and_metabolism",
                "Substrate_utilization_and_fat_oxidation",
                "Cardiovascular_and_hemodynamics",
            ],
            summary="Window 1 examines cellular bioenergetics.",
            confidence_score=0.9,
            topic_evidence={
                "Mitochondrial_and_cellular_adaptation": "PGC-1alpha activation.",
                "Lactate_kinetics_and_metabolism": "MCT1 transporters.",
            },
        )
        w2 = DocumentTaggingResult(
            category="nutrition",
            topics=[
                "Carbohydrate_fueling_and_gut_training",
                "Hydration_and_electrolyte_balance",
                "Ergogenic_supplements_and_buffers",
                "Lactate_kinetics_and_metabolism",
            ],
            summary="Window 2 examines intra-workout fueling.",
            confidence_score=0.95,
            topic_evidence={
                "Carbohydrate_fueling_and_gut_training": "90g/hr carbs.",
                "Lactate_kinetics_and_metabolism": "Lactate clearance in liver.",
            },
        )
        w3 = DocumentTaggingResult(
            category="training",
            topics=[
                "Threshold_intervals",
                "VO2max_and_aerobic_hiit",
                "Zone2_and_endurance_base",
                "Pacing_and_execution_dynamics",
            ],
            summary="Window 3 details interval prescriptions.",
            confidence_score=0.98,
            topic_evidence={
                "Threshold_intervals": "4x10min sweet spot.",
                "VO2max_and_aerobic_hiit": "4x8min intervals.",
            },
        )

        consolidated = _consolidate_window_results([w1, w2, w3], self.taxonomy)

        # Maximum 8 topics enforced
        self.assertLessEqual(len(consolidated.topics), 8)
        # Recurring topic Lactate_kinetics_and_metabolism ranked at top
        self.assertEqual(consolidated.topics[0], "Lactate_kinetics_and_metabolism")
        # Merged evidence contains both window snippets
        self.assertIn(
            "MCT1 transporters",
            consolidated.topic_evidence["Lactate_kinetics_and_metabolism"],
        )
        self.assertIn(
            "Lactate clearance in liver",
            consolidated.topic_evidence["Lactate_kinetics_and_metabolism"],
        )
        # Document-wide synthesized summary incorporates takeaways across windows
        self.assertIn("Window 1", consolidated.summary)
        self.assertIn("Window 2", consolidated.summary)

    def test_mlx_adapter_schema_and_sampler_wiring(self) -> None:
        """5. MLX schema and constrained sampler/logits_processor wiring."""
        adapter = MLXAdapter(model_name=DEFAULT_LOCAL_MODEL)
        with (
            patch.dict("sys.modules", {"mlx_lm": None}),
            self.assertRaises(MissingDependencyError),
        ):
            adapter.generate("Test prompt", schema=DocumentTaggingResult)

        mock_mlx = MagicMock()
        mock_tokenizer = MagicMock()
        mock_tokenizer.apply_chat_template.return_value = "Formatted Chat Prompt"
        mock_mlx.load.return_value = (MagicMock(), mock_tokenizer)
        mock_sample_utils = MagicMock()
        mock_sampler = MagicMock()
        mock_processors = MagicMock()
        mock_sample_utils.make_sampler.return_value = mock_sampler
        mock_sample_utils.make_logits_processors.return_value = mock_processors
        mock_mlx.sample_utils = mock_sample_utils
        mock_mlx.generate.return_value = json.dumps(
            {
                "category": "physiology",
                "topics": ["FTP_and_functional_metrics"],
                "summary": "Valid MLX output.",
            }
        )

        with patch.dict(
            "sys.modules",
            {"mlx_lm": mock_mlx, "mlx_lm.sample_utils": mock_sample_utils},
        ):
            loaded_adapter = MLXAdapter(model_name="mock-model")
            res_dict = loaded_adapter.generate(
                "Prompt text", schema=DocumentTaggingResult
            )
            self.assertEqual(res_dict["category"], "physiology")
            mock_mlx.generate.assert_called_once()
            # Verify sampler and logits_processors were passed
            call_kwargs = mock_mlx.generate.call_args[1]
            self.assertEqual(call_kwargs["sampler"], mock_sampler)
            self.assertEqual(call_kwargs["logits_processors"], mock_processors)

    def test_ollama_adapter_and_error_translation(self) -> None:
        """6. Ollama JSON parsing, HTTP errors, and validation failures."""
        adapter = OllamaAdapter(host="http://localhost:99999")

        with self.assertRaises(ModelConnectionError):
            adapter.generate("Prompt", schema=DocumentTaggingResult)

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = b'{"message": {"content": "Not JSON"}}'
            mock_urlopen.return_value.__enter__.return_value = mock_resp
            with self.assertRaises(ModelInferenceError):
                adapter.generate("Prompt", schema=DocumentTaggingResult)

    def test_public_apis_and_engine_facade(self) -> None:
        """7. All specified classifier and KBEngine public APIs."""
        article_path = self.kb_dir / "Articles" / "test_api.md"
        article_path.parent.mkdir(parents=True, exist_ok=True)
        article_path.write_text(
            "---\n"
            "title: API Test\n"
            "category: training\n"
            "topics: [Zone2_and_endurance_base]\n"
            "summary: S\n"
            "---\n\n"
            "Content",
            encoding="utf-8",
        )

        fake_adapter = FakeModelAdapter(
            default_response={
                "category": "physiology",
                "topics": ["Lactate_kinetics_and_metabolism"],
                "summary": "Lactate dynamics.",
                "confidence_score": 0.99,
                "topic_evidence": {},
            }
        )

        res1 = classify_content(
            "Lactate body content", adapter=fake_adapter, taxonomy=self.taxonomy
        )
        self.assertEqual(res1.category, "physiology")

        res2 = classify_document(
            article_path,
            kb_dir=self.kb_dir,
            adapter=fake_adapter,
            taxonomy=self.taxonomy,
        )
        self.assertEqual(res2.category, "physiology")

        res3 = apply_tags_to_file(
            article_path,
            dry_run=True,
            kb_dir=self.kb_dir,
            adapter=fake_adapter,
            taxonomy=self.taxonomy,
        )
        self.assertEqual(res3.category, "physiology")

        engine = KBEngine(kb_dir=self.kb_dir)
        e_res1 = engine.classify_content("Content", adapter=fake_adapter)
        self.assertEqual(e_res1.category, "physiology")

        e_res2 = engine.classify_document(article_path, adapter=fake_adapter)
        self.assertEqual(e_res2.category, "physiology")

        e_res3 = engine.apply_tags(article_path, dry_run=True, adapter=fake_adapter)
        self.assertEqual(e_res3.category, "physiology")

    def test_dry_run_immutability(self) -> None:
        """8. Dry-run filesystem immutability."""
        article_path = self.kb_dir / "Articles" / "dry.md"
        article_path.parent.mkdir(parents=True, exist_ok=True)
        orig_content = (
            "---\n"
            "title: Dry Test\n"
            "category: nutrition\n"
            "topics: [Carbohydrate_fueling_and_gut_training]\n"
            "summary: Original summary.\n"
            "---\n\n"
            "Body\n"
        )
        article_path.write_text(orig_content, encoding="utf-8")

        fake_adapter = FakeModelAdapter(
            default_response={
                "category": "training",
                "topics": ["Threshold_intervals"],
                "summary": "New summary.",
                "confidence_score": 0.95,
                "topic_evidence": {},
            }
        )
        engine = KBEngine(kb_dir=self.kb_dir)
        engine.apply_tags(article_path, dry_run=True, adapter=fake_adapter)

        self.assertEqual(article_path.read_text(encoding="utf-8"), orig_content)

    def test_apply_mode_preservation(self) -> None:
        """9. Apply-mode provenance, metadata, body-byte preservation."""
        article_path = self.kb_dir / "Articles" / "apply.md"
        article_path.parent.mkdir(parents=True, exist_ok=True)
        orig_content = (
            "---\n"
            "title: Apply Test\n"
            "language: en\n"
            "category: nutrition\n"
            "topics:\n"
            "  - Carbohydrate_fueling_and_gut_training\n"
            "source: Test Journal\n"
            "author: Dr. Smith\n"
            "date: '2026-05-01'\n"
            "summary: Old summary.\n"
            "key_takeaways:\n"
            "  - Keep this takeaway\n"
            "custom_metadata: custom_val\n"
            "---\n\n"
            "# Heading 1\n\n"
            "Paragraph body.\n"
        )
        article_path.write_text(orig_content, encoding="utf-8")
        os.chmod(article_path, 0o644)

        fake_adapter = FakeModelAdapter(
            default_response={
                "category": "training",
                "topics": ["Threshold_intervals", "Subthreshold_and_tempo"],
                "summary": "Applied new summary.",
                "confidence_score": 0.99,
                "topic_evidence": {},
            }
        )
        engine = KBEngine(kb_dir=self.kb_dir)
        engine.apply_tags(article_path, dry_run=False, adapter=fake_adapter)

        updated_text = article_path.read_text(encoding="utf-8")
        self.assertIn("category: training", updated_text)
        self.assertIn("Threshold_intervals", updated_text)
        self.assertIn("Subthreshold_and_tempo", updated_text)
        self.assertIn("author: Dr. Smith", updated_text)
        self.assertIn("source: Test Journal", updated_text)
        self.assertIn("date: '2026-05-01'", updated_text)
        self.assertIn("custom_metadata: custom_val", updated_text)
        self.assertIn("Keep this takeaway", updated_text)
        self.assertTrue(updated_text.endswith("\n# Heading 1\n\nParagraph body.\n"))
        self.assertEqual(os.stat(article_path).st_mode & 0o777, 0o644)

    def test_cli_modes_tag_and_autotag(self) -> None:
        """10. tag/auto-tag, --dry-run/--apply, whole-KB, and directory CLI modes."""
        sub_dir = self.kb_dir / "Articles" / "sub"
        sub_dir.mkdir(parents=True, exist_ok=True)
        doc1 = sub_dir / "doc1.md"
        doc1.write_text(
            "---\n"
            "title: D1\n"
            "category: nutrition\n"
            "topics: [Carbohydrate_fueling_and_gut_training]\n"
            "summary: S1\n"
            "---\n\n"
            "Body1",
            encoding="utf-8",
        )
        doc2 = self.kb_dir / "Articles" / "doc2.md"
        doc2.write_text(
            "---\n"
            "title: D2\n"
            "category: training\n"
            "topics: [Zone2_and_endurance_base]\n"
            "summary: S2\n"
            "---\n\n"
            "Body2",
            encoding="utf-8",
        )

        mock_response = {
            "category": "training",
            "topics": ["Zone2_and_endurance_base"],
            "summary": "Mock classification.",
            "confidence_score": 1.0,
            "topic_evidence": {},
        }

        out = io.StringIO()
        with patch(
            "main.utils.kb_engine.classifier.MLXAdapter.generate",
            return_value=mock_response,
        ):
            with contextlib.redirect_stdout(out):
                ret = main(["--kb-dir", str(self.kb_dir), "tag", str(doc1)])
            self.assertEqual(ret, 0)
            self.assertIn("Dry-run", out.getvalue())

            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                ret = main(
                    ["--kb-dir", str(self.kb_dir), "auto-tag", str(doc1), "--dry-run"]
                )
            self.assertEqual(ret, 0)
            self.assertIn("Dry-run", out.getvalue())

            ret = main(["--kb-dir", str(self.kb_dir), "tag", str(doc1), "--apply"])
            self.assertEqual(ret, 0)
            self.assertIn("Zone2_and_endurance_base", doc1.read_text(encoding="utf-8"))

            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                ret = main(
                    [
                        "--kb-dir",
                        str(self.kb_dir),
                        "tag",
                        str(sub_dir),
                        "--all",
                        "--dry-run",
                    ]
                )
            self.assertEqual(ret, 0)
            self.assertIn("Processed 1 documents", out.getvalue())

            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                ret = main(["--kb-dir", str(self.kb_dir), "tag", "--all"])
            self.assertEqual(ret, 0)
            self.assertIn("Processed 2 documents", out.getvalue())

    def test_batch_traversal_curated_only(self) -> None:
        """11. Batch traversal limited to curated Markdown Knowledge Sources."""
        (self.kb_dir / "INDEX.md").write_text("# Sitemap", encoding="utf-8")
        curated = self.kb_dir / "Articles" / "curated.md"
        curated.parent.mkdir(parents=True, exist_ok=True)
        curated.write_text(
            "---\n"
            "title: Curated\n"
            "category: training\n"
            "topics: [Zone2_and_endurance_base]\n"
            "summary: S\n"
            "---\n\n"
            "Body",
            encoding="utf-8",
        )

        fake_adapter = FakeModelAdapter()
        engine = KBEngine(kb_dir=self.kb_dir)
        results = engine.apply_tags_all(dry_run=True, adapter=fake_adapter)

        rel_paths = [s.rel_path for s, _ in results]
        self.assertIn("Articles/curated.md", rel_paths)
        self.assertNotIn("INDEX.md", rel_paths)
        self.assertNotIn("TAXONOMY.md", rel_paths)


if __name__ == "__main__":
    unittest.main()
