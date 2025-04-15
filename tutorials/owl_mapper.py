import owlready2
from owlready2 import *
import uuid
import os
import pathlib
import sexpdata # Needed for parsing the string
import sys
from typing import Any, Tuple, Dict, Optional # For type hinting

# --- Configuration (Define defaults or read from elsewhere) ---
# These can be overridden when calling the main processing function
DEFAULT_SOMA_OWL_PATH = "SOMA.owl"
DEFAULT_SOMA_IRI = "http://www.ease-crc.org/ont/SOMA.owl"
DEFAULT_DUL_IRI = "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl"
DEFAULT_DUL_OWL_PATH = "DUL.owl" # Set "" or None to disable
DEFAULT_OUTPUT_DIR = "ontology_output"
DEFAULT_OUTPUT_FILENAME = "populated_ontology.owl"
DEFAULT_SAVE_FORMAT = "rdfxml"

# --- Mappings (VERIFY THESE CAREFULLY!) ---
# (Keep the map definitions exactly as in the previous complete code)
CONCEPT_MAP = {
    "mug": "DesignedContainer", "cup": "DesignedContainer", "bottle": "DesignedContainer",
    "container": "DesignedContainer", "counter": "DesignedArtifact", "table": "DesignedArtifact",
    "kitchen": "PhysicalPlace", "region": "Region", "human": "Human", "knife":"DesignedTool",
    "blade":"DesignedTool", "apple": "DesignedArtifact", "mango":"DesignedArtifact",
}
ACTION_CLASSIFIER_MAP = { "cutting": "Cutting", "pickup": "PickingUp", "place": "Placing", "move": "Moving", }
DEFAULT_ACTION_BASE_CLASS = "PhysicalAction"
PROPERTY_MAP = {
    "color": "hasColor", "shape": "hasShape", "material": "hasMaterial", "name": "hasName",
    "at": "hasLocation", "on": "hasLocation", "in": "hasLocation", "destination": "hasRegion",
    "target": "isManipulationTarget", "participant": "hasParticipant", "tool": "usesTool",
    "size": "hasSize", "texture": "hasTexture",
}

# --- Global Variables ---
# These might need careful management if the processing function is called multiple times
# within the same Python session without restarting.
INSTANCE_NAMESPACE = None
instance_counters = {}

# --- Helper Functions (Keep ALL functions from previous complete code) ---

# load_ontologies(...)
# find_term(...)
# generate_instance_name(...)
# strip_quotes(...)
# convert_to_tuples(...) - Moved from __main__ to be generally available
# extract_entity_data(...)
# apply_assertions(...)
# parse_action_designator_two_pass(...)
# save_ontology(...)


