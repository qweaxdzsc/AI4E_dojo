import '@testing-library/jest-dom/vitest';

globalThis.matchMedia = globalThis.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {}, dispatchEvent() { return false; } }));
globalThis.ResizeObserver = globalThis.ResizeObserver || class { observe() {} unobserve() {} disconnect() {} };
globalThis.IntersectionObserver = globalThis.IntersectionObserver || class { observe() {} unobserve() {} disconnect() {} };
if (!globalThis.fetch) globalThis.fetch = () => Promise.reject(new Error('offline test'));
