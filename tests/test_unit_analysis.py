import os
import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock
from analyze_git_csv import *


class UnitTests(unittest.TestCase):
    def test_read_analytics__given_valid_csv_file__then_df_returned(self):
        # Arrange
        input = "tests/data/git_log_analysis.csv"

        # Act
        results = read_git_log_csv(input)
        print(results.columns)
        print(results)

        # Assert
        self.assertEqual(results.shape, (17, 14))

    def test_calculate_file_complexity__given_input_dir_of_files__files_scores_returned(
        self,
    ):
        # Arrange
        input = "tests/data/sample_source_files"

        # Act
        results = calculate_file_complexity(input)

        # Assert
        self.assertEqual(
            results,
            {
                "test_1.py": 22,
                "test_2.py": 67,
            },
        )

    def test_calculate_file_commits__given_simple_test_data__then_correct_data_returned(
        self,
    ):
        # Arrange
        input = "tests/data/git_log_analysis.csv"
        df = read_git_log_csv(input)

        # Act
        results = calculate_file_commits(df)

        # Assert
        self.assertEqual(
            results,
            {
                ".gitignore": 2,
                "README.md": 1,
                "report_template_json.txt": 1,
                "requirements.txt": 1,
                "run_tests.sh": 1,
                "test_and_format.py": 1,
                "tests/analyze_git_csv.py": 1,
                "tests/data/forem_git_log.csv": 1,
                "test_1.py": 3,
                "test_2.py": 3,
                "tests/data/short_sample.csv": 1,
                "tests/test_unit.py": 1,
            },
        )

    def test_get_commit_age__given_simple_test_data__then_correct_data_returned(
        self,
    ):
        # Arrange
        input = "tests/data/git_log_analysis.csv"
        df = read_git_log_csv(input)
        set_date = datetime(2021, 2, 14)

        # Act
        results = get_commit_age(df, set_date)
        print(json.dumps(results, indent=3))

        # Assert
        self.assertEqual(
            results,
            {
                ".gitignore": 2,
                "README.md": 2,
                "report_template_json.txt": 2,
                "requirements.txt": 2,
                "run_tests.sh": 2,
                "test_1.py": 2,
                "test_2.py": 1,
                "test_and_format.py": 2,
                "tests/analyze_git_csv.py": 2,
                "tests/data/forem_git_log.csv": 2,
                "tests/data/short_sample.csv": 2,
                "tests/test_unit.py": 2,
            },
        )

    def test_determine_hotspot_data__given_simple_data__then_correct_data_returned(
        self,
    ):
        # Arrange
        input = "tests/data/git_log_analysis.csv"
        df = read_git_log_csv(input)
        file_commits = calculate_file_commits(df)
        input = "tests/data/sample_source_files"
        file_complexities = calculate_file_complexity(input)
        print(json.dumps(file_complexities, indent=3, default=str))
        set_date = datetime(2021, 2, 14)
        commit_ages = get_commit_age(df, set_date)

        # Act
        results = determine_hotspot_data(file_commits, file_complexities, commit_ages)
        print(results)

        # Assert
        expected = [
            FileInfo(file="test_1.py", commits=3, complexity=22, age=3, score=32.8),
            FileInfo(file="test_2.py", commits=3, complexity=67, age=2, score=100.0),
        ]
        self.assertEqual(results, expected)

    def test_get_top_hotspots__given_short_list__then_top_3_returned(self):
        # Arrange
        input = [
            FileInfo(
                file="tests/data/forem_git_log.csv",
                commits=1,
                complexity=2,
                score=2,
                age=1,
            ),
            FileInfo(file="test_1.py", commits=3, complexity=22, score=66, age=1),
            FileInfo(file="test_2.py", commits=3, complexity=67, score=201, age=1),
            FileInfo(
                file="tests/data/short_sample.csv",
                commits=1,
                complexity=0,
                score=0,
                age=1,
            ),
            FileInfo(
                file="tests/test_unit.py", commits=1, complexity=0, score=0, age=1
            ),
        ]

        # Act
        results = get_top_hotspots(input, 3)
        print(json.dumps(results, indent=3, default=str))

        # Assert
        expected = [
            FileInfo(file="test_2.py", commits=3, complexity=67, score=201, age=1),
            FileInfo(file="test_1.py", commits=3, complexity=22, score=66, age=1),
            FileInfo(
                file="tests/data/forem_git_log.csv",
                commits=1,
                complexity=2,
                score=2,
                age=1,
            ),
        ]
        self.assertEqual(results, expected)

    def test_is_code_file__given_text_file__then_return_true(self):
        # Arrange
        input = os.getcwd() + "tests/data/git_log_analysis.csv"

        # Act
        results = is_code_file(input)

        # Assert
        self.assertEqual(results, True)

    def test_is_code_file__given_image__then_return_false(self):
        # Arrange
        input = os.getcwd() + "tests/data/picture.jpeg"

        # Act
        results = is_code_file(input)

        # Assert
        self.assertEqual(results, False)

    def test_is_code_file__given_readme__then_return_false(self):
        # Arrange
        input = os.getcwd() + "README.md"

        # Act
        results = is_code_file(input)

        # Assert
        self.assertEqual(results, False)

    def test_is_code_file__given_lock__then_return_false(self):
        # Arrange
        input = os.getcwd() + "yarn.lock"

        # Act
        results = is_code_file(input)

        # Assert
        self.assertEqual(results, False)


if __name__ == "__main__":
    unittest.main()
