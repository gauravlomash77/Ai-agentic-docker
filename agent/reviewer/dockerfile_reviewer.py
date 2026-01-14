"""
Dockerfile Reviewer
===================

Performs static analysis on generated Dockerfiles
using deterministic best-practice rules.
"""

from typing import Dict, List

from agent.reviewer.rules import (
    review_base_image,
    review_user_security,
    review_dependency_installation,
    review_entrypoint,
)


class DockerfileReviewer:
    """
    Deterministic Dockerfile reviewer.
    """

    def review(self, dockerfile: str) -> Dict[str, object]:
        """
        Review Dockerfile content and return issues.
        """
        issues: List[Dict[str, str]] = []

        issues.extend(review_base_image(dockerfile))
        issues.extend(review_user_security(dockerfile))
        issues.extend(review_dependency_installation(dockerfile))
        issues.extend(review_entrypoint(dockerfile))

        summary = {
            "errors": [i for i in issues if i["level"] == "error"],
            "warnings": [i for i in issues if i["level"] == "warning"],
        }

        return {
            "summary": summary,
            "issues": issues,
            "passed": len(summary["errors"]) == 0,
        }
