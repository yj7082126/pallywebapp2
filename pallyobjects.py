from flask import jsonify
from flask_table import Table, Col
from flask_restful import Resource, reqparse

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
    def __init__(self, **kwargs):
        self.cursor = kwargs['cursor']

    def get(self):
        self.cursor.execute("""SELECT * FROM [dbo].[Settings]""")
        rows = self.cursor.fetchall()
        result = {row.name: row.value for row in rows}
        return jsonify(result)

class Character1(Resource):
    def __init__(self, **kwargs):
        self.cursor = kwargs['cursor']

    def get(self):
        self.cursor.execute("""
            SELECT name, displayName, character
            FROM [dbo].[Character1] WHERE selected = 1
        """)
        row = self.cursor.fetchone()
        if not row:
            result = {"Message": "Weird Error"}
        else:
            result = {"name": row.name, "displayName": row.displayName,
                       "character": row.character}
        return jsonify(result)

class Character2(Resource):
    def __init__(self, **kwargs):
        self.cursor = kwargs['cursor']

    def get(self):
        self.cursor.execute("""
            SELECT name, displayName, character, action
            FROM [dbo].[Character2] WHERE selected = 1
        """)
        row = self.cursor.fetchone()
        if not row:
            result = {"Message": "Weird Error"}
        else:
            result = {"name": row.name, "displayName": row.displayName,
                       "character": row.character, "action": row.action}
        return jsonify(result)

class Position(Resource):
    def __init__(self, **kwargs):
        self.cursor = kwargs['cursor']

    def get(self):
        self.cursor.execute("SELECT posx, posy, posz FROM [dbo].[Position]")
        row = self.cursor.fetchone()
        if not row:
            result = {"Message": "Weird Error"}
        else:
            result = {"posx": row.posx, "posy": row.posy, "posz": row.posz}
        return jsonify(result)

class Position2(Resource):
    def __init__(self, **kwargs):
        self.cursor = kwargs['cursor']

    def get(self):
        self.cursor.execute("SELECT posx, posy, posz, rot FROM [dbo].[Position2]")
        row = self.cursor.fetchone()
        if not row:
            result = {"Message": "Weird Error"}
        else:
            result = {"posx": row.posx, "posy": row.posy,
                       "posz": row.posz, "rot": row.rot}
        return jsonify(result)

class SpatialAnchor(Resource):
    def __init__(self, **kwargs):
        self.cursor = kwargs['cursor']
        self.cnxn = kwargs['cnxn']

        self.parser = reqparse.RequestParser()
        self.parser.add_argument('anchor_id', type=str)

        super(SpatialAnchor, self).__init__()

    def get(self):
        self.cursor.execute("""
            SELECT name FROM
            (SELECT name, num FROM [dbo].[SpatialAnchor]) a
            JOIN
            (SELECT max(num) AS num FROM [dbo].[SpatialAnchor]) b
            ON a.num = b.num
        """)
        row = self.cursor.fetchone()
        if not row:
            result = {"Message": "Weird Error"}
        else:
            result = {"anchor": row.name}
        return jsonify(result)

    def post(self):
        self.cursor.execute("SELECT max(num) AS num FROM [dbo].[SpatialAnchor]")
        row = self.cursor.fetchone()
        if not row:
            return jsonify({"Message": "Weird Error"})
        num = int(row.num) + 1

        args = self.parser.parse_args()
        anchor_id = args['anchor_id']

        self.cursor.execute("""
            INSERT INTO [dbo].[SpatialAnchor]([name], [num])
            VALUES ('%s', %d)
        """ % (anchor_id, num))
        self.cnxn.commit()

        return {'Anchor added successfully!': 200, num: anchor_id}
