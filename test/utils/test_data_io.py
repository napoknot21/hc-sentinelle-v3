import os
import pytest
import polars as pl

from src.utils.data_io import *
from src.utils.logger import log

import tempfile
import shutil


@pytest.fixture(scope="module")
def temp_dir () :
    
    # Create a tmp directory
    tmp_dir = tempfile.mkdtemp()
    yield tmp_dir
    
    # Clean after tests
    shutil.rmtree(tmp_dir)


def test_load_excel_to_dataframe (temp_dir): 
    """
    Test de la fonction load_excel_to_dataframe.
    """
    test_file = os.path.join(temp_dir, "test_excel.xlsx")

    # Dataframe creation
    df = pl.DataFrame({
        "col1": [1, 2, 3],
        "col2": [4, 5, 6]
    })

    # Exporter le DataFrame en Excel sans spécifier le sheet_name
    df.write_excel(test_file)  # Pas de sheet_name

    # Essayer de charger la feuille Excel spécifiée
    result_df = load_excel_to_dataframe(test_file, sheet_name="Sheet1")  # Peut utiliser "Sheet1" ou 0 ici

    assert result_df is not None, "Échec de la lecture du fichier Excel"
    assert result_df.shape[0] == 3, "Le nombre de lignes dans le DataFrame est incorrect"
    assert "col1" in result_df.columns, "La colonne 'col1' manque"


def test_load_csv_to_dataframe(temp_dir):
    """
    Test de la fonction load_csv_to_dataframe.
    """
    test_file = os.path.join(temp_dir, "test_csv.csv")

    # Dataframe creation
    df = pl.DataFrame({
        "col1": [1, 2, 3],
        "col2": [4, 5, 6]
    })

    # Exporter le DataFrame en CSV
    df.write_csv(test_file)

    # Essayer de charger le fichier CSV
    result_df = load_csv_to_dataframe(test_file)

    assert result_df is not None, "Échec de la lecture du fichier CSV"
    assert result_df.shape[0] == 3, "Le nombre de lignes dans le DataFrame est incorrect"
    assert "col1" in result_df.columns, "La colonne 'col1' manque"
