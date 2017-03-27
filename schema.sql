/*  Two types of user: 'user' or 'admin.'
    Admin role (EVENTUALLY) allows creation, deletion and modification of all entries
*/
CREATE TABLE users(
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    user_email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(15) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'user'
);

CREATE TABLE projects(
    pid SERIAL PRIMARY KEY,
	title VARCHAR(100) NOT NULL,
	description VARCHAR(1000) NOT NULL,
	start_date DATE NOT NULL,
	end_date DATE NOT NULL,
	target_fund INTEGER NOT NULL,
	photo_url VARCHAR(1000),
	user_id INTEGER REFERENCES users(user_id) NOT NULL
);

CREATE TABLE categories(
    name VARCHAR(100) PRIMARY KEY
);

CREATE TABLE projects_categories(
    category_name VARCHAR(100) NOT NULL,
    pid INTEGER NOT NULL,
    PRIMARY KEY (category_name, pid),
    FOREIGN KEY (pid) REFERENCES projects(pid) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (category_name) REFERENCES categories(name) ON UPDATE CASCADE ON DELETE CASCADE
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

/* Logging */

CREATE TABLE projects_log(
    pid INTEGER NOT NULL,
    operation VARCHAR(10) NOT NULL,
    prev_title VARCHAR(100),
    prev_description VARCHAR(1000),
    prev_start_date DATE,
    prev_end_date DATE,
    prev_target_fund INTEGER,
    prev_photo_url VARCHAR(1000),
    next_title VARCHAR(100),
    next_description VARCHAR(1000),
    next_start_date DATE,
    next_end_date DATE,
    next_target_fund INTEGER,
    next_photo_url VARCHAR(1000),
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT old_title CHECK (operation = 'INSERT' OR prev_title IS NOT NULL),
    CONSTRAINT old_description CHECK (operation = 'INSERT' OR prev_description IS NOT NULL),
    CONSTRAINT old_start_date CHECK (operation = 'INSERT' OR prev_start_date IS NOT NULL),
    CONSTRAINT old_end_date CHECK (operation = 'INSERT' OR prev_end_date IS NOT NULL),
    CONSTRAINT old_target_fund CHECK (operation = 'INSERT' OR prev_target_fund IS NOT NULL),
    CONSTRAINT new_title CHECK (operation = 'DELETE' OR next_title IS NOT NULL),
    CONSTRAINT new_description CHECK (operation = 'DELETE' OR next_description IS NOT NULL),
    CONSTRAINT new_start_date CHECK (operation = 'DELETE' OR next_start_date IS NOT NULL),
    CONSTRAINT new_end_date CHECK (operation = 'DELETE' OR next_end_date IS NOT NULL),
    CONSTRAINT new_target_fund CHECK (operation = 'DELETE' OR next_target_fund IS NOT NULL),
    CONSTRAINT pk_projects_log PRIMARY KEY (pid, transaction_date)
);

CREATE TABLE users_log(
    user_id INTEGER PRIMARY KEY,
    prev_role VARCHAR(10) NOT NULL,
    next_role VARCHAR(10) NOT NULL,
    transaction_date DATE NOT NULL
);

CREATE OR REPLACE FUNCTION projectslog() RETURNS TRIGGER AS $$
    DECLARE pid INTEGER;
    DECLARE next_title VARCHAR(100);
    DECLARE next_description VARCHAR(1000);
    DECLARE next_start_date DATE;
    DECLARE next_end_date DATE;
    DECLARE next_target_fund INTEGER;
    DECLARE next_photo_url VARCHAR(1000);
    DECLARE prev_title VARCHAR(100);
    DECLARE prev_description VARCHAR(1000);
    DECLARE prev_start_date DATE;
    DECLARE prev_end_date DATE;
    DECLARE prev_target_fund INTEGER;
    DECLARE prev_photo_url VARCHAR(1000);

    BEGIN

    IF TG_OP = 'UPDATE' OR TG_OP = 'DELETE'
    THEN
        prev_title := OLD.title;
        prev_description := OLD.description;
        prev_start_date := OLD.start_date;
        prev_end_date := OLD.end_date;
        prev_target_fund := OLD.target_fund;
        prev_photo_url := OLD.photo_url;
        pid := OLD.pid;
    ELSE
        prev_title := NULL;
        prev_description := NULL;
        prev_start_date := NULL;
        prev_end_date := NULL;
        prev_target_fund := NULL;
        prev_photo_url := NULL;
    END IF;

    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE'
    THEN
        next_title := NEW.title;
        next_description := NEW.description;
        next_start_date := NEW.start_date;
        next_end_date := NEW.end_date;
        next_target_fund := NEW.target_fund;
        next_photo_url := NEW.photo_url;
        pid := NEW.pid;
    ELSE
        next_title := NULL;
        next_description := NULL;
        next_start_date := NULL;
        next_end_date := NULL;
        next_target_fund := NULL;
        next_photo_url := NULL;
    END IF;

    IF pid IS NULL
    THEN RAISE EXCEPTION 'pid cannot be null';
    END IF;

    INSERT INTO projects_log(
        pid, operation,
        prev_title, prev_description, prev_start_date, prev_end_date, prev_target_fund, prev_photo_url,
        next_title, next_description, next_start_date, next_end_date, next_target_fund, next_photo_url,
        transaction_date
    ) VALUES (
        pid, TG_OP,
        prev_title, prev_description, prev_start_date, prev_end_date, prev_target_fund, prev_photo_url,
        next_title, next_description, next_start_date, next_end_date, next_target_fund, next_photo_url,
        (SELECT CURRENT_TIMESTAMP)
    );
    RETURN NULL;

    END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER projectslog
AFTER INSERT OR UPDATE OR DELETE
ON projects
FOR EACH ROW
EXECUTE PROCEDURE projectslog();
