DROP TABLE IF EXISTS d_hcpcs;
CREATE TABLE d_hcpcs
  (-- rows=89200
     code              VARCHAR(255) NOT NULL,-- max=5
     category          TINYINT,
     long_description  TEXT,-- max=1182
     short_description TEXT NOT NULL -- max=165
  );


DROP TABLE IF EXISTS d_items;
CREATE TABLE d_items
  (-- rows=3835
     itemid          MEDIUMINT NOT NULL,
     label           TEXT NOT NULL,-- max=95
     abbreviation    VARCHAR(255) NOT NULL,-- max=50
     linksto         VARCHAR(255) NOT NULL,-- max=15
     category        VARCHAR(255) NOT NULL,-- max=27
     unitname        VARCHAR(255),-- max=19
     param_type      VARCHAR(255) NOT NULL,-- max=16
     lownormalvalue  SMALLINT,
     highnormalvalue FLOAT
  );


DROP TABLE IF EXISTS diagnoses_icd;
CREATE TABLE diagnoses_icd
  (-- rows=4677924
     subject_id  INT NOT NULL,
     hadm_id     INT NOT NULL,
     seq_num     TINYINT NOT NULL,
     icd_code    VARCHAR(255) NOT NULL,-- max=7
     icd_version TINYINT NOT NULL
  );


DROP TABLE IF EXISTS drgcodes;
CREATE TABLE drgcodes
  (-- rows=1168135
     subject_id    INT NOT NULL,
     hadm_id       INT NOT NULL,
     drg_type      VARCHAR(255) NOT NULL,-- max=4
     drg_code      VARCHAR(255) NOT NULL,-- max=4
     description   TEXT,-- max=88
     drg_severity  TINYINT,
     drg_mortality TINYINT
  );


DROP TABLE IF EXISTS hcpcsevents;
CREATE TABLE hcpcsevents
  (-- rows=144858
     subject_id        INT NOT NULL,
     hadm_id           INT NOT NULL,
     chartdate         DATETIME NOT NULL,
     hcpcs_cd          VARCHAR(255) NOT NULL,-- max=5
     seq_num           TINYINT NOT NULL,
     short_description TEXT NOT NULL -- max=165
  );


DROP TABLE IF EXISTS icustays;
CREATE TABLE icustays
  (-- rows=69619
     subject_id     INT NOT NULL,
     hadm_id        INT NOT NULL,
     stay_id        INT NOT NULL,
     first_careunit VARCHAR(255) NOT NULL,-- max=48
     last_careunit  VARCHAR(255) NOT NULL,-- max=48
     intime         DATETIME NOT NULL,
     outtime        DATETIME NOT NULL,
     los            FLOAT NOT NULL
  );


DROP TABLE IF EXISTS microbiologyevents;
CREATE TABLE microbiologyevents
  (-- rows=1026113
     microevent_id       MEDIUMINT NOT NULL,
     subject_id          INT NOT NULL,
     hadm_id             INT,
     micro_specimen_id   MEDIUMINT NOT NULL,
     chartdate           DATETIME NOT NULL,
     charttime           DATETIME,
     spec_itemid         MEDIUMINT NOT NULL,
     spec_type_desc      VARCHAR(255) NOT NULL,-- max=56
     test_seq            TINYINT NOT NULL,
     storedate           DATETIME,
     storetime           DATETIME,
     test_itemid         MEDIUMINT NOT NULL,
     test_name           VARCHAR(255) NOT NULL,-- max=66
     org_itemid          MEDIUMINT,
     org_name            VARCHAR(255),-- max=70
     isolate_num         TINYINT,
     quantity            VARCHAR(255),-- max=15
     ab_itemid           MEDIUMINT,
     ab_name             VARCHAR(255),-- max=20
     dilution_text       VARCHAR(255),-- max=6
     dilution_comparison VARCHAR(255),-- max=2
     dilution_value      FLOAT,
     interpretation      VARCHAR(255),-- max=1
     comments            VARCHAR(255)-- max=0
  );


