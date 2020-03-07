from flask import jsonify
from flask_table import Table, Col
from flask_restful import Resource, reqparse
from dotenv import load_dotenv
import os
import pyodbc
import struct

def handle_datetimeoffset(dto_value):
    tup = struct.unpack("<6hI2h", dto_value)
    tweaked = [tup[i] // 100 if i == 6 else tup[i] for i in range(len(tup))]
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:07d} {:+03d}:{:02d}".format(*tweaked)

project_folder = os.path.expanduser('~/pallywebapp2')
load_dotenv(os.path.join(project_folder, '.env'))

cnxn = pyodbc.connect(
    'DSN=sqlserverdatasource;database=PallyDB;Uid='
    + os.getenv("PALLYUSERNAME")
    + ';Pwd='
    + os.getenv("PALLYPASSWORD")
    + ';Encrypt=yes;Connection Timeout=30;')
cnxn.add_output_converter(-155, handle_datetimeoffset)
cursor = cnxn.cursor()

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

class Settings(Resource):
    def get(self):
        cursor.execute("SELECT * FROM [dbo].[Settings]")
        result = dict()
        rows = cursor.fetchall()
        for row in rows:
            result.update({row.name: row.value})
        return jsonify(result)

class Character1(Resource):
    def get(self):
        cursor.execute("SELECT name, displayName, character FROM [dbo].[Character1] WHERE selected = 1")
        result = dict()
        row = cursor.fetchone()
        if not row:
            return jsonify({"Message": "Weird Error"})

        result.update({"name": row.name, "displayName": row.displayName,
                       "character": row.character})
        return jsonify(result)

class Character2(Resource):
    def get(self):
        cursor.execute("SELECT name, displayName, character, action FROM [dbo].[Character2] WHERE selected = 1")
        result = dict()
        row = cursor.fetchone()
        if not row:
            return jsonify({"Message": "Weird Error"})

        result.update({"name": row.name, "displayName": row.displayName,
                       "character": row.character, "action": row.action})
        return jsonify(result)

class SpatialAnchor(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('anchor_id', type=str)
        super(SpatialAnchor, self).__init__()

    def get(self):
        cursor.execute("""
            SELECT name FROM
            (SELECT name, num FROM [dbo].[SpatialAnchor]) a
            JOIN
            (SELECT max(num) AS num FROM [dbo].[SpatialAnchor]) b
            ON a.num = b.num
        """)
        result = dict()
        row = cursor.fetchone()
        if not row:
            return jsonify({"Message": "Weird Error"})

        result.update({"anchor": row.name})
        return jsonify(result)

    def post(self):
        cursor.execute("SELECT max(num) AS num FROM [dbo].[SpatialAnchor]")
        row = cursor.fetchone()
        if not row:
            return jsonify({"Message": "Weird Error"})
        num = int(row.num) + 1

        args = self.parser.parse_args()
        anchor_id = args['anchor_id']

        sql = "INSERT INTO [dbo].[SpatialAnchor]([name], [num]) VALUES ('%s', %d)" % (anchor_id, num)
        cursor.execute(sql)
        cnxn.commit()

        return {'Anchor added successfully!': 200, num: anchor_id}

class Position(Resource):
    def get(self):
        cursor.execute("SELECT posx, posy, posz FROM [dbo].[Position]")
        result = dict()
        row = cursor.fetchone()
        if not row:
            return jsonify({"Message": "Weird Error"})

        result.update({"posx": row.posx, "posy": row.posy, "posz": row.posz})
        return jsonify(result)

class Position2(Resource):
    def get(self):
        cursor.execute("SELECT posx, posy, posz, rot FROM [dbo].[Position2]")
        result = dict()
        row = cursor.fetchone()
        if not row:
            return jsonify({"Message": "Weird Error"})

        result.update({"posx": row.posx, "posy": row.posy,
                       "posz": row.posz, "rot": row.rot})
        return jsonify(result)