-- POSTGRES EXTENSIONS
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- FOR PASSWORD HASHING
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- FOR GENERATING RANDOM UUID

-- DONOR ENTITY TABLE
CREATE TABLE IF NOT EXISTS donor (
	donor_name VARCHAR NOT NULL CHECK (LENGTH(TRIM(donor_name)) > 0),
	donor_email VARCHAR PRIMARY KEY CHECK (LENGTH(TRIM(donor_email)) > 0),
	donor_pw VARCHAR NOT NULL CHECK (LENGTH(TRIM(donor_email)) > 2), -- TODO: SET TO >5 EVENTUALLY
	coin INT NOT NULL DEFAULT 0 CHECK (coin >= 0)
);

SELECT LENGTH(TRIM(' '));

-- BENEFICIARY ENTITY TABLE
CREATE TABLE IF NOT EXISTS beneficiary (
	benef_name VARCHAR NOT NULL CHECK (LENGTH(TRIM(benef_name)) > 0),
	benef_email VARCHAR PRIMARY KEY CHECK (LENGTH(TRIM(benef_email)) > 0),
	benef_pw VARCHAR NOT NULL CHECK (LENGTH(TRIM(benef_pw)) > 7),
	household_income DECIMAL(5,2) NOT NULL CHECK (household_income >= 0),
	benef_location VARCHAR NOT NULL
	CONSTRAINT benef_location
	CHECK( benef_location = 'North'
		OR benef_location = 'South'
		OR benef_location = 'East'
		OR benef_location = 'West'
		OR benef_location = 'Central'
	)
);

-- MERCHANT ENTITY TABLE
CREATE TABLE IF NOT EXISTS merchant (
	merchant_name VARCHAR NOT NULL CHECK (LENGTH(TRIM(merchant_name)) > 0),
	merchant_email VARCHAR PRIMARY KEY CHECK (LENGTH(TRIM(merchant_email)) > 0),
	merchant_pw VARCHAR NOT NULL CHECK (LENGTH(TRIM(merchant_pw)) > 7),
	merchant_location VARCHAR NOT NULL
	CONSTRAINT merchant_location 
	CHECK( merchant_location = 'North' 
		OR merchant_location = 'South' 
		OR merchant_location = 'East'
		OR merchant_location = 'West'
		OR merchant_location = 'Central'
	)
);

-- FOOD ENTITY TABLE
CREATE TABLE IF NOT EXISTS food (
	food_sn VARCHAR PRIMARY KEY
	    DEFAULT uuid_generate_v4()
        CHECK (LENGTH(TRIM(food_sn)) > 0),
	food_name VARCHAR NOT NULL CHECK (LENGTH(TRIM(food_name)) > 0),
	food_desc VARCHAR NOT NULL CHECK (LENGTH(TRIM(food_desc)) > 0)
);

-- PRODUCED_BY RELATIONSHIP TABLE
CREATE TABLE IF NOT EXISTS produced_by (
	merchant_email VARCHAR,
	food_sn VARCHAR UNIQUE NOT NULL,
	FOREIGN KEY (merchant_email) REFERENCES merchant(merchant_email)
		ON UPDATE CASCADE ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY (food_sn) REFERENCES food(food_sn)
		ON UPDATE CASCADE ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED
);

-- DONATIONS RELATIONSHIP TABLE
CREATE TABLE IF NOT EXISTS donation (
	donation_date TIMESTAMP NOT NULL DEFAULT NOW(),
	donor_email VARCHAR,
	merchant_email VARCHAR,
	donation_amt NUMERIC NOT NULL CHECK (donation_amt >= 0),
	PRIMARY KEY (donation_date, donor_email, merchant_email),
	FOREIGN KEY (donor_email) REFERENCES donor(donor_email),
	FOREIGN KEY (merchant_email) REFERENCES merchant(merchant_email)
);

-- FUND TRIGGER AFTER EVERY NEW DONATION
CREATE OR REPLACE FUNCTION update_fund() RETURNS TRIGGER AS
$BODY$
BEGIN
	IF EXISTS (SELECT (1) FROM fund WHERE year_month = DATE_TRUNC('MONTH', NEW.donation_date))
	THEN
		UPDATE fund SET (total, quotient, remainder) = (
        SELECT SUM(d.donation_amt), TRUNC(SUM(d.donation_amt)/5), MOD(SUM(d.donation_amt),5)
        FROM donation d
        GROUP BY DATE_TRUNC('MONTH', d.donation_date) 
        HAVING DATE_TRUNC('MONTH', d.donation_date) = DATE_TRUNC('MONTH', NEW.donation_date)
    ) WHERE year_month = DATE_TRUNC('MONTH', NEW.donation_date);
	ELSE 
		INSERT INTO fund VALUES (DATE_TRUNC('MONTH', NEW.donation_date), NEW.donation_amt, TRUNC(NEW.donation_amt/5), MOD(NEW.donation_amt,5));
	END IF;
	RETURN NEW;
