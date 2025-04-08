from owlready2 import Imp

from .dependencies import *
from .classes import *
from .individuals import *
from .object_properties import *
from .classes import soma_onto

ForceMinimalExertion.is_a = [soma_onto.ForceAttribute]
# ForceMinimalExertion.restrictions = [exerts_force.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Cutting)]
# Restriction: Exerted by a physical object (e.g., a knife) during a cutting action with minimal force.

ForceProprioceptionFeedback.is_a = [soma_onto.ForceAttribute]
# ForceProprioceptionFeedback.restrictions = [is_exerted_by.some(soma_onto.Agent), occurs_during.some(soma_onto.Action)]
# Restriction: Feedback force sensed by a robot during an action (e.g., grasping or cutting).

ForceMinorResistance.is_a = [soma_onto.ForceAttribute]
# ForceMinorResistance.restrictions = [resists_force.some(soma_onto.PhysicalObject), occurs_during.some(soma_onto.Action)]
# Restriction: Resistance force from an object (e.g., air or workspace) during an action.

ForceContactForce.is_a = [soma_onto.ForceAttribute]
# ForceContactForce.restrictions = [exerts_force.some(soma_onto.PhysicalObject), applied_to.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Grasping)]
# Restriction: Initial grasping force exerted by one object (e.g., gripper) onto another (e.g., knife).

ForceResistanceFromObject.is_a = [soma_onto.ForceAttribute]
# ForceResistanceFromObject.restrictions = [resists_force.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Grasping)]
# Restriction: Resistance force from an object’s shape during grasping.

ForceEquilibriumHold.is_a = [soma_onto.ForceAttribute]
# ForceEquilibriumHold.restrictions = [exerts_force.some(soma_onto.PhysicalObject), applied_to.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Grasping)]
# Restriction: Stable force exerted to hold an object during grasping.

ForceEquilibriumState.is_a = [soma_onto.ForceAttribute]
# ForceEquilibriumState.restrictions = [exerts_force.some(soma_onto.PhysicalObject), occurs_during.some(soma_onto.Action)]
# Restriction: Minimal force state before contact, exerted by an object during an action.

ForceGravityCompensation.is_a = [soma_onto.ForceAttribute]
# ForceGravityCompensation.restrictions = [exerts_force.some(soma_onto.PhysicalObject), applied_to.some(soma_onto.PhysicalObject)]
# Restriction: Force exerted to compensate gravity on an object (e.g., holding a knife).

ForcePreloading.is_a = [soma_onto.ForceAttribute]
# ForcePreloading.restrictions = [exerts_force.some(soma_onto.PhysicalObject), applied_to.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Cutting)]
# Restriction: Pre-cutting downward force exerted on an object.

ForceShearForce.is_a = [soma_onto.ForceAttribute]
# ForceShearForce.restrictions = [exerts_force.some(soma_onto.PhysicalObject), applied_to.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Cutting)]
# Restriction: Lateral shear force exerted by a blade during cutting.

ForceCompressiveForce.is_a = [soma_onto.ForceAttribute]
# ForceCompressiveForce.restrictions = [exerts_force.some(soma_onto.PhysicalObject), applied_to.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Cutting)]
# Restriction: Downward compressive force exerted during cutting.

ForceBlockageEvent.is_a = [soma_onto.ForceAttribute]
# ForceBlockageEvent.restrictions = [resists_force.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Cutting)]
# Restriction: Resistance force before blade penetration during cutting.

ForceBreakageEvent.is_a = [soma_onto.ForceAttribute]
# ForceBreakageEvent.restrictions = [applied_to.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Cutting)]
# Restriction: Force causing an object to fracture during cutting.

ForceModulationDuringCutting.is_a = [soma_onto.ForceAttribute]
# ForceModulationDuringCutting.restrictions = [exerts_force.some(soma_onto.PhysicalObject), applied_to.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Cutting)]
# Restriction: Dynamically adjusted force exerted during cutting.

ForceLoadReduction.is_a = [soma_onto.ForceAttribute]
# ForceLoadReduction.restrictions = [exerts_force.some(soma_onto.PhysicalObject), applied_to.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Cutting)]
# Restriction: Force reduction after cutting.