DROP TABLE IF EXISTS outputevents;
CREATE TABLE outputevents
  (-- rows=4248828
     subject_id INT NOT NULL,
     hadm_id    INT NOT NULL,
     stay_id    INT NOT NULL,
     charttime  DATETIME NOT NULL,
     storetime  DATETIME NOT NULL,
     itemid     MEDIUMINT NOT NULL,
     value      FLOAT NOT NULL,
     valueuom   VARCHAR(255) NOT NULL -- max=2
  );


DROP TABLE IF EXISTS patients;
CREATE TABLE patients
  (-- rows=383220
     subject_id        INT NOT NULL,
     gender            VARCHAR(255) NOT NULL,-- max=1
     anchor_age        TINYINT NOT NULL,
     anchor_year       SMALLINT NOT NULL,
     anchor_year_group VARCHAR(255) NOT NULL,-- max=11
     dod               VARCHAR(255)-- max=0
  );


DROP TABLE IF EXISTS pharmacy;
CREATE TABLE pharmacy
  (-- rows=14747759
     subject_id        INT NOT NULL,
     hadm_id           INT NOT NULL,
     pharmacy_id       INT NOT NULL,
     poe_id            VARCHAR(255),-- max=14
     starttime         DATETIME,
     stoptime          DATETIME,
     medication        VARCHAR(255),-- max=84
     proc_type         VARCHAR(255) NOT NULL,-- max=21
     status            VARCHAR(255) NOT NULL,-- max=36
     entertime         DATETIME NOT NULL,
     verifiedtime      DATETIME,
     route             VARCHAR(255),-- max=28
     frequency         VARCHAR(255),-- max=25
     disp_sched        VARCHAR(255),-- max=84
     infusion_type     VARCHAR(255),-- max=2
     sliding_scale     VARCHAR(255),-- max=1
     lockout_interval  VARCHAR(255),-- max=43
     basal_rate        FLOAT,
     one_hr_max        VARCHAR(255),-- max=6
     doses_per_24_hrs  TINYINT,
     duration          FLOAT,
     duration_interval VARCHAR(255),-- max=7
     expiration_value  SMALLINT,
     expiration_unit   VARCHAR(255),-- max=14
     expirationdate    DATETIME,
     dispensation      VARCHAR(255),-- max=28
     fill_quantity     VARCHAR(255)-- max=16
  );


DROP TABLE IF EXISTS prescriptions;
CREATE TABLE prescriptions
  (-- rows=17021399
     subject_id       INT NOT NULL,
     hadm_id          INT NOT NULL,
     pharmacy_id      INT NOT NULL,
     starttime        DATETIME,
     stoptime         DATETIME,
     drug_type        VARCHAR(255) NOT NULL,-- max=8
     drug             VARCHAR(255),-- max=84
     gsn              TEXT,-- max=223
     ndc              VARCHAR(255),-- max=11
     prod_strength    TEXT,-- max=112
     form_rx          VARCHAR(255),-- max=9
     dose_val_rx      VARCHAR(255),-- max=44
     dose_unit_rx     VARCHAR(255),-- max=32
     form_val_disp    VARCHAR(255),-- max=22
     form_unit_disp   VARCHAR(255),-- max=19
     doses_per_24_hrs TINYINT,
     route            VARCHAR(255)-- max=28
  );


DROP TABLE IF EXISTS procedures_icd;
CREATE TABLE procedures_icd
  (-- rows=685414
     subject_id  INT NOT NULL,
     hadm_id     INT NOT NULL,
     seq_num     TINYINT NOT NULL,
     chartdate   DATETIME NOT NULL,
     icd_code    VARCHAR(255) NOT NULL,-- max=7
     icd_version TINYINT NOT NULL
  );


DROP TABLE IF EXISTS transfers;
CREATE TABLE transfers
  (-- rows=2192963
     subject_id  INT NOT NULL,
     hadm_id     INT,
     transfer_id INT NOT NULL,
     eventtype   VARCHAR(255) NOT NULL,-- max=9
     careunit    VARCHAR(255),-- max=48
     intime      DATETIME NOT NULL,
     outtime     DATETIME
  );
