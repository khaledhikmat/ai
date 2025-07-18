import sys
import os
import argparse
import json
import neo4j

from typing import Dict, Callable, Awaitable, List
from dotenv import load_dotenv
from dataclasses import dataclass, field

from helpers.visualizers import visualize_graph

from service.config.typex import IConfigService
from service.config.envvars import EnvVarsConfigService
from service.graph.typex import IGraphService
from service.graph.neo4j import Neo4jGraphService

load_dotenv()

# define `ingest` as a command processor to ingest inheritance data.
async def ingest(data_source: str) -> None:
    # Initialize services
    cfg_svc = EnvVarsConfigService()
    graph_svc = Neo4jGraphService(cfg_svc)

    try:
        await graph_svc.clear_graph()

        await _ingest_persons(cfg_svc, graph_svc)
        await _ingest_properties(cfg_svc, graph_svc)
    except Exception as e:
        print(f"Ingest error occurred: {e}")
    finally:
        # Finalize services
        cfg_svc.finalize()
        await graph_svc.finalize()

# define `_ingest_persons` as a command processor to ingest persons inheritance data.
async def _ingest_persons(_: IConfigService, graph_svc: IGraphService) -> None:
    @dataclass
    class Person:
        name: str
        residence_country: str
        residence_city: str
        profession: str
        gender: str
        education: str
        birth_city: str
        birth_country: str
        birth_day: str
        birth_month: str
        birth_year: str
        death_city: str
        death_country: str
        death_day: str
        death_month: str
        death_year: str
        photo: str
        birth_certificate: str
        death_certificate: str
        inheritance_confinement: str
        children: List[str] = field(default_factory=list)
        spouses: List[str] = field(default_factory=list)

    try:
        children: dict[str, list[str]] = {}
        spouses: dict[str, list[str]] = {}
        
        countries = set()
        cities = set()

        residence_cities: dict[str, str] = {}
        residence_countries: dict[str, str] = {}
        birth_cities: dict[str, str] = {}
        birth_countries: dict[str, str] = {}
        death_cities: dict[str, str] = {}
        death_countries: dict[str, str] = {}

        countrycities = dict[str, set[str]]()

        base_dir = os.path.dirname(os.path.abspath(__file__))

        persons_file_path = os.path.join(base_dir, "data", "persons.json")

        # load persons
        with open(persons_file_path, "r") as f:
            persons = json.load(f)

            # create person nodes
            for person_data in persons:
                person = Person(**person_data)

                # Add children
                children[person.name] = person.children

                # Add spouses
                spouses[person.name] = person.spouses

                # Add cities and countries
                if person.residence_country and person.residence_country != "n/a":
                    countries.add(person.residence_country)
                    residence_countries[person.name] = person.residence_country

                if person.birth_country and person.birth_country != "n/a":
                    countries.add(person.birth_country)
                    birth_countries[person.name] = person.birth_country

                if person.death_country and person.death_country != "n/a":
                    countries.add(person.death_country)
                    death_countries[person.name] = person.death_country

                if person.residence_city and person.residence_city != "n/a":
                    cities.add(person.residence_city)
                    residence_cities[person.name] = person.residence_city
                    countrycities.setdefault(person.residence_country, set()).add(person.residence_city)

                if person.birth_city and person.birth_city != "n/a":
                    cities.add(person.birth_city)
                    birth_cities[person.name] = person.birth_city
                    countrycities.setdefault(person.birth_country, set()).add(person.birth_city)

                if person.death_city and person.death_city != "n/a":
                    cities.add(person.death_city)
                    death_cities[person.name] = person.death_city
                    countrycities.setdefault(person.death_country, set()).add(person.death_city)

                # Create person node
                query = """
                    MERGE (p:Person {name: $name})
                        ON CREATE SET
                            p.residence_country = $residence_country,
                            p.residence_city = $residence_city,
                            p.profession = $profession,
                            p.gender = $gender,
                            p.education = $education,
                            p.birth_city = $birth_city,
                            p.birth_country = $birth_country,
                            p.birth_day = $birth_day,
                            p.birth_month = $birth_month,
                            p.birth_year = $birth_year,
                            p.death_city = $death_city,
                            p.death_country = $death_country,
                            p.death_day = $death_day,
                            p.death_month = $death_month,
                            p.death_year = $death_year,
                            p.photo = $photo,
                            p.birth_certificate = $birth_certificate,
                            p.death_certificate = $death_certificate,
                            p.inheritance_confinement = $inheritance_confinement
                        ON MATCH SET
                            p.residence_country = $residence_country,
                            p.residence_city = $residence_city,
                            p.profession = $profession,
                            p.gender = $gender,
                            p.education = $education,
                            p.birth_city = $birth_city,
                            p.birth_country = $birth_country,
                            p.birth_day = $birth_day,       
                            p.birth_month = $birth_month,
                            p.birth_year = $birth_year,
                            p.death_city = $death_city,
                            p.death_country = $death_country,
                            p.death_day = $death_day,
                            p.death_month = $death_month,
                            p.death_year = $death_year,
                            p.photo = $photo,
                            p.birth_certificate = $birth_certificate,
                            p.death_certificate = $death_certificate,
                            p.inheritance_confinement = $inheritance_confinement
                    RETURN p
                """

                params = {
                    "name": person.name,
                    "residence_country": person.residence_country,
                    "residence_city": person.residence_city,
                    "profession": person.profession,
                    "gender": person.gender,
                    "education": person.education,
                    "birth_city": person.birth_city,
                    "birth_country": person.birth_country,
                    "birth_day": person.birth_day,
                    "birth_month": person.birth_month,
                    "birth_year": person.birth_year,
                    "death_city": person.death_city,
                    "death_country": person.death_country,
                    "death_day": person.death_day,
                    "death_month": person.death_month,
                    "death_year": person.death_year,
                    "photo": person.photo,
                    "birth_certificate": person.birth_certificate,
                    "death_certificate": person.death_certificate,
                    "inheritance_confinement": person.inheritance_confinement
                }

                try:
                    _ = await graph_svc.query(
                        query,
                        params
                    )
                except Exception as e:
                    print(f"Error processing person query: {e}")

        # create country nodes
        for country in countries:
            # Create country node
            query = """
                MERGE (c:Country {name: $name})
                RETURN c
            """

            params = {
                "name": country
            }

            try:
                _ = await graph_svc.query(
                    query,
                    params
                )
            except Exception as e:
                print(f"Error processing country query: {e}")

        # create city nodes
        for city in cities:
            # Create city node
            query = """
                MERGE (c:City {name: $name})
                RETURN c
            """

            params = {
                "name": city
            }

            try:
                _ = await graph_svc.query(
                    query,
                    params
                )
            except Exception as e:
                print(f"Error processing city query: {e}")

        # map countries to their cities
        for country, cities_set in countrycities.items():
            for city in cities_set:
                query = """
                    MATCH (c:Country {name: $country}), (ci:City {name: $city})
                    MERGE (c)-[:HAS_CITY]->(ci)
                    MERGE (ci)-[:HAS_COUNTRY]->(c)
                """

                params = {
                    "country": country,
                    "city": city
                }

                try:
                    _ = await graph_svc.query(
                        query,
                        params
                    )
                except Exception as e:
                    print(f"Error processing country-city query: {e}")


        # map children to their parents
        for parent, children_list in children.items():
            for child in children_list:
                query = """
                    MATCH (p:Person {name: $parent}), (c:Person {name: $child})
                    MERGE (p)-[:PARENT_OF]->(c)
                """

                params = {
                    "parent": parent,
                    "child": child
                }

                try:
                    _ = await graph_svc.query(
                        query,
                        params
                    )
                except Exception as e:
                    print(f"Error processing parent-child query: {e}")

        # map spouses to their spouses
        for person, spouse_list in spouses.items():
            for spouse in spouse_list:
                query = """
                    MATCH (p:Person {name: $person}), (s:Person {name: $spouse})
                    MERGE (p)-[:SPOUSE_OF]->(s)
                """

                params = {
                    "person": person,
                    "spouse": spouse
                }

                try:
                    _ = await graph_svc.query(
                        query,
                        params
                    )
                except Exception as e:
                    print(f"Error processing spouse query: {e}")

        # map persons to their residence cities
        for person, city in residence_cities.items():
            query = """
                MATCH (p:Person {name: $person}), (c:City {name: $city})
                MERGE (p)-[:RESIDENT_OF]->(c)
            """

            params = {
                "person": person,
                "city": city
            }

            try:
                _ = await graph_svc.query(
                    query,
                    params
                )
            except Exception as e:
                print(f"Error processing residence city query: {e}")

        # map persons to their residence countries
        for person, country in residence_countries.items():
            query = """
                MATCH (p:Person {name: $person}), (c:Country {name: $country})
                MERGE (p)-[:RESIDENT_OF]->(c)
            """

            params = {
                "person": person,
                "country": country
            }

            try:
                _ = await graph_svc.query(
                    query,
                    params
                )
            except Exception as e:
                print(f"Error processing residence country query: {e}")

        # map persons to their birth cities
        for person, city in birth_cities.items():
            query = """
                MATCH (p:Person {name: $person}), (c:City {name: $city})
                MERGE (p)-[:BORN_IN]->(c)
            """

            params = {
                "person": person,
                "city": city
            }

            try:
                _ = await graph_svc.query(
                    query,
                    params
                )
            except Exception as e:
                print(f"Error processing birth city query: {e}")

        # map persons to their birth countries
        for person, country in birth_countries.items():
            query = """
                MATCH (p:Person {name: $person}), (c:Country {name: $country})
                MERGE (p)-[:BORN_IN]->(c)
            """

            params = {
                "person": person,
                "country": country
            }

            try:
                _ = await graph_svc.query(
                    query,
                    params
                )
            except Exception as e:
                print(f"Error processing birth country query: {e}")

        # map persons to their death cities
        for person, city in death_cities.items():
            query = """
                MATCH (p:Person {name: $person}), (c:City {name: $city})
                MERGE (p)-[:DIED_IN]->(c)
            """

            params = {
                "person": person,
                "city": city
            }

            try:
                _ = await graph_svc.query(
                    query,
                    params
                )
            except Exception as e:
                print(f"Error processing death city query: {e}")

        # map persons to their death countries
        for person, country in death_countries.items():
            query = """
                MATCH (p:Person {name: $person}), (c:Country {name: $country})
                MERGE (p)-[:DIED_IN]->(c)
            """

            params = {
                "person": person,
                "country": country
            }

            try:
                _ = await graph_svc.query(
                    query,
                    params
                )
            except Exception as e:
                print(f"Error processing death country query: {e}")

        # query the database
        query = """
            MATCH (p:Person)
            RETURN p.name, p.residence_city, p.residence_country
            ORDER BY p.name DESC
        """
        records = await graph_svc.query(query)
        print(f"Persons Query '{query}' returned {len(records)} records:")
        for row in records:
            print(row)
    except Exception as e:
        print(f"Ingest persons error occurred: {e}")

