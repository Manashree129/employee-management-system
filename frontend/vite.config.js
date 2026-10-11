import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The backend only allows the CORS origin in FRONTEND_ORIGIN (default http://localhost:5173),
// so the port is fixed.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, strictPort: true },
});
