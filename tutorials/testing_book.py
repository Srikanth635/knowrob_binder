from owlready2 import *

set_log_level(9)

onto = get_ontology("SOMA.owl").load()

with onto:
	class TestClass(Thing): pass