# define `_ingest_properties` as a command processor to ingest properties data.
async def _ingest_properties(_: IConfigService, graph_svc: IGraphService) -> None:
    @dataclass
    class Property:
        name: str
        lot: str
        description: str
        location: str
        city: str
        country: str
        area: float
        area_unit: str
        shares: float
        owner: str
        possessed: bool
        unsold: bool
        organized: bool
        effects: bool

    try:
        owners : dict[str, str] = {}
        countries : dict[str, str] = {}
        cities : dict[str, str] = {}

        base_dir = os.path.dirname(os.path.abspath(__file__))

        properties_file_path = os.path.join(base_dir, "data", "properties.json")

        # load properties
        with open(properties_file_path, "r") as f:
            properties = json.load(f)

            # create property nodes
            for prop_data in properties:
                property = Property(**prop_data)

                # Add owners
                if property.owner and property.owner != "n/a":
                    owners[property.name] = property.owner

                # Add countries
                if property.country and property.country != "n/a":
                    countries[property.name] = property.country

                # Add cities
                if property.city and property.city != "n/a":
                    cities[property.name] = property.city

                # Create property node
                query = """
                    MERGE (p:Property {name: $name})
                        ON CREATE SET
                            p.lot = $lot,
                            p.description = $description,
                            p.location = $location,
                            p.city = $city,
                            p.country = $country,
                            p.area = $area,
                            p.area_unit = $area_unit,
                            p.shares = $shares,
                            p.owner = $owner,
                            p.possessed = $possessed,
                            p.unsold = $unsold,
                            p.organized = $organized,
                            p.effects = $effects
                        ON MATCH SET
                            p.lot = $lot,
                            p.description = $description,
                            p.location = $location,
                            p.city = $city,
                            p.country = $country,
                            p.area = $area,
                            p.area_unit = $area_unit,
                            p.shares = $shares,
                            p.owner = $owner,
                            p.possessed = $possessed,
                            p.unsold = $unsold,
                            p.organized = $organized,
                            p.effects = $effects
                    RETURN p
                """

                params = {
                    "name": property.name,
                    "lot": property.lot,
                    "description": property.description,
                    "location": property.location,
                    "city": property.city,
                    "country": property.country,
                    "area": property.area,
                    "area_unit": property.area_unit,
                    "shares": property.shares,
                    "owner": property.owner,
                    "possessed": property.possessed,
                    "unsold": property.unsold,
                    "organized": property.organized,
                    "effects": property.effects
                }

                try:
                    _ = await graph_svc.query(
                        query,
                        params
                    )
                except Exception as e:
                    print(f"Error processing property query: {e}")

        # map properties to their owners
        for property_name, owner in owners.items():
            query = """
                MATCH (p:Property {name: $property_name}), (o:Person {name: $owner})
                MERGE (p)-[:OWNED_BY]->(o)
                MERGE (o)-[:OWNS]->(p)
            """

            params = {
                "property_name": property_name,
                "owner": owner
            }

            try:
                _ = await graph_svc.query(
                    query,
                    params
                )
            except Exception as e:
                print(f"Error processing property-owner query: {e}")

        # map properties to their countries
        for property_name, country in countries.items():
            query = """
                MATCH (p:Property {name: $property_name}), (c:Country {name: $country})
                MERGE (p)-[:LOCATED_IN]->(c)
                MERGE (c)-[:HAS_PROPERTY]->(p)
            """

            params = {
                "property_name": property_name,
                "country": country
            }

            try:
                _ = await graph_svc.query(
                    query,
                    params
                )
            except Exception as e:
                print(f"Error processing property-owner query: {e}")

        # map properties to their cities
        for property_name, city in cities.items():
            query = """
                MATCH (p:Property {name: $property_name}), (c:City {name: $city})
                MERGE (p)-[:LOCATED_IN]->(c)
                MERGE (c)-[:HAS_PROPERTY]->(p)
            """

            params = {
                "property_name": property_name,
                "city": city
            }

            try:
                _ = await graph_svc.query(
                    query,
                    params
                )
            except Exception as e:
                print(f"Error processing property-city query: {e}")

        # query the database
        query = """
            MATCH (p:Property)
            RETURN p.name, p.location, p.city, p.country
            ORDER BY p.name DESC
        """
        records = await graph_svc.query(query)
        print(f"Properties Query '{query}' returned {len(records)} records:")
        for row in records:
            print(row)
    except Exception as e:
        print(f"Ingest properties error occurred: {e}")

