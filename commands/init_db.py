from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash

def init_db(app):    
    # Define connection cursor
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'flask-apriori-store'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    mysql = MySQL(app)

    with app.app_context():
        cursor = mysql.connection.cursor()

        # Create users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INT(11) NOT NULL AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(64) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY email (email)
        )''')

        # insert user                                    
        cursor.execute('''INSERT IGNORE INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)''',
             ('admin', 'admin@example.com', generate_password_hash('admin', method='pbkdf2:sha256'), 'admin'))

        # Create datasets table
        cursor.execute('''CREATE TABLE IF NOT EXISTS datasets (
            id INT(11) NOT NULL AUTO_INCREMENT,         
            code VARCHAR(255) NOT NULL,   
            date DATE NOT NULL,
            items TEXT NOT NULL,
            payment VARCHAR(255) NOT NULL,
            total VARCHAR(255) NOT NULL,
            total_items VARCHAR(255) NOT NULL,
            detail_data TEXT NOT NULL,
            created_by INT(11) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        )''')

        # Create rules table
        cursor.execute('''CREATE TABLE IF NOT EXISTS rules (
            id INT(11) NOT NULL AUTO_INCREMENT,
            left_data TEXT NOT NULL,
            right_data TEXT NOT NULL,
            support VARCHAR(255) NOT NULL,
            confidence VARCHAR(255) NOT NULL,
            lift VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        )''')
       
        # commit to DB
        mysql.connection.commit()

        # close connection
        cursor.close()

    return mysql

