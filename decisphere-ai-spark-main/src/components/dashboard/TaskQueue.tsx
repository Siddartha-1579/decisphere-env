import { SimState } from "@/lib/simulation";
import { motion } from "framer-motion";

interface TaskQueueProps {
  state: SimState | null;
}

type TaskItem = SimState["tasks"][number];

export default function TaskQueue({ state }: TaskQueueProps) {
  if (!state) return null;

  const tasks: TaskItem[] = state.tasks ?? [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="ds-card p-5 flex flex-col gap-4"
    >
      <h3 className="font-display font-bold text-sm text-foreground">
        Task Queue
      </h3>

      <div className="flex flex-col gap-3">
        {tasks.length === 0 ? (
          <div className="text-sm text-muted-foreground">
            No tasks available
          </div>
        ) : (
          tasks.map((task, index) => {
            const taskData = task as unknown as Record<string, unknown>;

            const taskId =
              typeof taskData.id === "string"
                ? taskData.id
                : `task-${index}`;

            const taskName =
              typeof taskData.name === "string"
                ? taskData.name
                : taskId;

            const urgency =
              typeof taskData.urgency === "number"
                ? taskData.urgency
                : 0;

            const importance =
              typeof taskData.importance === "number"
                ? taskData.importance
                : 0;

            return (
              <div
                key={taskId}
                className="p-3 rounded-xl border border-border bg-background/40"
              >
                <div className="text-sm font-medium text-foreground">
                  {taskName}
                </div>

                <div className="text-xs text-muted-foreground">
                  Urgency: {urgency} | Importance: {importance}
                </div>
              </div>
            );
          })
        )}
      </div>
    </motion.div>
  );
}