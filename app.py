from flask import Flask, request, render_template, redirect, url_for
from flask_restful import Api
from dotenv import load_dotenv

import pallyobjects as po
import pandas as pd
import pyodbc
import struct
import os

#%%
def handle_datetimeoffset(dto_value):
    tup = struct.unpack("<6hI2h", dto_value)
    tweaked = [tup[i] // 100 if i == 6 else tup[i] for i in range(len(tup))]
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:07d} {:+03d}:{:02d}".format(*tweaked)

project_folder = os.path.expanduser('~/pallywebapp2')
load_dotenv(os.path.join(project_folder, '.env'))

#%%
cnxn = pyodbc.connect(
    'DSN=sqlserverdatasource;database=PallyDB;Uid='
    + os.getenv("PALLYUSERNAME")
    + ';Pwd='
    + os.getenv("PALLYPASSWORD")
    + ';Encrypt=yes;Connection Timeout=30;')
cnxn.add_output_converter(-155, handle_datetimeoffset)
cursor = cnxn.cursor()

#%%
app = Flask(__name__)

api = Api(app)
api.add_resource(po.Settings, '/sql/settings',
    resource_class_kwargs={ 'cursor': cursor })
api.add_resource(po.Character1, '/sql/character1',
    resource_class_kwargs={ 'cursor': cursor })
api.add_resource(po.Character2, '/sql/character2',
    resource_class_kwargs={ 'cursor': cursor })
api.add_resource(po.Position, '/sql/position',
    resource_class_kwargs={ 'cursor': cursor })
api.add_resource(po.Position2, '/sql/position2',
    resource_class_kwargs={ 'cursor': cursor })
api.add_resource(po.SpatialAnchor, '/sql/anchor',
    resource_class_kwargs={ 'cursor': cursor, 'cnxn': cnxn })

#%%
@app.route("/", methods=["GET", "POST"])
def hello_main():
    error = None
    if request.method == 'POST':
        if request.form['password'] != 'qwertyuiop':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('hello_index'))
    return render_template('login.html', error=error)

#%%
@app.route("/register", methods=["GET", "POST"])
def hello_reg():
    error = None
    if request.method == 'POST':
        return redirect(url_for('hello_index'))
    return render_template('register.html', error=error)

#%%
@app.route("/index", methods=["GET", "POST"])
def hello_index():
    return render_template('index.html')

#%%
@app.route("/results", methods=["GET", "POST"])
def hello_results():
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
        table = po.TaskTable(df2.to_dict(orient='records'), table_id="dataTable",
                          classes=["table", "table-bordered"])

    return render_template('tables.html', table = table.__html__())

#%%
@app.route("/video", methods=["GET", "POST"])
def hello_video():
    if request.method == 'POST':
        print(request.form['ip'])
        return render_template('video.html',
          source='<source src="https://'  + request.form['ip'] + '/api/holographic/stream/live_high.mp4?holo=true&pv=true&mic=false&loopback=true" type="video/mp4">')
    return render_template('video.html',
          source='<source src="http://10.200.4.46/api/holographic/stream/live_high.mp4?holo=true&pv=true&mic=false&loopback=true" type="video/mp4">''')

#%%
@app.route("/quest", methods=["GET", "POST"])
def hello_quest():
    cursor.execute("SELECT * FROM [dbo].[Character1]")
    row = cursor.fetchall()
    df = pd.DataFrame([list(t) for t in row], columns=["Id", "createAt", "updatedAt",
                                    "version", "deleted", "name",
                                    "selected", "character", "displayName"])
    df2 = df[['name', 'selected', 'displayName']]

    cursor.execute("SELECT * FROM [dbo].[Character2]")
    row = cursor.fetchall()
    df3 = pd.DataFrame([list(t) for t in row], columns=["Id", "createAt", "updatedAt",
                                    "version", "deleted", "name",
                                    "selected", "character", "displayName", "action"])
    df4 = df3[['name', 'selected', 'action']]

    cursor.execute("SELECT * FROM [dbo].[SoundEffect]")
    row = cursor.fetchall()
    df5 = pd.DataFrame([list(t) for t in row], columns=["Id", "createAt", "updatedAt",
                                    "version", "deleted", "name", "selected"])
    df6 = df5[['name', 'selected']]

    if request.method == "POST":
        print(request.form['chara'])
        df2.loc[df2['name'] == request.form['chara'], "selected"] = True
        df2.loc[df2['name'] != request.form['chara'], "selected"] = False
        cursor.execute("""UPDATE [dbo].[Character1] SET selected = 1
                       WHERE name = '""" + request.form['chara'] + "'")
        elements = df2.loc[df2['name'] != request.form['chara'], ]
        for index, row in elements.iterrows():
            cursor.execute("""UPDATE [dbo].[Character1] SET selected = 0
                       WHERE name = '""" + row['name'] + "'")

        print(request.form['chara2'])
        df4.loc[df4['name'] == request.form['chara2'], "selected"] = True
        df4.loc[df4['name'] != request.form['chara2'], "selected"] = False
        cursor.execute("""UPDATE [dbo].[Character2] SET selected = 1
                       WHERE name = '""" + request.form['chara2'] + "'")
        elements = df4.loc[df4['name'] != request.form['chara2'], ]
        for index, row in elements.iterrows():
            cursor.execute("""UPDATE [dbo].[Character2] SET selected = 0
                       WHERE name = '""" + row['name'] + "'")

        print(request.form['chara3'])
        df6.loc[df6['name'] == request.form['chara3'], "selected"] = True
        df6.loc[df6['name'] != request.form['chara3'], "selected"] = False
        cursor.execute("""UPDATE [dbo].[SoundEffect] SET selected = 1
                       WHERE name = '""" + request.form['chara3'] + "'")
        elements = df6.loc[df6['name'] != request.form['chara3'], ]
        for index, row in elements.iterrows():
            cursor.execute("""UPDATE [dbo].[SoundEffect] SET selected = 0
                       WHERE name = '""" + row['name'] + "'")
        cnxn.commit()

        return render_template('character.html', table=df2.values.tolist(),
                                                 table2=df4.values.tolist(),
                                                 table3=df6.values.tolist())
    else:
        return render_template('character.html', table=df2.values.tolist(),
                                                 table2=df4.values.tolist(),
                                                 table3=df6.values.tolist())

