from flask import jsonify


def err(message: str, status: int):
    return jsonify({"error": message}), status


def not_found(resource: str = "Resource"):
    return err(f"{resource} not found", 404)


def forbidden():
    return err("Permission denied", 403)


def bad_request(message: str = "Bad request"):
    return err(message, 400)


def ok(data, status: int = 200):
    return jsonify(data), status
