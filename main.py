import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import datetime

# Constants
TONNES_PER_MILLION_TONNES = 1e6
DEFAULT_FIGURE_SIZE = (12, 6)

# Dictionary mapping states to their coal mines
INDIAN_STATES_MINES = {
    'Jharkhand': ['Jharia', 'Karanpura', 'Bokaro Colliery'],
    'Chhattisgarh': ['Gevra', 'Dipka', 'Kusmunda', 'Mand-Raigarh'],
    'Madhya Pradesh': ['Nigahi', 'Jayant', 'Dudhichua', 'Umaria'],
    'West Bengal': ['Raniganj Coalfield'],
    'Maharashtra': ['Ghugus', 'Wani', 'Ballarpur Colliery'],
    'Odisha': ['Talcher Coalfield', 'Ib Valley Coalfield', 'Jagannath'],
    'Telangana': ['Kothagudem Coalfield', 'Ramagundam']
}

def create_database_and_table(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='coal_mines';")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("Creating coal_mines table...")
        cursor.execute("""
            CREATE TABLE coal_mines (
                mine_name TEXT,
                location TEXT,
                annual_production REAL,
                emission_factor REAL,
                date DATE
            );
        """)
        conn.commit()
        
        # Insert sample data with dates
        cursor.execute("""
            INSERT INTO coal_mines (mine_name, location, annual_production, emission_factor, date)
            VALUES 
                ('Jharia', 'Jharkhand', 3.5, 0.9, '2024-01-01'),
                ('Karanpura', 'Jharkhand', 2.8, 0.85, '2024-01-01'),
                ('Bokaro Colliery', 'Jharkhand', 3.2, 0.92, '2024-01-01'),
                ('Gevra', 'Chhattisgarh', 5.5, 0.9, '2024-01-01'),
                ('Dipka', 'Chhattisgarh', 3.8, 0.87, '2024-01-01'),
                ('Kusmunda', 'Chhattisgarh', 4.0, 0.88, '2024-01-01'),
                ('Mand-Raigarh', 'Chhattisgarh', 2.9, 0.85, '2024-01-01'),
                ('Nigahi', 'Madhya Pradesh', 4.5, 0.89, '2024-01-01'),
                ('Jayant', 'Madhya Pradesh', 3.0, 0.86, '2024-01-01'),
                ('Dudhichua', 'Madhya Pradesh', 3.2, 0.9, '2024-01-01'),
                ('Umaria', 'Madhya Pradesh', 2.5, 0.83, '2024-01-01'),
                ('Raniganj Coalfield', 'West Bengal', 2.7, 0.84, '2024-01-01'),
                ('Ghugus', 'Maharashtra', 4.2, 0.9, '2024-01-01'),
                ('Wani', 'Maharashtra', 3.4, 0.88, '2024-01-01'),
                ('Ballarpur Colliery', 'Maharashtra', 2.9, 0.85, '2024-01-01'),
                ('Talcher Coalfield', 'Odisha', 4.8, 0.9, '2024-01-01'),
                ('Ib Valley Coalfield', 'Odisha', 3.6, 0.87, '2024-01-01'),
                ('Jagannath', 'Odisha', 4.0, 0.88, '2024-01-01'),
                ('Kothagudem Coalfield', 'Telangana', 4.1, 0.89, '2024-01-01'),
                ('Ramagundam', 'Telangana', 5.0, 0.91, '2024-01-01');
        """)
        conn.commit()
        print("Table created and sample data inserted.")
    else:
        print("coal_mines table already exists.")
    
    conn.close()

def fetch_coal_mine_data_sqlite(conn):
    query = """
    SELECT mine_name AS "Mine Name", location AS "Location",
           annual_production AS "Annual Production", emission_factor AS "Emission Factor", date AS "Date"
    FROM coal_mines
    """
    df = pd.read_sql_query(query, conn)
    return df

class CoalMineFootprintCalculator:
    def __init__(self, sqlite_database_path=None):
        self.coal_mine_data = None
        self.sqlite_database_path = sqlite_database_path

    def connect_to_db(self):
        try:
            if self.sqlite_database_path:
                return sqlite3.connect(self.sqlite_database_path)
            else:
                raise ValueError("Database connection details not provided.")
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")
            raise

    def load_data_from_db(self):
        if self.coal_mine_data is None:
            try:
                conn = self.connect_to_db()
                self.coal_mine_data = fetch_coal_mine_data_sqlite(conn)
                print("Data loaded from database successfully.")
            except Exception as e:
                print(f"An error occurred while loading data: {e}")
                raise
            finally:
                conn.close()

    def get_user_data(self):
        try:
            mine_name = input("Enter mine name: ")
            location = input("Enter location: ")
            annual_production = float(input("Enter annual production (in million tonnes): "))
            emission_factor = float(input("Enter emission factor (in tCO2e/tonne): "))
            date = input("Enter date (YYYY-MM-DD): ")
        
            user_data = pd.DataFrame({
                'Mine Name': [mine_name],
                'Location': [location],
                'Annual Production': [annual_production],
                'Emission Factor': [emission_factor],
                'Date': [date]
            })

            # Add a new column 'Mine No.' starting from 1
            user_data.index = range(1, len(user_data) + 1)
            user_data.index.name = 'Mine No.'

            return user_data
        except ValueError:
            print("Invalid input. Please enter numeric values for production and emission factor.")
            return pd.DataFrame()

    def calculate_footprint(self, production, emission_factor):
        return production * emission_factor * TONNES_PER_MILLION_TONNES
    def visualize_data(self):
     if self.user_data is not None and not self.user_data.empty:
        plt.figure(figsize=DEFAULT_FIGURE_SIZE)
        
        # Visualizing Annual Production, Emission Factor, and Carbon Footprint
        bar_width = 0.25
        index = range(len(self.user_data['Mine Name']))
        
        # Plot Annual Production
        plt.bar(
            [i - bar_width for i in index],
            self.user_data['Annual Production'],
            bar_width,
            label='Annual Production',
            color='b'
        )

        # Plot Emission Factor
        plt.bar(
            index,
            self.user_data['Emission Factor'],
            bar_width,
            label='Emission Factor',
            color='r'
        )

        # Plot Carbon Footprint
        plt.bar(
            [i + bar_width for i in index],
            self.user_data['Carbon Footprint (tCO2e)'] / 1e6,  # Convert to Million Tonnes
            bar_width,
            label='Carbon Footprint',
            color='g'
        )

        plt.title('Carbon Footprint of Selected Coal Mines')
        plt.xlabel('Mine Name')
        plt.ylabel('Values')
        plt.xticks(index, self.user_data['Mine Name'], rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.savefig('coal_mines_carbon_footprint.png')
        plt.show()
     else:
        print("Unable to visualize data due to missing information.")

    def visualize_total_data(self):
        if self.coal_mine_data is not None and not self.coal_mine_data.empty:
            self.coal_mine_data['Carbon Footprint (tCO2e)'] = self.coal_mine_data.apply(
                lambda row: self.calculate_footprint(row['Annual Production'], row['Emission Factor']),
                axis=1
            )
            plt.figure(figsize=DEFAULT_FIGURE_SIZE)
            plt.bar(self.coal_mine_data['Mine Name'], self.coal_mine_data['Carbon Footprint (tCO2e)'] / 1e6)
            plt.title('Carbon Footprint of All Coal Mines')
            plt.xlabel('Mine Name')
            plt.ylabel('Carbon Footprint (Million Tonnes CO2e)')
            plt.xticks(rotation=90)
            plt.tight_layout()
            plt.show()
        else:
            print("No data available for visualization.")

    def visualize_specific_mines(self):
    
      if self.coal_mine_data is not None and not self.coal_mine_data.empty:
        try:
            # Display the list of states
            states = list(INDIAN_STATES_MINES.keys())
            print("Available States:")
            for i, state in enumerate(states, 1):
                print(f"{i}. {state}")

            # Prompt user to select a state by number
            state_choice = int(input("Select a state by number: ")) - 1

            if 0 <= state_choice < len(states):
                selected_state = states[state_choice]
                mines = INDIAN_STATES_MINES[selected_state]

                # Display the list of mines in the selected state
                print(f"\nAvailable Mines in {selected_state}:")
                for i, mine in enumerate(mines, 1):
                    print(f"{i}. {mine}")

                # Prompt user to select a mine by number
                mine_choice = int(input("Select a mine by number: ")) - 1

                if 0 <= mine_choice < len(mines):
                    selected_mine = mines[mine_choice]
                    
                    # Filter data for the selected mine
                    filtered_data = self.coal_mine_data[
                        (self.coal_mine_data['Location'] == selected_state) &
                        (self.coal_mine_data['Mine Name'] == selected_mine)
                    ].copy()

                    if not filtered_data.empty:
                        # Calculate the carbon footprint
                        filtered_data['Carbon Footprint (tCO2e)'] = filtered_data.apply(
                            lambda row: self.calculate_footprint(row['Annual Production'], row['Emission Factor']),
                            axis=1
                        )

                        # Visualization
                        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)

                        # Bar width and positions
                        bar_width = 0.25
                        index = range(len(filtered_data['Mine Name']))

                        # Plot Annual Production
                        bars1 = ax.bar(
                            [i - bar_width for i in index],
                            filtered_data['Annual Production'],
                            bar_width,
                            label='Annual Production',
                            color='b'
                        )

                        # Plot Emission Factor
                        bars2 = ax.bar(
                            index,
                            filtered_data['Emission Factor'],
                            bar_width,
                            label='Emission Factor',
                            color='r'
                        )

                        # Plot Carbon Footprint
                        bars3 = ax.bar(
                            [i + bar_width for i in index],
                            filtered_data['Carbon Footprint (tCO2e)'] / 1e6,  # Convert to Million Tonnes
                            bar_width,
                            label='Carbon Footprint',
                            color='g'
                        )

                        # Labels and legend
                        ax.set_xlabel('Mine Name')
                        ax.set_ylabel('Values')
                        ax.set_title(f'Attributes for {selected_mine} in {selected_state}')
                        ax.set_xticks(index)
                        ax.set_xticklabels(filtered_data['Mine Name'], rotation=45, ha='right')
                        ax.legend()

                        plt.tight_layout()
                        plt.savefig('visualization.png')  # Save the figure as a PNG file
                        plt.show()
                    else:
                        print("No data available for the selected mine.")
                else:
                    print("Invalid mine selection. Please choose a valid number.")
            else:
                print("Invalid state selection. Please choose a valid number.")
        except Exception as e:
            print(f"An error occurred while visualizing specific mines: {e}")
      else:
        print("No data available for visualization.")


    def visualize_trend_analysis(self):
        if self.coal_mine_data is not None and not self.coal_mine_data.empty:
            try:
                self.coal_mine_data['Date'] = pd.to_datetime(self.coal_mine_data['Date'])
                trend_data = self.coal_mine_data.groupby('Date').apply(
                    lambda x: self.calculate_footprint(x['Annual Production'].sum(), x['Emission Factor'].mean())
                )
                plt.figure(figsize=DEFAULT_FIGURE_SIZE)
                plt.plot(trend_data.index, trend_data.values / 1e6, marker='o')
                plt.title('Carbon Footprint Trend Over Time')
                plt.xlabel('Date')
                plt.ylabel('Carbon Footprint (Million Tonnes CO2e)')
                plt.grid(True)
                plt.tight_layout()
                plt.show()
            except Exception as e:
                print(f"An error occurred while analyzing trends: {e}")
        else:
            print("No data available for visualization.")

    def compare_mines(self):

     if self.coal_mine_data is not None and not self.coal_mine_data.empty:
        try:
            mine_names = self.coal_mine_data['Mine Name'].unique()
            print("Available mines for comparison:")
            for i, mine in enumerate(mine_names, 1):
                print(f"{i}. {mine}")
            
            # Get user input for mine selection
            choice1 = int(input("Select first mine by number: ")) - 1
            choice2 = int(input("Select second mine by number: ")) - 1

            if 0 <= choice1 < len(mine_names) and 0 <= choice2 < len(mine_names):
                mine1 = mine_names[choice1]
                mine2 = mine_names[choice2]

                # Filter data for selected mines
                data1 = self.coal_mine_data[self.coal_mine_data['Mine Name'] == mine1]
                data2 = self.coal_mine_data[self.coal_mine_data['Mine Name'] == mine2]

                if not data1.empty and not data2.empty:
                    # Calculate carbon footprints
                    footprint1 = self.calculate_footprint(data1['Annual Production'].sum(), data1['Emission Factor'].mean())
                    footprint2 = self.calculate_footprint(data2['Annual Production'].sum(), data2['Emission Factor'].mean())

                    # Prepare data for visualization
                    attributes = ['Annual Production', 'Emission Factor', 'Carbon Footprint']
                    mine1_values = [
                        data1['Annual Production'].sum(),
                        data1['Emission Factor'].mean(),
                        footprint1 / 1e6  # Convert to Million Tonnes
                    ]
                    mine2_values = [
                        data2['Annual Production'].sum(),
                        data2['Emission Factor'].mean(),
                        footprint2 / 1e6  # Convert to Million Tonnes
                    ]

                    x = range(len(attributes))

                    # Plot comparison
                    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
                    
                    bar_width = 0.35
                    opacity = 0.8

                    bars1 = ax.bar(
                        [p - bar_width/2 for p in x],
                        mine1_values,
                        bar_width,
                        alpha=opacity,
                        color='b',
                        label=mine1
                    )

                    bars2 = ax.bar(
                        [p + bar_width/2 for p in x],
                        mine2_values,
                        bar_width,
                        alpha=opacity,
                        color='r',
                        label=mine2
                    )
                    ax.set_xlabel('Attributes')
                    ax.set_ylabel('Values')
                    ax.set_title('Comparison of Mine Attributes')
                    ax.set_xticks(x)
                    ax.set_xticklabels(attributes)
                    ax.legend()

                    plt.tight_layout()
                    plt.savefig('comparison_mines.png')  # Save the figure as a PNG file
                    plt.show()
                else:
                    print("Data not available for selected mines.")
            else:
                print("Invalid selection. Please choose valid numbers.")
        except Exception as e:
            print(f"An error occurred while comparing mines: {e}")
     else:
        print("No data available for comparison.")
    def simulate_reduction_strategy(self):
     if self.coal_mine_data is not None and not self.coal_mine_data.empty:
        try:
            # Ask user to choose between reducing a specific mine or all mines
            reduction_choice = input("Choose reduction for:\n1. A Specific Mine\n2. All Mines\nEnter your choice (1/2): ")

            if reduction_choice == '1':
                # Reduction for a specific mine
                states = list(INDIAN_STATES_MINES.keys())
                print("Available States:")
                for i, state in enumerate(states, 1):
                    print(f"{i}. {state}")

                state_choice = int(input("Select a state by number: ")) - 1
                if 0 <= state_choice < len(states):
                    selected_state = states[state_choice]
                    mines = INDIAN_STATES_MINES[selected_state]
                    print(f"\nAvailable Mines in {selected_state}:")
                    for i, mine in enumerate(mines, 1):
                        print(f"{i}. {mine}")

                    mine_choice = int(input("Select a mine by number: ")) - 1
                    if 0 <= mine_choice < len(mines):
                        selected_mine = mines[mine_choice]

                        reduction_percentage = float(input("Enter the reduction percentage (0-100): "))
                        if 0 <= reduction_percentage <= 100:
                            # Create a copy to avoid modifying the original DataFrame
                            reduced_data = self.coal_mine_data.copy()

                            # Recalculate the original carbon footprint
                            self.coal_mine_data['Carbon Footprint (tCO2e)'] = self.coal_mine_data.apply(
                                lambda row: self.calculate_footprint(row['Annual Production'], row['Emission Factor']),
                                axis=1
                            )

                            # Apply reduction percentage to 'Annual Production' for the selected mine and recalculate the carbon footprint
                            reduced_data.loc[
                                (reduced_data['Location'] == selected_state) & 
                                (reduced_data['Mine Name'] == selected_mine),
                                'Annual Production'
                            ] *= (1 - reduction_percentage / 100)
                            reduced_data['Reduced Carbon Footprint (tCO2e)'] = reduced_data.apply(
                                lambda row: self.calculate_footprint(row['Annual Production'], row['Emission Factor']),
                                axis=1
                            )

                            # Plot visualization for the specific mine
                            filtered_data = reduced_data[
                                (reduced_data['Location'] == selected_state) & 
                                (reduced_data['Mine Name'] == selected_mine)
                            ]
                            
                            if not filtered_data.empty:
                                fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
                                index = range(len(filtered_data['Mine Name']))
                                bar_width = 0.35

                                # Plot Original Carbon Footprint
                                ax.bar(index, self.coal_mine_data[
                                    (self.coal_mine_data['Location'] == selected_state) & 
                                    (self.coal_mine_data['Mine Name'] == selected_mine)
                                ]['Carbon Footprint (tCO2e)'] / 1e6, bar_width, color='red', label='Previous Carbon Footprint')

                                # Plot Reduced Carbon Footprint
                                ax.bar([i + bar_width for i in index], filtered_data['Reduced Carbon Footprint (tCO2e)'] / 1e6, bar_width, color='blue', label='Reduced Carbon Footprint')

                                ax.set_xlabel('Mine Name')
                                ax.set_ylabel('Carbon Footprint (Million Tonnes CO2e)')
                                ax.set_title(f'Carbon Footprint Comparison for {selected_mine} After {reduction_percentage}% Reduction')
                                ax.set_xticks([i + bar_width / 2 for i in index])
                                ax.set_xticklabels(filtered_data['Mine Name'], rotation=90)
                                ax.legend()

                                plt.tight_layout()
                                plt.savefig('reduction_strategy_specific_mine.png')  # Save the figure as a PNG file
                                plt.show()
                            else:
                                print("No data available for the selected mine.")
                        else:
                            print("Invalid reduction percentage. Please enter a value between 0 and 100.")
                    else:
                        print("Invalid mine selection. Please choose a valid number.")
                else:
                    print("Invalid state selection. Please choose a valid number.")
                
            elif reduction_choice == '2':
                # Reduction for all mines
                reduction_percentage = float(input("Enter the reduction percentage (0-100): "))
                if 0 <= reduction_percentage <= 100:
                    reduced_data = self.coal_mine_data.copy()

                    # Recalculate the original carbon footprint
                    self.coal_mine_data['Carbon Footprint (tCO2e)'] = self.coal_mine_data.apply(
                        lambda row: self.calculate_footprint(row['Annual Production'], row['Emission Factor']),
                        axis=1
                    )

                    # Apply reduction percentage to 'Annual Production' for all mines and recalculate the carbon footprint
                    reduced_data['Annual Production'] *= (1 - reduction_percentage / 100)
                    reduced_data['Reduced Carbon Footprint (tCO2e)'] = reduced_data.apply(
                        lambda row: self.calculate_footprint(row['Annual Production'], row['Emission Factor']),
                        axis=1
                    )

                    # Plot visualization for all mines
                    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
                    index = range(len(reduced_data['Mine Name']))
                    bar_width = 0.35

                    # Plot Original Carbon Footprint
                    ax.bar(index, self.coal_mine_data['Carbon Footprint (tCO2e)'] / 1e6, bar_width, color='red', label='Previous Carbon Footprint')

                    # Plot Reduced Carbon Footprint
                    ax.bar([i + bar_width for i in index], reduced_data['Reduced Carbon Footprint (tCO2e)'] / 1e6, bar_width, color='blue', label='Reduced Carbon Footprint')

                    ax.set_xlabel('Mine Name')
                    ax.set_ylabel('Carbon Footprint (Million Tonnes CO2e)')
                    ax.set_title(f'Carbon Footprint Comparison After {reduction_percentage}% Reduction for All Mines')
                    ax.set_xticks([i + bar_width / 2 for i in index])
                    ax.set_xticklabels(reduced_data['Mine Name'], rotation=90)
                    ax.legend()

                    plt.tight_layout()
                    plt.savefig('reduction_strategy_all_mines.png')  # Save the figure as a PNG file
                    plt.show()
                else:
                    print("Invalid reduction percentage. Please enter a value between 0 and 100.")
            else:
                print("Invalid choice. Please select 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a numeric value for reduction percentage.")
        except Exception as e:
            print(f"An error occurred while simulating reduction strategy: {e}")
     else:
        print("No data available for simulation.")
    def process_all_mines_by_state(self):
     if self.coal_mine_data is not None and not self.coal_mine_data.empty:
        try:
            # Display the list of states
            states = list(INDIAN_STATES_MINES.keys())
            print("Available States:")
            for i, state in enumerate(states, 1):
                print(f"{i}. {state}")

            # Prompt user to select a state by number
            while True:
                try:
                    state_choice = int(input("Select a state by number: ")) - 1
                    if 0 <= state_choice < len(states):
                        selected_state = states[state_choice]
                        break
                    else:
                        print(f"Invalid choice. Please select a number between 1 and {len(states)}.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

            mines = INDIAN_STATES_MINES[selected_state]

            # Filter data for the selected state
            filtered_data = self.coal_mine_data[self.coal_mine_data['Location'] == selected_state].copy()

            if not filtered_data.empty:
                # Ensure necessary columns are numeric
                filtered_data['Annual Production'] = pd.to_numeric(filtered_data['Annual Production'], errors='coerce').fillna(0)
                filtered_data['Emission Factor'] = pd.to_numeric(filtered_data['Emission Factor'], errors='coerce').fillna(0)

                # Calculate the carbon footprint for each mine
                filtered_data['Carbon Footprint (tCO2e)'] = filtered_data.apply(
                    lambda row: self.calculate_footprint(row['Annual Production'], row['Emission Factor']),
                    axis=1
                )

                # Print column names and first few rows for debugging
                print("Columns in filtered data:", filtered_data.columns)
                print("First few rows of filtered data:\n", filtered_data.head())

                # Visualization
                plt.figure(figsize=DEFAULT_FIGURE_SIZE)
                plt.bar(filtered_data['Mine Name'], filtered_data['Carbon Footprint (tCO2e)'] / 1e6, color='b')
                plt.title(f'Carbon Footprint of Mines in {selected_state}')
                plt.xlabel('Mine Name')
                plt.ylabel('Carbon Footprint (Million Tonnes CO2e)')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.savefig('mines_by_state_visualization.png')  # Save the figure as a PNG file
                plt.show()
            else:
                print("No data available for the selected state.")
        except Exception as e:
            print(f"An error occurred while processing mines by state: {e}")
     else:
        print("No data available to process.")
    def run(self):
     while True:
        print("\nCarbon Footprint Calculator Menu:")
        print("1. Calculate carbon footprint")
        print("2. Visualize Total Data")
        print("3. Visualize Specific Mines")
        print("4. Trend Analysis")
        print("5. Compare Two Mines")
        print("6. Simulate Reduction Strategy")
        print("7. Process Mines by State")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            user_data = self.get_user_data()
            user_data['Carbon Footprint (tCO2e)'] = user_data.apply(
                lambda row: self.calculate_footprint(row['Annual Production'], row['Emission Factor']),
                axis=1
            )
            self.user_data = user_data  # Store the user_data in an instance variable
            self.visualize_data()  # Call visualize_data without arguments
        elif choice == '2':
            self.visualize_total_data()
        elif choice == '3':
            self.visualize_specific_mines()
        elif choice == '4':
            self.visualize_trend_analysis()
        elif choice == '5':
            self.compare_mines()
        elif choice == '6':
            self.simulate_reduction_strategy()
        elif choice == '7':
            self.process_all_mines_by_state()
        elif choice == '8':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select a valid option.")

    
    def get_valid_integer_input(prompt, min_value, max_value):
     while True:
        try:
            value = int(input(prompt))
            if min_value <= value <= max_value:
                return value
            else:
                print(f"Please enter a number between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    def get_valid_float_input(prompt, min_value, max_value):
     while True:
        try:
            value = float(input(prompt))
            if min_value <= value <= max_value:
                return value
            else:
                print(f"Please enter a number between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    def plot_bar_chart(x, data1, data2, labels, title, xlabel, ylabel, filename):
     fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
     bar_width = 0.35
     opacity = 0.8
     bars1 = ax.bar(
         [p - bar_width / 2 for p in x],
         data1,
         bar_width,
         alpha=opacity,
         color='b',
         label=labels[0]
     )
     bars2 = ax.bar(
         [p + bar_width / 2 for p in x],
         data2,
         bar_width,
         alpha=opacity,
         color='r',
         label=labels[1]
     )
     ax.set_xlabel(xlabel)
     ax.set_ylabel(ylabel)
     ax.set_title(title)
     ax.set_xticks(x)
     ax.set_xticklabels(labels)
     ax.legend()
    
     plt.tight_layout()
     plt.savefig(filename)
     plt.show()

    def plot_comparison(self, mine1_data, mine2_data, attributes, filename):

      mine1_values = [mine1_data[attr].sum() if attr == 'Annual Production' else mine1_data[attr].mean() for attr in attributes]
      mine2_values = [mine2_data[attr].sum() if attr == 'Annual Production' else mine2_data[attr].mean() for attr in attributes]
      x = range(len(attributes))
      fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
      bar_width = 0.35
      opacity = 0.8

      bars1 = ax.bar([p - bar_width/2 for p in x], mine1_values, bar_width, alpha=opacity, color='b', label=mine1_data['Mine Name'].values[0])
      bars2 = ax.bar([p + bar_width/2 for p in x], mine2_values, bar_width, alpha=opacity, color='r', label=mine2_data['Mine Name'].values[0])

      ax.set_xlabel('Attributes')
      ax.set_ylabel('Values')
      ax.set_title('Comparison of Mine Attributes')
      ax.set_xticks(x)
      ax.set_xticklabels(attributes)
      ax.legend()

      plt.tight_layout()
      plt.savefig(filename)  # Save the figure as a PNG file
    plt.show()
    
# Main execution
if __name__ == "__main__":
    db_path = "coal_mines.db"
    create_database_and_table(db_path)
    calculator = CoalMineFootprintCalculator(sqlite_database_path=db_path)
    calculator.load_data_from_db()
    calculator.run()