ForceEquilibriumReset.is_a = [soma_onto.ForceAttribute]
# ForceEquilibriumReset.restrictions = [exerts_force.some(soma_onto.PhysicalObject), occurs_during.some(soma_onto.Action)]
# Restriction: Stabilization force after task completion.

ForceFrictionGrip.is_a = [soma_onto.StaticFrictionAttribute]
# ForceFrictionGrip.restrictions = [exerts_force.some(soma_onto.PhysicalObject), applied_to.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Grasping)]
# Restriction: Static friction force exerted to prevent slipping during grasping.

ForceFrictionResistance.is_a = [soma_onto.KineticFrictionAttribute]
# ForceFrictionResistance.restrictions = [resists_force.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Cutting)]
# Restriction: Kinetic friction force from an object (e.g., apple fibers) during cutting.

ForceSeparationEvent.is_a = [soma_onto.NetForce]
# ForceSeparationEvent.restrictions = [applied_to.some(soma_onto.PhysicalObject), occurs_during.value(soma_onto.Cutting)]
# Restriction: Net force causing object separation (e.g., apple halves) during cutting.

# Properties
exerts_force.is_a = [ObjectProperty, TransitiveProperty]
exerts_force.domain = [soma_onto.PhysicalObject]
exerts_force.range = [soma_onto.ForceAttribute]
exerts_force.inverse_property = is_exerted_by

is_exerted_by.is_a = [ObjectProperty, TransitiveProperty]
is_exerted_by.domain = [soma_onto.ForceAttribute]
is_exerted_by.range = [soma_onto.PhysicalObject]

resists_force.is_a = [ObjectProperty, TransitiveProperty]
resists_force.domain = [soma_onto.PhysicalObject]
resists_force.range = [soma_onto.ForceAttribute]
resists_force.inverse_property = is_resisted_by

is_resisted_by.is_a = [ObjectProperty, TransitiveProperty]
is_resisted_by.domain = [soma_onto.ForceAttribute]
is_resisted_by.range = [soma_onto.PhysicalObject]

occurs_during.is_a = [ObjectProperty]
occurs_during.domain = [soma_onto.ForceAttribute]
occurs_during.range = [soma_onto.Action]

applied_to.is_a = [ObjectProperty]
applied_to.domain = [soma_onto.ForceAttribute]
applied_to.range = [soma_onto.PhysicalObject]

# Existing SOMA properties (mapped directly)
hasNetForce = soma_onto.hasNetForce  # Domain: PhysicalObject, Range: NetForce
isNetForceOf = soma_onto.isNetForceOf  # Inverse of hasNetForce
hasFrictionValue = soma_onto.hasFrictionValue  # Domain: FrictionAttribute, Range: xsd:double

# Class mappings to SOMA
Action.equivalent_to = [soma_onto.Action]
PhysicalAttribute.equivalent_to = [soma_onto.PhysicalAttribute]
ForceAttribute.equivalent_to = [soma_onto.ForceAttribute]
FrictionAttribute.equivalent_to = [soma_onto.FrictionAttribute]
NetForce.equivalent_to = [soma_onto.NetForce]
StaticFrictionAttribute.equivalent_to = [soma_onto.StaticFrictionAttribute]
KineticFrictionAttribute.equivalent_to = [soma_onto.KineticFrictionAttribute]
PhysicalObject.equivalent_to = [soma_onto.PhysicalObject]
Robot.equivalent_to = [soma_onto.Agent]
Cutting.equivalent_to = [soma_onto.Cutting]
Grasping.equivalent_to = [soma_onto.Grasping]


# Cutting.equivalent_to = [soma_onto.Cutting]
# Cutting.is_a = [Action]
# CuttingAction.restrictions = [involves.some(PhysicalObject), occurs_in.some(Room)]
# Example: A cutting action involves a physical object (e.g., knife, apple) in a room (e.g., kitchen).

# Grasping.equivalent_to = [soma_onto.Grasping]
# GraspingAction.is_a = [Action]
# GraspingAction.restrictions = [involves.some(PhysicalObject), performed_by.some(Agent)]
# # Example: A grasping action involves an object and is performed by an agent (e.g., robot).
# ************************************************************************************************************* #


Floor.is_a = [PhysicalObject]

Milk.is_a = [Food]

Robot.is_a = [Agent]

