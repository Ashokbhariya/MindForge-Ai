import API from "./api";

// POST
export const createDecayEvent = (data) => API.post("/knowledge-decay/", data);

// GET
export const getDecayEvents = (userId) => API.get(`/knowledge-decay/${userId}`);
