import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock
from git_log_to_csv import *


class UnitTests(unittest.TestCase):
    def test_process__given_two_commits_three_files__then_three_lines_created(self):
        # Arrange
        input = """^^c8ed1ef--1576592170--2019-12-17T09:16:10-05:00--Steve Ziegler


    3	5	README.md
    0	1	sam-app/add_cw_log_error_metric/CloudFormationReplicator.py
    ^^a999999--1576592605--2019-12-17T09:23:25-05:00--Steve Ziegler


    2	1	sam-app/add_cw_log_error_metric/CloudFormationReplicator.py
    """

        # Act
        results = process_git_log(input)
        print(results)

        # Assert
        expected = """commit_hash,epoch,timestamp,date,year,month,day,author,file,churn_count,dir_1,dir_2,dir_3,dir_4
c8ed1ef,1576592170,2019-12-17T09:16:10,2019-12-17,2019,12,17,"Steve Ziegler","README.md",8,,,,
c8ed1ef,1576592170,2019-12-17T09:16:10,2019-12-17,2019,12,17,"Steve Ziegler","sam-app/add_cw_log_error_metric/CloudFormationReplicator.py",1,sam-app,add_cw_log_error_metric,,
a999999,1576592605,2019-12-17T09:23:25,2019-12-17,2019,12,17,"Steve Ziegler","sam-app/add_cw_log_error_metric/CloudFormationReplicator.py",3,sam-app,add_cw_log_error_metric,,
"""
        expected_splits = expected.split("\n")
        for count, line in enumerate(results.split("\n")):
            self.assertEqual(line, expected_splits[count], f"line {count} is different")

    def test_process__given_insertion_is_dash__then_churn_set_to_two(self):
        # Arrange
        input = """^^c8ed1ef--1576592170--2019-12-17T09:16:10-05:00--Steve Ziegler


    -	-	README.md
    """

        # Act
        results = process_git_log(input)
        print(results)

        # Assert
        expected = """commit_hash,epoch,timestamp,date,year,month,day,author,file,churn_count,dir_1,dir_2,dir_3,dir_4
c8ed1ef,1576592170,2019-12-17T09:16:10,2019-12-17,2019,12,17,"Steve Ziegler","README.md",2,,,,
"""
        expected_splits = expected.split("\n")
        for count, line in enumerate(results.split("\n")):
            self.assertEqual(line, expected_splits[count], f"line {count} is different")

    def test_process__given_file_in_one_dir__then_dir_1_correct(self):
        # Arrange
        input = """^^c8ed1ef--1576592170--2019-12-17T09:16:10-05:00--Steve Ziegler


-	-	test1/README.md
"""

        # Act
        results = process_git_log(input)
        print(results)

        # Assert
        expected = """commit_hash,epoch,timestamp,date,year,month,day,author,file,churn_count,dir_1,dir_2,dir_3,dir_4
c8ed1ef,1576592170,2019-12-17T09:16:10,2019-12-17,2019,12,17,"Steve Ziegler","test1/README.md",2,test1,,,
"""
        expected_splits = expected.split("\n")
        for count, line in enumerate(results.split("\n")):
            self.assertEqual(line, expected_splits[count], f"line {count} is different")

    def test_process__given_file_in_four_dir__then_dirs_correct(self):
        # Arrange
        input = """^^c8ed1ef--1576592170--2019-12-17T09:16:10-05:00--Steve Ziegler


-	-	test1/test2/test3/test4/README.md
"""

        # Act
        results = process_git_log(input)
        print(results)

        # Assert
        expected = """commit_hash,epoch,timestamp,date,year,month,day,author,file,churn_count,dir_1,dir_2,dir_3,dir_4
c8ed1ef,1576592170,2019-12-17T09:16:10,2019-12-17,2019,12,17,"Steve Ziegler","test1/test2/test3/test4/README.md",2,test1,test2,test3,test4
"""
        expected_splits = expected.split("\n")
        for count, line in enumerate(results.split("\n")):
            self.assertEqual(line, expected_splits[count], f"line {count} is different")

    def test_process__given_files_with_different_dirs__then_dirs_correct(self):
        # Arrange
        input = """^^c8ed1ef--1576592170--2019-12-17T09:16:10-05:00--Steve Ziegler


-	-	README.md
-	-	test1/test2/README.md
-	-	test1/test2/test3/test4/README.md
"""

        # Act
        results = process_git_log(input)
        print(results)

        # Assert
        expected = """commit_hash,epoch,timestamp,date,year,month,day,author,file,churn_count,dir_1,dir_2,dir_3,dir_4
c8ed1ef,1576592170,2019-12-17T09:16:10,2019-12-17,2019,12,17,"Steve Ziegler","README.md",2,,,,
c8ed1ef,1576592170,2019-12-17T09:16:10,2019-12-17,2019,12,17,"Steve Ziegler","test1/test2/README.md",2,test1,test2,,
c8ed1ef,1576592170,2019-12-17T09:16:10,2019-12-17,2019,12,17,"Steve Ziegler","test1/test2/test3/test4/README.md",2,test1,test2,test3,test4
"""
        expected_splits = expected.split("\n")
        for count, line in enumerate(results.split("\n")):
            self.assertEqual(line, expected_splits[count], f"line {count} is different")

    def test_process__given_timezone_is_gmt__then_results_are_correct(self):
        # Arrange
        input = """^^c8ed1ef--1576592170--2019-12-17T09:16:10+00:00--Steve Ziegler


1	1	README.md
"""

        # Act
        results = process_git_log(input)
        print(results)

        # Assert
        expected = """commit_hash,epoch,timestamp,date,year,month,day,author,file,churn_count,dir_1,dir_2,dir_3,dir_4
c8ed1ef,1576592170,2019-12-17T09:16:10,2019-12-17,2019,12,17,"Steve Ziegler","README.md",2,,,,
"""
        expected_splits = expected.split("\n")
        for count, line in enumerate(results.split("\n")):
            self.assertEqual(line, expected_splits[count], f"line {count} is different")

    def test_process__given_exclude_files__then_three_lines_created(self):
        # Arrange
        input = """^^c8ed1ef--1576592170--2019-12-17T09:16:10-05:00--Steve Ziegler


    3	5	README.md
    0	1	sam-app/add_cw_log_error_metric/CloudFormationReplicator.py
    ^^a999999--1576592605--2019-12-17T09:23:25-05:00--Steve Ziegler


    2	1	sam-app/add_cw_log_error_metric/CloudFormationReplicator.py
    """

        # Act
        results = process_git_log(input, "READ|cw")
        print(results)

        # Assert
        expected = """commit_hash,epoch,timestamp,date,year,month,day,author,file,churn_count,dir_1,dir_2,dir_3,dir_4
"""
        expected_splits = expected.split("\n")
        for count, line in enumerate(results.split("\n")):
            self.assertEqual(line, expected_splits[count], f"line {count} is different")

    def test_process__given_exclude_authors__then_three_lines_created(self):
        # Arrange
        input = """^^c8ed1ef--1576592170--2019-12-17T09:16:10-05:00--Steve Ziegler


    3	5	README.md
    0	1	sam-app/add_cw_log_error_metric/CloudFormationReplicator.py
    ^^a999999--1576592605--2019-12-17T09:23:25-05:00--Steve Ziegler


    2	1	sam-app/add_cw_log_error_metric/CloudFormationReplicator.py
    """

        # Act
        results = process_git_log(input, "Ste.e")
        print(results)

        # Assert
        expected = """commit_hash,epoch,timestamp,date,year,month,day,author,file,churn_count,dir_1,dir_2,dir_3,dir_4
"""
        expected_splits = expected.split("\n")
        for count, line in enumerate(results.split("\n")):
            self.assertEqual(line, expected_splits[count], f"line {count} is different")


if __name__ == "__main__":
    unittest.main()
