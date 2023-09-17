"""scraibe/agent.py"""

from uuid import uuid4

import pandas as pd
from codeinterpreterapi import CodeInterpreterSession, File
from codeinterpreterapi.schema import CodeInterpreterResponse
from dotenv import load_dotenv

from config import DATA_DIR, PROJECT_DIR
from scraibe import SUBJECT_ID

load_dotenv(PROJECT_DIR.joinpath(".env"))


def prepare_data():
    """
    Read the data from /db/*.csv and filter subject_id == SUBJECT_ID if possible.
    Then save it to data/*.csv
    """

    db_dir = PROJECT_DIR.joinpath("db", "mimic")
    original_files = [fp for fp in db_dir.glob("*.csv")]

    for fp in original_files:
        print(f"Processing {fp.name}")
        # Do not read the first column as index
        df = pd.read_csv(fp)

        if "subject_id" in df.columns:
            df = df[df["subject_id"] == SUBJECT_ID]

        df.to_csv(DATA_DIR.joinpath("split", fp.name))
        print(f"Saved to {DATA_DIR.joinpath('split', fp.name)}")


async def analyze_data(files: list[File]) -> dict[str, dict[str, str]]:
    response = {}

    async with CodeInterpreterSession(max_iterations=25) as session:
        for dataset in files:
            # define the user request
            user_request = (
                "You're a seasoned medical data scientist with expertise in generating insightful visualizations. "
                "Examine the provided dataset with a sharp clinical perspective. "
                "Break down its primary features and present concise summaries to illuminate the essence of the data. "
                "Dive into the dataset from various perspectives to obtain an initial grasp of its potential. "
                "Your analysis should provide the data science team with rich, multidimensional insights. "
                "Only generate visualizations if they are truly meaningful. "
                "It is not required to generate a visual for each dataset table. "
                "Logically analyze and build on top of each table, which composes a part of the dataset as a whole. "
                "Build on top of each table's analysis to provided a holistic analysis that can be used in future."
            )

            resp = await session.agenerate_response(
                user_request,
                files=[dataset],
                detailed_error=True,
            )

            data = {"text": resp.content, "images": []}

            # Save the visualizations
            for file in resp.files:
                fp = DATA_DIR.joinpath("visualizations", f"{uuid4()}.png")
                file.save_image(fp)
                data["images"].append(str(fp))

            response.update({dataset.name: data})

            # Output to the user
            # print("AI: ", resp.content)
            # for file in resp.files:
            #     file.show_image()

        return response


