import API from "./api";

// POST
export const sendConfusionSignal = (data) => API.post("/confusion-signals/", data);

// GET
export const getConfusionSignals = (userId) => API.get(`/confusion-signals/${userId}`);
