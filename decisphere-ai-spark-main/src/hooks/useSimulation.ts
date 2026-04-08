import { useEffect, useState } from "react";
import {
  SimState,
  Action,
  createInitialState,
  tryBackendReset,
  tryBackendStep,
} from "@/lib/simulation";

const defaultState = createInitialState();

export function useSimulation() {
  const [state, setState] = useState<SimState>(defaultState);
  const [loading, setLoading] = useState(false);

  const resetSimulation = async () => {
    try {
      setLoading(true);

      const backendState = await tryBackendReset();

      if (backendState) {
        setState(backendState);
      } else {
        setState(createInitialState());
      }
    } catch (error) {
      console.error("Reset simulation failed:", error);
      setState(createInitialState());
    } finally {
      setLoading(false);
    }
  };

  const performAction = async (action: Action) => {
    try {
      setLoading(true);

      const backendState = await tryBackendStep(action);

      if (backendState) {
        setState(backendState);
      }
    } catch (error) {
      console.error("Perform action failed:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    resetSimulation();
  }, []);

  return {
    state,
    loading,
    resetSimulation,
    performAction,
  };
}