END;
$BODY$
language plpgsql;

CREATE TRIGGER trig_update_acc
AFTER INSERT ON donation
FOR EACH ROW
EXECUTE PROCEDURE update_fund();

-- FUND ENTITY TABLE
CREATE TABLE IF NOT EXISTS fund (
	year_month DATE PRIMARY KEY,
	total NUMERIC NOT NULL DEFAULT 0 CHECK (total >= 0),
	quotient NUMERIC NOT NULL DEFAULT 0 CHECK (quotient >= 0),
	remainder NUMERIC NOT NULL DEFAULT 0 CHECK (remainder >= 0)
);

-- RANDOMLY POPULATE DONATION TABLE, FOR DEMO
INSERT INTO donation
SELECT 	timestamp '2022-02-01 20:00:00' + ROUND(RANDOM()::NUMERIC,2) * (timestamp '2014-02-01 00:00:00' - timestamp '2014-01-01 00:00:00'),
		d.donor_email, m.merchant_email, ROUND((RANDOM()*10)::NUMERIC,2)
FROM donor d, merchant m
ORDER BY RANDOM() LIMIT 10;

-- COUPON RELATIONSHIP TABLE
CREATE TABLE IF NOT EXISTS coupon (
	coupon_sn VARCHAR
	    DEFAULT uuid_generate_v4()
        CHECK (LENGTH(TRIM(coupon_sn)) > 0),
	issue_date DATE NOT NULL 
	    CHECK (issue_date < expiry_date),
	expiry_date DATE NOT NULL
	    CHECK (expiry_date > issue_date),
	benef_email VARCHAR NOT NULL,
	PRIMARY KEY (coupon_sn, benef_email),
	FOREIGN KEY (benef_email) REFERENCES beneficiary(benef_email)
		ON UPDATE CASCADE ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED
);

-- CHECK RECIPIENT QUEUE
SELECT b.benef_email, b.household_income, COUNT(c.benef_email)
FROM beneficiary b LEFT JOIN coupon c
ON b.benef_email = c.benef_email 
GROUP BY b.benef_email, b.household_income
ORDER BY COUNT(c.benef_email), b.household_income;

SELECT *
FROM coupon c
WHERE c.issue_date = DATE_TRUNC('MONTH', CURRENT_TIMESTAMP);

SELECT *
FROM coupon c
WHERE c.issue_date = TIMESTAMP '2022-04-01';

-- CLAIM RELATIONSHIP TABLE
CREATE TABLE IF NOT EXISTS claim (
	coupon_sn VARCHAR UNIQUE NOT NULL,
	benef_email VARCHAR NOT NULL,
	merchant_email VARCHAR NOT NULL CHECK (merchant_email <> 'anonymous'),
	claim_date DATE NOT NULL DEFAULT NOW(),
	FOREIGN KEY (coupon_sn, benef_email) REFERENCES coupon(coupon_sn, benef_email)
);

-- CLAIM TRIGGER
CREATE OR REPLACE FUNCTION check_claim() RETURNS TRIGGER AS
$BODY$
BEGIN
	IF EXISTS (
        SELECT (1)
        FROM coupon
        WHERE (NEW.coupon_sn = coupon.coupon_sn
               AND NEW.benef_email = coupon.benef_email
               AND EXISTS (SELECT coupon_sn FROM claim WHERE claim.coupon_sn = NEW.coupon_sn)))
    THEN RAISE NOTICE 'This coupon has been claimed';
    RETURN NULL;

	ELSIF EXISTS (
        SELECT (1)
        FROM coupon
        WHERE (NEW.coupon_sn = coupon.coupon_sn AND NEW.benef_email = coupon.benef_email AND NEW.claim_date < coupon.issue_date))
    THEN RAISE NOTICE 'This coupon has not been issued.';
    RETURN NULL;

	ELSIF EXISTS (
        SELECT (1)
        FROM coupon
        WHERE (NEW.coupon_sn = coupon.coupon_sn AND NEW.benef_email = coupon.benef_email AND NEW.claim_date > coupon.expiry_date))
    THEN RAISE NOTICE 'This coupon has expired.';
    RETURN NULL;

	ELSIF EXISTS (
        SELECT (1)
        FROM coupon
        WHERE (NEW.coupon_sn = coupon.coupon_sn AND NEW.benef_email != coupon.benef_email))
    THEN RAISE NOTICE 'This coupon does not belong to you.';
    RETURN NULL;

	ELSE 
		UPDATE coupon
		SET claimed = TRUE
		WHERE (NEW.coupon_sn = coupon.coupon_sn AND NEW.benef_email = coupon.benef_email);

	END IF;
	RETURN NEW;
