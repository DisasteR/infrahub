import { Tooltip } from "@/components/ui/tooltip";
import { classNames } from "@/utils/common";
import { differenceInDays, format, formatDistanceToNow } from "date-fns";

type DateDisplayProps = {
  date?: number | string | Date;
  hideDefault?: boolean;
  className?: string;
};

export const getDateDisplay = (date?: number | string | Date) =>
  format(date ? new Date(date) : new Date(), "yyyy-MM-dd HH:mm:ss (O)");

export const DateDisplay = (props: DateDisplayProps) => {
  const { date, hideDefault, className } = props;

  if (!date && hideDefault) {
    return null;
  }

  const dateData = date ? new Date(date) : new Date();

  const distanceFromNow = differenceInDays(new Date(), dateData);

  if (distanceFromNow > 7) {
    return (
      <span className="flex items-center flex-wrap">
        <Tooltip enabled content={getDateDisplay(date)}>
          <span className="text-xs font-normal">{format(dateData, "MMM d")}</span>
        </Tooltip>
      </span>
    );
  }

  return (
    <span className={classNames("flex items-center flex-wrap", className)}>
      <Tooltip enabled content={getDateDisplay(date)}>
        <span className="text-xs font-normal">
          {formatDistanceToNow(dateData, { addSuffix: true })}
        </span>
      </Tooltip>
    </span>
  );
};
