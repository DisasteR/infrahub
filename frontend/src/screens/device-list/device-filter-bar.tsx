import { gql, useQuery, useReactiveVar } from "@apollo/client";
import { ChevronDownIcon, ChevronRightIcon, FunnelIcon } from "@heroicons/react/20/solid";
import { useAtom } from "jotai";
import { useState } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { StringParam, useQueryParam } from "use-query-params";
import { Button } from "../../components/button";
import { QSP } from "../../config/qsp";
import { comboxBoxFilterVar, iComboBoxFilter } from "../../graphql/variables/filtersVar";
import { iNodeSchema } from "../../state/atoms/schema.atom";
import { schemaKindNameState } from "../../state/atoms/schemaKindName.atom";
import { getDropdownOptionsForRelatedPeers } from "../../utils/dropdownOptionsForRelatedPeers";
import { resolve } from "../../utils/objects";
import { DynamicControl } from "../edit-form-hook/dynamic-control";
import { DynamicFieldData } from "../edit-form-hook/dynamic-control-types";
import ErrorScreen from "../error-screen/error-screen";
import LoadingScreen from "../loading-screen/loading-screen";
import NoDataFound from "../no-data-found/no-data-found";

// const sortOptions = [
//   { name: "Name", href: "#", current: true },
//   { name: "Status", href: "#", current: false },
//   { name: "ASN", href: "#", current: false },
// ];

interface Props {
  schema: iNodeSchema;
}

