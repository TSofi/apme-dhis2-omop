-- OMOP Common Data Model v5.4 DDL for PostgreSQL
-- Target tables: LOCATION, CARE_SITE, PERSON, DRUG_EXPOSURE, OBSERVATION

CREATE SCHEMA IF NOT EXISTS cdm;
SET search_path TO cdm, public;

DROP TABLE IF EXISTS observation CASCADE;
DROP TABLE IF EXISTS drug_exposure CASCADE;
DROP TABLE IF EXISTS person CASCADE;
DROP TABLE IF EXISTS care_site CASCADE;
DROP TABLE IF EXISTS location CASCADE;

CREATE TABLE location (
    location_id integer NOT NULL,
    address_1 varchar(50),
    address_2 varchar(50),
    city varchar(50),
    state varchar(50),
    zip varchar(9),
    county varchar(20),
    location_source_value varchar(50),
    country_concept_id integer,
    country_source_value varchar(80),
    latitude numeric,
    longitude numeric,
    CONSTRAINT xpk_location PRIMARY KEY (location_id)
);

CREATE TABLE care_site (
    care_site_id integer NOT NULL,
    care_site_name varchar(255),
    place_of_service_concept_id integer,
    location_id integer,
    care_site_source_value varchar(50),
    place_of_service_source_value varchar(50),
    CONSTRAINT xpk_care_site PRIMARY KEY (care_site_id),
    CONSTRAINT fpk_care_site_location FOREIGN KEY (location_id) REFERENCES location (location_id)
);

CREATE TABLE person (
    person_id integer NOT NULL,
    gender_concept_id integer NOT NULL,
    year_of_birth integer NOT NULL,
    month_of_birth integer,
    day_of_birth integer,
    birth_datetime timestamp,
    race_concept_id integer NOT NULL,
    ethnicity_concept_id integer NOT NULL,
    location_id integer,
    provider_id integer,
    care_site_id integer,
    person_source_value varchar(50),
    gender_source_value varchar(50),
    gender_source_concept_id integer,
    race_source_value varchar(50),
    race_source_concept_id integer,
    ethnicity_source_value varchar(50),
    ethnicity_source_concept_id integer,
    CONSTRAINT xpk_person PRIMARY KEY (person_id),
    CONSTRAINT fpk_person_care_site FOREIGN KEY (care_site_id) REFERENCES care_site (care_site_id),
    CONSTRAINT fpk_person_location FOREIGN KEY (location_id) REFERENCES location (location_id)
);

CREATE TABLE drug_exposure (
    drug_exposure_id integer NOT NULL,
    person_id integer NOT NULL,
    drug_concept_id integer NOT NULL,
    drug_exposure_start_date date NOT NULL,
    drug_exposure_start_datetime timestamp,
    drug_exposure_end_date date NOT NULL,
    drug_exposure_end_datetime timestamp,
    verbatim_end_date date,
    drug_type_concept_id integer NOT NULL,
    stop_reason varchar(20),
    refills integer,
    quantity numeric,
    days_supply integer,
    sig text,
    route_concept_id integer,
    lot_number varchar(50),
    provider_id integer,
    visit_occurrence_id integer,
    visit_detail_id integer,
    drug_source_value varchar(50),
    drug_source_concept_id integer,
    route_source_value varchar(50),
    dose_unit_source_value varchar(50),
    CONSTRAINT xpk_drug_exposure PRIMARY KEY (drug_exposure_id),
    CONSTRAINT fpk_drug_exposure_person FOREIGN KEY (person_id) REFERENCES person (person_id)
);

CREATE TABLE observation (
    observation_id integer NOT NULL,
    person_id integer NOT NULL,
    observation_concept_id integer NOT NULL,
    observation_date date NOT NULL,
    observation_datetime timestamp,
    observation_type_concept_id integer NOT NULL,
    value_as_number numeric,
    value_as_string varchar(255),
    value_as_concept_id integer,
    qualifier_concept_id integer,
    unit_concept_id integer,
    provider_id integer,
    visit_occurrence_id integer,
    visit_detail_id integer,
    observation_source_value varchar(255),
    observation_source_concept_id integer,
    unit_source_value varchar(50),
    qualifier_source_value varchar(50),
    value_source_value varchar(50),
    observation_event_id integer,
    obs_event_field_concept_id integer,
    CONSTRAINT xpk_observation PRIMARY KEY (observation_id),
    CONSTRAINT fpk_observation_person FOREIGN KEY (person_id) REFERENCES person (person_id)
);