def load_ontologies(soma_owl_path, soma_iri, dul_owl_path, dul_iri):
    local_owl_dirs = set()
    if soma_owl_path and os.path.exists(soma_owl_path):
        soma_dir = os.path.dirname(soma_owl_path); local_owl_dirs.add(soma_dir)
    dul_path_provided = bool(dul_owl_path and os.path.exists(dul_owl_path))
    if dul_path_provided:
        dul_dir = os.path.dirname(dul_owl_path); local_owl_dirs.add(dul_dir)
    if local_owl_dirs:
        # print(f"Adding directories to owlready2.onto_path: {local_owl_dirs}") # Optional print
        for d in local_owl_dirs: owlready2.onto_path.append(d)
    print(f"Attempting to load SOMA: {soma_iri}")
    soma_onto, dul_onto = None, None; loaded_ontologies = []
    try:
        soma_onto = get_ontology(soma_iri).load()
        print(f"SOMA <{soma_onto.base_iri}> loaded.")
        loaded_ontologies.append(soma_onto)
        global INSTANCE_NAMESPACE; INSTANCE_NAMESPACE = soma_onto
        dul_onto = soma_onto.world.get_ontology(dul_iri)
        if dul_onto and dul_onto.loaded:
            print(f"DUL <{dul_onto.base_iri}> loaded via SOMA import.")
            if dul_onto not in loaded_ontologies: loaded_ontologies.append(dul_onto)
        else:
            print("DUL not auto-loaded. Attempting explicit load...")
            dul_loaded_explicitly = False
            if dul_path_provided:
                try:
                    dul_path_uri = pathlib.Path(dul_owl_path).absolute().as_uri()
                    print(f"Attempting DUL from local: {dul_path_uri}")
                    dul_onto = soma_onto.world.get_ontology(dul_path_uri).load()
                    print(f"DUL <{dul_onto.base_iri}> loaded from local path.")
                    if dul_onto not in loaded_ontologies: loaded_ontologies.append(dul_onto)
                    dul_loaded_explicitly = True
                except Exception as e: print(f"Warning: DUL local load failed: {e}"); dul_onto = None
            if not dul_loaded_explicitly:
                print(f"Attempting DUL from web: {dul_iri}")
                try:
                    dul_onto = soma_onto.world.get_ontology(dul_iri).load()
                    print(f"DUL <{dul_onto.base_iri}> loaded from web IRI.")
                    if dul_onto not in loaded_ontologies: loaded_ontologies.append(dul_onto)
                    dul_loaded_explicitly = True
                except Exception as e: print(f"Warning: DUL web load failed: {e}")
            if not dul_loaded_explicitly: print("Warning: Failed to load DUL.")
    except Exception as e: print(f"Fatal Error loading SOMA: {e}"); return None
    if not soma_onto: print("Fatal Error: SOMA object not available."); return None
    print(f"\n--- Post-Load Verification ---")
    relevant_classes=set([DEFAULT_ACTION_BASE_CLASS]+list(ACTION_CLASSIFIER_MAP.values())+list(CONCEPT_MAP.values()))
    relevant_props=set(["isClassifiedBy","hasParticipant"]+list(PROPERTY_MAP.values()))
    print("Checking key classes:");all_classes_found=True
    for c_name in relevant_classes:
        term=find_term(c_name, loaded_ontologies)
        status="Found" if term and isinstance(term, owlready2.entity.ThingClass) else "*** NOT FOUND or Invalid ***"
        print(f"  Class '{c_name}': {status}");
        if status != "Found": all_classes_found=False
    print("\nChecking key properties:");all_props_found=True
    for p_name in relevant_props:
        term=find_term(p_name, loaded_ontologies)
        status="Found" if term and isinstance(term, owlready2.prop.PropertyClass) else "*** NOT FOUND or Invalid ***"
        print(f"  Property '{p_name}': {status}");
        if status != "Found": all_props_found=False
    if not all_classes_found or not all_props_found: print("\n*** WARNING: Not all required classes/properties found. ***")
    print("--- End Verification ---\n")
    return loaded_ontologies

def find_term(term_name, ontology_list):
    if not ontology_list: return None
    for onto in ontology_list:
        term = getattr(onto, term_name, None)
        if term is not None: return term
    return None

def generate_instance_name(base_name, specific_name=None):
    if specific_name:
        clean_name = strip_quotes(specific_name).replace(" ", "_").replace("-", "_").replace(":", "_").replace(".", "_").lower()
        if INSTANCE_NAMESPACE and INSTANCE_NAMESPACE[clean_name]: return clean_name
        return clean_name
    else:
        base_name_lower = base_name.lower()
        type_base_name = f"{base_name.__class__.__name__}_{base_name_lower}" if not isinstance(base_name, str) else base_name_lower
        count = instance_counters.get(type_base_name, 0) + 1
        instance_counters[type_base_name] = count
        gen_name = f"{base_name_lower}_{count}"
        while INSTANCE_NAMESPACE and INSTANCE_NAMESPACE[gen_name]:
            count += 1; instance_counters[type_base_name] = count; gen_name = f"{base_name_lower}_{count}"
        return gen_name

def strip_quotes(value):
    if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value

