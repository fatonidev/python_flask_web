from flask_mysqldb import MySQL

class User:
    def __init__(self, id, name, email, password, role):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return '<User %r>' % self.name

    @classmethod
    def get_all(cls, conn):
        cursor = conn.connection.cursor()
        cursor.execute('''SELECT * FROM users''')
        users = cursor.fetchall()
        cursor.close()
        return users

    @classmethod
    def get_by_id(cls, conn, id):
        cursor = conn.connection.cursor()
        cursor.execute('''SELECT * FROM users WHERE id = %s''', (id,))
        user = cursor.fetchone()
        cursor.close()
        return user

    @classmethod
    def update(cls, conn, id, name, email, role):
        cursor = conn.connection.cursor()
        cursor.execute('''UPDATE users SET name = %s, email = %s, role = %s WHERE id = %s''', (name, email, role, id))
        conn.connection.commit()
        cursor.close()

    @classmethod
    def store(cls, conn, name, email, password, role):
        cursor = conn.connection.cursor()
        cursor.execute('''INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)''', (name, email, password, role))
        conn.connection.commit()
        cursor.close()

    @classmethod
    def delete(cls, conn, id):
        cursor = conn.connection.cursor()
        cursor.execute('''DELETE FROM users WHERE id = %s''', (id,))
        conn.connection.commit()
        cursor.close()

    @classmethod
    def get_by_username(cls, conn, username):
        cursor = conn.connection.cursor()
        cursor.execute('''SELECT * FROM users WHERE name = %s''', (username,))
        user = cursor.fetchone()
        cursor.close()
        return user
