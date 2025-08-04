import os, time
import polars as pl

from src.config.parameters import *
from src.utils.logger import *


def load_excel_to_dataframe (excel_file_abs_pth : str, sheet_name : str = None, specific_cols : list = None, schema_overrides : dict = None) -> pl.DataFrame | None  :
    """
    Loads an Excel file and returns it as a Polars dataframe, applying schema overrides.

    Args:
        excel_file_abs_pth (str): Absolute path to the Excel file.
        sheet_name (str): Sheet name to read from.
        specific_cols (list): List of columns to import. If None, then all columns
        schema_overrides (dict): Dictionary mapping column names to Polars types.

    Returns:
        df (pl.DataFrame | None) : Loaded dataframe, or None if an error occurs.
    """
    if not os.path.isfile(excel_file_abs_pth) :
        
        log(f"[-] File not found : {excel_file_abs_pth}", "error")
        return None

    if sheet_name is None or sheet_name == "" :
        sheet_name = 0 # The default sheet index

    try :

        # sving the time of execution
        start = time.time()
        
        df = pl.read_excel(

            source=excel_file_abs_pth,
            sheet_name=sheet_name,
            columns=specific_cols,              # If None, pl manage this case
            schema_overrides=schema_overrides   # If None, Polars manages this case
        
        )
        
        log(f"[*] [POLARS] Read in {time.time() - start:.2f} seconds from {excel_file_abs_pth}", "info")

        return df
    
    except Exception as e :

        log(f"[-] Error while converting the Excel file : {e}", "error")
        
        return None


def load_csv_to_dataframe (csv_abs_path : str, specific_cols : list = None, schema_overrides : dict = None) -> pl.DataFrame | None :
    """
    Loads a CSV file into a Polars DataFrame, with optional column filtering and type overrides.

    Args:
        csv_abs_path (str): Absolute path to the CSV file.
        specific_cols (list, optional): List of columns to read. If None, all columns are read.
        schema_overrides (dict, optional): Dictionary mapping column names to Polars data types.

    Returns:
        pl.DataFrame | None: The loaded Polars DataFrame, or None if an error occurred.
    """
    if not os.path.isfile(csv_abs_path) :

        log(f"\n[-] File not found : {csv_abs_path}\n", "error")
        return None
    
    try :

        start = time.time()

        df = pl.read_csv(

            source=csv_abs_path,
            columns=specific_cols,
            schema_overrides=schema_overrides,

            low_memory=False,   # In order to get speed lecture
            n_threads=4         # In order to get speed lecture

        )

        log(f"[*] [POLARS] Read in {time.time() - start:.2f} seconds from CSV {csv_abs_path}", "info")

        return df
    
    except Exception as e :

        log(f"[-] Error during convertion of CSV {csv_abs_path} : {e}", "error")
    
        return None


def load_json_to_dataframe (json_abs_path : str, schema_overrides : dict = None) -> pl.DataFrame | None :
    """
    Loads a JSON file into a Polars DataFrame.

    Args:
        json_abs_path (str): Absolute path to the JSON file.
        schema_overrides (dict, optional): Dictionary mapping column names to Polars data types.

    Returns:
        pl.DataFrame | None: The loaded Polars DataFrame, or None if an error occurred.
    """
    if not os.path.isfile(json_abs_path) :

        log(f"[-] File {json_abs_path} not found...", "error")
        return None


    try :
            
        start = time.time()

        df = pl.read_json(

            source=json_abs_path,
            schema_overrides=schema_overrides

        )

        log(f"[*] [POLARS] Read in {time.time() - start:.2f} seconds from JSON {json_abs_path}", "info")

        return df

    except Exception as e :

        log(f"[-] Error during convertion of {json_abs_path} : {e}", "error")
    
        return None


