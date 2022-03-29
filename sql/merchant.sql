insert into merchant (merchant_name, merchant_email, merchant_pw, merchant_location) values ('Western', 'western0@odnoklassniki.ru', crypt('aVOkhzbkY', gen_salt('bf')), 'West');
insert into merchant (merchant_name, merchant_email, merchant_pw, merchant_location) values ('Malaysian', 'malaysian@google.com.au', crypt('8K0CN0I', gen_salt('bf')), 'North');
insert into merchant (merchant_name, merchant_email, merchant_pw, merchant_location) values ('Japanese', 'japanese@plala.or.jp', crypt('C0JSMj', gen_salt('bf')), 'East');
insert into merchant (merchant_name, merchant_email, merchant_pw, merchant_location) values ('Chinese', 'chinese@senate.gov', crypt('SiOUtMMyQ', gen_salt('bf')), 'East');
insert into merchant (merchant_name, merchant_email, merchant_pw, merchant_location) values ('Fast Food', 'fastfood4@comsenz.com', crypt('LsbUwPtJ', gen_salt('bf')), 'West');
insert into merchant (merchant_name, merchant_email, merchant_pw, merchant_location) values ('Drinks', 'drinks@zdnet.com', crypt('GdvXGvs', gen_salt('bf')), 'Central');
insert into merchant (merchant_name, merchant_email, merchant_pw, merchant_location) values ('Indian', 'indian@reverbnation.com', crypt('3uowkLa', gen_salt('bf')), 'East');
insert into merchant (merchant_name, merchant_email, merchant_pw, merchant_location) values ('Dessert', 'dessert@quantcast.com', crypt('3NeXUZk', gen_salt('bf')), 'South');

-- TEST DONATIONS TRIGGER
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-02-07 20:00:00', 'krowena9@de.vu', 'fastfood4@comsenz.com', 2.60);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-03-07 20:00:00', 'krowena9@de.vu', 'fastfood4@comsenz.com', 30.60);
INSERT INTO donation (donation_date, donor_email, merchant_email, donation_amt)
VALUES 	(timestamp '2022-03-08 20:00:00', 'krowena9@de.vu', 'fastfood4@comsenz.com', 100.60);