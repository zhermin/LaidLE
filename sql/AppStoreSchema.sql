/*******************

  Create the schema

********************/

CREATE TABLE IF NOT EXISTS donor (
 donor_email VARCHAR(64) PRIMARY KEY,
 donor_pw VARCHAR(64) NOT NULL,
 coins INT NOT NULL,
 cc_type VARCHAR(64) NOT NULL,
 cc_number VARCHAR(16) NOT NULL);
	
CREATE TABLE IF NOT EXISTS merchant (
 merchant_email VARCHAR(32) PRIMARY KEY,
 merchat_pw VARCHAR(32) NOT NULL,
 merchant_name VARCHAR(32) NOT NULL);

CREATE TABLE IF NOT EXISTS beneficiary (
benef_email VARCHAR(64) PRIMARY KEY, 
benef_pw VARCHAR(64) NOT NULL,
income INT NOT NULL CHECK (income > 0),
household_pax INT NOT NULL CHECK (household_pax > 0));



