--- TABLE POPULATION RUNNING ORDER
-- 1. run everything until ~line 300
-- 2. run the other sql files person/beneficiary/donor/merchant/food/reward/donation.sql
-- 3. run coupon.sql

-- WIPE OUT TABLES FROM SAMPLE AppStore
DROP TABLE IF EXISTS downloads;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS customers;

-- POSTGRES EXTENSIONS
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- FOR PASSWORD HASHING
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- FOR GENERATING RANDOM UUID

----------------------
-- ENTITY TABLES
----------------------

-- PERSON ENTITY TABLE
CREATE TABLE IF NOT EXISTS person (
	name VARCHAR NOT NULL CHECK (LENGTH(TRIM(name)) > 0),
	email VARCHAR PRIMARY KEY CHECK (LENGTH(TRIM(email)) > 0),
	password VARCHAR NOT NULL, -- not possible to check length of hashed password, must check from frontend
	pic VARCHAR NOT NULL DEFAULT 'https://robohash.org/laidle',
	role VARCHAR NOT NULL
	CONSTRAINT role
	CHECK (role = 'donor'
        OR role = 'merchant'
        OR role = 'beneficiary'
        OR role = 'manager')
);

-- DONOR ENTITY TABLE
CREATE TABLE IF NOT EXISTS donor (
	email VARCHAR UNIQUE NOT NULL CHECK (LENGTH(TRIM(email)) > 0),
	coin INT NOT NULL DEFAULT 0 CHECK (coin >= 0),
	FOREIGN KEY (email) REFERENCES person(email)
		ON UPDATE CASCADE ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED
);

-- BENEFICIARY ENTITY TABLE
CREATE TABLE IF NOT EXISTS beneficiary (
	email VARCHAR UNIQUE NOT NULL CHECK (LENGTH(TRIM(email)) > 0),
	household_income DECIMAL(5,2) NOT NULL CHECK (household_income >= 0),
	location VARCHAR NOT NULL
	CONSTRAINT location
	CHECK( location = 'North'
		OR location = 'South'
		OR location = 'East'
		OR location = 'West'
		OR location = 'Central'
	),
	FOREIGN KEY (email) REFERENCES person(email)
		ON UPDATE CASCADE ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED
);

-- MERCHANT ENTITY TABLE
CREATE TABLE IF NOT EXISTS merchant (
	email VARCHAR UNIQUE NOT NULL CHECK (LENGTH(TRIM(email)) > 0),
	location VARCHAR NOT NULL
	CONSTRAINT location
	CHECK( location = 'North'
		OR location = 'South'
		OR location = 'East'
		OR location = 'West'
		OR location = 'Central'
	),
	FOREIGN KEY (email) REFERENCES person(email)
		ON UPDATE CASCADE ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED
);

-- FOOD ENTITY TABLE
CREATE TABLE IF NOT EXISTS food (
	merchant_email VARCHAR NOT NULL CHECK (LENGTH(TRIM(food_name)) > 0),
	FOREIGN KEY (merchant_email) REFERENCES merchant(email)
		ON UPDATE CASCADE ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,
	food_sn VARCHAR PRIMARY KEY
	    DEFAULT uuid_generate_v4()
        CHECK (LENGTH(TRIM(food_sn)) > 0),
	food_name VARCHAR NOT NULL CHECK (LENGTH(TRIM(food_name)) > 0),
	food_desc VARCHAR NOT NULL CHECK (LENGTH(TRIM(food_desc)) > 0)
);

----------------------
-- INTERACTION TABLES
----------------------

-- DONATIONS RELATIONSHIP TABLE
CREATE TABLE IF NOT EXISTS donation (
	donation_date TIMESTAMP NOT NULL DEFAULT NOW(),
	donor_email VARCHAR,
	merchant_email VARCHAR,
	donation_amt NUMERIC NOT NULL CHECK (donation_amt >= 0),
	PRIMARY KEY (donation_date, donor_email, merchant_email),
	FOREIGN KEY (donor_email) REFERENCES donor(email)
	    ON UPDATE CASCADE ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY (merchant_email) REFERENCES merchant(email)
        ON UPDATE CASCADE ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED
);

-- TRIGGERS TO UPDATE COIN COUNT
CREATE OR REPLACE FUNCTION update_coin() RETURNS TRIGGER AS
$BODY$
BEGIN
	IF (NEW.donor_email <> 'anonymous_donor')
    THEN
        UPDATE donor
		SET coin = donor.coin + TRUNC(NEW.donation_amt/1)
        WHERE donor.email = NEW.donor_email;

	END IF;
	RETURN NULL;
END;
$BODY$
language plpgsql;

CREATE TRIGGER update_coin
AFTER INSERT ON donation
FOR EACH ROW
EXECUTE PROCEDURE update_coin();

-- FUND VIEW
-- RECURSION FOR FUND
-- CREATE BASELINE TABLE
CREATE VIEW fund_temp AS
SELECT DATE_TRUNC('MONTH', d.donation_date) AS year_month, SUM(d.donation_amt) AS month_total
FROM donation d
GROUP BY year_month
ORDER BY year_month;

-- CREATE RECURSION
CREATE VIEW fund_view AS
WITH RECURSIVE fund AS (
	SELECT 	year_month, month_total, CAST(0 AS NUMERIC) AS prev_remainder, TRUNC(month_total/5) AS quotient,
			MOD(month_total,5) AS remainder
 	FROM fund_temp ft
	WHERE ft.year_month = (
		SELECT MIN(year_month)
		FROM fund_temp
	)
	UNION ALL
	SELECT ft.year_month, ft.month_total, fd.remainder,
	TRUNC((ft.month_total + fd.remainder)/5) AS quotient,
	MOD(ft.month_total+fd.remainder,5) AS remainder
	FROM fund_temp ft, fund fd
 	WHERE ft.year_month = fd.year_month + INTERVAL '1 month'
) SELECT *
  FROM fund;

