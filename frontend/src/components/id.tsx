import { gql } from "@apollo/client";
import { NODE_OBJECT } from "../config/constants";
import { getObjectDisplayLabel } from "../graphql/queries/objects/getObjectDisplayLabel";
import useQuery from "../hooks/useQuery";
import LoadingScreen from "../screens/loading-screen/loading-screen";
import { BadgeCircle, CIRCLE_BADGE_TYPES } from "./badge-circle";
import { Clipboard } from "./clipboard";

type tId = {
  id: string;
  kind?: string;
};

export const Id = (props: tId) => {
  const { id, kind = NODE_OBJECT } = props;

  const queryString = getObjectDisplayLabel({
    id,
    kind,
  });

  const query = gql`
    ${queryString}
  `;

  const { loading, error, data } = useQuery(query);

  const object = data?.[kind]?.edges?.[0]?.node ?? {};

  if (loading) {
    return <LoadingScreen hideText size={24} />;
  }

  if (error || !object?.display_label) {
    return <BadgeCircle type={CIRCLE_BADGE_TYPES.LIGHT}>Name not found</BadgeCircle>;
  }

  return (
    <BadgeCircle type={CIRCLE_BADGE_TYPES.LIGHT}>
      {object?.display_label}

      <Clipboard
        value={id}
        alert="ID copied!"
        tooltip="Copy ID"
        className="ml-2 p-1 rounded-full"
      />
    </BadgeCircle>
  );
};