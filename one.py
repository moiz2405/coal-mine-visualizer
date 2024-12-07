import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import psycopg2

# Constants
TONNES_PER_MILLION_TONNES = 1e6
DEFAULT_FIGURE_SIZE = (12, 6)

def create_database_and_table(db_path):
    # Connect to the SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='coal_mines';")
    table_exists = cursor.fetchone()
    
    # If the table doesn't exist, create it
    if not table_exists:
        print("Creating coal_mines table...")
        cursor.execute("""
            CREATE TABLE coal_mines (
                mine_name TEXT,
                location TEXT,
                annual_production REAL,
                emission_factor REAL
            );
        """)
        conn.commit()
        
        # Insert data for Indian states and coal mines
        cursor.execute("""
            INSERT INTO coal_mines (mine_name, location, annual_production, emission_factor)
            VALUES 
                ('Dhanbad', 'Jharkhand', 3.5, 0.9),
                ('Bokaro', 'Jharkhand', 2.8, 0.85),
                ('Jharia', 'Jharkhand', 3.2, 0.92),
                ('Korba', 'Chhattisgarh', 4.0, 0.88),
                ('Gevra', 'Chhattisgarh', 5.5, 0.9),
                ('Dipka', 'Chhattisgarh', 3.8, 0.87),
                ('Singrauli', 'Madhya Pradesh', 4.5, 0.89),
                ('Sohagpur', 'Madhya Pradesh', 3.0, 0.86),
                ('Umaria', 'Madhya Pradesh', 3.2, 0.9),
                ('Raniganj', 'West Bengal', 2.7, 0.84),
                ('Asansol', 'West Bengal', 3.1, 0.88),
                ('Chandrapur', 'Maharashtra', 4.2, 0.9),
                ('Ballarpur', 'Maharashtra', 3.4, 0.88),
                ('Talcher', 'Odisha', 4.8, 0.9),
                ('Ib Valley', 'Odisha', 3.6, 0.87),
                ('Singareni', 'Telangana', 5.0, 0.91),
                ('Kothagudem', 'Telangana', 4.1, 0.89);
        """)
        conn.commit()
        print("Table created and sample data inserted.")
    else:
        print("coal_mines table already exists.")
    
    conn.close()

def fetch_coal_mine_data_sqlite(conn):
    query = """
    SELECT mine_name AS "Mine Name", location AS "Location",
           annual_production AS "Annual Production", emission_factor AS "Emission Factor"
    FROM coal_mines
    """
    df = pd.read_sql_query(query, conn)
    return df

def fetch_coal_mine_data_postgres(conn):
    query = """
    SELECT mine_name AS "Mine Name", location AS "Location",
           annual_production AS "Annual Production", emission_factor AS "Emission Factor"
    FROM coal_mines
    """
    df = pd.read_sql_query(query, conn)
    return df

class CoalMineFootprintCalculator:
    def __init__(self, sqlite_database_path=None, postgresql_connection_parameters=None):
        self.coal_mine_data = None
        self.sqlite_database_path = sqlite_database_path
        self.postgresql_connection_parameters = postgresql_connection_parameters

    def connect_to_db(self):
        try:
            if self.sqlite_database_path:
                return sqlite3.connect(self.sqlite_database_path)
            elif self.postgresql_connection_parameters:
                return psycopg2.connect(**self.postgresql_connection_parameters)
            else:
                raise ValueError("Database connection details not provided.")
        except (psycopg2.Error, sqlite3.Error) as e:
            print(f"Error connecting to the database: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise

    def load_data_from_db(self):
        if self.coal_mine_data is None:
            try:
                conn = self.connect_to_db()
                if self.sqlite_database_path:
                    self.coal_mine_data = fetch_coal_mine_data_sqlite(conn)
                elif self.postgresql_connection_parameters:
                    self.coal_mine_data = fetch_coal_mine_data_postgres(conn)
            finally:
                conn.close()

    def calculate_carbon_footprint(self):
        if self.coal_mine_data is None:
            raise ValueError("No data loaded. Please load data from the database first.")
        
        self.coal_mine_data["Carbon Footprint (tonnes CO2)"] = (
            self.coal_mine_data["Annual Production"] * self.coal_mine_data["Emission Factor"] * TONNES_PER_MILLION_TONNES
        )            

    def plot_carbon_footprint(self):
        if self.coal_mine_data is None or "Carbon Footprint (tonnes CO2)" not in self.coal_mine_data.columns:
            raise ValueError("Carbon footprint data is not available. Please calculate the carbon footprint first.")
        
        plt.figure(figsize=DEFAULT_FIGURE_SIZE)
        ax = self.coal_mine_data.plot(
            kind="bar", x="Mine Name", y="Carbon Footprint (tonnes CO2)", legend=False
        )
        ax.set_ylabel("Carbon Footprint (tonnes CO2)")
        ax.set_title("Carbon Footprint of Indian Coal Mines")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()    
        
if __name__ == "__main__":
    # Create the database and table (if not already present)
    sqlite_db_path = "coal_mines.db"
    create_database_and_table(sqlite_db_path)
    
    # Initialize the calculator with the SQLite database
    calculator = CoalMineFootprintCalculator(sqlite_database_path=sqlite_db_path)
    
    # Load the data, calculate the carbon footprint, and plot the results
    calculator.load_data_from_db()
    calculator.calculate_carbon_footprint()
    calculator.plot_carbon_footprint()        
           