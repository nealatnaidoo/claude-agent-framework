"""Baseline integrity verifier for agent framework files.

This module provides functionality to compute SHA-256 hashes of framework files
and verify they match a stored baseline, preventing unauthorized modifications.

Key Features:
- SHA-256 hash computation for files
- Baseline verification (current vs expected hashes)
- Baseline update for authorized framework changes
- Performance optimized (<2 seconds for typical framework file set)
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class VerificationResult:
    """Result of baseline verification.

    Attributes:
        passed: True if all hashes match baseline, False otherwise.
        changed_files: List of files with mismatched hashes (empty if passed=True).
        timestamp: When verification was performed.
    """

    passed: bool
    changed_files: list[Path]
    timestamp: datetime


class BaselineVerifier:
    """Baseline integrity verifier for framework files."""

    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of a file.

        Args:
            file_path: Path to file to hash.

        Returns:
            64-character hexadecimal SHA-256 hash.

        Raises:
            FileNotFoundError: If file_path does not exist.
            IOError: If file cannot be read.
        """
        sha256 = hashlib.sha256()

        with file_path.open("rb") as f:
            # Read file in chunks for memory efficiency
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    def compute_baseline(self, file_paths: list[Path]) -> dict[str, str]:
        """Compute SHA-256 hashes for all framework files.

        Args:
            file_paths: List of framework file paths to hash.

        Returns:
            Dictionary mapping file path (as string) to SHA-256 hash.
        """
        return {str(path): self.compute_hash(path) for path in file_paths if path.exists()}

    def verify_baseline(
        self, baseline_file: Path, framework_files: list[Path]
    ) -> VerificationResult:
        """Compare current hashes with stored baseline.

        Args:
            baseline_file: Path to JSON file containing baseline hashes.
            framework_files: List of framework files to verify.

        Returns:
            VerificationResult with pass/fail status and list of changed files.

        Raises:
            FileNotFoundError: If baseline_file does not exist.
        """
        if not baseline_file.exists():
            raise FileNotFoundError(f"Baseline file not found: {baseline_file}")

        # Load baseline
        with baseline_file.open() as f:
            baseline_data = json.load(f)

        expected_hashes = baseline_data["hashes"]

        # Compute current hashes
        current_hashes = self.compute_baseline(framework_files)

        # Find changed files
        changed = []
        for file_path_str, expected_hash in expected_hashes.items():
            current_hash = current_hashes.get(file_path_str)
            if current_hash != expected_hash:
                changed.append(Path(file_path_str))

        return VerificationResult(
            passed=(len(changed) == 0), changed_files=changed, timestamp=datetime.now(UTC)
        )

    def update_baseline(self, baseline_file: Path, new_hashes: dict[str, str]) -> None:
        """Update baseline hashes after authorized framework changes.

        Args:
            baseline_file: Path to JSON file to write baseline hashes.
            new_hashes: Dictionary mapping file paths (as strings) to SHA-256 hashes.
        """
        baseline_data = {
            "version": "1.0",
            "updated_at": datetime.now(UTC).isoformat(),
            "hashes": new_hashes,
        }

        with baseline_file.open("w") as f:
            json.dump(baseline_data, f, indent=2)


# Framework files to monitor (when used as CLI script)
FRAMEWORK_FILES = [
    Path.home() / ".claude/agents/backend-coding-agent.md",
    Path.home() / ".claude/agents/frontend-coding-agent.md",
    Path.home() / ".claude/agents/business-analyst.md",
    Path.home() / ".claude/prompts/system/coding_system_prompt_v4_0_hex_tdd_8k.md",
    Path.home() / ".claude/prompts/playbooks/coding_playbook_v4_0.md",
    Path.home() / ".claude/settings.local.json",
    Path.home() / ".claude/devops/manifest.yaml",
]

BASELINE_FILE = Path.home() / ".claude/devops/baseline_hashes.json"


if __name__ == "__main__":
    """CLI entry point for baseline verification."""
    verifier = BaselineVerifier()

    result = verifier.verify_baseline(BASELINE_FILE, FRAMEWORK_FILES)

    if not result.passed:
        print("BASELINE VERIFICATION FAILED")
        print("Changed files:")
        for file in result.changed_files:
            print(f"  - {file}")
        exit(1)
    else:
        print("Baseline verification passed")
        exit(0)
