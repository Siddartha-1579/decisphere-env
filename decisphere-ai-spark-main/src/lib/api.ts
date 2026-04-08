// src/lib/api.ts

const API_BASE = "http://127.0.0.1:7860";

// Define each task in the payload
export interface SimulationTask {
  id: string;
  priority: number;
  duration: number;
}

// Define the shape of the simulation payload
export interface SimulationPayload {
  tasks: SimulationTask[];
  resources?: number;
  deadline?: number;
  // Add more fields as needed
}

// Define the shape of the simulation result
export interface SimulationResult {
  score: number;
  risk: "Low" | "Medium" | "High";
  recommendation: string;
  timeline: number;
}

export async function runSimulation(
  payload: SimulationPayload
): Promise<SimulationResult> {
  try {
    const response = await fetch(`${API_BASE}/simulate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("Simulation failed");
    }

    // Explicitly type the JSON response
    const data: SimulationResult = await response.json();
    return data;
  } catch (error) {
    console.warn("Backend unavailable, using fallback", error);

    // Fallback result
    return {
      score: 90,
      risk: "Low",
      recommendation: "Mock fallback mode active",
      timeline: 12,
    };
  }
}