"""Test output build functions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from unittest.mock import patch, mock_open

from pazel.output_build import output_build_file
from pazel.pazel_extensions import OutputExtension


class OutputBuildTestCase(unittest.TestCase):
    """Test output build functions."""

    def setUp(self):
        self.build_file_path = "urbancompass/src/python3/uc/aws/BUILD"
        self.build_source = """
py_library(
    name = "__init__",
    srcs = ["__init__.py"],
)

py_library(
    name = "assume_role",
    srcs = ["assume_role.py"],
    deps = [
        requirement("boto3"),
        requirement("botocore"),
    ],
)"""
        self.requirement_load = 'load("@py3_deps//:requirements.bzl", "requirement")'
        self.checks = {}
        self.update = True
        self.custom_bazel_rules = []
        self.output_extension = OutputExtension(
            header="",
            footer="",
        )

    @patch("pazel.output_build.open", new_callable=mock_open, read_data="")
    def test_output_build_file_with_macro_requirement(self, mock_file):
        ignored_rules = [
            '\n# pazel-ignore\nload("//build-support/bazel/python3/deps:core.bzl", "py_library", "requirement")',
        ]
        output_build_file(
            self.build_source,
            ignored_rules,
            self.output_extension,
            self.custom_bazel_rules,
            self.build_file_path,
            self.requirement_load,
            self.checks,
            self.update,
        )

        expected_expression = """
# pazel-ignore
load("//build-support/bazel/python3/deps:core.bzl", "py_library", "requirement")

py_library(
    name = "__init__",
    srcs = ["__init__.py"],
)

py_library(
    name = "assume_role",
    srcs = ["assume_role.py"],
    deps = [
        requirement("boto3"),
        requirement("botocore"),
    ],
)
"""
        mock_file().write.assert_called_once_with(expected_expression)

    @patch("pazel.output_build.open", new_callable=mock_open, read_data="")
    def test_output_build_file_with_requirement_alias(self, mock_file):
        """Test parse_enclosed_expression."""

        ignored_rules = [
            '\n# pazel-ignore\nload("@py3_airflow_deps//:requirements.bzl", airflow_requirement = "requirement")'
        ]
        output_build_file(
            self.build_source,
            ignored_rules,
            self.output_extension,
            self.custom_bazel_rules,
            self.build_file_path,
            self.requirement_load,
            self.checks,
            self.update,
        )

        expected_expression = """load("@py3_deps//:requirements.bzl", "requirement")

# pazel-ignore
load("@py3_airflow_deps//:requirements.bzl", airflow_requirement = "requirement")

py_library(
    name = "__init__",
    srcs = ["__init__.py"],
)

py_library(
    name = "assume_role",
    srcs = ["assume_role.py"],
    deps = [
        requirement("boto3"),
        requirement("botocore"),
    ],
)
"""
        mock_file().write.assert_called_once_with(expected_expression)

    @patch("pazel.output_build.open", new_callable=mock_open, read_data="")
    def test_output_build_file_for_default_requirement(self, mock_file):
        ignored_rules = []
        output_build_file(
            self.build_source,
            ignored_rules,
            self.output_extension,
            self.custom_bazel_rules,
            self.build_file_path,
            self.requirement_load,
            self.checks,
            self.update,
        )

        expected_expression = """load("@py3_deps//:requirements.bzl", "requirement")

py_library(
    name = "__init__",
    srcs = ["__init__.py"],
)

py_library(
    name = "assume_role",
    srcs = ["assume_role.py"],
    deps = [
        requirement("boto3"),
        requirement("botocore"),
    ],
)
"""
        mock_file().write.assert_called_once_with(expected_expression)


if __name__ == "__main__":
    unittest.main()
