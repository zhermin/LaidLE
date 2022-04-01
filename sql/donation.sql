INSERT INTO donation
SELECT 	timestamp '2022-02-25 20:00:00' + ROUND(RANDOM()::NUMERIC,2) * (timestamp '2014-02-01 00:00:00' - timestamp '2014-01-01 00:00:00'), 
		d.email, m.email, ROUND((RANDOM()*10)::NUMERIC,2)
FROM donor d, merchant m
ORDER BY RANDOM() LIMIT 50;

INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-5 20:00:00', 'akupker1@state.tx.us', 'malaysian@google.com.au', 2.70);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-6 20:00:00', 'akupker1@state.tx.us', 'malaysian@google.com.au', 2.80);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-2 20:00:00', 'akupker1@state.tx.us', 'malaysian@google.com.au', 2.91);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-26 20:00:00', 'akupker1@state.tx.us', 'malaysian@google.com.au', 2.91);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-8 20:00:01', 'akupker1@state.tx.us', 'malaysian@google.com.au', 10.91);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-9 20:00:03', 'akupker1@state.tx.us', 'malaysian@google.com.au', 10.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-10 20:00:02', 'akupker1@state.tx.us', 'malaysian@google.com.au', 11.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-11 20:00:02', 'akupker1@state.tx.us', 'malaysian@google.com.au', 5.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-11 20:00:03', 'akupker1@state.tx.us', 'malaysian@google.com.au', 6.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-12 20:00:05', 'akupker1@state.tx.us', 'malaysian@google.com.au', 2.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-13 20:00:07', 'akupker1@state.tx.us', 'malaysian@google.com.au', 2.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-14 20:03:00', 'akupker1@state.tx.us', 'malaysian@google.com.au', 2.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-15 20:05:02', 'akupker1@state.tx.us', 'malaysian@google.com.au', 2.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-16 20:06:02', 'akupker1@state.tx.us', 'malaysian@google.com.au', 2.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-16 20:06:12', 'akupker1@state.tx.us', 'malaysian@google.com.au', 2.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-03-9 20:07:00', 'akupker1@state.tx.us', 'malaysian@google.com.au', 20.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-03-9 20:08:01', 'akupker1@state.tx.us', 'malaysian@google.com.au', 2.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-03-9 20:09:02', 'akupker1@state.tx.us', 'malaysian@google.com.au', 1.92);

INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-03-9 20:09:02', 'dyeomans0@telegraph.co.uk', 'western0@odnoklassniki.ru', 1.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-03-9 20:09:02', 'jwelbeck2@umich.edu', 'western0@odnoklassniki.ru', 10.92);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-03-19 20:09:02', 'jwelbeck2@umich.edu', 'western0@odnoklassniki.ru', 50.92);