# define `visualize` as a command processor to visualize queried data.
async def visualize(query_name: str) -> None:
    # Initialize services
    cfg_svc = EnvVarsConfigService()
    graph_svc = Neo4jGraphService(cfg_svc)

    try:
        # Get the directory where this cli.py file is located
        base_dir = os.path.dirname(os.path.abspath(__file__))

        query_file_path = os.path.join(base_dir, "queries", f"{query_name}.cypher")
        if not os.path.exists(query_file_path):
            print(f"Query file '{query_file_path}' does not exist.")
            return
        
        params_file_path = os.path.join(base_dir, "parameters", f"{query_name}.json")
        if not os.path.exists(params_file_path):
            print(f"Params file '{params_file_path}' does not exist.")
            return
        
        node_attrs_file_path = os.path.join(base_dir, "node_attrs", f"{query_name}.json")
        if not os.path.exists(node_attrs_file_path):
            node_attrs_file_path = os.path.join(base_dir, "node_attrs", "default.json")

        driver = graph_svc.expose_driver()
        if not driver:
            print("Graph service driver is not available.")
            return

        with open(query_file_path, "r") as f:
            query = f.read()

        with open(params_file_path, "r") as f:
            params = json.load(f)

        with open(node_attrs_file_path, "r") as f:
            node_attrs = json.load(f)

        # Query to get a graph result
        graph_result = driver.execute_query(
            query,
            params,
            result_transformer_=neo4j.Result.graph,
        )

        # Draw graph
        visualize_graph(graph_result, node_attrs)

    except Exception as e:
        print(f"Visualize error occurred: {e}")
    finally:
        # Finalize services
        cfg_svc.finalize()
        await graph_svc.finalize()

