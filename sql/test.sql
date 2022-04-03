SELECT * FROM fund_view;

-- POPULATE CLAIM TABLE (USE THE FIRST COUPON_SN AND FILL IT IN MANUALLY FOR TESTING)
INSERT INTO claim (coupon_sn, benef_email, merchant_email, food_sn, claim_date) values ('7d561d48-2d6e-4fe2-af5e-48607bd7c831', 'kdeetch5@stumbleupon.com', 'malaysian@google.com.au', '11b44b9d-fc81-49ff-a973-ec1654f154ac', TIMESTAMP '2022-03-15'); -- NOT ISSUED YET
INSERT INTO claim (coupon_sn, benef_email, merchant_email, food_sn, claim_date) values ('7d561d48-2d6e-4fe2-af5e-48607bd7c831', 'gmoylane4@bloomberg.com',  'malaysian@google.com.au', '11b44b9d-fc81-49ff-a973-ec1654f154ac', TIMESTAMP '2022-04-15'); -- SN AND BENEF DO NOT MATCH
INSERT INTO claim (coupon_sn, benef_email, merchant_email, food_sn, claim_date) values ('7d561d48-2d6e-4fe2-af5e-48607bd7c831', 'kdeetch5@stumbleupon.com', 'malaysian@google.com.au', '11b44b9d-fc81-49ff-a973-ec1654f154ac', TIMESTAMP '2022-06-15'); -- EXPIRED
INSERT INTO claim (coupon_sn, benef_email, merchant_email, food_sn, claim_date) values ('7d561d48-2d6e-4fe2-af5e-48607bd7c831', 'kdeetch5@stumbleupon.com', 'malaysian@google.com.au', '11b44b9d-fc81-49ff-a973-ec1654f154ac', TIMESTAMP '2022-04-15'); -- ONLY THIS SHOULD WORK
INSERT INTO claim (coupon_sn, benef_email, merchant_email, food_sn, claim_date) values ('7d561d48-2d6e-4fe2-af5e-48607bd7c831', 'kdeetch5@stumbleupon.com', 'malaysian@google.com.au', '11b44b9d-fc81-49ff-a973-ec1654f154ac', TIMESTAMP '2022-05-16'); -- DOUBLE CLAIM ERROR

-- POPULATE REDEMPTION TABLE (FILL IN THE COUPON_SN MANUALLY HERE AS WELL)
INSERT INTO redemption (reward_sn, donor_email) VALUES ('e2e4cc59-c181-4437-8d8a-9cefd69fcd0d', 'asimonnet3@liveinternet.ru'); -- DONOR NOT ENOUGH COINS
INSERT INTO redemption (reward_sn, donor_email) VALUES ('cdedff62-2a9b-43dd-b284-5fdfbcc12f4c', 'asimonnet3@liveinternet.ru'); -- REWARD OUT OF STOCK
INSERT INTO redemption (reward_sn, donor_email) VALUES ('cdedff62-2a9b-43dd-b284-5fdfbcc12f4c', 'akupker1@state.tx.us'); -- ONLY THIS SHOULD WORK

-- TEST INSERT/DELETE MULTIPLE COUPONS
INSERT INTO coupon (issue_date, expiry_date, benef_email) VALUES (NOW() - INTERVAL '2 MONTH', NOW() - INTERVAL '1 MONTH', 'kdeetch5@stumbleupon.com');
INSERT INTO coupon (benef_email) VALUES ('kdeetch5@stumbleupon.com');
SELECT *
FROM coupon
WHERE coupon.benef_email = 'kdeetch5@stumbleupon.com'
AND expiry_date >= NOW();

DELETE FROM claim WHERE benef_email = 'kdeetch5@stumbleupon.com';