-- COUPON RELATIONSHIP TABLE
CREATE TABLE IF NOT EXISTS coupon (
	coupon_sn VARCHAR
	    DEFAULT uuid_generate_v4()
        CHECK (LENGTH(TRIM(coupon_sn)) > 0),
	issue_date DATE NOT NULL
	    DEFAULT NOW()
	    CHECK (issue_date < expiry_date),
	expiry_date DATE NOT NULL
	    DEFAULT NOW() + INTERVAL '1 MONTH'
	    CHECK (expiry_date > issue_date),
	benef_email VARCHAR NOT NULL,
	PRIMARY KEY (coupon_sn, benef_email),
	FOREIGN KEY (benef_email) REFERENCES beneficiary(email)
		ON UPDATE CASCADE ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED
);

-- RANDOMLY POPULATE DONATION TABLE, FOR DEMO
INSERT INTO donation
SELECT 	timestamp '2022-02-01 20:00:00' + ROUND(RANDOM()::NUMERIC,2) * (timestamp '2014-02-01 00:00:00' - timestamp '2014-01-01 00:00:00'),
		d.email, m.email, ROUND((RANDOM()*10)::NUMERIC,2)
FROM donor d, merchant m
ORDER BY RANDOM() LIMIT 10;

-- CHECK RECIPIENT QUEUE
CREATE VIEW recipient_queue AS
SELECT b.email, b.household_income, COUNT(c.benef_email)
FROM beneficiary b LEFT JOIN coupon c
ON b.email = c.benef_email
GROUP BY b.email, b.household_income
ORDER BY COUNT(c.benef_email), b.household_income;

-- CLAIM RELATIONSHIP TABLE
CREATE TABLE IF NOT EXISTS claim (
	coupon_sn VARCHAR UNIQUE NOT NULL,
	benef_email VARCHAR NOT NULL,
	merchant_email VARCHAR NOT NULL CHECK (merchant_email <> 'anonymous_merchant'),
	food_sn VARCHAR NOT NULL,
	claim_date DATE NOT NULL DEFAULT NOW(),
	FOREIGN KEY (coupon_sn, benef_email) REFERENCES coupon(coupon_sn, benef_email)
        ON UPDATE CASCADE ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED
);
UPDATE beneficiary SET email = ''
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

	END IF;
	RETURN NEW;
END;
$BODY$
language plpgsql;

CREATE TRIGGER check_claim
BEFORE INSERT ON claim
FOR EACH ROW
EXECUTE PROCEDURE check_claim();

--- REWARD ENTITY TABLE
CREATE TABLE IF NOT EXISTS reward (
	reward_sn VARCHAR PRIMARY KEY
	    DEFAULT uuid_generate_v4()
        CHECK (LENGTH(TRIM(reward_sn)) > 0),
	reward_name VARCHAR NOT NULL CHECK (LENGTH(TRIM(reward_name)) > 0),
	reward_desc VARCHAR NOT NULL CHECK (LENGTH(TRIM(reward_desc)) > 0),
	reward_price INT NOT NULL CHECK (reward_price > 0),
	reward_qty INT NOT NULL CHECK (reward_qty >= 0) DEFAULT 0
);

--- REWARD ENTITY TABLE
CREATE TABLE IF NOT EXISTS redemption (
	redeem_date DATE NOT NULL DEFAULT NOW(),
	reward_sn VARCHAR NOT NULL CHECK (LENGTH(TRIM(reward_sn)) > 0),
	donor_email VARCHAR NOT NULL CHECK (LENGTH(TRIM(donor_email)) > 0),
	FOREIGN KEY (donor_email) REFERENCES donor(email)
		ON UPDATE CASCADE ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY (reward_sn) REFERENCES reward(reward_sn)
		ON UPDATE CASCADE ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED
);

-- TRIGGER TO CHECK REDEMPTION AND UPDATE REWARDS
CREATE OR REPLACE FUNCTION check_redemption() RETURNS TRIGGER AS
$BODY$
BEGIN
	IF EXISTS (
        SELECT (1)
        FROM reward, donor
        WHERE NEW.reward_sn = reward.reward_sn
		AND	NEW.donor_email = donor.email
		AND donor.coin < reward.reward_price )
    THEN RAISE NOTICE 'You do not have enough coins. Donate more!';
    RETURN NULL;

	ELSIF EXISTS (
        SELECT (1)
        FROM reward
        WHERE NEW.reward_sn = reward.reward_sn
		AND	reward.reward_qty = 0 )
    THEN RAISE NOTICE 'This reward is out of stock!';
    RETURN NULL;

	ELSIF EXISTS (
        SELECT (1)
        FROM reward, donor
        WHERE NEW.reward_sn = reward.reward_sn
		AND	NEW.donor_email = donor.email
		AND donor.coin >= reward.reward_price
		AND reward.reward_qty <> 0)
	THEN
		RAISE NOTICE 'Enjoy!';
        UPDATE donor
		SET coin = coin - (SELECT reward_price
						   FROM reward
						   WHERE reward.reward_sn = NEW.reward_sn)
	 	WHERE email = NEW.donor_email;
		UPDATE reward SET reward_qty = reward_qty - 1 WHERE reward_sn = NEW.reward_sn;

	END IF;
	RETURN NEW;
END;
$BODY$
language plpgsql;

CREATE TRIGGER check_redemption
BEFORE INSERT ON redemption
FOR EACH ROW
EXECUTE PROCEDURE check_redemption();
