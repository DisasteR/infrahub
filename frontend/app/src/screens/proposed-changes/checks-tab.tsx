import { Pill } from "@/components/display/pill";
import { PROPOSED_CHANGES_OBJECT } from "@/config/constants";
import { getProposedChangesChecks } from "@/graphql/queries/proposed-changes/getProposedChangesChecks";
import useQuery from "@/hooks/useQuery";
import { gql } from "@apollo/client";
import { useParams } from "react-router-dom";

export const ProposedChangesChecksTab = () => {
  const { proposedChangeId } = useParams();

  const queryString = getProposedChangesChecks({
    id: proposedChangeId,
    kind: PROPOSED_CHANGES_OBJECT,
  });

  const query = gql`
    ${queryString}
  `;

  const { loading, data } = useQuery(query);

  const result = data ? data[PROPOSED_CHANGES_OBJECT]?.edges[0]?.node : {};

  const validationsCount = result?.validations?.count ?? 0;

  return (
    <div className="flex ml-2">
      <Pill isLoading={loading}>{validationsCount}</Pill>
    </div>
  );
};
