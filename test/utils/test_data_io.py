import os
import pytest
import polars as pl

from src.utils.data_io import *
from src.utils.logger import log

import tempfile
import shutil


@pytest.fixture(scope="module")
def temp_dir():
    """
    Fixture to create a temporary directory for tests.
    """
    # Create a temporary directory
    tmp_dir = tempfile.mkdtemp()
    yield tmp_dir
    
    # Clean up after tests
    shutil.rmtree(tmp_dir)


def test_load_excel_to_dataframe(temp_dir):
    """
    Test the load_excel_to_dataframe function.
    """
    test_file = os.path.join(temp_dir, "test_excel.xlsx")

    # Create a DataFrame
    df = pl.DataFrame({
        "col1": [1, 2, 3],
        "col2": [4, 5, 6]
    })

    # Export the DataFrame to Excel without specifying the sheet_name
    df.write_excel(test_file)  # No sheet_name specified

    # Try to load the specified sheet from the Excel file
    result_df = load_excel_to_dataframe(test_file, sheet_name="Sheet1")  # Can use "Sheet1" or 0 here

    assert result_df is not None, "Failed to load the Excel file"
    assert result_df.shape[0] == 3, "Incorrect number of rows in the DataFrame"
    assert "col1" in result_df.columns, "Column 'col1' is missing"


def test_load_csv_to_dataframe(temp_dir):
    """
    Test the load_csv_to_dataframe function.
    """
    test_file = os.path.join(temp_dir, "test_csv.csv")

    # Create a DataFrame
    df = pl.DataFrame({
        "col1": [1, 2, 3],
        "col2": [4, 5, 6]
    })

    # Export the DataFrame to CSV
    df.write_csv(test_file)

    # Try to load the CSV file
    result_df = load_csv_to_dataframe(test_file)

    assert result_df is not None, "Failed to load the CSV file"
    assert result_df.shape[0] == 3, "Incorrect number of rows in the DataFrame"
    assert "col1" in result_df.columns, "Column 'col1' is missing"


def test_load_json_to_dataframe(temp_dir):
    """
    Test the load_json_to_dataframe function.
    """
    test_file = os.path.join(temp_dir, "test_json.json")

    # Create a DataFrame
    df = pl.DataFrame({
        "col1": [1, 2, 3],
        "col2": [4, 5, 6]
    })

    # Export the DataFrame to JSON
    df.write_json(test_file)

    # Try to load the JSON file
    result_df = load_json_to_dataframe(test_file)

    assert result_df is not None, "Failed to load the JSON file"
    assert result_df.shape[0] == 3, "Incorrect number of rows in the DataFrame"
    assert "col1" in result_df.columns, "Column 'col1' is missing"


def test_export_dataframe_to_csv(temp_dir):
    """
    Test the export_dataframe_to_csv function.
    """
    test_file = os.path.join(temp_dir, "output_csv.csv")

    # Create a DataFrame
    df = pl.DataFrame({
        "col1": [1, 2, 3],
        "col2": [4, 5, 6]
    })

    # Export the DataFrame to CSV
    result = export_dataframe_to_csv(df, output_abs_path=test_file)

    assert result['success'], "Failed to export CSV"
    assert os.path.isfile(test_file), "The CSV file was not created"
    
    # Verify that the data is correctly exported
    result_df = pl.read_csv(test_file)
    assert result_df.shape[0] == 3, "Incorrect number of rows in the CSV file"
    assert "col1" in result_df.columns, "Column 'col1' is missing in the CSV"


def test_export_dataframe_to_json(temp_dir):
    """
    Test the export_dataframe_to_json function.
    """
    test_file = os.path.join(temp_dir, "output_json.json")

    # Create a DataFrame
    df = pl.DataFrame({
        "col1": [1, 2, 3],
        "col2": [4, 5, 6]
    })

    # Export the DataFrame to JSON
    result = export_dataframe_to_json(df, output_abs_path=test_file)

    assert result['success'], "Failed to export JSON"
    assert os.path.isfile(test_file), "The JSON file was not created"
    
    # Verify that the data is correctly exported
    result_df = pl.read_json(test_file)
    assert result_df.shape[0] == 3, "Incorrect number of rows in the JSON file"
    assert "col1" in result_df.columns, "Column 'col1' is missing in the JSON"
