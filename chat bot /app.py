import os
import uuid
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

import db as db_module
from engine import QuestionEngine
import checklist

app = Flask(__name__)
CORS(app)
db_module.init_db()

# session_id -> QuestionEngine
sessions = {}

@app.route("/register", methods=["POST"])
def register():
    """Handles the new professional entity registration."""
    data = request.json
    # Validate and save organization details
    entity_id = str(uuid.uuid4())
    db_module.save_entity(entity_id, data)

    # Start a checklist session for this new entity
    engine = QuestionEngine(data.get("sector", "General"))
    sessions[entity_id] = engine

    return jsonify({
        "entity_id": entity_id,
        "message": "Organization registered successfully.",
        "next_question": engine.next_question()
    })

@app.route("/start", methods=["POST"])
def start():
    data = request.json
    entity_id = data.get("entity_id")
    if not entity_id:
        return jsonify({"error": "entity_id is required"}), 400

    engine = QuestionEngine()
    sessions[entity_id] = engine
    return jsonify({
        "session_id": entity_id,
        "question": engine.next_question(),
        "done": False
    })

@app.route("/answer", methods=["POST"])
def answer():
    data = request.json
    session_id = data["session_id"]
    engine = sessions.get(session_id)

    if engine is None:
        return jsonify({"error": "Session not found"}), 400

    engine.answer(data["key"], data["value"])
    db_module.save_session(session_id, engine.answers)

    if engine.is_complete():
        required = engine.get_required()
        db_module.save_documents(session_id, required)
        return jsonify({"done": True, "required": required})

    return jsonify({"done": False, "question": engine.next_question()})

@app.route("/export/<session_id>", methods=["GET"])
def export(session_id):
    engine = sessions.get(session_id)
    if engine is None:
        return jsonify({"error": "Session not found"}), 400

    filename = f"/tmp/nirman_checklist_{session_id}.pdf"
    checklist.export_pdf(engine.get_required(), filename)
    return send_file(filename, as_attachment=True, download_name="NIRMAN_Official_Checklist.pdf")

if __name__ == "__main__":
    app.run(debug=True, port=5000)