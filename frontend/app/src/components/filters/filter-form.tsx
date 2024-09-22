import { Form, FormProps, FormRef, FormSubmit } from "@/components/ui/form";
import { IModelSchema } from "@/state/atoms/schema.atom";
import { Filter } from "@/hooks/useFilters";
import React, { forwardRef } from "react";
import { getFormFieldsFromSchema } from "@/components/form/utils/getFormFieldsFromSchema";
import { getObjectFromFilters } from "@/components/filters/utils/getObjectFromFilters";
import { classNames, isGeneric } from "@/utils/common";
import { DynamicInput } from "@/components/form/dynamic-form";
import { Button } from "@/components/buttons/button-primitive";
import { FilterKindSelector } from "@/components/filters/filter-kind-selector";

export interface FilterFormProps extends FormProps {
  schema: IModelSchema;
  filters: Array<Filter>;
  onCancel?: () => void;
}

export const FilterForm = forwardRef<FormRef, FilterFormProps>(
  ({ filters, className, schema, onSubmit, onCancel, ...props }, ref) => {
    const fields = getFormFieldsFromSchema({
      schema,
      isFilterForm: true,
      initialObject: getObjectFromFilters(schema, filters),
    });

    return (
      <Form
        ref={ref}
        onSubmit={onSubmit}
        className={classNames("bg-custom-white flex flex-col flex-1 overflow-auto p-4", className)}
        {...props}>
        {isGeneric(schema) && schema.used_by?.length ? (
          <FilterKindSelector genericSchema={schema} />
        ) : null}

        {fields.map((field) => (
          <DynamicInput key={field.name} {...field} />
        ))}

        <div className="text-right">
          {onCancel && (
            <Button variant="outline" className="mr-2" onClick={onCancel}>
              Cancel
            </Button>
          )}

          <FormSubmit>Apply filters</FormSubmit>
        </div>
      </Form>
    );
  }
);