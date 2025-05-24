import unittest
import os
import numpy as np
import argparse
import io
import contextlib

from sup.utils import (
    check_file_type,
    get_dataset_names_sql, # Added for test_read_input_file_sql_all_columns setup
    get_all_column_dataset_names_sql,
    read_input_file,
    get_filters,
    SupRuntimeError
)
from sup.listmode import run as listmode_run


class TestSQLIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Set up for all tests.
        Defines the path to the test database.
        This database (test_data.sqlite) is assumed to be created by a previous step
        or setup script.
        """
        cls.test_db_path = os.path.join(os.path.dirname(__file__), 'test_data.sqlite')
        # Check if the database exists, to provide a clearer error if it's missing
        if not os.path.exists(cls.test_db_path):
            raise FileNotFoundError(
                f"Test database '{cls.test_db_path}' not found. "
                "Please ensure it's created before running integration tests."
            )

    def test_check_file_type_sql(self):
        self.assertEqual(check_file_type('dummy.db'), "sql")
        self.assertEqual(check_file_type('dummy.sqlite'), "sql")
        self.assertEqual(check_file_type('dummy.sqlite3'), "sql")
        self.assertEqual(check_file_type(self.test_db_path), "sql")

    def test_get_all_column_dataset_names_sql(self):
        expected_names = [
            'table1.id', 'table1.value1', 'table1.name1',
            'table2.id', 'table2.value2'
        ]
        names = get_all_column_dataset_names_sql(self.test_db_path)
        self.assertEqual(names, expected_names)

    def test_read_input_file_sql_all_columns(self):
        # In read_input_file_sql, dset_indices refer to table indices.
        # First, get table names to ensure indices [0, 1] are correct for 'table1' and 'table2'
        # This makes the test more robust if table creation order changes.
        table_names = get_dataset_names_sql(self.test_db_path)
        dset_indices = []
        if 'table1' in table_names:
            dset_indices.append(table_names.index('table1'))
        if 'table2' in table_names:
            dset_indices.append(table_names.index('table2'))
        
        self.assertEqual(len(dset_indices), 2, "Test setup error: table1 or table2 not found for indexing.")

        dsets, dnames = read_input_file(self.test_db_path, dset_indices=dset_indices, read_slice=None, delimiter=' ') # delimiter is not used for SQL

        expected_dnames = [
            'table1.id', 'table1.value1', 'table1.name1',
            'table2.id', 'table2.value2'
        ]
        self.assertEqual(dnames, expected_dnames)

        # table1.id
        np.testing.assert_array_equal(dsets[0], np.array([1, 2, 3]))
        # table1.value1
        np.testing.assert_array_almost_equal(dsets[1], np.array([10.5, 20.3, 30.1]))
        # table1.name1
        np.testing.assert_array_equal(dsets[2], np.array(['apple', 'banana', 'cherry']))
        # table2.id
        np.testing.assert_array_equal(dsets[3], np.array([1, 2, 3, 4]))
        # table2.value2
        np.testing.assert_array_equal(dsets[4], np.array([100, 200, 300, 400]))
        
        # Check dtypes for string array
        self.assertTrue(np.issubdtype(dsets[2].dtype, np.object_) or np.issubdtype(dsets[2].dtype, np.str_))


    def test_read_input_file_sql_specific_table(self):
        table_names = get_dataset_names_sql(self.test_db_path)
        table1_idx = -1
        if 'table1' in table_names:
            table1_idx = table_names.index('table1')
        self.assertNotEqual(table1_idx, -1, "Test setup error: table1 not found for indexing.")

        dsets, dnames = read_input_file(self.test_db_path, dset_indices=[table1_idx], read_slice=None, delimiter=' ')

        expected_dnames = ['table1.id', 'table1.value1', 'table1.name1']
        self.assertEqual(dnames, expected_dnames)

        np.testing.assert_array_equal(dsets[0], np.array([1, 2, 3]))
        np.testing.assert_array_almost_equal(dsets[1], np.array([10.5, 20.3, 30.1]))
        np.testing.assert_array_equal(dsets[2], np.array(['apple', 'banana', 'cherry']))
        self.assertTrue(np.issubdtype(dsets[2].dtype, np.object_) or np.issubdtype(dsets[2].dtype, np.str_))


    def test_get_filters_sql(self):
        all_names = get_all_column_dataset_names_sql(self.test_db_path)
        # Expected: ['table1.id', 'table1.value1', 'table1.name1', 'table2.id', 'table2.value2']
        
        idx_table1_value1 = -1
        idx_table2_id = -1

        try:
            idx_table1_value1 = all_names.index('table1.value1')
            idx_table2_id = all_names.index('table2.id')
        except ValueError:
            self.fail("Test setup error: Expected filter columns not found in all_names.")

        filter_indices = [idx_table1_value1, idx_table2_id]

        f_dsets, f_names = get_filters(self.test_db_path, filter_indices=filter_indices, read_slice=None, delimiter=' ')

        self.assertEqual(f_names, ['table1.value1', 'table2.id'])
        np.testing.assert_array_almost_equal(f_dsets[0], np.array([10.5, 20.3, 30.1]))
        np.testing.assert_array_equal(f_dsets[1], np.array([1, 2, 3, 4]))

    def test_listmode_sql(self):
        args = argparse.Namespace(
            input_file=self.test_db_path,
            # Other args that listmode.run might expect, e.g. from sup.py setup
            # Assuming listmode_run doesn't require more than input_file for basic operation
        )

        captured_output = io.StringIO()
        try:
            with contextlib.redirect_stdout(captured_output):
                listmode_run(args)
        except Exception as e:
            self.fail(f"listmode_run raised an exception: {e}\nCaptured output so far:\n{captured_output.getvalue()}")

        output = captured_output.getvalue()
        
        # Normalize path for comparison, especially on Windows
        normalized_db_path = os.path.normpath(self.test_db_path)

        expected_lines = [
            f"Reading {normalized_db_path} as an SQL (SQLite) file",
            "", # For the empty print()
            "Index \t Dataset",
            "----------------",
            "0 \t table1.id",
            "1 \t table1.value1",
            "2 \t table1.name1",
            "3 \t table2.id",
            "4 \t table2.value2"
        ]
        
        # Normalize line endings in output for cross-platform compatibility
        output_lines = [line.strip() for line in output.strip().replace('\\r\\n', '\\n').split('\\n')]
        
        # Check if each expected line is present in the output lines
        # This is more robust to slight variations in spacing than a direct string match of the whole block
        for expected_line in expected_lines:
            self.assertIn(expected_line.strip(), output_lines, f"Expected line '{expected_line.strip()}' not found in output.")

        # Additionally, check the exact sequence for critical parts if needed
        # For example, ensure the header is followed by the correct data lines in order
        try:
            header_idx = output_lines.index("Index \t Dataset")
            self.assertEqual(output_lines[header_idx + 1], "----------------")
            self.assertEqual(output_lines[header_idx + 2], "0 \t table1.id")
            self.assertEqual(output_lines[header_idx + 3], "1 \t table1.value1")
            self.assertEqual(output_lines[header_idx + 4], "2 \t table1.name1")
            self.assertEqual(output_lines[header_idx + 5], "3 \t table2.id")
            self.assertEqual(output_lines[header_idx + 6], "4 \t table2.value2")
        except ValueError:
            self.fail("Critical output structure (header/data) not found as expected.")
        except IndexError:
            self.fail("Output structure is shorter than expected for critical parts.")


if __name__ == '__main__':
    unittest.main()
