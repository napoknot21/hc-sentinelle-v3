import pandas as pd


def format_numeric_column (dataframe : pd.DataFrame, column : str, round_v=2) -> pd.DataFrame :
    """
    Formats a numeric column in a DataFrame by:
    - removing commas from the values (e.g., "1,000" -> "1000")
    - converting values to float
    - rounding to 'round_v' decimal places
    - formatting as strings with thousands separators and fixed decimal places

    Args:
        df (pd.DataFrame): Input DataFrame
        column (str): Name of the column to format
        round_v (int, optional): Number of decimals to round to (default=2)

    Returns:
        pd.DataFrame: A copy of the DataFrame with the formatted column as strings
    """
    df = dataframe.copy()

    df[column] = pd.to_numeric(df[column].astype(str).str.replace(",", ""), errors='coerce')
    df[column] = df[column].apply( lambda x : round(x, round_v))
    df[column] = df[column].apply( lambda x : "{:,.2f}".format(x))

    return df