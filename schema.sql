CREATE TABLE projects(
	title VARCHAR(100),
	description VARCHAR(1000),
	start_date DATE,
	end_date DATE,
	target_fund INTEGER
);


/*  user role is the default
    admin role (EVENTUALLY) allows creation, deletion and modification of all entries
*/
CREATE TABLE users(
    user_id SERIAL PRIMARY KEY,
    user_email VARCHAR(100) UNIQUE,
    password VARCHAR(15) NOT NULL,
    role VARCHAR(10) NOT NULL
);

CREATE TABLE sessions(
    session_id CHAR(36) PRIMARY KEY,
	user_id INTEGER REFERENCES users(user_id)
);
