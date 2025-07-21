import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: '/agisa_sac/',
  plugins: [react()],
});
