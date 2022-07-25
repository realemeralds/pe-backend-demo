from flask import Flask
import gspread
from faker import Faker

gc = gspread.service_account()
app = Flask(__name__)
fake = Faker()
Faker.seed(4321)


@app.route("/")
def index():
    sh = gc.open("backend-demo")
    ws = sh.get_worksheet(0)
    names_list = ws.col_values(1)
    if (ws.acell("A100").value == None):
        names = [[fake.unique.name(), f"5{str(int(i >= 100))}{(i//10 + 1) % 10}"] + ["FALSE"]*4 for i in range(1, 200)]
        ws.delete_rows(3, 201)
        ws.append_rows(names)
        print("appended?")
        print(names)
    return f'''<p>Hello world!</p>
    {names_list[2:]}
    '''

# the plan: have the flask app serve a gui, where names are placed alongside the 4 buttons
# each button withh have an index, with <index no.>_<hair>_<boolean>
# based on this, the server will update the google sheets

if __name__ == "__main__":
    app.run(debug=True)