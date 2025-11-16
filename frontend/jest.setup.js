import "@testing-library/jest-dom";
import "whatwg-fetch";

// =======================================================
// MOCK: window.URL.createObjectURL (no existe en JSDOM)
// =======================================================
global.URL.createObjectURL = vi.fn(() => "blob:mock");

// =======================================================
// MOCK: window.ethereum (MetaMask)
// =======================================================
global.window.ethereum = {
  request: vi.fn(async ({ method }) => {
    if (method === "eth_requestAccounts") return ["0x1234567890abcdef"];
    if (method === "eth_chainId") return "0x7A69"; // 31337
    return null;
  })
};

// =======================================================
// MOCK: ethers
// BrowserProvider, Signer, Contract
// =======================================================
vi.mock("ethers", () => {
  return {
    BrowserProvider: vi.fn().mockImplementation(() => ({
      getNetwork: vi.fn(async () => ({ chainId: 31337 })),
      getSigner: vi.fn(async () => ({
        getAddress: vi.fn(async () => "0x1234567890abcdef1234567890abcdef12345678"),
        signMessage: vi.fn(async () => "signed_nonce")
      }))
    })),

    Contract: vi.fn().mockImplementation(() => ({
      checkInEvent: vi.fn(async () => ({
        hash: "0xtesthash00000000000000",
        wait: vi.fn(async () => ({ status: 1, blockNumber: 12345 }))
      }))
    })),

    // Necesario para cualquier otra importación
    ethers: {}
  };
});

// =======================================================
// MOCK: maplibre-gl (WebGL no funciona en Jest)
// =======================================================
vi.mock("maplibre-gl", () => ({
  Map: vi.fn(),
  NavigationControl: vi.fn(),
  Popup: vi.fn(),
  Marker: vi.fn()
}));

// =======================================================
// MOCK: react-map-gl/maplibre
// =======================================================
vi.mock("react-map-gl/maplibre", () => {
  return {
    __esModule: true,
    default: vi.fn(({ children }) => (
      <div data-testid="mock-map">{children}</div>
    )),
    Source: vi.fn(({ children }) => (
      <div data-testid="mock-source">{children}</div>
    )),
    Layer: vi.fn(() => <div data-testid="mock-layer" />),
    Marker: vi.fn(({ children }) => (
      <div data-testid="mock-marker">{children}</div>
    )),
    Popup: vi.fn(({ children }) => (
      <div data-testid="mock-popup">{children}</div>
    ))
  };
});
