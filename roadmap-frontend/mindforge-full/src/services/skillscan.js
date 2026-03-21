import API from "./api";

// POST
export const createSkillScan = (data) => API.post("/skill-scan/", data);

// GET (if needed)
export const getSkillScan = (userId) => API.get(`/skill-scan/${userId}`);
