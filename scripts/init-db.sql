USE master;
GO

-- Check if the database exists and drop it if it does (for reusability)
IF EXISTS (SELECT name FROM sys.databases WHERE name = 'BuySell_Connect')
BEGIN
    ALTER DATABASE BuySell_Connect SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE BuySell_Connect;
END
GO

-- Create the BuySell_Connect database
CREATE DATABASE BuySell_Connect;
GO

USE BuySell_Connect;
GO

-- Create the users table
CREATE TABLE users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(255) NOT NULL,
    email NVARCHAR(255) NOT NULL,
    password NVARCHAR(255) NOT NULL,
    profile_picture NVARCHAR(255),
    bio NVARCHAR(1000)
);
GO

-- Create the listings table
CREATE TABLE listings (
    listing_id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(255) NOT NULL,
    description varchar(max),
    price DECIMAL(10, 2) NOT NULL,
    seller_id INT NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES users (user_id)
);
GO

-- Create the media_files table (for storing file metadata)
CREATE TABLE media_files (
    file_id INT IDENTITY(1,1) PRIMARY KEY,
    filename NVARCHAR(255) NOT NULL,
    blob_url NVARCHAR(500) NOT NULL,
    listing_id INT,
    user_id INT,  -- Change profile_id to user_id
    file_type NVARCHAR(50) NOT NULL,
    upload_date DATETIME NOT NULL,
    -- Add other file metadata columns as needed
    FOREIGN KEY (listing_id) REFERENCES listings (listing_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)  -- Change the foreign key reference
);
GO

-- Create the file_associations table (for associating files with listings and profiles)
CREATE TABLE file_associations (
    association_id INT IDENTITY(1,1) PRIMARY KEY,
    file_id INT NOT NULL,
    listing_id INT,
    user_id INT,  -- Change profile_id to user_id
    -- Add other columns as needed to specify associations
    FOREIGN KEY (file_id) REFERENCES media_files (file_id),
    FOREIGN KEY (listing_id) REFERENCES listings (listing_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)  -- Change the foreign key reference
);
GO