export default function DeviceFilterBar(props: Props) {
  const currentFilters = useReactiveVar(comboxBoxFilterVar);

  const [showFilters, setShowFilters] = useState(false);
  const [schemaKindName] = useAtom(schemaKindNameState);
  const [filtersInQueryString, setFiltersInQueryString] = useQueryParam(QSP.FILTER, StringParam);

  const filters = filtersInQueryString ? JSON.parse(filtersInQueryString) : currentFilters;

  const peers: string[] = [];
  (props.schema.filters || []).forEach((f) => {
    if (f.kind === "Object" && f.object_kind) {
      peers.push(schemaKindName[f.object_kind]);
    }
  });
  const queryString = getDropdownOptionsForRelatedPeers({
    peers,
  });

  const query = peers.length
    ? gql`
        ${queryString}
      `
    : gql`
        query {
          __type(name: "DataSource") {
            fields {
              name
              description
            }
          }
        }
      `;

  const { loading, error, data } = useQuery(query, { skip: !props.schema });

  const peerDropdownOptions: any = data;
  const formFields: DynamicFieldData[] = [];

  props.schema.filters?.forEach((filter) => {
    const currentValue = filters?.find((f: iComboBoxFilter) => f.name === filter.name);
    if (filter.kind === "Text" && !filter.enum) {
      formFields.push({
        label: filter.name,
        name: filter.name,
        type: "text",
        value: currentValue ?? "",
      });
    } else if (filter.kind === "Text" && filter.enum) {
      formFields.push({
        label: filter.name,
        name: filter.name,
        type: "select",
        value: currentValue ?? "",
        options: {
          values: filter.enum?.map((row: any) => ({
            name: row,
            id: row,
          })),
        },
      });
    } else if (filter.kind === "Object") {
      if (
        filter.object_kind &&
        peerDropdownOptions &&
        peerDropdownOptions[schemaKindName[filter.object_kind]]
      ) {
        const options = peerDropdownOptions[schemaKindName[filter.object_kind]].map((row: any) => ({
          name: row.display_label,
          id: row.id,
        }));
        formFields.push({
          label: filter.name,
          name: filter.name,
          type: "select",
          value: currentValue ? currentValue.value : "",
          options: {
            values: options,
          },
        });
      }
    }
  });

  const onSubmit = (data: any) => {
    const keys = Object.keys(data);
    const filters: iComboBoxFilter[] = [];
    for (let filterKey of keys) {
      const filterValue = data[filterKey];
      if (data[filterKey]) {
        filters.push({
          display_label: filterKey,
          name: filterKey,
          value: filterValue,
        });
      }
    }
    comboxBoxFilterVar(filters);
    if (filters.length) {
      setFiltersInQueryString(JSON.stringify(filters));
    } else {
      setFiltersInQueryString(undefined);
    }
  };

  const formMethods = useForm();
  const {
    handleSubmit,
    reset,
    resetField,
    formState: { errors },
  } = formMethods;

  const FilterField = (props: any) => {
    const { field, error } = props;

    return (
      <div className="p-2 mr-2">
        <DynamicControl {...field} error={error} />
      </div>
    );
  };

  if (error) {
    return <ErrorScreen />;
  }

  if (loading || !props.schema) {
    return <LoadingScreen />;
  }

  if (!data) {
    return <NoDataFound />;
  }

  return (
    <div className="bg-white">
      <div
        aria-labelledby="filter-heading"
        className="grid items-center border-t border-b border-gray-200">
        <h2 id="filter-heading" className="sr-only">
          Filters
        </h2>
        <div className="bg-gray-100">
          <div className="mx-auto py-3 sm:flex sm:items-center sm:px-6 lg:px-8">
            <div className="flex space-x-6 divide-x divide-gray-200 text-sm">
              <div>
                <div className="group flex items-center font-medium text-blue-500">
                  <FunnelIcon
                    className="mr-2 h-5 w-5 flex-none text-blue-400 group-hover:text-blue-500"
                    aria-hidden="true"
                  />
                  {filters.length} Filters
                </div>
              </div>
              <div className="pl-6">
                <button
                  onClick={() => {
                    comboxBoxFilterVar([]);
                    reset();
                    setFiltersInQueryString(undefined);
                  }}
                  // onClick={() => {
                  //   reset();
                  //   setCurrentFilters([]);
                  //   setFiltersInQueryString(undefined);
                  // }}
                  type="button"
                  className="text-gray-500">
                  Clear all
                </button>
              </div>
            </div>
            <div aria-hidden="true" className="hidden h-5 w-px bg-gray-300 sm:ml-4 sm:block" />
            <div className="mt-2 flex-1 sm:mt-0 sm:ml-4">
              <div className="-m-1 flex flex-wrap items-center">
                {/* {currentFilters.map((filter: iComboBoxFilter) => ( */}
                {filters.map((filter: iComboBoxFilter) => (
                  <span
                    key={filter.name}
                    className="m-1 inline-flex items-center rounded-full border border-gray-200 bg-white py-1.5 pl-3 pr-2 text-sm font-medium text-gray-900">
                    <span>{filter.display_label}</span>
                    <button
                      type="button"
                      onClick={() => {
                        const newFilters = filters.filter((row: iComboBoxFilter) => row !== filter);
                        comboxBoxFilterVar(newFilters);
                        if (newFilters.length) {
                          setFiltersInQueryString(JSON.stringify(newFilters));
                        } else {
                          setFiltersInQueryString(undefined);
                        }
                        resetField(filter.name);
                      }}
                      // onClick={() => {
                      //   const newFilters = filters.filter((row: iComboBoxFilter) => row !== filter);
                      //   setCurrentFilters(newFilters);
                      // if (newFilters.length) {
                      //   setFiltersInQueryString(JSON.stringify(newFilters));
                      // } else {
                      //   setFiltersInQueryString(undefined);
                      // }
                      // resetField(filter.name);
                      // }}
                      className="ml-1 inline-flex h-4 w-4 flex-shrink-0 rounded-full p-1 text-gray-400 hover:bg-gray-200 hover:text-gray-500">
                      <span className="sr-only">Remove filter for {filter.display_label}</span>
                      <svg className="h-2 w-2" stroke="currentColor" fill="none" viewBox="0 0 8 8">
                        <path strokeLinecap="round" strokeWidth="1.5" d="M1 1l6 6m0-6L1 7" />
                      </svg>
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {!showFilters && (
              <ChevronRightIcon
                onClick={() => setShowFilters(true)}
                className="w-6 h-6 cursor-pointer text-gray-500"
              />
            )}
            {showFilters && (
              <ChevronDownIcon
                onClick={() => setShowFilters(false)}
                className="w-6 h-6 cursor-pointer text-gray-500"
              />
            )}

            {/* Sort Options Dropdown */}
            {/* <div className="flex justify-end">
              <Menu as="div" className="relative inline-block">
                <div className="flex">
                  <Menu.Button className="group inline-flex justify-center text-sm font-medium text-gray-700 hover:text-gray-900">
                    Sort
                    <ChevronDownIcon
                      className="-mr-1 ml-1 h-5 w-5 flex-shrink-0 text-gray-400 group-hover:text-gray-500"
                      aria-hidden="true"
                    />
                  </Menu.Button>
                </div>

                <Transition
                  as={Fragment}
                  enter="transition ease-out duration-100"
                  enterFrom="transform opacity-0 scale-95"
                  enterTo="transform opacity-100 scale-100"
                  leave="transition ease-in duration-75"
                  leaveFrom="transform opacity-100 scale-100"
                  leaveTo="transform opacity-0 scale-95"
                >
                  <Menu.Items className="absolute right-0 z-20 mt-2 w-40 origin-top-right rounded-md bg-white shadow-2xl ring-1 ring-black ring-opacity-5 focus:outline-none">
                    <div className="py-1">
                      {
                        sortOptions
                        .map(
                          (option) => (
                            <Menu.Item key={option.name}>
                              {
                                ({ active }) => (
                                  <a
                                    href={option.href}
                                    className={classNames(
                                      option.current
                                        ? "font-medium text-gray-900"
                                        : "text-gray-500",
                                      active ? "bg-gray-100" : "",
                                      "block px-4 py-2 text-sm"
                                    )}
                                  >
                                    {option.name}
                                  </a>
                                )
                              }
                            </Menu.Item>
                          )
                        )
                      }
                    </div>
                  </Menu.Items>
                </Transition>
              </Menu>
            </div> */}
          </div>
        </div>
        {showFilters && (
          <div className="border-t border-gray-200 pb-10">
            <div className="mx-auto px-4 text-sm sm:px-6">
              <div>
                <form className="flex-1" onSubmit={handleSubmit(onSubmit)}>
                  <FormProvider {...formMethods}>
                    <div className="mb-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
                      {formFields.map((field: any, index: number) => (
                        <FilterField
                          key={index}
                          field={field}
                          error={resolve(field.name, errors)}
                        />
                      ))}
                    </div>
                    <Button className="ml-2" type="submit">
                      Filter
                      <FunnelIcon className="w-4 h-4 text-gray-500" />
                    </Button>
                  </FormProvider>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
