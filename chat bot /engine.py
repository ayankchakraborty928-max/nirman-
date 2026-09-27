import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "requirements_db.json")

def _load_db():
    with open(DB_PATH) as f:
        return json.load(f)

class QuestionEngine:
    def __init__(self, sector="General"):
        db = _load_db()
        self.questions = db["questions"]
        self.rules = db["rules"]
        self.answers = {}
        self.sector = sector

    def answer(self, key, value):
        self.answers[key] = value

    def next_question(self):
        for q in self.questions:
            if q["key"] not in self.answers:
                return q
        return None

    def is_complete(self):
        return self.next_question() is None

    def get_required(self):
        results = []
        for rule in self.rules:
            # Check if rule applies to this entity's sector
            if "sector" in rule["when"]:
                sector_cond = next(c for c in rule["when"] if c["key"] == "sector")
                if sector_cond["value"] != self.sector:
                    continue
            
            # Evaluate other conditions
            if all(self._matches(cond, self.answers) for cond in rule["when"]):
                results.append({
                    "id": rule["id"],
                    "approval": rule["approval"],
                    "documents": rule["documents"]
                })
        return results

    def _matches(self, condition, answers):
        key, op, value = condition["key"], condition["op"], condition["value"]
        if key not in answers: return False
        actual = answers[key]
        if op == "eq": return str(actual).lower() == str(value).lower()
        if op == "in": return str(actual).lower() in [str(v).lower() for v in value]
        return False