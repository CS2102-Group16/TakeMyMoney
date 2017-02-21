CREATE TABLE projects(
	title VARCHAR(100),
	description VARCHAR(1000),
	start_date DATE,
	end_date DATE,
	target_fund INTEGER
);

CREATE TABLE categories(
    name VARCHAR(100) NOT NULL PRIMARY KEY
);

CREATE TABLE projects_categories(
    project_id SERIAL NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(),
    FOREIGN KEY (category_name) REFERENCES categories(name),
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

