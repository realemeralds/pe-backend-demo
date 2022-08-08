from flask import Flask, jsonify, request
from flask_cors import CORS

import json
import os
from dotenv import load_dotenv
from pprint import pprint

import gspread
from gspread_formatting import *

from faker import Faker

load_dotenv()
json_creds = os.getenv('GOOGLE_SHEETS_CREDS_JSON')
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

creds_dict = json.loads(json_creds)
pprint(creds_dict)
gc = gspread.service_account_from_dict(creds_dict)

app = Flask(__name__)
CORS(app)
fake = Faker()
Faker.seed(4321)

sh = gc.open("backend-demo")
ws = sh.get_worksheet(0)

# config
id_column = 1  # column with the id values
col_offset = 3  # no of rows before the checkboxes start


@app.route("/load")
def index():
    names_list = ws.col_values(1)
    # if (ws.acell("A100").value == None):
    names = [[i] + [fake.unique.name(), f"5{str(int(i >= 100))}{(i//10 + 1) % 10}"] + [
        "FALSE"]*4 for i in range(1, 200)]
    ws.delete_rows(3, 201)
    ws.append_rows(names, value_input_option='USER_ENTERED')
    print("appended?")
    print(names)

    # add checkboxes
    validation_rule = DataValidationRule(
        # condition'type' and 'values', defaulting to TRUE/FALSE
        BooleanCondition('BOOLEAN', []),
        showCustomUi=True
    )
    set_data_validation_for_cell_range(ws, "D3:G201", validation_rule)
    return jsonify({"status": "Successfully populated database!",  "data": names_list[2:]})


@app.route("/students")
def getStudents():
    if (ws.acell("A100").value == None):
        return jsonify({"status": "error", "error": "Data not populated! Visit /load first."})
    rowNames = ws.get("A2:C2")
    studentArray = []
    for student in ws.get("A3:C201"):
        itemDict = {}
        for index, item in enumerate(student):
            itemDict[rowNames[0][index].lower()] = item
        studentArray.append(itemDict)
    return jsonify(studentArray)


@app.route("/")
def get():
    return jsonify({"sheet": ws.get_all_values()})


@app.route("/post", methods=["POST"])
def post():
    '''
    Changes the checkboxes in the spreadsheet.

    HTTP POST request - JSON body:
    {
        id: string -> corresponding to id of student,
        data: {
            int from 1-4 (coresponding to column): True / False 
        }, 
        password: myPassword
    }
    '''
    r = request
    rDict = r.json
    print(rDict)
    if rDict.get("password", None) != os.getenv('PASSWORD'):
        return jsonify({"status": "error", "error": "Invalid password..."})
    index = rDict.get("id", None)
    if index:
        row = ws.find(index, in_column=1).row
        data = rDict.get("data", [])
        status = []
        for k, v in data.items():
            if v:
                cell = f"{chr(64+col_offset+int(k))}{row}"
                ws.update(cell,
                          str(ws.acell(cell).value != "TRUE").upper(), raw=False)
            status.append(
                f"updated cell {chr(64+col_offset+int(k))}{row} with value {ws.acell(cell).value}")
            print(
                f"updated cell {chr(64+col_offset+int(k))}{row} with value {ws.acell(cell).value}")
    else:
        index = rDict.get("name", None)
        if index == None:
            return jsonify({"status": "error"})
    return jsonify({"dict": rDict, "status": ", ".join(status)})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