# Sexp Conversion function needed by the main processing function
def convert_to_tuples(data: Any) -> Any:
    if isinstance(data, list):
        return tuple(convert_to_tuples(item) for item in data)
    elif isinstance(data, sexpdata.Symbol):
        return data.value()
    elif isinstance(data, (str, int, float, bool, type(None))):
         return data
    else:
        return str(data) # Fallback

def extract_entity_data(content, role):
    if not isinstance(content, (list, tuple)) or len(content) < 2 or content[0] != 'an':
        print(f"Warning: Expected entity content ('an', 'kind', ...), got: {content}"); return None
    entity_kind = content[1]; entity_info = {'role': role, 'type_name': None, 'specific_name': None, 'properties': {}}
    for element in content[2:]:
        if isinstance(element, (list, tuple)) and len(element) == 2:
            key = element[0]; value = strip_quotes(element[1])
            if key == 'type': entity_info['type_name'] = value
            elif key == 'name': entity_info['specific_name'] = value
            elif key == 'properties':
                if isinstance(value, (list, tuple)):
                    for prop_pair in value:
                        if isinstance(prop_pair, (list, tuple)) and len(prop_pair) == 2:
                            entity_info['properties'][prop_pair[0]] = strip_quotes(prop_pair[1])
                        else: print(f"Warning: Invalid item in properties list: {prop_pair}")
                else: print(f"Warning: 'properties' element not list/tuple: {element}")
            # else: pass # Ignore other direct elements for now
        else: print(f"Warning: Unexpected element format in entity content: {element}")
    if not entity_info['type_name']: print(f"Warning: No 'type' found for role '{role}'. Content: {content}"); return None
    return entity_info

def apply_assertions(instance_map, planned_assertions, ontologies):
    print("\n--- Applying Assertions (Pass 2) ---")
    if not instance_map: print("Warning: Instance map empty."); return
    for role, instance_data in planned_assertions.get('instances', {}).items():
        subject_instance = instance_map.get(role)
        if not subject_instance: print(f"Warning: Instance for role '{role}' missing."); continue
        # print(f"Processing assertions for: {subject_instance.name} (Role: {role})") # Optional print
        # Apply isClassifiedBy
        if instance_data.get('classifier_class_name'):
            classifier_name = instance_data['classifier_class_name']
            ClassifierClass = find_term(classifier_name, ontologies); IsClassifiedByProp = find_term("isClassifiedBy", ontologies)
            if ClassifierClass and IsClassifiedByProp and isinstance(IsClassifiedByProp, owlready2.prop.ObjectPropertyClass):
                try: getattr(subject_instance, IsClassifiedByProp.name).append(ClassifierClass); # print(f"  Added: {IsClassifiedByProp.name} {ClassifierClass.name}") # Optional
                except Exception as e: print(f"  Error adding {IsClassifiedByProp.name}: {e}")
            # else: print(f"  *** Failed isClassifiedBy {classifier_name}: Class/Prop not found/invalid.") # Optional
        # Apply data properties
        for key, value in instance_data.get('properties', {}).items():
            prop_name = PROPERTY_MAP.get(key.lower())
            if not prop_name: continue
            DataProp = find_term(prop_name, ontologies)
            if DataProp and isinstance(DataProp, owlready2.prop.DataPropertyClass):
                try: getattr(subject_instance, prop_name).append(value); # print(f"  Added: {prop_name} = {value}") # Optional
                except Exception as e: print(f"  Error adding data property {prop_name}={value}: {e}")
            # else: print(f"  Skipping property '{key}': Property '{prop_name}' not found/invalid.") # Optional
    # Process links
    HasParticipantProp = find_term("hasParticipant", ontologies)
    if not HasParticipantProp or not isinstance(HasParticipantProp, owlready2.prop.ObjectPropertyClass): print("*** WARNING: 'hasParticipant' property missing/invalid.")
    for link_info in planned_assertions.get('links', []):
        subject_role = link_info.get('subject_role'); object_role = link_info.get('object_role'); link_prop_name = link_info.get('prop_name')
        subject_instance = instance_map.get(subject_role); object_instance = instance_map.get(object_role)
        if not subject_instance or not object_instance: print(f"Warning: Skip link {subject_role}->{object_role}. Missing instance."); continue
        LinkProp = HasParticipantProp # Default
        if link_prop_name and link_prop_name != "hasParticipant": LinkProp = find_term(link_prop_name, ontologies)
        if LinkProp and isinstance(LinkProp, owlready2.prop.ObjectPropertyClass):
            try: getattr(subject_instance, LinkProp.name).append(object_instance); print(f"  Added Link: {subject_instance.name} {LinkProp.name} {object_instance.name}")
            except Exception as e: print(f"  Error adding link {subject_instance.name} {LinkProp.name} {object_instance.name}: {e}")
        else: print(f"  *** Failed link {subject_instance.name} -> {object_instance.name}: Property '{link_prop_name or 'hasParticipant'}' not found/invalid.")
    # print("--- Finished Applying Assertions ---") # Optional

