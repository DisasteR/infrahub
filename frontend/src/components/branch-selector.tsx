import { gql, useReactiveVar } from "@apollo/client";
import { CheckIcon } from "@heroicons/react/20/solid";
import {
  CircleStackIcon,
  PlusIcon,
  ShieldCheckIcon,
  Square3Stack3DIcon,
} from "@heroicons/react/24/outline";
import { format, formatDistanceToNow } from "date-fns";
import { useAtom } from "jotai";
import { useCallback, useEffect, useState } from "react";
import { toast } from "react-toastify";
import { StringParam, useQueryParam } from "use-query-params";
import { QSP } from "../config/qsp";
import { Branch } from "../generated/graphql";
import graphqlClient from "../graphql/graphqlClientApollo";
import { createBranch } from "../graphql/mutations/branches/createBranch";
import { branchVar } from "../graphql/variables/branchVar";
import { dateVar } from "../graphql/variables/dateVar";
import { branchesState } from "../state/atoms/branches.atom";
import { configState } from "../state/atoms/config.atom";
import { classNames, objectToString } from "../utils/common";
import { ALERT_TYPES, Alert } from "./alert";
import { BUTTON_TYPES, Button } from "./button";
import { Input } from "./input";
import { PopOver } from "./popover";
import { Select } from "./select";
import { SelectButton } from "./select-button";
import { Switch } from "./switch";

export default function BranchSelector() {
  const [config] = useAtom(configState);
  const [branches] = useAtom(branchesState);
  const [branchInQueryString, setBranchInQueryString] = useQueryParam(QSP.BRANCH, StringParam);
  const branch = useReactiveVar(branchVar);
  const date = useReactiveVar(dateVar);

  const [newBranchName, setNewBranchName] = useState("");
  const [newBranchDescription, setNewBranchDescription] = useState("");
  const [originBranch, setOriginBranch] = useState();
  const [branchedFrom] = useState(); // TODO: Add calendar component
  const [isDataOnly, setIsDataOnly] = useState(true);

  const getCurrentBranch = useCallback((): Branch => {
    if (branch) {
      return branch;
    }

    if (branchInQueryString) {
      return branches.filter((b) => b.name === branchInQueryString.trim())[0];
    } else {
      return branches.filter((b) => b.is_default)[0];
    }
  }, [branch, branchInQueryString, branches]);

  useEffect(() => {
    // On page load, if no branch is set in reactive var. Fetching it from QSP and setting it in state.
    if (!branch && branchInQueryString && branches.length) {
      const selectedBranch = branches.find((b) => b.name === branchInQueryString);
      if (selectedBranch) {
        branchVar(selectedBranch);
      }
    }
  }, [branch, branchInQueryString, branches]);

  const valueLabel = (
    <>
      <Square3Stack3DIcon className="h-5 w-5" aria-hidden="true" />
      <p className="ml-2.5 text-sm font-medium">{getCurrentBranch()?.name}</p>
    </>
  );

  const PopOverButton = (
    <Button
      disabled={config?.main?.allow_anonymous_access}
      buttonType={BUTTON_TYPES.MAIN}
      className="flex-1 rounded-r-md border border-blue-600"
      type="submit">
      <PlusIcon className="h-5 w-5 text-white" aria-hidden="true" />
    </Button>
  );

  const branchesOptions = branches.map((branch) => ({
    id: branch.name,
    name: branch.name,
  }));

  const defaultBranch = branches?.filter((b) => b.is_default)[0]?.name;

  /**
   * Update GraphQL client endpoint whenever branch changes
   */
  const onBranchChange = useCallback((branch: Branch) => {
    branchVar(branch);

    if (branch?.is_default) {
      // undefined is needed to remove a parameter from the QSP
      setBranchInQueryString(undefined);
    } else {
      setBranchInQueryString(branch.name);
    }
  }, []);

  const handleBranchedFrom = (newBranch: any) => setOriginBranch(newBranch);

  const renderOption = ({ option, active, selected }: any) => (
    <div className="flex relative flex-col">
      {option.is_data_only && (
        <div className="absolute bottom-0 right-0">
          <CircleStackIcon
            className={classNames("h-4 w-4", active ? "text-white" : "text-gray-500")}
          />
        </div>
      )}

      {option.is_default && (
        <div className="absolute bottom-0 right-0">
          <ShieldCheckIcon
            className={classNames("h-4 w-4", active ? "text-white" : "text-gray-500")}
          />
        </div>
      )}

      <div className="flex justify-between">
        <p className={selected ? "font-semibold" : "font-normal"}>{option.name}</p>
        {selected ? (
          <span className={active ? "text-white" : "text-blue-500"}>
            <CheckIcon className="h-5 w-5" aria-hidden="true" />
          </span>
        ) : null}
      </div>
      {option?.created_at && (
        <p className={classNames(active ? "text-blue-200" : "text-gray-500", "mt-2")}>
          {formatDistanceToNow(new Date(option?.created_at), {
            addSuffix: true,
          })}
        </p>
      )}
    </div>
  );

  const handleSubmit = async (close: any) => {
    try {
      const newBranch = {
        name: newBranchName,
        description: newBranchDescription,
        // origin_branch: originBranch ?? branches[0]?.name,
        // branched_from: formatISO(branchedFrom ?? new Date()),
        is_data_only: isDataOnly,
      } as Branch;

      const mustationString = createBranch({ data: objectToString(newBranch) });

      const mutation = gql`
        ${mustationString}
      `;

      await graphqlClient.mutate({
        mutation,
        context: {
          branch: branch?.name,
          date,
        },
      });

      close();

      onBranchChange(newBranch);

      // toast(<Alert type={ALERT_TYPES.SUCCESS} message={"Branch created"} />);

      window.location.reload();
    } catch (error) {
      console.error("Error while creating the branch: ", error);
      toast(
        <Alert type={ALERT_TYPES.ERROR} message={"An error occured while creating the branch"} />
      );
    }
  };

  /**
   * There's always a main branch present at least.
   */
  if (!branches.length) {
    return null;
  }

  return (
    <div className="flex">
      <SelectButton
        value={getCurrentBranch()}
        valueLabel={valueLabel}
        onChange={onBranchChange}
        options={branches}
        renderOption={renderOption}
      />
      <PopOver
        disabled={config?.main?.allow_anonymous_access}
        buttonComponent={PopOverButton}
        className="right-0"
        title={"Create a new branch"}>
        {({ close }: any) => (
          <>
            <div className="flex flex-col">
              Branch name:
              <Input value={newBranchName} onChange={setNewBranchName} />
              Branch description:
              <Input value={newBranchDescription} onChange={setNewBranchDescription} />
              Branched from:
              <Select
                disabled
                options={branchesOptions}
                value={originBranch ?? defaultBranch}
                onChange={handleBranchedFrom}
              />
              Branched at:
              <Input
                value={format(branchedFrom ?? new Date(), "MM/dd/yyy HH:mm")}
                onChange={setNewBranchName}
                disabled
              />
              Is data only:
              <Switch checked={isDataOnly} onChange={setIsDataOnly} />
            </div>

            <div className="flex justify-center">
              <Button
                buttonType={BUTTON_TYPES.VALIDATE}
                onClick={() => handleSubmit(close)}
                className="mt-2">
                Create
              </Button>
            </div>
          </>
        )}
      </PopOver>
    </div>
  );
}
