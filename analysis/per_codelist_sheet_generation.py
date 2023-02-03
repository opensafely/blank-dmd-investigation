from pathlib import Path

import pandas as pd
import pandas_gbq as bq


sql = """
WITH
  codelist_rootnames AS (
  SELECT
    DISTINCT LOWER(md.rootname) rootname,
    cc.codelist
  FROM
    `ebmdatalab.blank_dmd_investigation.medication_dictionary` md
  JOIN
    `ebmdatalab.blank_dmd_investigation.codelists_combined` cc
  ON
    md.dmd_id = cc.dmd_id)
SELECT
  cr.codelist,
  d.*,
  count_rx
FROM
  blank_dmd_investigation.medication_dictionary d
JOIN (
  SELECT
    multilexdrug_id,
    SUM(count_rx) count_rx
  FROM
    blank_dmd_investigation.medication_issues
  GROUP BY
    multilexdrug_id) i
ON
  d.multilexdrug_id = i.multilexdrug_id
JOIN
  codelist_rootnames cr
ON
  d.FullName LIKE CONCAT('%',cr.rootname,'%')
  OR d.rootname LIKE CONCAT('%',cr.rootname,'%')
WHERE
  dmd_id IS null
"""
df = bq.read_gbq(sql, "ebmdatalab")

codelists = [(c, c.split("/")[-1][:31]) for c in df.codelist.unique()]

output_columns = [
    "MultilexDrug_ID",
    "ProductId",
    "FullName",
    "RootName",
    "PackDescription",
    "Form",
    "Strength",
    "CompanyName",
    "count_rx",
]

codelist_totals = pd.DataFrame(columns=["codelist", "sheetname"], data=codelists)
codelist_totals = codelist_totals.merge(
    df.groupby("codelist").sum("count_rx"),
    how="inner",
    on="codelist",
).sort_values("count_rx", ascending=False)


with pd.ExcelWriter(
    Path("output") / "missing_dmd_candidates.xlsx", engine="xlsxwriter"
) as writer:
    codelist_totals.to_excel(
        writer,
        sheet_name="Totals",
        index=None,
    )
    for _, c, sheetname, _ in codelist_totals.itertuples():
        df[df.codelist == c][output_columns].to_excel(
            writer,
            sheet_name=sheetname,
            index=None,
        )
