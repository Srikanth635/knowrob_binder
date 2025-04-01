from knowrob import *
import requests


class ADReasoner(RDFGoalReasoner):
	def __init__(self):
		super(ADReasoner, self).__init__()
		self.nlquery = IRIAtom("http://knowrob.org/kb/nlquery#nlquery")
		self.defineRelation(self.nlquery)
		self.api_endpoint = "http://127.0.0.1:5000/query"

	def initializeReasoner(self, config: PropertyTree) -> bool:
		# nothing to do here
		return True

	def evaluate(self, goal: RDFGoal) -> bool:
		literal = goal.rdfLiterals()[0]
		input_term = literal.subjectTerm()  # The natural language input
		output_var = literal.objectTerm()  # The variable to bind the output to

		# Ensure the input is a string (IRIAtom or StringTerm)
		if isinstance(input_term, IRIAtom) or isinstance(input_term, StringTerm):
			nl_input = str(input_term)
		else:
			logError("Input to nlquery must be a string, got: %s" % input_term)
			return False

		logDebug("Processing natural language query: %s" % nl_input)

		# Invoke the LLM
		llm_response = self._query_llm(nl_input)

		if not llm_response:
			logError("Failed to get response from LLM")
			return False
		if not isinstance(llm_response, str):
			logError(f"LLM response is not a string: {type(llm_response)} - {llm_response}")
			return False

		bindings = Bindings({output_var: String(llm_response)})
		goal.push(bindings)
		# self.storage().query(goal, goal.push)

		return True

	def _query_llm(self, input_text: str) -> str:
		try:
			headers = {
				"Content-Type": "application/json"
			}
			payload = {
				"instruction": input_text,
				"model" : "comprehensive"
			}
			response = requests.post(self.api_endpoint, headers=headers, json=payload)
			response.raise_for_status()  # Raise an exception for bad status codes
			logError(f"flask response text type is {type(response.text)}")
			return response.text

		except Exception as e:
			logError("LLM query failed: %s" % str(e))
			return None





