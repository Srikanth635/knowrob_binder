from knowrob import *
import requests
from owl_mapper import *
from typing import Tuple

class ADReasoner(RDFGoalReasoner):
	def __init__(self):
		super(ADReasoner, self).__init__()
		self.nlquery = IRIAtom("http://knowrob.org/kb/nlquery#nlquery")
		self.defineRelation(self.nlquery)

		self.nlreasoner = IRIAtom("http://knowrob.org/kb/nlreasoner#nlreasoner")
		self.defineRelation(self.nlreasoner)

		self.nlbuild = IRIAtom("http://knowrob.org/kb/nlbuild#nlbuild")
		self.defineRelation(self.nlbuild)

		self.reasoners = {"nlreasoner", "nlbuild"}

		self.gen_endpoint = "http://127.0.0.1:8081/generate"
		self.build_endpoint = "http://127.0.0.1:8081/build"
		self.reason_endpoint = "http://127.0.0.1:8081/reason"

		self.basic_designator : dict = {}
		self.flanagan : str = ""
		self.frame_net : str = ""

		# self.api_endpoint = "http://127.0.0.1:5000/query"

		self.fn_map = {self.nlreasoner : lambda g: self._evaluate_reasoner(g),
					   self.nlbuild : lambda g: self._evaluate_build(g)}

	def initializeReasoner(self, config: PropertyTree) -> bool:
		# nothing to do here
		return True

	def evaluate(self, goal: RDFGoal) -> bool:

		literal = goal.rdfLiterals()[0]
		input_term = literal.subjectTerm()  # The natural language input
		output_var = literal.objectTerm()  # The variable to bind the output to
		predicate_term = literal.propertyTerm()

		predicate = str(predicate_term).split(':')[1]

		if isinstance(predicate_term, IRIAtom) and predicate in self.reasoners:
			return self.fn_map[predicate_term](goal)

		logError("literals, got: %s" % literal)
		logError("predicate, got: %s" % type(predicate_term))

		# Ensure the input is a string (IRIAtom or StringTerm)
		if isinstance(input_term, IRIAtom) or isinstance(input_term, StringTerm):
			nl_input = str(input_term)
		else:
			logError("Input to nlquery must be a string, got: %s" % input_term)
			return False

		logDebug("Processing natural language query: %s" % nl_input)

		# Invoke the LLM
		llm_response_json = self._query_llm(nl_input)

		self.basic_designator = llm_response_json

		cram_plan = llm_response_json['cram_plan_response']

		# logError(f"LLM response: {llm_response}")
		#
		# example_designator = """
		#     (an action
		#         (type cutting)
		#         (object (an object
		#                   (type apple)
		#                   (name "apple")
		#                   (properties (size "medium")
		#                               (texture "smooth")
		#                               (color "red")))))
		#     """
		#
		# action_inst, participants = process_designator_string(designator_string=example_designator)
		# if action_inst:
		# 	print(f"\nFunction returned action instance: {action_inst.name}")
		# if participants:
		# 	print(f"Function returned participant instances: {[p.name for p in participants.values()]}")
		#
		# if not llm_response:
		# 	logError("Failed to get response from LLM")
		# 	return False
		# if not isinstance(llm_response, str):
		# 	logError(f"LLM response is not a string: {type(llm_response)} - {llm_response}")
		# 	return False

		bindings = Bindings({output_var: String(cram_plan)})
		goal.push(bindings)

		# self.storage().query(goal, goal.push)

		return True

	def _evaluate_reasoner(self, goal: RDFGoal) -> bool:
		logError("_evaluate_reasoner DEFINED")
		literal = goal.rdfLiterals()[0]
		input_term = literal.subjectTerm()
		output_var = literal.objectTerm()


		# Ensure the input is a string (IRIAtom or StringTerm)
		if isinstance(input_term, IRIAtom) or isinstance(input_term, StringTerm):
			nl_input = str(input_term)
		else:
			logError("Input to nlquery must be a string, got: %s" % input_term)
			return False

		reason_response_text, reason_response_json = self._reason_designator(nl_input)

		bindings = Bindings({output_var: String(reason_response_text)})
		goal.push(bindings)

		return True

	def _evaluate_build(self, goal: RDFGoal):
		literal = goal.rdfLiterals()[0]
		input_term = literal.subjectTerm()  # The natural language input
		output_var = literal.objectTerm()

		build_response, build_response_json = self._build_designator(self.basic_designator)
		self.flanagan = build_response_json["flanagan"]
		self.frame_net = build_response_json["framenet_model"]

		bindings = Bindings({output_var: String("Models Built")})
		goal.push(bindings)

		logError("Instruction %s" % self.basic_designator["instruction"])
		logError("Action Core %s" % self.basic_designator["action_core"])
		logError("CRAM PLAN %s" % self.basic_designator["cram_plan_response"])
		logError("ENRICHED ATTRIBUTES %s" % self.basic_designator["enriched_action_core_attributes"])

		return True

	def _query_llm(self, input_text: str) -> dict:
		try:
			headers = {
				"Content-Type": "application/json"
			}
			payload = {
				"instruction": input_text
			}
			response = requests.post(self.gen_endpoint, headers=headers, json=payload)
			response.raise_for_status()  # Raise an exception for bad status codes
			logError(f"flask response type is {type(response.json())}")
			logError(f"flask response text type is {type(response.text)}")
			return response.json()

		except Exception as e:
			logError("LLM query failed: %s" % str(e))
			return None

	def _build_designator(self, input_dict: dict):
		try:
			headers = {
				"Content-Type": "application/json"
			}
			payload = {
				"instruction": input_dict['instruction'],
				"cram_plan_response": input_dict['cram_plan_response'],
				"action_core": input_dict['action_core'],
				"enriched_action_core_attributes": input_dict['enriched_action_core_attributes']
			}
			response = requests.post(self.build_endpoint, headers=headers, json=payload)
			response.raise_for_status()  # Raise an exception for bad status codes
			logError(f"flask response type is {type(response.json())}")
			logError(f"flask response text type is {type(response.text)}")
			return response.text, response.json()

		except Exception as e:
			logError("LLM query failed: %s" % str(e))
			return None

	def _reason_designator(self, query_text:str):
		try:
			headers = {
				"Content-Type": "application/json"
			}
			payload = {
				"query" : query_text,
				"instruction": self.basic_designator['instruction'],
				"cram_plan_response": self.basic_designator['cram_plan_response'],
				"action_core": self.basic_designator['action_core'],
				"enriched_action_core_attributes": self.basic_designator['enriched_action_core_attributes'],
				"flanagan": self.flanagan,
				"framenet_model": self.frame_net
			}
			response = requests.post(self.reason_endpoint, headers=headers, json=payload)
			response.raise_for_status()  # Raise an exception for bad status codes
			logError(f"flask response type is {type(response.json())}")
			logError(f"flask response text type is {type(response.text)}")
			return response.text, response.json()

		except Exception as e:
			logError("LLM query failed: %s" % str(e))
			return None





