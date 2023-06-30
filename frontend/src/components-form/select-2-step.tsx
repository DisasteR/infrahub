import { gql, useReactiveVar } from "@apollo/client";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { SelectOption } from "../components/select";
import graphqlClient from "../graphql/graphqlClientApollo";
import { getDropdownOptionsForRelatedPeersPaginated } from "../graphql/queries/objects/dropdownOptionsForRelatedPeers";
import { branchVar } from "../graphql/variables/branchVar";
import { dateVar } from "../graphql/variables/dateVar";
import { FormFieldError } from "../screens/edit-form-hook/form";
import { classNames } from "../utils/common";
import { OpsSelect } from "./select";

export interface iTwoStepDropdownData {
  parent: string;
  child: string;
}

interface Props {
  label: string;
  options: SelectOption[];
  value: iTwoStepDropdownData;
  onChange: (value: iTwoStepDropdownData) => void;
  error?: FormFieldError;
  isProtected?: boolean;
}

export const OpsSelect2Step = (props: Props) => {
  const { label, options, value, error, onChange, isProtected } = props;

  const { objectid } = useParams();
  const branch = useReactiveVar(branchVar);
  const date = useReactiveVar(dateVar);

  const [optionsRight, setOptionsRight] = useState<SelectOption[]>([]);

  const [selectedLeft, setSelectedLeft] = useState<SelectOption | null | undefined>(
    value.parent ? options.find((option: SelectOption) => option.id === value.parent) : null
  );

  const [selectedRight, setSelectedRight] = useState<SelectOption | null | undefined>(
    value.child ? optionsRight.find((option) => option.id === value.child) : null
  );

  useEffect(() => {
    setSelectedRight(value.child ? optionsRight.find((option) => option.id === value.child) : null);
  }, [value.child, optionsRight]);

  useEffect(() => {
    setSelectedLeft(value.parent ? options.find((option) => option.id === value.parent) : null);
  }, [value.parent]);

  useEffect(() => {
    if (value) {
      onChange(value);
    }
  }, []);

  const setRightDropdownOptions = useCallback(async () => {
    const objectName = selectedLeft?.id;

    if (!objectName) {
      return;
    }

    const queryString = getDropdownOptionsForRelatedPeersPaginated({
      peers: [objectName],
    });

    const query = gql`
      ${queryString}
    `;

    const { data } = await graphqlClient.query({
      query,
      context: {
        date,
        branch: branch?.name,
      },
    });

    const newRigthOptions = data[objectName]?.edges.map((edge: any) => edge.node);

    setOptionsRight(
      newRigthOptions
        // Filter the options to not select the current object
        .filter((option: any) => option.id !== objectid)
        .map((option: any) => ({
          name: option.display_label,
          id: option.id,
        }))
    );

    if (value.child) {
      setSelectedRight(newRigthOptions.find((option: any) => option.id === value.child));
    }
  }, [selectedLeft?.id]);

  useEffect(() => {
    setRightDropdownOptions();
  }, [selectedLeft?.id]);

  return (
    <div className={classNames("grid grid-cols-6")}>
      <div className="sm:col-span-6">
        <label className="block text-sm font-medium leading-6 text-gray-900 capitalize">
          {label}
        </label>
      </div>
      <div className="sm:col-span-3 mr-2 mt-1">
        <OpsSelect
          error={error}
          disabled={false}
          value={selectedLeft?.id}
          options={options}
          label=""
          onChange={(value) => {
            setSelectedLeft(options.filter((option) => option.id === value.id)[0]);
          }}
          isProtected={isProtected}
        />
      </div>
      <div className="sm:col-span-3 ml-2 mt-1">
        {!!selectedLeft?.id && optionsRight.length > 0 && (
          <OpsSelect
            error={error}
            disabled={false}
            value={selectedRight?.id}
            options={optionsRight}
            label=""
            onChange={(value) => {
              const newOption = optionsRight.find((option) => option.id === value.id);
              setSelectedRight(newOption);
              onChange({
                parent: selectedLeft.id,
                child: value.id,
              });
            }}
            isProtected={isProtected}
          />
        )}
      </div>
    </div>
  );
};
