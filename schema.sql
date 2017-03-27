/*  Two types of user: 'user' or 'admin.'
    Admin role (EVENTUALLY) allows creation, deletion and modification of all entries
*/
CREATE TABLE users(
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    user_email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(15) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'user',
    CONSTRAINT role CHECK (role = 'user' OR role = 'admin')
);

CREATE TABLE projects(
    pid SERIAL PRIMARY KEY,
	title VARCHAR(100) NOT NULL,
	description VARCHAR(1000) NOT NULL,
	start_date DATE NOT NULL,
	end_date DATE NOT NULL,
	target_fund INTEGER NOT NULL,
	photo_url VARCHAR(1000),
	user_id INTEGER REFERENCES users(user_id) NOT NULL,
	CONSTRAINT end_date CHECK (end_date > start_date)
);

CREATE TABLE categories(
    name VARCHAR(100) PRIMARY KEY
);

CREATE TABLE projects_categories(
    category_name VARCHAR(100) NOT NULL,
    pid INTEGER NOT NULL,
    PRIMARY KEY (category_name, pid),
    FOREIGN KEY (pid) REFERENCES projects(pid),
    FOREIGN KEY (category_name) REFERENCES categories(name)
);

CREATE TABLE sessions(
    session_id CHAR(36) PRIMARY KEY,
	user_id INTEGER REFERENCES users(user_id) NOT NULL
);

CREATE TABLE funding(
    user_id INTEGER REFERENCES users(user_id),
    pid INTEGER REFERENCES projects(pid),
    amount INTEGER,
    PRIMARY KEY (user_id, pid)
);
