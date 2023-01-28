#!/usr/bin/python3
"""
Start a flask application
Your web application must be listening on 0.0.0.0, port 5001
Routes:
    /1-hbnb/: display a HTML page: (inside the tag BODY)
"""
from flask import Flask, render_template, url_for
from models import storage
import uuid

app = Flask(__name__)


@app.route('/1-hbnb/', strict_slashes=False)
def hbnb():
    """Displays state data"""
    states = storage.all("State")
    amenities = storage.all("Amenity")
    places = storage.all("Place")
    return render_template("1-hbnb.html",
                           states=states, amenities=amenities, places=places, cache_id=str(uuid.uuid4()))


@app.teardown_appcontext
def teardown(exc):
    """Remove the current SQLAlchemy session."""
    storage.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
