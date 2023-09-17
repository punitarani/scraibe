"""tests/test_agent.py"""

import asyncio

from codeinterpreterapi import File

from scraibe.agent import analyze_data


def test_analyze_data():
    """
    Test analyze_data() function.
    """

    files = [
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

    answer = asyncio.run(analyze_data(files=files))
    print(answer)


if __name__ == "__main__":
    test_analyze_data()
