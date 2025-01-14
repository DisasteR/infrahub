import { Button } from "@/components/buttons/button-primitive";
import { Retry } from "@/components/buttons/retry";
import { PieChart } from "@/components/display/pie-chart";
import { ALERT_TYPES, Alert } from "@/components/ui/alert";
import {
  CHECKS_LABEL,
  PROPOSED_CHANGES_VALIDATOR_OBJECT,
  VALIDATIONS_ENUM_MAP,
} from "@/config/constants";
import graphqlClient from "@/graphql/graphqlClientApollo";
import { runCheck } from "@/graphql/mutations/diff/runCheck";
import { useAuth } from "@/hooks/useAuth";
import LoadingScreen from "@/screens/loading-screen/loading-screen";
import { genericsState } from "@/state/atoms/schema.atom";
import { schemaKindLabelState } from "@/state/atoms/schemaKindLabel.atom";
import { getValidatorsStats } from "@/utils/checks";
import { classNames } from "@/utils/common";
import { gql } from "@apollo/client";
import { Icon } from "@iconify-icon/react";
import { useAtomValue } from "jotai";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";

type tChecksSummaryProps = {
  validators: any[];
  isLoading: boolean;
  refetch: Function;
};

export const ChecksSummary = (props: tChecksSummaryProps) => {
  const { isLoading, validators, refetch } = props;

  const { proposedChangeId } = useParams();
  const schemaKindLabel = useAtomValue(schemaKindLabelState);
  const schemaList = useAtomValue(genericsState);
  const { isAuthenticated } = useAuth();

  const schemaData = schemaList.find((s) => s.kind === PROPOSED_CHANGES_VALIDATOR_OBJECT);

  const validatorKinds = schemaData?.used_by ?? [];

  const validatorsCount = validatorKinds.reduce((acc, kind) => {
    const relatedValidators = validators.filter((validator: any) => validator.__typename === kind);

    return { ...acc, [kind]: getValidatorsStats(relatedValidators) };
  }, {});

  const handleRetry = async (validator: string) => {
    const runParams = {
      id: proposedChangeId,
      check_type: VALIDATIONS_ENUM_MAP[validator],
    };

    const mustationString = runCheck(runParams);

    const mutation = gql`
      ${mustationString}
    `;

    const result = await graphqlClient.mutate({ mutation });

    refetch();

    if (result?.data?.CoreProposedChangeRunCheck?.ok) {
      toast(<Alert type={ALERT_TYPES.SUCCESS} message="Checks are running" />);
    }
  };

  const canRetry = (stats: any) => {
    // Can't retry if there is no check
    if (!stats.length) return false;

    // Can't retry if it's empty
    if (stats.length === 1 && stats.find((stat: any) => stat.name === CHECKS_LABEL.EMPTY)) {
      return false;
    }

    // Can retry if there is no in progress check
    return !stats.find((stat: any) => stat.name === CHECKS_LABEL.IN_PROGRESS && !!stat.value);
  };

  return (
    <div className="flex justify-center m-4" data-testid="checks-summary">
      <div className="flex flex-col-reverse items-center relative">
        <div className="lg:absolute lg:top-1/2 lg:-left-28 lg:transform lg:-translate-y-1/2 flex items-center justify-between p-2">
          <Button
            onClick={() => handleRetry("all")}
            disabled={!isAuthenticated}
            variant="ghost"
            className="gap-1 hover:bg-neutral-200"
          >
            Retry all
            <Icon icon="mdi:reload" className={classNames(isLoading && "animate-spin")} />
          </Button>
        </div>

        <div className="flex">
          {!Object.entries(validatorsCount).length && <LoadingScreen hideText />}

          {Object.entries(validatorsCount).map(([kind, data]: [string, any]) => (
            <div key={kind} className="flex items-center justify-center gap-2 p-2">
              <div className={"flex flex-col items-center group relative"}>
                <PieChart data={data} onClick={() => canRetry(data) && handleRetry(kind)}>
                  {canRetry(data) && (
                    <div className="absolute invisible group-hover:visible cursor-pointer">
                      <Retry
                        isLoading={isLoading || !!data.inProgress}
                        isDisabled={!canRetry(data)}
                      />
                    </div>
                  )}
                </PieChart>

                <span className="text-xs">
                  {schemaKindLabel[kind]?.replace("Validator", "").trim()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