def parse_action_designator_two_pass(designator, ontologies):
    if not isinstance(designator, (list, tuple)) or len(designator) < 3 or designator[0]!='an' or designator[1]!='action':
        print(f"Error: Designator must start with ('an', 'action', ...)"); return None, None
    if not ontologies: print("Error: Ontologies not loaded."); return None, None
    # print(f"\n--- Parsing Designator (Two Pass) --- \n{designator}") # Optional
    planned_assertions = {'instances': {}, 'links': []}; created_instances = {}; action_role_id = "__action__"
    # --- Pass 1a: Plan Instances ---
    # print("--- Pass 1a: Planning Instances ---") # Optional
    action_type_name = None
    for element in designator[2:]:
        if isinstance(element, (list, tuple)) and len(element) >= 2:
            key = element[0]; content = element[1]
            if key == 'type' and isinstance(content, str):
                action_type_name = content; action_type_lower = action_type_name.lower()
                classifier_class_name = ACTION_CLASSIFIER_MAP.get(action_type_lower)
                if not classifier_class_name: print(f"*** Error: No classifier mapping for '{action_type_name}'."); continue
                instance_name = generate_instance_name(action_type_lower, None)
                planned_assertions['instances'][action_role_id] = {'base_class_name': DEFAULT_ACTION_BASE_CLASS,'instance_name': instance_name,'classifier_class_name': classifier_class_name,'properties': {}}
                # print(f"Planned action: Role='{action_role_id}', Name='{instance_name}'...") # Optional
            elif isinstance(content, (list, tuple)) and len(content) > 1 and content[0] == 'an':
                role_key = key
                entity_data = extract_entity_data(content, role_key)
                if entity_data:
                    entity_type = entity_data['type_name']; mapped_class_name = CONCEPT_MAP.get(entity_type.lower())
                    if not mapped_class_name: print(f"*** Error: No class mapping for '{entity_type}' (role '{role_key}')."); continue
                    instance_name = generate_instance_name(mapped_class_name, entity_data['specific_name'])
                    planned_assertions['instances'][role_key] = {'base_class_name': mapped_class_name,'instance_name': instance_name,'classifier_class_name': None,'properties': entity_data['properties']}
                    # print(f"Planned entity: Role='{role_key}', Name='{instance_name}'...") # Optional
                    link_prop = "hasParticipant" # Default link property
                    planned_assertions['links'].append({'subject_role': action_role_id,'prop_name': link_prop,'object_role': role_key})
                    # print(f"  Planned link: {action_role_id} --{link_prop}--> {role_key}") # Optional
                # else: print(f"Warning: Failed to extract data for element key '{key}'.") # Optional
    # --- Pass 1b: Create Instances ---
    # print("\n--- Pass 1b: Creating Instances ---") # Optional
    if not planned_assertions['instances']: print("Warning: No instances were planned.")
    else:
        for role, instance_data in planned_assertions['instances'].items():
            class_name=instance_data['base_class_name']; instance_name=instance_data['instance_name']
            BaseClass = find_term(class_name, ontologies)
            if BaseClass and isinstance(BaseClass, owlready2.entity.ThingClass):
                instance = INSTANCE_NAMESPACE[instance_name]
                if not instance:
                    try: instance = BaseClass(instance_name, namespace=INSTANCE_NAMESPACE); # print(f"Created: {instance.name} ({BaseClass.name})") # Optional
                    except Exception as e: print(f"*** Error creating '{instance_name}'({class_name}): {e}"); instance = None
                # else: print(f"Reusing: {instance.name}") # Optional
                if instance: created_instances[role] = instance
            else: print(f"*** Error: Cannot create for role '{role}'. Class '{class_name}' not found/invalid.")
    # --- Pass 2: Apply Assertions ---
    if created_instances: apply_assertions(created_instances, planned_assertions, ontologies)
    else: print("Skipping Pass 2 (Assertions): No instances created.")
    main_action_instance = created_instances.get(action_role_id); participant_entities = {r: i for r, i in created_instances.items() if r != action_role_id}
    # print(f"\n--- Finished Two-Pass Parsing ---") # Optional
    return main_action_instance, participant_entities

