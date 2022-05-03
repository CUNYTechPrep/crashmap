COPY boro FROM PROGRAM 'xzcat /docker-entrypoint-initdb.d/boro.csv.xz' CSV HEADER;
COPY nta2020 FROM PROGRAM 'xzcat /docker-entrypoint-initdb.d/nta2020.csv.xz' CSV HEADER;
COPY h3 FROM PROGRAM 'xzcat /docker-entrypoint-initdb.d/h3.csv.xz' CSV HEADER;
COPY h3_nta2020 FROM PROGRAM 'xzcat /docker-entrypoint-initdb.d/h3_nta2020.csv.xz' CSV HEADER;
--COPY collision FROM '/docker-entrypoint-initdb.d/collision.csv' CSV HEADER;
--COPY vehicle FROM '/docker-entrypoint-initdb.d/vehicle.csv' CSV HEADER;
--COPY person FROM '/docker-entrypoint-initdb.d/person.csv' CSV HEADER;

COPY public.collision (id, date, "time", latitude, longitude) FROM stdin;
1234567	2021-04-13	21:35:00	40.72158	-73.92781
\.

COPY public.vehicle (id, collision_id, state_registration, type, make, model, year, travel_direction, occupants, driver_sex, driver_license_status, driver_license_jurisdiction, pre_crash, point_of_impact, damages, public_property_damage, public_property_damage_type, contributing_factors) FROM stdin;
54321	1234567	NY	Sedan	TOYT -CAR/SUV	\N	2010	East	0	Male	Licensed	NY	Going Straight Ahead	Center Front End	{"Center Front End","No Damage","No Damage","No Damage"}	f	\N	{Unspecified,Unspecified}
\.

COPY public.person (id, collision_id, vehicle_id, type, injury, age, ejection, emotional_status, bodily_injury, position_in_vehicle, safety_equipment, location, action, complaint, role, contributing_factors, sex) FROM stdin;
1	1234567	\N	Occupant	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	Witness	\N	\N
2	1234567	54321	Occupant	\N	36	Not Ejected	Does Not Apply	Does Not Apply	Driver	Lap Belt & Harness	\N	\N	Does Not Apply	Driver	\N	Male
3	1234567	54321	Occupant	\N	36	\N	\N	\N	\N	\N	\N	\N	\N	Registrant	\N	Male
4	1234567	\N	Pedestrian	Injured	25	\N	Conscious	Head	\N	\N	Pedestrian/Bicyclist/Other Pedestrian Not at Intersection	Crossing Against Signal	None Visible	Pedestrian	{'Pedestrian/Bicyclist/Other Pedestrian Error/Confusion','Unspecified'}	Female
\.
