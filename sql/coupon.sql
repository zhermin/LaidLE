-- COUPON ALLOCATION: FRONTEND CONTROLLED
INSERT INTO coupon (issue_date, expiry_date, benef_email)
SELECT	DATE_TRUNC('MONTH', f.year_month + INTERVAL '1 MONTH') AS issue_date,
		DATE_TRUNC('MONTH', f.year_month + INTERVAL '2 MONTH') AS expiry_date,
		benef_email
FROM fund_view f
CROSS JOIN LATERAL (
	SELECT b.email AS benef_email
	FROM beneficiary b LEFT JOIN coupon c
	ON b.email = c.benef_email
	GROUP BY b.email, b.household_income, f.year_month
	HAVING f.year_month = DATE_TRUNC('MONTH', NOW() - INTERVAL '1 month')
	ORDER BY COUNT(c.benef_email), b.household_income
	LIMIT f.quotient
) AS benef_email;
