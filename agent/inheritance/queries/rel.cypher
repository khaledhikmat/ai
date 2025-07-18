MATCH (a:Person {name: $name})-[r]-(b)
RETURN a, r, b