#%%
@app.route("/setting", methods=["GET", "POST"])
def hello_setting():
    cursor.execute("SELECT * FROM [dbo].[Settings]")
    row = cursor.fetchall()
    df = pd.DataFrame([list(t) for t in row], columns=["Id", "createAt", "updatedAt",
                                    "version", "deleted", "name", "value"])
    df2 = df[['name', 'value']]

    cursor.execute("SELECT * FROM [dbo].[Position]")
    row = cursor.fetchall()
    df3 = pd.DataFrame([list(t) for t in row], columns=["Id", "createAt", "updatedAt",
                                    "version", "deleted", "posX", "posY", "posZ"])
    df4 = pd.DataFrame(columns=['Name', 'Value'])
    df4.loc[0] = ['posX', df3.loc[0, 'posX']]
    df4.loc[1] = ['posY', df3.loc[0, 'posY']]
    df4.loc[2] = ['posZ', df3.loc[0, 'posZ']]

    cursor.execute("SELECT * FROM [dbo].[Position2]")
    row = cursor.fetchall()
    df5 = pd.DataFrame([list(t) for t in row], columns=["Id", "createAt", "updatedAt",
                                    "version", "deleted", "posX", "posY", "posZ", "rot"])
    df6 = pd.DataFrame(columns=['Name', 'Value'])
    df6.loc[0] = ['posX', df5.loc[0, 'posX']]
    df6.loc[1] = ['posY', df5.loc[0, 'posY']]
    df6.loc[2] = ['posZ', df5.loc[0, 'posZ']]
    df6.loc[3] = ['rot', df5.loc[0, 'rot']]

    if request.method == "POST":
        newList = request.form.getlist('chara')
        newVal = request.form.getlist('chara2')
        newVal2 = request.form.getlist('chara3')

        df2.loc[df2['name'].isin(newList), "value"] = True
        df2.loc[~df2['name'].isin(newList), "value"] = False

        for index, row in df2.iterrows():
            if (row["value"]):
                cursor.execute("""UPDATE [dbo].[Settings] SET value = 1
                       WHERE name = '""" + row['name'] + "'")
            else:
                cursor.execute("""UPDATE [dbo].[Settings] SET value = 0
                       WHERE name = '""" + row['name'] + "'")

        df4.loc[0, 'Value'] = newVal[0]
        df4.loc[1, 'Value'] = newVal[1]
        df4.loc[2, 'Value'] = newVal[2]
        for index, row in df4.iterrows():
            cursor.execute("UPDATE [dbo].[Position] SET " + row['Name'] + " = " + row["Value"])

        df6.loc[0, 'Value'] = newVal2[0]
        df6.loc[1, 'Value'] = newVal2[1]
        df6.loc[2, 'Value'] = newVal2[2]
        df6.loc[3, 'Value'] = newVal2[3]
        for index, row in df6.iterrows():
            cursor.execute("UPDATE [dbo].[Position2] SET " + row['Name'] + " = " + row["Value"])

        cnxn.commit()

        return render_template('settings.html', table=df2.values.tolist(),
                                                table2=df4.values.tolist(),
                                                table3=df6.values.tolist())
    else:
        return render_template('settings.html', table=df2.values.tolist(),
                                                table2=df4.values.tolist(),
                                                table3=df6.values.tolist())

#%%
if __name__ == "__main__":
    app.run(debug=True)







