import os
import shutil

import pandas as pd
import pytest

from analysis.suppress_low_counts import (
    SUPPRESSED_OUTPUT_PATH,
    read_dictionary,
    read_issues,
    suppress_dictionary,
    suppress_issues,
    suppress_low_counts,
    write_csv,
)


@pytest.fixture(autouse=True)
def set_test_working_dir(monkeypatch):
    monkeypatch.chdir("tests")


def test_read_issues():
    df = read_issues()
    assert all([len(df) > 0, type(df) == pd.DataFrame])


def test_read_issues_dtypes():
    df = read_issues()
    assert all(
        [
            df.dtypes["ConsultationYear"] == int,
            df.dtypes["Count_Rx"] == int,
            df.dtypes["MultilexDrug_ID"] == object,
        ]
    )


def test_read_dictionary():
    df = read_dictionary()
    assert all([len(df) > 0, type(df) == pd.DataFrame])


def test_suppress_issues():
    df = suppress_issues(read_issues())
    assert len(df[df.Count_Rx < 100]) == 0


def test_suppress_dictionary():
    df_issues = read_issues()
    low_count_issues = df_issues[df_issues.Count_Rx < 100]
    high_count_issues = df_issues[df_issues.Count_Rx >= 100]
    low_count_only_multilex_ids = set(low_count_issues.MultilexDrug_ID.values) - set(
        high_count_issues.MultilexDrug_ID.values
    )

    df_issues = suppress_issues(df_issues)
    allowed_multilex_ids = df_issues.MultilexDrug_ID.unique()

    df_dictionary = read_dictionary()
    df_dictionary = suppress_dictionary(df_dictionary, allowed_multilex_ids)

    assert (
        len(
            df_dictionary[
                df_dictionary.MultilexDrug_ID.isin(low_count_only_multilex_ids)
            ]
        )
        == 0
    )


def test_write_csv():
    write_csv(read_issues(), "medication_issues.csv")
    write_csv(read_dictionary(), "medication_dictionary.csv")
    assert all(
        [
            os.path.exists(SUPPRESSED_OUTPUT_PATH + "medication_issues.csv"),
            os.path.exists(SUPPRESSED_OUTPUT_PATH + "medication_dictionary.csv"),
        ]
    )
    shutil.rmtree(SUPPRESSED_OUTPUT_PATH)


def test_suppress_low_counts():
    suppress_low_counts()
    assert all(
        [
            os.path.exists(SUPPRESSED_OUTPUT_PATH + "medication_issues.csv"),
            os.path.exists(SUPPRESSED_OUTPUT_PATH + "medication_dictionary.csv"),
        ]
    )
    shutil.rmtree(SUPPRESSED_OUTPUT_PATH)
