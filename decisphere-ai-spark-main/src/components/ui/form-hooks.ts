import * as React from "react";
import { FieldPath, FieldValues, useFormContext } from "react-hook-form";

// Context types
export type FormFieldContextValue<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
> = {
  name: TName;
};

export type FormItemContextValue = {
  id: string;
};

// Contexts
export const FormFieldContext = React.createContext<FormFieldContextValue | null>(null);
export const FormItemContext = React.createContext<FormItemContextValue | null>(null);

// Hook
export const useFormField = () => {
  const fieldContext = React.useContext(FormFieldContext);
  const itemContext = React.useContext(FormItemContext);
  const { getFieldState, formState } = useFormContext();

  if (!fieldContext) throw new Error("useFormField should be used within <FormField>");

  const { id } = itemContext || {};
  const fieldState = getFieldState(fieldContext.name, formState);

  return {
    id,
    name: fieldContext.name,
    formItemId: `${id}-form-item`,
    formDescriptionId: `${id}-form-item-description`,
    formMessageId: `${id}-form-item-message`,
    ...fieldState,
  };
};