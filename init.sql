-- Place your schema below this line.
-- Example: Paste your CREATE TABLE and INSERT INTO statements here.

CREATE TABLE Parking_Area (
    Parking_ID INT PRIMARY KEY,
    Parking_Name VARCHAR(255),
    Slot_No INT
);

CREATE TABLE Parking_Slots (
    Slot_ID INT PRIMARY KEY,
    Parking_ID INT,
    Arrival_time TIMESTAMP,
    Departure_time TIMESTAMP,
    Parked_Time INT,
    FOREIGN KEY (Parking_ID) REFERENCES Parking_Area(Parking_ID)
);

-- You may add your own data inserts below if desired.
-- INSERT INTO Parking_Area VALUES (...);