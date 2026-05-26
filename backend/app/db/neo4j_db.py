from __future__ import annotations

import json

from groq import Groq
from neo4j import GraphDatabase

from app.core.config import settings

groq_client = Groq(api_key=settings.GROQ_API_KEY)


class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )

    def close(self) -> None:
        self.driver.close()

    def health_check(self) -> bool:
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS ok")
                return result.single()["ok"] == 1
        except Exception:
            return False

    def initialize_schema(self) -> None:
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.filename IS UNIQUE")

    def extract_entities_with_groq(self, text: str) -> list[dict]:
        prompt = f"""Extract relationships from this text. Return ONLY a JSON array.
Use SHORT relation names with underscores like WORKS_AT, HAS_ROLE, LOCATED_IN.

Example:
[{{"subject": "Pavithra", "relation": "WORKS_AT", "object": "LTIMindtree"}},
 {{"subject": "Pavithra", "relation": "HAS_ROLE", "object": "Graduate Engineer Trainee"}}]

No explanation. No markdown. Just the JSON array.

Text: {text[:500]}"""

        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.0,
            )
            raw = response.choices[0].message.content.strip()
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()
            data = json.loads(raw)
            for item in data:
                item["relation"] = item.get("relation", "RELATED_TO").upper().replace(" ", "_")
            return data
        except Exception as e:
            print(f"[Graph] Extraction failed: {e}")
            return []

    def store_relationships(self, relationships: list[dict], filename: str) -> int:
        if not relationships:
            return 0

        stored = 0
        with self.driver.session() as session:
            session.run(
                "MERGE (d:Document {filename: $filename})",
                filename=filename,
            )
            for rel in relationships:
                subject = rel.get("subject", "").strip()
                relation = rel.get("relation", "RELATED_TO").strip().upper().replace(" ", "_")
                obj = rel.get("object", "").strip()

                if not subject or not obj:
                    continue

                try:
                    session.run(
                        """
                        MERGE (a:Entity {name: $subject})
                        MERGE (b:Entity {name: $object})
                        MERGE (a)-[r:RELATION {type: $relation}]->(b)
                        SET r.source = $filename
                        MERGE (d:Document {filename: $filename})
                        MERGE (a)-[:FOUND_IN]->(d)
                        MERGE (b)-[:FOUND_IN]->(d)
                        """,
                        subject=subject,
                        object=obj,
                        relation=relation,
                        filename=filename,
                    )
                    stored += 1
                except Exception:
                    continue

        return stored

    def extract_and_store_from_chunks(self, chunks: list[dict], filename: str) -> int:
        total_stored = 0
        for chunk in chunks[:10]:
            text = chunk.get("text", "")
            if len(text) < 50:
                continue
            relationships = self.extract_entities_with_groq(text)
            stored = self.store_relationships(relationships, filename)
            total_stored += stored
        return total_stored

    def search_relationships(self, query: str) -> list[dict]:
        words = [w for w in query.lower().split() if len(w) > 3]

        with self.driver.session() as session:
            for word in words:
                result = session.run(
                    """
                    MATCH (a:Entity)-[r:RELATION]->(b:Entity)
                    WHERE toLower(a.name) CONTAINS $term
                       OR toLower(b.name) CONTAINS $term
                    RETURN a.name AS subject, r.type AS relation, b.name AS object, r.source AS document
                    LIMIT 10
                    """,
                    term=word,
                )
                records = [dict(record) for record in result]
                if records:
                    return records

            result = session.run(
                """
                MATCH (a:Entity)-[r:RELATION]->(b:Entity)
                RETURN a.name AS subject, r.type AS relation, b.name AS object, r.source AS document
                LIMIT 10
                """
            )
            return [dict(record) for record in result]