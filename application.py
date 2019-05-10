from azure.storage import CloudStorageAccount
from flask import Flask, request, render_template, session, redirect
from flask_table import Table, Col, ButtonCol
import pandas as pd
app = Flask(__name__)

account_name = 'pallystorageacc'
account_key = 'BsM29pcnisLfDE2fe2PpOr3eU6cp6Bm4yKqHRvADhXZUZbNmYGlTo8HHwBmL6lGnnOolNa93n5Gsm/+6KAAy5w=='
table_name = 'TodoItem'
table_name2 = "Character"

class TaskTable(Table):
    text = Col('Text')
    update = Col('Updated')
    complete = Col('Completed')
    
class Task(object):
    def __init__(self, text, update, complete):
        self.text = text
        self.update = update
        self.complete = complete
        
@app.route("/", methods=["GET", "POST"])
def hello():
    if request.method == 'POST':
        print(dict(request.form).keys[0])
    else:
        df = []
        tasks = table_service.query_entities(table_name, filter="PartitionKey eq 'tasks'")
        for task in tasks:
            df.append(Task(task.Text, task.Updated.strftime("%Y/%m/%d %H:%M:%S"), task.Completed))
        table = TaskTable(df)
        table.border = True
        
    return render_template('index.html', table = table.__html__())
   
@app.route("/video", methods=["GET", "POST"])
def hello2():
    return render_template('video.html')

@app.route("/character", methods=["GET", "POST"])
def hello3():
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
    
if __name__ == "__main__":
    account = CloudStorageAccount(account_name, account_key)
    table_service = account.create_table_service()
    
    app.run(debug=True)
   
    




  

    
