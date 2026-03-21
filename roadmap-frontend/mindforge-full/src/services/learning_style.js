import API from "./api";

// POST
export const createLearningStyle = (data) => API.post("/learning-style/", data);

// GET
export const getLearningStyle = (userId) => API.get(`/learning-style/${userId}`);
