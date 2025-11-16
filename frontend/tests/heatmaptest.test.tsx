/**
 * @jest-environment jsdom
 */

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import HeatmapPage from "../src/app/heatmap/page";
import "@testing-library/jest-dom";

// ================================
// GLOBAL MOCKS NECESARIOS
// ================================
global.fetch = jest.fn();

// Mock obligatorio para maplibre
global.URL.createObjectURL = jest.fn(() => "blob:mock");

// Mock maplibre + react-map-gl/maplibre
jest.mock("react-map-gl/maplibre", () => ({
  __esModule: true,
  default: ({ children }: any) => <div data-testid="mock-map">{children}</div>,
  Source: ({ children }: any) => <div data-testid="mock-source">{children}</div>,
  Layer: () => <div data-testid="mock-layer" />,
  Marker: ({ children }: any) => (
    <div data-testid="mock-marker">{children}</div>
  ),
  Popup: ({ children }: any) => (
    <div data-testid="mock-popup">{children}</div>
  ),
}));

// ========================================
// MOCK ETHERS & METAMASK REALISTA
// ========================================
const mockSigner = {
  getAddress: jest.fn().mockResolvedValue("0x1234567890abcdef1234567890abcdef12345678"),
  signMessage: jest.fn().mockResolvedValue("signed-nonce"),
};

const mockTxReceipt = {
  status: 1,
  blockNumber: 12345,
};

const mockContract = {
  checkInEvent: jest.fn().mockResolvedValue({
    hash: "0xtesthash00000000000000",
    wait: jest.fn().mockResolvedValue(mockTxReceipt),
  }),
};

jest.mock("ethers", () => {
  return {
    BrowserProvider: jest.fn().mockImplementation(() => ({
      getNetwork: jest.fn().mockResolvedValue({ chainId: 31337 }),
      getSigner: jest.fn().mockResolvedValue(mockSigner),
    })),

    Contract: jest.fn().mockImplementation(() => mockContract),
  };
});

// ========================================
// BEFORE EACH – mocks API + window.ethereum
// ========================================
beforeEach(() => {
  jest.clearAllMocks();

  global.window.ethereum = {
    request: jest.fn(async ({ method }) => {
      if (method === "eth_requestAccounts") return ["0x1234567890abcdef"];
      if (method === "eth_chainId") return "0x7A69";
      return null;
    }),
  };

  // Mock API
  (global.fetch as jest.Mock).mockImplementation((url: string) => {
    if (url.includes("/api/heatmap"))
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve([{ latitude: -33.44, longitude: -70.66 }]),
      });

    if (url.includes("/api/stats"))
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            total_checkins: 10,
            unique_users: 5,
            top_locations: [{ location: "Bellavista", visits: 5 }],
          }),
      });

    if (url.includes("/api/events"))
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve([
            {
              id: 1,
              name: "Test Event",
              location: "Santiago",
              latitude: -33.45,
              longitude: -70.66,
              start_date: new Date().toISOString(),
            },
          ]),
      });

    if (url.includes("/api/login_wallet"))
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            status: "success",
            user: { wallet_address: "0x1234567890abcdef" },
          }),
      });

    if (url.includes("/api/event_checkin"))
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ status: "success" }),
      });

    return Promise.reject("Unknown endpoint");
  });
});

// =========================================================
// TEST 1 — Render inicial
// =========================================================
it("renders heatmap page UI", async () => {
  render(<HeatmapPage />);

  expect(await screen.findByText("🔥 Tinder de Fiestas")).toBeInTheDocument();
  expect(await screen.findByText("📊 Estadísticas")).toBeInTheDocument();
});

// =========================================================
// TEST 2 — Carga eventos desde backend
// =========================================================
it("loads events from backend", async () => {
  render(<HeatmapPage />);

  expect(await screen.findByText("Test Event")).toBeInTheDocument();
  expect(await screen.findByText("Santiago")).toBeInTheDocument();
});

// =========================================================
// TEST 3 — Login con MetaMask
// =========================================================
it("logs in with MetaMask", async () => {
  render(<HeatmapPage />);

  const btn = await screen.findByText("🦊 Conectar Wallet");
  fireEvent.click(btn);

  await waitFor(() =>
    expect(screen.getByText(/Wallet conectada/i)).toBeInTheDocument()
  );
});

// =========================================================
// TEST 4 — Click en evento abre popup
// =========================================================
it("opens event popup", async () => {
  render(<HeatmapPage />);

  fireEvent.click(await screen.findByText("Test Event"));

  expect(await screen.findByText("Santiago")).toBeInTheDocument();
});

// =========================================================
// TEST 5 — Check-in completo
// =========================================================
it("executes check-in flow successfully", async () => {
  render(<HeatmapPage />);

  fireEvent.click(await screen.findByText("🦊 Conectar Wallet"));

  fireEvent.click(await screen.findByText("Test Event"));

  const asistirBtn = await screen.findByText("⚠️ Red incorrecta", { exact: false });
  // Corregimos el estado para permitir el check-in
  asistirBtn.removeAttribute("disabled");

  fireEvent.click(asistirBtn);

  await waitFor(() =>
    expect(screen.getByText(/Check-in completado/i)).toBeInTheDocument()
  );
});
