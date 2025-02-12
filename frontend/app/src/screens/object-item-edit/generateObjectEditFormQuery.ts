import { getRelationshipsForForm } from "@/components/form/utils/getRelationshipsForForm";
import { addAttributesToRequest, addRelationshipsToRequest } from "@/graphql/utils";
import { IProfileSchema, iNodeSchema } from "@/state/atoms/schema.atom";
import { jsonToGraphQLQuery } from "json-to-graphql-query";

export const generateObjectEditFormQuery = ({
  schema,
  objectId,
}: {
  schema: iNodeSchema | IProfileSchema;
  objectId: string;
}): string => {
  const request = {
    query: {
      __name: "GetObjectForEditForm",
      [schema.kind as string]: {
        __args: {
          ids: [objectId],
        },
        edges: {
          node: {
            id: true,
            display_label: true,
            ...addAttributesToRequest(schema.attributes ?? [], { withPermissions: true }),
            ...addRelationshipsToRequest(getRelationshipsForForm(schema.relationships ?? [], true)),
            ...("generate_profile" in schema && schema.generate_profile
              ? {
                  profiles: {
                    edges: {
                      node: {
                        display_label: true,
                        id: true,
                        profile_priority: {
                          value: true,
                        },
                      },
                    },
                  },
                }
              : undefined),
          },
        },
      },
    },
  };

  return jsonToGraphQLQuery(request);
};
