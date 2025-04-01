import json
import sys
from knowrob import *
import LPNReasoner

sys.path.append("/home/malineni/ROS_WS/knowrob/tutorials")

InitKnowRob()

# Sample dictionary to be converted to JSON
sample_dict = {
	"logging": {
		"console-sink": {"level": "debug"},
		"file-sink": {"level": "debug"}
	},
	"semantic-web": {
		"prefixes": [
			{"alias": "swrl_test", "uri": "http://knowrob.org/kb/swrl_test"},
			{"alias": "lpn", "uri": "http://knowrob.org/kb/lpn"}
            # {"alias": "pizza", "uri": "http://www.co-ode.org/ontologies/pizza/pizza.owl"}
		]
	},
	"data-sources": [
		{"path": "tests/owl/swrl.owl", "format": "rdf-xml"}
        # {"path": "tests/owl/pizza.owl", "format": "rdf-xml"}
	],
	"data-backends": [
		{
			"type": "MongoDB",
			"name": "mongodb",
			"host": "localhost",
			"port": 27017,
			"db": "swrl",
			"read-only": False
		}
	],
	"reasoner": [
		{
            "name": "LPNReasoner",
            "type": "LPNReasoner",
            "module": "/home/malineni/ROS_WS/knowrob/tutorials/LPNReasoner.py",
			"data-backend": "mongodb",
		}
    ]
}
# Convert the dictionary to a JSON string
json_str = json.dumps(sample_dict)
# Initialize the KnowledgeBase with the PropertyTree
kb = KnowledgeBase(json_str)

if __name__ == "__main__":
	print("Started Main")
	phi1 = QueryParser.parse("swrl_test:hasAncestor(swrl_test:'Fred', ?y)")

	resultStream = kb.submitQuery(phi1, QueryContext(QueryFlag.QUERY_FLAG_ALL_SOLUTIONS))
	resultQueue = resultStream.createQueue()
	# Get the result
	nextResult1 = resultQueue.pop_front()

	if isinstance(nextResult1, AnswerYes):
		for substitution in nextResult1.substitution():
			variable = substitution[1]
			term = substitution[2]
			print(str(variable) + " : " + str(term))

	phi2 = QueryParser.parse("swrl_test:hasSibling(swrl_test:'Ernest', swrl_test:'Fred')")
	resultStream = kb.submitQuery(phi2, QueryContext(QueryFlag.QUERY_FLAG_ALL_SOLUTIONS))
	resultQueue = resultStream.createQueue()
	# Get the result
	nextResult2 = resultQueue.pop_front()
	if isinstance(nextResult2, AnswerNo):
		print("result is negative")
	else:
		print("result is positive")

	phi3 = QueryParser.parse("r(?x, ?y)")
	resultStream = kb.submitQuery(phi3, QueryContext(QueryFlag.QUERY_FLAG_ALL_SOLUTIONS))
	resultQueue = resultStream.createQueue()
	# Get the result
	nextResult3 = resultQueue.pop_front()
	if isinstance(nextResult3, AnswerDontKnow):
		print("We can't say if the result is true or false")