# define a command processors mapping where each key is a command name
# and the value is an async function that performs the command. 
# the processor is a callable function that takes variant 
# input arguments, returns None and must be awaited. 
processors: Dict[str, Callable[..., Awaitable [None]]] = {
    "ingest": ingest,
    "visualize": visualize
}

## Neo4J Useful Queries:
# Return all persons that are residents of Lebanon:
# MATCH (p:Person)-[:RESIDENT_OF]->(c:Country {name: "Lebanon"}) RETURN p LIMIT 25;
# Return all persons that are born in Syria:
# MATCH (p:Person)-[:BORN_IN]->(c:Country {name: "Syria"}) RETURN p LIMIT 25;
# Return all properties that are located in Syria:
# MATCH (p:Property)-[:LOCATED_IN]->(c:Country {name: "Syria"}) RETURN p LIMIT 25;
# Returns all person names:
# MATCH (p:Person) RETURN p.name LIMIT 25;
# Returns all person selected attributes:
# MATCH (p:Person) RETURN p.name, p.birth_country, p.birth_city, p.death_city, p.death_country LIMIT 25
# Returns all person selected attributes:
# MATCH (p:Person) RETURN p.name, p.profession, p.gender, p.residence_country, p.residence_city, p.birth_country, p.birth_city, p.death_city, p.death_country LIMIT 25;

# this cli processor is called from the main cli.py in the root folder.
# it is used to process the command line arguments and call the appropriate processor.
# it leverages the args passed to it from the main.cli
async def main(args=None):
    parser = argparse.ArgumentParser(description="CLI Processor to support ENH agent.")
    parser.add_argument("proc_name", help="processor command")
    parser.add_argument("data_source", nargs="?", help="data source from which to read person and property data: local json files or remote database.")
    args = parser.parse_args(args)

    if not args.proc_name:
        print("No proc name is provided. Please provide a processor i.e. build.")
        sys.exit(1)

    if args.proc_name not in processors:
        print(f"Unknown command: {args.proc_name}. Available commands: {', '.join(processors.keys())}")
        sys.exit(1)

    await processors[args.proc_name](args.data_source if args.data_source else None)
