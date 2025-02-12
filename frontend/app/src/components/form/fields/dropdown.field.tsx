import { DEFAULT_FORM_FIELD_VALUE } from "@/components/form/constants";
import { LabelFormField } from "@/components/form/fields/common";
import { DynamicDropdownFieldProps, FormAttributeValue } from "@/components/form/type";
import { updateFormFieldValue } from "@/components/form/utils/updateFormFieldValue";
import { Dropdown, DropdownProps } from "@/components/inputs/dropdown";
import { FormField, FormInput, FormMessage } from "@/components/ui/form";

export interface DropdownFieldProps
  extends Omit<DynamicDropdownFieldProps, "type">,
    Omit<DropdownProps, "defaultValue" | "name" | "options"> {}

const DropdownField = ({
  defaultValue = DEFAULT_FORM_FIELD_VALUE,
  description,
  items,
  label,
  name,
  rules,
  unique,
  ...props
}: DropdownFieldProps) => {
  return (
    <FormField
      key={name}
      name={name}
      rules={rules}
      defaultValue={defaultValue}
      render={({ field }) => {
        const fieldData: FormAttributeValue = field.value;

        return (
          <div className="flex flex-col gap-2">
            <LabelFormField
              label={label}
              unique={unique}
              required={!!rules?.required}
              description={description}
              fieldData={fieldData}
            />

            <FormInput>
              <Dropdown
                {...field}
                {...props}
                items={items}
                value={fieldData?.value as string | null}
                onChange={(newValue) => {
                  field.onChange(updateFormFieldValue(newValue, defaultValue));
                }}
              />
            </FormInput>

            <FormMessage />
          </div>
        );
      }}
    />
  );
};

export default DropdownField;
