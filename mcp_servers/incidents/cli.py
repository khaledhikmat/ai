#!/usr/bin/env python3
"""
Sample Data Generator for Security Knowledge Base
Generates realistic fake data for testing the MCP server
"""

import sys
import argparse
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable
from neo4j import GraphDatabase
import os

class SecurityDataGenerator:
    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        
        # Sample data pools
        self.first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
            "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
            "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
            "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna",
            "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle",
            "Kenneth", "Laura", "Kevin", "Sarah", "Brian", "Kimberly", "George", "Deborah",
            "Edward", "Dorothy", "Ronald", "Amy", "Timothy", "Angela", "Jason", "Ashley"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
            "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
            "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
            "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
            "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
            "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker"
        ]
        
        self.departments = [
            "Security", "Administration", "Maintenance", "IT", "HR", "Finance", 
            "Operations", "Customer Service", "Legal", "Marketing", "Research", "Facilities"
        ]
        
        self.shifts = ["Day", "Evening", "Night", "Swing", "Weekend"]
        
        self.vehicle_makes = [
            "Ford", "Chevrolet", "Toyota", "Honda", "Nissan", "BMW", "Mercedes", "Audi",
            "Volkswagen", "Subaru", "Hyundai", "Kia", "Mazda", "Jeep", "Ram", "GMC"
        ]
        
        self.vehicle_models = {
            "Ford": ["Explorer", "F-150", "Escape", "Mustang", "Focus", "Fusion"],
            "Chevrolet": ["Silverado", "Equinox", "Malibu", "Tahoe", "Suburban", "Cruze"],
            "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Prius", "Tacoma"],
            "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Odyssey", "Ridgeline"],
            "Nissan": ["Altima", "Sentra", "Rogue", "Pathfinder", "Titan", "370Z"],
            "BMW": ["3 Series", "5 Series", "X3", "X5", "7 Series", "Z4"],
            "Mercedes": ["C-Class", "E-Class", "S-Class", "GLC", "GLE", "A-Class"],
            "Audi": ["A3", "A4", "A6", "Q3", "Q5", "Q7"],
            "Volkswagen": ["Jetta", "Passat", "Tiguan", "Atlas", "Golf", "Beetle"],
            "Subaru": ["Outback", "Forester", "Impreza", "Legacy", "Ascent", "WRX"],
            "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Accent", "Genesis"],
            "Kia": ["Optima", "Sorento", "Sportage", "Soul", "Forte", "Stinger"],
            "Mazda": ["Mazda3", "Mazda6", "CX-5", "CX-9", "MX-5", "CX-3"],
            "Jeep": ["Wrangler", "Grand Cherokee", "Cherokee", "Compass", "Renegade", "Gladiator"],
            "Ram": ["1500", "2500", "3500", "ProMaster", "ProMaster City"],
            "GMC": ["Sierra", "Terrain", "Acadia", "Yukon", "Canyon", "Savana"]
        }
        
        self.colors = [
            "White", "Black", "Silver", "Gray", "Red", "Blue", "Green", "Brown",
            "Yellow", "Orange", "Purple", "Gold", "Maroon", "Navy", "Tan"
        ]
        
        self.hair_colors = ["Black", "Brown", "Blonde", "Red", "Gray", "White", "Auburn"]
        self.eye_colors = ["Brown", "Blue", "Green", "Hazel", "Gray", "Amber"]
        self.skin_tones = ["Light", "Medium", "Dark", "Olive", "Fair"]
        self.genders = ["Male", "Female", "Non-binary"]
        
        self.incident_types = [
            "Unauthorized Access", "Theft", "Vandalism", "Suspicious Activity", 
            "Medical Emergency", "Fire Alarm", "Equipment Malfunction", "Visitor Complaint",
            "Employee Misconduct", "Safety Violation", "Security Breach", "Trespassing",
            "Vehicle Incident", "Property Damage", "Workplace Violence", "Drug/Alcohol",
            "Emergency Evacuation", "System Failure", "Lost/Found Property", "Noise Complaint"
        ]

    def close(self):
        if self.driver:
            self.driver.close()

    def clear_database(self):
        """Clear all existing data (use with caution!)"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared")

    def generate_license_plate(self) -> str:
        """Generate a random license plate"""
        formats = [
            f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))}{''.join(random.choices('0123456789', k=4))}",
            f"{''.join(random.choices('0123456789', k=3))}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))}",
            f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))}{''.join(random.choices('0123456789', k=5))}"
        ]
        return random.choice(formats)

    def generate_campuses(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate sample campus data"""
        campuses = []
        cities = [
            ("San Antonio", "TX"), ("Austin", "TX"), ("Houston", "TX"), ("Dallas", "TX"),
            ("Phoenix", "AZ"), ("Los Angeles", "CA"), ("Chicago", "IL"), ("Miami", "FL"),
            ("Atlanta", "GA"), ("Denver", "CO"), ("Seattle", "WA"), ("Portland", "OR")
        ]
        
        campus_types = ["Main Campus", "North Campus", "South Campus", "East Campus", "West Campus",
                       "Downtown Campus", "Research Campus", "Training Campus", "Distribution Center", "Headquarters"]
        
        streets = ["Main St", "Oak Ave", "Business Blvd", "Corporate Dr", "Industrial Way", 
                  "Commerce St", "Technology Pkwy", "Innovation Blvd", "Executive Dr", "Campus Way"]
        
        for i in range(count):
            city, state = random.choice(cities)
            street_num = random.randint(100, 9999)
            street = random.choice(streets)
            campus_name = f"{city} {random.choice(campus_types)}"
            
            campus = {
                "name": campus_name,
                "address": f"{street_num} {street}",
                "city": city,
                "state": state
            }
            campuses.append(campus)
        
        return campuses

    def generate_vehicles(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate sample vehicle data"""
        vehicles = []
        
        for i in range(count):
            make = random.choice(self.vehicle_makes)
            model = random.choice(self.vehicle_models[make])
            year = random.randint(2015, 2024)
            license = self.generate_license_plate()
            color = random.choice(self.colors)
            
            # Some vehicles are security/company vehicles
            is_security = random.random() < 0.3
            if is_security:
                name = f"Security Vehicle {i+1:03d}"
                decal = random.choice(["Security", "Company", "Official", "Emergency"])
            else:
                name = f"{make} {model}"
                decal = random.choice(["None", "Personal", "Visitor", "Employee", ""])
            
            vehicle = {
                "name": name,
                "make": make,
                "model": model,
                "year": year,
                "license": license,
                "color": color,
                "decal": decal
            }
            vehicles.append(vehicle)
        
        return vehicles

    def generate_employees(self, count: int = 50, campuses: List[Dict] = None) -> List[Dict[str, Any]]:
        """Generate sample employee data"""
        employees = []
        
        for i in range(count):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            name = f"{first_name} {last_name}"
            employee_id = f"EMP{i+1:04d}"
            emp_type = random.choice(["Regular", "Contractor"])
            department = random.choice(self.departments)
            shift = random.choice(self.shifts)
            
            campus = random.choice(campuses)["name"] if campuses else "Main Campus"
            
            # Some employees have managers (will be set later)
            manager = ""  # Will be populated after all employees are created
            
            employee = {
                "name": name,
                "employee_id": employee_id,
                "type": emp_type,
                "department": department,
                "campus": campus,
                "work_shift": shift,
                "manager": manager,
                "photo": f"photos/employees/{employee_id}.jpg",
                "vehicles": []  # Will be populated with relationships
            }
            employees.append(employee)
        
        return employees

    def generate_officers(self, count: int = 50, campuses: List[Dict] = None) -> List[Dict[str, Any]]:
        """Generate sample security officer data"""
        officers = []
        
        for i in range(count):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            name = f"Officer {first_name} {last_name}"
            employee_id = f"OFF{i+1:04d}"
            emp_type = random.choice(["Regular", "Contractor"])
            department = "Security"  # All officers are in Security
            shift = random.choice(self.shifts)
            
            campus = random.choice(campuses)["name"] if campuses else "Main Campus"
            
            officer = {
                "name": name,
                "employee_id": employee_id,
                "type": emp_type,
                "department": department,
                "campus": campus,
                "work_shift": shift,
                "manager": "",  # Will be populated after all officers are created
                "photo": f"photos/officers/{employee_id}.jpg",
                "vehicles": []
            }
            officers.append(officer)
        
        return officers

    def generate_visitors(self, count: int = 50, campuses: List[Dict] = None) -> List[Dict[str, Any]]:
        """Generate sample visitor data"""
        visitors = []
        
        for i in range(count):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            name = f"{first_name} {last_name}"
            age = random.randint(18, 75)
            hair_color = random.choice(self.hair_colors)
            eye_color = random.choice(self.eye_colors)
            skin = random.choice(self.skin_tones)
            gender = random.choice(self.genders)
            restricted = random.random() < 0.1  # 10% chance of being restricted
            
            # Visitors can access multiple campuses
            available_campuses = [c["name"] for c in campuses] if campuses else ["Main Campus"]
            visitor_campuses = random.sample(available_campuses, random.randint(1, min(3, len(available_campuses))))
            
            visitor = {
                "name": name,
                "age": age,
                "hair_color": hair_color,
                "eye_color": eye_color,
                "skin": skin,
                "gender": gender,
                "photo": f"photos/visitors/visitor_{i+1:04d}.jpg",
                "restricted": restricted,
                "vehicles": [],
                "campuses": visitor_campuses
            }
            visitors.append(visitor)
        
        return visitors

    def generate_incidents(self, count: int = 100, campuses: List[Dict] = None, 
                          officers: List[Dict] = None, employees: List[Dict] = None, 
                          visitors: List[Dict] = None, vehicles: List[Dict] = None) -> List[Dict[str, Any]]:
        """Generate sample incident data"""
        incidents = []
        
        for i in range(count):
            incident_number = f"INC{i+1:06d}"
            campus = random.choice(campuses)["name"] if campuses else "Main Campus"
            
            # Generate random start time within last 2 years
            start_date = datetime.now() - timedelta(days=random.randint(1, 730))
            start_datetime = start_date.isoformat()
            
            # End time is 30 minutes to 8 hours after start
            duration_minutes = random.randint(30, 480)
            end_date = start_date + timedelta(minutes=duration_minutes)
            end_datetime = end_date.isoformat()
            
            # Generate incident narration
            incident_type = random.choice(self.incident_types)
            locations = ["parking lot", "main entrance", "lobby", "cafeteria", "loading dock", 
                        "conference room", "warehouse", "office building", "security checkpoint", "stairwell"]
            location = random.choice(locations)
            
            narrations = [
                f"{incident_type} reported at {location}. Initial response initiated.",
                f"Security alert: {incident_type} in progress at {location}. Investigating officer dispatched.",
                f"Incident involving {incident_type} at {location}. Witness statements collected.",
                f"Response to {incident_type} at {location}. Situation resolved without further incident.",
                f"Security breach: {incident_type} detected at {location}. Proper protocols followed."
            ]
            narration = random.choice(narrations)
            
            # Assign random officer
            assigned_officer = random.choice(officers)["employee_id"] if officers else "OFF0001"
            
            # Random involvement
            involved_employees = []
            involved_visitors = []
            involved_vehicles = []
            
            # 70% chance of employee involvement
            if employees and random.random() < 0.7:
                num_employees = random.randint(1, 3)
                involved_employees = [emp["employee_id"] for emp in random.sample(employees, min(num_employees, len(employees)))]
            
            # 60% chance of visitor involvement  
            if visitors and random.random() < 0.6:
                num_visitors = random.randint(1, 2)
                involved_visitors = [vis["name"] for vis in random.sample(visitors, min(num_visitors, len(visitors)))]
            
            # 40% chance of vehicle involvement
            if vehicles and random.random() < 0.4:
                num_vehicles = random.randint(1, 2)
                involved_vehicles = [veh["license"] for veh in random.sample(vehicles, min(num_vehicles, len(vehicles)))]
            
            incident = {
                "number": incident_number,
                "campus": campus,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "narration": narration,
                "assigned_officer": assigned_officer,
                "involved_vehicles": involved_vehicles,
                "involved_employees": involved_employees,
                "involved_visitors": involved_visitors
            }
            incidents.append(incident)
        
        return incidents

    def create_all_data(self, clear_first: bool = False):
        """Generate and insert all sample data"""
        if clear_first:
            self.clear_database()
        
        print("Generating sample data...")
        
        # Generate all data
        campuses = self.generate_campuses(10)
        vehicles = self.generate_vehicles(50)
        employees = self.generate_employees(50, campuses)
        officers = self.generate_officers(50, campuses)
        visitors = self.generate_visitors(50, campuses)
        incidents = self.generate_incidents(100, campuses, officers, employees, visitors, vehicles)
        
        # Set up management relationships
        # Some employees manage others
        for i in range(10, len(employees)):  # Skip first 10 to be managers
            if random.random() < 0.7:  # 70% of employees have managers
                manager = random.choice(employees[:10])  # Pick from first 10 as managers
                employees[i]["manager"] = manager["employee_id"]
        
        # Some officers manage others
        for i in range(5, len(officers)):  # Skip first 5 to be senior officers
            if random.random() < 0.8:  # 80% of officers have managers
                manager = random.choice(officers[:5])  # Pick from first 5 as senior officers
                officers[i]["manager"] = manager["employee_id"]
        
        print("Inserting data into Neo4j...")
        
        # Insert campuses
        print(f"Creating {len(campuses)} campuses...")
        with self.driver.session() as session:
            for campus in campuses:
                session.run(
                    """
                    CREATE (c:Campus {
                        name: $name,
                        address: $address,
                        city: $city,
                        state: $state,
                        created_at: datetime()
                    })
                    """,
                    **campus
                )
        
        # Insert vehicles
        print(f"Creating {len(vehicles)} vehicles...")
        with self.driver.session() as session:
            for vehicle in vehicles:
                session.run(
                    """
                    CREATE (v:Vehicle {
                        name: $name,
                        make: $make,
                        model: $model,
                        year: $year,
                        license: $license,
                        color: $color,
                        decal: $decal,
                        created_at: datetime()
                    })
                    """,
                    **vehicle
                )
        
        # Insert employees
        print(f"Creating {len(employees)} employees...")
        with self.driver.session() as session:
            for employee in employees:
                session.run(
                    """
                    CREATE (e:Employee {
                        name: $name,
                        employee_id: $employee_id,
                        type: $type,
                        department: $department,
                        campus: $campus,
                        work_shift: $work_shift,
                        manager: $manager,
                        photo: $photo,
                        vehicles: $vehicles,
                        created_at: datetime()
                    })
                    """,
                    **employee
                )
        
        # Insert officers
        print(f"Creating {len(officers)} officers...")
        with self.driver.session() as session:
            for officer in officers:
                session.run(
                    """
                    CREATE (o:Officer {
                        name: $name,
                        employee_id: $employee_id,
                        type: $type,
                        department: $department,
                        campus: $campus,
                        work_shift: $work_shift,
                        manager: $manager,
                        photo: $photo,
                        vehicles: $vehicles,
                        created_at: datetime()
                    })
                    """,
                    **officer
                )
        
        # Insert visitors
        print(f"Creating {len(visitors)} visitors...")
        with self.driver.session() as session:
            for visitor in visitors:
                session.run(
                    """
                    CREATE (v:Visitor {
                        name: $name,
                        age: $age,
                        hair_color: $hair_color,
                        eye_color: $eye_color,
                        skin: $skin,
                        gender: $gender,
                        photo: $photo,
                        restricted: $restricted,
                        vehicles: $vehicles,
                        campuses: $campuses,
                        created_at: datetime()
                    })
                    """,
                    **visitor
                )
        
        # Insert incidents
        print(f"Creating {len(incidents)} incidents...")
        with self.driver.session() as session:
            for incident in incidents:
                session.run(
                    """
                    CREATE (i:Incident {
                        number: $number,
                        campus: $campus,
                        start_datetime: datetime($start_datetime),
                        end_datetime: datetime($end_datetime),
                        narration: $narration,
                        assigned_officer: $assigned_officer,
                        involved_vehicles: $involved_vehicles,
                        involved_employees: $involved_employees,
                        involved_visitors: $involved_visitors,
                        created_at: datetime()
                    })
                    """,
                    **incident
                )
        
        print("Creating relationships...")
        
        # Create WORKS_IN relationships (Employees and Officers to Campuses)
        with self.driver.session() as session:
            session.run("""
                MATCH (e:Employee), (c:Campus)
                WHERE e.campus = c.name
                CREATE (e)-[:WORKS_IN]->(c)
            """)
            
            session.run("""
                MATCH (o:Officer), (c:Campus)
                WHERE o.campus = c.name
                CREATE (o)-[:WORKS_IN]->(c)
            """)
        
        # Create MANAGES relationships
        with self.driver.session() as session:
            session.run("""
                MATCH (e1:Employee), (e2:Employee)
                WHERE e1.manager = e2.employee_id
                CREATE (e2)-[:MANAGES]->(e1)
            """)
            
            session.run("""
                MATCH (o1:Officer), (o2:Officer)
                WHERE o1.manager = o2.employee_id
                CREATE (o2)-[:MANAGES]->(o1)
            """)
        
        # Create random OWNS relationships (People to Vehicles)
        with self.driver.session() as session:
            # Employees own vehicles
            employees_with_vehicles = random.sample(employees, random.randint(20, 35))
            for emp in employees_with_vehicles:
                vehicle = random.choice(vehicles)
                session.run("""
                    MATCH (e:Employee {employee_id: $emp_id}), (v:Vehicle {license: $license})
                    CREATE (e)-[:OWNS]->(v)
                """, emp_id=emp["employee_id"], license=vehicle["license"])
            
            # Officers own vehicles
            officers_with_vehicles = random.sample(officers, random.randint(25, 40))
            for off in officers_with_vehicles:
                vehicle = random.choice(vehicles)
                session.run("""
                    MATCH (o:Officer {employee_id: $off_id}), (v:Vehicle {license: $license})
                    CREATE (o)-[:OWNS]->(v)
                """, off_id=off["employee_id"], license=vehicle["license"])
            
            # Visitors own vehicles
            visitors_with_vehicles = random.sample(visitors, random.randint(15, 30))
            for vis in visitors_with_vehicles:
                vehicle = random.choice(vehicles)
                session.run("""
                    MATCH (v:Visitor {name: $vis_name}), (veh:Vehicle {license: $license})
                    CREATE (v)-[:OWNS]->(veh)
                """, vis_name=vis["name"], license=vehicle["license"])
        
        # Create incident relationships
        with self.driver.session() as session:
            # ASSIGNS relationships (Incident to Officer)
            session.run("""
                MATCH (i:Incident), (o:Officer)
                WHERE i.assigned_officer = o.employee_id
                CREATE (i)-[:ASSIGNS]->(o)
            """)
            
            # HAPPENED_IN relationships (Incident to Campus)
            session.run("""
                MATCH (i:Incident), (c:Campus)
                WHERE i.campus = c.name
                CREATE (i)-[:HAPPENED_IN]->(c)
            """)
            
            # INVOLVES relationships for employees
            for incident in incidents:
                for emp_id in incident["involved_employees"]:
                    session.run("""
                        MATCH (i:Incident {number: $inc_num}), (e:Employee {employee_id: $emp_id})
                        CREATE (i)-[:INVOLVES]->(e)
                    """, inc_num=incident["number"], emp_id=emp_id)
                
                # INVOLVES relationships for visitors
                for vis_name in incident["involved_visitors"]:
                    session.run("""
                        MATCH (i:Incident {number: $inc_num}), (v:Visitor {name: $vis_name})
                        CREATE (i)-[:INVOLVES]->(v)
                    """, inc_num=incident["number"], vis_name=vis_name)
        
        print("\n✅ Sample data generation complete!")
        print("\n📊 Summary:")
        print(f"   • {len(campuses)} Campuses")
        print(f"   • {len(vehicles)} Vehicles")
        print(f"   • {len(employees)} Employees")
        print(f"   • {len(officers)} Security Officers")
        print(f"   • {len(visitors)} Visitors")
        print(f"   • {len(incidents)} Security Incidents")
        print(f"   • Relationships: WORKS_IN, MANAGES, OWNS, INVOLVES, ASSIGNS, HAPPENED_IN")


def ingest_incidents():
    """Main function to generate sample data"""
    
    # Database connection settings
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    
    print("🔐 Security Knowledge Base - Sample Data Generator")
    print("=" * 60)
    
    try:
        # Initialize generator
        generator = SecurityDataGenerator(neo4j_uri, neo4j_username, neo4j_password)
        
        # Ask user if they want to clear existing data
        clear_first = input("\n⚠️  Clear existing data first? (y/N): ").lower() == 'y'
        
        if clear_first:
            confirm = input("🚨 This will DELETE ALL existing data! Are you sure? (y/N): ").lower() == 'y'
            if not confirm:
                print("Operation cancelled.")
                return
        
        # Generate all sample data
        generator.create_all_data(clear_first=clear_first)
        
        # Close the generator
        generator.close()
        
        print("\n🎉 Ready to test your Security Knowledge Base MCP Server!")
        print("   Run your MCP server and try some queries:")
        print("   • Search for employees in Security department")
        print("   • Find incidents involving specific visitors")
        print("   • Look up vehicle ownership relationships")
        print("   • Analyze incident patterns by campus")
        
    except Exception as e:
        print(f"\n❌ Error generating sample data: {e}")
        print("Please check your Neo4j connection settings.")

# define a command processors mapping where each key is a command name
# and the value is an async function that performs the command. 
# the processor is a callable function that takes variant 
# input arguments, returns None and must be awaited. 
processors: Dict[str, Callable[..., None]] = {
    "ingest": ingest_incidents,
}

async def main(args=None):
    parser = argparse.ArgumentParser(description="CLI Processor to support INC MCP Server.")
    parser.add_argument("proc_name", help="processor command")
    args = parser.parse_args(args)

    if not args.proc_name:
        print("No proc name is provided. Please provide a processor i.e. ingest.")
        sys.exit(1)

    if args.proc_name not in processors:
        print(f"Unknown command: {args.proc_name}. Available commands: {', '.join(processors.keys())}")
        sys.exit(1)

    processors[args.proc_name]()