def export_dataframe_to_excel (df : pl.DataFrame, sheet_name : str = "Sheet1", output_abs_path : str = None) -> dict :
    """
    Exports a Polars DataFrame to an Excel file.

    Args:
        df (pl.DataFrame): The DataFrame to export.
        sheet_name (str): Name of the Excel sheet. Default is "Sheet1".
        output_abs_path (str): Absolute path to output the Excel file.

    Returns:
        response (dict) : Dictionary containing:
            - 'success' (bool): Whether the export was successful.
            - 'message' (str): Description of the result.
            - 'path' (str): Output file path if successful.
    """
    response = {

        'success' :  False,
        'message' : None,
        'path' : None

    }

    if output_abs_path is None or output_abs_path == "" :

        response["message"] = "Output path not specified."
        return response
    
    try :

        start = time.time()

        df.write_excel(
        
            workbook=output_abs_path,
            sheet_name=sheet_name

        )

        duration = time.time() - start

        log(f"[+] [POLARS] Excel written in {duration:.2f} seconds to {output_abs_path}", "info")

        response["success"] = True
        response["message"] = "Export Successful"
        response["path"] = output_abs_path
    
    except Exception as e :

        log(f"[-] Failed to export DataFrame to Excel: {e}", "error")

        response["message"] = f"Export failed : {e}"
    
    finally :

        return response
    

def export_dataframe_to_json (df : pl.DataFrame, output_abs_path : str = None) -> dict :
    """
    Exports a Polars DataFrame to a JSON file.

    Args:
        df (pl.DataFrame): The Polars DataFrame to export.
        output_abs_path (str, optional): The absolute path where the JSON file will be saved. If None, the file is not saved.

    Returns:
        response (dict) : A dictionary containing:
            - 'success' (bool): Whether the export was successful or not.
            - 'message' (str): A message describing the result.
            - 'path' (str or None): The output file path if successful, None otherwise.
    """
    response = {

        'success' : False,
        'message' : None,
        'path' : None

    }

    if output_abs_path is None or output_abs_path == "" :
        
        response['message'] = "Output path not specified."
        return response
    
    try :

        start = time.time()

        df.write_json(

            file=output_abs_path

        )

        duration = time.time() - start
        log(f"[+] [POLARS] JSON written in {duration:.2f} seconds to {output_abs_path}", "info")

        response["success"] = True
        response["message"] = "Export Successful"
        response['path'] = output_abs_path

    except Exception as e :

        log(f"[-] Failed to export DataFrame to JSON: {e}", "error")

        response["message"] = f"Export failed : {e}"

    finally :

        return response
    

def export_dataframe_to_csv (df : pl.DataFrame, separator : str = ",", output_abs_path : str = None) -> dict :
    """
    Exports a Polars DataFrame to a CSV file.

    Args:
        df (pl.DataFrame): The Polars DataFrame to export.
        decimal_coma (bool, optional): Whether to use a comma as the decimal separator (True) or a period (False). Defaults to False.
        output_abs_path (str): The absolute path where the CSV file will be saved. If None, the file is not saved.

    Returns:
        response (dict) : A dictionary containing:
            - 'success' (bool): Whether the export was successful or not.
            - 'message' (str): A message describing the result.
            - 'path' (str or None): The output file path if successful, None otherwise.
    """
    response = {

        'success' : False,
        'message' : None,
        'path' : None

    }

    if output_abs_path is None or output_abs_path == "" :
        
        response['message'] = "Output path not specified."
        return response
    
    try : 

        start = time.time()

        df.write_csv(

            file=output_abs_path,
            # decimal_comma=decimal_comma # Error here due to the polars version
            separator=separator
        )

        duration = time.time() - start
        log(f"[+] [POLARS] CSV written in {duration:.2f} seconds to {output_abs_path}", "info")

        response["success"] = True
        response["message"] = "Export Successful"
        response['path'] = output_abs_path

    except Exception as e :

        log(f"[-] Failed to export DataFrame to CSV: {e}", "error")

        response["message"] = f"Export failed : {e}"

    finally :

        return response