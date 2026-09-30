import sqlite3

DATABASE = "bus_reservation.db"


# -------------------------------
# DATABASE CONNECTION
# -------------------------------
def connect():
    return sqlite3.connect(DATABASE)


# -------------------------------
# CREATE TABLES
# -------------------------------
def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buses (
            bus_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_name TEXT NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            departure TEXT NOT NULL,
            total_seats INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            fare REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passengers (
            passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            passenger_id INTEGER,
            bus_id INTEGER,
            seat_number INTEGER,
            status TEXT DEFAULT 'Booked',
            FOREIGN KEY(passenger_id) REFERENCES passengers(passenger_id),
            FOREIGN KEY(bus_id) REFERENCES buses(bus_id)
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------
# ADD SAMPLE BUSES
# -------------------------------
def add_sample_buses():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM buses")
    count = cursor.fetchone()[0]

    if count == 0:
        buses = [
            ("Express Travels", "Hyderabad", "Bangalore",
             "08:00 AM", 40, 40, 650),

            ("City Express", "Hyderabad", "Chennai",
             "09:30 AM", 40, 40, 750),

            ("Super Luxury", "Bangalore", "Hyderabad",
             "10:00 PM", 45, 45, 700),

            ("Royal Travels", "Hyderabad", "Vijayawada",
             "06:30 AM", 35, 35, 450)
        ]

        cursor.executemany("""
            INSERT INTO buses
            (bus_name, source, destination, departure,
             total_seats, available_seats, fare)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, buses)

        conn.commit()

    conn.close()


# -------------------------------
# VIEW BUSES
# -------------------------------
def view_buses():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM buses")
    buses = cursor.fetchall()

    print("\n--- Available Buses ---")

    for bus in buses:
        print(
            f"ID: {bus[0]} | "
            f"{bus[1]} | "
            f"{bus[2]} -> {bus[3]} | "
            f"Departure: {bus[4]} | "
            f"Seats: {bus[6]}/{bus[5]} | "
            f"Fare: ₹{bus[7]}"
        )

    conn.close()


# -------------------------------
# SEARCH BUSES
# -------------------------------
def search_buses():
    source = input("Enter source: ")
    destination = input("Enter destination: ")

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM buses
        WHERE LOWER(source) = LOWER(?)
        AND LOWER(destination) = LOWER(?)
    """, (source, destination))

    buses = cursor.fetchall()

    print("\n--- Search Results ---")

    if not buses:
        print("No buses found.")
    else:
        for bus in buses:
            print(
                f"ID: {bus[0]} | "
                f"{bus[1]} | "
                f"{bus[2]} -> {bus[3]} | "
                f"Departure: {bus[4]} | "
                f"Available Seats: {bus[6]} | "
                f"Fare: ₹{bus[7]}"
            )

    conn.close()


# -------------------------------
# REGISTER PASSENGER
# -------------------------------
def register_passenger():
    name = input("Enter passenger name: ")
    age = int(input("Enter age: "))
    phone = input("Enter phone number: ")

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO passengers (name, age, phone)
        VALUES (?, ?, ?)
    """, (name, age, phone))

    conn.commit()

    print("Passenger registered successfully.")
    print("Passenger ID:", cursor.lastrowid)

    conn.close()


# -------------------------------
# BOOK TICKET
# -------------------------------
def book_ticket():

    view_buses()

    bus_id = int(input("\nEnter Bus ID: "))

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM buses WHERE bus_id = ?",
        (bus_id,)
    )

    bus = cursor.fetchone()

    if not bus:
        print("Invalid Bus ID.")
        conn.close()
        return

    if bus[6] <= 0:
        print("No seats available.")
        conn.close()
        return

    passenger_id = int(input("Enter Passenger ID: "))

    cursor.execute(
        "SELECT * FROM passengers WHERE passenger_id = ?",
        (passenger_id,)
    )

    passenger = cursor.fetchone()

    if not passenger:
        print("Invalid Passenger ID.")
        conn.close()
        return

    seat_number = bus[5] - bus[6] + 1

    cursor.execute("""
        INSERT INTO bookings
        (passenger_id, bus_id, seat_number)
        VALUES (?, ?, ?)
    """, (passenger_id, bus_id, seat_number))

    cursor.execute("""
        UPDATE buses
        SET available_seats = available_seats - 1
        WHERE bus_id = ?
    """, (bus_id,))

    conn.commit()

    print("\nTicket booked successfully!")
    print("Booking ID:", cursor.lastrowid)
    print("Seat Number:", seat_number)
    print("Fare: ₹", bus[7])

    conn.close()


# -------------------------------
# VIEW BOOKINGS
# -------------------------------
def view_bookings():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            bookings.booking_id,
            passengers.name,
            buses.bus_name,
            buses.source,
            buses.destination,
            bookings.seat_number,
            bookings.status,
            buses.fare
        FROM bookings
        JOIN passengers
        ON bookings.passenger_id = passengers.passenger_id
        JOIN buses
        ON bookings.bus_id = buses.bus_id
    """)

    bookings = cursor.fetchall()

    print("\n--- Bookings ---")

    if not bookings:
        print("No bookings found.")
    else:
        for booking in bookings:
            print(
                f"Booking ID: {booking[0]} | "
                f"Passenger: {booking[1]} | "
                f"Bus: {booking[2]} | "
                f"Route: {booking[3]} -> {booking[4]} | "
                f"Seat: {booking[5]} | "
                f"Status: {booking[6]} | "
                f"Fare: ₹{booking[7]}"
            )

    conn.close()


# -------------------------------
# SEARCH BOOKING
# -------------------------------
def search_booking():
    booking_id = int(input("Enter Booking ID: "))

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            bookings.booking_id,
            passengers.name,
            passengers.phone,
            buses.bus_name,
            buses.source,
            buses.destination,
            bookings.seat_number,
            bookings.status,
            buses.fare
        FROM bookings
        JOIN passengers
        ON bookings.passenger_id = passengers.passenger_id
        JOIN buses
        ON bookings.bus_id = buses.bus_id
        WHERE bookings.booking_id = ?
    """, (booking_id,))

    booking = cursor.fetchone()

    if booking:
        print("\n--- Booking Details ---")
        print("Booking ID:", booking[0])
        print("Passenger:", booking[1])
        print("Phone:", booking[2])
        print("Bus:", booking[3])
        print("Route:", booking[4], "->", booking[5])
        print("Seat Number:", booking[6])
        print("Status:", booking[7])
        print("Fare: ₹", booking[8])
    else:
        print("Booking not found.")

    conn.close()


# -------------------------------
# CANCEL TICKET
# -------------------------------
def cancel_ticket():
    booking_id = int(input("Enter Booking ID: "))

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bus_id, status
        FROM bookings
        WHERE booking_id = ?
    """, (booking_id,))

    booking = cursor.fetchone()

    if not booking:
        print("Booking not found.")
        conn.close()
        return

    if booking[1] == "Cancelled":
        print("Ticket is already cancelled.")
        conn.close()
        return

    cursor.execute("""
        UPDATE bookings
        SET status = 'Cancelled'
        WHERE booking_id = ?
    """, (booking_id,))

    cursor.execute("""
        UPDATE buses
        SET available_seats = available_seats + 1
        WHERE bus_id = ?
    """, (booking[0],))

    conn.commit()

    print("Ticket cancelled successfully.")

    conn.close()


# -------------------------------
# MAIN MENU
# -------------------------------
def main():

    create_tables()
    add_sample_buses()

    while True:

        print("\n================================")
        print("      BUS RESERVATION SYSTEM")
        print("================================")
        print("1. View Buses")
        print("2. Search Buses")
        print("3. Register Passenger")
        print("4. Book Ticket")
        print("5. View Bookings")
        print("6. Search Booking")
        print("7. Cancel Ticket")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            view_buses()

        elif choice == "2":
            search_buses()

        elif choice == "3":
            register_passenger()

        elif choice == "4":
            book_ticket()

        elif choice == "5":
            view_bookings()

        elif choice == "6":
            search_booking()

        elif choice == "7":
            cancel_ticket()

        elif choice == "8":
            print("Thank you for using Bus Reservation System!")
            break

        else:
            print("Invalid choice. Please try again.")


main()