from distutils.command.config import config
from flask import Flask, jsonify, request
import gspread
from faker import Faker

gc = gspread.service_account()
app = Flask(__name__)
fake = Faker()
Faker.seed(4321)

sh = gc.open("backend-demo")
ws = sh.get_worksheet(0)

# config
id_column = 1 # column with the id values
col_offset = 3 # no of rows before the checkboxes start

@app.route("/load")
def index():
    names_list = ws.col_values(1)
    # if (ws.acell("A100").value == None):
    names = [[i] + [fake.unique.name(), f"5{str(int(i >= 100))}{(i//10 + 1) % 10}"] + ["FALSE"]*4 for i in range(1, 200)]
    ws.delete_rows(3, 201)
    ws.append_rows(names)
    print("appended?")
    print(names)
    return jsonify({"status": "Successfully populated database!",  "data": names_list[2:]})


@app.route("/")
def get():
    return jsonify({"sheet": ws.get_all_values()})

@app.route("/post", methods=["POST"])
def post():
    r = request
    rDict = r.form
    index = rDict.get("id", None)
    if index:
        row = ws.find(index, in_column=1).row
        for k, v in rDict.get("data", []).values:
            ws.update(f"{chr(64+col_offset+k)}{row}", str(bool(v)).upper(), raw=False)
            print(f"updated cell {chr(64+col_offset+k)}{row} with value {str(bool(v)).upper()}")
    else:
        index = rDict.get("name", None)
        if index == None:
            return jsonify({"status": "error"})
    return jsonify({"dict": rDict, "request": r})
    
# @app.errorhandler()


# the plan: have the flask app serve a gui, where names are placed alongside the 4 buttons
# each button withh have an index, with <index no.>_<hair>_<boolean>
# based on this, the server will update the google sheets

if __name__ == "__main__":
    app.run(debug=True)