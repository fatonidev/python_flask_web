from flask_mysqldb import MySQL

class Rules:
    def __init__(self, id, left, right, support, confidence, lift):
        self.id = id
        self.left = left
        self.right = right
        self.support = support
        self.confidence = confidence
        self.lift = lift

    def __repr__(self):
        return '<Rules %r>' % self.id

    @classmethod
    def get_all(cls, conn):
        cursor = conn.connection.cursor()
        cursor.execute('''SELECT * FROM rules ORDER BY support DESC''')
        rules = cursor.fetchall()
        cursor.close()
        return rules

    @classmethod
    def get_by_id(cls, conn, id):
        cursor = conn.connection.cursor()
        cursor.execute('''SELECT * FROM rules WHERE id = %s''', (id,))
        rule = cursor.fetchone()
        cursor.close()
        return rule

    @classmethod
    def store(cls, conn, left, right, support, confidence, lift):
        cursor = conn.connection.cursor()
        cursor.execute('''INSERT INTO rules (left_data, right_data, support, confidence, lift) VALUES (%s, %s, %s, %s, %s)''', (left, right, support, confidence, lift))
        conn.connection.commit()
        cursor.close()

    @classmethod
    def delete(cls, conn, id):
        cursor = conn.connection.cursor()
        cursor.execute('''DELETE FROM rules WHERE id = %s''', (id,))
        conn.connection.commit()
        cursor.close()

    @classmethod
    def delete_all(cls, conn):
        cursor = conn.connection.cursor()
        cursor.execute('''DELETE FROM rules''')
        conn.connection.commit()
        cursor.close()