-- Create users table with primary key
CREATE TABLE users (
  id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username varchar(50) NOT NULL UNIQUE,
  password varchar(100) NOT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),

) 

-- Create messages table with foreign key relationship
CREATE TABLE messages (
  id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id int NOT NULL,
  content text NOT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
   FOREIGN KEY (user_id) REFERENCES users (id)
) 