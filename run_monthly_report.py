# run_monthly_report.py

import datetime
import traceback
from main import main

def run():

    print("=" * 50)
    print(
        f"Monthly Report Started: "
        f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
    )
    print("=" * 50)

    try:
        main()

        print("=" * 50)
        print(
            f"Monthly Report Completed: "
            f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
        )
        print("=" * 50)

    except Exception as e:

        print("=" * 50)
        print("MONTHLY REPORT FAILED")
        print("=" * 50)
        print(f"Error: {e}")

        traceback.print_exc()


if __name__ == "__main__":
    run()
