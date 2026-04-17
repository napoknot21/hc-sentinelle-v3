import os
import pandas as pd

from datetime import datetime as dt

from params import temp_file_path

"""
This whole file is used to speed up the process of reading files. Each file is read only once and saved in a temporary folder.

"""

def read_file(path_file, sheet_name=None):
    """
    Function to read a file. If file was not previously read, 
    it saves a temporary file in the temp_file_path folder. 
    The files are saved in ".parquet" format for speed of use.
    """

    parquet_file_name = (
        temp_file_path + 
        "\\File_" + 
        path_file.split("\\")[-1].split(".")[0] + 
        ("_Sheet_" + sheet_name if sheet_name else "") + 
        "_time_" +
        str(os.path.getmtime(path_file)) +
        ".parquet"
        )
            
    # If the file was already read, it returns the file
    if os.path.exists(parquet_file_name):
        return pd.read_parquet(parquet_file_name)
    
    # If the file was not read, it reads the file and saves it in parquet format
    df = pd.DataFrame()
    if path_file.split(".")[-1] in ["xlsx", "xls"]:
        if sheet_name:
            df = pd.read_excel(path_file, sheet_name=sheet_name, engine='openpyxl')
        else:
            df = pd.read_excel(path_file, engine='openpyxl')
    elif path_file.split(".")[-1] in ["csv"]:
        df = pd.read_csv(path_file)
    else:
        raise ValueError("File type not supported. Please use .xlsx, .xls or .csv")
    
    # Save the file in parquet format
    try:
        df.to_parquet(parquet_file_name)
    except Exception as e:
        print('Failed to convert file ', path_file, ' to parquet for quick caching')
    return df


class FileReader:
    """
    The FileReader class is a class that contains functions to help the read file function.
    """
    def __init__(self) -> None:
        pass
    
    def rebase_date(date, end=False):
        if end:
            return date.replace(hour=23, minute=59, second=59, microsecond=999)
        else:
            return date.replace(hour=0, minute=0, second=0, microsecond=0)    
        
    def get_closest_date_to_date(path, suffix, date, latest=True):
        """
        Args:
            date (datetime.date)
            path (string)
        """
        # get all the files in the directory
        prefix = os.path.basename(path)
        path = os.path.dirname(path)
        files = os.listdir(path)
        
        # filter the files to only include the ones that start with the prefix and end with the suffix
        files = [f for f in files if f.startswith(prefix) and f.endswith(suffix)]
        
        
        # get the dates from the files
        dates = [f.replace(prefix, "").replace(suffix, "") for f in files]
        dates = [dt.strptime(d, "%Y-%m-%d_%H-%M") for d in dates]
        
        # if looking for the latest date of the day
        if latest:
            # if there are file corresponding to the date
            if FileReader.rebase_date(date) in [FileReader.rebase_date(d) for d in dates]:
                date = FileReader.rebase_date(date, end=True)
                # remove the dates that are not the same day
                dates = [d for d in dates if FileReader.rebase_date(d) == FileReader.rebase_date(date)]
        
        # find the closest date
        closest_date = min(dates, key=lambda d: abs(d - date))
        
        return closest_date

    
    def find_closest_file_to_date(date, path, suffix, latest=True):
        """
        Args:
            date (datetime.date)
            path (string)
        """
        # get the closest date
        closest_date = FileReader.get_closest_date_to_date(path, suffix, date, latest=latest)
        
        # get the file
        file = path + closest_date.strftime("%Y-%m-%d_%H-%M") + suffix

        return file
    
    def list_file_in_folder(path):
        return os.listdir(path)
    
    def readCsv(date, path):
        """
        Args:
            date (datetime.date)
            path (string)
        """
        # get the closest date
        data = pd.read_csv(path)
        return data

if __name__ == '__main__':
    FileReader