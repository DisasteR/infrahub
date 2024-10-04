import React from "react";
import { Link, LinkProps } from "react-router-dom";
import { Slot } from "@radix-ui/react-slot";
import { classNames } from "@/utils/common";
import { breadcrumbItemStyle } from "@/screens/layout/breadcrumb-navigation/style";

export const BreadcrumbLink = React.forwardRef<
  HTMLAnchorElement,
  LinkProps & {
    asChild?: boolean;
  }
>(({ asChild, className, ...props }, ref) => {
  const Comp = asChild ? Slot : Link;

  return <Comp ref={ref} className={classNames(breadcrumbItemStyle, className)} {...props} />;
});
