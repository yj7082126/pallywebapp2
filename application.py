from azure.storage import CloudStorageAccount
from flask import Flask, request, render_template, session, redirect
import pandas as pd
app = Flask(__name__)

account_name = 'pallystorageacc'
account_key = 'BsM29pcnisLfDE2fe2PpOr3eU6cp6Bm4yKqHRvADhXZUZbNmYGlTo8HHwBmL6lGnnOolNa93n5Gsm/+6KAAy5w=='
table_name = 'TodoItem'

@app.route("/", methods=("GET", "POST"))
def hello():
    account = CloudStorageAccount(account_name, account_key)

    table_service = account.create_table_service()
    
    df = pd.DataFrame(columns=['Text', 'Updated', 'Completed'])
    tasks = table_service.query_entities(table_name, filter="PartitionKey eq 'tasks'")
    for task in tasks:
        df.loc[int(task.RowKey)] = [task.Text, task.Updated.strftime("%Y/%m/%d %H:%M:%S"), task.Completed]
	
    return render_template('index.html', tables=[df.to_html(classes='data', header="true")])
    
if __name__ == "__main__":
    app.run()
   
    


  

    