def save_ontology(loaded_ontologies, output_path, file_format):
    # print(f"\n--- Saving Modified Ontology ---") # Optional
    output_dir = os.path.dirname(output_path)
    if output_dir:
        try: os.makedirs(output_dir, exist_ok=True); # print(f"Output directory: '{output_dir}'") # Optional
        except OSError as e: print(f"Error creating dir '{output_dir}': {e}"); return
    if loaded_ontologies:
        ontology_to_save = loaded_ontologies[0]
        # print(f"Target ontology: <{ontology_to_save.base_iri}>") # Optional
        # print(f"Output file: '{output_path}' ({file_format})") # Optional
        try:
            ontology_to_save.save(file=output_path, format=file_format)
            print("-" * 20 + f"\nOntology successfully saved to {output_path}\n" + "-" * 20)
        except Exception as e: print(f"\n!!! Error saving ontology: {e} !!!")
    # else: print("\nCannot save: No ontologies loaded.") # Optional


# --- END HELPER FUNCTION DEFINITIONS ---


# --- Main Processing Function ---

def process_designator_string(
    designator_string: str,
    soma_owl_path: str = DEFAULT_SOMA_OWL_PATH,
    soma_iri: str = DEFAULT_SOMA_IRI,
    dul_owl_path: Optional[str] = DEFAULT_DUL_OWL_PATH, # Allow None
    dul_iri: str = DEFAULT_DUL_IRI,
    output_owl_path: Optional[str] = None, # Optional output path
    output_format: str = DEFAULT_SAVE_FORMAT,
    perform_inspection: bool = True,
    save_result: bool = True,
    clear_counters: bool = True # Option to reset instance counters per call
) -> Tuple[Optional[Thing], Optional[Dict[str, Thing]]]:
    """
    Loads ontologies, parses a designator string using sexpdata, creates instances/assertions,
    optionally inspects results, optionally saves the ontology.

    Args:
        designator_string: The S-expression designator string.
        soma_owl_path: Filesystem path hint for SOMA ontology.
        soma_iri: IRI for SOMA ontology.
        dul_owl_path: Optional filesystem path for DUL ontology.
        dul_iri: IRI for DUL ontology.
        output_owl_path: Optional path to save the modified ontology. If None, uses default.
        output_format: Format for saving ("rdfxml", "ntriples").
        perform_inspection: If True, print inspection results to console.
        save_result: If True, save the modified ontology.
        clear_counters: If True, reset instance naming counters before processing.

    Returns:
        tuple: (main_action_instance, participant_entities map) or (None, None) on failure.
    """
    print(f"\n=== Processing Designator String ===")
    main_action_instance = None
    participant_entities = None

    # Optionally clear instance counters for independent processing
    if clear_counters:
        instance_counters.clear()
        print("Instance counters cleared.")

    # 1. Load Ontologies
    # Note: Consider if loading should happen outside if called multiple times
    loaded_ontologies = load_ontologies(soma_owl_path, soma_iri, dul_owl_path, dul_iri)

    if loaded_ontologies:
        # 2. Parse Designator String
        designator_tuple = None
        try:
            parsed_data = sexpdata.loads(designator_string)
            designator_tuple = convert_to_tuples(parsed_data)
            print("Designator string parsed successfully.")
        except sexpdata.ExpectSExp as e:
            print(f"*** Error parsing designator string: {e} ***", file=sys.stderr)
        except Exception as e:
            print(f"*** An unexpected error occurred during designator parsing: {e} ***", file=sys.stderr)

        # 3. Process Parsed Designator if valid
        if designator_tuple:
            print(f"Processing parsed designator tuple: {designator_tuple}")
            main_action_instance, participant_entities = parse_action_designator_two_pass(
                designator_tuple, loaded_ontologies
            )

            # 4. Inspection (Optional)
            if perform_inspection and main_action_instance:
                print(f"\n--- Inspection Results ---")
                IsClassifiedByProp = find_term("isClassifiedBy", loaded_ontologies)
                HasParticipantProp = find_term("hasParticipant", loaded_ontologies)
                print(f"Main Action Instance: {main_action_instance.name} (Type: {type(main_action_instance).__name__})")
                if IsClassifiedByProp and hasattr(main_action_instance, IsClassifiedByProp.name): print(f"  {IsClassifiedByProp.name}: {[c.name for c in getattr(main_action_instance, IsClassifiedByProp.name)]}")
                else: print(f"  isClassifiedBy: Not found or no value.")
                if HasParticipantProp and hasattr(main_action_instance, HasParticipantProp.name): print(f"  {HasParticipantProp.name}: {[p.name for p in getattr(main_action_instance, HasParticipantProp.name)]}")
                else: print(f"  hasParticipant: Not found or no value.")
                print("\nParticipant Entities Created:")
                if participant_entities:
                    for role, inst in participant_entities.items():
                        print(f"  Role '{role}': {inst.name} (Type: {type(inst).__name__})")
                        for prop_key in list(PROPERTY_MAP.keys()): # Check all mapped props
                            prop_name = PROPERTY_MAP.get(prop_key)
                            if prop_name:
                                Prop = find_term(prop_name, loaded_ontologies)
                                if Prop and isinstance(Prop, owlready2.prop.DataPropertyClass) and hasattr(inst, Prop.name):
                                      print(f"    {Prop.name}: {getattr(inst, Prop.name)}")
                else: print("  None.")

            # 5. Save (Optional)
            if save_result:
                # Determine final output path
                final_output_path = output_owl_path
                if not final_output_path:
                    final_output_path = os.path.join(DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_FILENAME)

                save_ontology(loaded_ontologies, final_output_path, output_format)
            else:
                print("\nSkipping ontology saving as requested.")

    else:
        print("\nOntology loading failed. Processing terminated.")

    print(f"=== Finished Processing Designator String ===")
    return main_action_instance, participant_entities


# --- Example Usage within __main__ ---

if __name__ == "__main__":
    pass
    # # Example designator string to process
    # example_designator = """
    # (an action
    #     (type cutting)
    #     (object (an object
    #               (type apple)
    #               (name "my_cut_apple")
    #               (properties (size "medium")
    #                           (texture "smooth")
    #                           (color "red")))))
    # """
	#
    # # Call the main processing function with the example string
    # # Uses default paths/IRIs defined at the top - MODIFY THOSE DEFAULTS
    # action_inst, participants = process_designator_string(
    #     designator_string=example_designator,
    #     # Optionally override defaults here:
    #     # soma_owl_path="/path/to/your/soma.owl",
    #     # dul_owl_path="/path/to/your/DUL.owl",
    #     # output_owl_path="specific_output.owl",
    #     # save_result=True,
    #     # perform_inspection=True
    # )
	#
    # # You can do further processing with the returned instances if needed
    # if action_inst:
    #     print(f"\nFunction returned action instance: {action_inst.name}")
    # if participants:
    #     print(f"Function returned participant instances: {[p.name for p in participants.values()]}")
