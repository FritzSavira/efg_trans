import os
import json
import pandas as pd


# Read session log file from \logs\sessions in pandas df
input_dir = "C:/Users/Fried/OneDrive/Dokumente/PycharmProjects_sync/efg_trans/logs/sessions/"
input_file = "session_20260212_221734_2f6fc8b0.jsonl"
input_session = os.path.join(input_dir, input_file)
session = []

try:
    with open(input_session, "r", encoding="utf-8") as file:        
        session = pd.read_json(input_session, lines=True)
                
except FileNotFoundError:
    print(f"File {input_session} not found!")
except json.JSONDecodeError:
    print(f"File {input_session} contains invalid JSON!")


pd.set_option("display.max_colwidth", 100)
ses_deu_en = session[["asr_text", "asr_confidence", "llm_text"]]
print(ses_deu_en)


# Create pandas table
# Write pandas table as csv in \logs\sessions
