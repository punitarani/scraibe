"""scraibe/agent.py"""

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


async def analyze_data(files: list[File]) -> dict[str, CodeInterpreterResponse]:
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

            response.update({dataset.name: resp})

            # Output to the user
            print("AI: ", resp.content)
            for file in resp.files:
                file.show_image()

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

    print(asyncio.run(analyze_data(files=_files)))
