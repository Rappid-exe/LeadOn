const envBase =
  import.meta.env.VITE_HACKATHON_CRM_API_URL ??
  import.meta.env.VITE_HACKATHON_API_BASE ??
  'http://localhost:8000/api';

export const CRM_API_BASE_URL = String(envBase).replace(/\/$/, '');
