import { vi } from 'vitest';
import '@testing-library/jest-dom';

// Mock fetch globally for all tests
global.fetch = vi.fn();

// Reset mocks before each test
beforeEach(() => {
  vi.clearAllMocks();
});
