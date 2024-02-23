from infrahub.core.validators.aggregated_checker import AggregatedConstraintChecker

from ....interface import DependencyBuilder, DependencyBuilderContext
from .attribute_regex import SchemaAttributeRegexConstraintDependency
from .attribute_uniqueness import SchemaAttributeUniqueConstraintDependency
from .relationship_optional import SchemaRelationshipOptionalConstraintDependency
from .uniqueness import SchemaUniquenessConstraintDependency


class AggregatedSchemaConstraintsDependency(DependencyBuilder[AggregatedConstraintChecker]):
    @classmethod
    def build(cls, context: DependencyBuilderContext) -> AggregatedConstraintChecker:
        return AggregatedConstraintChecker(
            constraints=[
                SchemaUniquenessConstraintDependency.build(context=context),
                SchemaRelationshipOptionalConstraintDependency.build(context=context),
                SchemaAttributeRegexConstraintDependency.build(context=context),
                SchemaAttributeUniqueConstraintDependency.build(context=context),
            ],
            db=context.db,
            branch=context.branch,
        )