Human.is_a = [Agent]

Cereal.is_a = [Food]

Kitchen.is_a = [Room]

Food.is_a = [PhysicalObject]

Apartment.is_a = [Room]

Container.is_a = [PhysicalObject]

Room.is_a = [Location, Container]

Cup.is_a = [Container]

Bowl.is_a = [Container]

DefaultPreferredGraspAlignment.is_a = [PreferredGraspAlignment, has_preferred_axis.some(NoAlignment),
                                       has_vertical_alignment.value(Falsy), has_rotated_gripper.value(Falsy),
                                       has_rim_grasp.value(Falsy)]

BowlPreferredGraspAlignment.is_a = [PreferredGraspAlignment, has_preferred_axis.value(NoAlignment),
                                    has_vertical_alignment.value(Truthy), has_rotated_gripper.value(Truthy),
                                    has_rim_grasp.value(Truthy)]

SpoonPreferredGraspAlignment.is_a = [PreferredGraspAlignment, has_preferred_axis.value(XAxis),
                                     has_vertical_alignment.value(Truthy), has_rotated_gripper.value(Falsy),
                                     has_rim_grasp.value(Falsy)]

CerealPreferredGraspAlignment.is_a = [PreferredGraspAlignment, has_preferred_axis.value(XAxis),
                                      has_vertical_alignment.value(Falsy), has_rotated_gripper.value(Falsy),
                                      has_rim_grasp.value(Falsy)]

Cabinet.is_a = [Container]

Drawer.is_a = [Container]

Spoon.is_a = [PhysicalObject]

ContinuousJoint.is_a = [HingeJoint]

HingeJoint.is_a = [MovableJoint]

FixedJoint.is_a = [Joint]

MovableJoint.is_a = [Joint]

PlanarJoint.is_a = [MovableJoint]

PrismaticJoint.is_a = [MovableJoint]

FloatingJoint.is_a = [MovableJoint]

RevoluteJoint.is_a = [HingeJoint]

Event.is_a = [Entity]

Entity.is_a = [Thing]

Action.is_a = [Event]

PhysicalTask.is_a = [Entity]

Supporter.is_a = [PhysicalObject]

SupportedObject.is_a = [PhysicalObject]

is_part_of.is_a = [ObjectProperty, TransitiveProperty, ReflexiveProperty]
is_part_of.domain = [PhysicalObject]
is_part_of.range = [PhysicalObject]

has_part.is_a = [ObjectProperty, TransitiveProperty, ReflexiveProperty]
has_part.domain = [PhysicalObject]
has_part.range = [PhysicalObject]

has_parent_link.is_a = [ObjectProperty]
has_parent_link.domain = [Joint]
has_parent_link.range = [PhysicalObject]

has_child_link.is_a = [ObjectProperty]
has_child_link.domain = [Joint]
has_child_link.range = [PhysicalObject]

contains.is_a = [ObjectProperty, TransitiveProperty]
contains.domain = [Base]
contains.range = [Base]
contains.inverse_property = is_contained_in

contains_object.is_a = [ObjectProperty, TransitiveProperty]
contains_object.domain = [Container]
contains_object.range = [PhysicalObject]
contains_object.inverse_property = is_physically_contained_in

is_contained_in.is_a = [ObjectProperty, TransitiveProperty]
is_contained_in.domain = [Base]
is_contained_in.range = [Base]

is_physically_contained_in.is_a = [ObjectProperty, TransitiveProperty]
is_physically_contained_in.domain = [PhysicalObject]
is_physically_contained_in.range = [Container]

supports.is_a = [ObjectProperty, TransitiveProperty]
supports.domain = [Supporter]
supports.range = [SupportedObject]
supports.inverse_property = is_supported_by

is_supported_by.is_a = [ObjectProperty, TransitiveProperty]
is_supported_by.domain = [SupportedObject]
is_supported_by.range = [Supporter]

for c in ontology.classes():
    c.has_preferred_alignment.append(DefaultPreferredGraspAlignment)

Bowl.has_preferred_alignment = [BowlPreferredGraspAlignment]
Spoon.has_preferred_alignment = [SpoonPreferredGraspAlignment]
Cereal.has_preferred_alignment = [CerealPreferredGraspAlignment]