async def generate_visuals(
    files: list[File], resp: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    processed_files = set()
    response = {}

    async with CodeInterpreterSession(max_iterations=40) as session:
        for name, data in resp.items():
            info_request = f"""
            Given the previous analysis, please summarize the key findings...
            {data['text']}  # Getting the text from the previous response
            """
            info_response = await session.agenerate_response(
                info_request,
                files=[dataset for dataset in files if dataset.name == name],
                detailed_error=True,
            )

            visualization_request = f"""
            Based on the summarized findings:
            {info_response.content}
            Design a mix of visual representations...
            """

            visual_response = await session.agenerate_response(
                visualization_request,
                files=[
                    dataset
                    for dataset in files
                    if dataset.name == name and dataset.name not in processed_files
                ],
                detailed_error=True,
            )

            data = {"text": visual_response.content, "images": []}

            # Save the visualizations
            for file in visual_response.files:
                if file.name not in processed_files:
                    fp = DATA_DIR.joinpath("visualizations", f"{uuid4()}.png")
                    file.save_image(fp)
                    data["images"].append(str(fp))
                    processed_files.add(file.name)

            response[name] = data

    return response


if __name__ == "__main__":
    # prepare_data()

    import asyncio

    _files = [
        File.from_path("data/split/d_hcpcs.csv"),
        File.from_path("data/split/patients.csv"),
        File.from_path("data/split/hcpcsevents.csv"),
        File.from_path("data/split/icustays.csv"),
        File.from_path("data/split/procedures_icd.csv"),
        File.from_path("data/split/drgcodes.csv"),
        File.from_path("data/split/transfers.csv"),
        File.from_path("data/split/diagnoses_icd.csv"),
        File.from_path("data/split/microbiologyevents.csv"),
        File.from_path("data/split/outputevents.csv"),
        File.from_path("data/split/prescriptions.csv"),
        File.from_path("data/split/pharmacy.csv"),
        File.from_path("data/split/d_items.csv"),
    ]

    _data = {
        "d_hcpcs.csv": {
            "content": "Here are the results of the analysis:\n\n- There are 89,200 unique HCPCS codes in the dataset.\n- The `category` column has 6,844 missing values, and the `long_description` column has 82,400 missing values. There are no missing values in the other columns.\n- The histograms show the distribution of the length of the long and short descriptions. Most of the long descriptions have a length of around 50 characters, while most of the short descriptions have a length of around 10 characters.\n\nThe large number of missing values in the `long_description` column is concerning. This column could potentially contain important information about the medical procedures, so it might be worth investigating why these values are missing.\n\nThe next step could be to examine the `category` column to see if it contains any useful information. We could also look at the most common words in the descriptions to get a better understanding of the types of medical procedures in the dataset."
        },
        "patients.csv": {
            "content": "The dataset contains the following columns:\n\n- `Unnamed: 0`: This seems to be an index column.\n- `subject_id`: This is likely a unique identifier for each patient.\n- `gender`: The gender of the patient.\n- `anchor_age`: The age of the patient.\n- `anchor_year`: The year of the patient's visit.\n- `anchor_year_group`: The year group of the patient's visit.\n- `dod`: This could be the date of death of the patient, but it's not clear without more context.\n\nLet's continue by examining the data types of each column, checking for missing values, and getting some basic statistics for the numerical columns."
        },
        "hcpcsevents.csv": {
            "content": "The basic statistics for the numerical columns in the `hcpcsevents.csv` dataset are as follows:\n\n- `Unnamed: 0`: This column ranges from 20 to 25, with a mean of 22.5. Since this is likely an index column, these statistics may not be very meaningful.\n- `subject_id`: All rows have the same subject ID of 10014354. This suggests that all the events in this dataset are for the same patient.\n- `hadm_id`: This column has a mean of approximately 24,648,430, with a standard deviation of approximately 2,595,482. The minimum value is 20,900,960 and the maximum value is 27,494,880. This suggests that the dataset includes events from a range of different hospital admissions.\n- `seq_num`: All rows have the same sequence number of 1. This suggests that each event is the first event of its respective hospital admission.\n\nNext, let's examine the non-numerical columns in the dataset. We can look at the unique values in the `hcpcs_cd` and `short_description` columns to get a better understanding of the types of procedures and services in the dataset."
        },
        "icustays.csv": {
            "content": "The `icustays.csv` dataset contains the following columns:\n\n- `Unnamed: 0`: This seems to be an index column.\n- `subject_id`: This is likely a unique identifier for each patient.\n- `hadm_id`: This could be a unique identifier for each hospital admission.\n- `stay_id`: This could be a unique identifier for each ICU stay.\n- `first_careunit`: The first care unit the patient was admitted to during their ICU stay.\n- `last_careunit`: The last care unit the patient was in during their ICU stay.\n- `intime`: The time the patient was admitted to the ICU.\n- `outtime`: The time the patient was discharged from the ICU.\n- `los`: The length of stay in the ICU, in days.\n\nThe dataset contains 4,000 rows and 9 columns. There are no missing values in the dataset.\n\nThe `first_careunit` and `last_careunit` columns contain the names of the care units, which could be useful for understanding the types of care the patients received. The `intime` and `outtime` columns contain timestamps, which could be useful for understanding the timing of the ICU stays. The `los` column contains the length of stay in the ICU, which could be useful for understanding the severity of the patients' conditions.\n\nNext, let's examine the distribution of the `los` column and the unique values in the `first_careunit` and `last_careunit` columns."
        },
        "procedures_icd.csv": {
            "content": "The `procedures_icd.csv` dataset contains the following columns:\n\n- `Unnamed: 0`: This seems to be an index column.\n- `subject_id`: This is likely a unique identifier for each patient.\n- `hadm_id`: This could be a unique identifier for each hospital admission.\n- `seq_num`: This could be a sequence number for the procedures performed during each hospital admission.\n- `chartdate`: The date of the procedure.\n- `icd_code`: The ICD code for the procedure.\n- `icd_version`: The version of the ICD code.\n\nThe dataset contains information about the procedures performed during each hospital admission. The `icd_code` and `icd_version` columns could be useful for understanding the types of procedures performed. The `chartdate` column could be useful for understanding the timing of the procedures.\n\nNext, let's examine the unique values in the `icd_code` and `icd_version` columns, and the distribution of the `chartdate` column."
        },
        "drgcodes.csv": {
            "content": "The `drgcodes.csv` dataset contains the following columns:\n\n- `Unnamed: 0`: This seems to be an index column.\n- `subject_id`: This is likely a unique identifier for each patient.\n- `hadm_id`: This could be a unique identifier for each hospital admission.\n- `drg_type`: The type of Diagnosis-Related Group (DRG).\n- `drg_code`: The code of the DRG.\n- `description`: The description of the DRG.\n- `drg_severity`: The severity of the DRG.\n- `drg_mortality`: The mortality rate of the DRG.\n\nThe dataset contains information about the DRGs associated with each hospital admission. The `drg_type`, `drg_code`, `description`, `drg_severity`, and `drg_mortality` columns could be useful for understanding the types of diagnoses and their severity and mortality rates.\n\nNext, let's examine the unique values in the `drg_type` and `drg_code` columns, and the distribution of the `drg_severity` and `drg_mortality` columns."
        },
        "transfers.csv": {
            "content": "The `transfers.csv` dataset contains the following columns:\n\n- `Unnamed: 0`: This seems to be an index column.\n- `subject_id`: This is likely a unique identifier for each patient.\n- `hadm_id`: This could be a unique identifier for each hospital admission.\n- `transfer_id`: This could be a unique identifier for each transfer.\n- `eventtype`: The type of event that triggered the transfer.\n- `careunit`: The care unit involved in the transfer.\n- `intime`: The time the transfer started.\n- `outtime`: The time the transfer ended.\n- `los`: The length of the transfer, in days.\n\nThe dataset contains information about the transfers that occurred during each hospital admission. The `eventtype` and `careunit` columns could be useful for understanding the types of events that trigger transfers and the types of care units involved in transfers. The `intime` and `outtime` columns could be useful for understanding the timing of the transfers. The `los` column contains the length of the transfer, which could be useful for understanding the duration of the transfers.\n\nNext, let's examine the unique values in the `eventtype` and `careunit` columns, and the distribution of the `los` column."
        },
        "diagnoses_icd.csv": {
            "content": "The `diagnoses_icd.csv` dataset contains the following columns:\n\n- `Unnamed: 0`: This seems to be an index column.\n- `subject_id`: This is likely a unique identifier for each patient.\n- `hadm_id`: This could be a unique identifier for each hospital admission.\n- `seq_num`: This could be a sequence number for the diagnoses made during each hospital admission.\n- `icd_code`: The ICD code for the diagnosis.\n- `icd_version`: The version of the ICD code.\n\nThe dataset contains information about the diagnoses made during each hospital admission. The `icd_code` and `icd_version` columns could be useful for understanding the types of diagnoses made.\n\nNext, let's examine the unique values in the `icd_code` and `icd_version` columns. We can also look at the distribution of the `seq_num` column to understand the number of diagnoses made during each hospital admission."
        },
        "microbiologyevents.csv": {
            "content": "The `microbiologyevents.csv` dataset contains the following columns:\n\n- `Unnamed: 0`: This seems to be an index column.\n- `subject_id`: This is likely a unique identifier for each patient.\n- `hadm_id`: This could be a unique identifier for each hospital admission.\n- `chartdate`: The date of the microbiology event.\n- `spec_itemid`: The item ID of the specimen.\n- `spec_type_desc`: The description of the specimen type.\n- `org_itemid`: The item ID of the organism.\n- `org_name`: The name of the organism.\n- `ab_itemid`: The item ID of the antibiotic.\n- `ab_name`: The name of the antibiotic.\n- `dilution_text`: The dilution text.\n- `dilution_comparison`: The dilution comparison.\n- `dilution_value`: The dilution value.\n- `interpretation`: The interpretation of the results.\n\nThe dataset contains information about microbiology events that occurred during each hospital admission. The `spec_itemid`, `spec_type_desc`, `org_itemid`, `org_name`, `ab_itemid`, `ab_name`, `dilution_text`, `dilution_comparison`, `dilution_value`, and `interpretation` columns could be useful for understanding the types of specimens, organisms, and antibiotics involved in the events, as well as the results of the events.\n\nNext, let's examine the unique values in the `spec_type_desc`, `org_name`, `ab_name`, and `interpretation` columns. We can also look at the distribution of the `chartdate` column to understand the timing of the microbiology events."
        },
        "outputevents.csv": {
            "content": "The `outputevents.csv` dataset contains the following columns:\n\n- `Unnamed: 0`: This seems to be an index column.\n- `subject_id`: This is likely a unique identifier for each patient.\n- `hadm_id`: This could be a unique identifier for each hospital admission.\n- `stay_id`: This could be a unique identifier for each ICU stay.\n- `charttime`: The time of the output event.\n- `itemid`: The item ID of the output.\n- `value`: The value of the output.\n- `valueuom`: The unit of measure of the output.\n- `storetime`: The time the output was stored.\n- `cgid`: The ID of the caregiver who recorded the output.\n- `stopped`: Whether the output was stopped.\n- `newbottle`: Whether a new bottle was used for the output.\n- `iserror`: Whether there was an error in recording the output.\n\nThe dataset contains information about output events that occurred during each ICU stay. The `itemid`, `value`, `valueuom`, `storetime`, `cgid`, `stopped`, `newbottle`, and `iserror` columns could be useful for understanding the types of outputs and any issues with the outputs.\n\nNext, let's examine the unique values in the `itemid`, `valueuom`, `stopped`, `newbottle`, and `iserror` columns. We can also look at the distribution of the `value` column to understand the range of output values."
        },
        "prescriptions.csv": {
            "content": "The `prescriptions.csv` dataset contains the following columns:\n\n- `Unnamed: 0`: This seems to be an index column.\n- `subject_id`: This is likely a unique identifier for each patient.\n- `hadm_id`: This could be a unique identifier for each hospital admission.\n- `stay_id`: This could be a unique identifier for each ICU stay.\n- `starttime`: The start time of the prescription.\n- `stoptime`: The stop time of the prescription.\n- `drug_type`: The type of drug prescribed.\n- `drug`: The name of the drug prescribed.\n- `drug_name_poe`: The name of the drug as entered by the provider.\n- `drug_name_generic`: The generic name of the drug.\n- `formulary_drug_cd`: The formulary drug code.\n- `gsn`: The group sequential number of the drug.\n- `ndc`: The National Drug Code of the drug.\n- `prod_strength`: The strength of the drug.\n- `dose_val_rx`: The dose value of the drug.\n- `dose_unit_rx`: The dose unit of the drug.\n- `form_val_disp`: The form value dispensed.\n- `form_unit_disp`: The form unit dispensed.\n- `route`: The route of administration.\n\nThe dataset contains information about prescriptions given during each ICU stay. The `drug_type`, `drug`, `drug_name_poe`, `drug_name_generic`, `formulary_drug_cd`, `gsn`, `ndc`, `prod_strength`, `dose_val_rx`, `dose_unit_rx`, `form_val_disp`, `form_unit_disp`, and `route` columns could be useful for understanding the types of drugs prescribed and their dosages.\n\nNext, let's examine the unique values in the `drug_type`, `drug`, `drug_name_poe`, `drug_name_generic`, `formulary_drug_cd`, `gsn`, `ndc`, `prod_strength`, `dose_val_rx`, `dose_unit_rx`, `form_val_disp`, `form_unit_disp`, and `route` columns. We can also look at the distribution of the `starttime` and `stoptime` columns to understand the timing of the prescriptions."
        },
        "pharmacy.csv": {
            "content": "The `pharmacy.csv` dataset contains the following columns:\n\n- `Unnamed: 0`: This seems to be an index column.\n- `subject_id`: This is likely a unique identifier for each patient.\n- `hadm_id`: This could be a unique identifier for each hospital admission.\n- `starttime`: The start time of the pharmacy event.\n- `stoptime`: The stop time of the pharmacy event.\n- `drug_type`: The type of drug involved in the event.\n- `drug`: The name of the drug.\n- `drug_name_poe`: The name of the drug as entered by the provider.\n- `drug_name_generic`: The generic name of the drug.\n- `formulary_drug_cd`: The formulary drug code.\n- `gsn`: The group sequential number of the drug.\n- `ndc`: The National Drug Code of the drug.\n- `prod_strength`: The strength of the drug.\n- `dose_val_rx`: The dose value of the drug.\n- `dose_unit_rx`: The dose unit of the drug.\n- `form_val_disp`: The form value dispensed.\n- `form_unit_disp`: The form unit dispensed.\n- `route`: The route of administration.\n\nThe dataset contains information about pharmacy events that occurred during each hospital admission. The `drug_type`, `drug`, `drug_name_poe`, `drug_name_generic`, `formulary_drug_cd`, `gsn`, `ndc`, `prod_strength`, `dose_val_rx`, `dose_unit_rx`, `form_val_disp`, `form_unit_disp`, and `route` columns could be useful for understanding the types of drugs involved in the events and their dosages.\n\nNext, let's examine the unique values in the `drug_type`, `drug`, `drug_name_poe`, `drug_name_generic`, `formulary_drug_cd`, `gsn`, `ndc`, `prod_strength`, `dose_val_rx`, `dose_unit_rx`, `form_val_disp`, `form_unit_disp`, and `route` columns. We can also look at the distribution of the `starttime` and `stoptime` columns to understand the timing of the pharmacy events."
        },
        "d_items.csv": {
            "content": "The `d_items.csv` dataset contains the following columns:\n\n- `Unnamed: 0`: This seems to be an index column.\n- `row_id`: This could be a unique identifier for each row.\n- `itemid`: The item ID.\n- `label`: The label of the item.\n- `abbreviation`: The abbreviation of the item.\n- `dbsource`: The source of the item.\n- `linksto`: The links to the item.\n- `category`: The category of the item.\n- `unitname`: The unit name of the item.\n- `param_type`: The parameter type of the item.\n- `lownormalvalue`: The low normal value of the item.\n- `highnormalvalue`: The high normal value of the item.\n\nThe dataset contains information about different items. The `itemid`, `label`, `abbreviation`, `dbsource`, `linksto`, `category`, `unitname`, `param_type`, `lownormalvalue`, and `highnormalvalue` columns could be useful for understanding the types of items and their characteristics.\n\nNext, let's examine the unique values in the `label`, `abbreviation`, `dbsource`, `linksto`, `category`, `unitname`, and `param_type` columns. We can also look at the distribution of the `lownormalvalue` and `highnormalvalue` columns to understand the range of normal values for the items."
        },
    }

    # print(asyncio.run(analyze_data(files=_files)))
    print(asyncio.run(generate_visuals(files=_files, resp=_data)))
