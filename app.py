from flask import Flask, jsonify, request

from duckfine import DuckFine

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/fine")
def fine():
    raw_days = request.args.get("days")
    if raw_days is None:
        return jsonify(error="days query parameter is required"), 400
    try:
        days = int(raw_days)
    except ValueError:
        return jsonify(error="days must be a whole number"), 400

    deluxe = request.args.get("deluxe", "0").lower() in ("1", "true", "yes")
    try:
        fee = DuckFine("quote").charge(days, deluxe=deluxe)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    return jsonify(days=days, deluxe=deluxe, fee=fee)


if __name__ == "__main__":
    app.run(debug=True)
