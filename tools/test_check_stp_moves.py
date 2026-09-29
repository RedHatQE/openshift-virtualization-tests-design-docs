#!/usr/bin/env python3

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from check_stp_moves import validate, validate_base_ref, without_html_tags
from unittest.mock import patch


STUB = """<!-- STP-MOVED-TO: stps/sig-virt/current.md -->

# MOVED

This STP was moved to [the current STP](../sig-virt/current.md).
"""


class CheckStpMovesTest(unittest.TestCase):
    def make_tree(self, stub=STUB, target=True):
        root = Path(tempfile.mkdtemp())
        old = root / "stps/sig-virt/old.md"
        old.parent.mkdir(parents=True)
        old.write_text(stub, encoding="utf-8")
        if target:
            (old.parent / "current.md").write_text("# Current STP\n", encoding="utf-8")
        return root

    def test_valid_stub(self):
        self.assertEqual(validate(self.make_tree()), [])

    def test_missing_target(self):
        self.assertIn("target does not exist", validate(self.make_tree(target=False))[0])

    def test_stub_cannot_target_another_stub(self):
        root = self.make_tree()
        (root / "stps/sig-virt/current.md").write_text(STUB.replace("current.md", "latest.md"), encoding="utf-8")
        (root / "stps/sig-virt/latest.md").write_text("# Current STP\n", encoding="utf-8")
        self.assertIn("another moved stub", validate(root)[0])

    def test_moved_heading_is_required(self):
        self.assertIn("missing '# MOVED' heading", validate(self.make_tree(STUB.replace("# MOVED", "# Old STP")))[0])

    def test_nested_relative_link(self):
        root = Path(tempfile.mkdtemp())
        old = root / "stps/sig-virt/feature/old.md"
        old.parent.mkdir(parents=True)
        old.write_text(STUB.replace("stps/sig-virt/current.md", "stps/sig-virt/feature/current.md").replace("../sig-virt/current.md", "current.md"), encoding="utf-8")
        (old.parent / "current.md").write_text("# Current STP\n", encoding="utf-8")
        self.assertEqual(validate(root), [])

    def test_mixed_fences_and_link_titles(self):
        root = self.make_tree(STUB.replace("[the current STP](../sig-virt/current.md)", "[the current STP](../sig-virt/current.md \"current\")\n\n~~~markdown\n<!-- STP-MOVED-TO: stps/not-a-stub.md -->\n~~~"))
        self.assertEqual(validate(root), [])

    def test_fence_with_trailing_text_does_not_close(self):
        root = self.make_tree(STUB.replace("This STP was moved to [the current STP](../sig-virt/current.md).", "This STP was moved to [the current STP](../sig-virt/current.md).\n\n~~~markdown\n<!-- STP-MOVED-TO: stps/not-a-stub.md -->\n~~~not-a-closing-fence"))
        self.assertEqual(validate(root), [])

    def test_inline_marker_is_not_a_stub(self):
        root = self.make_tree("`<!-- STP-MOVED-TO: stps/sig-virt/current.md -->`\n# Current STP\n")
        self.assertEqual(validate(root), [])

    def test_multibacktick_link_is_not_a_real_link(self):
        root = self.make_tree(STUB.replace("This STP was moved to [the current STP](../sig-virt/current.md).", "This STP was moved to ``[the current STP](../sig-virt/current.md)``."))
        self.assertIn("add a link directly", validate(root)[0])

    def test_image_and_escaped_links_are_not_real_links(self):
        for link in ["![current](../sig-virt/current.md)", "\\[current](../sig-virt/current.md)"]:
            root = self.make_tree(STUB.replace("[the current STP](../sig-virt/current.md)", link))
            self.assertIn("add a link directly", validate(root)[0])

    def test_heading_inside_comment_is_not_a_moved_stub(self):
        root = self.make_tree("<!--\n# MOVED\n-->\n# Current STP\n")
        self.assertEqual(validate(root), [])

    def test_nested_html_ranges_are_removed_together(self):
        self.assertEqual(without_html_tags("<div><span>text</span></div>"), "")

    def test_html_embedded_link_is_not_a_real_link(self):
        for html in [
            "<div>[the current STP](../sig-virt/current.md)</div>",
            '<input value="[the current STP](../sig-virt/current.md)" />',
            '<input value=">[the current STP](../sig-virt/current.md)">',
            '<a title="[the current STP](../sig-virt/current.md)">',
        ]:
            root = self.make_tree(STUB.replace("This STP was moved to [the current STP](../sig-virt/current.md).", html))
            self.assertIn("add a link directly", validate(root)[0])

    def test_even_escaped_backslashes_keep_a_link(self):
        root = self.make_tree(STUB.replace("[the current STP](../sig-virt/current.md)", r"\\[the current STP](../sig-virt/current.md)"))
        self.assertEqual(validate(root), [])

    def test_escaped_exclamation_keeps_a_link(self):
        root = self.make_tree(STUB.replace("[the current STP](../sig-virt/current.md)", r"\![the current STP](../sig-virt/current.md)"))
        self.assertEqual(validate(root), [])

    def test_html_backslash_attribute_does_not_hide_link(self):
        root = self.make_tree(STUB.replace("This STP was moved to [the current STP](../sig-virt/current.md).", "<div data=x\\>[the current STP](../sig-virt/current.md)"))
        self.assertEqual(validate(root), [])

    def test_marker_inside_html_is_not_a_stub(self):
        root = self.make_tree('<div data="<!-- STP-MOVED-TO: stps/sig-virt/current.md -->"># Current STP</div>')
        self.assertEqual(validate(root), [])

    def test_marker_inside_target_html_is_not_a_stub(self):
        root = self.make_tree()
        (root / "stps/sig-virt/current.md").write_text('<div data="<!-- STP-MOVED-TO: stps/sig-virt/other.md -->"># Current STP</div>\n', encoding="utf-8")
        self.assertEqual(validate(root), [])

    def test_unclosed_html_tag_does_not_hide_stub_content(self):
        root = self.make_tree("<div>\n<!-- STP-MOVED-TO: stps/sig-virt/current.md -->\n# Not moved\n")
        errors = validate(root)
        self.assertTrue(any("missing '# MOVED' heading" in error for error in errors))

    def test_closing_tag_inside_attribute_does_not_balance_open_tag(self):
        root = self.make_tree("<div>\n<input value=\"</div>\">\n<!-- STP-MOVED-TO: stps/sig-virt/current.md -->\n# Not moved\n")
        errors = validate(root)
        self.assertTrue(any("missing '# MOVED' heading" in error for error in errors))

    def test_multiline_html_attribute_does_not_supply_link(self):
        root = self.make_tree(STUB.replace("[the current STP](../sig-virt/current.md)", '<input\n value="[the current STP](../sig-virt/current.md)">'))
        self.assertIn("add a link directly", validate(root)[0])

    def test_indented_unmatched_fence_does_not_hide_content(self):
        root = self.make_tree(STUB.replace("This STP was moved to [the current STP](../sig-virt/current.md).", "    ```markdown\n<!-- STP-MOVED-TO: stps/not-a-stub.md -->"))
        self.assertIn("exactly one", validate(root)[0])

    def test_tab_indented_unmatched_fence_does_not_hide_content(self):
        root = self.make_tree(STUB.replace("This STP was moved to [the current STP](../sig-virt/current.md).", "\t```markdown\n<!-- STP-MOVED-TO: stps/not-a-stub.md -->"))
        self.assertIn("exactly one", validate(root)[0])

    def test_multiple_markers_are_rejected(self):
        self.assertIn("exactly one", validate(self.make_tree(STUB + STUB))[0])

    def test_target_cannot_escape_stps(self):
        root = self.make_tree(STUB.replace("stps/sig-virt/current.md", "stps/../outside.md"))
        (root / "outside.md").write_text("# Not an STP\n", encoding="utf-8")
        self.assertIn("remain under stps", validate(root)[0])

    def test_non_markdown_target_is_rejected(self):
        root = self.make_tree(STUB.replace("stps/sig-virt/current.md", "stps/sig-virt/current.txt"))
        (root / "stps/sig-virt/current.md").unlink()
        (root / "stps/sig-virt/current.txt").write_text("not an STP\n", encoding="utf-8")
        self.assertIn("normalized Markdown path", validate(root)[0])

    def test_source_symlink_is_rejected(self):
        root = self.make_tree()
        old = root / "stps/sig-virt/old.md"
        old.unlink()
        os.symlink("current.md", old)
        self.assertIn("symlinked STP", validate(root)[0])

    def test_stps_root_symlink_is_rejected(self):
        root = Path(tempfile.mkdtemp())
        real = root / "real-stps"
        (real / "sig-virt").mkdir(parents=True)
        (real / "sig-virt/current.md").write_text("# Current STP\n", encoding="utf-8")
        os.symlink("real-stps", root / "stps")
        self.assertIn("symlinked STP roots", validate(root)[0])

    def test_target_symlink_is_rejected(self):
        root = self.make_tree()
        current = root / "stps/sig-virt/current.md"
        current.unlink()
        (root / "stps/sig-virt/real.md").write_text("# Current STP\n", encoding="utf-8")
        os.symlink("real.md", current)
        self.assertTrue(any("symlinked targets" in error for error in validate(root)))

    def test_target_symlink_loop_is_reported(self):
        root = self.make_tree()
        current = root / "stps/sig-virt/current.md"
        current.unlink()
        os.symlink("loop-b.md", current)
        os.symlink("current.md", root / "stps/sig-virt/loop-b.md")
        self.assertTrue(any("cannot resolve target" in error for error in validate(root)))

    def test_invalid_base_ref_is_reported(self):
        root = self.make_tree()
        self.assertIn("base ref must not start", validate(root, "--bad")[0])
        self.assertIn("control characters", validate(root, "bad\0ref")[0])
        self.assertIn("must not be empty", validate(root, "")[0])

    def test_missing_stps_root_is_reported(self):
        root = Path(tempfile.mkdtemp())
        self.assertIn("directory is missing", validate(root)[0])

    def test_target_control_character_is_reported(self):
        root = self.make_tree(STUB.replace("stps/sig-virt/current.md", "stps/sig-virt/bad\0.md"))
        self.assertIn("target must not contain control", validate(root)[0])

    def test_deleted_path_requires_a_stub(self):
        root = Path(tempfile.mkdtemp())
        original = root / "stps/sig-virt/original.md"
        original.parent.mkdir(parents=True)
        original.write_text("# STP\n", encoding="utf-8")
        self.git(root, "init")
        self.git(root, "config user.email test@example.com")
        self.git(root, "config user.name Test")
        self.git(root, "add .")
        self.git(root, "commit -m initial")
        base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        original.unlink()
        self.git(root, "add .")
        self.git(root, "commit -m delete")
        self.assertIn("permanent stub", validate(root, base)[0])

    def test_deleted_path_with_special_characters_requires_a_stub(self):
        root = Path(tempfile.mkdtemp())
        original = root / 'stps/sig-virt/über\t"\roriginal".md'
        original.parent.mkdir(parents=True)
        original.write_text("# STP\n", encoding="utf-8")
        self.git(root, "init")
        self.git(root, "config user.email test@example.com")
        self.git(root, "config user.name Test")
        self.git(root, "add .")
        self.git(root, "commit -m initial")
        base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        original.unlink()
        self.git(root, "add .")
        self.git(root, "commit -m delete")
        errors = validate(root, base)
        escaped = repr(str(original.relative_to(root)))
        self.assertTrue(any(escaped in error and "permanent stub" in error for error in errors))
        original.write_text("<!-- STP-MOVED-TO: stps/sig-virt/current.md -->\n\n# MOVED\n\n[current](current.md)\n", encoding="utf-8")
        (original.parent / "current.md").write_text("# Current STP\n", encoding="utf-8")
        self.assertEqual(validate(root, base), [])

    @patch("check_stp_moves.subprocess.run")
    def test_copy_then_delete_records_are_indexed(self, run):
        run.side_effect = [
            subprocess.CompletedProcess([], 0, stdout=b""),
            subprocess.CompletedProcess([], 0, stdout=b"C100\0source.md\0copy.md\0D\0deleted.md\0"),
        ]
        errors = validate_base_ref(Path("."), "base", {})
        self.assertTrue(any("deleted.md" in error for error in errors))

    @patch("check_stp_moves.subprocess.run")
    def test_malformed_git_status_is_rejected(self, run):
        run.side_effect = [
            subprocess.CompletedProcess([], 0, stdout=b""),
            subprocess.CompletedProcess([], 0, stdout=b"D\0"),
        ]
        errors = validate_base_ref(Path("."), "base", {})
        self.assertTrue(any("malformed git diff" in error for error in errors))

    @patch("check_stp_moves.subprocess.run")
    def test_unknown_git_status_is_rejected(self, run):
        run.side_effect = [
            subprocess.CompletedProcess([], 0, stdout=b""),
            subprocess.CompletedProcess([], 0, stdout=b"Q\0evil.md\0"),
        ]
        errors = validate_base_ref(Path("."), "base", {})
        self.assertTrue(any("malformed git diff" in error for error in errors))

    @patch("check_stp_moves.subprocess.run")
    def test_invalid_git_status_score_is_rejected(self, run):
        run.side_effect = [
            subprocess.CompletedProcess([], 0, stdout=b""),
            subprocess.CompletedProcess([], 0, stdout=b"D100\0evil.md\0"),
        ]
        errors = validate_base_ref(Path("."), "base", {})
        self.assertTrue(any("malformed git diff" in error for error in errors))

    @patch("check_stp_moves.subprocess.run")
    def test_out_of_range_git_status_score_is_rejected(self, run):
        run.side_effect = [
            subprocess.CompletedProcess([], 0, stdout=b""),
            subprocess.CompletedProcess([], 0, stdout=b"R999\0old.md\0new.md\0"),
        ]
        errors = validate_base_ref(Path("."), "base", {})
        self.assertTrue(any("malformed git diff" in error for error in errors))
        run.reset_mock()
        run.side_effect = [
            subprocess.CompletedProcess([], 0, stdout=b""),
            subprocess.CompletedProcess([], 0, stdout=b"C101\0old.md\0new.md\0"),
        ]
        errors = validate_base_ref(Path("."), "base", {})
        self.assertTrue(any("malformed git diff" in error for error in errors))
        run.reset_mock()
        run.side_effect = [
            subprocess.CompletedProcess([], 0, stdout=b""),
            subprocess.CompletedProcess([], 0, stdout=(b"R" + b"9" * 5000 + b"\0old.md\0new.md\0")),
        ]
        errors = validate_base_ref(Path("."), "base", {})
        self.assertTrue(any("malformed git diff" in error for error in errors))
        run.reset_mock()
        run.side_effect = [
            subprocess.CompletedProcess([], 0, stdout=b""),
            subprocess.CompletedProcess([], 0, stdout="R²\0old.md\0new.md\0".encode()),
        ]
        errors = validate_base_ref(Path("."), "base", {})
        self.assertTrue(any("malformed git diff" in error for error in errors))

    @patch("check_stp_moves.subprocess.run")
    def test_unterminated_git_status_is_rejected(self, run):
        run.side_effect = [
            subprocess.CompletedProcess([], 0, stdout=b""),
            subprocess.CompletedProcess([], 0, stdout=b"D\0deleted.md"),
        ]
        errors = validate_base_ref(Path("."), "base", {})
        self.assertTrue(any("missing NUL terminator" in error for error in errors))

    def test_restored_stub_satisfies_committed_deletion(self):
        root = Path(tempfile.mkdtemp())
        original = root / "stps/sig-virt/original.md"
        original.parent.mkdir(parents=True)
        original.write_text("# STP\n", encoding="utf-8")
        self.git(root, "init")
        self.git(root, "config user.email test@example.com")
        self.git(root, "config user.name Test")
        self.git(root, "add .")
        self.git(root, "commit -m initial")
        base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        original.unlink()
        self.git(root, "add .")
        self.git(root, "commit -m delete")
        original.write_text("<!-- STP-MOVED-TO: stps/sig-virt/current.md -->\n\n# MOVED\n\n[current](current.md)\n", encoding="utf-8")
        (original.parent / "current.md").write_text("# Current STP\n", encoding="utf-8")
        self.assertEqual(validate(root, base), [])

    def test_rename_requires_a_stub(self):
        root = Path(tempfile.mkdtemp())
        original = root / "stps/sig-virt/original.md"
        renamed = root / "stps/sig-virt/renamed.md"
        original.parent.mkdir(parents=True)
        original.write_text("# STP\n", encoding="utf-8")
        self.git(root, "init")
        self.git(root, "config user.email test@example.com")
        self.git(root, "config user.name Test")
        self.git(root, "add .")
        self.git(root, "commit -m initial")
        base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        original.rename(renamed)
        self.git(root, "add .")
        self.git(root, "commit -m rename")
        self.assertIn("permanent stub", validate(root, base)[0])

    def test_rename_path_with_special_characters_requires_a_stub(self):
        root = Path(tempfile.mkdtemp())
        original = root / 'stps/sig-virt/über\t"\roriginal".md'
        renamed = root / 'stps/sig-virt/über\t"\rrenamed".md'
        original.parent.mkdir(parents=True)
        original.write_text("# STP\n", encoding="utf-8")
        self.git(root, "init")
        self.git(root, "config user.email test@example.com")
        self.git(root, "config user.name Test")
        self.git(root, "add .")
        self.git(root, "commit -m initial")
        base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        original.rename(renamed)
        self.git(root, "add .")
        self.git(root, "commit -m rename")
        errors = validate(root, base)
        escaped = repr(str(original.relative_to(root)))
        self.assertTrue(any(escaped in error and "permanent stub" in error for error in errors))

    @staticmethod
    def git(root, command):
        args = command.split()
        if args and args[0] == "commit":
            args.insert(0, "-c")
            args.insert(1, "commit.gpgSign=false")
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
