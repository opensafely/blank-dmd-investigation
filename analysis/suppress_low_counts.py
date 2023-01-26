import csv
import os

import pandas as pd


SUPPRESSED_OUTPUT_PATH = "output/suppressed/"


def read_issues():
    return pd.read_csv(
        "output/medication_issues.csv",
        dtype={
            "ConsultationYear": int,
            "MultilexDrug_ID": str,
            "Count_Rx": int,
        },
    )


def read_dictionary():
    return pd.read_csv(
        "output/medication_dictionary.csv",
        dtype={
            "MultilexDrug_ID": str,
            "ProductId": str,
            "FullName": str,
            "RootName": str,
            "PackDescription": str,
            "Form": str,
            "Strength": str,
            "CompanyName": str,
            "DMD_ID": str,  # could contain ints, blanks, and other strings
        },
    )


def suppress_issues(df_issues, mincount=100):
    return df_issues[df_issues.Count_Rx >= mincount]


def suppress_dictionary(df_dictionary, allowed_multilex_ids):
    return df_dictionary[df_dictionary.MultilexDrug_ID.isin(allowed_multilex_ids)]


def write_csv(df, filename):
    if not os.path.exists(SUPPRESSED_OUTPUT_PATH):
        os.makedirs(SUPPRESSED_OUTPUT_PATH, exist_ok=True)
    path = SUPPRESSED_OUTPUT_PATH + filename
    df.to_csv(
        path,
        index=False,
        quoting=csv.QUOTE_MINIMAL,
        quotechar='"',
    )


def suppress_low_counts():
    df_issues = read_issues()
    df_issues = suppress_issues(df_issues)
    write_csv(df_issues, "medication_issues.csv")

    allowed_multilex_ids = df_issues.MultilexDrug_ID.unique()

    df_dictionary = read_dictionary()
    df_dictionary = suppress_dictionary(df_dictionary, allowed_multilex_ids)
    write_csv(df_dictionary, "medication_dictionary,csv")


if __name__ == "__main__":
    suppress_low_counts()
