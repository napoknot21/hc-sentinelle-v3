import polars as pl

def format_numeric_column (dataframe : pl.DataFrame, column : str, round_v : int = 2) -> pl.DataFrame :
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
    df_cols = pl.col(column).cast(pl.Utf8)
    no_commas = df_cols.col.str.replace(",", "")

    as_float = no_commas.cast(pl.Float64)
    rounded = as_float.round(round_v)

    fmt_string = f"{{:,.{round_v}f}}"

    formatted = rounded.map_elements(

        lambda x: fmt_string.format(x) if x is not None else None,
        return_dtype=pl.Utf8

    )

    new_df = dataframe.with_columns([
        formatted.alias(column)
    ])

    return new_df