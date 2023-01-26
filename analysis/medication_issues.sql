SELECT
  YEAR(ConsultationDate) as ConsultationYear
  MultilexDrug_ID,
  COUNT(*) as Count_Rx
FROM OpenCorona.dbo.MedicationIssue
WHERE YEAR(ConsultationDate)>=2018
GROUP BY
  YEAR(ConsultationDate),
  MultilexDrug_ID
ORDER BY
  YEAR(ConsultationDate),
  MultilexDrug_ID
