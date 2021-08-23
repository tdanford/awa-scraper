"""Scraper
​
$ pip install pandas gspread oauth2client
$ export OAUTH2_CLIENT_ID=some_id
$ export OAUTH2_CLIENT_SECRET=some_secret
$ python scratch.py 

2021-08-22T19:07:35.511Z INFO:root:output_dir =  /tmp/output
                                              Name                                           Link Paywalled?            Date range                         Relevant search terms Approximate # of Responding Documents                                           Comments  
0  Afghanistan Independent Human Rights Commission  https://www.refworld.org/publisher/AIHRC.html         No                                                                                                        59                       Reports range from 2004-2018  
1     Congressional Research Service (CRS) Reports                https://crsreports.congress.gov         no                                                                                                      292?  This is a search engine -- it looks like there...  
2                               DOD press releases     https://www.defense.gov/Newsroom/releases/         no  1/20/2021 to present  personnel, afghan*, vulnerable, journalist,                                                                                            
3                                  DOD transcripts  https://www.defense.gov/Newsroom/Transcripts/         no  1/20/2021 to present                                                                                                                                         
4                                     DOD speeches     https://www.defense.gov/Newsroom/Speeches/         no  1/20/2021 to present                                                                                                                                         
"""
import argparse
import logging
import os
import sys
import time

import gspread
import oauth2client.client
import oauth2client.file
import pandas as pd

from oauth2client import tools

CLIENT_ID = os.environ.get("OAUTH2_CLIENT_ID")
CLIENT_SECRET = os.environ.get("OAUTH2_CLIENT_SECRET")


class REG:
    def __init__(self, output_dir=None):
        self._output_dir = os.path.abspath(output_dir)
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)
        logging.info(f"output_dir =  {self._output_dir}")
        self._sheets_creds = None

    def get_sheets_credentials(self):
        """Get google sheets google oauth credentials.
        ​
                The default google applications credentials from gcloud wont
                work cause the scopes dont match.
        """
        if self._sheets_creds:
            return self._sheets_creds

        scope = "https://www.googleapis.com/auth/spreadsheets.readonly"

        storage = oauth2client.file.Storage(os.path.join(self._output_dir, "sheets_creds.json"))
        credentials = storage.get()
        if not credentials:
            flow = oauth2client.client.OAuth2WebServerFlow(
                client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=scope
            )

            flags = tools.argparser.parse_args(args=[])
            credentials = tools.run_flow(flow, storage, flags)
            # For some reason, logging output stops after this so better to just rerun the script again.
            sys.exit()

        self._sheets_creds = credentials
        return self._sheets_creds

    def get_sheet(self):
        creds = self.get_sheets_credentials()
        gc = gspread.authorize(creds)
        sh = gc.open_by_url(
            "https://docs.google.com/spreadsheets/d/1UrfZhUviCaBWcSAUzmm_696o0sVSXFGNiVEsGPJjOFk/edit#gid=1448135732"
        )
        worksheet = sh.worksheet("Data sources to be scraped")
        data = worksheet.get_all_values()

        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)
        return df


if __name__ == "__main__":
    # Always log in UTC and output in RFC3339
    logging.Formatter.converter = time.gmtime

    formatter = logging.basicConfig(
        format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", default="./output", help="Where to dump output file")

    args = parser.parse_args()

    reg = REG(output_dir=args.output_dir)
    reg.get_sheets_credentials()

    df = reg.get_sheet()
    print(df.head())
