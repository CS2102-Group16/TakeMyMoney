CREATE TABLE projects(
    pid SERIAL PRIMARY KEY,
	title VARCHAR(100),
	description VARCHAR(1000),
	start_date DATE,
	end_date DATE,
	target_fund INTEGER, 
	photo_url VARCHAR(1000)
);

CREATE TABLE categories(
    name VARCHAR(100) NOT NULL PRIMARY KEY
);

CREATE TABLE projects_categories(
    category_name VARCHAR(100) NOT NULL,
    pid INTEGER NOT NULL,
    FOREIGN KEY (pid) REFERENCES projects(pid),
    FOREIGN KEY (category_name) REFERENCES categories(name)
);

/*  user role is the default
    admin role (EVENTUALLY) allows creation, deletion and modification of all entries
*/
CREATE TABLE users(
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    user_email VARCHAR(100) UNIQUE,
    password VARCHAR(15) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'user'
);

CREATE TABLE sessions(
    session_id CHAR(36) PRIMARY KEY,
	user_id INTEGER REFERENCES users(user_id)
);
