# File: dynamic_website.py
from owlready2 import *
from flask import Flask, url_for, abort
import werkzeug.serving

# Load the ontology with error handling
try:
    onto = get_ontology("SOMA.owl").load()
except Exception as e:
    print(f"Error loading ontology: {e}")
    exit(1)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def ontology_page():
    """Display the root page with all top-level classes in the ontology."""
    html = """<html><body>"""
    html += """<h2>'%s' ontology</h2>""" % onto.base_iri
    html += """<h3>Root classes</h3>"""
    for Class in Thing.subclasses():
        html += """<p><a href="%s">%s</a></p>""" % (url_for("class_page", iri=Class.iri), Class.name)
    html += """</body></html>"""
    return html

@app.route('/class/<path:iri>')
def class_page(iri):
    """Display a page for a specific class, including superclasses, equivalent classes, subclasses, and individuals."""
    # Retrieve the class from the IRI
    try:
        Class = IRIS[iri]
        if not isinstance(Class, ThingClass):
            abort(404, description="IRI does not correspond to a class")
    except KeyError:
        abort(404, description="Class not found")

    html = """<html><body><h2>'%s' class</h2>""" % Class.name

    # Superclasses
    html += """<h3>Superclasses</h3>"""
    for SuperClass in Class.is_a:
        if isinstance(SuperClass, ThingClass):
            html += """<p><a href="%s">%s</a></p>""" % (url_for("class_page", iri=SuperClass.iri), SuperClass.name)
        else:
            html += """<p>%s</p>""" % str(SuperClass)  # Handle restrictions (e.g., someValuesFrom)

    # Equivalent classes
    html += """<h3>Equivalent classes</h3>"""
    for EquivClass in Class.equivalent_to:
        html += """<p>%s</p>""" % str(EquivClass)

    # Subclasses
    html += """<h3>Subclasses</h3>"""
    for SubClass in Class.subclasses():
        html += """<p><a href="%s">%s</a></p>""" % (url_for("class_page", iri=SubClass.iri), SubClass.name)

    # Individuals
    html += """<h3>Individuals</h3>"""
    for individual in Class.instances():
        html += """<p><a href="%s">%s</a></p>""" % (url_for("individual_page", iri=individual.iri), individual.name)

    html += """</body></html>"""
    return html

@app.route('/individual/<path:iri>')
def individual_page(iri):
    """Display a page for a specific individual, including its classes and relations."""
    # Retrieve the individual from the IRI
    try:
        individual = IRIS[iri]
        if not isinstance(individual, Thing):
            abort(404, description="IRI does not correspond to an individual")
    except KeyError:
        abort(404, description="Individual not found")

    html = """<html><body><h2>'%s' individual</h2>""" % individual.name

    # Classes
    html += """<h3>Classes</h3>"""
    for Class in individual.is_a:
        if isinstance(Class, ThingClass):
            html += """<p><a href="%s">%s</a></p>""" % (url_for("class_page", iri=Class.iri), Class.name)
        else:
            html += """<p>%s</p>""" % str(Class)

    # Relations
    html += """<h3>Relations</h3>"""
    # Check if the individual is a Bacterium and has specific properties
    if isinstance(individual, onto.Bacterium):
        # Safely access properties with try-except to avoid AttributeError
        try:
            html += """<p>shape = %s</p>""" % individual.has_shape
        except AttributeError:
            html += """<p>shape = Not specified</p>"""
        try:
            html += """<p>grouping = %s</p>""" % individual.has_grouping
        except AttributeError:
            html += """<p>grouping = Not specified</p>"""
        try:
            if individual.gram_positive is True:
                html += """<p>Gram +</p>"""
            elif individual.gram_positive is False:
                html += """<p>Gram -</p>"""
            else:
                html += """<p>Gram status = Not specified</p>"""
        except AttributeError:
            html += """<p>Gram status = Not specified</p>"""
    else:
        html += """<p>No bacterium-specific relations available</p>"""

    html += """</body></html>"""
    return html

# Run the Flask app (for development only)
if __name__ == "__main__":
    print("Starting Flask server on http://localhost:5000")
    werkzeug.serving.run_simple("localhost", 5000, app)
