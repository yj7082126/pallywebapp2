from azure.storage import CloudStorageAccount
from flask import Flask, request, render_template, redirect
from flask_table import Table, Col
import pandas as pd
import pyodbc
import struct
app = Flask(__name__)

def handle_datetimeoffset(dto_value):
    # ref: https://github.com/mkleehammer/pyodbc/issues/134#issuecomment-281739794
    tup = struct.unpack("<6hI2h", dto_value)  # e.g., (2017, 3, 16, 10, 35, 18, 0, -6, 0)
    tweaked = [tup[i] // 100 if i == 6 else tup[i] for i in range(len(tup))]
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:07d} {:+03d}:{:02d}".format(*tweaked)


server = 'tcp:pallyserver.database.windows.net'
database = 'PallyDB'
username = 'ExternalPerson@pallyserver'
password = 'S$*if9c lw8sdfdf'
driver= '{ODBC Driver 13 for SQL Server}'

class TaskTable(Table):
    LU = Col('LU')
    user = Col('user')
    createAt = Col('createAt')
    trial = Col('trial')
    seconds = Col('seconds')
    
class Task(object):
    def __init__(self, LU, user, createAt, trial, seconds):
        self.LU = LU
        self.user = user
        self.createAt = createAt
        self.trial = trial
        self.seconds = seconds
        
@app.route("/", methods=["GET", "POST"])
def hello():
    cnxn = pyodbc.connect("Driver=" + driver + ";Server=" + server 
                      + ",1433;Database=" + database + 
                      ";Uid=" + username + ";Pwd=" + password + ";")
    cnxn.add_output_converter(-155, handle_datetimeoffset)
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM [dbo].[LUItem]")
    row = cursor.fetchall()
    
    df = pd.DataFrame([list(t) for t in row], columns=["Id", "createAt", "updatedAt", 
                                    "version", "deleted", "user", "trial",
                                    "completed", "LU", "seconds"])
    df2 = df[['LU', 'user', 'createAt', 'trial', 'seconds']]
    df2['createAt'] = pd.to_datetime(df2['createAt'])
    df2['createAt'] = df2['createAt'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))

    if request.method == 'POST':
        print(dict(request.form).keys[0])
    else:
        table = TaskTable(df2.to_dict(orient='records'))
        table.border = True
        
    return render_template('index.html', table = table.__html__())
   
@app.route("/video", methods=["GET", "POST"])
def hello2():
    if request.method == "POST":
        ip = request.form["ip"]
        print(ip)
        return redirect("https://" + ip)
    return render_template('video.html')

@app.route("/character", methods=["GET", "POST"])
def hello3():
    account = CloudStorageAccount(account_name, account_key)
    table_service = account.create_table_service()
    
    df2 = pd.DataFrame(columns=['PartitionKey', 'RowKey', 'Character', 'URL', 'Selected'])
    tasks = table_service.query_entities(table_name2, filter="PartitionKey eq 'character'")
    for task in tasks:
        df2.loc[int(task.RowKey)] = [task.PartitionKey, task.RowKey, 
                task.Character, task.URL, task.Selected]
    if request.method == "POST":
        df2.loc[df2['Character'] == request.form['chara'], "Selected"] = True
        df2.loc[df2['Character'] != request.form['chara'], "Selected"] = False
        table_service.update_entity(table_name2, 
            df2.loc[df2['Character'] == request.form['chara'], ].to_dict('records')[0])
        
        elements = df2.loc[df2['Character'] != request.form['chara'], ]
        for index, row in elements.iterrows():
            table_service.update_entity(table_name2, row.to_dict())
            
        return render_template('character.html', table=df2[['Character', 'Selected']].values.tolist())
    else:
        return render_template('character.html', table=df2[['Character', 'Selected']].values.tolist())
    
# if __name__ == "__main__":
    # app.run(debug=True)




  

    
