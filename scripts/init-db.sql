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
    password NVARCHAR(255) NOT NULL
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

-- Create the media_files table
CREATE TABLE media_files (
    file_id INT IDENTITY(1,1) PRIMARY KEY,
    filename NVARCHAR(255) NOT NULL,
    listing_id INT NOT NULL,
    FOREIGN KEY (listing_id) REFERENCES listings (listing_id)
);
GO