from turtle import st
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
id_column = 1  # column with the id values
col_offset = 3  # no of rows before the checkboxes start


@app.route("/load")
def index():
    names_list = ws.col_values(1)
    # if (ws.acell("A100").value == None):
    names = [[i] + [fake.unique.name(), f"5{str(int(i >= 100))}{(i//10 + 1) % 10}"] + [
        "FALSE"]*4 for i in range(1, 200)]
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
    rDict = r.json
    print(rDict)
    index = rDict.get("id", None)
    if index:
        row = ws.find(index, in_column=1).row
        data = rDict.get("data", [])
        status = []
        for k, v in data.items():
            ws.update(f"{chr(64+col_offset+int(k))}{row}",
                      str(bool(v)).upper(), raw=False)
            status.append(
                f"updated cell {chr(64+col_offset+int(k))}{row} with value {str(bool(v)).upper()}")
            print(
                f"updated cell {chr(64+col_offset+int(k))}{row} with value {str(bool(v)).upper()}")
    else:
        index = rDict.get("name", None)
        if index == None:
            return jsonify({"status": "error"})
    return jsonify({"dict": rDict, "status": ", ".join(status)})


if __name__ == "__main__":
    app.run(debug=True)
