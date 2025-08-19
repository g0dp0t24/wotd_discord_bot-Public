import helper_functions as hf
import sheets_api

# hf.logging.basicConfig(filename='data_entryDB.log', level=hf.logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_entrySuccess(newWord_entry):
    hf.logging.info(f"new word detected and added to DB: {newWord_entry}")

hf.log_duplicate('randomWord')