from owlready2 import (Thing, ThingClass, ObjectProperty, FunctionalProperty, get_ontology, And, Or, Not, OneOf,
					   Inverse, normstr, DatatypeProperty, TransitiveProperty, SymmetricProperty, AsymmetricProperty,
					   ReflexiveProperty, IrreflexiveProperty, datetime)
import tempfile
import os

ontology_file = tempfile.NamedTemporaryFile()
ontology = get_ontology("file://" + ontology_file.name).load()
CRAX_ONTOLOGY_NAME = "PyCRAP"

soma_onto = get_ontology("SOMA.owl").load()


class Base(Thing, metaclass=ThingClass):
    namespace = ontology


class BaseProperty(ObjectProperty):
    namespace = ontology


class BaseDatatype(DatatypeProperty):
    namespace = ontology


if __name__ == "__main__":
	import os
	print(os.getcwd())
	onto = get_ontology("SOMA.owl").load()
	print(onto.base_iri)
	print(onto.Cutting.is_a)
