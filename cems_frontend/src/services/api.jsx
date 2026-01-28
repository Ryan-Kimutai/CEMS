import axios from "axios";

const API_URL = "http://127.0.0.1:8000/";

// helper to get token
const getToken = () => localStorage.getItem("token");

// =======================
// Event APIs
// =======================

export const getEvents = async () => {
  const { data } = await axios.get(`${API_URL}/api/events`);
  return data;
};

export const getEventById = async (id) => {
  const { data } = await axios.get(`${API_URL}/api/events/${id}`);
  return data;
};

export const createEvent = async (eventData) => {
  const token = getToken();
  const { data } = await axios.post(`${API_URL}/api/events`, eventData, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return data;
};

export const deleteEvent = async (eventId) => {
  const token = getToken();
  await axios.delete(`${API_URL}/api/events/${eventId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
};

export const rsvpEvent = async (eventId) => {
  const token = getToken();
  await axios.post(
    `${API_URL}/api/events/${eventId}/rsvp`,
    {},
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );
};

export const getEventAttendees = async (eventId) => {
  const token = getToken();
  const { data } = await axios.get(
    `${API_URL}/api/events/${eventId}/attendees`,
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );
  return data;
};

export const sendEventReminder = async (eventId) => {
  const token = getToken();
  const { data } = await axios.post(
    `${API_URL}/api/events/${eventId}/remind`,
    {},
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );
  return data;
};

// =======================
// User APIs
// =======================

export const loginUser = async (email, password) => {
  const { data } = await axios.post(`${API_URL}api/auth/login/`, {
    email,
    password,
  });
  return data;
};

export const registerUser = async (name, email, password, isAdmin) => {
  try {
    const { data } = await axios.post(`${API_URL}api/auth/signup/`, {
      username: name,
      email,
      password,
      password2: password,
    });
    return data;
  } catch (error) {
    if (error.response) {
      console.error('Backend validation errors:', error.response.data);
    }
    throw error;
  }
};

export const logoutUser = async () => {
  const token = getToken();
  const { data } = await axios.post(
    `${API_URL}api/auth/logout/`,
    {},
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );
  return data;
};