END;
$BODY$
language plpgsql;

CREATE TRIGGER check_claim
BEFORE INSERT ON claim
FOR EACH ROW
EXECUTE PROCEDURE check_claim();

-- MEMBER/ROLE TESTING, CAN REMOVE
-- CREATE TABLE IF NOT EXISTS role (
--     role_name VARCHAR PRIMARY KEY
-- 	CONSTRAINT role_name
-- 	CHECK( role_name = 'anonymous'
-- 		OR role_name = 'donor'
-- 		OR role_name = 'beneficiary'
-- 		OR role_name = 'merchant'
-- 		OR role_name = 'manager'
-- 	)
-- );

-- CREATE TABLE IF NOT EXISTS member (
--     email VARCHAR NOT NULL,
--     role_name VARCHAR NOT NULL,
--     FOREIGN KEY (email)
--     REFERENCES donor(donor_email), beneficiary(benef_email), merchant(merchant_email)
-- );
--
-- CREATE TABLE IF NOT EXISTS anonymous (
--     one_row_only BOOL PRIMARY KEY DEFAULT TRUE,
--     donor_email VARCHAR UNIQUE NOT NULL DEFAULT 'anonymous',
--     merchant_email VARCHAR UNIQUE NOT NULL DEFAULT 'anonymous'
--     CONSTRAINT one_row_only CHECK (one_row_only)
-- );
-- INSERT INTO anonymous DEFAULT VALUES;
-- INSERT INTO anonymous VALUES (FALSE, 'a', 'b');
-- DELETE FROM anonymous;

--- TABLE POPULATION RUNNING ORDER
-- 0. run everything on top sequentially
-- 1. donor.sql
-- 2. merchant.sql
-- 3. beneficiary.sql
-- 4. donation.sql
-- 5. food_produced_by.sql (uuid must be copied from food table since this is manual)
-- 6. run coupon allocation below first
-- 7. check uuid from coupon table then populate claims table (only 2nd uuid should appear in claims)

-- COUPON ALLOCATION: FRONTEND CONTROLLED
INSERT INTO coupon (issue_date, expiry_date, benef_email)
SELECT	DATE_TRUNC('MONTH', a.year_month + INTERVAL '1 month') AS issue_date,
		DATE_TRUNC('MONTH', a.year_month + INTERVAL '2 month') AS expiry_date,
		benef_email
FROM fund a
CROSS JOIN LATERAL (
	SELECT b.benef_email
	FROM beneficiary b LEFT JOIN coupon c
	ON b.benef_email = c.benef_email
	GROUP BY b.benef_email, b.household_income, a.year_month
	HAVING a.year_month = DATE_TRUNC('MONTH', TIMESTAMP '2022-03-01')
	ORDER BY COUNT(c.benef_email), b.household_income
	LIMIT a.quotient
) AS benef_email;

-- POPULATE CLAIM TABLE (FILL COUPON_SN MANUALLY)

INSERT INTO claim (coupon_sn, benef_email, claim_date) values ('e361bbda-b567-4170-a576-a6c78a40bc38', 'kdeetch5@stumbleupon.com', TIMESTAMP '2022-03-15'); -- [1]
INSERT INTO claim (coupon_sn, benef_email, claim_date) values ('e361bbda-b567-4170-a576-a6c78a40bc38', 'kdeetch5@stumbleupon.com', TIMESTAMP '2022-05-15'); -- [1]
INSERT INTO claim (coupon_sn, benef_email, claim_date) values ('a13676d8-1bdd-4db5-89b8-36804a8f51d0', 'mkilmasterf@mapy.cz', TIMESTAMP '2022-04-15'); -- [2] ONLY THIS UUID SHOULD WORK
INSERT INTO claim (coupon_sn, benef_email, claim_date) values ('8180cf92-986b-4689-8eda-7aaf2bf021a8', 'lmilbya@buzzfeed.com', TIMESTAMP '2021-03-15'); -- [3]
INSERT INTO claim (coupon_sn, benef_email, claim_date) values ('8180cf92-986b-4689-8eda-7aaf2bf021a8', 'elisha@buzzfeed.com', TIMESTAMP '2022-04-15'); -- [3]

---
